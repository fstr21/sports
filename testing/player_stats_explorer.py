#!/usr/bin/env python3
"""
Explore potential player stats endpoints in ESPN API
"""

import asyncio
import httpx
from pathlib import Path
import os

def load_env():
    env_path = Path("C:/Users/fstr2/Desktop/sports/.env.local")
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k] = v

load_env()

ESPN_BASE = "https://site.api.espn.com"
HEADERS = {
    "User-Agent": "ESPN-Player-Explorer/1.0",
    "Accept": "application/json",
}

async def test_player_endpoints():
    """Test various potential player stats endpoints"""
    
    potential_endpoints = [
        # Player-specific endpoints
        "/apis/site/v2/sports/basketball/wnba/athletes",
        "/apis/site/v2/sports/basketball/wnba/players",
        "/apis/site/v2/sports/basketball/wnba/statistics/players",
        "/apis/site/v2/sports/basketball/wnba/leaders",
        "/apis/site/v2/sports/basketball/wnba/stats/players",
        
        # Team roster endpoints
        "/apis/site/v2/sports/basketball/wnba/teams/9/roster",  # Liberty
        "/apis/site/v2/sports/basketball/wnba/teams/9/athletes",
        
        # Season stats
        "/apis/site/v2/sports/basketball/wnba/seasons/2025/statistics",
        "/apis/site/v2/sports/basketball/wnba/seasons/2025/leaders",
        
        # Alternative formats
        "/apis/v1/sports/basketball/wnba/athletes",
        "/v2/sports/basketball/wnba/athletes",
    ]
    
    async with httpx.AsyncClient(headers=HEADERS, timeout=15.0) as client:
        print("🔍 Testing potential player stats endpoints...")
        print("=" * 60)
        
        working_endpoints = []
        
        for endpoint in potential_endpoints:
            try:
                print(f"Testing: {endpoint}")
                response = await client.get(f"{ESPN_BASE}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ SUCCESS! Status: {response.status_code}")
                    
                    # Analyze the data
                    if isinstance(data, dict):
                        print(f"  📊 Keys: {list(data.keys())}")
                        
                        # Look for player data
                        if "athletes" in data:
                            athletes = data["athletes"]
                            print(f"  👥 Found {len(athletes)} athletes")
                            if athletes and isinstance(athletes[0], dict):
                                print(f"  🏃 Player keys: {list(athletes[0].keys())}")
                        
                        if "players" in data:
                            players = data["players"]
                            print(f"  👥 Found {len(players)} players")
                        
                        if "statistics" in data:
                            stats = data["statistics"]
                            print(f"  📈 Statistics available")
                    
                    working_endpoints.append(endpoint)
                    print()
                    
                elif response.status_code == 404:
                    print(f"  ❌ Not found (404)")
                else:
                    print(f"  ⚠️ Status: {response.status_code}")
                    
            except Exception as e:
                print(f"  💥 Error: {str(e)}")
            
            await asyncio.sleep(0.3)  # Be nice to the API
        
        print("\n🎯 SUMMARY")
        print("=" * 60)
        if working_endpoints:
            print("✅ Working endpoints found:")
            for endpoint in working_endpoints:
                print(f"  • {endpoint}")
        else:
            print("❌ No player stats endpoints found in ESPN API")
            print("\n💡 RECOMMENDATION: Use web scraping for player stats")
            print("   Options:")
            print("   1. ESPN.com player pages")
            print("   2. WNBA.com official stats")
            print("   3. Basketball-Reference WNBA section")

async def test_specific_player_lookup():
    """Test if we can get individual player data by ID"""
    print("\n🔍 Testing individual player lookup...")
    print("=" * 60)
    
    # Try some known player IDs (these might not work)
    test_player_ids = ["4066533", "2529137", "3934719"]  # Some WNBA player IDs
    
    async with httpx.AsyncClient(headers=HEADERS, timeout=15.0) as client:
        for player_id in test_player_ids:
            endpoints_to_try = [
                f"/apis/site/v2/sports/basketball/wnba/athletes/{player_id}",
                f"/apis/site/v2/sports/basketball/wnba/athletes/{player_id}/stats",
                f"/apis/site/v2/sports/basketball/wnba/players/{player_id}",
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    response = await client.get(f"{ESPN_BASE}{endpoint}")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ Found player data: {endpoint}")
                        
                        # Look for player info
                        if "athlete" in data:
                            athlete = data["athlete"]
                            name = athlete.get("displayName", "Unknown")
                            print(f"  👤 Player: {name}")
                            print(f"  📊 Data keys: {list(athlete.keys())}")
                        
                        return True  # Found working endpoint
                        
                except Exception:
                    continue
    
    print("❌ No individual player endpoints found")
    return False

async def main():
    print("🏀 ESPN WNBA Player Stats Endpoint Explorer")
    print("=" * 60)
    
    await test_player_endpoints()
    await test_specific_player_lookup()
    
    print("\n🚀 NEXT STEPS FOR PLAYER STATS:")
    print("=" * 60)
    print("Since ESPN API doesn't provide player stats, consider:")
    print()
    print("1. 🕷️  Web Scraping MCP Server")
    print("   • Scrape ESPN.com player pages")
    print("   • More comprehensive data")
    print("   • Requires HTML parsing")
    print()
    print("2. 🏀 WNBA.com Official API")
    print("   • Check if WNBA has public APIs")
    print("   • Official source")
    print()
    print("3. 📊 Basketball-Reference")
    print("   • Historical and current stats")
    print("   • Well-structured data")
    print()
    print("4. 🔧 Hybrid Approach")
    print("   • Use ESPN API for games/teams/news")
    print("   • Use scraping for player stats")
    print("   • Best of both worlds")

if __name__ == "__main__":
    asyncio.run(main())