#!/usr/bin/env python3
"""
CONSERVATIVE TEST: Single Team Player Data via MCP

This tests getting player data for ONE team only to understand:
1. Data structure and quality
2. Whether recent stats are included
3. If approach is worth pursuing

Uses only 1-3 API calls maximum.
"""

import json
import asyncio
import httpx
from datetime import datetime

MCP_SERVER_URL = "http://localhost:3000/mcp"

async def call_mcp_tool(tool_name, arguments=None):
    """Call MCP tool with careful call tracking"""
    if arguments is None:
        arguments = {}
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    print(f"🔄 MCP Tool: {tool_name}")
    print(f"📊 Args: {arguments}")
    print(f"⚠️  API Call #{get_call_count()}")
    
    confirm = input("Use 1 API call? (y/n): ").lower().strip()
    if confirm != 'y':
        print("❌ Cancelled")
        return None
    
    increment_call_count()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(MCP_SERVER_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(f"❌ MCP Error: {result['error']}")
                return None
            
            # Save with descriptive filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mcp_{tool_name}_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved: {filename}")
            return result
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        return None

# Simple call counter
call_count = 0
def get_call_count():
    return call_count + 1

def increment_call_count():
    global call_count
    call_count += 1

async def strategy_1_known_team():
    """
    Strategy 1: If we know Liverpool's team_id, get players directly
    Common soccer APIs use IDs like 42, 50, 61 for Liverpool
    """
    print("\n🎯 Strategy 1: Try Known Liverpool Team IDs")
    print("Many APIs use common IDs for Liverpool: 42, 50, 61, 45")
    
    # Try common Liverpool team IDs
    liverpool_ids = [42, 50, 61, 45, 40]
    
    for team_id in liverpool_ids:
        print(f"\n🔍 Trying Liverpool team_id: {team_id}")
        
        # Try different possible tool names
        for tool_name in ["getPlayers", "getTeamRoster", "getTeamPlayers", "players"]:
            print(f"   Tool: {tool_name}")
            confirm = input(f"   Try {tool_name} with team_id {team_id}? (y/n/stop): ").lower().strip()
            
            if confirm == 'stop':
                return None
            elif confirm == 'y':
                result = await call_mcp_tool(tool_name, {"team_id": team_id})
                if result and "error" not in result:
                    print(f"🎉 SUCCESS! Found working combination:")
                    print(f"   Tool: {tool_name}")
                    print(f"   Liverpool team_id: {team_id}")
                    return result
                break  # Try next team_id
    
    print("❌ No luck with known team IDs")
    return None

async def strategy_2_find_liverpool():
    """
    Strategy 2: Get EPL teams, find Liverpool, then get players
    Uses 2 calls: teams + players
    """
    print("\n🎯 Strategy 2: Find Liverpool via EPL Teams")
    
    # First, get EPL teams (EPL league_id is often 39, 42, or 228)
    epl_ids = [39, 42, 228]
    
    for league_id in epl_ids:
        print(f"\n🔍 Trying EPL league_id: {league_id}")
        
        result = await call_mcp_tool("getTeams", {"league_id": league_id})
        if result:
            # Look for Liverpool in the response
            teams_data = extract_teams_from_response(result)
            liverpool_id = find_liverpool_in_teams(teams_data)
            
            if liverpool_id:
                print(f"🎉 Found Liverpool! team_id: {liverpool_id}")
                
                # Now get Liverpool players
                players_result = await call_mcp_tool("getPlayers", {"team_id": liverpool_id})
                return players_result
            else:
                print("❌ Liverpool not found in this league")
    
    return None

def extract_teams_from_response(mcp_response):
    """Extract teams data from MCP response"""
    try:
        if "result" in mcp_response:
            result = mcp_response["result"]
            if isinstance(result, list) and result:
                # MCP often returns content in text field
                if "text" in result[0]:
                    return json.loads(result[0]["text"])
        return None
    except:
        return None

def find_liverpool_in_teams(teams_data):
    """Find Liverpool's team_id in teams data"""
    if not teams_data:
        return None
    
    if isinstance(teams_data, list):
        for team in teams_data:
            if isinstance(team, dict):
                name = team.get("name", "").lower()
                if "liverpool" in name:
                    return team.get("id") or team.get("team_id")
    return None

async def analyze_player_data(result):
    """Analyze what player data we got"""
    if not result:
        return
    
    print("\n📊 PLAYER DATA ANALYSIS:")
    print("=" * 50)
    
    try:
        # Extract player data from MCP response
        if "result" in result:
            mcp_result = result["result"]
            if isinstance(mcp_result, list) and mcp_result:
                if "text" in mcp_result[0]:
                    players_data = json.loads(mcp_result[0]["text"])
                    
                    if isinstance(players_data, list):
                        print(f"✅ Found {len(players_data)} players")
                        
                        if players_data:
                            sample_player = players_data[0]
                            print(f"\n📋 Sample Player Data:")
                            print(f"   Keys available: {list(sample_player.keys())}")
                            
                            # Check for stats fields
                            stats_fields = ["goals", "assists", "appearances", "minutes", "stats"]
                            found_stats = [field for field in stats_fields if field in sample_player]
                            
                            print(f"   Stats fields found: {found_stats}")
                            print(f"   Has recent stats: {'YES' if found_stats else 'NO'}")
                            
                            # Show sample player
                            print(f"\n👤 Sample Player:")
                            for key, value in sample_player.items():
                                print(f"      {key}: {value}")
                    
                    else:
                        print(f"❌ Unexpected data structure: {type(players_data)}")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

async def main():
    print("🧪 CONSERVATIVE SOCCER PLAYER TEST")
    print("=" * 50)
    print("Goal: Get player data for ONE team to evaluate quality")
    print("Max usage: 3 API calls")
    print("=" * 50)
    
    print("\nChoose testing strategy:")
    print("1. Try known Liverpool team IDs (faster, 1 call)")
    print("2. Find Liverpool via EPL teams (slower, 2 calls)")
    
    choice = input("Strategy (1/2): ").strip()
    
    result = None
    if choice == "1":
        result = await strategy_1_known_team()
    elif choice == "2":
        result = await strategy_2_find_liverpool()
    else:
        print("❌ Invalid choice")
        return
    
    # Analyze what we got
    await analyze_player_data(result)
    
    print(f"\n📊 SUMMARY:")
    print(f"   API calls used: {call_count}")
    print(f"   Calls remaining today: {75 - call_count}")
    
    if result:
        print(f"   Result: SUCCESS - check JSON file for full data")
    else:
        print(f"   Result: FAILED - may need different approach")

if __name__ == "__main__":
    asyncio.run(main())