#!/usr/bin/env python3
"""
Fix 'Unknown Integration' Error
This script helps diagnose and fix Discord bot integration issues
"""

import os
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def diagnose_discord_bot():
    """Diagnose Discord bot integration issues"""
    
    print("🔍 DISCORD BOT DIAGNOSTICS")
    print("=" * 50)
    
    # Check environment variables
    token = os.getenv("DISCORD_TOKEN", "").strip()
    print(f"🔑 Discord Token: {'✅ Present' if token else '❌ Missing'}")
    
    if token:
        print(f"    Length: {len(token)} characters")
        print(f"    Starts with: {token[:10]}..." if len(token) >= 10 else "    Too short!")
        
        # Check token format
        if not token.startswith(('MTA', 'MTI', 'Nz', 'OD', 'MT')):
            print("    ⚠️  Token format looks unusual for Discord bot token")
    
    print()
    
    # Check if we can import discord.py
    try:
        import discord
        print(f"✅ discord.py: Version {discord.__version__}")
    except ImportError:
        print("❌ discord.py: Not installed")
        print("   Fix: pip install discord.py")
        return
    
    if not token:
        print("❌ Cannot continue without Discord token")
        return
    
    # Try to create bot and check basic connection
    print("\n🤖 TESTING BOT CONNECTION")
    print("-" * 30)
    
    try:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        bot = discord.Client(intents=intents)
        
        @bot.event
        async def on_ready():
            print(f"✅ Connected as: {bot.user}")
            print(f"✅ Bot ID: {bot.user.id}")
            print(f"✅ In {len(bot.guilds)} guilds:")
            
            for guild in bot.guilds:
                print(f"    - {guild.name} (ID: {guild.id})")
                
                # Check bot permissions in each guild
                member = guild.get_member(bot.user.id)
                if member:
                    perms = member.guild_permissions
                    print(f"      Permissions: Admin={perms.administrator}, Manage Channels={perms.manage_channels}")
            
            print("\n🔧 INTEGRATION STATUS:")
            if len(bot.guilds) == 0:
                print("❌ Bot is not in any guilds!")
                print("   Fix: Re-invite bot to your Discord server")
            else:
                print("✅ Bot is properly connected to Discord guilds")
            
            # Close the connection
            await bot.close()
        
        print("🔄 Connecting to Discord...")
        await bot.start(token)
        
    except discord.LoginFailure:
        print("❌ LOGIN FAILED: Invalid Discord token")
        print("   Fix: Check your DISCORD_TOKEN environment variable")
        print("   1. Go to Discord Developer Portal")
        print("   2. Select your application")
        print("   3. Go to Bot section")
        print("   4. Reset token and update environment variable")
        
    except discord.HTTPException as e:
        print(f"❌ HTTP ERROR: {e}")
        print("   This might be a rate limit or Discord API issue")
        
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")
        print("   Check your internet connection and Discord status")

async def fix_command_sync():
    """Try to fix command sync issues"""
    print("\n🔧 COMMAND SYNC FIX ATTEMPT")
    print("=" * 50)
    
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token:
        print("❌ No Discord token available")
        return
    
    try:
        import discord
        from discord.ext import commands
        
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        bot = commands.Bot(command_prefix=None, intents=intents)
        
        @bot.tree.command(name="test", description="Test command to verify sync")
        async def test_command(interaction: discord.Interaction):
            await interaction.response.send_message("✅ Command sync is working!")
        
        @bot.event
        async def on_ready():
            print(f"✅ Bot connected: {bot.user}")
            
            try:
                # Clear old commands first
                print("🔄 Clearing old commands...")
                bot.tree.clear_commands(guild=None)
                await bot.tree.sync()
                
                # Wait a moment
                await asyncio.sleep(2)
                
                # Sync new commands
                print("🔄 Syncing new commands...")
                synced = await bot.tree.sync()
                print(f"✅ Synced {len(synced)} command(s)")
                
                for cmd in synced:
                    print(f"    - /{cmd.name}: {cmd.description}")
                
            except Exception as e:
                print(f"❌ Sync failed: {e}")
            
            await bot.close()
        
        await bot.start(token)
        
    except Exception as e:
        print(f"❌ Fix attempt failed: {e}")

if __name__ == "__main__":
    print("Discord Bot 'Unknown Integration' Fixer")
    print("=" * 50)
    
    asyncio.run(diagnose_discord_bot())
    
    print("\n" + "=" * 50)
    choice = input("Try to fix command sync issues? (y/n): ").lower().strip()
    
    if choice == 'y':
        asyncio.run(fix_command_sync())
    
    print("\n🎯 RECOMMENDED ACTIONS:")
    print("1. If token is invalid: Generate new token in Discord Developer Portal")
    print("2. If bot not in guilds: Re-invite bot with proper permissions")
    print("3. If commands not syncing: Use /sync command in Discord")
    print("4. If still failing: Check Railway logs for detailed errors")