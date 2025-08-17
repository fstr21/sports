#!/usr/bin/env python3
"""
Fixed Direct API Call - Get Leagues

Corrected endpoint: /league/ (singular)
Optional country_id parameter to filter by country

YOUR API KEY: a9f37754a540df435e8c40ed89c08565166524ed
LIMIT: 75 calls/day - we used 1, have 74 remaining
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

def get_leagues(country_id=None):
    """Get leagues from SoccerDataAPI - corrected endpoint"""
    
    print("🏆 GETTING LEAGUES FROM SOCCERDATAAPI (FIXED)")
    print("=" * 50)
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print(f"📍 Endpoint: /league/ (corrected from /leagues/)")
    if country_id:
        print(f"🌍 Country ID: {country_id}")
    else:
        print(f"🌍 Country ID: All countries")
    print(f"⚠️  This will use 1 of your 74 remaining daily API calls")
    print("=" * 50)
    
    # Confirm before making call
    confirm = input("Make corrected API call? (y/n): ").lower().strip()
    if confirm != 'y':
        print("❌ API call cancelled")
        return None
    
    # Prepare request with corrected endpoint
    url = f"{BASE_URL}/league/"  # Singular, as per docs
    params = {
        'auth_token': API_KEY
    }
    
    # Add country_id if specified
    if country_id:
        params['country_id'] = country_id
    
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
        country_suffix = f"_country{country_id}" if country_id else "_all"
        filename = f"soccerdata_leagues{country_suffix}_{timestamp}.json"
        
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
        # Handle different response structures
        leagues_list = None
        
        if isinstance(leagues_data, dict):
            if "data" in leagues_data:
                leagues_list = leagues_data["data"]
                print(f"📦 Found leagues in 'data' field")
            elif "leagues" in leagues_data:
                leagues_list = leagues_data["leagues"]
                print(f"📦 Found leagues in 'leagues' field")
            else:
                print(f"📊 Response keys: {list(leagues_data.keys())}")
                # Try the whole dict as leagues
                leagues_list = leagues_data
        elif isinstance(leagues_data, list):
            leagues_list = leagues_data
            print(f"📦 Direct list of leagues")
        
        if leagues_list and isinstance(leagues_list, list):
            print(f"✅ Found {len(leagues_list)} leagues")
            
            # Look for key leagues we care about
            target_leagues = {
                "premier league": ["premier league", "english premier", "epl"],
                "la liga": ["la liga", "primera division", "laliga"],
                "mls": ["mls", "major league soccer"],
                "serie a": ["serie a", "italian serie"],
                "bundesliga": ["bundesliga", "german bundesliga"],
                "ligue 1": ["ligue 1", "french ligue"]
            }
            
            found_leagues = {}
            
            print(f"\n🔍 Searching for key leagues:")
            
            for league in leagues_list:
                if isinstance(league, dict):
                    league_name = str(league.get("name", "")).lower()
                    league_id = league.get("id") or league.get("league_id")
                    country = league.get("country", {})
                    country_name = ""
                    
                    if isinstance(country, dict):
                        country_name = country.get("name", "")
                    elif isinstance(country, str):
                        country_name = country
                    
                    # Check against all our target leagues
                    for target_key, search_terms in target_leagues.items():
                        for term in search_terms:
                            if term in league_name:
                                found_leagues[target_key] = {
                                    "id": league_id,
                                    "name": league.get("name"),
                                    "country": country_name,
                                    "is_cup": league.get("is_cup", False)
                                }
                                print(f"   ✅ {target_key.upper()}: ID {league_id} - {league.get('name')} ({country_name})")
                                break
            
            # Show missing leagues
            missing = [league for league in target_leagues.keys() if league not in found_leagues]
            if missing:
                print(f"\n❌ Not found: {', '.join(missing)}")
            
            # Show all leagues by country for reference
            print(f"\n🌍 Leagues by Country (first 20):")
            countries = {}
            for i, league in enumerate(leagues_list[:20]):
                if isinstance(league, dict):
                    country = league.get("country", {})
                    country_name = country.get("name", "Unknown") if isinstance(country, dict) else str(country)
                    
                    if country_name not in countries:
                        countries[country_name] = []
                    countries[country_name].append(f"{league.get('name')} (ID: {league.get('id')})")
            
            for country, leagues in countries.items():
                print(f"   {country.upper()}: {len(leagues)} leagues")
                for league in leagues[:3]:  # Show first 3 leagues per country
                    print(f"      - {league}")
                if len(leagues) > 3:
                    print(f"      ... and {len(leagues) - 3} more")
            
            # Summary for our needs
            print(f"\n🎯 SUMMARY FOR OUR NEEDS:")
            print(f"   Total leagues: {len(leagues_list)}")
            print(f"   Key leagues found: {len(found_leagues)}")
            print(f"   EPL available: {'✅' if 'premier league' in found_leagues else '❌'}")
            print(f"   La Liga available: {'✅' if 'la liga' in found_leagues else '❌'}")
            print(f"   MLS available: {'✅' if 'mls' in found_leagues else '❌'}")
            
            if found_leagues:
                print(f"\n📝 League IDs for future use:")
                for league_name, info in found_leagues.items():
                    print(f"   {league_name.upper()}: {info['id']} - {info['name']}")
        
        else:
            print(f"❓ Unexpected leagues data structure")
            print(f"Type: {type(leagues_list)}")
            if leagues_list:
                print(f"Content: {str(leagues_list)[:200]}...")
    
    except Exception as e:
        print(f"❌ Analysis error: {e}")

def main():
    print("🚀 SOCCERDATAAPI - GET LEAGUES (FIXED)")
    print("Goal: Get all leagues with corrected endpoint")
    print("API calls used so far: 1/75 (74 remaining)")
    
    # Ask if user wants to filter by country
    print("\nOptions:")
    print("1. Get all leagues (no country filter)")
    print("2. Get leagues for specific country")
    
    choice = input("Choice (1/2): ").strip()
    
    country_id = None
    if choice == "2":
        print("\nCommon country IDs:")
        print("  1 = USA (for MLS)")
        print("  3 = England (for EPL)")
        print("  6 = Spain (for La Liga)")
        print("  7 = Italy (for Serie A)")
        print("  8 = Germany (for Bundesliga)")
        print("  9 = France (for Ligue 1)")
        
        try:
            country_id = int(input("Enter country_id: "))
        except ValueError:
            print("❌ Invalid country_id, getting all leagues")
    
    result = get_leagues(country_id)
    
    print(f"\n📊 FINAL SUMMARY:")
    if result:
        print("✅ SUCCESS: Got leagues data with corrected endpoint")
        print("📁 Check the JSON file for complete league list")
        print("💡 Use the league IDs shown above for team/player queries")
    else:
        print("❌ FAILED: Still having issues")
        print("💡 May need to check API documentation further")
    
    print(f"\n⚠️  API calls used: 2/75 (including previous failed call)")
    print(f"📊 Calls remaining today: 73")

if __name__ == "__main__":
    main()