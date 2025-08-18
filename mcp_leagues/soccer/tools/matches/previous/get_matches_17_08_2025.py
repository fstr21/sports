#!/usr/bin/env python3
"""
SoccerDataAPI Matches by Date Fetcher for 17-08-2025
Retrieves matches for League 228 on 17-08-2025 and exports to JSON file
"""

import requests
import json
from datetime import datetime
import os

def get_matches_by_date(league_id, date, auth_token):
    """Get matches by league and date from SoccerDataAPI"""
    
    url = "https://api.soccerdataapi.com/matches/"
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
    date_clean = date.replace("/", "_").replace("-", "_")
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
        
        # Check if matches are in the main structure or in stages
        matches = []
        if 'matches' in league_info:
            matches = league_info.get('matches', [])
        elif 'stage' in league_info:
            # Look for matches in stages
            stages = league_info.get('stage', [])
            for stage in stages:
                stage_matches = stage.get('matches', [])
                matches.extend(stage_matches)
        
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
    date = "17-08-2025"  # DD-MM-YYYY format (we know this works)
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    
    # Get current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("SoccerDataAPI Matches by Date Fetcher")
    print(f"Fetching matches for League ID: {league_id}, Date: {date}")
    print(f"Output directory: {script_dir}")
    
    # Fetch match data
    match_data = get_matches_by_date(league_id, date, auth_token)
    
    if match_data:
        # Display formatted information
        display_matches_by_date(match_data, league_id, date)
        
        # Save to JSON file
        saved_file = save_to_json(match_data, league_id, date, script_dir)
        
        if saved_file:
            print(f"\nSUCCESS! Match data retrieved and saved.")
        else:
            print(f"\nWARNING - Data retrieved but failed to save to file.")
    else:
        print("ERROR - Failed to fetch match data")

if __name__ == "__main__":
    main()