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
COMMAND_PREFIX = "!"
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
            command_prefix=COMMAND_PREFIX,
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
        
        # Sync slash commands to Discord
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
        
        # Setup channel structure for each guild
        for guild in self.guilds:
            await self.setup_guild_channels(guild)
        
        # Start periodic tasks
        if not self.daily_picks_task.is_running():
            self.daily_picks_task.start()
        if not self.channel_management_task.is_running():
            self.channel_management_task.start()
    
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
@bot.command(name="sync", description="Manually sync slash commands")
async def sync_command(ctx):
    """Manually sync slash commands with Discord"""
    try:
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need Administrator permission to use this command.")
            return
        
        synced = await bot.tree.sync()
        await ctx.send(f"✅ Synced {len(synced)} slash commands!")
        logger.info(f"Manual sync: {len(synced)} commands synced by {ctx.author}")
        
    except Exception as e:
        await ctx.send(f"❌ Error syncing commands: {str(e)}")

@bot.command(name="debug-mlb", description="Debug MLB data from MCP")
async def debug_mlb_command(ctx, date: str = None):
    """Debug what data we get from MLB MCP"""
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        await ctx.send(f"🔍 Testing MLB MCP for date: {date}")
        
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
                await ctx.send(f"✅ MCP Response: {len(games_data)} games found")
                
                # Show first few games
                if games_data:
                    for i, game in enumerate(games_data[:3]):
                        away = game.get("away", {}).get("name", "Unknown")
                        home = game.get("home", {}).get("name", "Unknown")
                        time = game.get("start_et", "Unknown")
                        status = game.get("status", "Unknown")
                        await ctx.send(f"🏟️ **Game {i+1}**: {away} @ {home}\\n⏰ {time} - {status}")
            else:
                await ctx.send(f"❌ MCP Error: {mlb_response.get('error', 'Unknown error')}")
            
            # Send raw response for debugging (truncated)
            response_text = json.dumps(mlb_response, indent=2)[:1900]  # Discord limit
            await ctx.send(f"```json\\n{response_text}\\n```")
        else:
            await ctx.send("❌ No response from MLB MCP")
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.hybrid_command(name="setup", description="Setup channel structure for this server")
async def setup_command(ctx):
    """Setup the complete channel structure"""
    if hasattr(ctx, 'response'):  # Slash command
        await ctx.defer()
        send_func = ctx.followup.send
    else:  # Prefix command
        send_func = ctx.send
    
    try:
        if not ctx.author.guild_permissions.manage_channels:
            await send_func("❌ You need 'Manage Channels' permission to use this command.")
            return
        
        await bot.setup_guild_channels(ctx.guild)
        await send_func("✅ Channel structure setup completed!")
        
    except Exception as e:
        await send_func(f"❌ Error setting up channels: {str(e)}")

@bot.hybrid_command(name="refresh-channels", description="Refresh game channels for today")
async def refresh_channels_command(ctx, sport: str = "all"):
    """Refresh game channels for specific sport or all sports"""
    if hasattr(ctx, 'response'):  # Slash command
        await ctx.defer()
        send_func = ctx.followup.send
    else:  # Prefix command
        send_func = ctx.send
    
    try:
        if not ctx.author.guild_permissions.manage_channels:
            await send_func("❌ You need 'Manage Channels' permission to use this command.")
            return
        
        if sport.lower() == "all":
            await bot.update_game_channels(ctx.guild)
            await send_func("✅ Refreshed game channels for all sports!")
        else:
            # Refresh specific sport
            if sport.lower() == "mlb":
                mlb_games = await bot.call_mcp_server(
                    bot.mcp_urls["mlb"], 
                    "getMLBScheduleET",
                    {"date": datetime.now().strftime("%Y-%m-%d")}
                )
                if mlb_games:
                    games_list = bot.parse_games_from_content(mlb_games.get("content", ""), "mlb")
                    await bot.create_game_channels(ctx.guild, "mlb", games_list)
            
            await send_func(f"✅ Refreshed {sport.upper()} game channels!")
        
    except Exception as e:
        await send_func(f"❌ Error refreshing channels: {str(e)}")

@bot.hybrid_command(name="games", description="Get today's games across all sports")
async def games_command(ctx, sport: str = "all"):
    """Show today's games"""
    if hasattr(ctx, 'response'):  # Slash command
        await ctx.defer()
        send_func = ctx.followup.send
    else:  # Prefix command
        send_func = ctx.send
    
    try:
        games_data = {}
        
        if sport.lower() in ["all", "mlb"]:
            mlb_games = await bot.call_mcp_server(
                bot.mcp_urls["mlb"], 
                "getMLBScheduleET",
                {"date": datetime.now().strftime("%Y-%m-%d")}
            )
            games_data["MLB"] = mlb_games
        
        if sport.lower() in ["all", "soccer"]:
            soccer_games = await bot.call_mcp_server(
                bot.mcp_urls["soccer"],
                "getCompetitionMatches", 
                {"competition": "PL", "dateFrom": datetime.now().strftime("%Y-%m-%d")}
            )
            games_data["Soccer"] = soccer_games
            
        # Format and send response
        embed = discord.Embed(
            title=f"🏆 Today's Games - {datetime.now().strftime('%B %d, %Y')}",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        for sport_name, data in games_data.items():
            if data and "content" in data:
                games_text = data["content"][:1000] + "..." if len(data["content"]) > 1000 else data["content"]
                embed.add_field(name=f"{sport_name} Games", value=f"```{games_text}```", inline=False)
        
        await send_func(embed=embed)
        
    except Exception as e:
        await send_func(f"❌ Error fetching games: {str(e)}")

@bot.hybrid_command(name="odds", description="Get current betting odds")
async def odds_command(ctx, sport: str = "baseball_mlb"):
    """Show current betting odds"""
    if hasattr(ctx, 'response'):  # Slash command
        await ctx.defer()
        send_func = ctx.followup.send
    else:  # Prefix command
        send_func = ctx.send
    
    try:
        odds_data = await bot.call_mcp_server(
            bot.mcp_urls["odds"],
            "getOdds",
            {"sport": sport, "markets": "h2h,spreads,totals"}
        )
        
        embed = discord.Embed(
            title=f"💰 Current Odds - {sport.upper()}",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        if odds_data and "content" in odds_data:
            odds_text = odds_data["content"][:1500] + "..." if len(odds_data["content"]) > 1500 else odds_data["content"]
            embed.description = f"```{odds_text}```"
        
        await send_func(embed=embed)
        
    except Exception as e:
        await send_func(f"❌ Error fetching odds: {str(e)}")

@bot.hybrid_command(name="analyze", description="Get AI analysis for a game")
async def analyze_command(ctx, *, query: str):
    """Get AI analysis for a specific game or situation"""
    if hasattr(ctx, 'response'):  # Slash command
        await ctx.defer()
        send_func = ctx.followup.send
    else:  # Prefix command
        send_func = ctx.send
    
    try:
        # Get relevant data based on query
        prompt = f"""
You are a sports betting expert. Analyze this request and provide helpful insights.

User query: {query}

Provide a concise analysis with:
1. Key factors to consider
2. Potential betting value
3. Risk assessment
4. Recommendation

Keep response under 300 words.
"""
        
        ai_response = await bot.call_openrouter([
            {"role": "user", "content": prompt}
        ], max_tokens=400)
        
        embed = discord.Embed(
            title="🤖 AI Analysis",
            description=ai_response,
            color=discord.Color.purple(),
            timestamp=datetime.now()
        )
        
        await send_func(embed=embed)
        
    except Exception as e:
        await send_func(f"❌ Error generating analysis: {str(e)}")

@bot.hybrid_command(name="standings", description="Get league standings")
async def standings_command(ctx, league: str = "MLB"):
    """Show league standings"""
    if hasattr(ctx, 'response'):  # Slash command
        await ctx.defer()
        send_func = ctx.followup.send
    else:  # Prefix command
        send_func = ctx.send
    
    try:
        if league.upper() == "MLB":
            standings_data = await bot.call_mcp_server(
                bot.mcp_urls["mlb"],
                "getMLBTeams", 
                {}
            )
        elif league.upper() in ["EPL", "PL"]:
            standings_data = await bot.call_mcp_server(
                bot.mcp_urls["soccer"],
                "getCompetitionStandings",
                {"competition": "PL"}
            )
        else:
            await send_func("❌ League not supported. Try: MLB, EPL")
            return
        
        embed = discord.Embed(
            title=f"📊 {league.upper()} Standings",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        if standings_data and "content" in standings_data:
            standings_text = standings_data["content"][:1500] + "..." if len(standings_data["content"]) > 1500 else standings_data["content"]
            embed.description = f"```{standings_text}```"
        
        await send_func(embed=embed)
        
    except Exception as e:
        await send_func(f"❌ Error fetching standings: {str(e)}")

@bot.hybrid_command(name="create-mlb-channels", description="Create channels for today's MLB games")
async def create_mlb_channels_command(ctx, date: str = None):
    """Create Discord channels for today's MLB games"""
    # Handle both slash and prefix commands
    if hasattr(ctx, 'response'):  # Slash command (interaction)
        await ctx.defer()
        send_func = ctx.followup.send
    else:  # Prefix command (context)
        send_func = ctx.send
    
    try:
        if not ctx.author.guild_permissions.manage_channels:
            await send_func("❌ You need 'Manage Channels' permission to use this command.")
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
            await send_func(f"❌ Error getting MLB games: {mlb_response.get('error', 'Unknown error')}")
            return
        
        # Find or create MLB GAMES category
        category = discord.utils.get(ctx.guild.categories, name="⚾ MLB GAMES")
        if not category:
            category = await ctx.guild.create_category("⚾ MLB GAMES")
        
        # Parse games from the MCP response
        games_data = mlb_response.get("data", {}).get("games", [])
        
        # Debug logging
        logger.info(f"Found {len(games_data)} games for {date}")
        if games_data:
            logger.info(f"First game sample: {games_data[0]}")
        
        if not games_data:
            await send_func(f"📅 No MLB games scheduled for {date}")
            return
        
        created_channels = []
        
        for game in games_data[:10]:  # Limit to 10 games
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
                    continue
                
                # Create the channel
                new_channel = await ctx.guild.create_text_channel(
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
                
            except Exception as e:
                logger.error(f"Error creating channel for game: {e}")
                continue
        
        if created_channels:
            channels_list = "\\n".join([f"• #{name}" for name in created_channels])
            await send_func(f"✅ Created {len(created_channels)} MLB game channels:\\n{channels_list}")
        else:
            await send_func("ℹ️ All game channels already exist or no games found.")
        
    except Exception as e:
        await send_func(f"❌ Error creating MLB channels: {str(e)}")

@bot.hybrid_command(name="cleanup", description="Clean up old game channels")
async def cleanup_command(ctx, days: int = 1):
    """Clean up game channels older than specified days"""
    if hasattr(ctx, 'response'):  # Slash command
        await ctx.defer()
        send_func = ctx.followup.send
    else:  # Prefix command
        send_func = ctx.send
    
    try:
        if not ctx.author.guild_permissions.manage_channels:
            await send_func("❌ You need 'Manage Channels' permission to use this command.")
            return
        
        deleted_count = 0
        sport_categories = ["⚾ MLB GAMES", "⚽ SOCCER GAMES", "🏈 CFB GAMES"]
        
        for category_name in sport_categories:
            category = discord.utils.get(ctx.guild.categories, name=category_name)
            if category:
                for channel in category.channels:
                    if isinstance(channel, discord.TextChannel):
                        # Check if channel is old (basic date check in name)
                        try:
                            # Extract date from channel name (format: mm-dd-team-vs-team)
                            if "-" in channel.name:
                                date_part = channel.name.split("-")[:2]
                                if len(date_part) == 2 and date_part[0].isdigit() and date_part[1].isdigit():
                                    today = datetime.now()
                                    channel_date = f"{today.year}-{date_part[0].zfill(2)}-{date_part[1].zfill(2)}"
                                    channel_datetime = datetime.strptime(channel_date, "%Y-%m-%d")
                                    
                                    if (today - channel_datetime).days >= days:
                                        await channel.delete()
                                        deleted_count += 1
                        except:
                            continue
        
        await send_func(f"✅ Cleaned up {deleted_count} old game channels.")
        
    except Exception as e:
        await send_func(f"❌ Error cleaning up channels: {str(e)}")

# Health check endpoint for Railway
async def health_check(request):
    return JSONResponse({
        "status": "healthy", 
        "bot_ready": bot.is_ready(),
        "guilds": len(bot.guilds) if bot.is_ready() else 0,
        "channels_managed": len(bot.channel_structure)
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
    asyncio.run(main())