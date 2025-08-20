"""
Discord command synchronization manager with detailed feedback
"""
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import discord
from discord.ext import commands


logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Result of command synchronization operation"""
    success: bool
    commands_synced: int
    total_commands: int
    sync_time: datetime
    errors: List[str]
    details: Dict[str, Any]


class SyncManager:
    """
    Manages Discord command synchronization with detailed feedback
    and permission validation
    """
    
    def __init__(self, bot: commands.Bot, required_permissions: List[str] = None):
        """
        Initialize sync manager
        
        Args:
            bot: Discord bot instance
            required_permissions: List of required permissions for sync operations
        """
        self.bot = bot
        self.required_permissions = required_permissions or ["manage_channels"]
        self._last_sync: datetime = None
        self._last_sync_success: bool = False
        self._commands_count: int = 0
        self._sync_in_progress: bool = False
    
    async def sync_commands(self, interaction: discord.Interaction, guild_only: bool = True) -> SyncResult:
        """
        Synchronize Discord commands with detailed logging and feedback
        
        Args:
            interaction: Discord interaction object
            guild_only: Whether to sync only to current guild (faster) or globally
            
        Returns:
            SyncResult with operation details
        """
        if self._sync_in_progress:
            return SyncResult(
                success=False,
                commands_synced=0,
                total_commands=0,
                sync_time=datetime.now(),
                errors=["Sync already in progress"],
                details={}
            )
        
        # Validate permissions
        if not self.validate_sync_permissions(interaction.user):
            return SyncResult(
                success=False,
                commands_synced=0,
                total_commands=0,
                sync_time=datetime.now(),
                errors=["Insufficient permissions for sync operation"],
                details={"required_permissions": self.required_permissions}
            )
        
        self._sync_in_progress = True
        sync_start = datetime.now()
        errors = []
        
        try:
            logger.info(f"Starting command sync initiated by {interaction.user.name}")
            
            # Get current command count before sync
            current_commands = self.bot.tree.get_commands()
            total_commands = len(current_commands)
            
            # Perform synchronization
            if guild_only and interaction.guild:
                logger.info(f"Syncing commands to guild: {interaction.guild.name}")
                synced_commands = await self.bot.tree.sync(guild=interaction.guild)
            else:
                logger.info("Syncing commands globally")
                synced_commands = await self.bot.tree.sync()
            
            commands_synced = len(synced_commands)
            sync_time = datetime.now()
            
            # Update internal state
            self._last_sync = sync_time
            self._last_sync_success = True
            self._commands_count = commands_synced
            
            logger.info(f"Command sync completed: {commands_synced} commands synced")
            
            return SyncResult(
                success=True,
                commands_synced=commands_synced,
                total_commands=total_commands,
                sync_time=sync_time,
                errors=errors,
                details={
                    "guild_only": guild_only,
                    "guild_name": interaction.guild.name if interaction.guild else None,
                    "sync_duration": (sync_time - sync_start).total_seconds(),
                    "synced_commands": [cmd.name for cmd in synced_commands]
                }
            )
            
        except discord.HTTPException as e:
            error_msg = f"Discord API error during sync: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
            
        except discord.Forbidden as e:
            error_msg = f"Bot lacks permissions for command sync: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error during sync: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
        
        finally:
            self._sync_in_progress = False
        
        # Update state for failed sync
        self._last_sync = datetime.now()
        self._last_sync_success = False
        
        return SyncResult(
            success=False,
            commands_synced=0,
            total_commands=total_commands if 'total_commands' in locals() else 0,
            sync_time=datetime.now(),
            errors=errors,
            details={"guild_only": guild_only}
        )
    
    def validate_sync_permissions(self, user: discord.Member) -> bool:
        """
        Validate if user has required permissions for sync operations
        
        Args:
            user: Discord member to check
            
        Returns:
            True if user has required permissions
        """
        if not user.guild_permissions:
            return False
        
        for permission in self.required_permissions:
            if not getattr(user.guild_permissions, permission, False):
                logger.warning(f"User {user.name} lacks required permission: {permission}")
                return False
        
        return True
    
    def create_sync_embed(self, result: SyncResult) -> discord.Embed:
        """
        Create Discord embed for sync result
        
        Args:
            result: SyncResult object
            
        Returns:
            Discord embed with formatted sync information
        """
        if result.success:
            embed = discord.Embed(
                title="✅ Command Sync Successful",
                description=f"Successfully synchronized **{result.commands_synced}** commands",
                color=discord.Color.green(),
                timestamp=result.sync_time
            )
            
            # Add sync details
            if result.details.get("guild_name"):
                embed.add_field(
                    name="Scope",
                    value=f"Guild: {result.details['guild_name']}",
                    inline=True
                )
            else:
                embed.add_field(
                    name="Scope",
                    value="Global",
                    inline=True
                )
            
            if result.details.get("sync_duration"):
                embed.add_field(
                    name="Duration",
                    value=f"{result.details['sync_duration']:.2f}s",
                    inline=True
                )
        
        else:
            embed = discord.Embed(
                title="❌ Command Sync Failed",
                description="Command synchronization encountered errors",
                color=discord.Color.red(),
                timestamp=result.sync_time
            )
            
            # Add error details
            if result.errors:
                error_text = "\\n".join([f"• {error}" for error in result.errors[:3]])
                if len(result.errors) > 3:
                    error_text += f"\\n... and {len(result.errors) - 3} more errors"
                
                embed.add_field(
                    name="Errors",
                    value=error_text,
                    inline=False
                )
        
        embed.set_footer(text="Command Sync System")
        return embed
    
    def get_sync_status(self):
        """
        Get current synchronization status
        
        Returns:
            Dictionary with sync status information
        """
        return {
            "last_sync": self._last_sync,
            "last_sync_success": self._last_sync_success,
            "commands_count": self._commands_count,
            "sync_in_progress": self._sync_in_progress
        }