#!/usr/bin/env python3
import requests
import json
import sys
from typing import Any, Dict, List, Optional

# This script fetches all available schedule data for a league on a specific date.

BASE_URL = "http://site.api.espn.com/apis/site/v2/sports/football/"
LEAGUE = "nfl"  # NFL
GAME_DATE = "20250904" # Date format: YYYYMMDD

def get_json_from_endpoint(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Makes a request to an ESPN API endpoint and returns the JSON response."""
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: A request error occurred: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print("ERROR: Failed to decode JSON from the response.", file=sys.stderr)
        sys.exit(1)

def main():
    """
    Main function to fetch the scoreboard for a given date and save it.
    """
    # 1. Fetch the scoreboard for the specified league and date to find all games
    print(f"Fetching schedule for {LEAGUE.upper()} on {GAME_DATE}...")
    scoreboard_url = f"{BASE_URL}{LEAGUE}/scoreboard"
    scoreboard_params = {"dates": GAME_DATE}
    scoreboard_data = get_json_from_endpoint(scoreboard_url, scoreboard_params)

    events: List[Dict[str, Any]] = scoreboard_data.get("events", [])
    
    if not events:
        print(f"No games found for {LEAGUE.upper()} on {GAME_DATE}.", file=sys.stderr)
        sys.exit(0)
        
    print(f"Found {len(events)} game(s) scheduled for this date.")

    # 2. Save the complete scoreboard data to a JSON file
    output_filename = f"nfl_schedule_{GAME_DATE}.json"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(scoreboard_data, f, ensure_ascii=False, indent=4)
        print(f"\nSUCCESS: All available schedule data has been saved to '{output_filename}'")
    except IOError as e:
        print(f"ERROR: Could not write data to file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
