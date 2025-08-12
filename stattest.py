#!/usr/bin/env python3
"""
ESPN API Debug Test - Find the correct data structure
"""

import requests
import json
from datetime import datetime

# Test with one player first
PLAYER_ID = "40803"  # Brandon Marsh
PLAYER_NAME = "Brandon Marsh"

def debug_espn_api():
    """Debug ESPN API to understand the data structure"""
    print(f"ESPN API STRUCTURE DEBUG")
    print(f"Player: {PLAYER_NAME} (ID: {PLAYER_ID})")
    print("=" * 70)
    
    # Step 1: Get eventlog
    eventlog_url = f"https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/athletes/{PLAYER_ID}/eventlog"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"\n1. Fetching eventlog...")
    print(f"   URL: {eventlog_url}")
    
    response = requests.get(eventlog_url, headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print("   ERROR: Could not fetch eventlog")
        return
    
    eventlog_data = response.json()
    
    # Analyze the structure
    print(f"\n2. Eventlog Structure:")
    print(f"   Keys: {list(eventlog_data.keys())}")
    
    # Save to file for inspection
    with open("eventlog_debug.json", "w") as f:
        json.dump(eventlog_data, f, indent=2)
    print("   Saved full response to eventlog_debug.json")
    
    # Check different possible structures
    if "items" in eventlog_data:
        print(f"   Found 'items' directly: {len(eventlog_data['items'])} items")
        events = eventlog_data["items"]
    elif "events" in eventlog_data:
        events_data = eventlog_data["events"]
        print(f"   Found 'events' object")
        print(f"   Events keys: {list(events_data.keys())}")
        
        # Check if events has a $ref
        if "$ref" in events_data:
            events_url = events_data["$ref"]
            print(f"\n3. Following events $ref...")
            print(f"   URL: {events_url}")
            
            events_response = requests.get(events_url, headers=headers, timeout=10)
            print(f"   Status: {events_response.status_code}")
            
            if events_response.status_code == 200:
                events_json = events_response.json()
                print(f"   Events response keys: {list(events_json.keys())}")
                
                # Save events response
                with open("events_debug.json", "w") as f:
                    json.dump(events_json, f, indent=2)
                print("   Saved events response to events_debug.json")
                
                if "items" in events_json:
                    events = events_json["items"]
                    print(f"   Found {len(events)} items in events")
                else:
                    print("   No 'items' in events response")
                    events = []
            else:
                print("   ERROR: Could not fetch events")
                events = []
        else:
            events = []
    else:
        print("   No 'items' or 'events' found in eventlog")
        events = []
    
    # Process first few events
    if events:
        print(f"\n4. Processing first 3 events...")
        
        for i, event in enumerate(events[:3]):
            print(f"\n   Event {i+1}:")
            print(f"   Keys: {list(event.keys())}")
            
            if "$ref" in event:
                event_url = event["$ref"]
                print(f"   Following event $ref: {event_url}")
                
                event_response = requests.get(event_url, headers=headers, timeout=10)
                if event_response.status_code == 200:
                    event_data = event_response.json()
                    
                    # Save first event for detailed inspection
                    if i == 0:
                        with open("first_event_debug.json", "w") as f:
                            json.dump(event_data, f, indent=2)
                        print("   Saved first event to first_event_debug.json")
                    
                    print(f"   Event data keys: {list(event_data.keys())}")
                    
                    # Extract key information
                    if "gameDate" in event_data:
                        print(f"   Game date: {event_data['gameDate']}")
                    if "id" in event_data:
                        print(f"   Game ID: {event_data['id']}")
                    
                    # Check for statistics
                    if "statistics" in event_data:
                        stats = event_data["statistics"]
                        print(f"   Has statistics: {type(stats)}")
                        if isinstance(stats, dict) and "$ref" in stats:
                            print(f"   Statistics $ref: {stats['$ref']}")
                            
                            # Fetch stats
                            stats_response = requests.get(stats["$ref"], headers=headers, timeout=10)
                            if stats_response.status_code == 200:
                                stats_data = stats_response.json()
                                
                                # Save stats for inspection
                                if i == 0:
                                    with open("first_stats_debug.json", "w") as f:
                                        json.dump(stats_data, f, indent=2)
                                    print("   Saved first game stats to first_stats_debug.json")
                                
                                # Look for batting stats
                                if "splits" in stats_data:
                                    splits = stats_data["splits"]
                                    if "categories" in splits:
                                        for category in splits["categories"]:
                                            if category.get("name", "").lower() == "batting":
                                                print("   Found batting category!")
                                                batting_stats = {}
                                                for stat in category.get("stats", []):
                                                    stat_name = stat.get("name", "").lower()
                                                    stat_value = stat.get("value", 0)
                                                    if stat_name in ["hits", "homeruns", "home runs", "hr"]:
                                                        batting_stats[stat_name] = stat_value
                                                print(f"   Batting stats: {batting_stats}")
                else:
                    print(f"   ERROR fetching event: {event_response.status_code}")
    
    print("\n5. Summary:")
    print("   Check the saved JSON files to see the complete structure:")
    print("   - eventlog_debug.json: Initial eventlog response")
    print("   - events_debug.json: Events list (if applicable)")
    print("   - first_event_debug.json: First game event details")
    print("   - first_stats_debug.json: First game statistics")

if __name__ == "__main__":
    debug_espn_api()