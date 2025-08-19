"""
Command router for routing sport-specific commands to appropriate handlers
"""
import logging
from typing import Optional, List, Dict, Any
import discord
from discord.ext import commands
from .sport_manager import SportManager
from .base_sport_handler import BaseSportHandler


logger = logging.getLogger(__name__)


class CommandRouter:
    """
    Routes sport-specific commands to appropriate handlers with
    parameter validation and consistent error handling
    """
    
    def __init__(self, sport_manager: SportManager):
        """
        Initialize command router
        
        Args:
            sport_manager: SportManager instance
        """
        self.sport_manager = sport_manager
    
    async def route_create_channels(self, interaction: discord.Interaction, sport: str, date: str = None) -> bool:
        """
        Route create-channels command to appropriate sport handler
        
        Args:
            interaction: Discord interaction object
            sport: Sport name
            date: Date string (optional, defaults to today)
            
        Returns:
            True if command was handled successfully
        """
        try:
            # Get sport handler
            handler = self.sport_manager.get_sport_handler(sport)
            if not handler:
                await self._send_sport_not_found_error(interaction, sport)
                return False
            
            # Validate permissions
            if not handler.validate_permissions(interaction):
                await self._send_permission_error(interaction)
                return False
            
            # Use today's date if not provided
            if not date:
                from datetime import datetime
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Validate date format
            if not self._validate_date_format(date):
                await self._send_date_format_error(interaction)
                return False
            
            logger.info(f"Routing create-channels command: sport={sport}, date={date}, user={interaction.user.name}")
            
            # Route to sport handler
            result = await handler.create_channels(interaction, date)
            
            # Log result
            if result.success:
                logger.info(f"Create channels successful: {result.channels_created} channels created for {sport}")
            else:
                logger.warning(f"Create channels failed for {sport}: {result.message}")
            
            return result.success
            
        except Exception as e:
            logger.error(f"Error routing create-channels command: {e}")
            await self._send_generic_error(interaction, f"Error creating {sport} channels: {str(e)}")
            return False
    
    async def route_clear_channels(self, interaction: discord.Interaction, sport: str) -> bool:
        """
        Route clear-channels command to appropriate sport handler
        
        Args:
            interaction: Discord interaction object
            sport: Sport name
            
        Returns:
            True if command was handled successfully
        """
        try:
            # Get sport handler
            handler = self.sport_manager.get_sport_handler(sport)
            if not handler:
                await self._send_sport_not_found_error(interaction, sport)
                return False
            
            # Validate permissions
            if not handler.validate_permissions(interaction):
                await self._send_permission_error(interaction)
                return False
            
            logger.info(f"Routing clear-channels command: sport={sport}, user={interaction.user.name}")
            
            # Route to sport handler
            result = await handler.clear_channels(interaction, handler.category_name)
            
            # Log result
            if result.success:
                logger.info(f"Clear channels successful: {result.channels_deleted} channels deleted for {sport}")
            else:
                logger.warning(f"Clear channels failed for {sport}: {result.message}")
            
            return result.success
            
        except Exception as e:
            logger.error(f"Error routing clear-channels command: {e}")
            await self._send_generic_error(interaction, f"Error clearing {sport} channels: {str(e)}")
            return False
    
    def get_sport_choices(self) -> List[Dict[str, str]]:
        """
        Get available sports as Discord command choices
        
        Returns:
            List of choice dictionaries for Discord commands
        """
        choices = []
        for sport_name in self.sport_manager.get_available_sports():
            display_name = sport_name.upper()
            choices.append({
                "name": display_name,
                "value": sport_name
            })
        return choices
    
    def validate_sport(self, sport: str) -> bool:
        """
        Validate if sport is available
        
        Args:
            sport: Sport name to validate
            
        Returns:
            True if sport is available
        """
        return self.sport_manager.is_sport_available(sport)
    
    def get_sport_handler(self, sport: str) -> Optional[BaseSportHandler]:
        """
        Get sport handler for given sport
        
        Args:
            sport: Sport name
            
        Returns:
            Sport handler or None if not found
        """
        return self.sport_manager.get_sport_handler(sport)
    
    async def _send_sport_not_found_error(self, interaction: discord.Interaction, sport: str):
        """Send sport not found error message"""
        available_sports = ", ".join(self.sport_manager.get_available_sports())
        
        embed = discord.Embed(
            title="❌ Sport Not Available",
            description=f"Sport `{sport}` is not available or not configured.",
            color=discord.Color.red()
        )
        
        if available_sports:
            embed.add_field(
                name="Available Sports",
                value=available_sports,
                inline=False
            )
        else:
            embed.add_field(
                name="Configuration Issue",
                value="No sports are currently configured. Please check bot configuration.",
                inline=False
            )
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def _send_permission_error(self, interaction: discord.Interaction):
        """Send permission error message"""
        embed = discord.Embed(
            title="❌ Insufficient Permissions",
            description="You need `Manage Channels` permission to use this command.",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Required Permission",
            value="Manage Channels",
            inline=True
        )
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def _send_date_format_error(self, interaction: discord.Interaction):
        """Send date format error message"""
        embed = discord.Embed(
            title="❌ Invalid Date Format",
            description="Please use YYYY-MM-DD format for dates.",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Example",
            value="2024-03-15",
            inline=True
        )
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def _send_generic_error(self, interaction: discord.Interaction, error_message: str):
        """Send generic error message"""
        embed = discord.Embed(
            title="❌ Command Error",
            description=error_message,
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="💡 Troubleshooting",
            value="If this error persists, please contact an administrator.",
            inline=False
        )
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def _validate_date_format(self, date_str: str) -> bool:
        """
        Validate date string format (YYYY-MM-DD)
        
        Args:
            date_str: Date string to validate
            
        Returns:
            True if format is valid
        """
        try:
            from datetime import datetime
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    async def get_command_help(self, interaction: discord.Interaction, command_name: str = None):
        """
        Provide help information for commands
        
        Args:
            interaction: Discord interaction object
            command_name: Specific command to get help for (optional)
        """
        embed = discord.Embed(
            title="🏈 Sports Bot Commands",
            description="Available commands for managing sports channels",
            color=discord.Color.blue()
        )
        
        # Available sports
        available_sports = self.sport_manager.get_available_sports()
        if available_sports:
            embed.add_field(
                name="📊 Available Sports",
                value=", ".join([sport.upper() for sport in available_sports]),
                inline=False
            )
        
        # Commands
        embed.add_field(
            name="📝 Commands",
            value=(
                "`/create-channels <sport>` - Create channels for today's games\\n"
                "`/clear-channels <sport>` - Clear all channels for a sport\\n"
                "`/sync` - Sync bot commands (Admin only)\\n"
                "`/help` - Show this help message"
            ),
            inline=False
        )
        
        # Permissions
        embed.add_field(
            name="🔒 Required Permissions",
            value="Manage Channels (for create/clear commands)",
            inline=False
        )
        
        embed.set_footer(text="Sports Bot v2.0 - Enhanced Multi-Sport Architecture")
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)