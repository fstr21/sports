#!/usr/bin/env python3
"""
Enhanced Sports Discord Bot - Using New Core Infrastructure
Modular architecture with improved error handling and command synchronization
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
from config import config

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnhancedSportsBot(commands.Bot):
    """Enhanced Sports Bot using the new modular architecture"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=None,
            intents=intents,
            description="Enhanced Sports Bot v2.0"
        )
        
        # Initialize core components
        self.mcp_client = MCPClient(timeout=30.0, max_retries=3)
        self.sync_manager = SyncManager(self, required_permissions=["manage_channels"])
        
        # Store configuration
        self.config = config
        
        logger.info(f"Bot initialized with {len(self.config.get_enabled_sports())} sports: {', '.join(self.config.get_enabled_sports())}")
    
    async def setup_hook(self):
        """Setup hook called when bot is starting"""
        logger.info("Setting up bot...")
        
        # Ensure MCP client is ready
        await self.mcp_client._ensure_client()
        
        logger.info("Bot setup complete")
    
    async def close(self):
        """Cleanup when bot is shutting down"""
        logger.info("Shutting down bot...")
        await self.mcp_client.close()
        await super().close()
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Bot ready: {self.user}")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        
        # Auto-sync commands on startup (optional)
        try:
            synced = await self.tree.sync()
            logger.info(f"Auto-synced {len(synced)} commands on startup")
        except Exception as e:
            logger.error(f"Auto-sync failed: {e}")
    
    async def call_mcp_legacy(self, url: str, tool: str, args: dict = None) -> dict:
        """
        Legacy MCP call method for backward compatibility
        This wraps the new MCPClient for existing code
        """
        response = await self.mcp_client.call_mcp(url, tool, args)
        
        if response.success:
            return response.data
        else:
            return {"error": response.error}


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
async def create_channels(interaction: discord.Interaction, sport: app_commands.Choice[str]):
    """Create channels for today's games"""
    await interaction.response.defer()
    
    # Validate permissions
    if not interaction.user.guild_permissions.manage_channels:
        embed = discord.Embed(
            title="❌ Insufficient Permissions",
            description="You need `Manage Channels` permission to use this command.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    # Get sport configuration
    sport_config = bot.config.get_sport_config(sport.value)
    if not sport_config:
        embed = discord.Embed(
            title="❌ Sport Not Available",
            description=f"Sport `{sport.value}` is not configured or available.",
            color=discord.Color.red()
        )
        available_sports = ", ".join(bot.config.get_enabled_sports())
        if available_sports:
            embed.add_field(name="Available Sports", value=available_sports, inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    # Get today's date
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        logger.info(f"Creating {sport.value} channels for {today} - requested by {interaction.user.name}")
        
        if sport.value == "soccer":
            await create_soccer_channels_v2(interaction, today, sport_config)
        elif sport.value == "mlb":
            await create_mlb_channels_v2(interaction, today, sport_config)
        else:
            embed = discord.Embed(
                title="🚧 Coming Soon",
                description=f"{sport.value.upper()} channel creation is not implemented yet.",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed)
            
    except Exception as e:
        logger.error(f"Error creating {sport.value} channels: {e}")
        embed = discord.Embed(
            title="❌ Channel Creation Error",
            description=f"An error occurred while creating {sport.value.upper()} channels.",
            color=discord.Color.red()
        )
        embed.add_field(name="Error Details", value=str(e)[:500], inline=False)
        embed.add_field(
            name="💡 Try:",
            value="• Check if the MCP service is available\\n• Try again in a few moments\\n• Contact an administrator if this persists",
            inline=False
        )
        await interaction.followup.send(embed=embed)


@bot.tree.command(name="clear-channels", description="Clear all channels from selected sport category")
@app_commands.describe(sport="Choose a sport category to clear")
async def clear_channels(interaction: discord.Interaction, sport: app_commands.Choice[str]):
    """Clear all channels from a specific sport category"""
    await interaction.response.defer()
    
    # Validate permissions
    if not interaction.user.guild_permissions.manage_channels:
        embed = discord.Embed(
            title="❌ Insufficient Permissions",
            description="You need `Manage Channels` permission to use this command.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    # Get sport configuration
    sport_config = bot.config.get_sport_config(sport.value)
    if not sport_config:
        embed = discord.Embed(
            title="❌ Sport Not Available",
            description=f"Sport `{sport.value}` is not configured or available.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    try:
        logger.info(f"Clearing {sport.value} channels - requested by {interaction.user.name}")
        await clear_sport_channels_v2(interaction, sport_config)
        
    except Exception as e:
        logger.error(f"Error clearing {sport.value} channels: {e}")
        embed = discord.Embed(
            title="❌ Channel Clear Error",
            description=f"An error occurred while clearing {sport.value.upper()} channels.",
            color=discord.Color.red()
        )
        embed.add_field(name="Error Details", value=str(e)[:500], inline=False)
        await interaction.followup.send(embed=embed)


@bot.tree.command(name="help", description="Show bot help and available commands")
async def help_command(interaction: discord.Interaction):
    """Show help information"""
    embed = discord.Embed(
        title="🏈 Enhanced Sports Bot v2.0",
        description="Modular sports bot with improved architecture and error handling",
        color=discord.Color.blue()
    )
    
    # Available sports
    available_sports = bot.config.get_enabled_sports()
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
    
    embed.set_footer(text="Enhanced Sports Bot v2.0 - Modular Architecture")
    await interaction.response.send_message(embed=embed)


# Dynamic sport choices based on configuration
def get_sport_choices():
    """Get sport choices for commands based on available sports"""
    choices = []
    for sport_name in bot.config.get_enabled_sports():
        display_name = sport_name.upper()
        choices.append(app_commands.Choice(name=display_name, value=sport_name))
    return choices


# Update command choices dynamically
for command in [create_channels, clear_channels]:
    for param in command.parameters:
        if param.name == "sport":
            param.choices = get_sport_choices()


async def create_soccer_channels_v2(interaction: discord.Interaction, date: str, sport_config):
    """Enhanced soccer channel creation using new architecture"""
    # Convert YYYY-MM-DD to DD-MM-YYYY for soccer MCP
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    mcp_date = date_obj.strftime(sport_config.date_format)
    
    # Call soccer MCP using new client
    response = await bot.mcp_client.call_mcp(
        sport_config.mcp_url, 
        "get_betting_matches", 
        {"date": mcp_date}
    )
    
    if not response.success:
        embed = discord.Embed(
            title="❌ Soccer Data Error",
            description="Failed to fetch soccer match data.",
            color=discord.Color.red()
        )
        embed.add_field(name="Error", value=response.error, inline=False)
        await interaction.followup.send(embed=embed)
        return
    
    # Parse MCP response
    data = await bot.mcp_client.parse_mcp_content(response)
    if not data or "matches_by_league" not in data:
        embed = discord.Embed(
            title="📅 No Soccer Matches",
            description=f"No soccer matches found for {date}",
            color=discord.Color.orange()
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Get or create category
    category = None
    if sport_config.category_id:
        category = discord.utils.get(interaction.guild.categories, id=sport_config.category_id)
    if not category:
        category = discord.utils.get(interaction.guild.categories, name=sport_config.category_name)
    if not category:
        category = await interaction.guild.create_category(sport_config.category_name)
    
    # Create channels with enhanced error handling
    created = 0
    total_matches = 0
    errors = []
    
    for league, matches in data["matches_by_league"].items():
        total_matches += len(matches)
        
        for match in matches:
            try:
                teams = match.get("teams", {})
                home_team = teams.get("home", {}).get("name", "Unknown")
                away_team = teams.get("away", {}).get("name", "Unknown")
                
                # Create channel name
                channel_name = f"{away_team.lower().replace(' ', '-')[:10]}-vs-{home_team.lower().replace(' ', '-')[:10]}"
                
                # Check if exists
                if discord.utils.get(category.channels, name=channel_name):
                    continue
                
                # Create channel
                channel = await category.create_text_channel(
                    name=channel_name,
                    topic=f"{away_team} vs {home_team} - {league}"
                )
                
                # Create initial embed
                embed = discord.Embed(
                    title=f"⚽ {away_team} vs {home_team}",
                    description=f"**{league}**\\n🔄 Loading match analysis...",
                    color=sport_config.embed_color,
                    timestamp=datetime.now()
                )
                
                match_time = match.get("time", "TBD")
                embed.add_field(name="⏰ Time", value=match_time, inline=True)
                embed.set_footer(text="Enhanced Soccer Analysis")
                
                await channel.send(embed=embed)
                created += 1
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                error_msg = f"Failed to create channel for {away_team} vs {home_team}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
    
    # Send completion message
    embed = discord.Embed(
        title="✅ Soccer Channels Created",
        description=f"Successfully created **{created}** channels from {total_matches} matches",
        color=discord.Color.green()
    )
    
    if errors:
        error_text = "\\n".join([f"• {error}" for error in errors[:3]])
        if len(errors) > 3:
            error_text += f"\\n... and {len(errors) - 3} more errors"
        embed.add_field(name="⚠️ Errors", value=error_text, inline=False)
    
    await interaction.followup.send(embed=embed)


async def create_mlb_channels_v2(interaction: discord.Interaction, date: str, sport_config):
    """Enhanced MLB channel creation using new architecture"""
    # MLB uses YYYY-MM-DD format directly
    mcp_date = date
    
    # Call MLB MCP using new client
    response = await bot.mcp_client.call_mcp(
        sport_config.mcp_url,
        "get_games",  # Assuming this is the MLB MCP tool name
        {"date": mcp_date}
    )
    
    if not response.success:
        embed = discord.Embed(
            title="❌ MLB Data Error", 
            description="Failed to fetch MLB game data.",
            color=discord.Color.red()
        )
        embed.add_field(name="Error", value=response.error, inline=False)
        await interaction.followup.send(embed=embed)
        return
    
    # Parse MCP response
    data = await bot.mcp_client.parse_mcp_content(response)
    if not data:
        embed = discord.Embed(
            title="📅 No MLB Games",
            description=f"No MLB games found for {date}",
            color=discord.Color.orange()
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Implementation would continue similar to soccer...
    embed = discord.Embed(
        title="🚧 MLB Implementation",
        description="MLB channel creation is being enhanced with the new architecture.",
        color=discord.Color.orange()
    )
    await interaction.followup.send(embed=embed)


async def clear_sport_channels_v2(interaction: discord.Interaction, sport_config):
    """Enhanced channel clearing using new architecture"""
    # Get category
    category = None
    if sport_config.category_id:
        category = discord.utils.get(interaction.guild.categories, id=sport_config.category_id)
    if not category:
        category = discord.utils.get(interaction.guild.categories, name=sport_config.category_name)
    
    if not category:
        embed = discord.Embed(
            title="❌ Category Not Found",
            description=f"{sport_config.category_name} category not found.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Get channels to delete
    channels_to_delete = [ch for ch in category.channels if isinstance(ch, discord.TextChannel)]
    channel_count = len(channels_to_delete)
    
    if channel_count == 0:
        embed = discord.Embed(
            title="ℹ️ No Channels Found",
            description=f"No channels found in {sport_config.category_name} category.",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Show what will be deleted
    embed = discord.Embed(
        title="🗑️ Clearing Channels",
        description=f"Deleting **{channel_count} channels** from {sport_config.category_name}...",
        color=discord.Color.orange()
    )
    await interaction.followup.send(embed=embed)
    
    # Delete channels with enhanced error handling
    deleted_count = 0
    errors = []
    
    for i, channel in enumerate(channels_to_delete):
        try:
            await channel.delete()
            deleted_count += 1
            await asyncio.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            error_msg = f"Failed to delete {channel.name}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
    
    # Send final result
    if deleted_count > 0:
        embed = discord.Embed(
            title="✅ Channels Cleared",
            description=f"Successfully deleted **{deleted_count}** out of {channel_count} channels.",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="❌ Clear Failed",
            description="Could not delete any channels. Check bot permissions.",
            color=discord.Color.red()
        )
    
    if errors:
        error_text = "\\n".join([f"• {error}" for error in errors[:3]])
        if len(errors) > 3:
            error_text += f"\\n... and {len(errors) - 3} more errors"
        embed.add_field(name="⚠️ Errors", value=error_text, inline=False)
    
    await interaction.followup.send(embed=embed)


# Health check endpoint for Railway
async def health_check(request):
    """Health check endpoint"""
    return JSONResponse({"status": "healthy", "bot": str(bot.user) if bot.user else "not ready"})


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


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        # Run web server for health checks
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
    else:
        # Run Discord bot
        asyncio.run(run_bot())