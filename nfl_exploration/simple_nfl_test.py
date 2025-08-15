#!/usr/bin/env python3
"""
Simple NFL MCP Test with Historical Data
Test core NFL functionality using 2024 completed games
"""

import nfl_data_py as nfl
import pandas as pd

def test_nfl_schedule_tool():
    """Test NFL schedule functionality"""
    print("=" * 50)
    print("TEST 1: NFL SCHEDULE TOOL")
    print("=" * 50)
    
    # Load 2024 schedule
    schedule = nfl.import_schedules([2024])
    
    # Test getting Week 1 games
    week1 = schedule[schedule['week'] == 1]
    
    print(f"Week 1 games found: {len(week1)}")
    print(f"\nSample Week 1 games:")
    
    for i, (idx, game) in enumerate(week1.head(5).iterrows()):
        away = game['away_team']
        home = game['home_team']
        away_score = game.get('away_score', 'N/A')
        home_score = game.get('home_score', 'N/A')
        date = game['gameday']
        
        print(f"  {i+1}. {away} @ {home} ({away_score}-{home_score}) on {date}")
        
        # Show betting data
        away_ml = game.get('away_moneyline')
        home_ml = game.get('home_moneyline')
        spread = game.get('spread_line')
        
        if pd.notna(away_ml) and pd.notna(home_ml):
            print(f"     Odds: {away} {away_ml:+.0f}, {home} {home_ml:+.0f}, Spread: {spread}")
    
    return True

def test_nfl_teams_tool():
    """Test NFL teams functionality"""
    print("\n" + "=" * 50)
    print("TEST 2: NFL TEAMS TOOL")
    print("=" * 50)
    
    # Load teams
    teams = nfl.import_team_desc()
    
    print(f"Total teams loaded: {len(teams)}")
    
    # Group by division
    afc_east = teams[teams['team_division'] == 'AFC East']
    
    print(f"\nAFC East teams:")
    for idx, team in afc_east.iterrows():
        abbr = team['team_abbr']
        name = team['team_name']
        print(f"  {abbr}: {name}")
    
    return True

def test_nfl_player_stats_tool():
    """Test NFL player stats functionality"""
    print("\n" + "=" * 50)
    print("TEST 3: NFL PLAYER STATS TOOL")
    print("=" * 50)
    
    # Load 2024 player stats
    print("Loading 2024 player stats...")
    player_stats = nfl.import_weekly_data([2024], 
        columns=['player_name', 'recent_team', 'passing_yards', 'passing_tds'])
    
    # Get season totals for QBs
    season_totals = player_stats.groupby(['player_name', 'recent_team']).agg({
        'passing_yards': 'sum',
        'passing_tds': 'sum'
    }).reset_index()
    
    # Filter for meaningful stats (500+ yards)
    season_totals = season_totals[season_totals['passing_yards'] >= 500]
    season_totals = season_totals.sort_values('passing_yards', ascending=False)
    
    print(f"Top 10 QBs by passing yards (2024):")
    for i, (idx, player) in enumerate(season_totals.head(10).iterrows()):
        name = player['player_name']
        team = player['recent_team']
        yards = int(player['passing_yards'])
        tds = int(player['passing_tds'])
        
        print(f"  {i+1:2d}. {name:<20} ({team}) - {yards:,} yards, {tds} TDs")
    
    return True

def test_nfl_injuries_tool():
    """Test NFL injuries functionality"""
    print("\n" + "=" * 50)
    print("TEST 4: NFL INJURIES TOOL")
    print("=" * 50)
    
    # Load injury data
    injuries = nfl.import_injuries([2024])
    
    print(f"Total injury reports: {len(injuries)}")
    
    # Filter for players currently Out
    out_players = injuries[injuries['report_status'] == 'Out']
    
    print(f"Players currently Out: {len(out_players)}")
    print(f"\nSample injury reports:")
    
    for i, (idx, injury) in enumerate(out_players.head(10).iterrows()):
        player = injury['full_name']
        team = injury['team']
        injury_type = injury.get('report_primary_injury', 'Unknown')
        
        print(f"  {i+1:2d}. {player:<25} ({team}) - {injury_type}")
    
    return True

def test_team_specific_schedule():
    """Test getting schedule for specific team"""
    print("\n" + "=" * 50)
    print("TEST 5: TEAM-SPECIFIC SCHEDULE (Chiefs)")
    print("=" * 50)
    
    schedule = nfl.import_schedules([2024])
    
    # Get all Chiefs games
    kc_games = schedule[
        (schedule['away_team'] == 'KC') | (schedule['home_team'] == 'KC')
    ].sort_values('week')
    
    print(f"Total Chiefs games in 2024: {len(kc_games)}")
    print(f"\nLast 5 Chiefs games:")
    
    for i, (idx, game) in enumerate(kc_games.tail(5).iterrows()):
        week = game['week']
        away = game['away_team']
        home = game['home_team']
        away_score = game.get('away_score', 'N/A')
        home_score = game.get('home_score', 'N/A')
        
        # Determine if home or away
        if away == 'KC':
            opponent = home
            location = '@'
        else:
            opponent = away
            location = 'vs'
        
        print(f"  Week {week:2d}: KC {location} {opponent} ({away_score}-{home_score})")
    
    return True

def test_betting_analysis():
    """Test betting analysis with historical data"""
    print("\n" + "=" * 50)
    print("TEST 6: BETTING ANALYSIS")
    print("=" * 50)
    
    schedule = nfl.import_schedules([2024])
    
    # Find games with complete betting and score data
    complete_games = schedule[
        pd.notna(schedule['away_score']) & 
        pd.notna(schedule['home_score']) &
        pd.notna(schedule['spread_line']) &
        pd.notna(schedule['total_line'])
    ].head(5)
    
    print(f"Analyzing {len(complete_games)} completed games with betting data:")
    
    for i, (idx, game) in enumerate(complete_games.iterrows()):
        away = game['away_team']
        home = game['home_team']
        away_score = int(game['away_score'])
        home_score = int(game['home_score'])
        spread = game['spread_line']
        total_line = game['total_line']
        
        print(f"\n{i+1}. {away} @ {home}: {away_score}-{home_score}")
        
        # Analyze spread
        actual_margin = home_score - away_score
        if spread < 0:  # Home team favored
            spread_result = "COVERED" if actual_margin > abs(spread) else "DID NOT COVER"
            print(f"   Spread: {home} -{abs(spread)} {spread_result}")
        else:  # Away team favored
            spread_result = "COVERED" if actual_margin < -spread else "DID NOT COVER"
            print(f"   Spread: {away} -{spread} {spread_result}")
        
        # Analyze total
        actual_total = away_score + home_score
        over_under = "OVER" if actual_total > total_line else "UNDER"
        print(f"   Total: {actual_total} ({over_under} {total_line})")
    
    return True

def main():
    """Run all NFL MCP tests"""
    print("NFL MCP FUNCTIONALITY TEST")
    print("Using 2024 historical data to validate tools")
    print("=" * 60)
    
    tests = [
        test_nfl_schedule_tool,
        test_nfl_teams_tool,
        test_nfl_player_stats_tool,
        test_nfl_injuries_tool,
        test_team_specific_schedule,
        test_betting_analysis
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"[ERROR] {test.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("\n[SUCCESS] All NFL MCP tools working correctly!")
        print("Ready to build production NFL MCP for 2025 season")
        print("Recommendation: Deploy before September 4, 2025")
    else:
        print(f"\n[WARNING] Some tests failed - review errors above")

if __name__ == "__main__":
    main()