#!/usr/bin/env python3
"""
Test script to verify MLB totals data from Odds MCP
"""
import asyncio
import httpx
import json
from datetime import datetime

async def test_mlb_totals():
    """Test MLB totals integration with Odds MCP v2"""
    print("Testing MLB Totals Integration...")
    
    odds_url = "https://odds-mcp-v2-production.up.railway.app/mcp"
    
    payload = {
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
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("Calling Odds MCP for MLB games...")
            response = await client.post(odds_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "result" not in result or "data" not in result["result"]:
                print("ERROR: No odds data returned")
                return
            
            odds_data = result["result"]["data"]["odds"]
            if not odds_data:
                print("ERROR: No MLB games found with odds")
                return
            
            print(f"SUCCESS: Found {len(odds_data)} MLB games with odds")
            
            # Check first few games for totals data
            for i, game in enumerate(odds_data[:3]):
                print(f"\nGame {i+1}: {game.get('away_team')} @ {game.get('home_team')}")
                print(f"   Start time: {game.get('commence_time', 'TBD')}")
                
                if "bookmakers" not in game or not game["bookmakers"]:
                    print("   ERROR: No bookmakers available")
                    continue
                
                bookmaker = game["bookmakers"][0]
                bookmaker_name = bookmaker.get("title", "Unknown")
                print(f"   Bookmaker: {bookmaker_name}")
                
                # Check for totals market
                totals_found = False
                for market in bookmaker.get("markets", []):
                    market_key = market.get("key")
                    
                    if market_key == "totals":
                        totals_found = True
                        print(f"   SUCCESS: Totals market found!")
                        
                        outcomes = market.get("outcomes", [])
                        if len(outcomes) >= 2:
                            total_points = outcomes[0].get("point", 0) if outcomes else 0
                            print(f"      Total points: {total_points}")
                            
                            over_odds = under_odds = "N/A"
                            for outcome in outcomes:
                                name = outcome.get("name", "")
                                price = outcome.get("price")
                                point = outcome.get("point")
                                
                                price_str = f"({price:+d})" if isinstance(price, int) else f"({price})"
                                
                                if name.lower() == "over":
                                    over_odds = price_str
                                    print(f"      Over {point}: {price_str}")
                                elif name.lower() == "under":
                                    under_odds = price_str
                                    print(f"      Under {point}: {price_str}")
                            
                            # Test the parsing logic
                            formatted_total = f"O/U {total_points} {over_odds}/{under_odds}"
                            print(f"      Formatted result: '{formatted_total}'")
                            
                            # Test parsing logic
                            if formatted_total and "O/U" in formatted_total:
                                parts = formatted_total.split(" ", 2)
                                if len(parts) >= 2:
                                    parsed_line = parts[1]
                                    print(f"      SUCCESS: Parsed line: {parsed_line}")
                                    
                                    if len(parts) >= 3 and "/" in parts[2]:
                                        odds_part = parts[2]
                                        odds_split = odds_part.split("/")
                                        if len(odds_split) >= 2:
                                            parsed_over = odds_split[0].strip()
                                            parsed_under = odds_split[1].strip()
                                            print(f"      SUCCESS: Parsed over odds: {parsed_over}")
                                            print(f"      SUCCESS: Parsed under odds: {parsed_under}")
                
                if not totals_found:
                    print(f"   ERROR: No totals market found")
                    available_markets = [m.get("key") for m in bookmaker.get("markets", [])]
                    print(f"      Available markets: {available_markets}")
    
    except Exception as e:
        print(f"ERROR testing MLB totals: {e}")
        return False
    
    print(f"\nSUCCESS: MLB Totals test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return True

if __name__ == "__main__":
    asyncio.run(test_mlb_totals())