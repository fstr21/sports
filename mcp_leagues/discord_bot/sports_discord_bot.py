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

@bot.tree.command(name="clear-channels", description="Clear all channels from selected sport category")
@app_commands.describe(sport="Choose a sport category to clear")
@app_commands.choices(sport=[
    app_commands.Choice(name="Soccer", value="soccer"),
    app_commands.Choice(name="MLB", value="mlb"),
])
async def clear_channels(interaction: discord.Interaction, sport: str):
    """Clear all channels from a specific sport category"""
    await interaction.response.defer()
    
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.followup.send("❌ You need 'Manage Channels' permission to use this command.")
        return
    
    try:
        logger.info(f"Clear channels command used by {interaction.user.name} for sport: {sport}")
        
        # Get the appropriate category
        category_obj = None
        category_name = ""
        
        if sport == "soccer":
            # Use the specific soccer category ID you provided
            category_obj = discord.utils.get(interaction.guild.categories, id=1407474278374576178)
            category_name = "Soccer"
        elif sport == "mlb":
            # Use name lookup for MLB
            category_obj = discord.utils.get(interaction.guild.categories, name="MLB GAMES")
            category_name = "MLB"
        
        if not category_obj:
            await interaction.followup.send(f"❌ {category_name} category not found.")
            return
        
        # Get all text channels in the category
        channels_to_delete = [ch for ch in category_obj.channels if isinstance(ch, discord.TextChannel)]
        channel_count = len(channels_to_delete)
        
        if channel_count == 0:
            await interaction.followup.send(f"ℹ️ No channels found in {category_name} category.")
            return
        
        # Show what will be deleted
        embed = discord.Embed(
            title="🗑️ Clear Channels",
            description=f"Found **{channel_count} channels** in {category_name} category.",
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
        
        logger.info(f"🗑️ Attempting to delete {len(channels_to_delete)} channels from {category_name}...")
        
        for i, channel in enumerate(channels_to_delete):
            try:
                logger.info(f"🔄 Deleting channel {i+1}/{len(channels_to_delete)}: {channel.name}")
                await channel.delete()
                deleted_count += 1
                logger.info(f"✅ Successfully deleted: {channel.name}")
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
                
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
        
        # Send final result
        if deleted_count > 0:
            result_embed = discord.Embed(
                title="✅ Clear Complete",
                description=f"Successfully deleted **{deleted_count}** out of {channel_count} channels from {category_name} category.",
                color=discord.Color.green()
            )
        else:
            result_embed = discord.Embed(
                title="⚠️ Clear Failed",
                description=f"Could not delete any channels from {category_name} category. Check bot permissions.",
                color=discord.Color.red()
            )
        
        # Add failure details if any
        if failed_deletions:
            failure_text = "\\n".join(failed_deletions[:5])  # Show first 5 failures
            if len(failed_deletions) > 5:
                failure_text += f"\\n... and {len(failed_deletions) - 5} more failures"
            result_embed.add_field(
                name="❌ Failed Deletions",
                value=failure_text,
                inline=False
            )
        
        await interaction.followup.send(embed=result_embed)
        logger.info(f"Clear completed: {deleted_count}/{channel_count} channels deleted from {category_name}")
        
    except Exception as e:
        logger.error(f"Error in clear-channels command: {e}")
        await interaction.followup.send(f"❌ Error clearing channels: {str(e)}")

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
            
            # Get comprehensive analysis if we have team IDs
            if home_id and away_id:
                try:
                    # Use the proven H2H analysis (like schedule.py does)
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
                    
                    # Create comprehensive embed with proven H2H analysis
                    embed = create_comprehensive_match_embed_v3(
                        match, league, h2h_data, home_team, away_team, match_time
                    )
                    
                    # Update the message
                    await message.edit(embed=embed)
                    
                except Exception as e:
                    logger.error(f"Comprehensive analysis failed: {e}")
                    # Update with error info
                    embed.add_field(name="📊 Analysis", value="Analysis failed", inline=False)
                    await message.edit(embed=embed)
            
            created += 1
            # Small delay to avoid overwhelming the MCP
            await asyncio.sleep(1)
    
    await interaction.followup.send(f"Created {created} soccer channels from {total_matches} matches with comprehensive analysis")

def convert_to_american_odds(decimal_odds):
    """Convert decimal odds to American format - like schedule.py"""
    try:
        decimal = float(decimal_odds)
        if decimal >= 2.0:
            american = int((decimal - 1) * 100)
            return f"+{american}"
        else:
            american = int(-100 / (decimal - 1))
            return str(american)
    except (ValueError, ZeroDivisionError, TypeError):
        return str(decimal_odds)

def create_comprehensive_match_embed(match, league, h2h_data=None, home_form_data=None, away_form_data=None, home_team=None, away_team=None, match_time=None):
    """Create comprehensive match embed like schedule.py with all analysis"""
    embed = discord.Embed(
        title=f"⚽ {away_team} vs {home_team}",
        description=f"**{league}** - Comprehensive Analysis",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    
    # Basic match info
    embed.add_field(
        name="📅 Match Info",
        value=f"**Time:** {match_time}\n**League:** {league}",
        inline=True
    )
    
    # Enhanced betting odds (like schedule.py)
    odds = match.get("odds", {})
    if odds:
        betting_lines = []
        
        match_winner = odds.get('match_winner', {})
        if match_winner:
            home_odds = match_winner.get('home')
            draw_odds = match_winner.get('draw')
            away_odds = match_winner.get('away')
        else:
            home_odds = odds.get('home_win')
            draw_odds = odds.get('draw')
            away_odds = odds.get('away_win')
        
        if home_odds:
            american_home = convert_to_american_odds(home_odds)
            betting_lines.append(f"**{home_team}:** {home_odds} ({american_home})")
        if draw_odds:
            american_draw = convert_to_american_odds(draw_odds)
            betting_lines.append(f"**Draw:** {draw_odds} ({american_draw})")
        if away_odds:
            american_away = convert_to_american_odds(away_odds)
            betting_lines.append(f"**{away_team}:** {away_odds} ({american_away})")
        
        over_under = odds.get('over_under', {})
        if over_under:
            total = over_under.get('total')
            over = over_under.get('over')
            under = over_under.get('under')
            if total and over and under:
                american_over = convert_to_american_odds(over)
                american_under = convert_to_american_odds(under)
                betting_lines.append(f"**O/U {total}:** Over {over} ({american_over}), Under {under} ({american_under})")
        
        if betting_lines:
            embed.add_field(
                name="💰 Betting Lines",
                value="\\n".join(betting_lines),
                inline=False
            )
    
    # Comprehensive H2H analysis (like schedule.py)
    if h2h_data and "error" not in h2h_data:
        total_meetings = h2h_data.get('total_meetings', 0)
        if total_meetings > 0:
            team1_record = h2h_data.get('team_1_record', {})
            team2_record = h2h_data.get('team_2_record', {})
            draws = h2h_data.get('draws', {})
            
            h2h_text = f"**{total_meetings} meetings** | **{home_team}:** {team1_record.get('wins', 0)}W ({team1_record.get('win_rate', 0):.1f}%) | **{away_team}:** {team2_record.get('wins', 0)}W ({team2_record.get('win_rate', 0):.1f}%) | **Draws:** {draws.get('count', 0)}"
            
            embed.add_field(
                name="📊 Head-to-Head Record",
                value=h2h_text,
                inline=False
            )
            
            # Goals and betting analysis
            goals = h2h_data.get('goals', {})
            betting_insights = h2h_data.get('betting_insights', {})
            
            if goals:
                avg_goals = goals.get('average_per_game', 0)
                insights_text = f"**Avg Goals:** {avg_goals:.2f}/game\\n"
                
                if avg_goals > 2.8:
                    insights_text += "🔥 **OVER 2.5 Goals** - High-scoring history"
                elif avg_goals < 2.2:
                    insights_text += "🛡️ **UNDER 2.5 Goals** - Low-scoring trend"
                else:
                    insights_text += "⚖️ **Goals Market Balanced**"
                
                if betting_insights:
                    trend = betting_insights.get('goals_trend', '')
                    if trend:
                        insights_text += f"\\n**Trend:** {trend}"
                
                embed.add_field(
                    name="💡 H2H Betting Analysis",
                    value=insights_text,
                    inline=False
                )
        else:
            embed.add_field(
                name="📊 Head-to-Head",
                value=f"**No historical meetings** between {home_team} and {away_team}",
                inline=False
            )
    
    # Recent form analysis (like schedule.py comprehensive data)
    if home_form_data and "error" not in home_form_data:
        recent_form = home_form_data.get('recent_form', {})
        if recent_form:
            form_record = recent_form.get('last_5_games', {})
            wins = form_record.get('wins', 0)
            draws = form_record.get('draws', 0)
            losses = form_record.get('losses', 0)
            goals_for = recent_form.get('goals_scored', 0)
            goals_against = recent_form.get('goals_conceded', 0)
            
            home_form_text = f"**{home_team} Recent Form:** {wins}W-{draws}D-{losses}L\\n"
            home_form_text += f"**Goals:** {goals_for} scored, {goals_against} conceded"
            
            embed.add_field(
                name="🏠 Home Team Form",
                value=home_form_text,
                inline=True
            )
    
    if away_form_data and "error" not in away_form_data:
        recent_form = away_form_data.get('recent_form', {})
        if recent_form:
            form_record = recent_form.get('last_5_games', {})
            wins = form_record.get('wins', 0)
            draws = form_record.get('draws', 0)
            losses = form_record.get('losses', 0)
            goals_for = recent_form.get('goals_scored', 0)
            goals_against = recent_form.get('goals_conceded', 0)
            
            away_form_text = f"**{away_team} Recent Form:** {wins}W-{draws}D-{losses}L\\n"
            away_form_text += f"**Goals:** {goals_for} scored, {goals_against} conceded"
            
            embed.add_field(
                name="✈️ Away Team Form", 
                value=away_form_text,
                inline=True
            )
    
    # Enhanced betting recommendations based on comprehensive data
    if home_form_data and away_form_data and h2h_data:
        recommendations = []
        
        # Calculate expected goals from form data
        home_recent = home_form_data.get('recent_form', {})
        away_recent = away_form_data.get('recent_form', {})
        
        if home_recent and away_recent:
            home_avg_scored = home_recent.get('goals_scored', 0) / 5 if home_recent.get('goals_scored') else 0
            home_avg_conceded = home_recent.get('goals_conceded', 0) / 5 if home_recent.get('goals_conceded') else 0
            away_avg_scored = away_recent.get('goals_scored', 0) / 5 if away_recent.get('goals_scored') else 0
            away_avg_conceded = away_recent.get('goals_conceded', 0) / 5 if away_recent.get('goals_conceded') else 0
            
            expected_goals = (home_avg_scored + away_avg_conceded + away_avg_scored + home_avg_conceded) / 2
            
            if expected_goals > 2.8:
                recommendations.append("🎯 **OVER 2.5 Goals** - Based on recent form")
            elif expected_goals < 2.2:
                recommendations.append("🎯 **UNDER 2.5 Goals** - Based on recent form")
            
            # Form momentum
            home_form_record = home_recent.get('last_5_games', {})
            away_form_record = away_recent.get('last_5_games', {})
            
            home_points = (home_form_record.get('wins', 0) * 3) + home_form_record.get('draws', 0)
            away_points = (away_form_record.get('wins', 0) * 3) + away_form_record.get('draws', 0)
            
            if home_points > away_points + 3:
                recommendations.append(f"📈 **{home_team}** has better recent momentum")
            elif away_points > home_points + 3:
                recommendations.append(f"📈 **{away_team}** has better recent momentum")
        
        if recommendations:
            embed.add_field(
                name="🎯 Smart Betting Tips",
                value="\\n".join(recommendations),
                inline=False
            )
    
    embed.set_footer(text="Comprehensive analysis powered by Soccer MCP")
    return embed

def create_comprehensive_match_embed_v2(match, league, comprehensive_data=None, home_team=None, away_team=None, match_time=None):
    """Create comprehensive match embed using single analyze_match_betting call"""
    embed = discord.Embed(
        title=f"⚽ {away_team} vs {home_team}",
        description=f"**{league}** - Comprehensive Betting Analysis",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    
    # Basic match info
    embed.add_field(
        name="📅 Match Details",
        value=f"**Time:** {match_time}\\n**League:** {league}\\n**Match ID:** {match.get('id', 'N/A')}",
        inline=True
    )
    
    if comprehensive_data and "error" not in comprehensive_data:
        # Head-to-head analysis
        h2h = comprehensive_data.get("head_to_head", {})
        if h2h:
            total_meetings = h2h.get("total_meetings", 0)
            if total_meetings > 0:
                home_wins = h2h.get("home_team_wins", 0)
                away_wins = h2h.get("away_team_wins", 0)
                draws = h2h.get("draws", 0)
                avg_goals = h2h.get("average_goals_per_game", 0)
                
                h2h_text = f"**{total_meetings} meetings**\\n"
                h2h_text += f"**{home_team}:** {home_wins}W | **{away_team}:** {away_wins}W | **Draws:** {draws}\\n"
                h2h_text += f"**Avg Goals:** {avg_goals:.1f}/game"
                
                embed.add_field(
                    name="📊 Head-to-Head Record",
                    value=h2h_text,
                    inline=False
                )
        
        # Team form analysis
        home_form = comprehensive_data.get("home_team_form", {})
        away_form = comprehensive_data.get("away_team_form", {})
        
        if home_form:
            recent_results = home_form.get("recent_results", "")
            goals_scored = home_form.get("goals_scored_last_5", 0)
            goals_conceded = home_form.get("goals_conceded_last_5", 0)
            
            home_form_text = f"**Form:** {recent_results}\\n**Goals:** {goals_scored} scored, {goals_conceded} conceded"
            
            embed.add_field(
                name="🏠 Home Team Form",
                value=home_form_text,
                inline=True
            )
        
        if away_form:
            recent_results = away_form.get("recent_results", "")
            goals_scored = away_form.get("goals_scored_last_5", 0)
            goals_conceded = away_form.get("goals_conceded_last_5", 0)
            
            away_form_text = f"**Form:** {recent_results}\\n**Goals:** {goals_scored} scored, {goals_conceded} conceded"
            
            embed.add_field(
                name="✈️ Away Team Form",
                value=away_form_text,
                inline=True
            )
        
        # Betting predictions and insights
        predictions = comprehensive_data.get("betting_predictions", {})
        if predictions:
            insights = []
            
            # Goals prediction
            expected_goals = predictions.get("expected_total_goals")
            if expected_goals:
                if expected_goals > 2.75:
                    insights.append(f"🔥 **OVER 2.5 Goals** (Expected: {expected_goals:.1f})")
                elif expected_goals < 2.25:
                    insights.append(f"🛡️ **UNDER 2.5 Goals** (Expected: {expected_goals:.1f})")
                else:
                    insights.append(f"⚖️ **Goals Market Balanced** (Expected: {expected_goals:.1f})")
            
            # Winner prediction
            winner_prediction = predictions.get("most_likely_outcome")
            confidence = predictions.get("confidence_level", "")
            if winner_prediction:
                insights.append(f"🎯 **Prediction:** {winner_prediction} {confidence}")
            
            # BTTS prediction
            btts = predictions.get("both_teams_to_score")
            if btts is not None:
                btts_text = "YES" if btts else "NO"
                insights.append(f"🥅 **BTTS:** {btts_text}")
            
            # Value bets
            value_bets = predictions.get("value_bets", [])
            if value_bets:
                insights.append(f"💎 **Value Bets:** {', '.join(value_bets)}")
            
            if insights:
                embed.add_field(
                    name="🎯 Betting Analysis & Tips",
                    value="\\n".join(insights),
                    inline=False
                )
        
        # Key factors
        key_factors = comprehensive_data.get("key_factors", [])
        if key_factors:
            factors_text = "\\n".join([f"• {factor}" for factor in key_factors[:4]])  # Show top 4
            embed.add_field(
                name="🔑 Key Factors",
                value=factors_text,
                inline=False
            )
        
        # Risk assessment
        risk = comprehensive_data.get("risk_assessment", {})
        if risk:
            confidence = risk.get("confidence_level", "Unknown")
            risk_factors = risk.get("risk_factors", [])
            
            risk_text = f"**Confidence:** {confidence}"
            if risk_factors:
                risk_text += f"\\n**Risks:** {', '.join(risk_factors[:2])}"  # Show top 2 risks
            
            embed.add_field(
                name="⚠️ Risk Assessment",
                value=risk_text,
                inline=True
            )
    
    else:
        # Fallback to basic info if comprehensive analysis fails
        error_msg = comprehensive_data.get("error", "Analysis in progress...") if comprehensive_data else "Analysis in progress..."
        embed.add_field(
            name="📊 Analysis Status",
            value=f"⏳ {error_msg}",
            inline=False
        )
    
    # Add betting odds from original match data
    odds = match.get("odds", {})
    if odds:
        betting_lines = []
        
        match_winner = odds.get('match_winner', {})
        if match_winner:
            home_odds = match_winner.get('home')
            draw_odds = match_winner.get('draw')
            away_odds = match_winner.get('away')
        else:
            home_odds = odds.get('home_win')
            draw_odds = odds.get('draw')
            away_odds = odds.get('away_win')
        
        if home_odds:
            american_home = convert_to_american_odds(home_odds)
            betting_lines.append(f"**{home_team}:** {home_odds} ({american_home})")
        if draw_odds:
            american_draw = convert_to_american_odds(draw_odds)
            betting_lines.append(f"**Draw:** {draw_odds} ({american_draw})")
        if away_odds:
            american_away = convert_to_american_odds(away_odds)
            betting_lines.append(f"**{away_team}:** {away_odds} ({american_away})")
        
        if betting_lines:
            embed.add_field(
                name="💰 Current Odds",
                value="\\n".join(betting_lines),
                inline=False
            )
    
    embed.set_footer(text="Powered by Soccer MCP • Comprehensive Match Analysis")
    return embed

def create_comprehensive_match_embed_v3(match, league, h2h_data=None, home_team=None, away_team=None, match_time=None):
    """Create comprehensive match embed using proven H2H analysis (like schedule.py)"""
    embed = discord.Embed(
        title=f"⚽ {away_team} vs {home_team}",
        description=f"**{league}** - Comprehensive Analysis",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    
    # Basic match info
    embed.add_field(
        name="📅 Match Details",
        value=f"**Time:** {match_time}\\n**League:** {league}\\n**Match ID:** {match.get('id', 'N/A')}",
        inline=True
    )
    
    # Add betting odds from match data (like schedule.py)
    odds = match.get("odds", {})
    if odds:
        betting_lines = []
        
        match_winner = odds.get('match_winner', {})
        if match_winner:
            home_odds = match_winner.get('home')
            draw_odds = match_winner.get('draw')
            away_odds = match_winner.get('away')
        else:
            home_odds = odds.get('home_win')
            draw_odds = odds.get('draw')
            away_odds = odds.get('away_win')
        
        if home_odds:
            american_home = convert_to_american_odds(home_odds)
            betting_lines.append(f"**{home_team}:** {home_odds} ({american_home})")
        if draw_odds:
            american_draw = convert_to_american_odds(draw_odds)
            betting_lines.append(f"**Draw:** {draw_odds} ({american_draw})")
        if away_odds:
            american_away = convert_to_american_odds(away_odds)
            betting_lines.append(f"**{away_team}:** {away_odds} ({american_away})")
        
        # Add over/under if available
        over_under = odds.get('over_under', {})
        if over_under:
            total = over_under.get('total')
            over = over_under.get('over')
            under = over_under.get('under')
            if total and over and under:
                american_over = convert_to_american_odds(over)
                american_under = convert_to_american_odds(under)
                betting_lines.append(f"**O/U {total}:** Over {over} ({american_over}), Under {under} ({american_under})")
        
        if betting_lines:
            embed.add_field(
                name="💰 Betting Lines",
                value="\\n".join(betting_lines),
                inline=False
            )
    
    # Comprehensive H2H analysis (exactly like schedule.py)
    if h2h_data and "error" not in h2h_data:
        total_meetings = h2h_data.get('total_meetings', 0)
        if total_meetings > 0:
            team1_record = h2h_data.get('team_1_record', {})
            team2_record = h2h_data.get('team_2_record', {})
            draws = h2h_data.get('draws', {})
            
            h2h_text = f"**{total_meetings} meetings** | **{home_team}:** {team1_record.get('wins', 0)}W ({team1_record.get('win_rate', 0):.1f}%) | **{away_team}:** {team2_record.get('wins', 0)}W ({team2_record.get('win_rate', 0):.1f}%) | **Draws:** {draws.get('count', 0)}"
            
            embed.add_field(
                name="📊 Head-to-Head Record",
                value=h2h_text,
                inline=False
            )
            
            # Goals and betting analysis (like schedule.py)
            goals = h2h_data.get('goals', {})
            betting_insights = h2h_data.get('betting_insights', {})
            
            insights_text = ""
            if goals:
                avg_goals = goals.get('average_per_game', 0)
                insights_text += f"**Avg Goals:** {avg_goals:.2f}/game\\n"
                
                if avg_goals > 2.8:
                    insights_text += "🔥 **OVER 2.5 Goals** - High-scoring history\\n"
                elif avg_goals < 2.2:
                    insights_text += "🛡️ **UNDER 2.5 Goals** - Low-scoring trend\\n"
                else:
                    insights_text += "⚖️ **Goals Market Balanced**\\n"
            
            if betting_insights:
                trend = betting_insights.get('goals_trend', '')
                if trend:
                    insights_text += f"**Trend:** {trend}"
            
            if insights_text:
                embed.add_field(
                    name="💡 H2H Betting Analysis",
                    value=insights_text,
                    inline=False
                )
                
            # Dominance analysis (like schedule.py)
            team1_wins = team1_record.get('wins', 0)
            team2_wins = team2_record.get('wins', 0)
            
            dominance_text = ""
            if team1_wins > team2_wins * 2:
                dominance_text = f"📈 **{home_team} DOMINATES** this matchup ({team1_record.get('win_rate', 0):.1f}% win rate)"
            elif team2_wins > team1_wins * 2:
                dominance_text = f"📈 **{away_team} DOMINATES** this matchup ({team2_record.get('win_rate', 0):.1f}% win rate)"
            else:
                dominance_text = "⚖️ **Balanced matchup** - no clear historical dominance"
            
            if dominance_text:
                embed.add_field(
                    name="🏆 Historical Dominance",
                    value=dominance_text,
                    inline=False
                )
        else:
            embed.add_field(
                name="📊 Head-to-Head",
                value=f"**No historical meetings** between {home_team} and {away_team}\\nConsider recent form and league context for betting",
                inline=False
            )
    else:
        # Show error details for debugging
        error_msg = "Analysis in progress..."
        if h2h_data and "error" in h2h_data:
            error_msg = f"H2H data unavailable: {h2h_data['error']}"
        
        embed.add_field(
            name="📊 H2H Analysis",
            value=error_msg,
            inline=False
        )
    
    # Match events analysis if available
    events = match.get("events", [])
    if events:
        goal_events = [e for e in events if 'goal' in e.get('event_type', '').lower()]
        card_events = [e for e in events if 'card' in e.get('event_type', '').lower()]
        
        if match.get("status") == "finished":
            embed.add_field(
                name="⚽ Match Completed",
                value=f"**Final Score:** {match.get('goals', {}).get('home_ft_goals', 0)}-{match.get('goals', {}).get('away_ft_goals', 0)}\\n**Events:** {len(goal_events)} goals, {len(card_events)} cards",
                inline=True
            )
    
    embed.set_footer(text="Powered by Soccer MCP • Based on schedule.py methodology")
    return embed

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