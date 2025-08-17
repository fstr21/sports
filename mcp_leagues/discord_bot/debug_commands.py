#!/usr/bin/env python3
"""
Discord Bot Command Debugging Script

This script helps diagnose why certain Discord slash commands aren't working.
"""

import asyncio
import os
import discord
from discord.ext import commands
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()

class DebugBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix="!debug_",
            intents=intents,
            description="Debug Bot for Command Testing"
        )
    
    async def on_ready(self):
        logger.info(f"Debug bot logged in as {self.user}")
        logger.info(f"Bot is in {len(self.guilds)} guilds")
        
        # List all guilds
        for guild in self.guilds:
            logger.info(f"Guild: {guild.name} (ID: {guild.id})")
        
        # Check current slash commands
        try:
            commands = await self.tree.fetch_commands()
            logger.info(f"Currently registered slash commands: {len(commands)}")
            for cmd in commands:
                logger.info(f"  - /{cmd.name}: {cmd.description}")
        except Exception as e:
            logger.error(f"Failed to fetch commands: {e}")
        
        # Try to sync commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} commands")
            for cmd in synced:
                logger.info(f"  Synced: /{cmd.name}")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

# Create debug bot instance
debug_bot = DebugBot()

# Test commands
@debug_bot.tree.command(name="test-help", description="Test help command functionality")
async def test_help(interaction: discord.Interaction):
    """Test help command"""
    await interaction.response.send_message("✅ Help command test successful!")

@debug_bot.tree.command(name="test-clear", description="Test clear command functionality")
async def test_clear(interaction: discord.Interaction):
    """Test clear command"""
    await interaction.response.send_message("✅ Clear command test successful!")

@debug_bot.tree.command(name="list-commands", description="List all registered slash commands")
async def list_commands(interaction: discord.Interaction):
    """List all registered commands"""
    await interaction.response.defer()
    
    try:
        commands = await debug_bot.tree.fetch_commands()
        
        if not commands:
            await interaction.followup.send("❌ No slash commands are currently registered.")
            return
        
        embed = discord.Embed(
            title="🔍 Registered Slash Commands",
            description=f"Found {len(commands)} registered commands",
            color=discord.Color.blue()
        )
        
        for cmd in commands:
            embed.add_field(
                name=f"/{cmd.name}",
                value=cmd.description or "No description",
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error fetching commands: {str(e)}")

@debug_bot.tree.command(name="check-permissions", description="Check bot permissions in this server")
async def check_permissions(interaction: discord.Interaction):
    """Check bot permissions"""
    await interaction.response.defer()
    
    try:
        bot_member = interaction.guild.get_member(debug_bot.user.id)
        if not bot_member:
            await interaction.followup.send("❌ Bot member not found in guild")
            return
        
        permissions = bot_member.guild_permissions
        
        embed = discord.Embed(
            title="🔐 Bot Permissions Check",
            description=f"Permissions for {debug_bot.user.mention} in {interaction.guild.name}",
            color=discord.Color.green()
        )
        
        # Key permissions for the bot
        key_perms = {
            "Administrator": permissions.administrator,
            "Manage Channels": permissions.manage_channels,
            "Manage Messages": permissions.manage_messages,
            "Send Messages": permissions.send_messages,
            "Use Slash Commands": permissions.use_slash_commands,
            "Embed Links": permissions.embed_links,
            "Read Message History": permissions.read_message_history
        }
        
        for perm_name, has_perm in key_perms.items():
            status = "✅" if has_perm else "❌"
            embed.add_field(
                name=f"{status} {perm_name}",
                value="Granted" if has_perm else "Missing",
                inline=True
            )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error checking permissions: {str(e)}")

async def main():
    """Run the debug bot"""
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables")
        return
    
    try:
        await debug_bot.start(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Debug bot failed to start: {e}")

if __name__ == "__main__":
    print("🔍 Discord Bot Command Debugger")
    print("=" * 50)
    print("This script will help diagnose command issues.")
    print("Run this and then use the following commands in Discord:")
    print("  /test-help - Test basic command functionality")
    print("  /test-clear - Test clear command functionality") 
    print("  /list-commands - See all registered commands")
    print("  /check-permissions - Check bot permissions")
    print("=" * 50)
    
    asyncio.run(main())