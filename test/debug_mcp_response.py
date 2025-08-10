#!/usr/bin/env python3
"""
Debug what the MCP server is actually returning for Angel Reese.
"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sports_mcp'))

from interactive_sports_test import SportsTestInterface

def debug_mcp_response():
    """Debug the exact MCP server response"""
    print("DEBUG: MCP Server Response for Angel Reese")
    print("=" * 50)
    
    interface = SportsTestInterface()
    interface.current_sport_league = ("basketball", "wnba")
    
    success, result = interface.make_request("POST", "/espn/player-stats", {
        "sport": "basketball",
        "league": "wnba",
        "player_id": "4433402",
        "limit": 3
    })
    
    if success and result.get("ok"):
        print("✓ MCP Server call succeeded")
        
        # Save the full response
        filename = "test/mcp_server_response_debug.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"✓ Full response saved to: {filename}")
        
        # Check specific parts
        data = result.get("data", {})
        print(f"\nTop-level data keys: {list(data.keys())}")
        
        parsed_stats = data.get("parsed_statistics", {})
        print(f"Parsed statistics: {parsed_stats}")
        print(f"Number of parsed stats: {len(parsed_stats)}")
        
        # Check athlete season stats
        athlete = data.get("player_profile", {}).get("athlete", {})
        season_stats = athlete.get("season_stats", {})
        print(f"Athlete season stats: {season_stats}")
        print(f"Number of athlete season stats: {len(season_stats)}")
        
        # Check raw season data
        raw_season = data.get("season_stats", {})
        if raw_season:
            print(f"Raw season data keys: {list(raw_season.keys())}")
            if "splits" in raw_season:
                splits = raw_season["splits"]
                print(f"Splits data available: {type(splits)}")
                if isinstance(splits, dict) and "categories" in splits:
                    categories = splits["categories"]
                    print(f"Categories found: {len(categories)}")
        
        return True
    else:
        print(f"✗ MCP Server call failed: {result}")
        return False

if __name__ == "__main__":
    debug_mcp_response()