#!/usr/bin/env python3
"""
Get Players via Match Lineups

Since /team/ doesn't include players, let's try getting recent matches
for team 4145 (Fulham) and extract player data from match lineups.

The /match/ endpoint should include lineups with player names and IDs.

YOUR API KEY: a9f37754a540df435e8c40ed89c08565166524ed
LIMIT: 71 calls remaining
"""

import requests
import json
from datetime import datetime

# API Configuration
BASE_URL = "https://api.soccerdataapi.com"
API_KEY = "a9f37754a540df435e8c40ed89c08565166524ed"

HEADERS = {
    'Accept-Encoding': 'gzip',
    'Content-Type': 'application/json'
}

def get_team_matches(team_id):
    """Get recent matches for a team to extract player lineups"""
    
    print(f"⚽ GETTING RECENT MATCHES FOR TEAM {team_id} (FULHAM)")
    print("=" * 60)
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print(f"📍 Strategy: Get matches to extract player lineups")
    print(f"🏆 Team ID: {team_id}")
    print(f"⚠️  This will use 1 of your 71 remaining API calls")
    print("=" * 60)
    
    # Confirm before making call
    confirm = input(f"Get recent matches for team {team_id}? (y/n): ").lower().strip()
    if confirm != 'y':
        print("❌ API call cancelled")
        return None
    
    # Try different possible endpoints for team matches
    endpoints_to_try = [
        ("match", {"team_id": team_id}),
        ("matches", {"team_id": team_id}),
        ("fixture", {"team_id": team_id}),
        ("team_matches", {"team_id": team_id})
    ]
    
    for endpoint, params in endpoints_to_try:
        print(f"\n🔍 Trying endpoint: /{endpoint}/")
        
        # Prepare request
        url = f"{BASE_URL}/{endpoint}/"
        params['auth_token'] = API_KEY
        
        try:
            print(f"🌐 Making API request to /{endpoint}/...")
            print(f"🔗 URL: {url}")
            print(f"📊 Params: {params}")
            
            response = requests.get(url, headers=HEADERS, params=params, timeout=30)
            
            print(f"📈 HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                # Parse JSON response
                data = response.json()
                
                # Save to file with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"team_matches_{team_id}_{endpoint}_{timestamp}.json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Success with /{endpoint}/! Data saved to: {filename}")
                
                # Analyze for player data
                players = analyze_matches_for_players(data, team_id)
                if players:
                    return players
                else:
                    print("❌ No player data found in this response")
                    continue
            
            elif response.status_code == 404:
                print(f"❌ Endpoint /{endpoint}/ not found")
                continue
            
            else:
                print(f"❌ HTTP Error {response.status_code}")
                print(f"Response: {response.text[:200]}")
                continue
                
        except Exception as e:
            print(f"❌ Error with /{endpoint}/: {e}")
            continue
    
    print("❌ No working match endpoints found")
    return None

def analyze_matches_for_players(matches_data, team_id):
    """Extract player data from match lineups"""
    
    print(f"\n📊 ANALYZING MATCHES FOR PLAYER DATA")
    print("=" * 50)
    
    if not matches_data:
        print("❌ No matches data received")
        return None
    
    try:
        players_found = {}
        
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
                # Maybe it's a single match
                if "lineup" in matches_data or "lineups" in matches_data:
                    matches_list = [matches_data]
        elif isinstance(matches_data, list):
            matches_list = matches_data
        
        if matches_list:
            print(f"✅ Found {len(matches_list)} matches to analyze")
            
            for i, match in enumerate(matches_list):
                if isinstance(match, dict):
                    print(f"\n🏁 Match {i+1}:")
                    
                    # Show basic match info
                    home_team = match.get("home_team", {}).get("name", "Unknown")
                    away_team = match.get("away_team", {}).get("name", "Unknown")
                    match_date = match.get("date", "Unknown")
                    
                    print(f"   {home_team} vs {away_team} ({match_date})")
                    
                    # Look for lineup data
                    lineup_fields = ["lineup", "lineups", "players", "squad"]
                    
                    for field in lineup_fields:
                        if field in match:
                            lineup_data = match[field]
                            print(f"   📋 Found {field} data")
                            
                            # Extract players from lineup
                            match_players = extract_players_from_lineup(lineup_data, team_id)
                            
                            # Merge with our players collection
                            for player_id, player_info in match_players.items():
                                if player_id not in players_found:
                                    players_found[player_id] = player_info
                                    print(f"      + {player_info['name']} (ID: {player_id}) - {player_info.get('position', 'Unknown')}")
            
            if players_found:
                # Save players to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                players_file = f"fulham_players_extracted_{timestamp}.json"
                
                with open(players_file, 'w', encoding='utf-8') as f:
                    json.dump(players_found, f, indent=2, ensure_ascii=False)
                
                print(f"\n✅ Extracted {len(players_found)} unique players")
                print(f"📁 Players saved to: {players_file}")
                
                # Show player summary
                print(f"\n👥 FULHAM PLAYERS FOUND:")
                for player_id, player_info in list(players_found.items())[:10]:  # Show first 10
                    print(f"   {player_info['name']} (ID: {player_id}) - {player_info.get('position', 'Unknown')}")
                
                if len(players_found) > 10:
                    print(f"   ... and {len(players_found) - 10} more players")
                
                return players_found
            
            else:
                print("❌ No players found in match lineups")
                return None
        
        else:
            print("❌ No matches list found in response")
            return None
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return None

def extract_players_from_lineup(lineup_data, team_id):
    """Extract player info from lineup data"""
    
    players = {}
    
    try:
        if isinstance(lineup_data, dict):
            # Look for team-specific lineups
            for key, value in lineup_data.items():
                if isinstance(value, list):
                    # This might be a list of players
                    for player in value:
                        if isinstance(player, dict):
                            player_id = player.get("id") or player.get("player_id")
                            player_name = player.get("name") or player.get("player_name")
                            
                            if player_id and player_name:
                                players[player_id] = {
                                    "name": player_name,
                                    "position": player.get("position"),
                                    "number": player.get("number") or player.get("jersey_number"),
                                    "team_id": team_id
                                }
        
        elif isinstance(lineup_data, list):
            # Direct list of players
            for player in lineup_data:
                if isinstance(player, dict):
                    player_id = player.get("id") or player.get("player_id")
                    player_name = player.get("name") or player.get("player_name")
                    
                    if player_id and player_name:
                        players[player_id] = {
                            "name": player_name,
                            "position": player.get("position"),
                            "number": player.get("number") or player.get("jersey_number"),
                            "team_id": team_id
                        }
    
    except Exception as e:
        print(f"❌ Error extracting players: {e}")
    
    return players

def main():
    print("🚀 GET PLAYERS VIA MATCH LINEUPS")
    print("Strategy: Use match data to extract player names and IDs")
    print("API calls used so far: 4/75 (71 remaining)")
    
    team_id = 4145  # Fulham
    
    players = get_team_matches(team_id)
    
    print(f"\n📊 FINAL SUMMARY:")
    if players:
        print(f"✅ SUCCESS: Found {len(players)} Fulham players")
        print(f"📁 Check JSON files for complete player data")
        print(f"🎯 Next: Test getting individual player stats")
    else:
        print("❌ FAILED: Could not extract player data from matches")
        print("💡 May need to try different approach or contact API support")
    
    print(f"\n⚠️  API calls used: 5/75")
    print(f"📊 Calls remaining today: 70")

if __name__ == "__main__":
    main()