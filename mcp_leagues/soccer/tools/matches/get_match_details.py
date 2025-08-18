#!/usr/bin/env python3
"""
SoccerDataAPI Match Details Fetcher
Retrieves detailed match information for a specific match ID and exports to JSON file
"""

import requests
import json
from datetime import datetime
import os

def get_match_details(match_id, auth_token):
    """Get detailed match information from SoccerDataAPI"""
    
    url = "https://api.soccerdataapi.com/match/"
    querystring = {'match_id': match_id, 'auth_token': auth_token}
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

def save_to_json(data, match_id, output_dir):
    """Save match data to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"match_details_{match_id}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"SUCCESS - Data saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"ERROR - Error saving file: {e}")
        return None

def display_match_details(match_data, match_id):
    """Display match information in easy-to-read format"""
    print("\n" + "="*80)
    print(f"MATCH DETAILS - MATCH ID: {match_id}")
    print("="*80)
    
    if match_data:
        print("BASIC MATCH INFORMATION:")
        print("-" * 40)
        print(f"Match ID: {match_data.get('id', 'N/A')}")
        print(f"Date: {match_data.get('date', 'N/A')}")
        print(f"Time: {match_data.get('time', 'N/A')}")
        print(f"Status: {match_data.get('status', 'N/A')}")
        print(f"Winner: {match_data.get('winner', 'N/A')}")
        
        # League information
        league = match_data.get('league', {})
        if league:
            print(f"League: {league.get('name', 'N/A')} (ID: {league.get('id', 'N/A')})")
        
        # Stage information
        stage = match_data.get('stage', {})
        if stage:
            print(f"Stage: {stage.get('name', 'N/A')} (ID: {stage.get('id', 'N/A')})")
        
        # Teams
        teams = match_data.get('teams', {})
        home_team = teams.get('home', {})
        away_team = teams.get('away', {})
        print(f"Home Team: {home_team.get('name', 'N/A')} (ID: {home_team.get('id', 'N/A')})")
        print(f"Away Team: {away_team.get('name', 'N/A')} (ID: {away_team.get('id', 'N/A')})")
        
        # Stadium
        stadium = match_data.get('stadium', {})
        if stadium:
            print(f"Stadium: {stadium.get('name', 'N/A')}")
            print(f"City: {stadium.get('city', 'N/A')}")
        
        # Goals/Score
        goals = match_data.get('goals', {})
        if goals:
            print("\nSCORE INFORMATION:")
            print("-" * 20)
            ht_home = goals.get('home_ht_goals', 'N/A')
            ht_away = goals.get('away_ht_goals', 'N/A')
            ft_home = goals.get('home_ft_goals', 'N/A')
            ft_away = goals.get('away_ft_goals', 'N/A')
            
            if ft_home != 'N/A' and ft_away != 'N/A' and ft_home >= 0 and ft_away >= 0:
                print(f"Final Score: {ft_home} - {ft_away}")
            if ht_home != 'N/A' and ht_away != 'N/A' and ht_home >= 0 and ht_away >= 0:
                print(f"Half Time: {ht_home} - {ht_away}")
        
        # Events
        events = match_data.get('events', [])
        if events:
            print(f"\nMATCH EVENTS ({len(events)} total):")
            print("-" * 30)
            for i, event in enumerate(events[:10], 1):  # Show first 10 events
                event_type = event.get('event_type', 'N/A')
                minute = event.get('event_minute', 'N/A')
                team = event.get('team', 'N/A')
                player = event.get('player', {}).get('name', 'N/A')
                assist = event.get('assist_player', {})
                assist_name = assist.get('name', '') if assist else ''
                
                event_desc = f"{minute}' {event_type.replace('_', ' ').title()} - {team} - {player}"
                if assist_name:
                    event_desc += f" (Assist: {assist_name})"
                print(f"  {i}. {event_desc}")
            
            if len(events) > 10:
                print(f"  ... and {len(events) - 10} more events")
        
        # Odds
        odds = match_data.get('odds', {})
        if odds:
            print("\nBETTING ODDS:")
            print("-" * 15)
            match_winner = odds.get('match_winner', {})
            if match_winner:
                home_odds = match_winner.get('home', 'N/A')
                draw_odds = match_winner.get('draw', 'N/A')
                away_odds = match_winner.get('away', 'N/A')
                print(f"Match Winner - Home: {home_odds}, Draw: {draw_odds}, Away: {away_odds}")
            
            over_under = odds.get('over_under', {})
            if over_under:
                total = over_under.get('total', 'N/A')
                over = over_under.get('over', 'N/A')
                under = over_under.get('under', 'N/A')
                print(f"Over/Under {total} - Over: {over}, Under: {under}")
        
        # Lineups
        lineups = match_data.get('lineups', {})
        if lineups and lineups.get('lineups'):
            lineup_data = lineups.get('lineups', {})
            home_lineup = lineup_data.get('home', [])
            away_lineup = lineup_data.get('away', [])
            
            print(f"\nLINEUPS:")
            print("-" * 10)
            if home_lineup:
                print(f"Home Team ({len(home_lineup)} players):")
                for player in home_lineup[:5]:  # Show first 5 players
                    player_info = player.get('player', {})
                    position = player.get('position', 'N/A')
                    name = player_info.get('name', 'N/A')
                    print(f"  {name} ({position})")
                if len(home_lineup) > 5:
                    print(f"  ... and {len(home_lineup) - 5} more players")
            
            if away_lineup:
                print(f"Away Team ({len(away_lineup)} players):")
                for player in away_lineup[:5]:  # Show first 5 players
                    player_info = player.get('player', {})
                    position = player.get('position', 'N/A')
                    name = player_info.get('name', 'N/A')
                    print(f"  {name} ({position})")
                if len(away_lineup) > 5:
                    print(f"  ... and {len(away_lineup) - 5} more players")
        
        # Match Preview
        preview = match_data.get('match_preview', {})
        if preview:
            print(f"\nMATCH PREVIEW:")
            print("-" * 15)
            has_preview = preview.get('has_preview', False)
            word_count = preview.get('word_count', 'N/A')
            print(f"Has Preview: {'Yes' if has_preview else 'No'}")
            if word_count and word_count > 0:
                print(f"Word Count: {word_count}")
    else:
        print("No match data found")
    
    print("\n" + "="*80)
    print("RAW DATA STRUCTURE")
    print("="*80)
    print(json.dumps(match_data, indent=2, ensure_ascii=False))
    print("="*80)

def main():
    # Configuration
    match_id = 954382  # Leeds United vs Everton
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    
    # Get current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("SoccerDataAPI Match Details Fetcher")
    print(f"Fetching detailed match info for Match ID: {match_id}")
    print(f"Output directory: {script_dir}")
    
    # Fetch match data
    match_data = get_match_details(match_id, auth_token)
    
    if match_data:
        # Display formatted information
        display_match_details(match_data, match_id)
        
        # Save to JSON file
        saved_file = save_to_json(match_data, match_id, script_dir)
        
        if saved_file:
            print(f"\nSUCCESS! Match details retrieved and saved.")
        else:
            print(f"\nWARNING - Data retrieved but failed to save to file.")
    else:
        print("ERROR - Failed to fetch match data")

if __name__ == "__main__":
    main()