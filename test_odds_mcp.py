#!/usr/bin/env python3
"""
Test the Odds MCP v2 server for MLB betting lines
"""
import asyncio
import json
import sys
import os
import httpx

async def test_odds_mcp():
    """Test odds MCP v2 server capabilities"""
    
    odds_url = "https://odds-mcp-v2-production.up.railway.app/mcp"
    
    print("Testing Odds MCP v2 Server...")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test 1: Get available sports
            print("\n1. Testing getSports:")
            sports_payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 1,
                "params": {"name": "getSports", "arguments": {}}
            }
            
            response = await client.post(odds_url, json=sports_payload)
            response.raise_for_status()
            sports_result = response.json()
            
            if "result" in sports_result:
                sports_data = sports_result["result"]["data"]["sports"]
                mlb_sport = next((s for s in sports_data if s["key"] == "baseball_mlb"), None)
                print(f"SUCCESS: Found {len(sports_data)} sports")
                if mlb_sport:
                    print(f"MLB Available: {mlb_sport['title']} (Active: {mlb_sport.get('active', True)})")
                else:
                    print("WARNING: MLB not found in sports list")
            else:
                print(f"ERROR: {sports_result}")
                
            # Test 2: Get MLB odds
            print("\n2. Testing getOdds for MLB:")
            odds_payload = {
                "jsonrpc": "2.0", 
                "method": "tools/call",
                "id": 1,
                "params": {
                    "name": "getOdds",
                    "arguments": {
                        "sport": "baseball_mlb",
                        "markets": "h2h,spreads,totals",
                        "regions": "us"
                    }
                }
            }
            
            response = await client.post(odds_url, json=odds_payload)
            response.raise_for_status()
            odds_result = response.json()
            
            if "result" in odds_result and "data" in odds_result["result"]:
                odds_data = odds_result["result"]["data"]["odds"]
                print(f"SUCCESS: Found {len(odds_data)} MLB games with odds")
                
                if odds_data:
                    # Show first game as example
                    first_game = odds_data[0]
                    print(f"\nExample Game: {first_game.get('away_team')} @ {first_game.get('home_team')}")
                    print(f"Commence Time: {first_game.get('commence_time')}")
                    
                    if "bookmakers" in first_game and first_game["bookmakers"]:
                        bookmaker = first_game["bookmakers"][0]
                        print(f"Bookmaker: {bookmaker.get('title')}")
                        
                        for market in bookmaker.get("markets", []):
                            market_key = market.get("key")
                            print(f"\n{market_key.upper()} Market:")
                            
                            for outcome in market.get("outcomes", []):
                                name = outcome.get("name")
                                price = outcome.get("price")
                                point = outcome.get("point", "")
                                point_str = f" ({point:+g})" if point else ""
                                print(f"  {name}{point_str}: {price:+d}" if isinstance(price, int) else f"  {name}{point_str}: {price}")
                else:
                    print("No games found with odds")
            else:
                print(f"ERROR: {odds_result}")
                
            # Test 3: Get events for player props
            print("\n3. Testing getEvents for MLB:")
            events_payload = {
                "jsonrpc": "2.0",
                "method": "tools/call", 
                "id": 1,
                "params": {
                    "name": "getEvents",
                    "arguments": {"sport": "baseball_mlb"}
                }
            }
            
            response = await client.post(odds_url, json=events_payload)
            response.raise_for_status()
            events_result = response.json()
            
            if "result" in events_result:
                events_data = events_result["result"]["data"]["events"]
                print(f"SUCCESS: Found {len(events_data)} MLB events")
                
                if events_data:
                    first_event = events_data[0]
                    print(f"First Event: {first_event.get('away_team')} @ {first_event.get('home_team')}")
                    print(f"Event ID: {first_event.get('id')}")
            else:
                print(f"ERROR: {events_result}")
                
            # Test 4: Get quota info
            print("\n4. Testing getQuotaInfo:")
            quota_payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 1, 
                "params": {"name": "getQuotaInfo", "arguments": {}}
            }
            
            response = await client.post(odds_url, json=quota_payload)
            response.raise_for_status() 
            quota_result = response.json()
            
            if "result" in quota_result:
                quota_data = quota_result["result"]["data"]
                print(f"API Usage: {quota_data.get('used', 'N/A')}/{quota_data.get('remaining', 'N/A')} requests")
            else:
                print(f"Quota Error: {quota_result}")
                
        except Exception as e:
            print(f"Exception during testing: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_odds_mcp())