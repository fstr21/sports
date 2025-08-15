#!/usr/bin/env python3
"""
Find NFL Preseason Data - Alternative Sources
Look for preseason data in different ways or alternative sources
"""

import nfl_data_py as nfl
import pandas as pd
import requests
from datetime import datetime

def check_all_nfl_functions():
    """Check all available nfl_data_py functions for preseason data"""
    print("=" * 60)
    print("CHECKING ALL NFL_DATA_PY FUNCTIONS")
    print("=" * 60)
    
    # Get all functions
    nfl_functions = [attr for attr in dir(nfl) if callable(getattr(nfl, attr)) and not attr.startswith('_')]
    
    print(f"Total functions available: {len(nfl_functions)}")
    
    # Test functions that might have preseason data
    potential_functions = [
        'import_schedules',
        'import_sc_lines',  # Might be sportsbook lines
        'import_ftn_data',  # FantasyPros data
        'import_seasonal_data',
        'import_weekly_data'
    ]
    
    for func_name in potential_functions:
        if func_name in nfl_functions:
            print(f"\nTesting {func_name}...")
            try:
                func = getattr(nfl, func_name)
                
                if func_name == 'import_schedules':
                    # Try with different parameters
                    print("  Trying standard schedules...")
                    data = func([2024])
                    game_types = data['game_type'].unique() if 'game_type' in data.columns else []
                    print(f"    Game types: {list(game_types)}")
                    
                elif func_name == 'import_sc_lines':
                    print("  Trying sportsbook lines...")
                    data = func([2024])
                    print(f"    Shape: {data.shape}")
                    print(f"    Columns: {list(data.columns)[:10]}...")
                    if 'game_type' in data.columns:
                        game_types = data['game_type'].unique()
                        print(f"    Game types: {list(game_types)}")
                    
                elif func_name == 'import_ftn_data':
                    print("  Trying FTN data...")
                    data = func([2024])
                    print(f"    Shape: {data.shape}")
                    print(f"    Columns: {list(data.columns)[:10]}...")
                    
                else:
                    # Try basic call
                    data = func([2024])
                    print(f"    Shape: {data.shape}")
                    print(f"    Columns: {list(data.columns)[:5]}...")
                    
            except Exception as e:
                print(f"    Error: {e}")

def check_historical_preseason():
    """Check if older years have preseason data"""
    print(f"\n" + "=" * 60)
    print("CHECKING HISTORICAL YEARS FOR PRESEASON")
    print("=" * 60)
    
    # Go back further in years
    test_years = [2015, 2016, 2017, 2018, 2019, 2020]
    
    for year in test_years:
        print(f"\nChecking {year}...")
        try:
            schedule = nfl.import_schedules([year])
            game_types = schedule['game_type'].unique()
            print(f"  Game types: {list(game_types)}")
            
            if 'PRE' in game_types:
                preseason = schedule[schedule['game_type'] == 'PRE']
                print(f"  FOUND PRESEASON: {len(preseason)} games")
                
                # Show sample
                sample = preseason.head(3)
                for idx, game in sample.iterrows():
                    print(f"    {game['gameday']}: {game['away_team']} @ {game['home_team']}")
                
                return year, preseason
            
        except Exception as e:
            print(f"  Error: {e}")
    
    return None, None

def check_alternative_nfl_apis():
    """Check if there are alternative NFL APIs for preseason"""
    print(f"\n" + "=" * 60)
    print("ALTERNATIVE NFL DATA SOURCES")
    print("=" * 60)
    
    # ESPN API (public)
    print("1. Testing ESPN NFL API...")
    try:
        espn_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        response = requests.get(espn_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', [])
            print(f"   ESPN API working: {len(events)} current events")
            
            if events:
                sample = events[0]
                print(f"   Sample event: {sample.get('name', 'Unknown')}")
                print(f"   Date: {sample.get('date', 'Unknown')}")
        else:
            print(f"   ESPN API returned status: {response.status_code}")
            
    except Exception as e:
        print(f"   ESPN API error: {e}")
    
    # NFL.com API (if accessible)
    print(f"\n2. Testing NFL.com API...")
    try:
        nfl_url = "https://www.nfl.com/api/dolce/v1/games/nfl/2024"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(nfl_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"   NFL.com API accessible")
        else:
            print(f"   NFL.com API returned status: {response.status_code}")
            
    except Exception as e:
        print(f"   NFL.com API error: {e}")

def suggest_testing_strategy():
    """Suggest how to test without preseason data"""
    print(f"\n" + "=" * 60)
    print("TESTING STRATEGY WITHOUT PRESEASON")
    print("=" * 60)
    
    print("Since preseason data isn't available, here are testing options:")
    print()
    print("1. HISTORICAL GAME TESTING")
    print("   - Use 2024 completed games as test data")
    print("   - Validate all MCP tools with real historical data")
    print("   - Ensure data parsing and formatting works correctly")
    print()
    print("2. MOCK DATA TESTING")
    print("   - Create simulated preseason games using 2025 schedule format")
    print("   - Test MCP endpoints with realistic fake data")
    print("   - Validate tool responses and error handling")
    print()
    print("3. HYBRID APPROACH")
    print("   - Build MCP using 2024 historical data for testing")
    print("   - Deploy to Railway and validate deployment")
    print("   - Switch to 2025 data when regular season starts")
    print()
    print("4. REAL-TIME TESTING PREP")
    print("   - Build all tools now using available data")
    print("   - Test integration with Odds MCP using historical data")
    print("   - Monitor for when 2025 regular season data becomes available")

def main():
    """Run comprehensive preseason data search"""
    print("NFL PRESEASON DATA SEARCH")
    print("Looking for ways to get preseason data for testing")
    
    # Check all functions
    check_all_nfl_functions()
    
    # Check historical years
    year, preseason = check_historical_preseason()
    
    # Check alternative APIs
    check_alternative_nfl_apis()
    
    # Suggest testing strategy
    suggest_testing_strategy()
    
    print(f"\n" + "=" * 60)
    print("RECOMMENDATION")
    print("=" * 60)
    
    if year and preseason is not None:
        print(f"✓ Found preseason data in {year}")
        print(f"✓ Can use historical preseason for testing")
    else:
        print("✗ No preseason data found in nfl_data_py")
        print("✓ Recommend using 2024 historical games for testing")
        print("✓ Build and test MCP with completed games")
        print("✓ Deploy and validate before regular season starts")

if __name__ == "__main__":
    main()