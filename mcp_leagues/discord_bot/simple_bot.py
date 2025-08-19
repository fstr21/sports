#!/usr/bin/env python3
"""
Simple Sports Discord Bot - Clean Start
Just the basics: /create-channels with sport dropdown
"""
import asyncio
import logging
import os
from datetime import datetime, timezone, timedelta
import discord
from discord.ext import commands
from discord import app_commands
import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Config
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
SOCCER_MCP_URL = os.getenv("SOCCER_MCP_URL", "https://soccermcp-production.up.railway.app/mcp")
MLB_MCP_URL = os.getenv("MLB_MCP_URL", "https://mlbmcp-production.up.railway.app/mcp")

class SimpleSportsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=None,
            intents=intents,
            description="Simple Sports Bot"
        )
    
    async def call_mcp(self, url: str, tool: str, args: dict = None) -> dict:
        """Call MCP server"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool,
                "arguments": args or {}
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                result = response.json()
                return result.get("result", {})
        except Exception as e:
            logger.error(f"MCP call failed: {e}")
            return {"error": str(e)}
    
    async def on_ready(self):
        logger.info(f"Bot ready: {self.user}")
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} commands")
        except Exception as e:
            logger.error(f"Sync failed: {e}")

bot = SimpleSportsBot()

@bot.tree.command(name="create-channels", description="Create game channels for selected sport")
@app_commands.describe(sport="Choose a sport")
@app_commands.choices(sport=[
    app_commands.Choice(name="Soccer", value="soccer"),
    app_commands.Choice(name="MLB", value="mlb"),
])
async def create_channels(interaction: discord.Interaction, sport: str):
    """Create channels for today's games"""
    await interaction.response.defer()
    
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.followup.send("You need Manage Channels permission")
        return
    
    # Get today's date
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        if sport == "soccer":
            await create_soccer_channels(interaction, today)
        elif sport == "mlb":
            await create_mlb_channels(interaction, today)
        else:
            await interaction.followup.send(f"Sport {sport} not implemented yet")
    except Exception as e:
        logger.error(f"Error creating {sport} channels: {e}")
        await interaction.followup.send(f"Error: {e}")

async def create_soccer_channels(interaction: discord.Interaction, date: str):
    """Create soccer channels with H2H analysis"""
    # Convert YYYY-MM-DD to DD-MM-YYYY for soccer MCP
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    mcp_date = date_obj.strftime("%d-%m-%Y")
    
    # Call soccer MCP for matches
    result = await bot.call_mcp(SOCCER_MCP_URL, "get_betting_matches", {"date": mcp_date})
    
    if "error" in result:
        await interaction.followup.send(f"Soccer MCP error: {result['error']}")
        return
    
    # Handle MCP response format
    if "content" in result and isinstance(result["content"], list):
        import json
        data = json.loads(result["content"][0]["text"])
    else:
        data = result
    
    if "matches_by_league" not in data:
        await interaction.followup.send(f"No soccer matches found for {date}")
        return
    
    # Create soccer category
    category = discord.utils.get(interaction.guild.categories, name="SOCCER GAMES")
    if not category:
        category = await interaction.guild.create_category("SOCCER GAMES")
    
    created = 0
    total_matches = 0
    
    for league, matches in data["matches_by_league"].items():
        total_matches += len(matches)
        
        for match in matches:
            teams = match.get("teams", {})
            home_team = teams.get("home", {}).get("name", "Unknown")
            away_team = teams.get("away", {}).get("name", "Unknown")
            home_id = teams.get("home", {}).get("id")
            away_id = teams.get("away", {}).get("id")
            
            # Simple channel name
            channel_name = f"{away_team.lower().replace(' ', '-')[:10]}-vs-{home_team.lower().replace(' ', '-')[:10]}"
            
            # Check if exists
            if discord.utils.get(category.channels, name=channel_name):
                continue
            
            # Create channel
            channel = await category.create_text_channel(
                name=channel_name,
                topic=f"{away_team} vs {home_team} - {league}"
            )
            
            # Initial embed
            embed = discord.Embed(
                title=f"{away_team} vs {home_team}",
                description=f"League: {league}\n🔄 Fetching H2H analysis...",
                color=0x00ff00
            )
            
            # Add basic match info
            match_time = match.get("time", "TBD")
            embed.add_field(name="Time", value=match_time, inline=True)
            
            message = await channel.send(embed=embed)
            
            # Get H2H analysis if we have team IDs
            if home_id and away_id:
                try:
                    h2h_result = await bot.call_mcp(
                        SOCCER_MCP_URL, 
                        "get_h2h_betting_analysis",
                        {
                            "team_1_id": home_id,
                            "team_2_id": away_id,
                            "team_1_name": home_team,
                            "team_2_name": away_team
                        }
                    )
                    
                    # Parse H2H data
                    h2h_data = None
                    if "content" in h2h_result and isinstance(h2h_result["content"], list):
                        h2h_data = json.loads(h2h_result["content"][0]["text"])
                    
                    # Update embed with H2H data
                    if h2h_data and "error" not in h2h_data:
                        total_meetings = h2h_data.get("total_meetings", 0)
                        if total_meetings > 0:
                            team1_wins = h2h_data.get("team_1_record", {}).get("wins", 0)
                            team2_wins = h2h_data.get("team_2_record", {}).get("wins", 0)
                            draws = h2h_data.get("draws", {}).get("count", 0)
                            
                            embed.description = f"League: {league}"
                            embed.add_field(
                                name="📊 Head-to-Head",
                                value=f"**Total:** {total_meetings} meetings\n**{home_team}:** {team1_wins}W\n**{away_team}:** {team2_wins}W\n**Draws:** {draws}",
                                inline=False
                            )
                            
                            # Add betting insights if available
                            goals = h2h_data.get("goals", {})
                            if goals:
                                avg_goals = goals.get("average_per_game", 0)
                                embed.add_field(
                                    name="⚽ Goals Analysis", 
                                    value=f"**Avg Goals:** {avg_goals:.1f}/game",
                                    inline=True
                                )
                        else:
                            embed.add_field(
                                name="📊 Head-to-Head",
                                value="No previous meetings found",
                                inline=False
                            )
                    else:
                        embed.add_field(
                            name="📊 Head-to-Head",
                            value="Analysis unavailable",
                            inline=False
                        )
                    
                    # Update the message
                    await message.edit(embed=embed)
                    
                except Exception as e:
                    logger.error(f"H2H analysis failed: {e}")
                    # Update with error info
                    embed.add_field(name="📊 Head-to-Head", value="Analysis failed", inline=False)
                    await message.edit(embed=embed)
            
            created += 1
            # Small delay to avoid overwhelming the MCP
            await asyncio.sleep(1)
    
    await interaction.followup.send(f"Created {created} soccer channels from {total_matches} matches with H2H analysis")

async def create_mlb_channels(interaction: discord.Interaction, date: str):
    """Create MLB channels"""
    result = await bot.call_mcp(MLB_MCP_URL, "getMLBScheduleET", {"date": date})
    
    if not result.get("ok"):
        await interaction.followup.send(f"MLB MCP error: {result.get('error', 'Unknown')}")
        return
    
    games = result.get("data", {}).get("games", [])
    if not games:
        await interaction.followup.send(f"No MLB games for {date}")
        return
    
    # Create category
    category = discord.utils.get(interaction.guild.categories, name="MLB GAMES")
    if not category:
        category = await interaction.guild.create_category("MLB GAMES")
    
    created = 0
    
    for game in games:
        away_team = game.get("away", {}).get("name", "Unknown")
        home_team = game.get("home", {}).get("name", "Unknown")
        
        # Simple channel name
        away_short = away_team.split()[-1].lower()  # Team name only
        home_short = home_team.split()[-1].lower()
        channel_name = f"{away_short}-vs-{home_short}"
        
        # Check if exists
        if discord.utils.get(category.channels, name=channel_name):
            continue
        
        # Create channel
        channel = await category.create_text_channel(
            name=channel_name,
            topic=f"{away_team} @ {home_team}"
        )
        
        # Basic embed
        embed = discord.Embed(
            title=f"{away_team} @ {home_team}",
            description=f"Game Time: {game.get('start_et', 'TBD')}",
            color=0x0066cc
        )
        await channel.send(embed=embed)
        created += 1
    
    await interaction.followup.send(f"Created {created} MLB channels from {len(games)} games")

# Health check
async def health_check(request):
    return JSONResponse({"status": "ok", "bot_ready": bot.is_ready()})

app = Starlette(routes=[Route("/health", health_check, methods=["GET"])])

async def run_bot():
    if not DISCORD_TOKEN:
        logger.error("No DISCORD_TOKEN")
        return
    await bot.start(DISCORD_TOKEN)

async def main():
    port = int(os.getenv("PORT", 8080))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    
    await asyncio.gather(run_bot(), server.serve())

if __name__ == "__main__":
    print("Starting Simple Sports Discord Bot")
    print(f"Discord Token: {'SET' if DISCORD_TOKEN else 'MISSING'}")
    asyncio.run(main())