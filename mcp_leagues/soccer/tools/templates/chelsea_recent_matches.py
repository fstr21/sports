#!/usr/bin/env python3
"""
Chelsea Recent Matches Finder
Uses the proven date-by-date method to find Chelsea's actual recent matches
Based on the same timeframe as West Ham analysis
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

def find_chelsea_in_matches(match_data, target_date):
    """Find Chelsea matches in the response data"""
    chelsea_matches = []
    
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
        
        # Look for Chelsea (ID: 2916) in matches
        for match in matches:
            teams = match.get('teams', {})
            home_team = teams.get('home', {})
            away_team = teams.get('away', {})
            
            home_id = home_team.get('id')
            away_id = away_team.get('id')
            home_name = home_team.get('name', 'Unknown')
            away_name = away_team.get('name', 'Unknown')
            
            # Check if Chelsea is playing (ID: 2916)
            if home_id == 2916 or away_id == 2916:
                is_home = (home_id == 2916)
                opponent = away_team if is_home else home_team
                
                # Determine result
                result = determine_result(match, is_home)
                
                chelsea_matches.append({
                    'date': target_date,
                    'is_home': is_home,
                    'opponent': opponent.get('name', 'Unknown'),
                    'opponent_id': opponent.get('id', 'N/A'),
                    'match_data': match,
                    'result': result
                })
    
    return chelsea_matches

def determine_result(match, is_home):
    """Determine Chelsea's result (W/L/D)"""
    status = match.get('status', '')
    goals = match.get('goals', {})
    winner = match.get('winner', '')
    
    if status not in ['finished']:
        return 'pending'
    
    home_goals = goals.get('home_ft_goals', 0)
    away_goals = goals.get('away_ft_goals', 0)
    
    if is_home:
        chelsea_goals = home_goals
        opponent_goals = away_goals
    else:
        chelsea_goals = away_goals
        opponent_goals = home_goals
    
    if chelsea_goals > opponent_goals:
        return 'W'
    elif chelsea_goals < opponent_goals:
        return 'L'
    else:
        return 'D'

def generate_date_range():
    """Generate date range for the same period as West Ham analysis"""
    # We'll search April-May 2025 to match West Ham timeframe
    dates = []
    
    # May 2025 dates
    may_dates = [
        "25-05-2025", "24-05-2025", "23-05-2025", "22-05-2025", "21-05-2025",
        "20-05-2025", "19-05-2025", "18-05-2025", "17-05-2025", "16-05-2025",
        "15-05-2025", "14-05-2025", "13-05-2025", "12-05-2025", "11-05-2025",
        "10-05-2025", "09-05-2025", "08-05-2025", "07-05-2025", "06-05-2025",
        "05-05-2025", "04-05-2025", "03-05-2025", "02-05-2025", "01-05-2025"
    ]
    
    # April 2025 dates
    april_dates = [
        "30-04-2025", "29-04-2025", "28-04-2025", "27-04-2025", "26-04-2025",
        "25-04-2025", "24-04-2025", "23-04-2025", "22-04-2025", "21-04-2025",
        "20-04-2025", "19-04-2025", "18-04-2025", "17-04-2025", "16-04-2025",
        "15-04-2025", "14-04-2025", "13-04-2025", "12-04-2025", "11-04-2025",
        "10-04-2025", "09-04-2025", "08-04-2025", "07-04-2025", "06-04-2025",
        "05-04-2025", "04-04-2025", "03-04-2025", "02-04-2025", "01-04-2025"
    ]
    
    # March 2025 dates (last week)
    march_dates = [
        "31-03-2025", "30-03-2025", "29-03-2025", "28-03-2025", "27-03-2025",
        "26-03-2025", "25-03-2025"
    ]
    
    dates.extend(may_dates)
    dates.extend(april_dates)
    dates.extend(march_dates)
    
    return dates

def main():
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    league_id = 228  # Premier League
    
    # Generate date range to search for Chelsea matches
    target_dates = generate_date_range()
    
    print("="*80)
    print("CHELSEA RECENT MATCHES FINDER")
    print("="*80)
    print("Searching for Chelsea matches in April-May 2025...")
    print(f"League: Premier League (ID: {league_id})")
    print(f"Target Team: Chelsea (ID: 2916)")
    print(f"Searching {len(target_dates)} dates...")
    print()
    
    all_chelsea_matches = []
    dates_checked = 0
    
    for date in target_dates:
        dates_checked += 1
        if dates_checked % 10 == 0:
            print(f"Checked {dates_checked} dates... found {len(all_chelsea_matches)} matches so far")
        
        match_data = get_matches_by_date(league_id, date, auth_token)
        
        if match_data:
            chelsea_matches = find_chelsea_in_matches(match_data, date)
            
            if chelsea_matches:
                all_chelsea_matches.extend(chelsea_matches)
                for cm in chelsea_matches:
                    venue = "vs" if cm['is_home'] else "@"
                    opponent = cm['opponent']
                    result = cm['result']
                    
                    match = cm['match_data']
                    goals = match.get('goals', {})
                    home_goals = goals.get('home_ft_goals', 0)
                    away_goals = goals.get('away_ft_goals', 0)
                    
                    if cm['is_home']:
                        score = f"{home_goals}-{away_goals}"
                    else:
                        score = f"{away_goals}-{home_goals}"
                    
                    print(f"  FOUND: {date} | {venue} {opponent} | {result} {score}")
    
    print(f"\nCompleted search of {dates_checked} dates")
    print("\n" + "="*80)
    print("CHELSEA RECENT FORM SUMMARY")
    print("="*80)
    
    if all_chelsea_matches:
        # Sort by date (most recent first)
        all_chelsea_matches.sort(key=lambda x: datetime.strptime(x['date'], "%d-%m-%Y"), reverse=True)
        
        wins = len([m for m in all_chelsea_matches if m['result'] == 'W'])
        losses = len([m for m in all_chelsea_matches if m['result'] == 'L'])
        draws = len([m for m in all_chelsea_matches if m['result'] == 'D'])
        total = len(all_chelsea_matches)
        
        print(f"RECENT RECORD ({total} games found):")
        print(f"  Wins: {wins} | Losses: {losses} | Draws: {draws}")
        if total > 0:
            print(f"  Win Rate: {(wins/total*100):.1f}%")
        
        # Show form string
        form_string = ''.join([m['result'] for m in all_chelsea_matches[:5]])
        print(f"  Last {min(5, total)} Games: {form_string}")
        
        print(f"\nDETAILED RESULTS:")
        print("-" * 60)
        
        for i, cm in enumerate(all_chelsea_matches[:10], 1):
            venue = "vs" if cm['is_home'] else "@"
            opponent = cm['opponent']
            result = cm['result']
            date = cm['date']
            
            match = cm['match_data']
            goals = match.get('goals', {})
            home_goals = goals.get('home_ft_goals', 0)
            away_goals = goals.get('away_ft_goals', 0)
            
            if cm['is_home']:
                score = f"{home_goals}-{away_goals}"
            else:
                score = f"{away_goals}-{home_goals}"
            
            result_marker = "[W]" if result == 'W' else "[L]" if result == 'L' else "[D]"
            print(f"  {i}. {date} | {venue} {opponent:<20} | {result} {score} {result_marker}")
        
    else:
        print("No Chelsea matches found in the searched dates!")
        print("This might indicate:")
        print("- Different date format needed")
        print("- Matches in different league/competition")
        print("- API data not available for these dates")

if __name__ == "__main__":
    main()