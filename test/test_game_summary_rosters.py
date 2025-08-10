#!/usr/bin/env python3
"""
Test getting player rosters from ESPN game summary endpoint.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sports_mcp'))

from interactive_sports_test import SportsTestInterface

def test_game_summary_rosters():
    """Test getting player rosters from game summary"""
    print("Testing Game Summary for Player Rosters...")
    
    interface = SportsTestInterface()
    interface.current_sport_league = ("football", "nfl")
    
    # First get today's games to get an event ID
    print("1. Getting today's NFL games for event IDs...")
    success, result = interface.make_request("POST", "/espn/scoreboard", {
        "sport": "football",
        "league": "nfl"
    })
    
    if not success or not result.get("ok"):
        print(f"Failed to get games: {result}")
        return False
    
    games = result.get("data", {}).get("scoreboard", [])
    print(f"Found {len(games)} games")
    
    if not games:
        print("No games to test with")
        return False
    
    # Get the first game's event ID
    game = games[0]
    event_id = game.get("id")
    game_name = game.get("name", "Unknown vs Unknown")
    
    print(f"2. Testing game summary for: {game_name} (ID: {event_id})")
    
    # Get game summary
    success, result = interface.make_request("POST", "/espn/game-summary", {
        "sport": "football", 
        "league": "nfl",
        "event_id": event_id
    })
    
    if not success or not result.get("ok"):
        print(f"Failed to get game summary: {result}")
        return False
    
    summary_data = result.get("data", {})
    print(f"3. Game summary data keys: {list(summary_data.keys()) if summary_data else 'None'}")
    
    # Look for roster information in various places
    roster_sources = [
        "rosters",
        "boxscore", 
        "players",
        "teams",
        "header"
    ]
    
    found_players = []
    
    for source in roster_sources:
        if source in summary_data:
            print(f"\n   Found '{source}' in summary data")
            data = summary_data[source]
            
            if source == "boxscore":
                # Boxscore often contains player stats
                if "players" in data:
                    players_data = data["players"]
                    print(f"      Boxscore has players data: {type(players_data)}")
                    
                    if isinstance(players_data, list):
                        for i, team_players in enumerate(players_data):
                            if isinstance(team_players, dict) and "statistics" in team_players:
                                stats = team_players["statistics"]
                                print(f"      Team {i+1} has {len(stats)} stat categories")
                                
                                for stat_category in stats:
                                    if "athletes" in stat_category:
                                        athletes = stat_category["athletes"]
                                        print(f"        Found {len(athletes)} athletes in {stat_category.get('name', 'category')}")
                                        
                                        if athletes and len(found_players) < 5:  # Just collect first 5 as examples
                                            for athlete in athletes[:3]:  # First 3 from this category
                                                if "athlete" in athlete:
                                                    player_info = athlete["athlete"]
                                                    player_id = player_info.get("id")
                                                    player_name = player_info.get("displayName", "Unknown")
                                                    position = player_info.get("position", {}).get("abbreviation", "N/A")
                                                    
                                                    found_players.append({
                                                        "id": player_id,
                                                        "name": player_name, 
                                                        "position": position,
                                                        "source": f"boxscore.{stat_category.get('name', 'stats')}"
                                                    })
            
            elif source == "rosters":
                print(f"      Rosters data type: {type(data)}")
                if isinstance(data, list):
                    for team_roster in data:
                        if "roster" in team_roster:
                            roster = team_roster["roster"]
                            print(f"        Team roster has {len(roster) if isinstance(roster, list) else 'non-list'} players")
    
    # Display found players
    print(f"\n4. Found {len(found_players)} players total:")
    for i, player in enumerate(found_players[:10], 1):  # Show first 10
        print(f"   {i}. {player['name']} ({player['position']}) - ID: {player['id']} [from {player['source']}]")
    
    return len(found_players) > 0

def test_different_sports():
    """Test roster extraction across different sports"""
    print("\n" + "="*60)
    print("Testing Roster Extraction Across Sports")
    print("="*60)
    
    interface = SportsTestInterface()
    
    sports_to_test = [
        ("basketball", "nba", "NBA"),
        ("baseball", "mlb", "MLB"),
        ("hockey", "nhl", "NHL")
    ]
    
    for sport, league, name in sports_to_test:
        print(f"\nTesting {name}...")
        interface.current_sport_league = (sport, league)
        
        # Get games
        success, result = interface.make_request("POST", "/espn/scoreboard", {
            "sport": sport,
            "league": league  
        })
        
        if success and result.get("ok"):
            games = result.get("data", {}).get("scoreboard", [])
            print(f"  Found {len(games)} {name} games")
            
            if games:
                event_id = games[0].get("id")
                print(f"  Game ID for testing: {event_id}")
        else:
            print(f"  No {name} games available")

if __name__ == "__main__":
    success = test_game_summary_rosters()
    test_different_sports()
    
    print(f"\n{'='*40}")
    print(f"RESULT: {'SUCCESS' if success else 'FAILED'} - Found player rosters from game summary")