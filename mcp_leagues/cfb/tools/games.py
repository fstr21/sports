#!/usr/bin/env python3
"""
CFB Games Tool - Test college football games endpoint
"""

import asyncio
import json
import httpx
from datetime import datetime

# Test the games endpoint
async def test_cfb_games():
    """Test CFB games endpoint"""
    
    api_key = "Z0NGwLNiztE/3/YtS+Jajy4tID7xbjON1UFh6s8q0XgpM66VEkMGHYCt6ALSud7Y"
    base_url = "https://api.collegefootballdata.com"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    test_cases = [
        {
            "name": "August 23, 2025 Games",
            "params": {"year": 2025, "week": 1}
        },
        {
            "name": "Kansas State Games 2024",
            "params": {"year": 2024, "team": "Kansas State"}
        },
        {
            "name": "Big 12 Games Week 1 2025",
            "params": {"year": 2025, "week": 1, "conference": "Big 12"}
        }
    ]
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        for test in test_cases:
            print(f"\n🏈 Testing: {test['name']}")
            print("-" * 40)
            
            try:
                response = await client.get(
                    f"{base_url}/games",
                    headers=headers,
                    params=test['params']
                )
                
                if response.status_code == 200:
                    games = response.json()
                    print(f"✅ Success: Found {len(games)} games")
                    
                    # Show sample games
                    for i, game in enumerate(games[:3]):
                        home = game.get('homeTeam', 'Unknown')
                        away = game.get('awayTeam', 'Unknown')
                        date = game.get('startDate', 'Unknown').split('T')[0]
                        week = game.get('week', 'Unknown')
                        print(f"   {i+1}. {away} @ {home} (Week {week}, {date})")
                    
                    if len(games) > 3:
                        print(f"   ... and {len(games) - 3} more games")
                        
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_cfb_games())