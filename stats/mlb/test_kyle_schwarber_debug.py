#!/usr/bin/env python3
"""
Debug script to test Kyle Schwarber's recent 5 games
Player ID: 33712 (Kyle Schwarber, Philadelphia Phillies)

This script will test the ESPN MLB endpoints step by step to understand
why we're getting old games (March/April) instead of recent games (August).
"""

import requests
import json
from datetime import datetime
import pytz

def test_kyle_schwarber_endpoints():
    """Test all relevant ESPN endpoints for Kyle Schwarber"""
    
    player_id = "33712"
    base_url = f"https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/athletes/{player_id}"
    
    print("=" * 80)
    print("KYLE SCHWARBER MLB ENDPOINT DEBUG")
    print("=" * 80)
    print(f"Player ID: {player_id}")
    print(f"Base URL: {base_url}")
    print(f"Current Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Test player profile
    print("\n" + "=" * 50)
    print("STEP 1: PLAYER PROFILE")
    print("=" * 50)
    
    try:
        response = requests.get(base_url, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            player_data = response.json()
            print(f"Player Name: {player_data.get('displayName', 'Unknown')}")
            print(f"Team: {player_data.get('team', {}).get('displayName', 'Unknown')}")
            print(f"Position: {player_data.get('position', {}).get('displayName', 'Unknown')}")
            
            # Check available endpoints
            available_endpoints = []
            if "statistics" in player_data:
                available_endpoints.append("statistics")
            if "statisticslog" in player_data:
                available_endpoints.append("statisticslog")
            if "eventlog" in player_data:
                available_endpoints.append("eventlog")
            
            print(f"Available endpoints: {available_endpoints}")
        else:
            print(f"ERROR: {response.text}")
            return
            
    except Exception as e:
        print(f"ERROR: {e}")
        return
    
    # Step 2: Test eventlog (this should have recent games)
    print("\n" + "=" * 50)
    print("STEP 2: EVENTLOG (Recent Games)")
    print("=" * 50)
    
    eventlog_url = f"{base_url}/eventlog"
    print(f"Eventlog URL: {eventlog_url}")
    
    try:
        response = requests.get(eventlog_url, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            eventlog_data = response.json()
            events = eventlog_data.get("events", {})
            
            if isinstance(events, dict):
                total_events = events.get("count", 0)
                page_count = events.get("pageCount", 1)
                current_page = events.get("pageIndex", 1)
                items = events.get("items", [])
                
                print(f"Total Events: {total_events}")
                print(f"Total Pages: {page_count}")
                print(f"Current Page: {current_page}")
                print(f"Items on this page: {len(items)}")
                
                # Show first 5 events from page 1
                print(f"\nFirst 5 events from page 1:")
                for i, event_item in enumerate(items[:5]):
                    event_ref = event_item.get("event", {}).get("$ref", "No event ref")
                    stats_ref = event_item.get("statistics", {}).get("$ref", "No stats ref")
                    played = event_item.get("played", False)
                    
                    print(f"  Event {i+1}:")
                    print(f"    Played: {played}")
                    print(f"    Event Ref: {event_ref}")
                    print(f"    Stats Ref: {stats_ref}")
                
                # Test getting the LAST page (most recent games)
                if page_count > 1:
                    print(f"\n--- TESTING LAST PAGE ({page_count}) FOR RECENT GAMES ---")
                    last_page_url = f"{eventlog_url}?page={page_count}"
                    print(f"Last page URL: {last_page_url}")
                    
                    last_response = requests.get(last_page_url, timeout=15)
                    print(f"Last page status: {last_response.status_code}")
                    
                    if last_response.status_code == 200:
                        last_page_data = last_response.json()
                        last_events = last_page_data.get("events", {}).get("items", [])
                        
                        print(f"Events on last page: {len(last_events)}")
                        
                        # Show first 5 events from last page
                        print(f"First 5 events from last page (most recent):")
                        for i, event_item in enumerate(last_events[:5]):
                            event_ref = event_item.get("event", {}).get("$ref", "No event ref")
                            
                            # Get the actual event details to see the date
                            if event_ref and event_ref != "No event ref":
                                try:
                                    event_response = requests.get(event_ref, timeout=10)
                                    if event_response.status_code == 200:
                                        event_data = event_response.json()
                                        game_date = event_data.get("date", "Unknown date")
                                        
                                        # Convert to Eastern time
                                        try:
                                            utc_dt = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
                                            eastern = pytz.timezone('US/Eastern')
                                            et_dt = utc_dt.astimezone(eastern)
                                            eastern_time = et_dt.strftime("%m/%d/%Y %I:%M %p ET")
                                        except:
                                            eastern_time = game_date
                                        
                                        # Get opponent info
                                        competitors = event_data.get("competitions", [{}])[0].get("competitors", [])
                                        opponent = "vs Unknown"
                                        if len(competitors) >= 2:
                                            home_team = competitors[0].get("team", {}).get("displayName", "Home")
                                            away_team = competitors[1].get("team", {}).get("displayName", "Away")
                                            opponent = f"{away_team} @ {home_team}"
                                        
                                        print(f"  Event {i+1}: {eastern_time} - {opponent}")
                                    else:
                                        print(f"  Event {i+1}: Could not fetch event details")
                                except Exception as e:
                                    print(f"  Event {i+1}: Error getting event details: {e}")
                            else:
                                print(f"  Event {i+1}: No event reference")
            else:
                print(f"Unexpected events format: {type(events)}")
        else:
            print(f"ERROR: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Step 3: Test getting stats for one recent game
    print("\n" + "=" * 50)
    print("STEP 3: SAMPLE GAME STATS")
    print("=" * 50)
    
    # Try to get stats for the most recent game
    try:
        # Get last page again
        if page_count > 1:
            last_page_url = f"{eventlog_url}?page={page_count}"
            last_response = requests.get(last_page_url, timeout=15)
            
            if last_response.status_code == 200:
                last_page_data = last_response.json()
                last_events = last_page_data.get("events", {}).get("items", [])
                
                if last_events:
                    # Get stats for first event on last page
                    first_event = last_events[0]
                    stats_ref = first_event.get("statistics", {}).get("$ref")
                    
                    if stats_ref:
                        print(f"Testing stats URL: {stats_ref}")
                        
                        stats_response = requests.get(stats_ref, timeout=10)
                        print(f"Stats response status: {stats_response.status_code}")
                        
                        if stats_response.status_code == 200:
                            stats_data = stats_response.json()
                            
                            print(f"Stats data keys: {list(stats_data.keys())}")
                            
                            if "splits" in stats_data:
                                splits = stats_data["splits"]
                                print(f"Splits keys: {list(splits.keys())}")
                                
                                if "categories" in splits:
                                    categories = splits["categories"]
                                    print(f"Found {len(categories)} stat categories")
                                    
                                    for i, category in enumerate(categories):
                                        cat_name = category.get("name", f"Category {i}")
                                        stats = category.get("stats", [])
                                        print(f"  Category '{cat_name}': {len(stats)} stats")
                                        
                                        # Show first few stats
                                        for j, stat in enumerate(stats[:5]):
                                            stat_name = stat.get("name", "Unknown")
                                            stat_value = stat.get("value", 0)
                                            print(f"    {stat_name}: {stat_value}")
                                        
                                        if len(stats) > 5:
                                            print(f"    ... and {len(stats) - 5} more stats")
                            else:
                                print("No 'splits' in stats data")
                        else:
                            print(f"Stats request failed: {stats_response.text}")
                    else:
                        print("No stats reference found")
                else:
                    print("No events on last page")
            else:
                print("Could not get last page")
        else:
            print("Only one page available, checking first page for stats")
            
    except Exception as e:
        print(f"ERROR testing game stats: {e}")
    
    print("\n" + "=" * 80)
    print("DEBUG COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_kyle_schwarber_endpoints()