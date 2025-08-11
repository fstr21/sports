#!/usr/bin/env python3
"""
Fetch Kyle Schwarber's most recent 5 games using ESPN eventlog endpoint
Based on the working pattern from MLB_Extraction_Summary.json
"""

import requests
import json
from datetime import datetime
import pytz

def get_kyle_schwarber_recent_games():
    """Get Kyle Schwarber's recent 5 games with detailed batting stats"""
    
    player_id = "33712"  # Kyle Schwarber
    
    print("=== KYLE SCHWARBER RECENT 5 GAMES ===")
    print(f"Player ID: {player_id}")
    print(f"Using eventlog endpoint pattern from MLB_Extraction_Summary.json")
    
    # Use the working endpoint pattern from your extraction summary
    eventlog_url = f"https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/athletes/{player_id}/eventlog"
    
    try:
        print(f"\nFetching from: {eventlog_url}")
        response = requests.get(eventlog_url, timeout=15)
        
        if response.status_code != 200:
            print(f"ERROR: HTTP {response.status_code}")
            return
            
        eventlog_data = response.json()
        print(f"SUCCESS: Got eventlog data")
        
        # Get the events (games)
        events = eventlog_data.get("events", [])
        if not events:
            print("No events found in eventlog")
            return
            
        print(f"Found {len(events)} total games in eventlog")
        
        recent_games = []
        
        # Process first 5 games (most recent are typically first)
        for i, event in enumerate(events[:5]):
            print(f"\n--- GAME {i+1} ---")
            
            game_data = {
                "game_number": i+1,
                "event_id": event.get("id", "unknown"),
                "game_date": event.get("date", "unknown"),
            }
            
            # Get competition info
            competition = event.get("competitions", [{}])[0] if event.get("competitions") else {}
            competitors = competition.get("competitors", [])
            
            if len(competitors) >= 2:
                home_team = competitors[0].get("team", {}).get("displayName", "Unknown")
                away_team = competitors[1].get("team", {}).get("displayName", "Unknown") 
                game_data["matchup"] = f"{away_team} @ {home_team}"
                print(f"Matchup: {game_data['matchup']}")
            
            # Convert date to Eastern time
            if game_data["game_date"] != "unknown":
                try:
                    utc_dt = datetime.fromisoformat(game_data["game_date"].replace('Z', '+00:00'))
                    eastern = pytz.timezone('US/Eastern')
                    et_dt = utc_dt.astimezone(eastern)
                    game_data["eastern_time"] = et_dt.strftime("%m/%d/%Y %I:%M %p ET")
                    print(f"Date: {game_data['eastern_time']}")
                except:
                    game_data["eastern_time"] = game_data["game_date"]
                    print(f"Date: {game_data['game_date']}")
            
            # Get player statistics for this game
            statistics = event.get("statistics", [])
            game_data["stats"] = {"batting": {}}
            
            print(f"Statistics found: {len(statistics)} stat groups")
            
            for stat_group in statistics:
                if isinstance(stat_group, dict):
                    # Look for the statistics reference
                    stats_ref = stat_group.get("statistics", {})
                    if isinstance(stats_ref, dict) and "$ref" in stats_ref:
                        # Fetch the actual statistics
                        stats_url = stats_ref["$ref"]
                        print(f"  Fetching stats from: {stats_url}")
                        
                        try:
                            stats_response = requests.get(stats_url, timeout=10)
                            if stats_response.status_code == 200:
                                stats_data = stats_response.json()
                                
                                # Look for splits data (contains actual stats)
                                splits = stats_data.get("splits", [])
                                for split in splits:
                                    split_stats = split.get("statistics", [])
                                    for stat in split_stats:
                                        stat_name = stat.get("displayName", stat.get("name", "Unknown"))
                                        stat_value = stat.get("value", 0)
                                        
                                        # Store key batting stats
                                        if stat_name in ["Hits", "Home Runs", "RBIs", "Runs", "At Bats", "Strikeouts", "Walks"]:
                                            try:
                                                game_data["stats"]["batting"][stat_name] = float(stat_value)
                                                print(f"    {stat_name}: {stat_value}")
                                            except:
                                                game_data["stats"]["batting"][stat_name] = stat_value
                                                print(f"    {stat_name}: {stat_value}")
                            else:
                                print(f"    Failed to fetch stats: HTTP {stats_response.status_code}")
                        except Exception as e:
                            print(f"    Error fetching stats: {e}")
            
            recent_games.append(game_data)
        
        # Save results
        output_data = {
            "player_info": {
                "player_id": player_id,
                "name": "Kyle Schwarber", 
                "team": "Philadelphia Phillies",
                "extraction_date": datetime.now().isoformat()
            },
            "recent_games": recent_games
        }
        
        output_file = "Kyle_Schwarber_Recent_5_Games.json"
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n=== SUMMARY ===")
        print(f"✓ Extracted {len(recent_games)} games")
        print(f"✓ Saved to: {output_file}")
        
        # Calculate recent averages
        if recent_games:
            batting_totals = {}
            games_with_stats = 0
            
            for game in recent_games:
                batting = game["stats"]["batting"]
                if batting:
                    games_with_stats += 1
                    for stat_name, stat_value in batting.items():
                        if isinstance(stat_value, (int, float)):
                            if stat_name not in batting_totals:
                                batting_totals[stat_name] = []
                            batting_totals[stat_name].append(stat_value)
            
            if batting_totals:
                print(f"\n=== RECENT {games_with_stats} GAMES AVERAGES ===")
                for stat_name in ["Hits", "Home Runs", "RBIs", "Runs", "At Bats"]:
                    if stat_name in batting_totals:
                        values = batting_totals[stat_name] 
                        avg = sum(values) / len(values)
                        print(f"{stat_name}: {avg:.1f} per game")
                
                # Batting average
                if "Hits" in batting_totals and "At Bats" in batting_totals:
                    total_hits = sum(batting_totals["Hits"])
                    total_ab = sum(batting_totals["At Bats"])
                    if total_ab > 0:
                        batting_avg = total_hits / total_ab
                        print(f"Batting Average: {batting_avg:.3f}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_kyle_schwarber_recent_games()