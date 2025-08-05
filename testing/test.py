#!/usr/bin/env python3
import requests
import json
import sys
from typing import Any, Dict, List, Optional

# This script fetches detailed team-level stats for a single, specified team.

BASE_URL = "http://site.api.espn.com/apis/site/v2/sports/football/"
LEAGUE = "nfl"  # NFL
TEAM_ID = "6" # Example: Dallas Cowboys

def get_json_from_endpoint(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Makes a request to an ESPN API endpoint and returns the JSON response."""
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: A request error occurred: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print("ERROR: Failed to decode JSON from the response.", file=sys.stderr)
        sys.exit(1)

def main():
    """
    Main function to fetch detailed stats for a single specified team.
    """
    # 1. Fetch the detailed stats for the specified team ID
    print(f"Fetching stats for team ID: {TEAM_ID} in {LEAGUE.upper()}...")
    specific_team_url = f"{BASE_URL}{LEAGUE}/teams/{TEAM_ID}"
    team_stats_data = get_json_from_endpoint(specific_team_url)

    try:
        team_name = team_stats_data['team']['displayName']
        print(f"Successfully fetched data for the {team_name}.")
    except KeyError:
        print("Could not extract team name, but data was fetched.")


    # 2. Save the complete data to a JSON file
    output_filename = f"{LEAGUE}_team_{TEAM_ID}_stats.json"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(team_stats_data, f, ensure_ascii=False, indent=4)
        print(f"\nSUCCESS: All team stats have been saved to '{output_filename}'")
    except IOError as e:
        print(f"ERROR: Could not write data to file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
