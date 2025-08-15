#!/usr/bin/env python3
"""
Quick NFL Data Demo - Show Key Data Points
Simple script to see what NFL data looks like
"""

import nfl_data_py as nfl
import pandas as pd

def show_nfl_schedule():
    """Show upcoming NFL games"""
    print("=" * 50)
    print("NFL 2025 SCHEDULE PREVIEW")
    print("=" * 50)
    
    schedule = nfl.import_schedules([2025])
    
    print(f"Total games loaded: {len(schedule)}")
    print(f"Data columns available: {len(schedule.columns)}")
    
    # Show first 10 games
    print(f"\nFirst 10 games of 2025 season:")
    for i in range(10):
        game = schedule.iloc[i]
        week = game['week']
        date = game['gameday']
        away = game['away_team']
        home = game['home_team']
        away_ml = game.get('away_moneyline', 'N/A')
        home_ml = game.get('home_moneyline', 'N/A')
        spread = game.get('spread_line', 'N/A')
        total = game.get('total_line', 'N/A')
        
        print(f"Week {week} - {date}")
        print(f"  {away} @ {home}")
        print(f"  Moneyline: {away} {away_ml}, {home} {home_ml}")
        print(f"  Spread: {spread}, Total: {total}")
        print()

def show_nfl_teams():
    """Show NFL teams"""
    print("=" * 50)
    print("NFL TEAMS")
    print("=" * 50)
    
    teams = nfl.import_team_desc()
    
    print(f"Total teams: {len(teams)}")
    
    # Group by division
    divisions = teams.groupby('team_division')
    
    for division, team_group in divisions:
        print(f"\n{division}:")
        for idx, team in team_group.iterrows():
            abbr = team['team_abbr']
            name = team['team_name']
            print(f"  {abbr}: {name}")

def show_player_stats():
    """Show top NFL players"""
    print("=" * 50)
    print("2024 NFL PLAYER STATS (TOP PERFORMERS)")
    print("=" * 50)
    
    # Get 2024 weekly passing data
    passing = nfl.import_weekly_data([2024], columns=['player_name', 'recent_team', 'passing_yards', 'passing_tds'])
    
    # Get season totals
    season_passing = passing.groupby(['player_name', 'recent_team']).agg({
        'passing_yards': 'sum',
        'passing_tds': 'sum'
    }).reset_index()
    
    # Top 10 passers by yards
    top_passers = season_passing.sort_values('passing_yards', ascending=False).head(10)
    
    print("Top 10 Quarterbacks by Passing Yards (2024):")
    for idx, player in top_passers.iterrows():
        name = player['player_name']
        team = player['recent_team']
        yards = int(player['passing_yards'])
        tds = int(player['passing_tds'])
        print(f"  {name} ({team}): {yards:,} yards, {tds} TDs")

def show_injury_report():
    """Show current injuries"""
    print("=" * 50)
    print("CURRENT NFL INJURY REPORT")
    print("=" * 50)
    
    injuries = nfl.import_injuries([2024])
    
    # Show players who are Out or Questionable
    significant_injuries = injuries[injuries['report_status'].isin(['Out', 'Questionable'])]
    
    print(f"Total injury reports: {len(injuries)}")
    print(f"Players Out or Questionable: {len(significant_injuries)}")
    
    print(f"\nSample injury reports:")
    for idx, injury in significant_injuries.head(15).iterrows():
        player = injury['full_name']
        team = injury['team']
        status = injury['report_status']
        body_part = injury.get('report_primary_injury', 'Unknown')
        
        print(f"  {player} ({team}): {status} - {body_part}")

def show_key_columns():
    """Show what data is available"""
    print("=" * 50)
    print("AVAILABLE DATA FIELDS")
    print("=" * 50)
    
    schedule = nfl.import_schedules([2025])
    teams = nfl.import_team_desc()
    
    print("Schedule data includes:")
    schedule_cols = list(schedule.columns)
    for i, col in enumerate(schedule_cols):
        if i % 3 == 0:
            print()
        print(f"  {col:<20}", end="")
    
    print(f"\n\nTeam data includes:")
    team_cols = list(teams.columns)
    for i, col in enumerate(team_cols):
        if i % 3 == 0:
            print()
        print(f"  {col:<20}", end="")
    
    print(f"\n\nSample game data:")
    sample_game = schedule.iloc[0]
    print(f"  Game: {sample_game['away_team']} @ {sample_game['home_team']}")
    print(f"  Date: {sample_game['gameday']} at {sample_game.get('gametime', 'TBD')}")
    print(f"  Moneyline: Away {sample_game.get('away_moneyline', 'N/A')}, Home {sample_game.get('home_moneyline', 'N/A')}")
    print(f"  Spread: {sample_game.get('spread_line', 'N/A')}")
    print(f"  Total: {sample_game.get('total_line', 'N/A')}")
    print(f"  Stadium: {sample_game.get('stadium', 'N/A')}")
    print(f"  QBs: {sample_game.get('away_qb_name', 'TBD')} vs {sample_game.get('home_qb_name', 'TBD')}")

def main():
    """Run NFL data demo"""
    print("NFL DATA DEMONSTRATION")
    print("Showing real data from nfl_data_py package")
    print("=" * 60)
    
    try:
        show_nfl_schedule()
        show_nfl_teams()
        show_player_stats()
        show_injury_report()
        show_key_columns()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        print("✓ Schedule data with built-in betting odds")
        print("✓ Complete team information")
        print("✓ Player statistics and performance")
        print("✓ Current injury reports")
        print("✓ Rich metadata for analysis")
        print("\nRecommendation: This data quality supports building an NFL MCP")
        
    except Exception as e:
        print(f"Error running demo: {e}")

if __name__ == "__main__":
    main()