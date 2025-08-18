#!/usr/bin/env python3
"""
Quick Demo Script - Enhanced Soccer Betting Analyzer MCP

Demonstrates all 5 betting analysis tools with real examples and readable output.
Perfect for showcasing the capabilities to potential subscribers.
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

import httpx

# Remote MCP server URL
MCP_URL = "https://soccermcp-production.up.railway.app/mcp"

def print_section(title: str, emoji: str = ""):
    """Print formatted section header"""
    print("\n" + "🎯" * 30)
    print(f"{emoji} {title}")
    print("🎯" * 30)

def print_clean_result(data: Dict[str, Any], highlights: list = None):
    """Print key information in a clean, readable format"""
    if isinstance(data, dict):
        if "error" in data:
            print(f"❌ Error: {data['error']}")
            return
        
        # Extract key information based on highlights
        if highlights:
            for key in highlights:
                if key in data:
                    value = data[key]
                    print(f"📊 {key.replace('_', ' ').title()}: {value}")
        else:
            # Default clean printing
            for key, value in data.items():
                if key in ['error', 'jsonrpc', 'id']:
                    continue
                if isinstance(value, (str, int, float)):
                    print(f"📊 {key.replace('_', ' ').title()}: {value}")
                elif isinstance(value, dict) and len(value) <= 3:
                    print(f"📊 {key.replace('_', ' ').title()}:")
                    for sub_key, sub_value in value.items():
                        print(f"   • {sub_key.replace('_', ' ')}: {sub_value}")

async def mcp_call(method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make an MCP JSON-RPC call"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                MCP_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
            
    except Exception as e:
        return {"error": f"Request failed: {e}"}

async def demo_get_matches():
    """Demo: Find matches for betting analysis"""
    print_section("DEMO 1: FIND MATCHES FOR BETTING", "🔍")
    print("This tool finds soccer matches available for betting analysis...")
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
    
    result = await mcp_call("tools/call", {
        "name": "get_betting_matches",
        "arguments": {
            "date": tomorrow,
            "league_filter": "EPL"
        }
    })
    
    if "error" in result:
        print(f"❌ {result['error']}")
        return
    
    try:
        content = result["result"]["content"][0]["text"]
        data = json.loads(content)
        
        print(f"📅 Search Date: {data.get('date', 'N/A')}")
        print(f"⚽ Total Matches Found: {data.get('total_matches', 0)}")
        print(f"🏆 Leagues Searched: {', '.join(data.get('leagues_searched', []))}")
        
        matches_by_league = data.get('matches_by_league', {})
        for league, matches in matches_by_league.items():
            if matches:
                print(f"\n🏴󠁧󠁢󠁥󠁮󠁧󠁿 {league} Matches ({len(matches)}):")
                for i, match in enumerate(matches[:3], 1):  # Show first 3
                    teams = match.get('teams', {})
                    home = teams.get('home', {}).get('name', 'TBD')
                    away = teams.get('away', {}).get('name', 'TBD')
                    time = match.get('time', 'TBD')
                    status = match.get('status', 'scheduled')
                    print(f"   {i}. {home} vs {away} ({time}) - {status}")
        
        print("\n✅ This shows all available matches for betting analysis!")
        
    except Exception as e:
        print(f"❌ Failed to parse response: {e}")

async def demo_team_form():
    """Demo: Analyze team form and trends"""
    print_section("DEMO 2: TEAM FORM ANALYSIS", "📈")
    print("This tool analyzes a team's recent performance and betting trends...")
    
    result = await mcp_call("tools/call", {
        "name": "get_team_form_analysis", 
        "arguments": {
            "team_id": 100,
            "team_name": "Chelsea",
            "league_id": 228
        }
    })
    
    if "error" in result:
        print(f"❌ {result['error']}")
        return
    
    try:
        content = result["result"]["content"][0]["text"]
        data = json.loads(content)
        
        print(f"⚽ Team: {data.get('team_name', 'Unknown')}")
        print(f"📊 Recent Matches Analyzed: {data.get('matches_found', 0)}")
        print(f"🏆 Win Percentage: {data.get('win_percentage', 0):.1f}%")
        print(f"📈 Form Rating: {data.get('form_rating', 0)}/10")
        print(f"🚀 Momentum: {data.get('momentum', 'Unknown')}")
        print(f"⚽ Goals Per Game: {data.get('attacking_strength', 0):.2f}")
        print(f"🛡️ Goals Against Per Game: {data.get('defensive_strength', 0):.2f}")
        
        betting_trends = data.get('betting_trends', {})
        if betting_trends:
            print(f"\n💰 BETTING TRENDS:")
            print(f"   📊 Over 2.5 Goals: {betting_trends.get('over_2_5_percentage', 0):.1f}%")
            print(f"   🎯 Both Teams Score: {betting_trends.get('both_teams_score_percentage', 0):.1f}%")
            print(f"   🛡️ Clean Sheets: {betting_trends.get('clean_sheet_percentage', 0):.1f}%")
        
        print("\n✅ Perfect for assessing team strength before betting!")
        
    except Exception as e:
        print(f"❌ Failed to parse response: {e}")

async def demo_h2h_analysis():
    """Demo: Historical head-to-head analysis"""
    print_section("DEMO 3: HEAD-TO-HEAD HISTORY", "⚔️")
    print("This tool analyzes historical matchups between two teams...")
    
    result = await mcp_call("tools/call", {
        "name": "get_h2h_betting_analysis",
        "arguments": {
            "team_1_id": 100,
            "team_2_id": 200, 
            "team_1_name": "Chelsea",
            "team_2_name": "Arsenal"
        }
    })
    
    if "error" in result:
        print(f"❌ {result['error']}")
        return
    
    try:
        content = result["result"]["content"][0]["text"]
        data = json.loads(content)
        
        if "error" in data:
            print(f"⚠️ {data['error']}")
            print("📝 Note: This is expected when team IDs don't have historical data")
            return
        
        print(f"⚔️ Matchup: {data.get('teams', 'Unknown')}")
        print(f"📅 Total Historical Meetings: {data.get('total_meetings', 0)}")
        
        team1 = data.get('team_1_record', {})
        team2 = data.get('team_2_record', {})
        
        if team1 and team2:
            print(f"🏆 {team1.get('name', 'Team 1')}: {team1.get('wins', 0)} wins ({team1.get('win_rate', 0):.1f}%)")
            print(f"🏆 {team2.get('name', 'Team 2')}: {team2.get('wins', 0)} wins ({team2.get('win_rate', 0):.1f}%)")
        
        draws = data.get('draws', {})
        if draws:
            print(f"🤝 Draws: {draws.get('count', 0)} ({draws.get('rate', 0):.1f}%)")
        
        goals = data.get('goals', {})
        if goals:
            print(f"⚽ Average Goals Per Game: {goals.get('average_per_game', 0):.2f}")
        
        betting_insights = data.get('betting_insights', {})
        if betting_insights:
            print(f"\n💰 BETTING INSIGHTS:")
            print(f"   📊 Goals Trend: {betting_insights.get('goals_trend', 'Unknown')}")
            print(f"   📈 High Scoring: {betting_insights.get('high_scoring', False)}")
            print(f"   📉 Low Scoring: {betting_insights.get('low_scoring', False)}")
        
        print("\n✅ Historical data helps predict match patterns!")
        
    except Exception as e:
        print(f"❌ Failed to parse response: {e}")

async def demo_match_analysis():
    """Demo: Comprehensive match betting analysis"""
    print_section("DEMO 4: COMPREHENSIVE MATCH ANALYSIS", "🎯")
    print("This is the MAIN FEATURE - complete betting analysis for a specific match...")
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
    
    result = await mcp_call("tools/call", {
        "name": "analyze_match_betting",
        "arguments": {
            "home_team": "Chelsea",
            "away_team": "Arsenal",
            "league": "EPL",
            "match_date": tomorrow
        }
    })
    
    if "error" in result:
        print(f"❌ {result['error']}")
        return
    
    try:
        content = result["result"]["content"][0]["text"]
        data = json.loads(content)
        
        if "error" in data:
            print(f"⚠️ {data['error']}")
            print("📝 Note: No Chelsea vs Arsenal match found for tomorrow")
            
            available = data.get('available_matches', [])
            if available:
                print(f"\n📅 Available matches for {tomorrow}:")
                for i, match in enumerate(available[:3], 1):
                    print(f"   {i}. {match}")
            return
        
        match_info = data.get('match_info', {})
        predictions = data.get('predictions', {})
        
        print(f"⚽ MATCH: {match_info.get('home_team', 'TBD')} vs {match_info.get('away_team', 'TBD')}")
        print(f"🏆 League: {match_info.get('league', 'Unknown')}")
        print(f"📅 Date: {match_info.get('date', 'TBD')}")
        print(f"📊 Status: {match_info.get('status', 'scheduled')}")
        
        match_winner = predictions.get('match_winner', {})
        if match_winner:
            print(f"\n🎯 MATCH WINNER PREDICTION:")
            print(f"   🏆 Prediction: {match_winner.get('prediction', 'N/A')}")
            print(f"   📊 Confidence: {match_winner.get('confidence', 'N/A')} ({match_winner.get('confidence_percentage', 0):.1f}%)")
        
        goals = predictions.get('goals', {})
        if goals:
            print(f"\n⚽ GOALS PREDICTION:")
            print(f"   🎯 Prediction: {goals.get('prediction', 'N/A')}")
            print(f"   📊 Expected Goals: {goals.get('expected_goals', 0):.2f}")
            print(f"   📈 Confidence: {goals.get('confidence', 'N/A')}")
        
        insights = predictions.get('key_insights', [])
        if insights:
            print(f"\n💡 KEY BETTING INSIGHTS:")
            for insight in insights[:3]:
                print(f"   • {insight}")
        
        print(f"\n🎯 Overall Confidence: {data.get('confidence_level', 'Unknown')}")
        print("\n✅ This combines everything into actionable betting recommendations!")
        
    except Exception as e:
        print(f"❌ Failed to parse response: {e}")

async def demo_value_bets():
    """Demo: Find value bets across entire league"""
    print_section("DEMO 5: LEAGUE VALUE BET FINDER", "💎")
    print("This tool scans an entire league to find the best betting opportunities...")
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
    
    result = await mcp_call("tools/call", {
        "name": "get_league_value_bets",
        "arguments": {
            "league": "EPL",
            "date": tomorrow,
            "min_confidence": 50.0
        }
    })
    
    if "error" in result:
        print(f"❌ {result['error']}")
        return
    
    try:
        content = result["result"]["content"][0]["text"]
        data = json.loads(content)
        
        print(f"🏆 League: {data.get('league', 'Unknown')}")
        print(f"📅 Date: {data.get('date', 'Unknown')}")
        print(f"📊 Minimum Confidence: {data.get('min_confidence_threshold', 0)}%")
        print(f"⚽ Matches Analyzed: {data.get('total_matches_analyzed', 0)}")
        print(f"💎 Value Bets Found: {data.get('value_bets_found', 0)}")
        
        summary = data.get('summary', {})
        if summary:
            print(f"\n📈 SUMMARY:")
            print(f"   🔥 High Confidence Bets (80%+): {summary.get('high_confidence_bets', 0)}")
            print(f"   📊 Medium Confidence Bets (60-80%): {summary.get('medium_confidence_bets', 0)}")
            print(f"   📈 Average Confidence: {summary.get('avg_confidence', 0):.1f}%")
        
        value_bets = data.get('value_bets', [])
        if value_bets:
            print(f"\n💎 VALUE BETS FOUND:")
            for i, bet in enumerate(value_bets[:3], 1):
                print(f"   {i}. {bet.get('match', 'Unknown')}")
                print(f"      🎯 Recommended: {bet.get('recommended_bet', 'N/A')}")
                print(f"      📊 Confidence: {bet.get('confidence', 'N/A')}")
                print(f"      ⚽ Expected Goals: {bet.get('expected_goals', 'N/A')}")
        else:
            print(f"\n📝 No value bets found meeting {data.get('min_confidence_threshold', 50)}% confidence threshold")
            print("💡 Try lowering the confidence threshold or checking a different date")
        
        print("\n✅ Perfect for finding the best betting opportunities!")
        
    except Exception as e:
        print(f"❌ Failed to parse response: {e}")

async def run_full_demo():
    """Run complete demonstration of all tools"""
    print("🎯" * 20)
    print("ENHANCED SOCCER BETTING ANALYZER")
    print("Complete MCP Server Demo")
    print("🎯" * 20)
    print("\nThis demo showcases all 5 betting analysis tools available to your subscribers!")
    
    # Check server connection
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://soccermcp-production.up.railway.app/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connected to: {data.get('server')}")
            print(f"✅ Version: {data.get('version')}")
        else:
            print(f"⚠️ Server responded with: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach server: {e}")
        return
    
    input("\nPress Enter to start the demo...")
    
    # Run all demos
    await demo_get_matches()
    input("\nPress Enter to continue to next demo...")
    
    await demo_team_form()
    input("\nPress Enter to continue to next demo...")
    
    await demo_h2h_analysis()
    input("\nPress Enter to continue to next demo...")
    
    await demo_match_analysis()
    input("\nPress Enter to continue to next demo...")
    
    await demo_value_bets()
    
    print_section("DEMO COMPLETE! 🎉", "🎉")
    print("Your Enhanced Soccer Betting Analyzer MCP Server is fully operational!")
    print("\n🚀 READY FOR SUBSCRIBERS:")
    print("• Discord bot integration")
    print("• Web application calls")
    print("• Multi-tenant access")
    print("• Professional betting analysis")
    print("\n💰 BUSINESS VALUE:")
    print("• Comprehensive match analysis")
    print("• Value bet identification")
    print("• Historical insights")
    print("• Confidence-scored predictions")
    print("\n🎯 Endpoint: https://soccermcp-production.up.railway.app/mcp")

if __name__ == "__main__":
    try:
        asyncio.run(run_full_demo())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!")
    except Exception as e:
        print(f"\nDemo error: {e}")
        sys.exit(1)