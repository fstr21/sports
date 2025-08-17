#!/usr/bin/env python3
"""
SoccerDataAPI Testing Script

IMPORTANT: FREE PLAN = 75 CALLS/DAY ONLY!
This script is designed for minimal API usage during testing.

Usage:
    python test_soccerdataapi.py --endpoint countries
    python test_soccerdataapi.py --endpoint leagues  
    python test_soccerdataapi.py --endpoint matches --league_id 228
    python test_soccerdataapi.py --endpoint live_scores
    python test_soccerdataapi.py --endpoint standings --league_id 228

API Key: a9f37754a540df435e8c40ed89c08565166524ed
"""

import requests
import json
import argparse
from datetime import datetime
import sys

# API Configuration
BASE_URL = "https://api.soccerdataapi.com"
API_KEY = "a9f37754a540df435e8c40ed89c08565166524ed"

# Required headers
HEADERS = {
    'Accept-Encoding': 'gzip',
    'Content-Type': 'application/json'
}

def make_api_call(endpoint, params=None):
    """
    Make a single API call to SoccerDataAPI
    
    WARNING: Each call counts toward 75/day limit!
    """
    if params is None:
        params = {}
    
    # Always include auth token
    params['auth_token'] = API_KEY
    
    url = f"{BASE_URL}/{endpoint}/"
    
    print(f"🔄 Making API call to: {endpoint}")
    print(f"📊 Parameters: {params}")
    print(f"⚠️  WARNING: This uses 1 of your 75 daily API calls!")
    
    # Confirm before making call
    confirm = input("Continue? (y/n): ").lower().strip()
    if confirm != 'y':
        print("❌ API call cancelled")
        return None
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Save response to file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"soccerdataapi_{endpoint}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Success! Data saved to: {filename}")
        print(f"📝 Response size: {len(json.dumps(data))} characters")
        
        # Show preview of data structure
        print("\n📊 Data Preview:")
        if isinstance(data, dict):
            for key, value in list(data.items())[:5]:  # First 5 keys
                if isinstance(value, list):
                    print(f"  {key}: [{len(value)} items]")
                else:
                    print(f"  {key}: {str(value)[:100]}...")
        elif isinstance(data, list):
            print(f"  List with {len(data)} items")
            if data:
                print(f"  First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not a dict'}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API call failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return None

def test_countries():
    """Test countries endpoint"""
    print("\n🌍 Testing Countries Endpoint")
    print("This will show all available countries")
    return make_api_call("countries")

def test_leagues():
    """Test leagues endpoint"""
    print("\n🏆 Testing Leagues Endpoint") 
    print("This will show all 125+ available leagues")
    return make_api_call("leagues")

def test_matches(league_id=228):
    """Test matches endpoint for specific league"""
    print(f"\n⚽ Testing Matches Endpoint (League ID: {league_id})")
    print("This will show matches for the specified league")
    return make_api_call("matches", {"league_id": league_id})

def test_live_scores():
    """Test live scores endpoint"""
    print("\n🔴 Testing Live Scores Endpoint")
    print("This will show currently live matches")
    return make_api_call("live_scores")

def test_standings(league_id=228):
    """Test standings endpoint"""
    print(f"\n📊 Testing Standings Endpoint (League ID: {league_id})")
    print("This will show league table/standings")
    return make_api_call("standings", {"league_id": league_id})

def test_teams(league_id=228):
    """Test teams endpoint"""
    print(f"\n👥 Testing Teams Endpoint (League ID: {league_id})")
    print("This will show teams in the specified league")
    return make_api_call("teams", {"league_id": league_id})

def test_match_previews(match_id):
    """Test match previews endpoint"""
    print(f"\n🤖 Testing Match Previews Endpoint (Match ID: {match_id})")
    print("This will show AI-powered match preview")
    return make_api_call("match_previews", {"match_id": match_id})

def main():
    parser = argparse.ArgumentParser(description="Test SoccerDataAPI endpoints")
    parser.add_argument("--endpoint", required=True, 
                       choices=["countries", "leagues", "matches", "live_scores", "standings", "teams", "match_previews"],
                       help="Endpoint to test")
    parser.add_argument("--league_id", type=int, default=228, 
                       help="League ID for matches/standings/teams (default: 228)")
    parser.add_argument("--match_id", type=int, 
                       help="Match ID for match previews")
    
    args = parser.parse_args()
    
    print("🚨 SoccerDataAPI Testing Script")
    print("=" * 50)
    print(f"⚠️  FREE PLAN: 75 calls/day limit!")
    print(f"📅 Each test uses 1 API call")
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print("=" * 50)
    
    # Route to appropriate test function
    if args.endpoint == "countries":
        result = test_countries()
    elif args.endpoint == "leagues":
        result = test_leagues()
    elif args.endpoint == "matches":
        result = test_matches(args.league_id)
    elif args.endpoint == "live_scores":
        result = test_live_scores()
    elif args.endpoint == "standings":
        result = test_standings(args.league_id)
    elif args.endpoint == "teams":
        result = test_teams(args.league_id)
    elif args.endpoint == "match_previews":
        if not args.match_id:
            print("❌ match_id required for match_previews endpoint")
            sys.exit(1)
        result = test_match_previews(args.match_id)
    
    if result:
        print(f"\n✅ Test completed successfully!")
        print(f"📁 Check the generated JSON file for full response data")
    else:
        print(f"\n❌ Test failed!")

if __name__ == "__main__":
    main()