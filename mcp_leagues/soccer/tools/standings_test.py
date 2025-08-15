#!/usr/bin/env python3
"""
Test #3: Soccer MCP - Get League Standings/Tables
Tests the getCompetitionStandings tool for EPL and La Liga tables
Exports results to JSON file for analysis
"""

import httpx
import json
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, Optional

class SoccerStandingsTester:
    """Test Soccer MCP standings functionality"""
    
    def __init__(self):
        # Update this URL when your Soccer MCP is deployed
        self.server_url = "https://your-soccer-mcp.up.railway.app/mcp"  # TODO: Update with actual URL
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Target leagues
        self.leagues = {
            "EPL": {"id": "PL", "name": "Premier League"},
            "La_Liga": {"id": "PD", "name": "Primera División"}
        }
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "server_url": self.server_url,
            "leagues_tested": self.leagues,
            "tests": {},
            "standings_data": {},
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
        
        print(f"[*] Calling Soccer MCP: {tool_name}")
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
    
    async def test_league_standings(self):
        """Test getting standings for EPL and La Liga"""
        print("=" * 60)
        print("TEST #3: Soccer MCP - League Standings/Tables")
        print("=" * 60)
        print("Target: Current league tables for EPL and La Liga")
        
        # Test 3A: Test mode first
        print("\n--- Test 3A: Test Mode (Mock Data) ---")
        await self.test_standings_mock()
        
        # Test 3B: Live API - Current season standings
        print("\n--- Test 3B: Live API - Current Season ---")
        await self.test_current_standings()
        
        # Test 3C: Live API - Specific season (if different)
        print("\n--- Test 3C: Live API - Specific Season ---")
        await self.test_specific_season_standings()
        
        # Test 3D: Live API - Specific matchday (if available)
        print("\n--- Test 3D: Live API - Specific Matchday ---")
        await self.test_matchday_standings()
        
        # Summary
        await self.generate_summary()
        
        # Export results
        await self.export_results()
    
    async def test_standings_mock(self):
        """Test standings with mock data"""
        for league_key, league_info in self.leagues.items():
            league_id = league_info["id"]
            league_name = league_info["name"]
            
            print(f"\nTesting {league_name} ({league_id}) - Mock Mode:")
            
            result = await self.call_mcp_tool("getCompetitionStandings", {
                "competition_id": league_id,
                "use_test_mode": True
            })
            
            test_key = f"mock_{league_key.lower()}"
            if result:
                self.results["tests"][test_key] = {
                    "success": True,
                    "league": league_name,
                    "method": "test mode",
                    "raw_data": result
                }
                self.analyze_standings_result(result, f"{league_name} (Mock)")
            else:
                self.results["tests"][test_key] = {
                    "success": False,
                    "league": league_name,
                    "error": "No data returned"
                }
    
    async def test_current_standings(self):
        """Test getting current season standings"""
        for league_key, league_info in self.leagues.items():
            league_id = league_info["id"]
            league_name = league_info["name"]
            
            print(f"\nTesting {league_name} - Current Season Standings:")
            
            result = await self.call_mcp_tool("getCompetitionStandings", {
                "competition_id": league_id
            })
            
            test_key = f"current_{league_key.lower()}"
            if result:
                self.results["tests"][test_key] = {
                    "success": True,
                    "league": league_name,
                    "method": "current season standings",
                    "raw_data": result
                }
                standings = self.analyze_standings_result(result, f"{league_name} - Current")
                
                # Store standings data for analysis
                if standings:
                    self.results["standings_data"][f"current_{league_key.lower()}"] = standings
            else:
                self.results["tests"][test_key] = {
                    "success": False,
                    "league": league_name,
                    "error": "No data returned"
                }
    
    async def test_specific_season_standings(self):
        """Test getting specific season standings"""
        current_year = datetime.now().year
        target_season = current_year  # or current_year - 1 for last season
        
        for league_key, league_info in self.leagues.items():
            league_id = league_info["id"]
            league_name = league_info["name"]
            
            print(f"\nTesting {league_name} - {target_season} Season:")
            
            result = await self.call_mcp_tool("getCompetitionStandings", {
                "competition_id": league_id,
                "season": target_season
            })
            
            test_key = f"season_{league_key.lower()}"
            if result:
                self.results["tests"][test_key] = {
                    "success": True,
                    "league": league_name,
                    "method": f"{target_season} season standings",
                    "season": target_season,
                    "raw_data": result
                }
                standings = self.analyze_standings_result(result, f"{league_name} - {target_season}")
                
                # Store standings data
                if standings:
                    self.results["standings_data"][f"season_{league_key.lower()}"] = standings
            else:
                self.results["tests"][test_key] = {
                    "success": False,
                    "league": league_name,
                    "error": "No data returned"
                }
    
    async def test_matchday_standings(self):
        """Test getting standings as of specific matchday"""
        current_matchday = 10  # Adjust based on current season progress
        
        for league_key, league_info in self.leagues.items():
            league_id = league_info["id"]
            league_name = league_info["name"]
            
            print(f"\nTesting {league_name} - After Matchday {current_matchday}:")
            
            result = await self.call_mcp_tool("getCompetitionStandings", {
                "competition_id": league_id,
                "matchday": current_matchday
            })
            
            test_key = f"matchday_{league_key.lower()}"
            if result:
                self.results["tests"][test_key] = {
                    "success": True,
                    "league": league_name,
                    "method": f"standings after matchday {current_matchday}",
                    "matchday": current_matchday,
                    "raw_data": result
                }
                standings = self.analyze_standings_result(result, f"{league_name} - Matchday {current_matchday}")
                
                # Store standings data
                if standings:
                    self.results["standings_data"][f"matchday_{league_key.lower()}"] = standings
            else:
                self.results["tests"][test_key] = {
                    "success": False,
                    "league": league_name,
                    "error": "No data returned"
                }
    
    def analyze_standings_result(self, result: Dict[str, Any], test_name: str) -> Optional[dict]:
        """Analyze and display standings result"""
        print(f"\n[*] Analyzing: {test_name}")
        
        if not result.get("ok"):
            print(f"[!] ERROR: Result indicates failure")
            return None
        
        data = result.get("data", {})
        standings_info = data.get("standings", {})
        source = data.get("source", "unknown")
        
        print(f"    Source: {source}")
        
        # Handle standings structure
        if isinstance(standings_info, dict):
            season = standings_info.get("season", {})
            standings_list = standings_info.get("standings", [])
            
            print(f"    Season info: {season}")
            print(f"    Standings groups: {len(standings_list)}")
            
            # Process each standings group (usually just one for league tables)
            for i, standing_group in enumerate(standings_list):
                stage = standing_group.get("stage", "Unknown")
                table_type = standing_group.get("type", "Unknown")
                table = standing_group.get("table", [])
                
                print(f"    Group {i+1}: {stage} - {table_type}")
                print(f"    Teams in table: {len(table)}")
                
                if table:
                    print(f"    League table (Top 10):")
                    print(f"    {'Pos':<3} {'Team':<25} {'P':<3} {'W':<3} {'D':<3} {'L':<3} {'GF':<3} {'GA':<3} {'GD':<4} {'Pts':<3}")
                    print(f"    {'-'*3} {'-'*25} {'-'*3} {'-'*3} {'-'*3} {'-'*3} {'-'*3} {'-'*3} {'-'*4} {'-'*3}")
                    
                    for team_data in table[:10]:  # Show top 10
                        pos = team_data.get("position", 0)
                        team = team_data.get("team", {})
                        team_name = team.get("name", "Unknown")[:25]  # Truncate long names
                        
                        played = team_data.get("playedGames", 0)
                        won = team_data.get("won", 0)
                        draw = team_data.get("draw", 0)
                        lost = team_data.get("lost", 0)
                        goals_for = team_data.get("goalsFor", 0)
                        goals_against = team_data.get("goalsAgainst", 0)
                        goal_diff = team_data.get("goalDifference", 0)
                        points = team_data.get("points", 0)
                        
                        print(f"    {pos:<3} {team_name:<25} {played:<3} {won:<3} {draw:<3} {lost:<3} {goals_for:<3} {goals_against:<3} {goal_diff:<+4} {points:<3}")
                    
                    if len(table) > 10:
                        print(f"    ... and {len(table) - 10} more teams")
                    
                    # Highlight top and bottom teams
                    if len(table) >= 3:
                        top_team = table[0]["team"]["name"]
                        bottom_team = table[-1]["team"]["name"]
                        print(f"    Leaders: {top_team} ({table[0]['points']} pts)")
                        print(f"    Bottom: {bottom_team} ({table[-1]['points']} pts)")
                    
                    return {"season": season, "table": table, "stage": stage, "type": table_type}
        
        print(f"    [!] No valid standings data found")
        return None
    
    async def generate_summary(self):
        """Generate test summary"""
        print(f"\n{'=' * 60}")
        print("TEST #3 SUMMARY - League Standings")
        print(f"{'=' * 60}")
        
        summary = {
            "status": "UNKNOWN",
            "leagues_working": [],
            "leagues_failed": [],
            "total_tests": len(self.results["tests"]),
            "successful_tests": 0,
            "table_info": {}
        }
        
        # Count successful tests
        for test_name, test_data in self.results["tests"].items():
            if test_data.get("success", False):
                summary["successful_tests"] += 1
        
        # Analyze by league
        for league_key, league_info in self.leagues.items():
            league_name = league_info["name"]
            league_tests = [t for t in self.results["tests"].keys() if league_key.lower() in t]
            
            successful_league_tests = 0
            teams_found = 0
            
            for test_key in league_tests:
                test_data = self.results["tests"].get(test_key, {})
                if test_data.get("success", False):
                    successful_league_tests += 1
                    
                    # Get table info from this test
                    standings_data = self.results["standings_data"].get(test_key.replace("current_", "").replace("season_", "").replace("matchday_", ""))
                    if standings_data and "table" in standings_data:
                        teams_found = max(teams_found, len(standings_data["table"]))
            
            if successful_league_tests > 0:
                summary["leagues_working"].append(league_name)
                summary["table_info"][league_name] = {"teams": teams_found}
                print(f"[+] {league_name}: {successful_league_tests}/{len(league_tests)} tests passed, {teams_found} teams in table")
                
                # Show current leader if available
                current_data = self.results["standings_data"].get(f"current_{league_key.lower()}")
                if current_data and current_data.get("table"):
                    leader = current_data["table"][0]
                    leader_name = leader["team"]["name"]
                    leader_points = leader["points"]
                    print(f"    Current leader: {leader_name} ({leader_points} pts)")
            else:
                summary["leagues_failed"].append(league_name)
                print(f"[-] {league_name}: All tests failed")
        
        # Overall status
        if len(summary["leagues_working"]) == len(self.leagues):
            summary["status"] = "SUCCESS"
            print(f"[+] SUCCESS: All league standings working")
        elif len(summary["leagues_working"]) > 0:
            summary["status"] = "PARTIAL"
            print(f"[!] PARTIAL: {len(summary['leagues_working'])}/{len(self.leagues)} leagues working")
        else:
            summary["status"] = "FAILED"
            print(f"[-] FAILED: No league standings working")
        
        print(f"[+] Overall: {summary['successful_tests']}/{summary['total_tests']} tests passed")
        
        self.results["summary"] = summary
    
    async def export_results(self):
        """Export test results to JSON file"""
        output_dir = "C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\soccer\\tools"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"standings_test_results_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"\n[+] Results exported to: {filepath}")
            
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
            
            working_leagues = summary.get("leagues_working", [])
            if working_leagues:
                print(f"[+] Working leagues: {', '.join(working_leagues)}")
                
                # Show table info
                table_info = summary.get("table_info", {})
                for league, info in table_info.items():
                    teams = info.get("teams", 0)
                    print(f"    {league}: {teams} teams in table")
            
            failed_leagues = summary.get("leagues_failed", [])
            if failed_leagues:
                print(f"[!] Failed leagues: {', '.join(failed_leagues)}")
            
        except Exception as e:
            print(f"[!] Failed to export results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Run the standings test"""
    tester = SoccerStandingsTester()
    
    print("Soccer MCP - Standings Test")
    print("Testing EPL and La Liga league tables")
    print("NOTE: Update server_url in script with your deployed Soccer MCP URL")
    
    try:
        await tester.test_league_standings()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())