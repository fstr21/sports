#!/usr/bin/env python3
"""
SoccerDataAPI League Standing Fetcher
Retrieves league standings for a specified league and exports to JSON file
"""

import requests
import json
from datetime import datetime
import os

def get_standing(league_id, auth_token, season=None):
    """Get league standings from SoccerDataAPI"""
    
    url = "https://api.soccerdataapi.com/standing/"
    querystring = {'league_id': league_id, 'auth_token': auth_token}
    
    # Add season parameter if provided
    if season:
        querystring['season'] = season
    
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

def save_to_json(data, league_id, season, output_dir):
    """Save standing data to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    season_clean = season.replace("-", "_") if season else "current"
    filename = f"standing_league_{league_id}_season_{season_clean}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"SUCCESS - Data saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"ERROR - Error saving file: {e}")
        return None

def display_standing(standing_data, league_id):
    """Display league standing information in easy-to-read format"""
    print("\n" + "="*90)
    print(f"LEAGUE STANDINGS - LEAGUE ID: {league_id}")
    print("="*90)
    
    if standing_data:
        # Basic league info
        league_info = standing_data.get('league', {})
        season = standing_data.get('season', 'N/A')
        
        print("LEAGUE INFORMATION:")
        print("-" * 20)
        print(f"League: {league_info.get('name', 'N/A')} (ID: {league_info.get('id', 'N/A')})")
        print(f"Season: {season}")
        print(f"Standing ID: {standing_data.get('id', 'N/A')}")
        
        # Stages
        stages = standing_data.get('stage', [])
        
        if stages:
            for stage_num, stage in enumerate(stages, 1):
                stage_name = stage.get('stage_name', 'N/A')
                stage_id = stage.get('stage_id', 'N/A')
                is_active = stage.get('is_active', False)
                has_groups = stage.get('has_groups', False)
                
                print(f"\nSTAGE {stage_num}: {stage_name}")
                print("-" * 50)
                print(f"Stage ID: {stage_id}")
                print(f"Active: {'Yes' if is_active else 'No'}")
                print(f"Has Groups: {'Yes' if has_groups else 'No'}")
                
                standings = stage.get('standings', [])
                
                if standings:
                    print(f"\nSTANDINGS TABLE ({len(standings)} teams):")
                    print("-" * 40)
                    
                    # Header
                    print(f"{'Pos':<3} {'Team':<25} {'MP':<3} {'W':<3} {'D':<3} {'L':<3} {'GF':<3} {'GA':<3} {'GD':<4} {'Pts':<4}")
                    print("-" * 90)
                    
                    # Teams
                    for team in standings:
                        pos = team.get('position', 'N/A')
                        team_name = team.get('team_name', 'N/A')
                        team_id = team.get('team_id', 'N/A')
                        games = team.get('games_played', 0)
                        wins = team.get('wins', 0)
                        draws = team.get('draws', 0)
                        losses = team.get('losses', 0)
                        goals_for = team.get('goals_for', 0)
                        goals_against = team.get('goals_against', 0)
                        goal_diff = goals_for - goals_against
                        points = team.get('points', 0)
                        position_attr = team.get('position_attribute', '')
                        
                        # Truncate team name if too long
                        if len(team_name) > 24:
                            team_name = team_name[:21] + "..."
                        
                        print(f"{pos:<3} {team_name:<25} {games:<3} {wins:<3} {draws:<3} {losses:<3} {goals_for:<3} {goals_against:<3} {goal_diff:+4d} {points:<4}")
                        
                        # Show position attribute if important (Champions League, relegation, etc.)
                        if position_attr and any(keyword in position_attr.lower() for keyword in ['champions', 'europa', 'relegation', 'promotion']):
                            print(f"    -> {position_attr}")
                    
                    # Top teams summary
                    if len(standings) >= 3:
                        print(f"\nTOP 3 TEAMS:")
                        print("-" * 15)
                        for i, team in enumerate(standings[:3], 1):
                            team_name = team.get('team_name', 'N/A')
                            points = team.get('points', 0)
                            games = team.get('games_played', 0)
                            gd = team.get('goals_for', 0) - team.get('goals_against', 0)
                            print(f"{i}. {team_name} - {points} pts (GD: {gd:+d}, {games} games)")
                    
                    # Bottom teams (relegation zone)
                    if len(standings) >= 18:  # Typical for major leagues
                        print(f"\nRELEGATION ZONE (Bottom 3):")
                        print("-" * 30)
                        bottom_3 = standings[-3:]
                        for team in bottom_3:
                            pos = team.get('position', 'N/A')
                            team_name = team.get('team_name', 'N/A')
                            points = team.get('points', 0)
                            games = team.get('games_played', 0)
                            gd = team.get('goals_for', 0) - team.get('goals_against', 0)
                            print(f"{pos}. {team_name} - {points} pts (GD: {gd:+d}, {games} games)")
                    
                    # League stats
                    if len(standings) > 0:
                        total_games = sum(team.get('games_played', 0) for team in standings)
                        total_goals = sum(team.get('goals_for', 0) for team in standings)
                        avg_goals_per_game = total_goals / (total_games / 2) if total_games > 0 else 0
                        
                        print(f"\nLEAGUE STATISTICS:")
                        print("-" * 18)
                        print(f"Total Goals Scored: {total_goals}")
                        print(f"Average Goals Per Game: {avg_goals_per_game:.2f}")
                        
                        # Find top scorer team
                        top_scoring_team = max(standings, key=lambda x: x.get('goals_for', 0))
                        worst_defense = max(standings, key=lambda x: x.get('goals_against', 0))
                        
                        print(f"Top Scoring Team: {top_scoring_team.get('team_name', 'N/A')} ({top_scoring_team.get('goals_for', 0)} goals)")
                        print(f"Worst Defense: {worst_defense.get('team_name', 'N/A')} ({worst_defense.get('goals_against', 0)} conceded)")
                else:
                    print("No standings data available for this stage")
        else:
            print("No stages found in standings data")
    else:
        print("No standings data found")
    
    print("\n" + "="*90)
    print("RAW DATA STRUCTURE")
    print("="*90)
    print(json.dumps(standing_data, indent=2, ensure_ascii=False))
    print("="*90)

def main():
    # Configuration
    league_id = 228  # Premier League
    season = None    # Use current season (optional parameter)
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    
    # Get current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("SoccerDataAPI League Standing Fetcher")
    print(f"Fetching standings for League ID: {league_id}")
    if season:
        print(f"Season: {season}")
    else:
        print("Season: Current/Latest")
    print(f"Output directory: {script_dir}")
    
    # Fetch standing data
    standing_data = get_standing(league_id, auth_token, season)
    
    if standing_data:
        # Display formatted information
        display_standing(standing_data, league_id)
        
        # Save to JSON file
        season_data = standing_data.get('season', {})
        if isinstance(season_data, dict):
            season_for_file = season_data.get('year', 'current')
        else:
            season_for_file = season or 'current'
        saved_file = save_to_json(standing_data, league_id, season_for_file, script_dir)
        
        if saved_file:
            print(f"\nSUCCESS! League standings retrieved and saved.")
        else:
            print(f"\nWARNING - Data retrieved but failed to save to file.")
    else:
        print("ERROR - Failed to fetch standings data")

if __name__ == "__main__":
    main()