#!/usr/bin/env python3
"""
Test the parsing function directly on the MCP response data.
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import the parsing function from the HTTP server
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from sports_http_server import parse_espn_statistics

def test_parsing():
    print("Testing ESPN Statistics Parsing Function")
    print("=" * 45)
    
    # Load the MCP response
    with open("test/mcp_debug_response.json", 'r') as f:
        response_data = json.load(f)
    
    # Extract the splits data
    season_stats = response_data["data"]["season_stats"]
    
    if "splits" in season_stats:
        splits = season_stats["splits"]
        print(f"Found splits data: {splits.get('name', 'Unknown')}")
        print(f"Splits keys: {list(splits.keys())}")
        
        # Test the parsing function
        parsed_stats = parse_espn_statistics(splits, "basketball")
        
        print(f"\nParsing Results:")
        print(f"Number of stats parsed: {len(parsed_stats)}")
        
        if parsed_stats:
            print(f"Parsed statistics:")
            for stat_name, value in parsed_stats.items():
                print(f"  {stat_name:15}: {value}")
        else:
            print("No statistics were parsed!")
            
            # Debug why
            if "categories" in splits:
                categories = splits["categories"]
                print(f"\nDebugging - found {len(categories)} categories:")
                
                for i, category in enumerate(categories):
                    cat_name = category.get("name", "Unknown")
                    stats = category.get("stats", [])
                    print(f"  Category {i+1}: {cat_name} ({len(stats)} stats)")
                    
                    # Show first few stats
                    for j, stat in enumerate(stats[:3]):
                        name = stat.get("name", "Unknown")
                        value = stat.get("displayValue", stat.get("value", "N/A"))
                        print(f"    {name}: {value}")
            else:
                print("No categories found in splits!")
    else:
        print("No splits found in season stats!")
        print(f"Season stats keys: {list(season_stats.keys())}")

if __name__ == "__main__":
    test_parsing()