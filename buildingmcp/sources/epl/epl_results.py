#!/usr/bin/env python3
import requests
import json
import sys
from typing import Any, Dict, List, Optional

# This script fetches all available data for a single game on a specific date.

BASE_URL = "http://site.api.espn.com/apis/site/v2/sports/soccer/"
LEAGUE = "eng.1"  # English Premier League
GAME_DATE = "20250203" # Date format: YYYYMMDD

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
    Main function to fetch scoreboard, find the first game,
    and then fetch its detailed summary.
    """
    # 1. Fetch the scoreboard for the specified league and date to find games
    print(f"Fetching scoreboard for {LEAGUE} on {GAME_DATE}...")
    scoreboard_url = f"{BASE_URL}{LEAGUE}/scoreboard"
    scoreboard_params = {"dates": GAME_DATE}
    scoreboard_data = get_json_from_endpoint(scoreboard_url, scoreboard_params)

    events: List[Dict[str, Any]] = scoreboard_data.get("events", [])
    
    if not events:
        print(f"No games found for {LEAGUE} on {GAME_DATE}.", file=sys.stderr)
        sys.exit(0)

    # 2. Select the first event from the list
    first_event = events[0]
    event_id = first_event.get("id")
    event_name = first_event.get("name")

    if not event_id:
        print("ERROR: Could not find an event ID for the first game.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Found game: {event_name} (ID: {event_id})")

    # 3. Fetch the detailed summary data for that specific game
    print(f"Fetching detailed summary for event ID: {event_id}...")
    summary_url = f"{BASE_URL}{LEAGUE}/summary"
    summary_params = {"event": event_id}
    summary_data = get_json_from_endpoint(summary_url, summary_params)

    # 4. Save the complete data to a JSON file
    output_filename = f"epl_game_data_{event_id}_{GAME_DATE}.json"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=4)
        print(f"\nSUCCESS: All available data has been saved to '{output_filename}'")
    except IOError as e:
        print(f"ERROR: Could not write data to file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
