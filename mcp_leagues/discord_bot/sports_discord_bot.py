#!/usr/bin/env python3
"""
Sports Betting Discord Bot - Railway Deployment
Production-ready Discord bot for sports betting analytics platform.
Integrates with all MCP servers for comprehensive sports data.
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
        # Note: Channel management is handled through bot permissions, not intents
        
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
        
        # Channel structure configuration
        self.channel_structure = {
            "📚 BETTING EDUCATION": {
                "channels": ["💰-bankroll-management", "📈-tracking-your-bets", "🎯-understanding-value", "🤖-how-our-ai-works"],
                "type": "education"
            },
            "🏆 LEADERBOARDS": {
                "channels": ["📊-weekly-winners", "💯-accuracy-tracking", "👥-community-picks"],
                "type": "leaderboard"
            },
            "📌 FEATURED TODAY": {
                "channels": ["🔥-hot-picks", "🎰-high-confidence", "💎-value-plays"],
                "type": "featured"
            },
            "⚾ MLB GAMES": {
                "channels": [],  # Dynamic channels created daily
                "type": "sport",
                "sport": "mlb"
            },
            "⚽ SOCCER GAMES": {
                "channels": [],  # Dynamic channels created for match days
                "type": "sport", 
                "sport": "soccer"
            },
            "🏈 CFB GAMES": {
                "channels": [],  # Dynamic channels created for game days
                "type": "sport",
                "sport": "cfb"
            },
            "🎲 LIVE BETTING": {
                "channels": ["⚡-live-odds", "📊-line-movements", "🚨-value-alerts"],
                "type": "live"
            }
        }
        
    async def on_ready(self):
        logger.info(f"{self.user} has connected to Discord!")
        logger.info(f"Bot is in {len(self.guilds)} guilds")
        
        # List all guilds for debugging
        for guild in self.guilds:
            logger.info(f"Guild: {guild.name} (ID: {guild.id})")
        
        # FIXED: Improved command sync with retry logic
        await self.sync_commands_with_retry()
        
        # Setup channel structure for each guild
        for guild in self.guilds:
            await self.setup_guild_channels(guild)
        
        # Start periodic tasks
        if not self.daily_picks_task.is_running():
            self.daily_picks_task.start()
        if not self.channel_management_task.is_running():
            self.channel_management_task.start()
    
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
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ Unknown command. Use `!help` to see available commands.")
        else:
            await ctx.send(f"❌ An error occurred: {str(error)}")
    
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
    
    async def call_openrouter(self, messages: List[Dict], max_tokens: int = 300) -> str:
        """Call OpenRouter API for AI responses"""
        if not OPENROUTER_API_KEY:
            return "AI analysis unavailable - API key not configured"
        
        client = await get_http_client()
        
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        try:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            return result["choices"][0]["message"]["content"]
        
        except Exception as e:
            logger.error(f"OpenRouter call failed: {e}")
            return f"AI analysis error: {str(e)}"
    
    async def setup_guild_channels(self, guild: discord.Guild):
        """Setup the complete channel structure for a guild"""
        try:
            logger.info(f"Setting up channels for guild: {guild.name}")
            
            for category_name, config in self.channel_structure.items():
                # Find or create category
                category = discord.utils.get(guild.categories, name=category_name)
                if not category:
                    category = await guild.create_category(category_name)
                    logger.info(f"Created category: {category_name}")
                
                # Create static channels
                for channel_name in config["channels"]:
                    if not discord.utils.get(category.channels, name=channel_name):
                        await guild.create_text_channel(channel_name, category=category)
                        logger.info(f"Created channel: {channel_name} in {category_name}")
            
            logger.info(f"Channel setup completed for {guild.name}")
            
        except Exception as e:
            logger.error(f"Error setting up channels: {e}")
    
    async def create_game_channels(self, guild: discord.Guild, sport: str, games_data: List[Dict]):
        """Create dynamic channels for today's games"""
        try:
            # Find sport category
            category_name = None
            if sport == "mlb":
                category_name = "⚾ MLB GAMES"
            elif sport == "soccer":
                category_name = "⚽ SOCCER GAMES"
            elif sport == "cfb":
                category_name = "🏈 CFB GAMES"
            
            if not category_name:
                return
            
            category = discord.utils.get(guild.categories, name=category_name)
            if not category:
                category = await guild.create_category(category_name)
            
            # Clean up old game channels (older than today)
            today = datetime.now().strftime("%m-%d")
            for channel in category.channels:
                if isinstance(channel, discord.TextChannel):
                    # Remove channels not from today
                    if not channel.name.startswith(today):
                        await channel.delete()
                        logger.info(f"Deleted old channel: {channel.name}")
            
            # Create channels for today's games
            for i, game in enumerate(games_data[:10]):  # Limit to 10 games
                try:
                    # Extract team names (this will vary by sport/API response)
                    if sport == "mlb":
                        teams = self.extract_mlb_teams(game)
                    elif sport == "soccer":
                        teams = self.extract_soccer_teams(game)
                    elif sport == "cfb":
                        teams = self.extract_cfb_teams(game)
                    else:
                        continue
                    
                    if teams:
                        channel_name = f"{today}-{teams['away']}-vs-{teams['home']}".lower().replace(" ", "-")
                        
                        # Check if channel already exists
                        if not discord.utils.get(category.channels, name=channel_name):
                            channel = await guild.create_text_channel(channel_name, category=category)
                            
                            # Post initial game info
                            embed = discord.Embed(
                                title=f"{teams['away']} @ {teams['home']}",
                                description=f"Game Time: {game.get('time', 'TBD')}",
                                color=discord.Color.blue()
                            )
                            await channel.send(embed=embed)
                            
                            logger.info(f"Created game channel: {channel_name}")
                
                except Exception as e:
                    logger.error(f"Error creating channel for game {i}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error creating game channels: {e}")
    
    def extract_mlb_teams(self, game_data: Dict) -> Optional[Dict[str, str]]:
        """Extract team names from MLB game data"""
        try:
            # Updated for actual MLB MCP response format
            if "home" in game_data and "away" in game_data:
                return {
                    "home": game_data["home"].get("name", "Unknown"),
                    "away": game_data["away"].get("name", "Unknown")
                }
            return None
        except:
            return None
    
    def extract_soccer_teams(self, game_data: Dict) -> Optional[Dict[str, str]]:
        """Extract team names from Soccer game data"""
        try:
            # Adapt this based on your Soccer MCP response format
            if "homeTeam" in game_data and "awayTeam" in game_data:
                return {
                    "home": game_data["homeTeam"].get("name", "Unknown"),
                    "away": game_data["awayTeam"].get("name", "Unknown")
                }
            return None
        except:
            return None
    
    def extract_cfb_teams(self, game_data: Dict) -> Optional[Dict[str, str]]:
        """Extract team names from CFB game data"""
        try:
            # Adapt this based on your CFB MCP response format
            if "teams" in game_data:
                teams = game_data["teams"]
                return {
                    "home": teams[0].get("school", "Unknown") if len(teams) > 0 else "Unknown",
                    "away": teams[1].get("school", "Unknown") if len(teams) > 1 else "Unknown"
                }
            return None
        except:
            return None
    
    @tasks.loop(hours=24)
    async def daily_picks_task(self):
        """Daily task to post picks to featured channels"""
        try:
            # Find the hot-picks channel
            for guild in self.guilds:
                channel = discord.utils.get(guild.channels, name="🔥-hot-picks")
                if channel:
                    await self.post_daily_picks(channel)
                    break
        except Exception as e:
            logger.error(f"Daily picks task error: {e}")
    
    @tasks.loop(hours=6)  # Run every 6 hours
    async def channel_management_task(self):
        """Periodic task to manage game channels"""
        try:
            for guild in self.guilds:
                # Get today's games and create channels
                await self.update_game_channels(guild)
        except Exception as e:
            logger.error(f"Channel management task error: {e}")
    
    async def update_game_channels(self, guild: discord.Guild):
        """Update game channels for all sports"""
        try:
            # MLB games
            try:
                mlb_games = await self.call_mcp_server(
                    self.mcp_urls["mlb"], 
                    "getMLBScheduleET",
                    {"date": datetime.now().strftime("%Y-%m-%d")}
                )
                if mlb_games and "content" in mlb_games:
                    # Parse MLB games from content (adapt based on actual response format)
                    games_list = self.parse_games_from_content(mlb_games["content"], "mlb")
                    await self.create_game_channels(guild, "mlb", games_list)
            except Exception as e:
                logger.error(f"Error updating MLB channels: {e}")
            
            # Soccer games
            try:
                soccer_games = await self.call_mcp_server(
                    self.mcp_urls["soccer"],
                    "getCompetitionMatches",
                    {"competition": "PL", "dateFrom": datetime.now().strftime("%Y-%m-%d")}
                )
                if soccer_games and "content" in soccer_games:
                    games_list = self.parse_games_from_content(soccer_games["content"], "soccer")
                    await self.create_game_channels(guild, "soccer", games_list)
            except Exception as e:
                logger.error(f"Error updating Soccer channels: {e}")
            
            # CFB games (if in season)
            try:
                cfb_games = await self.call_mcp_server(
                    self.mcp_urls["cfb"],
                    "getCFBGames",
                    {"year": datetime.now().year, "week": 1}
                )
                if cfb_games and "content" in cfb_games:
                    games_list = self.parse_games_from_content(cfb_games["content"], "cfb")
                    await self.create_game_channels(guild, "cfb", games_list)
            except Exception as e:
                logger.error(f"Error updating CFB channels: {e}")
                
        except Exception as e:
            logger.error(f"Error in update_game_channels: {e}")
    
    def parse_games_from_content(self, content: str, sport: str) -> List[Dict]:
        """Parse games from MCP response content"""
        try:
            # This is a basic parser - you'll need to adapt based on actual MCP response formats
            if isinstance(content, str):
                # Try to parse as JSON first
                try:
                    games_data = json.loads(content)
                    if isinstance(games_data, list):
                        return games_data
                    elif isinstance(games_data, dict) and "games" in games_data:
                        return games_data["games"]
                except:
                    # If not JSON, create mock game data for channel creation
                    lines = content.split('\n')
                    games = []
                    for line in lines[:5]:  # Limit to 5 games
                        if 'vs' in line or '@' in line:
                            games.append({"description": line.strip(), "time": "TBD"})
                    return games
            return []
        except Exception as e:
            logger.error(f"Error parsing games content: {e}")
            return []

    async def post_daily_picks(self, channel):
        """Post daily hot picks to channel"""
        try:
            # Get today's games from MLB
            mlb_data = await self.call_mcp_server(
                self.mcp_urls["mlb"], 
                "getMLBScheduleET",
                {"date": datetime.now().strftime("%Y-%m-%d")}
            )
            
            # Get odds for games
            odds_data = await self.call_mcp_server(
                self.mcp_urls["odds"],
                "getOdds",
                {"sport": "baseball_mlb", "markets": "h2h,spreads,totals"}
            )
            
            # Generate AI picks
            ai_prompt = f"""
Based on today's MLB games and current odds, provide 3 top betting picks.
Focus on value and explain reasoning briefly.

Games: {json.dumps(mlb_data, indent=2)[:1000]}
Odds: {json.dumps(odds_data, indent=2)[:1000]}

Format as:
🔥 HOT PICKS - {datetime.now().strftime("%B %d, %Y")}

1. **Game**: Team vs Team
   **Pick**: Bet type and odds
   **Reasoning**: Brief explanation

2. **Game**: Team vs Team  
   **Pick**: Bet type and odds
   **Reasoning**: Brief explanation

3. **Game**: Team vs Team
   **Pick**: Bet type and odds  
   **Reasoning**: Brief explanation

Keep each pick under 50 words.
"""
            
            ai_response = await self.call_openrouter([
                {"role": "user", "content": ai_prompt}
            ], max_tokens=500)
            
            await channel.send(ai_response)
            logger.info("Posted daily picks")
            
        except Exception as e:
            logger.error(f"Failed to post daily picks: {e}")
            await channel.send("❌ Unable to generate daily picks at this time.")

# Initialize bot
bot = SportsBot()

# Slash Commands
@bot.tree.command(name="sync", description="Manually sync slash commands")
async def sync_command(interaction: discord.Interaction):
    """Manually sync slash commands with Discord"""
    await interaction.response.defer()
    
    try:
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("❌ You need Administrator permission to use this command.")
            return
        
        logger.info(f"Manual sync requested by {interaction.user}")
        
        # Clear and re-sync commands to avoid conflicts
        bot.tree.clear_commands(guild=None)
        synced = await bot.tree.sync()
        
        embed = discord.Embed(
            title="✅ Command Sync Complete",
            description=f"Successfully synced {len(synced)} slash commands!",
            color=discord.Color.green()
        )
        
        if synced:
            command_list = "\n".join([f"• /{cmd.name}" for cmd in synced])
            embed.add_field(name="Synced Commands", value=command_list, inline=False)
        
        await interaction.followup.send(embed=embed)
        logger.info(f"Manual sync completed: {len(synced)} commands synced by {interaction.user}")
        
    except Exception as e:
        logger.error(f"Manual sync failed: {e}")
        await interaction.followup.send(f"❌ Error syncing commands: {str(e)}")

@bot.tree.command(name="debug-mlb", description="Debug MLB data from MCP")
async def debug_mlb_command(interaction: discord.Interaction, date: str = None):
    """Debug what data we get from MLB MCP"""
    await interaction.response.defer()
    
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        await interaction.followup.send(f"🔍 Testing MLB MCP for date: {date}")
        
        # Get today's MLB games from your MCP
        mlb_response = await bot.call_mcp_server(
            bot.mcp_urls["mlb"],
            "getMLBScheduleET",
            {"date": date}
        )
        
        if mlb_response:
            # Show summary first
            if mlb_response.get("ok"):
                games_data = mlb_response.get("data", {}).get("games", [])
                await interaction.followup.send(f"✅ MCP Response: {len(games_data)} games found")
                
                # Show first few games
                if games_data:
                    for i, game in enumerate(games_data[:3]):
                        away = game.get("away", {}).get("name", "Unknown")
                        home = game.get("home", {}).get("name", "Unknown")
                        time = game.get("start_et", "Unknown")
                        status = game.get("status", "Unknown")
                        await interaction.followup.send(f"🏟️ **Game {i+1}**: {away} @ {home}\\n⏰ {time} - {status}")
            else:
                await interaction.followup.send(f"❌ MCP Error: {mlb_response.get('error', 'Unknown error')}")
            
            # Send raw response for debugging (truncated)
            response_text = json.dumps(mlb_response, indent=2)[:1900]  # Discord limit
            await interaction.followup.send(f"```json\\n{response_text}\\n```")
        else:
            await interaction.followup.send("❌ No response from MLB MCP")
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")

@bot.tree.command(name="setup", description="Setup channel structure for this server")
async def setup_command(interaction: discord.Interaction):
    """Setup the complete channel structure"""
    await interaction.response.defer()
    
    try:
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.followup.send("❌ You need 'Manage Channels' permission to use this command.")
            return
        
        await bot.setup_guild_channels(interaction.guild)
        await interaction.followup.send("✅ Channel structure setup completed!")
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error setting up channels: {str(e)}")

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
        
        # Get today's MLB games from your MCP
        mlb_response = await bot.call_mcp_server(
            bot.mcp_urls["mlb"],
            "getMLBScheduleET",
            {"date": date}
        )
        
        # Debug logging
        logger.info(f"MLB MCP Response for {date}: {mlb_response}")
        
        if not mlb_response or not mlb_response.get("ok"):
            await interaction.followup.send(f"❌ Error getting MLB games: {mlb_response.get('error', 'Unknown error')}")
            return
        
        # Find or create MLB GAMES category
        category = discord.utils.get(interaction.guild.categories, name="⚾ MLB GAMES")
        if not category:
            category = await interaction.guild.create_category("⚾ MLB GAMES")
        
        # Parse games from the MCP response
        games_data = mlb_response.get("data", {}).get("games", [])
        
        # Debug logging
        logger.info(f"Found {len(games_data)} games for {date}")
        if games_data:
            logger.info(f"First game sample: {games_data[0]}")
        
        if not games_data:
            await interaction.followup.send(f"📅 No MLB games scheduled for {date}")
            return
        
        created_channels = []
        skipped_channels = []
        
        # Send initial progress message
        total_games = len(games_data)
        await interaction.followup.send(f"🔄 Processing {total_games} games...")
        
        for i, game in enumerate(games_data):
            try:
                # Extract team info - updated for actual MLB MCP response format
                away_team = game.get("away", {}).get("name", "Unknown")
                home_team = game.get("home", {}).get("name", "Unknown")
                game_time = game.get("start_et", "TBD")
                
                # Clean team names for channel
                away_clean = away_team.lower().replace(" ", "").replace(".", "")[:10]
                home_clean = home_team.lower().replace(" ", "").replace(".", "")[:10]
                
                # Create channel name: 08-16-yankees-vs-red-sox
                date_short = datetime.strptime(date, "%Y-%m-%d").strftime("%m-%d")
                channel_name = f"{date_short}-{away_clean}-vs-{home_clean}"
                
                # Check if channel already exists
                existing_channel = discord.utils.get(category.channels, name=channel_name)
                if existing_channel:
                    skipped_channels.append(f"{away_team} @ {home_team}")
                    continue
                
                # Create the channel
                new_channel = await interaction.guild.create_text_channel(
                    name=channel_name,
                    category=category,
                    topic=f"{away_team} @ {home_team} - {game_time}"
                )
                
                # Post game info to channel
                embed = discord.Embed(
                    title=f"🔥 {away_team} @ {home_team}",
                    description=f"**Game Time:** {game_time}\\n**Date:** {date}",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Away Team", value=away_team, inline=True)
                embed.add_field(name="Home Team", value=home_team, inline=True)
                embed.set_footer(text="Use this channel to discuss betting analysis for this game")
                
                await new_channel.send(embed=embed)
                created_channels.append(channel_name)
                
                # Progress update every 5 channels
                if (i + 1) % 5 == 0:
                    logger.info(f"Created {len(created_channels)} channels, processed {i + 1}/{total_games} games")
                
            except Exception as e:
                logger.error(f"Error creating channel for game {i+1}: {e}")
                continue
        
        # Final summary
        summary_parts = []
        
        if created_channels:
            summary_parts.append(f"✅ **Created {len(created_channels)} new channels:**")
            channels_list = "\\n".join([f"• #{name}" for name in created_channels[:10]])
            if len(created_channels) > 10:
                channels_list += f"\\n• ... and {len(created_channels) - 10} more"
            summary_parts.append(channels_list)
        
        if skipped_channels:
            summary_parts.append(f"ℹ️ **Skipped {len(skipped_channels)} existing channels:**")
            skipped_list = "\\n".join([f"• {game}" for game in skipped_channels[:5]])
            if len(skipped_channels) > 5:
                skipped_list += f"\\n• ... and {len(skipped_channels) - 5} more"
            summary_parts.append(skipped_list)
        
        if not created_channels and not skipped_channels:
            summary_parts.append("ℹ️ No games found to process.")
        
        final_message = "\\n\\n".join(summary_parts)
        await interaction.followup.send(final_message)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error creating MLB channels: {str(e)}")


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
        
        # Confirm deletion
        embed = discord.Embed(
            title="🗑️ Clear Channels Confirmation",
            description=f"Are you sure you want to delete **{channel_count} channels** from '{category}'?",
            color=discord.Color.orange()
        )
        
        # Add list of channels (first 10)
        channel_names = [ch.name for ch in channels_to_delete[:10]]
        if len(channels_to_delete) > 10:
            channel_names.append(f"... and {len(channels_to_delete) - 10} more")
        
        embed.add_field(
            name="Channels to delete:",
            value="\\n".join([f"• #{name}" for name in channel_names]),
            inline=False
        )
        
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
        embed.add_field(name="Registered Commands", value=len(commands), inline=True)
        
        # List commands
        if commands:
            command_list = "\n".join([f"• /{cmd.name}" for cmd in commands[:15]])
            if len(commands) > 15:
                command_list += f"\n• ... and {len(commands) - 15} more"
            embed.add_field(name="Command List", value=command_list, inline=False)
        
        # MCP URLs status
        mcp_status = "\n".join([f"• {name.upper()}: {'✅' if url else '❌'}" for name, url in bot.mcp_urls.items()])
        embed.add_field(name="MCP Servers", value=mcp_status, inline=False)
        
        embed.set_footer(text=f"Bot User: {bot.user} | Latency: {round(bot.latency * 1000)}ms")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error checking bot status: {str(e)}")

@bot.tree.command(name="analyze", description="Analyze and populate game channels with betting insights")
@app_commands.describe(sport="Select the sport to analyze games for")
@app_commands.choices(sport=[
    app_commands.Choice(name="MLB", value="mlb"),
    app_commands.Choice(name="NFL", value="nfl"),
    app_commands.Choice(name="NHL", value="nhl"),
    app_commands.Choice(name="NBA", value="nba"),
    app_commands.Choice(name="CFB", value="cfb"),
    app_commands.Choice(name="Soccer", value="soccer"),
])
async def analyze_command(interaction: discord.Interaction, sport: str):
    """Analyze games and populate channels with AI betting insights"""
    await interaction.response.defer()
    
    try:
        # TODO: This will be implemented later
        # Will go through each channel in the selected sport category
        # and populate with AI analysis, odds, and betting insights
        
        await interaction.followup.send(f"🚧 Analyze feature coming soon for {sport.upper()}!")
        
    except Exception as e:
        logger.error(f"Error in analyze command: {e}")
        await interaction.followup.send(f"❌ Error analyzing {sport}: {str(e)}")

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
            value="`/create-mlb-channels` - Create channels for today's MLB games\n"
                  "`/setup` - Setup channel structure for this server\n"
                  "`/sync` - Manually sync slash commands",
            inline=False
        )
        
        # Management Commands
        embed.add_field(
            name="🗑️ Management Commands", 
            value="`/clear-channels` - Clear all channels from a sport category\n"
                  "└ Dropdown: MLB, NFL, NHL, NBA, CFB, Soccer",
            inline=False
        )
        
        # Analysis Commands
        embed.add_field(
            name="📊 Analysis Commands",
            value="`/analyze` - Analyze and populate game channels (Coming Soon)\n"
                  "└ Dropdown: MLB, NFL, NHL, NBA, CFB, Soccer",
            inline=False
        )
        
        # Debug Commands
        embed.add_field(
            name="🔧 Debug Commands",
            value="`/debug-mlb` - Debug MLB data from MCP server\n"
                  "`/help` - Show this help message",
            inline=False
        )
        
        # Permissions
        embed.add_field(
            name="🔐 Required Permissions",
            value="**Manage Channels** - Required for `/setup`, `/create-mlb-channels`, `/clear-channels`\n"
                  "**Administrator** - Required for `/sync`",
            inline=False
        )
        
        embed.set_footer(text="Sports Betting Bot | All commands use Discord slash command format")
        
        await interaction.followup.send(embed=embed)
        logger.info("Help command completed successfully")
        
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await interaction.followup.send(f"❌ Error showing help: {str(e)}")

# Health check endpoint for Railway
async def health_check(request):
    try:
        # Try to get command count for health check
        command_count = 0
        if bot.is_ready():
            try:
                commands = await bot.tree.fetch_commands()
                command_count = len(commands)
            except:
                command_count = -1  # Indicates sync issue
        
        return JSONResponse({
            "status": "healthy", 
            "bot_ready": bot.is_ready(),
            "guilds": len(bot.guilds) if bot.is_ready() else 0,
            "channels_managed": len(bot.channel_structure),
            "commands_registered": command_count
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "error": str(e)
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
        await bot.start(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Bot failed to start: {e}")
        traceback.print_exc()

async def main():
    """Main function to run both bot and health check server"""
    # Start health check server
    port = int(os.getenv("PORT", 8080))
    
    # Start bot and server concurrently
    import uvicorn
    
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    
    # Run bot and server together
    await asyncio.gather(
        run_bot(),
        server.serve()
    )

if __name__ == "__main__":
    print("🤖 Starting Sports Discord Bot")
    print("=" * 60)
    print("Expected commands after startup:")
    print("  /sync - Manual command sync")
    print("  /help - Show all commands") 
    print("  /clear-channels - Clear sport channels")
    print("  /create-mlb-channels - Create MLB channels")
    print("  /bot-status - Bot diagnostics")
    print("=" * 60)
    
    asyncio.run(main())