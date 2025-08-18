#!/usr/bin/env python3
"""
SoccerDataAPI Match Information Fetcher
Retrieves match information for specified league and season and exports to JSON file
"""

import requests
import json
from datetime import datetime
import os

def get_match_info(league_id, season, auth_token):
    """Get match information from SoccerDataAPI"""
    
    url = "https://api.soccerdataapi.com/matches/"
    querystring = {'league_id': league_id, 'season': season, 'auth_token': auth_token}
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

def save_to_json(data, league_id, season, output_dir):
    """Save match data to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    season_clean = season.replace("-", "_")
    filename = f"matches_league_{league_id}_season_{season_clean}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"SUCCESS - Data saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"ERROR - Error saving file: {e}")
        return None

def display_match_info(match_data, league_id, season):
    """Display match information in easy-to-read format"""
    print("\n" + "="*80)
    print(f"MATCH INFORMATION - LEAGUE ID: {league_id} - SEASON: {season}")
    print("="*80)
    
    if isinstance(match_data, list) and len(match_data) > 0:
        league_info = match_data[0]
        matches = league_info.get('matches', [])
        
        print(f"League: {league_info.get('league_name', 'N/A')}")
        print(f"Country: {league_info.get('country', {}).get('name', 'N/A')}")
        print(f"Is Cup: {'Yes' if league_info.get('is_cup') else 'No'}")
        print(f"Total Matches Found: {len(matches)}")
        print()
        
        # Show first few matches with date format analysis
        print("SAMPLE MATCHES (showing first 5):")
        print("-" * 60)
        
        for i, match in enumerate(matches[:5], 1):
            print(f"Match #{i}:")
            print(f"  Match ID: {match.get('id', 'N/A')}")
            print(f"  Date: {match.get('date', 'N/A')} (FORMAT: DD/MM/YYYY)")
            print(f"  Time: {match.get('time', 'N/A')} (FORMAT: HH:MM)")
            
            teams = match.get('teams', {})
            home_team = teams.get('home', {})
            away_team = teams.get('away', {})
            print(f"  Home Team: {home_team.get('name', 'N/A')} (ID: {home_team.get('id', 'N/A')})")
            print(f"  Away Team: {away_team.get('name', 'N/A')} (ID: {away_team.get('id', 'N/A')})")
            
            print(f"  Status: {match.get('status', 'N/A')}")
            print(f"  Winner: {match.get('winner', 'N/A')}")
            
            goals = match.get('goals', {})
            if goals:
                print(f"  Score: {goals.get('home_ft_goals', 'N/A')} - {goals.get('away_ft_goals', 'N/A')}")
            
            stage = match.get('stage', {})
            if stage:
                print(f"  Stage: {stage.get('name', 'N/A')}")
            
            print()
        
        # Date format analysis
        print("DATE FORMAT ANALYSIS:")
        print("-" * 40)
        sample_dates = [match.get('date') for match in matches[:10] if match.get('date')]
        sample_times = [match.get('time') for match in matches[:10] if match.get('time')]
        
        if sample_dates:
            print(f"Sample Dates: {sample_dates[:5]}")
            print("Date Format: DD/MM/YYYY (e.g., 26/08/2023)")
        
        if sample_times:
            print(f"Sample Times: {sample_times[:5]}")
            print("Time Format: HH:MM (24-hour format)")
        
    else:
        print("No match data found in response")
    
    print("\n" + "="*80)
    print("RAW DATA STRUCTURE (First 2 matches only for readability)")
    print("="*80)
    
    # Show limited raw data for readability
    if isinstance(match_data, list) and len(match_data) > 0:
        limited_data = match_data.copy()
        if 'matches' in limited_data[0] and len(limited_data[0]['matches']) > 2:
            limited_data[0]['matches'] = limited_data[0]['matches'][:2]
        print(json.dumps(limited_data, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(match_data, indent=2, ensure_ascii=False))
    print("="*80)

def main():
    # Configuration
    league_id = 228  # Premier League
    season = "2025-2026"
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    
    # Get current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("SoccerDataAPI Match Information Fetcher")
    print(f"Fetching match info for League ID: {league_id}, Season: {season}")
    print(f"Output directory: {script_dir}")
    
    # Fetch match data
    match_data = get_match_info(league_id, season, auth_token)
    
    if match_data:
        # Display formatted information
        display_match_info(match_data, league_id, season)
        
        # Save to JSON file
        saved_file = save_to_json(match_data, league_id, season, script_dir)
        
        if saved_file:
            print(f"\nSUCCESS! Match data retrieved and saved.")
        else:
            print(f"\nWARNING - Data retrieved but failed to save to file.")
    else:
        print("ERROR - Failed to fetch match data")

if __name__ == "__main__":
    main()