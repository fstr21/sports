#!/usr/bin/env python3
"""
Recent Form Analyzer
Searches recent matches for specific teams and analyzes their current form
"""

import requests
import json
from datetime import datetime, timedelta

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

def get_recent_team_matches(team_id, team_name, league_ids, auth_token, days_back=60):
    """Get recent matches for a specific team"""
    team_matches = []
    end_date = datetime.now()
    
    print(f"Searching last {days_back} days for {team_name} matches...")
    
    for i in range(days_back):
        search_date = (end_date - timedelta(days=i)).strftime("%d-%m-%Y")
        
        for league_id in league_ids:
            response_data = get_matches_by_date(league_id, search_date, auth_token)
            
            if response_data:
                matches = extract_matches_from_response(response_data)
                
                for match in matches:
                    teams = match.get('teams', {})
                    home_team = teams.get('home', {})
                    away_team = teams.get('away', {})
                    
                    home_id = home_team.get('id')
                    away_id = away_team.get('id')
                    
                    if home_id == team_id or away_id == team_id:
                        # Determine if team was home or away
                        is_home = (home_id == team_id)
                        opponent = away_team if is_home else home_team
                        
                        # Get match result for this team
                        match_result = analyze_match_result(match, team_id, is_home)
                        
                        team_matches.append({
                            'date': search_date,
                            'match_data': match,
                            'is_home': is_home,
                            'opponent': opponent,
                            'result': match_result,
                            'match_date_obj': datetime.strptime(search_date, "%d-%m-%Y")
                        })
    
    # Sort by date (most recent first)
    team_matches.sort(key=lambda x: x['match_date_obj'], reverse=True)
    return team_matches[:10]  # Return last 10 matches

def analyze_match_result(match, team_id, is_home):
    """Analyze match result for specific team"""
    status = match.get('status', '')
    goals = match.get('goals', {})
    winner = match.get('winner', '')
    
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

def calculate_form_stats(matches):
    """Calculate form statistics"""
    if not matches:
        return {}
    
    finished_matches = [m for m in matches if m['result'] in ['W', 'L', 'D']]
    
    if not finished_matches:
        return {'total_games': 0}
    
    wins = len([m for m in finished_matches if m['result'] == 'W'])
    losses = len([m for m in finished_matches if m['result'] == 'L'])
    draws = len([m for m in finished_matches if m['result'] == 'D'])
    
    total_games = len(finished_matches)
    win_rate = (wins / total_games * 100) if total_games > 0 else 0
    
    # Calculate recent form (last 5 games)
    recent_5 = finished_matches[:5]
    recent_form = ''.join([m['result'] for m in recent_5])
    
    return {
        'total_games': total_games,
        'wins': wins,
        'losses': losses,
        'draws': draws,
        'win_rate': win_rate,
        'recent_form': recent_form,
        'recent_games_count': len(recent_5)
    }

def display_team_form(team_name, matches, stats):
    """Display team form in a nice format"""
    print(f"\n{'='*60}")
    print(f"{team_name.upper()} - RECENT FORM ANALYSIS")
    print(f"{'='*60}")
    
    if stats.get('total_games', 0) == 0:
        print("No recent finished matches found")
        return
    
    # Form overview
    print(f"RECENT RECORD (Last {stats['total_games']} games):")
    print(f"  Wins: {stats['wins']} | Losses: {stats['losses']} | Draws: {stats['draws']}")
    print(f"  Win Rate: {stats['win_rate']:.1f}%")
    print(f"  Last 5 Games: {stats['recent_form']} (W=Win, L=Loss, D=Draw)")
    
    # Recent matches details
    print(f"\nRECENT MATCH RESULTS:")
    print("-" * 60)
    
    finished_matches = [m for m in matches if m['result'] in ['W', 'L', 'D']][:8]
    
    for i, match in enumerate(finished_matches, 1):
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
        
        result_emoji = "[W]" if result == 'W' else "[L]" if result == 'L' else "[D]"
        
        print(f"  {i}. {date} | {venue} {opponent_name:<15} | {result} {score} {result_emoji}")

def compare_recent_forms(team1_name, team1_stats, team2_name, team2_stats):
    """Compare recent forms between two teams"""
    print(f"\n{'='*80}")
    print("RECENT FORM COMPARISON")
    print(f"{'='*80}")
    
    if team1_stats.get('total_games', 0) == 0 or team2_stats.get('total_games', 0) == 0:
        print("Insufficient data for comparison")
        return
    
    print(f"| Metric           | {team1_name:<15} | {team2_name:<15} | Advantage       |")
    print("|" + "-"*18 + "|" + "-"*17 + "|" + "-"*17 + "|" + "-"*17 + "|")
    
    print(f"| Recent Games     | {team1_stats['total_games']:<15} | {team2_stats['total_games']:<15} | -               |")
    print(f"| Wins             | {team1_stats['wins']:<15} | {team2_stats['wins']:<15} | {team1_name if team1_stats['wins'] > team2_stats['wins'] else team2_name if team2_stats['wins'] > team1_stats['wins'] else 'Even':<15} |")
    print(f"| Win Rate         | {team1_stats['win_rate']:<14.1f}% | {team2_stats['win_rate']:<14.1f}% | {team1_name if team1_stats['win_rate'] > team2_stats['win_rate'] else team2_name if team2_stats['win_rate'] > team1_stats['win_rate'] else 'Even':<15} |")
    print(f"| Last 5 Form      | {team1_stats['recent_form']:<15} | {team2_stats['recent_form']:<15} | -               |")
    
    # Form momentum analysis
    team1_recent_wins = team1_stats['recent_form'].count('W')
    team2_recent_wins = team2_stats['recent_form'].count('W')
    
    print(f"| Last 5 Wins      | {team1_recent_wins:<15} | {team2_recent_wins:<15} | {team1_name if team1_recent_wins > team2_recent_wins else team2_name if team2_recent_wins > team1_recent_wins else 'Even':<15} |")
    
    print("\nFORM MOMENTUM:")
    if team1_stats['win_rate'] > team2_stats['win_rate'] + 10:
        print(f"  [UP] {team1_name} has significantly better recent form")
    elif team2_stats['win_rate'] > team1_stats['win_rate'] + 10:
        print(f"  [UP] {team2_name} has significantly better recent form")
    else:
        print(f"  [EVEN] Both teams have similar recent form")

def main():
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    
    # Team configurations
    teams = {
        'West Ham United': {'id': 3059},
        'Chelsea': {'id': 2916}
    }
    
    # League IDs to search (Premier League primarily)
    league_ids = [228]  # Premier League
    
    print("="*80)
    print("RECENT FORM ANALYZER")
    print("="*80)
    print("Analyzing recent form for West Ham United vs Chelsea...")
    print("This may take a moment as we search recent match data...")
    
    team_forms = {}
    
    # Get recent matches for both teams
    for team_name, team_info in teams.items():
        team_id = team_info['id']
        
        recent_matches = get_recent_team_matches(team_id, team_name, league_ids, auth_token, days_back=90)
        form_stats = calculate_form_stats(recent_matches)
        
        team_forms[team_name] = {
            'matches': recent_matches,
            'stats': form_stats
        }
        
        display_team_form(team_name, recent_matches, form_stats)
    
    # Compare forms
    if len(team_forms) == 2:
        team_names = list(team_forms.keys())
        compare_recent_forms(
            team_names[0], team_forms[team_names[0]]['stats'],
            team_names[1], team_forms[team_names[1]]['stats']
        )
    
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()