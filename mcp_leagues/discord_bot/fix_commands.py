#!/usr/bin/env python3
"""
Discord Bot Command Fix Script

This script adds diagnostic commands to help fix the missing /clear-channels and /help commands.
Add these commands to your main bot file temporarily to diagnose the issue.
"""

# Add these commands to your sports_discord_bot.py file:

DIAGNOSTIC_COMMANDS = '''
# Add these diagnostic commands to your bot:

@bot.tree.command(name="list-all-commands", description="List all registered slash commands")
async def list_all_commands(interaction: discord.Interaction):
    """List all registered commands for debugging"""
    await interaction.response.defer()
    
    try:
        commands = await bot.tree.fetch_commands()
        
        embed = discord.Embed(
            title="🔍 All Registered Commands",
            description=f"Found {len(commands)} registered commands",
            color=discord.Color.blue()
        )
        
        if not commands:
            embed.add_field(name="Status", value="❌ No commands registered", inline=False)
        else:
            command_list = []
            for i, cmd in enumerate(commands, 1):
                command_list.append(f"{i}. `/{cmd.name}` - {cmd.description}")
            
            # Split into chunks if too many commands
            chunk_size = 10
            for i in range(0, len(command_list), chunk_size):
                chunk = command_list[i:i+chunk_size]
                embed.add_field(
                    name=f"Commands {i+1}-{min(i+chunk_size, len(command_list))}",
                    value="\\n".join(chunk),
                    inline=False
                )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error fetching commands: {str(e)}")

@bot.tree.command(name="force-resync", description="Force re-sync all slash commands")
async def force_resync(interaction: discord.Interaction):
    """Force re-sync all commands"""
    await interaction.response.defer()
    
    try:
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("❌ You need Administrator permission to use this command.")
            return
        
        # Clear existing commands
        bot.tree.clear_commands(guild=None)
        
        # Re-sync all commands
        synced = await bot.tree.sync()
        
        embed = discord.Embed(
            title="🔄 Force Re-sync Complete",
            description=f"Successfully synced {len(synced)} commands",
            color=discord.Color.green()
        )
        
        if synced:
            command_names = [f"• /{cmd.name}" for cmd in synced]
            embed.add_field(
                name="Synced Commands",
                value="\\n".join(command_names),
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
        logger.info(f"Force re-sync completed: {len(synced)} commands")
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error during force re-sync: {str(e)}")
        logger.error(f"Force re-sync failed: {e}")

@bot.tree.command(name="check-missing", description="Check for missing expected commands")
async def check_missing(interaction: discord.Interaction):
    """Check which expected commands are missing"""
    await interaction.response.defer()
    
    try:
        # Expected commands
        expected_commands = [
            "sync", "create-mlb-channels", "clear-channels", "help", 
            "setup", "debug-mlb", "analyze"
        ]
        
        # Get currently registered commands
        registered = await bot.tree.fetch_commands()
        registered_names = [cmd.name for cmd in registered]
        
        # Find missing commands
        missing = [cmd for cmd in expected_commands if cmd not in registered_names]
        present = [cmd for cmd in expected_commands if cmd in registered_names]
        
        embed = discord.Embed(
            title="🔍 Command Status Check",
            description="Checking for expected vs registered commands",
            color=discord.Color.orange()
        )
        
        if present:
            embed.add_field(
                name="✅ Present Commands",
                value="\\n".join([f"• /{cmd}" for cmd in present]),
                inline=True
            )
        
        if missing:
            embed.add_field(
                name="❌ Missing Commands", 
                value="\\n".join([f"• /{cmd}" for cmd in missing]),
                inline=True
            )
        
        # Summary
        status = "🎉 All commands present!" if not missing else f"⚠️ {len(missing)} commands missing"
        embed.add_field(name="Status", value=status, inline=False)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error checking commands: {str(e)}")

@bot.tree.command(name="test-help-function", description="Test the help command functionality directly")
async def test_help_function(interaction: discord.Interaction):
    """Test help command functionality"""
    await interaction.response.defer()
    
    try:
        # This is the same code as the help command
        embed = discord.Embed(
            title="🤖 Sports Bot Commands (Test)",
            description="Testing help command functionality",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🏟️ Core Commands",
            value="`/create-mlb-channels` - Create channels for today's MLB games\\n"
                  "`/setup` - Setup channel structure for this server\\n"
                  "`/sync` - Manually sync slash commands",
            inline=False
        )
        
        embed.add_field(
            name="🗑️ Management Commands", 
            value="`/clear-channels` - Clear all channels from a sport category\\n"
                  "└ Dropdown: MLB, NFL, NHL, NBA, CFB, Soccer",
            inline=False
        )
        
        embed.set_footer(text="Help function test - if you see this, the help code works!")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Help function test failed: {str(e)}")
'''

print("🔧 Discord Bot Command Fix")
print("=" * 50)
print("Copy and paste the following diagnostic commands into your sports_discord_bot.py file:")
print("Add them before the 'Health check endpoint' section.")
print("=" * 50)
print(DIAGNOSTIC_COMMANDS)
print("=" * 50)
print("After adding these commands:")
print("1. Redeploy your bot on Railway")
print("2. Use /force-resync in Discord")
print("3. Use /check-missing to see what's missing")
print("4. Use /list-all-commands to see what's registered")
print("5. Use /test-help-function to test help functionality")
print("=" * 50)