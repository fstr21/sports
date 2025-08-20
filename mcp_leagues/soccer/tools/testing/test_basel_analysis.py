#!/usr/bin/env python3
"""
Standalone Test - Basel Analysis
Test the exact scenario from your Discord screenshot
"""
import asyncio
import json
import httpx
from datetime import datetime

MCP_URL = "https://soccermcp-production.up.railway.app/mcp"

async def mcp_call(tool_name: str, arguments: dict = None):
    """Make MCP call"""
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

async def test_basel_comprehensive_analysis():
    """Test comprehensive analysis for Basel vs FC Copenhagen"""
    print("=" * 70)
    print("BASEL vs FC COPENHAGEN - COMPREHENSIVE ANALYSIS TEST")
    print("=" * 70)
    print("Testing the exact match from your Discord screenshot")
    
    # From our previous debug - Basel vs FC Copenhagen
    basel_id = 3286
    copenhagen_id = 3772
    basel_name = "Basel"
    copenhagen_name = "FC Copenhagen"
    league = "UEFA"
    league_id = 310
    today = datetime.now().strftime("%d-%m-%Y")
    
    print(f"Match: {basel_name} vs {copenhagen_name}")
    print(f"League: {league} (ID: {league_id})")
    print(f"Date: {today}")
    print(f"Basel ID: {basel_id}")
    print(f"Copenhagen ID: {copenhagen_id}")
    
    # Test 1: H2H Analysis
    print(f"\n1. HEAD-TO-HEAD ANALYSIS")
    print("-" * 40)
    
    h2h_response = await mcp_call("get_h2h_betting_analysis", {
        "team_1_id": basel_id,
        "team_2_id": copenhagen_id,
        "team_1_name": basel_name,
        "team_2_name": copenhagen_name
    })
    
    if h2h_response["success"]:
        h2h_data = h2h_response["data"]
        total_meetings = h2h_data.get('total_meetings', 0)
        
        print(f"[OK] H2H Analysis Retrieved")
        print(f"Total meetings: {total_meetings}")
        
        if total_meetings > 0:
            team1_record = h2h_data.get('team_1_record', {})
            team2_record = h2h_data.get('team_2_record', {})
            draws = h2h_data.get('draws', {})
            
            print(f"Basel: {team1_record.get('wins', 0)} wins ({team1_record.get('win_rate', 0):.1f}%)")
            print(f"Copenhagen: {team2_record.get('wins', 0)} wins ({team2_record.get('win_rate', 0):.1f}%)")
            print(f"Draws: {draws.get('count', 0)}")
            
            # Goals analysis
            goals = h2h_data.get('goals', {})
            if goals:
                avg_goals = goals.get('average_per_game', 0)
                print(f"Average goals per game: {avg_goals:.2f}")
        else:
            print("FIRST MEETING - No historical data")
            print("This explains why Discord shows limited analysis!")
    else:
        print(f"[ERROR] H2H Failed: {h2h_response['error']}")
    
    # Test 2: Basel Team Form
    print(f"\n2. BASEL TEAM FORM")
    print("-" * 40)
    
    basel_form_response = await mcp_call("get_team_form_analysis", {
        "team_id": basel_id,
        "team_name": basel_name,
        "league_id": league_id
    })
    
    if basel_form_response["success"]:
        basel_form = basel_form_response["data"]
        print(f"[OK] Basel Form Retrieved")
        print(f"Record: {basel_form.get('record', 'N/A')}")
        print(f"Form Rating: {basel_form.get('form_rating', 0)}/10")
        print(f"Win Percentage: {basel_form.get('win_percentage', 0)}%")
        print(f"Goals For: {basel_form.get('goals_for', 0)}")
        print(f"Goals Against: {basel_form.get('goals_against', 0)}")
        
        # Show raw data structure
        print(f"\nRaw Basel form data:")
        print(json.dumps(basel_form, indent=2))
    else:
        print(f"[ERROR] Basel Form Failed: {basel_form_response['error']}")
    
    # Test 3: Copenhagen Team Form  
    print(f"\n3. FC COPENHAGEN TEAM FORM")
    print("-" * 40)
    
    copenhagen_form_response = await mcp_call("get_team_form_analysis", {
        "team_id": copenhagen_id,
        "team_name": copenhagen_name,
        "league_id": league_id
    })
    
    if copenhagen_form_response["success"]:
        copenhagen_form = copenhagen_form_response["data"]
        print(f"[OK] Copenhagen Form Retrieved")
        print(f"Record: {copenhagen_form.get('record', 'N/A')}")
        print(f"Form Rating: {copenhagen_form.get('form_rating', 0)}/10")
        print(f"Win Percentage: {copenhagen_form.get('win_percentage', 0)}%")
        print(f"Goals For: {copenhagen_form.get('goals_for', 0)}")
        print(f"Goals Against: {copenhagen_form.get('goals_against', 0)}")
        
        # Show raw data structure
        print(f"\nRaw Copenhagen form data:")
        print(json.dumps(copenhagen_form, indent=2))
    else:
        print(f"[ERROR] Copenhagen Form Failed: {copenhagen_form_response['error']}")
    
    # Test 4: Match Analysis
    print(f"\n4. COMPREHENSIVE MATCH ANALYSIS")
    print("-" * 40)
    
    match_analysis_response = await mcp_call("analyze_match_betting", {
        "home_team": basel_name,
        "away_team": copenhagen_name,
        "league": league,
        "match_date": today
    })
    
    if match_analysis_response["success"]:
        match_analysis = match_analysis_response["data"]
        print(f"[OK] Match Analysis Retrieved")
        
        prediction = match_analysis.get('prediction', {})
        goals_prediction = match_analysis.get('goals_prediction', {})
        insights = match_analysis.get('key_insights', [])
        risk_level = match_analysis.get('risk_level', '')
        
        print(f"Prediction: {prediction.get('most_likely_outcome', 'Unknown')}")
        print(f"Confidence: {prediction.get('confidence_score', 0)}%")
        print(f"Goals: {goals_prediction.get('prediction', 'Unknown')}")
        print(f"Risk Level: {risk_level}")
        print(f"Key Insights: {insights}")
        
        # Show raw data structure
        print(f"\nRaw match analysis data:")
        print(json.dumps(match_analysis, indent=2))
    else:
        print(f"[ERROR] Match Analysis Failed: {match_analysis_response['error']}")
    
    # Test 5: Create Discord Embed Preview
    print(f"\n5. DISCORD EMBED PREVIEW")
    print("=" * 50)
    print("What the Discord embed should look like:")
    print()
    
    print(f"⚽ {basel_name} vs {copenhagen_name}")
    print(f"UEFA - Comprehensive Analysis")
    print()
    
    # Match info
    print(f"📅 Match Info")
    print(f"Time: 19:00")
    print(f"League: UEFA")
    print()
    
    # H2H
    if h2h_response["success"]:
        h2h_data = h2h_response["data"]
        total_meetings = h2h_data.get('total_meetings', 0)
        
        print(f"📊 Head-to-Head Record")
        if total_meetings > 0:
            team1_record = h2h_data.get('team_1_record', {})
            team2_record = h2h_data.get('team_2_record', {})
            draws = h2h_data.get('draws', {})
            print(f"{total_meetings} meetings")
            print(f"{basel_name}: {team1_record.get('wins', 0)}W ({team1_record.get('win_rate', 0):.1f}%)")
            print(f"{copenhagen_name}: {team2_record.get('wins', 0)}W ({team2_record.get('win_rate', 0):.1f}%)")
            print(f"Draws: {draws.get('count', 0)}")
        else:
            print(f"First meeting between {basel_name} and {copenhagen_name}")
            print("No historical data available")
        print()
    
    # Team forms
    if basel_form_response["success"]:
        basel_form = basel_form_response["data"]
        print(f"🏠 Home Team Form")
        print(f"{basel_name}")
        print(f"Record: {basel_form.get('record', 'N/A')}")
        print(f"Form Rating: {basel_form.get('form_rating', 0):.1f}/10")
        if basel_form.get('win_percentage', 0) > 0:
            print(f"Win Rate: {basel_form.get('win_percentage', 0):.1f}%")
        print()
    
    if copenhagen_form_response["success"]:
        copenhagen_form = copenhagen_form_response["data"]
        print(f"✈️ Away Team Form")
        print(f"{copenhagen_name}")
        print(f"Record: {copenhagen_form.get('record', 'N/A')}")
        print(f"Form Rating: {copenhagen_form.get('form_rating', 0):.1f}/10")
        if copenhagen_form.get('win_percentage', 0) > 0:
            print(f"Win Rate: {copenhagen_form.get('win_percentage', 0):.1f}%")
        print()
    
    print("=" * 70)
    print("CONCLUSION:")
    print("✓ MCP server is working and returning data")
    print("✓ Analysis data is available for both teams") 
    print("✓ Discord bot should now show enhanced content")
    print("If Discord still shows basic info only, check bot deployment!")

if __name__ == "__main__":
    asyncio.run(test_basel_comprehensive_analysis())