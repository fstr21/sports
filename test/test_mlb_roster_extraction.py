#!/usr/bin/env python3
"""
Test roster extraction with MLB games (more likely to have active games).
"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sports_mcp'))

from interactive_sports_test import SportsTestInterface

def extract_all_players_from_summary(summary_data):
    """Extract all player IDs and names from any game summary data"""
    players = []
    
    def search_for_athletes(obj, path=""):
        """Recursively search for athlete data"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check if this is athlete data
                if key == "athlete" and isinstance(value, dict):
                    athlete_id = value.get("id")
                    athlete_name = value.get("displayName", value.get("fullName", "Unknown"))
                    position = value.get("position", {})
                    position_abbr = position.get("abbreviation", "N/A") if isinstance(position, dict) else "N/A"
                    
                    if athlete_id:
                        players.append({
                            "id": athlete_id,
                            "name": athlete_name,
                            "position": position_abbr,
                            "source": current_path
                        })
                
                # Continue searching recursively
                search_for_athletes(value, current_path)
                
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                search_for_athletes(item, f"{path}[{i}]")
    
    search_for_athletes(summary_data)
    return players

def test_mlb_roster_extraction():
    """Test MLB roster extraction"""
    print("Testing MLB Roster Extraction")
    print("="*40)
    
    interface = SportsTestInterface()
    interface.current_sport_league = ("baseball", "mlb")
    
    # Get MLB games
    success, result = interface.make_request("POST", "/espn/scoreboard", {
        "sport": "baseball",
        "league": "mlb"
    })
    
    if not success or not result.get("ok"):
        print("Failed to get MLB games")
        return False
    
    games = result.get("data", {}).get("scoreboard", [])
    print(f"Found {len(games)} MLB games")
    
    if not games:
        print("No MLB games to test with")
        return False
    
    # Test with first game
    game = games[0]
    event_id = game.get("id")
    game_name = game.get("name", "Unknown vs Unknown")
    
    print(f"Testing game: {game_name}")
    print(f"Event ID: {event_id}")
    
    # Get game summary
    success, result = interface.make_request("POST", "/espn/game-summary", {
        "sport": "baseball",
        "league": "mlb",
        "event_id": event_id
    })
    
    if not success or not result.get("ok"):
        print("Failed to get MLB game summary")
        return False
    
    summary_data = result.get("data", {})
    
    # Extract all players
    players = extract_all_players_from_summary(summary_data)
    
    print(f"\nFound {len(players)} players total:")
    
    # Group by source
    sources = {}
    for player in players:
        source = player["source"].split(".")[0]  # Top-level section
        if source not in sources:
            sources[source] = []
        sources[source].append(player)
    
    for source, source_players in sources.items():
        print(f"\n{source.upper()}: {len(source_players)} players")
        for i, player in enumerate(source_players[:5], 1):  # Show first 5
            print(f"  {i}. {player['name']} ({player['position']}) - ID: {player['id']}")
        if len(source_players) > 5:
            print(f"  ... and {len(source_players) - 5} more")
    
    # Save summary for analysis
    filename = f"test/mlb_game_summary_{event_id}.json"
    with open(filename, 'w') as f:
        json.dump(summary_data, f, indent=2)
    print(f"\nSaved full summary to: {filename}")
    
    return len(players) > 0

def test_player_id_formats():
    """Test what format the extracted player IDs are in"""
    print("\n" + "="*40)
    print("Testing Player ID Formats")
    print("="*40)
    
    interface = SportsTestInterface()
    
    # Test with known player ID from our extraction
    test_ids = [
        "4361093",  # Kyler Gordon from NFL
        "3116406",  # Tyreek Hill from NFL  
        "4241389",  # CeeDee Lamb from NFL
    ]
    
    for player_id in test_ids:
        print(f"\nTesting player ID: {player_id}")
        
        success, result = interface.make_request("POST", "/espn/player-stats", {
            "sport": "football",
            "league": "nfl",
            "player_id": player_id,
            "limit": 5
        })
        
        print(f"  API Success: {success}")
        if success:
            if result.get("ok"):
                print(f"  Result: SUCCESS - Got player data")
                player_data = result.get("data", {})
                profile = player_data.get("player_profile", {})
                if "athlete" in profile:
                    name = profile["athlete"].get("displayName", "Unknown")
                    print(f"  Player: {name}")
            else:
                print(f"  Result: FAILED - {result.get('message', 'Unknown error')}")
        else:
            print(f"  Result: API ERROR - {result}")

if __name__ == "__main__":
    found_mlb_players = test_mlb_roster_extraction()
    test_player_id_formats()
    
    print(f"\n{'='*40}")
    print(f"FINAL RESULT: {'SUCCESS' if found_mlb_players else 'FAILED'}")