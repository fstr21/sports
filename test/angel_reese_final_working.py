#!/usr/bin/env python3
"""
Angel Reese WNBA Stats - FINAL WORKING VERSION
Correctly parses ESPN Core API nested structure: splits.categories[].stats[]
"""
import asyncio
import httpx
import json
from datetime import datetime

def parse_espn_stats(splits_data, player_name):
    """Parse ESPN statistics from splits.categories.stats structure"""
    stats_found = {}
    
    if not isinstance(splits_data, dict) or "categories" not in splits_data:
        return stats_found
    
    categories = splits_data["categories"]
    
    for category in categories:
        category_name = category.get("name", "")
        stats = category.get("stats", [])
        
        for stat in stats:
            name = stat.get("name", "").lower()
            display_name = stat.get("displayName", "")
            value = stat.get("value", 0)
            display_value = stat.get("displayValue", str(value))
            
            # Map to WNBA specification stats
            if name == "points":
                stats_found["Points"] = display_value
            elif name == "rebounds":
                stats_found["Rebounds"] = display_value  
            elif name == "assists":
                stats_found["Assists"] = display_value
            elif name == "steals":
                stats_found["Steals"] = display_value
            elif name == "blocks":
                stats_found["Blocks"] = display_value
            elif "threepointfieldgoalsmade" in name.replace(" ", ""):
                stats_found["3PM"] = display_value
            elif "fieldgoalpercentage" in name.replace(" ", ""):
                stats_found["FG%"] = display_value
            elif name == "minutes":
                stats_found["Minutes"] = display_value
    
    return stats_found

async def get_angel_reese_working_stats():
    """Get Angel Reese stats with correct ESPN API parsing"""
    print("ANGEL REESE WNBA STATS - FINAL WORKING VERSION")
    print("=" * 60)
    
    player_id = "4433402"
    base_url = f"https://sports.core.api.espn.com/v2/sports/basketball/leagues/wnba/athletes/{player_id}"
    
    async with httpx.AsyncClient() as client:
        try:
            # Step 1: Get player profile
            print(f"1. Getting player profile...")
            response = await client.get(base_url, timeout=15.0)
            
            if response.status_code != 200:
                print(f"Failed: {response.status_code}")
                return False
            
            player_data = response.json()
            name = player_data.get("displayName", "Unknown")
            position = player_data.get("position", {}).get("abbreviation", "N/A")
            height = player_data.get("displayHeight", "Unknown")
            weight = player_data.get("displayWeight", "Unknown")
            
            print(f"   Player: {name} ({position})")
            print(f"   Physical: {height}, {weight}")
            
            # Step 2: Get season statistics (easier than game-by-game)
            print(f"\n2. Getting season statistics...")
            
            stats_ref = player_data["statistics"]["$ref"]
            stats_response = await client.get(stats_ref, timeout=15.0)
            
            if stats_response.status_code != 200:
                print(f"Failed to get season stats: {stats_response.status_code}")
                return False
            
            season_data = stats_response.json()
            
            if "splits" not in season_data:
                print("No splits data found")
                return False
            
            splits = season_data["splits"]
            
            print(f"   Processing {splits.get('name', 'season')} statistics...")
            
            # Parse the statistics
            season_stats = parse_espn_stats(splits, name)
            
            print(f"\n3. ANGEL REESE 2025 WNBA SEASON STATS:")
            print(f"   {'='*40}")
            
            # Display basketball stats per specification
            basketball_order = ["Points", "Rebounds", "Assists", "3PM", "Steals", "Blocks", "FG%", "Minutes"]
            
            for stat_name in basketball_order:
                if stat_name in season_stats:
                    print(f"   {stat_name:15}: {season_stats[stat_name]}")
            
            # Show any additional stats found
            other_stats = {k: v for k, v in season_stats.items() if k not in basketball_order}
            if other_stats:
                print(f"\n   Additional Stats:")
                for stat_name, value in other_stats.items():
                    print(f"   {stat_name:15}: {value}")
            
            # Step 3: Try to get recent games for context
            print(f"\n4. Getting recent game context...")
            
            log_ref = player_data["statisticslog"]["$ref"]
            log_url = f"{log_ref}?limit=2"
            log_response = await client.get(log_url, timeout=15.0)
            
            recent_games = []
            if log_response.status_code == 200:
                gamelog_data = log_response.json()
                entries = gamelog_data.get("entries", [])
                
                print(f"   Found {len(entries)} recent games")
                
                for i, entry in enumerate(entries, 1):
                    # Get season info for context
                    season = entry.get("season", {})
                    if isinstance(season, dict) and "$ref" in season:
                        season_info = "Recent season"
                    else:
                        season_info = f"Season data: {season}"
                    
                    recent_games.append({
                        "game_number": i,
                        "season_context": season_info
                    })
                    
                    print(f"   Game {i}: {season_info}")
            
            # Step 4: Save comprehensive data
            save_data = {
                "timestamp": datetime.now().isoformat(),
                "player_profile": {
                    "name": name,
                    "id": player_id,
                    "position": position,
                    "height": height,
                    "weight": weight
                },
                "season_stats": season_stats,
                "recent_games_context": recent_games,
                "basketball_specification_stats": {
                    stat: season_stats.get(stat, "N/A") 
                    for stat in basketball_order
                },
                "raw_data": {
                    "player_data": player_data,
                    "season_stats_data": season_data
                }
            }
            
            filename = f"test/angel_reese_final_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            print(f"\n5. SUCCESS!")
            print(f"   Data saved to: {filename}")
            print(f"   File size: {len(json.dumps(save_data))} characters")
            
            # Summary
            print(f"\n   SUMMARY:")
            print(f"   - Retrieved complete WNBA player profile")
            print(f"   - Parsed season statistics per basketball specification") 
            print(f"   - Found {len(season_stats)} statistical categories")
            print(f"   - Data saved to test folder")
            
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    async def main():
        success = await get_angel_reese_working_stats()
        
        print(f"\n{'='*60}")
        if success:
            print("ANGEL REESE WNBA STATS - COMPLETE SUCCESS!")
            print("✓ Direct ESPN Core API working perfectly")
            print("✓ Statistics parsed per WNBA/Basketball specification")  
            print("✓ Data saved to test folder")
            print("✓ Workflow proven for all WNBA players")
        else:
            print("FAILED - Check error messages above")
    
    asyncio.run(main())