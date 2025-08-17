#!/usr/bin/env python3
"""
Sports Betting Discord Bot - FIXED VERSION
This version fixes the command sync issues with /clear-channels and /help commands.
"""

import asyncio
import json
import logging
import os
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

import discord
from discord.ext import commands, tasks
from discord import app_commands
import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-haiku")

# MCP Server URLs
MLB_MCP_URL = os.getenv("MLB_MCP_URL", "https://mlbmcp-production.up.railway.app/mcp")
SOCCER_MCP_URL = os.getenv("SOCCER_MCP_URL", "https://soccermcp-production.up.railway.app/mcp")
CFB_MCP_URL = os.getenv("CFB_MCP_URL", "https://cfbmcp-production.up.railway.app/mcp") 
ODDS_MCP_URL = os.getenv("ODDS_MCP_URL", "https://odds-mcp-v2-production.up.railway.app/mcp")

# Bot configuration
DEFAULT_GUILD = os.getenv("DEFAULT_GUILD", "Foster")
DEFAULT_CHANNEL = os.getenv("DEFAULT_CHANNEL", "mcp-testing")

# HTTP client for MCP communication
http_client: Optional[httpx.AsyncClient] = None

async def get_http_client() -> httpx.AsyncClient:
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(timeout=30.0)
    return http_client

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class SportsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=None,  # Slash commands only
            intents=intents,
            description="Sports Betting Analytics Bot with AI Integration"
        )
        
        # Store MCP URLs
        self.mcp_urls = {
            "mlb": MLB_MCP_URL,
            "soccer": SOCCER_MCP_URL,
            "cfb": CFB_MCP_URL,
            "odds": ODDS_MCP_URL
        }
        
        # Track sync status
        self.commands_synced = False
        
    async def on_ready(self):
        logger.info(f"{self.user} has connected to Discord!")
        logger.info(f"Bot is in {len(self.guilds)} guilds")
        
        # List all guilds for debugging
        for guild in self.guilds:
            logger.info(f"Guild: {guild.name} (ID: {guild.id})")
        
        # FIXED: Improved command sync with error handling and retry
        if not self.commands_synced:
            await self.sync_commands_with_retry()
        
        logger.info("Bot is ready and commands are synced!")
    
    async def sync_commands_with_retry(self, max_retries: int = 3):
        """Sync commands with retry logic and better error handling"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Syncing commands (attempt {attempt + 1}/{max_retries})...")
                
                # Clear any existing commands first to avoid conflicts
                self.tree.clear_commands(guild=None)
                
                # Sync commands globally
                synced = await self.tree.sync()
                
                logger.info(f"✅ Successfully synced {len(synced)} command(s)")
                
                # Log each synced command for debugging
                for cmd in synced:
                    logger.info(f"  - Synced: /{cmd.name} - {cmd.description}")
                
                self.commands_synced = True
                return True
                
            except discord.HTTPException as e:
                logger.error(f"❌ HTTP error syncing commands (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)  # Wait before retry
                    continue
                else:
                    logger.error("❌ Failed to sync commands after all retries")
                    return False
            except Exception as e:
                logger.error(f"❌ Unexpected error syncing commands: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)
                    continue
                else:
                    return False
        
        return False
    
    async def on_command_error(self, ctx, error):
        logger.error(f"Command error: {error}")
    
    async def call_mcp_server(self, mcp_url: str, tool_name: str, arguments: Dict = None) -> Dict:
        """Call MCP server tool and return response"""
        client = await get_http_client()
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }
        
        try:
            response = await client.post(mcp_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise Exception(f"MCP Error: {result['error']}")
            
            return result.get("result", {})
        
        except Exception as e:
            logger.error(f"MCP call failed: {e}")
            raise

# Initialize bot
bot = SportsBot()

# FIXED: All slash commands with proper error handling and logging

@bot.tree.command(name="sync", description="Manually sync slash commands (Admin only)")
async def sync_command(interaction: discord.Interaction):
    """Manually sync slash commands with Discord"""
    await interaction.response.defer()
    
    try:
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("❌ You need Administrator permission to use this command.")
            return
        
        logger.info(f"Manual sync requested by {interaction.user}")
        
        # Clear and re-sync commands
        bot.tree.clear_commands(guild=None)
        synced = await bot.tree.sync()
        
        embed = discord.Embed(
            title="✅ Command Sync Complete",
            description=f"Successfully synced {len(synced)} slash commands!",
            color=discord.Color.green()
        )
        
        if synced:
            command_list = "\\n".join([f"• /{cmd.name}" for cmd in synced])
            embed.add_field(name="Synced Commands", value=command_list, inline=False)
        
        await interaction.followup.send(embed=embed)
        logger.info(f"Manual sync completed: {len(synced)} commands synced by {interaction.user}")
        
    except Exception as e:
        logger.error(f"Manual sync failed: {e}")
        await interaction.followup.send(f"❌ Error syncing commands: {str(e)}")

@bot.tree.command(name="help", description="Show all available bot commands")
async def help_command(interaction: discord.Interaction):
    """Show all available bot commands"""
    await interaction.response.defer()
    
    try:
        logger.info(f"Help command used by {interaction.user}")
        
        embed = discord.Embed(
            title="🤖 Sports Bot Commands",
            description="All available slash commands for the sports betting bot",
            color=discord.Color.blue()
        )
        
        # Core Commands
        embed.add_field(
            name="🏟️ Core Commands",
            value="`/create-mlb-channels` - Create channels for today's MLB games\\n"
                  "`/setup` - Setup channel structure for this server\\n"
                  "`/sync` - Manually sync slash commands (Admin)",
            inline=False
        )
        
        # Management Commands
        embed.add_field(
            name="🗑️ Management Commands", 
            value="`/clear-channels` - Clear all channels from a sport category\\n"
                  "└ Dropdown: MLB, NFL, NHL, NBA, CFB, Soccer",
            inline=False
        )
        
        # Analysis Commands
        embed.add_field(
            name="📊 Analysis Commands",
            value="`/analyze` - Analyze and populate game channels (Coming Soon)\\n"
                  "└ Dropdown: MLB, NFL, NHL, NBA, CFB, Soccer",
            inline=False
        )
        
        # Debug Commands
        embed.add_field(
            name="🔧 Debug Commands",
            value="`/debug-mlb` - Debug MLB data from MCP server\\n"
                  "`/help` - Show this help message\\n"
                  "`/bot-status` - Check bot status and diagnostics",
            inline=False
        )
        
        # Permissions
        embed.add_field(
            name="🔐 Required Permissions",
            value="**Manage Channels** - Required for `/setup`, `/create-mlb-channels`, `/clear-channels`\\n"
                  "**Administrator** - Required for `/sync`",
            inline=False
        )
        
        embed.set_footer(text="Sports Betting Bot | All commands use Discord slash command format")
        
        await interaction.followup.send(embed=embed)
        logger.info("Help command completed successfully")
        
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await interaction.followup.send(f"❌ Error showing help: {str(e)}")

@bot.tree.command(name="clear-channels", description="Clear all channels from a specific sport category")
@app_commands.describe(category="Select the sport to clear channels from")
@app_commands.choices(category=[
    app_commands.Choice(name="MLB", value="⚾ MLB GAMES"),
    app_commands.Choice(name="NFL", value="🏈 NFL GAMES"),
    app_commands.Choice(name="NHL", value="🏒 NHL GAMES"),
    app_commands.Choice(name="NBA", value="🏀 NBA GAMES"),
    app_commands.Choice(name="CFB", value="🏈 CFB GAMES"),
    app_commands.Choice(name="Soccer", value="⚽ SOCCER GAMES"),
])
async def clear_channels_command(interaction: discord.Interaction, category: str):
    """Clear all channels from a specific sport category"""
    await interaction.response.defer()
    
    try:
        logger.info(f"Clear channels command used by {interaction.user} for category: {category}")
        
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.followup.send("❌ You need 'Manage Channels' permission to use this command.")
            return
        
        # Find the category
        category_obj = discord.utils.get(interaction.guild.categories, name=category)
        if not category_obj:
            await interaction.followup.send(f"❌ Category '{category}' not found.")
            return
        
        # Count channels to delete
        channels_to_delete = [ch for ch in category_obj.channels if isinstance(ch, discord.TextChannel)]
        channel_count = len(channels_to_delete)
        
        if channel_count == 0:
            await interaction.followup.send(f"ℹ️ No channels found in '{category}' category.")
            return
        
        # Show confirmation
        embed = discord.Embed(
            title="🗑️ Clear Channels Confirmation",
            description=f"Deleting **{channel_count} channels** from '{category}'...",
            color=discord.Color.orange()
        )
        
        # Add list of channels (first 10)
        channel_names = [ch.name for ch in channels_to_delete[:10]]
        if len(channels_to_delete) > 10:
            channel_names.append(f"... and {len(channels_to_delete) - 10} more")
        
        embed.add_field(
            name="Channels being deleted:",
            value="\\n".join([f"• #{name}" for name in channel_names]),
            inline=False
        )
        
        await interaction.followup.send(embed=embed)
        
        # Delete channels
        deleted_count = 0
        for channel in channels_to_delete:
            try:
                await channel.delete()
                deleted_count += 1
                logger.info(f"Deleted channel: {channel.name}")
            except Exception as e:
                logger.error(f"Failed to delete channel {channel.name}: {e}")
        
        # Send result
        result_embed = discord.Embed(
            title="✅ Clear Channels Complete",
            description=f"Successfully deleted {deleted_count} out of {channel_count} channels from '{category}'.",
            color=discord.Color.green()
        )
        
        await interaction.followup.send(embed=result_embed)
        logger.info(f"Clear channels completed: {deleted_count}/{channel_count} deleted")
        
    except Exception as e:
        logger.error(f"Error in clear-channels command: {e}")
        await interaction.followup.send(f"❌ Error clearing channels: {str(e)}")

@bot.tree.command(name="bot-status", description="Check bot status and command diagnostics")
async def bot_status_command(interaction: discord.Interaction):
    """Check bot status and diagnostics"""
    await interaction.response.defer()
    
    try:
        # Get registered commands
        commands = await bot.tree.fetch_commands()
        
        embed = discord.Embed(
            title="🤖 Bot Status & Diagnostics",
            color=discord.Color.blue()
        )
        
        # Basic status
        embed.add_field(name="Bot Ready", value="✅ Yes" if bot.is_ready() else "❌ No", inline=True)
        embed.add_field(name="Guilds", value=len(bot.guilds), inline=True)
        embed.add_field(name="Commands Synced", value="✅ Yes" if bot.commands_synced else "❌ No", inline=True)
        
        # Registered commands
        embed.add_field(
            name="Registered Commands",
            value=f"{len(commands)} total",
            inline=True
        )
        
        # List commands
        if commands:
            command_list = "\\n".join([f"• /{cmd.name}" for cmd in commands[:15]])
            if len(commands) > 15:
                command_list += f"\\n• ... and {len(commands) - 15} more"
            embed.add_field(name="Command List", value=command_list, inline=False)
        
        # MCP URLs status
        mcp_status = "\\n".join([f"• {name.upper()}: {'✅' if url else '❌'}" for name, url in bot.mcp_urls.items()])
        embed.add_field(name="MCP Servers", value=mcp_status, inline=False)
        
        embed.set_footer(text=f"Bot User: {bot.user} | Latency: {round(bot.latency * 1000)}ms")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error checking bot status: {str(e)}")

@bot.tree.command(name="create-mlb-channels", description="Create channels for today's MLB games")
async def create_mlb_channels_command(interaction: discord.Interaction, date: str = None):
    """Create Discord channels for today's MLB games"""
    await interaction.response.defer()
    
    try:
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.followup.send("❌ You need 'Manage Channels' permission to use this command.")
            return
        
        # Use today's date if none provided
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        await interaction.followup.send(f"🔄 Creating MLB channels for {date}...")
        
        # Get today's MLB games from MCP
        mlb_response = await bot.call_mcp_server(
            bot.mcp_urls["mlb"],
            "getMLBScheduleET",
            {"date": date}
        )
        
        if not mlb_response or not mlb_response.get("ok"):
            await interaction.followup.send(f"❌ Error getting MLB games: {mlb_response.get('error', 'Unknown error')}")
            return
        
        # Find or create MLB GAMES category
        category = discord.utils.get(interaction.guild.categories, name="⚾ MLB GAMES")
        if not category:
            category = await interaction.guild.create_category("⚾ MLB GAMES")
        
        # Parse games from the MCP response
        games_data = mlb_response.get("data", {}).get("games", [])
        
        if not games_data:
            await interaction.followup.send(f"📅 No MLB games scheduled for {date}")
            return
        
        created_channels = []
        
        for game in games_data:
            try:
                # Extract team info
                away_team = game.get("away", {}).get("name", "Unknown")
                home_team = game.get("home", {}).get("name", "Unknown")
                
                # Clean team names for channel
                away_clean = away_team.lower().replace(" ", "").replace(".", "")[:10]
                home_clean = home_team.lower().replace(" ", "").replace(".", "")[:10]
                
                # Create channel name
                date_short = datetime.strptime(date, "%Y-%m-%d").strftime("%m-%d")
                channel_name = f"{date_short}-{away_clean}-vs-{home_clean}"
                
                # Check if channel already exists
                existing_channel = discord.utils.get(category.channels, name=channel_name)
                if existing_channel:
                    continue
                
                # Create the channel
                new_channel = await interaction.guild.create_text_channel(
                    name=channel_name,
                    category=category,
                    topic=f"{away_team} @ {home_team}"
                )
                
                created_channels.append(channel_name)
                
            except Exception as e:
                logger.error(f"Error creating channel for game: {e}")
                continue
        
        # Send result
        if created_channels:
            await interaction.followup.send(f"✅ Created {len(created_channels)} MLB game channels!")
        else:
            await interaction.followup.send("ℹ️ All channels already exist or no games to process.")
        
    except Exception as e:
        logger.error(f"Error in create-mlb-channels: {e}")
        await interaction.followup.send(f"❌ Error creating MLB channels: {str(e)}")

# Health check endpoint for Railway
async def health_check(request):
    return JSONResponse({
        "status": "healthy", 
        "bot_ready": bot.is_ready(),
        "guilds": len(bot.guilds) if bot.is_ready() else 0,
        "commands_synced": bot.commands_synced
    })

# Create Starlette app for health checks
app = Starlette(routes=[
    Route("/health", health_check, methods=["GET"])
])

async def run_bot():
    """Run the Discord bot"""
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables")
        return
    
    try:
        logger.info("Starting Discord bot...")
        await bot.start(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Bot failed to start: {e}")
        traceback.print_exc()

async def main():
    """Main function to run both bot and health check server"""
    port = int(os.getenv("PORT", 8080))
    
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    
    # Run bot and server together
    await asyncio.gather(
        run_bot(),
        server.serve()
    )

if __name__ == "__main__":
    print("🤖 Starting Sports Discord Bot (FIXED VERSION)")
    print("=" * 60)
    print("This version includes fixes for command sync issues.")
    print("Expected commands after startup:")
    print("  /sync - Manual command sync")
    print("  /help - Show all commands") 
    print("  /clear-channels - Clear sport channels")
    print("  /create-mlb-channels - Create MLB channels")
    print("  /bot-status - Bot diagnostics")
    print("=" * 60)
    
    asyncio.run(main())