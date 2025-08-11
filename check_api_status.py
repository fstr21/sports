#!/usr/bin/env python3
"""
Check API key status and quota
"""

import requests
import json

RAILWAY_URL = "https://web-production-b939f.up.railway.app"
API_KEY = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def check_api_status():
    """Check the status of our APIs"""
    
    print("=== CHECKING API STATUS ===")
    
    # 1. Check Railway server health
    print("\n1. Railway Server Health Check:")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        if response.status_code == 200:
            print("   ✓ Railway server is UP")
        else:
            print(f"   ✗ Railway server error: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Railway server DOWN: {e}")
    
    # 2. Check Odds API quota
    print("\n2. Odds API Quota Check:")
    try:
        response = requests.get(f"{RAILWAY_URL}/odds/quota", headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Quota endpoint accessible")
            print(f"   Data: {json.dumps(result, indent=2)}")
        else:
            print(f"   ✗ Quota check failed: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print(f"   ✗ Quota check error: {e}")
    
    # 3. Test a simple ESPN call (should work)
    print("\n3. ESPN API Test:")
    try:
        response = requests.post(f"{RAILWAY_URL}/espn/scoreboard", 
                               headers=headers,
                               json={"sport": "baseball", "league": "mlb"},
                               timeout=15)
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                games = result.get("data", {}).get("scoreboard", [])
                print(f"   ✓ ESPN working - found {len(games)} games")
            else:
                print(f"   ✗ ESPN returned error: {result}")
        else:
            print(f"   ✗ ESPN failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ ESPN error: {e}")
    
    # 4. Test direct Odds API call
    print("\n4. Direct Odds API Test:")
    try:
        response = requests.post(f"{RAILWAY_URL}/odds/get-odds",
                               headers=headers,
                               json={
                                   "sport": "baseball_mlb",
                                   "regions": "us", 
                                   "markets": "h2h",
                                   "odds_format": "american"
                               },
                               timeout=15)
        if response.status_code == 200:
            print("   ✓ Odds API call successful")
        else:
            print(f"   ✗ Odds API failed: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print(f"   ✗ Odds API error: {e}")
    
    print("\n=== STATUS CHECK COMPLETE ===")

if __name__ == "__main__":
    check_api_status()