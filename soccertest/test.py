import requests
from datetime import datetime

API_KEY = "4ef45782f5934d29afccf5f31469878c"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}

def get_competition_id_by_name(name):
    """Find competition ID by its name."""
    url = f"{BASE_URL}/competitions"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    for comp in resp.json().get("competitions", []):
        if comp["name"].lower() == name.lower():
            return comp["code"]
    raise ValueError(f"Competition '{name}' not found.")

def get_team_id_in_competition(competition_code, team_name):
    """Get team ID for a given competition."""
    url = f"{BASE_URL}/competitions/{competition_code}/teams"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    for team in resp.json().get("teams", []):
        if team["name"].lower() == team_name.lower():
            return team["id"]
    raise ValueError(f"Team '{team_name}' not found in competition {competition_code}.")

def get_player_id(team_id, player_name):
    """Fetch squad for a team and return player ID."""
    url = f"{BASE_URL}/teams/{team_id}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    for player in resp.json().get("squad", []):
        if player["name"].lower() == player_name.lower():
            return player["id"]
    raise ValueError(f"Player '{player_name}' not found in team {team_id}.")

def get_recent_matches(player_id, competition_code, limit=5):
    """Fetch recent matches for a player in a competition."""
    url = f"{BASE_URL}/persons/{player_id}/matches"
    params = {"competitions": competition_code, "status": "FINISHED"}
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    matches = resp.json().get("matches", [])
    matches.sort(key=lambda m: m.get("utcDate"), reverse=True)
    return matches[:limit]

def print_matches(player_name, matches):
    print(f"\n=== {player_name} - Last {len(matches)} Matches ===")
    for match in matches:
        date = datetime.fromisoformat(match["utcDate"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]
        opponent = away if home.lower() == "dc united" else home
        print(f"{date} | vs {opponent} | Status: {match['status']}")

if __name__ == "__main__":
    try:
        competition_code = get_competition_id_by_name("Major League Soccer")
        team_id = get_team_id_in_competition(competition_code, "DC United")
        player_id = get_player_id(team_id, "João Peglow")
        recent_matches = get_recent_matches(player_id, competition_code)
        print_matches("João Peglow", recent_matches)
    except Exception as e:
        print(f"Error: {e}")
