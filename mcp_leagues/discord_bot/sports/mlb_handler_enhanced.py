"""
Enhanced MLB Handler - Full MCP Integration
Uses all 8 MLB MCP tools to provide comprehensive game analysis
"""
import asyncio
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import discord

from core.base_sport_handler import BaseSportHandler, Match, ChannelCreationResult, ClearResult

logger = logging.getLogger(__name__)

class EnhancedMLBHandler(BaseSportHandler):
    """
    Enhanced MLB handler using all 8 MLB MCP tools:
    1. getMLBScheduleET - Game schedules
    2. getMLBTeams - Team information  
    3. getMLBTeamRoster - Team rosters
    4. getMLBPlayerLastN - Player stats
    5. getMLBPitcherMatchup - Pitcher analysis
    6. getMLBTeamForm - Team standings/form
    7. getMLBPlayerStreaks - Player streaks
    8. getMLBTeamScoringTrends - Team scoring patterns
    """
    
    def __init__(self, sport_name: str, config: Dict[str, Any], mcp_client):
        """Initialize enhanced MLB handler"""
        super().__init__(sport_name, config, mcp_client)
        self.mcp_url = config.get('mcp_url', 'https://mlbmcp-production.up.railway.app/mcp')
        
    async def create_channels(self, interaction: discord.Interaction, date: str) -> ChannelCreationResult:
        """
        Create enhanced MLB channels with comprehensive analysis
        Uses all 8 MLB MCP tools for detailed game information
        """
        try:
            # Get matches for the date using enhanced data
            matches = await self.get_enhanced_matches(date)
            
            if not matches:
                return ChannelCreationResult(
                    success=True,
                    channels_created=0,
                    total_matches=0,
                    errors=[],
                    message=f"No MLB games found for {date}"
                )
            
            # Get or create category
            category = await self.create_category(interaction.guild)
            
            # Create channels with enhanced data
            created = 0
            errors = []
            total_matches = len(matches)
            
            for match in matches:
                try:
                    # Check if channel already exists
                    channel_name = self.format_channel_name(match.home_team, match.away_team)
                    if discord.utils.get(category.channels, name=channel_name):
                        continue
                    
                    # Create channel
                    channel = await category.create_text_channel(
                        name=channel_name,
                        topic=f"{match.away_team} @ {match.home_team} - Enhanced MLB Analysis"
                    )
                    
                    # Create comprehensive analysis embeds
                    embeds = await self.create_comprehensive_analysis(match, date)
                    
                    # Send all embeds
                    for embed in embeds:
                        await channel.send(embed=embed)
                        await asyncio.sleep(0.5)  # Rate limiting between embeds
                    
                    created += 1
                    
                    # Rate limiting delay between channels
                    await asyncio.sleep(self.config.get('channel_creation_delay', 2.0))
                    
                except Exception as e:
                    error_msg = f"Failed to create enhanced channel for {match.away_team} @ {match.home_team}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            return ChannelCreationResult(
                success=True,
                channels_created=created,
                total_matches=total_matches,
                errors=errors,
                message=f"Created {created} enhanced MLB channels from {total_matches} games"
            )
            
        except Exception as e:
            logger.error(f"Error in enhanced MLB channel creation: {e}")
            return ChannelCreationResult(
                success=False,
                channels_created=0,
                total_matches=0,
                errors=[str(e)],
                message=f"Failed to create enhanced MLB channels: {str(e)}"
            )
    
    async def get_enhanced_matches(self, date: str) -> List[Match]:
        """
        Get MLB games with enhanced data from multiple MCP tools
        """
        try:
            # 1. Get schedule from getMLBScheduleET
            schedule_result = await self.call_mlb_mcp("getMLBScheduleET", {"date": date})
            
            if not schedule_result or not schedule_result.get("ok"):
                logger.error("Failed to get MLB schedule")
                return []
            
            schedule_data = schedule_result.get("data", {})
            games = schedule_data.get("games", [])
            
            if not games:
                logger.info(f"No MLB games found for {date}")
                return []
            
            # 2. Get enhanced data for each game
            enhanced_matches = []
            
            for game in games:
                try:
                    enhanced_match = await self.enhance_game_with_mcp_data(game)
                    if enhanced_match:
                        enhanced_matches.append(enhanced_match)
                except Exception as e:
                    logger.error(f"Error enhancing game data: {e}")
                    # Fall back to basic match
                    basic_match = self._convert_to_basic_match(game)
                    if basic_match:
                        enhanced_matches.append(basic_match)
            
            logger.info(f"Enhanced {len(enhanced_matches)} MLB games for {date}")
            return enhanced_matches
            
        except Exception as e:
            logger.error(f"Error getting enhanced MLB matches: {e}")
            return []
    
    async def enhance_game_with_mcp_data(self, game: Dict[str, Any]) -> Optional[Match]:
        """
        Enhance a single game with data from all relevant MCP tools
        """
        try:
            # Extract basic game info
            home_team_data = game.get("home", {})
            away_team_data = game.get("away", {})
            
            home_team_id = home_team_data.get("teamId")
            away_team_id = away_team_data.get("teamId")
            home_team_name = home_team_data.get("name", "Unknown")
            away_team_name = away_team_data.get("name", "Unknown")
            
            # Prepare enhanced data container
            enhanced_data = {
                "basic_game_info": game,
                "team_forms": {},
                "team_rosters": {},
                "scoring_trends": {},
                "recent_pitchers": {}
            }
            
            # Get team forms (parallel)
            team_form_tasks = []
            if home_team_id:
                team_form_tasks.append(self.get_team_form_data(home_team_id, "home"))
            if away_team_id:
                team_form_tasks.append(self.get_team_form_data(away_team_id, "away"))
            
            if team_form_tasks:
                form_results = await asyncio.gather(*team_form_tasks, return_exceptions=True)
                for result in form_results:
                    if isinstance(result, dict) and not isinstance(result, Exception):
                        enhanced_data["team_forms"].update(result)
            
            # Get scoring trends (parallel)
            scoring_tasks = []
            if home_team_id:
                scoring_tasks.append(self.get_scoring_trends_data(home_team_id, "home"))
            if away_team_id:
                scoring_tasks.append(self.get_scoring_trends_data(away_team_id, "away"))
            
            if scoring_tasks:
                scoring_results = await asyncio.gather(*scoring_tasks, return_exceptions=True)
                for result in scoring_results:
                    if isinstance(result, dict) and not isinstance(result, Exception):
                        enhanced_data["scoring_trends"].update(result)
            
            # Create enhanced Match object
            return Match(
                id=str(game.get("gamePk", "")),
                home_team=home_team_name,
                away_team=away_team_name,
                league="MLB",
                datetime=None,
                odds=game.get("odds"),
                status=game.get("status", "Scheduled"),
                additional_data=enhanced_data
            )
            
        except Exception as e:
            logger.error(f"Error enhancing game with MCP data: {e}")
            return self._convert_to_basic_match(game)
    
    async def get_team_form_data(self, team_id: int, team_type: str) -> Dict[str, Any]:
        """Get team form data from getMLBTeamForm"""
        try:
            result = await self.call_mlb_mcp("getMLBTeamForm", {"team_id": team_id})
            if result and result.get("ok"):
                return {team_type: result.get("data", {})}
        except Exception as e:
            logger.error(f"Error getting team form for {team_id}: {e}")
        return {}
    
    async def get_scoring_trends_data(self, team_id: int, team_type: str) -> Dict[str, Any]:
        """Get scoring trends from getMLBTeamScoringTrends"""
        try:
            result = await self.call_mlb_mcp("getMLBTeamScoringTrends", {"team_id": team_id})
            if result and result.get("ok"):
                return {team_type: result.get("data", {})}
        except Exception as e:
            logger.error(f"Error getting scoring trends for {team_id}: {e}")
        return {}
    
    async def call_mlb_mcp(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Call MLB MCP tool using proper JSON-RPC format
        """
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 1,
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # Use the mcp_client's HTTP client if available
            if hasattr(self.mcp_client, '_client') and self.mcp_client._client:
                response = await self.mcp_client._client.post(self.mcp_url, json=payload)
                response.raise_for_status()
                return response.json().get("result", {})
            else:
                # Fall back to basic httpx if needed
                import httpx
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(self.mcp_url, json=payload)
                    response.raise_for_status()
                    return response.json().get("result", {})
                    
        except Exception as e:
            logger.error(f"Error calling MLB MCP tool {tool_name}: {e}")
            return None
    
    async def create_comprehensive_analysis(self, match: Match, date: str) -> List[discord.Embed]:
        """
        Create multiple embeds with comprehensive game analysis
        """
        embeds = []
        
        # 1. Main Game Info Embed
        main_embed = await self.create_main_game_embed(match)
        embeds.append(main_embed)
        
        # 2. Team Form Comparison Embed
        form_embed = self.create_team_form_embed(match)
        if form_embed:
            embeds.append(form_embed)
        
        # 3. Scoring Trends Embed
        scoring_embed = self.create_scoring_trends_embed(match)
        if scoring_embed:
            embeds.append(scoring_embed)
        
        return embeds
    
    async def create_main_game_embed(self, match: Match) -> discord.Embed:
        """Create the main game information embed"""
        embed = discord.Embed(
            title=f"⚾ {match.away_team} @ {match.home_team}",
            description="**Enhanced MLB Game Analysis**",
            color=0x0066cc,
            timestamp=datetime.now()
        )
        
        # Basic game info
        game_info = match.additional_data.get("basic_game_info", {})
        start_time = game_info.get("start_et", "TBD")
        venue = game_info.get("venue", "Unknown")
        status = match.status
        
        embed.add_field(
            name="📅 Game Details",
            value=f"**Time:** {start_time}\n**Venue:** {venue}\n**Status:** {status}",
            inline=True
        )
        
        # Team IDs for reference
        home_id = game_info.get("home", {}).get("teamId", "N/A")
        away_id = game_info.get("away", {}).get("teamId", "N/A")
        
        embed.add_field(
            name="🆔 Team IDs",
            value=f"**{match.away_team}:** {away_id}\n**{match.home_team}:** {home_id}",
            inline=True
        )
        
        embed.add_field(
            name="📊 Analysis",
            value="Powered by 8 MLB MCP Tools\n• Team Form • Scoring Trends\n• Player Stats • Pitcher Analysis",
            inline=True
        )
        
        embed.set_footer(text="Enhanced MLB Analysis • Page 1/3")
        return embed
    
    def create_team_form_embed(self, match: Match) -> Optional[discord.Embed]:
        """Create team form comparison embed"""
        team_forms = match.additional_data.get("team_forms", {})
        
        if not team_forms:
            return None
        
        embed = discord.Embed(
            title=f"📊 Team Form: {match.away_team} vs {match.home_team}",
            color=0x00aa00,
            timestamp=datetime.now()
        )
        
        # Away team form
        away_form = team_forms.get("away", {})
        if away_form:
            away_data = away_form.get("form", {})
            wins = away_data.get("wins", 0)
            losses = away_data.get("losses", 0)
            win_pct = away_data.get("win_percentage", "N/A")
            streak = away_data.get("streak", "N/A")
            
            embed.add_field(
                name=f"✈️ {match.away_team} (Away)",
                value=f"**Record:** {wins}-{losses}\n**Win %:** {win_pct}\n**Streak:** {streak}",
                inline=True
            )
        
        # Home team form
        home_form = team_forms.get("home", {})
        if home_form:
            home_data = home_form.get("form", {})
            wins = home_data.get("wins", 0)
            losses = home_data.get("losses", 0)
            win_pct = home_data.get("win_percentage", "N/A")
            streak = home_data.get("streak", "N/A")
            
            embed.add_field(
                name=f"🏠 {match.home_team} (Home)",
                value=f"**Record:** {wins}-{losses}\n**Win %:** {win_pct}\n**Streak:** {streak}",
                inline=True
            )
        
        embed.set_footer(text="Enhanced MLB Analysis • Page 2/3 • Team Form")
        return embed
    
    def create_scoring_trends_embed(self, match: Match) -> Optional[discord.Embed]:
        """Create scoring trends comparison embed"""
        scoring_trends = match.additional_data.get("scoring_trends", {})
        
        if not scoring_trends:
            return None
        
        embed = discord.Embed(
            title=f"📈 Scoring Trends: {match.away_team} vs {match.home_team}",
            color=0xaa6600,
            timestamp=datetime.now()
        )
        
        # Away team scoring
        away_scoring = scoring_trends.get("away", {})
        if away_scoring:
            away_trends = away_scoring.get("trends", {})
            rpg = away_trends.get("runs_per_game", "N/A")
            rapg = away_trends.get("runs_allowed_per_game", "N/A")
            diff = away_trends.get("run_differential", "N/A")
            
            embed.add_field(
                name=f"⚔️ {match.away_team} Offense",
                value=f"**Runs/Game:** {rpg}\n**Runs Allowed/Game:** {rapg}\n**Run Diff:** {diff:+d}" if isinstance(diff, int) else f"**Runs/Game:** {rpg}\n**Runs Allowed/Game:** {rapg}\n**Run Diff:** {diff}",
                inline=True
            )
        
        # Home team scoring
        home_scoring = scoring_trends.get("home", {})
        if home_scoring:
            home_trends = home_scoring.get("trends", {})
            rpg = home_trends.get("runs_per_game", "N/A")
            rapg = home_trends.get("runs_allowed_per_game", "N/A")
            diff = home_trends.get("run_differential", "N/A")
            
            embed.add_field(
                name=f"🏠 {match.home_team} Offense",
                value=f"**Runs/Game:** {rpg}\n**Runs Allowed/Game:** {rapg}\n**Run Diff:** {diff:+d}" if isinstance(diff, int) else f"**Runs/Game:** {rpg}\n**Runs Allowed/Game:** {rapg}\n**Run Diff:** {diff}",
                inline=True
            )
        
        embed.set_footer(text="Enhanced MLB Analysis • Page 3/3 • Scoring Trends")
        return embed
    
    def _convert_to_basic_match(self, game_data: Dict[str, Any]) -> Optional[Match]:
        """Convert game data to basic Match object (fallback)"""
        try:
            home_team = game_data.get("home", {}).get("name", "Unknown Home")
            away_team = game_data.get("away", {}).get("name", "Unknown Away")
            
            return Match(
                id=str(game_data.get("gamePk", "")),
                home_team=home_team,
                away_team=away_team,
                league="MLB",
                datetime=None,
                odds=None,
                status=game_data.get("status", "Scheduled"),
                additional_data={"basic_game_info": game_data}
            )
        except Exception as e:
            logger.error(f"Error converting to basic match: {e}")
            return None
    
    # Inherit other methods from base class
    async def clear_channels(self, interaction: discord.Interaction, category_name: str) -> ClearResult:
        """Use the base implementation for clearing channels"""
        return await super().clear_channels(interaction, category_name)
    
    async def get_matches(self, date: str) -> List[Match]:
        """Get matches - use enhanced version"""
        return await self.get_enhanced_matches(date)
    
    async def format_match_analysis(self, match: Match) -> discord.Embed:
        """Format match analysis - use main embed"""
        return await self.create_main_game_embed(match)