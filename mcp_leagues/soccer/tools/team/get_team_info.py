#!/usr/bin/env python3
"""
SoccerDataAPI Team Information Fetcher
Retrieves team information and exports to JSON file
"""

import requests
import json
from datetime import datetime
import os

def get_team_info(team_id, auth_token):
    """Get team information from SoccerDataAPI"""
    
    url = "https://api.soccerdataapi.com/team/"
    querystring = {'team_id': team_id, 'auth_token': auth_token}
    headers = {
        'Accept-Encoding': 'gzip',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        
        data = response.json()
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR - Error making request: {e}")
        return None
    except ValueError as e:
        print(f"ERROR - Error parsing JSON: {e}")
        return None

def save_to_json(data, team_id, output_dir):
    """Save team data to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"team_{team_id}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"SUCCESS - Data saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"ERROR - Error saving file: {e}")
        return None

def display_team_info(team_data):
    """Display team information in easy-to-read format"""
    print("\n" + "="*60)
    print("TEAM INFORMATION")
    print("="*60)
    
    print(f"Team ID: {team_data.get('id', 'N/A')}")
    print(f"Team Name: {team_data.get('name', 'N/A')}")
    
    country = team_data.get('country', {})
    if country:
        print(f"Country: {country.get('name', 'N/A').title()} (ID: {country.get('id', 'N/A')})")
    
    stadium = team_data.get('stadium', {})
    if stadium:
        print(f"Stadium: {stadium.get('name', 'N/A')}")
        print(f"City: {stadium.get('city', 'N/A')}")
        print(f"Stadium ID: {stadium.get('id', 'N/A')}")
    
    print(f"Is National Team: {'Yes' if team_data.get('is_nation') else 'No'}")
    
    print("\n" + "="*60)
    print("RAW DATA STRUCTURE")
    print("="*60)
    print(json.dumps(team_data, indent=2, ensure_ascii=False))
    print("="*60)

def main():
    # Configuration
    team_id = 4140  # Crystal Palace
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    
    # Get current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("SoccerDataAPI Team Information Fetcher")
    print(f"Fetching team info for Team ID: {team_id}")
    print(f"Output directory: {script_dir}")
    
    # Fetch team data
    team_data = get_team_info(team_id, auth_token)
    
    if team_data:
        # Display formatted information
        display_team_info(team_data)
        
        # Save to JSON file
        saved_file = save_to_json(team_data, team_id, script_dir)
        
        if saved_file:
            print(f"\nSUCCESS! Team data retrieved and saved.")
        else:
            print(f"\nWARNING - Data retrieved but failed to save to file.")
    else:
        print("ERROR - Failed to fetch team data")

if __name__ == "__main__":
    main()