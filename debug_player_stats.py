#!/usr/bin/env python3
"""
Debug MLB player stats tools to understand data structure
"""
import asyncio
import json
import httpx

async def debug_player_stats():
    """Debug MLB player stats data structure"""
    
    mlb_url = "https://mlbmcp-production.up.railway.app/mcp"
    
    print("Debugging MLB Player Stats Tools")
    print("=" * 40)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test 1: Get team roster to find player IDs
            print("\n1. Testing getMLBTeamRoster (Athletics - team_id: 133):")
            roster_payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 1,
                "params": {
                    "name": "getMLBTeamRoster",
                    "arguments": {"teamId": 133}  # Athletics
                }
            }
            
            response = await client.post(mlb_url, json=roster_payload)
            response.raise_for_status()
            roster_result = response.json()
            
            print("Roster Response Structure:")
            response_text = json.dumps(roster_result, indent=2)
            if len(response_text) > 1000:
                print(response_text[:1000] + "...")
            else:
                print(response_text)
            
            # Find a player for testing
            test_player_id = None
            test_player_name = None
            
            if "result" in roster_result and "data" in roster_result["result"]:
                players = roster_result["result"]["data"].get("players", [])
                if players:
                    test_player = players[1]  # Use Brent Rooker (index 1)
                    test_player_id = test_player.get("playerId")
                    test_player_name = test_player.get("fullName")
                    print(f"\nUsing test player: {test_player_name} (ID: {test_player_id})")
            
            if not test_player_id:
                print("Could not find player ID for testing")
                return
            
            # Test 2: Get player last N games
            print(f"\n2. Testing getMLBPlayerLastN for {test_player_name}:")
            stats_payload = {
                "jsonrpc": "2.0",
                "method": "tools/call", 
                "id": 1,
                "params": {
                    "name": "getMLBPlayerLastN",
                    "arguments": {
                        "player_ids": [test_player_id],
                        "games": 5
                    }
                }
            }
            
            response = await client.post(mlb_url, json=stats_payload)
            response.raise_for_status()
            stats_result = response.json()
            
            print("Player Stats Response Structure:")
            response_text = json.dumps(stats_result, indent=2)
            if len(response_text) > 800:
                print(response_text[:800] + "...")
            else:
                print(response_text)
                
            # Test 3: Get player streaks
            print(f"\n3. Testing getMLBPlayerStreaks for {test_player_name}:")
            streaks_payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 1,
                "params": {
                    "name": "getMLBPlayerStreaks", 
                    "arguments": {"player_ids": [test_player_id]}
                }
            }
            
            response = await client.post(mlb_url, json=streaks_payload)
            response.raise_for_status()
            streaks_result = response.json()
            
            print("Player Streaks Response Structure:")
            response_text = json.dumps(streaks_result, indent=2)
            if len(response_text) > 800:
                print(response_text[:800] + "...")
            else:
                print(response_text)
                
        except Exception as e:
            print(f"Exception: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_player_stats())