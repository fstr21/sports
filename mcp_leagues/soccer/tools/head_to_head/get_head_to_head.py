#!/usr/bin/env python3
"""
SoccerDataAPI Head-to-Head Fetcher
Retrieves head-to-head statistics between two teams and exports to JSON file
"""

import requests
import json
from datetime import datetime
import os

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
        print(f"ERROR - Error making request: {e}")
        return None
    except ValueError as e:
        print(f"ERROR - Error parsing JSON: {e}")
        return None

def save_to_json(data, team_1_id, team_2_id, output_dir):
    """Save head-to-head data to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"head_to_head_{team_1_id}_vs_{team_2_id}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"SUCCESS - Data saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"ERROR - Error saving file: {e}")
        return None

def display_head_to_head(h2h_data, team_1_id, team_2_id):
    """Display head-to-head information in easy-to-read format"""
    print("\n" + "="*80)
    print(f"HEAD-TO-HEAD STATISTICS")
    print("="*80)
    
    if h2h_data:
        print("TEAMS:")
        print("-" * 10)
        
        team1 = h2h_data.get('team1', {})
        team2 = h2h_data.get('team2', {})
        
        team1_name = team1.get('name', 'N/A')
        team1_id_display = team1.get('id', 'N/A')
        team2_name = team2.get('name', 'N/A')
        team2_id_display = team2.get('id', 'N/A')
        
        print(f"Team 1: {team1_name} (ID: {team1_id_display})")
        print(f"Team 2: {team2_name} (ID: {team2_id_display})")
        print(f"H2H Record ID: {h2h_data.get('id', 'N/A')}")
        
        # Overall statistics
        stats = h2h_data.get('stats', {})
        overall = stats.get('overall', {})
        
        if overall:
            print("\nOVERALL HEAD-TO-HEAD RECORD:")
            print("-" * 35)
            total_games = overall.get('overall_games_played', 0)
            team1_wins = overall.get('overall_team1_wins', 0)
            team2_wins = overall.get('overall_team2_wins', 0)
            draws = overall.get('overall_draws', 0)
            team1_scored = overall.get('overall_team1_scored', 0)
            team2_scored = overall.get('overall_team2_scored', 0)
            
            print(f"Total Games Played: {total_games}")
            print(f"{team1_name} Wins: {team1_wins}")
            print(f"{team2_name} Wins: {team2_wins}")
            print(f"Draws: {draws}")
            print(f"Total Goals - {team1_name}: {team1_scored}, {team2_name}: {team2_scored}")
            
            # Calculate percentages
            if total_games > 0:
                team1_win_pct = (team1_wins / total_games) * 100
                team2_win_pct = (team2_wins / total_games) * 100
                draw_pct = (draws / total_games) * 100
                
                print(f"\nWin Percentages:")
                print(f"{team1_name}: {team1_win_pct:.1f}%")
                print(f"{team2_name}: {team2_win_pct:.1f}%")
                print(f"Draws: {draw_pct:.1f}%")
                
                avg_goals_per_game = (team1_scored + team2_scored) / total_games
                print(f"Average Goals Per Game: {avg_goals_per_game:.2f}")
        
        # Team 1 at home statistics
        team1_home = stats.get('team1_at_home', {})
        if team1_home:
            print(f"\n{team1_name.upper()} AT HOME vs {team2_name}:")
            print("-" * 40)
            home_games = team1_home.get('team1_games_played_at_home', 0)
            home_wins = team1_home.get('team1_wins_at_home', 0)
            home_losses = team1_home.get('team1_losses_at_home', 0)
            home_draws = team1_home.get('team1_draws_at_home', 0)
            home_scored = team1_home.get('team1_scored_at_home', 0)
            home_conceded = team1_home.get('team1_conceded_at_home', 0)
            
            print(f"Games at Home: {home_games}")
            print(f"Wins: {home_wins}, Losses: {home_losses}, Draws: {home_draws}")
            print(f"Goals Scored: {home_scored}, Goals Conceded: {home_conceded}")
            
            if home_games > 0:
                home_win_pct = (home_wins / home_games) * 100
                print(f"Home Win Rate: {home_win_pct:.1f}%")
                home_avg_scored = home_scored / home_games
                home_avg_conceded = home_conceded / home_games
                print(f"Avg Goals Scored at Home: {home_avg_scored:.2f}")
                print(f"Avg Goals Conceded at Home: {home_avg_conceded:.2f}")
        
        # Team 2 at home statistics
        team2_home = stats.get('team2_at_home', {})
        if team2_home:
            print(f"\n{team2_name.upper()} AT HOME vs {team1_name}:")
            print("-" * 40)
            away_games = team2_home.get('team2_games_played_at_home', 0)
            away_wins = team2_home.get('team2_wins_at_home', 0)
            away_losses = team2_home.get('team2_losses_at_home', 0)
            away_draws = team2_home.get('team2_draws_at_home', 0)
            away_scored = team2_home.get('team2_scored_at_home', 0)
            away_conceded = team2_home.get('team2_conceded_at_home', 0)
            
            print(f"Games at Home: {away_games}")
            print(f"Wins: {away_wins}, Losses: {away_losses}, Draws: {away_draws}")
            print(f"Goals Scored: {away_scored}, Goals Conceded: {away_conceded}")
            
            if away_games > 0:
                away_win_pct = (away_wins / away_games) * 100
                print(f"Home Win Rate: {away_win_pct:.1f}%")
                away_avg_scored = away_scored / away_games
                away_avg_conceded = away_conceded / away_games
                print(f"Avg Goals Scored at Home: {away_avg_scored:.2f}")
                print(f"Avg Goals Conceded at Home: {away_avg_conceded:.2f}")
        
        # Summary insights
        if overall and overall.get('overall_games_played', 0) > 0:
            print(f"\nKEY INSIGHTS:")
            print("-" * 15)
            
            total_games = overall.get('overall_games_played', 0)
            team1_wins = overall.get('overall_team1_wins', 0)
            team2_wins = overall.get('overall_team2_wins', 0)
            
            if team1_wins > team2_wins:
                advantage = team1_wins - team2_wins
                print(f"• {team1_name} leads the head-to-head record ({team1_wins}-{team2_wins}, +{advantage})")
            elif team2_wins > team1_wins:
                advantage = team2_wins - team1_wins
                print(f"• {team2_name} leads the head-to-head record ({team2_wins}-{team1_wins}, +{advantage})")
            else:
                print(f"• The teams are evenly matched ({team1_wins}-{team2_wins})")
            
            avg_goals = (overall.get('overall_team1_scored', 0) + overall.get('overall_team2_scored', 0)) / total_games
            if avg_goals > 2.5:
                print(f"• High-scoring fixture (avg {avg_goals:.2f} goals per game)")
            elif avg_goals < 2.0:
                print(f"• Low-scoring fixture (avg {avg_goals:.2f} goals per game)")
            else:
                print(f"• Moderate-scoring fixture (avg {avg_goals:.2f} goals per game)")
    else:
        print("No head-to-head data found")
    
    print("\n" + "="*80)
    print("RAW DATA STRUCTURE")
    print("="*80)
    print(json.dumps(h2h_data, indent=2, ensure_ascii=False))
    print("="*80)

def main():
    # Configuration
    team_1_id = 4145  # First team
    team_2_id = 2916  # Second team
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    
    # Get current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("SoccerDataAPI Head-to-Head Fetcher")
    print(f"Fetching head-to-head stats for Team {team_1_id} vs Team {team_2_id}")
    print(f"Output directory: {script_dir}")
    
    # Fetch head-to-head data
    h2h_data = get_head_to_head(team_1_id, team_2_id, auth_token)
    
    if h2h_data:
        # Display formatted information
        display_head_to_head(h2h_data, team_1_id, team_2_id)
        
        # Save to JSON file
        saved_file = save_to_json(h2h_data, team_1_id, team_2_id, script_dir)
        
        if saved_file:
            print(f"\nSUCCESS! Head-to-head data retrieved and saved.")
        else:
            print(f"\nWARNING - Data retrieved but failed to save to file.")
    else:
        print("ERROR - Failed to fetch head-to-head data")

if __name__ == "__main__":
    main()