"""
Soccer-specific handler implementing the BaseSportHandler interface
"""
import asyncio
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import discord

from core.base_sport_handler import BaseSportHandler, Match, ChannelCreationResult, ClearResult
# Removed formatter import - all formatting back in this file


logger = logging.getLogger(__name__)


class SoccerHandler(BaseSportHandler):
    """
    Soccer-specific implementation of BaseSportHandler
    Handles soccer match data, channel creation, and comprehensive analysis
    """
    
    def __init__(self, sport_name: str, config: Dict[str, Any], mcp_client):
        """Initialize soccer handler with soccer-specific configuration"""
        super().__init__(sport_name, config, mcp_client)
        self.default_league_id = config.get('default_league_id', 297)  # La Liga default
# Removed formatter - all methods back in this class
        
    async def create_channels(self, interaction: discord.Interaction, date: str) -> ChannelCreationResult:
        """
        Create soccer channels with comprehensive H2H and form analysis
        
        Args:
            interaction: Discord interaction object
            date: Date string in YYYY-MM-DD format
            
        Returns:
            ChannelCreationResult with operation details
        """
        try:
            # Get matches for the date
            matches = await self.get_matches(date)
            
            if not matches:
                return ChannelCreationResult(
                    success=True,
                    channels_created=0,
                    total_matches=0,
                    errors=[],
                    message=f"No soccer matches found for {date}"
                )
            
            # Get or create category
            category = await self.create_category(interaction.guild)
            
            # Create channels with comprehensive analysis
            created = 0
            errors = []
            total_matches = len(matches)
            
            for match in matches:
                try:
                    # Check if channel already exists
                    channel_name = self.format_channel_name(match.home_team, match.away_team)
                    if discord.utils.get(category.channels, name=channel_name):
                        continue
                    
                    # Create channel
                    channel = await category.create_text_channel(
                        name=channel_name,
                        topic=f"{match.away_team} vs {match.home_team} - {match.league}"
                    )
                    
                    # Create and send initial embed using formatter
                    initial_embed = self.formatter.create_loading_embed(
                        match.home_team, 
                        match.away_team, 
                        match.league, 
                        match.additional_data.get('time', 'TBD')
                    )
                    message = await channel.send(embed=initial_embed)
                    
                    # Get comprehensive analysis and update embed
                    await self._update_channel_with_analysis(message, match)
                    
                    created += 1
                    
                    # Rate limiting delay
                    await asyncio.sleep(self.config.get('channel_creation_delay', 1.0))
                    
                except Exception as e:
                    error_msg = f"Failed to create channel for {match.away_team} vs {match.home_team}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            return ChannelCreationResult(
                success=True,
                channels_created=created,
                total_matches=total_matches,
                errors=errors,
                message=f"Created {created} soccer channels from {total_matches} matches with comprehensive analysis"
            )
            
        except Exception as e:
            logger.error(f"Error in soccer channel creation: {e}")
            return ChannelCreationResult(
                success=False,
                channels_created=0,
                total_matches=0,
                errors=[str(e)],
                message=f"Failed to create soccer channels: {str(e)}"
            )
    
    async def clear_channels(self, interaction: discord.Interaction, category_name: str) -> ClearResult:
        """
        Clear all channels from the soccer category
        
        Args:
            interaction: Discord interaction object
            category_name: Name of category to clear
            
        Returns:
            ClearResult with operation details
        """
        try:
            # Get category
            category = self.get_category(interaction.guild)
            if not category:
                return ClearResult(
                    success=False,
                    channels_deleted=0,
                    total_channels=0,
                    errors=[f"Category {category_name} not found"],
                    message=f"Soccer category {category_name} not found"
                )
            
            # Get channels to delete
            channels_to_delete = [ch for ch in category.channels if isinstance(ch, discord.TextChannel)]
            total_channels = len(channels_to_delete)
            
            if total_channels == 0:
                return ClearResult(
                    success=True,
                    channels_deleted=0,
                    total_channels=0,
                    errors=[],
                    message="No soccer channels found to delete"
                )
            
            # Delete channels
            deleted_count = 0
            errors = []
            
            for channel in channels_to_delete:
                try:
                    await channel.delete()
                    deleted_count += 1
                    await asyncio.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    error_msg = f"Failed to delete {channel.name}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            return ClearResult(
                success=deleted_count > 0,
                channels_deleted=deleted_count,
                total_channels=total_channels,
                errors=errors,
                message=f"Deleted {deleted_count} out of {total_channels} soccer channels"
            )
            
        except Exception as e:
            logger.error(f"Error clearing soccer channels: {e}")
            return ClearResult(
                success=False,
                channels_deleted=0,
                total_channels=0,
                errors=[str(e)],
                message=f"Failed to clear soccer channels: {str(e)}"
            )
    
    async def get_matches(self, date: str) -> List[Match]:
        """
        Fetch soccer matches for the specified date from MCP service
        
        Args:
            date: Date string in YYYY-MM-DD format
            
        Returns:
            List of Match objects
        """
        try:
            # Convert YYYY-MM-DD to DD-MM-YYYY for soccer MCP
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            mcp_date = date_obj.strftime(self.config.get('date_format', "%d-%m-%Y"))
            
            # Call soccer MCP
            response = await self.mcp_client.call_mcp(
                self.config['mcp_url'],
                "get_betting_matches",
                {"date": mcp_date}
            )
            
            if not response.success:
                logger.error(f"Soccer MCP error: {response.error}")
                return []
            
            # Parse MCP response
            data = await self.mcp_client.parse_mcp_content(response)
            if not data or "matches_by_league" not in data:
                logger.info(f"No soccer matches found for {date}")
                return []
            
            # Convert to Match objects
            matches = []
            for league, league_matches in data["matches_by_league"].items():
                for match_data in league_matches:
                    match = self._convert_to_match_object(match_data, league, mcp_date)
                    if match:
                        matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error fetching soccer matches: {e}")
            return []
    
    async def format_match_analysis(self, match: Match) -> discord.Embed:
        """Create formatted Discord embed for soccer match analysis (legacy fallback)"""
        return self.formatter.create_basic_embed(
            match.home_team,
            match.away_team,
            match.league,
            match.additional_data.get('time', 'TBD'),
            match.odds
        )
    
    def _convert_to_match_object(self, match_data: Dict[str, Any], league: str, match_date: str = None) -> Optional[Match]:
        """Convert MCP match data to Match object"""
        try:
            teams = match_data.get("teams", {})
            home_team = teams.get("home", {}).get("name", "Unknown")
            away_team = teams.get("away", {}).get("name", "Unknown")
            
            # Use the match date from the data or passed parameter
            date = match_data.get("date", match_date)
            
            return Match(
                id=str(match_data.get("id", "")),
                home_team=home_team,
                away_team=away_team,
                league=league,
                datetime=None,  # Could parse match time if needed
                odds=match_data.get("odds"),
                status=match_data.get("status", "scheduled"),
                additional_data={
                    "time": match_data.get("time", "TBD"),
                    "date": date,  # Store the match date for MCP calls
                    "home_id": teams.get("home", {}).get("id"),
                    "away_id": teams.get("away", {}).get("id"),
                    "league_info": match_data.get("league_info", {}),
                    "raw_data": match_data
                }
            )
        except Exception as e:
            logger.error(f"Error converting match data: {e}")
            return None
    
    # Removed: All formatting methods moved to soccer_embed_formatter.py
    # This keeps the soccer handler focused on business logic only
    
    def _create_loading_embed(self, match: Match) -> discord.Embed:
        """Create initial loading embed for a match"""
        embed = discord.Embed(
            title=f"⚽ {match.away_team} vs {match.home_team}",
            description=f"**{match.league}**\n🔄 Loading comprehensive analysis...",
            color=self.config.get('embed_color', 0x00ff00),
            timestamp=datetime.now()
        )
        
        match_time = match.additional_data.get('time', 'TBD')
        embed.add_field(name="⏰ Time", value=match_time, inline=True)
        embed.set_footer(text="Soccer Analysis")
        
        return embed
    
    async def _update_channel_with_analysis(self, message: discord.Message, match: Match):
        """Update channel message with comprehensive analysis"""
        try:
            home_id = match.additional_data.get('home_id')
            away_id = match.additional_data.get('away_id')
            
            if not home_id or not away_id:
                # Update with basic info only
                embed = await self.format_match_analysis(match)
                await message.edit(embed=embed)
                return
            
            # Get comprehensive analysis with match date
            match_date = match.additional_data.get('date', datetime.now().strftime("%d-%m-%Y"))
            h2h_data, home_form_data, away_form_data, match_analysis_data = await self._get_comprehensive_analysis(
                home_id, away_id, match.home_team, match.away_team, 
                match.additional_data.get('league_info', {}).get('id', self.default_league_id),
                match_date
            )
            
            # Create enhanced embed
            embed = self._create_comprehensive_embed(
                match, h2h_data, home_form_data, away_form_data, match_analysis_data
            )
            
            # Update the message
            await message.edit(embed=embed)
            
        except Exception as e:
            logger.error(f"Error updating channel with analysis: {e}")
            # Fallback to basic embed
            try:
                embed = await self.format_match_analysis(match)
                embed.add_field(name="📊 Analysis", value="Analysis failed to load", inline=False)
                await message.edit(embed=embed)
            except Exception as fallback_error:
                logger.error(f"Fallback embed update failed: {fallback_error}")
    
    async def _get_comprehensive_analysis(self, home_id: str, away_id: str, home_team: str, away_team: str, league_id: int, match_date: str = None):
        """Get H2H, form analysis, and comprehensive match betting analysis for both teams"""
        try:
            # Get H2H analysis
            h2h_response = await self.mcp_client.call_mcp(
                self.config['mcp_url'],
                "get_h2h_betting_analysis",
                {
                    "team_1_id": home_id,
                    "team_2_id": away_id,
                    "team_1_name": home_team,
                    "team_2_name": away_team
                }
            )
            
            # Get home team form
            home_form_response = await self.mcp_client.call_mcp(
                self.config['mcp_url'],
                "get_team_form_analysis",
                {
                    "team_id": home_id,
                    "team_name": home_team,
                    "league_id": league_id
                }
            )
            
            # Get away team form
            away_form_response = await self.mcp_client.call_mcp(
                self.config['mcp_url'],
                "get_team_form_analysis",
                {
                    "team_id": away_id,
                    "team_name": away_team,
                    "league_id": league_id
                }
            )
            
            # Get comprehensive match betting analysis
            match_analysis_response = None
            if match_date:
                # Map league_id to league code for the MCP call
                league_map = {228: "EPL", 297: "La Liga", 168: "MLS"}
                league_code = league_map.get(league_id, "EPL")
                
                match_analysis_response = await self.mcp_client.call_mcp(
                    self.config['mcp_url'],
                    "analyze_match_betting",
                    {
                        "home_team": home_team,
                        "away_team": away_team,
                        "league": league_code,
                        "match_date": match_date
                    }
                )
            
            # Parse responses
            h2h_data = await self.mcp_client.parse_mcp_content(h2h_response) if h2h_response.success else None
            home_form_data = await self.mcp_client.parse_mcp_content(home_form_response) if home_form_response.success else None
            away_form_data = await self.mcp_client.parse_mcp_content(away_form_response) if away_form_response.success else None
            match_analysis_data = await self.mcp_client.parse_mcp_content(match_analysis_response) if match_analysis_response and match_analysis_response.success else None
            
            return h2h_data, home_form_data, away_form_data, match_analysis_data
            
        except Exception as e:
            logger.error(f"Error getting comprehensive analysis: {e}")
            return None, None, None, None
    
    def _create_comprehensive_embed(self, match: Match, h2h_data: Dict = None, home_form_data: Dict = None, away_form_data: Dict = None, match_analysis_data: Dict = None) -> discord.Embed:
        """Create comprehensive match embed with clean, professional formatting"""
        embed = discord.Embed(
            title=f"⚽ {match.away_team} vs {match.home_team}",
            description=f"**{match.league}** • {match.additional_data.get('time', 'TBD')}",
            color=0x2F3136,  # Discord dark theme color
            timestamp=datetime.now()
        )
        
        # Add betting odds
        if match.odds:
            self._add_betting_odds_to_embed(embed, match.odds, match.home_team, match.away_team)
        
        # Add H2H analysis
        if h2h_data and "error" not in h2h_data:
            self._add_h2h_analysis_to_embed(embed, h2h_data, match.home_team, match.away_team)
        
        # Add team form analysis
        if home_form_data and "error" not in home_form_data:
            self._add_team_form_to_embed(embed, home_form_data, match.home_team, "🏠 Home Team Form")
        
        if away_form_data and "error" not in away_form_data:
            self._add_team_form_to_embed(embed, away_form_data, match.away_team, "✈️ Away Team Form")
        
        # Add comprehensive match analysis predictions
        if match_analysis_data and "error" not in match_analysis_data:
            self._add_match_predictions_to_embed(embed, match_analysis_data, match.home_team, match.away_team)
        
        # Add betting recommendations (fallback if match analysis not available)
        elif h2h_data and home_form_data and away_form_data:
            self._add_betting_recommendations_to_embed(embed, h2h_data, home_form_data, away_form_data, match.home_team, match.away_team)
        
        embed.set_footer(text="Powered by Soccer MCP • Enhanced Analysis")
        return embed
    
    def _add_betting_odds_to_embed(self, embed: discord.Embed, odds: Dict[str, Any], home_team: str, away_team: str):
        """Add betting odds section to embed"""
        betting_lines = []
        
        # Match winner odds
        match_winner = odds.get('match_winner', {})
        if match_winner:
            home_odds = match_winner.get('home')
            draw_odds = match_winner.get('draw')
            away_odds = match_winner.get('away')
        else:
            home_odds = odds.get('home_win')
            draw_odds = odds.get('draw')
            away_odds = odds.get('away_win')
        
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
        over_under = odds.get('over_under', {})
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
                value=" • ".join(betting_lines),  # Horizontal layout to save space
                inline=False
            )
    
    def _add_h2h_analysis_to_embed(self, embed: discord.Embed, h2h_data: Dict[str, Any], home_team: str, away_team: str):
        """Add head-to-head analysis to embed"""
        total_meetings = h2h_data.get('total_meetings', 0)
        
        # Always show H2H section with cleaner formatting
        if total_meetings > 0:
            team1_record = h2h_data.get('team_1_record', {})
            team2_record = h2h_data.get('team_2_record', {})
            draws = h2h_data.get('draws', {})
            
            # Clean, compact H2H display
            h2h_text = f"**{total_meetings} meetings**\n"
            h2h_text += f"• **{home_team}:** {team1_record.get('wins', 0)}W ({team1_record.get('win_rate', 0):.0f}%)\n"
            h2h_text += f"• **{away_team}:** {team2_record.get('wins', 0)}W ({team2_record.get('win_rate', 0):.0f}%)\n"
            h2h_text += f"• **Draws:** {draws.get('count', 0)}"
            
            embed.add_field(
                name="📊 Head-to-Head",
                value=h2h_text,
                inline=False
            )
            
            # Compact goals analysis
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
            # Compact first meeting display
            embed.add_field(
                name="📊 Head-to-Head",
                value="**First meeting** - No historical data",
                inline=False
            )
    
    def _add_team_form_to_embed(self, embed: discord.Embed, form_data: Dict[str, Any], team_name: str, field_name: str):
        """Add team form analysis to embed with clean formatting"""
        try:
            # Handle the actual MCP form data structure
            record = form_data.get('record', 'N/A')
            form_rating = form_data.get('form_rating', 0)
            win_percentage = form_data.get('win_percentage', 0)
            goals_for = form_data.get('goals_for', 0)
            goals_against = form_data.get('goals_against', 0)
            
            if record != 'N/A' or form_rating > 0:
                # Compact form display with key metrics only
                form_text = f"**{record}** | **{form_rating:.1f}/10**"
                
                if win_percentage > 0:
                    form_text += f"\n{win_percentage:.0f}% win rate"
                    
                if goals_for > 0 or goals_against > 0:
                    form_text += f"\n{goals_for} for, {goals_against} against"
                
                # Add form rating emoji
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
                # Compact no data display
                embed.add_field(
                    name=f"📊 {field_name}",
                    value="No recent UEFA form",
                    inline=True
                )
        except Exception as e:
            logger.error(f"Error adding team form to embed: {e}")
            embed.add_field(
                name=f"❌ {field_name}",
                value="Form data error",
                inline=True
            )
    
    def _add_betting_recommendations_to_embed(self, embed: discord.Embed, h2h_data: Dict, home_form_data: Dict, away_form_data: Dict, home_team: str, away_team: str):
        """Add betting recommendations based on comprehensive data"""
        recommendations = []
        
        # Calculate expected goals from form data
        home_recent = home_form_data.get('recent_form', {})
        away_recent = away_form_data.get('recent_form', {})
        
        if home_recent and away_recent:
            home_avg_scored = home_recent.get('goals_scored', 0) / 5 if home_recent.get('goals_scored') else 0
            home_avg_conceded = home_recent.get('goals_conceded', 0) / 5 if home_recent.get('goals_conceded') else 0
            away_avg_scored = away_recent.get('goals_scored', 0) / 5 if away_recent.get('goals_scored') else 0
            away_avg_conceded = away_recent.get('goals_conceded', 0) / 5 if away_recent.get('goals_conceded') else 0
            
            expected_goals = (home_avg_scored + away_avg_conceded + away_avg_scored + home_avg_conceded) / 2
            
            if expected_goals > 2.8:
                recommendations.append("🎯 **OVER 2.5 Goals** - Based on recent form")
            elif expected_goals < 2.2:
                recommendations.append("🎯 **UNDER 2.5 Goals** - Based on recent form")
            
            # Form momentum
            home_form_record = home_recent.get('last_5_games', {})
            away_form_record = away_recent.get('last_5_games', {})
            
            home_points = (home_form_record.get('wins', 0) * 3) + home_form_record.get('draws', 0)
            away_points = (away_form_record.get('wins', 0) * 3) + away_form_record.get('draws', 0)
            
            if home_points > away_points + 3:
                recommendations.append(f"📈 **{home_team}** has better recent momentum")
            elif away_points > home_points + 3:
                recommendations.append(f"📈 **{away_team}** has better recent momentum")
        
        if recommendations:
            embed.add_field(
                name="🎯 Smart Betting Tips",
                value="\n".join(recommendations),
                inline=False
            )
    
    def _add_match_predictions_to_embed(self, embed: discord.Embed, match_analysis_data: Dict[str, Any], home_team: str, away_team: str):
        """Add comprehensive match predictions with clean formatting"""
        try:
            # Extract prediction data
            predictions = match_analysis_data.get('predictions', {})
            match_winner = predictions.get('match_winner', {})
            goals_pred = predictions.get('goals', {})
            insights = predictions.get('key_insights', [])
            
            # Winner prediction - compact format
            if match_winner:
                prediction = match_winner.get('prediction', 'Unknown')
                confidence = match_winner.get('confidence_percentage', 0)
                
                if confidence > 0:
                    embed.add_field(
                        name="🎯 Prediction",
                        value=f"**{prediction}** ({confidence}%)",
                        inline=True
                    )
            
            # Goals prediction - compact format  
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
            
            # Key insights - clean bullets, max 3 lines
            if insights:
                clean_insights = []
                for insight in insights[:3]:
                    # Clean up insight text
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
            logger.error(f"Error adding match predictions to embed: {e}")
            # Don't show error to users, just log it

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