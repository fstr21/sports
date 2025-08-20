"""
Soccer-specific handler implementing the BaseSportHandler interface
CLEAN VERSION - All formatting moved to soccer_embed_formatter.py
"""
import asyncio
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import discord

from core.base_sport_handler import BaseSportHandler, Match, ChannelCreationResult, ClearResult
from sports.soccer_embed_formatter import DynamicLayoutSoccerEmbedFormatter


logger = logging.getLogger(__name__)


class SoccerHandler(BaseSportHandler):
    """
    Soccer-specific implementation of BaseSportHandler
    Handles soccer match data, channel creation, and comprehensive analysis
    CLEAN VERSION: Formatting logic moved to dedicated SoccerEmbedFormatter
    """
    
    def __init__(self, sport_name: str, config: Dict[str, Any], mcp_client):
        """Initialize soccer handler with soccer-specific configuration"""
        super().__init__(sport_name, config, mcp_client)
        self.default_league_id = config.get('default_league_id', 297)  # La Liga default
        self.formatter = DynamicLayoutSoccerEmbedFormatter(config)
        
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
    
    async def _update_channel_with_analysis(self, message: discord.Message, match: Match):
        """Update channel message with comprehensive analysis"""
        try:
            home_id = match.additional_data.get('home_id')
            away_id = match.additional_data.get('away_id')
            
            if not home_id or not away_id:
                # Update with basic info only using formatter
                embed = self.formatter.create_basic_embed(
                    match.home_team,
                    match.away_team,
                    match.league,
                    match.additional_data.get('time', 'TBD'),
                    match.odds
                )
                await message.edit(embed=embed)
                return
            
            # Get comprehensive analysis with match date
            match_date = match.additional_data.get('date', datetime.now().strftime("%d-%m-%Y"))
            h2h_data, home_form_data, away_form_data, match_analysis_data = await self._get_comprehensive_analysis(
                home_id, away_id, match.home_team, match.away_team, 
                match.additional_data.get('league_info', {}).get('id', self.default_league_id),
                match_date
            )
            
            # Create enhanced embed using formatter
            embed = self.formatter.create_comprehensive_embed(
                match.home_team,
                match.away_team,
                match.league,
                match.additional_data.get('time', 'TBD'),
                match.odds,
                h2h_data,
                home_form_data,
                away_form_data,
                match_analysis_data
            )
            
            # Update the message
            await message.edit(embed=embed)
            
        except Exception as e:
            logger.error(f"Error updating channel with analysis: {e}")
            # Fallback to basic embed using formatter
            try:
                embed = self.formatter.create_basic_embed(
                    match.home_team,
                    match.away_team,
                    match.league,
                    match.additional_data.get('time', 'TBD'),
                    match.odds
                )
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