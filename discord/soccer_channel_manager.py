"""
Soccer Channel Manager Module
Handles Discord channel creation, management, and cleanup for soccer matches
Enhanced with comprehensive error handling and logging
"""

import asyncio
import discord
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Import enhanced error handling system
from soccer_error_handling import (
    SoccerBotError, DiscordAPIError, ErrorContext, ErrorSeverity,
    retry_with_backoff, GracefulDegradation, error_handler, bot_logger
)

# Data classes for soccer integration
from dataclasses import dataclass
from typing import Optional

@dataclass
class Team:
    """Soccer team information"""
    id: int
    name: str
    short_name: str
    logo_url: Optional[str] = None
    country: Optional[str] = None

@dataclass
class League:
    """Soccer league information"""
    id: int
    name: str
    country: str
    season: Optional[str] = None
    logo_url: Optional[str] = None

@dataclass
class ProcessedMatch:
    """Complete processed match data for Discord display"""
    match_id: int
    home_team: Team
    away_team: Team
    league: League
    date: str
    time: str
    venue: str
    status: str
    odds: Optional[object] = None
    h2h_summary: Optional[object] = None


class SoccerChannelManager:
    """
    Manages soccer-specific Discord channel operations with comprehensive analytics enrichment
    Handles channel creation, naming, cleanup, and organization
    """
    
    def __init__(self, bot):
        """
        Initialize the channel manager with comprehensive analytics support
        
        Args:
            bot: Discord bot instance
        """
        self.bot = bot
        self.category_name = "⚽ SOCCER"
        self.channel_prefix = "📊"
        self.logger = logging.getLogger(f"{__name__}.SoccerChannelManager")
        
        # Initialize channel enricher for comprehensive analytics
        from soccer_channel_enricher import SoccerChannelEnricher
        self.enricher = SoccerChannelEnricher()
        
        # Channel management settings
        self.max_channels_per_category = 50  # Discord limit
        self.cleanup_retention_days = 3
        self.channel_name_max_length = 100  # Discord limit
    
    @retry_with_backoff(max_retries=2, base_delay=2.0, exceptions=(discord.HTTPException,))
    async def get_or_create_soccer_category(self, guild: discord.Guild, 
                                          context: Optional[ErrorContext] = None) -> Optional[discord.CategoryChannel]:
        """
        Get existing soccer category or create new one with enhanced error handling
        
        Args:
            guild: Discord guild object
            context: Error context for logging
            
        Returns:
            CategoryChannel object or None if creation fails
        """
        # Create context if not provided
        if context is None:
            context = ErrorContext(
                "get_or_create_soccer_category",
                guild_id=guild.id,
                additional_data={"category_name": self.category_name}
            )
        
        try:
            # Log operation start
            bot_logger.log_operation_start("get_or_create_soccer_category", context)
            
            # Check bot permissions first
            if not await self._validate_category_permissions(guild, context):
                return None
            
            # Check if category already exists
            existing_category = discord.utils.get(guild.categories, name=self.category_name)
            if existing_category:
                self.logger.info(f"Found existing soccer category: {self.category_name}")
                bot_logger.log_operation_success(
                    "get_or_create_soccer_category", 
                    context, 
                    result_summary="Found existing category"
                )
                return existing_category
            
            # Check category limits
            if len(guild.categories) >= 50:  # Discord limit
                error = DiscordAPIError(
                    "Guild has reached maximum category limit (50)",
                    error_code=400,
                    context=context
                )
                bot_logger.log_operation_error("get_or_create_soccer_category", error, context)
                return None
            
            # Create new category
            category = await guild.create_category(
                name=self.category_name,
                reason="Soccer match channels category"
            )
            
            self.logger.info(f"Created new soccer category: {self.category_name}")
            bot_logger.log_operation_success(
                "get_or_create_soccer_category", 
                context, 
                result_summary="Created new category"
            )
            return category
            
        except discord.Forbidden as e:
            error = DiscordAPIError(
                f"Permission denied creating soccer category: {e}",
                error_code=403,
                context=context
            )
            bot_logger.log_operation_error("get_or_create_soccer_category", error, context)
            return None
            
        except discord.HTTPException as e:
            if e.status == 429:  # Rate limited
                error = DiscordAPIError(
                    f"Rate limited creating soccer category: {e}",
                    error_code=429,
                    retry_after=getattr(e, 'retry_after', None),
                    context=context
                )
            else:
                error = DiscordAPIError(
                    f"Discord API error creating soccer category: {e}",
                    error_code=getattr(e, 'status', None),
                    context=context
                )
            
            bot_logger.log_operation_error("get_or_create_soccer_category", error, context)
            raise error  # Let retry decorator handle this
            
        except Exception as e:
            error = SoccerBotError(
                f"Unexpected error creating soccer category: {str(e)}",
                ErrorSeverity.HIGH,
                context
            )
            bot_logger.log_operation_error("get_or_create_soccer_category", error, context)
            return None
    
    async def _validate_category_permissions(self, guild: discord.Guild, context: ErrorContext) -> bool:
        """Validate bot permissions for category management"""
        try:
            bot_member = guild.get_member(self.bot.user.id)
            if not bot_member:
                error = DiscordAPIError(
                    "Bot is not a member of the guild",
                    error_code=404,
                    context=context
                )
                bot_logger.log_operation_error("validate_category_permissions", error, context)
                return False
            
            required_permissions = discord.Permissions(
                manage_channels=True,
                send_messages=True,
                embed_links=True
            )
            
            if not bot_member.guild_permissions >= required_permissions:
                error = DiscordAPIError(
                    "Bot lacks required permissions for category management",
                    error_code=403,
                    context=context
                )
                bot_logger.log_operation_error("validate_category_permissions", error, context)
                return False
            
            return True
            
        except Exception as e:
            error = SoccerBotError(
                f"Error validating permissions: {str(e)}",
                ErrorSeverity.MEDIUM,
                context
            )
            bot_logger.log_operation_error("validate_category_permissions", error, context)
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error creating soccer category: {e}")
            return None
    
    def generate_channel_name(self, match: ProcessedMatch, date: str) -> str:
        """
        Generate Discord channel name for a match
        Format: 📊 {date_short}-{away_team}-vs-{home_team}
        
        Args:
            match: ProcessedMatch object
            date: Date string in YYYY-MM-DD format
            
        Returns:
            Generated channel name
        """
        try:
            # Parse date and format as MM-DD
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            date_short = date_obj.strftime("%m-%d")
            
            # Clean team names for channel use
            away_clean = self._clean_team_name_for_channel(match.away_team.name)
            home_clean = self._clean_team_name_for_channel(match.home_team.name)
            
            # Generate base channel name
            channel_name = f"{self.channel_prefix} {date_short}-{away_clean}-vs-{home_clean}"
            
            # Ensure channel name doesn't exceed Discord's limit
            if len(channel_name) > self.channel_name_max_length:
                # Truncate team names proportionally
                available_length = self.channel_name_max_length - len(f"{self.channel_prefix} {date_short}--vs-")
                team_length = available_length // 2
                
                away_clean = away_clean[:team_length].rstrip('-')
                home_clean = home_clean[:team_length].rstrip('-')
                
                channel_name = f"{self.channel_prefix} {date_short}-{away_clean}-vs-{home_clean}"
            
            self.logger.debug(f"Generated channel name: {channel_name}")
            return channel_name
            
        except Exception as e:
            self.logger.error(f"Error generating channel name: {e}")
            # Fallback to basic name
            return f"{self.channel_prefix} soccer-match-{match.match_id}"
    
    def _clean_team_name_for_channel(self, team_name: str) -> str:
        """
        Clean team name for Discord channel creation
        
        Args:
            team_name: Original team name
            
        Returns:
            Cleaned team name suitable for channel names
        """
        if not team_name or not isinstance(team_name, str):
            return "team"
        
        # Convert to lowercase and replace problematic characters
        cleaned = team_name.lower().strip()
        
        # Handle accented characters
        import unicodedata
        cleaned = unicodedata.normalize('NFD', cleaned)
        cleaned = ''.join(c for c in cleaned if unicodedata.category(c) != 'Mn')
        
        # Replace spaces and special characters
        replacements = {
            ' ': '-',
            '.': '',
            '&': 'and',
            '/': '-',
            '\\': '-',
            '(': '',
            ')': '',
            '[': '',
            ']': '',
            '{': '',
            '}': '',
            '!': '',
            '?': '',
            ',': '',
            ';': '',
            ':': '',
            '"': '',
            "'": '',
            '#': '',
            '@': '',
            '\n': '',
            '\t': '',
            '%': '',
            '^': '',
            '*': '',
            '+': '',
            '=': '',
            '|': '',
            '~': '',
            '`': ''
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        # Remove multiple consecutive dashes
        while '--' in cleaned:
            cleaned = cleaned.replace('--', '-')
        
        # Remove leading/trailing dashes
        cleaned = cleaned.strip('-')
        
        # Ensure it's not empty and not too long
        if not cleaned:
            cleaned = "team"
        
        # Keep team names reasonable for channel names (but preserve full words when possible)
        if len(cleaned) > 20:
            # Try to truncate at word boundaries
            words = cleaned.split('-')
            truncated = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + (1 if truncated else 0) <= 20:
                    truncated.append(word)
                    current_length += len(word) + (1 if truncated else 0)
                else:
                    break
            
            if truncated:
                cleaned = '-'.join(truncated)
            else:
                # Fallback to simple truncation
                cleaned = cleaned[:20].rstrip('-')
        
        return cleaned
    
    async def create_match_channels(self, matches: List[ProcessedMatch], date: str, guild) -> List[discord.TextChannel]:
        """
        Create Discord channels for soccer matches following MLB channel creation logic
        
        Args:
            matches: List of ProcessedMatch objects
            date: Date string in YYYY-MM-DD format
            guild: Discord guild object
            
        Returns:
            List of created TextChannel objects
        """
        if not matches:
            self.logger.info("No matches provided for channel creation")
            return []
        
        created_channels = []
        
        try:
            # Get or create soccer category
            category = await self.get_or_create_soccer_category(guild)
            if not category:
                self.logger.error("Failed to get or create soccer category")
                return []
            
            # Check current channel count in category
            current_channels = len(category.channels)
            if current_channels >= self.max_channels_per_category:
                self.logger.warning(f"Soccer category at channel limit ({current_channels}/{self.max_channels_per_category})")
                # Trigger cleanup before creating new channels
                await self.cleanup_old_channels(guild, days_old=1)
            
            # Create channels for each match
            for match in matches:
                try:
                    channel = await self._create_single_match_channel(match, date, category)
                    if channel:
                        created_channels.append(channel)
                        self.logger.info(f"Created channel for {match.away_team.name} vs {match.home_team.name}")
                    else:
                        self.logger.warning(f"Failed to create channel for match {match.match_id}")
                        
                except Exception as e:
                    self.logger.error(f"Error creating channel for match {match.match_id}: {e}")
                    continue
            
            self.logger.info(f"Successfully created {len(created_channels)} soccer match channels")
            return created_channels
            
        except Exception as e:
            self.logger.error(f"Error in create_match_channels: {e}")
            return created_channels
    
    async def _create_single_match_channel(self, match: ProcessedMatch, date: str, category: discord.CategoryChannel) -> Optional[discord.TextChannel]:
        """
        Create a single match channel with comprehensive analytics content
        
        Args:
            match: ProcessedMatch object
            date: Date string in YYYY-MM-DD format
            category: Discord category to create channel in
            
        Returns:
            Created TextChannel or None if creation fails
        """
        try:
            # Generate channel name
            channel_name = self.generate_channel_name(match, date)
            
            # Check if channel already exists
            existing_channel = discord.utils.get(category.channels, name=channel_name)
            if existing_channel:
                self.logger.info(f"Channel already exists: {channel_name}")
                # Try to enrich existing channel if it's empty
                await self._enrich_existing_channel_if_needed(existing_channel, match, date)
                return existing_channel
            
            # Create channel topic (home vs away format for consistency)
            league_name = match.league.name
            venue_info = f" at {match.venue}" if match.venue and match.venue != "TBD" else ""
            topic = f"{match.home_team.name} vs {match.away_team.name} - {league_name} - {date}{venue_info}"
            
            # Create the channel
            channel = await category.create_text_channel(
                name=channel_name,
                topic=topic,
                reason=f"Soccer match channel for {match.away_team.name} vs {match.home_team.name}"
            )
            
            self.logger.debug(f"Created channel: {channel_name} with topic: {topic}")
            
            # Enrich the channel with comprehensive analytics content
            await self._enrich_new_channel(channel, match, date)
            
            return channel
            
        except discord.HTTPException as e:
            if e.status == 429:  # Rate limited
                self.logger.warning(f"Rate limited creating channel, waiting {e.retry_after}s")
                await asyncio.sleep(e.retry_after)
                return await self._create_single_match_channel(match, date, category)
            else:
                self.logger.error(f"HTTP error creating channel: {e}")
                return None
        except Exception as e:
            self.logger.error(f"Unexpected error creating channel: {e}")
            return None
    
    async def cleanup_old_channels(self, guild, days_old: int = None) -> Dict[str, int]:
        """
        Remove soccer game channels older than specified days with 3-day retention policy
        
        Args:
            guild: Discord guild object
            days_old: Number of days old for cleanup (defaults to retention policy)
            
        Returns:
            Dict with cleanup statistics
        """
        if days_old is None:
            days_old = self.cleanup_retention_days
        
        cleanup_stats = {
            "channels_deleted": 0,
            "channels_preserved": 0,
            "errors": 0
        }
        
        try:
            # Find soccer category
            soccer_category = discord.utils.get(guild.categories, name=self.category_name)
            if not soccer_category:
                self.logger.info("No soccer category found for cleanup")
                return cleanup_stats
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            self.logger.info(f"Starting cleanup of channels older than {days_old} days (before {cutoff_date})")
            
            # Get all soccer match channels
            match_channels = [ch for ch in soccer_category.channels if ch.name.startswith(self.channel_prefix)]
            
            for channel in match_channels:
                try:
                    # Check if channel should be preserved
                    if await self._should_preserve_channel(channel, cutoff_date):
                        cleanup_stats["channels_preserved"] += 1
                        continue
                    
                    # Delete the channel
                    await channel.delete(reason=f"Automated cleanup - older than {days_old} days")
                    cleanup_stats["channels_deleted"] += 1
                    self.logger.info(f"Deleted old channel: {channel.name}")
                    
                    # Add small delay to avoid rate limits
                    await asyncio.sleep(0.5)
                    
                except discord.HTTPException as e:
                    self.logger.error(f"Failed to delete channel {channel.name}: {e}")
                    cleanup_stats["errors"] += 1
                except Exception as e:
                    self.logger.error(f"Unexpected error deleting channel {channel.name}: {e}")
                    cleanup_stats["errors"] += 1
            
            self.logger.info(f"Cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            self.logger.error(f"Error in cleanup_old_channels: {e}")
            cleanup_stats["errors"] += 1
            return cleanup_stats
    
    async def _should_preserve_channel(self, channel: discord.TextChannel, cutoff_date: datetime) -> bool:
        """
        Determine if a channel should be preserved during cleanup
        
        Args:
            channel: Discord text channel
            cutoff_date: Cutoff date for cleanup
            
        Returns:
            True if channel should be preserved, False otherwise
        """
        try:
            # Always preserve if channel is newer than cutoff
            if channel.created_at > cutoff_date:
                return True
            
            # Check for recent activity
            try:
                async for message in channel.history(limit=1, after=cutoff_date):
                    self.logger.debug(f"Preserving {channel.name} due to recent activity")
                    return True
            except discord.HTTPException:
                # If we can't check history, err on the side of caution
                pass
            
            # Check for pinned messages
            try:
                pinned_messages = await channel.pins()
                if pinned_messages:
                    self.logger.debug(f"Preserving {channel.name} due to pinned messages")
                    return True
            except discord.HTTPException:
                pass
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking if channel should be preserved: {e}")
            # Err on the side of caution
            return True
    
    async def update_channel_content(self, channel: discord.TextChannel, match_data: ProcessedMatch) -> bool:
        """
        Update channel content with match information
        
        Args:
            channel: Discord text channel
            match_data: ProcessedMatch object with updated information
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            # This method can be used for future live updates
            # For now, it's a placeholder for the channel management system
            self.logger.info(f"Channel content update requested for {channel.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating channel content: {e}")
            return False
    
    async def create_match_channels(self, matches: List[ProcessedMatch], guild: discord.Guild,
                                  context: Optional[ErrorContext] = None) -> Dict[str, List[discord.TextChannel]]:
        """
        Create Discord channels for soccer matches with comprehensive error handling
        
        Args:
            matches: List of processed match data
            guild: Discord guild object
            context: Error context for logging
            
        Returns:
            Dictionary with created channels organized by league and error information
        """
        # Create context if not provided
        if context is None:
            context = ErrorContext(
                "create_match_channels",
                guild_id=guild.id,
                additional_data={"match_count": len(matches)}
            )
        
        result = {
            "created_channels": {},
            "failed_channels": [],
            "errors": [],
            "total_matches": len(matches),
            "successful_creations": 0,
            "failed_creations": 0
        }
        
        try:
            # Log operation start
            bot_logger.log_operation_start("create_match_channels", context)
            
            # Get or create soccer category
            category = await self.get_or_create_soccer_category(guild, context)
            if not category:
                error_msg = "Failed to get or create soccer category"
                result["errors"].append(error_msg)
                bot_logger.log_operation_error("create_match_channels", 
                                             SoccerBotError(error_msg, ErrorSeverity.HIGH, context), context)
                return result
            
            # Check channel limits
            existing_channels = len(category.channels)
            if existing_channels + len(matches) > self.max_channels_per_category:
                # Attempt cleanup first
                cleaned_count = await self._cleanup_old_channels_in_category(category, context)
                self.logger.info(f"Cleaned up {cleaned_count} old channels to make space")
                
                # Recheck limits
                existing_channels = len(category.channels)
                if existing_channels + len(matches) > self.max_channels_per_category:
                    max_new_channels = self.max_channels_per_category - existing_channels
                    if max_new_channels <= 0:
                        error_msg = f"Category is at maximum capacity ({self.max_channels_per_category} channels)"
                        result["errors"].append(error_msg)
                        return result
                    
                    # Limit matches to what we can create
                    matches = matches[:max_new_channels]
                    self.logger.warning(f"Limited channel creation to {max_new_channels} matches due to capacity")
            
            # Group matches by league for organized creation
            matches_by_league = self._group_matches_by_league(matches)
            
            # Create channels for each league
            for league_name, league_matches in matches_by_league.items():
                league_channels = []
                
                for match in league_matches:
                    try:
                        channel = await self._create_single_match_channel(match, category, context)
                        if channel:
                            league_channels.append(channel)
                            result["successful_creations"] += 1
                            
                            # Add initial match content
                            await self._add_initial_match_content(channel, match, context)
                        else:
                            result["failed_channels"].append({
                                "match_id": match.match_id,
                                "teams": f"{match.away_team.name} vs {match.home_team.name}",
                                "error": "Channel creation returned None"
                            })
                            result["failed_creations"] += 1
                            
                    except Exception as e:
                        error_msg = f"Failed to create channel for match {match.match_id}: {str(e)}"
                        result["failed_channels"].append({
                            "match_id": match.match_id,
                            "teams": f"{match.away_team.name} vs {match.home_team.name}",
                            "error": error_msg
                        })
                        result["errors"].append(error_msg)
                        result["failed_creations"] += 1
                        
                        # Log individual channel creation error
                        channel_context = ErrorContext(
                            "create_single_match_channel",
                            guild_id=guild.id,
                            match_id=match.match_id,
                            additional_data={"teams": f"{match.away_team.name} vs {match.home_team.name}"}
                        )
                        bot_logger.log_operation_error("create_single_match_channel", 
                                                     SoccerBotError(error_msg, ErrorSeverity.MEDIUM, channel_context), 
                                                     channel_context)
                
                if league_channels:
                    result["created_channels"][league_name] = league_channels
            
            # Log overall operation result
            success_rate = (result["successful_creations"] / result["total_matches"]) * 100 if result["total_matches"] > 0 else 0
            bot_logger.log_operation_success(
                "create_match_channels",
                context,
                result_summary=f"Created {result['successful_creations']}/{result['total_matches']} channels ({success_rate:.1f}% success rate)"
            )
            
            return result
            
        except Exception as e:
            error = SoccerBotError(
                f"Unexpected error in create_match_channels: {str(e)}",
                ErrorSeverity.HIGH,
                context
            )
            result["errors"].append(str(e))
            bot_logger.log_operation_error("create_match_channels", error, context)
            return result
    
    @retry_with_backoff(max_retries=2, base_delay=1.0, exceptions=(discord.HTTPException,))
    async def _create_single_match_channel(self, match: ProcessedMatch, category: discord.CategoryChannel,
                                         context: ErrorContext) -> Optional[discord.TextChannel]:
        """Create a single match channel with retry logic"""
        try:
            # Generate channel name
            channel_name = self._generate_channel_name(match)
            
            # Check if channel already exists
            existing_channel = discord.utils.get(category.channels, name=channel_name)
            if existing_channel:
                self.logger.info(f"Channel already exists: {channel_name}")
                return existing_channel
            
            # Create the channel
            channel = await category.create_text_channel(
                name=channel_name,
                reason=f"Soccer match: {match.away_team.name} vs {match.home_team.name}"
            )
            
            self.logger.info(f"Created match channel: {channel_name}")
            return channel
            
        except discord.Forbidden as e:
            raise DiscordAPIError(
                f"Permission denied creating channel for match {match.match_id}",
                error_code=403,
                context=context
            )
        except discord.HTTPException as e:
            if e.status == 429:  # Rate limited
                raise DiscordAPIError(
                    f"Rate limited creating channel for match {match.match_id}",
                    error_code=429,
                    retry_after=getattr(e, 'retry_after', None),
                    context=context
                )
            else:
                raise DiscordAPIError(
                    f"Discord API error creating channel for match {match.match_id}: {e}",
                    error_code=getattr(e, 'status', None),
                    context=context
                )
        except Exception as e:
            raise SoccerBotError(
                f"Unexpected error creating channel for match {match.match_id}: {str(e)}",
                ErrorSeverity.MEDIUM,
                context
            )
    
    def _generate_channel_name(self, match: ProcessedMatch) -> str:
        """Generate Discord channel name for a match with length validation"""
        try:
            # Parse date for short format
            date_obj = datetime.strptime(match.date, "%Y-%m-%d")
            date_short = date_obj.strftime("%m-%d")
            
            # Clean team names for channel naming
            away_clean = self._clean_team_name_for_channel(match.away_team.name)
            home_clean = self._clean_team_name_for_channel(match.home_team.name)
            
            # Generate base name
            base_name = f"{self.channel_prefix} {date_short}-{away_clean}-vs-{home_clean}"
            
            # Ensure name doesn't exceed Discord's limit
            if len(base_name) > self.channel_name_max_length:
                # Truncate team names proportionally
                available_length = self.channel_name_max_length - len(f"{self.channel_prefix} {date_short}--vs-")
                team_length = available_length // 2
                
                away_truncated = away_clean[:team_length].rstrip('-')
                home_truncated = home_clean[:team_length].rstrip('-')
                
                base_name = f"{self.channel_prefix} {date_short}-{away_truncated}-vs-{home_truncated}"
            
            return base_name.lower()
            
        except Exception as e:
            # Fallback to simple naming
            self.logger.warning(f"Error generating channel name for match {match.match_id}: {e}")
            return f"{self.channel_prefix} match-{match.match_id}".lower()
    
    def _clean_team_name_for_channel(self, team_name: str) -> str:
        """Clean team name for Discord channel naming"""
        # Remove special characters and replace spaces with hyphens
        cleaned = team_name.lower()
        cleaned = cleaned.replace(' ', '-')
        cleaned = cleaned.replace('.', '')
        cleaned = cleaned.replace('&', 'and')
        cleaned = cleaned.replace('/', '-')
        cleaned = cleaned.replace('\\', '-')
        cleaned = cleaned.replace('(', '')
        cleaned = cleaned.replace(')', '')
        cleaned = cleaned.replace('[', '')
        cleaned = cleaned.replace(']', '')
        cleaned = cleaned.replace('{', '')
        cleaned = cleaned.replace('}', '')
        cleaned = cleaned.replace('!', '')
        cleaned = cleaned.replace('?', '')
        cleaned = cleaned.replace(',', '')
        cleaned = cleaned.replace(';', '')
        cleaned = cleaned.replace(':', '')
        cleaned = cleaned.replace('"', '')
        cleaned = cleaned.replace("'", '')
        
        # Remove multiple consecutive hyphens
        while '--' in cleaned:
            cleaned = cleaned.replace('--', '-')
        
        # Remove leading/trailing hyphens
        cleaned = cleaned.strip('-')
        
        return cleaned
    
    def _group_matches_by_league(self, matches: List[ProcessedMatch]) -> Dict[str, List[ProcessedMatch]]:
        """Group matches by league for organized channel creation"""
        grouped = {}
        
        for match in matches:
            league_name = match.league.name
            if league_name not in grouped:
                grouped[league_name] = []
            grouped[league_name].append(match)
        
        return grouped
    
    async def _add_initial_match_content(self, channel: discord.TextChannel, match: ProcessedMatch,
                                       context: ErrorContext):
        """Add initial content to a match channel with error handling"""
        try:
            # Import embed builder here to avoid circular imports
            from soccer_integration import SoccerEmbedBuilder
            
            embed_builder = SoccerEmbedBuilder()
            embed = embed_builder.create_match_preview_embed(match)
            
            await channel.send(embed=embed)
            self.logger.debug(f"Added initial content to channel: {channel.name}")
            
        except Exception as e:
            # Log error but don't fail channel creation
            error = SoccerBotError(
                f"Failed to add initial content to channel {channel.name}: {str(e)}",
                ErrorSeverity.LOW,
                context
            )
            bot_logger.log_operation_error("add_initial_match_content", error, context)
    
    async def _cleanup_old_channels_in_category(self, category: discord.CategoryChannel,
                                              context: ErrorContext) -> int:
        """Clean up old channels in the category to make space"""
        cleaned_count = 0
        cutoff_date = datetime.utcnow() - timedelta(days=self.cleanup_retention_days)
        
        try:
            for channel in category.channels:
                if isinstance(channel, discord.TextChannel):
                    # Check if channel is old enough for cleanup
                    if channel.created_at < cutoff_date:
                        try:
                            # Check if channel has recent activity
                            has_recent_activity = await self._check_recent_activity(channel)
                            
                            if not has_recent_activity:
                                await channel.delete(reason="Automated cleanup of old soccer match channel")
                                cleaned_count += 1
                                self.logger.info(f"Cleaned up old channel: {channel.name}")
                                
                                # Add small delay to avoid rate limits
                                await asyncio.sleep(0.5)
                                
                        except Exception as e:
                            self.logger.warning(f"Failed to cleanup channel {channel.name}: {e}")
            
            return cleaned_count
            
        except Exception as e:
            error = SoccerBotError(
                f"Error during channel cleanup: {str(e)}",
                ErrorSeverity.LOW,
                context
            )
            bot_logger.log_operation_error("cleanup_old_channels_in_category", error, context)
            return cleaned_count
    
    async def _check_recent_activity(self, channel: discord.TextChannel) -> bool:
        """Check if channel has recent activity (messages in last 24 hours)"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            async for message in channel.history(limit=10, after=cutoff_time):
                return True  # Found recent message
            
            return False  # No recent messages
            
        except discord.Forbidden:
            # Can't read message history, assume no recent activity
            return False
        except Exception:
            # On any error, assume there's recent activity to be safe
            return True

    # ============================================================================
    # CHANNEL ENRICHMENT METHODS
    # ============================================================================

    async def _enrich_new_channel(self, channel: discord.TextChannel, match: ProcessedMatch, date: str) -> bool:
        """
        Enrich a newly created channel with comprehensive analytics
        
        Args:
            channel: Discord text channel to enrich
            match: ProcessedMatch object with match details
            date: Match date in YYYY-MM-DD format
            
        Returns:
            bool: True if enrichment succeeded, False otherwise
        """
        try:
            # Determine league code from match data
            league_code = self._get_league_code_from_match(match)
            
            # Use enricher to populate channel with comprehensive analytics
            success = await self.enricher.enrich_channel_on_creation(
                channel=channel,
                home_team=match.home_team.name,
                away_team=match.away_team.name,
                match_date=date,
                league_code=league_code
            )
            
            if success:
                self.logger.info(f"Successfully enriched channel {channel.name} with comprehensive analytics")
            else:
                self.logger.warning(f"Channel enrichment failed for {channel.name}, but channel was created")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error enriching channel {channel.name}: {e}")
            # Don't fail channel creation if enrichment fails
            return False

    async def _enrich_existing_channel_if_needed(self, channel: discord.TextChannel, match: ProcessedMatch, date: str) -> bool:
        """
        Enrich an existing channel if it appears to be empty or missing content
        
        Args:
            channel: Existing Discord text channel
            match: ProcessedMatch object with match details
            date: Match date in YYYY-MM-DD format
            
        Returns:
            bool: True if enrichment was performed, False otherwise
        """
        try:
            # Check if channel needs enrichment (has fewer than 3 messages)
            message_count = 0
            async for _ in channel.history(limit=5):
                message_count += 1
            
            # If channel has few messages, it might need enrichment
            if message_count < 3:
                self.logger.info(f"Channel {channel.name} appears empty, enriching with analytics...")
                
                league_code = self._get_league_code_from_match(match)
                
                success = await self.enricher.enrich_channel_on_creation(
                    channel=channel,
                    home_team=match.home_team.name,
                    away_team=match.away_team.name,
                    match_date=date,
                    league_code=league_code
                )
                
                return success
            
            return False  # Channel doesn't need enrichment
            
        except Exception as e:
            self.logger.error(f"Error checking/enriching existing channel {channel.name}: {e}")
            return False

    def _get_league_code_from_match(self, match: ProcessedMatch) -> str:
        """
        Determine league code from match data
        
        Args:
            match: ProcessedMatch object
            
        Returns:
            str: League code for supported leagues (EPL, La Liga, etc.)
        """
        # Map league IDs to codes based on soccer_integration.py SUPPORTED_LEAGUES
        league_id_to_code = {
            228: "EPL",           # Premier League
            297: "La Liga",       # La Liga
            168: "MLS",           # MLS
            241: "Bundesliga",    # Bundesliga
            253: "Serie A",       # Serie A
            310: "UEFA"           # Champions League
        }
        
        # Try to match by league ID first
        if hasattr(match.league, 'id') and match.league.id in league_id_to_code:
            return league_id_to_code[match.league.id]
        
        # Fall back to name matching
        league_name = match.league.name.lower()
        if "premier" in league_name or "england" in league_name:
            return "EPL"
        elif "la liga" in league_name or "spain" in league_name:
            return "La Liga"
        elif "mls" in league_name:
            return "MLS"
        elif "bundesliga" in league_name or "germany" in league_name:
            return "Bundesliga"
        elif "serie a" in league_name or "italy" in league_name:
            return "Serie A"
        elif "champions" in league_name or "uefa" in league_name:
            return "UEFA"
        
        # Default to EPL if can't determine
        return "EPL"
    
    # ============================================================================
    # SINGULAR CHANNEL CREATION METHOD (for compatibility)
    # ============================================================================
    
    async def create_match_channel(self, match: ProcessedMatch) -> Optional[discord.TextChannel]:
        """
        Create a single match channel (compatibility method for bot_structure.py)
        
        Args:
            match: ProcessedMatch object
            
        Returns:
            Created channel or None if failed
        """
        try:
            # Get guild from bot - this is a simplified approach
            guild = None
            if hasattr(self.bot, 'guilds') and self.bot.guilds:
                guild = self.bot.guilds[0]  # Use first guild
            
            if not guild:
                self.logger.error("No guild available for channel creation")
                return None
            
            # Get or create category
            category = await self.get_or_create_soccer_category(guild)
            if not category:
                self.logger.error("Failed to get or create soccer category")
                return None
            
            # Extract date from match
            match_date = match.date or datetime.now().strftime("%Y-%m-%d")
            
            # Create single channel with enrichment
            channel = await self._create_single_match_channel(match, match_date, category)
            
            if channel:
                self.logger.info(f"Successfully created enriched channel: {channel.name}")
                return channel
            else:
                self.logger.error("Failed to create match channel")
                return None
                
        except Exception as e:
            self.logger.error(f"Error in create_match_channel: {e}")
            return None