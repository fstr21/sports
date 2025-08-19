"""
Soccer Cleanup Commands
Slash commands for manual cleanup and maintenance operations
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from datetime import datetime, timedelta

from soccer_cleanup_system import SoccerCleanupSystem

class SoccerCleanupCommands(commands.Cog):
    """Cog containing soccer cleanup slash commands"""
    
    def __init__(self, bot, cleanup_system: SoccerCleanupSystem):
        self.bot = bot
        self.cleanup_system = cleanup_system
    
    @app_commands.command(name="soccer-cleanup", description="Manually clean up old soccer channels")
    @app_commands.describe(
        days_old="Number of days old for cleanup (default: 3)",
        preserve_active="Preserve channels with recent activity (default: True)",
        preserve_pinned="Preserve channels with pinned messages (default: True)",
        dry_run="Show what would be deleted without actually deleting (default: False)"
    )
    async def soccer_cleanup_command(
        self, 
        interaction: discord.Interaction,
        days_old: Optional[int] = None,
        preserve_active: bool = True,
        preserve_pinned: bool = True,
        dry_run: bool = False
    ):
        """Manual cleanup command for administrators"""
        
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You need administrator permissions to use this command.", 
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            # Use default retention if not specified
            if days_old is None:
                days_old = self.cleanup_system.default_retention_days
            
            # Validate days_old parameter
            if days_old < 0 or days_old > 30:
                embed = discord.Embed(
                    title="❌ Invalid Parameter",
                    description="Days old must be between 0 and 30",
                    color=0xff0000
                )
                await interaction.followup.send(embed=embed)
                return
            
            if dry_run:
                # Perform dry run analysis
                embed = await self._perform_dry_run_analysis(
                    interaction.guild, days_old, preserve_active, preserve_pinned
                )
                await interaction.followup.send(embed=embed)
            else:
                # Perform actual cleanup
                stats = await self.cleanup_system.manual_cleanup_command(
                    interaction, days_old, preserve_active, preserve_pinned
                )
                
                # Create result embed
                embed = self._create_cleanup_result_embed(stats, days_old, "manual")
                await interaction.followup.send(embed=embed)
        
        except Exception as e:
            embed = discord.Embed(
                title="❌ Cleanup Error",
                description=f"An error occurred during cleanup: {str(e)}",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="soccer-cleanup-stats", description="Show cleanup system statistics")
    async def soccer_cleanup_stats_command(self, interaction: discord.Interaction):
        """Show cleanup system statistics"""
        
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You need administrator permissions to use this command.", 
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            stats = self.cleanup_system.get_cleanup_statistics()
            embed = self._create_statistics_embed(stats)
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Statistics Error",
                description=f"An error occurred retrieving statistics: {str(e)}",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="soccer-channel-limits", description="Manage soccer channel limits")
    @app_commands.describe(
        priority_retention="Use priority-based retention when managing limits (default: True)"
    )
    async def soccer_channel_limits_command(
        self, 
        interaction: discord.Interaction,
        priority_retention: bool = True
    ):
        """Manage channel limits with priority-based retention"""
        
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You need administrator permissions to use this command.", 
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            results = await self.cleanup_system.channel_limit_management(
                interaction.guild, priority_retention
            )
            
            embed = self._create_limit_management_embed(results, priority_retention)
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Limit Management Error",
                description=f"An error occurred managing channel limits: {str(e)}",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
    
    async def _perform_dry_run_analysis(self, guild: discord.Guild, days_old: int, 
                                      preserve_active: bool, preserve_pinned: bool) -> discord.Embed:
        """Perform dry run analysis and return results embed"""
        
        # Find soccer category
        soccer_category = await self.cleanup_system._find_soccer_category(guild)
        if not soccer_category:
            return discord.Embed(
                title="📊 Dry Run Results",
                description="No soccer category found in this server",
                color=0xffa500
            )
        
        # Get soccer match channels
        match_channels = await self.cleanup_system._get_soccer_match_channels(soccer_category)
        if not match_channels:
            return discord.Embed(
                title="📊 Dry Run Results",
                description="No soccer match channels found for analysis",
                color=0xffa500
            )
        
        # Analyze channels
        from soccer_error_handling import ErrorContext
        context = ErrorContext("dry_run_analysis", guild_id=guild.id)
        
        channel_analysis = await self.cleanup_system._analyze_channels_for_cleanup(
            match_channels, days_old, preserve_active, preserve_pinned, context
        )
        
        # Separate channels by action
        channels_to_delete = [info for info in channel_analysis if info.priority_score == 0]
        channels_to_preserve = [info for info in channel_analysis if info.priority_score > 0]
        
        # Create results embed
        embed = discord.Embed(
            title="📊 Cleanup Dry Run Results",
            description=f"Analysis for channels older than {days_old} days",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📈 Summary",
            value=f"**Total Channels:** {len(match_channels)}\n"
                  f"**Would Delete:** {len(channels_to_delete)}\n"
                  f"**Would Preserve:** {len(channels_to_preserve)}",
            inline=True
        )
        
        # Preservation reasons
        activity_preserved = len([info for info in channels_to_preserve 
                                if info.last_message_at and 
                                info.last_message_at > datetime.utcnow() - timedelta(hours=24)])
        pins_preserved = len([info for info in channels_to_preserve if info.has_pinned_messages])
        
        embed.add_field(
            name="🛡️ Preservation Reasons",
            value=f"**Recent Activity:** {activity_preserved}\n"
                  f"**Pinned Messages:** {pins_preserved}\n"
                  f"**Other Factors:** {len(channels_to_preserve) - activity_preserved - pins_preserved}",
            inline=True
        )
        
        embed.add_field(
            name="⚙️ Settings",
            value=f"**Preserve Active:** {'Yes' if preserve_active else 'No'}\n"
                  f"**Preserve Pinned:** {'Yes' if preserve_pinned else 'No'}",
            inline=True
        )
        
        # List channels to be deleted (limit to first 10)
        if channels_to_delete:
            delete_list = []
            for i, info in enumerate(channels_to_delete[:10]):
                age_days = (datetime.utcnow() - info.created_at).days
                delete_list.append(f"{i+1}. {info.channel.name} ({age_days}d old)")
            
            embed.add_field(
                name="🗑️ Channels to Delete",
                value="\n".join(delete_list) + (f"\n... and {len(channels_to_delete) - 10} more" if len(channels_to_delete) > 10 else ""),
                inline=False
            )
        
        embed.set_footer(text="This is a dry run - no channels were actually deleted")
        return embed
    
    def _create_cleanup_result_embed(self, stats, days_old: int, cleanup_type: str) -> discord.Embed:
        """Create embed showing cleanup results"""
        
        # Determine embed color based on results
        if stats.errors > 0:
            color = 0xffa500  # Orange for warnings
        elif stats.channels_deleted > 0:
            color = 0x00ff00  # Green for success
        else:
            color = 0x0099ff  # Blue for info
        
        embed = discord.Embed(
            title="🧹 Soccer Channel Cleanup Complete",
            description=f"Cleanup completed for channels older than {days_old} days",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📊 Results",
            value=f"**Processed:** {stats.total_processed} channels\n"
                  f"**Deleted:** {stats.channels_deleted} channels\n"
                  f"**Preserved:** {stats.channels_preserved} channels\n"
                  f"**Errors:** {stats.errors}",
            inline=True
        )
        
        if stats.duration:
            embed.add_field(
                name="⏱️ Performance",
                value=f"**Duration:** {stats.duration.total_seconds():.1f}s\n"
                      f"**Success Rate:** {stats.success_rate:.1f}%",
                inline=True
            )
        
        embed.add_field(
            name="🔧 Cleanup Type",
            value=cleanup_type.title(),
            inline=True
        )
        
        if stats.channels_with_activity > 0 or stats.channels_with_pins > 0:
            embed.add_field(
                name="🛡️ Preservation Details",
                value=f"**Recent Activity:** {stats.channels_with_activity}\n"
                      f"**Pinned Messages:** {stats.channels_with_pins}",
                inline=False
            )
        
        if stats.errors > 0:
            embed.add_field(
                name="⚠️ Errors",
                value=f"{stats.errors} channels could not be deleted. Check bot permissions and try again.",
                inline=False
            )
        
        embed.set_footer(text="Soccer Bot Cleanup System")
        return embed
    
    def _create_statistics_embed(self, stats: dict) -> discord.Embed:
        """Create embed showing cleanup system statistics"""
        
        embed = discord.Embed(
            title="📊 Soccer Cleanup System Statistics",
            description="Current system status and historical data",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        # System information
        system_info = stats["system_info"]
        embed.add_field(
            name="🔧 System Configuration",
            value=f"**Total Cleanups:** {system_info['total_cleanups_performed']}\n"
                  f"**Default Retention:** {system_info['default_retention_days']} days\n"
                  f"**Max Channels:** {system_info['max_channels_per_category']}\n"
                  f"**Scheduled Cleanup:** {'Enabled' if system_info['scheduled_cleanup_enabled'] else 'Disabled'}",
            inline=True
        )
        
        # Next scheduled cleanup
        if system_info.get("next_scheduled_cleanup"):
            next_cleanup = system_info["next_scheduled_cleanup"]
            embed.add_field(
                name="⏰ Next Scheduled Cleanup",
                value=f"<t:{int(next_cleanup.timestamp())}:R>",
                inline=True
            )
        
        # Last cleanup information
        last_cleanup = stats.get("last_cleanup")
        if last_cleanup:
            embed.add_field(
                name="🕐 Last Cleanup",
                value=f"**When:** <t:{int(last_cleanup['start_time'].timestamp())}:R>\n"
                      f"**Duration:** {last_cleanup['duration_seconds']:.1f}s\n"
                      f"**Success Rate:** {last_cleanup['success_rate']:.1f}%",
                inline=True
            )
            
            embed.add_field(
                name="📈 Last Cleanup Results",
                value=f"**Processed:** {last_cleanup['total_processed']}\n"
                      f"**Deleted:** {last_cleanup['channels_deleted']}\n"
                      f"**Preserved:** {last_cleanup['channels_preserved']}\n"
                      f"**Errors:** {last_cleanup['errors']}",
                inline=True
            )
            
            if last_cleanup['channels_with_activity'] > 0 or last_cleanup['channels_with_pins'] > 0:
                embed.add_field(
                    name="🛡️ Preservation Breakdown",
                    value=f"**Recent Activity:** {last_cleanup['channels_with_activity']}\n"
                          f"**Pinned Messages:** {last_cleanup['channels_with_pins']}",
                    inline=True
                )
        else:
            embed.add_field(
                name="🕐 Last Cleanup",
                value="No cleanup has been performed yet",
                inline=False
            )
        
        embed.set_footer(text="Soccer Bot Cleanup System")
        return embed
    
    def _create_limit_management_embed(self, results: dict, priority_retention: bool) -> discord.Embed:
        """Create embed showing channel limit management results"""
        
        # Determine embed color
        if results["errors"] > 0:
            color = 0xffa500  # Orange for warnings
        elif results["channels_removed"] > 0:
            color = 0x00ff00  # Green for action taken
        else:
            color = 0x0099ff  # Blue for no action needed
        
        embed = discord.Embed(
            title="📊 Channel Limit Management",
            description="Results of channel limit management operation",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📈 Results",
            value=f"**Channels Removed:** {results['channels_removed']}\n"
                  f"**Channels Remaining:** {results['channels_remaining']}\n"
                  f"**Errors:** {results['errors']}",
            inline=True
        )
        
        embed.add_field(
            name="⚙️ Settings",
            value=f"**Priority Retention:** {'Enabled' if priority_retention else 'Disabled'}\n"
                  f"**Channel Limit:** {self.cleanup_system.max_channels_per_category}",
            inline=True
        )
        
        # Status message
        if results["channels_removed"] == 0 and results["errors"] == 0:
            status = "✅ No action needed - channel count is within limits"
        elif results["channels_removed"] > 0 and results["errors"] == 0:
            status = f"✅ Successfully managed channel limits - removed {results['channels_removed']} channels"
        else:
            status = f"⚠️ Partial success - {results['errors']} errors occurred during limit management"
        
        embed.add_field(
            name="📋 Status",
            value=status,
            inline=False
        )
        
        if results["errors"] > 0:
            embed.add_field(
                name="⚠️ Errors",
                value=f"{results['errors']} channels could not be removed. Check bot permissions.",
                inline=False
            )
        
        embed.set_footer(text="Soccer Bot Channel Management")
        return embed

async def setup(bot):
    """Setup function for the cog"""
    # Get cleanup system from bot
    cleanup_system = getattr(bot, 'soccer_cleanup_system', None)
    if cleanup_system:
        await bot.add_cog(SoccerCleanupCommands(bot, cleanup_system))
    else:
        raise RuntimeError("SoccerCleanupSystem not found in bot instance")