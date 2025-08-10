#!/usr/bin/env python3
"""
Test different ESPN API URL patterns to find working player stats endpoint.
"""
import sys
import os
import asyncio
import httpx
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

async def test_espn_url_patterns():
    """Test various ESPN API URL patterns"""
    print("Testing ESPN API URL Patterns")
    print("="*40)
    
    # Known working player: Byron Buxton, ID: 32655
    player_id = "32655"
    player_name = "Byron Buxton"
    
    # Different URL patterns to try
    url_patterns = [
        # Current pattern (failing)
        f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/athletes/{player_id}",
        
        # Try with different paths
        f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/athletes/{player_id}/gamelog",
        f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/athletes/{player_id}/stats",
        f"https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/athletes/{player_id}",
        
        # Try core API
        f"https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/athletes/{player_id}/statistics",
        
        # Try different version
        f"https://site.api.espn.com/apis/site/v3/sports/baseball/mlb/athletes/{player_id}",
        
        # Try with seasons
        f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/athletes/{player_id}?season=2024",
        f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/seasons/2024/athletes/{player_id}",
    ]
    
    async with httpx.AsyncClient() as client:
        for i, url in enumerate(url_patterns, 1):
            print(f"\n{i}. Testing: {url}")
            
            try:
                response = await client.get(url, timeout=10.0)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   SUCCESS! Got JSON data")
                        print(f"   Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
                        
                        # Check if it looks like player data
                        if isinstance(data, dict):
                            if "displayName" in data or "fullName" in data:
                                name = data.get("displayName", data.get("fullName", "Unknown"))
                                print(f"   Found player name: {name}")
                            
                            if "statistics" in data or "stats" in data or "gamelog" in data:
                                print(f"   HAS STATISTICS DATA!")
                        
                        return url, data  # Return first working URL
                        
                    except Exception as e:
                        print(f"   JSON parse error: {e}")
                elif response.status_code == 404:
                    print(f"   404 Not Found")
                elif response.status_code == 403:
                    print(f"   403 Forbidden (might need auth)")
                else:
                    print(f"   Unexpected status")
                    
            except Exception as e:
                print(f"   Request error: {e}")
    
    print(f"\nAll URL patterns failed for {player_name}")
    return None, None

async def test_working_endpoints():
    """Test endpoints we know work to understand the pattern"""
    print("\n" + "="*40)
    print("Testing Known Working ESPN Endpoints")
    print("="*40)
    
    working_urls = [
        # We know scoreboard works
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard",
        # We know game summary works  
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/summary?event=401696675",
        # Try teams
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams"
    ]
    
    async with httpx.AsyncClient() as client:
        for url in working_urls:
            print(f"\nTesting: {url}")
            try:
                response = await client.get(url, timeout=10.0)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("SUCCESS - This pattern works")
                    
                    # For teams endpoint, look for athlete references
                    if "teams" in url:
                        try:
                            data = response.json()
                            print("Looking for player/athlete references in teams data...")
                            
                            # This might show us the right path to individual players
                            athletes_found = str(data).count("athlete")
                            players_found = str(data).count("player") 
                            print(f"Found {athletes_found} 'athlete' references")
                            print(f"Found {players_found} 'player' references")
                            
                        except Exception as e:
                            print(f"JSON parse error: {e}")
                    
            except Exception as e:
                print(f"Request error: {e}")

if __name__ == "__main__":
    async def main():
        working_url, data = await test_espn_url_patterns()
        await test_working_endpoints()
        
        print(f"\n{'='*40}")
        if working_url:
            print(f"FOUND WORKING PATTERN: {working_url}")
        else:
            print("NO WORKING PLAYER STATS URL FOUND")
            print("Next step: Check if we need different approach")
    
    asyncio.run(main())