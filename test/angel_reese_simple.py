#!/usr/bin/env python3
"""
Get WNBA stats for Angel Reese - Simple version without Unicode characters
"""
import sys
import os
import asyncio
import httpx
import json
from datetime import datetime

async def get_angel_reese_stats():
    """Get Angel Reese WNBA stats using direct ESPN Core API"""
    print("ANGEL REESE WNBA STATS TEST")
    print("=" * 40)
    
    player_id = "4433402"
    sport = "basketball"
    league = "wnba"
    
    # Direct ESPN Core API call
    base_url = f"https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/athletes/{player_id}"
    
    async with httpx.AsyncClient() as client:
        print(f"Calling ESPN Core API...")
        print(f"URL: {base_url}")
        
        try:
            # Get base player data
            response = await client.get(base_url, timeout=15.0)
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                player_data = response.json()
                
                # Display player info
                name = player_data.get("displayName", "Unknown")
                position = player_data.get("position", {}).get("abbreviation", "N/A")
                team = player_data.get("team", {}).get("displayName", "Unknown Team")
                
                print(f"\nPLAYER INFO:")
                print(f"  Name: {name}")
                print(f"  Position: {position}")
                print(f"  Team: {team}")
                
                # Get recent game statistics
                print(f"\nGETTING RECENT GAMES...")
                
                if "statisticslog" in player_data:
                    log_ref = player_data["statisticslog"].get("$ref")
                    if log_ref:
                        log_url = f"{log_ref}?limit=3"
                        print(f"Game log URL: {log_url}")
                        
                        log_response = await client.get(log_url, timeout=15.0)
                        print(f"Game log response: {log_response.status_code}")
                        
                        if log_response.status_code == 200:
                            gamelog_data = log_response.json()
                            games = gamelog_data.get("entries", [])
                            
                            print(f"\nRECENT GAMES ({len(games)} games):")
                            
                            all_stats = []
                            
                            for i, game in enumerate(games[:3], 1):
                                print(f"\n  Game {i}:")
                                
                                # Get game statistics
                                game_stats = game.get("statistics", [])
                                
                                game_data = {"game_number": i, "stats": {}}
                                
                                # Parse basketball stats
                                for stat in game_stats:
                                    if isinstance(stat, dict):
                                        stat_name = stat.get("name", "")
                                        stat_value = stat.get("displayValue", stat.get("value", 0))
                                        
                                        # Look for key basketball stats
                                        if "points" in stat_name.lower():
                                            print(f"    Points: {stat_value}")
                                            game_data["stats"]["points"] = stat_value
                                        elif "rebound" in stat_name.lower():
                                            print(f"    Rebounds: {stat_value}")
                                            game_data["stats"]["rebounds"] = stat_value
                                        elif "assist" in stat_name.lower():
                                            print(f"    Assists: {stat_value}")
                                            game_data["stats"]["assists"] = stat_value
                                        elif "steal" in stat_name.lower():
                                            print(f"    Steals: {stat_value}")
                                            game_data["stats"]["steals"] = stat_value
                                        elif "block" in stat_name.lower():
                                            print(f"    Blocks: {stat_value}")
                                            game_data["stats"]["blocks"] = stat_value
                                        elif "minutes" in stat_name.lower():
                                            print(f"    Minutes: {stat_value}")
                                            game_data["stats"]["minutes"] = stat_value
                                
                                all_stats.append(game_data)
                            
                            # Save data to file
                            save_data = {
                                "timestamp": datetime.now().isoformat(),
                                "player_name": name,
                                "player_id": player_id,
                                "position": position,
                                "team": team,
                                "recent_games": all_stats,
                                "raw_player_data": player_data,
                                "raw_gamelog": gamelog_data
                            }
                            
                            # Save to test folder
                            filename = f"test/angel_reese_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                            with open(filename, 'w') as f:
                                json.dump(save_data, f, indent=2)
                            
                            print(f"\nSUCCESS!")
                            print(f"Data saved to: {filename}")
                            print(f"File size: {os.path.getsize(filename)} bytes")
                            
                            return True
                        else:
                            print(f"Failed to get game log: {log_response.status_code}")
                    else:
                        print("No game log reference found")
                else:
                    print("No statistics log available")
                
            else:
                print(f"Failed to get player data: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error: {e}")
            return False

if __name__ == "__main__":
    async def main():
        success = await get_angel_reese_stats()
        
        print(f"\n{'=' * 40}")
        if success:
            print("ANGEL REESE WNBA STATS - COMPLETE!")
            print("Direct ESPN Core API approach working!")
        else:
            print("FAILED - Check error messages above")
    
    asyncio.run(main())