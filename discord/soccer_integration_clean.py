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