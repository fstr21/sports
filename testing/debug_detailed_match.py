#!/usr/bin/env python3
"""
Debug script to see what detailed match data we're getting
"""

import asyncio
import json
import os
import sys
import httpx
from dotenv import load_dotenv

# Add parent directory to path to load .env
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
load_dotenv(os.path.join(parent_dir, '.env'))

async def debug_match_details():
    soccer_mcp_url = "https://soccermcp-production.up.railway.app/mcp"
    
    # Get the Liverpool vs Bournemouth match ID from the previous call
    # First get the match list
    get_matches_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getCompetitionMatches",
            "arguments": {
                "competition_id": "2021",
                "date_from": "2025-07-31",
                "date_to": "2025-08-15",
                "status": "FINISHED"
            }
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get matches first
        print("Getting matches...")
        try:
            response = await client.post(
                soccer_mcp_url,
                json=get_matches_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result and result["result"].get("ok"):
                    matches = result["result"]["data"]["matches"]
                    if matches:
                        match = matches[0]  # Liverpool vs Bournemouth
                        match_id = match["id"]
                        print(f"Found match ID: {match_id}")
                        print(f"Match: {match['homeTeam']['name']} vs {match['awayTeam']['name']}")
                        
                        # Now get detailed match info
                        print(f"\nGetting detailed match info for ID {match_id}...")
                        
                        match_details_payload = {
                            "jsonrpc": "2.0",
                            "method": "tools/call",
                            "id": 2,
                            "params": {
                                "name": "getMatchDetails",
                                "arguments": {"match_id": match_id}
                            }
                        }
                        
                        detail_response = await client.post(
                            soccer_mcp_url,
                            json=match_details_payload,
                            headers={"Content-Type": "application/json"}
                        )
                        
                        if detail_response.status_code == 200:
                            detail_result = detail_response.json()
                            print("\n" + "="*60)
                            print("DETAILED MATCH RESPONSE:")
                            print("="*60)
                            print(json.dumps(detail_result, indent=2))
                            
                            # Check specifically for statistics
                            if "result" in detail_result and detail_result["result"].get("ok"):
                                match_data = detail_result["result"]["data"]["match"]
                                print(f"\n" + "="*60)
                                print("STATISTICS CHECK:")
                                print("="*60)
                                
                                home_stats = match_data.get("homeTeam", {}).get("statistics")
                                away_stats = match_data.get("awayTeam", {}).get("statistics")
                                
                                print(f"Home team statistics: {home_stats}")
                                print(f"Away team statistics: {away_stats}")
                                
                                goals = match_data.get("goals", [])
                                print(f"Goals data: {goals}")
                                
                                bookings = match_data.get("bookings", [])
                                print(f"Bookings data: {bookings}")
                        else:
                            print(f"Detail request failed: {detail_response.status_code}")
                            print(detail_response.text)
                    else:
                        print("No matches found")
                else:
                    print("Error in matches result:", result)
            else:
                print(f"HTTP Error: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_match_details())