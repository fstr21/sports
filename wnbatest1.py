#!/usr/bin/env python3
"""
wnbatest1.py - Direct test of WNBA games and moneylines via Railway MCP servers
"""

import requests
import json

# Railway URL and API key
RAILWAY_URL = "https://web-production-b939f.up.railway.app"
API_KEY = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print("WNBA Test 1 - Games and Moneylines")
print("="*40)

# Step 1: Get WNBA games today
print("1. Getting today's WNBA games...")
response = requests.post(
    f"{RAILWAY_URL}/espn/scoreboard",
    headers=headers,
    json={"sport": "basketball", "league": "wnba"}
)

if response.status_code == 200:
    games_data = response.json()
    if games_data.get("ok"):
        games = games_data.get("data", {}).get("scoreboard", {}).get("events", [])
        print(f"Found {len(games)} WNBA games today")
        
        for i, game in enumerate(games, 1):
            competitors = game.get("competitions", [{}])[0].get("competitors", [])
            if len(competitors) >= 2:
                away = competitors[1].get("team", {}).get("displayName", "Away")
                home = competitors[0].get("team", {}).get("displayName", "Home")
                status = game.get("status", {}).get("type", {}).get("description", "TBD")
                print(f"  Game {i}: {away} @ {home} ({status})")
    else:
        print("Error getting games:", games_data.get("message"))
else:
    print(f"Request failed: {response.status_code}")

# Step 2: Get WNBA moneylines
print("\n2. Getting WNBA moneylines...")
response = requests.post(
    f"{RAILWAY_URL}/odds/get-odds",
    headers=headers,
    json={
        "sport": "basketball_wnba",
        "regions": "us",
        "markets": "h2h",
        "odds_format": "american"
    }
)

if response.status_code == 200:
    odds_data = response.json()
    
    # Handle both live data and test data formats
    if isinstance(odds_data, list):
        games_with_odds = odds_data
    elif isinstance(odds_data, dict) and "data" in odds_data:
        games_with_odds = odds_data["data"]
    else:
        games_with_odds = []
    
    print(f"Found moneylines for {len(games_with_odds)} games")
    
    for i, game in enumerate(games_with_odds, 1):
        home_team = game.get("home_team", "Home")
        away_team = game.get("away_team", "Away")
        
        print(f"  Game {i}: {away_team} @ {home_team}")
        
        bookmakers = game.get("bookmakers", [])
        if bookmakers:
            # Show first bookmaker's odds
            book = bookmakers[0]
            book_name = book.get("title", "Unknown")
            print(f"    {book_name}:")
            
            for market in book.get("markets", []):
                if market.get("key") == "h2h":
                    for outcome in market.get("outcomes", []):
                        team = outcome.get("name", "Unknown")
                        price = outcome.get("price", "N/A")
                        print(f"      {team}: {price}")
        else:
            print("    No odds available")
else:
    print(f"Odds request failed: {response.status_code}")
    print(response.text)

print("\nTest complete.")