#!/usr/bin/env python3
"""
Check if we can get recent form data for teams
Tests different approaches to get recent match results
"""

import requests
import json
from datetime import datetime, timedelta

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
        return response.json()
    except Exception as e:
        print(f"Team API error: {e}")
        return None

def get_recent_matches_by_date_range(league_id, auth_token, days_back=30):
    """Try to get recent matches by searching date ranges"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    matches_found = []
    
    # Check last 30 days
    for i in range(days_back):
        check_date = (end_date - timedelta(days=i)).strftime("%d-%m-%Y")
        
        url = "https://api.soccerdataapi.com/matches/"
        querystring = {'league_id': league_id, 'date': check_date, 'auth_token': auth_token}
        headers = {
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, params=querystring)
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list):
                    for league_data in data:
                        if isinstance(league_data, dict) and 'matches' in league_data:
                            for match in league_data['matches']:
                                teams = match.get('teams', {})
                                home_id = teams.get('home', {}).get('id')
                                away_id = teams.get('away', {}).get('id')
                                
                                # Check if West Ham or Chelsea played
                                if home_id in [3059, 2916] or away_id in [3059, 2916]:
                                    matches_found.append({
                                        'date': check_date,
                                        'match': match
                                    })
        except Exception as e:
            continue
    
    return matches_found

def analyze_form_capability():
    """Analyze what form data we can extract"""
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    
    print("="*80)
    print("RECENT FORM DATA ANALYSIS")
    print("="*80)
    
    # Test team endpoint for West Ham and Chelsea
    print("1. TESTING TEAM ENDPOINT:")
    print("-" * 30)
    
    west_ham_data = get_team_info(3059, auth_token)
    chelsea_data = get_team_info(2916, auth_token)
    
    if west_ham_data:
        print("West Ham team data structure:")
        print(json.dumps(west_ham_data, indent=2)[:500] + "...")
        print()
    
    if chelsea_data:
        print("Chelsea team data structure:")  
        print(json.dumps(chelsea_data, indent=2)[:500] + "...")
        print()
    
    # Test recent matches by date range
    print("2. TESTING RECENT MATCHES VIA DATE SEARCH:")
    print("-" * 45)
    
    recent_matches = get_recent_matches_by_date_range(228, auth_token, 10)  # Last 10 days
    
    if recent_matches:
        print(f"Found {len(recent_matches)} recent matches involving West Ham or Chelsea:")
        for i, match_info in enumerate(recent_matches[:3], 1):
            match = match_info['match']
            date = match_info['date']
            teams = match.get('teams', {})
            home_name = teams.get('home', {}).get('name', 'Unknown')
            away_name = teams.get('away', {}).get('name', 'Unknown')
            status = match.get('status', 'Unknown')
            
            print(f"  {i}. {date}: {home_name} vs {away_name} ({status})")
    else:
        print("No recent matches found")
    
    print("\n3. FORM DATA CONCLUSIONS:")
    print("-" * 25)
    print("• Head-to-head endpoint: Historical data only (no recent form)")
    print("• Team endpoint: Need to check if it includes recent matches")
    print("• Match search by date: Can find recent games but requires date iteration")
    print("• Best approach: Search recent dates for team-specific matches")

def main():
    analyze_form_capability()

if __name__ == "__main__":
    main()