#!/usr/bin/env python3
"""
Debug Angel Reese API responses to understand exact data structure
"""
import asyncio
import httpx
import json

async def debug_angel_reese_api():
    """Debug the exact ESPN Core API responses"""
    print("DEBUG: Angel Reese ESPN Core API Structure")
    print("=" * 50)
    
    player_id = "4433402"
    base_url = f"https://sports.core.api.espn.com/v2/sports/basketball/leagues/wnba/athletes/{player_id}"
    
    async with httpx.AsyncClient() as client:
        try:
            # Get base player data
            response = await client.get(base_url, timeout=15.0)
            player_data = response.json()
            
            # Get one game's statistics
            log_ref = player_data["statisticslog"]["$ref"]
            log_url = f"{log_ref}?limit=1"
            
            print(f"Getting game log: {log_url}")
            log_response = await client.get(log_url, timeout=15.0)
            gamelog_data = log_response.json()
            
            # Get first game entry
            first_game = gamelog_data["entries"][0]
            print(f"\nFirst game structure:")
            print(f"Keys: {list(first_game.keys())}")
            
            statistics = first_game.get("statistics", [])
            print(f"\nStatistics array has {len(statistics)} items")
            
            for i, stat_group in enumerate(statistics):
                print(f"\nStat group {i+1}:")
                print(f"  Keys: {list(stat_group.keys())}")
                print(f"  Type: {stat_group.get('type', 'No type')}")
                
                if "statistics" in stat_group:
                    stat_ref = stat_group["statistics"]["$ref"]
                    print(f"  Ref: {stat_ref}")
                    
                    # Follow the reference
                    print(f"  Following reference...")
                    stat_response = await client.get(stat_ref, timeout=15.0)
                    
                    if stat_response.status_code == 200:
                        stat_data = stat_response.json()
                        print(f"  Response keys: {list(stat_data.keys())}")
                        
                        # Save the first stat response for detailed analysis
                        if i == 0:
                            filename = f"test/angel_reese_debug_stats_{i+1}.json"
                            with open(filename, 'w') as f:
                                json.dump(stat_data, f, indent=2)
                            print(f"  Saved to: {filename}")
                            
                            # Check if there are actual statistics
                            if "statistics" in stat_data:
                                stats_list = stat_data["statistics"]
                                print(f"  Statistics list type: {type(stats_list)}")
                                print(f"  Statistics list length: {len(stats_list) if isinstance(stats_list, list) else 'Not list'}")
                                
                                if isinstance(stats_list, list) and stats_list:
                                    first_stat = stats_list[0]
                                    print(f"  First stat: {first_stat}")
                    else:
                        print(f"  Failed: {stat_response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False

if __name__ == "__main__":
    asyncio.run(debug_angel_reese_api())