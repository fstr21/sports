#!/usr/bin/env python3
"""
Debug Discord Bot Flow - Test what happens when creating channels
Simulate the exact flow the Discord bot follows
"""
import asyncio
import json
import httpx
from datetime import datetime

MCP_URL = "https://soccermcp-production.up.railway.app/mcp"

async def mcp_call(tool_name: str, arguments: dict = None):
    """Make MCP call exactly like Discord bot does"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(MCP_URL, json=payload)
            result = response.json()
            
            if "result" in result and "content" in result["result"]:
                return {"success": True, "data": json.loads(result["result"]["content"][0]["text"])}
            else:
                return {"success": False, "error": f"Unexpected response: {result}"}
                
    except Exception as e:
        return {"success": False, "error": f"Request failed: {e}"}

async def debug_channel_creation_flow():
    """Debug the exact flow when creating Discord channels"""
    print("=" * 70)
    print("DEBUGGING DISCORD BOT CHANNEL CREATION FLOW")
    print("=" * 70)
    
    # Step 1: Get matches (like Discord bot does)
    print("\n1. GETTING MATCHES (Discord bot step)")
    print("-" * 50)
    
    today = datetime.now().strftime("%d-%m-%Y")
    print(f"Calling get_betting_matches with date: {today}")
    
    matches_response = await mcp_call("get_betting_matches", {"date": today})
    
    if not matches_response["success"]:
        print(f"❌ FAILED to get matches: {matches_response['error']}")
        return
    
    matches_data = matches_response["data"]
    matches_by_league = matches_data.get('matches_by_league', {})
    
    # Find a match to test with
    test_match = None
    for league, league_matches in matches_by_league.items():
        if league_matches:
            test_match = league_matches[0]
            test_league = league
            break
    
    if not test_match:
        print("❌ No matches found to test with")
        return
    
    print(f"[OK] Found match: {test_match['teams']['home']['name']} vs {test_match['teams']['away']['name']}")
    print(f"   League: {test_league}")
    print(f"   Home ID: {test_match['teams']['home']['id']}")
    print(f"   Away ID: {test_match['teams']['away']['id']}")
    
    # Step 2: Test comprehensive analysis calls (like Discord bot does)
    print(f"\n2. TESTING COMPREHENSIVE ANALYSIS (Discord bot step)")
    print("-" * 50)
    
    home_id = test_match['teams']['home']['id']
    away_id = test_match['teams']['away']['id']
    home_name = test_match['teams']['home']['name']
    away_name = test_match['teams']['away']['name']
    
    # Map league to ID (same as Discord bot)
    league_map = {"EPL": 228, "La Liga": 297, "MLS": 168, "UEFA": 310}
    league_id = league_map.get(test_league, 228)
    
    print(f"Using league_id: {league_id} for {test_league}")
    
    # Test H2H analysis
    print(f"\n  A. Testing get_h2h_betting_analysis:")
    h2h_response = await mcp_call("get_h2h_betting_analysis", {
        "team_1_id": home_id,
        "team_2_id": away_id,
        "team_1_name": home_name,
        "team_2_name": away_name
    })
    
    if h2h_response["success"]:
        h2h_data = h2h_response["data"]
        print(f"     [OK] H2H SUCCESS: {h2h_data.get('total_meetings', 0)} meetings")
        print(f"     {home_name}: {h2h_data.get('team_1_record', {}).get('wins', 0)} wins")
        print(f"     {away_name}: {h2h_data.get('team_2_record', {}).get('wins', 0)} wins")
    else:
        print(f"     [ERROR] H2H FAILED: {h2h_response['error']}")
    
    # Test home team form
    print(f"\n  B. Testing get_team_form_analysis (Home):")
    home_form_response = await mcp_call("get_team_form_analysis", {
        "team_id": home_id,
        "team_name": home_name,
        "league_id": league_id
    })
    
    if home_form_response["success"]:
        home_form = home_form_response["data"]
        print(f"     [OK] HOME FORM SUCCESS: {home_form.get('record', 'N/A')}")
        print(f"     Form rating: {home_form.get('form_rating', 0)}/10")
    else:
        print(f"     [ERROR] HOME FORM FAILED: {home_form_response['error']}")
    
    # Test away team form  
    print(f"\n  C. Testing get_team_form_analysis (Away):")
    away_form_response = await mcp_call("get_team_form_analysis", {
        "team_id": away_id,
        "team_name": away_name,
        "league_id": league_id
    })
    
    if away_form_response["success"]:
        away_form = away_form_response["data"]
        print(f"     [OK] AWAY FORM SUCCESS: {away_form.get('record', 'N/A')}")
        print(f"     Form rating: {away_form.get('form_rating', 0)}/10")
    else:
        print(f"     [ERROR] AWAY FORM FAILED: {away_form_response['error']}")
    
    # Test match analysis
    print(f"\n  D. Testing analyze_match_betting:")
    match_analysis_response = await mcp_call("analyze_match_betting", {
        "home_team": home_name,
        "away_team": away_name,
        "league": test_league,
        "match_date": today
    })
    
    if match_analysis_response["success"]:
        match_analysis = match_analysis_response["data"]
        prediction = match_analysis.get('prediction', {})
        print(f"     [OK] MATCH ANALYSIS SUCCESS")
        print(f"     Prediction: {prediction.get('most_likely_outcome', 'Unknown')}")
        print(f"     Confidence: {prediction.get('confidence_score', 0)}%")
    else:
        print(f"     [ERROR] MATCH ANALYSIS FAILED: {match_analysis_response['error']}")
    
    # Step 3: Summary
    print(f"\n3. SUMMARY - WHY DISCORD BOT MIGHT SHOW LIMITED INFO")
    print("=" * 50)
    
    if h2h_response["success"]:
        print("[OK] H2H data available - should show in Discord")
    else:
        print("[ERROR] H2H data failed - won't show in Discord")
    
    if home_form_response["success"] and away_form_response["success"]:
        print("[OK] Team form data available - should show in Discord") 
    else:
        print("[ERROR] Team form data failed - won't show in Discord")
    
    if match_analysis_response["success"]:
        print("[OK] Match analysis available - should show predictions")
    else:
        print("[ERROR] Match analysis failed - no predictions in Discord")
    
    print(f"\nIf Discord bot only shows basic info, check:")
    print("1. Are team IDs being extracted correctly from match data?")
    print("2. Is the _add_h2h_analysis_to_embed method being called?")
    print("3. Are there formatting errors in the embed creation?")
    print("4. Check Discord bot logs for errors during analysis")

if __name__ == "__main__":
    asyncio.run(debug_channel_creation_flow())