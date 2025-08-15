#!/usr/bin/env python3
"""
Test #2: Odds MCP - Game-Level Odds
Tests getting moneylines, spreads, and totals for MLB games
Exports results to JSON file for analysis
"""

import httpx
import json
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, List

class OddsGameLevelTester:
    """Test Odds MCP game-level odds functionality"""
    
    def __init__(self):
        self.server_url = "https://odds-mcp-v2-production.up.railway.app/mcp"
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "server_url": self.server_url,
            "tests": {}
        }
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call an MCP tool"""
        if arguments is None:
            arguments = {}
            
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        print(f"[*] Calling Odds MCP: {tool_name}")
        if arguments:
            print(f"    Arguments: {arguments}")
        
        try:
            response = await self.client.post(self.server_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                print(f"[!] MCP Error: {result['error']}")
                return None
            
            return result.get("result", {})
            
        except Exception as e:
            print(f"[!] Request failed: {e}")
            return None
    
    async def test_game_level_odds(self):
        """Test getting game-level odds for MLB"""
        print("=" * 50)
        print("TEST #2: Odds MCP - Game-Level Odds")
        print("=" * 50)
        
        # Test 2A: Get basic moneylines
        print("\n--- Test 2A: Moneylines (h2h) ---")
        result_h2h = await self.call_mcp_tool("getOdds", {
            "sport": "baseball_mlb",
            "markets": "h2h",
            "regions": "us"
        })
        
        if result_h2h:
            self.analyze_odds_result(result_h2h, "Moneylines", ["h2h"])
            self.results["tests"]["moneylines"] = {
                "success": True,
                "markets_requested": ["h2h"],
                "raw_data": result_h2h
            }
        else:
            self.results["tests"]["moneylines"] = {"success": False, "error": "No data returned"}
        
        # Test 2B: Get spreads (run lines)
        print("\n--- Test 2B: Spreads (Run Lines) ---")
        result_spreads = await self.call_mcp_tool("getOdds", {
            "sport": "baseball_mlb",
            "markets": "spreads",
            "regions": "us"
        })
        
        if result_spreads:
            self.analyze_odds_result(result_spreads, "Spreads", ["spreads"])
            self.results["tests"]["spreads"] = {
                "success": True,
                "markets_requested": ["spreads"],
                "raw_data": result_spreads
            }
        else:
            self.results["tests"]["spreads"] = {"success": False, "error": "No data returned"}
        
        # Test 2C: Get totals (over/under)
        print("\n--- Test 2C: Totals (Over/Under) ---")
        result_totals = await self.call_mcp_tool("getOdds", {
            "sport": "baseball_mlb",
            "markets": "totals",
            "regions": "us"
        })
        
        if result_totals:
            self.analyze_odds_result(result_totals, "Totals", ["totals"])
            self.results["tests"]["totals"] = {
                "success": True,
                "markets_requested": ["totals"],
                "raw_data": result_totals
            }
        else:
            self.results["tests"]["totals"] = {"success": False, "error": "No data returned"}
        
        # Test 2D: Get all markets combined
        print("\n--- Test 2D: All Markets Combined ---")
        result_all = await self.call_mcp_tool("getOdds", {
            "sport": "baseball_mlb",
            "markets": "h2h,spreads,totals",
            "regions": "us"
        })
        
        if result_all:
            self.analyze_odds_result(result_all, "All Markets", ["h2h", "spreads", "totals"])
            self.results["tests"]["all_markets"] = {
                "success": True,
                "markets_requested": ["h2h", "spreads", "totals"],
                "raw_data": result_all
            }
        else:
            self.results["tests"]["all_markets"] = {"success": False, "error": "No data returned"}
        
        # Summary
        print(f"\n{'=' * 50}")
        print("TEST #2 SUMMARY")
        print(f"{'=' * 50}")
        
        working_tests = []
        if result_h2h:
            working_tests.append("Moneylines")
        if result_spreads:
            working_tests.append("Spreads")
        if result_totals:
            working_tests.append("Totals")
        if result_all:
            working_tests.append("Combined")
        
        if working_tests:
            print(f"[+] Working markets: {', '.join(working_tests)}")
            print(f"[+] Odds MCP getOdds: WORKING")
            self.results["summary"] = {
                "status": "SUCCESS",
                "working_markets": working_tests,
                "total_tests": 4,
                "successful_tests": len(working_tests)
            }
        else:
            print(f"[-] No markets working")
            print(f"[-] Odds MCP getOdds: FAILED")
            self.results["summary"] = {
                "status": "FAILED",
                "working_markets": [],
                "total_tests": 4,
                "successful_tests": 0
            }
        
        # Export results to JSON
        await self.export_results()
    
    def analyze_odds_result(self, result: Dict[str, Any], test_name: str, expected_markets: List[str]):
        """Analyze and display odds result"""
        print(f"\n[*] Analyzing: {test_name}")
        
        # Check result structure
        if not isinstance(result, dict):
            print(f"[!] ERROR: Result is not a dict: {type(result)}")
            return
        
        print(f"    Result keys: {list(result.keys())}")
        
        # Check data field
        data = result.get("data")
        if not data:
            print(f"[!] ERROR: No 'data' field in result")
            return
        
        print(f"    Data keys: {list(data.keys())}")
        
        # Extract odds data
        odds_data = None
        if isinstance(data, dict) and "odds" in data:
            odds_data = data["odds"]
        elif isinstance(data, list):
            odds_data = data
        else:
            odds_data = data
        
        if not odds_data:
            print(f"[!] ERROR: No odds data found")
            return
        
        if not isinstance(odds_data, list):
            print(f"[!] ERROR: Odds data is not a list: {type(odds_data)}")
            return
        
        print(f"    Games found: {len(odds_data)}")
        
        # Analyze first few games
        for i, game in enumerate(odds_data[:2]):  # Show first 2 games
            self.analyze_single_game(game, i+1, expected_markets)
    
    def analyze_single_game(self, game: Dict[str, Any], game_num: int, expected_markets: List[str]):
        """Analyze a single game's odds"""
        home_team = game.get("home_team", "Unknown")
        away_team = game.get("away_team", "Unknown")
        commence_time = game.get("commence_time", "Unknown")
        
        print(f"\n    Game {game_num}: {away_team} @ {home_team}")
        print(f"    Time: {commence_time}")
        
        bookmakers = game.get("bookmakers", [])
        if not bookmakers:
            print(f"    [!] No bookmakers found")
            return
        
        # Show first bookmaker
        bookie = bookmakers[0]
        bookie_name = bookie.get("title", "Unknown")
        print(f"    Bookmaker: {bookie_name}")
        
        markets = bookie.get("markets", [])
        found_markets = [market.get("key") for market in markets]
        
        print(f"    Markets available: {found_markets}")
        
        # Check if we got expected markets
        for expected in expected_markets:
            if expected in found_markets:
                print(f"    [+] {expected}: FOUND")
            else:
                print(f"    [-] {expected}: MISSING")
        
        # Show sample odds for each market
        for market in markets:
            market_key = market.get("key", "unknown")
            outcomes = market.get("outcomes", [])
            
            print(f"      {market_key}:")
            for outcome in outcomes[:2]:  # Show first 2 outcomes
                name = outcome.get("name", "Unknown")
                price = outcome.get("price", "N/A")
                point = outcome.get("point", "")
                
                if point:
                    print(f"        {name} {point:+g}: {price}")
                else:
                    print(f"        {name}: {price}")
    
    async def export_results(self):
        """Export test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mcp_leagues/mlb/tools/game_level_odds_results_{timestamp}.json"
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"\n[+] Results exported to: {filename}")
            
            # Show file size
            file_size = os.path.getsize(filename)
            if file_size > 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size} bytes"
            
            print(f"[+] File size: {size_str}")
            
            # Show summary of what was saved
            total_games = 0
            for test_name, test_data in self.results["tests"].items():
                if test_data.get("success") and "raw_data" in test_data:
                    raw_data = test_data["raw_data"]
                    if isinstance(raw_data, dict) and "data" in raw_data:
                        odds_data = raw_data["data"].get("odds", [])
                        if isinstance(odds_data, list):
                            game_count = len(odds_data)
                            total_games = max(total_games, game_count)
                            print(f"[+] {test_name}: {game_count} games")
            
            if total_games > 0:
                print(f"[+] Total unique games found: {total_games}")
            
        except Exception as e:
            print(f"[!] Failed to export results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Run the test"""
    tester = OddsGameLevelTester()
    
    try:
        await tester.test_game_level_odds()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())