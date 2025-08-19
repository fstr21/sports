"""
Comprehensive error handling system with user-friendly messages
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import discord
from discord.ext import commands


logger = logging.getLogger(__name__)


class ErrorHandler:
    """
    Centralized error handling with user-friendly messages and recovery suggestions
    """
    
    @staticmethod
    def create_error_embed(title: str, description: str, error_type: str = "error") -> discord.Embed:
        """
        Create standardized error embed
        
        Args:
            title: Error title
            description: Error description
            error_type: Type of error (error, warning, info)
            
        Returns:
            Discord embed with error information
        """
        color_map = {
            "error": discord.Color.red(),
            "warning": discord.Color.orange(),
            "info": discord.Color.blue()
        }
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=color_map.get(error_type, discord.Color.red()),
            timestamp=datetime.now()
        )
        
        return embed
    
    @staticmethod
    def mcp_timeout_error(sport: str, timeout_duration: float = 30.0) -> discord.Embed:
        """Create embed for MCP timeout errors"""
        embed = ErrorHandler.create_error_embed(
            title="⏱️ Request Timeout",
            description=f"The {sport.upper()} service took too long to respond (>{timeout_duration}s)."
        )
        
        embed.add_field(
            name="💡 What you can do:",
            value=(
                "• Try again in a few moments\\n"
                "• The service might be experiencing high load\\n"
                "• Check if the date has available games"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔧 If this persists:",
            value="Contact an administrator - the MCP service may need attention",
            inline=False
        )
        
        return embed
    
    @staticmethod
    def mcp_connection_error(sport: str, error_details: str = None) -> discord.Embed:
        """Create embed for MCP connection errors"""
        embed = ErrorHandler.create_error_embed(
            title="🔌 Service Connection Error",
            description=f"Unable to connect to the {sport.upper()} data service."
        )
        
        embed.add_field(
            name="💡 What you can do:",
            value=(
                "• Try again in a few minutes\\n"
                "• The service might be temporarily unavailable\\n"
                "• Check your internet connection"
            ),
            inline=False
        )
        
        if error_details:
            embed.add_field(
                name="🔍 Technical Details:",
                value=f"```{error_details[:500]}```",
                inline=False
            )
        
        embed.add_field(
            name="🔧 If this persists:",
            value="Contact an administrator - the service may be down",
            inline=False
        )
        
        return embed
    
    @staticmethod
    def permission_error(required_permission: str, current_permissions: list = None) -> discord.Embed:
        """Create embed for permission errors"""
        embed = ErrorHandler.create_error_embed(
            title="🔒 Insufficient Permissions",
            description=f"You need the `{required_permission}` permission to use this command."
        )
        
        embed.add_field(
            name="📋 Required Permission:",
            value=f"`{required_permission}`",
            inline=True
        )
        
        if current_permissions:
            embed.add_field(
                name="✅ Your Permissions:",
                value="\\n".join([f"• {perm}" for perm in current_permissions[:5]]),
                inline=True
            )
        
        embed.add_field(
            name="💡 How to fix:",
            value=(
                "• Ask a server administrator for the required permission\\n"
                "• Make sure you have a role with channel management rights"
            ),
            inline=False
        )
        
        return embed
    
    @staticmethod
    def data_unavailable_error(sport: str, date: str, reason: str = None) -> discord.Embed:
        """Create embed for data unavailable errors"""
        embed = ErrorHandler.create_error_embed(
            title="📅 No Data Available",
            description=f"No {sport.upper()} games found for {date}.",
            error_type="warning"
        )
        
        embed.add_field(
            name="🤔 Possible reasons:",
            value=(
                f"• No {sport.upper()} games scheduled for this date\\n"
                "• Games may not be available yet\\n"
                "• Service may be updating data"
            ),
            inline=False
        )
        
        if reason:
            embed.add_field(
                name="📝 Additional Info:",
                value=reason,
                inline=False
            )
        
        embed.add_field(
            name="💡 Try:",
            value=(
                "• Check a different date\\n"
                "• Try again in a few minutes\\n"
                "• Verify the sport is in season"
            ),
            inline=False
        )
        
        return embed
    
    @staticmethod
    def rate_limit_error(retry_after: float = None) -> discord.Embed:
        """Create embed for rate limit errors"""
        embed = ErrorHandler.create_error_embed(
            title="🚦 Rate Limited",
            description="Too many requests have been made. Please wait before trying again.",
            error_type="warning"
        )
        
        if retry_after:
            embed.add_field(
                name="⏰ Wait Time:",
                value=f"{retry_after:.1f} seconds",
                inline=True
            )
        
        embed.add_field(
            name="💡 What's happening:",
            value=(
                "• Discord or the data service is limiting requests\\n"
                "• This protects the service from overload\\n"
                "• Your request will work after the wait time"
            ),
            inline=False
        )
        
        return embed
    
    @staticmethod
    def channel_creation_error(sport: str, failed_channels: int, total_channels: int, errors: list = None) -> discord.Embed:
        """Create embed for channel creation errors"""
        success_count = total_channels - failed_channels
        
        if success_count > 0:
            embed = ErrorHandler.create_error_embed(
                title="⚠️ Partial Channel Creation",
                description=f"Created {success_count}/{total_channels} {sport.upper()} channels. {failed_channels} failed.",
                error_type="warning"
            )
        else:
            embed = ErrorHandler.create_error_embed(
                title="❌ Channel Creation Failed",
                description=f"Failed to create {sport.upper()} channels."
            )
        
        if errors:
            error_text = "\\n".join([f"• {error}" for error in errors[:5]])
            if len(errors) > 5:
                error_text += f"\\n... and {len(errors) - 5} more errors"
            
            embed.add_field(
                name="🔍 Errors:",
                value=error_text,
                inline=False
            )
        
        embed.add_field(
            name="💡 Common solutions:",
            value=(
                "• Check bot permissions in the category\\n"
                "• Ensure the category isn't full (50 channel limit)\\n"
                "• Try creating fewer channels at once"
            ),
            inline=False
        )
        
        return embed
    
    @staticmethod
    def generic_error(operation: str, error_message: str, suggestions: list = None) -> discord.Embed:
        """Create embed for generic errors"""
        embed = ErrorHandler.create_error_embed(
            title=f"❌ {operation} Error",
            description=f"An error occurred during {operation.lower()}."
        )
        
        embed.add_field(
            name="🔍 Error Details:",
            value=f"```{error_message[:500]}```",
            inline=False
        )
        
        if suggestions:
            suggestion_text = "\\n".join([f"• {suggestion}" for suggestion in suggestions])
            embed.add_field(
                name="💡 Suggestions:",
                value=suggestion_text,
                inline=False
            )
        else:
            embed.add_field(
                name="💡 General troubleshooting:",
                value=(
                    "• Try the command again\\n"
                    "• Check your permissions\\n"
                    "• Contact an administrator if the issue persists"
                ),
                inline=False
            )
        
        return embed
    
    @staticmethod
    def configuration_error(missing_config: str, sport: str = None) -> discord.Embed:
        """Create embed for configuration errors"""
        if sport:
            title = f"⚙️ {sport.upper()} Configuration Error"
            description = f"The {sport.upper()} sport is not properly configured."
        else:
            title = "⚙️ Configuration Error"
            description = "Bot configuration is incomplete or invalid."
        
        embed = ErrorHandler.create_error_embed(title=title, description=description)
        
        embed.add_field(
            name="🔧 Missing Configuration:",
            value=f"`{missing_config}`",
            inline=False
        )
        
        embed.add_field(
            name="👨‍💻 For Administrators:",
            value=(
                "• Check environment variables\\n"
                "• Verify MCP service URLs\\n"
                "• Review bot configuration files"
            ),
            inline=False
        )
        
        return embed
    
    @staticmethod
    async def handle_command_error(interaction: discord.Interaction, error: Exception, context: Dict[str, Any] = None):
        """
        Handle command errors with appropriate user feedback
        
        Args:
            interaction: Discord interaction object
            error: Exception that occurred
            context: Additional context information
        """
        logger.error(f"Command error: {error}", exc_info=True)
        
        # Determine error type and create appropriate embed
        if isinstance(error, commands.MissingPermissions):
            embed = ErrorHandler.permission_error(
                required_permission="Manage Channels",
                current_permissions=getattr(interaction.user, 'guild_permissions', None)
            )
        elif isinstance(error, commands.CommandOnCooldown):
            embed = ErrorHandler.rate_limit_error(error.retry_after)
        elif "timeout" in str(error).lower():
            sport = context.get('sport', 'service') if context else 'service'
            embed = ErrorHandler.mcp_timeout_error(sport)
        elif "connection" in str(error).lower():
            sport = context.get('sport', 'service') if context else 'service'
            embed = ErrorHandler.mcp_connection_error(sport, str(error))
        else:
            operation = context.get('operation', 'Command') if context else 'Command'
            embed = ErrorHandler.generic_error(operation, str(error))
        
        # Send error message
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as send_error:
            logger.error(f"Failed to send error message: {send_error}")
    
    @staticmethod
    def log_error(error: Exception, context: Dict[str, Any] = None):
        """
        Log error with context information
        
        Args:
            error: Exception to log
            context: Additional context information
        """
        context_str = ""
        if context:
            context_items = [f"{k}={v}" for k, v in context.items()]
            context_str = f" [{', '.join(context_items)}]"
        
        logger.error(f"Error{context_str}: {error}", exc_info=True)