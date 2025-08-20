#!/usr/bin/env python3
"""
Explore Soccer MCP Endpoints
Test existing MCP tools to understand what data is available for comprehensive match analysis
"""
import asyncio
import json
import httpx
from datetime import datetime

# MCP server URL from MCP_TOOLS_OVERVIEW.md
MCP_URL = "https://soccermcp-production.up.railway.app/mcp"

async def mcp_call(tool_name: str, arguments: dict = None):
    """Make MCP call to test endpoints"""
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
            
            if "result" in result:
                return result["result"]
            else:
                return {"error": f"Unexpected response format: {result}"}
                
    except Exception as e:
        return {"error": f"Request failed: {e}"}

async def list_available_tools():
    """Get list of all available MCP tools"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(MCP_URL, json=payload)
            result = response.json()
            return result.get("tools", [])
    except Exception as e:
        return {"error": f"Failed to list tools: {e}"}

async def test_basic_endpoints():
    """Test basic endpoints to understand data availability"""
    print("=" * 60)
    print("TESTING BASIC MCP ENDPOINTS")
    print("=" * 60)
    
    # Test 1: List all available tools
    print("\n1. Available MCP Tools:")
    print("-" * 30)
    tools = await list_available_tools()
    if isinstance(tools, list):
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
    else:
        print(f"Error: {tools}")
    
    # Test 2: Get EPL info
    print("\n\n2. Testing get_leagues for England (country_id=8):")
    print("-" * 50)
    leagues = await mcp_call("get_leagues", {"country_id": 8})
    if "error" not in leagues:
        epl_leagues = [l for l in leagues if "Premier" in l.get("name", "")]
        for league in epl_leagues[:2]:  # Show first 2
            print(f"  - {league.get('name')} (ID: {league.get('id')})")
    else:
        print(f"Error: {leagues}")
    
    # Test 3: Get today's matches
    print("\n\n3. Testing get_matches for today:")
    print("-" * 40)
    today = datetime.now().strftime("%d/%m/%Y")
    matches = await mcp_call("get_matches", {"date": today})
    print(f"Searched for matches on: {today}")
    if "error" not in matches:
        if isinstance(matches, list) and matches:
            print(f"Found {len(matches)} matches/leagues")
            # Show structure
            print("Response structure:")
            print(json.dumps(matches[0] if matches else {}, indent=2)[:500] + "...")
        else:
            print("No matches found for today")
    else:
        print(f"Error: {matches}")

async def test_betting_analysis_tools():
    """Test the betting analysis tools mentioned in MCP_TOOLS_OVERVIEW.md"""
    print("\n\n" + "=" * 60)
    print("TESTING BETTING ANALYSIS TOOLS")
    print("=" * 60)
    
    # Test betting tools from overview
    betting_tools = [
        "get_h2h_betting_analysis",
        "get_team_form_analysis", 
        "get_betting_matches",
        "analyze_match_betting",
        "get_league_value_bets"
    ]
    
    for tool in betting_tools:
        print(f"\n4. Testing {tool}:")
        print("-" * 40)
        
        # Try with minimal parameters first
        if tool == "get_h2h_betting_analysis":
            result = await mcp_call(tool, {"team_1_id": 4138, "team_2_id": 4140, "team_1_name": "Liverpool", "team_2_name": "Chelsea"})
        elif tool == "get_team_form_analysis":
            result = await mcp_call(tool, {"team_id": 4138, "team_name": "Liverpool", "league_id": 228})
        elif tool == "get_betting_matches":
            today = datetime.now().strftime("%d-%m-%Y")
            result = await mcp_call(tool, {"date": today})
        elif tool == "analyze_match_betting":
            result = await mcp_call(tool, {"home_team_id": 4138, "away_team_id": 4140, "league_id": 228})
        elif tool == "get_league_value_bets":
            today = datetime.now().strftime("%d-%m-%Y")
            result = await mcp_call(tool, {"league_id": 228, "date": today})
        else:
            result = await mcp_call(tool, {})
        
        if "error" not in result:
            print(f"[OK] {tool} - SUCCESS")
            print("Sample response:")
            print(json.dumps(result, indent=2)[:300] + "...")
        else:
            print(f"[ERROR] {tool} - ERROR: {result.get('error', 'Unknown error')}")

async def test_comprehensive_data_endpoints():
    """Test endpoints that might provide comprehensive match data"""
    print("\n\n" + "=" * 60)
    print("TESTING COMPREHENSIVE DATA ENDPOINTS")
    print("=" * 60)
    
    # Test head-to-head
    print("\n5. Testing get_head_to_head (Liverpool vs Chelsea):")
    print("-" * 50)
    h2h = await mcp_call("get_head_to_head", {"team_1_id": 4138, "team_2_id": 4140})
    if "error" not in h2h:
        print("[OK] Head-to-head data available")
        print("Sample data:")
        print(json.dumps(h2h, indent=2)[:400] + "...")
    else:
        print(f"[ERROR] H2H Error: {h2h}")
    
    # Test team info
    print("\n\n6. Testing get_team_info (Liverpool):")
    print("-" * 40)
    team_info = await mcp_call("get_team_info", {"team_id": 4138})
    if "error" not in team_info:
        print("[OK] Team info available")
        print(f"Team: {team_info.get('name')}, Stadium: {team_info.get('stadium', {}).get('name')}")
    else:
        print(f"[ERROR] Team info error: {team_info}")
    
    # Test league standings
    print("\n\n7. Testing get_league_standings (EPL):")
    print("-" * 40)
    standings = await mcp_call("get_league_standings", {"league_id": 228})
    if "error" not in standings:
        print("[OK] League standings available")
        if isinstance(standings, list) and standings:
            print(f"Found {len(standings)} standings entries")
            # Show top team
            top_team = standings[0] if standings else {}
            print(f"Sample: {top_team.get('team', {}).get('name', 'Unknown')} - {top_team.get('stats', {}).get('points', 0)} pts")
    else:
        print(f"[ERROR] Standings error: {standings}")

async def main():
    """Main exploration function"""
    print("Soccer MCP Endpoint Explorer")
    print("=" * 60)
    print("Testing existing MCP tools to understand available data")
    print("for comprehensive match analysis implementation")
    
    try:
        # Test basic endpoints
        await test_basic_endpoints()
        
        # Test betting analysis tools
        await test_betting_analysis_tools()
        
        # Test comprehensive data endpoints  
        await test_comprehensive_data_endpoints()
        
        print("\n\n" + "=" * 60)
        print("EXPLORATION COMPLETE")
        print("=" * 60)
        print("Next steps:")
        print("1. Identify which existing tools provide the data we need")
        print("2. Determine what new tools need to be created")
        print("3. Plan comprehensive match analysis implementation")
        
    except Exception as e:
        print(f"Exploration failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())