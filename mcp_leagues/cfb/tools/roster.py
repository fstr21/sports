#!/usr/bin/env python3
"""
CFB Roster Tool - Test college football roster endpoint
"""

import asyncio
import json
import httpx

# Test the roster endpoint
async def test_cfb_roster():
    """Test CFB roster endpoint"""
    
    api_key = "Z0NGwLNiztE/3/YtS+Jajy4tID7xbjON1UFh6s8q0XgpM66VEkMGHYCt6ALSud7Y"
    base_url = "https://api.collegefootballdata.com"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    test_cases = [
        {
            "name": "Kansas State 2024 Roster",
            "params": {"team": "Kansas State", "year": 2024}
        },
        {
            "name": "Iowa State 2024 Roster",
            "params": {"team": "Iowa State", "year": 2024}
        },
        {
            "name": "Stanford 2024 Roster",
            "params": {"team": "Stanford", "year": 2024}
        }
    ]
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        for test in test_cases:
            print(f"\n👥 Testing: {test['name']}")
            print("-" * 40)
            
            try:
                response = await client.get(
                    f"{base_url}/roster",
                    headers=headers,
                    params=test['params']
                )
                
                if response.status_code == 200:
                    roster = response.json()
                    print(f"✅ Success: Found {len(roster)} players")
                    
                    # Group by position
                    positions = {}
                    for player in roster:
                        pos = player.get('position', 'Unknown')
                        if pos not in positions:
                            positions[pos] = []
                        positions[pos].append(player)
                    
                    print(f"📊 Position breakdown:")
                    for pos, players in sorted(positions.items()):
                        print(f"   {pos}: {len(players)} players")
                    
                    # Show sample players
                    print(f"\n⭐ Sample players:")
                    for i, player in enumerate(roster[:5]):
                        name = f"{player.get('firstName', '')} {player.get('lastName', '')}".strip()
                        pos = player.get('position', 'Unknown')
                        jersey = player.get('jersey', 'N/A')
                        year = player.get('year', 'Unknown')
                        print(f"   {i+1}. #{jersey} {name} - {pos} ({year})")
                        
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_cfb_roster())