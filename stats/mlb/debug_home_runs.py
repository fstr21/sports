#!/usr/bin/env python3
"""
Debug script to see what ESPN is returning for home runs
"""

import requests
import json

def debug_home_runs():
    """Debug what ESPN returns for home runs in Kyle Schwarber's recent games"""
    
    player_id = "33712"
    
    # Get a recent game with home runs (8/8 game)
    stats_url = "http://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/events/401696408/competitions/401696408/competitors/22/roster/33712/statistics/0?lang=en&region=us"
    
    print("=" * 80)
    print("DEBUGGING HOME RUN STATS")
    print("=" * 80)
    print(f"Testing stats URL: {stats_url}")
    
    try:
        response = requests.get(stats_url, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            stats_data = response.json()
            
            if "splits" in stats_data and "categories" in stats_data["splits"]:
                categories = stats_data["splits"]["categories"]
                
                for category in categories:
                    if category.get("name") == "batting":
                        batting_stats = category.get("stats", [])
                        
                        print(f"\nFound {len(batting_stats)} batting stats")
                        print("Looking for home run related stats:")
                        
                        for stat in batting_stats:
                            name = stat.get("name", "")
                            value = stat.get("value", 0)
                            display_value = stat.get("displayValue", "")
                            
                            # Look for anything related to home runs
                            if "home" in name.lower() or "hr" in name.lower():
                                print(f"  🏠 {name}: value={value}, displayValue='{display_value}'")
                            
                            # Also show hits and runs for comparison
                            elif name.lower() in ["hits", "runs", "rbis"]:
                                print(f"  ⚾ {name}: value={value}, displayValue='{display_value}'")
                        
                        # Show ALL stats to see what's available
                        print(f"\nALL BATTING STATS:")
                        for i, stat in enumerate(batting_stats):
                            name = stat.get("name", "")
                            value = stat.get("value", 0)
                            print(f"  {i+1:2d}. {name}: {value}")
                        
                        break
            else:
                print("No batting stats found")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_home_runs()