#!/usr/bin/env python3
"""
Direct API Call - Get Leagues Only

Simple test to get all available leagues from SoccerDataAPI.
Uses exactly 1 API call to see what leagues are available.

YOUR API KEY: a9f37754a540df435e8c40ed89c08565166524ed
LIMIT: 75 calls/day
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

def get_leagues():
    """Get all available leagues from SoccerDataAPI"""
    
    print("🏆 GETTING ALL LEAGUES FROM SOCCERDATAAPI")
    print("=" * 50)
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print(f"📍 Endpoint: /leagues/")
    print(f"⚠️  This will use 1 of your 75 daily API calls")
    print("=" * 50)
    
    # Confirm before making call
    confirm = input("Make API call to get leagues? (y/n): ").lower().strip()
    if confirm != 'y':
        print("❌ API call cancelled")
        return None
    
    # Prepare request
    url = f"{BASE_URL}/leagues/"
    params = {
        'auth_token': API_KEY
    }
    
    try:
        print("🌐 Making API request...")
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
        filename = f"soccerdata_leagues_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Success! Data saved to: {filename}")
        
        # Analyze the leagues data
        analyze_leagues(data)
        
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

def analyze_leagues(leagues_data):
    """Analyze the leagues data received"""
    
    print("\n📊 LEAGUES DATA ANALYSIS")
    print("=" * 40)
    
    if not leagues_data:
        print("❌ No leagues data received")
        return
    
    try:
        if isinstance(leagues_data, list):
            print(f"✅ Found {len(leagues_data)} leagues")
            
            # Look for key leagues we care about
            target_leagues = ["premier league", "la liga", "mls", "serie a", "bundesliga", "ligue 1"]
            found_leagues = {}
            
            print(f"\n🔍 Searching for key leagues:")
            
            for league in leagues_data:
                if isinstance(league, dict):
                    league_name = str(league.get("name", "")).lower()
                    league_id = league.get("id") or league.get("league_id")
                    
                    for target in target_leagues:
                        if target in league_name:
                            found_leagues[target] = {
                                "id": league_id,
                                "name": league.get("name"),
                                "country": league.get("country", "Unknown")
                            }
                            print(f"   ✅ {target.upper()}: ID {league_id} - {league.get('name')}")
            
            # Show missing leagues
            missing = [league for league in target_leagues if league not in found_leagues]
            if missing:
                print(f"\n❌ Not found: {', '.join(missing)}")
            
            # Show sample league structure
            if leagues_data:
                print(f"\n📋 Sample League Structure:")
                sample_league = leagues_data[0]
                for key, value in sample_league.items():
                    print(f"   {key}: {value}")
            
            # Summary for our needs
            print(f"\n🎯 SUMMARY FOR OUR NEEDS:")
            print(f"   Total leagues: {len(leagues_data)}")
            print(f"   Key leagues found: {len(found_leagues)}")
            print(f"   EPL available: {'✅' if 'premier league' in found_leagues else '❌'}")
            print(f"   La Liga available: {'✅' if 'la liga' in found_leagues else '❌'}")
            print(f"   MLS available: {'✅' if 'mls' in found_leagues else '❌'}")
            
            if found_leagues:
                print(f"\n📝 League IDs for future use:")
                for league_name, info in found_leagues.items():
                    print(f"   {league_name.upper()}: {info['id']}")
        
        elif isinstance(leagues_data, dict):
            print(f"📊 Received dict with keys: {list(leagues_data.keys())}")
            
            # Check if leagues are nested in the response
            if "leagues" in leagues_data:
                print("🔍 Found nested leagues data")
                analyze_leagues(leagues_data["leagues"])
            elif "data" in leagues_data:
                print("🔍 Found nested data")
                analyze_leagues(leagues_data["data"])
        
        else:
            print(f"❓ Unexpected data type: {type(leagues_data)}")
    
    except Exception as e:
        print(f"❌ Analysis error: {e}")

def main():
    print("🚀 SOCCERDATAAPI - GET LEAGUES TEST")
    print("Goal: See all available leagues and find EPL, La Liga, MLS")
    
    result = get_leagues()
    
    print(f"\n📊 FINAL SUMMARY:")
    if result:
        print("✅ SUCCESS: Got leagues data")
        print("📁 Check the JSON file for complete league list")
        print("💡 Use the league IDs shown above for team/player queries")
    else:
        print("❌ FAILED: Could not get leagues data")
        print("💡 Check API key or endpoint availability")
    
    print(f"\n⚠️  API calls used: 1/75")
    print(f"📊 Calls remaining today: 74")

if __name__ == "__main__":
    main()