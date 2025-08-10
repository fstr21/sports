#!/usr/bin/env python3
"""
Debug the ESPN player stats endpoint to fix 404 errors.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sports_mcp'))

from interactive_sports_test import SportsTestInterface

def test_mlb_player_ids():
    """Test with MLB player IDs from our extraction"""
    print("Testing MLB Player Stats with Extracted IDs")
    print("="*50)
    
    interface = SportsTestInterface()
    interface.current_sport_league = ("baseball", "mlb")
    
    # Use MLB player IDs we extracted
    mlb_players = [
        ("32655", "Byron Buxton", "CF"),
        ("42450", "Joe Ryan", "SP"), 
        ("31127", "Salvador Perez", "C"),
        ("4905884", "Maikel Garcia", "3B")
    ]
    
    for player_id, name, position in mlb_players:
        print(f"\nTesting: {name} ({position}) - ID: {player_id}")
        
        success, result = interface.make_request("POST", "/espn/player-stats", {
            "sport": "baseball",
            "league": "mlb",
            "player_id": player_id,
            "limit": 5
        })
        
        print(f"  API Success: {success}")
        
        if success:
            if result.get("ok"):
                print(f"  Result: SUCCESS!")
                player_data = result.get("data", {})
                
                # Check what we got
                profile = player_data.get("player_profile", {})
                recent_games = player_data.get("recent_games", {})
                
                if "athlete" in profile:
                    athlete = profile["athlete"]
                    found_name = athlete.get("displayName", "Unknown")
                    print(f"    Found player: {found_name}")
                
                if recent_games:
                    events = recent_games.get("events", [])
                    print(f"    Recent games: {len(events)}")
                    
                    if events:
                        print("    FOUND GAME STATS - This works!")
                        return True
            else:
                error = result.get("message", "Unknown error")
                print(f"  Result: FAILED - {error}")
        else:
            print(f"  Result: API ERROR")
    
    return False

def test_direct_espn_url():
    """Test the actual ESPN URL structure we're using"""
    print("\n" + "="*50)
    print("Testing Direct ESPN API URL Structure")
    print("="*50)
    
    # The URL format from our code:
    # https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/athletes/{player_id}
    
    test_urls = [
        ("baseball", "mlb", "32655", "Byron Buxton"),
        ("football", "nfl", "4361093", "Kyler Gordon"),
        ("basketball", "nba", "1966", "LeBron James (guessed)")
    ]
    
    for sport, league, player_id, name in test_urls:
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/athletes/{player_id}"
        print(f"\n{name}:")
        print(f"  URL: {url}")
        print(f"  This is what our server is calling")

def test_season_parameters():
    """Test if season parameter is needed"""
    print("\n" + "="*50)  
    print("Testing Season Parameters")
    print("="*50)
    
    interface = SportsTestInterface()
    
    # Try with current season
    print("\nTrying with season=2024...")
    success, result = interface.make_request("POST", "/espn/player-stats", {
        "sport": "baseball",
        "league": "mlb",
        "player_id": "32655",  # Byron Buxton
        "season": "2024",
        "limit": 5
    })
    
    print(f"API Success: {success}")
    if success and result.get("ok"):
        print("SUCCESS with season parameter!")
        return True
    elif success:
        print(f"Failed: {result.get('message', 'Unknown error')}")
    
    # Try with no season
    print("\nTrying without season parameter...")
    success, result = interface.make_request("POST", "/espn/player-stats", {
        "sport": "baseball", 
        "league": "mlb",
        "player_id": "32655",
        "limit": 5
    })
    
    print(f"API Success: {success}")
    if success and result.get("ok"):
        print("SUCCESS without season parameter!")
        return True
    elif success:
        print(f"Failed: {result.get('message', 'Unknown error')}")
    
    return False

if __name__ == "__main__":
    mlb_success = test_mlb_player_ids()
    test_direct_espn_url()
    season_success = test_season_parameters()
    
    print(f"\n{'='*50}")
    print("DEBUGGING RESULTS:")
    print(f"MLB player IDs work: {'YES' if mlb_success else 'NO'}")
    print(f"Season parameter helps: {'YES' if season_success else 'NO'}")
    
    if not mlb_success and not season_success:
        print("\nNEED TO INVESTIGATE:")
        print("- ESPN API might require authentication")
        print("- URL structure might be different")
        print("- Player stats might be in different endpoint")
        print("- Rate limiting or access restrictions")