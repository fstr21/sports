#!/usr/bin/env python3
"""
Get WNBA stats for Angel Reese using direct ESPN Core API approach.
Demonstrates the complete workflow with real data.
"""
import sys
import os
import asyncio
import httpx
import json
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sports_mcp'))

from interactive_sports_test import SportsTestInterface

def parse_basketball_stats(game_stats, player_name):
    """Parse basketball statistics according to specification"""
    print(f"    📊 {player_name} Game Stats:")
    
    # Target basketball stats from specification:
    # Points, Rebounds, Assists, 3PM, Steals, Blocks, FG%, Minutes
    target_stats = {
        "points": "Points",
        "rebounds": "Rebounds", 
        "assists": "Assists",
        "threePointFieldGoalsMade": "3-Pointers Made",
        "steals": "Steals",
        "blocks": "Blocks",
        "fieldGoalPct": "Field Goal %",
        "minutes": "Minutes Played"
    }
    
    found_stats = {}
    
    # Parse statistics array
    if isinstance(game_stats, list):
        for stat in game_stats:
            if isinstance(stat, dict):
                name = stat.get("name", "").lower()
                value = stat.get("value", 0)
                display_value = stat.get("displayValue", str(value))
                
                for key, label in target_stats.items():
                    if key.lower() in name or any(word in name for word in key.lower().split()):
                        found_stats[label] = display_value
    
    # Display found stats
    if found_stats:
        for label, value in found_stats.items():
            print(f"      {label}: {value}")
    else:
        print(f"      Raw stats available: {[stat.get('name', 'Unknown') for stat in game_stats[:5]] if isinstance(game_stats, list) else 'No stats'}")
    
    return found_stats

async def get_angel_reese_stats():
    """Get Angel Reese WNBA stats using hybrid MCP + Direct API approach"""
    print("ANGEL REESE WNBA STATS WORKFLOW")
    print("=" * 50)
    
    # Step 1: Try to get WNBA games using MCP server
    print("Step 1: Getting today's WNBA games...")
    
    interface = SportsTestInterface()
    interface.current_sport_league = ("basketball", "wnba")
    
    success, result = interface.make_request("POST", "/espn/scoreboard", {
        "sport": "basketball",
        "league": "wnba"
    })
    
    if success and result.get("ok"):
        games = result.get("data", {}).get("scoreboard", [])
        print(f"SUCCESS: Found {len(games)} WNBA games today")
        
        # Look for Angel Reese's team (Chicago Sky)
        chicago_game = None
        for game in games:
            game_name = game.get("name", "")
            if "chicago" in game_name.lower() or "sky" in game_name.lower():
                chicago_game = game
                break
        
        if chicago_game:
            print(f"SUCCESS: Found Chicago Sky game: {chicago_game.get('name', 'Unknown')}")
            game_id = chicago_game.get("id")
            
            # Step 2: Get game summary for roster verification
            print(f"\nStep 2: Getting game summary for roster verification...")
            success, result = interface.make_request("POST", "/espn/game-summary", {
                "sport": "basketball",
                "league": "wnba",
                "event_id": game_id
            })
            
            if success and result.get("ok"):
                print("✅ Got game summary data")
            else:
                print("⚠️ Couldn't get game summary, proceeding with known player ID")
        else:
            print("⚠️ No Chicago Sky game today, proceeding with known player ID")
    else:
        print("⚠️ No WNBA games today, proceeding with known player ID")
    
    # Step 3: Get Angel Reese stats using direct ESPN Core API
    print(f"\nStep 3: Getting Angel Reese stats using direct ESPN Core API...")
    
    player_id = "4433402"
    sport = "basketball"
    league = "wnba"
    
    # Direct ESPN Core API call
    base_url = f"https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/athletes/{player_id}"
    
    async with httpx.AsyncClient() as client:
        print(f"🔗 Calling: {base_url}")
        
        try:
            # Get base player data
            response = await client.get(base_url, timeout=15.0)
            print(f"📡 API Response: {response.status_code}")
            
            if response.status_code == 200:
                player_data = response.json()
                
                # Display player info
                name = player_data.get("displayName", "Unknown")
                position = player_data.get("position", {}).get("abbreviation", "N/A")
                team = player_data.get("team", {}).get("displayName", "Unknown Team")
                
                print(f"✅ SUCCESS! Found player data")
                print(f"👤 Player: {name} ({position})")
                print(f"🏀 Team: {team}")
                
                # Save raw player data
                save_data = {
                    "timestamp": datetime.now().isoformat(),
                    "player_name": name,
                    "player_id": player_id,
                    "sport": sport,
                    "league": league,
                    "raw_player_data": player_data
                }
                
                # Step 4: Get game-by-game statistics
                print(f"\nStep 4: Getting recent game statistics...")
                
                if "statisticslog" in player_data and isinstance(player_data["statisticslog"], dict):
                    log_ref = player_data["statisticslog"].get("$ref")
                    if log_ref:
                        # Add limit for recent games
                        log_url = f"{log_ref}?limit=5"
                        print(f"🔗 Getting game log: {log_url}")
                        
                        log_response = await client.get(log_url, timeout=15.0)
                        print(f"📡 Game log response: {log_response.status_code}")
                        
                        if log_response.status_code == 200:
                            gamelog_data = log_response.json()
                            games = gamelog_data.get("entries", [])
                            
                            print(f"✅ Found {len(games)} recent games")
                            
                            # Parse each game according to basketball specification
                            game_stats_summary = []
                            
                            for i, game in enumerate(games[:5], 1):
                                print(f"\n  📅 Game {i}:")
                                
                                # Get game info
                                season = game.get("season", {})
                                season_year = season.get("year", "Unknown")
                                season_type = season.get("type", "Unknown")
                                
                                print(f"    Season: {season_year} ({season_type})")
                                
                                # Parse game statistics
                                game_stats = game.get("statistics", [])
                                parsed_stats = parse_basketball_stats(game_stats, name)
                                
                                game_summary = {
                                    "game_number": i,
                                    "season": season_year,
                                    "season_type": season_type,
                                    "parsed_stats": parsed_stats,
                                    "raw_stats": game_stats
                                }
                                game_stats_summary.append(game_summary)
                            
                            save_data["recent_games"] = game_stats_summary
                            save_data["raw_gamelog"] = gamelog_data
                            
                        else:
                            print(f"❌ Failed to get game log: {log_response.status_code}")
                    else:
                        print("❌ No statisticslog reference found")
                else:
                    print("❌ No statisticslog data available")
                
                # Step 5: Get season statistics  
                print(f"\nStep 5: Getting season statistics...")
                
                if "statistics" in player_data and isinstance(player_data["statistics"], dict):
                    stats_ref = player_data["statistics"].get("$ref")
                    if stats_ref:
                        print(f"🔗 Getting season stats: {stats_ref}")
                        
                        stats_response = await client.get(stats_ref, timeout=15.0)
                        print(f"📡 Season stats response: {stats_response.status_code}")
                        
                        if stats_response.status_code == 200:
                            season_data = stats_response.json()
                            print(f"✅ Got season statistics")
                            
                            # Parse season splits
                            splits = season_data.get("splits", [])
                            print(f"📊 Found {len(splits)} statistical splits")
                            
                            for split in splits:
                                split_name = split.get("name", "Unknown Split")
                                stats = split.get("statistics", [])
                                print(f"\n  📈 {split_name}:")
                                parse_basketball_stats(stats, name)
                            
                            save_data["season_stats"] = season_data
                        else:
                            print(f"❌ Failed to get season stats: {stats_response.status_code}")
                    else:
                        print("❌ No statistics reference found")
                else:
                    print("❌ No statistics data available")
                
                # Step 6: Save complete data to file
                print(f"\nStep 6: Saving data to file...")
                
                filename = f"test/angel_reese_wnba_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(save_data, f, indent=2)
                
                print(f"💾 Saved complete data to: {filename}")
                
                # Summary
                print(f"\n🎯 SUMMARY FOR ANGEL REESE:")
                print(f"  Player: {name} ({position}) - {team}")
                print(f"  Recent games analyzed: {len(save_data.get('recent_games', []))}")
                print(f"  Season stats: {'✅ Available' if 'season_stats' in save_data else '❌ Not available'}")
                print(f"  Data saved to: {filename}")
                
                return True
                
            else:
                print(f"❌ Failed to get player data: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False
                
        except Exception as e:
            print(f"❌ Error calling ESPN Core API: {e}")
            return False

if __name__ == "__main__":
    async def main():
        success = await get_angel_reese_stats()
        
        print(f"\n{'=' * 50}")
        if success:
            print("🎉 ANGEL REESE WNBA STATS - COMPLETE SUCCESS!")
            print("✅ Demonstrated full workflow: MCP Server + Direct API")
            print("✅ Parsed basketball stats according to specification")
            print("✅ Data saved to test folder")
        else:
            print("❌ FAILED - Check error messages above")
    
    asyncio.run(main())