#!/usr/bin/env python3
"""
Angel Reese WNBA stats - Fixed version that follows $ref links to get actual stats
"""
import sys
import os
import asyncio
import httpx
import json
from datetime import datetime

def parse_basketball_stats(stats_data, player_name):
    """Parse basketball statistics from ESPN data"""
    print(f"    Basketball Stats for {player_name}:")
    
    if not isinstance(stats_data, list):
        print(f"      No valid stats data (type: {type(stats_data)})")
        return {}
    
    found_stats = {}
    
    for stat in stats_data:
        if isinstance(stat, dict):
            name = stat.get("name", "").lower()
            value = stat.get("value", 0)
            display_value = stat.get("displayValue", str(value))
            
            # Map to basketball specification stats
            if "points" in name or name == "pts":
                found_stats["Points"] = display_value
                print(f"      Points: {display_value}")
            elif "rebounds" in name or "reb" in name:
                if "offensive" not in name and "defensive" not in name:  # Total rebounds
                    found_stats["Rebounds"] = display_value
                    print(f"      Rebounds: {display_value}")
            elif "assists" in name or name == "ast":
                found_stats["Assists"] = display_value
                print(f"      Assists: {display_value}")
            elif "steals" in name or name == "stl":
                found_stats["Steals"] = display_value
                print(f"      Steals: {display_value}")
            elif "blocks" in name or name == "blk":
                found_stats["Blocks"] = display_value
                print(f"      Blocks: {display_value}")
            elif "minutes" in name or name == "min":
                found_stats["Minutes"] = display_value
                print(f"      Minutes: {display_value}")
            elif "3pt" in name.replace("-", "") or "threept" in name.replace("-", ""):
                if "made" in name or "fg3m" in name:
                    found_stats["3PM"] = display_value
                    print(f"      3-Pointers Made: {display_value}")
            elif "fg%" in name or "fieldgoalpct" in name.replace(" ", ""):
                found_stats["FG%"] = display_value
                print(f"      Field Goal %: {display_value}")
    
    if not found_stats:
        # Show what stats are available
        stat_names = [stat.get("name", "Unknown") for stat in stats_data[:10]]
        print(f"      Available stats: {stat_names}")
    
    return found_stats

async def get_angel_reese_complete_stats():
    """Get Angel Reese complete stats by following all $ref links"""
    print("ANGEL REESE WNBA STATS - Complete Version")
    print("=" * 50)
    
    player_id = "4433402"
    sport = "basketball"
    league = "wnba"
    
    async with httpx.AsyncClient() as client:
        try:
            # Step 1: Get base player data
            base_url = f"https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/athletes/{player_id}"
            print(f"1. Getting player profile: {base_url}")
            
            response = await client.get(base_url, timeout=15.0)
            print(f"   Response: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Failed to get player data: {response.status_code}")
                return False
            
            player_data = response.json()
            name = player_data.get("displayName", "Unknown")
            position = player_data.get("position", {}).get("abbreviation", "N/A")
            
            print(f"   Player: {name} ({position})")
            
            # Step 2: Get statistics log (game-by-game)
            if "statisticslog" not in player_data:
                print("No statistics log available")
                return False
            
            log_ref = player_data["statisticslog"].get("$ref")
            if not log_ref:
                print("No statistics log reference")
                return False
            
            log_url = f"{log_ref}?limit=3"
            print(f"\n2. Getting game log: {log_url}")
            
            log_response = await client.get(log_url, timeout=15.0)
            print(f"   Response: {log_response.status_code}")
            
            if log_response.status_code != 200:
                print(f"Failed to get game log: {log_response.status_code}")
                return False
            
            gamelog_data = log_response.json()
            entries = gamelog_data.get("entries", [])
            print(f"   Found {len(entries)} game entries")
            
            # Step 3: Get actual game statistics by following $ref links
            all_game_stats = []
            
            for i, entry in enumerate(entries[:3], 1):
                print(f"\n  Game {i}:")
                
                statistics = entry.get("statistics", [])
                game_stats = {}
                
                for stat_group in statistics:
                    if isinstance(stat_group, dict) and "statistics" in stat_group:
                        stat_ref = stat_group["statistics"].get("$ref")
                        if stat_ref:
                            print(f"    Getting stats from: {stat_ref[:80]}...")
                            
                            try:
                                stat_response = await client.get(stat_ref, timeout=15.0)
                                if stat_response.status_code == 200:
                                    stat_data = stat_response.json()
                                    
                                    # Look for the actual statistics array
                                    if "statistics" in stat_data:
                                        stats_list = stat_data["statistics"]
                                        parsed_stats = parse_basketball_stats(stats_list, name)
                                        game_stats.update(parsed_stats)
                                    elif "splits" in stat_data:
                                        # Sometimes stats are in splits
                                        splits = stat_data["splits"]
                                        for split in splits:
                                            if "statistics" in split:
                                                stats_list = split["statistics"]
                                                parsed_stats = parse_basketball_stats(stats_list, name)
                                                game_stats.update(parsed_stats)
                                                break
                                else:
                                    print(f"    Failed to get stats: {stat_response.status_code}")
                            except Exception as e:
                                print(f"    Error getting stats: {e}")
                
                all_game_stats.append({
                    "game_number": i,
                    "stats": game_stats
                })
            
            # Step 4: Get season totals
            print(f"\n3. Getting season statistics...")
            
            if "statistics" in player_data:
                stats_ref = player_data["statistics"].get("$ref")
                if stats_ref:
                    print(f"   Getting season stats from: {stats_ref}")
                    
                    try:
                        season_response = await client.get(stats_ref, timeout=15.0)
                        if season_response.status_code == 200:
                            season_data = season_response.json()
                            
                            print(f"\n  Season Totals:")
                            season_stats = {}
                            
                            # Parse season splits
                            if "splits" in season_data:
                                splits = season_data["splits"]
                                for split in splits:
                                    split_name = split.get("name", "Unknown")
                                    if "statistics" in split:
                                        print(f"    {split_name}:")
                                        stats_list = split["statistics"]
                                        parsed_stats = parse_basketball_stats(stats_list, name)
                                        if split_name.lower() in ["total", "overall", "season"]:
                                            season_stats = parsed_stats
                        else:
                            print(f"   Failed to get season stats: {season_response.status_code}")
                    except Exception as e:
                        print(f"   Error getting season stats: {e}")
            
            # Step 5: Save complete data
            save_data = {
                "timestamp": datetime.now().isoformat(),
                "player_name": name,
                "player_id": player_id,
                "position": position,
                "recent_games": all_game_stats,
                "season_totals": season_stats if 'season_stats' in locals() else {},
                "raw_data": {
                    "player_profile": player_data,
                    "gamelog": gamelog_data
                }
            }
            
            filename = f"test/angel_reese_complete_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            # Summary
            print(f"\n{'='*50}")
            print(f"ANGEL REESE COMPLETE STATS SUMMARY")
            print(f"{'='*50}")
            print(f"Player: {name} ({position})")
            print(f"Games analyzed: {len(all_game_stats)}")
            
            # Show recent games summary
            for game_data in all_game_stats:
                game_num = game_data["game_number"]
                stats = game_data["stats"]
                print(f"\nGame {game_num} Summary:")
                for stat_name, stat_value in stats.items():
                    print(f"  {stat_name}: {stat_value}")
            
            print(f"\nData saved to: {filename}")
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False

if __name__ == "__main__":
    async def main():
        success = await get_angel_reese_complete_stats()
        
        if success:
            print(f"\nSUCCESS: Angel Reese WNBA stats complete!")
            print("Demonstrated following $ref links to get actual statistics")
        else:
            print(f"\nFAILED: Check error messages above")
    
    asyncio.run(main())