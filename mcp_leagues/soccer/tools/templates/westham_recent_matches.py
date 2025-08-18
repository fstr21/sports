#!/usr/bin/env python3
"""
West Ham Recent Matches Finder
Uses the proven date-by-date method to find West Ham's actual recent matches
Based on the dates shown in the West Ham results screenshot
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
        print(f"ERROR - Error making request for {date}: {e}")
        return None
    except ValueError as e:
        print(f"ERROR - Error parsing JSON for {date}: {e}")
        return None

def find_westham_in_matches(match_data, target_date):
    """Find West Ham matches in the response data"""
    westham_matches = []
    
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
        
        # Look for West Ham (ID: 3059) in matches
        for match in matches:
            teams = match.get('teams', {})
            home_team = teams.get('home', {})
            away_team = teams.get('away', {})
            
            home_id = home_team.get('id')
            away_id = away_team.get('id')
            home_name = home_team.get('name', 'Unknown')
            away_name = away_team.get('name', 'Unknown')
            
            # Check if West Ham is playing (ID: 3059)
            if home_id == 3059 or away_id == 3059:
                is_home = (home_id == 3059)
                opponent = away_team if is_home else home_team
                
                # Determine result
                result = determine_result(match, is_home)
                
                westham_matches.append({
                    'date': target_date,
                    'is_home': is_home,
                    'opponent': opponent.get('name', 'Unknown'),
                    'opponent_id': opponent.get('id', 'N/A'),
                    'match_data': match,
                    'result': result
                })
    
    return westham_matches

def determine_result(match, is_home):
    """Determine West Ham's result (W/L/D)"""
    status = match.get('status', '')
    goals = match.get('goals', {})
    winner = match.get('winner', '')
    
    if status not in ['finished']:
        return 'pending'
    
    home_goals = goals.get('home_ft_goals', 0)
    away_goals = goals.get('away_ft_goals', 0)
    
    if is_home:
        westham_goals = home_goals
        opponent_goals = away_goals
    else:
        westham_goals = away_goals
        opponent_goals = home_goals
    
    if westham_goals > opponent_goals:
        return 'W'
    elif westham_goals < opponent_goals:
        return 'L'
    else:
        return 'D'

def main():
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    league_id = 228  # Premier League
    
    # Dates from the West Ham screenshot (DD-MM-YYYY format)
    target_dates = [
        "25-05-2025",  # vs Ipswich Town
        "18-05-2025",  # vs Nottingham Forest  
        "11-05-2025",  # vs Manchester United
        "04-05-2025",  # vs Tottenham Hotspur
        "26-04-2025",  # vs Brighton & Hove Albion
        "19-04-2025",  # vs Southampton
        "13-04-2025",  # vs Liverpool
        "05-04-2025",  # vs AFC Bournemouth
        "01-04-2025",  # vs Wolverhampton Wanderers
    ]
    
    print("="*80)
    print("WEST HAM RECENT MATCHES FINDER")
    print("="*80)
    print("Searching for West Ham matches on specific dates from screenshot...")
    print(f"League: Premier League (ID: {league_id})")
    print(f"Target Team: West Ham United (ID: 3059)")
    print()
    
    all_westham_matches = []
    
    for date in target_dates:
        print(f"Searching {date}...")
        
        match_data = get_matches_by_date(league_id, date, auth_token)
        
        if match_data:
            westham_matches = find_westham_in_matches(match_data, date)
            
            if westham_matches:
                all_westham_matches.extend(westham_matches)
                for wm in westham_matches:
                    venue = "vs" if wm['is_home'] else "@"
                    opponent = wm['opponent']
                    result = wm['result']
                    
                    match = wm['match_data']
                    goals = match.get('goals', {})
                    home_goals = goals.get('home_ft_goals', 0)
                    away_goals = goals.get('away_ft_goals', 0)
                    
                    if wm['is_home']:
                        score = f"{home_goals}-{away_goals}"
                    else:
                        score = f"{away_goals}-{home_goals}"
                    
                    print(f"  FOUND: {date} | {venue} {opponent} | {result} {score}")
            else:
                print(f"  No West Ham match found on {date}")
        else:
            print(f"  Failed to get data for {date}")
    
    print("\n" + "="*80)
    print("WEST HAM RECENT FORM SUMMARY")
    print("="*80)
    
    if all_westham_matches:
        # Sort by date (most recent first)
        all_westham_matches.sort(key=lambda x: datetime.strptime(x['date'], "%d-%m-%Y"), reverse=True)
        
        wins = len([m for m in all_westham_matches if m['result'] == 'W'])
        losses = len([m for m in all_westham_matches if m['result'] == 'L'])
        draws = len([m for m in all_westham_matches if m['result'] == 'D'])
        total = len(all_westham_matches)
        
        print(f"RECENT RECORD ({total} games found):")
        print(f"  Wins: {wins} | Losses: {losses} | Draws: {draws}")
        if total > 0:
            print(f"  Win Rate: {(wins/total*100):.1f}%")
        
        # Show form string
        form_string = ''.join([m['result'] for m in all_westham_matches[:5]])
        print(f"  Last {min(5, total)} Games: {form_string}")
        
        print(f"\nDETAILED RESULTS:")
        print("-" * 60)
        
        for i, wm in enumerate(all_westham_matches[:10], 1):
            venue = "vs" if wm['is_home'] else "@"
            opponent = wm['opponent']
            result = wm['result']
            date = wm['date']
            
            match = wm['match_data']
            goals = match.get('goals', {})
            home_goals = goals.get('home_ft_goals', 0)
            away_goals = goals.get('away_ft_goals', 0)
            
            if wm['is_home']:
                score = f"{home_goals}-{away_goals}"
            else:
                score = f"{away_goals}-{home_goals}"
            
            result_marker = "[W]" if result == 'W' else "[L]" if result == 'L' else "[D]"
            print(f"  {i}. {date} | {venue} {opponent:<18} | {result} {score} {result_marker}")
        
    else:
        print("No West Ham matches found in the searched dates!")
        print("This might indicate:")
        print("- Different date format needed")
        print("- Matches in different league/competition")
        print("- API data not available for these dates")

if __name__ == "__main__":
    main()