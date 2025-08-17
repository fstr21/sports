#!/usr/bin/env python3
"""
Discord Bot Command Fix - Complete Solution

This script provides a comprehensive fix for the missing Discord commands issue.
The problem is likely a guild vs global command sync conflict.
"""

import asyncio
import os
import discord
from discord.ext import commands
from discord import app_commands
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()

class FixBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix="!fix_",
            intents=intents,
            description="Command Fix Bot"
        )
    
    async def on_ready(self):
        logger.info(f"Fix bot logged in as {self.user}")
        logger.info(f"Bot is in {len(self.guilds)} guilds")
        
        # List guilds
        for guild in self.guilds:
            logger.info(f"Guild: {guild.name} (ID: {guild.id})")

# Create fix bot
fix_bot = FixBot()

@fix_bot.tree.command(name="emergency-clear-commands", description="Emergency: Clear all commands and re-sync")
async def emergency_clear(interaction: discord.Interaction):
    """Emergency command to clear and re-sync all commands"""
    await interaction.response.defer()
    
    try:
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("❌ Administrator permission required")
            return
        
        guild_id = interaction.guild.id
        
        # Step 1: Clear global commands
        fix_bot.tree.clear_commands(guild=None)
        await fix_bot.tree.sync()
        logger.info("Cleared global commands")
        
        # Step 2: Clear guild-specific commands
        guild_obj = discord.Object(id=guild_id)
        fix_bot.tree.clear_commands(guild=guild_obj)
        await fix_bot.tree.sync(guild=guild_obj)
        logger.info(f"Cleared guild commands for {guild_id}")
        
        await interaction.followup.send(
            "✅ **Emergency Clear Complete**\\n"
            "All commands have been cleared from both global and guild scope.\\n"
            "**Next Steps:**\\n"
            "1. Redeploy your main bot on Railway\\n"
            "2. Wait 2-3 minutes for startup\\n"
            "3. Commands should reappear in autocomplete"
        )
        
    except Exception as e:
        await interaction.followup.send(f"❌ Emergency clear failed: {str(e)}")

@fix_bot.tree.command(name="diagnose-commands", description="Diagnose command registration issues")
async def diagnose_commands(interaction: discord.Interaction):
    """Diagnose command registration issues"""
    await interaction.response.defer()
    
    try:
        guild_id = interaction.guild.id
        
        # Check global commands
        global_commands = await fix_bot.tree.fetch_commands()
        
        # Check guild commands
        guild_obj = discord.Object(id=guild_id)
        guild_commands = await fix_bot.tree.fetch_commands(guild=guild_obj)
        
        embed = discord.Embed(
            title="🔍 Command Registration Diagnosis",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Global Commands",
            value=f"{len(global_commands)} registered\\n" + 
                  "\\n".join([f"• /{cmd.name}" for cmd in global_commands[:10]]) if global_commands else "None",
            inline=True
        )
        
        embed.add_field(
            name="Guild Commands",
            value=f"{len(guild_commands)} registered\\n" + 
                  "\\n".join([f"• /{cmd.name}" for cmd in guild_commands[:10]]) if guild_commands else "None",
            inline=True
        )
        
        # Diagnosis
        diagnosis = []
        if len(global_commands) > 0 and len(guild_commands) > 0:
            diagnosis.append("⚠️ **CONFLICT**: Both global and guild commands exist")
            diagnosis.append("**Solution**: Clear one scope and re-sync")
        elif len(global_commands) == 0 and len(guild_commands) == 0:
            diagnosis.append("❌ **NO COMMANDS**: No commands in either scope")
            diagnosis.append("**Solution**: Bot needs to register commands")
        elif len(global_commands) > 0:
            diagnosis.append("✅ **GLOBAL ONLY**: Commands in global scope (normal)")
        else:
            diagnosis.append("⚠️ **GUILD ONLY**: Commands only in this guild")
        
        embed.add_field(
            name="Diagnosis",
            value="\\n".join(diagnosis),
            inline=False
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Diagnosis failed: {str(e)}")

@fix_bot.tree.command(name="force-guild-sync", description="Force sync commands to this guild only")
async def force_guild_sync(interaction: discord.Interaction):
    """Force sync commands to this specific guild"""
    await interaction.response.defer()
    
    try:
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("❌ Administrator permission required")
            return
        
        guild_obj = discord.Object(id=interaction.guild.id)
        
        # Clear guild commands first
        fix_bot.tree.clear_commands(guild=guild_obj)
        
        # Add a test command
        @fix_bot.tree.command(name="test-guild-sync", description="Test command for guild sync")
        async def test_guild_sync(inter: discord.Interaction):
            await inter.response.send_message("✅ Guild sync working!")
        
        # Sync to this guild
        synced = await fix_bot.tree.sync(guild=guild_obj)
        
        await interaction.followup.send(
            f"✅ **Guild Sync Complete**\\n"
            f"Synced {len(synced)} commands to this guild.\\n"
            f"Try `/test-guild-sync` to verify it works.\\n\\n"
            f"**If this works, your main bot has a sync issue.**"
        )
        
    except Exception as e:
        await interaction.followup.send(f"❌ Guild sync failed: {str(e)}")

async def main():
    """Run the fix bot"""
    if not DISCORD_TOKEN:
        print("❌ DISCORD_TOKEN not found")
        return
    
    print("🔧 Discord Command Fix Bot Starting...")
    print("Available commands after bot starts:")
    print("  /emergency-clear-commands - Clear all commands and force re-sync")
    print("  /diagnose-commands - Check command registration status")
    print("  /force-guild-sync - Test guild-specific sync")
    print()
    print("Use these commands to diagnose and fix the missing command issue.")
    
    try:
        await fix_bot.start(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Fix bot failed to start: {e}")

if __name__ == "__main__":
    asyncio.run(main())