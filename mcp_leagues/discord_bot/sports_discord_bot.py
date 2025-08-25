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
from config import config, BotConfig  # type: ignore

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
            command_prefix="!",  # Default prefix for text commands
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
        
        # Create template data dictionary using the actual method
        if hasattr(mlb_handler, 'create_template_data_for_image'):
            template_data = await mlb_handler.create_template_data_for_image(  # type: ignore
                match, team_forms, betting_odds, pitcher_matchup
            )
        else:
            # Fallback template data if method doesn't exist
            template_data = {
                'game_date': datetime.now().strftime('%B %d, %Y - %I:%M %p ET'),
                'venue_name': match.additional_data.get('venue', 'MLB Stadium'),
                'home_team_name': match.home_team,
                'away_team_name': match.away_team,
                'home_team_logo': match.home_team[:3].upper(),
                'away_team_logo': match.away_team[:3].upper(),
                'home_team_color_primary': '#1a4f3a',
                'away_team_color_secondary': '#2d5a27'
            }
        
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


@bot.tree.command(name="textonly", description="Enhanced Custom Chronulus AI analysis - Clean readable format")
async def test_textonly_command(interaction: discord.Interaction):
    """Display comprehensive Chronulus analysis in clean, readable Discord format"""
    await interaction.response.defer()
    
    try:
        # Same game data as test script
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
                "PUBLIC BETTING: 67% of bets on Yankees, 33% on Red Sox. "
                "ANALYSIS REQUIREMENTS: MANDATORY player-specific analysis with names and statistics. "
                "Must specifically mention 'Gerrit Cole (3.41 ERA)' vs 'Brayan Bello (4.15 ERA)' comparison. "
                "Include individual player performance metrics, ERA comparisons, WHIP analysis, and strikeout rates. "
                "Analyze how Cole's 3.41 ERA compares to Bello's 4.15 ERA and impact on game outcome. "
                "Reference key position players by name (Aaron Judge, Juan Soto, Rafael Devers, Trevor Story). "
                "Provide detailed statistical breakdowns showing why specific players give advantages to their teams."
            )
        }
        # Get Custom Chronulus MCP URL from config
        custom_chronulus_url = bot.config.custom_chronulus_mcp_url
        
        # MCP request for 5-expert analysis with player focus
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": "getCustomChronulusAnalysis",
                "arguments": {
                    "game_data": game_data,
                    "expert_count": 5,
                    "analysis_depth": "comprehensive",
                    "player_analysis_required": True,
                    "specific_instructions": "Must analyze individual player matchups, especially Gerrit Cole vs Brayan Bello pitching comparison with ERA analysis"
                }
            }
        }
        
        # Call Custom Chronulus MCP
        import httpx
        import json
        from datetime import datetime
        
        logger.info(f"Starting Enhanced Chronulus Analysis (matching test script)...")
        logger.info(f"Game: {game_data['away_team']} @ {game_data['home_team']}")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(custom_chronulus_url, json=mcp_request)
            response.raise_for_status()
            result = response.json()
            
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
            
            # Parse the JSON analysis (same as test script)
            try:
                analysis_data = json.loads(analysis_text)
                analysis = analysis_data.get("analysis", {})
                
                # EMBED 1: Test Overview & Metrics (matching console output)
                embed1 = discord.Embed(
                    title="🧪 Enhanced Chronulus Test Results",
                    description=f"**{game_data['away_team']} @ {game_data['home_team']}**\n{game_data['game_date']} | {game_data['venue']}",
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                
                # Test metrics (matching console output)
                embed1.add_field(
                    name="📊 Analysis Quality Metrics",
                    value=f"**Expert Count**: {analysis.get('expert_count', 'N/A')}\n**Model Used**: {analysis.get('model_used', 'N/A')}\n**Cost Estimate**: {analysis.get('cost_estimate', 'N/A')}\n**Analysis Length**: {len(analysis.get('expert_analysis', ''))} characters",
                    inline=True
                )
                
                # Game context
                embed1.add_field(
                    name="⚾ Game Data Analysis",
                    value=f"**Yankees**: {game_data['home_moneyline']} (62.3% implied)\n**Red Sox**: +{game_data['away_moneyline']} (40.8% implied)\n**Context Length**: {len(game_data['additional_context'])} chars",
                    inline=True
                )
                
                await interaction.followup.send(embed=embed1)
                
                # EMBED 2: Win Probabilities (matching test output)
                embed2 = discord.Embed(
                    title="🎯 Win Probability Assessment",
                    color=discord.Color.green()
                )
                
                if "away_team_win_probability" in analysis and "home_team_win_probability" in analysis:
                    away_prob = analysis["away_team_win_probability"] * 100
                    home_prob = analysis["home_team_win_probability"] * 100
                    
                    # Visual probability display
                    away_bars = int(away_prob / 10)
                    home_bars = int(home_prob / 10)
                    away_visual = f"{'🟩' * away_bars}{'⬜' * (10 - away_bars)}"
                    home_visual = f"{'🟦' * home_bars}{'⬜' * (10 - home_bars)}"
                    
                    embed2.add_field(
                        name="📊 Win Probabilities",
                        value=f"**Red Sox: {away_prob:.1f}%**\n{away_visual}\n\n**Yankees: {home_prob:.1f}%**\n{home_visual}",
                        inline=False
                    )
                
                # Betting recommendation (matching test output)
                if "betting_recommendation" in analysis:
                    rec_emoji = "✅" if "BET" in analysis["betting_recommendation"].upper() else "⚠️"
                    embed2.add_field(
                        name="💰 Recommendation",
                        value=f"{rec_emoji} **{analysis['betting_recommendation']}**",
                        inline=True
                    )
                
                await interaction.followup.send(embed=embed2)
                
                # EMBED 3: Expert Analysis Content
                expert_analysis = analysis.get("expert_analysis", "")
                if expert_analysis:
                    embed3 = discord.Embed(
                        title="📋 Expert Analysis Report",
                        color=discord.Color.orange()
                    )
                    
                    # Extract Market Baseline section
                    if "**MARKET BASELINE**:" in expert_analysis:
                        start = expert_analysis.find("**MARKET BASELINE**:")
                        end = expert_analysis.find("**ANALYTICAL", start)
                        if end == -1:
                            end = expert_analysis.find("**KEY FACTORS", start)
                        if end > start:
                            market_baseline = expert_analysis[start:end].strip()
                            embed3.add_field(
                                name="📊 Market Baseline",
                                value=market_baseline[:1000],
                                inline=False
                            )
                    
                    # Extract Key Factors section
                    if "**KEY FACTORS FROM DATA**:" in expert_analysis:
                        start = expert_analysis.find("**KEY FACTORS FROM DATA**:")
                        end = expert_analysis.find("**BASEBALL VARIANCE", start)
                        if end == -1:
                            end = expert_analysis.find("**DIRECTIONAL", start)
                        if end > start:
                            key_factors = expert_analysis[start:end].strip()
                            embed3.add_field(
                                name="🔍 Key Factors From Data",
                                value=key_factors[:1000],
                                inline=False
                            )
                    
                    await interaction.followup.send(embed=embed3)
                
                # EMBED 4: Final Assessment & Quality Check
                embed4 = discord.Embed(
                    title="⚖️ Final Assessment & Quality Check",
                    color=discord.Color.purple()
                )
                
                # Extract Final Assessment (matching test structure)
                if "FINAL ASSESSMENT:" in expert_analysis:
                    final_start = expert_analysis.find("FINAL ASSESSMENT:")
                    final_assessment = expert_analysis[final_start:].strip()
                    embed4.add_field(
                        name="🎯 Expert Final Assessment",
                        value=final_assessment[:1000],
                        inline=False
                    )
                
                # Quality indicators check (matching test output)
                quality_indicators = [
                    "MARKET BASELINE",
                    "FINAL ASSESSMENT",
                    "Win Probability:",
                    "Analyst Confidence:",
                    "Recommendation:"
                ]
                found_indicators = [indicator for indicator in quality_indicators if indicator in expert_analysis]
                
                embed4.add_field(
                    name="✅ Quality Indicators Found",
                    value=f"**Count**: {len(found_indicators)}/5\n**All Elements**: {'✅' if len(found_indicators) == 5 else '❌'}\n**Indicators**: {', '.join(found_indicators[:3])}",
                    inline=True
                )
                
                # Beta parameters (matching test data)
                if "beta_params" in analysis:
                    beta = analysis["beta_params"]
                    embed4.add_field(
                        name="📈 Statistical Model",
                        value=f"**Alpha**: {beta.get('alpha', 0):.2f}\n**Beta**: {beta.get('beta', 0):.2f}\n**Mean**: {beta.get('mean', 0):.3f}\n**Variance**: {beta.get('variance', 0):.6f}",
                        inline=True
                    )
                
                embed4.set_footer(text=f"Enhanced Chronulus Test Completed • {datetime.now().strftime('%I:%M %p ET')}")
                await interaction.followup.send(embed=embed4)
                
                logger.info(f"Successfully displayed enhanced Chronulus test results in readable Discord format")
                
            except json.JSONDecodeError:
                # Fallback for unexpected text format
                embed = discord.Embed(
                    title="📄 Raw Analysis Output",
                    description=f"**{game_data['away_team']} @ {game_data['home_team']}**",
                    color=discord.Color.blue()
                )
                
                embed.add_field(
                    name="🤖 Analysis Content",
                    value=analysis_text[:1000] + "..." if len(analysis_text) > 1000 else analysis_text,
                    inline=False
                )
                
                await interaction.followup.send(embed=embed)
                
    except Exception as e:
        logger.error(f"Error in enhanced textonly command: {e}")
        import traceback
        traceback.print_exc()
        
        embed = discord.Embed(
            title="❌ Test Error",
            description=f"Failed to run enhanced Chronulus test: {str(e)}",
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

