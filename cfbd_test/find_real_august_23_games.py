#!/usr/bin/env python3
"""
Find real games on August 23, 2025 - Direct API approach
"""

import requests
import json
from datetime import datetime

def find_august_23_games_direct():
    """Use direct API to find August 23, 2025 games"""
    
    api_key = "Z0NGwLNiztE/3/YtS+Jajy4tID7xbjON1UFh6s8q0XgpM66VEkMGHYCt6ALSud7Y"
    base_url = "https://api.collegefootballdata.com"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    
    print("🏈 Finding Games on August 23, 2025 (Direct API)")
    print("=" * 60)
    
    # Try different approaches
    search_params = [
        {"year": 2025, "week": 1, "description": "Week 1"},
        {"year": 2025, "week": 0, "description": "Week 0"},
        {"year": 2025, "description": "All 2025 games"}
    ]
    
    august_23_games = []
    all_august_games = []
    
    for params in search_params:
        description = params.pop('description')
        print(f"\n🔍 Searching: {description}")
        
        try:
            response = requests.get(f"{base_url}/games", headers=headers, params=params, timeout=15)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                games = response.json()
                print(f"   Total games found: {len(games)}")
                
                # Look for August 23 games
                aug_23_count = 0
                aug_games_count = 0
                
                for game in games:
                    start_date = game.get('startDate', '')
                    
                    # Check for August 23, 2025
                    if start_date.startswith('2025-08-23'):
                        august_23_games.append(game)
                        aug_23_count += 1
                    
                    # Collect all August games for reference
                    if '2025-08' in start_date:
                        all_august_games.append(game)
                        aug_games_count += 1
                
                print(f"   Games on 2025-08-23: {aug_23_count}")
                print(f"   Games in August 2025: {aug_games_count}")
                
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Display August 23 games
    if august_23_games:
        print(f"\n🎯 FOUND {len(august_23_games)} GAMES ON AUGUST 23, 2025!")
        print("=" * 70)
        
        for i, game in enumerate(august_23_games, 1):
            home_team = game.get('homeTeam', 'Unknown')
            away_team = game.get('awayTeam', 'Unknown')
            start_time = game.get('startDate', 'Unknown')
            venue = game.get('venue', 'Unknown')
            week = game.get('week', 'Unknown')
            
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
            print(f"   📊 Week: {week}")
            print(f"   🆔 Game ID: {game.get('id', 'Unknown')}")
            
            # Additional details
            if game.get('homeConference'):
                print(f"   🏆 Home Conference: {game.get('homeConference')}")
            if game.get('awayConference'):
                print(f"   🏆 Away Conference: {game.get('awayConference')}")
            if game.get('neutralSite'):
                print(f"   🏟️  Neutral Site: Yes")
    
    else:
        print("\n❌ No games found specifically on August 23, 2025")
        
        # Show what August dates DO have games
        if all_august_games:
            print(f"\n📅 However, found {len(all_august_games)} games in August 2025:")
            
            # Group by date
            dates_with_games = {}
            for game in all_august_games:
                date = game.get('startDate', '').split('T')[0]
                if date and date.startswith('2025-08'):
                    if date not in dates_with_games:
                        dates_with_games[date] = []
                    dates_with_games[date].append(game)
            
            for date in sorted(dates_with_games.keys()):
                games_on_date = dates_with_games[date]
                print(f"\n   📅 {date} ({len(games_on_date)} games):")
                for game in games_on_date[:5]:  # Show first 5
                    print(f"     • {game.get('awayTeam', 'Unknown')} @ {game.get('homeTeam', 'Unknown')}")
                if len(games_on_date) > 5:
                    print(f"     ... and {len(games_on_date) - 5} more")
        else:
            print("\n⚠️  No August 2025 games found at all")
    
    return august_23_games

if __name__ == "__main__":
    games = find_august_23_games_direct()
    
    if games:
        print(f"\n✅ SUCCESS: Found {len(games)} games on August 23, 2025!")
        print("These games match what you see in your app! 🎉")
    else:
        print("\n🤔 No games found - there might be an issue with the search parameters")
        print("The games you see might be in a different week or date format")