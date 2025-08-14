#!/usr/bin/env python3
"""
Enhanced MLB Player Stats Testing
Show detailed game-by-game data to verify accuracy
"""

import requests
import json
from datetime import datetime

# MLB MCP Server URL
MLB_MCP_URL = "https://mlbmcp-production.up.railway.app/mcp"

def call_mlb_tool(tool_name, arguments=None):
    """Call an MLB MCP tool and return the response"""
    if arguments is None:
        arguments = {}
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    try:
        response = requests.post(MLB_MCP_URL, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def print_separator(title):
    """Print a nice separator with title"""
    print("=" * 80)
    print(f" {title}")
    print("=" * 80)

def test_player_detailed_stats():
    """Test player stats with detailed game-by-game breakdown"""
    print_separator("DETAILED PLAYER STATS TEST")
    
    # Use active player IDs 
    player_ids = [592450]  # Aaron Judge - guaranteed recent activity
    
    result = call_mlb_tool("getMLBPlayerLastN", {
        "player_ids": player_ids,
        "count": 10,
        "stats": ["hits", "homeRuns", "atBats", "runsBattedIn", "doubles", "triples"]
    })
    
    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
        return
    
    if not result.get("result", {}).get("ok"):
        print(f"❌ FAILED: {result.get('result', {}).get('error', 'Unknown error')}")
        return
    
    data = result["result"]["data"]
    print(f"✅ SUCCESS: Player stats retrieved")
    print(f"📊 Source: {data['source']}")
    print(f"🎯 Stats requested: {', '.join(data['requested_stats'])}")
    print()
    
    # Show detailed results for each player
    for player_id, player_data in data["results"].items():
        print(f"👤 Player {player_id}:")
        print(f"  📊 Last {player_data['count']} games (most recent first)")
        print()
        
        # Show individual games
        for i, game in enumerate(player_data["games"], 1):
            date = game["date_et"]
            time = game["et_datetime"]
            hits = game.get("hits", 0)
            hrs = game.get("homeRuns", 0)
            abs = game.get("atBats", 0)
            rbis = game.get("runsBattedIn", 0)
            doubles = game.get("doubles", 0)
            triples = game.get("triples", 0)
            
            print(f"    Game {i} ({date}):")
            print(f"      🕐 {time}")
            print(f"      📊 {hits}-for-{abs}, {hrs} HR, {doubles} 2B, {triples} 3B, {rbis} RBI")
            print()
        
        # Show aggregates
        aggs = player_data.get("aggregates", {})
        print(f"  📈 10-Game Totals:")
        for stat_name in data["requested_stats"]:
            avg = aggs.get(f"{stat_name}_avg", 0)
            total = aggs.get(f"{stat_name}_sum", 0)
            print(f"    • {stat_name}: {avg:.2f} avg, {total} total")
        print()
        print("-" * 60)
        print()
    
    # Show any errors
    if data.get("errors"):
        print("❌ Errors:")
        for player_id, error in data["errors"].items():
            print(f"  Player {player_id}: {error}")
        print()

def main():
    """Run detailed player stats test"""
    print_separator("MLB Player Stats - Detailed Verification")
    print(f"🚀 Testing MLB MCP at: {MLB_MCP_URL}")
    print(f"🕐 Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_player_detailed_stats()
    
    print_separator("Testing Complete!")
    print("🎉 Review the game-by-game data above to verify accuracy!")

if __name__ == "__main__":
    main()