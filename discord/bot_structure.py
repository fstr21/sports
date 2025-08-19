# Discord Bot Structure - Foundation Code
"""
Sports Betting Discord Bot - Core Structure
Implements category-based league organization with game-specific channels
"""

import discord
from discord.ext import commands
from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime, timedelta

# Import enhanced soccer integration components with multi-league support
from soccer_channel_manager import SoccerChannelManager
from soccer_integration import SoccerDataProcessor, SoccerEmbedBuilder, League
from soccer_config import (
    get_soccer_config, get_active_soccer_leagues, 
    perform_soccer_startup_checks, validate_soccer_environment
)

# Bot configuration
BOT_TOKEN = "your-bot-token-here"  # Store in environment variables
COMMAND_PREFIX = "/"

class SportsBot(commands.Bot):
    """Main bot class with sports betting focus"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        
        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            description="Sports Betting Analytics Bot"
        )
        
        # Configure logging first
        self.logger = logging.getLogger(__name__)
        
        # Perform configuration validation and startup checks
        self._validate_configuration()
        
        # Category and channel tracking
        self.league_categories: Dict[str, discord.CategoryChannel] = {}
        self.game_channels: Dict[str, discord.TextChannel] = {}
        
        # Enhanced league configurations with multi-league support
        self.leagues = {
            "NFL": {
                "emoji": "🏈",
                "active": False,  # Will be True when season starts
                "channels_per_week": 16
            },
            "MLB": {
                "emoji": "⚾",
                "active": True,
                "channels_per_day": 15
            },
            "SOCCER": {
                "emoji": "⚽",
                "active": True,
                "channels_per_day": 15,  # Increased for multi-league support
                "supported_leagues": {
                    "EPL": {"priority": 1, "active": True},
                    "La Liga": {"priority": 2, "active": True},
                    "Bundesliga": {"priority": 3, "active": True},
                    "Serie A": {"priority": 4, "active": True},
                    "MLS": {"priority": 5, "active": True},
                    "UEFA": {"priority": 0, "active": True}  # Highest priority
                },
                "priority_leagues": ["UEFA", "EPL", "La Liga", "Bundesliga", "Serie A", "MLS"]
            },
            "NBA": {
                "emoji": "🏀",
                "active": False,  # Future season
                "channels_per_day": 12
            },
            "NHL": {
                "emoji": "🏒",
                "active": False,  # Future season
                "channels_per_day": 12
            }
        }
        
        # Initialize enhanced soccer components with multi-league support
        self.soccer_channel_manager = SoccerChannelManager(self)
        self.soccer_data_processor = SoccerDataProcessor()
        self.soccer_embed_builder = SoccerEmbedBuilder()
        
        # Initialize soccer MCP client for multi-league support
        from soccer_integration import SoccerMCPClient
        self.soccer_mcp_client = SoccerMCPClient()
        
        # Initialize soccer cleanup system
        from soccer_cleanup_system import SoccerCleanupSystem
        self.soccer_cleanup_system = SoccerCleanupSystem(self, self.soccer_channel_manager)
        
        # Load soccer configuration
        self.soccer_config = get_soccer_config()
    
    def _validate_configuration(self):
        """Validate bot configuration and environment setup"""
        self.logger.info("Validating bot configuration...")
        
        # Validate environment variables
        env_validation = validate_soccer_environment()
        
        if not env_validation["valid"]:
            self.logger.error("Configuration validation failed:")
            for error in env_validation["errors"]:
                self.logger.error(f"  - {error}")
            raise RuntimeError("Invalid configuration - check environment variables")
        
        # Log warnings
        for warning in env_validation["warnings"]:
            self.logger.warning(warning)
        
        # Log missing optional variables
        if env_validation["missing_optional"]:
            self.logger.info(f"Optional environment variables not set: {', '.join(env_validation['missing_optional'])}")
        
        # Perform soccer-specific startup checks
        if not perform_soccer_startup_checks():
            self.logger.error("Soccer configuration startup checks failed")
            raise RuntimeError("Soccer configuration validation failed")
        
        self.logger.info("Configuration validation completed successfully")
    
    async def create_multi_league_soccer_channels(self, date: str, priority_leagues: Optional[List[str]] = None) -> Dict[str, List]:
        """
        Create soccer channels for multiple leagues with priority ordering
        
        Args:
            date: Date string in YYYY-MM-DD format
            priority_leagues: Optional list of priority league codes
            
        Returns:
            Dictionary with created channels organized by league
        """
        try:
            # Use configured priority leagues if none specified
            if not priority_leagues:
                priority_leagues = self.leagues["SOCCER"]["priority_leagues"]
            
            # Fetch matches for multiple leagues
            raw_matches = await self.soccer_mcp_client.get_matches_for_multiple_leagues(
                date, priority_leagues
            )
            
            # Process matches with standings information
            processed_matches = self.soccer_data_processor.process_match_data(
                raw_matches, include_standings=True
            )
            
            if not processed_matches:
                self.logger.info(f"No soccer matches found for date {date}")
                return {}
            
            # Create channels organized by league priority
            channels_by_league = {}
            
            for match in processed_matches:
                league_code = None
                if match.league.config:
                    league_code = match.league.config.get("code", "Unknown")
                
                if league_code not in channels_by_league:
                    channels_by_league[league_code] = []
                
                # Create channel for this match
                channel = await self.soccer_channel_manager.create_match_channel(match)
                if channel:
                    channels_by_league[league_code].append(channel)
                    
                    # Post enhanced match preview with standings
                    embed = self.soccer_embed_builder.create_match_preview_embed(match)
                    await channel.send(embed=embed)
            
            # Log creation summary
            total_channels = sum(len(channels) for channels in channels_by_league.values())
            self.logger.info(f"Created {total_channels} soccer channels across {len(channels_by_league)} leagues")
            
            return channels_by_league
            
        except Exception as e:
            self.logger.error(f"Error creating multi-league soccer channels: {e}")
            return {}
    
    async def get_league_standings(self, league_code: str) -> Optional[discord.Embed]:
        """
        Get league standings embed for a specific league
        
        Args:
            league_code: League code (e.g., "EPL", "La Liga")
            
        Returns:
            Discord embed with league standings or None if unavailable
        """
        try:
            from soccer_integration import SUPPORTED_LEAGUES
            
            if league_code not in SUPPORTED_LEAGUES:
                self.logger.error(f"Unsupported league code: {league_code}")
                return None
            
            league_config = SUPPORTED_LEAGUES[league_code]
            
            # Skip standings for tournament competitions
            if league_config.get("tournament_type") == "knockout":
                return self.soccer_embed_builder._create_error_embed(
                    "No Standings Available",
                    f"{league_config['name']} is a knockout tournament without league standings"
                )
            
            # Fetch standings data
            standings_data = await self.soccer_mcp_client.get_league_standings(
                league_config["id"], include_form=True
            )
            
            # Create league object
            league = League(
                id=league_config["id"],
                name=league_config["name"],
                country=league_config["country"],
                season=league_config.get("season_format"),
                priority=league_config["priority"],
                tournament_type=league_config["tournament_type"]
            )
            
            # Create standings embed
            return self.soccer_embed_builder.create_league_standings_embed(standings_data, league)
            
        except Exception as e:
            self.logger.error(f"Error fetching league standings for {league_code}: {e}")
            return self.soccer_embed_builder._create_error_embed(
                "Standings Error",
                f"Unable to fetch standings for {league_code}: {str(e)}"
            )
    
    def get_active_soccer_leagues(self) -> List[str]:
        """
        Get list of currently active soccer leagues
        
        Returns:
            List of active league codes
        """
        active_leagues = []
        soccer_config = self.leagues.get("SOCCER", {})
        supported_leagues = soccer_config.get("supported_leagues", {})
        
        for league_code, league_info in supported_leagues.items():
            if league_info.get("active", False):
                active_leagues.append(league_code)
        
        # Sort by priority
        priority_order = soccer_config.get("priority_leagues", [])
        active_leagues.sort(key=lambda x: priority_order.index(x) if x in priority_order else 999)
        
        return active_leagues

    async def on_ready(self):
        """Bot startup - initialize server structure"""
        print(f'{self.user} has connected to Discord!')
        
        # Load cleanup commands cog
        try:
            from soccer_cleanup_commands import SoccerCleanupCommands
            await self.add_cog(SoccerCleanupCommands(self, self.soccer_cleanup_system))
            print("Loaded soccer cleanup commands")
        except Exception as e:
            print(f"Failed to load cleanup commands: {e}")
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
            
        # Initialize server structure
        await self.setup_server_structure()

    async def setup_server_structure(self):
        """Create league categories and basic structure"""
        guild = self.guilds[0] if self.guilds else None
        if not guild:
            print("Bot not connected to any guilds")
            return
            
        print(f"Setting up server structure for {guild.name}")
        
        # Create league categories
        for league, config in self.leagues.items():
            category_name = f"{config['emoji']} {league}"
            
            # Check if category already exists
            existing_category = discord.utils.get(guild.categories, name=category_name)
            if not existing_category:
                category = await guild.create_category(category_name)
                print(f"Created category: {category_name}")
            else:
                category = existing_category
                print(f"Found existing category: {category_name}")
                
            self.league_categories[league] = category

    async def create_game_channel(self, league: str, team1: str, team2: str, 
                                game_date: datetime) -> Optional[discord.TextChannel]:
        """Create a new game channel under appropriate league category"""
        
        if league not in self.league_categories:
            print(f"League {league} not found in categories")
            return None
            
        category = self.league_categories[league]
        channel_name = f"📊 {team1.lower().replace(' ', '-')}-vs-{team2.lower().replace(' ', '-')}"
        
        # Check if channel already exists
        existing_channel = discord.utils.get(category.channels, name=channel_name)
        if existing_channel:
            return existing_channel
            
        # Create new channel
        try:
            channel = await category.create_text_channel(
                name=channel_name,
                topic=f"{team1} vs {team2} - {game_date.strftime('%B %d, %Y')}"
            )
            
            # Store channel reference
            game_key = f"{league}_{team1}_{team2}_{game_date.strftime('%Y%m%d')}"
            self.game_channels[game_key] = channel
            
            print(f"Created game channel: {channel_name}")
            return channel
            
        except Exception as e:
            print(f"Failed to create channel {channel_name}: {e}")
            return None

    async def cleanup_old_channels(self, days_old: int = 3):
        """Remove game channels older than specified days - delegates to soccer cleanup system"""
        for guild in self.guilds:
            try:
                # Use the new soccer cleanup system for soccer channels
                if hasattr(self, 'soccer_cleanup_system'):
                    stats = await self.soccer_cleanup_system.cleanup_old_channels(guild, days_old)
                    if stats.channels_deleted > 0 or stats.errors > 0:
                        print(f"Cleanup for {guild.name}: deleted {stats.channels_deleted}, errors {stats.errors}")
                else:
                    # Fallback to old method for other leagues
                    cutoff_date = datetime.now() - timedelta(days=days_old)
                    for category in guild.categories:
                        if any(league in category.name for league in self.leagues.keys()):
                            for channel in category.channels:
                                if channel.name.startswith("📊"):
                                    # Extract date from channel topic or creation time
                                    channel_age = datetime.now() - channel.created_at
                                    if channel_age.days > days_old:
                                        try:
                                            await channel.delete()
                                            print(f"Deleted old channel: {channel.name}")
                                        except Exception as e:
                                            print(f"Failed to delete {channel.name}: {e}")
            except Exception as e:
                print(f"Error cleaning up channels in {guild.name}: {e}")

# Global bot instance
bot = SportsBot()

# ============================================================================
# SLASH COMMANDS
# ============================================================================

@bot.tree.command(name="create-channels", description="Create game channels for a specific date")
@discord.app_commands.describe(
    sport="Select the sport for channel creation",
    date="Date in MM/DD/YYYY, DD-MM-YYYY, or YYYY-MM-DD format"
)
@discord.app_commands.choices(sport=[
    discord.app_commands.Choice(name="Soccer", value="Soccer"),
    discord.app_commands.Choice(name="MLB", value="MLB")
])
async def create_channels_command(interaction: discord.Interaction, 
                                sport: discord.app_commands.Choice[str], 
                                date: str):
    """Create game channels for a specific sport and date"""
    
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ You need administrator permissions to use this command.", 
            ephemeral=True
        )
        return
    
    await interaction.response.defer()
    
    try:
        # Get sport value from Choice object
        sport_value = sport.value
        
        # Validate and convert date format
        try:
            validated_date = validate_date_input(date)
        except ValueError as e:
            embed = discord.Embed(
                title="❌ Invalid Date Format",
                description=str(e),
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Handle soccer channel creation
        if sport_value == "Soccer":
            await handle_soccer_channel_creation(interaction, validated_date)
        elif sport_value == "MLB":
            # Placeholder for MLB implementation
            embed = discord.Embed(
                title="🚧 MLB Integration",
                description="MLB channel creation will be implemented soon",
                color=0xffa500
            )
            await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Error in create-channels command: {e}")
        embed = discord.Embed(
            title="❌ Command Error",
            description="An unexpected error occurred while creating channels",
            color=0xff0000
        )
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="schedule", description="Show games for today or specific date")
async def schedule_command(interaction: discord.Interaction, 
                          league: str = None, 
                          date: str = None):
    """Display game schedule"""
    
    await interaction.response.defer()
    
    # This will integrate with your MCP servers
    embed = discord.Embed(
        title="🗓️ Game Schedule",
        description="*Integration with MCP servers pending*",
        color=0x00ff00
    )
    
    if league:
        embed.add_field(name="League", value=league.upper(), inline=True)
    if date:
        embed.add_field(name="Date", value=date, inline=True)
        
    embed.add_field(
        name="Coming Soon", 
        value="Schedule data from MLB, Soccer, and other MCPs", 
        inline=False
    )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="odds", description="Get betting odds for a matchup")
async def odds_command(interaction: discord.Interaction, 
                      team1: str, 
                      team2: str):
    """Display betting odds"""
    
    await interaction.response.defer()
    
    # This will integrate with your Odds MCP
    embed = discord.Embed(
        title="💰 Betting Odds",
        description=f"**{team1.title()} vs {team2.title()}**",
        color=0xffd700
    )
    
    embed.add_field(
        name="Moneyline", 
        value="*Odds MCP integration pending*", 
        inline=True
    )
    embed.add_field(
        name="Spread", 
        value="*Coming soon*", 
        inline=True
    )
    embed.add_field(
        name="Total", 
        value="*Coming soon*", 
        inline=True
    )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="player", description="Get player stats and prop history")
async def player_command(interaction: discord.Interaction, 
                        player_name: str):
    """Display player information"""
    
    await interaction.response.defer()
    
    # This will integrate with your ESPN Player ID MCP
    embed = discord.Embed(
        title="👤 Player Stats",
        description=f"**{player_name.title()}**",
        color=0x0099ff
    )
    
    embed.add_field(
        name="Current Stats", 
        value="*ESPN Player ID MCP integration pending*", 
        inline=False
    )
    embed.add_field(
        name="Prop History", 
        value="*Coming soon*", 
        inline=False
    )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="setup", description="Admin command to create game channels")
async def setup_command(interaction: discord.Interaction, 
                       league: str, 
                       team1: str, 
                       team2: str):
    """Admin command to manually create game channels"""
    
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ You need administrator permissions to use this command.", 
            ephemeral=True
        )
        return
    
    await interaction.response.defer()
    
    # Create game channel
    game_date = datetime.now()
    channel = await bot.create_game_channel(league.upper(), team1, team2, game_date)
    
    if channel:
        embed = discord.Embed(
            title="✅ Channel Created",
            description=f"Game channel created: {channel.mention}",
            color=0x00ff00
        )
    else:
        embed = discord.Embed(
            title="❌ Channel Creation Failed",
            description="Could not create the game channel",
            color=0xff0000
        )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="cleanup", description="Admin command to remove old game channels")
async def cleanup_command(interaction: discord.Interaction, days: int = 3):
    """Admin command to cleanup old channels"""
    
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ You need administrator permissions to use this command.", 
            ephemeral=True
        )
        return
    
    await interaction.response.defer()
    
    await bot.cleanup_old_channels(days)
    
    embed = discord.Embed(
        title="🧹 Cleanup Complete",
        description=f"Removed game channels older than {days} days",
        color=0x00ff00
    )
    
    await interaction.followup.send(embed=embed)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_date_input(date_string: str) -> str:
    """
    Validate and normalize date input for soccer API
    
    Args:
        date_string: Date in MM/DD/YYYY, DD-MM-YYYY, or YYYY-MM-DD format
        
    Returns:
        Normalized date string in YYYY-MM-DD format
        
    Raises:
        ValueError: If date format is invalid or date is out of range
    """
    allowed_formats = ["%m/%d/%Y", "%d-%m-%Y", "%Y-%m-%d"]
    
    for fmt in allowed_formats:
        try:
            parsed_date = datetime.strptime(date_string, fmt)
            # Validate date is not too far in past/future
            if not (datetime.now() - timedelta(days=30) <= parsed_date <= datetime.now() + timedelta(days=365)):
                raise ValueError("Date must be within 30 days past to 1 year future")
            return parsed_date.strftime("%Y-%m-%d")  # Normalize to YYYY-MM-DD format
        except ValueError:
            continue
    
    raise ValueError(f"Invalid date format. Use MM/DD/YYYY, DD-MM-YYYY, or YYYY-MM-DD")

async def handle_soccer_channel_creation(interaction: discord.Interaction, date: str):
    """
    Handle soccer-specific channel creation workflow
    
    Args:
        interaction: Discord interaction object
        date: Validated date string in YYYY-MM-DD format
    """
    try:
        # Import soccer MCP client here to avoid circular imports
        from soccer_integration import SoccerMCPClient
        
        # Initialize MCP client
        soccer_client = SoccerMCPClient()
        
        # Fetch matches for the date
        try:
            matches_data = await soccer_client.get_matches_for_date(date)
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to fetch soccer matches: {e}")
            embed = discord.Embed(
                title="❌ MCP Server Error",
                description="Failed to connect to Soccer MCP server. Please try again later.",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Process matches data
        if not matches_data or 'matches_by_league' not in matches_data:
            embed = discord.Embed(
                title="📅 No Matches Found",
                description=f"No soccer matches found for {date}",
                color=0xffa500
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Process and create channels
        processed_matches = bot.soccer_data_processor.process_match_data(matches_data)
        
        if not processed_matches:
            embed = discord.Embed(
                title="📅 No Valid Matches",
                description=f"No valid soccer matches found for {date}",
                color=0xffa500
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Create channels using SoccerChannelManager
        created_channels = await bot.soccer_channel_manager.create_match_channels(
            processed_matches, date, interaction.guild
        )
        
        if not created_channels:
            embed = discord.Embed(
                title="❌ Channel Creation Failed",
                description="Failed to create soccer match channels",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Success response
        embed = discord.Embed(
            title="✅ Soccer Channels Created",
            description=f"Successfully created {len(created_channels)} soccer match channels for {date}",
            color=0x00ff00
        )
        
        # Add channel list (limit to first 10 to avoid embed limits)
        channel_list = []
        for i, channel in enumerate(created_channels[:10]):
            channel_list.append(f"{i+1}. {channel.mention}")
        
        if channel_list:
            embed.add_field(
                name="📊 Created Channels",
                value="\n".join(channel_list),
                inline=False
            )
        
        if len(created_channels) > 10:
            embed.add_field(
                name="ℹ️ Note",
                value=f"Showing first 10 of {len(created_channels)} channels",
                inline=False
            )
        
        # Add match summary by league
        league_summary = {}
        for match in processed_matches:
            league_name = match.league.name
            if league_name not in league_summary:
                league_summary[league_name] = 0
            league_summary[league_name] += 1
        
        if league_summary:
            summary_text = []
            for league, count in league_summary.items():
                summary_text.append(f"⚽ {league}: {count} matches")
            
            embed.add_field(
                name="🏆 Leagues",
                value="\n".join(summary_text),
                inline=True
            )
        
        embed.set_footer(text=f"Date: {date} | Soccer Bot")
        await interaction.followup.send(embed=embed)
        
        # Post initial content to each channel
        for channel, match in zip(created_channels, processed_matches):
            try:
                match_embed = bot.soccer_embed_builder.create_match_preview_embed(match)
                await channel.send(embed=match_embed)
            except Exception as e:
                logging.getLogger(__name__).error(f"Failed to post initial content to {channel.name}: {e}")
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Error in handle_soccer_channel_creation: {e}")
        embed = discord.Embed(
            title="❌ Unexpected Error",
            description="An unexpected error occurred during channel creation",
            color=0xff0000
        )
        await interaction.followup.send(embed=embed)

async def send_game_analysis(channel: discord.TextChannel, 
                           team1: str, 
                           team2: str, 
                           game_data: dict):
    """Send comprehensive game analysis to specific channel"""
    
    embed = discord.Embed(
        title=f"📊 {team1} vs {team2}",
        description="Pre-Game Analysis",
        color=0x0099ff,
        timestamp=datetime.now()
    )
    
    # Game information
    embed.add_field(
        name="🏟️ Game Info",
        value=f"**Date:** {game_data.get('date', 'TBD')}\n"
              f"**Time:** {game_data.get('time', 'TBD')}\n"
              f"**Venue:** {game_data.get('venue', 'TBD')}",
        inline=True
    )
    
    # Betting lines
    embed.add_field(
        name="💰 Betting Lines",
        value=f"**Spread:** {game_data.get('spread', 'TBD')}\n"
              f"**Total:** {game_data.get('total', 'TBD')}\n"
              f"**Moneyline:** {game_data.get('moneyline', 'TBD')}",
        inline=True
    )
    
    # AI Prediction
    embed.add_field(
        name="🤖 AI Analysis",
        value="*MCP integration pending*\n"
              "Detailed analysis coming soon",
        inline=False
    )
    
    embed.set_footer(text="Sports Betting Bot | Data from MCP Servers")
    
    await channel.send(embed=embed)

# ============================================================================
# SOCCER-SPECIFIC SLASH COMMANDS
# ============================================================================

@bot.tree.command(name="soccer-schedule", description="Display upcoming soccer matches for current day")
@discord.app_commands.describe(
    league="Optional league filter (EPL, La Liga, MLS, Bundesliga, Serie A, UEFA)",
    date="Optional date in MM/DD/YYYY, DD-MM-YYYY, or YYYY-MM-DD format (defaults to today)"
)
@discord.app_commands.choices(league=[
    discord.app_commands.Choice(name="Premier League", value="EPL"),
    discord.app_commands.Choice(name="La Liga", value="La Liga"),
    discord.app_commands.Choice(name="MLS", value="MLS"),
    discord.app_commands.Choice(name="Bundesliga", value="Bundesliga"),
    discord.app_commands.Choice(name="Serie A", value="Serie A"),
    discord.app_commands.Choice(name="UEFA Champions League", value="UEFA")
])
async def soccer_schedule_command(interaction: discord.Interaction, 
                                league: discord.app_commands.Choice[str] = None, 
                                date: str = None):
    """Display upcoming soccer matches for current day or specified date"""
    
    await interaction.response.defer()
    
    try:
        # Import soccer components
        from soccer_integration import SoccerMCPClient, SoccerDataProcessor, SoccerEmbedBuilder
        
        # Initialize components
        soccer_client = SoccerMCPClient()
        soccer_processor = SoccerDataProcessor()
        soccer_embed_builder = SoccerEmbedBuilder()
        
        # Use current date if none provided
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        else:
            try:
                date = validate_date_input(date)
            except ValueError as e:
                embed = discord.Embed(
                    title="❌ Invalid Date Format",
                    description=str(e),
                    color=0xff0000
                )
                await interaction.followup.send(embed=embed)
                return
        
        # Get league filter value
        league_filter = league.value if league else None
        
        # Fetch matches from MCP server
        try:
            matches_data = await soccer_client.get_matches_for_date(date, league_filter)
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to fetch soccer schedule: {e}")
            embed = discord.Embed(
                title="❌ MCP Server Error",
                description="Failed to connect to Soccer MCP server. Please try again later.",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Process matches data
        processed_matches = soccer_processor.process_match_data(matches_data)
        
        if not processed_matches:
            league_text = f" for {league.name}" if league else ""
            embed = discord.Embed(
                title="📅 No Matches Found",
                description=f"No soccer matches found{league_text} on {date}",
                color=0xffa500
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Create schedule embed
        embed = discord.Embed(
            title=f"⚽ Soccer Schedule - {date}",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        
        if league_filter:
            embed.add_field(name="🏆 League Filter", value=league.name, inline=True)
        
        # Group matches by league
        matches_by_league = {}
        for match in processed_matches:
            league_name = match.league.name
            if league_name not in matches_by_league:
                matches_by_league[league_name] = []
            matches_by_league[league_name].append(match)
        
        # Add matches to embed (limit to avoid embed size limits)
        total_matches = 0
        for league_name, league_matches in matches_by_league.items():
            if total_matches >= 20:  # Limit total matches displayed
                break
                
            match_list = []
            for match in league_matches[:8]:  # Limit matches per league
                time_str = match.display_time
                match_str = f"⚽ **{match.away_team.name}** vs **{match.home_team.name}**"
                if time_str != "TBD":
                    match_str += f" - {time_str}"
                if match.venue and match.venue != "TBD":
                    match_str += f"\n   📍 {match.venue}"
                match_list.append(match_str)
                total_matches += 1
            
            if match_list:
                field_value = "\n\n".join(match_list)
                if len(league_matches) > 8:
                    field_value += f"\n\n*... and {len(league_matches) - 8} more matches*"
                
                embed.add_field(
                    name=f"🏆 {league_name}",
                    value=field_value,
                    inline=False
                )
        
        # Add summary
        embed.add_field(
            name="📊 Summary",
            value=f"Total matches: {len(processed_matches)} across {len(matches_by_league)} leagues",
            inline=False
        )
        
        embed.set_footer(text="Use /create-channels to create match discussion channels")
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Error in soccer-schedule command: {e}")
        embed = discord.Embed(
            title="❌ Command Error",
            description="An unexpected error occurred while fetching the schedule",
            color=0xff0000
        )
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="soccer-odds", description="Get betting odds for a specific soccer matchup")
@discord.app_commands.describe(
    team1="First team name (away team)",
    team2="Second team name (home team)",
    date="Optional date in MM/DD/YYYY, DD-MM-YYYY, or YYYY-MM-DD format (defaults to today)"
)
async def soccer_odds_command(interaction: discord.Interaction, 
                            team1: str, 
                            team2: str, 
                            date: str = None):
    """Display betting odds for specific matchup"""
    
    await interaction.response.defer()
    
    try:
        # Import soccer components
        from soccer_integration import SoccerMCPClient, SoccerDataProcessor, SoccerEmbedBuilder
        
        # Initialize components
        soccer_client = SoccerMCPClient()
        soccer_processor = SoccerDataProcessor()
        soccer_embed_builder = SoccerEmbedBuilder()
        
        # Use current date if none provided
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        else:
            try:
                date = validate_date_input(date)
            except ValueError as e:
                embed = discord.Embed(
                    title="❌ Invalid Date Format",
                    description=str(e),
                    color=0xff0000
                )
                await interaction.followup.send(embed=embed)
                return
        
        # Fetch matches for the date
        try:
            matches_data = await soccer_client.get_matches_for_date(date)
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to fetch soccer matches for odds: {e}")
            embed = discord.Embed(
                title="❌ MCP Server Error",
                description="Failed to connect to Soccer MCP server. Please try again later.",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Process matches and find the requested matchup
        processed_matches = soccer_processor.process_match_data(matches_data)
        
        # Search for matching teams (case-insensitive, partial matching)
        matching_match = None
        team1_lower = team1.lower()
        team2_lower = team2.lower()
        
        for match in processed_matches:
            home_name_lower = match.home_team.name.lower()
            away_name_lower = match.away_team.name.lower()
            
            # Check if team names match (either order)
            if ((team1_lower in home_name_lower or home_name_lower in team1_lower) and
                (team2_lower in away_name_lower or away_name_lower in team2_lower)) or \
               ((team1_lower in away_name_lower or away_name_lower in team1_lower) and
                (team2_lower in home_name_lower or home_name_lower in team2_lower)):
                matching_match = match
                break
        
        if not matching_match:
            embed = discord.Embed(
                title="❌ Match Not Found",
                description=f"No match found between **{team1}** and **{team2}** on {date}",
                color=0xff0000
            )
            embed.add_field(
                name="💡 Tip",
                value="Try using partial team names or check the date. Use `/soccer-schedule` to see available matches.",
                inline=False
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Create betting odds embed
        if matching_match.odds and matching_match.odds.has_odds:
            odds_embed = soccer_embed_builder.create_betting_odds_embed(matching_match)
        else:
            # Create a basic match info embed if no odds available
            odds_embed = discord.Embed(
                title=f"⚽ {matching_match.away_team.name} vs {matching_match.home_team.name}",
                description="Match found but no betting odds available",
                color=0xffa500
            )
            odds_embed.add_field(
                name="🏆 League",
                value=matching_match.league.name,
                inline=True
            )
            odds_embed.add_field(
                name="📅 Date",
                value=matching_match.date,
                inline=True
            )
            odds_embed.add_field(
                name="⏰ Time",
                value=matching_match.display_time,
                inline=True
            )
            if matching_match.venue and matching_match.venue != "TBD":
                odds_embed.add_field(
                    name="🏟️ Venue",
                    value=matching_match.venue,
                    inline=False
                )
        
        await interaction.followup.send(embed=odds_embed)
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Error in soccer-odds command: {e}")
        embed = discord.Embed(
            title="❌ Command Error",
            description="An unexpected error occurred while fetching betting odds",
            color=0xff0000
        )
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="soccer-h2h", description="Get comprehensive head-to-head analysis between two teams")
@discord.app_commands.describe(
    team1="First team name",
    team2="Second team name"
)
async def soccer_h2h_command(interaction: discord.Interaction, 
                           team1: str, 
                           team2: str):
    """Display comprehensive head-to-head analysis"""
    
    await interaction.response.defer()
    
    try:
        # Import soccer components
        from soccer_integration import SoccerMCPClient, SoccerDataProcessor, SoccerEmbedBuilder
        
        # Initialize components
        soccer_client = SoccerMCPClient()
        soccer_processor = SoccerDataProcessor()
        soccer_embed_builder = SoccerEmbedBuilder()
        
        # First, try to find team IDs by searching recent matches
        try:
            # Get matches from the last few days to find team IDs
            recent_dates = []
            for i in range(7):  # Check last 7 days
                check_date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                recent_dates.append(check_date)
            
            team1_id = None
            team2_id = None
            team1_obj = None
            team2_obj = None
            league_obj = None
            
            # Search through recent matches to find team IDs
            for check_date in recent_dates:
                if team1_id and team2_id:
                    break
                    
                try:
                    matches_data = await soccer_client.get_matches_for_date(check_date)
                    processed_matches = soccer_processor.process_match_data(matches_data)
                    
                    for match in processed_matches:
                        home_name_lower = match.home_team.name.lower()
                        away_name_lower = match.away_team.name.lower()
                        team1_lower = team1.lower()
                        team2_lower = team2.lower()
                        
                        # Check for team1
                        if not team1_id and (team1_lower in home_name_lower or home_name_lower in team1_lower):
                            team1_id = match.home_team.id
                            team1_obj = match.home_team
                            league_obj = match.league
                        elif not team1_id and (team1_lower in away_name_lower or away_name_lower in team1_lower):
                            team1_id = match.away_team.id
                            team1_obj = match.away_team
                            league_obj = match.league
                        
                        # Check for team2
                        if not team2_id and (team2_lower in home_name_lower or home_name_lower in team2_lower):
                            team2_id = match.home_team.id
                            team2_obj = match.home_team
                            league_obj = match.league
                        elif not team2_id and (team2_lower in away_name_lower or away_name_lower in team2_lower):
                            team2_id = match.away_team.id
                            team2_obj = match.away_team
                            league_obj = match.league
                        
                        if team1_id and team2_id:
                            break
                            
                except Exception:
                    continue  # Try next date
            
            if not team1_id or not team2_id:
                embed = discord.Embed(
                    title="❌ Teams Not Found",
                    description=f"Could not find team IDs for **{team1}** and/or **{team2}**",
                    color=0xff0000
                )
                embed.add_field(
                    name="💡 Tip",
                    value="Make sure the team names are spelled correctly. Teams must have played recently to be found.",
                    inline=False
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Fetch H2H analysis
            try:
                h2h_data = await soccer_client.get_h2h_analysis(team1_id, team2_id)
            except Exception as e:
                logging.getLogger(__name__).error(f"Failed to fetch H2H data: {e}")
                embed = discord.Embed(
                    title="❌ H2H Data Error",
                    description="Failed to fetch head-to-head analysis from MCP server",
                    color=0xff0000
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Process H2H data into insights
            if not h2h_data or not isinstance(h2h_data, dict):
                embed = discord.Embed(
                    title="❌ No H2H Data",
                    description=f"No head-to-head data available between **{team1_obj.name}** and **{team2_obj.name}**",
                    color=0xffa500
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create H2HInsights object from raw data
            from soccer_integration import H2HInsights
            
            h2h_insights = H2HInsights(
                total_meetings=h2h_data.get('total_meetings', 0),
                home_team_wins=h2h_data.get('team2_wins', 0),  # team2 is home in our context
                away_team_wins=h2h_data.get('team1_wins', 0),  # team1 is away in our context
                draws=h2h_data.get('draws', 0),
                avg_goals_per_game=h2h_data.get('avg_goals_per_game', 0.0),
                recent_form=h2h_data.get('recent_form', {}),
                betting_recommendations=h2h_data.get('betting_recommendations', []),
                key_statistics=h2h_data.get('key_statistics', {})
            )
            
            # Create H2H analysis embed
            h2h_embed = soccer_embed_builder.create_h2h_analysis_embed(
                h2h_insights, team1_obj, team2_obj, league_obj
            )
            
            await interaction.followup.send(embed=h2h_embed)
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Error processing H2H request: {e}")
            embed = discord.Embed(
                title="❌ Processing Error",
                description="Failed to process head-to-head analysis request",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
            return
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Error in soccer-h2h command: {e}")
        embed = discord.Embed(
            title="❌ Command Error",
            description="An unexpected error occurred while fetching head-to-head analysis",
            color=0xff0000
        )
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="soccer-standings", description="Display current league table for a soccer league")
@discord.app_commands.describe(
    league="Select the league to display standings for"
)
@discord.app_commands.choices(league=[
    discord.app_commands.Choice(name="Premier League", value="EPL"),
    discord.app_commands.Choice(name="La Liga", value="La Liga"),
    discord.app_commands.Choice(name="MLS", value="MLS"),
    discord.app_commands.Choice(name="Bundesliga", value="Bundesliga"),
    discord.app_commands.Choice(name="Serie A", value="Serie A"),
    discord.app_commands.Choice(name="UEFA Champions League", value="UEFA")
])
async def soccer_standings_command(interaction: discord.Interaction, 
                                 league: discord.app_commands.Choice[str]):
    """Display current league standings"""
    
    await interaction.response.defer()
    
    try:
        # Import soccer components
        from soccer_integration import SoccerMCPClient, SoccerEmbedBuilder, SUPPORTED_LEAGUES, League
        
        # Initialize components
        soccer_client = SoccerMCPClient()
        soccer_embed_builder = SoccerEmbedBuilder()
        
        # Get league configuration
        league_key = league.value
        if league_key not in SUPPORTED_LEAGUES:
            embed = discord.Embed(
                title="❌ Unsupported League",
                description=f"League {league.name} is not currently supported",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
            return
        
        league_config = SUPPORTED_LEAGUES[league_key]
        league_id = league_config["id"]
        
        # Create League object for embed styling
        league_obj = League(
            id=league_id,
            name=league_config["name"],
            country=league_config["country"]
        )
        
        # Fetch league standings
        try:
            standings_data = await soccer_client.get_league_standings(league_id)
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to fetch league standings: {e}")
            embed = discord.Embed(
                title="❌ MCP Server Error",
                description=f"Failed to fetch standings for {league.name}. Please try again later.",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Create standings embed
        if not standings_data or 'standings' not in standings_data:
            embed = discord.Embed(
                title="❌ No Standings Data",
                description=f"No standings data available for {league.name}",
                color=0xffa500
            )
            await interaction.followup.send(embed=embed)
            return
        
        standings_embed = soccer_embed_builder.create_league_standings_embed(standings_data, league_obj)
        await interaction.followup.send(embed=standings_embed)
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Error in soccer-standings command: {e}")
        embed = discord.Embed(
            title="❌ Command Error",
            description="An unexpected error occurred while fetching league standings",
            color=0xff0000
        )
        await interaction.followup.send(embed=embed)

# ============================================================================
# BOT STARTUP
# ============================================================================

if __name__ == "__main__":
    print("Starting Sports Betting Discord Bot...")
    print("Make sure to set BOT_TOKEN environment variable")
    
    # In production, load from environment variables
    # bot.run(os.getenv('DISCORD_BOT_TOKEN'))
    
    # For development
    print("Bot structure ready - add your Discord bot token to run")