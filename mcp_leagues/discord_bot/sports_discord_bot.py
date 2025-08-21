#!/usr/bin/env python3
"""
Enhanced Sports Discord Bot - Full Modular Architecture Implementation
Uses the new sport handlers, MCP client, and comprehensive error handling
"""
import asyncio
import logging
import os
from datetime import datetime
import discord
from discord.ext import commands
from discord import app_commands
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

# Import our new core infrastructure
from core.mcp_client import MCPClient
from core.sync_manager import SyncManager
from core.sport_manager import SportManager
from config import config

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Print statements moved to main section


class EnhancedSportsBot(commands.Bot):
    """Enhanced Sports Bot using the full modular architecture"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=None,
            intents=intents,
            description="Enhanced Sports Bot v2.0 - Full Architecture"
        )
        
        # Initialize core components
        self.mcp_client = MCPClient(timeout=30.0, max_retries=3)
        self.sync_manager = SyncManager(self, required_permissions=["manage_channels"])
        self.sport_manager = SportManager(config, self.mcp_client)
        
        # Store configuration
        self.config = config
        
        logger.info(f"Enhanced bot initialized with configuration for: {', '.join(self.config.get_enabled_sports())}")
    
    async def setup_hook(self):
        """Setup hook called when bot is starting"""
        logger.info("Setting up enhanced bot...")
        
        # Ensure MCP client is ready
        await self.mcp_client._ensure_client()
        
        # Load sport handlers
        self.sport_manager.load_sports()
        
        # Validate sport handlers
        validation_errors = self.sport_manager.validate_sports()
        if validation_errors:
            logger.warning(f"Sport validation warnings: {validation_errors}")
        
        # Update command choices based on available sports
        self._update_command_choices()
        
        logger.info("Enhanced bot setup complete")
    
    async def close(self):
        """Cleanup when bot is shutting down"""
        logger.info("Shutting down enhanced bot...")
        await self.mcp_client.close()
        await super().close()
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Enhanced bot ready: {self.user}")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        logger.info(f"Available sports: {', '.join(self.sport_manager.get_available_sports())}")
        
        # Auto-sync commands on startup (optional)
        try:
            synced = await self.tree.sync()
            logger.info(f"Auto-synced {len(synced)} commands on startup")
        except Exception as e:
            logger.error(f"Auto-sync failed: {e}")
    
    def _update_command_choices(self):
        """Log available sports (choices are defined statically)"""
        available_sports = self.sport_manager.get_available_sports()
        logger.info(f"Available sports for commands: {', '.join(available_sports)}")


# Initialize bot
bot = EnhancedSportsBot()


@bot.tree.command(name="sync", description="Synchronize bot commands (Admin only)")
async def sync_commands(interaction: discord.Interaction):
    """Synchronize Discord commands"""
    await interaction.response.defer(ephemeral=True)
    
    try:
        result = await bot.sync_manager.sync_commands(interaction, guild_only=True)
        embed = bot.sync_manager.create_sync_embed(result)
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Sync command error: {e}")
        embed = discord.Embed(
            title="❌ Sync Error",
            description=f"An error occurred during sync: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="create-channels", description="Create game channels for selected sport")
@app_commands.describe(sport="Choose a sport")
@app_commands.choices(sport=[
    app_commands.Choice(name="Soccer", value="soccer"),
    app_commands.Choice(name="MLB", value="mlb"),
])
async def create_channels(interaction: discord.Interaction, sport: app_commands.Choice[str]):
    """Create channels for today's games using sport handlers"""
    await interaction.response.defer()
    
    try:
        # Get sport handler
        handler = bot.sport_manager.get_sport_handler(sport.value)
        if not handler:
            embed = discord.Embed(
                title="❌ Sport Not Available",
                description=f"Sport `{sport.value}` is not available or not configured.",
                color=discord.Color.red()
            )
            available_sports = ", ".join(bot.sport_manager.get_available_sports())
            if available_sports:
                embed.add_field(name="Available Sports", value=available_sports, inline=False)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Validate permissions
        if not handler.validate_permissions(interaction):
            embed = discord.Embed(
                title="❌ Insufficient Permissions",
                description="You need `Manage Channels` permission to use this command.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
        
        logger.info(f"Current time: {current_time}")
        logger.info(f"Creating {sport.value} channels for {today} - requested by {interaction.user.name}")
        
        # Use sport handler to create channels
        result = await handler.create_channels(interaction, today)
        
        # Create result embed
        if result.success:
            embed = discord.Embed(
                title="✅ Channels Created",
                description=result.message,
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📊 Summary",
                value=f"**Created:** {result.channels_created}\n**Total Games:** {result.total_matches}",
                inline=True
            )
            
            if result.errors:
                error_text = "\\n".join([f"• {error}" for error in result.errors[:3]])
                if len(result.errors) > 3:
                    error_text += f"\\n... and {len(result.errors) - 3} more errors"
                embed.add_field(name="⚠️ Errors", value=error_text, inline=False)
        else:
            embed = discord.Embed(
                title="❌ Channel Creation Failed",
                description=result.message,
                color=discord.Color.red()
            )
            
            if result.errors:
                error_text = "\\n".join([f"• {error}" for error in result.errors[:3]])
                if len(result.errors) > 3:
                    error_text += f"\\n... and {len(result.errors) - 3} more errors"
                embed.add_field(name="🔍 Errors", value=error_text, inline=False)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in create-channels command: {e}")
        embed = discord.Embed(
            title="❌ Command Error",
            description=f"An unexpected error occurred: {str(e)}",
            color=discord.Color.red()
        )
        embed.add_field(
            name="💡 Try:",
            value="• Check if the MCP service is available\n• Try again in a few moments\n• Contact an administrator if this persists",
            inline=False
        )
        await interaction.followup.send(embed=embed)


@bot.tree.command(name="clear-channels", description="Clear all channels from selected sport category")
@app_commands.describe(sport="Choose a sport category to clear")
@app_commands.choices(sport=[
    app_commands.Choice(name="Soccer", value="soccer"),
    app_commands.Choice(name="MLB", value="mlb"),
])
async def clear_channels(interaction: discord.Interaction, sport: app_commands.Choice[str]):
    """Clear all channels from a specific sport category using sport handlers"""
    await interaction.response.defer()
    
    try:
        # Get sport handler
        handler = bot.sport_manager.get_sport_handler(sport.value)
        if not handler:
            embed = discord.Embed(
                title="❌ Sport Not Available",
                description=f"Sport `{sport.value}` is not available or not configured.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Validate permissions
        if not handler.validate_permissions(interaction):
            embed = discord.Embed(
                title="❌ Insufficient Permissions",
                description="You need `Manage Channels` permission to use this command.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        logger.info(f"Clearing {sport.value} channels - requested by {interaction.user.name}")
        
        # Use sport handler to clear channels
        result = await handler.clear_channels(interaction, handler.category_name)
        
        # Create result embed
        if result.success:
            embed = discord.Embed(
                title="✅ Channels Cleared",
                description=result.message,
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📊 Summary",
                value=f"**Deleted:** {result.channels_deleted}\n**Total Found:** {result.total_channels}",
                inline=True
            )
            
            if result.errors:
                error_text = "\\n".join([f"• {error}" for error in result.errors[:3]])
                if len(result.errors) > 3:
                    error_text += f"\\n... and {len(result.errors) - 3} more errors"
                embed.add_field(name="⚠️ Errors", value=error_text, inline=False)
        else:
            embed = discord.Embed(
                title="❌ Channel Clear Failed",
                description=result.message,
                color=discord.Color.red()
            )
            
            if result.errors:
                error_text = "\\n".join([f"• {error}" for error in result.errors[:3]])
                if len(result.errors) > 3:
                    error_text += f"\\n... and {len(result.errors) - 3} more errors"
                embed.add_field(name="🔍 Errors", value=error_text, inline=False)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in clear-channels command: {e}")
        embed = discord.Embed(
            title="❌ Command Error",
            description=f"An unexpected error occurred: {str(e)}",
            color=discord.Color.red()
        )
        try:
            await interaction.followup.send(embed=embed)
        except discord.NotFound:
            # Interaction may have expired, try edit_original_response
            try:
                await interaction.edit_original_response(embed=embed)
            except:
                # If all else fails, just log the error
                logger.error(f"Failed to send error response for clear-channels: {str(e)}")


@bot.tree.command(name="status", description="Show bot status and available sports")
async def status_command(interaction: discord.Interaction):
    """Show bot status and health information"""
    embed = discord.Embed(
        title="🤖 Bot Status",
        description="Enhanced Sports Bot v2.0 Status",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    # Available sports
    available_sports = bot.sport_manager.get_available_sports()
    if available_sports:
        embed.add_field(
            name="📊 Available Sports",
            value=", ".join([sport.upper() for sport in available_sports]),
            inline=False
        )
    else:
        embed.add_field(
            name="⚠️ Sports Status",
            value="No sports currently available",
            inline=False
        )
    
    # MCP Client status
    mcp_status = "🟢 Healthy" if bot.mcp_client.is_healthy() else "🔴 Unhealthy"
    embed.add_field(
        name="🔗 MCP Client",
        value=mcp_status,
        inline=True
    )
    
    # Guild info
    embed.add_field(
        name="🏠 Guilds",
        value=str(len(bot.guilds)),
        inline=True
    )
    
    # Last sync info
    sync_status = bot.sync_manager.get_sync_status()
    if sync_status.get("last_sync"):
        last_sync = sync_status["last_sync"]
        sync_success = sync_status["last_sync_success"]
        sync_text = f"✅ {last_sync.strftime('%Y-%m-%d %H:%M:%S')}" if sync_success else f"❌ {last_sync.strftime('%Y-%m-%d %H:%M:%S')}"
        embed.add_field(
            name="🔄 Last Sync",
            value=sync_text,
            inline=True
        )
    
    embed.set_footer(text="Enhanced Sports Bot v2.0")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="help", description="Show bot help and available commands")
async def help_command(interaction: discord.Interaction):
    """Show help information"""
    embed = discord.Embed(
        title="🏈 Enhanced Sports Bot v2.0",
        description="Modular sports bot with comprehensive analysis and error handling",
        color=discord.Color.blue()
    )
    
    # Available sports
    available_sports = bot.sport_manager.get_available_sports()
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
            "`/create-channels <sport>` - Create channels for today's games\n"
            "`/clear-channels <sport>` - Clear all channels for a sport\n"
            "`/status` - Show bot status and health\n"
            "`/sync` - Sync bot commands (Admin only)\n"
            "`/help` - Show this help message"
        ),
        inline=False
    )
    
    # Features
    embed.add_field(
        name="✨ Features",
        value=(
            "• Comprehensive match analysis\n"
            "• Head-to-head statistics\n"
            "• Team form analysis\n"
            "• Betting odds and recommendations\n"
            "• Robust error handling\n"
            "• Modular sport architecture"
        ),
        inline=False
    )
    
    # Permissions
    embed.add_field(
        name="🔒 Required Permissions",
        value="Manage Channels (for create/clear commands)",
        inline=False
    )
    
    embed.set_footer(text="Enhanced Sports Bot v2.0 - Full Modular Architecture")
    await interaction.response.send_message(embed=embed)


# Health check endpoint for Railway
async def health_check(request):
    """Health check endpoint"""
    health_data = {
        "status": "healthy",
        "bot": str(bot.user) if bot.user else "not ready",
        "sports": bot.sport_manager.get_available_sports() if hasattr(bot, 'sport_manager') else [],
        "mcp_client": bot.mcp_client.is_healthy() if hasattr(bot, 'mcp_client') else False
    }
    return JSONResponse(health_data)


# Starlette app for health checks
app = Starlette(routes=[
    Route("/health", health_check, methods=["GET"]),
])


async def run_bot():
    """Run the Discord bot"""
    try:
        await bot.start(bot.config.discord_token)
    except Exception as e:
        logger.error(f"Bot failed to start: {e}")
        raise


async def main():
    """Main function to run both Discord bot and health check server"""
    port = int(os.getenv("PORT", 8080))
    config_server = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config_server)
    
    # Run both Discord bot and health check server concurrently
    await asyncio.gather(run_bot(), server.serve())


if __name__ == "__main__":
    print("Starting Enhanced Sports Discord Bot v2.0")
    print(f"Discord Token: {'SET' if config.discord_token else 'MISSING'}")
    asyncio.run(main())