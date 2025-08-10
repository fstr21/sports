#!/usr/bin/env python3
"""
Deep dive analysis of ESPN boxscore structure to find player data.
"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sports_mcp'))

from interactive_sports_test import SportsTestInterface

def analyze_nfl_boxscore():
    """Analyze NFL boxscore structure in detail"""
    print("DEEP ANALYSIS: NFL Boxscore Structure")
    print("="*50)
    
    interface = SportsTestInterface()
    interface.current_sport_league = ("football", "nfl")
    
    # Get games
    success, result = interface.make_request("POST", "/espn/scoreboard", {
        "sport": "football", 
        "league": "nfl"
    })
    
    if not success or not result.get("ok"):
        print("Failed to get NFL games")
        return False
    
    games = result.get("data", {}).get("scoreboard", [])
    if not games:
        print("No NFL games found")
        return False
    
    event_id = games[0].get("id")
    game_name = games[0].get("name")
    
    print(f"Analyzing: {game_name}")
    print(f"Event ID: {event_id}")
    
    # Get detailed game summary
    success, result = interface.make_request("POST", "/espn/game-summary", {
        "sport": "football",
        "league": "nfl", 
        "event_id": event_id
    })
    
    if not success or not result.get("ok"):
        print("Failed to get game summary")
        return False
    
    data = result.get("data", {})
    
    print(f"\nTop-level keys: {list(data.keys())}")
    
    # Focus on boxscore
    if "boxscore" in data:
        boxscore = data["boxscore"]
        print(f"\nBoxscore type: {type(boxscore)}")
        print(f"Boxscore keys: {list(boxscore.keys()) if isinstance(boxscore, dict) else 'Not dict'}")
        
        if isinstance(boxscore, dict) and "players" in boxscore:
            players_data = boxscore["players"]
            print(f"\nPlayers data type: {type(players_data)}")
            print(f"Players data length: {len(players_data) if isinstance(players_data, list) else 'Not list'}")
            
            if isinstance(players_data, list):
                for team_idx, team_data in enumerate(players_data):
                    print(f"\n--- TEAM {team_idx + 1} ---")
                    print(f"Team data type: {type(team_data)}")
                    print(f"Team data keys: {list(team_data.keys()) if isinstance(team_data, dict) else 'Not dict'}")
                    
                    if isinstance(team_data, dict):
                        # Look at team info
                        if "team" in team_data:
                            team_info = team_data["team"]
                            team_name = team_info.get("displayName", "Unknown Team")
                            print(f"Team name: {team_name}")
                        
                        # Look at statistics
                        if "statistics" in team_data:
                            stats = team_data["statistics"]
                            print(f"Statistics type: {type(stats)}")
                            print(f"Statistics length: {len(stats) if isinstance(stats, list) else 'Not list'}")
                            
                            if isinstance(stats, list):
                                for stat_idx, stat_group in enumerate(stats):
                                    print(f"\n  Stat Group {stat_idx + 1}:")
                                    print(f"    Type: {type(stat_group)}")
                                    print(f"    Keys: {list(stat_group.keys()) if isinstance(stat_group, dict) else 'Not dict'}")
                                    
                                    if isinstance(stat_group, dict):
                                        name = stat_group.get("name", "Unknown")
                                        print(f"    Name: {name}")
                                        
                                        if "athletes" in stat_group:
                                            athletes = stat_group["athletes"]
                                            print(f"    Athletes count: {len(athletes) if isinstance(athletes, list) else 'Not list'}")
                                            
                                            if isinstance(athletes, list) and athletes:
                                                athlete = athletes[0]
                                                print(f"    First athlete keys: {list(athlete.keys()) if isinstance(athlete, dict) else 'Not dict'}")
                                                
                                                if isinstance(athlete, dict) and "athlete" in athlete:
                                                    athlete_info = athlete["athlete"]
                                                    player_name = athlete_info.get("displayName", "Unknown")
                                                    player_id = athlete_info.get("id")
                                                    position = athlete_info.get("position", {}).get("abbreviation", "N/A")
                                                    print(f"    FOUND PLAYER: {player_name} (ID: {player_id}, Pos: {position})")
                                                    
                                                    return True  # Found at least one player
    
    return False

def save_full_structure():
    """Save full boxscore structure to file for analysis"""
    print("\n" + "="*50)
    print("SAVING FULL STRUCTURE TO FILE")
    print("="*50)
    
    interface = SportsTestInterface()
    interface.current_sport_league = ("football", "nfl")
    
    # Get games
    success, result = interface.make_request("POST", "/espn/scoreboard", {
        "sport": "football",
        "league": "nfl"
    })
    
    if success and result.get("ok"):
        games = result.get("data", {}).get("scoreboard", [])
        if games:
            event_id = games[0].get("id")
            
            # Get game summary
            success, result = interface.make_request("POST", "/espn/game-summary", {
                "sport": "football",
                "league": "nfl",
                "event_id": event_id
            })
            
            if success and result.get("ok"):
                data = result.get("data", {})
                
                # Save to file
                filename = f"test/nfl_game_summary_{event_id}.json"
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                
                print(f"Saved full game summary to: {filename}")
                print(f"File size: {os.path.getsize(filename)} bytes")
                return True
    
    return False

if __name__ == "__main__":
    found_players = analyze_nfl_boxscore()
    saved_file = save_full_structure()
    
    print(f"\n{'='*40}")
    print(f"ANALYSIS RESULTS:")
    print(f"Found players in boxscore: {'YES' if found_players else 'NO'}")  
    print(f"Saved structure to file: {'YES' if saved_file else 'NO'}")