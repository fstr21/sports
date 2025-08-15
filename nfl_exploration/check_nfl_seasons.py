#!/usr/bin/env python3
"""
Check NFL Data Available Seasons
Find what years have preseason data and when 2025 preseason starts
"""

import nfl_data_py as nfl
import pandas as pd

def check_available_seasons():
    """Check what NFL data is available"""
    print("=" * 60)
    print("NFL DATA AVAILABILITY CHECK")
    print("=" * 60)
    
    # Test a few recent years
    test_years = [2022, 2023, 2024, 2025]
    
    for year in test_years:
        print(f"\nChecking {year} season...")
        
        try:
            schedule = nfl.import_schedules([year])
            total_games = len(schedule)
            
            # Check game types
            game_types = schedule['game_type'].value_counts()
            
            print(f"  Total games: {total_games}")
            print(f"  Game types:")
            for game_type, count in game_types.items():
                type_name = {"REG": "Regular Season", "PRE": "Preseason", "POST": "Playoffs"}.get(game_type, game_type)
                print(f"    {type_name}: {count} games")
            
            # Show date range
            min_date = schedule['gameday'].min()
            max_date = schedule['gameday'].max()
            print(f"  Date range: {min_date} to {max_date}")
            
            # Show preseason dates if any
            if 'PRE' in game_types:
                preseason = schedule[schedule['game_type'] == 'PRE']
                pre_min = preseason['gameday'].min()
                pre_max = preseason['gameday'].max()
                print(f"  Preseason: {pre_min} to {pre_max}")
                
                # Show preseason weeks
                weeks = sorted(preseason['week'].unique())
                print(f"  Preseason weeks: {weeks}")
            
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Check 2024 preseason specifically 
    print(f"\n" + "=" * 40)
    print("2024 PRESEASON DETAIL")
    print("=" * 40)
    
    try:
        schedule_2024 = nfl.import_schedules([2024])
        preseason_2024 = schedule_2024[schedule_2024['game_type'] == 'PRE']
        
        if len(preseason_2024) > 0:
            print(f"2024 Preseason games: {len(preseason_2024)}")
            
            # Show all preseason games
            print("\nAll 2024 preseason games:")
            for idx, game in preseason_2024.iterrows():
                week = game['week']
                date = game['gameday']
                away = game['away_team']
                home = game['home_team']
                time = game.get('gametime', 'TBD')
                print(f"  Week {week} - {date}: {away} @ {home} at {time}")
        else:
            print("No 2024 preseason games found")
            
    except Exception as e:
        print(f"Error checking 2024: {e}")

def main():
    check_available_seasons()

if __name__ == "__main__":
    main()