#!/usr/bin/env python3
"""
Get Kansas State players using CFBD API
"""

import requests
import json
from datetime import datetime

def get_kansas_state_players():
    """Get Kansas State player data"""
    
    api_key = "Z0NGwLNiztE/3/YtS+Jajy4tID7xbjON1UFh6s8q0XgpM66VEkMGHYCt6ALSud7Y"
    base_url = "https://api.collegefootballdata.com"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    
    print("🏈 Kansas State Players Data")
    print("=" * 50)
    
    # Try different player-related endpoints
    endpoints_to_try = [
        {
            "name": "Roster (2024)",
            "url": "/roster",
            "params": {"team": "Kansas State", "year": 2024}
        },
        {
            "name": "Roster (2025)", 
            "url": "/roster",
            "params": {"team": "Kansas State", "year": 2025}
        },
        {
            "name": "Player Stats (2024)",
            "url": "/stats/player/season",
            "params": {"team": "Kansas State", "year": 2024}
        },
        {
            "name": "Player Usage (2024)",
            "url": "/player/usage",
            "params": {"team": "Kansas State", "year": 2024}
        }
    ]
    
    for endpoint in endpoints_to_try:
        print(f"\n🔍 Trying: {endpoint['name']}")
        print(f"   Endpoint: {endpoint['url']}")
        
        try:
            response = requests.get(
                f"{base_url}{endpoint['url']}", 
                headers=headers, 
                params=endpoint['params'], 
                timeout=15
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success! Found {len(data)} records")
                
                if len(data) > 0:
                    print(f"   📊 Sample data structure:")
                    sample = data[0]
                    for key, value in sample.items():
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:50] + "..."
                        print(f"     • {key}: {value}")
                    
                    # Show some actual players if this is roster data
                    if 'name' in sample or 'player' in sample:
                        print(f"\n   👥 Sample Players:")
                        for i, player in enumerate(data[:5]):
                            name = player.get('name') or player.get('player', 'Unknown')
                            position = player.get('position', 'Unknown')
                            jersey = player.get('jersey', 'N/A')
                            year = player.get('year', 'Unknown')
                            print(f"     {i+1}. #{jersey} {name} - {position} ({year})")
                        
                        if len(data) > 5:
                            print(f"     ... and {len(data) - 5} more players")
                
            elif response.status_code == 404:
                print(f"   ⚠️  Endpoint not found or no data available")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Try to get the most recent successful roster data
    print(f"\n🎯 Getting Complete Kansas State Roster...")
    
    try:
        # Try 2024 roster first (most likely to have data)
        response = requests.get(
            f"{base_url}/roster", 
            headers=headers, 
            params={"team": "Kansas State", "year": 2024}, 
            timeout=15
        )
        
        if response.status_code == 200:
            roster = response.json()
            
            if roster:
                print(f"✅ Found {len(roster)} Kansas State players (2024 roster)")
                print("=" * 60)
                
                # Group by position
                positions = {}
                for player in roster:
                    pos = player.get('position', 'Unknown')
                    if pos not in positions:
                        positions[pos] = []
                    positions[pos].append(player)
                
                # Display by position
                for position in sorted(positions.keys()):
                    players = positions[position]
                    print(f"\n🏈 {position} ({len(players)} players):")
                    
                    for player in sorted(players, key=lambda x: int(x.get('jersey', 0)) if str(x.get('jersey', '')).isdigit() else 999):
                        name = player.get('name', 'Unknown')
                        jersey = player.get('jersey', 'N/A')
                        year = player.get('year', 'Unknown')
                        height = player.get('height', 'N/A')
                        weight = player.get('weight', 'N/A')
                        hometown = player.get('hometown', 'N/A')
                        
                        print(f"   #{jersey:2} {name:25} {year:2} {height:6} {weight:3}lbs {hometown}")
                
                return roster
            else:
                print("⚠️  No roster data found for Kansas State")
        else:
            print(f"❌ Failed to get roster: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting roster: {e}")
    
    return []

if __name__ == "__main__":
    players = get_kansas_state_players()
    
    if players:
        print(f"\n✅ SUCCESS: Retrieved {len(players)} Kansas State players!")
        print("Player data is available through the CFBD API! 🎉")
    else:
        print("\n🤔 No player data found")
        print("Player data might not be available for the current season yet")