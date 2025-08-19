"""
SoccerEmbedBuilder - Creates rich Discord embeds for soccer content with dual-endpoint analysis
Matches schedule.py output format for comprehensive match analysis
"""

import discord
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# Enhanced data models for dual-endpoint analysis
from dataclasses import dataclass, field

# Temporary definitions - these should come from soccer_integration
SUPPORTED_LEAGUES = {
    "EPL": {
        "id": 228,
        "name": "Premier League",
        "country": "England",
        "color": 0x3d195b,
        "emoji": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"
    },
    "La Liga": {
        "id": 297,
        "name": "La Liga",
        "country": "Spain", 
        "color": 0xff6900,
        "emoji": "🇪🇸"
    }
}

@dataclass
class OddsFormat:
    decimal: float
    american: int
    
    @classmethod
    def from_decimal(cls, decimal_odds: float):
        american = int((decimal_odds - 1) * 100) if decimal_odds >= 2.0 else int(-100 / (decimal_odds - 1))
        return cls(decimal=decimal_odds, american=american)

@dataclass
class OverUnder:
    line: float
    over_odds: OddsFormat
    under_odds: OddsFormat

@dataclass
class Handicap:
    line: float
    home_odds: OddsFormat
    away_odds: OddsFormat

@dataclass
class BettingOdds:
    home_win: Optional[OddsFormat] = None
    draw: Optional[OddsFormat] = None
    away_win: Optional[OddsFormat] = None
    over_under: Optional[OverUnder] = None
    handicap: Optional[Handicap] = None
    both_teams_score: Optional[OddsFormat] = None
    
    @property
    def has_odds(self) -> bool:
        return any([self.home_win, self.draw, self.away_win])

@dataclass
class Team:
    id: int
    name: str
    short_name: str
    logo_url: Optional[str] = None
    country: Optional[str] = None

@dataclass
class League:
    id: int
    name: str
    country: str
    season: Optional[str] = None
    logo_url: Optional[str] = None
    
    @property
    def config(self) -> Optional[Dict]:
        for key, config in SUPPORTED_LEAGUES.items():
            if config["id"] == self.id:
                return config
        return None

@dataclass
class H2HSummary:
    total_meetings: int
    home_team_wins: int
    away_team_wins: int
    draws: int
    last_meeting_result: Optional[str] = None

@dataclass
class H2HInsights:
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
        if self.total_meetings == 0:
            return 0.0
        return (self.home_team_wins / self.total_meetings) * 100
    
    @property
    def away_win_percentage(self) -> float:
        if self.total_meetings == 0:
            return 0.0
        return (self.away_team_wins / self.total_meetings) * 100
    
    @property
    def draw_percentage(self) -> float:
        if self.total_meetings == 0:
            return 0.0
        return (self.draws / self.total_meetings) * 100

# Enhanced data models for dual-endpoint analysis
@dataclass
class H2HHistoricalRecord:
    """Direct head-to-head historical record from H2H endpoint"""
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
        return (self.home_team_wins / self.total_meetings * 100) if self.total_meetings > 0 else 0.0
    
    @property
    def away_win_percentage(self) -> float:
        return (self.away_team_wins / self.total_meetings * 100) if self.total_meetings > 0 else 0.0
    
    @property
    def draw_percentage(self) -> float:
        return (self.draws / self.total_meetings * 100) if self.total_meetings > 0 else 0.0

@dataclass
class TeamAnalysis:
    """Individual team analysis from matches endpoint (recent 10 matches)"""
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
    advanced_metrics: Dict[str, Any]  # Early goals, late drama, comeback wins, etc.
    
    @property
    def win_percentage(self) -> float:
        total_games = sum(self.form_record.values())
        return (self.form_record["wins"] / total_games * 100) if total_games > 0 else 0.0

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

@dataclass
class ProcessedMatch:
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
    
    # New fields for dual-endpoint analysis
    h2h_historical_record: Optional[H2HHistoricalRecord] = None
    home_team_analysis: Optional[TeamAnalysis] = None
    away_team_analysis: Optional[TeamAnalysis] = None
    comprehensive_insights: Optional[ComprehensiveInsights] = None
    
    @property
    def display_time(self) -> str:
        try:
            from datetime import datetime
            time_obj = datetime.strptime(self.time, "%H:%M")
            return time_obj.strftime("%I:%M %p")
        except ValueError:
            return self.time

class SoccerDataProcessor:
    def extract_betting_insights(self, odds: BettingOdds) -> List[str]:
        return ["Sample insight"]


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
        Includes both decimal and American formats to match schedule.py output
        
        Args:
            odds: BettingOdds object
            
        Returns:
            Formatted odds summary string with both decimal and American formats
        """
        summary_parts = []
        
        if odds.home_win and odds.away_win and odds.draw:
            home_formatted = self._format_odds(odds.home_win)
            draw_formatted = self._format_odds(odds.draw)
            away_formatted = self._format_odds(odds.away_win)
            summary_parts.append(f"1X2: {home_formatted} / {draw_formatted} / {away_formatted}")
        
        if odds.over_under:
            over_formatted = self._format_odds(odds.over_under.over_odds)
            under_formatted = self._format_odds(odds.over_under.under_odds)
            summary_parts.append(f"O/U {odds.over_under.line}: {over_formatted} / {under_formatted}")
        
        if odds.both_teams_score:
            btts_formatted = self._format_odds(odds.both_teams_score)
            summary_parts.append(f"BTTS: {btts_formatted}")
        
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
    
    def create_h2h_historical_record_embed(self, h2h_record: H2HHistoricalRecord, 
                                          home_team: Team, away_team: Team, league: League) -> discord.Embed:
        """
        Create H2H historical record embed displaying H2H endpoint data
        
        Args:
            h2h_record: H2HHistoricalRecord from H2H endpoint
            home_team: Home team object
            away_team: Away team object
            league: League object for styling
            
        Returns:
            Discord embed with H2H historical record
        """
        try:
            if not h2h_record or h2h_record.total_meetings == 0:
                return self._create_error_embed("No H2H History", "No historical meetings found between these teams")
            
            # Get league-specific styling
            color = self._get_league_color(league)
            league_emoji = self._get_league_emoji(league)
            
            # Create embed
            title = f"{league_emoji} Historical H2H Record"
            embed = discord.Embed(
                title=title,
                description=f"**{away_team.name}** vs **{home_team.name}**",
                color=color,
                timestamp=datetime.now()
            )
            
            # Overall record section
            record_text = (
                f"📊 **Total Meetings**: {h2h_record.total_meetings}\n"
                f"🏠 **{home_team.name} Wins**: {h2h_record.home_team_wins} ({h2h_record.home_win_percentage:.1f}%)\n"
                f"✈️ **{away_team.name} Wins**: {h2h_record.away_team_wins} ({h2h_record.away_win_percentage:.1f}%)\n"
                f"🤝 **Draws**: {h2h_record.draws} ({h2h_record.draw_percentage:.1f}%)"
            )
            embed.add_field(name="📈 Overall Record", value=record_text, inline=False)
            
            # Goals analysis
            goals_text = (
                f"⚽ **Average Goals per Game**: {h2h_record.avg_goals_per_game:.2f}\n"
                f"🏠 **{home_team.name} Total Goals**: {h2h_record.home_team_goals_total} ({h2h_record.home_team_goals_total/h2h_record.total_meetings:.1f} per game)\n"
                f"✈️ **{away_team.name} Total Goals**: {h2h_record.away_team_goals_total} ({h2h_record.away_team_goals_total/h2h_record.total_meetings:.1f} per game)"
            )
            embed.add_field(name="🎯 Goals Analysis", value=goals_text, inline=False)
            
            # Last meeting info
            if h2h_record.last_meeting_date and h2h_record.last_meeting_result:
                last_meeting_text = (
                    f"📅 **Date**: {h2h_record.last_meeting_date}\n"
                    f"🏆 **Result**: {h2h_record.last_meeting_result}"
                )
                embed.add_field(name="🕐 Last Meeting", value=last_meeting_text, inline=True)
            
            # Historical trend analysis
            if h2h_record.home_win_percentage >= 60:
                trend = f"🏠 {home_team.name} dominates this matchup"
                trend_color = "🟢"
            elif h2h_record.away_win_percentage >= 60:
                trend = f"✈️ {away_team.name} dominates this matchup"
                trend_color = "🔴"
            elif h2h_record.draw_percentage >= 40:
                trend = "🤝 High tendency for draws"
                trend_color = "🟡"
            else:
                trend = "⚖️ Evenly matched historically"
                trend_color = "🔵"
            
            embed.add_field(name="📊 Historical Trend", value=f"{trend_color} {trend}", inline=False)
            
            # Betting insights based on H2H data
            betting_insights = []
            
            if h2h_record.avg_goals_per_game > 2.8:
                betting_insights.append("💡 **Over 2.5 Goals** - High-scoring history")
            elif h2h_record.avg_goals_per_game < 2.2:
                betting_insights.append("💡 **Under 2.5 Goals** - Low-scoring history")
            
            if h2h_record.draw_percentage >= 30:
                betting_insights.append("💡 **Draw** - Frequent stalemates")
            
            if h2h_record.home_win_percentage >= 60:
                betting_insights.append(f"💡 **{home_team.name} Win** - Strong home dominance")
            elif h2h_record.away_win_percentage >= 60:
                betting_insights.append(f"💡 **{away_team.name} Win** - Strong away record")
            
            if betting_insights:
                embed.add_field(name="🎲 H2H Betting Insights", value="\n".join(betting_insights), inline=False)
            
            embed.set_footer(text="H2H Analysis | Historical data from direct meetings")
            
            return embed
            
        except Exception as e:
            self.logger.error(f"Error creating H2H historical record embed: {e}")
            return self._create_error_embed("H2H Analysis Error", str(e))
    
    def create_team_analysis_embed(self, team_analysis: TeamAnalysis, team: Team, league: League, 
                                  is_home: bool = True) -> discord.Embed:
        """
        Create team analysis embed for individual team analysis from matches endpoint
        Matches schedule.py comprehensive team analysis format
        
        Args:
            team_analysis: TeamAnalysis from matches endpoint (recent 10 matches)
            team: Team object
            league: League object for styling
            is_home: Whether this is the home team (affects emoji and positioning)
            
        Returns:
            Discord embed with comprehensive team analysis
        """
        try:
            if not team_analysis or team_analysis.recent_matches_count == 0:
                return self._create_error_embed("No Team Data", f"No recent match data available for {team.name}")
            
            # Get league-specific styling
            color = self._get_league_color(league)
            league_emoji = self._get_league_emoji(league)
            
            # Create embed with team-specific title
            venue_emoji = "🏠" if is_home else "✈️"
            title = f"{league_emoji} {venue_emoji} {team.name} Analysis"
            embed = discord.Embed(
                title=title,
                description=f"Recent {team_analysis.recent_matches_count} matches analysis",
                color=color,
                timestamp=datetime.now()
            )
            
            # Basic form summary (matching schedule.py format)
            total_games = team_analysis.recent_matches_count
            wins = team_analysis.form_record.get("wins", 0)
            draws = team_analysis.form_record.get("draws", 0)
            losses = team_analysis.form_record.get("losses", 0)
            
            form_text = (
                f"📊 **Record**: {wins}W-{draws}D-{losses}L ({team_analysis.win_percentage:.1f}% win rate)\n"
                f"📈 **Form**: {team_analysis.form_string}\n"
                f"⚽ **Goals per game**: {team_analysis.goals_per_game:.1f} for, {team_analysis.goals_against_per_game:.1f} against"
            )
            embed.add_field(name="📋 Basic Form Summary", value=form_text, inline=False)
            
            # Advanced metrics (matching schedule.py comprehensive analysis)
            advanced_text = ""
            
            # Clean sheets and defensive stats
            clean_sheet_pct = team_analysis.clean_sheet_percentage
            advanced_text += f"🛡️ **Clean sheets**: {clean_sheet_pct:.1f}%\n"
            
            # Both teams scored patterns
            btts_pct = team_analysis.btts_percentage
            advanced_text += f"⚽ **Both teams scored**: {btts_pct:.1f}%\n"
            
            # High scoring games
            high_scoring_pct = team_analysis.high_scoring_percentage
            advanced_text += f"🎯 **High scoring (3+ goals)**: {high_scoring_pct:.1f}%"
            
            embed.add_field(name="📊 Advanced Metrics", value=advanced_text, inline=True)
            
            # Card discipline (matching schedule.py format)
            card_text = ""
            yellow_per_game = team_analysis.card_discipline.get("yellow_per_game", 0)
            red_total = team_analysis.card_discipline.get("red_total", 0)
            
            card_text += f"🟨 **Yellow cards per game**: {yellow_per_game:.1f}\n"
            card_text += f"🟥 **Red cards total**: {red_total}"
            
            embed.add_field(name="🃏 Card Discipline", value=card_text, inline=True)
            
            # Advanced patterns from comprehensive data (schedule.py style)
            patterns_text = ""
            
            # Early/late goal patterns
            early_goals = team_analysis.advanced_metrics.get("early_goals_frequency", 0)
            late_goals = team_analysis.advanced_metrics.get("late_goals_frequency", 0)
            
            if early_goals > 0.3:  # 30% of games
                patterns_text += "⏰ **Early goals** (0-15min) frequent\n"
            if late_goals > 0.3:
                patterns_text += "🕐 **Late drama** (75+min) frequent\n"
            
            # Comeback patterns
            comeback_frequency = team_analysis.advanced_metrics.get("comeback_wins", 0)
            if comeback_frequency > 0:
                patterns_text += f"🔄 **Comeback wins**: {comeback_frequency}\n"
            
            # Home vs away splits
            home_performance = team_analysis.advanced_metrics.get("home_win_rate", 0)
            away_performance = team_analysis.advanced_metrics.get("away_win_rate", 0)
            
            if home_performance > 0 and away_performance > 0:
                if abs(home_performance - away_performance) > 20:  # Significant difference
                    if home_performance > away_performance:
                        patterns_text += "🏠 **Much stronger at home**\n"
                    else:
                        patterns_text += "✈️ **Better away from home**\n"
            
            if patterns_text:
                embed.add_field(name="🔍 Key Patterns", value=patterns_text.strip(), inline=False)
            
            # Betting insights from team data (schedule.py methodology)
            betting_insights = []
            
            # Goals market insights
            if team_analysis.goals_per_game > 2.0:
                betting_insights.append("💡 **Strong Attack** - Excellent goal scoring form")
            elif team_analysis.goals_per_game < 1.0:
                betting_insights.append("💡 **Weak Attack** - Struggling to find the net")
            
            if team_analysis.goals_against_per_game < 1.0:
                betting_insights.append("💡 **Solid Defense** - Very tight at the back")
            elif team_analysis.goals_against_per_game > 2.0:
                betting_insights.append("💡 **Leaky Defense** - Conceding too easily")
            
            # BTTS insights
            if btts_pct > 60:
                betting_insights.append("💡 **BTTS Yes** - Both teams score frequently")
            elif btts_pct < 30:
                betting_insights.append("💡 **BTTS No** - Often one-sided games")
            
            # Over/Under insights
            if high_scoring_pct > 60:
                betting_insights.append("💡 **Over 2.5** - Frequently in high-scoring games")
            elif high_scoring_pct < 30:
                betting_insights.append("💡 **Under 2.5** - Often in low-scoring affairs")
            
            # Cards market insights
            total_cards_per_game = yellow_per_game + (red_total / total_games if total_games > 0 else 0)
            if total_cards_per_game > 4:
                betting_insights.append("💡 **Cards Market** - High card count team")
            
            # Late drama insights
            if late_goals > 0.6:
                betting_insights.append("💡 **Late Drama** - Frequent late goals (good for in-play)")
            
            if betting_insights:
                embed.add_field(name="🎲 Team Betting Insights", value="\n".join(betting_insights[:4]), inline=False)
            
            # Performance summary
            performance_summary = ""
            if team_analysis.win_percentage >= 60:
                performance_summary = "🟢 **Excellent form** - Strong recent performances"
            elif team_analysis.win_percentage >= 40:
                performance_summary = "🟡 **Decent form** - Mixed recent results"
            else:
                performance_summary = "🔴 **Poor form** - Struggling recently"
            
            embed.add_field(name="📈 Current Form Assessment", value=performance_summary, inline=False)
            
            embed.set_footer(text=f"Team Analysis | Based on last {total_games} matches")
            
            return embed
            
        except Exception as e:
            self.logger.error(f"Error creating team analysis embed: {e}")
            return self._create_error_embed("Team Analysis Error", str(e))
            
            # Overall record
            record_text = (
                f"📊 **Total Meetings**: {h2h_record.total_meetings}\n"
                f"🏠 **{home_team.name} Wins**: {h2h_record.home_team_wins} ({h2h_record.home_win_percentage:.1f}%)\n"
                f"✈️ **{away_team.name} Wins**: {h2h_record.away_team_wins} ({h2h_record.away_win_percentage:.1f}%)\n"
                f"🤝 **Draws**: {h2h_record.draws} ({h2h_record.draw_percentage:.1f}%)"
            )
            embed.add_field(name="📈 Head-to-Head Record", value=record_text, inline=False)
            
            # Goals statistics
            goals_text = (
                f"⚽ **Total Goals**: {h2h_record.home_team_goals_total + h2h_record.away_team_goals_total}\n"
                f"🏠 **{home_team.name} Goals**: {h2h_record.home_team_goals_total}\n"
                f"✈️ **{away_team.name} Goals**: {h2h_record.away_team_goals_total}\n"
                f"📊 **Average Goals/Game**: {h2h_record.avg_goals_per_game:.2f}"
            )
            embed.add_field(name="🎯 Historical Goals", value=goals_text, inline=True)
            
            # Last meeting info
            if h2h_record.last_meeting_date and h2h_record.last_meeting_result:
                last_meeting_text = (
                    f"📅 **Date**: {h2h_record.last_meeting_date}\n"
                    f"🏆 **Result**: {h2h_record.last_meeting_result}"
                )
                embed.add_field(name="🕐 Last Meeting", value=last_meeting_text, inline=True)
            
            # Dominance analysis
            if h2h_record.home_win_percentage >= 60:
                dominance = f"🏠 {home_team.name} dominates this fixture"
            elif h2h_record.away_win_percentage >= 60:
                dominance = f"✈️ {away_team.name} dominates this fixture"
            elif h2h_record.draw_percentage >= 40:
                dominance = "🤝 High tendency for draws in this matchup"
            else:
                dominance = "⚖️ Evenly matched historically"
            
            embed.add_field(name="📊 Historical Trend", value=dominance, inline=False)
            
            embed.set_footer(text="H2H Historical Record | Direct head-to-head data")
            
            return embed
            
        except Exception as e:
            self.logger.error(f"Error creating H2H historical record embed: {e}")
            return self._create_error_embed("H2H Record Error", str(e))
    
    def create_team_analysis_embed(self, team_analysis: TeamAnalysis, team: Team, 
                                 league: League, is_home: bool = True) -> discord.Embed:
        """
        Create team analysis embed for individual team analysis from matches endpoint
        
        Args:
            team_analysis: TeamAnalysis from matches endpoint
            team: Team object
            league: League object for styling
            is_home: Whether this is the home team
            
        Returns:
            Discord embed with team analysis
        """
        try:
            if not team_analysis or team_analysis.recent_matches_count == 0:
                return self._create_error_embed("No Team Data", f"No recent match data found for {team.name}")
            
            # Get league-specific styling
            color = self._get_league_color(league)
            league_emoji = self._get_league_emoji(league)
            
            # Create embed
            venue_emoji = "🏠" if is_home else "✈️"
            title = f"{league_emoji} {venue_emoji} {team.name} Analysis"
            embed = discord.Embed(
                title=title,
                description=f"Recent {team_analysis.recent_matches_count} matches analysis",
                color=color,
                timestamp=datetime.now()
            )
            
            # Basic form summary
            form_text = (
                f"📊 **Record**: {team_analysis.form_record['wins']}W-{team_analysis.form_record['draws']}D-{team_analysis.form_record['losses']}L\n"
                f"📈 **Win Rate**: {team_analysis.win_percentage:.1f}%\n"
                f"🔥 **Form**: {team_analysis.form_string}\n"
                f"🎯 **Matches Analyzed**: {team_analysis.recent_matches_count}"
            )
            embed.add_field(name="📋 Recent Form", value=form_text, inline=False)
            
            # Goals analysis
            goals_text = (
                f"⚽ **Goals per Game**: {team_analysis.goals_per_game:.2f}\n"
                f"🥅 **Goals Against per Game**: {team_analysis.goals_against_per_game:.2f}\n"
                f"🛡️ **Clean Sheets**: {team_analysis.clean_sheet_percentage:.1f}%\n"
                f"🎯 **Both Teams Score**: {team_analysis.btts_percentage:.1f}%"
            )
            embed.add_field(name="🎯 Goals & Defense", value=goals_text, inline=True)
            
            # Match patterns
            patterns_text = (
                f"🔥 **High Scoring (3+ goals)**: {team_analysis.high_scoring_percentage:.1f}%\n"
                f"📊 **Average Goals/Game**: {team_analysis.goals_per_game + team_analysis.goals_against_per_game:.2f}"
            )
            
            # Add advanced metrics if available
            if team_analysis.advanced_metrics:
                if 'early_goals_percentage' in team_analysis.advanced_metrics:
                    patterns_text += f"\n⏰ **Early Goals (0-15min)**: {team_analysis.advanced_metrics['early_goals_percentage']:.1f}%"
                if 'late_drama_percentage' in team_analysis.advanced_metrics:
                    patterns_text += f"\n🕐 **Late Drama (75+min)**: {team_analysis.advanced_metrics['late_drama_percentage']:.1f}%"
            
            embed.add_field(name="📊 Match Patterns", value=patterns_text, inline=True)
            
            # Card discipline
            if team_analysis.card_discipline:
                cards_text = (
                    f"🟨 **Yellow Cards/Game**: {team_analysis.card_discipline.get('yellow_per_game', 0):.1f}\n"
                    f"🟥 **Red Cards Total**: {team_analysis.card_discipline.get('red_total', 0)}\n"
                    f"📊 **Total Cards/Game**: {team_analysis.card_discipline.get('total_per_game', 0):.1f}"
                )
                embed.add_field(name="🃏 Discipline", value=cards_text, inline=False)
            
            # Advanced insights
            insights = []
            if team_analysis.goals_per_game > 2.0:
                insights.append("🔥 **Strong Attack** - Excellent scoring form")
            elif team_analysis.goals_per_game < 1.0:
                insights.append("❄️ **Weak Attack** - Struggling to score")
            
            if team_analysis.goals_against_per_game < 1.0:
                insights.append("🛡️ **Solid Defense** - Very tight at the back")
            elif team_analysis.goals_against_per_game > 2.0:
                insights.append("🕳️ **Leaky Defense** - Conceding too easily")
            
            if team_analysis.btts_percentage > 60:
                insights.append("⚽ **BTTS Friendly** - Both teams often score")
            elif team_analysis.btts_percentage < 30:
                insights.append("🚫 **BTTS Unfriendly** - Often one-sided games")
            
            if team_analysis.high_scoring_percentage > 60:
                insights.append("📈 **High Scoring** - Frequently in 3+ goal games")
            elif team_analysis.high_scoring_percentage < 30:
                insights.append("📉 **Low Scoring** - Often in tight, low-scoring affairs")
            
            if insights:
                embed.add_field(name="💡 Key Insights", value="\n".join(insights), inline=False)
            
            embed.set_footer(text=f"Team Analysis | Based on recent {team_analysis.recent_matches_count} matches")
            
            return embed
            
        except Exception as e:
            self.logger.error(f"Error creating team analysis embed: {e}")
            return self._create_error_embed("Team Analysis Error", str(e))
    
    def create_comprehensive_betting_insights_embed(self, insights: ComprehensiveInsights, 
                                                  home_team: Team, away_team: Team, 
                                                  league: League,
                                                  h2h_record: Optional[H2HHistoricalRecord] = None,
                                                  home_analysis: Optional[TeamAnalysis] = None,
                                                  away_analysis: Optional[TeamAnalysis] = None) -> discord.Embed:
        """
        Create comprehensive betting insights embed combining H2H patterns with team form
        Matches schedule.py enhanced betting recommendations methodology
        
        Args:
            insights: ComprehensiveInsights combining all data sources
            home_team: Home team object
            away_team: Away team object
            league: League object for styling
            h2h_record: Optional H2H historical record for additional context
            home_analysis: Optional home team analysis for additional context
            away_analysis: Optional away team analysis for additional context
            
        Returns:
            Discord embed with comprehensive betting recommendations
        """
        try:
            if not insights:
                return self._create_error_embed("No Betting Insights", "Unable to generate betting recommendations")
            
            # Get league-specific styling
            color = self._get_league_color(league)
            league_emoji = self._get_league_emoji(league)
            
            # Create embed
            title = f"{league_emoji} 🎲 Comprehensive Betting Insights"
            embed = discord.Embed(
                title=title,
                description=f"**{away_team.name}** @ **{home_team.name}**\nCombining H2H history + current form",
                color=color,
                timestamp=datetime.now()
            )
            
            # Primary betting recommendations (schedule.py style)
            primary_recs = []
            
            # Over/Under recommendation with confidence
            ou_rec = insights.over_under_recommendation
            if ou_rec != "Neutral":
                confidence_emoji = self._get_confidence_emoji(insights.confidence_level)
                primary_recs.append(f"{confidence_emoji} **{ou_rec}** Goals")
            
            # BTTS recommendation
            btts_rec = insights.btts_recommendation
            if btts_rec != "Neutral":
                confidence_emoji = self._get_confidence_emoji(insights.confidence_level)
                primary_recs.append(f"{confidence_emoji} **{btts_rec}**")
            
            # Match outcome lean
            outcome_lean = insights.match_outcome_lean
            if outcome_lean != "Neutral":
                confidence_emoji = self._get_confidence_emoji(insights.confidence_level)
                primary_recs.append(f"{confidence_emoji} **{outcome_lean}**")
            
            if primary_recs:
                embed.add_field(name="🎯 Primary Recommendations", value="\n".join(primary_recs), inline=False)
            
            # Market analysis breakdown (schedule.py methodology)
            market_analysis = ""
            
            # Goals market analysis
            expected_goals = insights.expected_goals_total
            market_analysis += f"⚽ **Expected Total Goals**: {expected_goals:.1f}\n"
            
            if expected_goals > 2.8:
                market_analysis += "📈 **Over 2.5 Goals** favored by data\n"
            elif expected_goals < 2.2:
                market_analysis += "📉 **Under 2.5 Goals** favored by data\n"
            else:
                market_analysis += "⚖️ **Goals market** close to line\n"
            
            # BTTS probability
            btts_prob = insights.btts_probability
            market_analysis += f"🥅 **BTTS Probability**: {btts_prob:.1f}%\n"
            
            if btts_prob > 65:
                market_analysis += "✅ **BTTS Yes** strongly indicated\n"
            elif btts_prob < 35:
                market_analysis += "❌ **BTTS No** strongly indicated\n"
            
            embed.add_field(name="📊 Market Analysis", value=market_analysis.strip(), inline=True)
            
            # Form momentum analysis
            momentum_text = ""
            form_momentum = insights.form_momentum
            
            if form_momentum == "home_advantage":
                momentum_text += f"🏠 **{home_team.name}** has form advantage\n"
            elif form_momentum == "away_advantage":
                momentum_text += f"✈️ **{away_team.name}** has form advantage\n"
            else:
                momentum_text += "⚖️ **Balanced** form between teams\n"
            
            # H2H dominance
            h2h_dominance = insights.h2h_dominance
            if h2h_dominance == "home_team":
                momentum_text += f"📈 **{home_team.name}** dominates H2H\n"
            elif h2h_dominance == "away_team":
                momentum_text += f"📈 **{away_team.name}** dominates H2H\n"
            else:
                momentum_text += "📊 **Balanced** H2H record\n"
            
            # Goals trend
            h2h_goals_trend = insights.h2h_goals_trend
            if h2h_goals_trend == "high_scoring":
                momentum_text += "🎯 **High-scoring** H2H history"
            elif h2h_goals_trend == "low_scoring":
                momentum_text += "🛡️ **Low-scoring** H2H history"
            else:
                momentum_text += "📊 **Average** H2H scoring"
            
            embed.add_field(name="📈 Form & H2H Momentum", value=momentum_text, inline=True)
            
            # Specialized markets (schedule.py advanced insights)
            specialized_markets = []
            
            # Cards market
            cards_insight = insights.cards_market_insight
            if cards_insight != "Average":
                if cards_insight == "High Cards":
                    specialized_markets.append("🟨 **Over 4.5 Cards** - High card count expected")
                elif cards_insight == "Low Cards":
                    specialized_markets.append("🟨 **Under 3.5 Cards** - Disciplined teams")
            
            # Add team-specific insights if available
            if home_analysis and away_analysis:
                # Halftime/Fulltime patterns
                home_early = home_analysis.advanced_metrics.get("early_goals_frequency", 0)
                away_early = away_analysis.advanced_metrics.get("early_goals_frequency", 0)
                
                if home_early > 0.4 or away_early > 0.4:
                    specialized_markets.append("⏰ **First Goal Under 15.5 min** - Early goal pattern")
                
                # Late drama patterns
                home_late = home_analysis.advanced_metrics.get("late_goals_frequency", 0)
                away_late = away_analysis.advanced_metrics.get("late_goals_frequency", 0)
                
                if home_late > 0.5 or away_late > 0.5:
                    specialized_markets.append("🕐 **Goal in 75-90 min** - Late drama teams")
                
                # Clean sheet patterns
                if home_analysis.clean_sheet_percentage > 50 and away_analysis.goals_per_game < 1.2:
                    specialized_markets.append(f"🛡️ **{home_team.name} Clean Sheet** - Strong defense vs weak attack")
                elif away_analysis.clean_sheet_percentage > 50 and home_analysis.goals_per_game < 1.2:
                    specialized_markets.append(f"🛡️ **{away_team.name} Clean Sheet** - Strong defense vs weak attack")
            
            if specialized_markets:
                embed.add_field(name="🎲 Specialized Markets", value="\n".join(specialized_markets[:3]), inline=False)
            
            # Supporting evidence (schedule.py reasoning)
            if insights.recommendation_reasoning:
                evidence_text = "\n".join([f"• {reason}" for reason in insights.recommendation_reasoning[:4]])
                embed.add_field(name="📋 Supporting Evidence", value=evidence_text, inline=False)
            
            # Confidence and risk assessment
            confidence_level = insights.confidence_level
            confidence_text = f"📊 **Analysis Confidence**: {confidence_level}\n"
            
            if confidence_level == "High":
                confidence_text += "✅ Strong data convergence across all sources"
            elif confidence_level == "Medium":
                confidence_text += "⚠️ Mixed signals - proceed with caution"
            else:
                confidence_text += "❌ Limited data - high risk recommendations"
            
            embed.add_field(name="🎯 Confidence Assessment", value=confidence_text, inline=False)
            
            # Disclaimer
            embed.add_field(
                name="⚠️ Important Disclaimer",
                value="Analysis based on historical data and recent form. Always gamble responsibly and within your means.",
                inline=False
            )
            
            embed.set_footer(text="Comprehensive Analysis | H2H + Team Form + Advanced Metrics")
            
            return embed
            
        except Exception as e:
            self.logger.error(f"Error creating comprehensive betting insights embed: {e}")
            return self._create_error_embed("Betting Insights Error", str(e))
    
    def _get_confidence_emoji(self, confidence_level: str) -> str:
        """Get emoji for confidence level"""
        confidence_emojis = {
            "High": "🟢",
            "Medium": "🟡", 
            "Low": "🔴"
        }
        return confidence_emojis.get(confidence_level, "⚪")
    
    def create_comprehensive_analysis_embed_set(self, match: ProcessedMatch) -> List[discord.Embed]:
        """
        Generate all 4-5 embeds for a match using dual-endpoint data
        Matches schedule.py output format with graceful degradation for missing data
        
        Args:
            match: ProcessedMatch with all dual-endpoint data populated
            
        Returns:
            List of Discord embeds for comprehensive analysis (4-5 embeds)
        """
        try:
            embeds = []
            missing_data_warnings = []
            
            # 1. Match Preview Embed (always first - basic match info)
            try:
                match_preview = self.create_match_preview_embed(match)
                embeds.append(match_preview)
            except Exception as e:
                self.logger.error(f"Error creating match preview embed: {e}")
                # Create minimal fallback embed
                fallback_embed = discord.Embed(
                    title=f"⚽ {match.away_team.name} vs {match.home_team.name}",
                    description="Match preview unavailable",
                    color=0x00ff00
                )
                embeds.append(fallback_embed)
            
            # 2. H2H Historical Record Embed (if H2H endpoint data available)
            if match.h2h_historical_record and match.h2h_historical_record.total_meetings > 0:
                try:
                    h2h_embed = self.create_h2h_historical_record_embed(
                        match.h2h_historical_record,
                        match.home_team,
                        match.away_team,
                        match.league
                    )
                    embeds.append(h2h_embed)
                except Exception as e:
                    self.logger.error(f"Error creating H2H embed: {e}")
                    missing_data_warnings.append("H2H historical analysis")
            else:
                missing_data_warnings.append("H2H historical data")
            
            # 3. Home Team Analysis Embed (if matches endpoint data available)
            if match.home_team_analysis and match.home_team_analysis.recent_matches_count > 0:
                try:
                    home_analysis = self.create_team_analysis_embed(
                        match.home_team_analysis,
                        match.home_team,
                        match.league,
                        is_home=True
                    )
                    embeds.append(home_analysis)
                except Exception as e:
                    self.logger.error(f"Error creating home team analysis embed: {e}")
                    missing_data_warnings.append(f"{match.home_team.name} team analysis")
            else:
                missing_data_warnings.append(f"{match.home_team.name} recent matches data")
            
            # 4. Away Team Analysis Embed (if matches endpoint data available)
            if match.away_team_analysis and match.away_team_analysis.recent_matches_count > 0:
                try:
                    away_analysis = self.create_team_analysis_embed(
                        match.away_team_analysis,
                        match.away_team,
                        match.league,
                        is_home=False
                    )
                    embeds.append(away_analysis)
                except Exception as e:
                    self.logger.error(f"Error creating away team analysis embed: {e}")
                    missing_data_warnings.append(f"{match.away_team.name} team analysis")
            else:
                missing_data_warnings.append(f"{match.away_team.name} recent matches data")
            
            # 5. Comprehensive Betting Insights Embed (if comprehensive insights available)
            if match.comprehensive_insights:
                try:
                    betting_insights = self.create_comprehensive_betting_insights_embed(
                        match.comprehensive_insights,
                        match.home_team,
                        match.away_team,
                        match.league,
                        h2h_record=match.h2h_historical_record,
                        home_analysis=match.home_team_analysis,
                        away_analysis=match.away_team_analysis
                    )
                    embeds.append(betting_insights)
                except Exception as e:
                    self.logger.error(f"Error creating betting insights embed: {e}")
                    missing_data_warnings.append("comprehensive betting insights")
            else:
                missing_data_warnings.append("comprehensive analysis data")
            
            # Add missing data warning embed if there are significant gaps
            if len(missing_data_warnings) >= 3:  # If more than half the data is missing
                warning_embed = self._create_missing_data_warning_embed(
                    missing_data_warnings, 
                    match.home_team.name, 
                    match.away_team.name,
                    match.league
                )
                embeds.append(warning_embed)
            
            # Add embed numbering and data source indicators for clarity
            for i, embed in enumerate(embeds, 1):
                current_footer = embed.footer.text if embed.footer else ""
                
                # Add data source indicators
                if i == 1:
                    source_indicator = "Basic Match Data"
                elif i == 2 and "H2H" in embed.title:
                    source_indicator = "H2H Endpoint Data"
                elif "Analysis" in embed.title and ("🏠" in embed.title or "✈️" in embed.title):
                    source_indicator = "Matches Endpoint Data"
                elif "Betting Insights" in embed.title:
                    source_indicator = "Combined Analysis"
                else:
                    source_indicator = "Soccer Bot"
                
                embed.set_footer(text=f"Embed {i}/{len(embeds)} | {source_indicator}")
            
            # Log successful embed generation
            self.logger.info(f"Generated {len(embeds)} embeds for match {match.match_id}")
            if missing_data_warnings:
                self.logger.warning(f"Missing data for: {', '.join(missing_data_warnings)}")
            
            return embeds
            
        except Exception as e:
            self.logger.error(f"Error creating comprehensive analysis embed set: {e}")
            # Return at least the match preview embed on error
            try:
                return [self.create_match_preview_embed(match)]
            except:
                # Ultimate fallback
                return [self._create_error_embed("Analysis Error", "Unable to generate match analysis")]
    
    def _create_missing_data_warning_embed(self, missing_items: List[str], 
                                         home_team: str, away_team: str, 
                                         league: League) -> discord.Embed:
        """
        Create warning embed for missing data with graceful degradation message
        
        Args:
            missing_items: List of missing data components
            home_team: Home team name
            away_team: Away team name
            league: League object for styling
            
        Returns:
            Discord embed with missing data warning
        """
        color = self._get_league_color(league)
        league_emoji = self._get_league_emoji(league)
        
        embed = discord.Embed(
            title=f"{league_emoji} ⚠️ Partial Analysis Available",
            description=f"**{away_team}** vs **{home_team}**",
            color=0xffa500,  # Orange for warning
            timestamp=datetime.now()
        )
        
        # List missing components
        missing_text = "The following analysis components are unavailable:\n"
        missing_text += "\n".join([f"• {item}" for item in missing_items[:5]])
        
        if len(missing_items) > 5:
            missing_text += f"\n• ... and {len(missing_items) - 5} more"
        
        embed.add_field(name="📋 Missing Data Components", value=missing_text, inline=False)
        
        # Explanation
        explanation = (
            "This may be due to:\n"
            "• Limited historical data for these teams\n"
            "• Recent team changes or new season\n"
            "• Temporary MCP server issues\n"
            "• Teams from lower leagues with less data coverage"
        )
        embed.add_field(name="💡 Possible Reasons", value=explanation, inline=False)
        
        # Available analysis note
        available_note = (
            "✅ Available analysis is still valuable and based on the best data sources accessible.\n"
            "📊 Consider this when making betting decisions."
        )
        embed.add_field(name="ℹ️ Note", value=available_note, inline=False)
        
        embed.set_footer(text="Graceful Degradation | Showing available data only")
        
        return embed
    
    def validate_embed_content_consistency(self, embeds: List[discord.Embed], 
                                         schedule_output: str) -> Dict[str, Any]:
        """
        Validate embed content against schedule.py console output for consistency
        Ensures Discord bot provides same analytical value as working schedule.py script
        
        Args:
            embeds: List of generated embeds
            schedule_output: Console output from schedule.py for comparison
            
        Returns:
            Dictionary with detailed validation results and consistency scores
        """
        try:
            validation_results = {
                "team_names_match": False,
                "odds_format_consistent": False,
                "h2h_data_consistent": False,
                "team_analysis_consistent": False,
                "betting_insights_similar": False,
                "advanced_metrics_present": False,
                "schedule_py_keywords_found": [],
                "missing_schedule_py_elements": [],
                "consistency_score": 0.0,
                "overall_consistency": False,
                "detailed_comparison": {}
            }
            
            # Extract embed content for comparison
            embed_content = ""
            embed_titles = []
            embed_fields = []
            
            for embed in embeds:
                embed_titles.append(embed.title or "")
                embed_content += f"{embed.title}\n"
                embed_content += f"{embed.description or ''}\n"
                for field in embed.fields:
                    field_content = f"{field.name}: {field.value}"
                    embed_fields.append(field_content)
                    embed_content += field_content + "\n"
            
            embed_content_lower = embed_content.lower()
            schedule_output_lower = schedule_output.lower()
            
            # 1. Team names consistency check
            team_vs_patterns = ["vs", "v ", "@"]
            if any(pattern in embed_content_lower for pattern in team_vs_patterns):
                validation_results["team_names_match"] = True
            
            # 2. Odds format consistency (decimal and American format like schedule.py)
            # Look for patterns like "2.50 (+150)" or "1.80 (-125)"
            import re
            decimal_american_pattern = r'\d+\.\d+\s*\([+-]\d+\)'
            if re.search(decimal_american_pattern, embed_content):
                validation_results["odds_format_consistent"] = True
            
            # 3. H2H data consistency - check for schedule.py H2H elements
            schedule_h2h_keywords = [
                "total meetings", "head-to-head", "h2h", "historical record",
                "wins", "draws", "losses", "win rate", "dominance"
            ]
            
            h2h_matches = 0
            for keyword in schedule_h2h_keywords:
                if keyword in embed_content_lower:
                    h2h_matches += 1
                    validation_results["schedule_py_keywords_found"].append(f"H2H: {keyword}")
            
            if h2h_matches >= 3:  # At least 3 H2H keywords found
                validation_results["h2h_data_consistent"] = True
            
            # 4. Team analysis consistency - check for schedule.py team analysis elements
            schedule_team_keywords = [
                "recent matches", "form", "goals per game", "clean sheet", 
                "card discipline", "yellow cards", "advanced metrics",
                "early goals", "late drama", "comeback", "btts", "high scoring"
            ]
            
            team_analysis_matches = 0
            for keyword in schedule_team_keywords:
                if keyword in embed_content_lower:
                    team_analysis_matches += 1
                    validation_results["schedule_py_keywords_found"].append(f"Team: {keyword}")
            
            if team_analysis_matches >= 4:  # At least 4 team analysis keywords found
                validation_results["team_analysis_consistent"] = True
            
            # 5. Betting insights similarity - check for schedule.py betting recommendations
            schedule_betting_keywords = [
                "over 2.5", "under 2.5", "btts yes", "btts no", "strong attack",
                "weak attack", "solid defense", "leaky defense", "cards market",
                "late drama", "early goal", "clean sheet", "high cards", "low cards"
            ]
            
            betting_matches = 0
            for keyword in schedule_betting_keywords:
                if keyword in embed_content_lower:
                    betting_matches += 1
                    validation_results["schedule_py_keywords_found"].append(f"Betting: {keyword}")
            
            if betting_matches >= 3:  # At least 3 betting keywords found
                validation_results["betting_insights_similar"] = True
            
            # 6. Advanced metrics presence - check for schedule.py advanced analysis
            advanced_metrics_keywords = [
                "comprehensive", "dual-endpoint", "matches endpoint", "h2h endpoint",
                "expected goals", "probability", "confidence", "supporting evidence",
                "form momentum", "specialized markets", "halftime", "substitution"
            ]
            
            advanced_matches = 0
            for keyword in advanced_metrics_keywords:
                if keyword in embed_content_lower:
                    advanced_matches += 1
                    validation_results["schedule_py_keywords_found"].append(f"Advanced: {keyword}")
            
            if advanced_matches >= 2:  # At least 2 advanced metrics found
                validation_results["advanced_metrics_present"] = True
            
            # 7. Check for missing schedule.py elements
            critical_schedule_elements = [
                ("H2H Analysis", "head-to-head" in embed_content_lower or "h2h" in embed_content_lower),
                ("Team Form Analysis", "form" in embed_content_lower and "recent" in embed_content_lower),
                ("Goals Analysis", "goals per game" in embed_content_lower or "expected goals" in embed_content_lower),
                ("Betting Recommendations", any(bet_word in embed_content_lower for bet_word in ["over", "under", "btts"])),
                ("Card Discipline", "card" in embed_content_lower and ("yellow" in embed_content_lower or "discipline" in embed_content_lower)),
                ("Advanced Metrics", "advanced" in embed_content_lower or "comprehensive" in embed_content_lower)
            ]
            
            for element_name, is_present in critical_schedule_elements:
                if not is_present:
                    validation_results["missing_schedule_py_elements"].append(element_name)
            
            # 8. Calculate consistency score
            total_checks = 6  # Number of main validation categories
            passed_checks = sum([
                validation_results["team_names_match"],
                validation_results["odds_format_consistent"],
                validation_results["h2h_data_consistent"],
                validation_results["team_analysis_consistent"],
                validation_results["betting_insights_similar"],
                validation_results["advanced_metrics_present"]
            ])
            
            validation_results["consistency_score"] = (passed_checks / total_checks) * 100
            
            # 9. Overall consistency determination
            validation_results["overall_consistency"] = (
                validation_results["consistency_score"] >= 70 and  # At least 70% consistency
                len(validation_results["missing_schedule_py_elements"]) <= 2  # At most 2 missing elements
            )
            
            # 10. Detailed comparison for debugging
            validation_results["detailed_comparison"] = {
                "embed_count": len(embeds),
                "embed_titles": embed_titles,
                "total_keywords_found": len(validation_results["schedule_py_keywords_found"]),
                "h2h_keyword_matches": h2h_matches,
                "team_analysis_matches": team_analysis_matches,
                "betting_keyword_matches": betting_matches,
                "advanced_metrics_matches": advanced_matches,
                "embed_content_length": len(embed_content),
                "schedule_output_length": len(schedule_output)
            }
            
            # Log validation results
            self.logger.info(f"Embed validation completed: {validation_results['consistency_score']:.1f}% consistency")
            if not validation_results["overall_consistency"]:
                self.logger.warning(f"Low consistency detected. Missing: {validation_results['missing_schedule_py_elements']}")
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Error validating embed content consistency: {e}")
            return {
                "error": str(e), 
                "overall_consistency": False,
                "consistency_score": 0.0,
                "detailed_comparison": {"error": "Validation failed"}
            }
    
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