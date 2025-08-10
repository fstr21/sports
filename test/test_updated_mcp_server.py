#!/usr/bin/env python3
"""
Test the updated MCP server with fixed ESPN Core API implementation.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sports_mcp'))

from interactive_sports_test import SportsTestInterface

def test_updated_mcp_angel_reese():
    """Test Angel Reese through updated MCP server"""
    print("Testing Updated MCP Server - Angel Reese WNBA Stats")
    print("=" * 55)
    
    interface = SportsTestInterface()
    interface.current_sport_league = ("basketball", "wnba")
    
    # Test with Angel Reese
    player_id = "4433402"
    
    print(f"Testing player ID: {player_id} (Angel Reese)")
    print("Calling updated MCP server endpoint...")
    
    success, result = interface.make_request("POST", "/espn/player-stats", {
        "sport": "basketball",
        "league": "wnba",
        "player_id": player_id,
        "limit": 5
    })
    
    print(f"API Success: {success}")
    
    if success and result.get("ok"):
        print("SUCCESS! MCP server now working!")
        
        player_data = result.get("data", {})
        profile = player_data.get("player_profile", {})
        
        if "athlete" in profile:
            athlete = profile["athlete"]
            name = athlete.get("displayName", "Unknown")
            position = athlete.get("position", {}).get("abbreviation", "N/A")
            height = athlete.get("height", "Unknown")
            weight = athlete.get("weight", "Unknown")
            
            print(f"\nPlayer Profile:")
            print(f"  Name: {name}")
            print(f"  Position: {position}")
            print(f"  Height: {height}")
            print(f"  Weight: {weight}")
            
            # Check for parsed statistics
            season_stats = athlete.get("season_stats", {})
            if season_stats:
                print(f"\nSeason Statistics (Parsed):")
                basketball_order = ["Points", "Rebounds", "Assists", "3PM", "Steals", "Blocks", "FG%", "Minutes"]
                
                for stat_name in basketball_order:
                    if stat_name in season_stats:
                        print(f"  {stat_name:15}: {season_stats[stat_name]}")
            
            # Check parsed statistics at top level
            parsed_stats = player_data.get("parsed_statistics", {})
            if parsed_stats:
                print(f"\nParsed Statistics (Top Level):")
                for stat_name, value in parsed_stats.items():
                    print(f"  {stat_name:15}: {value}")
            
            # Check recent games
            recent_games = player_data.get("recent_games", {}).get("events", [])
            print(f"\nRecent Games: {len(recent_games)} games found")
            
            return True
        else:
            print("No athlete data found in profile")
            return False
            
    elif success:
        error = result.get("message", "Unknown error")
        print(f"MCP Server Error: {error}")
        return False
    else:
        print(f"API Call Failed: {result}")
        return False

def test_multiple_sports():
    """Test the updated MCP server across multiple sports"""
    print(f"\n{'='*55}")
    print("Testing Multiple Sports Through Updated MCP Server")
    print("=" * 55)
    
    interface = SportsTestInterface()
    
    # Test cases: (sport, league, player_id, player_name)
    test_cases = [
        ("basketball", "nba", "1966", "LeBron James"),  # NBA
        ("football", "nfl", "4361093", "Kyler Gordon"),  # NFL (from our extraction)
        ("baseball", "mlb", "32655", "Byron Buxton"),   # MLB (from our extraction)
    ]
    
    results = {}
    
    for sport, league, player_id, name in test_cases:
        print(f"\nTesting {sport.upper()}: {name} (ID: {player_id})")
        interface.current_sport_league = (sport, league)
        
        success, result = interface.make_request("POST", "/espn/player-stats", {
            "sport": sport,
            "league": league,
            "player_id": player_id,
            "limit": 3
        })
        
        if success and result.get("ok"):
            player_data = result.get("data", {})
            parsed_stats = player_data.get("parsed_statistics", {})
            
            print(f"  SUCCESS! Found {len(parsed_stats)} parsed stats")
            
            # Show a few stats
            stats_shown = 0
            for stat_name, value in list(parsed_stats.items())[:3]:
                print(f"    {stat_name}: {value}")
                stats_shown += 1
            
            if len(parsed_stats) > 3:
                print(f"    ... and {len(parsed_stats) - 3} more stats")
            
            results[f"{sport}/{league}"] = True
            
        elif success:
            error = result.get("message", "Unknown error")
            print(f"  FAILED: {error}")
            results[f"{sport}/{league}"] = False
        else:
            print(f"  API ERROR: {result}")
            results[f"{sport}/{league}"] = False
    
    return results

if __name__ == "__main__":
    print("TESTING UPDATED MCP SERVER WITH FIXED ESPN CORE API")
    print("=" * 60)
    
    # Test Angel Reese specifically
    angel_success = test_updated_mcp_angel_reese()
    
    # Test multiple sports
    multi_results = test_multiple_sports()
    
    # Summary
    print(f"\n{'='*60}")
    print("FINAL RESULTS:")
    print(f"Angel Reese WNBA: {'SUCCESS' if angel_success else 'FAILED'}")
    
    for sport, success in multi_results.items():
        print(f"{sport:<15}: {'SUCCESS' if success else 'FAILED'}")
    
    total_success = sum(multi_results.values()) + (1 if angel_success else 0)
    total_tests = len(multi_results) + 1
    
    print(f"\nOverall: {total_success}/{total_tests} tests passed")
    
    if total_success == total_tests:
        print("🎉 ALL TESTS PASSED - MCP SERVER FULLY FIXED!")
    else:
        print("⚠️ Some tests failed - needs further debugging")