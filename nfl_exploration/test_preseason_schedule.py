#!/usr/bin/env python3
"""
Test NFL Preseason Schedule - August 15, 2025
Check if we can get tomorrow's preseason games
"""

import nfl_data_py as nfl
import pandas as pd
from datetime import datetime, timedelta

def test_preseason_games():
    """Test getting preseason games for tomorrow"""
    print("=" * 60)
    print("NFL PRESEASON SCHEDULE TEST - August 15, 2025")
    print("=" * 60)
    
    try:
        # Get 2025 schedule
        print("Getting 2025 NFL schedule (including preseason)...")
        schedule = nfl.import_schedules([2025])
        
        print(f"Total games in 2025 schedule: {len(schedule)}")
        print(f"Schedule columns: {list(schedule.columns)}")
        
        # Filter for preseason games
        preseason_games = schedule[schedule['game_type'] == 'PRE']
        print(f"\nTotal preseason games: {len(preseason_games)}")
        
        # Look for games on 8/15/2025
        target_date = "2025-08-15"
        tomorrow_games = preseason_games[preseason_games['gameday'] == target_date]
        
        print(f"\nGames on {target_date}:")
        if len(tomorrow_games) > 0:
            print(f"Found {len(tomorrow_games)} preseason games tomorrow!")
            
            for idx, game in tomorrow_games.iterrows():
                away_team = game['away_team']
                home_team = game['home_team']
                game_time = game.get('gametime', 'TBD')
                week = game.get('week', 'Unknown')
                
                print(f"  Preseason Week {week}: {away_team} @ {home_team} at {game_time}")
                
                # Show additional details
                print(f"    Game ID: {game.get('game_id', 'Unknown')}")
                if not pd.isna(game.get('away_moneyline')):
                    print(f"    Moneyline: {away_team} {game.get('away_moneyline')}, {home_team} {game.get('home_moneyline')}")
                if not pd.isna(game.get('spread_line')):
                    print(f"    Spread: {game.get('spread_line')}")
                if not pd.isna(game.get('total_line')):
                    print(f"    Total: {game.get('total_line')}")
                print()
        else:
            print(f"No preseason games found for {target_date}")
            
            # Show nearby dates
            print("\nChecking nearby dates for preseason games...")
            
            # Check a few days around target date
            for days_offset in [-2, -1, 0, 1, 2]:
                check_date = datetime.strptime(target_date, "%Y-%m-%d") + timedelta(days=days_offset)
                check_date_str = check_date.strftime("%Y-%m-%d")
                
                games_on_date = preseason_games[preseason_games['gameday'] == check_date_str]
                if len(games_on_date) > 0:
                    print(f"  {check_date_str}: {len(games_on_date)} games")
                    for idx, game in games_on_date.iterrows():
                        away = game['away_team']
                        home = game['home_team']
                        time = game.get('gametime', 'TBD')
                        print(f"    {away} @ {home} at {time}")
                else:
                    print(f"  {check_date_str}: No games")
        
        # Show all preseason weeks
        print(f"\nAll preseason games by week:")
        preseason_by_week = preseason_games.groupby('week').size()
        for week, count in preseason_by_week.items():
            print(f"  Preseason Week {week}: {count} games")
            
            # Show dates for this week
            week_games = preseason_games[preseason_games['week'] == week]
            dates = week_games['gameday'].unique()
            print(f"    Dates: {', '.join(sorted(dates))}")
        
        # Show sample preseason game with all data
        if len(preseason_games) > 0:
            print(f"\nSample preseason game (first one):")
            sample_game = preseason_games.iloc[0]
            print(f"  Game: {sample_game['away_team']} @ {sample_game['home_team']}")
            print(f"  Date: {sample_game['gameday']} at {sample_game.get('gametime', 'TBD')}")
            print(f"  Week: Preseason Week {sample_game['week']}")
            print(f"  Game Type: {sample_game['game_type']}")
            print(f"  Stadium: {sample_game.get('stadium', 'Unknown')}")
            
            # Show all available data points
            print(f"\nAll data fields for this game:")
            for col, val in sample_game.items():
                if not pd.isna(val):
                    print(f"    {col}: {val}")
        
        return schedule, preseason_games, tomorrow_games
        
    except Exception as e:
        print(f"[!] Error testing preseason schedule: {e}")
        return None, None, None

def main():
    """Run preseason schedule test"""
    schedule, preseason, tomorrow = test_preseason_games()
    
    if schedule is not None:
        print("\n" + "=" * 60)
        print("PRESEASON TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully loaded 2025 NFL schedule")
        print(f"📊 Total games: {len(schedule)}")
        print(f"🏈 Preseason games: {len(preseason) if preseason is not None else 0}")
        print(f"📅 Tomorrow's games: {len(tomorrow) if tomorrow is not None else 0}")
        
        if tomorrow is not None and len(tomorrow) > 0:
            print(f"🎯 RESULT: Found {len(tomorrow)} preseason games tomorrow!")
        else:
            print(f"🎯 RESULT: No preseason games tomorrow, but preseason data exists")
    else:
        print("\n❌ Failed to load NFL schedule data")

if __name__ == "__main__":
    main()