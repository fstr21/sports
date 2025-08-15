#!/usr/bin/env python3
"""
Show Upcoming NFL Games
Simple script to display upcoming NFL games in terminal
"""

import nfl_data_py as nfl
import pandas as pd
from datetime import datetime, timedelta

def show_upcoming_games():
    """Show upcoming NFL games"""
    print("=" * 70)
    print("UPCOMING NFL GAMES - 2025 SEASON")
    print("=" * 70)
    
    # Get 2025 schedule
    schedule = nfl.import_schedules([2025])
    
    # Get today's date
    today = datetime.now().date()
    
    # Convert gameday to datetime for comparison
    schedule['game_date'] = pd.to_datetime(schedule['gameday']).dt.date
    
    # Filter for upcoming games (next 30 days)
    future_date = today + timedelta(days=30)
    upcoming = schedule[
        (schedule['game_date'] >= today) & 
        (schedule['game_date'] <= future_date)
    ].sort_values('gameday')
    
    if len(upcoming) == 0:
        print("No games found in the next 30 days")
        print(f"Season starts: {schedule['gameday'].min()}")
        
        # Show first few games of the season
        print(f"\nFirst 10 games of 2025 season:")
        first_games = schedule.head(10)
        
        for idx, game in first_games.iterrows():
            week = game['week']
            date = game['gameday']
            weekday = game['weekday']
            time = game.get('gametime', 'TBD')
            away = game['away_team']
            home = game['home_team']
            
            print(f"\nWeek {week} - {weekday}, {date} at {time}")
            print(f"  {away} @ {home}")
            
            # Show betting info if available
            away_ml = game.get('away_moneyline')
            home_ml = game.get('home_moneyline')
            spread = game.get('spread_line')
            total = game.get('total_line')
            
            if pd.notna(away_ml) and pd.notna(home_ml):
                print(f"  Moneyline: {away} {away_ml:+.0f}, {home} {home_ml:+.0f}")
            
            if pd.notna(spread):
                print(f"  Spread: {spread}")
            
            if pd.notna(total):
                print(f"  Over/Under: {total}")
    
    else:
        print(f"Found {len(upcoming)} games in the next 30 days:")
        
        current_week = None
        for idx, game in upcoming.iterrows():
            week = game['week']
            
            # Print week header
            if week != current_week:
                print(f"\n--- WEEK {week} ---")
                current_week = week
            
            date = game['gameday']
            weekday = game['weekday'] 
            time = game.get('gametime', 'TBD')
            away = game['away_team']
            home = game['home_team']
            
            print(f"\n{weekday}, {date} at {time}")
            print(f"  {away} @ {home}")
            
            # Show betting odds
            away_ml = game.get('away_moneyline')
            home_ml = game.get('home_moneyline')
            spread = game.get('spread_line')
            total = game.get('total_line')
            
            odds_line = "  Odds: "
            if pd.notna(away_ml) and pd.notna(home_ml):
                odds_line += f"ML {away} {away_ml:+.0f}, {home} {home_ml:+.0f}"
            
            if pd.notna(spread):
                odds_line += f" | Spread {spread}"
            
            if pd.notna(total):
                odds_line += f" | O/U {total}"
            
            if len(odds_line) > 8:  # More than just "  Odds: "
                print(odds_line)
    
    print(f"\n" + "=" * 70)

def show_this_week():
    """Show this week's games specifically"""
    print("=" * 70)
    print("THIS WEEK'S NFL GAMES")
    print("=" * 70)
    
    schedule = nfl.import_schedules([2025])
    
    # Get current week number (approximate)
    today = datetime.now()
    season_start = datetime(2025, 9, 4)  # First game date
    
    if today < season_start:
        print("Season hasn't started yet")
        print(f"Season starts: {season_start.strftime('%B %d, %Y')}")
        
        # Show Week 1 games
        week1_games = schedule[schedule['week'] == 1]
        print(f"\nWeek 1 games ({len(week1_games)} games):")
        
        for idx, game in week1_games.iterrows():
            date = game['gameday']
            weekday = game['weekday']
            time = game.get('gametime', 'TBD')
            away = game['away_team']
            home = game['home_team']
            
            print(f"  {weekday} {date} at {time}: {away} @ {home}")
        
        return
    
    # Calculate current week
    days_since_start = (today - season_start).days
    current_week = min(1 + (days_since_start // 7), 18)  # Cap at week 18
    
    week_games = schedule[schedule['week'] == current_week]
    
    print(f"Week {current_week} games ({len(week_games)} games):")
    
    for idx, game in week_games.iterrows():
        date = game['gameday']
        weekday = game['weekday']
        time = game.get('gametime', 'TBD')
        away = game['away_team']
        home = game['home_team']
        
        print(f"\n{weekday}, {date} at {time}")
        print(f"  {away} @ {home}")
        
        # Show stadium and other details
        stadium = game.get('stadium', 'Unknown')
        qb_away = game.get('away_qb_name', 'TBD')
        qb_home = game.get('home_qb_name', 'TBD')
        
        print(f"  Stadium: {stadium}")
        print(f"  QBs: {qb_away} vs {qb_home}")
        
        # Show betting odds
        away_ml = game.get('away_moneyline')
        home_ml = game.get('home_moneyline')
        spread = game.get('spread_line')
        total = game.get('total_line')
        
        if pd.notna(away_ml) and pd.notna(home_ml):
            print(f"  Moneyline: {away} {away_ml:+.0f}, {home} {home_ml:+.0f}")
        
        if pd.notna(spread):
            print(f"  Spread: {spread}")
        
        if pd.notna(total):
            print(f"  Over/Under: {total}")

def main():
    """Run the upcoming games display"""
    try:
        show_upcoming_games()
        print()
        show_this_week()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()