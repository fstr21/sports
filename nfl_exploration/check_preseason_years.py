#!/usr/bin/env python3
"""
Check Historical NFL Preseason Data
Look at older years to see if preseason data exists
"""

import nfl_data_py as nfl
import pandas as pd

def check_preseason_history():
    """Check if preseason data exists in historical years"""
    print("=" * 60)
    print("NFL PRESEASON DATA HISTORICAL CHECK")
    print("=" * 60)
    
    # Test years going back further
    test_years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
    
    preseason_found = False
    
    for year in test_years:
        print(f"\nChecking {year}...")
        
        try:
            schedule = nfl.import_schedules([year])
            
            # Get unique game types
            game_types = schedule['game_type'].unique()
            
            print(f"  Game types available: {list(game_types)}")
            
            # Check for preseason
            if 'PRE' in game_types:
                preseason_found = True
                preseason = schedule[schedule['game_type'] == 'PRE']
                print(f"  FOUND PRESEASON: {len(preseason)} games")
                
                # Show sample preseason games
                print(f"  Sample preseason games:")
                for idx, game in preseason.head(3).iterrows():
                    print(f"    {game['gameday']}: {game['away_team']} @ {game['home_team']}")
                
                return year, preseason
            else:
                print(f"  No preseason data")
                
        except Exception as e:
            print(f"  ERROR: {e}")
    
    if not preseason_found:
        print(f"\n[!] No preseason data found in any tested years")
        
        # Try different approach - check if there are different data imports
        print(f"\nChecking alternative nfl_data_py functions...")
        
        # List all available functions
        nfl_functions = [attr for attr in dir(nfl) if callable(getattr(nfl, attr)) and not attr.startswith('_')]
        print(f"Available functions in nfl_data_py:")
        for func in sorted(nfl_functions):
            if 'import' in func.lower() or 'schedule' in func.lower():
                print(f"  - {func}")
    
    return None, None

def test_current_season_detail():
    """Check current season in more detail"""
    print(f"\n" + "=" * 40)
    print("CURRENT SEASON DETAIL (2024)")
    print("=" * 40)
    
    try:
        # Try different approaches
        print("1. Standard schedule import...")
        schedule = nfl.import_schedules([2024])
        
        print(f"   Total games: {len(schedule)}")
        print(f"   Columns: {len(schedule.columns)}")
        print(f"   Game types: {list(schedule['game_type'].unique())}")
        
        # Check if there's a way to get all games including preseason
        print(f"\n2. Trying to import with different parameters...")
        
        # Some packages have include_preseason flags
        try:
            # This might not work but worth trying
            all_schedule = nfl.import_schedules([2024], include_playoffs=True)
            print(f"   With playoffs: {len(all_schedule)} games")
            print(f"   Game types: {list(all_schedule['game_type'].unique())}")
        except:
            print(f"   include_playoffs parameter not available")
        
        # Check earliest and latest dates
        earliest = schedule['gameday'].min()
        latest = schedule['gameday'].max()
        print(f"\n3. Date range analysis:")
        print(f"   Earliest game: {earliest}")
        print(f"   Latest game: {latest}")
        
        # August would be preseason time
        august_games = schedule[schedule['gameday'].str.startswith('2024-08')]
        print(f"   August 2024 games: {len(august_games)}")
        
        if len(august_games) > 0:
            print(f"   August games found:")
            for idx, game in august_games.iterrows():
                print(f"     {game['gameday']}: {game['away_team']} @ {game['home_team']} ({game['game_type']})")
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    year, preseason_data = check_preseason_history()
    test_current_season_detail()
    
    print(f"\n" + "=" * 60)
    print("PRESEASON DATA CONCLUSION")
    print("=" * 60)
    
    if year:
        print(f"✅ Preseason data found in {year}")
        print(f"📊 Can access historical preseason games")
        print(f"🎯 Recommendation: Build NFL MCP with note about preseason availability")
    else:
        print(f"❌ No preseason data found in nfl_data_py")
        print(f"📊 Only regular season and playoff data available")
        print(f"🎯 Recommendation: Build NFL MCP focused on regular season")
        print(f"🔄 Alternative: Look for different NFL data sources for preseason")

if __name__ == "__main__":
    main()