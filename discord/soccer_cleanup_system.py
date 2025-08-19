"""
Soccer Channel Cleanup and Maintenance System
Provides automated cleanup, manual cleanup commands, and maintenance statistics
"""

import asyncio
import discord
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from discord.ext import commands, tasks

# Import enhanced error handling system
from soccer_error_handling import (
    SoccerBotError, DiscordAPIError, ErrorContext, ErrorSeverity,
    retry_with_backoff, GracefulDegradation, error_handler, bot_logger
)

@dataclass
class CleanupStats:
    """Statistics for cleanup operations"""
    channels_deleted: int = 0
    channels_preserved: int = 0
    channels_with_activity: int = 0
    channels_with_pins: int = 0
    errors: int = 0
    total_processed: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Calculate cleanup duration"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_processed == 0:
            return 0.0
        return ((self.total_processed - self.errors) / self.total_processed) * 100

@dataclass
class ChannelInfo:
    """Information about a channel for cleanup decisions"""
    channel: discord.TextChannel
    created_at: datetime
    last_message_at: Optional[datetime] = None
    has_pinned_messages: bool = False
    message_count: int = 0
    is_match_channel: bool = False
    match_date: Optional[datetime] = None
    priority_score: int = 0  # Higher score = higher priority to keep

class SoccerCleanupSystem:
    """
    Automated channel cleanup and maintenance system for soccer channels
    Handles scheduled cleanup, manual cleanup commands, and maintenance statistics
    """
    
    def __init__(self, bot, soccer_channel_manager):
        """
        Initialize the cleanup system
        
        Args:
            bot: Discord bot instance
            soccer_channel_manager: SoccerChannelManager instance
        """
        self.bot = bot
        self.soccer_channel_manager = soccer_channel_manager
        self.logger = logging.getLogger(f"{__name__}.SoccerCleanupSystem")
        
        # Cleanup configuration
        self.default_retention_days = 3
        self.max_channels_per_category = 50
        self.cleanup_batch_size = 10  # Process channels in batches to avoid rate limits
        self.cleanup_delay_between_batches = 2.0  # Seconds between batches
        self.cleanup_delay_between_channels = 0.5  # Seconds between individual channel operations
        
        # Activity thresholds
        self.recent_activity_hours = 24  # Consider activity within last 24 hours as "recent"
        self.min_messages_for_preservation = 5  # Minimum messages to consider preserving
        
        # Cleanup statistics
        self.last_cleanup_stats: Optional[CleanupStats] = None
        self.total_cleanups_performed = 0
        
        # Start scheduled cleanup task
        self.scheduled_cleanup_task.start()
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.scheduled_cleanup_task.cancel()
    
    @tasks.loop(hours=6)  # Run every 6 hours
    async def scheduled_cleanup_task(self):
        """Scheduled cleanup task that runs automatically"""
        try:
            self.logger.info("Starting scheduled cleanup task")
            
            # Run cleanup for all guilds
            for guild in self.bot.guilds:
                try:
                    context = ErrorContext(
                        "scheduled_cleanup",
                        guild_id=guild.id,
                        additional_data={"cleanup_type": "scheduled"}
                    )
                    
                    stats = await self.cleanup_old_channels(
                        guild, 
                        days_old=self.default_retention_days,
                        context=context
                    )
                    
                    # Log cleanup results
                    if stats.channels_deleted > 0 or stats.errors > 0:
                        self.logger.info(
                            f"Scheduled cleanup for {guild.name}: "
                            f"deleted {stats.channels_deleted}, "
                            f"preserved {stats.channels_preserved}, "
                            f"errors {stats.errors}"
                        )
                    
                    # Notify administrators if there were significant changes or errors
                    await self._notify_administrators_if_needed(guild, stats, "scheduled")
                    
                except Exception as e:
                    self.logger.error(f"Error in scheduled cleanup for guild {guild.name}: {e}")
                    continue
            
            self.total_cleanups_performed += 1
            self.logger.info("Scheduled cleanup task completed")
            
        except Exception as e:
            self.logger.error(f"Error in scheduled cleanup task: {e}")
    
    @scheduled_cleanup_task.before_loop
    async def before_scheduled_cleanup(self):
        """Wait for bot to be ready before starting scheduled cleanup"""
        await self.bot.wait_until_ready()
    
    async def cleanup_old_channels(self, guild: discord.Guild, days_old: int = None, 
                                 preserve_active: bool = True, preserve_pinned: bool = True,
                                 context: Optional[ErrorContext] = None) -> CleanupStats:
        """
        Clean up old soccer channels with comprehensive preservation logic
        
        Args:
            guild: Discord guild object
            days_old: Number of days old for cleanup (defaults to retention policy)
            preserve_active: Whether to preserve channels with recent activity
            preserve_pinned: Whether to preserve channels with pinned messages
            context: Error context for logging
            
        Returns:
            CleanupStats object with cleanup results
        """
        # Create context if not provided
        if context is None:
            context = ErrorContext(
                "cleanup_old_channels",
                guild_id=guild.id,
                additional_data={
                    "days_old": days_old or self.default_retention_days,
                    "preserve_active": preserve_active,
                    "preserve_pinned": preserve_pinned
                }
            )
        
        # Initialize statistics
        stats = CleanupStats(start_time=datetime.utcnow())
        
        try:
            # Log operation start
            bot_logger.log_operation_start("cleanup_old_channels", context)
            
            # Use default retention if not specified
            if days_old is None:
                days_old = self.default_retention_days
            
            # Find soccer category
            soccer_category = await self._find_soccer_category(guild)
            if not soccer_category:
                self.logger.info(f"No soccer category found in guild {guild.name}")
                stats.end_time = datetime.utcnow()
                return stats
            
            # Get all soccer match channels
            match_channels = await self._get_soccer_match_channels(soccer_category)
            stats.total_processed = len(match_channels)
            
            if not match_channels:
                self.logger.info(f"No soccer match channels found for cleanup in {guild.name}")
                stats.end_time = datetime.utcnow()
                return stats
            
            # Analyze channels for cleanup decisions
            channel_analysis = await self._analyze_channels_for_cleanup(
                match_channels, days_old, preserve_active, preserve_pinned, context
            )
            
            # Process channels in batches to avoid rate limits
            channels_to_delete = [info for info in channel_analysis if info.priority_score == 0]
            channels_to_preserve = [info for info in channel_analysis if info.priority_score > 0]
            
            # Update preservation statistics
            stats.channels_preserved = len(channels_to_preserve)
            stats.channels_with_activity = len([info for info in channels_to_preserve 
                                              if info.last_message_at and 
                                              info.last_message_at > datetime.utcnow() - timedelta(hours=self.recent_activity_hours)])
            stats.channels_with_pins = len([info for info in channels_to_preserve if info.has_pinned_messages])
            
            # Delete channels in batches
            if channels_to_delete:
                deleted_count = await self._delete_channels_in_batches(channels_to_delete, context)
                stats.channels_deleted = deleted_count
                stats.errors = len(channels_to_delete) - deleted_count
            
            # Store cleanup statistics
            stats.end_time = datetime.utcnow()
            self.last_cleanup_stats = stats
            
            # Log successful operation
            bot_logger.log_operation_success(
                "cleanup_old_channels",
                context,
                stats.duration.total_seconds() if stats.duration else 0,
                f"Deleted {stats.channels_deleted}, preserved {stats.channels_preserved}, errors {stats.errors}"
            )
            
            self.logger.info(
                f"Cleanup completed for {guild.name}: "
                f"processed {stats.total_processed}, "
                f"deleted {stats.channels_deleted}, "
                f"preserved {stats.channels_preserved}, "
                f"errors {stats.errors}"
            )
            
            return stats
            
        except Exception as e:
            stats.end_time = datetime.utcnow()
            stats.errors += 1
            
            error = SoccerBotError(
                f"Unexpected error in cleanup_old_channels: {str(e)}",
                ErrorSeverity.HIGH,
                context
            )
            bot_logger.log_operation_error("cleanup_old_channels", error, context)
            return stats
    
    async def _find_soccer_category(self, guild: discord.Guild) -> Optional[discord.CategoryChannel]:
        """Find the soccer category in the guild"""
        return discord.utils.get(guild.categories, name=self.soccer_channel_manager.category_name)
    
    async def _get_soccer_match_channels(self, category: discord.CategoryChannel) -> List[discord.TextChannel]:
        """Get all soccer match channels from the category"""
        return [
            channel for channel in category.channels 
            if isinstance(channel, discord.TextChannel) and 
            channel.name.startswith(self.soccer_channel_manager.channel_prefix)
        ]
    
    async def _analyze_channels_for_cleanup(self, channels: List[discord.TextChannel], 
                                          days_old: int, preserve_active: bool, 
                                          preserve_pinned: bool, context: ErrorContext) -> List[ChannelInfo]:
        """
        Analyze channels to determine which should be preserved or deleted
        
        Args:
            channels: List of channels to analyze
            days_old: Age threshold for cleanup
            preserve_active: Whether to preserve channels with recent activity
            preserve_pinned: Whether to preserve channels with pinned messages
            context: Error context for logging
            
        Returns:
            List of ChannelInfo objects with priority scores
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        channel_analysis = []
        
        for channel in channels:
            try:
                info = ChannelInfo(
                    channel=channel,
                    created_at=channel.created_at,
                    is_match_channel=True
                )
                
                # Extract match date from channel name if possible
                info.match_date = self._extract_match_date_from_channel(channel)
                
                # Check for recent activity if preservation is enabled
                if preserve_active:
                    info.last_message_at = await self._get_last_message_time(channel)
                    info.message_count = await self._get_message_count(channel, cutoff_date)
                
                # Check for pinned messages if preservation is enabled
                if preserve_pinned:
                    info.has_pinned_messages = await self._has_pinned_messages(channel)
                
                # Calculate priority score
                info.priority_score = self._calculate_priority_score(info, cutoff_date, preserve_active, preserve_pinned)
                
                channel_analysis.append(info)
                
            except Exception as e:
                self.logger.error(f"Error analyzing channel {channel.name}: {e}")
                # Create basic info for error case
                info = ChannelInfo(
                    channel=channel,
                    created_at=channel.created_at,
                    priority_score=1  # Preserve on error to be safe
                )
                channel_analysis.append(info)
        
        return channel_analysis
    
    def _extract_match_date_from_channel(self, channel: discord.TextChannel) -> Optional[datetime]:
        """Extract match date from channel name"""
        try:
            # Channel format: 📊 MM-DD-team1-vs-team2
            parts = channel.name.split('-')
            if len(parts) >= 2:
                month_day = f"{parts[1]}-{parts[2]}"  # MM-DD
                current_year = datetime.now().year
                
                # Try current year first, then next year
                for year in [current_year, current_year + 1]:
                    try:
                        match_date = datetime.strptime(f"{year}-{month_day}", "%Y-%m-%d")
                        return match_date
                    except ValueError:
                        continue
        except Exception:
            pass
        
        return None
    
    async def _get_last_message_time(self, channel: discord.TextChannel) -> Optional[datetime]:
        """Get the timestamp of the last message in the channel"""
        try:
            async for message in channel.history(limit=1):
                return message.created_at
        except discord.HTTPException:
            pass
        return None
    
    async def _get_message_count(self, channel: discord.TextChannel, after: datetime) -> int:
        """Get count of messages after a specific date"""
        try:
            count = 0
            async for message in channel.history(limit=100, after=after):
                count += 1
            return count
        except discord.HTTPException:
            return 0
    
    async def _has_pinned_messages(self, channel: discord.TextChannel) -> bool:
        """Check if channel has pinned messages"""
        try:
            pinned_messages = await channel.pins()
            return len(pinned_messages) > 0
        except discord.HTTPException:
            return False
    
    def _calculate_priority_score(self, info: ChannelInfo, cutoff_date: datetime, 
                                preserve_active: bool, preserve_pinned: bool) -> int:
        """
        Calculate priority score for channel preservation
        
        Args:
            info: ChannelInfo object
            cutoff_date: Cutoff date for cleanup
            preserve_active: Whether to consider activity
            preserve_pinned: Whether to consider pinned messages
            
        Returns:
            Priority score (0 = delete, >0 = preserve with higher numbers = higher priority)
        """
        score = 0
        
        # Base preservation: channel is newer than cutoff
        if info.created_at > cutoff_date:
            score += 10
        
        # Match date preservation: match is in the future or recent past
        if info.match_date:
            days_from_match = (datetime.now() - info.match_date).days
            if days_from_match < 0:  # Future match
                score += 20
            elif days_from_match <= 1:  # Match was today or yesterday
                score += 15
        
        # Activity preservation
        if preserve_active and info.last_message_at:
            hours_since_activity = (datetime.utcnow() - info.last_message_at).total_seconds() / 3600
            if hours_since_activity <= self.recent_activity_hours:
                score += 15
            elif hours_since_activity <= 72:  # Activity within 3 days
                score += 5
        
        # Message count preservation
        if info.message_count >= self.min_messages_for_preservation:
            score += 5
        
        # Pinned messages preservation
        if preserve_pinned and info.has_pinned_messages:
            score += 10
        
        return score
    
    async def _delete_channels_in_batches(self, channels_to_delete: List[ChannelInfo], 
                                        context: ErrorContext) -> int:
        """
        Delete channels in batches to avoid rate limits
        
        Args:
            channels_to_delete: List of ChannelInfo objects to delete
            context: Error context for logging
            
        Returns:
            Number of successfully deleted channels
        """
        deleted_count = 0
        
        # Process in batches
        for i in range(0, len(channels_to_delete), self.cleanup_batch_size):
            batch = channels_to_delete[i:i + self.cleanup_batch_size]
            
            for channel_info in batch:
                try:
                    await channel_info.channel.delete(
                        reason=f"Automated cleanup - older than retention period"
                    )
                    deleted_count += 1
                    self.logger.info(f"Deleted channel: {channel_info.channel.name}")
                    
                    # Small delay between deletions
                    await asyncio.sleep(self.cleanup_delay_between_channels)
                    
                except discord.HTTPException as e:
                    if e.status == 429:  # Rate limited
                        retry_after = getattr(e, 'retry_after', 5)
                        self.logger.warning(f"Rate limited, waiting {retry_after}s")
                        await asyncio.sleep(retry_after)
                        
                        # Retry the deletion
                        try:
                            await channel_info.channel.delete(
                                reason=f"Automated cleanup - older than retention period (retry)"
                            )
                            deleted_count += 1
                            self.logger.info(f"Deleted channel (retry): {channel_info.channel.name}")
                        except Exception as retry_e:
                            self.logger.error(f"Failed to delete channel {channel_info.channel.name} on retry: {retry_e}")
                    else:
                        self.logger.error(f"Failed to delete channel {channel_info.channel.name}: {e}")
                        
                except Exception as e:
                    self.logger.error(f"Unexpected error deleting channel {channel_info.channel.name}: {e}")
            
            # Delay between batches
            if i + self.cleanup_batch_size < len(channels_to_delete):
                await asyncio.sleep(self.cleanup_delay_between_batches)
        
        return deleted_count
    
    async def _notify_administrators_if_needed(self, guild: discord.Guild, stats: CleanupStats, 
                                             cleanup_type: str):
        """
        Notify administrators if cleanup results warrant attention
        
        Args:
            guild: Discord guild object
            stats: CleanupStats from cleanup operation
            cleanup_type: Type of cleanup ("scheduled" or "manual")
        """
        try:
            # Only notify for significant events
            should_notify = (
                stats.channels_deleted >= 5 or  # Many channels deleted
                stats.errors >= 2 or  # Multiple errors
                (cleanup_type == "scheduled" and stats.channels_deleted > 0)  # Any scheduled deletions
            )
            
            if not should_notify:
                return
            
            # Find a suitable channel to send notifications (admin channel, general, etc.)
            notification_channel = None
            
            # Look for admin/mod channels first
            for channel in guild.text_channels:
                if any(keyword in channel.name.lower() for keyword in ['admin', 'mod', 'staff', 'log']):
                    notification_channel = channel
                    break
            
            # Fallback to system messages channel or first available channel
            if not notification_channel:
                notification_channel = guild.system_channel or guild.text_channels[0] if guild.text_channels else None
            
            if not notification_channel:
                return
            
            # Create notification embed
            embed = discord.Embed(
                title="🧹 Soccer Channel Cleanup Report",
                description=f"Automated cleanup completed for **{guild.name}**",
                color=0x00ff00 if stats.errors == 0 else 0xffa500,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="📊 Statistics",
                value=f"**Processed:** {stats.total_processed} channels\n"
                      f"**Deleted:** {stats.channels_deleted} channels\n"
                      f"**Preserved:** {stats.channels_preserved} channels\n"
                      f"**Errors:** {stats.errors}",
                inline=True
            )
            
            if stats.duration:
                embed.add_field(
                    name="⏱️ Duration",
                    value=f"{stats.duration.total_seconds():.1f} seconds",
                    inline=True
                )
            
            embed.add_field(
                name="🔧 Cleanup Type",
                value=cleanup_type.title(),
                inline=True
            )
            
            if stats.channels_with_activity > 0 or stats.channels_with_pins > 0:
                embed.add_field(
                    name="🛡️ Preservation Reasons",
                    value=f"**Recent Activity:** {stats.channels_with_activity}\n"
                          f"**Pinned Messages:** {stats.channels_with_pins}",
                    inline=False
                )
            
            embed.set_footer(text="Soccer Bot Cleanup System")
            
            await notification_channel.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error sending cleanup notification: {e}")
    
    async def manual_cleanup_command(self, interaction: discord.Interaction, 
                                   days_old: int = None, preserve_active: bool = True, 
                                   preserve_pinned: bool = True) -> CleanupStats:
        """
        Manual cleanup command for administrators
        
        Args:
            interaction: Discord interaction object
            days_old: Number of days old for cleanup
            preserve_active: Whether to preserve channels with recent activity
            preserve_pinned: Whether to preserve channels with pinned messages
            
        Returns:
            CleanupStats object with cleanup results
        """
        context = ErrorContext(
            "manual_cleanup_command",
            guild_id=interaction.guild.id,
            user_id=interaction.user.id,
            additional_data={
                "days_old": days_old or self.default_retention_days,
                "preserve_active": preserve_active,
                "preserve_pinned": preserve_pinned
            }
        )
        
        try:
            # Perform cleanup
            stats = await self.cleanup_old_channels(
                interaction.guild, 
                days_old=days_old,
                preserve_active=preserve_active,
                preserve_pinned=preserve_pinned,
                context=context
            )
            
            return stats
            
        except Exception as e:
            error = SoccerBotError(
                f"Error in manual cleanup command: {str(e)}",
                ErrorSeverity.HIGH,
                context
            )
            bot_logger.log_operation_error("manual_cleanup_command", error, context)
            raise e
    
    def get_cleanup_statistics(self) -> Dict[str, any]:
        """
        Get comprehensive cleanup statistics
        
        Returns:
            Dictionary with cleanup statistics and system information
        """
        stats = {
            "system_info": {
                "total_cleanups_performed": self.total_cleanups_performed,
                "default_retention_days": self.default_retention_days,
                "max_channels_per_category": self.max_channels_per_category,
                "scheduled_cleanup_enabled": not self.scheduled_cleanup_task.is_being_cancelled(),
                "next_scheduled_cleanup": self.scheduled_cleanup_task.next_iteration
            },
            "last_cleanup": None
        }
        
        if self.last_cleanup_stats:
            stats["last_cleanup"] = {
                "start_time": self.last_cleanup_stats.start_time,
                "end_time": self.last_cleanup_stats.end_time,
                "duration_seconds": self.last_cleanup_stats.duration.total_seconds() if self.last_cleanup_stats.duration else None,
                "channels_deleted": self.last_cleanup_stats.channels_deleted,
                "channels_preserved": self.last_cleanup_stats.channels_preserved,
                "channels_with_activity": self.last_cleanup_stats.channels_with_activity,
                "channels_with_pins": self.last_cleanup_stats.channels_with_pins,
                "errors": self.last_cleanup_stats.errors,
                "total_processed": self.last_cleanup_stats.total_processed,
                "success_rate": self.last_cleanup_stats.success_rate
            }
        
        return stats
    
    async def channel_limit_management(self, guild: discord.Guild, 
                                     priority_retention: bool = True) -> Dict[str, int]:
        """
        Manage channel limits with priority-based retention
        
        Args:
            guild: Discord guild object
            priority_retention: Whether to use priority-based retention
            
        Returns:
            Dictionary with management results
        """
        context = ErrorContext(
            "channel_limit_management",
            guild_id=guild.id,
            additional_data={"priority_retention": priority_retention}
        )
        
        results = {
            "channels_removed": 0,
            "channels_remaining": 0,
            "errors": 0
        }
        
        try:
            # Find soccer category
            soccer_category = await self._find_soccer_category(guild)
            if not soccer_category:
                return results
            
            # Get current channel count
            current_channels = await self._get_soccer_match_channels(soccer_category)
            results["channels_remaining"] = len(current_channels)
            
            # Check if we're at or near the limit
            if len(current_channels) < self.max_channels_per_category * 0.9:  # 90% threshold
                return results
            
            # Calculate how many channels to remove
            target_count = int(self.max_channels_per_category * 0.8)  # Reduce to 80% of limit
            channels_to_remove = len(current_channels) - target_count
            
            if channels_to_remove <= 0:
                return results
            
            # Analyze channels for priority-based removal
            channel_analysis = await self._analyze_channels_for_cleanup(
                current_channels, 
                days_old=1,  # More aggressive for limit management
                preserve_active=priority_retention,
                preserve_pinned=priority_retention,
                context=context
            )
            
            # Sort by priority score (lowest first for removal)
            channel_analysis.sort(key=lambda x: x.priority_score)
            
            # Remove lowest priority channels
            channels_to_delete = channel_analysis[:channels_to_remove]
            
            if channels_to_delete:
                deleted_count = await self._delete_channels_in_batches(channels_to_delete, context)
                results["channels_removed"] = deleted_count
                results["channels_remaining"] = len(current_channels) - deleted_count
                results["errors"] = len(channels_to_delete) - deleted_count
            
            self.logger.info(
                f"Channel limit management for {guild.name}: "
                f"removed {results['channels_removed']}, "
                f"remaining {results['channels_remaining']}"
            )
            
            return results
            
        except Exception as e:
            results["errors"] += 1
            error = SoccerBotError(
                f"Error in channel limit management: {str(e)}",
                ErrorSeverity.MEDIUM,
                context
            )
            bot_logger.log_operation_error("channel_limit_management", error, context)
            return results