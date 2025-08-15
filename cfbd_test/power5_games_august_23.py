#!/usr/bin/env python3
"""
Find Power 5 conference games on August 23, 2025
Only games where at least one team is from SEC, Big Ten, Big 12, or ACC
"""

import requests
import json
from datetime import datetime

def find_power5_games():
    """Find Power 5 games on August 23, 2025"""
    
    api_key = "Z0NGwLNiztE/3/YtS+Jajy4tID7xbjON1UFh6s8q0XgpM66VEkMGHYCt6ALSud7Y"
    base_url = "https://api.collegefootballdata.com"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    
    # Power 5 conferences
    power5_conferences = {
        'SEC',
        'Big Ten', 
        'Big 12',
        'ACC'
    }
    
    print("🏈 Power 5 Games on August 23, 2025")
    print("=" * 50)
    print("Filtering for games with at least one team from:")
    for conf in sorted(power5_conferences):
        print(f"  • {conf}")
    print()
    
    try:
        # Get all games for August 23, 2025
        response = requests.get(
            f"{base_url}/games", 
            headers=headers, 
            params={"year": 2025, "week": 1}, 
            timeout=15
        )
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            return []
        
        all_games = response.json()
        print(f"🔍 Checking {len(all_games)} total games...")
        
        # Filter for August 23 games
        august_23_games = [
            game for game in all_games 
            if game.get('startDate', '').startswith('2025-08-23')
        ]
        
        print(f"📅 Found {len(august_23_games)} games on August 23, 2025")
        
        # Filter for Power 5 games
        power5_games = []
        
        for game in august_23_games:
            home_conf = game.get('homeConference', '')
            away_conf = game.get('awayConference', '')
            
            # Check if at least one team is from Power 5
            if home_conf in power5_conferences or away_conf in power5_conferences:
                power5_games.append(game)
        
        print(f"🏆 Found {len(power5_games)} Power 5 games on August 23, 2025")
        print("=" * 60)
        
        if power5_games:
            for i, game in enumerate(power5_games, 1):
                home_team = game.get('homeTeam', 'Unknown')
                away_team = game.get('awayTeam', 'Unknown')
                home_conf = game.get('homeConference', 'Unknown')
                away_conf = game.get('awayConference', 'Unknown')
                start_time = game.get('startDate', 'Unknown')
                venue = game.get('venue', 'Unknown')
                neutral_site = game.get('neutralSite', False)
                
                # Parse time
                if start_time != 'Unknown':
                    try:
                        dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        time_str = dt.strftime('%I:%M %p ET')
                    except:
                        time_str = start_time.split('T')[1] if 'T' in start_time else 'TBD'
                else:
                    time_str = 'TBD'
                
                print(f"\n🏈 Game {i}: {away_team} @ {home_team}")
                print(f"   📅 Date: Saturday, August 23, 2025")
                print(f"   ⏰ Time: {time_str}")
                print(f"   🏟️  Venue: {venue}")
                
                if neutral_site:
                    print(f"   🌍 Neutral Site Game")
                
                # Highlight Power 5 conferences
                home_power5 = home_conf in power5_conferences
                away_power5 = away_conf in power5_conferences
                
                if home_power5 and away_power5:
                    print(f"   🏆 Power 5 vs Power 5: {away_conf} vs {home_conf}")
                elif home_power5:
                    print(f"   🏆 Power 5 Home: {home_conf}")
                    print(f"   📊 Away Conference: {away_conf}")
                elif away_power5:
                    print(f"   🏆 Power 5 Away: {away_conf}")
                    print(f"   📊 Home Conference: {home_conf}")
                
                print(f"   🆔 Game ID: {game.get('id', 'Unknown')}")
                
                # Additional context
                if game.get('seasonType'):
                    print(f"   📋 Season Type: {game.get('seasonType')}")
        
        else:
            print("\n❌ No Power 5 games found on August 23, 2025")
            print("\nAll August 23 games by conference:")
            
            # Show breakdown of all games by conference
            conf_breakdown = {}
            for game in august_23_games:
                home_conf = game.get('homeConference', 'Unknown')
                away_conf = game.get('awayConference', 'Unknown')
                
                for conf in [home_conf, away_conf]:
                    if conf not in conf_breakdown:
                        conf_breakdown[conf] = 0
                    conf_breakdown[conf] += 1
            
            for conf, count in sorted(conf_breakdown.items()):
                marker = "🏆" if conf in power5_conferences else "📊"
                print(f"   {marker} {conf}: {count} team appearances")
        
        return power5_games
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

if __name__ == "__main__":
    games = find_power5_games()
    
    if games:
        print(f"\n✅ SUCCESS: Found {len(games)} Power 5 games!")
        print("These are the marquee matchups for August 23, 2025! 🎉")
    else:
        print("\n🤔 No Power 5 games on this date")
        print("Most major conference games typically start later in the season")