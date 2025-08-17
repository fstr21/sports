#!/usr/bin/env python3
"""
Get EPL Teams via Standings Endpoint

Since there's no direct "teams by league" endpoint, let's try the standings
endpoint which should give us all EPL teams with their IDs.

League ID 228 = EPL (from our previous analysis)

YOUR API KEY: a9f37754a540df435e8c40ed89c08565166524ed
LIMIT: 73 calls remaining
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

def get_epl_standings():
    """Get EPL standings to extract team IDs and names"""
    
    print("⚽ GETTING EPL TEAMS VIA STANDINGS")
    print("=" * 50)
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print(f"📍 Endpoint: /standing/")
    print(f"🏆 League ID: 228 (EPL)")
    print(f"⚠️  This will use 1 of your 73 remaining API calls")
    print("=" * 50)
    
    # Confirm before making call
    confirm = input("Get EPL standings to extract team data? (y/n): ").lower().strip()
    if confirm != 'y':
        print("❌ API call cancelled")
        return None
    
    # Prepare request
    url = f"{BASE_URL}/standing/"
    params = {
        'league_id': 228,  # EPL
        'auth_token': API_KEY
    }
    
    try:
        print("🌐 Making API request...")
        print(f"🔗 URL: {url}")
        print(f"📊 Params: {params}")
        
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        
        print(f"📈 HTTP Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"Response text: {response.text[:500]}")
            return None
        
        # Parse JSON response
        data = response.json()
        
        # Save to file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"epl_standings_teams_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Success! Data saved to: {filename}")
        
        # Analyze the standings data to extract teams
        teams = analyze_standings_for_teams(data)
        
        return teams
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print(f"Raw response: {response.text[:500]}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def analyze_standings_for_teams(standings_data):
    """Extract team IDs and names from standings data"""
    
    print("\n📊 ANALYZING STANDINGS FOR TEAM DATA")
    print("=" * 50)
    
    if not standings_data:
        print("❌ No standings data received")
        return None
    
    try:
        teams = []
        
        # Handle different possible response structures
        standings_list = None
        
        if isinstance(standings_data, dict):
            # Common patterns in API responses
            if "data" in standings_data:
                standings_list = standings_data["data"]
            elif "results" in standings_data:
                standings_list = standings_data["results"]
            elif "standings" in standings_data:
                standings_list = standings_data["standings"]
            else:
                print(f"📊 Response keys: {list(standings_data.keys())}")
                # Maybe the standings are directly in the response
                standings_list = standings_data
        elif isinstance(standings_data, list):
            standings_list = standings_data
        
        if standings_list:
            if isinstance(standings_list, list):
                print(f"✅ Found {len(standings_list)} teams in EPL standings")
                
                for position, team_data in enumerate(standings_list, 1):
                    if isinstance(team_data, dict):
                        # Extract team information
                        team_info = extract_team_from_standing(team_data)
                        if team_info:
                            team_info["position"] = position
                            teams.append(team_info)
                            
                            print(f"   {position:2d}. {team_info['name']} (ID: {team_info['id']})")
                
                # Save teams list
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                teams_file = f"epl_teams_extracted_{timestamp}.json"
                
                with open(teams_file, 'w', encoding='utf-8') as f:
                    json.dump(teams, f, indent=2, ensure_ascii=False)
                
                print(f"\n✅ Extracted {len(teams)} EPL teams")
                print(f"📁 Teams saved to: {teams_file}")
                
                # Show some key teams we care about
                key_teams = ["liverpool", "arsenal", "chelsea", "manchester united", "manchester city", "tottenham"]
                print(f"\n🎯 KEY EPL TEAMS FOUND:")
                
                for key_team in key_teams:
                    found_team = next((team for team in teams if key_team in team['name'].lower()), None)
                    if found_team:
                        print(f"   ✅ {found_team['name']}: ID {found_team['id']}")
                    else:
                        print(f"   ❌ {key_team.title()}: Not found")
                
                return teams
            
            elif isinstance(standings_list, dict):
                print(f"📊 Standings is a dict with keys: {list(standings_list.keys())}")
        
        print("❌ Could not extract teams from standings")
        return None
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return None

def extract_team_from_standing(standing_entry):
    """Extract team info from a single standings entry"""
    
    # Try different possible field names for team data
    team_data = None
    team_id = None
    team_name = None
    
    # Direct fields
    if "team_id" in standing_entry:
        team_id = standing_entry["team_id"]
    elif "id" in standing_entry:
        team_id = standing_entry["id"]
    
    if "team_name" in standing_entry:
        team_name = standing_entry["team_name"]
    elif "name" in standing_entry:
        team_name = standing_entry["name"]
    
    # Nested team object
    if "team" in standing_entry:
        team_obj = standing_entry["team"]
        if isinstance(team_obj, dict):
            team_id = team_obj.get("id") or team_obj.get("team_id")
            team_name = team_obj.get("name") or team_obj.get("team_name")
    
    if team_id and team_name:
        return {
            "id": team_id,
            "name": team_name,
            "points": standing_entry.get("points"),
            "played": standing_entry.get("played") or standing_entry.get("games_played"),
            "wins": standing_entry.get("wins"),
            "losses": standing_entry.get("losses"),
            "draws": standing_entry.get("draws")
        }
    
    return None

def main():
    print("🚀 GET EPL TEAMS VIA STANDINGS")
    print("Strategy: Use standings endpoint to extract all EPL team IDs")
    print("API calls used so far: 2/75 (73 remaining)")
    
    teams = get_epl_standings()
    
    print(f"\n📊 FINAL SUMMARY:")
    if teams:
        print(f"✅ SUCCESS: Extracted {len(teams)} EPL teams with IDs")
        print(f"📁 Check JSON files for complete team data")
        print(f"🎯 Next step: Pick a team and get players")
        
        # Show next steps
        if teams:
            print(f"\n💡 NEXT STEPS:")
            print(f"   1. Pick a team (e.g., Liverpool ID: {next((t['id'] for t in teams if 'liverpool' in t['name'].lower()), 'TBD')})")
            print(f"   2. Test getting that team's players")
            print(f"   3. Analyze player data quality")
    else:
        print("❌ FAILED: Could not extract team data")
        print("💡 May need to try different approach or check API docs")
    
    print(f"\n⚠️  API calls used: 3/75")
    print(f"📊 Calls remaining today: 72")

if __name__ == "__main__":
    main()