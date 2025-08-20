"""
Soccer Discord Embed Formatter (Improved Version)
Dedicated module for formatting soccer match analysis into Discord embeds.
Enhanced for readability, maintainability, and visual appeal.
"""
import discord
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ImprovedSoccerEmbedFormatter:
    """
    Handles all Discord embed formatting for soccer matches.
    Keeps formatting logic separate from data fetching and business logic.
    Refactored for improved readability and easier customization.
    """
    
    # [IMPROVEMENT] Centralize all emojis, titles, and colors for easy customization.
    DEFAULT_CONFIG = {
        'embed_color': 0x00B0F0,  # A brighter, more distinct color
        'emojis': {
            'vs': '⚔️',
            'odds': '💰',
            'h2h': '📊',
            'trend': '💡',
            'form': '📈',
            'home': '🏠',
            'away': '✈️',
            'prediction': '🎯',
            'goals': '⚽',
            'insights': '🧠',
            'fire': '🔥',
            'shield': '🛡️',
            'balance': '⚖️',
        },
        'titles': {
            'odds': 'Odds',
            'h2h': 'Head-to-Head',
            'trends': 'Key Trends',
            'home_form': 'Home Team Form',
            'away_form': 'Away Team Form',
            'prediction': 'Match Prediction',
            'goals': 'Goals Prediction',
            'insights': 'Actionable Insights',
        }
    }

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize formatter with configuration"""
        # Merge user config with defaults
        self.config = self.DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)
        
        self.emojis = self.config['emojis']
        self.titles = self.config['titles']
        self.embed_color = self.config['embed_color']

    def create_comprehensive_embed(
        self, 
        home_team: str, 
        away_team: str, 
        league: str, 
        match_time: str = "TBD",
        odds_data: Dict = None,
        h2h_data: Dict = None, 
        home_form_data: Dict = None, 
        away_form_data: Dict = None, 
        match_analysis_data: Dict = None
    ) -> discord.Embed:
        """Create comprehensive match embed with all analysis data."""
        
        # [IMPROVEMENT] Fixed title to follow "Home vs Away" convention.
        embed = discord.Embed(
            title=f"{self.emojis['vs']} {home_team} vs {away_team}",
            description=f"**{league}** • {match_time}",
            color=self.embed_color,
            timestamp=datetime.now()
        )
        
        if odds_data:
            self._add_betting_odds(embed, odds_data, home_team, away_team)
        
        if h2h_data:
            self._add_h2h_analysis(embed, h2h_data, home_team, away_team)
            # [IMPROVEMENT] Grouped goals trend with H2H analysis for better flow.
            self._add_goals_trend(embed, h2h_data)

        if home_form_data or away_form_data:
            self._add_team_forms(embed, home_form_data, away_form_data)
        
        if match_analysis_data:
            self._add_match_predictions(embed, match_analysis_data)
        
        embed.set_footer(text="Powered by Soccer MCP • Enhanced Analysis")
        return embed

    def _add_betting_odds(self, embed: discord.Embed, odds_data: Dict[str, Any], home_team: str, away_team: str):
        """Add betting odds section to embed."""
        lines = []
        
        # Match Winner Odds (1X2)
        home_odds = odds_data.get('home_win')
        draw_odds = odds_data.get('draw')
        away_odds = odds_data.get('away_win')

        if home_odds and draw_odds and away_odds:
            lines.append(f"**{home_team}:** {home_odds} ({self._convert_to_american_odds(home_odds)})")
            lines.append(f"**Draw:** {draw_odds} ({self._convert_to_american_odds(draw_odds)})")
            lines.append(f"**{away_team}:** {away_odds} ({self._convert_to_american_odds(away_odds)})")
        
        # Over/Under Odds
        over_under = odds_data.get('over_under', {})
        total, over, under = over_under.get('total'), over_under.get('over'), over_under.get('under')
        
        if total and over and under:
            # Add a separator if both 1X2 and O/U odds are present
            if lines: lines.append("---")
            lines.append(f"**Over {total}:** {over} ({self._convert_to_american_odds(over)})")
            lines.append(f"**Under {total}:** {under} ({self._convert_to_american_odds(under)})")

        if lines:
            # [IMPROVEMENT] Using newlines for readability instead of a single long line.
            embed.add_field(
                name=f"{self.emojis['odds']} {self.titles['odds']}",
                value="\n".join(lines),
                inline=True
            )

    def _add_h2h_analysis(self, embed: discord.Embed, h2h_data: Dict[str, Any], home_team: str, away_team: str):
        """Add head-to-head analysis to embed."""
        total_meetings = h2h_data.get('total_meetings', 0)
        
        if total_meetings > 0:
            h_wins = h2h_data.get('home_team_wins', 0)
            a_wins = h2h_data.get('away_team_wins', 0)
            draws = h2h_data.get('draws', 0)
            
            # [IMPROVEMENT] Cleaner string formatting using a list and join.
            h2h_lines = [
                f"**{h_wins}** {home_team} Wins ({h_wins/total_meetings:.0%})",
                f"**{a_wins}** {away_team} Wins ({a_wins/total_meetings:.0%})",
                f"**{draws}** Draws ({draws/total_meetings:.0%})"
            ]
            
            embed.add_field(
                name=f"{self.emojis['h2h']} {self.titles['h2h']} ({total_meetings} meetings)",
                value="\n".join(h2h_lines),
                inline=True
            )
        else:
            embed.add_field(name=f"{self.emojis['h2h']} {self.titles['h2h']}", value="No previous meetings.", inline=True)

    def _add_goals_trend(self, embed: discord.Embed, h2h_data: Dict[str, Any]):
        """Add a dedicated field for goals trend analysis."""
        goals = h2h_data.get('goals', {})
        avg_goals = goals.get('average_per_game')
        
        if avg_goals is not None:
            if avg_goals > 2.8:
                trend_emoji = self.emojis['fire']
                trend_text = "Over 2.5 Goals"
            elif avg_goals < 2.2:
                trend_emoji = self.emojis['shield']
                trend_text = "Under 2.5 Goals"
            else:
                trend_emoji = self.emojis['balance']
                trend_text = "Balanced"
            
            value_text = f"{trend_emoji} **{trend_text}**\n*({avg_goals:.1f} avg goals in H2H)*"
            
            embed.add_field(
                name=f"{self.emojis['trend']} {self.titles['trends']}",
                value=value_text,
                inline=True
            )

    def _add_team_forms(self, embed: discord.Embed, home_form_data: Dict, away_form_data: Dict):
        """Add both team forms with a visual separator."""
        if home_form_data:
            self._add_single_team_form(embed, home_form_data, self.emojis['home'], self.titles['home_form'])
        
        # [IMPROVEMENT] Add a blank, inline field to create visual space between the two form blocks.
        embed.add_field(name='\u200b', value='\u200b', inline=True)
        
        if away_form_data:
            self._add_single_team_form(embed, away_form_data, self.emojis['away'], self.titles['away_form'])

    def _add_single_team_form(self, embed: discord.Embed, form_data: Dict, emoji: str, title: str):
        """Add an individual, cleanly formatted team form field."""
        record = form_data.get('record', 'N/A')
        rating = form_data.get('form_rating', 0)
        win_pct = form_data.get('win_percentage', 0)
        gf = form_data.get('goals_for', 0)
        ga = form_data.get('goals_against', 0)
        
        if record != 'N/A':
            # [IMPROVEMENT] Layout prioritizes key stats for quick scanning.
            form_lines = [
                f"**Rating: {rating:.1f}/10.0**",
                f"Record: `{record}` ({win_pct:.0f}% Win)",
                f"Goals: `{gf} For / {ga} Against`"
            ]
            embed.add_field(
                name=f"{emoji} {title}",
                value="\n".join(form_lines),
                inline=True
            )
        else:
            embed.add_field(name=f"{emoji} {title}", value="No recent form data.", inline=True)
            
    # [IMPROVEMENT] Marked as a static method as it doesn't use 'self'.
    def create_loading_embed(self, home_team: str, away_team: str, league: str, match_time: str = "TBD") -> discord.Embed:
        """Create initial loading embed for a match"""
        embed = discord.Embed(
            title=f"{self.emojis['vs']} {home_team} vs {away_team}",
            description=f"**{league}** • {match_time}\n🔄 Loading comprehensive analysis...",
            color=self.embed_color,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Loading analysis...")
        return embed
    
    def create_basic_embed(self, home_team: str, away_team: str, league: str, match_time: str = "TBD", odds_data: Dict = None) -> discord.Embed:
        """Create basic match embed without comprehensive analysis (fallback)"""
        embed = discord.Embed(
            title=f"{self.emojis['vs']} {home_team} vs {away_team}",
            description=f"**{league}** • {match_time}",
            color=self.embed_color,
            timestamp=datetime.now()
        )
        
        if odds_data:
            self._add_betting_odds(embed, odds_data, home_team, away_team)
        
        embed.set_footer(text="Basic match info • Powered by Soccer MCP")
        return embed
    
    def _add_match_predictions(self, embed: discord.Embed, match_analysis_data: Dict[str, Any]):
        """Add match predictions with clean formatting"""
        try:
            predictions = match_analysis_data.get('predictions', {})
            match_winner = predictions.get('match_winner', {})
            goals_pred = predictions.get('goals', {})
            insights = predictions.get('key_insights', [])
            
            # Winner prediction
            if match_winner:
                prediction = match_winner.get('prediction', 'Unknown')
                confidence = match_winner.get('confidence_percentage', 0)
                
                if confidence > 0:
                    embed.add_field(
                        name=f"{self.emojis['prediction']} {self.titles['prediction']}",
                        value=f"**{prediction}** ({confidence}%)",
                        inline=True
                    )
            
            # Goals prediction
            if goals_pred and goals_pred.get('prediction') != 'No prediction available':
                expected_goals = goals_pred.get('expected_goals', 0)
                if expected_goals > 0:
                    if expected_goals > 2.5:
                        goals_text = f"{self.emojis['fire']} **Over 2.5** ({expected_goals} exp)"
                    else:
                        goals_text = f"{self.emojis['shield']} **Under 2.5** ({expected_goals} exp)"
                    
                    embed.add_field(
                        name=f"{self.emojis['goals']} {self.titles['goals']}",
                        value=goals_text,
                        inline=True
                    )
            
            # Key insights - only actionable ones
            if insights:
                clean_insights = []
                for insight in insights[:3]:
                    if "Home Team Form:" in insight or "Away Team Form:" in insight:
                        continue  # Skip form insights (shown elsewhere)
                    if len(insight) < 60:  # Only short, actionable insights
                        clean_insights.append(f"• {insight}")
                
                if clean_insights:
                    embed.add_field(
                        name=f"{self.emojis['insights']} {self.titles['insights']}",
                        value="\n".join(clean_insights),
                        inline=False
                    )
                    
        except Exception as e:
            logger.error(f"Error adding match predictions: {e}")

    @staticmethod
    def _convert_to_american_odds(decimal_odds) -> str:
        """Convert decimal odds to American format."""
        try:
            decimal = float(decimal_odds)
            if decimal >= 2.0:
                return f"+{int((decimal - 1) * 100)}"
            else:
                return str(int(-100 / (decimal - 1)))
        except (ValueError, ZeroDivisionError, TypeError):
            return str(decimal_odds)