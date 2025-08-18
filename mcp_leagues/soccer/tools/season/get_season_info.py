#!/usr/bin/env python3
"""
SoccerDataAPI Season Information Fetcher
Retrieves season information for specified leagues and exports to JSON file
"""

import requests
import json
from datetime import datetime
import os

def get_season_info(league_id, auth_token):
    """Get season information from SoccerDataAPI"""
    
    url = "https://api.soccerdataapi.com/season/"
    querystring = {'league_id': league_id, 'auth_token': auth_token}
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

def save_to_json(data, league_id, output_dir):
    """Save season data to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"seasons_league_{league_id}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"SUCCESS - Data saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"ERROR - Error saving file: {e}")
        return None

def display_season_info(season_data, league_id):
    """Display season information in easy-to-read format"""
    print("\n" + "="*60)
    print(f"SEASON INFORMATION - LEAGUE ID: {league_id}")
    print("="*60)
    
    if 'results' in season_data:
        seasons = season_data['results']
        print(f"Total Seasons Found: {season_data.get('count', len(seasons))}")
        print()
        
        for i, season in enumerate(seasons, 1):
            season_info = season.get('season', {})
            league_info = season.get('league', {})
            
            print(f"Season #{i}:")
            print(f"  Season ID: {season.get('id', 'N/A')}")
            print(f"  Year: {season_info.get('year', 'N/A')}")
            print(f"  League: {league_info.get('name', 'N/A')}")
            print(f"  Is Active: {'Yes' if season_info.get('is_active') else 'No'}")
            print()
    else:
        print("No season data found in response")
    
    print("="*60)
    print("RAW DATA STRUCTURE")
    print("="*60)
    print(json.dumps(season_data, indent=2, ensure_ascii=False))
    print("="*60)

def main():
    # Configuration
    league_ids = [228, 297]  # Premier League and Bundesliga
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    
    # Get current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("SoccerDataAPI Season Information Fetcher")
    print(f"Fetching season info for League IDs: {league_ids}")
    print(f"Output directory: {script_dir}")
    
    all_data = {}
    
    for league_id in league_ids:
        print(f"\n{'='*40}")
        print(f"Processing League ID: {league_id}")
        print(f"{'='*40}")
        
        # Fetch season data
        season_data = get_season_info(league_id, auth_token)
        
        if season_data:
            # Store data for combined export
            all_data[f"league_{league_id}"] = season_data
            
            # Display formatted information
            display_season_info(season_data, league_id)
            
            # Save individual JSON file
            saved_file = save_to_json(season_data, league_id, script_dir)
            
            if saved_file:
                print(f"SUCCESS - League {league_id} data retrieved and saved.")
            else:
                print(f"WARNING - League {league_id} data retrieved but failed to save to file.")
        else:
            print(f"ERROR - Failed to fetch season data for league {league_id}")
    
    # Save combined data
    if all_data:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        combined_filename = f"all_seasons_combined_{timestamp}.json"
        combined_filepath = os.path.join(script_dir, combined_filename)
        
        try:
            with open(combined_filepath, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False)
            print(f"\nSUCCESS - Combined data saved to: {combined_filepath}")
        except Exception as e:
            print(f"ERROR - Failed to save combined file: {e}")

if __name__ == "__main__":
    main()