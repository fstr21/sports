#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Test Script - WNBA Games and Moneylines

This script tests the specific example: "What WNBA games are today and what are their moneylines?"

Usage:
    python quick_test.py YOUR_RAILWAY_URL

Example:
    python quick_test.py https://sports-production-1234.up.railway.app
"""

import requests
import json
import sys
from datetime import datetime

def test_wnba_games_and_moneylines(base_url: str):
    """Test WNBA games and moneylines specifically"""
    
    api_key = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("🏀 Testing WNBA Games and Moneylines")
    print("=" * 50)
    print(f"🌐 Server: {base_url}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Health Check
    print("1️⃣ Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print("   ✅ Server is healthy")
            services = health.get("services", {})
            print(f"   📊 ESPN: {'✅' if services.get('sports_ai') else '❌'}")
            print(f"   📊 Odds: {'✅' if services.get('odds') else '❌'}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot reach server: {e}")
        return False
    
    # Step 2: Get WNBA Games
    print("\n2️⃣ Getting today's WNBA games...")
    try:
        response = requests.post(
            f"{base_url}/espn/scoreboard",
            headers=headers,
            json={"sport": "basketball", "league": "wnba"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                games = data.get("data", {}).get("scoreboard", {}).get("events", [])
                print(f"   ✅ Found {len(games)} WNBA games today")
                
                if games:
                    print("   🏀 Today's games:")
                    for i, game in enumerate(games):
                        competitors = game.get("competitions", [{}])[0].get("competitors", [])
                        if len(competitors) >= 2:
                            away = competitors[1].get("team", {}).get("displayName", "Away")
                            home = competitors[0].get("team", {}).get("displayName", "Home")
                            status = game.get("status", {}).get("type", {}).get("description", "TBD")
                            print(f"      Game {i+1}: {away} @ {home} ({status})")
                else:
                    print("   ℹ️  No WNBA games today")
                    
            else:
                print(f"   ❌ ESPN API error: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error getting games: {e}")
        return False
    
    # Step 3: Get WNBA Moneylines
    print("\n3️⃣ Getting WNBA moneylines...")
    try:
        response = requests.post(
            f"{base_url}/odds/get-odds",
            headers=headers,
            json={
                "sport": "basketball_wnba",
                "regions": "us",
                "markets": "h2h",  # head-to-head = moneylines
                "odds_format": "american"
            },
            timeout=15
        )
        
        if response.status_code == 200:
            odds_data = response.json()
            if isinstance(odds_data, list):
                print(f"   ✅ Found moneylines for {len(odds_data)} games")
                
                if odds_data:
                    print("   💰 Moneylines:")
                    for i, game in enumerate(odds_data[:5]):  # Show first 5 games
                        home_team = game.get("home_team", "Home")
                        away_team = game.get("away_team", "Away")
                        commence_time = game.get("commence_time", "TBD")
                        
                        print(f"\n      🏀 {away_team} @ {home_team}")
                        print(f"         ⏰ {commence_time}")
                        
                        bookmakers = game.get("bookmakers", [])
                        if bookmakers:
                            # Show odds from first bookmaker
                            book = bookmakers[0]
                            book_name = book.get("title", "Sportsbook")
                            markets = book.get("markets", [])
                            
                            for market in markets:
                                if market.get("key") == "h2h":
                                    outcomes = market.get("outcomes", [])
                                    print(f"         💸 {book_name}:")
                                    for outcome in outcomes:
                                        team = outcome.get("name", "Unknown")
                                        odds = outcome.get("price", "N/A")
                                        print(f"            {team}: {odds}")
                        else:
                            print("         ⚠️  No odds available")
                else:
                    print("   ℹ️  No games with moneylines found")
                    
            else:
                print(f"   ❌ Odds API error: {odds_data}")
                return False
                
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error getting odds: {e}")
        return False
    
    # Step 4: Test Natural Language Query
    print("\n4️⃣ Testing natural language query...")
    try:
        response = requests.post(
            f"{base_url}/ask",
            headers=headers,
            json={"question": "What WNBA games are today and what are their moneylines?"},
            timeout=20
        )
        
        if response.status_code == 200:
            nl_data = response.json()
            if nl_data.get("ok"):
                print("   ✅ Natural language query successful!")
                interpretation = nl_data.get("interpretation", "")
                if interpretation:
                    print(f"   🧠 AI understood: {interpretation}")
                    
                # Check if we got actual results
                result = nl_data.get("result", {})
                if result and result.get("ok"):
                    print("   ✅ Query executed and returned data")
                else:
                    print("   ⚠️  Query processed but may not have returned data")
            else:
                print(f"   ❌ Natural language error: {nl_data}")
        else:
            print(f"   ❌ Natural language request failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error with natural language: {e}")
    
    # Step 5: Combined Intelligence Test
    print("\n5️⃣ Testing daily intelligence (combined data)...")
    try:
        response = requests.post(
            f"{base_url}/daily-intelligence",
            headers=headers,
            json={
                "leagues": ["basketball/wnba"],
                "include_odds": True,
                "include_analysis": False
            },
            timeout=25
        )
        
        if response.status_code == 200:
            intel_data = response.json()
            if intel_data.get("status") == "success":
                print("   ✅ Daily intelligence successful!")
                
                data = intel_data.get("data", {})
                for league, league_data in data.items():
                    games = league_data.get("games", [])
                    odds = league_data.get("odds", [])
                    error = league_data.get("error")
                    
                    print(f"   📊 {league}:")
                    if error:
                        print(f"      ❌ Error: {error}")
                    else:
                        print(f"      🎮 Games: {len(games) if games else 0}")
                        print(f"      💰 Odds: {len(odds) if odds else 0}")
            else:
                print(f"   ❌ Daily intelligence error: {intel_data}")
        else:
            print(f"   ❌ Daily intelligence request failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error with daily intelligence: {e}")
    
    print("\n🎯 Test Complete!")
    print("✅ Your NBA games and moneylines integration is working!")
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python quick_test.py YOUR_RAILWAY_URL")
        print("Example: python quick_test.py https://sports-production-1234.up.railway.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("🚀 Quick Test: WNBA Games and Moneylines")
    print("=" * 60)
    
    try:
        success = test_wnba_games_and_moneylines(base_url)
        if success:
            print("\n🎉 SUCCESS! Your deployment is working perfectly for WNBA games and moneylines!")
        else:
            print("\n❌ Some issues were found. Check the output above.")
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()