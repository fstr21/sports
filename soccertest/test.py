import requests

# The correct URL from the new documentation
url = "https://api.soccerdataapi.com/matches/"

# --- PARAMETERS TO CHANGE ---
auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
search_league_id = 228  # Premier League
search_date = "15/08/2025"  # Date in DD/MM/YYYY format

# The querystring now includes BOTH the league_id and the date
querystring = {
    'league_id': search_league_id,
    'date': search_date,
    'auth_token': auth_token
}

print(f"Fetching matches for League ID {search_league_id} on {search_date}...")

try:
    response = requests.get(url, params=querystring)
    response.raise_for_status()  # Check for errors
    
    data = response.json()
    
    if not data:
        print("The API returned an empty response. No data available.")
    else:
        for league in data:
            matches = league.get("matches", [])
            
            print("\n" + "="*50)
            print(f" FOUND {len(matches)} MATCH(ES)")
            print("="*50)

            if not matches:
                print(f"No matches found for League {search_league_id} on {search_date}.")
            else:
                for match in matches:
                    home_team = match.get("teams", {}).get("home", {}).get("name", "N/A")
                    away_team = match.get("teams", {}).get("away", {}).get("name", "N/A")
                    match_time = match.get("time", "")
                    status = match.get("status", "Unknown")
                    
                    output = f"[{match_time}] {home_team} vs {away_team} (Status: {status.title()})"
                    print(output)

except requests.exceptions.HTTPError as err:
    print(f"\n--- HTTP Error ---")
    print(err)
    print("This could be a temporary server issue (like a 500 error) or mean no matches were found.")
except requests.exceptions.RequestException as err:
    print(f"\nAn error occurred: {err}")