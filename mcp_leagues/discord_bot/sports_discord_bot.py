#!/usr/bin/env python3
"""
Simple Sports Discord Bot - Clear Channels Only
Starting fresh with minimal commands to test functionality
"""

import asyncio
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

import discord
from discord.ext import commands
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

# MCP Server URLs
MLB_MCP_URL = os.getenv("MLB_MCP_URL", "https://mlbmcp-production.up.railway.app/mcp")
SOCCER_MCP_URL = os.getenv("SOCCER_MCP_URL", "https://soccermcp-production.up.railway.app/mcp")
CFB_MCP_URL = os.getenv("CFB_MCP_URL", "https://cfbmcp-production.up.railway.app/mcp")
ODDS_MCP_URL = os.getenv("ODDS_MCP_URL", "https://odds-mcp-v2-production.up.railway.app/mcp")

class SportsBot(commands.Bot):
    """Simple bot for channel management"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=None,  # Slash commands only
            intents=intents,
            description="Sports Channel Management Bot"
        )
        
        # MCP URLs
        self.mcp_urls = {
            "mlb": MLB_MCP_URL,
            "soccer": SOCCER_MCP_URL,
            "cfb": CFB_MCP_URL,
            "odds": ODDS_MCP_URL
        }
    
    async def call_mcp_server(self, mcp_url: str, tool_name: str, arguments: Dict = None) -> Dict:
        """Call an MCP server tool"""
        if arguments is None:
            arguments = {}
            
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(mcp_url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                if "error" in result:
                    logger.error(f"MCP Error: {result['error']}")
                    return {}
                
                return result.get("result", {})
                
        except Exception as e:
            logger.error(f"MCP call failed: {e}")
            return {}
    
    async def on_ready(self):
        logger.info(f"{self.user} has connected to Discord!")
        logger.info(f"Bot is in {len(self.guilds)} guilds")
        
        # List all guilds for debugging
        for guild in self.guilds:
            logger.info(f"Guild: {guild.name} (ID: {guild.id})")
        
        # Sync commands with multiple attempts
        await self.sync_commands_properly()
    
    async def sync_commands_properly(self):
        """Properly sync commands with Discord"""
        max_attempts = 3
        
        # First, let's debug what commands are actually defined
        logger.info("🔍 DEBUGGING: Checking command tree before sync")
        local_commands = list(self.tree.get_commands())
        logger.info(f"📊 Local commands in tree: {len(local_commands)}")
        
        for cmd in local_commands:
            logger.info(f"  🎯 Found local command: /{cmd.name} - {cmd.description}")
            logger.info(f"      Callback: {cmd.callback.__name__ if cmd.callback else 'None'}")
        
        if len(local_commands) == 0:
            logger.error("❌ CRITICAL: No commands found in command tree!")
            logger.error("   This means the @bot.tree.command decorators are not working")
            return False
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"🔄 Syncing commands (attempt {attempt + 1}/{max_attempts})")
                
                # DON'T clear commands - this might be removing our commands
                # self.tree.clear_commands(guild=None)
                
                # Add a small delay
                await asyncio.sleep(1)
                
                # Sync globally 
                synced = await self.tree.sync()
                
                logger.info(f"✅ Successfully synced {len(synced)} command(s)")
                for cmd in synced:
                    logger.info(f"  - /{cmd.name}: {cmd.description}")
                
                # Try to fetch commands to verify
                await asyncio.sleep(2)
                try:
                    fetched = await self.tree.fetch_commands()
                    logger.info(f"🔍 Verified: Discord shows {len(fetched)} registered commands")
                    
                    if len(fetched) > 0:
                        return True  # Success
                    else:
                        logger.warning("⚠️ No commands found after sync")
                        
                except Exception as fetch_error:
                    logger.error(f"❌ Could not fetch commands: {fetch_error}")
                
                # If we got here, something might be wrong
                if attempt < max_attempts - 1:
                    logger.info(f"🔄 Retrying command sync in 5 seconds...")
                    await asyncio.sleep(5)
                else:
                    logger.error(f"❌ Failed to properly sync commands after {max_attempts} attempts")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Sync attempt {attempt + 1} failed: {e}")
                logger.error(f"   Exception type: {type(e).__name__}")
                logger.error(f"   Exception details: {str(e)}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(5)
                else:
                    logger.error(f"❌ All sync attempts failed")
                    return False
        
        return False

# Initialize bot
bot = SportsBot()

# Commands defined AFTER bot initialization
@bot.tree.command(name="clear", description="Clear all channels from a sport category")
@app_commands.describe(category="Select the sport category to clear")
@app_commands.choices(category=[
    app_commands.Choice(name="MLB", value="⚾ MLB GAMES"),
    app_commands.Choice(name="NFL", value="🏈 NFL GAMES"),
    app_commands.Choice(name="NBA", value="🏀 NBA GAMES"),
    app_commands.Choice(name="NHL", value="🏒 NHL GAMES"),
    app_commands.Choice(name="SOCCER", value="⚽ SOCCER GAMES"),
    app_commands.Choice(name="CFB", value="🏈 CFB GAMES"),
])
async def clear_command(interaction: discord.Interaction, category: str):
    """Clear all channels from a specific sport category"""
    await interaction.response.defer()
    
    try:
        logger.info(f"Clear command used by {interaction.user.name} for category: {category}")
        
        # Check permissions
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.followup.send("❌ You need 'Manage Channels' permission to use this command.")
            return
        
        # Find the category
        category_obj = discord.utils.get(interaction.guild.categories, name=category)
        if not category_obj:
            await interaction.followup.send(f"❌ Category '{category}' not found.")
            return
        
        # Get all text channels in the category
        channels_to_delete = [ch for ch in category_obj.channels if isinstance(ch, discord.TextChannel)]
        channel_count = len(channels_to_delete)
        
        if channel_count == 0:
            await interaction.followup.send(f"ℹ️ No channels found in '{category}' category.")
            return
        
        # Show what will be deleted
        embed = discord.Embed(
            title="🗑️ Clear Channels",
            description=f"Found **{channel_count} channels** in '{category}' category.",
            color=discord.Color.orange()
        )
        
        # List first 10 channels
        if channels_to_delete:
            channel_names = [ch.name for ch in channels_to_delete[:10]]
            if len(channels_to_delete) > 10:
                channel_names.append(f"... and {len(channels_to_delete) - 10} more")
            
            embed.add_field(
                name="Channels to delete:",
                value="\\n".join([f"• #{name}" for name in channel_names]),
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
        
        # Delete channels
        deleted_count = 0
        failed_deletions = []
        
        logger.info(f"🗑️ Attempting to delete {len(channels_to_delete)} channels...")
        
        for i, channel in enumerate(channels_to_delete):
            try:
                logger.info(f"🔄 Deleting channel {i+1}/{len(channels_to_delete)}: {channel.name}")
                await channel.delete()
                deleted_count += 1
                logger.info(f"✅ Successfully deleted: {channel.name}")
            except discord.Forbidden as e:
                error_msg = f"Permission denied: {channel.name}"
                logger.error(f"❌ {error_msg}: {e}")
                failed_deletions.append(error_msg)
            except discord.NotFound as e:
                error_msg = f"Channel not found: {channel.name}"
                logger.error(f"❌ {error_msg}: {e}")
                failed_deletions.append(error_msg)
            except Exception as e:
                error_msg = f"Unknown error with {channel.name}: {str(e)}"
                logger.error(f"❌ {error_msg}")
                failed_deletions.append(error_msg)
        
        logger.info(f"🏁 Deletion complete: {deleted_count}/{len(channels_to_delete)} successful")
        
        # Send final result with detailed info
        if deleted_count > 0:
            result_embed = discord.Embed(
                title="✅ Clear Complete",
                description=f"Successfully deleted **{deleted_count}** out of {channel_count} channels from '{category}'.",
                color=discord.Color.green()
            )
        else:
            result_embed = discord.Embed(
                title="⚠️ Clear Failed",
                description=f"Could not delete any channels from '{category}'. Check bot permissions.",
                color=discord.Color.red()
            )
        
        # Add failure details if any
        if failed_deletions:
            failure_text = "\n".join(failed_deletions[:5])  # Show first 5 failures
            if len(failed_deletions) > 5:
                failure_text += f"\n... and {len(failed_deletions) - 5} more failures"
            result_embed.add_field(
                name="❌ Failed Deletions",
                value=failure_text,
                inline=False
            )
        
        await interaction.followup.send(embed=result_embed)
        logger.info(f"Clear completed: {deleted_count}/{channel_count} channels deleted")
        
    except Exception as e:
        logger.error(f"Error in clear command: {e}")
        await interaction.followup.send(f"❌ Error clearing channels: {str(e)}")

@bot.tree.command(name="sync", description="Force sync slash commands with Discord")
async def sync_command(interaction: discord.Interaction):
    """Force sync commands - for troubleshooting"""
    await interaction.response.defer()
    
    try:
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("❌ You need Administrator permission to use this command.")
            return
        
        logger.info(f"Manual sync requested by {interaction.user.name}")
        
        # Force sync
        await interaction.followup.send("🔄 Force syncing commands...")
        
        # Clear and re-sync
        bot.tree.clear_commands(guild=None)
        await asyncio.sleep(2)
        
        synced = await bot.tree.sync()
        
        embed = discord.Embed(
            title="🔄 Manual Sync Results",
            description=f"Synced {len(synced)} commands with Discord",
            color=discord.Color.blue()
        )
        
        if synced:
            command_list = "\\n".join([f"• /{cmd.name} - {cmd.description}" for cmd in synced])
            embed.add_field(name="Commands Synced", value=command_list, inline=False)
        
        # Try to verify
        await asyncio.sleep(1)
        try:
            fetched = await bot.tree.fetch_commands()
            embed.add_field(
                name="✅ Verification", 
                value=f"Discord API shows {len(fetched)} registered commands",
                inline=False
            )
        except Exception as e:
            embed.add_field(
                name="⚠️ Verification", 
                value=f"Could not verify: {str(e)[:100]}",
                inline=False
            )
        
        embed.add_field(
            name="ℹ️ Note",
            value="Commands may take 1-2 minutes to appear in Discord. Try refreshing the app.",
            inline=False
        )
        
        await interaction.followup.send(embed=embed)
        logger.info(f"Manual sync completed by {interaction.user.name}")
        
    except Exception as e:
        logger.error(f"Manual sync failed: {e}")
        await interaction.followup.send(f"❌ Sync failed: {str(e)}")

@bot.tree.command(name="create-channels", description="Create game channels for a specific date")
@app_commands.describe(
    sport="Select the sport to create channels for",
    date="Date in YYYY-MM-DD format (optional, defaults to today)"
)
@app_commands.choices(sport=[
    app_commands.Choice(name="Soccer", value="soccer"),
    app_commands.Choice(name="MLB", value="mlb"),
    app_commands.Choice(name="NFL", value="nfl"),
    app_commands.Choice(name="NBA", value="nba"),
    app_commands.Choice(name="NHL", value="nhl"),
    app_commands.Choice(name="CFB", value="cfb"),
])
async def create_channels_command(interaction: discord.Interaction, sport: str, date: str = None):
    """Create Discord channels for today's games"""
    await interaction.response.defer()
    
    try:
        logger.info(f"Create channels command used by {interaction.user.name} for sport: {sport}")
        
        # Check permissions
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.followup.send("❌ You need 'Manage Channels' permission to use this command.")
            return
        
        # Use provided date or default to today
        if date is None:
            from datetime import datetime, timezone, timedelta
            et_tz = timezone(timedelta(hours=-5))  # EST/EDT approximation
            target_date = datetime.now(et_tz).strftime("%Y-%m-%d")
        else:
            # Validate date format
            try:
                datetime.strptime(date, "%Y-%m-%d")
                target_date = date
            except ValueError:
                await interaction.followup.send("❌ Invalid date format. Please use YYYY-MM-DD (e.g., 2025-08-19)")
                return
        
        await interaction.followup.send(f"🔄 Creating {sport.upper()} channels for {target_date}...")
        
        # Route to appropriate sport handler
        if sport == "mlb":
            await create_mlb_channels(interaction, target_date)
        elif sport == "nfl":
            await create_nfl_channels(interaction, target_date)
        elif sport == "nba":
            await create_nba_channels(interaction, target_date)
        elif sport == "nhl":
            await create_nhl_channels(interaction, target_date)
        elif sport == "soccer":
            await create_soccer_channels(interaction, target_date)
        elif sport == "cfb":
            await create_cfb_channels(interaction, target_date)
        else:
            await interaction.followup.send(f"❌ Sport '{sport}' not yet implemented.")
        
    except Exception as e:
        logger.error(f"Error in create-channels command: {e}")
        await interaction.followup.send(f"❌ Error creating channels: {str(e)}")

def extract_team_name(full_team_name: str) -> str:
    """Extract just the team name from 'City Team' format"""
    # MLB team name mappings - extract last word(s) as team name
    team_mapping = {
        # Handle multi-word team names
        "Los Angeles Angels": "Angels",
        "Los Angeles Dodgers": "Dodgers", 
        "New York Yankees": "Yankees",
        "New York Mets": "Mets",
        "San Francisco Giants": "Giants",
        "San Diego Padres": "Padres",
        "St. Louis Cardinals": "Cardinals",
        "Tampa Bay Rays": "Rays",
        "Boston Red Sox": "RedSox",
        "Chicago White Sox": "WhiteSox",
        "Chicago Cubs": "Cubs",
        "Kansas City Royals": "Royals",
        # Single word teams - extract last word
    }
    
    # Check if we have a specific mapping
    if full_team_name in team_mapping:
        return team_mapping[full_team_name]
    
    # Default: take the last word (team name)
    words = full_team_name.split()
    if len(words) > 1:
        return words[-1]  # Last word is usually the team name
    else:
        return full_team_name  # Fallback

async def create_mlb_channels(interaction: discord.Interaction, date: str):
    """Create MLB game channels using the proven working method"""
    try:
        # Get today's MLB games from MCP (using our documented working method)
        mlb_response = await bot.call_mcp_server(
            bot.mcp_urls["mlb"],
            "getMLBScheduleET",
            {"date": date}
        )
        
        logger.info(f"MLB MCP Response for {date}: {mlb_response}")
        
        if not mlb_response or not mlb_response.get("ok"):
            await interaction.followup.send(f"❌ Error getting MLB games: {mlb_response.get('error', 'Unknown error')}")
            return
        
        # Find or create MLB GAMES category
        category = discord.utils.get(interaction.guild.categories, name="⚾ MLB GAMES")
        if not category:
            category = await interaction.guild.create_category("⚾ MLB GAMES")
            logger.info(f"Created new category: ⚾ MLB GAMES")
        
        # Parse games from the MCP response (using documented structure)
        games_data = mlb_response.get("data", {}).get("games", [])
        
        logger.info(f"Found {len(games_data)} MLB games for {date}")
        if games_data:
            logger.info(f"First game sample: {games_data[0]}")
        
        if not games_data:
            await interaction.followup.send(f"📅 No MLB games scheduled for {date}")
            return
        
        created_channels = []
        skipped_channels = []
        
        # Process all games
        for i, game in enumerate(games_data):
            try:
                # Extract team info using documented working method
                away_team = game.get("away", {}).get("name", "Unknown")
                home_team = game.get("home", {}).get("name", "Unknown")
                game_time = game.get("start_et", "TBD")
                
                # Extract just team names (remove cities)
                away_team_name = extract_team_name(away_team)
                home_team_name = extract_team_name(home_team)
                
                # Create channel name without date
                channel_name = f"{away_team_name.lower()}-vs-{home_team_name.lower()}"
                
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
                    description=f"**Game Time:** {game_time}",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Away Team", value=away_team, inline=True)
                embed.add_field(name="Home Team", value=home_team, inline=True)
                embed.set_footer(text="Use this channel to discuss betting analysis for this game")
                
                await new_channel.send(embed=embed)
                created_channels.append(channel_name)
                
                logger.info(f"Created MLB channel: {channel_name}")
                
            except Exception as e:
                logger.error(f"Error creating MLB channel for game {i+1}: {e}")
                continue
        
        # Send final summary
        summary_parts = []
        
        if created_channels:
            summary_parts.append(f"✅ **Created {len(created_channels)} new MLB channels:**")
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
        logger.error(f"Error in create_mlb_channels: {e}")
        await interaction.followup.send(f"❌ Error creating MLB channels: {str(e)}")

async def create_nfl_channels(interaction: discord.Interaction, date: str):
    """Create NFL game channels - placeholder for now"""
    await interaction.followup.send("🚧 NFL channel creation coming soon!")

async def create_nba_channels(interaction: discord.Interaction, date: str):
    """Create NBA game channels - placeholder for now"""
    await interaction.followup.send("🚧 NBA channel creation coming soon!")

async def create_nhl_channels(interaction: discord.Interaction, date: str):
    """Create NHL game channels - placeholder for now"""
    await interaction.followup.send("🚧 NHL channel creation coming soon!")

async def create_soccer_channels(interaction: discord.Interaction, date: str):
    """Create Soccer game channels using Soccer MCP server"""
    try:
        logger.info(f"Creating soccer channels for date: {date}")
        
        # Convert date to DD-MM-YYYY format for Soccer MCP server
        from datetime import datetime
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
            mcp_date = parsed_date.strftime("%d-%m-%Y")
        except ValueError:
            await interaction.followup.send("❌ Invalid date format")
            return
        
        # Call Soccer MCP server
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_betting_matches",
                "arguments": {"date": mcp_date}
            }
        }
        
        logger.info(f"Calling Soccer MCP with date: {mcp_date}")
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(SOCCER_MCP_URL, json=payload)
            
            if response.status_code != 200:
                logger.error(f"Soccer MCP error: {response.status_code}")
                await interaction.followup.send("❌ Failed to connect to Soccer MCP server")
                return
            
            data = response.json()
            
            if "error" in data:
                logger.error(f"Soccer MCP error: {data['error']}")
                await interaction.followup.send("❌ Soccer MCP server error")
                return
            
            result = data.get("result", {})
            
            # Handle MCP server's content array format
            if isinstance(result, dict) and "content" in result:
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    first_content = content[0]
                    if isinstance(first_content, dict) and "text" in first_content:
                        import json
                        result = json.loads(first_content["text"])
            
            # Process matches
            if not result or "matches_by_league" not in result:
                await interaction.followup.send(f"📅 No soccer matches found for {date}")
                return
            
            matches_by_league = result["matches_by_league"]
            total_matches = 0
            created_channels = []
            
            # Get or create soccer category
            guild = interaction.guild
            soccer_category = discord.utils.get(guild.categories, name="⚽ SOCCER")
            if not soccer_category:
                soccer_category = await guild.create_category("⚽ SOCCER")
            
            # Process matches by league
            league_summary = {}
            for league_name, matches in matches_by_league.items():
                if not isinstance(matches, list) or len(matches) == 0:
                    continue
                
                league_summary[league_name] = len(matches)
                total_matches += len(matches)
                
                for match in matches:
                    try:
                        # Extract match info
                        match_id = match.get("id", 0)
                        teams = match.get("teams", {})
                        home_team = teams.get("home", {}).get("name", "Unknown")
                        away_team = teams.get("away", {}).get("name", "Unknown")
                        match_time = match.get("time", "TBD")
                        
                        # Create channel name
                        date_short = parsed_date.strftime("%m-%d")
                        home_clean = home_team.lower().replace(' ', '-').replace('.', '').replace('&', 'and')[:15]
                        away_clean = away_team.lower().replace(' ', '-').replace('.', '').replace('&', 'and')[:15]
                        channel_name = f"📊 {date_short}-{away_clean}-vs-{home_clean}"
                        
                        # Check if channel already exists
                        existing_channel = discord.utils.get(soccer_category.channels, name=channel_name)
                        if existing_channel:
                            continue
                        
                        # Create channel
                        channel = await soccer_category.create_text_channel(
                            name=channel_name,
                            topic=f"{away_team} vs {home_team} - {league_name} - {date}"
                        )
                        created_channels.append(channel)
                        
                        # Create match embed
                        embed = discord.Embed(
                            title=f"⚽ {away_team} vs {home_team}",
                            description=f"**{league_name}**",
                            color=0x00ff00,
                            timestamp=datetime.now()
                        )
                        
                        embed.add_field(name="📅 Date", value=date, inline=True)
                        embed.add_field(name="⏰ Time", value=match_time, inline=True)
                        embed.add_field(name="🏆 League", value=league_name, inline=True)
                        
                        # Add odds if available
                        if "odds" in match and match["odds"]:
                            odds = match["odds"]
                            odds_text = []
                            if "home_win" in odds:
                                odds_text.append(f"🏠 {home_team}: {odds['home_win']}")
                            if "draw" in odds:
                                odds_text.append(f"🤝 Draw: {odds['draw']}")
                            if "away_win" in odds:
                                odds_text.append(f"✈️ {away_team}: {odds['away_win']}")
                            
                            if odds_text:
                                embed.add_field(name="💰 Odds", value="\n".join(odds_text), inline=False)
                        
                        embed.set_footer(text=f"Match ID: {match_id}")
                        
                        # Send embed to channel
                        await channel.send(embed=embed)
                        
                    except Exception as e:
                        logger.error(f"Error creating channel for match {match.get('id', 'unknown')}: {e}")
                        continue
            
            # Send success response
            if created_channels:
                embed = discord.Embed(
                    title="✅ Soccer Channels Created",
                    description=f"Successfully created {len(created_channels)} soccer match channels for {date}",
                    color=0x00ff00
                )
                
                # Add channel list (limit to first 10)
                if len(created_channels) <= 10:
                    channel_list = [f"{i+1}. {channel.mention}" for i, channel in enumerate(created_channels)]
                    embed.add_field(name="📊 Created Channels", value="\n".join(channel_list), inline=False)
                else:
                    channel_list = [f"{i+1}. {channel.mention}" for i, channel in enumerate(created_channels[:10])]
                    embed.add_field(name="📊 Created Channels", value="\n".join(channel_list), inline=False)
                    embed.add_field(name="ℹ️ Note", value=f"Showing first 10 of {len(created_channels)} channels", inline=False)
                
                # Add league summary
                if league_summary:
                    summary_text = [f"⚽ {league}: {count} matches" for league, count in league_summary.items()]
                    embed.add_field(name="🏆 Leagues", value="\n".join(summary_text), inline=True)
                
                embed.set_footer(text=f"Date: {date} | Soccer Bot")
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"📅 No new soccer channels created for {date} (may already exist)")
                
    except Exception as e:
        logger.error(f"Error in create_soccer_channels: {e}")
        await interaction.followup.send(f"❌ Error creating soccer channels: {str(e)}")

async def create_cfb_channels(interaction: discord.Interaction, date: str):
    """Create CFB game channels - placeholder for now"""
    await interaction.followup.send("🚧 CFB channel creation coming soon!")

# Health check endpoint for Railway
async def health_check(request):
    try:
        return JSONResponse({
            "status": "healthy", 
            "bot_ready": bot.is_ready(),
            "guilds": len(bot.guilds) if bot.is_ready() else 0,
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
    print("🤖 Starting Simple Sports Discord Bot")
    print("=" * 50)
    print("Expected commands after startup:")
    print("  /clear - Clear channels from sport categories")
    print("  /create-channels - Create game channels (dropdown: MLB, NFL, NBA, NHL, SOCCER, CFB)")
    print("  /sync - Force sync commands (admin only)")
    print("=" * 50)
    print(f"🚀 Build timestamp: {datetime.now().isoformat()}")
    print(f"🔧 Discord Token: {'✅ Set' if DISCORD_TOKEN else '❌ Missing'}")
    print("=" * 50)
    print("🔍 TROUBLESHOOTING:")
    print("  If commands don't appear in Discord:")
    print("  1. Use /sync command (if available)")
    print("  2. Restart Discord app")
    print("  3. Check Railway logs for errors")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\\n💥 Bot crashed: {e}")
        import traceback
        traceback.print_exc()