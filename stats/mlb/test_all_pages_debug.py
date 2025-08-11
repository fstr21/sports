#!/usr/bin/env python3
"""
Check ALL pages of Kyle Schwarber's eventlog to find the most recent games
"""

import requests
from datetime import datetime
import pytz

def check_all_eventlog_pages():
    """Check every page of the eventlog to find the most recent games"""
    
    player_id = "33712"
    eventlog_url = f"https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/athletes/{player_id}/eventlog"
    
    print("=" * 80)
    print("CHECKING ALL EVENTLOG PAGES FOR MOST RECENT GAMES")
    print("=" * 80)
    
    try:
        # Get page 1 to find total pages
        response = requests.get(eventlog_url, timeout=15)
        if response.status_code != 200:
            print(f"ERROR: {response.status_code}")
            return
        
        eventlog_data = response.json()
        events = eventlog_data.get("events", {})
        total_pages = events.get("pageCount", 1)
        total_events = events.get("count", 0)
        
        print(f"Total events: {total_events}")
        print(f"Total pages: {total_pages}")
        
        # Check each page and show the date range
        all_dates = []
        
        for page in range(1, total_pages + 1):
            page_url = eventlog_url if page == 1 else f"{eventlog_url}?page={page}"
            
            page_response = requests.get(page_url, timeout=15)
            if page_response.status_code != 200:
                print(f"Page {page}: ERROR {page_response.status_code}")
                continue
            
            page_data = page_response.json()
            page_events = page_data.get("events", {}).get("items", [])
            
            if not page_events:
                print(f"Page {page}: No events")
                continue
            
            # Get dates for first and last event on this page
            first_event = page_events[0]
            last_event = page_events[-1]
            
            first_date = get_event_date(first_event.get("event", {}).get("$ref"))
            last_date = get_event_date(last_event.get("event", {}).get("$ref"))
            
            all_dates.extend([first_date, last_date])
            
            print(f"Page {page}: {len(page_events)} events | {first_date} to {last_date}")
        
        # Find the absolute most recent date
        valid_dates = [d for d in all_dates if d and d != "Unknown"]
        if valid_dates:
            print(f"\nMost recent game found: {max(valid_dates)}")
            print(f"Oldest game found: {min(valid_dates)}")
        
        # Also check if there might be a "current season" or "recent" endpoint
        print(f"\n" + "=" * 50)
        print("CHECKING ALTERNATIVE ENDPOINTS")
        print("=" * 50)
        
        # Try statisticslog (might have more recent data)
        base_url = f"https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/athletes/{player_id}"
        statslog_url = f"{base_url}/statisticslog"
        
        print(f"Trying statisticslog: {statslog_url}")
        statslog_response = requests.get(statslog_url, timeout=15)
        print(f"Statisticslog status: {statslog_response.status_code}")
        
        if statslog_response.status_code == 200:
            statslog_data = statslog_response.json()
            entries = statslog_data.get("entries", [])
            print(f"Statisticslog entries: {len(entries)}")
            
            if entries:
                # Check first few entries for dates
                for i, entry in enumerate(entries[:3]):
                    event_ref = entry.get("event", {}).get("$ref")
                    if event_ref:
                        event_date = get_event_date(event_ref)
                        print(f"  Entry {i+1}: {event_date}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

def get_event_date(event_ref):
    """Get the date from an event reference"""
    if not event_ref:
        return "Unknown"
    
    try:
        response = requests.get(event_ref, timeout=10)
        if response.status_code == 200:
            event_data = response.json()
            game_date = event_data.get("date", "Unknown")
            
            if game_date != "Unknown":
                # Convert to Eastern time
                try:
                    utc_dt = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
                    eastern = pytz.timezone('US/Eastern')
                    et_dt = utc_dt.astimezone(eastern)
                    return et_dt.strftime("%m/%d/%Y")
                except:
                    return game_date
        return "Unknown"
    except:
        return "Unknown"

if __name__ == "__main__":
    check_all_eventlog_pages()