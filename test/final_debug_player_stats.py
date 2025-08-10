#!/usr/bin/env python3
"""
Final debug test - call ESPN APIs directly vs through our HTTP server.
"""
import sys
import os
import asyncio
import httpx
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sports_mcp'))

from interactive_sports_test import SportsTestInterface

async def test_direct_vs_server():
    """Compare direct ESPN API calls vs our HTTP server"""
    print("Direct ESPN API vs HTTP Server Comparison")
    print("="*50)
    
    player_id = "32655"  # Byron Buxton
    sport = "baseball"
    league = "mlb"
    
    # Test 1: Direct ESPN Core API call (we know this works)
    print("1. Direct ESPN Core API call...")
    direct_url = f"https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/athletes/{player_id}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(direct_url, timeout=10.0)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   SUCCESS: Got player {data.get('displayName', 'Unknown')}")
                
                # Check for $ref links
                if "statisticslog" in data:
                    log_ref = data["statisticslog"].get("$ref", "No $ref")
                    print(f"   Statisticslog ref: {log_ref[:80]}...")
                
            else:
                print(f"   FAILED: {response.status_code}")
                
        except Exception as e:
            print(f"   ERROR: {e}")
    
    # Test 2: HTTP server call  
    print(f"\n2. Our HTTP server call...")
    interface = SportsTestInterface()
    interface.current_sport_league = (sport, league)
    
    success, result = interface.make_request("POST", "/espn/player-stats", {
        "sport": sport,
        "league": league,
        "player_id": player_id,
        "limit": 5
    })
    
    print(f"   API Success: {success}")
    if success:
        if result.get("ok"):
            print(f"   Result: SUCCESS!")
            player_data = result.get("data", {})
            profile = player_data.get("player_profile", {})
            if "athlete" in profile:
                name = profile["athlete"].get("displayName", "Unknown")
                print(f"   Player: {name}")
        else:
            print(f"   Result: FAILED - {result.get('message', 'Unknown error')}")
    else:
        print(f"   Result: API ERROR - {result}")

async def test_different_params():
    """Test if ESPN Core API needs specific parameters"""
    print(f"\n{'='*50}")
    print("Testing ESPN Core API Parameters")
    print("="*50)
    
    base_url = "https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/athletes/32655"
    
    # Different parameter combinations
    param_tests = [
        {},
        {"lang": "en", "region": "us"},
        {"lang": "en"},
        {"region": "us"},
        {"season": "2024"},
        {"limit": "5"}
    ]
    
    async with httpx.AsyncClient() as client:
        for i, params in enumerate(param_tests, 1):
            print(f"\n{i}. Testing with params: {params}")
            
            try:
                response = await client.get(base_url, params=params, timeout=10.0)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   SUCCESS with these params!")
                elif response.status_code == 404:
                    print(f"   404 Not Found")
                else:
                    print(f"   Other status: {response.status_code}")
                    
            except Exception as e:
                print(f"   ERROR: {e}")

if __name__ == "__main__":
    async def main():
        await test_direct_vs_server()
        await test_different_params()
    
    asyncio.run(main())