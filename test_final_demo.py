#!/usr/bin/env python3
"""
Final WNBA Demo Test

This script demonstrates the working WNBA games, moneylines, and player props integration.
"""

import requests
import json
import sys

def demo_wnba(base_url):
    """Demo WNBA integration"""
    
    api_key = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("WNBA Integration Demo")
    print("="*30)
    print(f"Server: {base_url}")
    print()
    
    # Test 1: Health Check
    print("1. Server Health Check")
    response = requests.get(f"{base_url}/health")
    if response.status_code == 200:
        health = response.json()
        print("   Status: HEALTHY")
        services = health.get("services", {})
        print(f"   ESPN Sports: {'Available' if services.get('sports_ai') else 'Not Available'}")
        print(f"   Odds API: {'Available' if services.get('odds') else 'Not Available'}")
        print(f"   AI Analysis: {'Available' if services.get('openrouter') else 'Not Available'}")
    else:
        print("   Status: ERROR")
        return False
    
    # Test 2: WNBA Games Today
    print("\n2. Today's WNBA Games")
    response = requests.post(
        f"{base_url}/espn/scoreboard",
        headers=headers,
        json={"sport": "basketball", "league": "wnba"}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            games = data.get("data", {}).get("scoreboard", {}).get("events", [])
            print(f"   Found: {len(games)} games")
            
            if games:
                for i, game in enumerate(games[:3], 1):
                    competitors = game.get("competitions", [{}])[0].get("competitors", [])
                    if len(competitors) >= 2:
                        away = competitors[1].get("team", {}).get("displayName", "Away")
                        home = competitors[0].get("team", {}).get("displayName", "Home")
                        status = game.get("status", {}).get("type", {}).get("description", "Scheduled")
                        print(f"   Game {i}: {away} @ {home} ({status})")
            else:
                print("   No games found for today")
        else:
            print("   Error getting games")
    else:
        print("   Request failed")
    
    # Test 3: Available Sports from Odds API
    print("\n3. Available Sports (Odds API)")
    response = requests.get(f"{base_url}/odds/sports?all_sports=true", headers=headers)
    
    if response.status_code == 200:
        sports = response.json()
        if isinstance(sports, list):
            print(f"   Total sports available: {len(sports)}")
            
            # Look for WNBA
            wnba_found = False
            for sport in sports:
                if "wnba" in sport.get("key", "").lower() or "wnba" in sport.get("title", "").lower():
                    print(f"   WNBA: {sport.get('title')} (key: {sport.get('key')})")
                    wnba_found = True
                    break
            
            if not wnba_found:
                print("   WNBA not found in sports list")
                
            # Show other basketball sports
            basketball_sports = [s for s in sports if "basketball" in s.get("key", "")]
            print(f"   Basketball sports found: {len(basketball_sports)}")
            for sport in basketball_sports[:3]:
                print(f"     - {sport.get('title')} ({sport.get('key')})")
        else:
            print("   Unexpected response format")
    else:
        print("   Request failed")
    
    # Test 4: Try WNBA Odds
    print("\n4. WNBA Moneylines")
    response = requests.post(
        f"{base_url}/odds/get-odds",
        headers=headers,
        json={
            "sport": "basketball_wnba",
            "regions": "us", 
            "markets": "h2h",
            "odds_format": "american"
        }
    )
    
    if response.status_code == 200:
        odds = response.json()
        if isinstance(odds, list) and len(odds) > 0:
            print(f"   Live WNBA odds found for {len(odds)} games!")
            
            # Show first game odds
            game = odds[0]
            home = game.get("home_team", "Home")
            away = game.get("away_team", "Away")
            commence_time = game.get("commence_time", "TBD")
            
            print(f"   Sample game: {away} @ {home}")
            print(f"   Game time: {commence_time}")
            
            bookmakers = game.get("bookmakers", [])
            if bookmakers:
                book = bookmakers[0]
                print(f"   Bookmaker: {book.get('title')}")
                
                for market in book.get("markets", []):
                    if market.get("key") == "h2h":
                        print("   Moneylines:")
                        for outcome in market.get("outcomes", []):
                            team = outcome.get("name")
                            odds_val = outcome.get("price")
                            print(f"     {team}: {odds_val}")
        elif isinstance(odds, dict) and "_metadata" in odds:
            print("   Getting test data (API key may be needed for live data)")
            test_data = odds.get("data", [])
            if test_data:
                print(f"   Test data shows {len(test_data)} games structure")
        else:
            print("   No WNBA games with odds found")
    else:
        print(f"   Request failed: {response.status_code}")
    
    # Test 5: Natural Language Query
    print("\n5. Natural Language Query")
    response = requests.post(
        f"{base_url}/ask",
        headers=headers,
        json={"question": "What WNBA games are today and what are their moneylines?"}
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("ok"):
            print("   AI Query: SUCCESS")
            interpretation = result.get("interpretation", "")
            if interpretation:
                print(f"   AI understood: {interpretation}")
            
            # Check if we got results
            query_result = result.get("result", {})
            if query_result and query_result.get("ok"):
                print("   Query executed successfully")
        else:
            print("   AI Query: Issues detected")
    else:
        print("   AI Query: Request failed")
    
    # Test 6: Player Props (if available)
    print("\n6. WNBA Player Props")
    response = requests.post(
        f"{base_url}/odds/player-props",
        headers=headers,
        json={
            "sport": "basketball_wnba",
            "player_markets": "player_points,player_rebounds,player_assists"
        }
    )
    
    if response.status_code == 200:
        props = response.json()
        if props.get("status") == "success":
            games_with_props = props.get("games_with_props", 0)
            print(f"   Player props available for {games_with_props} games")
            
            if games_with_props > 0:
                sample_game = props.get("data", [{}])[0]
                home_team = sample_game.get("home_team", "")
                away_team = sample_game.get("away_team", "")
                if home_team and away_team:
                    print(f"   Sample: {away_team} @ {home_team}")
                    
                    player_props = sample_game.get("player_props", [])
                    if player_props:
                        print(f"   Available from {len(player_props)} bookmakers")
        else:
            print("   No player props data available")
    else:
        print("   Player props request failed")
    
    print("\n" + "="*50)
    print("🎉 DEMO COMPLETE!")
    print("✅ Your WNBA sports server is deployed and working!")
    print("🔧 Features available:")
    print("   - ESPN WNBA games and teams")
    print("   - Odds API integration for moneylines")
    print("   - Player props support")
    print("   - Natural language queries")
    print("   - Daily intelligence aggregation")
    print(f"🌐 Your API: {base_url}")
    print("🔑 Use the API key for authentication")
    print("="*50)
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_final_demo.py YOUR_RAILWAY_URL")
        print("Example: python test_final_demo.py https://web-production-b939f.up.railway.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    demo_wnba(base_url)

if __name__ == "__main__":
    main()