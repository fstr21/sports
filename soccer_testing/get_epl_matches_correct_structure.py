#!/usr/bin/env python3
"""
Get EPL Matches with Correct Structure Understanding

Now that we know the actual response structure:
[
  {
    "league_id": 228,
    "league_name": "Premier League", 
    "matches": [
      {
        "teams": {
          "home": {"id": 3104, "name": "Burnley"},
          "away": {"id": 4136, "name": "Manchester City"}
        }
      }
    ]
  }
]

Let's properly find Fulham matches and see if there's any player data.
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

def get_epl_matches_correct():
    """Get EPL matches with correct structure handling"""
    
    print(f"⚽ GETTING EPL MATCHES (CORRECT STRUCTURE)")
    print("=" * 60)
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print(f"📍 Endpoint: /matches/ with league_id=228")
    print(f"🏆 Looking for: Fulham (team_id: 4145)")
    print(f"⚠️  This will use 1 of your 69 remaining API calls")
    print("=" * 60)
    
    # Confirm before making call
    confirm = input(f"Get EPL matches with correct structure parsing? (y/n): ").lower().strip()
    if confirm != 'y':
        print("❌ API call cancelled")
        return None
    
    # Prepare request exactly like the docs
    url = f"{BASE_URL}/matches/"
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
        filename = f"epl_matches_correct_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Success! Data saved to: {filename}")
        
        # Analyze with correct structure understanding
        analyze_matches_correct_structure(data)
        
        return data
        
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

def analyze_matches_correct_structure(data):
    """Analyze matches data with correct structure understanding"""
    
    print(f"\n📊 ANALYZING EPL MATCHES (CORRECT STRUCTURE)")
    print("=" * 50)
    
    try:
        if isinstance(data, list):
            print(f"✅ Response is array with {len(data)} league entries")
            
            total_matches = 0
            fulham_matches = []
            all_teams = set()
            
            for league_entry in data:
                if isinstance(league_entry, dict):
                    league_name = league_entry.get("league_name", "Unknown")
                    league_id = league_entry.get("league_id", "Unknown")
                    matches = league_entry.get("matches", [])
                    
                    print(f"\n🏆 League: {league_name} (ID: {league_id})")
                    print(f"   📅 Matches: {len(matches)}")
                    
                    total_matches += len(matches)
                    
                    # Check each match for Fulham
                    for match in matches:
                        if isinstance(match, dict):
                            teams = match.get("teams", {})
                            home_team = teams.get("home", {})
                            away_team = teams.get("away", {})
                            
                            home_name = home_team.get("name", "")
                            away_name = away_team.get("name", "")
                            home_id = home_team.get("id")
                            away_id = away_team.get("id")
                            
                            # Add to teams list
                            all_teams.add(f"{home_name} (ID: {home_id})")
                            all_teams.add(f"{away_name} (ID: {away_id})")
                            
                            # Check if Fulham is involved
                            if "fulham" in home_name.lower() or "fulham" in away_name.lower() or home_id == 4145 or away_id == 4145:
                                print(f"   🎯 FOUND FULHAM MATCH!")
                                print(f"      {home_name} (ID: {home_id}) vs {away_name} (ID: {away_id})")
                                print(f"      Date: {match.get('date', 'Unknown')}")
                                print(f"      Status: {match.get('status', 'Unknown')}")
                                print(f"      Match ID: {match.get('id', 'Unknown')}")
                                
                                fulham_matches.append(match)
                                
                                # Check for player-related data in this match
                                check_match_for_player_data(match)
            
            print(f"\n📊 SUMMARY:")
            print(f"   Total matches found: {total_matches}")
            print(f"   Fulham matches: {len(fulham_matches)}")
            print(f"   Unique teams seen: {len(all_teams)}")
            
            # Show some team names for reference
            print(f"\n👥 Sample team names found:")
            for team in list(all_teams)[:10]:
                print(f"   - {team}")
            if len(all_teams) > 10:
                print(f"   ... and {len(all_teams) - 10} more teams")
            
            # If we found Fulham matches, analyze them further
            if fulham_matches:
                print(f"\n🎯 FULHAM MATCH ANALYSIS:")
                for i, match in enumerate(fulham_matches, 1):
                    print(f"\n   Match {i}:")
                    analyze_single_match_for_players(match)
                
                return fulham_matches
            else:
                print(f"\n❌ No Fulham matches found")
                print(f"💡 Possible reasons:")
                print(f"   - No recent Fulham matches in EPL")
                print(f"   - Fulham might be called something else")
                print(f"   - Team ID 4145 might be incorrect")
                return None
        
        else:
            print(f"❌ Unexpected response type: {type(data)}")
            print(f"Response: {str(data)[:300]}")
            return None
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return None

def check_match_for_player_data(match):
    """Check a single match for any player-related data"""
    
    player_fields = ["lineup", "lineups", "players", "squad", "events", "statistics", "scorers"]
    found_fields = []
    
    for field in player_fields:
        if field in match:
            found_fields.append(field)
    
    if found_fields:
        print(f"      ✅ Player-related fields found: {found_fields}")
    else:
        print(f"      ❌ No obvious player data fields")
        print(f"      🔍 Available fields: {list(match.keys())}")

def analyze_single_match_for_players(match):
    """Detailed analysis of a single Fulham match for player data"""
    
    match_id = match.get("id", "Unknown")
    date = match.get("date", "Unknown")
    status = match.get("status", "Unknown")
    
    print(f"      Match ID: {match_id}, Date: {date}, Status: {status}")
    
    # Check all fields for potential player data
    all_fields = list(match.keys())
    interesting_fields = ["lineup", "lineups", "players", "events", "statistics", "scorers", "odds", "match_preview"]
    
    for field in all_fields:
        if field in interesting_fields:
            field_data = match[field]
            print(f"         {field}: {type(field_data)}")
            
            if isinstance(field_data, dict):
                if field_data:  # Not empty
                    print(f"            Keys: {list(field_data.keys())}")
            elif isinstance(field_data, list):
                print(f"            Length: {len(field_data)}")
                if field_data:
                    if isinstance(field_data[0], dict):
                        print(f"            First item keys: {list(field_data[0].keys())}")

def main():
    print("🚀 GET EPL MATCHES - CORRECT STRUCTURE")
    print("Using the exact structure from API documentation")
    print("API calls used so far: 6/75 (69 remaining)")
    
    result = get_epl_matches_correct()
    
    print(f"\n📊 FINAL SUMMARY:")
    if result:
        if isinstance(result, list) and result:
            print(f"✅ SUCCESS: Found Fulham matches with potential player data")
            print(f"📁 Check JSON file for complete match data")
            print(f"🎯 Next: Investigate player data fields in matches")
        else:
            print(f"✅ SUCCESS: Got EPL data but no Fulham matches")
            print(f"💡 Fulham might not have recent matches")
    else:
        print("❌ FAILED: Could not get EPL matches")
    
    print(f"\n⚠️  API calls used: 7/75")
    print(f"📊 Calls remaining today: 68")

if __name__ == "__main__":
    main()