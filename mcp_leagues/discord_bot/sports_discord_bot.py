#!/usr/bin/env python3
"""
Simple Sports Discord Bot - Clear Channels Only
Starting fresh with minimal commands to test functionality
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

import discord
from discord.ext import commands
from discord import app_commands
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()

class SportsBot(commands.Bot):
    """Simple bot for channel management"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=None,  # Slash commands only
            intents=intents,
            description="Sports Channel Management Bot"
        )
    
    async def on_ready(self):
        logger.info(f"{self.user} has connected to Discord!")
        logger.info(f"Bot is in {len(self.guilds)} guilds")
        
        # List all guilds for debugging
        for guild in self.guilds:
            logger.info(f"Guild: {guild.name} (ID: {guild.id})")
        
        # Sync commands with multiple attempts
        await self.sync_commands_properly()
    
    async def sync_commands_properly(self):
        """Properly sync commands with Discord"""
        max_attempts = 3
        
        # First, let's debug what commands are actually defined
        logger.info("🔍 DEBUGGING: Checking command tree before sync")
        local_commands = list(self.tree.get_commands())
        logger.info(f"📊 Local commands in tree: {len(local_commands)}")
        
        for cmd in local_commands:
            logger.info(f"  🎯 Found local command: /{cmd.name} - {cmd.description}")
            logger.info(f"      Callback: {cmd.callback.__name__ if cmd.callback else 'None'}")
        
        if len(local_commands) == 0:
            logger.error("❌ CRITICAL: No commands found in command tree!")
            logger.error("   This means the @bot.tree.command decorators are not working")
            return False
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"🔄 Syncing commands (attempt {attempt + 1}/{max_attempts})")
                
                # DON'T clear commands - this might be removing our commands
                # self.tree.clear_commands(guild=None)
                
                # Add a small delay
                await asyncio.sleep(1)
                
                # Sync globally 
                synced = await self.tree.sync()
                
                logger.info(f"✅ Successfully synced {len(synced)} command(s)")
                for cmd in synced:
                    logger.info(f"  - /{cmd.name}: {cmd.description}")
                
                # Try to fetch commands to verify
                await asyncio.sleep(2)
                try:
                    fetched = await self.tree.fetch_commands()
                    logger.info(f"🔍 Verified: Discord shows {len(fetched)} registered commands")
                    
                    if len(fetched) > 0:
                        return True  # Success
                    else:
                        logger.warning("⚠️ No commands found after sync")
                        
                except Exception as fetch_error:
                    logger.error(f"❌ Could not fetch commands: {fetch_error}")
                
                # If we got here, something might be wrong
                if attempt < max_attempts - 1:
                    logger.info(f"🔄 Retrying command sync in 5 seconds...")
                    await asyncio.sleep(5)
                else:
                    logger.error(f"❌ Failed to properly sync commands after {max_attempts} attempts")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Sync attempt {attempt + 1} failed: {e}")
                logger.error(f"   Exception type: {type(e).__name__}")
                logger.error(f"   Exception details: {str(e)}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(5)
                else:
                    logger.error(f"❌ All sync attempts failed")
                    return False
        
        return False

# Initialize bot
bot = SportsBot()

# Commands defined AFTER bot initialization
@bot.tree.command(name="clear", description="Clear all channels from a sport category")
@app_commands.describe(category="Select the sport category to clear")
@app_commands.choices(category=[
    app_commands.Choice(name="MLB", value="⚾ MLB GAMES"),
    app_commands.Choice(name="NFL", value="🏈 NFL GAMES"),
    app_commands.Choice(name="NBA", value="🏀 NBA GAMES"),
    app_commands.Choice(name="NHL", value="🏒 NHL GAMES"),
    app_commands.Choice(name="SOCCER", value="⚽ SOCCER GAMES"),
    app_commands.Choice(name="CFB", value="🏈 CFB GAMES"),
])
async def clear_command(interaction: discord.Interaction, category: str):
    """Clear all channels from a specific sport category"""
    await interaction.response.defer()
    
    try:
        logger.info(f"Clear command used by {interaction.user.name} for category: {category}")
        
        # Check permissions
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.followup.send("❌ You need 'Manage Channels' permission to use this command.")
            return
        
        # Find the category
        category_obj = discord.utils.get(interaction.guild.categories, name=category)
        if not category_obj:
            await interaction.followup.send(f"❌ Category '{category}' not found.")
            return
        
        # Get all text channels in the category
        channels_to_delete = [ch for ch in category_obj.channels if isinstance(ch, discord.TextChannel)]
        channel_count = len(channels_to_delete)
        
        if channel_count == 0:
            await interaction.followup.send(f"ℹ️ No channels found in '{category}' category.")
            return
        
        # Show what will be deleted
        embed = discord.Embed(
            title="🗑️ Clear Channels",
            description=f"Found **{channel_count} channels** in '{category}' category.",
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
        
        logger.info(f"🗑️ Attempting to delete {len(channels_to_delete)} channels...")
        
        for i, channel in enumerate(channels_to_delete):
            try:
                logger.info(f"🔄 Deleting channel {i+1}/{len(channels_to_delete)}: {channel.name}")
                await channel.delete()
                deleted_count += 1
                logger.info(f"✅ Successfully deleted: {channel.name}")
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
        
        # Send final result with detailed info
        if deleted_count > 0:
            result_embed = discord.Embed(
                title="✅ Clear Complete",
                description=f"Successfully deleted **{deleted_count}** out of {channel_count} channels from '{category}'.",
                color=discord.Color.green()
            )
        else:
            result_embed = discord.Embed(
                title="⚠️ Clear Failed",
                description=f"Could not delete any channels from '{category}'. Check bot permissions.",
                color=discord.Color.red()
            )
        
        # Add failure details if any
        if failed_deletions:
            failure_text = "\n".join(failed_deletions[:5])  # Show first 5 failures
            if len(failed_deletions) > 5:
                failure_text += f"\n... and {len(failed_deletions) - 5} more failures"
            result_embed.add_field(
                name="❌ Failed Deletions",
                value=failure_text,
                inline=False
            )
        
        await interaction.followup.send(embed=result_embed)
        logger.info(f"Clear completed: {deleted_count}/{channel_count} channels deleted")
        
    except Exception as e:
        logger.error(f"Error in clear command: {e}")
        await interaction.followup.send(f"❌ Error clearing channels: {str(e)}")

@bot.tree.command(name="sync", description="Force sync slash commands with Discord")
async def sync_command(interaction: discord.Interaction):
    """Force sync commands - for troubleshooting"""
    await interaction.response.defer()
    
    try:
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("❌ You need Administrator permission to use this command.")
            return
        
        logger.info(f"Manual sync requested by {interaction.user.name}")
        
        # Force sync
        await interaction.followup.send("🔄 Force syncing commands...")
        
        # Clear and re-sync
        bot.tree.clear_commands(guild=None)
        await asyncio.sleep(2)
        
        synced = await bot.tree.sync()
        
        embed = discord.Embed(
            title="🔄 Manual Sync Results",
            description=f"Synced {len(synced)} commands with Discord",
            color=discord.Color.blue()
        )
        
        if synced:
            command_list = "\\n".join([f"• /{cmd.name} - {cmd.description}" for cmd in synced])
            embed.add_field(name="Commands Synced", value=command_list, inline=False)
        
        # Try to verify
        await asyncio.sleep(1)
        try:
            fetched = await bot.tree.fetch_commands()
            embed.add_field(
                name="✅ Verification", 
                value=f"Discord API shows {len(fetched)} registered commands",
                inline=False
            )
        except Exception as e:
            embed.add_field(
                name="⚠️ Verification", 
                value=f"Could not verify: {str(e)[:100]}",
                inline=False
            )
        
        embed.add_field(
            name="ℹ️ Note",
            value="Commands may take 1-2 minutes to appear in Discord. Try refreshing the app.",
            inline=False
        )
        
        await interaction.followup.send(embed=embed)
        logger.info(f"Manual sync completed by {interaction.user.name}")
        
    except Exception as e:
        logger.error(f"Manual sync failed: {e}")
        await interaction.followup.send(f"❌ Sync failed: {str(e)}")

# Health check endpoint for Railway
async def health_check(request):
    try:
        return JSONResponse({
            "status": "healthy", 
            "bot_ready": bot.is_ready(),
            "guilds": len(bot.guilds) if bot.is_ready() else 0,
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "error": str(e)
        })

# Create Starlette app for health checks
app = Starlette(routes=[
    Route("/health", health_check, methods=["GET"])
])

async def run_bot():
    """Run the Discord bot"""
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables")
        return
    
    try:
        await bot.start(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Bot failed to start: {e}")

async def main():
    """Main function to run both bot and health check server"""
    port = int(os.getenv("PORT", 8080))
    
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    
    # Run bot and server together
    await asyncio.gather(
        run_bot(),
        server.serve()
    )

if __name__ == "__main__":
    print("🤖 Starting Simple Sports Discord Bot")
    print("=" * 50)
    print("Expected commands after startup:")
    print("  /clear - Clear channels from sport categories")
    print("  /sync - Force sync commands (admin only)")
    print("=" * 50)
    print(f"🚀 Build timestamp: {datetime.now().isoformat()}")
    print(f"🔧 Discord Token: {'✅ Set' if DISCORD_TOKEN else '❌ Missing'}")
    print("=" * 50)
    print("🔍 TROUBLESHOOTING:")
    print("  If commands don't appear in Discord:")
    print("  1. Use /sync command (if available)")
    print("  2. Restart Discord app")
    print("  3. Check Railway logs for errors")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\\n💥 Bot crashed: {e}")
        import traceback
        traceback.print_exc()