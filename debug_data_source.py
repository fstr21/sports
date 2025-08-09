#!/usr/bin/env python3
"""
Debug script to understand data sources
"""

import requests
import json

RAILWAY_URL = "https://web-production-b939f.up.railway.app"
API_KEY = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print("DEBUG: Data Source Investigation")
print("="*50)

# Check 1: What sports are available in odds API?
print("\n1. Available sports from Odds API:")
response = requests.get(f"{RAILWAY_URL}/odds/sports?all_sports=true", headers=headers)
if response.status_code == 200:
    sports = response.json()
    if isinstance(sports, list):
        basketball_sports = [s for s in sports if "basketball" in s.get("key", "").lower()]
        print(f"Found {len(basketball_sports)} basketball sports:")
        for sport in basketball_sports:
            print(f"  - {sport.get('title')} (key: {sport.get('key')})")
    else:
        print("Unexpected format:", type(sports))
        if isinstance(sports, dict):
            print("Keys:", list(sports.keys())[:5])
else:
    print(f"Error: {response.status_code}")

# Check 2: Are we using test mode or real API?
print("\n2. Check if we're getting test/mock data:")
response = requests.post(
    f"{RAILWAY_URL}/odds/get-odds",
    headers=headers,
    json={"sport": "basketball_wnba", "regions": "us", "markets": "h2h"}
)

if response.status_code == 200:
    data = response.json()
    if isinstance(data, dict) and "_metadata" in data:
        print("FOUND: This is test/mock data!")
        metadata = data.get("_metadata", {})
        print(f"  Captured at: {metadata.get('captured_at')}")
        print(f"  Description: {metadata.get('description')}")
        print(f"  Tool: {metadata.get('tool')}")
        print(f"  Parameters used: {metadata.get('parameters')}")
        
        actual_data = data.get("data", [])
        if actual_data:
            sample_game = actual_data[0]
            print(f"  Sample game: {sample_game.get('away_team')} @ {sample_game.get('home_team')}")
            print(f"  Sport key: {sample_game.get('sport_key')}")
            print(f"  Sport title: {sample_game.get('sport_title')}")
    elif isinstance(data, list):
        print("This appears to be live data")
        if data:
            sample = data[0]
            print(f"  Sample: {sample.get('sport_key')} - {sample.get('sport_title')}")
    else:
        print("Unknown data format")
else:
    print(f"Request failed: {response.status_code}")

# Check 3: What happens if we request NBA explicitly?
print("\n3. Testing NBA request for comparison:")
response = requests.post(
    f"{RAILWAY_URL}/odds/get-odds",
    headers=headers,
    json={"sport": "basketball_nba", "regions": "us", "markets": "h2h"}
)

if response.status_code == 200:
    data = response.json()
    if isinstance(data, dict) and "_metadata" in data:
        print("NBA also returns test data")
        nba_data = data.get("data", [])
        if nba_data:
            sample = nba_data[0]
            print(f"  NBA sample: {sample.get('sport_key')} - {sample.get('sport_title')}")
    elif isinstance(data, list) and data:
        print("NBA returns live data")
        sample = data[0]
        print(f"  Sample: {sample.get('sport_key')} - {sample.get('sport_title')}")
else:
    print(f"NBA request failed: {response.status_code}")

# Check 4: Are ESPN games actually WNBA?
print("\n4. Verifying ESPN WNBA games:")
response = requests.post(
    f"{RAILWAY_URL}/espn/scoreboard",
    headers=headers,
    json={"sport": "basketball", "league": "wnba"}
)

if response.status_code == 200:
    data = response.json()
    if data.get("ok"):
        games = data.get("data", {}).get("scoreboard", {}).get("events", [])
        print(f"ESPN found {len(games)} games for WNBA")
        
        if games:
            # Look at the actual team data
            sample_game = games[0]
            competitors = sample_game.get("competitions", [{}])[0].get("competitors", [])
            if competitors:
                for comp in competitors:
                    team = comp.get("team", {})
                    team_name = team.get("displayName", "Unknown")
                    team_abbr = team.get("abbreviation", "UNK")
                    print(f"  Team: {team_name} ({team_abbr})")
        else:
            print("  No games found")
    else:
        print("ESPN request failed:", data.get("message"))
else:
    print(f"ESPN request failed: {response.status_code}")

print("\n" + "="*50)
print("CONCLUSION:")
print("This will help us understand where the NBA data is coming from")
print("when we're requesting WNBA odds.")