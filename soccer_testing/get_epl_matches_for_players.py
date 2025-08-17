#!/usr/bin/env python3
"""
Get EPL Matches to Find Player Data

Since team-specific endpoints don't work, let's get recent EPL matches
and look for Fulham games to extract player lineups.

Strategy: /matches/?league_id=228&date=recent to find Fulham matches

YOUR API KEY: a9f37754a540df435e8c40ed89c08565166524ed
LIMIT: 70 calls remaining
"""

import requests
import json
from datetime import datetime, timedelta

# API Configuration
BASE_URL = "https://api.soccerdataapi.com"
API_KEY = "a9f37754a540df435e8c40ed89c08565166524ed"

HEADERS = {
    'Accept-Encoding': 'gzip',
    'Content-Type': 'application/json'
}

def get_recent_epl_matches():
    """Get recent EPL matches to find ones with Fulham"""
    
    print(f"⚽ GETTING RECENT EPL MATCHES TO FIND FULHAM")
    print("=" * 60)
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print(f"📍 Strategy: Get EPL matches, find Fulham games, extract players")
    print(f"🏆 League ID: 228 (EPL)")
    print(f"⚠️  This will use 1 of your 70 remaining API calls")
    print("=" * 60)
    
    # Confirm before making call
    confirm = input(f"Get recent EPL matches to find Fulham players? (y/n): ").lower().strip()
    if confirm != 'y':
        print("❌ API call cancelled")
        return None
    
    # Try different date approaches
    today = datetime.now()
    date_options = [
        today.strftime("%Y-%m-%d"),  # Today
        (today - timedelta(days=1)).strftime("%Y-%m-%d"),  # Yesterday
        (today - timedelta(days=7)).strftime("%Y-%m-%d"),  # Last week
        None  # No date filter
    ]
    
    for date_str in date_options:
        print(f"\n🔍 Trying date: {date_str or 'No date filter'}")
        
        # Prepare request
        url = f"{BASE_URL}/matches/"
        params = {
            'league_id': 228,  # EPL
            'auth_token': API_KEY
        }
        
        if date_str:
            params['date'] = date_str
        
        try:
            print(f"🌐 Making API request...")
            print(f"🔗 URL: {url}")
            print(f"📊 Params: {params}")
            
            response = requests.get(url, headers=HEADERS, params=params, timeout=30)
            
            print(f"📈 HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                # Parse JSON response
                data = response.json()
                
                # Save to file with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                date_suffix = f"_{date_str}" if date_str else "_no_date"
                filename = f"epl_matches{date_suffix}_{timestamp}.json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Success! Data saved to: {filename}")
                
                # Look for Fulham matches and analyze for players
                fulham_players = analyze_epl_matches_for_fulham(data)
                if fulham_players:
                    return fulham_players
                else:
                    print("❌ No Fulham matches found with player data")
                    continue
            
            elif response.status_code == 400:
                print(f"❌ HTTP Error 400")
                print(f"Response: {response.text[:200]}")
                continue
            
            else:
                print(f"❌ HTTP Error {response.status_code}")
                print(f"Response: {response.text[:200]}")
                continue
                
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    print("❌ No Fulham matches found in recent EPL data")
    return None

def analyze_epl_matches_for_fulham(matches_data):
    """Find Fulham matches and extract player data"""
    
    print(f"\n📊 ANALYZING EPL MATCHES FOR FULHAM PLAYERS")
    print("=" * 50)
    
    if not matches_data:
        print("❌ No matches data received")
        return None
    
    try:
        # Handle different response structures
        matches_list = None
        
        if isinstance(matches_data, dict):
            if "data" in matches_data:
                matches_list = matches_data["data"]
            elif "results" in matches_data:
                matches_list = matches_data["results"]
            elif "matches" in matches_data:
                matches_list = matches_data["matches"]
            else:
                print(f"📊 Response keys: {list(matches_data.keys())}")
                print(f"📄 Sample content: {str(matches_data)[:300]}")
                return None
        elif isinstance(matches_data, list):
            matches_list = matches_data
        
        if matches_list:
            print(f"✅ Found {len(matches_list)} EPL matches to check")
            
            fulham_matches = []
            
            # Look for Fulham matches
            for match in matches_list:
                if isinstance(match, dict):
                    home_team = match.get("home_team", {})
                    away_team = match.get("away_team", {})
                    
                    # Check if Fulham is in this match
                    home_name = home_team.get("name", "").lower() if isinstance(home_team, dict) else str(home_team).lower()
                    away_name = away_team.get("name", "").lower() if isinstance(away_team, dict) else str(away_team).lower()
                    
                    if "fulham" in home_name or "fulham" in away_name:
                        print(f"🎯 Found Fulham match!")
                        print(f"   {home_team.get('name', 'Unknown')} vs {away_team.get('name', 'Unknown')}")
                        print(f"   Match ID: {match.get('id', 'Unknown')}")
                        print(f"   Date: {match.get('date', 'Unknown')}")
                        
                        fulham_matches.append(match)
            
            if fulham_matches:
                print(f"\n✅ Found {len(fulham_matches)} Fulham matches")
                
                # Extract players from these matches
                all_players = {}
                
                for match in fulham_matches:
                    match_players = extract_players_from_match(match)
                    
                    # Merge players
                    for player_id, player_info in match_players.items():
                        if player_id not in all_players:
                            all_players[player_id] = player_info
                
                if all_players:
                    # Save players
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    players_file = f"fulham_players_from_matches_{timestamp}.json"
                    
                    with open(players_file, 'w', encoding='utf-8') as f:
                        json.dump(all_players, f, indent=2, ensure_ascii=False)
                    
                    print(f"\n✅ Extracted {len(all_players)} Fulham players")
                    print(f"📁 Players saved to: {players_file}")
                    
                    # Show player summary
                    print(f"\n👥 FULHAM PLAYERS FOUND:")
                    for player_id, player_info in list(all_players.items())[:15]:
                        print(f"   {player_info['name']} (ID: {player_id}) - {player_info.get('position', 'Unknown')}")
                    
                    if len(all_players) > 15:
                        print(f"   ... and {len(all_players) - 15} more players")
                    
                    return all_players
                
                else:
                    print("❌ No player data found in Fulham matches")
                    
                    # Show match structure for debugging
                    if fulham_matches:
                        sample_match = fulham_matches[0]
                        print(f"\n🔍 Sample Fulham match structure:")
                        print(f"   Match keys: {list(sample_match.keys())}")
                        
                        # Look for lineup-like fields
                        lineup_fields = ["lineup", "lineups", "players", "squad", "events", "statistics"]
                        for field in lineup_fields:
                            if field in sample_match:
                                print(f"   ✅ Found '{field}' field")
                            else:
                                print(f"   ❌ No '{field}' field")
                    
                    return None
            
            else:
                print("❌ No Fulham matches found in EPL data")
                print("💡 Fulham might not have recent matches, or different team name")
                
                # Show sample team names for debugging
                print(f"\n🔍 Sample team names found:")
                sample_teams = set()
                for match in matches_list[:5]:
                    if isinstance(match, dict):
                        home_team = match.get("home_team", {})
                        away_team = match.get("away_team", {})
                        
                        home_name = home_team.get("name", "Unknown") if isinstance(home_team, dict) else str(home_team)
                        away_name = away_team.get("name", "Unknown") if isinstance(away_team, dict) else str(away_team)
                        
                        sample_teams.add(home_name)
                        sample_teams.add(away_name)
                
                for team_name in list(sample_teams)[:10]:
                    print(f"   - {team_name}")
                
                return None
        
        else:
            print("❌ No matches list found in response")
            return None
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return None

def extract_players_from_match(match_data):
    """Extract player info from a single match"""
    
    players = {}
    
    try:
        # Look for lineup/player data in various fields
        player_fields = ["lineup", "lineups", "players", "squad", "events", "home_lineup", "away_lineup"]
        
        for field in player_fields:
            if field in match_data:
                field_data = match_data[field]
                
                if isinstance(field_data, dict):
                    # Might have home/away lineups
                    for key, value in field_data.items():
                        if isinstance(value, list):
                            for player in value:
                                if isinstance(player, dict):
                                    player_id = player.get("id") or player.get("player_id")
                                    player_name = player.get("name") or player.get("player_name")
                                    
                                    if player_id and player_name:
                                        players[player_id] = {
                                            "name": player_name,
                                            "position": player.get("position"),
                                            "number": player.get("number") or player.get("jersey_number"),
                                            "team_id": 4145  # Fulham
                                        }
                
                elif isinstance(field_data, list):
                    # Direct list of players
                    for player in field_data:
                        if isinstance(player, dict):
                            player_id = player.get("id") or player.get("player_id")
                            player_name = player.get("name") or player.get("player_name")
                            
                            if player_id and player_name:
                                players[player_id] = {
                                    "name": player_name,
                                    "position": player.get("position"),
                                    "number": player.get("number") or player.get("jersey_number"),
                                    "team_id": 4145  # Fulham
                                }
    
    except Exception as e:
        print(f"❌ Error extracting players from match: {e}")
    
    return players

def main():
    print("🚀 GET FULHAM PLAYERS VIA EPL MATCHES")
    print("Strategy: Get EPL matches, find Fulham games, extract lineups")
    print("API calls used so far: 5/75 (70 remaining)")
    
    players = get_recent_epl_matches()
    
    print(f"\n📊 FINAL SUMMARY:")
    if players:
        print(f"✅ SUCCESS: Found {len(players)} Fulham players")
        print(f"📁 Check JSON files for complete player data")
        print(f"🎯 Next: Test individual player stats with player IDs")
    else:
        print("❌ FAILED: Could not find Fulham players")
        print("💡 Possible issues:")
        print("   - No recent Fulham matches")
        print("   - Match data doesn't include lineups")
        print("   - Different team name format")
    
    print(f"\n⚠️  API calls used: 6/75")
    print(f"📊 Calls remaining today: 69")

if __name__ == "__main__":
    main()