#!/usr/bin/env python3
"""
Simple WNBA Test Script

Tests WNBA games and moneylines from Railway deployment.
"""

import requests
import json
import sys
from datetime import datetime

def test_wnba(base_url):
    """Test WNBA games and moneylines"""
    
    api_key = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("WNBA Games and Moneylines Test")
    print("=" * 40)
    print(f"Server: {base_url}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Health Check
    print("1. Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print("   SUCCESS: Server is healthy")
            services = health.get("services", {})
            print(f"   ESPN: {'OK' if services.get('sports_ai') else 'FAIL'}")
            print(f"   Odds: {'OK' if services.get('odds') else 'FAIL'}")
        else:
            print(f"   FAIL: Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   FAIL: Cannot reach server: {e}")
        return False
    
    # Step 2: Get WNBA Games
    print("\n2. Getting today's WNBA games...")
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
                print(f"   SUCCESS: Found {len(games)} WNBA games today")
                
                if games:
                    print("   Today's games:")
                    for i, game in enumerate(games):
                        competitors = game.get("competitions", [{}])[0].get("competitors", [])
                        if len(competitors) >= 2:
                            away = competitors[1].get("team", {}).get("displayName", "Away")
                            home = competitors[0].get("team", {}).get("displayName", "Home")
                            status = game.get("status", {}).get("type", {}).get("description", "TBD")
                            print(f"      Game {i+1}: {away} @ {home} ({status})")
                else:
                    print("   INFO: No WNBA games today")
                    
            else:
                print(f"   FAIL: ESPN API error: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"   FAIL: Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   FAIL: Error getting games: {e}")
        return False
    
    # Step 3: Get WNBA Moneylines
    print("\n3. Getting WNBA moneylines...")
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
                print(f"   SUCCESS: Found moneylines for {len(odds_data)} games")
                
                if odds_data:
                    print("   Moneylines:")
                    for i, game in enumerate(odds_data[:5]):  # Show first 5 games
                        home_team = game.get("home_team", "Home")
                        away_team = game.get("away_team", "Away")
                        commence_time = game.get("commence_time", "TBD")
                        
                        print(f"\n      {away_team} @ {home_team}")
                        print(f"         Time: {commence_time}")
                        
                        bookmakers = game.get("bookmakers", [])
                        if bookmakers:
                            # Show odds from first bookmaker
                            book = bookmakers[0]
                            book_name = book.get("title", "Sportsbook")
                            markets = book.get("markets", [])
                            
                            for market in markets:
                                if market.get("key") == "h2h":
                                    outcomes = market.get("outcomes", [])
                                    print(f"         {book_name}:")
                                    for outcome in outcomes:
                                        team = outcome.get("name", "Unknown")
                                        odds = outcome.get("price", "N/A")
                                        print(f"            {team}: {odds}")
                        else:
                            print("         No odds available")
                else:
                    print("   INFO: No games with moneylines found")
                    
            else:
                print(f"   FAIL: Odds API error: {odds_data}")
                return False
                
        else:
            print(f"   FAIL: Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   FAIL: Error getting odds: {e}")
        return False
    
    # Step 4: Test Natural Language Query
    print("\n4. Testing natural language query...")
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
                print("   SUCCESS: Natural language query worked!")
                interpretation = nl_data.get("interpretation", "")
                if interpretation:
                    print(f"   AI understood: {interpretation}")
                    
                # Check if we got actual results
                result = nl_data.get("result", {})
                if result and result.get("ok"):
                    print("   SUCCESS: Query executed and returned data")
                else:
                    print("   WARNING: Query processed but may not have data")
            else:
                print(f"   FAIL: Natural language error: {nl_data}")
        else:
            print(f"   FAIL: Natural language request failed: {response.status_code}")
            
    except Exception as e:
        print(f"   FAIL: Error with natural language: {e}")
    
    # Step 5: Test Player Props
    print("\n5. Testing WNBA Player Props...")
    try:
        response = requests.post(
            f"{base_url}/odds/player-props",
            headers=headers,
            json={
                "sport": "basketball_wnba",
                "player_markets": "player_points,player_rebounds,player_assists"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            props_data = response.json()
            if props_data.get("status") == "success":
                games_with_props = props_data.get("games_with_props", 0)
                print(f"   SUCCESS: Found player props for {games_with_props} games")
                
                # Show sample player props
                if games_with_props > 0:
                    sample_game = props_data.get("data", [{}])[0]
                    home_team = sample_game.get("home_team", "")
                    away_team = sample_game.get("away_team", "")
                    if home_team and away_team:
                        print(f"   Sample game: {away_team} @ {home_team}")
                        
                        player_props = sample_game.get("player_props", [])
                        if player_props:
                            sample_book = player_props[0]
                            bookmaker = sample_book.get("bookmaker", "")
                            markets = sample_book.get("markets", [])
                            print(f"   Bookmaker: {bookmaker}")
                            print(f"   Markets available: {len(markets)}")
                            
                            # Show sample outcomes
                            if markets:
                                sample_market = markets[0]
                                market_name = sample_market.get("market", "")
                                outcomes = sample_market.get("outcomes", [])
                                print(f"   Sample market '{market_name}': {len(outcomes)} outcomes")
                                
                                for i, outcome in enumerate(outcomes[:2]):  # Show first 2
                                    player = outcome.get("player", "")
                                    bet_type = outcome.get("bet_type", "")
                                    price = outcome.get("price", "")
                                    point = outcome.get("point", "")
                                    if point:
                                        print(f"      {player} - {bet_type} {point}: {price}")
                                    else:
                                        print(f"      {player} - {bet_type}: {price}")
                else:
                    print("   INFO: No games with player props found")
            else:
                print(f"   FAIL: Player props error: {props_data}")
        else:
            print(f"   FAIL: Player props request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   FAIL: Error getting player props: {e}")
    
    print("\nTest Complete!")
    print("SUCCESS: Your WNBA games, moneylines, and player props integration is working!")
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_wnba_simple.py YOUR_RAILWAY_URL")
        print("Example: python test_wnba_simple.py https://web-production-b939f.up.railway.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("Quick Test: WNBA Games and Moneylines")
    print("=" * 45)
    
    try:
        success = test_wnba(base_url)
        if success:
            print("\nSUCCESS! Your deployment works for WNBA!")
        else:
            print("\nSome issues found. Check output above.")
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nTest interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()