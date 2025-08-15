#!/usr/bin/env python3
"""
Find actual games on August 23, 2025 using CFBD MCP server
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def find_august_23_games():
    """Find games specifically on August 23, 2025"""
    
    server_dir = Path(__file__).parent / "lenwood_cfbd-mcp-server"
    cfbd_exe = server_dir / ".venv" / "Scripts" / "cfbd-mcp-server.exe"
    
    server_params = StdioServerParameters(
        command=str(cfbd_exe),
        cwd=str(server_dir),
        env={
            **os.environ,
            "CFB_API_KEY": "Z0NGwLNiztE/3/YtS+Jajy4tID7xbjON1UFh6s8q0XgpM66VEkMGHYCt6ALSud7Y"
        }
    )
    
    print("🏈 Finding Games on August 23, 2025")
    print("=" * 50)
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Try different approaches to find August 23 games
                search_strategies = [
                    {"name": "2025 Week 1", "args": {"year": 2025, "week": 1}},
                    {"name": "2025 Week 0", "args": {"year": 2025, "week": 0}},
                    {"name": "2025 All Games", "args": {"year": 2025}},
                ]
                
                august_23_games = []
                
                for strategy in search_strategies:
                    print(f"\n🔍 Searching: {strategy['name']}")
                    
                    try:
                        result = await session.call_tool("get-games", strategy['args'])
                        
                        if result.content and result.content[0].text:
                            data = json.loads(result.content[0].text)
                            
                            if isinstance(data, list):
                                print(f"   Found {len(data)} total games")
                                
                                # Filter for August 23, 2025 specifically
                                for game in data:
                                    start_date = game.get('startDate', '')
                                    if start_date.startswith('2025-08-23'):
                                        august_23_games.append(game)
                                
                                print(f"   Games on 2025-08-23: {len([g for g in data if g.get('startDate', '').startswith('2025-08-23')])}")
                                
                    except Exception as e:
                        print(f"   ❌ Error: {e}")
                
                # Display all August 23 games found
                if august_23_games:
                    print(f"\n🎯 FOUND {len(august_23_games)} GAMES ON AUGUST 23, 2025!")
                    print("=" * 60)
                    
                    for i, game in enumerate(august_23_games, 1):
                        home_team = game.get('homeTeam', 'Unknown')
                        away_team = game.get('awayTeam', 'Unknown')
                        start_time = game.get('startDate', 'Unknown')
                        venue = game.get('venue', 'Unknown')
                        
                        # Parse time
                        if start_time != 'Unknown':
                            try:
                                dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                                time_str = dt.strftime('%I:%M %p ET')
                            except:
                                time_str = start_time
                        else:
                            time_str = 'TBD'
                        
                        print(f"\n🏈 Game {i}:")
                        print(f"   {away_team} @ {home_team}")
                        print(f"   Time: {time_str}")
                        print(f"   Venue: {venue}")
                        print(f"   Game ID: {game.get('id', 'Unknown')}")
                        
                        # Show additional details
                        if game.get('conference'):
                            print(f"   Conference: {game.get('conference')}")
                        if game.get('seasonType'):
                            print(f"   Season Type: {game.get('seasonType')}")
                        if game.get('week'):
                            print(f"   Week: {game.get('week')}")
                
                else:
                    print("\n❌ No games found on August 23, 2025")
                    print("Let me check what dates DO have games in late August 2025...")
                    
                    # Check for games in late August 2025
                    try:
                        result = await session.call_tool("get-games", {"year": 2025})
                        if result.content and result.content[0].text:
                            data = json.loads(result.content[0].text)
                            
                            august_games = []
                            for game in data:
                                start_date = game.get('startDate', '')
                                if '2025-08' in start_date:
                                    august_games.append(game)
                            
                            if august_games:
                                print(f"\n📅 Found {len(august_games)} games in August 2025:")
                                dates = set()
                                for game in august_games:
                                    date = game.get('startDate', '').split('T')[0]
                                    if date:
                                        dates.add(date)
                                
                                for date in sorted(dates):
                                    games_on_date = [g for g in august_games if g.get('startDate', '').startswith(date)]
                                    print(f"   {date}: {len(games_on_date)} games")
                                    for game in games_on_date[:3]:  # Show first 3
                                        print(f"     • {game.get('awayTeam')} @ {game.get('homeTeam')}")
                    except Exception as e:
                        print(f"Error checking August games: {e}")
                        
    except Exception as e:
        print(f"❌ Failed to connect to server: {e}")

if __name__ == "__main__":
    asyncio.run(find_august_23_games())