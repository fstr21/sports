# file: get_wnba_player_props_aug9.py
import requests
from datetime import datetime, timedelta
import pytz

ODDS_API_KEY = "85edbe8616f7887b660905e1ecde8600"
SPORT = "basketball_wnba"
REGION = "us"
PLAYER_MARKETS = "player_points,player_rebounds,player_assists"  # Player prop markets

# Timezone setup
eastern = pytz.timezone("US/Eastern")
utc = pytz.UTC

# Set our target date (Aug 9, 2025 in Eastern Time)
target_date_et = eastern.localize(datetime(2025, 8, 9))
next_day_et = target_date_et + timedelta(days=1)

# Convert to UTC for filtering
target_date_utc = target_date_et.astimezone(utc)
next_day_utc = next_day_et.astimezone(utc)

# Step 1: Get all WNBA games to get event IDs
print("Getting WNBA games...")
games_url = "https://api.the-odds-api.com/v4/sports/{}/odds".format(SPORT)
games_params = {
    "apiKey": ODDS_API_KEY,
    "regions": REGION,
    "markets": "h2h",  # Just need basic info to get event IDs
    "oddsFormat": "american"
}

games_response = requests.get(games_url, params=games_params)

if games_response.status_code != 200:
    print("Error getting games:", games_response.status_code, games_response.text)
    exit()

games = games_response.json()

print(f"WNBA Player Props for {target_date_et.strftime('%B %d, %Y')} (Eastern Time):\n")

# Step 2: For each game on target date, get player props
for game in games:
    commence_time_utc = datetime.fromisoformat(game["commence_time"].replace("Z", "+00:00"))
    if target_date_utc <= commence_time_utc < next_day_utc:
        commence_time_et = commence_time_utc.astimezone(eastern)
        event_id = game["id"]
        
        print(f"{game['home_team']} vs {game['away_team']} - {commence_time_et.strftime('%Y-%m-%d %I:%M %p ET')}")
        print(f"Event ID: {event_id}")
        
        # Get player props for this specific event
        event_url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/events/{event_id}/odds"
        event_params = {
            "apiKey": ODDS_API_KEY,
            "regions": REGION,
            "markets": PLAYER_MARKETS,
            "oddsFormat": "american"
        }
        
        event_response = requests.get(event_url, params=event_params)
        
        if event_response.status_code == 200:
            event_data = event_response.json()
            
            if event_data.get("bookmakers"):
                for bookmaker in event_data.get("bookmakers", []):
                    print(f"  Bookmaker: {bookmaker['title']}")
                    for market in bookmaker.get("markets", []):
                        print(f"    Market: {market['key']}")
                        for outcome in market.get("outcomes", []):
                            player_name = outcome.get('description', 'Unknown Player')
                            bet_type = outcome.get('name', 'Unknown')
                            price = outcome.get('price', 'N/A')
                            point = outcome.get('point', '')
                            if point:
                                print(f"      {player_name} - {bet_type} {point}: {price}")
                            else:
                                print(f"      {player_name} - {bet_type}: {price}")
            else:
                print("  No player props available for this game")
        else:
            print(f"  Error getting player props: {event_response.status_code} - {event_response.text}")
        
        print()
