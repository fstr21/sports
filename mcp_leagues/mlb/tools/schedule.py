#!/usr/bin/env python3
"""
Test #1: MLB MCP - Get Schedule for Current Day
Tests the getMLBScheduleET tool specifically
Exports results to JSON file for analysis
"""

import httpx
import json
import asyncio
import os
from datetime import datetime
from typing import Dict, Any

class MLBScheduleTester:
    """Test MLB MCP schedule functionality"""
    
    def __init__(self):
        self.server_url = "https://mlbmcp-production.up.railway.app/mcp"
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
        
        print(f"[*] Calling MLB MCP: {tool_name}")
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
    
    async def test_todays_schedule(self):
        """Test getting today's MLB schedule"""
        print("=" * 50)
        print("TEST #1: MLB MCP - Today's Schedule")
        print("=" * 50)
        
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"\n[*] Testing date: {today}")
        
        # Test 1: Get today's schedule (no date argument - should default to today)
        print("\n--- Test 1A: Default (today) ---")
        result1 = await self.call_mcp_tool("getMLBScheduleET")
        
        if result1:
            self.analyze_schedule_result(result1, "Default (today)")
            self.results["tests"]["default_today"] = {
                "success": True,
                "method": "default (no date argument)",
                "raw_data": result1
            }
        else:
            self.results["tests"]["default_today"] = {"success": False, "error": "No data returned"}
        
        # Test 1B: Get today's schedule (explicit date)
        print("\n--- Test 1B: Explicit date ---")
        result2 = await self.call_mcp_tool("getMLBScheduleET", {"date": today})
        
        if result2:
            self.analyze_schedule_result(result2, f"Explicit date ({today})")
            self.results["tests"]["explicit_date"] = {
                "success": True,
                "method": f"explicit date ({today})",
                "date_requested": today,
                "raw_data": result2
            }
        else:
            self.results["tests"]["explicit_date"] = {"success": False, "error": "No data returned"}
        
        # Test 1C: Compare results
        print("\n--- Test 1C: Comparison ---")
        comparison_result = {"both_successful": False, "game_counts_match": False}
        
        if result1 and result2:
            data1 = result1.get("data", {})
            data2 = result2.get("data", {})
            
            games1 = data1.get("games", [])
            games2 = data2.get("games", [])
            
            comparison_result["both_successful"] = True
            comparison_result["default_game_count"] = len(games1)
            comparison_result["explicit_game_count"] = len(games2)
            
            if len(games1) == len(games2):
                print(f"[+] PASS: Both methods returned {len(games1)} games")
                comparison_result["game_counts_match"] = True
                comparison_result["status"] = "PASS"
            else:
                print(f"[!] WARN: Different game counts: {len(games1)} vs {len(games2)}")
                comparison_result["status"] = "WARN"
        else:
            comparison_result["status"] = "FAIL"
        
        self.results["tests"]["comparison"] = comparison_result
        
        print(f"\n{'=' * 50}")
        print("TEST #1 SUMMARY")
        print(f"{'=' * 50}")
        
        if result1:
            data = result1.get("data", {})
            game_count = data.get("count", 0)
            print(f"[+] Successfully retrieved {game_count} games for {today}")
            print(f"[+] MLB MCP getMLBScheduleET: WORKING")
            
            self.results["summary"] = {
                "status": "SUCCESS",
                "date_tested": today,
                "game_count": game_count,
                "total_tests": 3,
                "successful_tests": sum(1 for test in self.results["tests"].values() if test.get("success", False))
            }
        else:
            print(f"[-] Failed to retrieve games for {today}")
            print(f"[-] MLB MCP getMLBScheduleET: FAILED")
            
            self.results["summary"] = {
                "status": "FAILED",
                "date_tested": today,
                "game_count": 0,
                "total_tests": 3,
                "successful_tests": 0
            }
        
        # Export results to JSON
        await self.export_results()
    
    def analyze_schedule_result(self, result: Dict[str, Any], test_name: str):
        """Analyze and display schedule result"""
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
        
        # Extract key info
        source = data.get("source", "unknown")
        date_et = data.get("date_et", "unknown")
        count = data.get("count", 0)
        games = data.get("games", [])
        
        print(f"    Source: {source}")
        print(f"    Date (ET): {date_et}")
        print(f"    Game count: {count}")
        print(f"    Actual games: {len(games)}")
        
        # Show first few games
        if games:
            print(f"\n    First few games:")
            for i, game in enumerate(games[:3]):
                away_team = game.get("away", {}).get("name", "Unknown")
                home_team = game.get("home", {}).get("name", "Unknown")
                start_time = game.get("start_et", "Unknown")
                status = game.get("status", "Unknown")
                
                print(f"      {i+1}. {away_team} @ {home_team}")
                print(f"         Time: {start_time}")
                print(f"         Status: {status}")
        else:
            print(f"    [!] No games found")
        
        # Check meta field
        meta = result.get("meta")
        if meta:
            timestamp = meta.get("timestamp", "unknown")
            print(f"    Timestamp: {timestamp}")
    
    async def export_results(self):
        """Export test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mcp_leagues/mlb/tools/schedule_test_results_{timestamp}.json"
        
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
            for test_name, test_data in self.results["tests"].items():
                if test_data.get("success") and "raw_data" in test_data:
                    raw_data = test_data["raw_data"]
                    if isinstance(raw_data, dict) and "data" in raw_data:
                        schedule_data = raw_data["data"]
                        game_count = schedule_data.get("count", 0)
                        games_list = schedule_data.get("games", [])
                        actual_games = len(games_list)
                        
                        print(f"[+] {test_name}: {game_count} games reported, {actual_games} games in data")
                        
                        # Show sample game info
                        if games_list:
                            first_game = games_list[0]
                            away_team = first_game.get("away", {}).get("name", "Unknown")
                            home_team = first_game.get("home", {}).get("name", "Unknown")
                            print(f"    Sample game: {away_team} @ {home_team}")
            
            # Show comparison results
            comparison = self.results["tests"].get("comparison", {})
            if comparison.get("both_successful"):
                status = comparison.get("status", "UNKNOWN")
                print(f"[+] Comparison test: {status}")
                if comparison.get("game_counts_match"):
                    print(f"    Both methods returned identical results")
                else:
                    default_count = comparison.get("default_game_count", 0)
                    explicit_count = comparison.get("explicit_game_count", 0)
                    print(f"    Game count mismatch: default={default_count}, explicit={explicit_count}")
            
        except Exception as e:
            print(f"[!] Failed to export results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Run the test"""
    tester = MLBScheduleTester()
    
    try:
        await tester.test_todays_schedule()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())