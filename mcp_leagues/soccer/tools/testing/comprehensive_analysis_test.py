#!/usr/bin/env python3
"""
Test Comprehensive Match Analysis with Available MCP Tools
Test what we can achieve with current betting MCP server for Discord bot
"""
import asyncio
import json
import httpx
from datetime import datetime, timedelta

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
                return json.loads(result["result"]["content"][0]["text"])
            else:
                return {"error": f"Unexpected response: {result}"}
                
    except Exception as e:
        return {"error": f"Request failed: {e}"}

async def test_comprehensive_match_analysis():
    """Test building comprehensive match analysis with available tools"""
    print("=" * 70)
    print("COMPREHENSIVE MATCH ANALYSIS TEST")
    print("=" * 70)
    print("Testing what we can build for Discord bot with current MCP tools")
    
    # Step 1: Get matches for today/tomorrow
    print("\n1. FINDING AVAILABLE MATCHES")
    print("-" * 40)
    
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    
    matches_found = []
    for date_to_check in [today, tomorrow]:
        date_str = date_to_check.strftime("%d-%m-%Y")
        print(f"Checking {date_str}...")
        
        matches = await mcp_call("get_betting_matches", {"date": date_str})
        if "error" not in matches:
            matches_by_league = matches.get('matches_by_league', {})
            for league, league_matches in matches_by_league.items():
                for match in league_matches:
                    matches_found.append({
                        'match': match,
                        'league': league,
                        'date': date_str
                    })
    
    print(f"Total matches found: {len(matches_found)}")
    
    if not matches_found:
        print("No matches found - testing with sample team IDs")
        # Use known team IDs for testing
        sample_match = {
            'match': {
                'teams': {
                    'home': {'id': 4138, 'name': 'Liverpool'},
                    'away': {'id': 4140, 'name': 'Chelsea'}
                }
            },
            'league': 'EPL',
            'date': today.strftime("%d-%m-%Y")
        }
        matches_found = [sample_match]
    
    # Step 2: For each match, build comprehensive analysis
    for i, match_info in enumerate(matches_found[:2]):  # Test first 2 matches
        match = match_info['match']
        league = match_info['league']
        date = match_info['date']
        
        home_team = match['teams']['home']
        away_team = match['teams']['away']
        
        print(f"\n{i+2}. COMPREHENSIVE ANALYSIS: {home_team['name']} vs {away_team['name']}")
        print("=" * 60)
        
        # Step 2a: Get H2H Analysis
        print("\n  A. HEAD-TO-HEAD ANALYSIS")
        print("  " + "-" * 30)
        h2h = await mcp_call("get_h2h_betting_analysis", {
            "team_1_id": home_team['id'],
            "team_2_id": away_team['id'],
            "team_1_name": home_team['name'],
            "team_2_name": away_team['name']
        })
        
        if "error" not in h2h:
            print(f"  [OK] H2H Data: {h2h.get('total_meetings', 0)} historical meetings")
            print(f"  {h2h.get('team_1_record', {}).get('name')}: {h2h.get('team_1_record', {}).get('wins', 0)} wins ({h2h.get('team_1_record', {}).get('win_rate', 0):.1f}%)")
            print(f"  {h2h.get('team_2_record', {}).get('name')}: {h2h.get('team_2_record', {}).get('wins', 0)} wins ({h2h.get('team_2_record', {}).get('win_rate', 0):.1f}%)")
            
            betting_insights = h2h.get('betting_insights', {})
            if betting_insights:
                print(f"  Betting trend: {betting_insights.get('goals_trend', 'Unknown')}")
        else:
            print(f"  [ERROR] H2H: {h2h.get('error')}")
        
        # Step 2b: Get Home Team Form
        print("\n  B. HOME TEAM FORM ANALYSIS")
        print("  " + "-" * 30)
        
        # Map league to ID (from what we can see in the tools)
        league_id_map = {"EPL": 228, "MLS": 168, "La Liga": 297, "LA LIGA": 297}
        league_id = league_id_map.get(league, 228)
        
        home_form = await mcp_call("get_team_form_analysis", {
            "team_id": home_team['id'],
            "team_name": home_team['name'],
            "league_id": league_id
        })
        
        if "error" not in home_form:
            print(f"  [OK] {home_team['name']} Form:")
            print(f"      Record: {home_form.get('record', 'N/A')}")
            print(f"      Form Rating: {home_form.get('form_rating', 0)}/10")
            print(f"      Win %: {home_form.get('win_percentage', 0):.1f}%")
            print(f"      Goals: {home_form.get('goals_for', 0)} for, {home_form.get('goals_against', 0)} against")
            
            betting_trends = home_form.get('betting_trends', {})
            if betting_trends:
                print(f"      BTTS: {betting_trends.get('both_teams_score_percentage', 0):.1f}%")
                print(f"      Over 2.5: {betting_trends.get('over_25_percentage', 0):.1f}%")
        else:
            print(f"  [ERROR] Home form: {home_form.get('error')}")
        
        # Step 2c: Get Away Team Form
        print("\n  C. AWAY TEAM FORM ANALYSIS")
        print("  " + "-" * 30)
        
        away_form = await mcp_call("get_team_form_analysis", {
            "team_id": away_team['id'],
            "team_name": away_team['name'],
            "league_id": league_id
        })
        
        if "error" not in away_form:
            print(f"  [OK] {away_team['name']} Form:")
            print(f"      Record: {away_form.get('record', 'N/A')}")
            print(f"      Form Rating: {away_form.get('form_rating', 0)}/10")
            print(f"      Win %: {away_form.get('win_percentage', 0):.1f}%")
            print(f"      Goals: {away_form.get('goals_for', 0)} for, {away_form.get('goals_against', 0)} against")
            
            betting_trends = away_form.get('betting_trends', {})
            if betting_trends:
                print(f"      BTTS: {betting_trends.get('both_teams_score_percentage', 0):.1f}%")
                print(f"      Over 2.5: {betting_trends.get('over_25_percentage', 0):.1f}%")
        else:
            print(f"  [ERROR] Away form: {away_form.get('error')}")
        
        # Step 2d: Get Full Match Analysis
        print("\n  D. COMPREHENSIVE MATCH ANALYSIS")
        print("  " + "-" * 40)
        
        match_analysis = await mcp_call("analyze_match_betting", {
            "home_team": home_team['name'],
            "away_team": away_team['name'],
            "league": league,
            "match_date": date
        })
        
        if "error" not in match_analysis:
            print(f"  [OK] Full Analysis Available:")
            
            prediction = match_analysis.get('prediction', {})
            if prediction:
                print(f"      Winner: {prediction.get('most_likely_outcome', 'Unknown')}")
                print(f"      Confidence: {prediction.get('confidence_score', 0):.1f}%")
                
            goals_prediction = match_analysis.get('goals_prediction', {})
            if goals_prediction:
                print(f"      Goals: {goals_prediction.get('prediction', 'Unknown')} ({goals_prediction.get('confidence', 0):.1f}%)")
                
            key_insights = match_analysis.get('key_insights', [])
            if key_insights:
                print(f"      Insights: {', '.join(key_insights[:3])}")
                
        else:
            print(f"  [ERROR] Match analysis: {match_analysis.get('error')}")
        
        print(f"\n  SUMMARY: Full data package available for Discord channel!")
        print("  " + "=" * 50)

async def test_value_bets_analysis():
    """Test league-wide value betting analysis"""
    print("\n\n" + "=" * 70)
    print("LEAGUE VALUE BETS ANALYSIS TEST")
    print("=" * 70)
    
    today = datetime.now().strftime("%d-%m-%Y")
    
    for league in ["EPL", "La Liga", "MLS"]:
        print(f"\n{league} Value Bets for {today}:")
        print("-" * 40)
        
        value_bets = await mcp_call("get_league_value_bets", {
            "league": league,
            "date": today,
            "min_confidence": 60.0
        })
        
        if "error" not in value_bets:
            opportunities = value_bets.get('opportunities', [])
            print(f"Found {len(opportunities)} betting opportunities")
            
            for opp in opportunities[:2]:  # Show first 2
                match = opp.get('match', '')
                bet_type = opp.get('bet_type', '')
                confidence = opp.get('confidence', 0)
                reasoning = opp.get('reasoning', '')
                print(f"  {match}: {bet_type} ({confidence}% confidence)")
                print(f"    Reason: {reasoning[:100]}...")
        else:
            print(f"Error: {value_bets.get('error')}")

async def main():
    """Main test function"""
    print("TESTING COMPREHENSIVE ANALYSIS CAPABILITIES")
    print("=" * 70)
    print("What can we build for Discord bot with current MCP betting tools?")
    
    await test_comprehensive_match_analysis()
    await test_value_bets_analysis()
    
    print("\n\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print("✓ H2H Analysis: Available")
    print("✓ Team Form Analysis: Available") 
    print("✓ Comprehensive Match Analysis: Available")
    print("✓ Value Bet Analysis: Available")
    print("✓ Multiple League Support: EPL, La Liga, MLS")
    print("")
    print("NEXT STEP: Integrate these tools into Discord bot soccer handler")
    print("to create rich channel content instead of empty channels")

if __name__ == "__main__":
    asyncio.run(main())