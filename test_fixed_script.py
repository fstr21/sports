#!/usr/bin/env python3
"""
Test the fixed interactive script - non-interactive version
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interactive_sports_test import *

def test_mlb():
    """Test MLB games fetching"""
    print("=" * 60)
    print("  TESTING MLB GAMES")
    print("=" * 60)
    
    # Select MLB
    league_config = LEAGUES["1"]  # MLB
    print(f"Testing league: {league_config['name']}")
    
    # Test fetching games
    success, games = fetch_games(league_config)
    
    if success and games:
        print(f"\nSUCCESS: Found {len(games)} games")
        
        # Test fetching odds (this will likely fail but let's see)
        print("\nTesting odds integration...")
        odds_success, matched_games, odds_games = fetch_odds_for_games(league_config, games)
        
        if odds_success:
            print(f"Odds SUCCESS: {len(matched_games)} games with odds")
        else:
            print("Odds FAILED (expected)")
        
        return True
    else:
        print(f"FAILED: {games}")
        return False

if __name__ == "__main__":
    # Reset the global counter
    odds_api_calls = 0
    
    mlb_success = test_mlb()
    
    print("\n" + "=" * 60)
    print("  FINAL RESULTS")
    print("=" * 60)
    print(f"MLB Games: {'PASS' if mlb_success else 'FAIL'}")
    print(f"Total Odds API calls: {odds_api_calls}")
    
    if mlb_success:
        print("\n=> ESPN direct integration working!")
        print("=> Ready to fix odds API integration")
    else:
        print("\n=> Still need to fix ESPN integration")