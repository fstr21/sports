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
            
            # Parse MCP content properly
            parsed_data = await self.mcp_client.parse_mcp_content(response)
            if not parsed_data:
                logger.error(f"No parseable MLB data for {date}")
                return []
            
            # Extract games from parsed data - games are nested in data.games
            games_data = parsed_data.get("data", {}).get("games", [])
            
            logger.debug(f"Parsed data keys: {list(parsed_data.keys()) if isinstance(parsed_data, dict) else 'Not a dict'}")
            logger.debug(f"First game sample: {games_data[0] if games_data else 'No games'}")
            
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
    


    async def format_match_analysis_new(self, match: Match) -> discord.Embed:
        """
        Create Discord embed following the exact specification format.
        Uses structured fields with specific inline properties as defined.
        """
        # Get team information for enhanced context and betting odds
        home_team_id = match.additional_data.get("home_team_id")
        away_team_id = match.additional_data.get("away_team_id")
        
        # Get team form data and betting odds in parallel
        tasks = []
        if home_team_id and away_team_id:
            tasks = [
                self.call_mlb_mcp_tool("getMLBTeamFormEnhanced", {"team_id": home_team_id}),
                self.call_mlb_mcp_tool("getMLBTeamFormEnhanced", {"team_id": away_team_id}),
                self.call_mlb_mcp_tool("getMLBTeamForm", {"team_id": home_team_id}),
                self.call_mlb_mcp_tool("getMLBTeamForm", {"team_id": away_team_id}),
                self.call_mlb_mcp_tool("getMLBTeamScoringTrends", {"team_id": home_team_id}),
                self.call_mlb_mcp_tool("getMLBTeamScoringTrends", {"team_id": away_team_id}),
                self.get_betting_odds_for_game(match)
            ]
            home_form_enhanced, away_form_enhanced, home_form_basic, away_form_basic, home_trends, away_trends, betting_odds = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            home_form_enhanced = away_form_enhanced = home_form_basic = away_form_basic = home_trends = away_trends = betting_odds = None
        
        # Format game time and date
        raw_game_time = match.additional_data.get('time', match.additional_data.get('start_time', 'TBD'))
        game_time = raw_game_time
        game_date = "August 22, 2025"
        try:
            if raw_game_time != 'TBD' and 'T' in raw_game_time:
                dt = datetime.fromisoformat(raw_game_time.replace('Z', '+00:00'))
                from datetime import timezone, timedelta
                # Convert to Eastern Time (UTC-5 or UTC-4 for DST)
                eastern_tz = timezone(timedelta(hours=-5))  # EST/EDT approximation
                dt_eastern = dt.astimezone(eastern_tz)
                game_time = dt_eastern.strftime("%I:%M %p ET").lstrip('0')
                game_date = dt_eastern.strftime("%B %d, %Y")
        except Exception:
            pass

        # Extract season record data from basic form
        away_record, home_record = "0-0", "0-0"
        away_winpct, home_winpct = ".000", ".000"
        away_run_diff, home_run_diff = 0, 0
        away_ra_game, home_ra_game = 0.0, 0.0

        # Get season record from basic team form
        if not isinstance(away_form_basic, Exception) and away_form_basic:
            away_data = away_form_basic.get("data", {}).get("form", {})
            away_record = f"{away_data.get('wins', 0)}-{away_data.get('losses', 0)}"
            away_winpct = away_data.get('win_percentage', '.000')

        if not isinstance(home_form_basic, Exception) and home_form_basic:
            home_data = home_form_basic.get("data", {}).get("form", {})
            home_record = f"{home_data.get('wins', 0)}-{home_data.get('losses', 0)}"
            home_winpct = home_data.get('win_percentage', '.000')

        # Get scoring trends
        if not isinstance(away_trends, Exception) and away_trends:
            away_trends_data = away_trends.get("data", {}).get("trends", {})
            away_run_diff = away_trends_data.get("run_differential", 0)
            away_ra_game = away_trends_data.get("runs_allowed_per_game", 0.0)

        if not isinstance(home_trends, Exception) and home_trends:
            home_trends_data = home_trends.get("data", {}).get("trends", {})
            home_run_diff = home_trends_data.get("run_differential", 0)
            home_ra_game = home_trends_data.get("runs_allowed_per_game", 0.0)

        # Get recent form from enhanced data
        away_last10, home_last10 = "N/A", "N/A"
        if not isinstance(away_form_enhanced, Exception) and away_form_enhanced:
            away_enhanced = away_form_enhanced.get("data", {}).get("enhanced_records", {})
            away_last10 = away_enhanced.get("last_10", "N/A")

        if not isinstance(home_form_enhanced, Exception) and home_form_enhanced:
            home_enhanced = home_form_enhanced.get("data", {}).get("enhanced_records", {})
            home_last10 = home_enhanced.get("last_10", "N/A")

        # Extract betting odds
        away_ml, home_ml = "N/A", "N/A"
        away_rl, home_rl = "N/A", "N/A"
        total_line, over_odds, under_odds = "N/A", "N/A", "N/A"

        if not isinstance(betting_odds, Exception) and betting_odds:
            if betting_odds.get("moneyline"):
                ml_parts = betting_odds["moneyline"].split(' | ')
                if len(ml_parts) == 2:
                    home_ml = ml_parts[0].replace(match.home_team, "").strip()
                    away_ml = ml_parts[1].replace(match.away_team, "").strip()

            if betting_odds.get("spread"):
                sp_parts = betting_odds["spread"].split(' | ')
                if len(sp_parts) == 2:
                    home_rl = sp_parts[0].replace(match.home_team, "").strip()
                    away_rl = sp_parts[1].replace(match.away_team, "").strip()

            total_raw = betting_odds.get("total", "")
            # Parse total line and odds
            if "Over" in total_raw and "Under" in total_raw:
                parts = total_raw.split(",")
                if len(parts) >= 2:
                    over_part = parts[0].strip()
                    under_part = parts[1].strip()
                    
                    # Extract over line and odds
                    if "Over" in over_part and "(" in over_part:
                        over_split = over_part.split("(")
                        total_line = over_split[0].replace("Over", "").strip()
                        over_odds = "(" + over_split[1] if len(over_split) > 1 else "N/A"
                    
                    # Extract under odds
                    if "(" in under_part:
                        under_odds = under_part.split("(")[1].replace(")", "") if "(" in under_part else "N/A"

        # Generate analysis following the specification
        analysis = self.generate_matchup_analysis(
            match.away_team, match.home_team,
            away_last10, home_last10,
            away_ra_game, home_ra_game,
            away_run_diff, home_run_diff
        )

        # Create embed following exact specification
        venue = match.additional_data.get('venue', 'TBD')
        
        embed = discord.Embed(
            title=f"{match.away_team} @ {match.home_team}",
            description=f"📅 {game_date} | ⏰ {game_time} | 🏟️ {venue}",
            color=self.config.get('embed_color', 0x0066cc),
            timestamp=datetime.now()
        )

        # Add fields following refined specification with emojis and symmetrical betting grid
        # Header for Betting Lines with emoji
        embed.add_field(name="\u200B", value="**__💰 Betting Lines__**", inline=False)
        
        # Symmetrical betting grid (2x3 layout)
        embed.add_field(name="Moneyline", value=f"{match.away_team}: `{away_ml}`\n{match.home_team}: `{home_ml}`", inline=True)
        embed.add_field(name="Run Line", value=f"{match.away_team}: `{away_rl}`\n{match.home_team}: `{home_rl}`", inline=True)
        over_field_name = f"Over {total_line}" if total_line != "N/A" else "Over"
        under_field_name = f"Under {total_line}" if total_line != "N/A" else "Under"
        embed.add_field(name=over_field_name, value=f"`{over_odds}`", inline=True)
        embed.add_field(name=under_field_name, value=f"`{under_odds}`", inline=True)
        
        # Clean separator and header for Tale of the Tape with emoji
        embed.add_field(name="\u200B", value="**__📊 Tale of the Tape__**", inline=False)
        
        # Team stats with merged L10 form
        embed.add_field(
            name=match.away_team, 
            value=f"Record: `{away_record} ({away_winpct})`\nRun Diff: `{away_run_diff:+d}`\nAllowed/Game: `{away_ra_game:.2f}`\nL10 Form: `{away_last10}`", 
            inline=True
        )
        embed.add_field(
            name=match.home_team, 
            value=f"Record: `{home_record} ({home_winpct})`\nRun Diff: `{home_run_diff:+d}`\nAllowed/Game: `{home_ra_game:.2f}`\nL10 Form: `{home_last10}`", 
            inline=True
        )
        
        # Analysis section with clean separator and emoji
        embed.add_field(name="\u200B", value=f"**__💡 Analysis & Recommendation__**\n{analysis}", inline=False)
        
        embed.set_footer(text="MLB Analysis powered by MLB MCP")
        return embed

    def generate_matchup_analysis(self, away_team: str, home_team: str, away_l10: str, home_l10: str, 
                                away_ra_game: float, home_ra_game: float, away_run_diff: int, home_run_diff: int) -> str:
        """Generate impartial, data-driven analysis following specification rules"""
        
        # Parse recent form records
        away_wins = away_losses = home_wins = home_losses = 0
        try:
            if "-" in away_l10:
                away_wins, away_losses = map(int, away_l10.split("-"))
            if "-" in home_l10:
                home_wins, home_losses = map(int, home_l10.split("-"))
        except:
            pass
        
        # Identify recent form advantage with contrasting elements
        recent_advantage = ""
        if away_wins > home_wins:
            recent_advantage = f"The {away_team} are hot ({away_l10} in their last 10)"
            if home_wins <= 3:
                recent_advantage += f", contrasting sharply with the {home_team}' recent struggles ({home_l10})"
        elif home_wins > away_wins:
            recent_advantage = f"The {home_team} are hot ({home_l10} in their last 10)"
            if away_wins <= 3:
                recent_advantage += f", contrasting sharply with the {away_team}' recent struggles ({away_l10})"
        else:
            recent_advantage = f"Both teams have similar recent form ({away_l10} vs {home_l10})"
        
        # Find the key statistical mismatch
        defense_diff = abs(away_ra_game - home_ra_game)
        run_diff_gap = abs(away_run_diff - home_run_diff)
        
        key_factor = ""
        if defense_diff > 1.0:  # Significant defensive difference
            better_defense = away_team if away_ra_game < home_ra_game else home_team
            key_factor = f"However, {better_defense}'s superior defense (allowing {defense_diff:.1f} fewer runs per game) is the key differentiator. This significant defensive gap is the primary factor to consider beyond the teams' recent forms."
        elif run_diff_gap > 30:  # Significant run differential gap
            better_diff_team = away_team if away_run_diff > home_run_diff else home_team
            key_factor = f"The season-long run differential heavily favors {better_diff_team} ({max(away_run_diff, home_run_diff):+d} vs {min(away_run_diff, home_run_diff):+d}), making overall team quality more significant than recent momentum."
        else:
            key_factor = "Both teams show similar underlying metrics, making recent form and situational factors the primary considerations for this matchup."
        
        return f"{recent_advantage}. {key_factor}"

    async def format_match_analysis(self, match: Match) -> discord.Embed:
        """
        Create comprehensive embed matching the clean format from your screenshot.
        Combines betting lines, team comparison, and scoring analysis into one embed.
        
        Args:
            match: Match object with data to format
            
        Returns:
            Discord embed with comprehensive game analysis
        """
        # Get team information for enhanced context and betting odds
        home_team_id = match.additional_data.get("home_team_id")
        away_team_id = match.additional_data.get("away_team_id")
        
        # Get team form data and betting odds in parallel
        tasks = []
        if home_team_id and away_team_id:
            tasks = [
                self.call_mlb_mcp_tool("getMLBTeamFormEnhanced", {"team_id": home_team_id}),
                self.call_mlb_mcp_tool("getMLBTeamFormEnhanced", {"team_id": away_team_id}),
                self.call_mlb_mcp_tool("getMLBTeamForm", {"team_id": home_team_id}),
                self.call_mlb_mcp_tool("getMLBTeamForm", {"team_id": away_team_id}),
                self.call_mlb_mcp_tool("getMLBTeamScoringTrends", {"team_id": home_team_id}),
                self.call_mlb_mcp_tool("getMLBTeamScoringTrends", {"team_id": away_team_id}),
                self.get_betting_odds_for_game(match)
            ]
            home_form_enhanced, away_form_enhanced, home_form_basic, away_form_basic, home_trends, away_trends, betting_odds = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            home_form_enhanced = away_form_enhanced = home_form_basic = away_form_basic = home_trends = away_trends = betting_odds = None
        
        # Format game time and date
        raw_game_time = match.additional_data.get('time', match.additional_data.get('start_time', 'TBD'))
        game_time = raw_game_time
        game_date = "August 21, 2025"  # You can make this dynamic
        try:
            if raw_game_time != 'TBD' and 'T' in raw_game_time:
                dt = datetime.fromisoformat(raw_game_time.replace('Z', '+00:00'))
                from datetime import timezone, timedelta
                # Convert to Eastern Time (UTC-5 or UTC-4 for DST)
                eastern_tz = timezone(timedelta(hours=-5))  # EST/EDT approximation
                dt_eastern = dt.astimezone(eastern_tz)
                game_time = dt_eastern.strftime("%I:%M %p ET").lstrip('0')
                game_date = dt_eastern.strftime("%B %d, %Y")
        except Exception:
            pass

        # Extract season record data from basic form
        away_record, home_record = "0-0", "0-0"
        away_winpct, home_winpct = ".000", ".000"
        away_streak, home_streak = "N/A", "N/A"
        away_gb, home_gb = "-", "-"
        away_rpg, home_rpg = 4.4, 4.4
        away_rapg, home_rapg = 4.6, 4.2
        away_diff, home_diff = 0, 0

        # Get season record from basic team form
        if not isinstance(away_form_basic, Exception) and away_form_basic:
            away_data = away_form_basic.get("data", {}).get("form", {})
            away_record = f"{away_data.get('wins', 0)}-{away_data.get('losses', 0)}"
            away_winpct = away_data.get('win_percentage', '.000')
            away_gb = str(away_data.get("games_back", "-"))

        if not isinstance(home_form_basic, Exception) and home_form_basic:
            home_data = home_form_basic.get("data", {}).get("form", {})
            home_record = f"{home_data.get('wins', 0)}-{home_data.get('losses', 0)}"
            home_winpct = home_data.get('win_percentage', '.000')
            home_gb = str(home_data.get("games_back", "-"))

        # Get current streak from enhanced form
        if not isinstance(away_form_enhanced, Exception) and away_form_enhanced:
            enhanced_data = away_form_enhanced.get("data", {}).get("form", {})
            away_streak = enhanced_data.get("streak", "N/A")

        if not isinstance(home_form_enhanced, Exception) and home_form_enhanced:
            enhanced_data = home_form_enhanced.get("data", {}).get("form", {})
            home_streak = enhanced_data.get("streak", "N/A")
            
        if not isinstance(away_trends, Exception) and away_trends:
            away_trends_data = away_trends.get("data", {}).get("trends", {})
            away_rpg = away_trends_data.get("runs_per_game", 4.4)
            away_rapg = away_trends_data.get("runs_allowed_per_game", 4.6)
            away_diff = away_trends_data.get("run_differential", -26)

        if not isinstance(home_trends, Exception) and home_trends:
            home_trends_data = home_trends.get("data", {}).get("trends", {})
            home_rpg = home_trends_data.get("runs_per_game", 4.4)
            home_rapg = home_trends_data.get("runs_allowed_per_game", 4.2)
            home_diff = home_trends_data.get("run_differential", +27)

        # Create embed matching your screenshot
        embed = discord.Embed(
            title=f"⚾ {match.away_team} @ {match.home_team} ⚾",
            color=0x2F3136,  # Dark theme color
            timestamp=datetime.now()
        )

        # Game info section
        venue = match.additional_data.get('venue', 'George M. Steinbrenner Field')
        embed.add_field(name="📅 Date:", value=game_date, inline=False)
        embed.add_field(name="⏰ Time:", value=game_time, inline=False)
        embed.add_field(name="🏟️ Venue:", value=venue, inline=False)

        # Live Betting Lines section
        betting_content = "```\nOdds via BetOnline.ag\n\n"
        if not isinstance(betting_odds, Exception) and betting_odds:
            # Parse actual odds
            ml_away, ml_home = "N/A", "N/A"
            spread_away, spread_home = "N/A", "N/A"
            total_over, total_under = "N/A", "N/A"
            
            if betting_odds.get("moneyline"):
                ml_parts = betting_odds["moneyline"].split(' | ')
                if len(ml_parts) == 2:
                    ml_home = ml_parts[0].replace(match.home_team, "").strip()
                    ml_away = ml_parts[1].replace(match.away_team, "").strip()

            if betting_odds.get("spread"):
                sp_parts = betting_odds["spread"].split(' | ')
                if len(sp_parts) == 2:
                    spread_home = sp_parts[0].replace(match.home_team, "").strip()
                    spread_away = sp_parts[1].replace(match.away_team, "").strip()

            betting_content += f"| Line      | {match.away_team:<20} | {match.home_team:<20} |\n"
            betting_content += f"|-----------|{'-' * 20}|{'-' * 20}|\n"
            betting_content += f"| Moneyline | {ml_away + ' (Favorite)' if '-' in ml_away else ml_away + ' (Underdog)':<20} | {ml_home + ' (Underdog)' if '+' in ml_home else ml_home + ' (Favorite)':<20} |\n"
            betting_content += f"| Run Line  | {spread_away:<20} | {spread_home:<20} |\n"
            betting_content += f"| Total     | {total_over:<20} | {total_under:<20} |\n"
        else:
            betting_content += "Betting lines not available\n"
        betting_content += "```"
        
        embed.add_field(name="💰 Live Betting Lines", value=betting_content, inline=False)

        # Enhanced Team Comparison section with better formatting
        team_content = "```\n"
        team_content += f"| Stat          | {match.away_team:<20} | {match.home_team:<20} |\n"
        team_content += f"|---------------|{'-' * 20}|{'-' * 20}|\n"
        team_content += f"| Record        | {away_record:<20} | {home_record:<20} |\n"
        team_content += f"| Win %         | {away_winpct:<20} | {home_winpct:<20} |\n"
        team_content += f"| Current Streak| {away_streak:<20} | {home_streak:<20} |\n"
        team_content += f"| Games Back    | {away_gb:<20} | {home_gb:<20} |\n"
        team_content += "```"
        
        embed.add_field(name="📊 Team Comparison", value=team_content, inline=False)

        # Enhanced Recent Form section using real MLB data
        form_content = "```\n"
        
        # Get enhanced form data from MCP response
        away_last10 = "N/A"
        home_last10 = "N/A"
        away_home_recent = "N/A"
        away_away_recent = "N/A"
        home_home_recent = "N/A" 
        home_away_recent = "N/A"
        away_streak_emoji = ""
        home_streak_emoji = ""
        
        if not isinstance(away_form_enhanced, Exception) and away_form_enhanced:
            away_data = away_form_enhanced.get("data", {})
            enhanced = away_data.get("enhanced_records", {})
            streak_info = away_data.get("streak_info", {})
            
            away_last10 = enhanced.get("last_10", "N/A")
            away_home_recent = enhanced.get("home_recent", "N/A")
            away_away_recent = enhanced.get("away_recent", "N/A")
            away_streak_emoji = streak_info.get("emoji", "")

        if not isinstance(home_form_enhanced, Exception) and home_form_enhanced:
            home_data = home_form_enhanced.get("data", {})
            enhanced = home_data.get("enhanced_records", {})
            streak_info = home_data.get("streak_info", {})
            
            home_last10 = enhanced.get("last_10", "N/A")
            home_home_recent = enhanced.get("home_recent", "N/A")
            home_away_recent = enhanced.get("away_recent", "N/A")
            home_streak_emoji = streak_info.get("emoji", "")
        
        form_content += f"| Recent Form   | {match.away_team:<20} | {match.home_team:<20} |\n"
        form_content += f"|---------------|{'-' * 20}|{'-' * 20}|\n"
        form_content += f"| Last 10 Games | {away_last10:<20} | {home_last10:<20} |\n"
        form_content += f"| Home Recent   | {away_home_recent:<20} | {home_home_recent:<20} |\n"
        form_content += f"| Away Recent   | {away_away_recent:<20} | {home_away_recent:<20} |\n"
        form_content += f"| Streak        | {away_streak_emoji + ' ' + away_streak:<19} | {home_streak_emoji + ' ' + home_streak:<19} |\n"
        form_content += "```"
        
        embed.add_field(name="📈 Recent Form", value=form_content, inline=False)

        # Scoring Trends & Analysis section (no colors)
        scoring_content = "```\n"
        scoring_content += f"| Metric        | {match.away_team:<20} | {match.home_team:<20} |\n"
        scoring_content += f"|---------------|{'-' * 20}|{'-' * 20}|\n"
        scoring_content += f"| Runs / Game   | {away_rpg:<20} | {home_rpg:<20} |\n"
        scoring_content += f"| Allowed / Game| {away_rapg:<20} | {home_rapg:<20} |\n"
        scoring_content += f"| Run Diff      | {away_diff:<20} | {home_diff:+d}{' ' * 16} |\n"
        scoring_content += "```"
        
        embed.add_field(name="🔥 Scoring Trends & Analysis", value=scoring_content, inline=False)

        # Enhanced Analysis section matching your screenshot
        better_defense_team = match.home_team if home_rapg < away_rapg else match.away_team
        worse_defense_team = match.away_team if home_rapg < away_rapg else match.home_team
        better_diff = max(home_diff, away_diff)
        worse_diff = min(home_diff, away_diff)
        diff_swing = abs(better_diff - worse_diff)
        
        analysis_text = f"💡 **Analysis:** While their offense is nearly identical, the highlighted stats show the game's key difference: The {better_defense_team}' superior defense/pitching. This results in a massive {diff_swing}-run swing in the season-long **Run Differential**, which is the most significant statistic heading into this matchup."
        
        embed.add_field(name="", value=analysis_text, inline=False)
        
        embed.set_footer(text="MLB Analysis powered by MLB MCP • Today at 7:01 PM")
        return embed
    

    

    def _parse_moneyline(self, ml_string: str, match: Match) -> Dict[str, str]:
        """Parse moneyline string and return formatted home/away odds"""
        if not ml_string or ml_string == "N/A":
            return None
            
        try:
            # Expected format: "Cubs -138 | Brewers +118"
            parts = ml_string.split(" | ")
            if len(parts) != 2:
                return None
            
            home_part = parts[0].strip()
            away_part = parts[1].strip()
            
            # Extract team names and odds
            home_odds = away_odds = "N/A"
            
            # Parse home team odds
            if match.home_team in home_part:
                home_odds = home_part.replace(match.home_team, "").strip()
                home_team_display = f"{match.home_team} {home_odds}"
            else:
                home_team_display = home_part
            
            # Parse away team odds  
            if match.away_team in away_part:
                away_odds = away_part.replace(match.away_team, "").strip()
                away_team_display = f"{match.away_team} {away_odds}"
            else:
                away_team_display = away_part
            
            return {
                "home": home_team_display,
                "away": away_team_display
            }
        except Exception as e:
            logger.debug(f"Error parsing moneyline: {e}")
            return None
    
    def _parse_spread(self, spread_string: str, match: Match) -> Dict[str, str]:
        """Parse spread string and return formatted home/away spreads"""
        if not spread_string or spread_string == "N/A":
            return None
            
        try:
            # Expected format: "Cubs -1.5 (+162) | Brewers +1.5 (-196)"
            parts = spread_string.split(" | ")
            if len(parts) != 2:
                return None
            
            home_part = parts[0].strip()
            away_part = parts[1].strip()
            
            # Extract team names, points, and odds
            home_team_display = home_part
            away_team_display = away_part
            
            # Clean up team names if they're in the spread string
            if match.home_team in home_part:
                spread_info = home_part.replace(match.home_team, "").strip()
                home_team_display = f"{match.home_team} {spread_info}"
            
            if match.away_team in away_part:
                spread_info = away_part.replace(match.away_team, "").strip()  
                away_team_display = f"{match.away_team} {spread_info}"
            
            return {
                "home": home_team_display,
                "away": away_team_display
            }
        except Exception as e:
            logger.debug(f"Error parsing spread: {e}")
            return None
    
    async def get_betting_odds_for_game(self, match: Match) -> Dict[str, str]:
        """Get betting odds for a specific game and format them"""
        try:
            import httpx
            
            odds_url = "https://odds-mcp-v2-production.up.railway.app/mcp"
            
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 1,
                "params": {
                    "name": "getOdds",
                    "arguments": {
                        "sport": "baseball_mlb",
                        "markets": "h2h,spreads,totals",
                        "regions": "us"
                    }
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(odds_url, json=payload)
                response.raise_for_status()
                result = response.json()
                
                if "result" not in result or "data" not in result["result"]:
                    return {}
                
                odds_data = result["result"]["data"]["odds"]
                if not odds_data:
                    return {}
                
                # Find our specific game by team names
                target_game = None
                for game in odds_data:
                    away_team = game.get("away_team", "").lower()
                    home_team = game.get("home_team", "").lower()
                    
                    # Match team names (handle different name formats)
                    if (match.away_team.lower() in away_team or away_team in match.away_team.lower()) and \
                       (match.home_team.lower() in home_team or home_team in match.home_team.lower()):
                        target_game = game
                        break
                
                if not target_game or "bookmakers" not in target_game or not target_game["bookmakers"]:
                    return {}
                
                # Use first bookmaker
                bookmaker = target_game["bookmakers"][0]
                formatted_odds = {}
                
                # Process each market
                for market in bookmaker.get("markets", []):
                    market_key = market.get("key")
                    
                    if market_key == "h2h":
                        # Moneyline
                        outcomes = market.get("outcomes", [])
                        if len(outcomes) >= 2:
                            home_ml = away_ml = "N/A"
                            for outcome in outcomes:
                                name = outcome.get("name", "")
                                price = outcome.get("price")
                                if isinstance(price, int):
                                    price_str = f"{price:+d}" if price < 0 else f"+{price}"
                                else:
                                    price_str = str(price)
                                
                                if match.home_team.lower() in name.lower():
                                    home_ml = f"{match.home_team} {price_str}"
                                elif match.away_team.lower() in name.lower():
                                    away_ml = f"{match.away_team} {price_str}"
                            
                            formatted_odds["moneyline"] = f"{home_ml} | {away_ml}"
                    
                    elif market_key == "spreads":
                        # Spread (Run Line)
                        outcomes = market.get("outcomes", [])
                        if len(outcomes) >= 2:
                            home_spread = away_spread = "N/A"
                            for outcome in outcomes:
                                name = outcome.get("name", "")
                                price = outcome.get("price")
                                point = outcome.get("point", 0)
                                
                                price_str = f"({price:+d})" if isinstance(price, int) else f"({price})"
                                spread_str = f"{point:+g}"
                                
                                if match.home_team.lower() in name.lower():
                                    home_spread = f"{match.home_team} {spread_str} {price_str}"
                                elif match.away_team.lower() in name.lower():
                                    away_spread = f"{match.away_team} {spread_str} {price_str}"
                            
                            formatted_odds["spread"] = f"{home_spread} | {away_spread}"
                    
                    elif market_key == "totals":
                        # Over/Under
                        outcomes = market.get("outcomes", [])
                        if len(outcomes) >= 2:
                            over_odds = under_odds = "N/A"
                            total_points = outcomes[0].get("point", 0) if outcomes else 0
                            
                            for outcome in outcomes:
                                name = outcome.get("name", "")
                                price = outcome.get("price")
                                
                                price_str = f"({price:+d})" if isinstance(price, int) else f"({price})"
                                
                                if name.lower() == "over":
                                    over_odds = price_str
                                elif name.lower() == "under":
                                    under_odds = price_str
                            
                            formatted_odds["total"] = f"O/U {total_points} {over_odds}/{under_odds}"
                
                return formatted_odds
                
        except Exception as e:
            logger.error(f"Error getting betting odds: {e}")
            return {}
    
    async def create_comprehensive_game_analysis(self, match: Match) -> List[discord.Embed]:
        """
        Create streamlined 2-embed analysis:
        1. Comprehensive main embed (betting, team comparison, scoring trends)
        2. Player props + stats embed (with betting lines and performance data)
        """
        embeds = []
        
        # 1. New Structured Format Embed (follows exact specification)
        structured_embed = await self.format_match_analysis_new(match)
        embeds.append(structured_embed)
        
        # Extract team IDs from match data
        home_team_id = match.additional_data.get("home_team_id")
        away_team_id = match.additional_data.get("away_team_id")
        
        if home_team_id and away_team_id:
            logger.info(f"Creating player props analysis for {match.away_team} @ {match.home_team}")
            
            # 2. Player Props Analysis Only (keep the important betting data)
            player_props_embed = await self.create_player_props_embed(match, home_team_id, away_team_id)
            if player_props_embed:
                embeds.append(player_props_embed)
                logger.info(f"Added player props embed for {match.away_team} @ {match.home_team}")
            else:
                logger.warning(f"Failed to create player props embed for {match.away_team} @ {match.home_team}")
        else:
            logger.warning(f"Missing team IDs for {match.away_team} @ {match.home_team}: home={home_team_id}, away={away_team_id}")
        
        logger.info(f"Generated {len(embeds)} streamlined embeds for {match.away_team} @ {match.home_team}")
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
            
            # Collect team form data
            away_form_data = {}
            home_form_data = {}
            
            # Away team form
            if isinstance(away_form_result, Exception):
                logger.error(f"Exception getting away team form for team {away_team_id}: {away_form_result}")
            elif not away_form_result:
                logger.warning(f"No form data returned for away team {away_team_id}")
            elif away_form_result:
                logger.info(f"Away team form result for team {away_team_id}: {away_form_result}")
                # Extract form data from the nested structure: data.form
                away_data = away_form_result.get("data", {}).get("form", {})
                away_form_data = {
                    "wins": away_data.get("wins", 0),
                    "losses": away_data.get("losses", 0),
                    "win_pct": away_data.get("win_percentage", "N/A"),
                    "streak": away_data.get("streak", "N/A"),
                    "games_back": away_data.get("games_back", "N/A")
                }
            
            # Home team form  
            if isinstance(home_form_result, Exception):
                logger.error(f"Exception getting home team form for team {home_team_id}: {home_form_result}")
            elif not home_form_result:
                logger.warning(f"No form data returned for home team {home_team_id}")
            elif home_form_result:
                logger.info(f"Home team form result for team {home_team_id}: {home_form_result}")
                # Extract form data from the nested structure: data.form
                home_data = home_form_result.get("data", {}).get("form", {})
                home_form_data = {
                    "wins": home_data.get("wins", 0),
                    "losses": home_data.get("losses", 0),
                    "win_pct": home_data.get("win_percentage", "N/A"),
                    "streak": home_data.get("streak", "N/A"),
                    "games_back": home_data.get("games_back", "N/A")
                }
            
            # Create aligned two-column table format
            if away_form_data or home_form_data:
                # Format team names for header (max 30 chars each side)
                away_header = f"**{match.away_team} (Away)**"
                home_header = f"**{match.home_team} (Home)**"
                
                # Create the aligned table
                form_table = "```\n"
                form_table += f"{away_header:<32} | {home_header}\n"
                form_table += f"{'─' * 32}|{'─' * 32}\n"
                
                # Record line
                away_record = f"- Record: {away_form_data.get('wins', 0)}-{away_form_data.get('losses', 0)}" if away_form_data else "- Record: N/A"
                home_record = f"- Record: {home_form_data.get('wins', 0)}-{home_form_data.get('losses', 0)}" if home_form_data else "- Record: N/A"
                form_table += f"{away_record:<32} | {home_record}\n"
                
                # Win % line
                away_winpct = f"- Win %: {away_form_data.get('win_pct', 'N/A')}" if away_form_data else "- Win %: N/A"
                home_winpct = f"- Win %: {home_form_data.get('win_pct', 'N/A')}" if home_form_data else "- Win %: N/A"
                form_table += f"{away_winpct:<32} | {home_winpct}\n"
                
                # Streak line
                away_streak = f"- Streak: {away_form_data.get('streak', 'N/A')}" if away_form_data else "- Streak: N/A"
                home_streak = f"- Streak: {home_form_data.get('streak', 'N/A')}" if home_form_data else "- Streak: N/A"
                form_table += f"{away_streak:<32} | {home_streak}\n"
                
                # Games Back line
                away_gb = f"- Games Back: {away_form_data.get('games_back', 'N/A')}" if away_form_data else "- Games Back: N/A"
                home_gb = f"- Games Back: {home_form_data.get('games_back', 'N/A')}" if home_form_data else "- Games Back: N/A"
                
                # Format Games Back with "GB" suffix if it's a number
                if home_form_data and home_form_data.get('games_back') != 'N/A' and home_form_data.get('games_back') != '-':
                    home_gb = f"- Games Back: {home_form_data.get('games_back')} GB"
                elif home_form_data and home_form_data.get('games_back') == '-':
                    home_gb = "- Games Back: -"
                    
                if away_form_data and away_form_data.get('games_back') != 'N/A' and away_form_data.get('games_back') != '-':
                    away_gb = f"- Games Back: {away_form_data.get('games_back')} GB"
                elif away_form_data and away_form_data.get('games_back') == '-':
                    away_gb = "- Games Back: -"
                
                form_table += f"{away_gb:<32} | {home_gb}\n"
                form_table += "```"
                
                embed.add_field(
                    name="📊 **Team Form:**",
                    value=form_table,
                    inline=False
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
            
            # Collect scoring trends data
            away_trends_data = {}
            home_trends_data = {}
            
            # Away team scoring
            if not isinstance(away_trends_result, Exception) and away_trends_result:
                logger.debug(f"Away team trends result: {away_trends_result}")
                # Extract trends data from the nested structure: data.trends
                away_trends = away_trends_result.get("data", {}).get("trends", {})
                away_trends_data = {
                    "rpg": away_trends.get("runs_per_game", 0),
                    "rapg": away_trends.get("runs_allowed_per_game", 0),
                    "diff": away_trends.get("run_differential", 0),
                    "games_played": away_trends.get("games_played", 0)
                }
            
            # Home team scoring
            if not isinstance(home_trends_result, Exception) and home_trends_result:
                logger.debug(f"Home team trends result: {home_trends_result}")
                # Extract trends data from the nested structure: data.trends
                home_trends = home_trends_result.get("data", {}).get("trends", {})
                home_trends_data = {
                    "rpg": home_trends.get("runs_per_game", 0),
                    "rapg": home_trends.get("runs_allowed_per_game", 0),
                    "diff": home_trends.get("run_differential", 0),
                    "games_played": home_trends.get("games_played", 0)
                }
            
            # Create aligned two-column table format
            if away_trends_data or home_trends_data:
                # Format team names for header
                away_header = f"**{match.away_team}**"
                home_header = f"**{match.home_team}**"
                
                # Create the aligned table
                trends_table = "```\n"
                trends_table += f"{away_header:<32} | {home_header}\n"
                trends_table += f"{'─' * 32}|{'─' * 32}\n"
                
                # Runs per game line
                away_rpg = f"⚾ Runs/Game: {away_trends_data.get('rpg', 0):.1f}" if away_trends_data else "⚾ Runs/Game: N/A"
                home_rpg = f"⚾ Runs/Game: {home_trends_data.get('rpg', 0):.1f}" if home_trends_data else "⚾ Runs/Game: N/A"
                trends_table += f"{away_rpg:<32} | {home_rpg}\n"
                
                # Runs allowed per game line
                away_rapg = f"🚫 Allowed/Game: {away_trends_data.get('rapg', 0):.1f}" if away_trends_data else "🚫 Allowed/Game: N/A"
                home_rapg = f"🚫 Allowed/Game: {home_trends_data.get('rapg', 0):.1f}" if home_trends_data else "🚫 Allowed/Game: N/A"
                trends_table += f"{away_rapg:<32} | {home_rapg}\n"
                
                # Run differential line with appropriate emoji
                if away_trends_data:
                    away_diff = away_trends_data.get('diff', 0)
                    away_emoji = "📈" if away_diff > 0 else "📉" if away_diff < 0 else "➖"
                    away_diff_text = f"{away_emoji} Run Diff: {away_diff:+d}"
                else:
                    away_diff_text = "📊 Run Diff: N/A"
                
                if home_trends_data:
                    home_diff = home_trends_data.get('diff', 0)
                    home_emoji = "📈" if home_diff > 0 else "📉" if home_diff < 0 else "➖"
                    home_diff_text = f"{home_emoji} Run Diff: {home_diff:+d}"
                else:
                    home_diff_text = "📊 Run Diff: N/A"
                
                trends_table += f"{away_diff_text:<32} | {home_diff_text}\n"
                trends_table += "```"
                
                embed.add_field(
                    name="📈 **Scoring Trends:**",
                    value=trends_table,
                    inline=False
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
    
    async def create_betting_odds_embed(self, match: Match, home_team_id: int, away_team_id: int) -> Optional[discord.Embed]:
        """Create betting odds analysis using Odds MCP v2"""
        try:
            # Call odds MCP directly for MLB betting lines
            import httpx
            
            odds_url = "https://odds-mcp-v2-production.up.railway.app/mcp"
            
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 1,
                "params": {
                    "name": "getOdds",
                    "arguments": {
                        "sport": "baseball_mlb",
                        "markets": "h2h,spreads,totals",
                        "regions": "us"
                    }
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(odds_url, json=payload)
                response.raise_for_status()
                result = response.json()
                
                if "result" not in result or "data" not in result["result"]:
                    logger.warning(f"No odds data returned for MLB")
                    return None
                
                odds_data = result["result"]["data"]["odds"]
                if not odds_data:
                    logger.warning(f"No MLB games found with odds")
                    return None
                
                # Find our specific game by team names
                target_game = None
                for game in odds_data:
                    away_team = game.get("away_team", "")
                    home_team = game.get("home_team", "")
                    
                    # Match team names (handle different name formats)
                    if (match.away_team in away_team or away_team in match.away_team) and \
                       (match.home_team in home_team or home_team in match.home_team):
                        target_game = game
                        break
                
                if not target_game:
                    logger.warning(f"No odds found for {match.away_team} @ {match.home_team}")
                    return None
                
                logger.debug(f"Found odds for {target_game.get('away_team')} @ {target_game.get('home_team')}")
                
                # Create betting odds embed
                embed = discord.Embed(
                    title=f"💰 Betting Odds: {match.away_team} vs {match.home_team}",
                    color=0x00FF00,  # Green color for money/betting
                    timestamp=datetime.now()
                )
                
                if "bookmakers" not in target_game or not target_game["bookmakers"]:
                    embed.add_field(name="❌ No Odds Available", value="Betting lines not available for this game", inline=False)
                    return embed
                
                # Use first bookmaker (usually FanDuel)
                bookmaker = target_game["bookmakers"][0]
                bookmaker_name = bookmaker.get("title", "Sportsbook")
                
                embed.add_field(
                    name="🏪 Sportsbook",
                    value=bookmaker_name,
                    inline=True
                )
                
                # Process each market
                for market in bookmaker.get("markets", []):
                    market_key = market.get("key")
                    
                    if market_key == "h2h":
                        # Moneyline
                        ml_text = ""
                        for outcome in market.get("outcomes", []):
                            name = outcome.get("name")
                            price = outcome.get("price")
                            if isinstance(price, int):
                                ml_text += f"**{name}:** {price:+d}\\n"
                            else:
                                ml_text += f"**{name}:** {price}\\n"
                        
                        if ml_text:
                            embed.add_field(
                                name="💵 Moneyline (ML)",
                                value=ml_text.strip(),
                                inline=True
                            )
                    
                    elif market_key == "spreads":
                        # Run Line
                        spread_text = ""
                        for outcome in market.get("outcomes", []):
                            name = outcome.get("name")
                            price = outcome.get("price")
                            point = outcome.get("point", 0)
                            
                            if isinstance(price, int):
                                spread_text += f"**{name} ({point:+g}):** {price:+d}\\n"
                            else:
                                spread_text += f"**{name} ({point:+g}):** {price}\\n"
                        
                        if spread_text:
                            embed.add_field(
                                name="📊 Run Line (RL)",
                                value=spread_text.strip(),
                                inline=True
                            )
                    
                    elif market_key == "totals":
                        # Over/Under
                        total_text = ""
                        for outcome in market.get("outcomes", []):
                            name = outcome.get("name")
                            price = outcome.get("price")
                            point = outcome.get("point", 0)
                            
                            if isinstance(price, int):
                                total_text += f"**{name} {point}:** {price:+d}\\n"
                            else:
                                total_text += f"**{name} {point}:** {price}\\n"
                        
                        if total_text:
                            embed.add_field(
                                name="🎯 Total (O/U)",
                                value=total_text.strip(),
                                inline=True
                            )
                
                # Add betting notes
                embed.add_field(
                    name="📝 Betting Notes",
                    value="American odds format (+/-)\nNegative = Favorite, Positive = Underdog\nLines subject to change",
                    inline=False
                )
                
                embed.set_footer(text=f"Betting Odds • Powered by {bookmaker_name}")
                return embed
                
        except Exception as e:
            logger.error(f"Error creating betting odds embed: {e}")
            return None
    


    async def create_player_props_embed(self, match: Match, home_team_id: int, away_team_id: int) -> Optional[discord.Embed]:
        """Create player props analysis using Odds MCP v2 for hits, home runs, strikeouts only"""
        try:
            import httpx
            
            odds_url = "https://odds-mcp-v2-production.up.railway.app/mcp"
            
            # Step 1: Get event ID for this specific game
            events_payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 1,
                "params": {
                    "name": "getEvents",
                    "arguments": {"sport": "baseball_mlb"}
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get events (games) to find our specific game
                events_response = await client.post(odds_url, json=events_payload)
                events_response.raise_for_status()
                events_result = events_response.json()
                
                if "result" not in events_result or "data" not in events_result["result"]:
                    logger.warning("No events data from Odds MCP")
                    return None
                
                events = events_result["result"]["data"]["events"]
                
                # Find our specific game by matching team names
                target_event = None
                for event in events:
                    home_team = event.get("home_team", "").lower()
                    away_team = event.get("away_team", "").lower()
                    
                    match_home = match.home_team.lower()
                    match_away = match.away_team.lower()
                    
                    if (match_home in home_team or home_team in match_home) and \
                       (match_away in away_team or away_team in match_away):
                        target_event = event
                        break
                
                if not target_event:
                    logger.warning(f"Could not find event for {match.away_team} @ {match.home_team}")
                    return None
                
                event_id = target_event["id"]
                
                # Step 2: Get player props for specific markets
                target_markets = ["batter_hits", "batter_home_runs", "pitcher_strikeouts"]
                player_props_data = {}
                
                for market in target_markets:
                    props_payload = {
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "id": 1,
                        "params": {
                            "name": "getEventOdds",
                            "arguments": {
                                "sport": "baseball_mlb",
                                "event_id": event_id,
                                "markets": market
                            }
                        }
                    }
                    
                    props_response = await client.post(odds_url, json=props_payload)
                    props_response.raise_for_status()
                    props_result = props_response.json()
                    
                    if "result" in props_result and "data" in props_result["result"]:
                        event_data = props_result["result"]["data"]["event"]
                        if "bookmakers" in event_data and event_data["bookmakers"]:
                            bookmaker = event_data["bookmakers"][0]
                            for market_data in bookmaker.get("markets", []):
                                if market_data.get("key") == market:
                                    player_props_data[market] = market_data["outcomes"]
                                    break
                
                all_player_names = set()
                for market_data in player_props_data.values():
                    for outcome in market_data:
                        if outcome.get("name") == "Over":
                            player_name = outcome.get("description", "")
                            if player_name:
                                all_player_names.add(player_name)
                
                player_stats = await self.get_player_stats_by_names(
                    list(all_player_names), home_team_id, away_team_id
                )
                
                embed = discord.Embed(
                    title=f"Player Props + Stats • {match.away_team} @ {match.home_team}",
                    description="Live betting markets with recent player performance.",
                    color=0x1E88E5,
                    timestamp=datetime.now()
                )
                
                if "batter_hits" in player_props_data:
                    hits_text = "```\nPlayer                 Line  Odds   Avg H/G   L5\n"
                    hits_text += "---------------------- ----- ------ -------   --\n"
                    processed_players = set()
                    
                    for outcome in player_props_data["batter_hits"]:
                        if outcome.get("name") == "Over" and outcome.get("point", 0) == 0.5:
                            player_name = outcome.get("description", "")
                            if player_name and player_name not in processed_players:
                                processed_players.add(player_name)
                                price = outcome.get("price")
                                odds_str = f"{price:+d}" if isinstance(price, int) else str(price)
                                
                                avg_hits, streak_info, emoji = 0.0, "--", ""
                                if player_name in player_stats:
                                    stats = player_stats[player_name]
                                    avg_hits = stats.get("avg_hits", 0.0)
                                    hit_streak = stats.get("hit_streak", 0)
                                    if avg_hits >= 1.5: emoji = "🔥"
                                    elif avg_hits >= 1.2: emoji = "⚡"
                                    elif hit_streak >= 3: emoji = "🎯"
                                    streak_info = f"{hit_streak}G" if hit_streak > 0 else "--"
                                
                                name_display = f"{player_name}{emoji}"
                                hits_text += f"{name_display:<22s} O0.5  {odds_str:<6s} {f'{avg_hits:.1f}':<9s} {streak_info}\n"
                                
                                if len(processed_players) >= 10: break
                    
                    hits_text += "```"
                    if processed_players:
                        embed.add_field(name="🏃 Player Hits", value=hits_text, inline=False)

                # REVISED HOME RUNS LOGIC
                if "batter_home_runs" in player_props_data:
                    hr_text = "```\nPlayer             Line  Odds   L5 HR\n"
                    hr_text += "------------------ ----- ------ -----\n"
                    processed_players = set()
                    
                    for outcome in player_props_data["batter_home_runs"]:
                        if outcome.get("name") == "Over" and outcome.get("point", 0) == 0.5:
                            player_name = outcome.get("description", "")
                            if player_name and player_name not in processed_players:
                                processed_players.add(player_name)
                                price = outcome.get("price")
                                odds_str = f"{price:+d}" if isinstance(price, int) else str(price)

                                recent_hrs, emoji = 0, ""
                                if player_name in player_stats:
                                    stats = player_stats[player_name]
                                    recent_hrs = stats.get("recent_hrs", 0)
                                    if recent_hrs >= 2: emoji = "🔥"
                                
                                name_display = f"{player_name}{emoji}"
                                line_display = "O0.5"
                                hr_display = f"{recent_hrs} HR"

                                # This is the new, robust f-string that builds the line in one go
                                hr_text += f"{name_display:<18s} {line_display:<5s} {odds_str:<6s} {hr_display}\n"

                                if len(processed_players) >= 10: break
                    
                    hr_text += "```"
                    if processed_players:
                        embed.add_field(name="⚾ Home Runs", value=hr_text, inline=True)

                # REVISED PITCHER STRIKEOUTS LOGIC
                if "pitcher_strikeouts" in player_props_data:
                    k_text = "```\nPlayer               Line  Odds\n"
                    k_text += "-------------------- ----- ------\n"
                    processed_players = set()
                    
                    for outcome in player_props_data["pitcher_strikeouts"]:
                        if outcome.get("name") == "Over":
                            player_name = outcome.get("description", "")
                            if player_name and player_name not in processed_players:
                                processed_players.add(player_name)
                                point = outcome.get("point", 0)
                                price = outcome.get("price")
                                
                                odds_str = f"{price:+d}" if isinstance(price, int) else str(price)
                                line_display = f"O{point:.1f}"

                                # This is the new, robust f-string
                                k_text += f"{player_name:<20s} {line_display:<5s} {odds_str}\n"
                                
                                if len(processed_players) >= 6: break
                    
                    k_text += "```"
                    if processed_players:
                        embed.add_field(name="🔥 Pitcher Strikeouts", value=k_text, inline=True)
                
                info_text = "• **Betting:** Over lines only, no alternate lines\n"
                info_text += "• **Stats:** H/G = Hits per game, L5 = Last 5 games\n"
                info_text += "• Lines subject to change"
                
                embed.add_field(name="ℹ️ Player Props + Stats Info", value=info_text, inline=False)
                embed.set_footer(text="Player Props • Powered by The Odds API")
                
                if not any(market in player_props_data for market in target_markets):
                    embed.add_field(name="❌ No Props Available", value="Player props not available for this game", inline=False)
                
                return embed
                
        except Exception as e:
            logger.error(f"Error creating player props embed: {e}")
            return None


    async def get_player_stats_by_names(self, player_names: List[str], home_team_id: int, away_team_id: int) -> Dict[str, Dict]:
        """Get player stats for players with betting lines"""
        try:
            # Get rosters for both teams to find player IDs
            home_roster_task = self.call_mlb_mcp_tool("getMLBTeamRoster", {"teamId": home_team_id})
            away_roster_task = self.call_mlb_mcp_tool("getMLBTeamRoster", {"teamId": away_team_id})
            
            home_roster_result, away_roster_result = await asyncio.gather(
                home_roster_task, away_roster_task, return_exceptions=True
            )
            
            # Build name -> player_id mapping
            player_id_map = {}
            
            for roster_result in [home_roster_result, away_roster_result]:
                if not isinstance(roster_result, Exception) and "data" in roster_result:
                    players = roster_result["data"].get("players", [])
                    for player in players:
                        full_name = player.get("fullName", "")
                        player_id = player.get("playerId")
                        if full_name and player_id:
                            player_id_map[full_name] = {
                                "playerId": player_id,
                                "position": player.get("position", ""),
                                "number": player.get("primaryNumber", "")
                            }
            
            # Find player IDs for betting props players
            found_player_ids = []
            name_to_id = {}
            
            for prop_name in player_names:
                # Try exact match first
                if prop_name in player_id_map:
                    found_player_ids.append(player_id_map[prop_name]["playerId"])
                    name_to_id[prop_name] = player_id_map[prop_name]["playerId"]
                else:
                    # Try partial matching (last name)
                    prop_last_name = prop_name.split()[-1].lower() if " " in prop_name else prop_name.lower()
                    for roster_name, info in player_id_map.items():
                        roster_last_name = roster_name.split()[-1].lower() if " " in roster_name else roster_name.lower()
                        if prop_last_name == roster_last_name:
                            found_player_ids.append(info["playerId"])
                            name_to_id[prop_name] = info["playerId"]
                            break
            
            if not found_player_ids:
                logger.warning("No matching player IDs found for betting props players")
                return {}
            
            # Get recent stats and streaks in parallel
            stats_task = self.call_mlb_mcp_tool("getMLBPlayerLastN", {"player_ids": found_player_ids, "games": 5})
            streaks_task = self.call_mlb_mcp_tool("getMLBPlayerStreaks", {"player_ids": found_player_ids})
            
            stats_result, streaks_result = await asyncio.gather(
                stats_task, streaks_task, return_exceptions=True
            )
            
            # Process results
            player_stats = {}
            
            # Add recent stats
            if not isinstance(stats_result, Exception) and "data" in stats_result:
                results = stats_result["data"].get("results", {})
                for player_name, player_id in name_to_id.items():
                    player_id_str = str(player_id)
                    if player_id_str in results:
                        stats_data = results[player_id_str]
                        games = stats_data.get("games", [])
                        
                        # Calculate recent performance
                        recent_hits = sum(game.get("hits", 0) for game in games)
                        recent_hrs = sum(game.get("homeRuns", 0) for game in games)
                        games_count = len(games)
                        
                        player_stats[player_name] = {
                            "recent_hits": recent_hits,
                            "recent_hrs": recent_hrs, 
                            "recent_games": games_count,
                            "avg_hits": round(recent_hits / games_count, 1) if games_count > 0 else 0,
                            "position": player_id_map.get(player_name, {}).get("position", "")
                        }
            
            # Add streaks data
            if not isinstance(streaks_result, Exception) and "data" in streaks_result:
                results = streaks_result["data"].get("results", {})
                for player_name, player_id in name_to_id.items():
                    player_id_str = str(player_id)
                    if player_id_str in results and player_name in player_stats:
                        streaks_data = results[player_id_str].get("streaks", {})
                        player_stats[player_name].update({
                            "hit_streak": streaks_data.get("current_hit_streak", 0),
                            "multi_hit_games": streaks_data.get("multi_hit_games", 0),
                            "hr_streak": streaks_data.get("current_hr_streak", 0)
                        })
            
            logger.info(f"Found stats for {len(player_stats)} players with betting lines")
            return player_stats
            
        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            return {}
    
    async def create_pitcher_matchup_embed(self, match: Match, home_team_id: int, away_team_id: int) -> Optional[discord.Embed]:
        """Create pitcher matchup analysis using getMLBPitcherMatchup"""
        try:
            # Use raw HTTP call to bypass MCP client parsing issues
            import httpx
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "getMLBPitcherMatchup",
                    "arguments": {"teams": [away_team_id, home_team_id]}
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.config['mcp_url'], json=payload)
                response.raise_for_status()
                result = response.json()
                
                if "error" in result:
                    logger.warning(f"Pitcher matchup JSON-RPC error: {result['error']}")
                    return None
                
                mcp_result = result.get("result", {})
                logger.debug(f"Raw pitcher matchup result: {mcp_result}")
                
                # Handle different response formats
                if "content" in mcp_result and isinstance(mcp_result["content"], list):
                    # Parse JSON from content array
                    import json
                    content_text = mcp_result["content"][0]["text"]
                    pitcher_data = json.loads(content_text)
                else:
                    # Use direct data
                    pitcher_data = mcp_result
                
                if not pitcher_data:
                    logger.warning(f"No pitcher matchup data available for teams {away_team_id}, {home_team_id}")
                    return None
            
            # Create pitcher matchup embed
            embed = discord.Embed(
                title=f"⚾ Pitching Matchup: {match.away_team} vs {match.home_team}",
                color=0x8B4513,  # Brown color for pitching
                timestamp=datetime.now()
            )
            
            # Try different data access patterns
            if "team_rosters" in pitcher_data:
                team_rosters = pitcher_data["team_rosters"]
            elif "data" in pitcher_data and "team_rosters" in pitcher_data["data"]:
                team_rosters = pitcher_data["data"]["team_rosters"]
            else:
                logger.warning(f"Could not find team_rosters in pitcher data: {list(pitcher_data.keys())}")
                return None
            
            logger.debug(f"Found team rosters for teams: {list(team_rosters.keys())}")
            
            # Away team pitchers
            away_roster = team_rosters.get(str(away_team_id), {})
            if away_roster:
                away_pitchers = away_roster.get("pitcher_list", [])[:5]  # Top 5 pitchers
                if away_pitchers:
                    pitcher_names = []
                    for pitcher in away_pitchers:
                        name = pitcher.get("fullName", "Unknown")
                        number = pitcher.get("primaryNumber", "")
                        status = pitcher.get("status", "")
                        if number:
                            pitcher_names.append(f"#{number} {name}")
                        else:
                            pitcher_names.append(name)
                    
                    embed.add_field(
                        name=f"✈️ {match.away_team} Rotation",
                        value="\\n".join(pitcher_names[:3]) + (f"\\n+ {len(away_pitchers)-3} more" if len(away_pitchers) > 3 else ""),
                        inline=True
                    )
            
            # Home team pitchers
            home_roster = team_rosters.get(str(home_team_id), {})
            if home_roster:
                home_pitchers = home_roster.get("pitcher_list", [])[:5]  # Top 5 pitchers
                if home_pitchers:
                    pitcher_names = []
                    for pitcher in home_pitchers:
                        name = pitcher.get("fullName", "Unknown")
                        number = pitcher.get("primaryNumber", "")
                        status = pitcher.get("status", "")
                        if number:
                            pitcher_names.append(f"#{number} {name}")
                        else:
                            pitcher_names.append(name)
                    
                    embed.add_field(
                        name=f"🏠 {match.home_team} Rotation",
                        value="\\n".join(pitcher_names[:3]) + (f"\\n+ {len(home_pitchers)-3} more" if len(home_pitchers) > 3 else ""),
                        inline=True
                    )
            
            # Add rotation depth comparison
            away_pitcher_count = away_roster.get("pitchers", 0)
            home_pitcher_count = home_roster.get("pitchers", 0)
            
            if away_pitcher_count and home_pitcher_count:
                embed.add_field(
                    name="📊 Pitching Depth",
                    value=f"**{match.away_team}:** {away_pitcher_count} pitchers\\n**{match.home_team}:** {home_pitcher_count} pitchers",
                    inline=True
                )
            
            # Add analysis note
            embed.add_field(
                name="🎯 Rotation Analysis",
                value="Starting rotation showing top pitchers\\nDepth comparison based on active roster",
                inline=False
            )
            
            embed.set_footer(text="Pitcher Matchup Analysis • Powered by getMLBPitcherMatchup")
            return embed
            
        except Exception as e:
            logger.error(f"Error creating pitcher matchup embed: {e}")
            return None
    
    async def get_team_info(self, team_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed team information including division and league"""
        try:
            # Get all teams data
            teams_response = await self.call_mlb_mcp_tool("getMLBTeams", {})
            if not teams_response:
                return None
            
            teams = teams_response.get("data", {}).get("teams", [])
            
            # Find the specific team (teams use "teamId" field)
            team_info = next((team for team in teams if team.get("teamId") == team_id), None)
            return team_info
            
        except Exception as e:
            logger.error(f"Error getting team info for {team_id}: {e}")
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
            logger.debug(f"Converting game data: {game_data}")
            
            # Handle getMLBScheduleET data structure
            # Current structure: game has home{teamId, name} and away{teamId, name}
            home_team_data = game_data.get("home", {})
            away_team_data = game_data.get("away", {})
            
            # Fallback to old structure if needed
            if not home_team_data:
                home_team_data = game_data.get("home_team", {})
            if not away_team_data:
                away_team_data = game_data.get("away_team", {})
            
            home_team = home_team_data.get("name", "Unknown Home")
            away_team = away_team_data.get("name", "Unknown Away")
            home_team_id = home_team_data.get("teamId") or home_team_data.get("id")
            away_team_id = away_team_data.get("teamId") or away_team_data.get("id")
            
            logger.debug(f"Extracted team IDs: home={home_team_id} ({home_team}), away={away_team_id} ({away_team})")
            
            # Extract start time - current structure uses start_et directly
            game_time = game_data.get("start_et", "TBD")
            
            # Fallback to nested structure if needed
            if game_time == "TBD":
                start_time_data = game_data.get("start_time", {})
                if isinstance(start_time_data, dict):
                    game_time = start_time_data.get("formatted", start_time_data.get("raw", "TBD"))
                else:
                    game_time = str(start_time_data) if start_time_data else "TBD"
            
            # Extract status
            status_data = game_data.get("status", {})
            if isinstance(status_data, dict):
                status = status_data.get("raw", "Scheduled")
            else:
                status = str(status_data) if status_data else "Scheduled"
            
            return Match(
                id=str(game_data.get("gamePk", game_data.get("game_pk", game_data.get("id", "")))),
                home_team=home_team,
                away_team=away_team,
                league="MLB",
                datetime=None,
                odds=game_data.get("odds"),
                status=status,
                additional_data={
                    "time": game_time,
                    "venue": game_data.get("venue", "Unknown Venue"),
                    "home_team_id": home_team_id,
                    "away_team_id": away_team_id,
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