"""
Soccer Discord Embed Formatter
Dedicated module for formatting soccer match analysis into Discord embeds.
Separate from main soccer handler logic for easy formatting improvements.
"""
import discord
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SoccerEmbedFormatter:
    """
    Handles all Discord embed formatting for soccer matches.
    Keeps formatting logic separate from data fetching and business logic.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize formatter with configuration"""
        self.config = config or {}
        self.embed_color = self.config.get('embed_color', 0x2F3136)  # Discord dark theme
    
    def create_loading_embed(self, home_team: str, away_team: str, league: str, match_time: str = "TBD") -> discord.Embed:
        """Create initial loading embed for a match"""
        embed = discord.Embed(
            title=f"⚽ {away_team} vs {home_team}",
            description=f"**{league}** • {match_time}\n🔄 Loading comprehensive analysis...",
            color=self.embed_color,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Loading analysis...")
        return embed
    
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
        """
        Create comprehensive match embed with all analysis data.
        
        Args:
            home_team: Home team name
            away_team: Away team name  
            league: League name
            match_time: Match time string
            odds_data: Betting odds data
            h2h_data: Head-to-head analysis data
            home_form_data: Home team form data
            away_form_data: Away team form data
            match_analysis_data: Comprehensive match analysis data
            
        Returns:
            Formatted Discord embed
        """
        # Create main embed structure
        embed = discord.Embed(
            title=f"⚽ {away_team} vs {home_team}",
            description=f"**{league}** • {match_time}",
            color=self.embed_color,
            timestamp=datetime.now()
        )
        
        # Add betting odds
        if odds_data:
            self._add_betting_odds(embed, odds_data, home_team, away_team)
        
        # Add H2H analysis
        if h2h_data:
            self._add_h2h_analysis(embed, h2h_data, home_team, away_team)
        
        # Add team forms side by side
        if home_form_data or away_form_data:
            self._add_team_forms(embed, home_form_data, away_form_data, home_team, away_team)
        
        # Add match predictions
        if match_analysis_data:
            self._add_match_predictions(embed, match_analysis_data, home_team, away_team)
        
        # Footer
        embed.set_footer(text="Powered by Soccer MCP • Enhanced Analysis")
        return embed
    
    def _add_betting_odds(self, embed: discord.Embed, odds_data: Dict[str, Any], home_team: str, away_team: str):
        """Add betting odds section to embed"""
        betting_lines = []
        
        # Match winner odds
        match_winner = odds_data.get('match_winner', {})
        if match_winner:
            home_odds = match_winner.get('home')
            draw_odds = match_winner.get('draw')
            away_odds = match_winner.get('away')
        else:
            home_odds = odds_data.get('home_win')
            draw_odds = odds_data.get('draw')
            away_odds = odds_data.get('away_win')
        
        if home_odds:
            american_home = self._convert_to_american_odds(home_odds)
            betting_lines.append(f"**{home_team}:** {home_odds} ({american_home})")
        if draw_odds:
            american_draw = self._convert_to_american_odds(draw_odds)
            betting_lines.append(f"**Draw:** {draw_odds} ({american_draw})")
        if away_odds:
            american_away = self._convert_to_american_odds(away_odds)
            betting_lines.append(f"**{away_team}:** {away_odds} ({american_away})")
        
        # Over/Under odds
        over_under = odds_data.get('over_under', {})
        if over_under:
            total = over_under.get('total')
            over = over_under.get('over')
            under = over_under.get('under')
            if total and over and under:
                american_over = self._convert_to_american_odds(over)
                american_under = self._convert_to_american_odds(under)
                betting_lines.append(f"**O/U {total}:** Over {over} ({american_over}), Under {under} ({american_under})")
        
        if betting_lines:
            embed.add_field(
                name="💰 Odds",
                value=" • ".join(betting_lines),  # Horizontal layout
                inline=False
            )
    
    def _add_h2h_analysis(self, embed: discord.Embed, h2h_data: Dict[str, Any], home_team: str, away_team: str):
        """Add head-to-head analysis to embed"""
        total_meetings = h2h_data.get('total_meetings', 0)
        
        if total_meetings > 0:
            team1_record = h2h_data.get('team_1_record', {})
            team2_record = h2h_data.get('team_2_record', {})
            draws = h2h_data.get('draws', {})
            
            # Clean H2H display
            h2h_text = f"**{total_meetings} meetings**\n"
            h2h_text += f"• **{home_team}:** {team1_record.get('wins', 0)}W ({team1_record.get('win_rate', 0):.0f}%)\n"
            h2h_text += f"• **{away_team}:** {team2_record.get('wins', 0)}W ({team2_record.get('win_rate', 0):.0f}%)\n"
            h2h_text += f"• **Draws:** {draws.get('count', 0)}"
            
            embed.add_field(
                name="📊 Head-to-Head",
                value=h2h_text,
                inline=False
            )
            
            # Goals trend analysis
            goals = h2h_data.get('goals', {})
            if goals:
                avg_goals = goals.get('average_per_game', 0)
                
                if avg_goals > 2.8:
                    trend_text = f"🔥 **Over 2.5 Goals** ({avg_goals:.1f} avg)"
                elif avg_goals < 2.2:
                    trend_text = f"🛡️ **Under 2.5 Goals** ({avg_goals:.1f} avg)"
                else:
                    trend_text = f"⚖️ **Balanced** ({avg_goals:.1f} avg goals)"
                
                embed.add_field(
                    name="💡 Goals Trend",
                    value=trend_text,
                    inline=True
                )
        else:
            embed.add_field(
                name="📊 Head-to-Head",
                value="**First meeting** - No historical data",
                inline=False
            )
    
    def _add_team_forms(self, embed: discord.Embed, home_form_data: Dict, away_form_data: Dict, home_team: str, away_team: str):
        """Add both team forms side by side"""
        # Home team form
        if home_form_data and "error" not in home_form_data:
            self._add_single_team_form(embed, home_form_data, home_team, "🏠 Home Team Form")
        else:
            embed.add_field(
                name="📊 🏠 Home Team Form",
                value="No recent UEFA form",
                inline=True
            )
        
        # Away team form
        if away_form_data and "error" not in away_form_data:
            self._add_single_team_form(embed, away_form_data, away_team, "✈️ Away Team Form")
        else:
            embed.add_field(
                name="📊 ✈️ Away Team Form",
                value="No recent UEFA form",
                inline=True
            )
    
    def _add_single_team_form(self, embed: discord.Embed, form_data: Dict[str, Any], team_name: str, field_name: str):
        """Add individual team form with clean formatting"""
        try:
            record = form_data.get('record', 'N/A')
            form_rating = form_data.get('form_rating', 0)
            win_percentage = form_data.get('win_percentage', 0)
            goals_for = form_data.get('goals_for', 0)
            goals_against = form_data.get('goals_against', 0)
            
            if record != 'N/A' or form_rating > 0:
                # Compact form display
                form_text = f"**{record}** | **{form_rating:.1f}/10**"
                
                if win_percentage > 0:
                    form_text += f"\n{win_percentage:.0f}% win rate"
                    
                if goals_for > 0 or goals_against > 0:
                    form_text += f"\n{goals_for} for, {goals_against} against"
                
                # Form rating emoji
                if form_rating >= 7:
                    form_emoji = "🔥"
                elif form_rating >= 5:
                    form_emoji = "⚡"
                elif form_rating >= 3:
                    form_emoji = "📈"
                else:
                    form_emoji = "📉"
                
                embed.add_field(
                    name=f"{form_emoji} {field_name}",
                    value=form_text,
                    inline=True
                )
            else:
                embed.add_field(
                    name=f"📊 {field_name}",
                    value="No recent UEFA form",
                    inline=True
                )
        except Exception as e:
            logger.error(f"Error adding team form: {e}")
            embed.add_field(
                name=f"❌ {field_name}",
                value="Form data error",
                inline=True
            )
    
    def _add_match_predictions(self, embed: discord.Embed, match_analysis_data: Dict[str, Any], home_team: str, away_team: str):
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
                        name="🎯 Prediction",
                        value=f"**{prediction}** ({confidence}%)",
                        inline=True
                    )
            
            # Goals prediction
            if goals_pred and goals_pred.get('prediction') != 'No prediction available':
                expected_goals = goals_pred.get('expected_goals', 0)
                if expected_goals > 0:
                    if expected_goals > 2.5:
                        goals_text = f"🔥 **Over 2.5** ({expected_goals} exp)"
                    else:
                        goals_text = f"🛡️ **Under 2.5** ({expected_goals} exp)"
                    
                    embed.add_field(
                        name="⚽ Goals",
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
                        name="💡 Insights",
                        value="\n".join(clean_insights),
                        inline=False
                    )
                    
        except Exception as e:
            logger.error(f"Error adding match predictions: {e}")
    
    def _convert_to_american_odds(self, decimal_odds) -> str:
        """Convert decimal odds to American format"""
        try:
            decimal = float(decimal_odds)
            if decimal >= 2.0:
                american = int((decimal - 1) * 100)
                return f"+{american}"
            else:
                american = int(-100 / (decimal - 1))
                return str(american)
        except (ValueError, ZeroDivisionError, TypeError):
            return str(decimal_odds)
    
    def create_basic_embed(self, home_team: str, away_team: str, league: str, match_time: str = "TBD", odds_data: Dict = None) -> discord.Embed:
        """Create basic match embed without comprehensive analysis (fallback)"""
        embed = discord.Embed(
            title=f"⚽ {away_team} vs {home_team}",
            description=f"**{league}** • {match_time}",
            color=self.embed_color,
            timestamp=datetime.now()
        )
        
        if odds_data:
            self._add_betting_odds(embed, odds_data, home_team, away_team)
        
        embed.set_footer(text="Basic match info • Powered by Soccer MCP")
        return embed