#!/usr/bin/env python3
"""
Direct SoccerDataAPI Test - Conservative Liverpool Player Test

Since the MCP server package isn't available, let's test directly.
This will use 1-3 API calls maximum to test player data quality.

YOUR API KEY: a9f37754a540df435e8c40ed89c08565166524ed
LIMIT: 75 calls/day - we'll be very careful!
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

# Call counter
call_count = 0

def make_api_call(endpoint, params=None):
    """Make careful API call with tracking"""
    global call_count
    
    if params is None:
        params = {}
    
    params['auth_token'] = API_KEY
    url = f"{BASE_URL}/{endpoint}/"
    
    call_count += 1
    print(f"\n🔄 API Call #{call_count}/75")
    print(f"📍 Endpoint: {endpoint}")
    print(f"📊 Params: {params}")
    
    confirm = input("Execute this API call? (y/n): ").lower().strip()
    if confirm != 'y':
        call_count -= 1  # Don't count cancelled calls
        print("❌ Cancelled")
        return None
    
    try:
        print("🌐 Making request...")
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        
        print(f"📈 Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None
        
        data = response.json()
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"soccerdata_{endpoint}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Success! Saved to: {filename}")
        return data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_strategy_1_known_liverpool_ids():
    """Try common Liverpool team IDs directly"""
    print("\n🎯 STRATEGY 1: Try Known Liverpool Team IDs")
    print("Testing common IDs used for Liverpool in soccer APIs")
    
    # Common Liverpool team IDs in various APIs
    liverpool_ids = [42, 40, 61, 50, 45, 17]
    
    for team_id in liverpool_ids:
        print(f"\n🔍 Testing team_id: {team_id}")
        
        # Try teams endpoint first to see if this ID exists
        result = make_api_call("teams", {"team_id": team_id})
        
        if result:
            # Check if this is actually Liverpool
            if is_liverpool(result):
                print(f"🎉 FOUND LIVERPOOL! team_id: {team_id}")
                
                # Now try to get players for this team
                players = make_api_call("players", {"team_id": team_id})
                return players
            else:
                print(f"❌ team_id {team_id} exists but not Liverpool")
                print(f"   Team name: {get_team_name(result)}")
        else:
            print(f"❌ team_id {team_id} not found or error")
    
    print("❌ No Liverpool found with known IDs")
    return None

def test_strategy_2_find_via_league():
    """Find Liverpool via EPL league"""
    print("\n🎯 STRATEGY 2: Find Liverpool via EPL")
    
    # Common EPL league IDs
    epl_ids = [39, 42, 228, 17, 61]
    
    for league_id in epl_ids:
        print(f"\n🔍 Testing EPL league_id: {league_id}")
        
        result = make_api_call("teams", {"league_id": league_id})
        
        if result and isinstance(result, list):
            # Look for Liverpool in teams list
            for team in result:
                if is_liverpool_in_team_data(team):
                    liverpool_id = team.get("id") or team.get("team_id")
                    print(f"🎉 FOUND LIVERPOOL! team_id: {liverpool_id}")
                    
                    # Get Liverpool players
                    players = make_api_call("players", {"team_id": liverpool_id})
                    return players
            
            print(f"❌ Liverpool not found in league_id {league_id}")
            print(f"   Found {len(result)} teams in this league")
        else:
            print(f"❌ league_id {league_id} not found or error")
    
    return None

def is_liverpool(team_data):
    """Check if team data represents Liverpool"""
    if not team_data:
        return False
    
    if isinstance(team_data, dict):
        name = str(team_data.get("name", "")).lower()
        return "liverpool" in name
    
    return False

def is_liverpool_in_team_data(team):
    """Check if team in teams list is Liverpool"""
    if not isinstance(team, dict):
        return False
    
    name = str(team.get("name", "")).lower()
    return "liverpool" in name

def get_team_name(team_data):
    """Extract team name from API response"""
    if isinstance(team_data, dict):
        return team_data.get("name", "Unknown")
    return "Unknown"

def analyze_player_data(players_data):
    """Analyze the player data we received"""
    print("\n📊 PLAYER DATA ANALYSIS")
    print("=" * 50)
    
    if not players_data:
        print("❌ No player data received")
        return
    
    try:
        if isinstance(players_data, list):
            print(f"✅ Received {len(players_data)} players")
            
            if players_data:
                sample_player = players_data[0]
                print(f"\n👤 Sample Player Structure:")
                print(f"   Available fields: {list(sample_player.keys())}")
                
                # Check for stats
                stats_fields = ["goals", "assists", "appearances", "minutes", "stats", "goals_scored", "yellow_cards", "red_cards"]
                found_stats = [field for field in stats_fields if field in sample_player]
                
                print(f"   Stats fields found: {found_stats}")
                print(f"   Has player stats: {'YES' if found_stats else 'NO'}")
                
                # Show first player as example
                print(f"\n📋 First Player Example:")
                for key, value in sample_player.items():
                    print(f"      {key}: {value}")
                
                # Quality assessment
                print(f"\n🎯 QUALITY ASSESSMENT:")
                if found_stats:
                    print("   ✅ GOOD: Has player statistics")
                    print("   ✅ Suitable for betting analysis")
                else:
                    print("   ❌ LIMITED: No detailed statistics")
                    print("   ❌ May need additional endpoints")
        
        elif isinstance(players_data, dict):
            print(f"📊 Received dict with keys: {list(players_data.keys())}")
            
        else:
            print(f"❓ Unexpected data type: {type(players_data)}")
    
    except Exception as e:
        print(f"❌ Analysis error: {e}")

def main():
    print("🧪 DIRECT SOCCERDATAAPI TEST - LIVERPOOL PLAYERS")
    print("=" * 60)
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print(f"⚠️  Daily Limit: 75 calls")
    print(f"🎯 Goal: Get Liverpool players + stats with minimal calls")
    print("=" * 60)
    
    print("\nChoose strategy:")
    print("1. Try known Liverpool team IDs (faster)")
    print("2. Find Liverpool via EPL league (more reliable)")
    
    choice = input("\nStrategy (1/2): ").strip()
    
    players_data = None
    
    if choice == "1":
        players_data = test_strategy_1_known_liverpool_ids()
    elif choice == "2":
        players_data = test_strategy_2_find_via_league()
    else:
        print("❌ Invalid choice")
        return
    
    # Analyze results
    analyze_player_data(players_data)
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 30)
    print(f"API calls used: {call_count}/75")
    print(f"Calls remaining: {75 - call_count}")
    
    if players_data:
        print("Result: ✅ SUCCESS")
        print("Check JSON files for full data")
    else:
        print("Result: ❌ FAILED")
        print("May need different approach")
    
    print("\n💡 Next steps:")
    if players_data:
        print("- Analyze data quality for betting")
        print("- Estimate calls needed for EPL + La Liga + MLS")
        print("- Compare with Football-Data.org")
    else:
        print("- Try different team/league IDs")
        print("- Check API documentation for correct endpoints")
        print("- Consider sticking with Football-Data.org")

if __name__ == "__main__":
    main()