#!/usr/bin/env python3
"""
Test script for value betting system
"""

import requests
import json

RAILWAY_URL = "https://web-production-b939f.up.railway.app"
API_KEY = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def test_value_betting():
    print("Testing Value Betting System")
    print("=" * 50)
    
    # Test 1: Check if PlayerMatcher endpoints exist
    print("\n1. Testing PlayerMatcher endpoints...")
    
    # Test health endpoint to see if player_matcher is available
    print("   Checking health endpoint...")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", headers=headers, timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            player_matcher_available = health_data.get("services", {}).get("player_matcher", False)
            print(f"   Health check: player_matcher = {player_matcher_available}")
            
            if not player_matcher_available:
                print("   PlayerMatcher not available - need to redeploy to Railway")
                return False
        else:
            print(f"   Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   Health check error: {e}")
        return False
    
    # Test 2: Test pending matches endpoint
    print("\n2. Testing pending matches endpoint...")
    try:
        response = requests.get(f"{RAILWAY_URL}/player/pending", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   Pending matches endpoint works")
            print(f"   Current stats: {data.get('stats', {})}")
        else:
            print(f"   ❌ Pending matches failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Pending matches error: {e}")
        return False
    
    # Test 3: Test player matching
    print("\n3. Testing player matching...")
    try:
        response = requests.post(f"{RAILWAY_URL}/player/match", headers=headers, json={
            "odds_player_name": "Kyle Schwarber",
            "sport_key": "baseball_mlb"
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            match_found = data.get("match_found", False)
            print(f"   ✅ Player matching works: match_found = {match_found}")
            if match_found:
                match = data.get("match", {})
                print(f"   🏆 Match: {match.get('espn_name')} (ID: {match.get('espn_id')})")
        else:
            print(f"   ❌ Player matching failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Player matching error: {e}")
        return False
    
    # Test 4: Test value betting analysis 
    print("\n4. Testing value betting analysis...")
    try:
        response = requests.post(f"{RAILWAY_URL}/value-betting/analyze", headers=headers, json={
            "sport_key": "baseball_mlb",
            "player_markets": "batter_hits,batter_home_runs",
            "min_confidence": 0.8,
            "value_threshold": 1.1
        }, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            print(f"   ✅ Value betting analysis works: status = {status}")
            
            if status == "success":
                value_bets = data.get("value_bets", [])
                unmatched = data.get("unmatched_players", [])
                print(f"   🎯 Found {len(value_bets)} value bets")
                print(f"   🤔 Found {len(unmatched)} unmatched players")
            else:
                print(f"   ⚠️  Analysis status: {status}")
                print(f"   Message: {data.get('message', 'No message')}")
                
        else:
            print(f"   ❌ Value betting failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Value betting error: {e}")
        return False
    
    print(f"\n✅ All tests passed! Value betting system is working.")
    return True

if __name__ == "__main__":
    test_value_betting()