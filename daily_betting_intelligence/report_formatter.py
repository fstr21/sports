"""
Report formatter for generating structured markdown reports.

This module provides the ReportFormatter class that converts daily betting
intelligence data into well-formatted markdown reports with consistent
structure across all sports and leagues.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import pytz

from .models import (
    ReportData, GameData, BettingOdds, PlayerProp, 
    GameAnalysis, PlayerAnalysis
)


class ReportFormatter:
    """Generates structured markdown reports from daily betting intelligence data."""
    
    def __init__(self, timezone: str = "US/Eastern"):
        """Initialize the report formatter with timezone configuration."""
        self.timezone = pytz.timezone(timezone)
    
    def format_daily_report(self, report_data: ReportData) -> str:
        """
        Generate a complete daily betting intelligence report in markdown format.
        
        Args:
            report_data: Complete report data structure
            
        Returns:
            Formatted markdown report as string
        """
        sections = []
        
        # Header and executive summary
        sections.append(self._format_header(report_data))
        sections.append(self._format_executive_summary(report_data))
        
        # Group games by league for organized presentation
        games_by_league = self._group_games_by_league(report_data.games_data)
        
        # Generate league sections
        for league, games in games_by_league.items():
            sections.append(self._format_league_section(
                league, games, report_data
            ))
        
        # Footer with generation info and errors
        sections.append(self._format_footer(report_data))
        
        return "\n\n".join(sections)
    
    def _format_header(self, report_data: ReportData) -> str:
        """Format the report header with date and title."""
        formatted_date = datetime.strptime(report_data.target_date, "%Y%m%d").strftime("%B %d, %Y")
        return f"# Daily Betting Intelligence Report - {formatted_date}"
    
    def _format_executive_summary(self, report_data: ReportData) -> str:
        """Format the executive summary section."""
        summary_lines = [
            "## Executive Summary",
            "",
            f"- **Total games analyzed:** {report_data.total_games}",
            f"- **Leagues covered:** {', '.join(report_data.leagues_analyzed)}",
            f"- **Report generated:** {self._format_timestamp(report_data.generation_timestamp)}"
        ]
        
        # Add high-confidence recommendations count if available
        high_confidence_count = self._count_high_confidence_recommendations(report_data)
        if high_confidence_count > 0:
            summary_lines.append(f"- **High-confidence recommendations:** {high_confidence_count}")
        
        # Add error/warning summary if present
        if report_data.errors:
            summary_lines.append(f"- **Errors encountered:** {len(report_data.errors)}")
        if report_data.warnings:
            summary_lines.append(f"- **Warnings:** {len(report_data.warnings)}")
        
        return "\n".join(summary_lines)
    
    def _format_league_section(self, league: str, games: List[GameData], report_data: ReportData) -> str:
        """Format a complete league section with all games."""
        league_name = self._format_league_name(league)
        sections = [f"## {league_name} Analysis"]
        
        if not games:
            sections.append("No games scheduled for this league.")
            return "\n\n".join(sections)
        
        # Sort games by time
        sorted_games = sorted(games, key=lambda g: g.game_time)
        
        for game in sorted_games:
            game_section = self._format_game_section(game, report_data)
            sections.append(game_section)
        
        return "\n\n".join(sections)
    
    def _format_game_section(self, game: GameData, report_data: ReportData) -> str:
        """Format a complete game section with all available data."""
        sections = []
        
        # Game header
        game_time = self._format_game_time(game.game_time)
        sections.append(f"### {game.away_team} @ {game.home_team} - {game_time}")
        
        # Game overview
        sections.append(self._format_game_overview(game))
        
        # Betting lines (if available)
        if game.event_id in report_data.betting_odds:
            betting_section = self._format_betting_lines(
                report_data.betting_odds[game.event_id]
            )
            sections.append(betting_section)
        
        # Player props (if available)
        if game.event_id in report_data.player_props:
            props_section = self._format_player_props(
                report_data.player_props[game.event_id]
            )
            sections.append(props_section)
        
        # Game analysis (if available)
        if game.event_id in report_data.game_analyses:
            analysis_section = self._format_game_analysis(
                report_data.game_analyses[game.event_id]
            )
            sections.append(analysis_section)
        
        # Player analyses (if available)
        if game.event_id in report_data.player_analyses:
            player_section = self._format_player_analyses(
                report_data.player_analyses[game.event_id]
            )
            sections.append(player_section)
        
        return "\n\n".join(sections)
    
    def _format_game_overview(self, game: GameData) -> str:
        """Format the game overview section with metadata."""
        lines = ["#### Game Overview"]
        
        # Basic game info
        lines.append(f"- **Venue:** {game.venue}")
        lines.append(f"- **Status:** {game.status.title()}")
        
        # Add scores if game is live or final
        if game.status in ["live", "final"] and game.home_score is not None:
            lines.append(f"- **Score:** {game.away_team} {game.away_score} - {game.home_score} {game.home_team}")
        
        # Add weather if available
        if game.weather:
            lines.append(f"- **Weather:** {game.weather}")
        
        # Add any additional metadata
        for key, value in game.additional_metadata.items():
            if value:
                formatted_key = key.replace("_", " ").title()
                lines.append(f"- **{formatted_key}:** {value}")
        
        return "\n".join(lines)
    
    def _format_betting_lines(self, odds_list: List[BettingOdds]) -> str:
        """Format betting lines section with best odds highlighted."""
        if not odds_list:
            return "#### Betting Lines\n\nNo betting lines available."
        
        lines = ["#### Betting Lines"]
        
        # Find best odds for each market
        best_odds = self._find_best_odds(odds_list)
        
        # Moneyline
        if best_odds.get("moneyline"):
            lines.append("\n**Moneyline:**")
            ml_data = best_odds["moneyline"]
            lines.append(f"- Home: {self._format_odds(ml_data['home_odds'])} ({ml_data['home_book']})")
            lines.append(f"- Away: {self._format_odds(ml_data['away_odds'])} ({ml_data['away_book']})")
        
        # Point Spread
        if best_odds.get("spread"):
            lines.append("\n**Point Spread:**")
            spread_data = best_odds["spread"]
            lines.append(f"- Home {self._format_spread(spread_data['line'])}: {self._format_odds(spread_data['home_odds'])} ({spread_data['home_book']})")
            lines.append(f"- Away {self._format_spread(-spread_data['line'])}: {self._format_odds(spread_data['away_odds'])} ({spread_data['away_book']})")
        
        # Totals
        if best_odds.get("total"):
            lines.append("\n**Total (Over/Under):**")
            total_data = best_odds["total"]
            lines.append(f"- Over {total_data['line']}: {self._format_odds(total_data['over_odds'])} ({total_data['over_book']})")
            lines.append(f"- Under {total_data['line']}: {self._format_odds(total_data['under_odds'])} ({total_data['under_book']})")
        
        return "\n".join(lines)
    
    def _format_player_props(self, props_list: List[PlayerProp]) -> str:
        """Format player props section grouped by player."""
        if not props_list:
            return "#### Player Props\n\nNo player props available."
        
        lines = ["#### Player Props"]
        
        # Group props by player
        props_by_player = {}
        for prop in props_list:
            if prop.player_name not in props_by_player:
                props_by_player[prop.player_name] = []
            props_by_player[prop.player_name].append(prop)
        
        # Format each player's props
        for player_name, player_props in props_by_player.items():
            lines.append(f"\n**{player_name}:**")
            for prop in sorted(player_props, key=lambda p: p.prop_type):
                prop_line = f"- {prop.prop_type.title()}: O/U {prop.line} "
                prop_line += f"({self._format_odds(prop.over_odds)}/{self._format_odds(prop.under_odds)}) "
                prop_line += f"- {prop.sportsbook}"
                lines.append(prop_line)
        
        return "\n".join(lines)
    
    def _format_game_analysis(self, analysis: GameAnalysis) -> str:
        """Format game analysis section with predictions and recommendations."""
        lines = ["#### Analysis & Predictions"]
        
        # Prediction
        lines.append(f"\n**Predicted Winner:** {analysis.predicted_winner}")
        lines.append(f"**Confidence:** {analysis.confidence_score:.1%}")
        lines.append(f"**Risk Level:** {analysis.risk_level.title()}")
        
        # Key factors
        if analysis.key_factors:
            lines.append("\n**Key Factors:**")
            for factor in analysis.key_factors:
                lines.append(f"- {factor}")
        
        # Value bets
        if analysis.value_bets:
            lines.append("\n**Value Opportunities:**")
            for bet in analysis.value_bets:
                bet_desc = f"- {bet.get('bet_type', 'Unknown')}: {bet.get('description', 'N/A')}"
                if bet.get('confidence'):
                    bet_desc += f" (Confidence: {bet['confidence']:.1%})"
                lines.append(bet_desc)
        
        # Reasoning
        if analysis.reasoning:
            lines.append(f"\n**Analysis:** {analysis.reasoning}")
        
        return "\n".join(lines)
    
    def _format_player_analyses(self, player_analyses: List[PlayerAnalysis]) -> str:
        """Format player analyses section with key players and recommendations."""
        if not player_analyses:
            return ""
        
        lines = ["#### Key Players Analysis"]
        
        # Sort by confidence score (highest first)
        sorted_analyses = sorted(player_analyses, key=lambda p: p.confidence_score, reverse=True)
        
        for analysis in sorted_analyses:
            lines.append(f"\n**{analysis.player_name}** (Confidence: {analysis.confidence_score:.1%})")
            
            # Projected stats
            if analysis.projected_stats:
                stats_line = "- Projected: "
                stat_strings = []
                for stat, value in analysis.projected_stats.items():
                    stat_strings.append(f"{value:.1f} {stat}")
                stats_line += ", ".join(stat_strings)
                lines.append(stats_line)
            
            # Prop recommendations
            if analysis.prop_recommendations:
                lines.append("- Recommendations:")
                for rec in analysis.prop_recommendations:
                    rec_line = f"  - {rec.get('prop_type', 'Unknown')}: {rec.get('recommendation', 'N/A')}"
                    if rec.get('reasoning'):
                        rec_line += f" ({rec['reasoning']})"
                    lines.append(rec_line)
            
            # Analysis reasoning
            if analysis.reasoning:
                lines.append(f"- Analysis: {analysis.reasoning}")
        
        return "\n".join(lines)
    
    def _format_footer(self, report_data: ReportData) -> str:
        """Format report footer with generation info and errors."""
        lines = ["---", ""]
        
        # Generation timestamp
        lines.append(f"*Report generated at {self._format_timestamp(report_data.generation_timestamp)}*")
        
        # Errors and warnings
        if report_data.errors or report_data.warnings:
            lines.append("\n### Issues Encountered")
            
            if report_data.errors:
                lines.append("\n**Errors:**")
                for error in report_data.errors:
                    lines.append(f"- {error}")
            
            if report_data.warnings:
                lines.append("\n**Warnings:**")
                for warning in report_data.warnings:
                    lines.append(f"- {warning}")
        
        return "\n".join(lines)
    
    # Helper methods
    
    def _group_games_by_league(self, games: List[GameData]) -> Dict[str, List[GameData]]:
        """Group games by league for organized presentation."""
        games_by_league = {}
        for game in games:
            if game.league not in games_by_league:
                games_by_league[game.league] = []
            games_by_league[game.league].append(game)
        return games_by_league
    
    def _format_league_name(self, league: str) -> str:
        """Format league code into display name."""
        league_names = {
            "nfl": "NFL",
            "nba": "NBA", 
            "wnba": "WNBA",
            "mlb": "MLB",
            "nhl": "NHL",
            "mls": "MLS",
            "epl": "English Premier League",
            "laliga": "La Liga",
            "ncaaf": "NCAA Football",
            "ncaab": "NCAA Basketball"
        }
        return league_names.get(league.lower(), league.upper())
    
    def _format_game_time(self, game_time: datetime) -> str:
        """Format game time in configured timezone."""
        if game_time.tzinfo is None:
            # Assume UTC if no timezone info
            game_time = pytz.UTC.localize(game_time)
        
        local_time = game_time.astimezone(self.timezone)
        # Get timezone abbreviation
        tz_abbrev = local_time.strftime("%Z")
        return local_time.strftime(f"%I:%M %p {tz_abbrev}")
    
    def _format_timestamp(self, timestamp: datetime) -> str:
        """Format timestamp for display."""
        if timestamp.tzinfo is None:
            timestamp = pytz.UTC.localize(timestamp)
        
        local_time = timestamp.astimezone(self.timezone)
        tz_abbrev = local_time.strftime("%Z")
        return local_time.strftime(f"%B %d, %Y at %I:%M %p {tz_abbrev}")
    
    def _format_odds(self, odds: Optional[int]) -> str:
        """Format betting odds for display."""
        if odds is None:
            return "N/A"
        
        if odds > 0:
            return f"+{odds}"
        else:
            return str(odds)
    
    def _format_spread(self, spread: float) -> str:
        """Format point spread for display."""
        if spread > 0:
            return f"+{spread}"
        else:
            return str(spread)
    
    def _find_best_odds(self, odds_list: List[BettingOdds]) -> Dict[str, Any]:
        """Find the best odds across all sportsbooks for each market."""
        best_odds = {}
        
        # Find best moneyline odds
        best_ml_home = None
        best_ml_away = None
        best_ml_home_book = ""
        best_ml_away_book = ""
        
        for odds in odds_list:
            if odds.moneyline_home is not None:
                if best_ml_home is None or odds.moneyline_home > best_ml_home:
                    best_ml_home = odds.moneyline_home
                    best_ml_home_book = odds.sportsbook
            
            if odds.moneyline_away is not None:
                if best_ml_away is None or odds.moneyline_away > best_ml_away:
                    best_ml_away = odds.moneyline_away
                    best_ml_away_book = odds.sportsbook
        
        if best_ml_home is not None and best_ml_away is not None:
            best_odds["moneyline"] = {
                "home_odds": best_ml_home,
                "away_odds": best_ml_away,
                "home_book": best_ml_home_book,
                "away_book": best_ml_away_book
            }
        
        # Find best spread odds (similar logic for spreads and totals)
        # This is a simplified version - in practice, you'd want to find the best odds
        # for the same spread line, not just any spread
        for odds in odds_list:
            if (odds.spread_line is not None and 
                odds.spread_home_odds is not None and 
                odds.spread_away_odds is not None):
                
                if "spread" not in best_odds:
                    best_odds["spread"] = {
                        "line": odds.spread_line,
                        "home_odds": odds.spread_home_odds,
                        "away_odds": odds.spread_away_odds,
                        "home_book": odds.sportsbook,
                        "away_book": odds.sportsbook
                    }
        
        # Find best total odds
        for odds in odds_list:
            if (odds.total_line is not None and 
                odds.total_over_odds is not None and 
                odds.total_under_odds is not None):
                
                if "total" not in best_odds:
                    best_odds["total"] = {
                        "line": odds.total_line,
                        "over_odds": odds.total_over_odds,
                        "under_odds": odds.total_under_odds,
                        "over_book": odds.sportsbook,
                        "under_book": odds.sportsbook
                    }
        
        return best_odds
    
    def _count_high_confidence_recommendations(self, report_data: ReportData) -> int:
        """Count high-confidence recommendations across all analyses."""
        count = 0
        
        # Count high-confidence game analyses
        for analysis in report_data.game_analyses.values():
            if analysis.confidence_score >= 0.8:  # 80% confidence threshold
                count += 1
        
        # Count high-confidence player analyses
        for player_list in report_data.player_analyses.values():
            for player_analysis in player_list:
                if player_analysis.confidence_score >= 0.8:
                    count += 1
        
        return count