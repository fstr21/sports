#!/usr/bin/env python3
"""
Get Avery Johnson's detailed season statistics with breakdown
"""

import requests
import json

def get_avery_johnson_detailed_stats():
    """Get detailed breakdown of Avery Johnson's statistics"""
    
    api_key = "Z0NGwLNiztE/3/YtS+Jajy4tID7xbjON1UFh6s8q0XgpM66VEkMGHYCt6ALSud7Y"
    base_url = "https://api.collegefootballdata.com"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    
    print("🏈 Avery Johnson - Detailed Statistics")
    print("=" * 60)
    print("Kansas State QB #2 (Junior) - Player ID: 4870857")
    print("=" * 60)
    
    # Get his stats for both 2023 and 2024
    seasons = [2024, 2023]
    
    for season in seasons:
        print(f"\n📅 {season} SEASON STATISTICS")
        print("=" * 40)
        
        try:
            response = requests.get(
                f"{base_url}/stats/player/season", 
                headers=headers, 
                params={"team": "Kansas State", "year": season, "player": "Avery Johnson"}, 
                timeout=15
            )
            
            if response.status_code == 200:
                stats = response.json()
                
                # Filter for Avery Johnson
                avery_stats = [s for s in stats if 'avery' in s.get('player', '').lower() and 'johnson' in s.get('player', '').lower()]
                
                if avery_stats:
                    print(f"✅ Found {len(avery_stats)} statistical categories")
                    
                    # Group by category
                    categories = {}
                    for stat in avery_stats:
                        category = stat.get('category', 'Unknown')
                        if category not in categories:
                            categories[category] = []
                        categories[category].append(stat)
                    
                    # Display by category
                    for category, cat_stats in categories.items():
                        print(f"\n🏈 {category.upper()}")
                        print("-" * 25)
                        
                        for stat in cat_stats:
                            stat_type = stat.get('statType', 'Unknown')
                            value = stat.get('stat', 0)
                            print(f"   {stat_type}: {value}")
                    
                    # Show total games played (if available)
                    games_played = len(set(s.get('gameId') for s in avery_stats if s.get('gameId')))
                    if games_played > 0:
                        print(f"\n📊 Games with recorded stats: {games_played}")
                
                else:
                    print(f"⚠️  No stats found for Avery Johnson in {season}")
                    
        except Exception as e:
            print(f"❌ Error getting {season} stats: {e}")
    
    # Try to get game-by-game data using a different approach
    print(f"\n🎯 ATTEMPTING GAME-BY-GAME BREAKDOWN...")
    print("=" * 50)
    
    try:
        # Get all Kansas State games for 2024
        games_response = requests.get(
            f"{base_url}/games", 
            headers=headers, 
            params={"team": "Kansas State", "year": 2024}, 
            timeout=15
        )
        
        if games_response.status_code == 200:
            games = games_response.json()
            
            # Try advanced box score for recent games
            print("Checking advanced box scores for recent games...")
            
            for i, game in enumerate(games[:5]):  # Check first 5 games
                game_id = game.get('id')
                opponent = game.get('awayTeam') if game.get('homeTeam') == 'Kansas State' else game.get('homeTeam')
                date = game.get('startDate', '').split('T')[0]
                completed = game.get('completed', False)
                
                if completed:
                    print(f"\n🏈 Game {i+1}: vs {opponent} ({date}) - Game ID: {game_id}")
                    
                    try:
                        # Try advanced box score
                        box_response = requests.get(
                            f"{base_url}/game/box/advanced",
                            headers=headers,
                            params={"gameId": game_id},
                            timeout=10
                        )
                        
                        if box_response.status_code == 200:
                            box_data = box_response.json()
                            print(f"   ✅ Advanced box score available")
                            
                            # Look for Kansas State data
                            for team_data in box_data.get('teams', []):
                                if team_data.get('team') == 'Kansas State':
                                    # Look through players
                                    for player in team_data.get('players', []):
                                        if ('avery' in player.get('name', '').lower() and 
                                            'johnson' in player.get('name', '').lower()):
                                            print(f"   🎯 Found Avery Johnson in this game!")
                                            
                                            # Show his stats for this game
                                            for category, stats in player.items():
                                                if isinstance(stats, dict) and category != 'name':
                                                    print(f"     {category.upper()}:")
                                                    for stat_name, value in stats.items():
                                                        if value is not None and value != 0:
                                                            print(f"       {stat_name}: {value}")
                        else:
                            print(f"   ⚠️  Advanced box score not available (Status: {box_response.status_code})")
                            
                    except Exception as e:
                        print(f"   ❌ Error getting box score: {e}")
                else:
                    print(f"\n🏈 Game {i+1}: vs {opponent} ({date}) - Not completed yet")
                    
    except Exception as e:
        print(f"❌ Error getting games: {e}")
    
    print(f"\n📋 SUMMARY")
    print("=" * 30)
    print("✅ Player statistics ARE available through CFBD API!")
    print("📊 Available data includes:")
    print("   • Season totals by statistical category")
    print("   • Multiple seasons of historical data")
    print("   • Player performance across different stat types")
    print("   • Advanced box scores for completed games")
    print("\n💡 For game-by-game breakdowns:")
    print("   • Use advanced box score endpoint with specific game IDs")
    print("   • Player stats are categorized (passing, rushing, receiving, etc.)")
    print("   • Historical data available for multiple seasons")

if __name__ == "__main__":
    get_avery_johnson_detailed_stats()