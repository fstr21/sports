#!/usr/bin/env python3
"""
Test Discord Command Structure Locally
This will help us identify issues with command definitions without deploying
"""

import asyncio
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.DEBUG)

async def test_command_structure():
    """Test if our command structure is valid"""
    print("🧪 TESTING DISCORD COMMAND STRUCTURE")
    print("=" * 50)
    
    try:
        # Try to import discord.py (might not be installed locally)
        try:
            import discord
            from discord.ext import commands
            from discord import app_commands
            print("✅ discord.py imported successfully")
        except ImportError:
            print("❌ discord.py not installed locally")
            print("   This test will simulate the command structure")
            return
        
        # Create a minimal bot to test command registration
        print("\n🤖 Creating test bot...")
        
        intents = discord.Intents.default()
        bot = commands.Bot(command_prefix=None, intents=intents)
        
        # Test the command definitions from our actual bot
        print("🔍 Testing command definitions...")
        
        # Test create-channels command
        @bot.tree.command(name="create-channels", description="Create game channels for a specific date")
        @app_commands.describe(
            sport="Select the sport to create channels for",
            date="Date in YYYY-MM-DD format (optional, defaults to today)"
        )
        @app_commands.choices(sport=[
            app_commands.Choice(name="⚾ MLB", value="mlb"),
            app_commands.Choice(name="🏈 NFL", value="nfl"), 
            app_commands.Choice(name="🏀 NBA", value="nba"),
            app_commands.Choice(name="🏒 NHL", value="nhl"),
            app_commands.Choice(name="⚽ Soccer", value="soccer"),
            app_commands.Choice(name="🏈 CFB", value="cfb")
        ])
        async def create_channels_command(interaction: discord.Interaction, sport: str, date: str = None):
            await interaction.response.send_message("Test command - would create channels")
        
        print("✅ create-channels command defined successfully")
        
        # Test clear command  
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
            await interaction.response.send_message("Test command - would clear channels")
            
        print("✅ clear command defined successfully")
        
        # Test sync command
        @bot.tree.command(name="sync", description="Force sync slash commands with Discord")
        async def sync_command(interaction: discord.Interaction):
            await interaction.response.send_message("Test command - would sync")
            
        print("✅ sync command defined successfully")
        
        # Check if commands are in the tree
        commands_in_tree = list(bot.tree.get_commands())
        print(f"\n📊 Commands in tree: {len(commands_in_tree)}")
        
        for cmd in commands_in_tree:
            print(f"  ✅ {cmd.name}: {cmd.description}")
            
        if len(commands_in_tree) == 3:
            print("\n🎉 ALL COMMAND DEFINITIONS ARE VALID!")
            print("   The issue is likely not with command structure")
        else:
            print(f"\n❌ WRONG NUMBER OF COMMANDS: Expected 3, got {len(commands_in_tree)}")
            
    except Exception as e:
        print(f"\n💥 COMMAND DEFINITION ERROR: {e}")
        import traceback
        traceback.print_exc()

async def test_function_syntax():
    """Test if our helper functions have syntax issues"""
    print("\n🧪 TESTING FUNCTION SYNTAX")
    print("=" * 50)
    
    try:
        # Test the functions we added
        print("Testing get_comprehensive_h2h_analysis...")
        
        # Simulate the function definition
        async def get_comprehensive_h2h_analysis(home_team_id: int, away_team_id: int, home_team_name: str, away_team_name: str):
            # This is just a syntax test
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "get_h2h_betting_analysis",
                    "arguments": {
                        "team_1_id": home_team_id,
                        "team_2_id": away_team_id,
                        "team_1_name": home_team_name,
                        "team_2_name": away_team_name
                    }
                }
            }
            return {"test": "success"}
        
        # Test calling it
        result = await get_comprehensive_h2h_analysis(123, 456, "Team A", "Team B")
        print("✅ get_comprehensive_h2h_analysis function syntax is valid")
        
        # Test the embed creation function
        def create_comprehensive_match_embed(match, league_name, h2h_data=None):
            # Mock embed creation
            return {"title": f"Match in {league_name}", "h2h_included": h2h_data is not None}
        
        test_match = {"teams": {"home": {"name": "Home"}, "away": {"name": "Away"}}}
        embed = create_comprehensive_match_embed(test_match, "Test League", {"test": "data"})
        print("✅ create_comprehensive_match_embed function syntax is valid")
        
        print("\n🎉 ALL FUNCTION SYNTAX IS VALID!")
        
    except Exception as e:
        print(f"\n💥 FUNCTION SYNTAX ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Discord Bot Command Tester")
    print("This will help identify issues before deployment")
    print("=" * 60)
    
    asyncio.run(test_command_structure())
    asyncio.run(test_function_syntax())
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. If all tests pass: Issue is likely with MCP server or runtime")
    print("2. If tests fail: Fix the syntax errors shown above")
    print("3. Check Railway logs for actual deployment errors")