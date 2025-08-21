#!/usr/bin/env python3
"""
Debug player props data structure to fix parsing issues
"""
import asyncio
import json
import httpx

async def debug_player_props():
    """Debug player props data structure"""
    
    odds_url = "https://odds-mcp-v2-production.up.railway.app/mcp"
    
    print("Debugging Player Props Data Structure")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Step 1: Get events to find a game
            print("\n1. Getting MLB events...")
            events_payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 1,
                "params": {
                    "name": "getEvents",
                    "arguments": {"sport": "baseball_mlb"}
                }
            }
            
            events_response = await client.post(odds_url, json=events_payload)
            events_response.raise_for_status()
            events_result = events_response.json()
            
            if "result" not in events_result:
                print(f"❌ No events result: {events_result}")
                return
            
            events = events_result["result"]["data"]["events"]
            print(f"Found {len(events)} events")
            
            if events:
                first_event = events[0]
                event_id = first_event["id"]
                print(f"Using event: {first_event.get('away_team')} @ {first_event.get('home_team')}")
                print(f"Event ID: {event_id}")
                
                # Step 2: Test each player prop market
                markets = ["batter_hits", "batter_home_runs", "pitcher_strikeouts"]
                
                for market in markets:
                    print(f"\n2. Testing {market} market...")
                    
                    props_payload = {
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "id": 1,
                        "params": {
                            "name": "getEventOdds",
                            "arguments": {
                                "sport": "baseball_mlb",
                                "event_id": event_id,
                                "markets": market
                            }
                        }
                    }
                    
                    props_response = await client.post(odds_url, json=props_payload)
                    props_response.raise_for_status()
                    props_result = props_response.json()
                    
                    print(f"{market} Response Structure:")
                    response_text = json.dumps(props_result, indent=2)
                    if len(response_text) > 1000:
                        print(response_text[:1000] + "...")
                    else:
                        print(response_text)
                    
                    if "result" in props_result and "data" in props_result["result"]:
                        event_data = props_result["result"]["data"]["event"]
                        if "bookmakers" in event_data and event_data["bookmakers"]:
                            bookmaker = event_data["bookmakers"][0]
                            print(f"\nBookmaker: {bookmaker.get('title')}")
                            
                            for market_data in bookmaker.get("markets", []):
                                if market_data.get("key") == market:
                                    outcomes = market_data["outcomes"]
                                    print(f"Found {len(outcomes)} outcomes for {market}")
                                    
                                    # Show first few outcomes structure
                                    for i, outcome in enumerate(outcomes[:3]):
                                        print(f"\nOutcome {i+1}:")
                                        print(f"  name: {outcome.get('name')}")
                                        print(f"  description: {outcome.get('description')}")
                                        print(f"  price: {outcome.get('price')}")
                                        print(f"  point: {outcome.get('point')}")
                                    break
                            else:
                                print(f"Market {market} not found in bookmaker markets")
                        else:
                            print(f"No bookmakers found for {market}")
                    else:
                        print(f"No result data for {market}")
                    
                    print("-" * 40)
            else:
                print("No events found")
                
        except Exception as e:
            print(f"Exception: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_player_props())