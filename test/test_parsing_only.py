#!/usr/bin/env python3
"""
Test just the parsing function.
"""
import json

def parse_espn_statistics(splits_data, sport):
    """Parse ESPN statistics from splits.categories.stats structure for any sport"""
    stats_found = {}
    
    if not isinstance(splits_data, dict) or "categories" not in splits_data:
        return stats_found
    
    categories = splits_data["categories"]
    
    for category in categories:
        stats = category.get("stats", [])
        
        for stat in stats:
            name = stat.get("name", "").lower()
            display_value = stat.get("displayValue", str(stat.get("value", 0)))
            
            # Map to sport-specific stats based on specification
            if sport == "basketball":
                # Basketball: Points, Rebounds, Assists, 3PM, Steals, Blocks, FG%, Minutes
                if name == "points":
                    stats_found["Points"] = display_value
                elif name == "rebounds":
                    stats_found["Rebounds"] = display_value  
                elif name == "assists":
                    stats_found["Assists"] = display_value
                elif name == "steals":
                    stats_found["Steals"] = display_value
                elif name == "blocks":
                    stats_found["Blocks"] = display_value
                elif "threepointfieldgoalsmade" in name.replace(" ", ""):
                    stats_found["3PM"] = display_value
                elif "fieldgoalpercentage" in name.replace(" ", ""):
                    stats_found["FG%"] = display_value
                elif name == "minutes":
                    stats_found["Minutes"] = display_value
    
    return stats_found

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
            
            # Show what stats are available
            categories = splits["categories"]
            print(f"\nAvailable stats:")
            for category in categories:
                cat_name = category.get("name", "Unknown")
                stats = category.get("stats", [])
                print(f"  {cat_name}: {len(stats)} stats")
                
                for stat in stats[:5]:  # First 5
                    name = stat.get("name", "Unknown")
                    value = stat.get("displayValue", stat.get("value", "N/A"))
                    print(f"    {name}: {value}")

if __name__ == "__main__":
    test_parsing()