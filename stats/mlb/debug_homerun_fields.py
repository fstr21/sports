#!/usr/bin/env python3
"""
Debug what home run fields ESPN actually returns
"""

import requests

def debug_homerun_fields():
    """Check what home run fields are available in ESPN stats"""
    
    # Use the eventlog to get a valid stats URL
    player_id = "33712"
    eventlog_url = f"https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/athletes/{player_id}/eventlog?page=5"
    
    print("=" * 80)
    print("DEBUGGING HOME RUN FIELD NAMES")
    print("=" * 80)
    
    try:
        # Get the last page
        response = requests.get(eventlog_url, timeout=15)
        if response.status_code != 200:
            print(f"Error getting eventlog: {response.status_code}")
            return
        
        eventlog_data = response.json()
        events = eventlog_data.get("events", {}).get("items", [])
        
        if not events:
            print("No events found")
            return
        
        # Get stats for the most recent game with a home run (8/8 game)
        # Find the 8/8 game
        target_event = None
        for event in events:
            event_ref = event.get("event", {}).get("$ref")
            if event_ref:
                event_response = requests.get(event_ref, timeout=10)
                if event_response.status_code == 200:
                    event_data = event_response.json()
                    game_date = event_data.get("date", "")
                    if "2025-08-08" in game_date:  # 8/8 game
                        target_event = event
                        print(f"Found 8/8 game: {event_ref}")
                        break
        
        if not target_event:
            print("Could not find 8/8 game")
            return
        
        # Get stats for this game
        stats_ref = target_event.get("statistics", {}).get("$ref")
        if not stats_ref:
            print("No stats reference")
            return
        
        print(f"Getting stats from: {stats_ref}")
        stats_response = requests.get(stats_ref, timeout=15)
        
        if stats_response.status_code != 200:
            print(f"Stats error: {stats_response.status_code}")
            return
        
        stats_data = stats_response.json()
        
        if "splits" in stats_data and "categories" in stats_data["splits"]:
            categories = stats_data["splits"]["categories"]
            
            for category in categories:
                if category.get("name") == "batting":
                    batting_stats = category.get("stats", [])
                    
                    print(f"\nBATTING STATS FOR 8/8 GAME (should have 1 HR):")
                    print("=" * 50)
                    
                    homerun_fields = []
                    
                    for stat in batting_stats:
                        name = stat.get("name", "")
                        value = stat.get("value", 0)
                        display_value = stat.get("displayValue", "")
                        
                        # Look for ANY field containing "home" or "hr"
                        if "home" in name.lower() or "hr" in name.lower():
                            homerun_fields.append({
                                "name": name,
                                "value": value,
                                "display_value": display_value
                            })
                    
                    if homerun_fields:
                        print("HOME RUN RELATED FIELDS:")
                        for field in homerun_fields:
                            print(f"  📊 {field['name']}: value={field['value']}, display='{field['display_value']}'")
                    else:
                        print("❌ No home run fields found!")
                    
                    # Also show some reference stats
                    print(f"\nREFERENCE STATS:")
                    for stat in batting_stats:
                        name = stat.get("name", "")
                        value = stat.get("value", 0)
                        
                        if name.lower() in ["hits", "runs", "rbis", "strikeouts"]:
                            print(f"  ⚾ {name}: {value}")
                    
                    break
        else:
            print("No batting stats found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_homerun_fields()