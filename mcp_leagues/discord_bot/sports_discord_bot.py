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

# Import HTML-to-image functionality
from utils.html_to_image import create_baseball_analysis_image
import io

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


@bot.tree.command(name="testmlb", description="Generate MLB analysis as image (Test Command)")
async def test_mlb_image_command(interaction: discord.Interaction):
    """Test command to generate MLB analysis as image"""
    await interaction.response.defer()
    
    try:
        # Get MLB handler 
        mlb_handler = bot.sport_manager.get_sport_handler("mlb")
        if not mlb_handler:
            embed = discord.Embed(
                title="❌ Error",
                description="MLB handler not available",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
            
        # Get today's games
        today_str = datetime.now().strftime("%Y-%m-%d")
        matches = await mlb_handler.get_matches(today_str)
        
        if not matches:
            embed = discord.Embed(
                title="❌ No Games",
                description="No MLB games found for today",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Get first game for testing
        match = matches[0]
        logger.info(f"Testing image generation for: {match.away_team} @ {match.home_team}")
        
        # Get comprehensive analysis data (simplified for test)
        # For now, just use basic data - can enhance later with real MCP calls
        team_forms = None  # Could call real team form methods later
        betting_odds = None  # Could call real betting odds methods later
        pitcher_matchup = None  # Could call real pitcher methods later
        
        # Create template data dictionary
        template_data = await mlb_handler.create_template_data_for_image(
            match, team_forms, betting_odds, pitcher_matchup
        )
        
        # Generate image
        image_bytes = await create_baseball_analysis_image(template_data)
        
        # Create Discord file
        image_file = discord.File(
            io.BytesIO(image_bytes), 
            filename=f"mlb_analysis_{match.away_team.replace(' ', '_')}_vs_{match.home_team.replace(' ', '_')}.png"
        )
        
        # Create simple embed to go with image
        embed = discord.Embed(
            title="⚾ MLB Analysis (Image Test)",
            description=f"**{match.away_team} @ {match.home_team}**\n📊 Generated comprehensive analysis image",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_footer(text="Enhanced Chronulus MCP • Image Generation Test")
        
        # Send image with embed
        await interaction.followup.send(embed=embed, file=image_file)
        logger.info(f"Successfully sent MLB analysis image for {match.away_team} @ {match.home_team}")
        
    except Exception as e:
        logger.error(f"Error in testmlb command: {e}")
        import traceback
        traceback.print_exc()
        
        embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to generate MLB analysis image: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)


@bot.tree.command(name="textonly", description="Test Custom Chronulus AI analysis with Red Sox @ Yankees data")
async def test_textonly_command(interaction: discord.Interaction):
    """Test command to run Custom Chronulus analysis and break into Discord embeds"""
    await interaction.response.defer()
    
    try:
        # Enhanced comprehensive game data matching the successful comprehensive analysis
        game_data = {
            "home_team": "New York Yankees (82-58, .586 win%, AL East leaders)",
            "away_team": "Boston Red Sox (75-65, .536 win%, Wild Card contention)", 
            "sport": "Baseball",
            "venue": "Yankee Stadium (49,642 capacity, pitcher-friendly dimensions, iconic atmosphere)",
            "game_date": "August 24, 2025 - 7:05 PM ET",
            "home_record": "82-58 (.586 win%), +89 run differential, 4.12 ERA, 7-3 L10, 43-26 home record",
            "away_record": "75-65 (.536 win%), +42 run differential, 4.38 ERA, 6-4 L10, 35-35 road record",
            "home_moneyline": -165,
            "away_moneyline": 145,
            "additional_context": (
                "COMPLETE MARKET DATA: "
                "Moneyline - Yankees -165 (62.3% implied), Red Sox +145 (40.8% implied). "
                "Run Line - Yankees -1.5 (+115), Red Sox +1.5 (-135). "
                "Total - Over 9.0 (-108), Under 9.0 (-112). "
                "TEAM PERFORMANCE: "
                "Yankees: 82-58 record, +89 run differential (5.21 scored, 4.32 allowed), "
                "43-26 home record, 7-3 in last 10, currently 2.5 games ahead in AL East. "
                "Key players: Aaron Judge (.312 BA, 48 HR), Juan Soto (.288 BA, 35 HR). "
                "Red Sox: 75-65 record, +42 run differential (4.89 scored, 4.38 allowed), "
                "35-35 road record, 6-4 in last 10, fighting for Wild Card spot. "
                "Key players: Rafael Devers (.287 BA, 28 HR), Trevor Story (.251 BA, 15 HR). "
                "PITCHING MATCHUP: "
                "Yankees starter: Gerrit Cole (12-7, 3.41 ERA, 1.09 WHIP, 198 K). "
                "Red Sox starter: Brayan Bello (11-9, 4.15 ERA, 1.31 WHIP, 156 K). "
                "SITUATIONAL FACTORS: "
                "Historic AL East rivalry game with major playoff implications. "
                "Yankees need wins to secure division title. Red Sox need wins for Wild Card. "
                "Late season pressure, national TV audience, sellout crowd expected. "
                "Weather: 72°F, clear skies, 8mph wind from left field. "
                "Recent head-to-head: Yankees 7-6 this season vs Red Sox. "
                "BETTING TRENDS: "
                "Yankees 54-86 ATS this season, 21-48 ATS as home favorites. "
                "Red Sox 73-67 ATS this season, 34-31 ATS as road underdogs. "
                "Over/Under: Yankees games 68-72 O/U, Red Sox games 71-69 O/U. "
                "INJURY REPORT: "
                "Yankees: Giancarlo Stanton (hamstring, questionable). "
                "Red Sox: All key players healthy and available. "
                "PUBLIC BETTING: 67% of bets on Yankees, 33% on Red Sox."
            )
        }
        
        # Get Custom Chronulus MCP URL from config
        custom_chronulus_url = bot.config.custom_chronulus_mcp_url
        
        # MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": "getCustomChronulusAnalysis",
                "arguments": {
                    "game_data": game_data,
                    "expert_count": 5,
                    "analysis_depth": "comprehensive"
                }
            }
        }
        
        # Call Custom Chronulus MCP
        import httpx
        import json
        from datetime import datetime
        import os
        
        logger.info(f"Starting Custom Chronulus analysis...")
        logger.info(f"MCP URL: {custom_chronulus_url}")
        logger.info(f"Game: {game_data['away_team']} @ {game_data['home_team']}")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            logger.info(f"Sending request to Custom Chronulus MCP...")
            response = await client.post(custom_chronulus_url, json=mcp_request)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Received response from Custom Chronulus MCP")
            
            if "result" not in result:
                error_msg = result.get('error', 'Unknown error')
                embed = discord.Embed(
                    title="❌ MCP Error",
                    description=f"Custom Chronulus MCP error: {error_msg}",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Extract analysis text
            mcp_result = result["result"]
            analysis_text = mcp_result["content"][0]["text"] if "content" in mcp_result and mcp_result["content"] else "No analysis returned"
            
            # Export raw MCP results to markdown
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_dir = "C:\\Users\\fstr2\\Desktop\\sports\\chronulus\\results"
            md_file = f"{results_dir}\\textonly_raw_{timestamp}.md"
            
            # Create directory if it doesn't exist
            try:
                os.makedirs(results_dir, exist_ok=True)
                logger.info(f"Created/verified results directory: {results_dir}")
            except Exception as dir_error:
                logger.error(f"Failed to create results directory: {dir_error}")
                # Fallback to a simpler path
                results_dir = "C:\\Users\\fstr2\\Desktop\\sports"
                md_file = f"{results_dir}\\textonly_raw_{timestamp}.md"
            
            try:
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(f"# /textonly Command - Raw MCP Results\\n\\n")
                    f.write(f"**Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}\\n")
                    f.write(f"**Command**: /textonly\\n")
                    f.write(f"**Game**: {game_data['away_team']} @ {game_data['home_team']}\\n\\n")
                    f.write("## Raw MCP Response\\n\\n")
                    f.write("```json\\n")
                    f.write(json.dumps(result, indent=2))
                    f.write("\\n```\\n\\n")
                    f.write("## Analysis Text\\n\\n")
                    f.write("```\\n")
                    f.write(analysis_text)
                    f.write("\\n```\\n")
                
                logger.info(f"✅ SUCCESS: Raw MCP results exported to: {md_file}")
                
                # Verify file was created
                if os.path.exists(md_file):
                    file_size = os.path.getsize(md_file)
                    logger.info(f"File verified: {md_file} ({file_size} bytes)")
                else:
                    logger.error(f"❌ File was not created: {md_file}")
                    
            except Exception as file_error:
                logger.error(f"❌ Failed to create markdown file: {file_error}")
                # Try alternative location
                fallback_file = f"C:\\Users\\fstr2\\Desktop\\sports\\textonly_raw_{timestamp}.md"
                try:
                    with open(fallback_file, 'w', encoding='utf-8') as f:
                        f.write(f"# /textonly Command - Raw MCP Results (Fallback)\\n\\n")
                        f.write(f"**Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}\\n")
                        f.write(f"Analysis Text: {analysis_text[:500]}...\\n")
                    logger.info(f"✅ Fallback file created: {fallback_file}")
                    md_file = fallback_file
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback file also failed: {fallback_error}")
                    md_file = "file_creation_failed"
            
            # Parse analysis if it's JSON
            try:
                analysis_data = json.loads(analysis_text)
                
                # Create multiple Discord embeds
                embeds = []
                
                # Embed 1: Game Overview
                embed1 = discord.Embed(
                    title="⚾ Custom Chronulus Analysis",
                    description=f"**{game_data['away_team']} @ {game_data['home_team']}**\\n{game_data['game_date']} | {game_data['venue']}",
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                
                # Add betting lines
                embed1.add_field(
                    name="💰 Betting Market",
                    value=f"**Moneyline**\\nRed Sox: +{game_data['away_moneyline']} (40.8% implied)\\nYankees: {game_data['home_moneyline']} (62.3% implied)\\n\\n**Run Line**\\nRed Sox: +1.5 (-135)\\nYankees: -1.5 (+115)\\n\\n**Total**\\nOver 9.0 (-108) | Under 9.0 (-112)",
                    inline=False
                )
                embeds.append(embed1)
                
                # Embed 2: AI Probabilities 
                if "analysis" in analysis_data:
                    analysis = analysis_data["analysis"]
                    embed2 = discord.Embed(
                        title="🤖 AI Probability Assessment",
                        color=discord.Color.green()
                    )
                    
                    if "away_team_win_probability" in analysis and "home_team_win_probability" in analysis:
                        away_prob = analysis["away_team_win_probability"] * 100
                        home_prob = analysis["home_team_win_probability"] * 100
                        
                        embed2.add_field(
                            name="🎯 Win Probabilities",
                            value=f"**Red Sox**: {away_prob:.1f}%\\n**Yankees**: {home_prob:.1f}%",
                            inline=True
                        )
                        
                        # Calculate edges
                        red_sox_edge = away_prob - 40.8
                        yankees_edge = home_prob - 62.3
                        
                        embed2.add_field(
                            name="📊 Market Edge",
                            value=f"**Red Sox**: {red_sox_edge:+.1f}pp\\n**Yankees**: {yankees_edge:+.1f}pp",
                            inline=True
                        )
                    
                    if "betting_recommendation" in analysis:
                        embed2.add_field(
                            name="💡 Recommendation", 
                            value=analysis["betting_recommendation"],
                            inline=False
                        )
                    
                    embeds.append(embed2)
                
                # Embed 3: Expert Analysis (enhanced processing for comprehensive format)
                if "analysis" in analysis_data and "expert_analysis" in analysis_data["analysis"]:
                    embed3 = discord.Embed(
                        title="🧠 Chief Analyst Report",
                        color=discord.Color.orange()
                    )
                    
                    expert_text = analysis_data["analysis"]["expert_analysis"]
                    
                    # Enhanced processing to preserve key sections from comprehensive analysis
                    if len(expert_text) > 1000:
                        # Strategy: Keep key sections and final assessment, trim verbose parts
                        if "FINAL ASSESSMENT:" in expert_text:
                            # Find key sections
                            market_baseline_start = expert_text.find("**MARKET BASELINE**:")
                            final_start = expert_text.find("FINAL ASSESSMENT:")
                            
                            if market_baseline_start > 0 and final_start > 0:
                                # Get market baseline (essential)
                                market_section = expert_text[market_baseline_start:market_baseline_start + 200] + "..."
                                
                                # Final assessment (must keep)
                                final_section = expert_text[final_start:]
                                
                                # Reconstruct with key information
                                expert_text = f"{market_section}\n\n{final_section}"
                            
                            # Final length check
                            if len(expert_text) > 1000:
                                # Last resort: prioritize final assessment
                                final_start = expert_text.find("FINAL ASSESSMENT:")
                                if final_start > 0:
                                    final_section = expert_text[final_start:]
                                    beginning_allowance = 1000 - len(final_section) - 50
                                    if beginning_allowance > 0:
                                        expert_text = expert_text[:beginning_allowance] + "\n\n*[Analysis condensed]*\n\n" + final_section
                                    else:
                                        expert_text = expert_text[:500] + "\n\n" + final_section
                                else:
                                    expert_text = expert_text[:950] + "..."
                        else:
                            expert_text = expert_text[:950] + "..."
                    
                    embed3.add_field(
                        name="📋 Institutional Analysis",
                        value=expert_text,
                        inline=False
                    )
                    embeds.append(embed3)
                
                # Embed 4: Technical Details
                embed4 = discord.Embed(
                    title="🔧 Technical Details",
                    color=discord.Color.purple()
                )
                
                if "analysis" in analysis_data:
                    analysis = analysis_data["analysis"] 
                    embed4.add_field(
                        name="📊 Analysis Info",
                        value=f"**Expert Count**: {analysis.get('expert_count', 'N/A')}\\n**Depth**: {analysis.get('analysis_depth', 'N/A')}\\n**Model**: {analysis.get('model_used', 'N/A')}\\n**Cost**: {analysis.get('cost_estimate', 'N/A')}",
                        inline=True
                    )
                    
                    if "beta_params" in analysis:
                        beta = analysis["beta_params"]
                        embed4.add_field(
                            name="📈 Statistical Params",
                            value=f"**Alpha**: {beta.get('alpha', 0):.2f}\\n**Beta**: {beta.get('beta', 0):.2f}\\n**Mean**: {beta.get('mean', 0):.3f}",
                            inline=True
                        )
                
                if md_file != "file_creation_failed":
                    embed4.add_field(
                        name="📄 Export Info",
                        value=f"Raw MCP results exported to:\\n`{os.path.basename(md_file)}`\\n\\nFull path: `{md_file}`",
                        inline=False
                    )
                else:
                    embed4.add_field(
                        name="⚠️ Export Warning",
                        value="Failed to export raw MCP results to file",
                        inline=False
                    )
                
                embed4.set_footer(text=f"Custom Chronulus MCP • {datetime.now().strftime('%I:%M %p ET')}")
                embeds.append(embed4)
                
                # Send all embeds
                for i, embed in enumerate(embeds):
                    if i == 0:
                        await interaction.followup.send(embed=embed)
                    else:
                        await asyncio.sleep(0.5)  # Slight delay between embeds
                        await interaction.followup.send(embed=embed)
                
                logger.info(f"Successfully sent {len(embeds)} embeds for Custom Chronulus analysis")
                
            except json.JSONDecodeError:
                # Handle non-JSON response
                embed = discord.Embed(
                    title="📝 Custom Chronulus Analysis (Text)",
                    description=f"**{game_data['away_team']} @ {game_data['home_team']}**",
                    color=discord.Color.blue()
                )
                
                # Truncate text response for Discord
                if len(analysis_text) > 1000:
                    analysis_text = analysis_text[:1000] + "..."
                
                embed.add_field(
                    name="🤖 AI Analysis",
                    value=analysis_text,
                    inline=False
                )
                
                embed.add_field(
                    name="📄 Full Results",
                    value=f"Complete analysis exported to:\\n`{os.path.basename(md_file)}`",
                    inline=False
                )
                
                embed.set_footer(text=f"Custom Chronulus MCP • Text Response")
                await interaction.followup.send(embed=embed)
                
    except Exception as e:
        logger.error(f"Error in textonly command: {e}")
        import traceback
        traceback.print_exc()
        
        embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to run Custom Chronulus analysis: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)


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