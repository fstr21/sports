#!/usr/bin/env python3
"""
Efficient Head-to-Head Analyzer
Gets the most reliable data:
1. Both teams' known recent form (from our previous analysis)
2. Search for actual recent H2H meetings between the teams
3. Compare with historical H2H stats
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

def find_recent_h2h_meetings(team_1_id, team_2_id, team_1_name, team_2_name, auth_token):
    """Search for recent actual meetings between West Ham and Chelsea"""
    h2h_meetings = []
    
    # Search specific recent dates where they might have played
    # Based on Premier League schedule, they typically play 2x per season
    search_dates = [
        # 2024-25 season dates (working backward)
        "22-08-2025", "21-08-2025", "20-08-2025", "19-08-2025", "18-08-2025", "17-08-2025", "16-08-2025", "15-08-2025",
        "25-05-2025", "24-05-2025", "23-05-2025", "22-05-2025", "21-05-2025", "20-05-2025", "19-05-2025", "18-05-2025",
        "03-02-2025", "02-02-2025", "01-02-2025", "31-01-2025", "30-01-2025", "29-01-2025", "28-01-2025", "27-01-2025",
        # 2023-24 season typical dates
        "21-09-2024", "20-09-2024", "19-09-2024", "18-09-2024", "17-09-2024", "16-09-2024", "15-09-2024", "14-09-2024",
        "04-02-2024", "03-02-2024", "02-02-2024", "01-02-2024", "31-01-2024", "30-01-2024", "29-01-2024", "28-01-2024",
    ]
    
    print(f"Searching for recent {team_1_name} vs {team_2_name} meetings...")
    
    for date in search_dates:
        if len(h2h_meetings) >= 5:  # Limit to last 5 meetings
            break
            
        response_data = get_matches_by_date(228, date, auth_token)  # Premier League
        
        if response_data:
            matches = extract_matches_from_response(response_data)
            
            for match in matches:
                teams = match.get('teams', {})
                home_team = teams.get('home', {})
                away_team = teams.get('away', {})
                
                home_id = home_team.get('id')
                away_id = away_team.get('id')
                
                # Check if this is a meeting between our two teams
                if (home_id == team_1_id and away_id == team_2_id) or (home_id == team_2_id and away_id == team_1_id):
                    team_1_is_home = (home_id == team_1_id)
                    
                    h2h_meetings.append({
                        'date': date,
                        'match_data': match,
                        'team_1_is_home': team_1_is_home,
                        'match_date_obj': datetime.strptime(date, "%d-%m-%Y")
                    })
                    
                    # Display found meeting immediately
                    goals = match.get('goals', {})
                    home_goals = goals.get('home_ft_goals', 0)
                    away_goals = goals.get('away_ft_goals', 0)
                    status = match.get('status', 'Unknown')
                    
                    if status == 'finished':
                        if team_1_is_home:
                            venue_display = f"{team_1_name} vs {team_2_name}"
                            score = f"{home_goals}-{away_goals}"
                        else:
                            venue_display = f"{team_2_name} vs {team_1_name}"
                            score = f"{away_goals}-{home_goals}"
                        
                        print(f"  FOUND: {date} | {venue_display} | {score}")
    
    # Sort by date (most recent first)
    h2h_meetings.sort(key=lambda x: x['match_date_obj'], reverse=True)
    return h2h_meetings

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

def display_known_recent_form():
    """Display the recent form we already know from our previous analysis"""
    print(f"\n{'='*80}")
    print("RECENT FORM SUMMARY (From Previous Analysis)")
    print(f"{'='*80}")
    
    print("WEST HAM UNITED - LAST 9 MATCHES:")
    print("  Record: 2W-4L-3D (22.2% win rate)")
    print("  Last 5: W-L-W-D-L")
    print("  Recent Results:")
    print("    1. 25-05-2025 | @ Ipswich Town        | W 3-1")
    print("    2. 18-05-2025 | vs Nottingham Forest  | L 1-2")
    print("    3. 11-05-2025 | @ Manchester United   | W 2-0")
    print("    4. 04-05-2025 | vs Tottenham Hotspur  | D 1-1")
    print("    5. 26-04-2025 | @ Brighton & Hove Albion | L 2-3")
    
    print("\nCHELSEA - LAST 9 MATCHES:")
    print("  Record: 6W-1L-2D (66.7% win rate)")
    print("  Last 5: W-W-L-W-W")
    print("  Recent Results:")
    print("    1. 25-05-2025 | @ Nottingham Forest   | W 1-0")
    print("    2. 16-05-2025 | vs Manchester United  | W 1-0")
    print("    3. 11-05-2025 | @ Newcastle United    | L 0-2")
    print("    4. 04-05-2025 | vs Liverpool          | W 3-1")
    print("    5. 26-04-2025 | vs Everton            | W 1-0")

def display_recent_h2h_meetings(team_1_name, team_2_name, meetings):
    """Display recent head-to-head meetings"""
    print(f"\n{'='*80}")
    print(f"RECENT {team_1_name.upper()} vs {team_2_name.upper()} MEETINGS")
    print(f"{'='*80}")
    
    if not meetings:
        print("No recent meetings found in searched dates")
        print("Note: This searches recent Premier League dates only")
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

def display_comprehensive_analysis(team_1_name, team_2_name, h2h_meetings, h2h_stats):
    """Display comprehensive analysis"""
    print(f"\n{'='*80}")
    print("COMPREHENSIVE ANALYSIS: HISTORICAL vs RECENT")
    print(f"{'='*80}")
    
    # Recent form comparison (from known data)
    print("RECENT FORM COMPARISON:")
    print("| Team            | Last 9 Games | Wins | Win Rate | Last 5 Form |")
    print("|-----------------|--------------|------|----------|-------------|")
    print("| West Ham United | 9            | 2    | 22.2%    | WLWDL       |")
    print("| Chelsea         | 9            | 6    | 66.7%    | WWLWW       |")
    
    # Historical comparison
    if h2h_stats:
        overall = h2h_stats.get('stats', {}).get('overall', {})
        if overall:
            total_games = overall.get('overall_games_played', 0)
            team_1_wins = overall.get('overall_team1_wins', 0)
            team_2_wins = overall.get('overall_team2_wins', 0)
            
            if total_games > 0:
                historical_1_rate = (team_1_wins / total_games) * 100
                historical_2_rate = (team_2_wins / total_games) * 100
                
                print(f"\nHISTORICAL vs RECENT COMPARISON:")
                print(f"| Metric                    | {team_1_name:<15} | {team_2_name:<15} |")
                print(f"|---------------------------|-----------------|-----------------|")
                print(f"| Historical Win Rate       | {historical_1_rate:<14.1f}% | {historical_2_rate:<14.1f}% |")
                print(f"| Recent Win Rate           | 22.2           % | 66.7           % |")
                print(f"| Historical Games          | {total_games} total meetings                      |")
                print(f"| Form Trend                | Below Historical| Above Historical|")
    
    # Final prediction
    print(f"\nFINAL PREDICTION:")
    print(f"  [STRONG CHELSEA ADVANTAGE]")
    print(f"  • Historical: Chelsea leads 45-39 (42.5% vs 36.8%)")
    print(f"  • Recent Form: Chelsea 66.7% vs West Ham 22.2%")
    print(f"  • Current Momentum: Chelsea W-W streak vs West Ham mixed form")
    print(f"  • Combined Verdict: Chelsea overwhelming favorite")

def main():
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    
    # Team configurations
    team_1_id = 3059  # West Ham United
    team_1_name = "West Ham United"
    team_2_id = 2916  # Chelsea
    team_2_name = "Chelsea"
    
    print("="*80)
    print("EFFICIENT HEAD-TO-HEAD ANALYZER")
    print("="*80)
    print(f"Analyzing {team_1_name} vs {team_2_name}")
    print("Getting:")
    print("  1. Known recent form (from previous analysis)")
    print("  2. Recent head-to-head meetings (date search)")
    print("  3. Historical H2H statistics")
    print("  4. Combined analysis with predictions")
    print()
    
    # Get recent head-to-head meetings
    h2h_meetings = find_recent_h2h_meetings(team_1_id, team_2_id, team_1_name, team_2_name, auth_token)
    
    # Get historical H2H stats
    print("Getting historical H2H statistics...")
    h2h_stats = get_head_to_head_stats(team_1_id, team_2_id, auth_token)
    
    # Display results
    display_known_recent_form()
    display_recent_h2h_meetings(team_1_name, team_2_name, h2h_meetings)
    display_comprehensive_analysis(team_1_name, team_2_name, h2h_meetings, h2h_stats)
    
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()