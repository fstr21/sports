#!/usr/bin/env python3
"""
Simple test script for value betting system
"""

import requests
import json

RAILWAY_URL = "https://web-production-b939f.up.railway.app"
API_KEY = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def test_simple():
    print("Testing Value Betting System")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Health Check...")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", headers=headers, timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            services = health_data.get("services", {})
            print(f"   Status: {health_data.get('status')}")
            print(f"   Services: {services}")
            
            # Check if new endpoints are available
            player_matcher = services.get("player_matcher", False)
            if not player_matcher:
                print("   WARNING: player_matcher not available - Railway deployment needs update")
        else:
            print(f"   FAILED: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 2: Try value betting endpoint
    print("\n2. Value Betting Endpoint...")
    try:
        response = requests.post(f"{RAILWAY_URL}/value-betting/analyze", headers=headers, json={
            "sport_key": "baseball_mlb",
            "player_markets": "batter_hits",
            "min_confidence": 0.8
        }, timeout=20)
        
        print(f"   Response Status: {response.status_code}")
        if response.status_code == 404:
            print("   RESULT: Endpoint not found - need to redeploy to Railway")
        elif response.status_code == 200:
            data = response.json()
            print(f"   RESULT: Success - {data.get('status', 'unknown')}")
        else:
            print(f"   RESULT: Error - {response.text[:100]}")
            
    except Exception as e:
        print(f"   ERROR: {e}")

    print(f"\nConclusion: The new value betting endpoints need to be deployed to Railway")
    print(f"Current Railway deployment doesn't have the PlayerMatcher system yet")

if __name__ == "__main__":
    test_simple()