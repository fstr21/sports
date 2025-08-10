#!/usr/bin/env python3
"""
Simple debug of MCP server response.
"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sports_mcp'))

from interactive_sports_test import SportsTestInterface

def debug_mcp():
    interface = SportsTestInterface()
    interface.current_sport_league = ("basketball", "wnba")
    
    success, result = interface.make_request("POST", "/espn/player-stats", {
        "sport": "basketball",
        "league": "wnba",
        "player_id": "4433402",
        "limit": 3
    })
    
    if success and result.get("ok"):
        print("SUCCESS: MCP Server responded")
        
        data = result.get("data", {})
        print(f"Data keys: {list(data.keys())}")
        
        parsed_stats = data.get("parsed_statistics", {})
        print(f"Parsed stats: {parsed_stats}")
        
        # Save response
        with open("test/mcp_debug_response.json", 'w') as f:
            json.dump(result, f, indent=2)
        print("Response saved to test/mcp_debug_response.json")
        
    else:
        print(f"FAILED: {result}")

if __name__ == "__main__":
    debug_mcp()