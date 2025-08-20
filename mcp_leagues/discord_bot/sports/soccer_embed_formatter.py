"""
Soccer Discord Embed Formatter (Dynamic Layout Version)
Dedicated module for formatting soccer match analysis into Discord embeds.
This version uses a dynamic layout manager to prevent misalignment with missing data.
"""
import discord
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class DynamicLayoutSoccerEmbedFormatter:
    """
    Handles Discord embed formatting with a dynamic grid layout.
    This prevents visual bugs when analysis data is sparse or missing.
    """
    
    DEFAULT_CONFIG = {
        'embed_color': 0x00B0F0,
        'error_color': 0xFF0000, # Added a color for error messages
        'emojis': {
            'vs': '⚔️', 'odds': '💰', 'h2h': '📊', 'trend': '💡', 'form': '📈',
            'home': '🏠', 'away': '✈️', 'prediction': '🎯', 'goals': '⚽',
            'insights': '🧠', 'error': '⚠️'
        },
        'titles': {
            'odds': 'Odds', 'h2h': 'Head-to-Head', 'trends': 'Key Trends',
            'home_form': 'Home Form', 'away_form': 'Away Form',
            'prediction': 'Prediction', 'analysis_error': 'Analysis Failed'
        }
    }

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize formatter with configuration"""
        self.config = self.DEFAULT_CONFIG.copy()
        if config: self.config.update(config)
        self.emojis = self.config['emojis']
        self.titles = self.config['titles']

    def create_error_embed(self, home_team: str, away_team: str, league: str, error_message: str) -> discord.Embed:
        """Creates a dedicated embed for when analysis fails."""
        embed = discord.Embed(
            title=f"{self.emojis['vs']} {home_team} vs {away_team}",
            description=f"**{league}**",
            color=self.config['error_color'],
            timestamp=datetime.now()
        )
        embed.add_field(
            name=f"{self.emojis['error']} {self.titles['analysis_error']}",
            value=f"Could not retrieve detailed analysis.\n*Reason: {error_message}*",
            inline=False
        )
        embed.set_footer(text="Powered by Soccer MCP • Basic Info Only")
        return embed

    def create_comprehensive_embed(self, **kwargs) -> discord.Embed:
        """
        Create comprehensive match embed with a dynamic layout.
        
        Args (via kwargs):
            home_team, away_team, league, match_time, odds_data, 
            h2h_data, home_form_data, away_form_data, etc.
        """
        home_team = kwargs.get('home_team', 'Home')
        away_team = kwargs.get('away_team', 'Away')
        
        embed = discord.Embed(
            title=f"{self.emojis['vs']} {home_team} vs {away_team}",
            description=f"**{kwargs.get('league')}** • {kwargs.get('match_time', 'TBD')}",
            color=self.config['embed_color'],
            timestamp=datetime.now()
        )

        # [IMPROVEMENT] Collect all potential fields into a list first.
        # Helper methods will now return a dict (a field) or None if there's no data.
        inline_fields = []
        
        # Add fields only if they have data
        inline_fields.append(self._prepare_odds_field(kwargs.get('odds_data'), home_team, away_team))
        inline_fields.append(self._prepare_h2h_field(kwargs.get('h2h_data'), home_team, away_team))
        inline_fields.append(self._prepare_form_field(kwargs.get('home_form_data'), self.emojis['home'], self.titles['home_form']))
        inline_fields.append(self._prepare_form_field(kwargs.get('away_form_data'), self.emojis['away'], self.titles['away_form']))
        
        # Remove any `None` entries where data was missing
        inline_fields = [field for field in inline_fields if field]

        # [IMPROVEMENT] Add fields to the embed and pad the grid to ensure alignment
        for field in inline_fields:
            embed.add_field(**field)

        padding_needed = (3 - len(inline_fields) % 3) % 3
        for _ in range(padding_needed):
            embed.add_field(name='\u200b', value='\u200b', inline=True)
            
        # Add non-inline fields last (if any)
        # e.g., self._add_match_predictions(embed, ...)
        
        embed.set_footer(text="Powered by Soccer MCP • Enhanced Analysis")
        return embed

    def _prepare_odds_field(self, odds_data: Dict, home_team: str, away_team: str) -> Optional[Dict]:
        """Prepares the odds field if data exists."""
        if not odds_data: return None
        
        lines = []
        # Support both 1x2 and O/U odds
        home_odds, draw_odds, away_odds = odds_data.get('home_win'), odds_data.get('draw'), odds_data.get('away_win')
        if home_odds and draw_odds and away_odds:
            lines.append(f"**{home_team}:** {home_odds}")
            lines.append(f"**Draw:** {draw_odds}")
            lines.append(f"**{away_team}:** {away_odds}")
        
        over_under = odds_data.get('over_under', {})
        total, over, under = over_under.get('total'), over_under.get('over'), over_under.get('under')
        if total and over and under:
            if lines: lines.append("---")
            lines.append(f"**Over {total}:** {over}")
            lines.append(f"**Under {total}:** {under}")

        if not lines: return None
        
        return {
            "name": f"{self.emojis['odds']} {self.titles['odds']}",
            "value": "\n".join(lines),
            "inline": True
        }

    def _prepare_h2h_field(self, h2h_data: Dict, home_team: str, away_team: str) -> Optional[Dict]:
        """Prepares the H2H field if data exists."""
        if not h2h_data or h2h_data.get('total_meetings', 0) == 0:
            return {
                "name": f"{self.emojis['h2h']} {self.titles['h2h']}",
                "value": "No previous meetings.",
                "inline": True
            }
        
        total = h2h_data['total_meetings']
        h_wins = h2h_data.get('home_team_wins', 0)
        a_wins = h2h_data.get('away_team_wins', 0)
        draws = h2h_data.get('draws', 0)

        value = (f"**{h_wins}** {home_team} Wins ({h_wins/total:.0%})\n"
                 f"**{a_wins}** {away_team} Wins ({a_wins/total:.0%})\n"
                 f"**{draws}** Draws ({draws/total:.0%})")
        
        return {
            "name": f"{self.emojis['h2h']} {self.titles['h2h']} ({total} meetings)",
            "value": value,
            "inline": True
        }

    def _prepare_form_field(self, form_data: Dict, emoji: str, title: str) -> Optional[Dict]:
        """Prepares a team form field if data exists."""
        if not form_data or form_data.get('record', 'N/A') == 'N/A':
            # Return a placeholder only if you want it to appear, otherwise return None
            # For a cleaner layout, returning None is better.
            # We'll handle the "No Data" case in the embed itself if all fields are empty.
            return None

        rating = form_data.get('form_rating', 0)
        record = form_data.get('record', '')
        win_pct = form_data.get('win_percentage', 0)
        gf, ga = form_data.get('goals_for', 0), form_data.get('goals_against', 0)
        
        lines = [
            f"**Rating: {rating:.1f}/10.0**",
            f"Record: `{record}` ({win_pct:.0f}% Win)",
            f"Goals: `{gf} For / {ga} Against`"
        ]
        
        return {
            "name": f"{emoji} {title}",
            "value": "\n".join(lines),
            "inline": True
        }