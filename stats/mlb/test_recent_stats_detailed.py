#!/usr/bin/env python3
"""
Detailed test of Kyle Schwarber's most recent games with actual stats extraction
"""

import requests
import json
from datetime import datetime
import pytz

def get_recent_games_with_stats():
    """Get Kyle Schwarber's most recent games with detailed stats"""
    
    player_id = "33712"
    base_url = f"https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/athletes/{player_id}"
    eventlog_url = f"{base_url}/eventlog"
    
    print("=" * 80)
    print("KYLE SCHWARBER - RECENT GAMES WITH DETAILED STATS")
    print("=" * 80)
    
    # Get the last page (most recent games)
    try:
        # First get page 1 to find total pages
        response = requests.get(eventlog_url, timeout=15)
        if response.status_code != 200:
            print(f"ERROR: Could not get eventlog: {response.status_code}")
            return
        
        eventlog_data = response.json()
        events = eventlog_data.get("events", {})
        total_pages = events.get("pageCount", 1)
        
        print(f"Total pages: {total_pages}")
        
        # Get the last page (most recent games)
        last_page_url = f"{eventlog_url}?page={total_pages}"
        print(f"Getting most recent games from: {last_page_url}")
        
        last_response = requests.get(last_page_url, timeout=15)
        if last_response.status_code != 200:
            print(f"ERROR: Could not get last page: {last_response.status_code}")
            return
        
        last_page_data = last_response.json()
        recent_events = last_page_data.get("events", {}).get("items", [])
        
        print(f"Found {len(recent_events)} events on last page")
        
        # Process the 5 most recent games
        recent_games = []
        
        for i, event_item in enumerate(recent_events[:5]):
            print(f"\n--- PROCESSING GAME {i+1} ---")
            
            event_ref = event_item.get("event", {}).get("$ref")
            stats_ref = event_item.get("statistics", {}).get("$ref")
            
            if not event_ref or not stats_ref:
                print("Missing event or stats reference")
                continue
            
            # Get game details
            event_response = requests.get(event_ref, timeout=10)
            if event_response.status_code != 200:
                print(f"Could not get event details: {event_response.status_code}")
                continue
            
            event_data = event_response.json()
            game_date = event_data.get("date", "Unknown")
            
            # Convert to Eastern time
            try:
                utc_dt = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
                eastern = pytz.timezone('US/Eastern')
                et_dt = utc_dt.astimezone(eastern)
                eastern_time = et_dt.strftime("%m/%d/%Y %I:%M %p ET")
            except:
                eastern_time = game_date
            
            # Get opponent
            competitors = event_data.get("competitions", [{}])[0].get("competitors", [])
            opponent = "vs Unknown"
            if len(competitors) >= 2:
                home_team = competitors[0].get("team", {}).get("displayName", "Home")
                away_team = competitors[1].get("team", {}).get("displayName", "Away")
                opponent = f"{away_team} @ {home_team}"
            
            print(f"Game: {eastern_time} - {opponent}")
            
            # Get player stats
            stats_response = requests.get(stats_ref, timeout=10)
            if stats_response.status_code != 200:
                print(f"Could not get stats: {stats_response.status_code}")
                continue
            
            stats_data = stats_response.json()
            
            # Extract batting stats
            game_stats = {}
            
            if "splits" in stats_data and "categories" in stats_data["splits"]:
                categories = stats_data["splits"]["categories"]
                
                for category in categories:
                    if category.get("name") == "batting":
                        batting_stats = category.get("stats", [])
                        
                        print(f"Found {len(batting_stats)} batting stats")
                        
                        # Extract key stats
                        key_stats = {}
                        for stat in batting_stats:
                            name = stat.get("name", "").lower()
                            value = stat.get("value", 0)
                            
                            if name == "hits":
                                key_stats["hits"] = value
                            elif name == "homeruns":
                                key_stats["homeruns"] = value
                            elif name == "rbi":
                                key_stats["rbis"] = value
                            elif name == "runs":
                                key_stats["runs"] = value
                            elif name == "strikeouts":
                                key_stats["strikeouts"] = value
                            elif name == "walks":
                                key_stats["walks"] = value
                            elif name == "atbats":
                                key_stats["atbats"] = value
                        
                        game_stats = key_stats
                        
                        # Show the key stats
                        print(f"Key Stats:")
                        for stat_name, stat_value in key_stats.items():
                            print(f"  {stat_name}: {stat_value}")
                        
                        # Show ALL batting stats for debugging
                        print(f"\nAll batting stats available:")
                        for stat in batting_stats[:10]:  # Show first 10
                            name = stat.get("name", "Unknown")
                            value = stat.get("value", 0)
                            print(f"  {name}: {value}")
                        
                        if len(batting_stats) > 10:
                            print(f"  ... and {len(batting_stats) - 10} more stats")
                        
                        break
            
            recent_games.append({
                "date": eastern_time,
                "opponent": opponent,
                "stats": game_stats
            })
        
        # Calculate averages
        print(f"\n" + "=" * 50)
        print("5-GAME AVERAGES")
        print("=" * 50)
        
        if recent_games:
            stat_totals = {}
            
            for game in recent_games:
                for stat_name, stat_value in game["stats"].items():
                    if stat_name not in stat_totals:
                        stat_totals[stat_name] = []
                    stat_totals[stat_name].append(float(stat_value))
            
            print(f"Games processed: {len(recent_games)}")
            for stat_name, values in stat_totals.items():
                if values:
                    avg = sum(values) / len(values)
                    print(f"{stat_name}: {avg:.1f} per game")
        
        # Save results
        output_data = {
            "player": "Kyle Schwarber",
            "player_id": player_id,
            "extraction_date": datetime.now().isoformat(),
            "recent_games": recent_games
        }
        
        with open("stats/mlb/Kyle_Schwarber_Recent_Debug.json", "w") as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\nResults saved to: stats/mlb/Kyle_Schwarber_Recent_Debug.json")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_recent_games_with_stats()