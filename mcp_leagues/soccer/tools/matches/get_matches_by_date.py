#!/usr/bin/env python3
"""
SoccerDataAPI Matches by Date Fetcher
Retrieves matches for specified league and date and exports to JSON file
"""

import requests
import json
from datetime import datetime
import os

def get_matches_by_date(league_id, date, auth_token):
    """Get matches by league and date from SoccerDataAPI"""
    
    url = "https://api.soccerdataapi.com/matches/"
    # Add both league_id and date parameters
    querystring = {'league_id': league_id, 'date': date, 'auth_token': auth_token}
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

def save_to_json(data, league_id, date, output_dir):
    """Save match data to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    date_clean = date.replace("/", "_")
    filename = f"matches_league_{league_id}_date_{date_clean}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"SUCCESS - Data saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"ERROR - Error saving file: {e}")
        return None

def display_matches_by_date(match_data, league_id, date):
    """Display match information in easy-to-read format"""
    print("\n" + "="*80)
    print(f"MATCHES BY DATE - LEAGUE ID: {league_id} - DATE: {date}")
    print("="*80)
    
    if isinstance(match_data, list) and len(match_data) > 0:
        league_info = match_data[0]
        matches = league_info.get('matches', [])
        
        print(f"League: {league_info.get('league_name', 'N/A')}")
        print(f"Country: {league_info.get('country', {}).get('name', 'N/A')}")
        print(f"Is Cup: {'Yes' if league_info.get('is_cup') else 'No'}")
        print(f"Total Matches Found on {date}: {len(matches)}")
        print()
        
        if matches:
            print("MATCHES ON THIS DATE:")
            print("-" * 60)
            
            for i, match in enumerate(matches, 1):
                print(f"Match #{i}:")
                print(f"  Match ID: {match.get('id', 'N/A')}")
                print(f"  Date: {match.get('date', 'N/A')}")
                print(f"  Time: {match.get('time', 'N/A')}")
                
                teams = match.get('teams', {})
                home_team = teams.get('home', {})
                away_team = teams.get('away', {})
                print(f"  Home Team: {home_team.get('name', 'N/A')} (ID: {home_team.get('id', 'N/A')})")
                print(f"  Away Team: {away_team.get('name', 'N/A')} (ID: {away_team.get('id', 'N/A')})")
                
                print(f"  Status: {match.get('status', 'N/A')}")
                print(f"  Winner: {match.get('winner', 'N/A')}")
                
                goals = match.get('goals', {})
                if goals and goals.get('home_ft_goals') is not None and goals.get('away_ft_goals') is not None:
                    home_goals = goals.get('home_ft_goals', 0)
                    away_goals = goals.get('away_ft_goals', 0)
                    if home_goals >= 0 and away_goals >= 0:
                        print(f"  Final Score: {home_goals} - {away_goals}")
                
                stage = match.get('stage', {})
                if stage:
                    print(f"  Stage: {stage.get('name', 'N/A')}")
                
                # Show events count if any
                events = match.get('events', [])
                if events:
                    print(f"  Events: {len(events)} (goals, cards, substitutions)")
                
                # Show odds if available
                odds = match.get('odds', {})
                match_winner_odds = odds.get('match_winner', {})
                if match_winner_odds:
                    home_odds = match_winner_odds.get('home')
                    draw_odds = match_winner_odds.get('draw')
                    away_odds = match_winner_odds.get('away')
                    if home_odds and draw_odds and away_odds:
                        print(f"  Odds: H:{home_odds} D:{draw_odds} A:{away_odds}")
                
                print()
        else:
            print(f"No matches found for {date}")
            
    else:
        print("No match data found in response")
    
    print("\n" + "="*80)
    print("RAW DATA STRUCTURE")
    print("="*80)
    print(json.dumps(match_data, indent=2, ensure_ascii=False))
    print("="*80)

def main():
    # Configuration
    league_id = 228  # Premier League
    target_date = "18/08/2025"  # The date we want
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    
    # Get current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("SoccerDataAPI Matches by Date Fetcher")
    print(f"Trying to fetch matches for League ID: {league_id}, Date: {target_date}")
    print(f"Output directory: {script_dir}")
    
    # Try multiple date formats
    date_formats = [
        "18/08/2025",    # DD/MM/YYYY
        "2025-08-18",    # YYYY-MM-DD
        "08/18/2025",    # MM/DD/YYYY
        "18-08-2025",    # DD-MM-YYYY
        "2025/08/18"     # YYYY/MM/DD
    ]
    
    match_data = None
    successful_format = None
    
    for date_format in date_formats:
        print(f"\nTrying date format: {date_format}")
        match_data = get_matches_by_date(league_id, date_format, auth_token)
        if match_data:
            successful_format = date_format
            print(f"SUCCESS with format: {date_format}")
            break
        else:
            print(f"Failed with format: {date_format}")
    
    if match_data and successful_format:
        # Display formatted information
        display_matches_by_date(match_data, league_id, successful_format)
        
        # Save to JSON file
        saved_file = save_to_json(match_data, league_id, successful_format, script_dir)
        
        if saved_file:
            print(f"\nSUCCESS! Match data retrieved and saved using date format: {successful_format}")
        else:
            print(f"\nWARNING - Data retrieved but failed to save to file.")
    else:
        print("ERROR - Failed to fetch match data with any date format")

if __name__ == "__main__":
    main()