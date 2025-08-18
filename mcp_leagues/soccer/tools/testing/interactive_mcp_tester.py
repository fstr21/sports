#!/usr/bin/env python3
"""
Interactive Enhanced Soccer Betting Analyzer MCP Tester

Easy-to-use tool for testing individual MCP tools with readable results.
Provides a menu-driven interface to test each betting analysis function.
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

import httpx

# Remote MCP server URL
MCP_URL = "https://soccermcp-production.up.railway.app/mcp"
HEALTH_URL = "https://soccermcp-production.up.railway.app/"

def print_header(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_result(data: Dict[str, Any], max_depth: int = 3):
    """Pretty print JSON data with readable formatting"""
    try:
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        print(formatted)
    except Exception as e:
        print(f"[Error formatting result]: {e}")
        print(str(data))

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

async def test_tool(tool_name: str, arguments: Dict[str, Any]):
    """Test a specific MCP tool"""
    print(f"\nCalling tool: {tool_name}")
    print(f"Arguments: {json.dumps(arguments, indent=2)}")
    
    result = await mcp_call("tools/call", {
        "name": tool_name,
        "arguments": arguments
    })
    
    print_header("RESULT")
    
    if "error" in result:
        print(f"[ERROR] {result['error']}")
        return False
    
    try:
        content = result["result"]["content"][0]["text"]
        data = json.loads(content)
        print_result(data)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to parse response: {e}")
        print("Raw response:")
        print_result(result)
        return False

async def test_get_betting_matches():
    """Test 1: Get betting matches"""
    print_header("TEST 1: GET BETTING MATCHES")
    
    print("This tool gets soccer matches for betting analysis on a specific date.")
    print("Supports filtering by league (MLS, EPL, La Liga)")
    
    # Test with different date options
    today = datetime.now().strftime("%d-%m-%Y")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
    
    print(f"\nTesting with tomorrow's date ({tomorrow}) for EPL matches...")
    
    await test_tool("get_betting_matches", {
        "date": tomorrow,
        "league_filter": "EPL"
    })
    
    input("\nPress Enter to continue...")

async def test_team_form_analysis():
    """Test 2: Team form analysis"""
    print_header("TEST 2: TEAM FORM ANALYSIS")
    
    print("This tool analyzes a team's recent form, momentum, and betting trends.")
    print("Requires team ID and league ID from SoccerDataAPI")
    
    print("\nTesting with Chelsea (example team ID)...")
    print("Note: This may return no data if team ID doesn't match current season")
    
    await test_tool("get_team_form_analysis", {
        "team_id": 100,  # Example Chelsea ID
        "team_name": "Chelsea",
        "league_id": 228  # EPL
    })
    
    input("\nPress Enter to continue...")

async def test_h2h_analysis():
    """Test 3: Head-to-head analysis"""
    print_header("TEST 3: HEAD-TO-HEAD ANALYSIS")
    
    print("This tool provides historical head-to-head analysis with betting insights.")
    print("Shows win rates, average goals, and betting trends between two teams")
    
    print("\nTesting Chelsea vs Arsenal H2H (example team IDs)...")
    
    await test_tool("get_h2h_betting_analysis", {
        "team_1_id": 100,  # Example Chelsea ID
        "team_2_id": 200,  # Example Arsenal ID
        "team_1_name": "Chelsea",
        "team_2_name": "Arsenal"
    })
    
    input("\nPress Enter to continue...")

async def test_analyze_match_betting():
    """Test 4: Comprehensive match betting analysis"""
    print_header("TEST 4: COMPREHENSIVE MATCH ANALYSIS")
    
    print("This is the main tool - comprehensive betting analysis for a specific match.")
    print("Combines team form, H2H history, and generates predictions with confidence scores")
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
    
    print(f"\nTesting match analysis for tomorrow ({tomorrow})...")
    print("Looking for Chelsea vs Arsenal (will show available matches if not found)")
    
    await test_tool("analyze_match_betting", {
        "home_team": "Chelsea",
        "away_team": "Arsenal",
        "league": "EPL",
        "match_date": tomorrow
    })
    
    input("\nPress Enter to continue...")

async def test_league_value_bets():
    """Test 5: League-wide value bet finder"""
    print_header("TEST 5: LEAGUE VALUE BETS")
    
    print("This tool finds potential value bets across all matches in a league.")
    print("Analyzes every match and returns only those meeting minimum confidence threshold")
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
    
    print(f"\nScanning EPL matches for {tomorrow} with 50% minimum confidence...")
    
    await test_tool("get_league_value_bets", {
        "league": "EPL",
        "date": tomorrow,
        "min_confidence": 50.0
    })
    
    input("\nPress Enter to continue...")

async def custom_test():
    """Custom tool test with user input"""
    print_header("CUSTOM TOOL TEST")
    
    print("Available tools:")
    print("1. get_betting_matches")
    print("2. analyze_match_betting") 
    print("3. get_team_form_analysis")
    print("4. get_h2h_betting_analysis")
    print("5. get_league_value_bets")
    
    tool_name = input("\nEnter tool name: ").strip()
    
    print("\nEnter arguments as JSON (or press Enter for empty):")
    args_input = input("Arguments: ").strip()
    
    try:
        arguments = json.loads(args_input) if args_input else {}
    except json.JSONDecodeError:
        print("[ERROR] Invalid JSON format")
        return
    
    await test_tool(tool_name, arguments)

async def run_interactive_tests():
    """Run interactive test menu"""
    print("Enhanced Soccer Betting Analyzer - Interactive MCP Tester")
    print("=" * 60)
    
    # Check server health first
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(HEALTH_URL)
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Connected to server: {data.get('server')}")
            print(f"[OK] Version: {data.get('version')}")
        else:
            print(f"[WARNING] Server health check failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Cannot reach server: {e}")
        return
    
    while True:
        print_header("INTERACTIVE TOOL TESTER")
        
        print("Choose a test to run:")
        print("1. Get Betting Matches (find matches for analysis)")
        print("2. Team Form Analysis (analyze team recent performance)")
        print("3. Head-to-Head Analysis (historical matchup data)")
        print("4. Match Betting Analysis (comprehensive match prediction)")
        print("5. League Value Bets (find value bets across league)")
        print("6. Custom Tool Test (enter your own parameters)")
        print("7. Run All Tests")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-7): ").strip()
        
        try:
            if choice == "0":
                print("\nGoodbye!")
                break
            elif choice == "1":
                await test_get_betting_matches()
            elif choice == "2":
                await test_team_form_analysis()
            elif choice == "3":
                await test_h2h_analysis()
            elif choice == "4":
                await test_analyze_match_betting()
            elif choice == "5":
                await test_league_value_bets()
            elif choice == "6":
                await custom_test()
            elif choice == "7":
                await test_get_betting_matches()
                await test_team_form_analysis()
                await test_h2h_analysis() 
                await test_analyze_match_betting()
                await test_league_value_bets()
                print_header("ALL TESTS COMPLETED")
            else:
                print("[ERROR] Invalid choice. Please enter 0-7.")
                
        except KeyboardInterrupt:
            print("\n\n[INFO] Test interrupted by user")
        except Exception as e:
            print(f"\n[ERROR] Test failed: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    print("Loading Interactive MCP Tester...")
    
    try:
        asyncio.run(run_interactive_tests())
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)