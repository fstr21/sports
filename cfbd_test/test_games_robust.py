#!/usr/bin/env python3
"""
Robust test script to get games data and handle various response formats
"""

import asyncio
import json
import os
import requests
from datetime import datetime
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()

def test_direct_api_first():
    """Test the API directly to see what data is available"""
    print("🔍 Testing Direct API Access First...")
    print("=" * 50)
    
    api_key = "Z0NGwLNiztE/3/YtS+Jajy4tID7xbjON1UFh6s8q0XgpM66VEkMGHYCt6ALSud7Y"
    base_url = "https://api.collegefootballdata.com"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    
    # Test different years and scenarios
    test_cases = [
        {"year": 2025, "description": "2025 season (future)"},
        {"year": 2024, "week": 1, "description": "2024 Week 1 (reference)"},
        {"year": 2024, "description": "2024 full season (reference)"}
    ]
    
    for test_case in test_cases:
        print(f"\n📅 Testing: {test_case['description']}")
        
        try:
            params = {k: v for k, v in test_case.items() if k not in ['description']}
            response = requests.get(f"{base_url}/games", headers=headers, params=params, timeout=10)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success! Found {len(data)} games")
                
                if len(data) > 0:
                    # Show sample games
                    print("   📊 Sample games:")
                    for game in data[:3]:
                        date = game.get('startDate', 'Unknown').split('T')[0]
                        home = game.get('homeTeam', 'Unknown')
                        away = game.get('awayTeam', 'Unknown')
                        print(f"     {date}: {away} @ {home}")
                        
                    # For 2025, look specifically for August games
                    if test_case['year'] == 2025:
                        august_games = [g for g in data if g.get('startDate', '').startswith('2025-08')]
                        if august_games:
                            print(f"   🎯 Found {len(august_games)} games in August 2025:")
                            for game in august_games[:5]:
                                date = game.get('startDate', 'Unknown').split('T')[0]
                                home = game.get('homeTeam', 'Unknown')
                                away = game.get('awayTeam', 'Unknown')
                                print(f"     {date}: {away} @ {home}")
                        else:
                            print("   ⚠️  No August 2025 games found")
                else:
                    print("   ℹ️  No games returned")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

async def test_mcp_server():
    """Test the MCP server with better error handling"""
    print("\n\n🤖 Testing MCP Server...")
    print("=" * 50)
    
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
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Test with 2024 data first (known to work)
                print("\n🔍 Testing MCP Server with 2024 data...")
                
                try:
                    result = await session.call_tool("get-games", {"year": 2024, "week": 1})
                    
                    if result.content and result.content[0].text:
                        raw_text = result.content[0].text
                        print(f"   Raw response length: {len(raw_text)} characters")
                        print(f"   First 200 chars: {raw_text[:200]}")
                        
                        try:
                            data = json.loads(raw_text)
                            print(f"   ✅ Successfully parsed JSON: {len(data)} games")
                            
                            if len(data) > 0:
                                sample_game = data[0]
                                date = sample_game.get('startDate', 'Unknown').split('T')[0]
                                home = sample_game.get('homeTeam', 'Unknown')
                                away = sample_game.get('awayTeam', 'Unknown')
                                print(f"   📊 Sample: {date}: {away} @ {home}")
                                
                        except json.JSONDecodeError as e:
                            print(f"   ❌ JSON Parse Error: {e}")
                            print(f"   Raw text: {raw_text[:500]}")
                    else:
                        print("   ❌ No content in response")
                        
                except Exception as e:
                    print(f"   ❌ MCP Error: {e}")
                
                # Now test 2025
                print("\n🔍 Testing MCP Server with 2025 data...")
                
                try:
                    result = await session.call_tool("get-games", {"year": 2025})
                    
                    if result.content and result.content[0].text:
                        raw_text = result.content[0].text
                        print(f"   Raw response: {raw_text[:200]}")
                        
                        try:
                            data = json.loads(raw_text)
                            print(f"   ✅ 2025 data available: {len(data)} games")
                            
                            # Look for August games
                            august_games = [g for g in data if '2025-08' in g.get('startDate', '')]
                            if august_games:
                                print(f"   🎯 August 2025 games: {len(august_games)}")
                                for game in august_games[:3]:
                                    date = game.get('startDate', 'Unknown').split('T')[0]
                                    home = game.get('homeTeam', 'Unknown')
                                    away = game.get('awayTeam', 'Unknown')
                                    print(f"     {date}: {away} @ {home}")
                            else:
                                print("   ⚠️  No August 2025 games in MCP response")
                                
                        except json.JSONDecodeError:
                            print(f"   ⚠️  2025 response not JSON: {raw_text}")
                    else:
                        print("   ℹ️  No 2025 data returned")
                        
                except Exception as e:
                    print(f"   ❌ 2025 MCP Error: {e}")
                    
    except Exception as e:
        print(f"❌ Failed to connect to MCP server: {e}")

def main():
    """Main function to run both tests"""
    print("🏈 CFBD Games Test - August 23, 2025")
    print("=" * 60)
    
    # First test direct API
    test_direct_api_first()
    
    # Then test MCP server
    asyncio.run(test_mcp_server())
    
    print("\n📋 CONCLUSION")
    print("=" * 50)
    print("This test checks both direct API access and MCP server functionality")
    print("to determine what data is available for August 23, 2025.")

if __name__ == "__main__":
    main()