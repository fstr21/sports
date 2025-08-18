#!/usr/bin/env python3
"""
Interactive Multi-League Match Finder
Prompts user for a date and fetches matches for EPL, La Liga, and MLS
"""

import requests
import json
from datetime import datetime
import os

# League configurations
LEAGUES = {
    'EPL': {
        'id': 228,
        'name': 'Premier League',
        'country': 'England'
    },
    'La Liga': {
        'id': 297,
        'name': 'La Liga',
        'country': 'Spain'
    },
    'MLS': {
        'id': 168,
        'name': 'Major League Soccer',
        'country': 'USA'
    }
}

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
        print(f"ERROR - API request failed: {e}")
        return None
    except ValueError as e:
        print(f"ERROR - JSON parsing failed: {e}")
        return None

def validate_date_format(date_string):
    """Validate and convert date to DD-MM-YYYY format"""
    formats_to_try = [
        "%d-%m-%Y",    # DD-MM-YYYY (API format)
        "%d/%m/%Y",    # DD/MM/YYYY
        "%Y-%m-%d",    # YYYY-MM-DD
        "%m/%d/%Y",    # MM/DD/YYYY
        "%d-%m-%y",    # DD-MM-YY
        "%d/%m/%y",    # DD/MM/YY
    ]
    
    for date_format in formats_to_try:
        try:
            parsed_date = datetime.strptime(date_string, date_format)
            # Convert to API format (DD-MM-YYYY)
            return parsed_date.strftime("%d-%m-%Y")
        except ValueError:
            continue
    
    return None

def extract_matches_from_response(response_data):
    """Extract matches from API response handling different structures"""
    matches = []
    
    if not response_data:
        return matches
    
    if isinstance(response_data, list):
        for league_data in response_data:
            if isinstance(league_data, dict):
                # Check for matches in main structure
                if 'matches' in league_data:
                    matches.extend(league_data['matches'])
                # Check for matches in stages
                elif 'stage' in league_data:
                    stages = league_data['stage']
                    for stage in stages:
                        if 'matches' in stage:
                            matches.extend(stage['matches'])
    
    return matches

def display_league_matches(league_name, league_country, matches, date):
    """Display matches for a specific league"""
    print(f"\n{'='*60}")
    print(f"{league_name} ({league_country}) - {date}")
    print(f"{'='*60}")
    
    if not matches:
        print("No matches found for this date")
        return
    
    print(f"Found {len(matches)} match(es)")
    print("-" * 60)
    
    for i, match in enumerate(matches, 1):
        match_id = match.get('id', 'N/A')
        match_date = match.get('date', 'N/A')
        match_time = match.get('time', 'N/A')
        status = match.get('status', 'N/A')
        winner = match.get('winner', 'tbd')
        
        teams = match.get('teams', {})
        home_team = teams.get('home', {})
        away_team = teams.get('away', {})
        
        home_name = home_team.get('name', 'TBD')
        away_name = away_team.get('name', 'TBD')
        home_id = home_team.get('id', 'N/A')
        away_id = away_team.get('id', 'N/A')
        
        print(f"Match #{i} (ID: {match_id})")
        print(f"  Home: {home_name} (ID: {home_id})")
        print(f"  Away: {away_name} (ID: {away_id})")
        print(f"  Date: {match_date} at {match_time}")
        print(f"  Status: {status}")
        
        # Show score if available
        goals = match.get('goals', {})
        if goals and status in ['finished', 'live']:
            home_goals = goals.get('home_ft_goals', 0)
            away_goals = goals.get('away_ft_goals', 0)
            
            if home_goals >= 0 and away_goals >= 0:
                print(f"  Score: {home_goals} - {away_goals}")
                
                if winner == 'home':
                    print(f"  Winner: {home_name}")
                elif winner == 'away':
                    print(f"  Winner: {away_name}")
                elif winner == 'draw':
                    print(f"  Result: Draw")
        
        # Show odds if available
        odds = match.get('odds', {})
        
        # Match winner odds (1X2)
        match_winner_odds = odds.get('match_winner', {})
        if match_winner_odds:
            home_odds = match_winner_odds.get('home')
            draw_odds = match_winner_odds.get('draw')
            away_odds = match_winner_odds.get('away')
            
            if home_odds and draw_odds and away_odds:
                print(f"  Match Winner: H:{home_odds} D:{draw_odds} A:{away_odds}")
        
        # Over/Under odds
        over_under_odds = odds.get('over_under', {})
        if over_under_odds:
            over_odds = over_under_odds.get('over')
            under_odds = over_under_odds.get('under')
            total = over_under_odds.get('total')
            
            if over_odds and under_odds:
                total_str = f" ({total})" if total else ""
                print(f"  Over/Under{total_str}: O:{over_odds} U:{under_odds}")
        
        # Handicap odds
        handicap_odds = odds.get('handicap', {})
        if handicap_odds:
            home_handicap = handicap_odds.get('home')
            away_handicap = handicap_odds.get('away')
            market = handicap_odds.get('market')
            
            if home_handicap and away_handicap:
                market_str = f" ({market})" if market else ""
                print(f"  Handicap{market_str}: H:{home_handicap} A:{away_handicap}")
        
        print()

def save_all_data(all_data, date, output_dir):
    """Save all match data to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    date_clean = date.replace("-", "_")
    filename = f"multi_league_matches_{date_clean}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        print(f"All data saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"ERROR - Failed to save file: {e}")
        return None

def get_head_to_head(team_1_id, team_2_id, auth_token):
    """Get head-to-head statistics from SoccerDataAPI"""
    
    url = "https://api.soccerdataapi.com/head-to-head/"
    querystring = {'team_1_id': team_1_id, 'team_2_id': team_2_id, 'auth_token': auth_token}
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
        print(f"ERROR - H2H API request failed: {e}")
        return None
    except ValueError as e:
        print(f"ERROR - H2H JSON parsing failed: {e}")
        return None

def display_head_to_head_summary(h2h_data, team_1_name, team_2_name):
    """Display head-to-head summary in beautiful table format"""
    print(f"\n[FIGHT] {team_1_name} vs {team_2_name} Head-to-Head Summary Table")
    print()
    
    if not h2h_data:
        print("No head-to-head data available")
        return
    
    team1 = h2h_data.get('team1', {})
    team2 = h2h_data.get('team2', {})
    stats = h2h_data.get('stats', {})
    overall = stats.get('overall', {})
    team1_home = stats.get('team1_at_home', {})
    team2_home = stats.get('team2_at_home', {})
    
    if not overall:
        print("No overall statistics available")
        return
    
    total_games = overall.get('overall_games_played', 0)
    team1_wins = overall.get('overall_team1_wins', 0)
    team2_wins = overall.get('overall_team2_wins', 0)
    draws = overall.get('overall_draws', 0)
    team1_scored = overall.get('overall_team1_scored', 0)
    team2_scored = overall.get('overall_team2_scored', 0)
    
    if total_games == 0:
        print("No historical matches found")
        return
    
    # Calculate percentages
    team1_pct = (team1_wins / total_games) * 100
    team2_pct = (team2_wins / total_games) * 100
    draws_pct = (draws / total_games) * 100
    team1_goals_per_game = team1_scored / total_games
    team2_goals_per_game = team2_scored / total_games
    avg_goals = (team1_scored + team2_scored) / total_games
    
    print("[CHART] Overall Historical Record")
    print()
    print("| Metric         | " + f"{team_1_name:<10}" + " | " + f"{team_2_name:<10}" + " | Draws |")
    print("|" + "-"*16 + "|" + "-"*12 + "|" + "-"*12 + "|" + "-"*7 + "|")
    print(f"| Total Wins     | {team1_wins:<10} | {team2_wins:<10} | {draws:<5} |")
    print(f"| Win Percentage | {team1_pct:<9.1f}% | {team2_pct:<9.1f}% | {draws_pct:<4.1f}% |")
    print(f"| Goals Scored   | {team1_scored:<10} | {team2_scored:<10} | -     |")
    print(f"| Goals Per Game | {team1_goals_per_game:<10.2f} | {team2_goals_per_game:<10.2f} | -     |")
    print()
    
    # Home vs Away Performance
    if team1_home and team2_home:
        print("---")
        print("[HOME] Home vs Away Performance")
        print()
        print("When Playing at Home:")
        print()
        
        team1_home_games = team1_home.get('team1_games_played_at_home', 0)
        team1_home_wins = team1_home.get('team1_wins_at_home', 0)
        team1_home_losses = team1_home.get('team1_losses_at_home', 0)
        team1_home_draws = team1_home.get('team1_draws_at_home', 0)
        team1_home_scored = team1_home.get('team1_scored_at_home', 0)
        team1_home_conceded = team1_home.get('team1_conceded_at_home', 0)
        
        team2_home_games = team2_home.get('team2_games_played_at_home', 0)
        team2_home_wins = team2_home.get('team2_wins_at_home', 0)
        team2_home_losses = team2_home.get('team2_losses_at_home', 0)
        team2_home_draws = team2_home.get('team2_draws_at_home', 0)
        team2_home_scored = team2_home.get('team2_scored_at_home', 0)
        team2_home_conceded = team2_home.get('team2_conceded_at_home', 0)
        
        team1_home_rate = (team1_home_wins / team1_home_games * 100) if team1_home_games > 0 else 0
        team2_home_rate = (team2_home_wins / team2_home_games * 100) if team2_home_games > 0 else 0
        team1_home_goal_avg = team1_home_scored / team1_home_games if team1_home_games > 0 else 0
        team2_home_goal_avg = team2_home_scored / team2_home_games if team2_home_games > 0 else 0
        
        print("| Team at Home | Games | Wins | Losses | Draws | Win Rate | Goals For | Goals Against | Goal Avg |")
        print("|" + "-"*14 + "|" + "-"*7 + "|" + "-"*6 + "|" + "-"*8 + "|" + "-"*7 + "|" + "-"*10 + "|" + "-"*11 + "|" + "-"*15 + "|" + "-"*10 + "|")
        print(f"| {team_1_name:<12} | {team1_home_games:<5} | {team1_home_wins:<4} | {team1_home_losses:<6} | {team1_home_draws:<5} | {team1_home_rate:<7.1f}% | {team1_home_scored:<9} | {team1_home_conceded:<13} | {team1_home_goal_avg:<8.2f} |")
        print(f"| {team_2_name:<12} | {team2_home_games:<5} | {team2_home_wins:<4} | {team2_home_losses:<6} | {team2_home_draws:<5} | {team2_home_rate:<7.1f}% | {team2_home_scored:<9} | {team2_home_conceded:<13} | {team2_home_goal_avg:<8.2f} |")
        print()
    
    # Key Statistical Comparisons
    print("---")
    print("[SOCCER] Key Statistical Comparisons")
    print()
    
    win_advantage = abs(team1_wins - team2_wins)
    win_leader = team_1_name if team1_wins > team2_wins else team_2_name if team2_wins > team1_wins else "Even"
    
    home_rate_diff = abs(team1_home_rate - team2_home_rate) if 'team1_home_rate' in locals() else 0
    home_leader = team_1_name if team1_home_rate > team2_home_rate else team_2_name if 'team1_home_rate' in locals() and team2_home_rate > team1_home_rate else "Even"
    
    goals_diff = abs(team1_goals_per_game - team2_goals_per_game)
    goals_leader = team_1_name if team1_goals_per_game > team2_goals_per_game else team_2_name
    
    print("| Category                 | " + f"{team_1_name:<13}" + " | " + f"{team_2_name:<13}" + " | Advantage      |")
    print("|" + "-"*26 + "|" + "-"*15 + "|" + "-"*15 + "|" + "-"*16 + "|")
    print(f"| Historical Dominance     | {team1_wins:<13} | {team2_wins:<13} | {win_leader} +{win_advantage:<7} |")
    if 'team1_home_rate' in locals():
        print(f"| Home Win Rate            | {team1_home_rate:<12.1f}% | {team2_home_rate:<12.1f}% | {home_leader} +{home_rate_diff:<6.1f}% |")
    print(f"| Goals Per Game (Overall) | {team1_goals_per_game:<13.2f} | {team2_goals_per_game:<13.2f} | {goals_leader} +{goals_diff:<7.2f}  |")
    if 'team1_home_conceded' in locals():
        team1_def = team1_home_conceded / team1_home_games if team1_home_games > 0 else 0
        team2_def = team2_home_conceded / team2_home_games if team2_home_games > 0 else 0
        def_diff = abs(team1_def - team2_def)
        def_leader = team_2_name if team1_def > team2_def else team_1_name  # Lower is better for defense
        print(f"| Home Defense             | {team1_def:<13.2f} | {team2_def:<13.2f} | {def_leader} +{def_diff:<7.2f}  |")
        print(f"| Home Attack              | {team1_home_goal_avg:<13.2f} | {team2_home_goal_avg:<13.2f} | {team_2_name if team2_home_goal_avg > team1_home_goal_avg else team_1_name} +{abs(team2_home_goal_avg - team1_home_goal_avg):<7.2f}  |")
    print()
    
    # Head-to-Head Insights
    print("---")
    print("[TARGET] Head-to-Head Insights")
    print()
    
    most_dominant = team_1_name if team1_pct > team2_pct else team_2_name if team2_pct > team1_pct else "Even"
    dominant_pct = max(team1_pct, team2_pct)
    
    if 'team1_home_rate' in locals():
        home_fortress = team_1_name if team1_home_rate > team2_home_rate else team_2_name
        home_losses = team1_home_losses if team1_home_rate > team2_home_rate else team2_home_losses
    
    scoring_type = "High" if avg_goals > 2.5 else "Low" if avg_goals < 2.0 else "Moderate"
    
    print("| Insight            | Details                                       |")
    print("|" + "-"*20 + "|" + "-"*47 + "|")
    print(f"| Total Games        | {total_games} matches played                             |")
    print(f"| Most Dominant      | {most_dominant} ({dominant_pct:.1f}% win rate)                      |")
    if 'home_fortress' in locals():
        print(f"| Home Fortress      | {home_fortress} (only {home_losses} home loss{'es' if home_losses != 1 else ''} in this fixture)          |")
    print(f"| Scoring Rate       | {scoring_type} ({avg_goals:.2f} goals per game average)            |")
    if 'home_rate_diff' in locals():
        print(f"| Biggest Gap        | Home performance (+{home_rate_diff:.1f}% win rate difference) |")
    
    best_hope = "Drawing" if draws_pct > max(team1_pct, team2_pct) else f"Winning away" if team1_pct < team2_pct else f"Home advantage"
    hope_pct = draws_pct if draws_pct > max(team1_pct, team2_pct) else min(team1_pct, team2_pct)
    underdog = team_1_name if team1_pct < team2_pct else team_2_name
    
    print(f"| {underdog}'s Best Hope | {best_hope} ({hope_pct:.1f}% of all games)                  |")
    print()
    
    # Quick Visual Summary
    print("---")
    print("[CHART_BAR] Quick Visual Summary")
    print()
    
    # Wins comparison bars
    max_wins = max(team1_wins, team2_wins, draws)
    team1_bar_length = int((team1_wins / max_wins) * 40) if max_wins > 0 else 0
    team2_bar_length = int((team2_wins / max_wins) * 40) if max_wins > 0 else 0
    draws_bar_length = int((draws / max_wins) * 40) if max_wins > 0 else 0
    
    print("WINS COMPARISON:")
    print(f"{team_2_name}: {'█' * team2_bar_length} ({team2_wins})")
    print(f"Draws:   {'█' * draws_bar_length} ({draws})")
    print(f"{team_1_name}: {'█' * team1_bar_length} ({team1_wins})")
    print()
    
    # Home win rates
    if 'team1_home_rate' in locals():
        max_home_rate = max(team1_home_rate, team2_home_rate)
        team1_home_bar = int((team1_home_rate / max_home_rate) * 30) if max_home_rate > 0 else 0
        team2_home_bar = int((team2_home_rate / max_home_rate) * 30) if max_home_rate > 0 else 0
        
        print("HOME WIN RATES:")
        print(f"{team_2_name} at Home: {'█' * team2_home_bar} ({team2_home_rate:.1f}%)")
        print(f"{team_1_name} at Home:  {'█' * team1_home_bar} ({team1_home_rate:.1f}%)")
        print()
    
    # Bottom line analysis
    if team1_wins > team2_wins:
        advantage_text = f"{team_1_name} dominates this fixture"
    elif team2_wins > team1_wins:
        advantage_text = f"{team_2_name} dominates this fixture"
    else:
        advantage_text = "This is a very evenly matched fixture"
    
    home_analysis = ""
    if 'team1_home_rate' in locals() and 'team2_home_rate' in locals():
        if team1_home_rate > team2_home_rate + 20:
            home_analysis = f", especially when {team_1_name} plays at home"
        elif team2_home_rate > team1_home_rate + 20:
            home_analysis = f", especially when {team_2_name} plays at home"
    
    print(f"Bottom Line: {advantage_text} historically with a {'massive' if win_advantage > 10 else 'significant' if win_advantage > 5 else 'slight'} advantage")
    print(f"in {'all' if win_advantage > 10 else 'most'} categories{home_analysis}. Expect a {scoring_type.lower()}-scoring match ({avg_goals:.1f} goals avg).")

def collect_all_matches(all_data):
    """Collect all matches from all leagues into a single numbered list"""
    all_matches = []
    match_counter = 1
    
    for league_code, league_data in all_data.items():
        if 'processed_matches' in league_data:
            league_info = league_data['league_info']
            matches = league_data['processed_matches']
            
            for match in matches:
                match_info = {
                    'number': match_counter,
                    'league': league_info['name'],
                    'league_country': league_info['country'],
                    'match_data': match
                }
                all_matches.append(match_info)
                match_counter += 1
    
    return all_matches

def display_match_selection_menu(all_matches):
    """Display all matches with numbers for selection"""
    print("\n" + "="*80)
    print("SELECT A MATCH FOR HEAD-TO-HEAD ANALYSIS")
    print("="*80)
    
    if not all_matches:
        print("No matches available for selection")
        return
    
    for match_info in all_matches:
        match = match_info['match_data']
        league = match_info['league']
        number = match_info['number']
        
        teams = match.get('teams', {})
        home_team = teams.get('home', {})
        away_team = teams.get('away', {})
        home_name = home_team.get('name', 'TBD')
        away_name = away_team.get('name', 'TBD')
        match_time = match.get('time', 'N/A')
        
        print(f"  {number}. {home_name} vs {away_name} ({league}) - {match_time}")
    
    print(f"\nEnter a number (1-{len(all_matches)}) or 'skip' to continue:")

def main():
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("MULTI-LEAGUE MATCH FINDER")
    print("=" * 60)
    print("Searches EPL, La Liga, and MLS for matches on your chosen date")
    print("\nSupported date formats:")
    print("  - DD-MM-YYYY (e.g., 17-08-2025)")
    print("  - DD/MM/YYYY (e.g., 17/08/2025)")
    print("  - YYYY-MM-DD (e.g., 2025-08-17)")
    print("  - MM/DD/YYYY (e.g., 08/17/2025)")
    print()
    
    # Get date from user
    while True:
        date_input = input("Enter the date to search for matches: ").strip()
        
        if not date_input:
            print("ERROR - Please enter a date")
            continue
        
        # Validate and convert date
        api_date = validate_date_format(date_input)
        
        if api_date:
            print(f"SUCCESS - Date converted to API format: {api_date}")
            break
        else:
            print("ERROR - Invalid date format. Please try again.")
            print("   Examples: 17-08-2025, 17/08/2025, 2025-08-17")
            continue
    
    print(f"\nSearching for matches on {api_date}...")
    print("=" * 70)
    
    all_data = {}
    total_matches = 0
    
    # Search each league
    for league_code, league_info in LEAGUES.items():
        league_id = league_info['id']
        league_name = league_info['name']
        league_country = league_info['country']
        
        print(f"\n[SEARCHING] {league_name}...")
        
        # Fetch matches
        response_data = get_matches_by_date(league_id, api_date, auth_token)
        
        if response_data:
            matches = extract_matches_from_response(response_data)
            
            # Store data
            all_data[league_code] = {
                'league_info': league_info,
                'date_searched': api_date,
                'matches_found': len(matches),
                'raw_response': response_data,
                'processed_matches': matches
            }
            
            # Display results
            display_league_matches(league_name, league_country, matches, api_date)
            total_matches += len(matches)
        
        else:
            print(f"[ERROR] Failed to fetch data for {league_name}")
            all_data[league_code] = {
                'league_info': league_info,
                'date_searched': api_date,
                'matches_found': 0,
                'error': 'Failed to fetch data'
            }
    
    # Summary
    print("\n" + "=" * 70)
    print("SEARCH SUMMARY")
    print("=" * 70)
    print(f"Date Searched: {api_date}")
    print(f"Leagues Searched: {len(LEAGUES)}")
    print(f"Total Matches Found: {total_matches}")
    
    for league_code, data in all_data.items():
        if 'matches_found' in data:
            league_name = data['league_info']['name']
            match_count = data['matches_found']
            print(f"  • {league_name}: {match_count} matches")
    
    # Save data
    if all_data:
        saved_file = save_all_data(all_data, api_date, script_dir)
        
        if saved_file:
            print(f"\nComplete session data saved to:")
            print(f"   {saved_file}")
    
    # Head-to-head analysis option
    if total_matches > 0:
        all_matches = collect_all_matches(all_data)
        
        if all_matches:
            display_match_selection_menu(all_matches)
            
            while True:
                selection = input().strip().lower()
                
                if selection == 'skip':
                    print("Skipping head-to-head analysis.")
                    break
                
                try:
                    match_number = int(selection)
                    if 1 <= match_number <= len(all_matches):
                        selected_match_info = all_matches[match_number - 1]
                        selected_match = selected_match_info['match_data']
                        
                        # Get team information
                        teams = selected_match.get('teams', {})
                        home_team = teams.get('home', {})
                        away_team = teams.get('away', {})
                        
                        home_id = home_team.get('id')
                        away_id = away_team.get('id')
                        home_name = home_team.get('name', 'Unknown')
                        away_name = away_team.get('name', 'Unknown')
                        
                        if home_id and away_id:
                            print(f"\nFetching head-to-head data for {home_name} vs {away_name}...")
                            
                            # Get head-to-head data
                            h2h_data = get_head_to_head(home_id, away_id, auth_token)
                            
                            if h2h_data:
                                display_head_to_head_summary(h2h_data, home_name, away_name)
                            else:
                                print("Failed to retrieve head-to-head data.")
                        else:
                            print("ERROR - Could not find team IDs for this match.")
                        
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(all_matches)}, or 'skip':")
                        continue
                        
                except ValueError:
                    print("Please enter a valid number or 'skip':")
                    continue
    
    print("\nSearch complete!")

if __name__ == "__main__":
    main()