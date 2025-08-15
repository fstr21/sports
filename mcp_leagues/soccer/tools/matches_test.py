#!/usr/bin/env python3
"""
Test #2: Soccer MCP - Get League Matches
Tests the getCompetitionMatches tool for EPL and La Liga fixtures
Exports results to JSON file for analysis
"""

import httpx
import json
import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class SoccerMatchesTester:
    """Test Soccer MCP matches functionality"""
    
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
            "match_data": {},
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
    
    async def test_league_matches(self):
        """Test getting matches for EPL and La Liga"""
        print("=" * 60)
        print("TEST #2: Soccer MCP - League Matches")
        print("=" * 60)
        print("Target: Current and upcoming fixtures for EPL and La Liga")
        
        # Test 2A: Test mode first
        print("\n--- Test 2A: Test Mode (Mock Data) ---")
        await self.test_matches_mock()
        
        # Test 2B: Live API - Current fixtures
        print("\n--- Test 2B: Live API - Current Fixtures ---")
        await self.test_current_fixtures()
        
        # Test 2C: Live API - This week's matches
        print("\n--- Test 2C: Live API - This Week's Matches ---")
        await self.test_weekly_fixtures()
        
        # Test 2D: Live API - Next matchday
        print("\n--- Test 2D: Live API - Specific Matchday ---")
        await self.test_matchday_fixtures()
        
        # Summary
        await self.generate_summary()
        
        # Export results
        await self.export_results()
    
    async def test_matches_mock(self):
        """Test matches with mock data"""
        for league_key, league_info in self.leagues.items():
            league_id = league_info["id"]
            league_name = league_info["name"]
            
            print(f"\nTesting {league_name} ({league_id}) - Mock Mode:")
            
            result = await self.call_mcp_tool("getCompetitionMatches", {
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
                self.analyze_matches_result(result, f"{league_name} (Mock)")
            else:
                self.results["tests"][test_key] = {
                    "success": False,
                    "league": league_name,
                    "error": "No data returned"
                }
    
    async def test_current_fixtures(self):
        """Test getting current/today's fixtures"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        for league_key, league_info in self.leagues.items():
            league_id = league_info["id"]
            league_name = league_info["name"]
            
            print(f"\nTesting {league_name} - Today's Fixtures ({today}):")
            
            result = await self.call_mcp_tool("getCompetitionMatches", {
                "competition_id": league_id,
                "date_from": today,
                "date_to": today
            })
            
            test_key = f"current_{league_key.lower()}"
            if result:
                self.results["tests"][test_key] = {
                    "success": True,
                    "league": league_name,
                    "method": f"current fixtures ({today})",
                    "date_range": {"from": today, "to": today},
                    "raw_data": result
                }
                matches = self.analyze_matches_result(result, f"{league_name} - Today")
                
                # Store match data for analysis
                if matches:
                    self.results["match_data"][f"today_{league_key.lower()}"] = matches
            else:
                self.results["tests"][test_key] = {
                    "success": False,
                    "league": league_name,
                    "error": "No data returned"
                }
    
    async def test_weekly_fixtures(self):
        """Test getting this week's fixtures"""
        today = datetime.now()
        week_end = today + timedelta(days=7)
        
        date_from = today.strftime("%Y-%m-%d")
        date_to = week_end.strftime("%Y-%m-%d")
        
        for league_key, league_info in self.leagues.items():
            league_id = league_info["id"]
            league_name = league_info["name"]
            
            print(f"\nTesting {league_name} - Next 7 Days ({date_from} to {date_to}):")
            
            result = await self.call_mcp_tool("getCompetitionMatches", {
                "competition_id": league_id,
                "date_from": date_from,
                "date_to": date_to
            })
            
            test_key = f"weekly_{league_key.lower()}"
            if result:
                self.results["tests"][test_key] = {
                    "success": True,
                    "league": league_name,
                    "method": f"weekly fixtures ({date_from} to {date_to})",
                    "date_range": {"from": date_from, "to": date_to},
                    "raw_data": result
                }
                matches = self.analyze_matches_result(result, f"{league_name} - Next 7 Days")
                
                # Store match data
                if matches:
                    self.results["match_data"][f"weekly_{league_key.lower()}"] = matches
            else:
                self.results["tests"][test_key] = {
                    "success": False,
                    "league": league_name,
                    "error": "No data returned"
                }
    
    async def test_matchday_fixtures(self):
        """Test getting specific matchday fixtures"""
        # Current typical matchday (adjust based on season)
        current_matchday = 10  # Adjust this based on current season progress
        
        for league_key, league_info in self.leagues.items():
            league_id = league_info["id"]
            league_name = league_info["name"]
            
            print(f"\nTesting {league_name} - Matchday {current_matchday}:")
            
            result = await self.call_mcp_tool("getCompetitionMatches", {
                "competition_id": league_id,
                "matchday": current_matchday
            })
            
            test_key = f"matchday_{league_key.lower()}"
            if result:
                self.results["tests"][test_key] = {
                    "success": True,
                    "league": league_name,
                    "method": f"matchday {current_matchday}",
                    "matchday": current_matchday,
                    "raw_data": result
                }
                matches = self.analyze_matches_result(result, f"{league_name} - Matchday {current_matchday}")
                
                # Store match data
                if matches:
                    self.results["match_data"][f"matchday_{league_key.lower()}"] = matches
            else:
                self.results["tests"][test_key] = {
                    "success": False,
                    "league": league_name,
                    "error": "No data returned"
                }
    
    def analyze_matches_result(self, result: Dict[str, Any], test_name: str) -> Optional[list]:
        """Analyze and display matches result"""
        print(f"\n[*] Analyzing: {test_name}")
        
        if not result.get("ok"):
            print(f"[!] ERROR: Result indicates failure")
            return None
        
        data = result.get("data", {})
        matches = data.get("matches", [])
        count = data.get("count", len(matches))
        source = data.get("source", "unknown")
        
        print(f"    Source: {source}")
        print(f"    Match count: {count}")
        print(f"    Actual matches: {len(matches)}")
        
        if matches:
            print(f"    Match details:")
            
            # Group matches by status
            by_status = {}
            for match in matches:
                status = match.get("status", "UNKNOWN")
                if status not in by_status:
                    by_status[status] = []
                by_status[status].append(match)
            
            # Show status summary
            for status, status_matches in by_status.items():
                print(f"      {status}: {len(status_matches)} matches")
            
            # Show first few matches in detail
            print(f"    First {min(3, len(matches))} matches:")
            for i, match in enumerate(matches[:3]):
                match_id = match.get("id", "Unknown")
                utc_date = match.get("utcDate", "Unknown")
                status = match.get("status", "Unknown")
                
                home_team = match.get("homeTeam", {})
                away_team = match.get("awayTeam", {})
                home_name = home_team.get("name", "Unknown")
                away_name = away_team.get("name", "Unknown")
                
                score = match.get("score", {})
                full_time = score.get("fullTime", {})
                home_score = full_time.get("home", "")
                away_score = full_time.get("away", "")
                
                print(f"      {i+1}. {away_name} vs {home_name}")
                print(f"         Date: {utc_date}")
                print(f"         Status: {status}")
                if home_score is not None and away_score is not None:
                    print(f"         Score: {home_score} - {away_score}")
                print(f"         Match ID: {match_id}")
            
            return matches
        else:
            print(f"    [!] No matches found")
            return None
    
    async def generate_summary(self):
        """Generate test summary"""
        print(f"\n{'=' * 60}")
        print("TEST #2 SUMMARY - League Matches")
        print(f"{'=' * 60}")
        
        summary = {
            "status": "UNKNOWN",
            "leagues_working": [],
            "leagues_failed": [],
            "total_tests": len(self.results["tests"]),
            "successful_tests": 0,
            "match_counts": {}
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
            total_matches_found = 0
            
            for test_key in league_tests:
                test_data = self.results["tests"].get(test_key, {})
                if test_data.get("success", False):
                    successful_league_tests += 1
                    
                    # Count matches from this test
                    raw_data = test_data.get("raw_data", {})
                    if raw_data and raw_data.get("ok"):
                        matches = raw_data.get("data", {}).get("matches", [])
                        total_matches_found += len(matches)
            
            if successful_league_tests > 0:
                summary["leagues_working"].append(league_name)
                summary["match_counts"][league_name] = total_matches_found
                print(f"[+] {league_name}: {successful_league_tests}/{len(league_tests)} tests passed, {total_matches_found} total matches found")
            else:
                summary["leagues_failed"].append(league_name)
                print(f"[-] {league_name}: All tests failed")
        
        # Overall status
        if len(summary["leagues_working"]) == len(self.leagues):
            summary["status"] = "SUCCESS"
            print(f"[+] SUCCESS: All leagues working")
        elif len(summary["leagues_working"]) > 0:
            summary["status"] = "PARTIAL"
            print(f"[!] PARTIAL: {len(summary['leagues_working'])}/{len(self.leagues)} leagues working")
        else:
            summary["status"] = "FAILED"
            print(f"[-] FAILED: No leagues working")
        
        print(f"[+] Overall: {summary['successful_tests']}/{summary['total_tests']} tests passed")
        
        self.results["summary"] = summary
    
    async def export_results(self):
        """Export test results to JSON file"""
        output_dir = "C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\soccer\\tools"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"matches_test_results_{timestamp}.json"
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
                
                # Show match counts
                match_counts = summary.get("match_counts", {})
                for league, count in match_counts.items():
                    print(f"    {league}: {count} matches found")
            
            failed_leagues = summary.get("leagues_failed", [])
            if failed_leagues:
                print(f"[!] Failed leagues: {', '.join(failed_leagues)}")
            
        except Exception as e:
            print(f"[!] Failed to export results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Run the matches test"""
    tester = SoccerMatchesTester()
    
    print("Soccer MCP - Matches Test")
    print("Testing EPL and La Liga fixtures")
    print("NOTE: Update server_url in script with your deployed Soccer MCP URL")
    
    try:
        await tester.test_league_matches()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())