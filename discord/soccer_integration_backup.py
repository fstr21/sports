"""
Soccer Integration Module for Discord Bot
Provides comprehensive soccer data integration using Soccer MCP server
"""

import asyncio
import httpx
import json
import logging
import discord
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# Soccer MCP Server Configuration
SOCCER_MCP_URL = "https://soccermcp-production.up.railway.app/mcp"
SOCCER_MCP_TIMEOUT = 30.0

# Supported Soccer Leagues Configuration
SUPPORTED_LEAGUES = {
    "EPL": {
        "id": 228,
        "name": "Premier League",
        "country": "England",
        "color": 0x3d195b,  # Premier League purple
        "emoji": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"
    },
    "La Liga": {
        "id": 297,
        "name": "La Liga",
        "country": "Spain", 
        "color": 0xff6900,  # La Liga orange
        "emoji": "🇪🇸"
    },
    "MLS": {
        "id": 168,
        "name": "MLS",
        "country": "USA",
        "color": 0x005da6,  # MLS blue
        "emoji": "🇺🇸"
    },
    "Bundesliga": {
        "id": 241,
        "name": "Bundesliga",
        "country": "Germany",
        "color": 0xd20515,  # Bundesliga red
        "emoji": "🇩🇪"
    },
    "Serie A": {
        "id": 253,
        "name": "Serie A",
        "country": "Italy",
        "color": 0x0066cc,  # Serie A blue
        "emoji": "🇮🇹"
    },
    "UEFA": {
        "id": 310,
        "name": "UEFA Champions League",
        "country": "Europe",
        "color": 0x00336a,  # UEFA dark blue
        "emoji": "🏆"
    }
}

# MCP Tools Available
AVAILABLE_MCP_TOOLS = [
    "get_matches",
    "get_head_to_head",
    "get_league_standings", 
    "get_match_details",
    "get_team_info"
]

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class OddsFormat:
    """Represents betting odds in both decimal and American formats"""
    decimal: float
    american: int
    
    @classmethod
    def from_decimal(cls, decimal_odds: float) -> 'OddsFormat':
        """Convert decimal odds to both formats"""
        american = cls._decimal_to_american(decimal_odds)
        return cls(decimal=decimal_odds, american=american)
    
    @staticmethod
    def _decimal_to_american(decimal_odds: float) -> int:
        """Convert decimal odds to American format"""
        if decimal_odds >= 2.0:
            return int((decimal_odds - 1) * 100)
        else:
            return int(-100 / (decimal_odds - 1))

@dataclass
class OverUnder:
    """Over/Under betting market"""
    line: float
    over_odds: OddsFormat
    under_odds: OddsFormat

@dataclass
class Handicap:
    """Handicap/Spread betting market"""
    line: float
    home_odds: OddsFormat
    away_odds: OddsFormat

@dataclass
class BettingOdds:
    """Complete betting odds for a soccer match"""
    home_win: Optional[OddsFormat] = None
    draw: Optional[OddsFormat] = None
    away_win: Optional[OddsFormat] = None
    over_under: Optional[OverUnder] = None
    handicap: Optional[Handicap] = None
    both_teams_score: Optional[OddsFormat] = None
    
    @property
    def has_odds(self) -> bool:
        """Check if any odds are available"""
        return any([self.home_win, self.draw, self.away_win])

@dataclass
class Team:
    """Soccer team information"""
    id: int
    name: str
    short_name: str
    logo_url: Optional[str] = None
    country: Optional[str] = None
    
    @property
    def clean_name(self) -> str:
        """Get cleaned team name for channel creation"""
        return self.name.lower().replace(' ', '-').replace('.', '').replace('&', 'and')

@dataclass
class League:
    """Soccer league information"""
    id: int
    name: str
    country: str
    season: Optional[str] = None
    logo_url: Optional[str] = None
    
    @property
    def config(self) -> Optional[Dict]:
        """Get league configuration from SUPPORTED_LEAGUES"""
        for key, config in SUPPORTED_LEAGUES.items():
            if config["id"] == self.id:
                return config
        return None

@dataclass
class H2HSummary:
    """Brief head-to-head summary for match preview"""
    total_meetings: int
    home_team_wins: int
    away_team_wins: int
    draws: int
    last_meeting_result: Optional[str] = None

@dataclass
class H2HInsights:
    """Comprehensive head-to-head analysis"""
    total_meetings: int
    home_team_wins: int
    away_team_wins: int
    draws: int
    avg_goals_per_game: float
    recent_form: Dict[str, List[str]] = field(default_factory=dict)
    betting_recommendations: List[str] = field(default_factory=list)
    key_statistics: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def home_win_percentage(self) -> float:
        """Calculate home team win percentage"""
        if self.total_meetings == 0:
            return 0.0
        return (self.home_team_wins / self.total_meetings) * 100
    
    @property
    def away_win_percentage(self) -> float:
        """Calculate away team win percentage"""
        if self.total_meetings == 0:
            return 0.0
        return (self.away_team_wins / self.total_meetings) * 100
    
    @property
    def draw_percentage(self) -> float:
        """Calculate draw percentage"""
        if self.total_meetings == 0:
            return 0.0
        return (self.draws / self.total_meetings) * 100

@dataclass
class ProcessedMatch:
    """Complete processed match data for Discord display"""
    match_id: int
    home_team: Team
    away_team: Team
    league: League
    date: str
    time: str
    venue: str
    status: str
    odds: Optional[BettingOdds] = None
    h2h_summary: Optional[H2HSummary] = None
    
    @property
    def channel_name(self) -> str:
        """Generate Discord channel name for this match"""
        date_short = datetime.strptime(self.date, "%Y-%m-%d").strftime("%m-%d")
        return f"📊 {date_short}-{self.away_team.clean_name}-vs-{self.home_team.clean_name}"
    
    @property
    def display_time(self) -> str:
        """Format time for display"""
        try:
            time_obj = datetime.strptime(self.time, "%H:%M")
            return time_obj.strftime("%I:%M %p")
        except ValueError:
            return self.time

# ============================================================================
# EXCEPTIONS
# ============================================================================

class SoccerMCPError(Exception):
    """Base exception for Soccer MCP operations"""
    pass

class MCPConnectionError(SoccerMCPError):
    """MCP server connection issues"""
    pass

class MCPDataError(SoccerMCPError):
    """Invalid or missing data from MCP"""
    pass

class MCPTimeoutError(SoccerMCPError):
    """MCP server timeout"""
    pass

# ============================================================================
# SOCCER MCP CLIENT
# ============================================================================

class SoccerMCPClient:
    """Client for communicating with Soccer MCP server"""
    
    def __init__(self, mcp_url: str = SOCCER_MCP_URL, timeout: float = SOCCER_MCP_TIMEOUT):
        self.mcp_url = mcp_url
        self.timeout = timeout
        self.supported_tools = AVAILABLE_MCP_TOOLS.copy()
        self._session: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self._session = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._session:
            await self._session.aclose()
            self._session = None
    
    async def _get_session(self) -> httpx.AsyncClient:
        """Get or create HTTP session"""
        if not self._session:
            self._session = httpx.AsyncClient(timeout=self.timeout)
        return self._session
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic method to call any MCP tool
        
        Args:
            tool_name: Name of the MCP tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Dict containing the tool response
            
        Raises:
            MCPConnectionError: If connection to MCP server fails
            MCPDataError: If response data is invalid
            MCPTimeoutError: If request times out
        """
        if tool_name not in self.supported_tools:
            raise MCPDataError(f"Tool '{tool_name}' not supported. Available tools: {self.supported_tools}")
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            session = await self._get_session()
            response = await session.post(
                self.mcp_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "error" in data:
                raise MCPDataError(f"MCP server error: {data['error']}")
            
            if "result" not in data:
                raise MCPDataError("Invalid MCP response format")
            
            return data["result"]
            
        except httpx.TimeoutException:
            raise MCPTimeoutError(f"Request to MCP server timed out after {self.timeout}s")
        except httpx.HTTPStatusError as e:
            raise MCPConnectionError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise MCPConnectionError(f"Connection error: {str(e)}")
        except json.JSONDecodeError:
            raise MCPDataError("Invalid JSON response from MCP server")
    
    async def get_matches_for_date(self, date: str, league_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Get soccer matches for a specific date
        
        Args:
            date: Date in YYYY-MM-DD format
            league_filter: Optional league filter (e.g., "EPL", "La Liga")
            
        Returns:
            Dict containing matches organized by league
        """
        arguments = {"date": date}
        if league_filter:
            arguments["league"] = league_filter
        
        try:
            result = await self.call_mcp_tool("get_matches", arguments)
            logger.info(f"Retrieved matches for date {date}")
            return result
        except Exception as e:
            logger.error(f"Failed to get matches for date {date}: {str(e)}")
            raise
    
    async def get_h2h_analysis(self, team1_id: int, team2_id: int) -> Dict[str, Any]:
        """
        Get head-to-head analysis between two teams
        
        Args:
            team1_id: ID of first team
            team2_id: ID of second team
            
        Returns:
            Dict containing H2H analysis data
        """
        arguments = {
            "team1_id": team1_id,
            "team2_id": team2_id
        }
        
        try:
            result = await self.call_mcp_tool("get_head_to_head", arguments)
            logger.info(f"Retrieved H2H analysis for teams {team1_id} vs {team2_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to get H2H analysis for teams {team1_id} vs {team2_id}: {str(e)}")
            raise
    
    async def get_betting_odds(self, match_id: int) -> Dict[str, Any]:
        """
        Get betting odds for a specific match
        
        Args:
            match_id: ID of the match
            
        Returns:
            Dict containing betting odds data
        """
        arguments = {"match_id": match_id}
        
        try:
            result = await self.call_mcp_tool("get_match_details", arguments)
            logger.info(f"Retrieved betting odds for match {match_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to get betting odds for match {match_id}: {str(e)}")
            raise
    
    async def get_league_standings(self, league_id: int) -> Dict[str, Any]:
        """
        Get current league standings
        
        Args:
            league_id: ID of the league
            
        Returns:
            Dict containing league standings data
        """
        arguments = {"league_id": league_id}
        
        try:
            result = await self.call_mcp_tool("get_league_standings", arguments)
            logger.info(f"Retrieved standings for league {league_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to get standings for league {league_id}: {str(e)}")
            raise
    
    async def get_team_info(self, team_id: int) -> Dict[str, Any]:
        """
        Get detailed team information
        
        Args:
            team_id: ID of the team
            
        Returns:
            Dict containing team information
        """
        arguments = {"team_id": team_id}
        
        try:
            result = await self.call_mcp_tool("get_team_info", arguments)
            logger.info(f"Retrieved team info for team {team_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to get team info for team {team_id}: {str(e)}")
            raise
    
    async def validate_connection(self) -> bool:
        """
        Validate connection to MCP server
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try a simple call to test connectivity
            await self.call_mcp_tool("get_matches", {"date": datetime.now().strftime("%Y-%m-%d")})
            return True
        except Exception as e:
            logger.error(f"MCP server connection validation failed: {str(e)}")
            return False

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_date_format(date_string: str) -> str:
    """
    Validate and normalize date input to YYYY-MM-DD format
    
    Args:
        date_string: Date in MM/DD/YYYY, DD-MM-YYYY, or YYYY-MM-DD format
        
    Returns:
        Normalized date string in YYYY-MM-DD format
        
    Raises:
        ValueError: If date format is invalid or date is out of range
    """
    allowed_formats = ["%m/%d/%Y", "%d-%m-%Y", "%Y-%m-%d"]
    parsed_date = None
    
    # First, try to parse the date with any of the allowed formats
    for fmt in allowed_formats:
        try:
            parsed_date = datetime.strptime(date_string, fmt)
            break
        except ValueError:
            continue
    
    # If no format worked, raise format error
    if parsed_date is None:
        raise ValueError(f"Invalid date format. Use MM/DD/YYYY, DD-MM-YYYY, or YYYY-MM-DD")
    
    # Now validate the date range
    now = datetime.now()
    min_date = now - timedelta(days=30)
    max_date = now + timedelta(days=365)
    
    if not (min_date <= parsed_date <= max_date):
        raise ValueError("Date must be within 30 days past to 1 year future")
    
    return parsed_date.strftime("%Y-%m-%d")

def get_league_config(league_identifier: Union[str, int]) -> Optional[Dict[str, Any]]:
    """
    Get league configuration by name or ID
    
    Args:
        league_identifier: League name (e.g., "EPL") or ID (e.g., 228)
        
    Returns:
        League configuration dict or None if not found
    """
    if isinstance(league_identifier, str):
        return SUPPORTED_LEAGUES.get(league_identifier)
    
    elif isinstance(league_identifier, int):
        for config in SUPPORTED_LEAGUES.values():
            if config["id"] == league_identifier:
                return config
    
    return None

def clean_team_name_for_channel(team_name: str) -> str:
    """
    Clean team name for Discord channel creation
    
    Args:
        team_name: Original team name
        
    Returns:
        Cleaned team name suitable for channel names
    """
    # Convert to lowercase and replace problematic characters
    cleaned = team_name.lower()
    cleaned = cleaned.replace(' ', '-')
    cleaned = cleaned.replace('.', '')
    cleaned = cleaned.replace('&', 'and')
    cleaned = cleaned.replace('/', '-')
    cleaned = cleaned.replace('\\', '-')
    cleaned = cleaned.replace('(', '')
    cleaned = cleaned.replace(')', '')
    cleaned = cleaned.replace('[', '')
    cleaned = cleaned.replace(']', '')
    cleaned = cleaned.replace('{', '')
    cleaned = cleaned.replace('}', '')
    cleaned = cleaned.replace('!', '')
    cleaned = cleaned.replace('?', '')
    cleaned = cleaned.replace(',', '')
    cleaned = cleaned.replace(';', '')
    cleaned = cleaned.replace(':', '')
    cleaned = cleaned.replace('"', '')
    cleaned = cleaned.replace("'", '')
    
    # Remove multiple consecutive dashes
    while '--' in cleaned:
        cleaned = cleaned.replace('--', '-')
    
    # Remove leading/trailing dashes
    cleaned = cleaned.strip('-')
    
    # Ensure it's not empty and not too long
    if not cleaned:
        cleaned = "team"
    
    if len(cleaned) > 20:  # Keep channel names reasonable
        cleaned = cleaned[:20].rstrip('-')
    
    return cleaned

# ============================================================================
# SOCCER DATA PROCESSOR
# ============================================================================

class SoccerDataProcessor:
    """
    Processes and normalizes soccer data from MCP responses
    Handles odds conversion, team name cleaning, and data validation
    """
    
    def __init__(self):
        """Initialize the data processor"""
        self.logger = logging.getLogger(f"{__name__}.SoccerDataProcessor")
    
    def convert_to_american_odds(self, decimal_odds: float) -> int:
        """
        Convert decimal odds to American format
        
        Args:
            decimal_odds: Decimal odds (e.g., 2.50)
            
        Returns:
            American odds as integer (e.g., +150 or -200)
            
        Raises:
            ValueError: If decimal odds are invalid
        """
        if decimal_odds <= 0:
            raise ValueError("Decimal odds must be positive")
        
        if decimal_odds < 1:
            raise ValueError("Decimal odds must be 1.0 or greater")
        
        if decimal_odds >= 2.0:
            # Positive American odds
            american = int(round((decimal_odds - 1) * 100))
            return american
        else:
            # Negative American odds
            american = int(round(-100 / (decimal_odds - 1)))
            return american
    
    def clean_team_name_for_channel(self, team_name: str) -> str:
        """
        Clean team name for Discord channel creation following MLB patterns
        
        Args:
            team_name: Original team name
            
        Returns:
            Cleaned team name suitable for channel names
        """
        if not team_name or not isinstance(team_name, str):
            return "team"
        
        # Convert to lowercase and replace problematic characters
        cleaned = team_name.lower().strip()
        
        # Handle accented characters
        import unicodedata
        cleaned = unicodedata.normalize('NFD', cleaned)
        cleaned = ''.join(c for c in cleaned if unicodedata.category(c) != 'Mn')
        
        # Replace spaces and special characters
        replacements = {
            ' ': '-',
            '.': '',
            '&': 'and',
            '/': '-',
            '\\': '-',
            '(': '',
            ')': '',
            '[': '',
            ']': '',
            '{': '',
            '}': '',
            '!': '',
            '?': '',
            ',': '',
            ';': '',
            ':': '',
            '"': '',
            "'": '',
            '#': '',
            '@': '',
            '$': '',
            '%': '',
            '^': '',
            '*': '',
            '+': '',
            '=': '',
            '|': '',
            '~': '',
            '`': ''
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        # Remove multiple consecutive dashes
        while '--' in cleaned:
            cleaned = cleaned.replace('--', '-')
        
        # Remove leading/trailing dashes
        cleaned = cleaned.strip('-')
        
        # Ensure it's not empty and not too long
        if not cleaned:
            cleaned = "team"
        
        # Keep channel names reasonable (Discord limit is 100, but keep shorter)
        if len(cleaned) > 20:
            cleaned = cleaned[:20].rstrip('-')
        
        return cleaned
    
    def process_match_data(self, raw_matches: Dict[str, Any]) -> List[ProcessedMatch]:
        """
        Normalize MCP responses into ProcessedMatch objects
        
        Args:
            raw_matches: Raw match data from MCP server
            
        Returns:
            List of ProcessedMatch objects
            
        Raises:
            MCPDataError: If match data is invalid or incomplete
        """
        if not isinstance(raw_matches, dict):
            raise MCPDataError("Raw matches data must be a dictionary")
        
        processed_matches = []
        
        try:
            # Handle different possible response structures
            matches_data = raw_matches.get('matches', [])
            if not matches_data and 'content' in raw_matches:
                # Try to extract from content field
                content = raw_matches['content']
                if isinstance(content, list) and content:
                    content_item = content[0]
                    if isinstance(content_item, dict) and 'text' in content_item:
                        import json
                        try:
                            parsed_content = json.loads(content_item['text'])
                            matches_data = parsed_content.get('matches', [])
                        except json.JSONDecodeError:
                            self.logger.warning("Could not parse JSON from content text")
            
            if not matches_data:
                self.logger.info("No matches found in response")
                return processed_matches
            
            for match_data in matches_data:
                try:
                    processed_match = self._process_single_match(match_data)
                    if processed_match:
                        processed_matches.append(processed_match)
                except Exception as e:
                    self.logger.error(f"Failed to process match: {e}")
                    continue
            
            self.logger.info(f"Successfully processed {len(processed_matches)} matches")
            return processed_matches
            
        except Exception as e:
            self.logger.error(f"Error processing match data: {e}")
            raise MCPDataError(f"Failed to process match data: {str(e)}")
    
    def _process_single_match(self, match_data: Dict[str, Any]) -> Optional[ProcessedMatch]:
        """
        Process a single match from raw data
        
        Args:
            match_data: Raw match data dictionary
            
        Returns:
            ProcessedMatch object or None if processing fails
        """
        try:
            # Extract basic match information
            match_id = match_data.get('id', 0)
            if not match_id:
                self.logger.warning("Match missing ID, skipping")
                return None
            
            # Extract teams
            home_team_data = match_data.get('home_team', {})
            away_team_data = match_data.get('away_team', {})
            
            if not home_team_data or not away_team_data:
                self.logger.warning(f"Match {match_id} missing team data")
                return None
            
            home_team = Team(
                id=home_team_data.get('id', 0),
                name=home_team_data.get('name', 'Unknown'),
                short_name=home_team_data.get('short_name', home_team_data.get('name', 'UNK')[:3]),
                logo_url=home_team_data.get('logo_url'),
                country=home_team_data.get('country')
            )
            
            away_team = Team(
                id=away_team_data.get('id', 0),
                name=away_team_data.get('name', 'Unknown'),
                short_name=away_team_data.get('short_name', away_team_data.get('name', 'UNK')[:3]),
                logo_url=away_team_data.get('logo_url'),
                country=away_team_data.get('country')
            )
            
            # Extract league information
            league_data = match_data.get('league', {})
            league = League(
                id=league_data.get('id', 0),
                name=league_data.get('name', 'Unknown League'),
                country=league_data.get('country', 'Unknown'),
                season=league_data.get('season'),
                logo_url=league_data.get('logo_url')
            )
            
            # Extract match details
            date = match_data.get('date', '')
            time = match_data.get('time', '')
            venue = match_data.get('venue', 'TBD')
            status = match_data.get('status', 'scheduled')
            
            # Process betting odds if available
            odds = None
            odds_data = match_data.get('odds', {})
            if odds_data:
                odds = self._process_betting_odds(odds_data)
            
            # Process H2H summary if available
            h2h_summary = None
            h2h_data = match_data.get('h2h_summary', {})
            if h2h_data:
                h2h_summary = self._process_h2h_summary(h2h_data)
            
            return ProcessedMatch(
                match_id=match_id,
                home_team=home_team,
                away_team=away_team,
                league=league,
                date=date,
                time=time,
                venue=venue,
                status=status,
                odds=odds,
                h2h_summary=h2h_summary
            )
            
        except Exception as e:
            self.logger.error(f"Error processing single match: {e}")
            return None
    
    def _process_betting_odds(self, odds_data: Dict[str, Any]) -> Optional[BettingOdds]:
        """
        Process betting odds from raw data
        
        Args:
            odds_data: Raw odds data dictionary
            
        Returns:
            BettingOdds object or None if processing fails
        """
        try:
            betting_odds = BettingOdds()
            
            # Process moneyline odds
            if 'home_win' in odds_data:
                home_decimal = float(odds_data['home_win'])
                betting_odds.home_win = OddsFormat.from_decimal(home_decimal)
            
            if 'draw' in odds_data:
                draw_decimal = float(odds_data['draw'])
                betting_odds.draw = OddsFormat.from_decimal(draw_decimal)
            
            if 'away_win' in odds_data:
                away_decimal = float(odds_data['away_win'])
                betting_odds.away_win = OddsFormat.from_decimal(away_decimal)
            
            # Process over/under if available
            if 'over_under' in odds_data:
                ou_data = odds_data['over_under']
                if isinstance(ou_data, dict) and 'line' in ou_data:
                    betting_odds.over_under = OverUnder(
                        line=float(ou_data['line']),
                        over_odds=OddsFormat.from_decimal(float(ou_data.get('over', 2.0))),
                        under_odds=OddsFormat.from_decimal(float(ou_data.get('under', 2.0)))
                    )
            
            # Process both teams to score if available
            if 'both_teams_score' in odds_data:
                btts_decimal = float(odds_data['both_teams_score'])
                betting_odds.both_teams_score = OddsFormat.from_decimal(btts_decimal)
            
            return betting_odds if betting_odds.has_odds else None
            
        except Exception as e:
            self.logger.error(f"Error processing betting odds: {e}")
            return None
    
    def _process_h2h_summary(self, h2h_data: Dict[str, Any]) -> Optional[H2HSummary]:
        """
        Process head-to-head summary from raw data
        
        Args:
            h2h_data: Raw H2H data dictionary
            
        Returns:
            H2HSummary object or None if processing fails
        """
        try:
            return H2HSummary(
                total_meetings=h2h_data.get('total_meetings', 0),
                home_team_wins=h2h_data.get('home_team_wins', 0),
                away_team_wins=h2h_data.get('away_team_wins', 0),
                draws=h2h_data.get('draws', 0),
                last_meeting_result=h2h_data.get('last_meeting_result')
            )
        except Exception as e:
            self.logger.error(f"Error processing H2H summary: {e}")
            return None

# ============================================================================
# SOCCER CHANNEL MANAGER
# ============================================================================

class SoccerChannelManager:
    """
    Manages soccer-specific Discord channel operations
    Handles channel creation, naming, cleanup, and organization
    """
    
    def __init__(self, bot):
        """
        Initialize the channel manager
        
        Args:
            bot: Discord bot instance
        """
        self.bot = bot
        self.category_name = "⚽ SOCCER"
        self.channel_prefix = "📊"
        self.logger = logging.getLogger(f"{__name__}.SoccerChannelManager")
        
        # Channel management settings
        self.max_channels_per_category = 50  # Discord limit
        self.cleanup_retention_days = 3
        self.channel_name_max_length = 100  # Discord limit
    
    async def get_or_create_soccer_category(self, guild) -> Optional[discord.CategoryChannel]:
        """
        Get existing soccer category or create new one
        
        Args:
            guild: Discord guild object
            
        Returns:
            CategoryChannel object or None if creation fails
        """
        try:
            # Check if category already exists
            existing_category = discord.utils.get(guild.categories, name=self.category_name)
            if existing_category:
                self.logger.info(f"Found existing soccer category: {self.category_name}")
                return existing_category
            
            # Create new category
            category = await guild.create_category(
                name=self.category_name,
                reason="Soccer match channels category"
            )
            
            self.logger.info(f"Created new soccer category: {self.category_name}")
            return category
            
        except discord.HTTPException as e:
            self.logger.error(f"Failed to create soccer category: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error creating soccer category: {e}")
            return None
    
    def generate_channel_name(self, match: ProcessedMatch, date: str) -> str:
        """
        Generate Discord channel name for a match
        Format: 📊 {date_short}-{away_team}-vs-{home_team}
        
        Args:
            match: ProcessedMatch object
            date: Date string in YYYY-MM-DD format
            
        Returns:
            Generated channel name
        """
        try:
            # Parse date and format as MM-DD
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            date_short = date_obj.strftime("%m-%d")
            
            # Clean team names for channel use
            away_clean = self._clean_team_name_for_channel(match.away_team.name)
            home_clean = self._clean_team_name_for_channel(match.home_team.name)
            
            # Generate base channel name
            channel_name = f"{self.channel_prefix} {date_short}-{away_clean}-vs-{home_clean}"
            
            # Ensure channel name doesn't exceed Discord's limit
            if len(channel_name) > self.channel_name_max_length:
                # Truncate team names proportionally
                available_length = self.channel_name_max_length - len(f"{self.channel_prefix} {date_short}--vs-")
                team_length = available_length // 2
                
                away_clean = away_clean[:team_length].rstrip('-')
                home_clean = home_clean[:team_length].rstrip('-')
                
                channel_name = f"{self.channel_prefix} {date_short}-{away_clean}-vs-{home_clean}"
            
            self.logger.debug(f"Generated channel name: {channel_name}")
            return channel_name
            
        except Exception as e:
            self.logger.error(f"Error generating channel name: {e}")
            # Fallback to basic name
            return f"{self.channel_prefix} soccer-match-{match.match_id}"
    
    def _clean_team_name_for_channel(self, team_name: str) -> str:
        """
        Clean team name for Discord channel creation
        
        Args:
            team_name: Original team name
            
        Returns:
            Cleaned team name suitable for channel names
        """
        if not team_name or not isinstance(team_name, str):
            return "team"
        
        # Convert to lowercase and replace problematic characters
        cleaned = team_name.lower().strip()
        
        # Handle accented characters
        import unicodedata
        cleaned = unicodedata.normalize('NFD', cleaned)
        cleaned = ''.join(c for c in cleaned if unicodedata.category(c) != 'Mn')
        
        # Replace spaces and special characters
        replacements = {
            ' ': '-',
            '.': '',
            '&': 'and',
            '/': '-',
            '\\': '-',
            '(': '',
            ')': '',
            '[': '',
            ']': '',
            '{': '',
            '}': '',
            '!': '',
            '?': '',
            ',': '',
            ';': '',
            ':': '',
            '"': '',
            "'": '',
            '#': '',
            '@': '',
            '\n': '',
            '\t': '',
            '%': '',
            '^': '',
            '*': '',
            '+': '',
            '=': '',
            '|': '',
            '~': '',
            '`': ''
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        # Remove multiple consecutive dashes
        while '--' in cleaned:
            cleaned = cleaned.replace('--', '-')
        
        # Remove leading/trailing dashes
        cleaned = cleaned.strip('-')
        
        # Ensure it's not empty and not too long
        if not cleaned:
            cleaned = "team"
        
        # Keep team names reasonable for channel names
        if len(cleaned) > 20:
            cleaned = cleaned[:20].rstrip('-')
        
        return cleaned
    
    async def create_match_channels(self, matches: List[ProcessedMatch], date: str, guild) -> List[discord.TextChannel]:
        """
        Create Discord channels for soccer matches following MLB channel creation logic
        
        Args:
            matches: List of ProcessedMatch objects
            date: Date string in YYYY-MM-DD format
            guild: Discord guild object
            
        Returns:
            List of created TextChannel objects
        """
        if not matches:
            self.logger.info("No matches provided for channel creation")
            return []
        
        created_channels = []
        
        try:
            # Get or create soccer category
            category = await self.get_or_create_soccer_category(guild)
            if not category:
                self.logger.error("Failed to get or create soccer category")
                return []
            
            # Check current channel count in category
            current_channels = len(category.channels)
            if current_channels >= self.max_channels_per_category:
                self.logger.warning(f"Soccer category at channel limit ({current_channels}/{self.max_channels_per_category})")
                # Trigger cleanup before creating new channels
                await self.cleanup_old_channels(guild, days_old=1)
            
            # Create channels for each match
            for match in matches:
                try:
                    channel = await self._create_single_match_channel(match, date, category)
                    if channel:
                        created_channels.append(channel)
                        self.logger.info(f"Created channel for {match.away_team.name} vs {match.home_team.name}")
                    else:
                        self.logger.warning(f"Failed to create channel for match {match.match_id}")
                        
                except Exception as e:
                    self.logger.error(f"Error creating channel for match {match.match_id}: {e}")
                    continue
            
            self.logger.info(f"Successfully created {len(created_channels)} soccer match channels")
            return created_channels
            
        except Exception as e:
            self.logger.error(f"Error in create_match_channels: {e}")
            return created_channels
    
    async def _create_single_match_channel(self, match: ProcessedMatch, date: str, category: discord.CategoryChannel) -> Optional[discord.TextChannel]:
        """
        Create a single match channel
        
        Args:
            match: ProcessedMatch object
            date: Date string in YYYY-MM-DD format
            category: Discord category to create channel in
            
        Returns:
            Created TextChannel or None if creation fails
        """
        try:
            # Generate channel name
            channel_name = self.generate_channel_name(match, date)
            
            # Check if channel already exists
            existing_channel = discord.utils.get(category.channels, name=channel_name)
            if existing_channel:
                self.logger.info(f"Channel already exists: {channel_name}")
                return existing_channel
            
            # Create channel topic
            league_name = match.league.name
            venue_info = f" at {match.venue}" if match.venue and match.venue != "TBD" else ""
            topic = f"{match.away_team.name} vs {match.home_team.name} - {league_name} - {date}{venue_info}"
            
            # Create the channel
            channel = await category.create_text_channel(
                name=channel_name,
                topic=topic,
                reason=f"Soccer match channel for {match.away_team.name} vs {match.home_team.name}"
            )
            
            self.logger.debug(f"Created channel: {channel_name} with topic: {topic}")
            return channel
            
        except discord.HTTPException as e:
            if e.status == 429:  # Rate limited
                self.logger.warning(f"Rate limited creating channel, waiting {e.retry_after}s")
                await asyncio.sleep(e.retry_after)
                return await self._create_single_match_channel(match, date, category)
            else:
                self.logger.error(f"HTTP error creating channel: {e}")
                return None
        except Exception as e:
            self.logger.error(f"Unexpected error creating channel: {e}")
            return None
    
    async def cleanup_old_channels(self, guild, days_old: int = None) -> Dict[str, int]:
        """
        Remove soccer game channels older than specified days with 3-day retention policy
        
        Args:
            guild: Discord guild object
            days_old: Number of days old for cleanup (defaults to retention policy)
            
        Returns:
            Dict with cleanup statistics
        """
        if days_old is None:
            days_old = self.cleanup_retention_days
        
        cleanup_stats = {
            "channels_deleted": 0,
            "channels_preserved": 0,
            "errors": 0
        }
        
        try:
            # Find soccer category
            soccer_category = discord.utils.get(guild.categories, name=self.category_name)
            if not soccer_category:
                self.logger.info("No soccer category found for cleanup")
                return cleanup_stats
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            self.logger.info(f"Starting cleanup of channels older than {days_old} days (before {cutoff_date})")
            
            # Get all soccer match channels
            match_channels = [ch for ch in soccer_category.channels if ch.name.startswith(self.channel_prefix)]
            
            for channel in match_channels:
                try:
                    # Check if channel should be preserved
                    if await self._should_preserve_channel(channel, cutoff_date):
                        cleanup_stats["channels_preserved"] += 1
                        continue
                    
                    # Delete the channel
                    await channel.delete(reason=f"Automated cleanup - older than {days_old} days")
                    cleanup_stats["channels_deleted"] += 1
                    self.logger.info(f"Deleted old channel: {channel.name}")
                    
                    # Add small delay to avoid rate limits
                    await asyncio.sleep(0.5)
                    
                except discord.HTTPException as e:
                    self.logger.error(f"Failed to delete channel {channel.name}: {e}")
                    cleanup_stats["errors"] += 1
                except Exception as e:
                    self.logger.error(f"Unexpected error deleting channel {channel.name}: {e}")
                    cleanup_stats["errors"] += 1
            
            self.logger.info(f"Cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            self.logger.error(f"Error in cleanup_old_channels: {e}")
            cleanup_stats["errors"] += 1
            return cleanup_stats
    
    async def _should_preserve_channel(self, channel: discord.TextChannel, cutoff_date: datetime) -> bool:
        """
        Determine if a channel should be preserved during cleanup
        
        Args:
            channel: Discord text channel
            cutoff_date: Cutoff date for cleanup
            
        Returns:
            True if channel should be preserved, False otherwise
        """
        try:
            # Always preserve if channel is newer than cutoff
            if channel.created_at > cutoff_date:
                return True
            
            # Check for recent activity
            try:
                async for message in channel.history(limit=1, after=cutoff_date):
                    self.logger.debug(f"Preserving {channel.name} due to recent activity")
                    return True
            except discord.HTTPException:
                # If we can't check history, err on the side of caution
                pass
            
            # Check for pinned messages
            try:
                pinned_messages = await channel.pins()
                if pinned_messages:
                    self.logger.debug(f"Preserving {channel.name} due to pinned messages")
                    return True
            except discord.HTTPException:
                pass
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking if channel should be preserved: {e}")
            # Err on the side of caution
            return True
    
    async def update_channel_content(self, channel: discord.TextChannel, match_data: ProcessedMatch) -> bool:
        """
        Update channel content with match information
        
        Args:
            channel: Discord text channel
            match_data: ProcessedMatch object with updated information
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            # This method can be used for future live updates
            # For now, it's a placeholder for the channel management system
            self.logger.info(f"Channel content update requested for {channel.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating channel content: {e}")
            return Falseata
        
        Args:
            h2h_data: Raw H2H data dictionary
            
        Returns:
            H2HSummary object or None if processing fails
        """
        try:
            return H2HSummary(
                total_meetings=int(h2h_data.get('total_meetings', 0)),
                home_team_wins=int(h2h_data.get('home_team_wins', 0)),
                away_team_wins=int(h2h_data.get('away_team_wins', 0)),
                draws=int(h2h_data.get('draws', 0)),
                last_meeting_result=h2h_data.get('last_meeting_result')
            )
        except Exception as e:
            self.logger.error(f"Error processing H2H summary: {e}")
            return None
    
    def validate_date_format(self, date_string: str) -> str:
        """
        Validate and normalize date input supporting MM/DD/YYYY, DD-MM-YYYY, and YYYY-MM-DD formats
        
        Args:
            date_string: Date string in various formats
            
        Returns:
            Normalized date string in YYYY-MM-DD format
            
        Raises:
            ValueError: If date format is invalid or date is out of range
        """
        if not date_string or not isinstance(date_string, str):
            raise ValueError("Date string cannot be empty")
        
        date_string = date_string.strip()
        allowed_formats = [
            "%m/%d/%Y",    # MM/DD/YYYY
            "%d-%m-%Y",    # DD-MM-YYYY  
            "%Y-%m-%d"     # YYYY-MM-DD
        ]
        
        parsed_date = None
        
        # Try to parse the date with any of the allowed formats
        for fmt in allowed_formats:
            try:
                parsed_date = datetime.strptime(date_string, fmt)
                break
            except ValueError:
                continue
        
        # If no format worked, raise format error
        if parsed_date is None:
            raise ValueError(
                f"Invalid date format '{date_string}'. "
                f"Use MM/DD/YYYY, DD-MM-YYYY, or YYYY-MM-DD"
            )
        
        # Validate the date range (30 days past to 1 year future)
        now = datetime.now()
        min_date = now - timedelta(days=30)
        max_date = now + timedelta(days=365)
        
        if not (min_date <= parsed_date <= max_date):
            raise ValueError(
                f"Date must be within 30 days past to 1 year future. "
                f"Provided date: {parsed_date.strftime('%Y-%m-%d')}"
            )
        
        return parsed_date.strftime("%Y-%m-%d")
    
    def extract_betting_insights(self, odds: BettingOdds, h2h_data: Optional[H2HInsights] = None) -> List[str]:
        """
        Generate betting insights based on odds and historical data
        
        Args:
            odds: Betting odds for the match
            h2h_data: Optional head-to-head insights
            
        Returns:
            List of betting insight strings
        """
        insights = []
        
        if not odds or not odds.has_odds:
            return ["No betting odds available"]
        
        try:
            # Analyze moneyline odds
            if odds.home_win and odds.away_win and odds.draw:
                home_prob = 1 / odds.home_win.decimal * 100
                away_prob = 1 / odds.away_win.decimal * 100
                draw_prob = 1 / odds.draw.decimal * 100
                
                if home_prob > away_prob and home_prob > draw_prob:
                    insights.append(f"Home team favored ({home_prob:.1f}% implied probability)")
                elif away_prob > home_prob and away_prob > draw_prob:
                    insights.append(f"Away team favored ({away_prob:.1f}% implied probability)")
                else:
                    insights.append(f"Draw most likely ({draw_prob:.1f}% implied probability)")
            
            # Analyze over/under if available
            if odds.over_under:
                line = odds.over_under.line
                insights.append(f"Total goals line set at {line}")
                
                if h2h_data and h2h_data.avg_goals_per_game > 0:
                    if h2h_data.avg_goals_per_game > line:
                        insights.append("Historical average suggests Over")
                    else:
                        insights.append("Historical average suggests Under")
            
            # Add H2H insights if available
            if h2h_data and h2h_data.total_meetings > 0:
                if h2h_data.draw_percentage > 30:
                    insights.append(f"High draw rate in H2H ({h2h_data.draw_percentage:.1f}%)")
                
                if h2h_data.home_win_percentage >= 60:
                    insights.append("Home team dominates this matchup historically")
                elif h2h_data.away_win_percentage >= 60:
                    insights.append("Away team dominates this matchup historically")
            
        except Exception as e:
            self.logger.error(f"Error generating betting insights: {e}")
            insights.append("Unable to generate betting insights")
        
        return insights if insights else ["No specific insights available"]

# ============================================================================
# SOCCER EMBED BUILDER  
# ============================================================================

class SoccerEmbedBuilder:
    """
    Creates rich Discord embeds for soccer content with league-specific styling
    Handles match previews, betting odds, H2H analysis, and league standings
    """
    
    def __init__(self):
        """Initialize the embed builder with league-specific color schemes"""
        self.colors = {
            "EPL": 0x3d195b,      # Premier League purple
            "La Liga": 0xff6900,   # La Liga orange
            "MLS": 0x005da6,       # MLS blue
            "Bundesliga": 0xd20515, # Bundesliga red
            "Serie A": 0x0066cc,   # Serie A blue
            "UEFA": 0x00336a,      # UEFA dark blue
            "default": 0x00ff00    # Default green for unknown leagues
        }
        
        self.emojis = {
            "EPL": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            "La Liga": "🇪🇸",
            "MLS": "🇺🇸",
            "Bundesliga": "🇩🇪",
            "Serie A": "🇮🇹",
            "UEFA": "🏆",
            "default": "⚽"
        }
        
        self.logger = logging.getLogger(f"{__name__}.SoccerEmbedBuilder")
    
    def _get_league_color(self, league: League) -> int:
        """
        Get color for a specific league
        
        Args:
            league: League object
            
        Returns:
            Color integer for the league
        """
        league_config = league.config
        if league_config:
            return league_config.get("color", self.colors["default"])
        
        # Fallback to name-based lookup
        for league_name, color in self.colors.items():
            if league_name.lower() in league.name.lower():
                return color
        
        return self.colors["default"]
    
    def _get_league_emoji(self, league: League) -> str:
        """
        Get emoji for a specific league
        
        Args:
            league: League object
            
        Returns:
            Emoji string for the league
        """
        league_config = league.config
        if league_config:
            return league_config.get("emoji", self.emojis["default"])
        
        # Fallback to name-based lookup
        for league_name, emoji in self.emojis.items():
            if league_name.lower() in league.name.lower():
                return emoji
        
        return self.emojis["default"]
    
    def _format_odds(self, odds_format: OddsFormat) -> str:
        """
        Format odds for display in both decimal and American formats
        
        Args:
            odds_format: OddsFormat object
            
        Returns:
            Formatted odds string
        """
        american_str = f"+{odds_format.american}" if odds_format.american > 0 else str(odds_format.american)
        return f"{odds_format.decimal:.2f} ({american_str})"
    
    def _safe_get_field_value(self, value: Any, default: str = "N/A") -> str:
        """
        Safely get field value with fallback for missing data
        
        Args:
            value: Value to check
            default: Default value if original is None/empty
            
        Returns:
            String representation of value or default
        """
        if value is None or value == "":
            return default
        return str(value)
    
    def create_match_preview_embed(self, match: ProcessedMatch) -> discord.Embed:
        """
        Create match preview embed with team info, odds, venue, and time
        
        Args:
            match: ProcessedMatch object
            
        Returns:
            Discord embed with match preview information
        """
        try:
            # Get league-specific styling
            color = self._get_league_color(match.league)
            league_emoji = self._get_league_emoji(match.league)
            
            # Create embed with title
            title = f"{league_emoji} {match.away_team.name} vs {match.home_team.name}"
            embed = discord.Embed(
                title=title,
                color=color,
                timestamp=datetime.now()
            )
            
            # Add league and competition info
            league_info = f"{match.league.name}"
            if match.league.country and match.league.country != "Unknown":
                league_info += f" ({match.league.country})"
            embed.add_field(name="🏆 Competition", value=league_info, inline=True)
            
            # Add match details
            match_date = self._safe_get_field_value(match.date, "TBD")
            match_time = self._safe_get_field_value(match.display_time, "TBD")
            embed.add_field(name="📅 Date", value=match_date, inline=True)
            embed.add_field(name="⏰ Time", value=match_time, inline=True)
            
            # Add venue information
            venue = self._safe_get_field_value(match.venue, "TBD")
            embed.add_field(name="🏟️ Venue", value=venue, inline=False)
            
            # Add team information
            away_info = f"**{match.away_team.name}**"
            if match.away_team.short_name != match.away_team.name:
                away_info += f" ({match.away_team.short_name})"
            if match.away_team.country:
                away_info += f"\n🌍 {match.away_team.country}"
            
            home_info = f"**{match.home_team.name}**"
            if match.home_team.short_name != match.home_team.name:
                home_info += f" ({match.home_team.short_name})"
            if match.home_team.country:
                home_info += f"\n🌍 {match.home_team.country}"
            
            embed.add_field(name="✈️ Away Team", value=away_info, inline=True)
            embed.add_field(name="🏠 Home Team", value=home_info, inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)  # Spacer
            
            # Add betting odds if available
            if match.odds and match.odds.has_odds:
                odds_text = self._create_odds_summary(match.odds)
                embed.add_field(name="💰 Betting Odds", value=odds_text, inline=False)
            
            # Add H2H summary if available
            if match.h2h_summary and match.h2h_summary.total_meetings > 0:
                h2h_text = self._create_h2h_summary_text(match.h2h_summary)
                embed.add_field(name="📊 Head-to-Head", value=h2h_text, inline=False)
            
            # Add match status
            status_emoji = "🟢" if match.status == "scheduled" else "🔴"
            embed.add_field(name="📋 Status", value=f"{status_emoji} {match.status.title()}", inline=True)
            
            # Set footer
            embed.set_footer(text=f"Match ID: {match.match_id} | Soccer Bot")
            
            return embed
            
        except Exception as e:
            self.logger.error(f"Error creating match preview embed: {e}")
            return self._create_error_embed("Failed to create match preview", str(e))
    
    def create_betting_odds_embed(self, match: ProcessedMatch) -> discord.Embed:
        """
        Create betting odds embed displaying moneyline, draw, and over/under in both formats
        
        Args:
            match: ProcessedMatch object with betting odds
            
        Returns:
            Discord embed with detailed betting odds
        """
        try:
            if not match.odds or not match.odds.has_odds:
                return self._create_error_embed("No Betting Odds", "No betting odds available for this match")
            
            # Get league-specific styling
            color = self._get_league_color(match.league)
            league_emoji = self._get_league_emoji(match.league)
            
            # Create embed
            title = f"{league_emoji} Betting Odds: {match.away_team.name} vs {match.home_team.name}"
            embed = discord.Embed(
                title=title,
                color=color,
                timestamp=datetime.now()
            )
            
            # Add match info
            embed.add_field(
                name="⚽ Match",
                value=f"{match.league.name}\n{match.date} at {match.display_time}",
                inline=False
            )
            
            # Add moneyline odds
            if match.odds.home_win and match.odds.away_win and match.odds.draw:
                moneyline_text = (
                    f"🏠 **{match.home_team.name} Win**: {self._format_odds(match.odds.home_win)}\n"
                    f"🤝 **Draw**: {self._format_odds(match.odds.draw)}\n"
                    f"✈️ **{match.away_team.name} Win**: {self._format_odds(match.odds.away_win)}"
                )
                embed.add_field(name="💰 Moneyline (1X2)", value=moneyline_text, inline=False)
            
            # Add over/under if available
            if match.odds.over_under:
                ou = match.odds.over_under
                ou_text = (
                    f"📈 **Over {ou.line}**: {self._format_odds(ou.over_odds)}\n"
                    f"📉 **Under {ou.line}**: {self._format_odds(ou.under_odds)}"
                )
                embed.add_field(name="🎯 Total Goals", value=ou_text, inline=True)
            
            # Add both teams to score if available
            if match.odds.both_teams_score:
                btts_text = f"⚽ **Both Teams Score**: {self._format_odds(match.odds.both_teams_score)}"
                embed.add_field(name="🥅 BTTS", value=btts_text, inline=True)
            
            # Add handicap if available
            if match.odds.handicap:
                handicap = match.odds.handicap
                handicap_text = (
                    f"🏠 **{match.home_team.name} ({handicap.line:+.1f})**: {self._format_odds(handicap.home_odds)}\n"
                    f"✈️ **{match.away_team.name} ({-handicap.line:+.1f})**: {self._format_odds(handicap.away_odds)}"
                )
                embed.add_field(name="⚖️ Handicap", value=handicap_text, inline=False)
            
            # Add betting insights if available
            processor = SoccerDataProcessor()
            insights = processor.extract_betting_insights(match.odds)
            if insights and insights != ["No specific insights available"]:
                insights_text = "\n".join([f"• {insight}" for insight in insights[:3]])  # Limit to 3 insights
                embed.add_field(name="💡 Betting Insights", value=insights_text, inline=False)
            
            # Add disclaimer
            embed.add_field(
                name="⚠️ Disclaimer",
                value="Odds are for informational purposes only. Please gamble responsibly.",
                inline=False
            )
            
            embed.set_footer(text=f"Match ID: {match.match_id} | Odds subject to change")
            
            return embed
            
        except Exception as e:
            self.logger.error(f"Error creating betting odds embed: {e}")
            return self._create_error_embed("Betting Odds Error", str(e))
    
    def create_h2h_analysis_embed(self, h2h_data: H2HInsights, team1: Team, team2: Team, league: League) -> discord.Embed:
        """
        Create head-to-head analysis embed with historical records and recent form
        
        Args:
            h2h_data: H2HInsights object with comprehensive analysis
            team1: First team (typically away team)
            team2: Second team (typically home team)
            league: League object for styling
            
        Returns:
            Discord embed with H2H analysis
        """
        try:
            if not h2h_data or h2h_data.total_meetings == 0:
                return self._create_error_embed("No H2H Data", "No head-to-head data available for these teams")
            
            # Get league-specific styling
            color = self._get_league_color(league)
            league_emoji = self._get_league_emoji(league)
            
            # Create embed
            title = f"{league_emoji} Head-to-Head: {team1.name} vs {team2.name}"
            embed = discord.Embed(
                title=title,
                color=color,
                timestamp=datetime.now()
            )
            
            # Add overall record
            record_text = (
                f"📊 **Total Meetings**: {h2h_data.total_meetings}\n"
                f"✈️ **{team1.name} Wins**: {h2h_data.away_team_wins} ({h2h_data.away_win_percentage:.1f}%)\n"
                f"🤝 **Draws**: {h2h_data.draws} ({h2h_data.draw_percentage:.1f}%)\n"
                f"🏠 **{team2.name} Wins**: {h2h_data.home_team_wins} ({h2h_data.home_win_percentage:.1f}%)"
            )
            embed.add_field(name="📈 Overall Record", value=record_text, inline=False)
            
            # Add average goals
            if h2h_data.avg_goals_per_game > 0:
                goals_text = f"⚽ **Average Goals per Game**: {h2h_data.avg_goals_per_game:.2f}"
                embed.add_field(name="🎯 Scoring Stats", value=goals_text, inline=True)
            
            # Add recent form if available
            if h2h_data.recent_form:
                form_text = ""
                for team_name, form_list in h2h_data.recent_form.items():
                    if form_list:
                        form_display = " ".join(form_list[:5])  # Show last 5 matches
                        form_text += f"**{team_name}**: {form_display}\n"
                
                if form_text:
                    embed.add_field(name="📋 Recent Form (W-D-L)", value=form_text.strip(), inline=True)
            
            # Add key statistics if available
            if h2h_data.key_statistics:
                stats_text = ""
                for stat_name, stat_value in h2h_data.key_statistics.items():
                    if isinstance(stat_value, (int, float)):
                        stats_text += f"• **{stat_name}**: {stat_value}\n"
                    else:
                        stats_text += f"• **{stat_name}**: {stat_value}\n"
                
                if stats_text:
                    embed.add_field(name="📊 Key Statistics", value=stats_text[:1024], inline=False)
            
            # Add betting recommendations if available
            if h2h_data.betting_recommendations:
                recommendations_text = "\n".join([f"💡 {rec}" for rec in h2h_data.betting_recommendations[:3]])
                embed.add_field(name="🎲 Betting Insights", value=recommendations_text, inline=False)
            
            # Add trend analysis
            if h2h_data.home_win_percentage >= 60:
                trend = f"🏠 {team2.name} dominates this matchup"
            elif h2h_data.away_win_percentage >= 60:
                trend = f"✈️ {team1.name} dominates this matchup"
            elif h2h_data.draw_percentage >= 40:
                trend = "🤝 High tendency for draws"
            else:
                trend = "⚖️ Evenly matched historically"
            
            embed.add_field(name="📈 Historical Trend", value=trend, inline=False)
            
            embed.set_footer(text="H2H Analysis | Data may not include all competitions")
            
            return embed
            
        except Exception as e:
            self.logger.error(f"Error creating H2H analysis embed: {e}")
            return self._create_error_embed("H2H Analysis Error", str(e))
    
    def create_league_standings_embed(self, standings_data: Dict[str, Any], league: League) -> discord.Embed:
        """
        Create league standings embed for current table positions
        
        Args:
            standings_data: Dictionary containing league standings data
            league: League object for styling
            
        Returns:
            Discord embed with league standings
        """
        try:
            if not standings_data or 'standings' not in standings_data:
                return self._create_error_embed("No Standings Data", "No league standings data available")
            
            # Get league-specific styling
            color = self._get_league_color(league)
            league_emoji = self._get_league_emoji(league)
            
            # Create embed
            title = f"{league_emoji} {league.name} Standings"
            embed = discord.Embed(
                title=title,
                color=color,
                timestamp=datetime.now()
            )
            
            # Add league info
            if league.season:
                embed.add_field(name="🏆 Season", value=league.season, inline=True)
            if league.country:
                embed.add_field(name="🌍 Country", value=league.country, inline=True)
            
            # Process standings data
            standings = standings_data['standings']
            if not isinstance(standings, list):
                return self._create_error_embed("Invalid Data", "Standings data format is invalid")
            
            # Create standings table (top 10 teams to fit in embed)
            standings_text = "```\nPos Team                 P  W  D  L  GF GA GD Pts\n"
            standings_text += "─" * 50 + "\n"
            
            for i, team_data in enumerate(standings[:10]):  # Limit to top 10
                try:
                    pos = team_data.get('position', i + 1)
                    team_name = team_data.get('team', {}).get('name', 'Unknown')[:15]  # Truncate long names
                    played = team_data.get('played', 0)
                    wins = team_data.get('wins', 0)
                    draws = team_data.get('draws', 0)
                    losses = team_data.get('losses', 0)
                    goals_for = team_data.get('goals_for', 0)
                    goals_against = team_data.get('goals_against', 0)
                    goal_diff = goals_for - goals_against
                    points = team_data.get('points', 0)
                    
                    # Format the line
                    standings_text += f"{pos:2d}. {team_name:<15} {played:2d} {wins:2d} {draws:2d} {losses:2d} {goals_for:2d} {goals_against:2d} {goal_diff:+3d} {points:3d}\n"
                    
                except Exception as e:
                    self.logger.error(f"Error processing team standings data: {e}")
                    continue
            
            standings_text += "```"
            
            # Add standings table to embed
            embed.add_field(name="📊 League Table", value=standings_text, inline=False)
            
            # Add additional info if available
            if len(standings) > 10:
                embed.add_field(
                    name="ℹ️ Note",
                    value=f"Showing top 10 of {len(standings)} teams",
                    inline=False
                )
            
            # Add legend
            legend_text = (
                "**P** = Played, **W** = Wins, **D** = Draws, **L** = Losses\n"
                "**GF** = Goals For, **GA** = Goals Against, **GD** = Goal Difference"
            )
            embed.add_field(name="📝 Legend", value=legend_text, inline=False)
            
            embed.set_footer(text=f"{league.name} | Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            return embed
            
        except Exception as e:
            self.logger.error(f"Error creating league standings embed: {e}")
            return self._create_error_embed("Standings Error", str(e))
    
    def _create_odds_summary(self, odds: BettingOdds) -> str:
        """
        Create a summary of betting odds for match preview
        
        Args:
            odds: BettingOdds object
            
        Returns:
            Formatted odds summary string
        """
        summary_parts = []
        
        if odds.home_win and odds.away_win and odds.draw:
            summary_parts.append(f"1X2: {odds.home_win.decimal:.2f} / {odds.draw.decimal:.2f} / {odds.away_win.decimal:.2f}")
        
        if odds.over_under:
            summary_parts.append(f"O/U {odds.over_under.line}: {odds.over_under.over_odds.decimal:.2f} / {odds.over_under.under_odds.decimal:.2f}")
        
        if odds.both_teams_score:
            summary_parts.append(f"BTTS: {odds.both_teams_score.decimal:.2f}")
        
        return "\n".join(summary_parts) if summary_parts else "Limited odds available"
    
    def _create_h2h_summary_text(self, h2h_summary: H2HSummary) -> str:
        """
        Create a brief H2H summary for match preview
        
        Args:
            h2h_summary: H2HSummary object
            
        Returns:
            Formatted H2H summary string
        """
        if h2h_summary.total_meetings == 0:
            return "No previous meetings"
        
        summary = f"Last {h2h_summary.total_meetings} meetings: "
        summary += f"{h2h_summary.home_team_wins}W-{h2h_summary.draws}D-{h2h_summary.away_team_wins}L"
        
        if h2h_summary.last_meeting_result:
            summary += f"\nLast result: {h2h_summary.last_meeting_result}"
        
        return summary
    
    def _create_error_embed(self, title: str, description: str) -> discord.Embed:
        """
        Create an error embed with graceful degradation
        
        Args:
            title: Error title
            description: Error description
            
        Returns:
            Discord embed with error information
        """
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=0xff0000,  # Red color for errors
            timestamp=datetime.now()
        )
        
        embed.set_footer(text="Soccer Bot | Error occurred")
        return embed

# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

# Configure module-level logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Export main classes and functions
__all__ = [
    'SoccerMCPClient',
    'SoccerDataProcessor',
    'SoccerChannelManager',
    'SoccerEmbedBuilder',
    'ProcessedMatch',
    'BettingOdds', 
    'H2HInsights',
    'H2HSummary',
    'Team',
    'League',
    'OddsFormat',
    'OverUnder',
    'Handicap',
    'SoccerMCPError',
    'MCPConnectionError',
    'MCPDataError',
    'MCPTimeoutError',
    'SUPPORTED_LEAGUES',
    'validate_date_format',
    'get_league_config',
    'clean_team_name_for_channel'
]c
lass SoccerEmbedBuilder:
    """Creates rich Discord embeds for soccer content with league-specific styling"""
    
    def __init__(self):
        """Initialize the embed builder with league-specific color schemes"""
        self.colors = {
            "EPL": 0x3d195b,      # Premier League purple
            "La Liga": 0xff6900,   # La Liga orange
            "MLS": 0x005da6,       # MLS blue
            "Bundesliga": 0xd20515, # Bundesliga red
            "Serie A": 0x0066cc,   # Serie A blue
            "UEFA": 0x00336a,      # UEFA dark blue
            "default": 0x00ff00    # Default green for unknown leagues
        }
        
        self.emojis = {
            "EPL": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            "La Liga": "🇪🇸",
            "MLS": "🇺🇸",
            "Bundesliga": "🇩🇪",
            "Serie A": "🇮🇹",
            "UEFA": "🏆",
            "default": "⚽"
        }
        
        self.logger = logging.getLogger(f"{__name__}.SoccerEmbedBuilder")
    
    def _get_league_color(self, league: League) -> int:
        """Get color for a specific league"""
        league_config = league.config
        if league_config:
            return league_config.get("color", self.colors["default"])
        
        # Fallback to name-based lookup
        for league_name, color in self.colors.items():
            if league_name.lower() in league.name.lower():
                return color
        
        return self.colors["default"]
    
    def _get_league_emoji(self, league: League) -> str:
        """Get emoji for a specific league"""
        league_config = league.config
        if league_config:
            return league_config.get("emoji", self.emojis["default"])
        
        # Fallback to name-based lookup
        for league_name, emoji in self.emojis.items():
            if league_name.lower() in league.name.lower():
                return emoji
        
        return self.emojis["default"]
    
    def _format_odds(self, odds_format: OddsFormat) -> str:
        """Format odds for display in both decimal and American formats"""
        american_str = f"+{odds_format.american}" if odds_format.american > 0 else str(odds_format.american)
        return f"{odds_format.decimal:.2f} ({american_str})"
    
    def _safe_get_field_value(self, value: Any, default: str = "TBD") -> str:
        """Safely get field value with fallback for missing data"""
        if value is None or value == "":
            return default
        return str(value)
    
    def create_match_preview_embed(self, match: ProcessedMatch) -> discord.Embed:
        """Create match preview embed with team info, odds, venue, and time"""
        try:
            # Get league-specific styling
            color = self._get_league_color(match.league)
            league_emoji = self._get_league_emoji(match.league)
            
            # Create embed with title
            title = f"{league_emoji} {match.away_team.name} vs {match.home_team.name}"
            embed = discord.Embed(
                title=title,
                color=color,
                timestamp=datetime.now()
            )
            
            # Add basic match information
            embed.add_field(name="🏆 Competition", value=match.league.name, inline=True)
            embed.add_field(name="📅 Date", value=self._safe_get_field_value(match.date), inline=True)
            embed.add_field(name="⏰ Time", value=self._safe_get_field_value(match.display_time), inline=True)
            embed.add_field(name="🏟️ Venue", value=self._safe_get_field_value(match.venue), inline=False)
            
            # Set footer
            embed.set_footer(text=f"Match ID: {match.match_id} | Soccer Bot")
            
            return embed
            
        except Exception as e:
            self.logger.error(f"Error creating match preview embed: {e}")
            return self._create_error_embed("Failed to create match preview", str(e))
    
    def create_betting_odds_embed(self, match: ProcessedMatch) -> discord.Embed:
        """Create betting odds embed displaying moneyline, draw, and over/under in both formats"""
        try:
            if not match.odds or not match.odds.has_odds:
                return self._create_error_embed("No Betting Odds", "No betting odds available for this match")
            
            # Get league-specific styling
            color = self._get_league_color(match.league)
            league_emoji = self._get_league_emoji(match.league)
            
            # Create embed
            title = f"{league_emoji} Betting Odds: {match.away_team.name} vs {match.home_team.name}"
            embed = discord.Embed(
                title=title,
                color=color,
                timestamp=datetime.now()
            )
            
            # Add moneyline odds
            if match.odds.home_win and match.odds.away_win and match.odds.draw:
                moneyline_text = (
                    f"🏠 **{match.home_team.name} Win**: {self._format_odds(match.odds.home_win)}\n"
                    f"🤝 **Draw**: {self._format_odds(match.odds.draw)}\n"
                    f"✈️ **{match.away_team.name} Win**: {self._format_odds(match.odds.away_win)}"
                )
                embed.add_field(name="💰 Moneyline (1X2)", value=moneyline_text, inline=False)
            
            embed.set_footer(text=f"Match ID: {match.match_id} | Odds subject to change")
            
            return embed
            
        except Exception as e:
            self.logger.error(f"Error creating betting odds embed: {e}")
            return self._create_error_embed("Betting Odds Error", str(e))
    
    def create_h2h_analysis_embed(self, h2h_data: H2HInsights, team1: Team, team2: Team, league: League) -> discord.Embed:
        """Create head-to-head analysis embed with historical records and recent form"""
        try:
            if not h2h_data or h2h_data.total_meetings == 0:
                return self._create_error_embed("No H2H Data", "No head-to-head data available for these teams")
            
            # Get league-specific styling
            color = self._get_league_color(league)
            league_emoji = self._get_league_emoji(league)
            
            # Create embed
            title = f"{league_emoji} Head-to-Head: {team1.name} vs {team2.name}"
            embed = discord.Embed(
                title=title,
                color=color,
                timestamp=datetime.now()
            )
            
            # Add overall record
            record_text = (
                f"📊 **Total Meetings**: {h2h_data.total_meetings}\n"
                f"✈️ **{team1.name} Wins**: {h2h_data.away_team_wins} ({h2h_data.away_win_percentage:.1f}%)\n"
                f"🤝 **Draws**: {h2h_data.draws} ({h2h_data.draw_percentage:.1f}%)\n"
                f"🏠 **{team2.name} Wins**: {h2h_data.home_team_wins} ({h2h_data.home_win_percentage:.1f}%)"
            )
            embed.add_field(name="📈 Overall Record", value=record_text, inline=False)
            
            embed.set_footer(text="H2H Analysis | Data may not include all competitions")
            
            return embed
            
        except Exception as e:
            self.logger.error(f"Error creating H2H analysis embed: {e}")
            return self._create_error_embed("H2H Analysis Error", str(e))
    
    def create_league_standings_embed(self, standings_data: Dict[str, Any], league: League) -> discord.Embed:
        """Create league standings embed for current table positions"""
        try:
            if not standings_data or 'standings' not in standings_data:
                return self._create_error_embed("No Standings Data", "No league standings data available")
            
            # Get league-specific styling
            color = self._get_league_color(league)
            league_emoji = self._get_league_emoji(league)
            
            # Create embed
            title = f"{league_emoji} {league.name} Standings"
            embed = discord.Embed(
                title=title,
                color=color,
                timestamp=datetime.now()
            )
            
            # Add basic standings info
            standings = standings_data['standings']
            if isinstance(standings, list) and standings:
                standings_text = f"Top teams in {league.name}"
                embed.add_field(name="📊 League Table", value=standings_text, inline=False)
            
            embed.set_footer(text=f"{league.name} | Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            return embed
            
        except Exception as e:
            self.logger.error(f"Error creating league standings embed: {e}")
            return self._create_error_embed("Standings Error", str(e))
    
    def _create_error_embed(self, title: str, description: str) -> discord.Embed:
        """Create an error embed with graceful degradation"""
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=0xff0000,  # Red color for errors
            timestamp=datetime.now()
        )
        
        embed.set_footer(text="Soccer Bot | Error occurred")
        return embed

# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

# Configure module-level logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Export main classes and functions
__all__ = [
    'SoccerMCPClient',
    'SoccerDataProcessor',
    'SoccerChannelManager',
    'SoccerEmbedBuilder',
    'ProcessedMatch',
    'BettingOdds', 
    'H2HInsights',
    'H2HSummary',
    'Team',
    'League',
    'OddsFormat',
    'OverUnder',
    'Handicap',
    'SoccerMCPError',
    'MCPConnectionError',
    'MCPDataError',
    'MCPTimeoutError',
    'SUPPORTED_LEAGUES',
    'validate_date_format',
    'get_league_config',
    'clean_team_name_for_channel'
]