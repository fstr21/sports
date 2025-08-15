#!/usr/bin/env python3
"""
CFB Player Stats Tool - Test college football player statistics endpoint
"""

import asyncio
import json
import httpx

# Test the player stats endpoint
async def test_cfb_player_stats():
    """Test CFB player stats endpoint"""
    
    api_key = "Z0NGwLNiztE/3/YtS+Jajy4tID7xbjON1UFh6s8q0XgpM66VEkMGHYCt6ALSud7Y"
    base_url = "https://api.collegefootballdata.com"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    test_cases = [
        {
            "name": "Avery Johnson 2024 Stats",
            "params": {"year": 2024, "team": "Kansas State", "player": "Avery Johnson"}
        },
        {
            "name": "Kansas State 2024 Passing Stats",
            "params": {"year": 2024, "team": "Kansas State", "category": "passing"}
        },
        {
            "name": "Big 12 2024 Rushing Stats",
            "params": {"year": 2024, "conference": "Big 12", "category": "rushing"}
        }
    ]
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        for test in test_cases:
            print(f"\n📊 Testing: {test['name']}")
            print("-" * 40)
            
            try:
                response = await client.get(
                    f"{base_url}/stats/player/season",
                    headers=headers,
                    params=test['params']
                )
                
                if response.status_code == 200:
                    stats = response.json()
                    print(f"✅ Success: Found {len(stats)} stat records")
                    
                    # Group by player and category
                    players = {}
                    categories = {}
                    
                    for stat in stats:
                        player_name = stat.get('player', 'Unknown')
                        category = stat.get('category', 'Unknown')
                        stat_type = stat.get('statType', 'Unknown')
                        value = stat.get('stat', 0)
                        
                        if player_name not in players:
                            players[player_name] = {}
                        if category not in players[player_name]:
                            players[player_name][category] = {}
                        players[player_name][category][stat_type] = value
                        
                        if category not in categories:
                            categories[category] = 0
                        categories[category] += 1
                    
                    print(f"📈 Categories found:")
                    for cat, count in categories.items():
                        print(f"   {cat}: {count} records")
                    
                    print(f"\n⭐ Sample player stats:")
                    for i, (player, player_stats) in enumerate(list(players.items())[:3]):
                        print(f"   {i+1}. {player}:")
                        for category, cat_stats in player_stats.items():
                            key_stats = list(cat_stats.items())[:3]  # Show first 3 stats
                            stats_str = ", ".join([f"{k}: {v}" for k, v in key_stats])
                            print(f"      {category}: {stats_str}")
                        
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_cfb_player_stats())