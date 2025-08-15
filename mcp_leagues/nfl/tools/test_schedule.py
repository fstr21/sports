#!/usr/bin/env python3
"""
Test #1: NFL MCP - Schedule Testing
Test NFL schedule retrieval for 2025 season
"""

import httpx
import json
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, Optional

class NFLScheduleTester:
    """Test NFL MCP schedule functionality"""
    
    def __init__(self):
        # NFL MCP deployed on Railway
        self.server_url = "https://nflmcp-production.up.railway.app/mcp"
        self.client = httpx.AsyncClient(timeout=30.0)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "server_url": self.server_url,
            "tests": {},
            "schedule_data": {},
            "summary": {}
        }
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
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
        
        print(f"[*] Calling NFL MCP: {tool_name}")
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
    
    async def test_nfl_schedule(self):
        """Test NFL schedule functionality"""
        print("=" * 60)
        print("TEST #1: NFL MCP - Schedule Testing")
        print("=" * 60)
        print("Target: 2025 NFL Season Schedule")
        
        # Test 1A: Test mode first
        print("\n--- Test 1A: Test Mode (Mock Data) ---")
        await self.test_schedule_mock()
        
        # Test 1B: Week 1 games (Season opener)
        print("\n--- Test 1B: Week 1 Games (Season Opener) ---")
        await self.test_week1_games()
        
        # Test 1C: Full season schedule
        print("\n--- Test 1C: Full 2025 Season ---")
        await self.test_full_season()
        
        # Test 1D: Team-specific schedule (Chiefs)
        print("\n--- Test 1D: Team-Specific Schedule (Chiefs) ---")
        await self.test_team_schedule()
        
        # Test 1E: Playoff schedule
        print("\n--- Test 1E: Playoff Games ---")
        await self.test_playoff_schedule()
        
        # Summary and export
        await self.generate_summary()
        await self.export_results()
    
    async def test_schedule_mock(self):
        """Test schedule with mock data"""
        print("Testing NFL schedule - Mock Mode:")
        
        result = await self.call_mcp_tool("getNFLSchedule", {
            "season": 2025,
            "week": 1,
            "use_test_mode": True
        })
        
        test_key = "mock_schedule"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "test mode",
                "raw_data": result
            }
            self.analyze_schedule_result(result, "Mock Schedule")
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    async def test_week1_games(self):
        """Test Week 1 games (season opener)"""
        print("Testing Week 1 games - Season Opener:")
        
        result = await self.call_mcp_tool("getNFLSchedule", {
            "season": 2025,
            "week": 1
        })
        
        test_key = "week1_games"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "week 1 schedule",
                "raw_data": result
            }
            games = self.analyze_schedule_result(result, "Week 1 Games")
            
            # Store Week 1 data for analysis
            if games:
                self.results["schedule_data"]["week1"] = games
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    async def test_full_season(self):
        """Test full 2025 season schedule"""
        print("Testing Full 2025 Season:")
        
        result = await self.call_mcp_tool("getNFLSchedule", {
            "season": 2025
        })
        
        test_key = "full_season"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "full season schedule",
                "raw_data": result
            }
            games = self.analyze_schedule_result(result, "Full 2025 Season")
            
            # Store season data
            if games:
                self.results["schedule_data"]["full_season"] = {
                    "total_games": len(games),
                    "weeks": list(set([g.get("week") for g in games if g.get("week")])),
                    "teams": list(set([g.get("away_team") for g in games] + [g.get("home_team") for g in games]))
                }
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    async def test_team_schedule(self):
        """Test team-specific schedule (Chiefs)"""
        print("Testing Chiefs Schedule:")
        
        result = await self.call_mcp_tool("getNFLSchedule", {
            "season": 2025,
            "team": "KC"
        })
        
        test_key = "chiefs_schedule"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "team-specific schedule",
                "team": "KC",
                "raw_data": result
            }
            games = self.analyze_schedule_result(result, "Chiefs Schedule")
            
            # Store Chiefs data
            if games:
                self.results["schedule_data"]["chiefs"] = games
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    async def test_playoff_schedule(self):
        """Test playoff schedule"""
        print("Testing Playoff Schedule:")
        
        result = await self.call_mcp_tool("getNFLSchedule", {
            "season": 2025,
            "game_type": "POST"
        })
        
        test_key = "playoff_schedule"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "playoff schedule",
                "raw_data": result
            }
            games = self.analyze_schedule_result(result, "Playoff Schedule")
            
            if games:
                self.results["schedule_data"]["playoffs"] = games
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    def analyze_schedule_result(self, result: Dict[str, Any], test_name: str) -> Optional[list]:
        """Analyze and display schedule result"""
        print(f"\n[*] Analyzing: {test_name}")
        
        if not result.get("ok"):
            print(f"[!] ERROR: Result indicates failure")
            return None
        
        data = result.get("data", {})
        games = data.get("games", [])
        source = data.get("source", "unknown")
        
        print(f"    Source: {source}")
        print(f"    Games found: {len(games)}")
        
        if games:
            print(f"    Sample games:")
            for i, game in enumerate(games[:5]):  # Show first 5
                week = game.get("week", "?")
                date = game.get("date", "Unknown")
                away = game.get("away_team", "?")
                home = game.get("home_team", "?")
                
                print(f"      Week {week} - {date}: {away} @ {home}")
                
                # Show betting odds if available
                odds = game.get("betting_odds", {})
                if odds.get("away_moneyline") and odds.get("home_moneyline"):
                    away_ml = odds.get("away_moneyline")
                    home_ml = odds.get("home_moneyline")
                    spread = odds.get("spread_line", "N/A")
                    total = odds.get("total_line", "N/A")
                    print(f"        Odds: {away} {away_ml:+.0f}, {home} {home_ml:+.0f}, Spread: {spread}, Total: {total}")
            
            if len(games) > 5:
                print(f"      ... and {len(games) - 5} more games")
            
            return games
        
        print(f"    [!] No games found")
        return None
    
    async def generate_summary(self):
        """Generate test summary"""
        print(f"\n{'=' * 60}")
        print("TEST #1 SUMMARY - NFL Schedule")
        print(f"{'=' * 60}")
        
        summary = {
            "status": "UNKNOWN",
            "total_tests": len(self.results["tests"]),
            "successful_tests": 0,
            "schedule_info": {}
        }
        
        # Count successful tests
        for test_name, test_data in self.results["tests"].items():
            if test_data.get("success", False):
                summary["successful_tests"] += 1
        
        # Analyze schedule data
        if "week1" in self.results["schedule_data"]:
            week1_games = self.results["schedule_data"]["week1"]
            summary["schedule_info"]["week1_games"] = len(week1_games)
            
            # Find season opener
            if week1_games:
                opener = min(week1_games, key=lambda x: x.get("date", ""))
                summary["schedule_info"]["season_opener"] = {
                    "date": opener.get("date"),
                    "matchup": f"{opener.get('away_team')} @ {opener.get('home_team')}"
                }
        
        if "full_season" in self.results["schedule_data"]:
            season_data = self.results["schedule_data"]["full_season"]
            summary["schedule_info"]["total_games"] = season_data.get("total_games", 0)
            summary["schedule_info"]["total_weeks"] = len(season_data.get("weeks", []))
            summary["schedule_info"]["total_teams"] = len(season_data.get("teams", []))
        
        # Overall status
        if summary["successful_tests"] >= 4:
            summary["status"] = "SUCCESS"
            print(f"[+] SUCCESS: NFL schedule working")
        elif summary["successful_tests"] >= 2:
            summary["status"] = "PARTIAL"
            print(f"[!] PARTIAL: {summary['successful_tests']}/{summary['total_tests']} tests passed")
        else:
            summary["status"] = "FAILED"
            print(f"[-] FAILED: NFL schedule not working")
        
        print(f"[+] Overall: {summary['successful_tests']}/{summary['total_tests']} tests passed")
        
        # Show key findings
        if "season_opener" in summary["schedule_info"]:
            opener = summary["schedule_info"]["season_opener"]
            print(f"[+] Season Opener: {opener['matchup']} on {opener['date']}")
        
        if "total_games" in summary["schedule_info"]:
            total = summary["schedule_info"]["total_games"]
            weeks = summary["schedule_info"]["total_weeks"]
            teams = summary["schedule_info"]["total_teams"]
            print(f"[+] Full Season: {total} games, {weeks} weeks, {teams} teams")
        
        self.results["summary"] = summary
    
    async def export_results(self):
        """Export test results to JSON file"""
        output_dir = "C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\nfl\\tools"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"schedule_test_results_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"\n[+] Results exported to: {filename}")
            
            # Show file size
            file_size = os.path.getsize(filepath)
            if file_size > 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size} bytes"
            
            print(f"[+] File size: {size_str}")
            
            # Show key findings
            summary = self.results.get("summary", {})
            status = summary.get("status", "UNKNOWN")
            print(f"[+] Test status: {status}")
            
        except Exception as e:
            print(f"[!] Failed to export results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Run the NFL schedule test"""
    tester = NFLScheduleTester()
    
    print("NFL MCP - Schedule Test")
    print("Testing 2025 NFL season schedule")
    print(f"Server: nflmcp-production.up.railway.app")
    
    try:
        await tester.test_nfl_schedule()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())