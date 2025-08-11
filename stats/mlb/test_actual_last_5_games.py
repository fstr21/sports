#!/usr/bin/env python3
"""
Test script to get Kyle Schwarber's ACTUAL last 5 games (should be Aug 4-9, 2025)
This will confirm we can get the right games before updating the server.
"""

import requests
import json
from datetime import datetime
import pytz

def get_actual_last_5_games():
    """Get Kyle Schwarber's actual last 5 games with correct dates"""
    
    player_id = "33712"
    base_url = f"https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/athletes/{player_id}"
    eventlog_url = f"{base_url}/eventlog"
    
    print("=" * 80)
    print("KYLE SCHWARBER - ACTUAL LAST 5 GAMES TEST")
    print("Expected dates: Aug 9, Aug 8, Aug 6, Aug 5, Aug 4")
    print("=" * 80)
    
    try:
        # Get page 1 to find total pages
        response = requests.get(eventlog_url, timeout=15)
        if response.status_code != 200:
            print(f"ERROR: Could not get eventlog: {response.status_code}")
            return
        
        eventlog_data = response.json()
        events = eventlog_data.get("events", {})
        total_pages = events.get("pageCount", 1)
        
        print(f"Total pages: {total_pages}")
        
        # Get the last page
        last_page_url = f"{eventlog_url}?page={total_pages}"
        print(f"Getting last page: {last_page_url}")
        
        last_response = requests.get(last_page_url, timeout=15)
        if last_response.status_code != 200:
            print(f"ERROR: Could not get last page: {last_response.status_code}")
            return
        
        last_page_data = last_response.json()
        last_page_events = last_page_data.get("events", {}).get("items", [])
        
        print(f"Events on last page: {len(last_page_events)}")
        
        # Get ALL events from the last page and sort by date
        all_games_with_dates = []
        
        print(f"\nProcessing all {len(last_page_events)} events on last page...")
        
        for i, event_item in enumerate(last_page_events):
            event_ref = event_item.get("event", {}).get("$ref")
            stats_ref = event_item.get("statistics", {}).get("$ref")
            
            if not event_ref:
                continue
            
            # Get event details for date
            try:
                event_response = requests.get(event_ref, timeout=10)
                if event_response.status_code == 200:
                    event_data = event_response.json()
                    game_date = event_data.get("date", "")
                    
                    if game_date:
                        # Convert to Eastern time
                        utc_dt = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
                        eastern = pytz.timezone('US/Eastern')
                        et_dt = utc_dt.astimezone(eastern)
                        
                        # Get opponent info
                        competitors = event_data.get("competitions", [{}])[0].get("competitors", [])
                        opponent = "vs Unknown"
                        if len(competitors) >= 2:
                            home_team = competitors[0].get("team", {}).get("displayName", "Home")
                            away_team = competitors[1].get("team", {}).get("displayName", "Away")
                            opponent = f"{away_team} @ {home_team}"
                        
                        all_games_with_dates.append({
                            "datetime_obj": et_dt,
                            "eastern_time": et_dt.strftime("%m/%d/%Y %I:%M %p ET"),
                            "short_date": et_dt.strftime("%a %m/%d"),
                            "opponent": opponent,
                            "event_ref": event_ref,
                            "stats_ref": stats_ref
                        })
                        
                        print(f"  Event {i+1}: {et_dt.strftime('%a %m/%d')} - {opponent}")
                
            except Exception as e:
                print(f"  Event {i+1}: Error getting date - {e}")
                continue
        
        # Sort by date (most recent first)
        all_games_with_dates.sort(key=lambda x: x["datetime_obj"], reverse=True)
        
        print(f"\n" + "=" * 50)
        print("ALL GAMES SORTED BY DATE (MOST RECENT FIRST)")
        print("=" * 50)
        
        for i, game in enumerate(all_games_with_dates):
            print(f"{i+1:2d}. {game['short_date']} - {game['opponent']}")
        
        # Get the actual last 5 games
        last_5_games = all_games_with_dates[:5]
        
        print(f"\n" + "=" * 50)
        print("LAST 5 GAMES WITH STATS")
        print("=" * 50)
        
        games_with_stats = []
        
        for i, game in enumerate(last_5_games):
            print(f"\n--- GAME {i+1}: {game['short_date']} ---")
            print(f"Date: {game['eastern_time']}")
            print(f"Opponent: {game['opponent']}")
            
            # Get stats if available
            if game['stats_ref']:
                try:
                    stats_response = requests.get(game['stats_ref'], timeout=10)
                    if stats_response.status_code == 200:
                        stats_data = stats_response.json()
                        
                        # Extract batting stats
                        game_stats = {}
                        
                        if "splits" in stats_data and "categories" in stats_data["splits"]:
                            categories = stats_data["splits"]["categories"]
                            
                            for category in categories:
                                if category.get("name") == "batting":
                                    batting_stats = category.get("stats", [])
                                    
                                    # Extract key stats
                                    for stat in batting_stats:
                                        name = stat.get("name", "").lower()
                                        value = stat.get("value", 0)
                                        
                                        if name == "hits":
                                            game_stats["hits"] = value
                                        elif name == "homeruns":
                                            game_stats["homeruns"] = value
                                        elif name.lower() == "rbis":  # ESPN uses "RBIs"
                                            game_stats["rbis"] = value
                                        elif name == "runs":
                                            game_stats["runs"] = value
                                        elif name == "strikeouts":
                                            game_stats["strikeouts"] = value
                                        elif name == "walks":
                                            game_stats["walks"] = value
                                    
                                    break
                        
                        print(f"Stats: {game_stats}")
                        
                        games_with_stats.append({
                            "date": game['short_date'],
                            "eastern_time": game['eastern_time'],
                            "opponent": game['opponent'],
                            "stats": game_stats
                        })
                        
                    else:
                        print(f"Could not get stats: {stats_response.status_code}")
                        
                except Exception as e:
                    print(f"Error getting stats: {e}")
            else:
                print("No stats reference available")
        
        # Calculate 5-game averages
        print(f"\n" + "=" * 50)
        print("5-GAME AVERAGES")
        print("=" * 50)
        
        if games_with_stats:
            stat_totals = {}
            
            for game in games_with_stats:
                for stat_name, stat_value in game["stats"].items():
                    if stat_name not in stat_totals:
                        stat_totals[stat_name] = []
                    stat_totals[stat_name].append(float(stat_value))
            
            print(f"Games with stats: {len(games_with_stats)}")
            for stat_name, values in stat_totals.items():
                if values:
                    avg = sum(values) / len(values)
                    print(f"  {stat_name}: {avg:.1f} per game")
        
        # Save results
        output_data = {
            "player": "Kyle Schwarber",
            "player_id": player_id,
            "extraction_date": datetime.now().isoformat(),
            "last_5_games": games_with_stats,
            "verification": "These should be Aug 4-9, 2025 games"
        }
        
        with open("stats/mlb/Kyle_Schwarber_Actual_Last_5.json", "w") as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\nResults saved to: stats/mlb/Kyle_Schwarber_Actual_Last_5.json")
        
        # Final verification
        print(f"\n" + "=" * 50)
        print("VERIFICATION")
        print("=" * 50)
        
        expected_dates = ["Sat 8/9", "Fri 8/8", "Wed 8/6", "Tue 8/5", "Mon 8/4"]
        actual_dates = [game["date"] for game in games_with_stats]
        
        print("Expected dates:", expected_dates)
        print("Actual dates:  ", actual_dates)
        
        if len(actual_dates) >= 5:
            matches = 0
            for expected, actual in zip(expected_dates, actual_dates):
                if expected.split()[1] == actual.split()[1]:  # Compare just the date part
                    matches += 1
            
            print(f"Date matches: {matches}/5")
            
            if matches >= 4:  # Allow for some flexibility
                print("✅ SUCCESS: Got the correct recent games!")
            else:
                print("❌ ISSUE: Dates don't match expected recent games")
        else:
            print("❌ ISSUE: Not enough games found")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_actual_last_5_games()