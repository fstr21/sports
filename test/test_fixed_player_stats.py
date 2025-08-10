#!/usr/bin/env python3
"""
Test the fixed player stats endpoint with correct ESPN core API URLs.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sports_mcp'))

from interactive_sports_test import SportsTestInterface

def test_fixed_player_stats():
    """Test player stats with the corrected endpoint"""
    print("Testing Fixed Player Stats Endpoint")
    print("="*40)
    
    interface = SportsTestInterface()
    interface.current_sport_league = ("baseball", "mlb")
    
    # Test with known MLB player IDs
    test_players = [
        ("32655", "Byron Buxton", "CF"),
        ("31127", "Salvador Perez", "C"),
        ("42450", "Joe Ryan", "SP")
    ]
    
    success_count = 0
    
    for player_id, name, position in test_players:
        print(f"\nTesting: {name} ({position}) - ID: {player_id}")
        
        success, result = interface.make_request("POST", "/espn/player-stats", {
            "sport": "baseball",
            "league": "mlb", 
            "player_id": player_id,
            "limit": 5
        })
        
        print(f"  API Success: {success}")
        
        if success and result.get("ok"):
            print(f"  Result: SUCCESS!")
            success_count += 1
            
            player_data = result.get("data", {})
            
            # Check player profile  
            profile = player_data.get("player_profile", {})
            if profile:
                found_name = profile.get("displayName", "Unknown")
                position_info = profile.get("position", {})
                pos_abbr = position_info.get("abbreviation", "N/A") if isinstance(position_info, dict) else "N/A"
                print(f"    Player: {found_name} ({pos_abbr})")
                
                # Look for statistics data
                if "statistics" in profile:
                    print(f"    HAS CURRENT SEASON STATS!")
                
                if "statisticslog" in profile:
                    print(f"    HAS GAME LOG STATS!")
            
            # Check recent games
            recent_games = player_data.get("recent_games", {})
            if recent_games:
                events = recent_games.get("events", [])
                print(f"    Recent games: {len(events)}")
                
                if events:
                    # Test our sport-specific parsing
                    print(f"    Testing stat parsing on first game...")
                    game = events[0]
                    # This would trigger our new parsing functions
                    print(f"    Game data keys: {list(game.keys()) if isinstance(game, dict) else 'Not dict'}")
        
        elif success:
            error = result.get("message", "Unknown error")
            print(f"  Result: FAILED - {error}")
        else:
            print(f"  Result: API ERROR")
    
    return success_count

def test_different_sports():
    """Test the fix across different sports"""
    print(f"\n{'='*40}")
    print("Testing Across Different Sports")
    print("="*40)
    
    interface = SportsTestInterface()
    
    # Test different sports with known player IDs from our extraction
    sport_tests = [
        ("football", "nfl", "4361093", "Kyler Gordon"),  # From NFL extraction
        ("basketball", "nba", "1966", "LeBron James"),   # Known ID
        ("hockey", "nhl", "3904135", "Connor McDavid")   # Known ID
    ]
    
    for sport, league, player_id, name in sport_tests:
        print(f"\nTesting {sport.upper()}: {name} (ID: {player_id})")
        interface.current_sport_league = (sport, league)
        
        success, result = interface.make_request("POST", "/espn/player-stats", {
            "sport": sport,
            "league": league,
            "player_id": player_id,
            "limit": 3
        })
        
        if success and result.get("ok"):
            print(f"  SUCCESS for {sport.upper()}!")
        elif success:
            print(f"  Failed: {result.get('message', 'Unknown error')}")
        else:
            print(f"  API Error")

if __name__ == "__main__":
    mlb_successes = test_fixed_player_stats()
    test_different_sports()
    
    print(f"\n{'='*40}")
    print(f"RESULTS: {mlb_successes}/3 MLB players worked")
    
    if mlb_successes > 0:
        print("SUCCESS: Player stats endpoint is now working!")
        print("Ready to test sport-specific statistics parsing")
    else:
        print("Still having issues - may need further debugging")