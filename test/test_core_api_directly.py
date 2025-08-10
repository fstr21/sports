#!/usr/bin/env python3
"""
Test the ESPN core API directly to understand the data structure.
"""
import asyncio
import httpx
import json

async def test_core_api_structure():
    """Test the ESPN core API structure we found"""
    print("Testing ESPN Core API Structure")
    print("="*40)
    
    # We know this URL works
    base_url = "https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/athletes/32655"
    
    async with httpx.AsyncClient() as client:
        print(f"1. Testing base player data: {base_url}")
        
        try:
            response = await client.get(base_url, timeout=10.0)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Save full player data for analysis
                with open("test/byron_buxton_full_data.json", "w") as f:
                    json.dump(data, f, indent=2)
                
                print(f"   SUCCESS! Saved full data to byron_buxton_full_data.json")
                print(f"   Player: {data.get('displayName', 'Unknown')}")
                print(f"   Keys: {list(data.keys())}")
                
                # Check statistics structure
                if "statistics" in data:
                    stats = data["statistics"]
                    print(f"   Statistics type: {type(stats)}")
                    
                    if isinstance(stats, dict) and "$ref" in stats:
                        stats_url = stats["$ref"]
                        print(f"   Statistics URL: {stats_url}")
                        
                        # Try to get statistics
                        print(f"\n2. Testing statistics URL...")
                        stats_response = await client.get(stats_url, timeout=10.0)
                        print(f"   Status: {stats_response.status_code}")
                        
                        if stats_response.status_code == 200:
                            stats_data = stats_response.json()
                            print(f"   SUCCESS! Got statistics data")
                            print(f"   Stats keys: {list(stats_data.keys()) if isinstance(stats_data, dict) else 'Not dict'}")
                            
                            # Save stats data
                            with open("test/byron_buxton_stats.json", "w") as f:
                                json.dump(stats_data, f, indent=2)
                
                # Check statisticslog structure  
                if "statisticslog" in data:
                    log = data["statisticslog"]
                    print(f"   Statisticslog type: {type(log)}")
                    
                    if isinstance(log, dict) and "$ref" in log:
                        log_url = log["$ref"]
                        print(f"   Statisticslog URL: {log_url}")
                        
                        # Try to get game log
                        print(f"\n3. Testing statisticslog URL...")
                        log_response = await client.get(log_url, timeout=10.0)
                        print(f"   Status: {log_response.status_code}")
                        
                        if log_response.status_code == 200:
                            log_data = log_response.json()
                            print(f"   SUCCESS! Got game log data")
                            print(f"   Log keys: {list(log_data.keys()) if isinstance(log_data, dict) else 'Not dict'}")
                            
                            # Save log data
                            with open("test/byron_buxton_gamelog.json", "w") as f:
                                json.dump(log_data, f, indent=2)
                            
                            # Check for entries (individual games)
                            if isinstance(log_data, dict) and "entries" in log_data:
                                entries = log_data["entries"]
                                print(f"   Found {len(entries) if isinstance(entries, list) else 'non-list'} game entries")
                                
                                if isinstance(entries, list) and entries:
                                    first_game = entries[0]
                                    print(f"   First game keys: {list(first_game.keys()) if isinstance(first_game, dict) else 'Not dict'}")
                
            else:
                print(f"   Failed with status {response.status_code}")
                
        except Exception as e:
            print(f"   Error: {e}")

async def fix_http_server_implementation():
    """Analyze what the HTTP server implementation should be"""
    print(f"\n{'='*40}")
    print("HTTP Server Implementation Analysis")
    print("="*40)
    
    print("Current issues:")
    print("1. We're trying to fetch statisticslog directly")
    print("2. Should fetch base player data first")
    print("3. Then follow $ref links to get statistics")
    print("4. ESPN core API uses reference links, not direct paths")
    
    print("\nCorrect approach:")
    print("1. GET base player: https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/athletes/{id}")
    print("2. Extract statisticslog.$ref URL from response")
    print("3. GET that URL to get game-by-game stats")
    print("4. Extract statistics.$ref URL for season totals")

if __name__ == "__main__":
    async def main():
        await test_core_api_structure()
        await fix_http_server_implementation()
    
    asyncio.run(main())