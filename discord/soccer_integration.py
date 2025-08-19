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

# Supported Soccer Leagues Configuration with Enhanced Multi-League Support
SUPPORTED_LEAGUES = {
    "EPL": {
        "id": 228,
        "name": "Premier League",
        "country": "England",
        "color": 0x3d195b,  # Premier League purple
        "emoji": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        "priority": 1,  # Highest priority for channel organization
        "tournament_type": "league",
        "season_format": "2024-25",
        "standings_available": True
    },
    "La Liga": {
        "id": 297,
        "name": "La Liga",
        "country": "Spain", 
        "color": 0xff6900,  # La Liga orange
        "emoji": "🇪🇸",
        "priority": 2,
        "tournament_type": "league",
        "season_format": "2024-25",
        "standings_available": True
    },
    "MLS": {
        "id": 168,
        "name": "MLS",
        "country": "USA",
        "color": 0x005da6,  # MLS blue
        "emoji": "🇺🇸",
        "priority": 5,  # Lower priority due to different season
        "tournament_type": "league",
        "season_format": "2025",
        "standings_available": True
    },
    "Bundesliga": {
        "id": 241,
        "name": "Bundesliga",
        "country": "Germany",
        "color": 0xd20515,  # Bundesliga red
        "emoji": "🇩🇪",
        "priority": 3,
        "tournament_type": "league",
        "season_format": "2024-25",
        "standings_available": True
    },
    "Serie A": {
        "id": 253,
        "name": "Serie A",
        "country": "Italy",
        "color": 0x0066cc,  # Serie A blue
        "emoji": "🇮🇹",
        "priority": 4,
        "tournament_type": "league",
        "season_format": "2024-25",
        "standings_available": True
    },
    "UEFA": {
        "id": 310,
        "name": "UEFA Champions League",
        "country": "Europe",
        "color": 0x00336a,  # UEFA dark blue
        "emoji": "🏆",
        "priority": 0,  # Highest priority for tournament matches
        "tournament_type": "knockout",
        "season_format": "2024-25",
        "standings_available": False,
        "stages": {
            "group": "Group Stage",
            "round_16": "Round of 16",
            "quarter": "Quarter Finals",
            "semi": "Semi Finals",
            "final": "Final"
        }
    }
}

# League Priority Order for Channel Organization
LEAGUE_PRIORITY_ORDER = [
    "UEFA",      # Champions League gets top priority
    "EPL",       # Premier League
    "La Liga",   # La Liga
    "Bundesliga", # Bundesliga
    "Serie A",   # Serie A
    "MLS"        # MLS (different season timing)
]

# Tournament Stage Mappings for UEFA Champions League
UEFA_STAGE_MAPPINGS = {
    "group_stage": {"name": "Group Stage", "emoji": "🔵", "priority": 1},
    "round_of_16": {"name": "Round of 16", "emoji": "🟡", "priority": 2},
    "quarter_finals": {"name": "Quarter Finals", "emoji": "🟠", "priority": 3},
    "semi_finals": {"name": "Semi Finals", "emoji": "🔴", "priority": 4},
    "final": {"name": "Final", "emoji": "🏆", "priority": 5}
}

# MCP Tools Available
AVAILABLE_MCP_TOOLS = [
    "get_betting_matches",
    "analyze_match_betting",
    "get_team_form_analysis",
    "get_h2h_betting_analysis",
    "get_league_value_bets"
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
class TeamStanding:
    """Team standings information for league context"""
    position: int
    points: int
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    form: Optional[List[str]] = None  # Recent form: ["W", "L", "D", "W", "W"]
    
    @property
    def points_per_game(self) -> float:
        """Calculate points per game"""
        return self.points / self.played if self.played > 0 else 0.0
    
    @property
    def win_percentage(self) -> float:
        """Calculate win percentage"""
        return (self.won / self.played * 100) if self.played > 0 else 0.0

@dataclass
class Team:
    """Enhanced soccer team information with standings context"""
    id: int
    name: str
    short_name: str
    logo_url: Optional[str] = None
    country: Optional[str] = None
    standing: Optional[TeamStanding] = None  # League standing information
    
    @property
    def clean_name(self) -> str:
        """Get cleaned team name for channel creation"""
        return self.name.lower().replace(' ', '-').replace('.', '').replace('&', 'and')
    
    @property
    def display_name_with_position(self) -> str:
        """Get team name with league position if available"""
        if self.standing and self.standing.position:
            return f"{self.name} ({self.standing.position})"
        return self.name
    
    @property
    def form_display(self) -> str:
        """Get recent form as display string"""
        if self.standing and self.standing.form:
            return "".join(self.standing.form[-5:])  # Last 5 matches
        return "N/A"

@dataclass
class League:
    """Enhanced soccer league information with multi-league support"""
    id: int
    name: str
    country: str
    season: Optional[str] = None
    logo_url: Optional[str] = None
    priority: int = 999  # Default low priority
    tournament_type: str = "league"  # "league" or "knockout"
    stage: Optional[str] = None  # For tournament stages (UEFA)
    stage_name: Optional[str] = None
    standings_position: Optional[int] = None  # Team's position in league
    points: Optional[int] = None  # Team's points in league
    goal_difference: Optional[int] = None  # Team's goal difference
    
    @property
    def config(self) -> Optional[Dict]:
        """Get league configuration from SUPPORTED_LEAGUES"""
        for key, config in SUPPORTED_LEAGUES.items():
            if config["id"] == self.id:
                return {**config, "code": key}
        return None
    
    @property
    def is_tournament(self) -> bool:
        """Check if this is a tournament (knockout) competition"""
        return self.tournament_type == "knockout"
    
    @property
    def display_name(self) -> str:
        """Get display name with stage information for tournaments"""
        if self.is_tournament and self.stage_name:
            return f"{self.name} - {self.stage_name}"
        return self.name
    
    @property
    def emoji(self) -> str:
        """Get league emoji from configuration"""
        config = self.config
        if config:
            return config.get("emoji", "⚽")
        return "⚽"
    
    @property
    def color(self) -> int:
        """Get league color from configuration"""
        config = self.config
        if config:
            return config.get("color", 0x00ff00)
        return 0x00ff00

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

@dataclass
class H2HHistoricalRecord:
    """Historical head-to-head record from H2H endpoint"""
    total_meetings: int
    home_team_wins: int
    away_team_wins: int
    draws: int
    home_team_goals_total: int
    away_team_goals_total: int
    avg_goals_per_game: float
    last_meeting_date: Optional[str] = None
    last_meeting_result: Optional[str] = None
    
    @property
    def home_win_percentage(self) -> float:
        """Calculate home team win percentage"""
        return (self.home_team_wins / self.total_meetings * 100) if self.total_meetings > 0 else 0.0
    
    @property
    def away_win_percentage(self) -> float:
        """Calculate away team win percentage"""
        return (self.away_team_wins / self.total_meetings * 100) if self.total_meetings > 0 else 0.0
    
    @property
    def draw_percentage(self) -> float:
        """Calculate draw percentage"""
        return (self.draws / self.total_meetings * 100) if self.total_meetings > 0 else 0.0

@dataclass
class TeamAnalysis:
    """Team analysis from matches endpoint (recent 10 matches)"""
    team_name: str
    recent_matches_count: int
    form_record: Dict[str, int]  # {"wins": 3, "draws": 1, "losses": 1}
    form_string: str  # "W-L-D-W-W"
    goals_per_game: float
    goals_against_per_game: float
    clean_sheet_percentage: float
    btts_percentage: float  # Both teams scored percentage
    high_scoring_percentage: float  # 3+ goals percentage
    card_discipline: Dict[str, float]  # {"yellow_per_game": 2.1, "red_total": 0}
    advanced_metrics: Dict[str, Any] = field(default_factory=dict)  # Early goals, late drama, etc.
    
    @property
    def win_percentage(self) -> float:
        """Calculate win percentage"""
        total_games = sum(self.form_record.values())
        return (self.form_record["wins"] / total_games * 100) if total_games > 0 else 0.0
    
    @property
    def points_per_game(self) -> float:
        """Calculate points per game (3 for win, 1 for draw)"""
        total_games = sum(self.form_record.values())
        if total_games == 0:
            return 0.0
        points = (self.form_record["wins"] * 3) + self.form_record["draws"]
        return points / total_games

@dataclass
class ComprehensiveInsights:
    """Combined analysis from both H2H and matches endpoints"""
    # H2H insights
    h2h_dominance: str  # "home_team", "away_team", "balanced"
    h2h_goals_trend: str  # "high_scoring", "low_scoring", "average"
    
    # Combined team form insights
    form_momentum: str  # "home_advantage", "away_advantage", "neutral"
    expected_goals_total: float  # Based on both teams' recent scoring
    btts_probability: float  # Based on both teams' BTTS patterns
    
    # Betting recommendations (combining all data sources)
    over_under_recommendation: str  # "Over 2.5", "Under 2.5", "Neutral"
    btts_recommendation: str  # "BTTS Yes", "BTTS No", "Neutral"
    match_outcome_lean: str  # "Home Win", "Away Win", "Draw", "Neutral"
    cards_market_insight: str  # "High Cards", "Low Cards", "Average"
    
    # Supporting evidence
    recommendation_reasoning: List[str] = field(default_factory=list)
    confidence_level: str = "Medium"  # "High", "Medium", "Low"
    
    @classmethod
    def from_dual_endpoint_data(cls, h2h_record: H2HHistoricalRecord, 
                               home_analysis: TeamAnalysis, 
                               away_analysis: TeamAnalysis) -> 'ComprehensiveInsights':
        """Create comprehensive insights from both H2H and matches endpoint data"""
        # Analyze H2H dominance
        if h2h_record.total_meetings >= 5:
            if h2h_record.home_win_percentage > 50:
                h2h_dominance = "home_team"
            elif h2h_record.away_win_percentage > 50:
                h2h_dominance = "away_team"
            else:
                h2h_dominance = "balanced"
        else:
            h2h_dominance = "insufficient_data"
        
        # Analyze goals trend
        if h2h_record.avg_goals_per_game > 2.5:
            h2h_goals_trend = "high_scoring"
        elif h2h_record.avg_goals_per_game < 2.0:
            h2h_goals_trend = "low_scoring"
        else:
            h2h_goals_trend = "average"
        
        # Analyze form momentum
        home_form_points = home_analysis.points_per_game if home_analysis else 0
        away_form_points = away_analysis.points_per_game if away_analysis else 0
        
        if home_form_points > away_form_points + 0.5:
            form_momentum = "home_advantage"
        elif away_form_points > home_form_points + 0.5:
            form_momentum = "away_advantage"
        else:
            form_momentum = "neutral"
        
        # Calculate expected goals
        home_goals_avg = home_analysis.goals_per_game if home_analysis else 1.0
        away_goals_avg = away_analysis.goals_per_game if away_analysis else 1.0
        expected_goals_total = home_goals_avg + away_goals_avg
        
        # Calculate BTTS probability
        home_btts = home_analysis.btts_percentage if home_analysis else 50.0
        away_btts = away_analysis.btts_percentage if away_analysis else 50.0
        btts_probability = (home_btts + away_btts) / 2
        
        # Generate recommendations
        over_under_rec = "Over 2.5" if expected_goals_total > 2.5 else "Under 2.5"
        btts_rec = "BTTS Yes" if btts_probability > 60 else "BTTS No"
        
        if form_momentum == "home_advantage":
            match_outcome_lean = "Home Win"
        elif form_momentum == "away_advantage":
            match_outcome_lean = "Away Win"
        else:
            match_outcome_lean = "Neutral"
        
        # Cards market insight
        home_cards = home_analysis.card_discipline.get("yellow_per_game", 2.0) if home_analysis else 2.0
        away_cards = away_analysis.card_discipline.get("yellow_per_game", 2.0) if away_analysis else 2.0
        avg_cards = (home_cards + away_cards) / 2
        
        if avg_cards > 4.0:
            cards_market_insight = "High Cards"
        elif avg_cards < 2.0:
            cards_market_insight = "Low Cards"
        else:
            cards_market_insight = "Average"
        
        return cls(
            h2h_dominance=h2h_dominance,
            h2h_goals_trend=h2h_goals_trend,
            form_momentum=form_momentum,
            expected_goals_total=expected_goals_total,
            btts_probability=btts_probability,
            over_under_recommendation=over_under_rec,
            btts_recommendation=btts_rec,
            match_outcome_lean=match_outcome_lean,
            cards_market_insight=cards_market_insight,
            recommendation_reasoning=[
                f"H2H: {h2h_dominance} dominance, {h2h_goals_trend} scoring",
                f"Form: {form_momentum} based on recent performances",
                f"Expected goals: {expected_goals_total:.1f}",
                f"BTTS probability: {btts_probability:.1f}%"
            ],
            confidence_level="High" if h2h_record.total_meetings >= 10 else "Medium"
        )

# Import enhanced error handling system
from soccer_error_handling import (
    SoccerBotError, MCPConnectionError, MCPTimeoutError, MCPDataError, 
    DiscordAPIError, ValidationError, ErrorContext, ErrorSeverity,
    retry_with_backoff, GracefulDegradation, error_handler, bot_logger
)

# ============================================================================
# SOCCER MCP CLIENT
# ============================================================================

class SoccerMCPClient:
    """
    Handles all communication with the Soccer MCP server
    Provides methods for fetching matches, odds, H2H data, and standings
    """
    
    def __init__(self):
        """Initialize the MCP client with server configuration"""
        self.mcp_url = SOCCER_MCP_URL
        self.timeout = SOCCER_MCP_TIMEOUT
        self.supported_tools = AVAILABLE_MCP_TOOLS
        self.logger = logging.getLogger(f"{__name__}.SoccerMCPClient")
        
        # Get AUTH_KEY from environment
        import os
        auth_key = os.getenv('AUTH_KEY')
        
        # HTTP client configuration
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Discord-Soccer-Bot/1.0"
        }
        
        # Add authentication header if AUTH_KEY is provided
        if auth_key:
            headers["Authorization"] = f"Bearer {auth_key}"
            self.logger.info("Using AUTH_KEY for MCP server authentication")
        else:
            self.logger.warning("No AUTH_KEY provided - some features may be limited")
        
        self.client_config = {
            "timeout": self.timeout,
            "headers": headers
        }
    
    @retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=30.0)
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any], 
                           context: Optional[ErrorContext] = None) -> Dict[str, Any]:
        """
        Generic MCP server communication method with enhanced error handling and retry logic
        
        Args:
            tool_name: Name of the MCP tool to call
            arguments: Arguments to pass to the tool
            context: Error context for logging and debugging
            
        Returns:
            MCP server response data
            
        Raises:
            MCPConnectionError: If connection to MCP server fails
            MCPTimeoutError: If request times out
            MCPDataError: If response data is invalid
        """
        # Create context if not provided
        if context is None:
            context = ErrorContext(f"mcp_tool_{tool_name}")
        
        # Log operation start
        bot_logger.log_operation_start(f"call_mcp_tool_{tool_name}", context)
        
        # Validate tool name
        if tool_name not in self.supported_tools:
            error = MCPDataError(
                f"Unsupported MCP tool: {tool_name}",
                "tool_validation",
                context=context
            )
            bot_logger.log_operation_error(f"call_mcp_tool_{tool_name}", error, context)
            raise error
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        start_time = datetime.utcnow()
        
        try:
            async with httpx.AsyncClient(**self.client_config) as client:
                self.logger.debug(f"Calling MCP tool: {tool_name} with args: {arguments}")
                
                response = await client.post(self.mcp_url, json=payload)
                response.raise_for_status()
                
                data = response.json()
                
                # Validate response structure
                if "error" in data:
                    error_msg = data["error"].get("message", "Unknown MCP error")
                    error_code = data["error"].get("code", -1)
                    
                    error = MCPDataError(
                        f"MCP server error: {error_msg} (code: {error_code})",
                        f"{tool_name}_response",
                        context=context
                    )
                    bot_logger.log_operation_error(f"call_mcp_tool_{tool_name}", error, context)
                    raise error
                
                if "result" not in data:
                    error = MCPDataError(
                        "Invalid MCP response format: missing 'result' field",
                        f"{tool_name}_response",
                        context=context
                    )
                    bot_logger.log_operation_error(f"call_mcp_tool_{tool_name}", error, context)
                    raise error
                
                # Process MCP server response format
                result = data["result"]
                
                # Handle MCP server's content array format
                if isinstance(result, dict) and "content" in result:
                    content = result["content"]
                    if isinstance(content, list) and len(content) > 0:
                        # Extract text from first content item
                        first_content = content[0]
                        if isinstance(first_content, dict) and "text" in first_content:
                            try:
                                # Parse the JSON text
                                import json
                                result = json.loads(first_content["text"])
                            except json.JSONDecodeError as e:
                                error = MCPDataError(
                                    f"Failed to parse MCP response JSON: {str(e)}",
                                    f"{tool_name}_json_parse",
                                    context=context
                                )
                                bot_logger.log_operation_error(f"call_mcp_tool_{tool_name}", error, context)
                                raise error
                
                # Log successful operation
                duration = (datetime.utcnow() - start_time).total_seconds()
                result_size = len(str(result)) if result else 0
                bot_logger.log_operation_success(
                    f"call_mcp_tool_{tool_name}", 
                    context, 
                    duration, 
                    f"Response size: {result_size} chars"
                )
                
                self.logger.debug(f"MCP tool {tool_name} completed successfully")
                return result
                
        except httpx.TimeoutException as e:
            error = MCPTimeoutError(
                f"MCP server timeout for tool: {tool_name}",
                self.timeout,
                context
            )
            bot_logger.log_operation_error(f"call_mcp_tool_{tool_name}", error, context)
            raise error
            
        except httpx.HTTPStatusError as e:
            error = MCPConnectionError(
                f"MCP server HTTP error: {e.response.status_code}",
                e.response.status_code,
                context=context
            )
            bot_logger.log_operation_error(f"call_mcp_tool_{tool_name}", error, context)
            raise error
            
        except httpx.RequestError as e:
            error = MCPConnectionError(
                f"MCP server connection error: {str(e)}",
                context=context
            )
            bot_logger.log_operation_error(f"call_mcp_tool_{tool_name}", error, context)
            raise error
            
        except Exception as e:
            error = MCPDataError(
                f"Unexpected error calling MCP tool: {str(e)}",
                f"{tool_name}_unexpected",
                context=context
            )
            bot_logger.log_operation_error(f"call_mcp_tool_{tool_name}", error, context)
            raise error
    
    async def get_matches_for_date(self, date: str, league_filter: Optional[List[str]] = None,
                                 context: Optional[ErrorContext] = None) -> Dict[str, Any]:
        """
        Fetch soccer matches for a specific date across multiple leagues with filtering and error handling
        
        Args:
            date: Date string in YYYY-MM-DD format
            league_filter: Optional list of league codes to filter (e.g., ["EPL", "La Liga"])
            context: Error context for logging and debugging
            
        Returns:
            Dictionary containing matches organized by league with priority ordering
        """
        # Create context if not provided
        if context is None:
            context = ErrorContext("get_matches_for_date", additional_data={"date": date, "league_filter": league_filter})
        
        try:
            # Validate date format (expects YYYY-MM-DD)
            self._validate_date_format(date)
            
            # Convert date to DD-MM-YYYY format for MCP server
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
            mcp_date = parsed_date.strftime("%d-%m-%Y")
            
            arguments = {"date": mcp_date}
            
            # Add league filtering if specified
            if league_filter:
                # Convert league codes to MCP server format
                mcp_leagues = []
                invalid_leagues = []
                
                # Map our league codes to MCP server league names
                league_mapping = {
                    "EPL": "EPL",
                    "La Liga": "La Liga", 
                    "MLS": "MLS"
                }
                
                for league_code in league_filter:
                    if league_code in league_mapping:
                        mcp_leagues.append(league_mapping[league_code])
                    else:
                        invalid_leagues.append(league_code)
                
                if invalid_leagues:
                    self.logger.warning(f"League codes not supported by MCP server: {invalid_leagues}")
                
                if mcp_leagues:
                    # Use the first league for filtering (MCP server takes single league)
                    arguments["league_filter"] = mcp_leagues[0]
                    self.logger.debug(f"Filtering matches for league: {mcp_leagues[0]}")
            
            # Call MCP tool with error handling
            result = await self.call_mcp_tool("get_betting_matches", arguments, context)
            
            # Validate and process response
            return self._process_matches_response(result, date, league_filter, context)
            
        except (MCPConnectionError, MCPTimeoutError, MCPDataError) as e:
            # MCP-specific errors - attempt graceful degradation
            return self._create_fallback_matches_response(date, league_filter, str(e))
            
        except ValidationError as e:
            # Re-raise validation errors as they're user input issues
            raise e
            
        except Exception as e:
            # Unexpected errors
            error = MCPDataError(
                f"Unexpected error fetching matches for date {date}: {str(e)}",
                "matches_fetch",
                context=context
            )
            bot_logger.log_operation_error("get_matches_for_date", error, context)
            raise error
    
    def _validate_date_format(self, date: str):
        """Validate date format and range"""
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
            
            # Check if date is within reasonable range (30 days past to 1 year future)
            now = datetime.now()
            min_date = now - timedelta(days=30)
            max_date = now + timedelta(days=365)
            
            if not (min_date <= parsed_date <= max_date):
                raise ValidationError(
                    f"Date {date} is outside allowed range",
                    "date",
                    date,
                    "YYYY-MM-DD within 30 days past to 1 year future"
                )
                
        except ValueError:
            raise ValidationError(
                f"Invalid date format: {date}",
                "date",
                date,
                "YYYY-MM-DD (e.g., 2025-08-17)"
            )
    
    def _process_matches_response(self, result: Dict[str, Any], date: str, 
                                league_filter: Optional[List[str]], context: ErrorContext) -> Dict[str, Any]:
        """Process and validate matches response with graceful degradation"""
        try:
            # Validate response structure
            if not isinstance(result, dict):
                raise MCPDataError("Invalid matches response format", "matches_response", context=context)
            
            # Check for matches data
            if "matches_by_league" not in result:
                # No matches found - this is normal, not an error
                self.logger.info(f"No matches found for date {date}")
                return {
                    "matches_by_league": {},
                    "total_matches": 0,
                    "date": date,
                    "league_filter": league_filter,
                    "message": "No matches scheduled for this date"
                }
            
            # Apply league priority ordering to results
            result["matches_by_league"] = self._apply_league_priority_ordering(result["matches_by_league"])
            
            # Add metadata
            result["date"] = date
            result["league_filter"] = league_filter
            result["total_matches"] = sum(
                len(matches) if isinstance(matches, list) else 1 
                for matches in result["matches_by_league"].values()
            )
            
            return result
            
        except Exception as e:
            # If processing fails, create fallback response
            bot_logger.log_graceful_degradation(
                "process_matches_response",
                ["match_processing"],
                ["raw_data"],
                context
            )
            return self._create_fallback_matches_response(date, league_filter, str(e))
    
    def _create_fallback_matches_response(self, date: str, league_filter: Optional[List[str]], 
                                        error_message: str) -> Dict[str, Any]:
        """Create fallback response when matches cannot be fetched"""
        return {
            "matches_by_league": {},
            "total_matches": 0,
            "date": date,
            "league_filter": league_filter,
            "error": error_message,
            "fallback": True,
            "message": "Unable to fetch match data. Please try again later."
        }
    
    async def get_matches_for_multiple_leagues(self, date: str, priority_leagues: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fetch matches for multiple leagues with priority-based organization
        
        Args:
            date: Date string in YYYY-MM-DD format
            priority_leagues: Optional list of priority league codes
            
        Returns:
            Dictionary with matches organized by league priority
        """
        try:
            # Use priority leagues or default to all supported leagues
            target_leagues = priority_leagues or LEAGUE_PRIORITY_ORDER
            
            # Fetch matches for all target leagues
            result = await self.get_matches_for_date(date, target_leagues)
            
            # Enrich with league-specific data
            if "matches_by_league" in result:
                enriched_matches = {}
                
                for league_code in target_leagues:
                    league_config = SUPPORTED_LEAGUES.get(league_code)
                    if not league_config:
                        continue
                    
                    # Find matches for this league in the result
                    league_name = league_config["name"]
                    league_matches = None
                    
                    # Search by league name or ID in the response
                    for response_league, matches_data in result["matches_by_league"].items():
                        if (response_league == league_name or 
                            response_league == league_code or
                            (isinstance(matches_data, dict) and 
                             matches_data.get("league_info", {}).get("id") == league_config["id"])):
                            league_matches = matches_data
                            break
                    
                    if league_matches:
                        # Enrich with league configuration data
                        if isinstance(league_matches, dict):
                            league_matches["league_config"] = league_config
                            league_matches["priority"] = league_config["priority"]
                        
                        enriched_matches[league_code] = league_matches
                
                result["matches_by_league"] = enriched_matches
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error fetching multi-league matches for date {date}: {e}")
            raise
    
    def _apply_league_priority_ordering(self, matches_by_league: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply priority ordering to league matches based on LEAGUE_PRIORITY_ORDER
        
        Args:
            matches_by_league: Original matches dictionary
            
        Returns:
            Reordered matches dictionary with priority-based ordering
        """
        try:
            ordered_matches = {}
            
            # First, add leagues in priority order
            for league_code in LEAGUE_PRIORITY_ORDER:
                league_config = SUPPORTED_LEAGUES[league_code]
                league_name = league_config["name"]
                
                # Find this league in the matches
                for key, matches_data in matches_by_league.items():
                    if (key == league_name or key == league_code or
                        (isinstance(matches_data, dict) and 
                         matches_data.get("league_info", {}).get("id") == league_config["id"])):
                        ordered_matches[league_code] = matches_data
                        break
            
            # Add any remaining leagues not in priority order
            for key, matches_data in matches_by_league.items():
                if key not in ordered_matches and key not in [config["name"] for config in SUPPORTED_LEAGUES.values()]:
                    ordered_matches[key] = matches_data
            
            return ordered_matches
            
        except Exception as e:
            self.logger.error(f"Error applying league priority ordering: {e}")
            return matches_by_league
    
    async def get_comprehensive_match_data(self, match_id: int) -> Dict[str, Any]:
        """
        Get detailed match information including odds and team data
        
        Args:
            match_id: Unique match identifier
            
        Returns:
            Comprehensive match data dictionary
        """
        try:
            arguments = {"match_id": match_id}
            result = await self.call_mcp_tool("get_match_details", arguments)
            
            if not isinstance(result, dict):
                raise MCPDataError("Invalid match details response format")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error fetching match details for ID {match_id}: {e}")
            raise
    
    async def get_h2h_analysis(self, team1_id: int, team2_id: int, include_recent_form: bool = True,
                             context: Optional[ErrorContext] = None) -> Dict[str, Any]:
        """
        Retrieve comprehensive head-to-head statistics between two teams with robust error handling
        
        Args:
            team1_id: First team's unique identifier
            team2_id: Second team's unique identifier
            include_recent_form: Whether to include recent form data (last 5-10 matches)
            context: Error context for logging and debugging
            
        Returns:
            Comprehensive head-to-head analysis data including:
            - Historical H2H records
            - Recent form for both teams
            - Advanced metrics (cards, clean sheets, goal timing)
            - Statistical insights
        """
        # Create context if not provided
        if context is None:
            context = ErrorContext(
                "get_h2h_analysis",
                team_ids=[team1_id, team2_id],
                additional_data={"include_recent_form": include_recent_form}
            )
        
        try:
            # Validate team IDs
            if not isinstance(team1_id, int) or not isinstance(team2_id, int):
                raise ValidationError(
                    f"Invalid team IDs: {team1_id}, {team2_id}",
                    "team_ids",
                    f"{team1_id}, {team2_id}",
                    "positive integers"
                )
            
            if team1_id <= 0 or team2_id <= 0:
                raise ValidationError(
                    f"Team IDs must be positive: {team1_id}, {team2_id}",
                    "team_ids",
                    f"{team1_id}, {team2_id}",
                    "positive integers greater than 0"
                )
            
            if team1_id == team2_id:
                raise ValidationError(
                    f"Team IDs must be different: {team1_id}",
                    "team_ids",
                    f"{team1_id}, {team2_id}",
                    "two different team IDs"
                )
            
            arguments = {
                "team1_id": team1_id,
                "team2_id": team2_id,
                "include_recent_form": include_recent_form,
                "include_advanced_metrics": True,
                "matches_limit": 10  # Last 10 H2H matches
            }
            
            # Call MCP tool with error handling
            result = await self.call_mcp_tool("get_head_to_head", arguments, context)
            
            # Process and validate the response
            return self._process_h2h_response(result, team1_id, team2_id, include_recent_form, context)
            
        except (MCPConnectionError, MCPTimeoutError, MCPDataError) as e:
            # Handle MCP-specific errors with graceful degradation
            bot_logger.log_graceful_degradation(
                "get_h2h_analysis",
                ["h2h_data", "recent_form", "advanced_metrics"],
                ["basic_structure"],
                context
            )
            return self._create_fallback_h2h_response(team1_id, team2_id, str(e))
            
        except ValidationError as e:
            # Re-raise validation errors
            raise e
            
        except Exception as e:
            # Unexpected errors
            error = MCPDataError(
                f"Unexpected error fetching H2H data for teams {team1_id} vs {team2_id}: {str(e)}",
                "h2h_analysis",
                context=context
            )
            bot_logger.log_operation_error("get_h2h_analysis", error, context)
            return self._create_fallback_h2h_response(team1_id, team2_id, str(e))
    
    def _process_h2h_response(self, result: Dict[str, Any], team1_id: int, team2_id: int,
                            include_recent_form: bool, context: ErrorContext) -> Dict[str, Any]:
        """Process and validate H2H response with graceful degradation for missing data"""
        try:
            if not isinstance(result, dict):
                raise MCPDataError("Invalid H2H response format", "h2h_response", context=context)
            
            # Required fields for basic H2H data
            required_fields = ['total_meetings', 'team1_wins', 'team2_wins', 'draws']
            missing_fields = []
            
            # Validate and fix required fields
            for field in required_fields:
                if field not in result or not isinstance(result[field], int):
                    missing_fields.append(field)
                    result[field] = 0
                    self.logger.warning(f"Missing or invalid H2H field: {field}, defaulting to 0")
            
            # Ensure recent form data structure exists
            if include_recent_form:
                if 'recent_form' not in result or not isinstance(result['recent_form'], dict):
                    missing_fields.append('recent_form')
                    result['recent_form'] = {'team1': [], 'team2': []}
                else:
                    # Validate recent form structure
                    if 'team1' not in result['recent_form']:
                        result['recent_form']['team1'] = []
                    if 'team2' not in result['recent_form']:
                        result['recent_form']['team2'] = []
            
            # Ensure advanced metrics structure exists
            if 'advanced_metrics' not in result or not isinstance(result['advanced_metrics'], dict):
                missing_fields.append('advanced_metrics')
                result['advanced_metrics'] = {'team1': {}, 'team2': {}}
            else:
                # Validate advanced metrics structure
                if 'team1' not in result['advanced_metrics']:
                    result['advanced_metrics']['team1'] = {}
                if 'team2' not in result['advanced_metrics']:
                    result['advanced_metrics']['team2'] = {}
            
            # Add metadata
            result['team1_id'] = team1_id
            result['team2_id'] = team2_id
            result['include_recent_form'] = include_recent_form
            
            # Log graceful degradation if there were missing fields
            if missing_fields:
                bot_logger.log_graceful_degradation(
                    "process_h2h_response",
                    missing_fields,
                    [field for field in required_fields if field not in missing_fields],
                    context
                )
                result['_partial_data'] = True
                result['_missing_fields'] = missing_fields
            
            self.logger.debug(f"Successfully processed H2H data for teams {team1_id} vs {team2_id}")
            return result
            
        except Exception as e:
            # If processing fails completely, return fallback
            bot_logger.log_graceful_degradation(
                "process_h2h_response",
                ["all_h2h_data"],
                ["basic_structure"],
                context
            )
            return self._create_fallback_h2h_response(team1_id, team2_id, str(e))
    
    def _create_fallback_h2h_response(self, team1_id: int, team2_id: int, error_message: str) -> Dict[str, Any]:
        """Create fallback H2H response when data cannot be fetched or processed"""
        return {
            'team1_id': team1_id,
            'team2_id': team2_id,
            'total_meetings': 0,
            'team1_wins': 0,
            'team2_wins': 0,
            'draws': 0,
            'recent_form': {'team1': [], 'team2': []},
            'advanced_metrics': {'team1': {}, 'team2': {}},
            'error': error_message,
            'fallback': True,
            '_partial_data': True,
            '_missing_fields': ['all_data'],
            'message': 'Head-to-head data is currently unavailable. Please try again later.'
        }
    
    async def get_team_recent_matches(self, team_id: int, league_id: int, limit: int = 10,
                                    context: Optional[ErrorContext] = None) -> Dict[str, Any]:
        """
        Fetch recent matches for a specific team using matches endpoint
        
        Args:
            team_id: Team identifier
            league_id: League identifier
            limit: Number of recent matches to fetch (default 10)
            context: Error context for logging
            
        Returns:
            Dictionary containing recent matches data for the team
        """
        if context is None:
            context = ErrorContext(
                "get_team_recent_matches",
                additional_data={"team_id": team_id, "league_id": league_id, "limit": limit}
            )
        
        try:
            # Use get_betting_matches tool with team filter
            arguments = {
                "team_id": team_id,
                "league_id": league_id,
                "limit": limit,
                "include_events": True  # Get detailed match events for analysis
            }
            
            result = await self.call_mcp_tool("get_betting_matches", arguments, context)
            
            if not result or "error" in result:
                self.logger.warning(f"No recent matches data for team {team_id}")
                return self._create_fallback_team_matches_response(team_id, limit)
            
            # Process and validate team matches data
            return self._process_team_matches_response(result, team_id, limit, context)
            
        except (MCPConnectionError, MCPTimeoutError, MCPDataError) as e:
            # MCP-specific errors - attempt graceful degradation
            self.logger.warning(f"MCP error fetching team matches for team {team_id}: {e}")
            return self._create_fallback_team_matches_response(team_id, limit, str(e))
            
        except Exception as e:
            error = MCPDataError(
                f"Unexpected error fetching team matches for team {team_id}: {str(e)}",
                "team_matches_fetch",
                context=context
            )
            bot_logger.log_operation_error("get_team_recent_matches", error, context)
            return self._create_fallback_team_matches_response(team_id, limit, str(e))
    
    def _process_team_matches_response(self, result: Dict[str, Any], team_id: int, 
                                     limit: int, context: ErrorContext) -> Dict[str, Any]:
        """Process and validate team matches response"""
        try:
            # Validate response structure
            if not isinstance(result, dict):
                raise MCPDataError("Invalid team matches response format", "team_matches_response", context=context)
            
            # Extract matches data
            matches = result.get('matches', [])
            if not isinstance(matches, list):
                matches = []
            
            # Filter and process matches for the specific team
            team_matches = []
            for match in matches[:limit]:
                if self._is_team_in_match(match, team_id):
                    processed_match = self._process_single_team_match(match, team_id)
                    if processed_match:
                        team_matches.append(processed_match)
            
            return {
                "team_id": team_id,
                "recent_matches": team_matches,
                "matches_count": len(team_matches),
                "limit": limit,
                "success": True
            }
            
        except Exception as e:
            bot_logger.log_graceful_degradation(
                "process_team_matches_response",
                ["team_matches_processing"],
                ["raw_data"],
                context
            )
            return self._create_fallback_team_matches_response(team_id, limit, str(e))
    
    def _is_team_in_match(self, match: Dict[str, Any], team_id: int) -> bool:
        """Check if team is involved in the match"""
        try:
            teams = match.get('teams', {})
            home_team = teams.get('home', {})
            away_team = teams.get('away', {})
            
            return (home_team.get('id') == team_id or away_team.get('id') == team_id)
        except Exception:
            return False
    
    def _process_single_team_match(self, match: Dict[str, Any], team_id: int) -> Optional[Dict[str, Any]]:
        """Process a single match from team perspective"""
        try:
            teams = match.get('teams', {})
            home_team = teams.get('home', {})
            away_team = teams.get('away', {})
            
            # Determine if team is home or away
            is_home = home_team.get('id') == team_id
            
            # Extract match details
            processed_match = {
                "match_id": match.get('id'),
                "date": match.get('date'),
                "time": match.get('time'),
                "home_team": home_team.get('name', 'Unknown'),
                "away_team": away_team.get('name', 'Unknown'),
                "home_goals": match.get('home_goals', 0),
                "away_goals": match.get('away_goals', 0),
                "team_is_home": is_home,
                "status": match.get('status', 'completed'),
                "venue": match.get('venue', ''),
                
                # Extract events for detailed analysis
                "yellow_cards": self._extract_team_cards(match, team_id, 'yellow'),
                "red_cards": self._extract_team_cards(match, team_id, 'red'),
                "goals_scored": self._extract_team_goals(match, team_id),
                "goals_conceded": self._extract_opponent_goals(match, team_id),
                
                # Additional match context
                "league": match.get('league', {}),
                "competition": match.get('competition', ''),
                "round": match.get('round', '')
            }
            
            return processed_match
            
        except Exception as e:
            self.logger.warning(f"Error processing single team match: {e}")
            return None
    
    def _extract_team_cards(self, match: Dict[str, Any], team_id: int, card_type: str) -> int:
        """Extract card count for specific team"""
        try:
            events = match.get('events', [])
            card_count = 0
            
            for event in events:
                if (event.get('type') == f'{card_type}_card' and 
                    event.get('team_id') == team_id):
                    card_count += 1
            
            return card_count
        except Exception:
            return 0
    
    def _extract_team_goals(self, match: Dict[str, Any], team_id: int) -> List[Dict[str, Any]]:
        """Extract goals scored by specific team"""
        try:
            events = match.get('events', [])
            goals = []
            
            for event in events:
                if (event.get('type') == 'goal' and 
                    event.get('team_id') == team_id):
                    goals.append({
                        'minute': event.get('minute', 0),
                        'player': event.get('player', 'Unknown'),
                        'type': event.get('goal_type', 'regular')
                    })
            
            return goals
        except Exception:
            return []
    
    def _extract_opponent_goals(self, match: Dict[str, Any], team_id: int) -> List[Dict[str, Any]]:
        """Extract goals scored by opponent team"""
        try:
            events = match.get('events', [])
            goals = []
            
            for event in events:
                if (event.get('type') == 'goal' and 
                    event.get('team_id') != team_id):
                    goals.append({
                        'minute': event.get('minute', 0),
                        'player': event.get('player', 'Unknown'),
                        'type': event.get('goal_type', 'regular')
                    })
            
            return goals
        except Exception:
            return []
    
    def _create_fallback_team_matches_response(self, team_id: int, limit: int, error_message: str = None) -> Dict[str, Any]:
        """Create fallback response when team matches cannot be fetched"""
        return {
            "team_id": team_id,
            "recent_matches": [],
            "matches_count": 0,
            "limit": limit,
            "success": False,
            "error": error_message or "Unable to fetch team matches data",
            "fallback": True,
            "message": "Team analysis temporarily unavailable. Please try again later."
        }
    
    async def get_h2h_direct_analysis(self, team1_id: int, team2_id: int, team1_name: str, team2_name: str,
                                    context: Optional[ErrorContext] = None) -> Dict[str, Any]:
        """
        Fetch direct head-to-head record using H2H endpoint
        
        Args:
            team1_id: First team's unique identifier (typically home team)
            team2_id: Second team's unique identifier (typically away team)
            team1_name: First team's name for logging
            team2_name: Second team's name for logging
            context: Error context for logging
            
        Returns:
            Dictionary containing direct H2H historical record between the two teams
        """
        if context is None:
            context = ErrorContext(
                "get_h2h_direct_analysis",
                additional_data={
                    "team1_id": team1_id, "team2_id": team2_id,
                    "team1_name": team1_name, "team2_name": team2_name
                }
            )
        
        try:
            # Validate team IDs
            if not isinstance(team1_id, int) or not isinstance(team2_id, int):
                raise ValidationError(
                    f"Invalid team IDs: {team1_id}, {team2_id}",
                    "team_ids",
                    f"{team1_id}, {team2_id}",
                    "positive integers"
                )
            
            if team1_id <= 0 or team2_id <= 0:
                raise ValidationError(
                    f"Team IDs must be positive: {team1_id}, {team2_id}",
                    "team_ids",
                    f"{team1_id}, {team2_id}",
                    "positive integers greater than 0"
                )
            
            if team1_id == team2_id:
                raise ValidationError(
                    f"Team IDs must be different: {team1_id}",
                    "team_ids",
                    f"{team1_id}, {team2_id}",
                    "two different team IDs"
                )
            
            # Use H2H endpoint specifically for direct historical record
            arguments = {
                "team1_id": team1_id,
                "team2_id": team2_id,
                "team1_name": team1_name,
                "team2_name": team2_name,
                "analysis_type": "direct_h2h",
                "include_historical_meetings": True,
                "include_goal_statistics": True
            }
            
            # Call H2H endpoint
            result = await self.call_mcp_tool("get_h2h_betting_analysis", arguments, context)
            
            # Process H2H response
            return self._process_h2h_direct_response(result, team1_id, team2_id, team1_name, team2_name, context)
            
        except (MCPConnectionError, MCPTimeoutError, MCPDataError) as e:
            # Handle MCP-specific errors with graceful degradation
            bot_logger.log_graceful_degradation(
                "get_h2h_direct_analysis",
                ["h2h_historical_record"],
                ["basic_structure"],
                context
            )
            return self._create_fallback_h2h_direct_response(team1_id, team2_id, team1_name, team2_name, str(e))
            
        except ValidationError as e:
            # Re-raise validation errors
            raise e
            
        except Exception as e:
            # Unexpected errors
            error = MCPDataError(
                f"Unexpected error fetching direct H2H data for {team1_name} vs {team2_name}: {str(e)}",
                "h2h_direct_analysis",
                context=context
            )
            bot_logger.log_operation_error("get_h2h_direct_analysis", error, context)
            return self._create_fallback_h2h_direct_response(team1_id, team2_id, team1_name, team2_name, str(e))
    
    def _process_h2h_direct_response(self, result: Dict[str, Any], team1_id: int, team2_id: int,
                                   team1_name: str, team2_name: str, context: ErrorContext) -> Dict[str, Any]:
        """Process direct H2H endpoint response"""
        try:
            if not isinstance(result, dict):
                raise MCPDataError("Invalid H2H direct response format", "h2h_direct_response", context=context)
            
            # Extract H2H statistics with defaults
            h2h_stats = result.get('h2h_statistics', {})
            
            processed_response = {
                "team1_id": team1_id,
                "team2_id": team2_id,
                "team1_name": team1_name,
                "team2_name": team2_name,
                "total_meetings": h2h_stats.get('total_meetings', 0),
                "team1_wins": h2h_stats.get('team1_wins', 0),
                "team2_wins": h2h_stats.get('team2_wins', 0),
                "draws": h2h_stats.get('draws', 0),
                "team1_goals_total": h2h_stats.get('team1_goals_total', 0),
                "team2_goals_total": h2h_stats.get('team2_goals_total', 0),
                "avg_goals_per_game": h2h_stats.get('avg_goals_per_game', 0.0),
                "last_meeting_date": h2h_stats.get('last_meeting_date'),
                "last_meeting_result": h2h_stats.get('last_meeting_result'),
                "source": "h2h_endpoint",
                "success": True
            }
            
            # Add recent H2H meetings if available
            if 'recent_meetings' in result:
                processed_response['recent_meetings'] = result['recent_meetings']
            
            self.logger.debug(f"Successfully processed direct H2H data for {team1_name} vs {team2_name}")
            return processed_response
            
        except Exception as e:
            bot_logger.log_graceful_degradation(
                "process_h2h_direct_response",
                ["h2h_direct_processing"],
                ["basic_structure"],
                context
            )
            return self._create_fallback_h2h_direct_response(team1_id, team2_id, team1_name, team2_name, str(e))
    
    def _create_fallback_h2h_direct_response(self, team1_id: int, team2_id: int, 
                                           team1_name: str, team2_name: str, error_message: str) -> Dict[str, Any]:
        """Create fallback H2H direct response when data cannot be fetched"""
        return {
            "team1_id": team1_id,
            "team2_id": team2_id,
            "team1_name": team1_name,
            "team2_name": team2_name,
            "total_meetings": 0,
            "team1_wins": 0,
            "team2_wins": 0,
            "draws": 0,
            "team1_goals_total": 0,
            "team2_goals_total": 0,
            "avg_goals_per_game": 0.0,
            "last_meeting_date": None,
            "last_meeting_result": None,
            "recent_meetings": [],
            "source": "h2h_endpoint",
            "success": False,
            "error": error_message,
            "fallback": True,
            "message": f"Direct H2H data for {team1_name} vs {team2_name} is currently unavailable."
        }
    
    async def get_comprehensive_match_analysis(self, home_team_id: int, away_team_id: int, 
                                             home_team_name: str, away_team_name: str, league_id: int,
                                             context: Optional[ErrorContext] = None) -> Dict[str, Any]:
        """
        Get comprehensive match analysis combining H2H endpoint data with matches endpoint data for both teams
        
        Args:
            home_team_id: Home team identifier
            away_team_id: Away team identifier
            home_team_name: Home team name
            away_team_name: Away team name
            league_id: League identifier
            context: Error context for logging
            
        Returns:
            Dictionary containing comprehensive analysis from both endpoints
        """
        if context is None:
            context = ErrorContext(
                "get_comprehensive_match_analysis",
                additional_data={
                    "home_team_id": home_team_id, "away_team_id": away_team_id,
                    "home_team_name": home_team_name, "away_team_name": away_team_name,
                    "league_id": league_id
                }
            )
        
        try:
            # Make three MCP calls concurrently for efficiency
            h2h_task = self.get_h2h_direct_analysis(home_team_id, away_team_id, home_team_name, away_team_name, context)
            home_matches_task = self.get_team_recent_matches(home_team_id, league_id, 10, context)
            away_matches_task = self.get_team_recent_matches(away_team_id, league_id, 10, context)
            
            # Wait for all three calls to complete
            h2h_data, home_matches_data, away_matches_data = await asyncio.gather(
                h2h_task, home_matches_task, away_matches_task, return_exceptions=True
            )
            
            # Handle exceptions from individual calls
            if isinstance(h2h_data, Exception):
                self.logger.warning(f"H2H data fetch failed: {h2h_data}")
                h2h_data = self._create_fallback_h2h_direct_response(
                    home_team_id, away_team_id, home_team_name, away_team_name, str(h2h_data)
                )
            
            if isinstance(home_matches_data, Exception):
                self.logger.warning(f"Home team matches fetch failed: {home_matches_data}")
                home_matches_data = self._create_fallback_team_matches_response(home_team_id, 10, str(home_matches_data))
            
            if isinstance(away_matches_data, Exception):
                self.logger.warning(f"Away team matches fetch failed: {away_matches_data}")
                away_matches_data = self._create_fallback_team_matches_response(away_team_id, 10, str(away_matches_data))
            
            # Combine all data sources
            comprehensive_analysis = {
                "match_info": {
                    "home_team_id": home_team_id,
                    "away_team_id": away_team_id,
                    "home_team_name": home_team_name,
                    "away_team_name": away_team_name,
                    "league_id": league_id
                },
                "h2h_analysis": h2h_data,
                "home_team_analysis": home_matches_data,
                "away_team_analysis": away_matches_data,
                "data_sources": {
                    "h2h_endpoint": h2h_data.get('success', False),
                    "home_matches_endpoint": home_matches_data.get('success', False),
                    "away_matches_endpoint": away_matches_data.get('success', False)
                },
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "success": True
            }
            
            self.logger.info(f"Successfully fetched comprehensive analysis for {home_team_name} vs {away_team_name}")
            return comprehensive_analysis
            
        except Exception as e:
            error = MCPDataError(
                f"Unexpected error in comprehensive match analysis for {home_team_name} vs {away_team_name}: {str(e)}",
                "comprehensive_analysis",
                context=context
            )
            bot_logger.log_operation_error("get_comprehensive_match_analysis", error, context)
            
            # Return fallback with partial data if possible
            return {
                "match_info": {
                    "home_team_id": home_team_id,
                    "away_team_id": away_team_id,
                    "home_team_name": home_team_name,
                    "away_team_name": away_team_name,
                    "league_id": league_id
                },
                "h2h_analysis": self._create_fallback_h2h_direct_response(
                    home_team_id, away_team_id, home_team_name, away_team_name, str(e)
                ),
                "home_team_analysis": self._create_fallback_team_matches_response(home_team_id, 10, str(e)),
                "away_team_analysis": self._create_fallback_team_matches_response(away_team_id, 10, str(e)),
                "data_sources": {
                    "h2h_endpoint": False,
                    "home_matches_endpoint": False,
                    "away_matches_endpoint": False
                },
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "error": str(e),
                "fallback": True,
                "message": "Comprehensive analysis temporarily unavailable. Please try again later."
            }
    
    async def get_betting_odds(self, match_id: int) -> Dict[str, Any]:
        """
        Fetch betting odds for a specific match
        
        Args:
            match_id: Unique match identifier
            
        Returns:
            Betting odds data dictionary
        """
        try:
            # Use match details to get odds information
            match_data = await self.get_comprehensive_match_data(match_id)
            
            # Extract odds from match data
            if "odds" in match_data:
                return match_data["odds"]
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Error fetching betting odds for match {match_id}: {e}")
            raise
    
    async def get_league_standings(self, league_id: int, include_form: bool = True) -> Dict[str, Any]:
        """
        Get current league standings/table with enhanced data
        
        Args:
            league_id: League identifier from SUPPORTED_LEAGUES
            include_form: Whether to include recent form data
            
        Returns:
            League standings data with enhanced information
        """
        try:
            arguments = {
                "league_id": league_id,
                "include_form": include_form,
                "include_stats": True  # Include goals for/against, points, etc.
            }
            result = await self.call_mcp_tool("get_league_standings", arguments)
            
            if not isinstance(result, dict):
                raise MCPDataError("Invalid standings response format")
            
            # Enrich with league configuration
            league_config = self._get_league_config_by_id(league_id)
            if league_config:
                result["league_config"] = league_config
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error fetching league standings for league {league_id}: {e}")
            raise
    
    async def get_tournament_stage_info(self, match_id: int) -> Dict[str, Any]:
        """
        Get tournament stage information for UEFA Champions League matches
        
        Args:
            match_id: Match identifier
            
        Returns:
            Tournament stage information including stage name, round, and context
        """
        try:
            # Get comprehensive match data
            match_data = await self.get_comprehensive_match_data(match_id)
            
            # Extract tournament stage information
            stage_info = {
                "stage": "unknown",
                "stage_name": "Unknown Stage",
                "round": None,
                "group": None,
                "is_knockout": False,
                "leg": None  # For two-leg knockout matches
            }
            
            # Check if this is a UEFA Champions League match
            if "league" in match_data:
                league_info = match_data["league"]
                if league_info.get("id") == SUPPORTED_LEAGUES["UEFA"]["id"]:
                    # Extract stage information from match data
                    if "stage" in match_data:
                        stage_data = match_data["stage"]
                        stage_info.update(self._parse_uefa_stage_data(stage_data))
                    
                    # Add UEFA-specific context
                    stage_info["is_uefa"] = True
                    stage_info["tournament_name"] = "UEFA Champions League"
            
            return stage_info
            
        except Exception as e:
            self.logger.error(f"Error fetching tournament stage info for match {match_id}: {e}")
            return {"stage": "unknown", "stage_name": "Unknown Stage", "error": str(e)}
    
    def _parse_uefa_stage_data(self, stage_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse UEFA Champions League stage data
        
        Args:
            stage_data: Raw stage data from MCP
            
        Returns:
            Parsed stage information
        """
        parsed_info = {}
        
        try:
            stage_name = stage_data.get("name", "").lower()
            
            # Map stage names to our configuration
            if "group" in stage_name:
                parsed_info.update({
                    "stage": "group_stage",
                    "stage_name": "Group Stage",
                    "is_knockout": False,
                    "group": stage_data.get("group_name", stage_data.get("group"))
                })
            elif "round of 16" in stage_name or "r16" in stage_name:
                parsed_info.update({
                    "stage": "round_of_16",
                    "stage_name": "Round of 16",
                    "is_knockout": True,
                    "leg": stage_data.get("leg")
                })
            elif "quarter" in stage_name:
                parsed_info.update({
                    "stage": "quarter_finals",
                    "stage_name": "Quarter Finals",
                    "is_knockout": True,
                    "leg": stage_data.get("leg")
                })
            elif "semi" in stage_name:
                parsed_info.update({
                    "stage": "semi_finals",
                    "stage_name": "Semi Finals",
                    "is_knockout": True,
                    "leg": stage_data.get("leg")
                })
            elif "final" in stage_name:
                parsed_info.update({
                    "stage": "final",
                    "stage_name": "Final",
                    "is_knockout": True
                })
            
            # Add round information if available
            if "round" in stage_data:
                parsed_info["round"] = stage_data["round"]
            
            return parsed_info
            
        except Exception as e:
            self.logger.error(f"Error parsing UEFA stage data: {e}")
            return {"stage": "unknown", "stage_name": "Unknown Stage"}
    
    def _get_league_config_by_id(self, league_id: int) -> Optional[Dict[str, Any]]:
        """
        Get league configuration by league ID
        
        Args:
            league_id: League identifier
            
        Returns:
            League configuration dictionary or None
        """
        for league_code, config in SUPPORTED_LEAGUES.items():
            if config["id"] == league_id:
                return {**config, "code": league_code}
        return None
    
    async def validate_date_format(self, date_string: str) -> str:
        """
        Validate and normalize date format for MCP server
        
        Args:
            date_string: Date string in various formats
            
        Returns:
            Normalized date string in YYYY-MM-DD format
            
        Raises:
            ValueError: If date format is invalid
        """
        allowed_formats = ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"]
        
        for fmt in allowed_formats:
            try:
                parsed_date = datetime.strptime(date_string, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        raise ValueError(f"Invalid date format: {date_string}")

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
    
    def process_match_data(self, raw_matches: Dict[str, Any], include_standings: bool = True) -> List[ProcessedMatch]:
        """
        Process raw MCP match data into ProcessedMatch objects with multi-league support
        
        Args:
            raw_matches: Raw match data from MCP server
            include_standings: Whether to include team standings information
            
        Returns:
            List of ProcessedMatch objects sorted by league priority
        """
        processed_matches = []
        
        try:
            if not raw_matches or 'matches_by_league' not in raw_matches:
                self.logger.warning("No matches_by_league data in response")
                return processed_matches
            
            matches_by_league = raw_matches['matches_by_league']
            
            # Map MCP server league names to our league codes
            league_name_mapping = {
                "UEFA": "UEFA",
                "EPL": "EPL", 
                "LA LIGA": "La Liga",
                "BUNDESLIGA": "Bundesliga",
                "SERIE A": "Serie A",
                "MLS": "MLS"
            }
            
            # Process matches by league priority order
            for league_code in LEAGUE_PRIORITY_ORDER:
                # Find the league in the response (might have different name)
                league_data = None
                mcp_league_name = None
                
                # Try direct match first
                if league_code in matches_by_league:
                    league_data = matches_by_league[league_code]
                    mcp_league_name = league_code
                else:
                    # Try mapped names
                    for mcp_name, our_name in league_name_mapping.items():
                        if our_name == league_code and mcp_name in matches_by_league:
                            league_data = matches_by_league[mcp_name]
                            mcp_league_name = mcp_name
                            break
                
                if not league_data or not isinstance(league_data, list):
                    continue
                
                # Get league configuration
                league_config = SUPPORTED_LEAGUES.get(league_code, {})
                
                # Create league object
                league = League(
                    id=league_config.get('id', 0),
                    name=league_config.get('name', league_code),
                    country=league_config.get('country', 'Unknown'),
                    season=league_config.get('season_format'),
                    priority=league_config.get('priority', 999),
                    tournament_type=league_config.get('tournament_type', 'league')
                )
                
                # Process matches for this league
                league_matches = []
                for match_data in league_data:
                    try:
                        processed_match = self._process_single_match(match_data, league, include_standings)
                        if processed_match:
                            league_matches.append(processed_match)
                    except Exception as e:
                        self.logger.error(f"Error processing match in {league_code}: {e}")
                        continue
                
                # Sort matches within league by time
                league_matches.sort(key=lambda m: (m.date, m.time))
                processed_matches.extend(league_matches)
            
            # Process any remaining leagues not in priority order
            for league_name, league_data in matches_by_league.items():
                if league_name in LEAGUE_PRIORITY_ORDER:
                    continue
                
                if not isinstance(league_data, dict) or 'matches' not in league_data:
                    continue
                
                # Create basic league object for unknown leagues
                league_info = league_data.get('league_info', {})
                league = League(
                    id=league_info.get('id', 0),
                    name=league_info.get('name', league_name),
                    country=league_info.get('country', 'Unknown'),
                    season=league_info.get('season'),
                    logo_url=league_info.get('logo_url'),
                    priority=999  # Low priority for unknown leagues
                )
                
                for match_data in league_data['matches']:
                    try:
                        processed_match = self._process_single_match(match_data, league, include_standings)
                        if processed_match:
                            processed_matches.append(processed_match)
                    except Exception as e:
                        self.logger.error(f"Error processing match in {league_name}: {e}")
                        continue
            
            self.logger.info(f"Processed {len(processed_matches)} matches from {len(matches_by_league)} leagues")
            return processed_matches
            
        except Exception as e:
            self.logger.error(f"Error processing match data: {e}")
            return processed_matches
    
    def _process_single_match(self, match_data: Dict[str, Any], league: League, include_standings: bool = True) -> Optional[ProcessedMatch]:
        """
        Process a single match from MCP data with enhanced team information
        
        Args:
            match_data: Single match data dictionary
            league: League object for this match
            include_standings: Whether to include team standings information
            
        Returns:
            ProcessedMatch object or None if processing fails
        """
        try:
            # Extract basic match information
            match_id = match_data.get('id', 0)
            raw_date = match_data.get('date', '')
            time = match_data.get('time', '')
            venue = match_data.get('venue', 'TBD')
            status = match_data.get('status', 'scheduled')
            
            # Convert date format from DD/MM/YYYY to YYYY-MM-DD
            date = raw_date
            if raw_date and '/' in raw_date:
                try:
                    from datetime import datetime
                    parsed_date = datetime.strptime(raw_date, "%d/%m/%Y")
                    date = parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    self.logger.warning(f"Could not parse date format: {raw_date}")
                    date = raw_date
            
            # Extract team information with standings (handle MCP server format)
            teams_data = match_data.get('teams', {})
            home_team_data = teams_data.get('home', {})
            away_team_data = teams_data.get('away', {})
            
            # Process home team with standings
            home_standing = None
            if include_standings and 'standing' in home_team_data:
                home_standing = self._process_team_standing(home_team_data['standing'])
            
            home_team = Team(
                id=home_team_data.get('id', 0),
                name=home_team_data.get('name', 'Unknown'),
                short_name=home_team_data.get('short_name', home_team_data.get('name', 'Unknown')),
                logo_url=home_team_data.get('logo_url'),
                country=home_team_data.get('country'),
                standing=home_standing
            )
            
            # Process away team with standings
            away_standing = None
            if include_standings and 'standing' in away_team_data:
                away_standing = self._process_team_standing(away_team_data['standing'])
            
            away_team = Team(
                id=away_team_data.get('id', 0),
                name=away_team_data.get('name', 'Unknown'),
                short_name=away_team_data.get('short_name', away_team_data.get('name', 'Unknown')),
                logo_url=away_team_data.get('logo_url'),
                country=away_team_data.get('country'),
                standing=away_standing
            )
            
            # Process tournament stage information for UEFA matches
            if league.is_tournament and league.config and league.config.get("code") == "UEFA":
                if 'stage' in match_data:
                    stage_info = match_data['stage']
                    league.stage = stage_info.get('stage')
                    league.stage_name = stage_info.get('stage_name')
            
            # Process betting odds if available
            odds = None
            if 'odds' in match_data and match_data['odds']:
                odds = self._process_betting_odds(match_data['odds'])
            
            # Process H2H summary if available
            h2h_summary = None
            if 'h2h_summary' in match_data and match_data['h2h_summary']:
                h2h_summary = self._process_h2h_summary(match_data['h2h_summary'])
            
            # Create ProcessedMatch object
            processed_match = ProcessedMatch(
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
            
            return processed_match
            
        except Exception as e:
            self.logger.error(f"Error processing single match: {e}")
            return None
    
    def _process_team_standing(self, standing_data: Dict[str, Any]) -> Optional[TeamStanding]:
        """
        Process team standing information
        
        Args:
            standing_data: Raw standing data from MCP
            
        Returns:
            TeamStanding object or None if processing fails
        """
        try:
            # Extract form data if available
            form = None
            if 'form' in standing_data and isinstance(standing_data['form'], list):
                form = standing_data['form']
            elif 'recent_form' in standing_data:
                form = standing_data['recent_form']
            
            return TeamStanding(
                position=int(standing_data.get('position', 0)),
                points=int(standing_data.get('points', 0)),
                played=int(standing_data.get('played', 0)),
                won=int(standing_data.get('won', 0)),
                drawn=int(standing_data.get('drawn', 0)),
                lost=int(standing_data.get('lost', 0)),
                goals_for=int(standing_data.get('goals_for', 0)),
                goals_against=int(standing_data.get('goals_against', 0)),
                goal_difference=int(standing_data.get('goal_difference', 0)),
                form=form
            )
            
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error processing team standing: {e}")
            return None
    
    def _process_betting_odds(self, odds_data: Dict[str, Any]) -> Optional[BettingOdds]:
        """
        Process betting odds data into BettingOdds object
        
        Args:
            odds_data: Raw odds data from MCP
            
        Returns:
            BettingOdds object or None if processing fails
        """
        try:
            betting_odds = BettingOdds()
            
            # Process moneyline odds (1X2)
            if 'home_win' in odds_data:
                betting_odds.home_win = OddsFormat.from_decimal(float(odds_data['home_win']))
            if 'draw' in odds_data:
                betting_odds.draw = OddsFormat.from_decimal(float(odds_data['draw']))
            if 'away_win' in odds_data:
                betting_odds.away_win = OddsFormat.from_decimal(float(odds_data['away_win']))
            
            # Process over/under if available
            if 'over_under' in odds_data and odds_data['over_under']:
                ou_data = odds_data['over_under']
                if 'line' in ou_data and 'over' in ou_data and 'under' in ou_data:
                    betting_odds.over_under = OverUnder(
                        line=float(ou_data['line']),
                        over_odds=OddsFormat.from_decimal(float(ou_data['over'])),
                        under_odds=OddsFormat.from_decimal(float(ou_data['under']))
                    )
            
            # Process both teams to score if available
            if 'both_teams_score' in odds_data:
                betting_odds.both_teams_score = OddsFormat.from_decimal(float(odds_data['both_teams_score']))
            
            # Process handicap if available
            if 'handicap' in odds_data and odds_data['handicap']:
                hc_data = odds_data['handicap']
                if 'line' in hc_data and 'home' in hc_data and 'away' in hc_data:
                    betting_odds.handicap = Handicap(
                        line=float(hc_data['line']),
                        home_odds=OddsFormat.from_decimal(float(hc_data['home'])),
                        away_odds=OddsFormat.from_decimal(float(hc_data['away']))
                    )
            
            return betting_odds if betting_odds.has_odds else None
            
        except Exception as e:
            self.logger.error(f"Error processing betting odds: {e}")
            return None
    
    def _process_h2h_summary(self, h2h_data: Dict[str, Any]) -> Optional[H2HSummary]:
        """
        Process head-to-head summary data
        
        Args:
            h2h_data: Raw H2H data from MCP
            
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
    
    def calculate_h2h_insights(self, h2h_data: Dict[str, Any], team1_name: str, team2_name: str) -> H2HInsights:
        """
        Calculate comprehensive head-to-head insights from raw MCP data
        
        Args:
            h2h_data: Raw H2H data from MCP server
            team1_name: Name of the first team (typically home team)
            team2_name: Name of the second team (typically away team)
            
        Returns:
            H2HInsights object with calculated statistics and recommendations
        """
        try:
            # Extract basic H2H statistics with type validation
            total_meetings = int(h2h_data.get('total_meetings', 0)) if h2h_data.get('total_meetings') is not None else 0
            team1_wins = int(h2h_data.get('team1_wins', 0)) if h2h_data.get('team1_wins') is not None else 0
            team2_wins = int(h2h_data.get('team2_wins', 0)) if h2h_data.get('team2_wins') is not None else 0
            draws = int(h2h_data.get('draws', 0)) if h2h_data.get('draws') is not None else 0
            
            # Calculate average goals per game
            avg_goals = 0.0
            if 'match_history' in h2h_data and isinstance(h2h_data['match_history'], list):
                total_goals = 0
                match_count = 0
                for match in h2h_data['match_history']:
                    if isinstance(match, dict) and 'team1_score' in match and 'team2_score' in match:
                        try:
                            total_goals += int(match['team1_score']) + int(match['team2_score'])
                            match_count += 1
                        except (ValueError, TypeError):
                            continue
                if match_count > 0:
                    avg_goals = total_goals / match_count
            
            # Process recent form data
            recent_form = {}
            if 'recent_form' in h2h_data:
                recent_form = self._process_recent_form(h2h_data['recent_form'])
            
            # Calculate key statistics from advanced metrics
            key_statistics = {}
            if 'advanced_metrics' in h2h_data:
                key_statistics = self._calculate_advanced_statistics(h2h_data['advanced_metrics'])
            
            # Create H2HInsights object
            insights = H2HInsights(
                total_meetings=total_meetings,
                home_team_wins=team1_wins,  # Assuming team1 is home team
                away_team_wins=team2_wins,  # Assuming team2 is away team
                draws=draws,
                avg_goals_per_game=avg_goals,
                recent_form=recent_form,
                key_statistics=key_statistics
            )
            
            # Generate betting recommendations
            insights.betting_recommendations = self.generate_betting_recommendations(insights, h2h_data)
            
            self.logger.debug(f"Calculated H2H insights for {team1_name} vs {team2_name}: {total_meetings} meetings")
            return insights
            
        except Exception as e:
            self.logger.error(f"Error calculating H2H insights: {e}")
            # Return minimal insights object for graceful degradation
            return H2HInsights(
                total_meetings=0,
                home_team_wins=0,
                away_team_wins=0,
                draws=0,
                avg_goals_per_game=0.0,
                recent_form={},
                key_statistics={'error': str(e)},
                betting_recommendations=["Unable to generate recommendations due to data error"]
            )
    
    def _process_recent_form(self, recent_form_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Process recent form data for both teams
        
        Args:
            recent_form_data: Raw recent form data from MCP
            
        Returns:
            Dictionary with processed recent form for both teams
        """
        processed_form = {'team1': [], 'team2': []}
        
        try:
            for team_key in ['team1', 'team2']:
                if team_key in recent_form_data and isinstance(recent_form_data[team_key], list):
                    team_form = []
                    for match in recent_form_data[team_key][:10]:  # Last 10 matches
                        if isinstance(match, dict):
                            result = match.get('result', 'U')  # W/L/D/U(nknown)
                            opponent = match.get('opponent', 'Unknown')
                            score = match.get('score', '')
                            date = match.get('date', '')
                            
                            form_entry = f"{result}"
                            if score:
                                form_entry += f" ({score})"
                            if opponent:
                                form_entry += f" vs {opponent}"
                            if date:
                                form_entry += f" [{date}]"
                            
                            team_form.append(form_entry)
                    
                    processed_form[team_key] = team_form
            
            return processed_form
            
        except Exception as e:
            self.logger.error(f"Error processing recent form: {e}")
            return {'team1': [], 'team2': []}
    
    def _calculate_advanced_statistics(self, advanced_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate advanced statistics from metrics data
        
        Args:
            advanced_metrics: Raw advanced metrics from MCP
            
        Returns:
            Dictionary with calculated advanced statistics
        """
        statistics = {}
        
        try:
            for team_key in ['team1', 'team2']:
                if team_key in advanced_metrics:
                    team_metrics = advanced_metrics[team_key]
                    team_stats = {}
                    
                    # Cards per game
                    if 'total_cards' in team_metrics and 'matches_played' in team_metrics:
                        matches = team_metrics['matches_played']
                        if matches > 0:
                            team_stats['cards_per_game'] = team_metrics['total_cards'] / matches
                    
                    # Clean sheet percentage
                    if 'clean_sheets' in team_metrics and 'matches_played' in team_metrics:
                        matches = team_metrics['matches_played']
                        if matches > 0:
                            team_stats['clean_sheet_percentage'] = (team_metrics['clean_sheets'] / matches) * 100
                    
                    # Goals per game
                    if 'total_goals' in team_metrics and 'matches_played' in team_metrics:
                        matches = team_metrics['matches_played']
                        if matches > 0:
                            team_stats['goals_per_game'] = team_metrics['total_goals'] / matches
                    
                    # Goals conceded per game
                    if 'goals_conceded' in team_metrics and 'matches_played' in team_metrics:
                        matches = team_metrics['matches_played']
                        if matches > 0:
                            team_stats['goals_conceded_per_game'] = team_metrics['goals_conceded'] / matches
                    
                    # Goal timing patterns (if available)
                    if 'goal_timing' in team_metrics:
                        team_stats['goal_timing_patterns'] = team_metrics['goal_timing']
                    
                    # Both teams to score frequency
                    if 'btts_matches' in team_metrics and 'matches_played' in team_metrics:
                        matches = team_metrics['matches_played']
                        if matches > 0:
                            team_stats['btts_frequency'] = (team_metrics['btts_matches'] / matches) * 100
                    
                    statistics[team_key] = team_stats
            
            return statistics
            
        except Exception as e:
            self.logger.error(f"Error calculating advanced statistics: {e}")
            return {'error': str(e)}
    
    def generate_betting_recommendations(self, insights: H2HInsights, raw_h2h_data: Dict[str, Any]) -> List[str]:
        """
        Generate betting recommendations based on H2H insights and advanced metrics
        
        Args:
            insights: Calculated H2H insights
            raw_h2h_data: Raw H2H data for additional context
            
        Returns:
            List of betting recommendation strings
        """
        recommendations = []
        
        try:
            # Match outcome recommendations
            if insights.total_meetings >= 5:  # Need sufficient data
                if insights.home_win_percentage >= 60:
                    recommendations.append(f"🏠 Home team strong in this matchup ({insights.home_win_percentage:.1f}% win rate)")
                elif insights.away_win_percentage >= 60:
                    recommendations.append(f"✈️ Away team dominates historically ({insights.away_win_percentage:.1f}% win rate)")
                elif insights.draw_percentage >= 35:
                    recommendations.append(f"🤝 High draw probability in this fixture ({insights.draw_percentage:.1f}%)")
            
            # Over/Under recommendations
            if insights.avg_goals_per_game > 0:
                if insights.avg_goals_per_game >= 3.0:
                    recommendations.append(f"⚽ High-scoring fixture (avg {insights.avg_goals_per_game:.1f} goals)")
                    recommendations.append("📈 Consider Over 2.5 goals")
                elif insights.avg_goals_per_game <= 2.0:
                    recommendations.append(f"🛡️ Low-scoring fixture (avg {insights.avg_goals_per_game:.1f} goals)")
                    recommendations.append("📉 Consider Under 2.5 goals")
            
            # Both Teams to Score (BTTS) recommendations
            btts_percentage = self._calculate_btts_percentage(raw_h2h_data)
            if btts_percentage >= 70:
                recommendations.append(f"🎯 Both teams likely to score ({btts_percentage:.1f}% in H2H)")
            elif btts_percentage <= 30:
                recommendations.append(f"🚫 Low BTTS probability ({btts_percentage:.1f}% in H2H)")
            
            # Advanced metrics recommendations
            if insights.key_statistics:
                recommendations.extend(self._generate_advanced_recommendations(insights.key_statistics))
            
            # Recent form recommendations
            if insights.recent_form:
                form_recommendations = self._analyze_recent_form_trends(insights.recent_form)
                recommendations.extend(form_recommendations)
            
            # Ensure we have at least some recommendations
            if not recommendations:
                recommendations.append("📊 Insufficient data for specific recommendations")
                if insights.total_meetings > 0:
                    recommendations.append(f"ℹ️ Based on {insights.total_meetings} previous meetings")
            
            return recommendations[:8]  # Limit to 8 recommendations for readability
            
        except Exception as e:
            self.logger.error(f"Error generating betting recommendations: {e}")
            return ["❌ Unable to generate recommendations due to analysis error"]
    
    def _calculate_btts_percentage(self, raw_h2h_data: Dict[str, Any]) -> float:
        """Calculate Both Teams to Score percentage from match history"""
        try:
            if 'match_history' not in raw_h2h_data or not raw_h2h_data['match_history']:
                return 0.0
            
            btts_count = 0
            total_matches = 0
            
            for match in raw_h2h_data['match_history']:
                if 'team1_score' in match and 'team2_score' in match:
                    team1_score = match['team1_score']
                    team2_score = match['team2_score']
                    
                    if team1_score > 0 and team2_score > 0:
                        btts_count += 1
                    total_matches += 1
            
            return (btts_count / total_matches * 100) if total_matches > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating BTTS percentage: {e}")
            return 0.0
    
    def _generate_advanced_recommendations(self, key_statistics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on advanced statistics"""
        recommendations = []
        
        try:
            for team_key in ['team1', 'team2']:
                if team_key in key_statistics:
                    stats = key_statistics[team_key]
                    team_label = "Home" if team_key == 'team1' else "Away"
                    
                    # Cards recommendations
                    if 'cards_per_game' in stats and stats['cards_per_game'] >= 3.0:
                        recommendations.append(f"🟨 {team_label} team averages {stats['cards_per_game']:.1f} cards/game")
                    
                    # Clean sheet recommendations
                    if 'clean_sheet_percentage' in stats:
                        if stats['clean_sheet_percentage'] >= 40:
                            recommendations.append(f"🛡️ {team_label} team strong defensively ({stats['clean_sheet_percentage']:.1f}% clean sheets)")
                        elif stats['clean_sheet_percentage'] <= 15:
                            recommendations.append(f"⚠️ {team_label} team vulnerable defensively ({stats['clean_sheet_percentage']:.1f}% clean sheets)")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating advanced recommendations: {e}")
            return []
    
    def _analyze_recent_form_trends(self, recent_form: Dict[str, List[str]]) -> List[str]:
        """Analyze recent form trends for betting insights"""
        recommendations = []
        
        try:
            for team_key in ['team1', 'team2']:
                if team_key in recent_form and recent_form[team_key]:
                    form_list = recent_form[team_key][:5]  # Last 5 matches
                    team_label = "Home" if team_key == 'team1' else "Away"
                    
                    # Count wins in last 5
                    wins = sum(1 for match in form_list if match.startswith('W'))
                    losses = sum(1 for match in form_list if match.startswith('L'))
                    
                    if wins >= 4:
                        recommendations.append(f"🔥 {team_label} team in excellent form ({wins}/5 wins)")
                    elif losses >= 4:
                        recommendations.append(f"📉 {team_label} team struggling ({losses}/5 losses)")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error analyzing recent form trends: {e}")
            return []

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
    
    def _format_advanced_statistics(self, key_statistics: Dict[str, Any], team1_name: str, team2_name: str) -> str:
        """Format advanced statistics for embed display"""
        stats_text = ""
        
        try:
            # Format team1 (away team) statistics
            if 'team1' in key_statistics:
                team1_stats = key_statistics['team1']
                stats_text += f"**{team1_name}:**\n"
                
                if 'goals_per_game' in team1_stats:
                    stats_text += f"⚽ Goals/Game: {team1_stats['goals_per_game']:.1f}\n"
                if 'goals_conceded_per_game' in team1_stats:
                    stats_text += f"🥅 Conceded/Game: {team1_stats['goals_conceded_per_game']:.1f}\n"
                if 'clean_sheet_percentage' in team1_stats:
                    stats_text += f"🛡️ Clean Sheets: {team1_stats['clean_sheet_percentage']:.1f}%\n"
                if 'cards_per_game' in team1_stats:
                    stats_text += f"🟨 Cards/Game: {team1_stats['cards_per_game']:.1f}\n"
                
                stats_text += "\n"
            
            # Format team2 (home team) statistics
            if 'team2' in key_statistics:
                team2_stats = key_statistics['team2']
                stats_text += f"**{team2_name}:**\n"
                
                if 'goals_per_game' in team2_stats:
                    stats_text += f"⚽ Goals/Game: {team2_stats['goals_per_game']:.1f}\n"
                if 'goals_conceded_per_game' in team2_stats:
                    stats_text += f"🥅 Conceded/Game: {team2_stats['goals_conceded_per_game']:.1f}\n"
                if 'clean_sheet_percentage' in team2_stats:
                    stats_text += f"🛡️ Clean Sheets: {team2_stats['clean_sheet_percentage']:.1f}%\n"
                if 'cards_per_game' in team2_stats:
                    stats_text += f"🟨 Cards/Game: {team2_stats['cards_per_game']:.1f}\n"
            
            return stats_text.strip()
            
        except Exception as e:
            self.logger.error(f"Error formatting advanced statistics: {e}")
            return "Unable to display advanced statistics"
    
    def _safe_get_field_value(self, value: Any, default: str = "TBD") -> str:
        """Safely get field value with fallback for missing data"""
        if value is None or value == "":
            return default
        return str(value)
    
    def create_match_preview_embed(self, match: ProcessedMatch) -> discord.Embed:
        """Create enhanced match preview embed with multi-league support and team standings"""
        try:
            # Get league-specific styling
            color = self._get_league_color(match.league)
            league_emoji = self._get_league_emoji(match.league)
            
            # Create embed with enhanced title
            title = f"{league_emoji} {match.away_team.name} vs {match.home_team.name}"
            if match.league.is_tournament and match.league.stage_name:
                title += f" - {match.league.stage_name}"
            
            embed = discord.Embed(
                title=title,
                color=color,
                timestamp=datetime.now()
            )
            
            # Add enhanced league and competition info
            league_info = f"{match.league.display_name}"
            if match.league.country and match.league.country != "Unknown":
                league_info += f" ({match.league.country})"
            if match.league.season:
                league_info += f"\n📅 Season: {match.league.season}"
            embed.add_field(name="🏆 Competition", value=league_info, inline=True)
            
            # Add match details
            match_date = self._safe_get_field_value(match.date, "TBD")
            match_time = self._safe_get_field_value(match.display_time, "TBD")
            embed.add_field(name="📅 Date", value=match_date, inline=True)
            embed.add_field(name="⏰ Time", value=match_time, inline=True)
            
            # Add venue information
            venue = self._safe_get_field_value(match.venue, "TBD")
            embed.add_field(name="🏟️ Venue", value=venue, inline=False)
            
            # Add enhanced team information with standings
            away_info = self._format_team_info_with_standings(match.away_team, "away")
            home_info = self._format_team_info_with_standings(match.home_team, "home")
            
            embed.add_field(name="✈️ Away Team", value=away_info, inline=True)
            embed.add_field(name="🏠 Home Team", value=home_info, inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)  # Spacer
            
            # Add league standings comparison if available
            if (match.home_team.standing and match.away_team.standing and 
                not match.league.is_tournament):
                standings_comparison = self._create_standings_comparison(
                    match.away_team, match.home_team
                )
                embed.add_field(name="📊 League Positions", value=standings_comparison, inline=False)
            
            # Add betting odds if available
            if match.odds and match.odds.has_odds:
                odds_text = self._create_odds_summary(match.odds)
                embed.add_field(name="💰 Betting Odds", value=odds_text, inline=False)
            
            # Add H2H summary if available
            if match.h2h_summary and match.h2h_summary.total_meetings > 0:
                h2h_text = self._create_h2h_summary_text(match.h2h_summary)
                embed.add_field(name="📊 Head-to-Head", value=h2h_text, inline=False)
            
            # Add match status with tournament context
            status_emoji = "🟢" if match.status == "scheduled" else "🔴"
            status_text = f"{status_emoji} {match.status.title()}"
            if match.league.is_tournament and match.league.stage:
                stage_config = UEFA_STAGE_MAPPINGS.get(match.league.stage, {})
                if stage_config:
                    status_text += f" {stage_config.get('emoji', '')}"
            embed.add_field(name="📋 Status", value=status_text, inline=True)
            
            # Set enhanced footer with league priority
            footer_text = f"Match ID: {match.match_id} | Priority: {match.league.priority} | Soccer Bot"
            embed.set_footer(text=footer_text)
            
            return embed
            
        except Exception as e:
            self.logger.error(f"Error creating match preview embed: {e}")
            return self._create_error_embed("Failed to create match preview", str(e))
    
    def _format_team_info_with_standings(self, team: Team, team_type: str) -> str:
        """
        Format team information with standings data
        
        Args:
            team: Team object with potential standings
            team_type: "home" or "away"
            
        Returns:
            Formatted team information string
        """
        info = f"**{team.name}**"
        
        # Add short name if different
        if team.short_name != team.name:
            info += f" ({team.short_name})"
        
        # Add country if available
        if team.country:
            info += f"\n🌍 {team.country}"
        
        # Add standings information if available
        if team.standing:
            info += f"\n📍 Position: {team.standing.position}"
            info += f"\n⚽ Points: {team.standing.points}"
            info += f"\n📊 Form: {team.form_display}"
            
            # Add goal difference for context
            if team.standing.goal_difference != 0:
                gd_sign = "+" if team.standing.goal_difference > 0 else ""
                info += f"\n🥅 GD: {gd_sign}{team.standing.goal_difference}"
        
        return info
    
    def _create_standings_comparison(self, away_team: Team, home_team: Team) -> str:
        """
        Create a comparison of team standings
        
        Args:
            away_team: Away team with standings
            home_team: Home team with standings
            
        Returns:
            Formatted standings comparison string
        """
        try:
            away_pos = away_team.standing.position if away_team.standing else "N/A"
            home_pos = home_team.standing.position if home_team.standing else "N/A"
            
            away_pts = away_team.standing.points if away_team.standing else 0
            home_pts = home_team.standing.points if home_team.standing else 0
            
            comparison = f"✈️ {away_team.short_name}: {away_pos} ({away_pts} pts)\n"
            comparison += f"🏠 {home_team.short_name}: {home_pos} ({home_pts} pts)"
            
            # Add position difference context
            if (away_team.standing and home_team.standing and 
                away_pos != "N/A" and home_pos != "N/A"):
                pos_diff = abs(int(away_pos) - int(home_pos))
                if pos_diff == 0:
                    comparison += "\n🤝 Teams level on position"
                elif pos_diff <= 3:
                    comparison += f"\n📏 Close in table ({pos_diff} positions apart)"
                else:
                    comparison += f"\n📏 {pos_diff} positions apart"
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Error creating standings comparison: {e}")
            return "Standings comparison unavailable"
    
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
            
            # Add advanced statistics if available
            if h2h_data.key_statistics and not h2h_data.key_statistics.get('error'):
                stats_text = self._format_advanced_statistics(h2h_data.key_statistics, team1.name, team2.name)
                if stats_text:
                    embed.add_field(name="📊 Advanced Metrics", value=stats_text[:1024], inline=False)
            
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
        """Create a summary of betting odds for match preview"""
        summary_parts = []
        
        if odds.home_win and odds.away_win and odds.draw:
            summary_parts.append(f"1X2: {odds.home_win.decimal:.2f} / {odds.draw.decimal:.2f} / {odds.away_win.decimal:.2f}")
        
        if odds.over_under:
            summary_parts.append(f"O/U {odds.over_under.line}: {odds.over_under.over_odds.decimal:.2f} / {odds.over_under.under_odds.decimal:.2f}")
        
        if odds.both_teams_score:
            summary_parts.append(f"BTTS: {odds.both_teams_score.decimal:.2f}")
        
        return "\n".join(summary_parts) if summary_parts else "Limited odds available"
    
    def _create_h2h_summary_text(self, h2h_summary: H2HSummary) -> str:
        """Create a brief H2H summary for match preview"""
        if h2h_summary.total_meetings == 0:
            return "No previous meetings"
        
        summary = f"Last {h2h_summary.total_meetings} meetings: "
        summary += f"{h2h_summary.home_team_wins}W-{h2h_summary.draws}D-{h2h_summary.away_team_wins}L"
        
        if h2h_summary.last_meeting_result:
            summary += f"\nLast result: {h2h_summary.last_meeting_result}"
        
        return summary
    
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
    'SoccerDataProcessor',
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
    'SUPPORTED_LEAGUES'
]