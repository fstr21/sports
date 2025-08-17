#!/usr/bin/env python3
"""
Test Getting Team Details for Team ID 4145

Let's see what data the /team/ endpoint provides for a specific team.
Maybe it includes player roster or other useful data.

Team ID 4145 from your EPL teams list.

YOUR API KEY: a9f37754a540df435e8c40ed89c08565166524ed
LIMIT: 72 calls remaining
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

def get_team_details(team_id):
    """Get team details to see what data is available"""
    
    print(f"⚽ GETTING TEAM DETAILS FOR TEAM ID {team_id}")
    print("=" * 50)
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print(f"📍 Endpoint: /team/")
    print(f"🏆 Team ID: {team_id}")
    print(f"⚠️  This will use 1 of your 72 remaining API calls")
    print("=" * 50)
    
    # Confirm before making call
    confirm = input(f"Get team details for team {team_id}? (y/n): ").lower().strip()
    if confirm != 'y':
        print("❌ API call cancelled")
        return None
    
    # Prepare request
    url = f"{BASE_URL}/team/"
    params = {
        'team_id': team_id,
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
        filename = f"team_details_{team_id}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Success! Data saved to: {filename}")
        
        # Analyze the team data
        analyze_team_data(data, team_id)
        
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

def analyze_team_data(team_data, team_id):
    """Analyze what data we got for the team"""
    
    print(f"\n📊 TEAM DATA ANALYSIS")
    print("=" * 40)
    
    if not team_data:
        print("❌ No team data received")
        return
    
    try:
        if isinstance(team_data, dict):
            print(f"✅ Team data received for ID {team_id}")
            print(f"📊 Available fields: {list(team_data.keys())}")
            
            # Show basic team info
            team_name = team_data.get("name", "Unknown")
            country = team_data.get("country", {})
            stadium = team_data.get("stadium", {})
            
            print(f"\n🏆 TEAM INFORMATION:")
            print(f"   Name: {team_name}")
            print(f"   ID: {team_data.get('id', team_id)}")
            
            if isinstance(country, dict):
                print(f"   Country: {country.get('name', 'Unknown')}")
            
            if isinstance(stadium, dict):
                print(f"   Stadium: {stadium.get('name', 'Unknown')}")
                print(f"   City: {stadium.get('city', 'Unknown')}")
            
            # Look for player-related data
            player_fields = ["players", "roster", "squad", "lineup", "members"]
            found_player_fields = [field for field in player_fields if field in team_data]
            
            print(f"\n🔍 PLAYER DATA CHECK:")
            if found_player_fields:
                print(f"   ✅ Found player-related fields: {found_player_fields}")
                
                for field in found_player_fields:
                    player_data = team_data[field]
                    if isinstance(player_data, list):
                        print(f"   📋 {field}: {len(player_data)} players")
                        if player_data:
                            sample_player = player_data[0]
                            print(f"      Sample player keys: {list(sample_player.keys()) if isinstance(sample_player, dict) else 'Not a dict'}")
                    else:
                        print(f"   📋 {field}: {type(player_data)} - {str(player_data)[:100]}")
            else:
                print(f"   ❌ No player data in team details")
                print(f"   💡 May need different endpoint for players")
            
            # Show all available data for manual inspection
            print(f"\n📄 FULL TEAM DATA:")
            for key, value in team_data.items():
                if isinstance(value, (dict, list)):
                    print(f"   {key}: {type(value)} - {len(value) if isinstance(value, (list, dict)) else 'N/A'} items")
                else:
                    print(f"   {key}: {value}")
        
        else:
            print(f"❓ Unexpected data type: {type(team_data)}")
            print(f"Content: {str(team_data)[:200]}")
    
    except Exception as e:
        print(f"❌ Analysis error: {e}")

def suggest_next_steps(team_data):
    """Suggest next steps based on what we found"""
    
    print(f"\n💡 NEXT STEPS FOR GETTING PLAYERS:")
    
    if not team_data:
        print("   1. Try different team IDs")
        print("   2. Check API documentation for player endpoints")
        return
    
    # Check if we found any player data
    player_fields = ["players", "roster", "squad", "lineup", "members"]
    found_player_fields = [field for field in player_fields if field in team_data]
    
    if found_player_fields:
        print("   ✅ Team details include player data!")
        print("   1. Analyze player data structure")
        print("   2. Check if player stats are included")
        print("   3. Test with more teams")
    else:
        print("   ❌ No player data in team details")
        print("   1. Look for other endpoints (matches, lineups)")
        print("   2. Try /match/ endpoint to get lineups")
        print("   3. Contact API support for player roster endpoint")
        print("   4. Check if recent matches include player names")

def main():
    print("🚀 TEST TEAM DETAILS FOR PLAYER DATA")
    print("Goal: See if team endpoint includes players/roster")
    print("API calls used so far: 3/75 (72 remaining)")
    
    team_id = 4145  # From your selection
    
    # Check which team this is from our extracted data
    try:
        import glob
        files = glob.glob("epl_teams_final_*.json")
        if files:
            latest_file = max(files, key=lambda x: x.split('_')[-1])
            with open(latest_file, 'r') as f:
                teams = json.load(f)
            
            team_info = next((team for team in teams if team['id'] == team_id), None)
            if team_info:
                print(f"🏆 Testing team: {team_info['name']} (Position: {team_info['position']})")
            else:
                print(f"🏆 Testing team ID: {team_id}")
    except:
        print(f"🏆 Testing team ID: {team_id}")
    
    team_data = get_team_details(team_id)
    suggest_next_steps(team_data)
    
    print(f"\n📊 FINAL SUMMARY:")
    if team_data:
        print(f"✅ SUCCESS: Got team details")
        print(f"📁 Check JSON file for complete team data")
    else:
        print("❌ FAILED: Could not get team details")
    
    print(f"\n⚠️  API calls used: 4/75")
    print(f"📊 Calls remaining today: 71")

if __name__ == "__main__":
    main()