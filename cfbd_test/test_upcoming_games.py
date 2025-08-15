#!/usr/bin/env python3
"""
Test script to get upcoming games for 8/23/2025 using the CFBD MCP server
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def get_upcoming_games():
    """Get upcoming games for 8/23/2025"""
    
    # Get the path to the server directory
    server_dir = Path(__file__).parent / "lenwood_cfbd-mcp-server"
    cfbd_exe = server_dir / ".venv" / "Scripts" / "cfbd-mcp-server.exe"
    
    # Server parameters
    server_params = StdioServerParameters(
        command=str(cfbd_exe),
        cwd=str(server_dir),
        env={
            **os.environ,
            "CFB_API_KEY": "Z0NGwLNiztE/3/YtS+Jajy4tID7xbjON1UFh6s8q0XgpM66VEkMGHYCt6ALSud7Y"
        }
    )
    
    print("🏈 CFBD MCP Server - Upcoming Games Test")
    print("=" * 50)
    print("Target Date: August 23, 2025")
    print("Looking for games in 2025 season...")
    print()
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                
                # Test different approaches to find games around 8/23/2025
                test_scenarios = [
                    {
                        "name": "2025 Season - Week 1",
                        "args": {"year": 2025, "week": 1},
                        "description": "Check if Week 1 of 2025 has games around 8/23"
                    },
                    {
                        "name": "2025 Season - Week 0", 
                        "args": {"year": 2025, "week": 0},
                        "description": "Check Week 0 (often has early season games)"
                    },
                    {
                        "name": "2025 Season - All Games",
                        "args": {"year": 2025},
                        "description": "Get all 2025 games to see what's available"
                    },
                    {
                        "name": "2024 Season - Week 1 (Reference)",
                        "args": {"year": 2024, "week": 1},
                        "description": "Compare with 2024 data to see typical early season structure"
                    }
                ]
                
                for scenario in test_scenarios:
                    print(f"🔍 Testing: {scenario['name']}")
                    print(f"   {scenario['description']}")
                    
                    try:
                        result = await session.call_tool("get-games", scenario['args'])
                        
                        if result.content and result.content[0].text:
                            data = json.loads(result.content[0].text)
                            
                            if isinstance(data, list):
                                print(f"   ✅ Found {len(data)} games")
                                
                                if len(data) > 0:
                                    # Look for games around 8/23
                                    target_date = "2025-08-23"
                                    relevant_games = []
                                    
                                    for game in data:
                                        game_date = game.get('startDate', '')
                                        if game_date:
                                            # Extract date part
                                            game_date_only = game_date.split('T')[0]
                                            if scenario['args']['year'] == 2025:
                                                # For 2025, look for games around our target date
                                                if '2025-08' in game_date_only:
                                                    relevant_games.append(game)
                                            else:
                                                # For 2024, just show a few examples
                                                if len(relevant_games) < 3:
                                                    relevant_games.append(game)
                                    
                                    if relevant_games:
                                        print(f"   📅 Games around target date:")
                                        for game in relevant_games[:5]:  # Show max 5 games
                                            date = game.get('startDate', 'Unknown').split('T')[0]
                                            home = game.get('homeTeam', 'Unknown')
                                            away = game.get('awayTeam', 'Unknown')
                                            completed = game.get('completed', False)
                                            status = "✅ Completed" if completed else "⏳ Scheduled"
                                            print(f"     {date}: {away} @ {home} ({status})")
                                    else:
                                        if scenario['args']['year'] == 2025:
                                            print("   ⚠️  No games found around 8/23/2025")
                                        else:
                                            print("   📊 Sample games from this dataset:")
                                            for game in data[:3]:
                                                date = game.get('startDate', 'Unknown').split('T')[0]
                                                home = game.get('homeTeam', 'Unknown')
                                                away = game.get('awayTeam', 'Unknown')
                                                print(f"     {date}: {away} @ {home}")
                                else:
                                    print("   ℹ️  No games found for this query")
                            else:
                                print(f"   ✅ Response received: {str(data)[:100]}...")
                        else:
                            print("   ❌ No data returned")
                            
                    except Exception as e:
                        print(f"   ❌ Error: {e}")
                    
                    print()  # Add spacing between tests
                
                # Summary and recommendations
                print("📋 SUMMARY & RECOMMENDATIONS")
                print("=" * 50)
                print("🔮 Future Data Availability:")
                print("   • College football schedules are typically released in spring")
                print("   • 2025 season data may not be available yet in the API")
                print("   • The API focuses on historical and current season data")
                print()
                print("📅 For 8/23/2025 specifically:")
                print("   • This would likely be Week 0 or Week 1 of 2025 season")
                print("   • Games typically start late August/early September")
                print("   • Check back closer to the 2025 season for schedule data")
                print()
                print("🔄 Alternative approaches:")
                print("   • Use 2024 data to understand typical early season patterns")
                print("   • Monitor the API for when 2025 schedules are added")
                print("   • Focus on historical analysis of similar timeframes")
                
    except Exception as e:
        print(f"❌ Failed to connect to server: {e}")
        print("\n🔧 Make sure the CFBD MCP server is properly set up")

if __name__ == "__main__":
    asyncio.run(get_upcoming_games())