#!/usr/bin/env python3
"""
Working test script that bypasses MCP and directly calls ESPN API
"""

import requests
import json
from datetime import datetime
import pytz

def test_direct_espn():
    """Test ESPN API directly"""
    print("Testing ESPN API directly...")
    
    # Test MLB scoreboard directly
    url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
    
    try:
        response = requests.get(url, timeout=30)
        print(f"ESPN Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            events = data.get("events", [])
            print(f"SUCCESS: Found {len(events)} MLB games")
            
            if events:
                print("\nTodas's MLB Games:")
                for i, event in enumerate(events[:3], 1):  # Show first 3
                    competitions = event.get("competitions", [{}])
                    if competitions:
                        competitors = competitions[0].get("competitors", [])
                        if len(competitors) >= 2:
                            away = competitors[1].get("team", {}).get("displayName", "Away")
                            home = competitors[0].get("team", {}).get("displayName", "Home")
                            date_str = event.get("date", "")
                            event_id = competitions[0].get("id", "No ID")
                            
                            print(f"  {i}. {away} @ {home}")
                            print(f"     Time: {date_str}")
                            print(f"     Event ID: {event_id}")
            
            return True
        else:
            print(f"FAILED: ESPN API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False

def test_odds_api():
    """Test if we can call odds API directly"""
    print("\n" + "="*50)
    print("Testing Odds API via our server...")
    
    # Try the odds endpoint that might exist
    RAILWAY_URL = "https://web-production-b939f.up.railway.app"
    API_KEY = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Try different odds endpoints
    odds_endpoints = [
        "/odds/get-odds",
        "/api/odds",
        "/odds",
        "/get-odds"
    ]
    
    for endpoint in odds_endpoints:
        print(f"\nTrying: {endpoint}")
        try:
            data = {
                "sport": "baseball_mlb",
                "regions": "us", 
                "markets": "h2h",
                "odds_format": "american"
            }
            
            response = requests.post(f"{RAILWAY_URL}{endpoint}", headers=headers, json=data, timeout=30)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  SUCCESS: {json.dumps(result, indent=2)[:200]}...")
                return True
            elif response.status_code != 404:
                print(f"  Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"  Exception: {e}")
    
    print("FAILED: No working odds endpoint found")
    return False

if __name__ == "__main__":
    print("="*60)
    print("  WORKING TEST")
    print("="*60)
    
    # Test direct ESPN API access
    espn_success = test_direct_espn()
    
    # Test odds API
    odds_success = test_odds_api()
    
    print("\n" + "="*60) 
    print("  RESULTS")
    print("="*60)
    print(f"ESPN Direct: {'PASS' if espn_success else 'FAIL'}")
    print(f"Odds API: {'PASS' if odds_success else 'FAIL'}")
    
    if espn_success and not odds_success:
        print("\n=> ESPN works directly - we can bypass MCP for ESPN calls")
        print("=> Focus on getting odds API working or find alternative")
    elif espn_success and odds_success:
        print("\n=> Both APIs working - ready to build!")
    else:
        print("\n=> Need to fix API connectivity issues")