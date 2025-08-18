#!/usr/bin/env python3
"""
Comprehensive Head-to-Head Analyzer
Gets:
1. Both teams' last 10 individual matches (recent form)
2. Their actual recent head-to-head meetings (last 5 encounters)
3. Historical H2H statistics
4. Combined analysis with predictions
"""

import requests
import json
from datetime import datetime, timedelta
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
        return response.json()
    except Exception as e:
        return None

def get_head_to_head_stats(team_1_id, team_2_id, auth_token):
    """Get historical H2H statistics from SoccerDataAPI"""
    url = "https://api.soccerdataapi.com/head-to-head/"
    querystring = {'team_1_id': team_1_id, 'team_2_id': team_2_id, 'auth_token': auth_token}
    headers = {
        'Accept-Encoding': 'gzip',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None

def find_team_matches(team_id, team_name, league_ids, auth_token, days_back=120, max_matches=10):
    """Find a team's recent matches"""
    team_matches = []
    end_date = datetime.now()
    
    print(f"Searching {team_name} matches (last {days_back} days, max {max_matches} matches)...")
    
    for i in range(days_back):
        if len(team_matches) >= max_matches:
            break
            
        search_date = (end_date - timedelta(days=i)).strftime("%d-%m-%Y")
        
        for league_id in league_ids:
            if len(team_matches) >= max_matches:
                break
                
            response_data = get_matches_by_date(league_id, search_date, auth_token)
            
            if response_data:
                matches = extract_matches_from_response(response_data)
                
                for match in matches:
                    if len(team_matches) >= max_matches:
                        break
                        
                    teams = match.get('teams', {})
                    home_team = teams.get('home', {})
                    away_team = teams.get('away', {})
                    
                    home_id = home_team.get('id')
                    away_id = away_team.get('id')
                    
                    if home_id == team_id or away_id == team_id:
                        is_home = (home_id == team_id)
                        opponent = away_team if is_home else home_team
                        result = analyze_match_result(match, team_id, is_home)
                        
                        team_matches.append({
                            'date': search_date,
                            'match_data': match,
                            'is_home': is_home,
                            'opponent': opponent,
                            'result': result,
                            'match_date_obj': datetime.strptime(search_date, "%d-%m-%Y")
                        })
    
    # Sort by date (most recent first)
    team_matches.sort(key=lambda x: x['match_date_obj'], reverse=True)
    return team_matches[:max_matches]

def find_recent_h2h_meetings(team_1_id, team_2_id, team_1_name, team_2_name, league_ids, auth_token, days_back=365, max_meetings=5):
    """Find actual recent head-to-head meetings between the two teams"""
    h2h_meetings = []
    end_date = datetime.now()
    
    print(f"Searching recent {team_1_name} vs {team_2_name} meetings (last {days_back} days, max {max_meetings} meetings)...")
    
    for i in range(days_back):
        if len(h2h_meetings) >= max_meetings:
            break
            
        search_date = (end_date - timedelta(days=i)).strftime("%d-%m-%Y")
        
        for league_id in league_ids:
            if len(h2h_meetings) >= max_meetings:
                break
                
            response_data = get_matches_by_date(league_id, search_date, auth_token)
            
            if response_data:
                matches = extract_matches_from_response(response_data)
                
                for match in matches:
                    if len(h2h_meetings) >= max_meetings:
                        break
                        
                    teams = match.get('teams', {})
                    home_team = teams.get('home', {})
                    away_team = teams.get('away', {})
                    
                    home_id = home_team.get('id')
                    away_id = away_team.get('id')
                    
                    # Check if this is a meeting between our two teams
                    if (home_id == team_1_id and away_id == team_2_id) or (home_id == team_2_id and away_id == team_1_id):
                        team_1_is_home = (home_id == team_1_id)
                        
                        h2h_meetings.append({
                            'date': search_date,
                            'match_data': match,
                            'team_1_is_home': team_1_is_home,
                            'match_date_obj': datetime.strptime(search_date, "%d-%m-%Y")
                        })
    
    # Sort by date (most recent first)
    h2h_meetings.sort(key=lambda x: x['match_date_obj'], reverse=True)
    return h2h_meetings[:max_meetings]

def extract_matches_from_response(response_data):
    """Extract matches from API response"""
    matches = []
    if not response_data or not isinstance(response_data, list):
        return matches
    
    for league_data in response_data:
        if isinstance(league_data, dict):
            if 'matches' in league_data:
                matches.extend(league_data['matches'])
            elif 'stage' in league_data:
                for stage in league_data['stage']:
                    if 'matches' in stage:
                        matches.extend(stage['matches'])
    return matches

def analyze_match_result(match, team_id, is_home):
    """Analyze match result for specific team"""
    status = match.get('status', '')
    goals = match.get('goals', {})
    
    if status not in ['finished']:
        return 'pending'
    
    home_goals = goals.get('home_ft_goals', 0)
    away_goals = goals.get('away_ft_goals', 0)
    
    if is_home:
        team_goals = home_goals
        opponent_goals = away_goals
    else:
        team_goals = away_goals
        opponent_goals = home_goals
    
    if team_goals > opponent_goals:
        return 'W'
    elif team_goals < opponent_goals:
        return 'L'
    else:
        return 'D'

def display_team_recent_form(team_name, matches):
    """Display team's recent form"""
    print(f"\n{'='*60}")
    print(f"{team_name.upper()} - LAST {len(matches)} MATCHES")
    print(f"{'='*60}")
    
    if not matches:
        print("No recent matches found")
        return
    
    # Calculate stats
    finished_matches = [m for m in matches if m['result'] in ['W', 'L', 'D']]
    wins = len([m for m in finished_matches if m['result'] == 'W'])
    losses = len([m for m in finished_matches if m['result'] == 'L'])
    draws = len([m for m in finished_matches if m['result'] == 'D'])
    total = len(finished_matches)
    
    if total > 0:
        win_rate = (wins / total) * 100
        form_string = ''.join([m['result'] for m in finished_matches[:5]])
        
        print(f"FORM SUMMARY:")
        print(f"  Record: {wins}W-{losses}L-{draws}D ({win_rate:.1f}% win rate)")
        print(f"  Last 5: {form_string}")
        print()
    
    print("RECENT MATCHES:")
    print("-" * 60)
    
    for i, match in enumerate(finished_matches[:10], 1):
        match_data = match['match_data']
        opponent = match['opponent']
        
        date = match['date']
        opponent_name = opponent.get('name', 'Unknown')
        venue = "vs" if match['is_home'] else "@"
        result = match['result']
        
        goals = match_data.get('goals', {})
        home_goals = goals.get('home_ft_goals', 0)
        away_goals = goals.get('away_ft_goals', 0)
        
        if match['is_home']:
            score = f"{home_goals}-{away_goals}"
        else:
            score = f"{away_goals}-{home_goals}"
        
        result_marker = "[W]" if result == 'W' else "[L]" if result == 'L' else "[D]"
        print(f"  {i:2}. {date} | {venue} {opponent_name:<18} | {result} {score} {result_marker}")

def display_recent_h2h_meetings(team_1_name, team_2_name, meetings):
    """Display recent head-to-head meetings"""
    print(f"\n{'='*80}")
    print(f"RECENT {team_1_name.upper()} vs {team_2_name.upper()} MEETINGS")
    print(f"{'='*80}")
    
    if not meetings:
        print("No recent meetings found")
        return
    
    print(f"LAST {len(meetings)} HEAD-TO-HEAD MEETINGS:")
    print("-" * 80)
    
    team_1_wins = 0
    team_2_wins = 0
    draws = 0
    
    for i, meeting in enumerate(meetings, 1):
        match_data = meeting['match_data']
        date = meeting['date']
        team_1_is_home = meeting['team_1_is_home']
        
        goals = match_data.get('goals', {})
        home_goals = goals.get('home_ft_goals', 0)
        away_goals = goals.get('away_ft_goals', 0)
        status = match_data.get('status', 'Unknown')
        
        if status == 'finished':
            if team_1_is_home:
                team_1_goals = home_goals
                team_2_goals = away_goals
                venue_display = f"{team_1_name} vs {team_2_name}"
            else:
                team_1_goals = away_goals
                team_2_goals = home_goals
                venue_display = f"{team_2_name} vs {team_1_name}"
            
            # Determine winner
            if team_1_goals > team_2_goals:
                winner = team_1_name
                team_1_wins += 1
                result_marker = f"[{team_1_name} WIN]"
            elif team_2_goals > team_1_goals:
                winner = team_2_name
                team_2_wins += 1
                result_marker = f"[{team_2_name} WIN]"
            else:
                winner = "Draw"
                draws += 1
                result_marker = "[DRAW]"
            
            score = f"{team_1_goals}-{team_2_goals}" if team_1_is_home else f"{team_2_goals}-{team_1_goals}"
            
            print(f"  {i}. {date} | {venue_display:<30} | {score} {result_marker}")
        else:
            print(f"  {i}. {date} | Match not finished ({status})")
    
    if team_1_wins + team_2_wins + draws > 0:
        print(f"\nRECENT H2H RECORD:")
        print(f"  {team_1_name}: {team_1_wins} wins")
        print(f"  {team_2_name}: {team_2_wins} wins") 
        print(f"  Draws: {draws}")

def display_comprehensive_analysis(team_1_name, team_1_matches, team_2_name, team_2_matches, h2h_meetings, h2h_stats):
    """Display comprehensive analysis combining all data"""
    print(f"\n{'='*80}")
    print("COMPREHENSIVE HEAD-TO-HEAD ANALYSIS")
    print(f"{'='*80}")
    
    # Recent form comparison
    team_1_finished = [m for m in team_1_matches if m['result'] in ['W', 'L', 'D']]
    team_2_finished = [m for m in team_2_matches if m['result'] in ['W', 'L', 'D']]
    
    team_1_wins = len([m for m in team_1_finished if m['result'] == 'W'])
    team_2_wins = len([m for m in team_2_finished if m['result'] == 'W'])
    
    team_1_rate = (team_1_wins / len(team_1_finished) * 100) if team_1_finished else 0
    team_2_rate = (team_2_wins / len(team_2_finished) * 100) if team_2_finished else 0
    
    print("RECENT FORM COMPARISON (Last 10 games):")
    print(f"| Team              | Games | Wins | Win Rate | Last 5 Form |")
    print(f"|-------------------|-------|------|----------|-------------|")
    
    team_1_form = ''.join([m['result'] for m in team_1_finished[:5]])
    team_2_form = ''.join([m['result'] for m in team_2_finished[:5]])
    
    print(f"| {team_1_name:<17} | {len(team_1_finished):<5} | {team_1_wins:<4} | {team_1_rate:<7.1f}% | {team_1_form:<11} |")
    print(f"| {team_2_name:<17} | {len(team_2_finished):<5} | {team_2_wins:<4} | {team_2_rate:<7.1f}% | {team_2_form:<11} |")
    
    # Historical vs Recent comparison
    if h2h_stats:
        overall = h2h_stats.get('stats', {}).get('overall', {})
        if overall:
            historical_1_rate = (overall.get('overall_team1_wins', 0) / overall.get('overall_games_played', 1)) * 100
            historical_2_rate = (overall.get('overall_team2_wins', 0) / overall.get('overall_games_played', 1)) * 100
            
            print(f"\nHISTORICAL vs RECENT FORM:")
            print(f"| Metric                    | {team_1_name:<15} | {team_2_name:<15} |")
            print(f"|---------------------------|-----------------|-----------------|")
            print(f"| Historical Win Rate       | {historical_1_rate:<14.1f}% | {historical_2_rate:<14.1f}% |")
            print(f"| Recent Win Rate (10 games)| {team_1_rate:<14.1f}% | {team_2_rate:<14.1f}% |")
            print(f"| Form vs History           | {'+' if team_1_rate > historical_1_rate else '-'}{abs(team_1_rate - historical_1_rate):<13.1f}% | {'+' if team_2_rate > historical_2_rate else '-'}{abs(team_2_rate - historical_2_rate):<13.1f}% |")
    
    # Prediction
    print(f"\nPREDICTION ANALYSIS:")
    if team_1_rate > team_2_rate + 10:
        print(f"  [STRONG] {team_1_name} favored based on recent form ({team_1_rate:.1f}% vs {team_2_rate:.1f}%)")
    elif team_2_rate > team_1_rate + 10:
        print(f"  [STRONG] {team_2_name} favored based on recent form ({team_2_rate:.1f}% vs {team_1_rate:.1f}%)")
    else:
        print(f"  [CLOSE] Evenly matched based on recent form ({team_1_rate:.1f}% vs {team_2_rate:.1f}%)")

def main():
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    league_ids = [228]  # Premier League
    
    # Team configurations
    team_1_id = 3059  # West Ham United
    team_1_name = "West Ham United"
    team_2_id = 2916  # Chelsea
    team_2_name = "Chelsea"
    
    print("="*80)
    print("COMPREHENSIVE HEAD-TO-HEAD ANALYZER")
    print("="*80)
    print(f"Analyzing {team_1_name} vs {team_2_name}")
    print("Getting:")
    print("  1. Both teams' last 10 matches (recent form)")
    print("  2. Their recent head-to-head meetings")
    print("  3. Historical H2H statistics")
    print("  4. Combined analysis with predictions")
    print()
    
    # Get each team's recent matches
    team_1_matches = find_team_matches(team_1_id, team_1_name, league_ids, auth_token, days_back=120, max_matches=10)
    team_2_matches = find_team_matches(team_2_id, team_2_name, league_ids, auth_token, days_back=120, max_matches=10)
    
    # Get recent head-to-head meetings
    h2h_meetings = find_recent_h2h_meetings(team_1_id, team_2_id, team_1_name, team_2_name, league_ids, auth_token, days_back=730, max_meetings=5)
    
    # Get historical H2H stats
    h2h_stats = get_head_to_head_stats(team_1_id, team_2_id, auth_token)
    
    # Display results
    display_team_recent_form(team_1_name, team_1_matches)
    display_team_recent_form(team_2_name, team_2_matches)
    display_recent_h2h_meetings(team_1_name, team_2_name, h2h_meetings)
    display_comprehensive_analysis(team_1_name, team_1_matches, team_2_name, team_2_matches, h2h_meetings, h2h_stats)
    
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()