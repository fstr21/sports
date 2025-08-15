#!/usr/bin/env python3
"""
Get Avery Johnson's game-by-game statistics
"""

import requests
import json
from datetime import datetime

def get_avery_johnson_stats():
    """Get Avery Johnson's detailed game statistics"""
    
    api_key = "Z0NGwLNiztE/3/YtS+Jajy4tID7xbjON1UFh6s8q0XgpM66VEkMGHYCt6ALSud7Y"
    base_url = "https://api.collegefootballdata.com"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    
    print("🏈 Avery Johnson - Game-by-Game Statistics")
    print("=" * 60)
    print("Kansas State QB #2 - Junior from Wichita, KS")
    print("=" * 60)
    
    # First, let's find Avery Johnson's player ID from the roster
    player_id = None
    try:
        roster_response = requests.get(
            f"{base_url}/roster", 
            headers=headers, 
            params={"team": "Kansas State", "year": 2024}, 
            timeout=15
        )
        
        if roster_response.status_code == 200:
            roster = roster_response.json()
            for player in roster:
                if (player.get('firstName', '').lower() == 'avery' and 
                    player.get('lastName', '').lower() == 'johnson'):
                    player_id = player.get('id')
                    print(f"✅ Found Avery Johnson - Player ID: {player_id}")
                    break
    except Exception as e:
        print(f"⚠️  Error finding player ID: {e}")
    
    # Try different approaches to get game stats
    stat_endpoints = [
        {
            "name": "Player Game Stats (2024)",
            "url": "/stats/player/season",
            "params": {"team": "Kansas State", "year": 2024, "player": "Avery Johnson"}
        },
        {
            "name": "Player Game Stats by ID (2024)",
            "url": "/stats/player/season", 
            "params": {"playerId": player_id, "year": 2024} if player_id else None
        },
        {
            "name": "Player Game Stats (2023)",
            "url": "/stats/player/season",
            "params": {"team": "Kansas State", "year": 2023, "player": "Avery Johnson"}
        },
        {
            "name": "Game Player Stats (2024)",
            "url": "/games/players",
            "params": {"team": "Kansas State", "year": 2024}
        }
    ]
    
    all_stats = []
    
    for endpoint in stat_endpoints:
        if endpoint['params'] is None:
            continue
            
        print(f"\n🔍 Trying: {endpoint['name']}")
        
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
                print(f"   ✅ Found {len(data)} records")
                
                # Filter for Avery Johnson
                avery_stats = []
                for record in data:
                    player_name = record.get('player', '') or record.get('name', '')
                    if 'avery' in player_name.lower() and 'johnson' in player_name.lower():
                        avery_stats.append(record)
                
                if avery_stats:
                    print(f"   🎯 Found {len(avery_stats)} Avery Johnson records")
                    all_stats.extend(avery_stats)
                    
                    # Show sample data structure
                    sample = avery_stats[0]
                    print(f"   📊 Sample data fields:")
                    for key, value in list(sample.items())[:8]:
                        print(f"     • {key}: {value}")
                else:
                    print(f"   ⚠️  No Avery Johnson records found")
                    
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Try to get specific game-by-game data
    print(f"\n🎯 Searching for Game-by-Game Performance...")
    
    try:
        # Get Kansas State games for 2024
        games_response = requests.get(
            f"{base_url}/games", 
            headers=headers, 
            params={"team": "Kansas State", "year": 2024}, 
            timeout=15
        )
        
        if games_response.status_code == 200:
            games = games_response.json()
            print(f"✅ Found {len(games)} Kansas State games in 2024")
            
            # Try to get player stats for specific games
            game_stats = []
            for i, game in enumerate(games[:3]):  # Check first 3 games
                game_id = game.get('id')
                opponent = game.get('awayTeam') if game.get('homeTeam') == 'Kansas State' else game.get('homeTeam')
                date = game.get('startDate', '').split('T')[0]
                
                print(f"\n   🏈 Game {i+1}: vs {opponent} ({date})")
                
                try:
                    # Try player stats for this specific game
                    game_stats_response = requests.get(
                        f"{base_url}/games/players",
                        headers=headers,
                        params={"gameId": game_id},
                        timeout=10
                    )
                    
                    if game_stats_response.status_code == 200:
                        game_data = game_stats_response.json()
                        
                        # Look for Avery Johnson in this game
                        for team_data in game_data:
                            if team_data.get('team') == 'Kansas State':
                                for category in team_data.get('categories', []):
                                    for player_stat in category.get('types', []):
                                        for athlete in player_stat.get('athletes', []):
                                            if ('avery' in athlete.get('name', '').lower() and 
                                                'johnson' in athlete.get('name', '').lower()):
                                                
                                                print(f"     ✅ Found Avery Johnson stats!")
                                                print(f"     📊 Category: {category.get('name')}")
                                                print(f"     📈 Stat: {player_stat.get('name')}")
                                                print(f"     🔢 Value: {athlete.get('stat')}")
                                                
                                                game_stats.append({
                                                    'game': f"vs {opponent}",
                                                    'date': date,
                                                    'category': category.get('name'),
                                                    'stat_type': player_stat.get('name'),
                                                    'value': athlete.get('stat')
                                                })
                    else:
                        print(f"     ⚠️  No game stats available (Status: {game_stats_response.status_code})")
                        
                except Exception as e:
                    print(f"     ❌ Error getting game stats: {e}")
            
            if game_stats:
                print(f"\n🎉 FOUND GAME-BY-GAME STATS!")
                print("=" * 50)
                
                # Group by game
                games_dict = {}
                for stat in game_stats:
                    game_key = f"{stat['game']} ({stat['date']})"
                    if game_key not in games_dict:
                        games_dict[game_key] = []
                    games_dict[game_key].append(stat)
                
                for game, stats in games_dict.items():
                    print(f"\n🏈 {game}")
                    print("-" * 40)
                    for stat in stats:
                        print(f"   {stat['category']} - {stat['stat_type']}: {stat['value']}")
                        
    except Exception as e:
        print(f"❌ Error getting games: {e}")
    
    # Summary
    if all_stats or game_stats:
        print(f"\n✅ SUCCESS: Found Avery Johnson statistics!")
        print("=" * 50)
        print("📊 Available data types:")
        if all_stats:
            print(f"   • Season statistics: {len(all_stats)} records")
        if game_stats:
            print(f"   • Game-by-game stats: {len(game_stats)} records")
        
        print("\n💡 The CFBD API provides:")
        print("   • Individual player game statistics")
        print("   • Season totals and averages")
        print("   • Performance by category (passing, rushing, etc.)")
        print("   • Historical data across multiple seasons")
        
        return all_stats + game_stats
    else:
        print(f"\n⚠️  No specific stats found for Avery Johnson")
        print("This could mean:")
        print("   • Limited playing time in 2024")
        print("   • Stats recorded under different name format")
        print("   • Data not yet available for current season")
        
        return []

if __name__ == "__main__":
    stats = get_avery_johnson_stats()
    
    if stats:
        print(f"\n🎯 CONCLUSION: Game-by-game stats ARE available!")
        print("The CFBD API can provide detailed player performance data! 🚀")
    else:
        print(f"\n🤔 No stats found, but the infrastructure is there!")
        print("Try with a different player or season for more data.")