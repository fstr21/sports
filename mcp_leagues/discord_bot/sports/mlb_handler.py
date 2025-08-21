"""
MLB-specific handler implementing the BaseSportHandler interface
"""
import asyncio
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import discord

from core.base_sport_handler import BaseSportHandler, Match, ChannelCreationResult, ClearResult


logger = logging.getLogger(__name__)


class MLBHandler(BaseSportHandler):
    """
    MLB-specific implementation of BaseSportHandler
    Handles MLB game data, channel creation, and analysis
    """
    
    def __init__(self, sport_name: str, config: Dict[str, Any], mcp_client):
        """Initialize MLB handler with MLB-specific configuration"""
        super().__init__(sport_name, config, mcp_client)
        
    async def create_channels(self, interaction: discord.Interaction, date: str) -> ChannelCreationResult:
        """
        Create MLB channels with game analysis
        
        Args:
            interaction: Discord interaction object
            date: Date string in YYYY-MM-DD format
            
        Returns:
            ChannelCreationResult with operation details
        """
        try:
            # Get matches for the date
            matches = await self.get_matches(date)
            
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
            
            # Create channels
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
                        topic=f"{match.away_team} @ {match.home_team} - MLB"
                    )
                    
                    # Create and send comprehensive match analysis
                    embeds = await self.create_comprehensive_game_analysis(match)
                    
                    # Send all embeds
                    for embed in embeds:
                        await channel.send(embed=embed)
                        await asyncio.sleep(0.5)  # Rate limit between embeds
                    
                    created += 1
                    
                    # Rate limiting delay
                    await asyncio.sleep(self.config.get('channel_creation_delay', 1.0))
                    
                except Exception as e:
                    error_msg = f"Failed to create channel for {match.away_team} @ {match.home_team}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            return ChannelCreationResult(
                success=True,
                channels_created=created,
                total_matches=total_matches,
                errors=errors,
                message=f"Created {created} MLB channels from {total_matches} games"
            )
            
        except Exception as e:
            logger.error(f"Error in MLB channel creation: {e}")
            return ChannelCreationResult(
                success=False,
                channels_created=0,
                total_matches=0,
                errors=[str(e)],
                message=f"Failed to create MLB channels: {str(e)}"
            )
    
    async def clear_channels(self, interaction: discord.Interaction, category_name: str) -> ClearResult:
        """
        Clear all channels from the MLB category
        
        Args:
            interaction: Discord interaction object
            category_name: Name of category to clear
            
        Returns:
            ClearResult with operation details
        """
        try:
            # Get category
            category = self.get_category(interaction.guild)
            if not category:
                return ClearResult(
                    success=False,
                    channels_deleted=0,
                    total_channels=0,
                    errors=[f"Category {category_name} not found"],
                    message=f"MLB category {category_name} not found"
                )
            
            # Get channels to delete
            channels_to_delete = [ch for ch in category.channels if isinstance(ch, discord.TextChannel)]
            total_channels = len(channels_to_delete)
            
            if total_channels == 0:
                return ClearResult(
                    success=True,
                    channels_deleted=0,
                    total_channels=0,
                    errors=[],
                    message="No MLB channels found to delete"
                )
            
            # Delete channels
            deleted_count = 0
            errors = []
            
            for channel in channels_to_delete:
                try:
                    await channel.delete()
                    deleted_count += 1
                    await asyncio.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    error_msg = f"Failed to delete {channel.name}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            return ClearResult(
                success=deleted_count > 0,
                channels_deleted=deleted_count,
                total_channels=total_channels,
                errors=errors,
                message=f"Deleted {deleted_count} out of {total_channels} MLB channels"
            )
            
        except Exception as e:
            logger.error(f"Error clearing MLB channels: {e}")
            return ClearResult(
                success=False,
                channels_deleted=0,
                total_channels=0,
                errors=[str(e)],
                message=f"Failed to clear MLB channels: {str(e)}"
            )
    
    async def get_matches(self, date: str) -> List[Match]:
        """
        Fetch MLB games for the specified date from MCP service
        
        Args:
            date: Date string in YYYY-MM-DD format
            
        Returns:
            List of Match objects
        """
        try:
            # MLB uses YYYY-MM-DD format directly
            mcp_date = date
            
            # Call MLB MCP using correct tool name
            response = await self.mcp_client.call_mcp(
                self.config['mcp_url'],
                "getMLBScheduleET",  # Correct MLB MCP tool name
                {"date": mcp_date}
            )
            
            if not response.success:
                logger.error(f"MLB MCP error: {response.error}")
                return []
            
            # Parse MCP response
            # MCPClient.data contains the "result" from JSON-RPC
            # getMLBScheduleET structure: result.data.games
            if not response.data:
                logger.info(f"No MLB response data for {date}")
                return []
            
            # Check if the MCP call was successful
            if not response.data.get("ok"):
                error_msg = response.data.get("error", "Unknown MLB MCP error")
                logger.error(f"MLB MCP returned error: {error_msg}")
                return []
            
            # Extract games from: response.data.data.games
            mcp_data = response.data.get("data", {})
            games_data = mcp_data.get("games", [])
            
            logger.info(f"MLB MCP returned {len(games_data)} games for {date}")
            
            if not games_data:
                logger.info(f"No MLB games found for {date}")
                return []
            
            # Convert to Match objects
            matches = []
            
            if isinstance(games_data, list):
                for i, game_data in enumerate(games_data):
                    logger.debug(f"Processing game {i+1}: {game_data.get('matchup', 'Unknown matchup')}")
                    match = self._convert_to_match_object(game_data)
                    if match:
                        matches.append(match)
                        logger.debug(f"Successfully converted: {match.away_team} @ {match.home_team}")
                    else:
                        logger.warning(f"Failed to convert game data: {game_data}")
            elif isinstance(games_data, dict):
                # Handle nested structure (e.g., games by date)
                for key, value in games_data.items():
                    if isinstance(value, list):
                        for game_data in value:
                            match = self._convert_to_match_object(game_data)
                            if match:
                                matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error fetching MLB games: {e}")
            return []
    
    async def format_match_analysis(self, match: Match) -> discord.Embed:
        """
        Create formatted Discord embed for MLB game analysis
        
        Args:
            match: Match object with data to format
            
        Returns:
            Discord embed with formatted match analysis
        """
        embed = discord.Embed(
            title=f"⚾ {match.away_team} @ {match.home_team}",
            description="**MLB Game Analysis**",
            color=self.config.get('embed_color', 0x0066cc),
            timestamp=datetime.now()
        )
        
        # Basic game info
        game_time = match.additional_data.get('time', match.additional_data.get('start_time', 'TBD'))
        embed.add_field(
            name="📅 Game Info",
            value=f"**Time:** {game_time}\\n**League:** MLB",
            inline=True
        )
        
        # Add team records if available
        home_record = match.additional_data.get('home_record')
        away_record = match.additional_data.get('away_record')
        
        if home_record or away_record:
            records_text = ""
            if away_record:
                records_text += f"**{match.away_team}:** {away_record}\\n"
            if home_record:
                records_text += f"**{match.home_team}:** {home_record}"
            
            embed.add_field(
                name="📊 Team Records",
                value=records_text,
                inline=True
            )
        
        # Add pitching matchup if available
        home_pitcher = match.additional_data.get('home_pitcher')
        away_pitcher = match.additional_data.get('away_pitcher')
        
        if home_pitcher or away_pitcher:
            pitching_text = ""
            if away_pitcher:
                pitching_text += f"**{match.away_team}:** {away_pitcher}\\n"
            if home_pitcher:
                pitching_text += f"**{match.home_team}:** {home_pitcher}"
            
            embed.add_field(
                name="🥎 Pitching Matchup",
                value=pitching_text,
                inline=False
            )
        
        # Add betting odds if available
        if match.odds:
            self._add_betting_odds_to_embed(embed, match.odds, match.home_team, match.away_team)
        
        # Add game status
        if match.status and match.status != "scheduled":
            embed.add_field(
                name="🎮 Status",
                value=match.status.title(),
                inline=True
            )
        
        embed.set_footer(text="MLB Analysis powered by MLB MCP")
        return embed
    
    async def create_comprehensive_game_analysis(self, match: Match) -> List[discord.Embed]:
        """
        Create comprehensive analysis using additional MLB MCP tools
        Uses: getMLBTeamForm, getMLBTeamScoringTrends for both teams
        """
        embeds = []
        
        # 1. Main Game Embed (existing)
        main_embed = await self.format_match_analysis(match)
        embeds.append(main_embed)
        
        # Extract team IDs from match data
        home_team_id = match.additional_data.get("home_team_id")
        away_team_id = match.additional_data.get("away_team_id")
        
        if home_team_id and away_team_id:
            logger.info(f"Creating enhanced analysis for {match.away_team} @ {match.home_team} (teams: {away_team_id} @ {home_team_id})")
            
            # 2. Team Form Analysis Embed
            form_embed = await self.create_team_form_embed(match, home_team_id, away_team_id)
            if form_embed:
                embeds.append(form_embed)
                logger.info(f"Added team form embed for {match.away_team} @ {match.home_team}")
            else:
                logger.warning(f"Failed to create team form embed for {match.away_team} @ {match.home_team}")
            
            # 3. Scoring Trends Analysis Embed  
            scoring_embed = await self.create_scoring_trends_embed(match, home_team_id, away_team_id)
            if scoring_embed:
                embeds.append(scoring_embed)
                logger.info(f"Added scoring trends embed for {match.away_team} @ {match.home_team}")
            else:
                logger.warning(f"Failed to create scoring trends embed for {match.away_team} @ {match.home_team}")
        else:
            logger.warning(f"Missing team IDs for {match.away_team} @ {match.home_team}: home={home_team_id}, away={away_team_id}")
        
        logger.info(f"Generated {len(embeds)} embeds for {match.away_team} @ {match.home_team}")
        return embeds
    
    async def create_team_form_embed(self, match: Match, home_team_id: int, away_team_id: int) -> Optional[discord.Embed]:
        """Create team form comparison using getMLBTeamForm"""
        try:
            # Get team forms in parallel
            home_form_task = self.call_mlb_mcp_tool("getMLBTeamForm", {"team_id": home_team_id})
            away_form_task = self.call_mlb_mcp_tool("getMLBTeamForm", {"team_id": away_team_id})
            
            home_form_result, away_form_result = await asyncio.gather(
                home_form_task, away_form_task, return_exceptions=True
            )
            
            # Create form embed
            embed = discord.Embed(
                title=f"📊 Team Form: {match.away_team} vs {match.home_team}",
                color=0x00aa00,
                timestamp=datetime.now()
            )
            
            # Away team form
            if not isinstance(away_form_result, Exception) and away_form_result:
                logger.debug(f"Away team form result: {away_form_result}")
                # Data is already parsed, no need for double nesting
                away_data = away_form_result.get("form", {}) if "form" in away_form_result else away_form_result
                wins = away_data.get("wins", 0)
                losses = away_data.get("losses", 0)
                win_pct = away_data.get("win_percentage", "N/A")
                streak = away_data.get("streak", "N/A")
                games_back = away_data.get("games_back", "N/A")
                
                embed.add_field(
                    name=f"✈️ {match.away_team} (Away)",
                    value=f"**Record:** {wins}-{losses}\n**Win %:** {win_pct}\n**Streak:** {streak}\n**GB:** {games_back}",
                    inline=True
                )
            
            # Home team form
            if not isinstance(home_form_result, Exception) and home_form_result:
                logger.debug(f"Home team form result: {home_form_result}")
                # Data is already parsed, no need for double nesting
                home_data = home_form_result.get("form", {}) if "form" in home_form_result else home_form_result
                wins = home_data.get("wins", 0)
                losses = home_data.get("losses", 0)
                win_pct = home_data.get("win_percentage", "N/A")
                streak = home_data.get("streak", "N/A")
                games_back = home_data.get("games_back", "N/A")
                
                embed.add_field(
                    name=f"🏠 {match.home_team} (Home)",
                    value=f"**Record:** {wins}-{losses}\n**Win %:** {win_pct}\n**Streak:** {streak}\n**GB:** {games_back}",
                    inline=True
                )
            
            # Add matchup analysis
            embed.add_field(
                name="⚖️ Matchup Notes",
                value="Form data from current season standings\nStreaks: W=Win, L=Loss\nGB=Games Back from division lead",
                inline=False
            )
            
            embed.set_footer(text="Team Form Analysis • Powered by getMLBTeamForm")
            return embed
            
        except Exception as e:
            logger.error(f"Error creating team form embed: {e}")
            return None
    
    async def create_scoring_trends_embed(self, match: Match, home_team_id: int, away_team_id: int) -> Optional[discord.Embed]:
        """Create scoring trends comparison using getMLBTeamScoringTrends"""
        try:
            # Get scoring trends in parallel
            home_trends_task = self.call_mlb_mcp_tool("getMLBTeamScoringTrends", {"team_id": home_team_id})
            away_trends_task = self.call_mlb_mcp_tool("getMLBTeamScoringTrends", {"team_id": away_team_id})
            
            home_trends_result, away_trends_result = await asyncio.gather(
                home_trends_task, away_trends_task, return_exceptions=True
            )
            
            # Create scoring embed
            embed = discord.Embed(
                title=f"📈 Scoring Trends: {match.away_team} vs {match.home_team}",
                color=0xaa6600,
                timestamp=datetime.now()
            )
            
            # Away team scoring
            if not isinstance(away_trends_result, Exception) and away_trends_result:
                logger.debug(f"Away team trends result: {away_trends_result}")
                # Data is already parsed, no need for double nesting
                away_trends = away_trends_result.get("trends", {}) if "trends" in away_trends_result else away_trends_result
                rpg = away_trends.get("runs_per_game", 0)
                rapg = away_trends.get("runs_allowed_per_game", 0)
                diff = away_trends.get("run_differential", 0)
                games_played = away_trends.get("games_played", 0)
                
                embed.add_field(
                    name=f"⚔️ {match.away_team} Offense",
                    value=f"**Runs/Game:** {rpg:.1f}\n**Allowed/Game:** {rapg:.1f}\n**Run Diff:** {diff:+d}\n**Games:** {games_played}",
                    inline=True
                )
            
            # Home team scoring
            if not isinstance(home_trends_result, Exception) and home_trends_result:
                logger.debug(f"Home team trends result: {home_trends_result}")
                # Data is already parsed, no need for double nesting
                home_trends = home_trends_result.get("trends", {}) if "trends" in home_trends_result else home_trends_result
                rpg = home_trends.get("runs_per_game", 0)
                rapg = home_trends.get("runs_allowed_per_game", 0)
                diff = home_trends.get("run_differential", 0)
                games_played = home_trends.get("games_played", 0)
                
                embed.add_field(
                    name=f"🏠 {match.home_team} Offense",
                    value=f"**Runs/Game:** {rpg:.1f}\n**Allowed/Game:** {rapg:.1f}\n**Run Diff:** {diff:+d}\n**Games:** {games_played}",
                    inline=True
                )
            
            # Add analysis
            embed.add_field(
                name="💡 Scoring Analysis",
                value="Season-long offensive and defensive averages\nRun Differential = Total Runs Scored - Total Runs Allowed\nPositive diff = Better offense than defense",
                inline=False
            )
            
            embed.set_footer(text="Scoring Trends Analysis • Powered by getMLBTeamScoringTrends")
            return embed
            
        except Exception as e:
            logger.error(f"Error creating scoring trends embed: {e}")
            return None
    
    async def call_mlb_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Helper method to call MLB MCP tools"""
        try:
            response = await self.mcp_client.call_mcp(
                self.config['mcp_url'],
                tool_name,
                arguments
            )
            
            if not response.success:
                logger.error(f"MLB MCP tool {tool_name} error: {response.error}")
                return None
            
            # Parse MCP content properly
            parsed_data = await self.mcp_client.parse_mcp_content(response)
            if not parsed_data:
                logger.error(f"MLB MCP tool {tool_name} returned no parseable data")
                return None
            
            logger.debug(f"MLB MCP tool {tool_name} returned data successfully")
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error calling MLB MCP tool {tool_name}: {e}")
            return None
    
    def _convert_to_match_object(self, game_data: Dict[str, Any]) -> Optional[Match]:
        """Convert getMLBScheduleET game data to Match object"""
        try:
            # Handle getMLBScheduleET data structure
            # Structure: game has home_team{name, id} and away_team{name, id}
            home_team_data = game_data.get("home_team", {})
            away_team_data = game_data.get("away_team", {})
            
            # Also try the nested structure from raw MCP response
            if not home_team_data:
                home_team_data = game_data.get("home", {})
            if not away_team_data:
                away_team_data = game_data.get("away", {})
            
            home_team = home_team_data.get("name", "Unknown Home")
            away_team = away_team_data.get("name", "Unknown Away")
            
            # Extract start time from nested structure
            start_time_data = game_data.get("start_time", {})
            if isinstance(start_time_data, dict):
                game_time = start_time_data.get("formatted", start_time_data.get("raw", "TBD"))
            else:
                game_time = game_data.get("start_et", str(start_time_data) if start_time_data else "TBD")
            
            # Extract status
            status_data = game_data.get("status", {})
            if isinstance(status_data, dict):
                status = status_data.get("raw", "Scheduled")
            else:
                status = str(status_data) if status_data else "Scheduled"
            
            return Match(
                id=str(game_data.get("game_pk", game_data.get("gamePk", game_data.get("id", "")))),
                home_team=home_team,
                away_team=away_team,
                league="MLB",
                datetime=None,
                odds=game_data.get("odds"),
                status=status,
                additional_data={
                    "time": game_time,
                    "venue": game_data.get("venue", "Unknown Venue"),
                    "home_team_id": home_team_data.get("id"),
                    "away_team_id": away_team_data.get("id"),
                    "matchup": game_data.get("matchup", f"{away_team} @ {home_team}"),
                    "raw_data": game_data
                }
            )
        except Exception as e:
            logger.error(f"Error converting MLB game data: {e}")
            return None
    
    def _add_betting_odds_to_embed(self, embed: discord.Embed, odds: Dict[str, Any], home_team: str, away_team: str):
        """Add betting odds section to embed"""
        betting_lines = []
        
        # Moneyline odds
        home_ml = odds.get('home_ml', odds.get('home'))
        away_ml = odds.get('away_ml', odds.get('away'))
        
        if home_ml:
            betting_lines.append(f"**{home_team}:** {home_ml}")
        if away_ml:
            betting_lines.append(f"**{away_team}:** {away_ml}")
        
        # Run line (spread)
        run_line = odds.get('run_line', odds.get('spread'))
        if run_line:
            home_spread = run_line.get('home')
            away_spread = run_line.get('away')
            if home_spread and away_spread:
                betting_lines.append(f"**Run Line:** {away_team} {away_spread}, {home_team} {home_spread}")
        
        # Over/Under (total)
        total = odds.get('total', odds.get('over_under'))
        if total:
            over = total.get('over')
            under = total.get('under')
            total_runs = total.get('total', total.get('runs'))
            if over and under and total_runs:
                betting_lines.append(f"**O/U {total_runs}:** Over {over}, Under {under}")
        
        if betting_lines:
            embed.add_field(
                name="💰 Betting Lines",
                value="\\n".join(betting_lines),
                inline=False
            )