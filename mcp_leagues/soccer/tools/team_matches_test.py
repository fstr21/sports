#!/usr/bin/env python3
"""
Test #4: Soccer MCP - Get Team-Specific Matches
Tests the getTeamMatches tool for specific teams in EPL and La Liga
Exports results to JSON file for analysis
"""

import httpx
import json
import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

class SoccerTeamMatchesTester:
    """Test Soccer MCP team matches functionality"""
    
    def __init__(self):
        # Update this URL when your Soccer MCP is deployed
        self.server_url = "https://your-soccer-mcp.up.railway.app/mcp"  # TODO: Update with actual URL
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Target teams (we'll try to find their IDs first)
        self.target_teams = {
            "EPL": [
                {"name": "Arsenal FC", "search_terms": ["arsenal"]},
                {"name": "Chelsea FC", "search_terms": ["chelsea"]},
                {"name": "Manchester City FC", "search_terms": ["manchester city", "man city"]},
                {"name": "Liverpool FC", "search_terms": ["liverpool"]}
            ],
            "La_Liga": [
                {"name": "Real Madrid CF", "search_terms": ["real madrid"]},
                {"name": "FC Barcelona", "search_terms": ["barcelona", "barça"]},
                {"name": "Atlético de Madrid", "search_terms": ["atletico madrid", "atlético"]},
                {"name": "Sevilla FC", "search_terms": ["sevilla"]}
            ]
        }
        
        self.leagues = {
            "EPL": {"id": "PL", "name": "Premier League"},
            "La_Liga": {"id": "PD", "name": "Primera División"}
        }
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "server_url": self.server_url,
            "target_teams": self.target_teams,
            "found_teams": {},
            "tests": {},
            "team_data": {},
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
    
    async def test_team_matches(self):
        """Test getting matches for specific teams"""
        print("=" * 60)
        print("TEST #4: Soccer MCP - Team-Specific Matches")
        print("=" * 60)
        print("Target: Fixtures for specific EPL and La Liga teams")
        
        # Step 1: Find team IDs
        print("\n--- Step 1: Find Team IDs ---")
        await self.find_team_ids()
        
        # Step 2: Test team matches with mock data
        print("\n--- Step 2: Test Mode (Mock Data) ---")
        await self.test_team_matches_mock()
        
        # Step 3: Test real team matches
        print("\n--- Step 3: Live API - Team Fixtures ---")
        await self.test_team_fixtures()
        
        # Step 4: Test recent team matches
        print("\n--- Step 4: Live API - Recent Matches ---")
        await self.test_recent_team_matches()
        
        # Summary
        await self.generate_summary()
        
        # Export results
        await self.export_results()
    
    async def find_team_ids(self):
        """Find team IDs by getting teams from each competition"""
        for league_key, league_info in self.leagues.items():
            league_id = league_info["id"]
            league_name = league_info["name"]
            
            print(f"\nFinding teams in {league_name}:")
            
            # Get teams for this competition
            result = await self.call_mcp_tool("getCompetitionTeams", {
                "competition_id": league_id
            })
            
            if result and result.get("ok"):
                data = result.get("data", {})
                teams = data.get("teams", [])
                
                print(f"    Found {len(teams)} teams in {league_name}")
                
                # Initialize found teams for this league
                self.results["found_teams"][league_key] = []
                
                # Look for our target teams
                target_teams = self.target_teams.get(league_key, [])
                for target_team in target_teams:
                    target_name = target_team["name"]
                    search_terms = target_team["search_terms"]
                    
                    found_team = self.find_team_in_list(teams, search_terms)
                    if found_team:
                        team_info = {
                            "target_name": target_name,
                            "found_name": found_team.get("name", "Unknown"),
                            "team_id": found_team.get("id"),
                            "short_name": found_team.get("shortName", ""),
                            "area": found_team.get("area", {}).get("name", "")
                        }
                        self.results["found_teams"][league_key].append(team_info)
                        print(f"    [+] Found: {team_info['found_name']} (ID: {team_info['team_id']})")
                    else:
                        print(f"    [-] Not found: {target_name}")
                
                print(f"    Total found: {len(self.results['found_teams'][league_key])}/{len(target_teams)}")
            else:
                print(f"    [!] Failed to get teams for {league_name}")
                self.results["found_teams"][league_key] = []
    
    def find_team_in_list(self, teams: List[Dict], search_terms: List[str]) -> Optional[Dict]:
        """Find a team in the teams list using search terms"""
        for team in teams:
            team_name = team.get("name", "").lower()
            short_name = team.get("shortName", "").lower()
            
            for term in search_terms:
                if term.lower() in team_name or term.lower() in short_name:
                    return team
        
        return None
    
    async def test_team_matches_mock(self):
        """Test team matches with mock data"""
        print("\nTesting team matches with mock data:")
        
        # Use a fake team ID for mock testing
        mock_team_id = 57  # Arsenal's typical ID
        
        result = await self.call_mcp_tool("getTeamMatches", {
            "team_id": mock_team_id,
            "use_test_mode": True
        })
        
        if result:
            self.results["tests"]["mock_team"] = {
                "success": True,
                "method": "test mode",
                "team_id": mock_team_id,
                "raw_data": result
            }
            self.analyze_team_matches_result(result, f"Mock Team (ID: {mock_team_id})")
        else:
            self.results["tests"]["mock_team"] = {
                "success": False,
                "error": "No data returned"
            }
    
    async def test_team_fixtures(self):
        """Test getting upcoming fixtures for found teams"""
        today = datetime.now()
        future_date = today + timedelta(days=30)
        
        date_from = today.strftime("%Y-%m-%d")
        date_to = future_date.strftime("%Y-%m-%d")
        
        for league_key, found_teams in self.results["found_teams"].items():
            if not found_teams:
                continue
            
            league_name = self.leagues[league_key]["name"]
            print(f"\nTesting upcoming fixtures for {league_name} teams:")
            
            # Test first 2 teams found (to save API calls)
            for i, team_info in enumerate(found_teams[:2]):
                team_name = team_info["found_name"]
                team_id = team_info["team_id"]
                
                print(f"  Testing {team_name} (ID: {team_id}):")
                
                result = await self.call_mcp_tool("getTeamMatches", {
                    "team_id": team_id,
                    "date_from": date_from,
                    "date_to": date_to,
                    "status": "SCHEDULED"
                })
                
                test_key = f"fixtures_{league_key.lower()}_{i}"
                if result:
                    self.results["tests"][test_key] = {
                        "success": True,
                        "league": league_name,
                        "team_name": team_name,
                        "team_id": team_id,
                        "method": f"upcoming fixtures ({date_from} to {date_to})",
                        "raw_data": result
                    }
                    matches = self.analyze_team_matches_result(result, f"{team_name} - Upcoming")
                    
                    if matches:
                        self.results["team_data"][f"fixtures_{team_name}"] = matches
                else:
                    self.results["tests"][test_key] = {
                        "success": False,
                        "team_name": team_name,
                        "error": "No data returned"
                    }
    
    async def test_recent_team_matches(self):
        """Test getting recent matches for found teams"""
        today = datetime.now()
        past_date = today - timedelta(days=30)
        
        date_from = past_date.strftime("%Y-%m-%d")
        date_to = today.strftime("%Y-%m-%d")
        
        for league_key, found_teams in self.results["found_teams"].items():
            if not found_teams:
                continue
            
            league_name = self.leagues[league_key]["name"]
            print(f"\nTesting recent matches for {league_name} teams:")
            
            # Test first 2 teams found
            for i, team_info in enumerate(found_teams[:2]):
                team_name = team_info["found_name"]
                team_id = team_info["team_id"]
                
                print(f"  Testing {team_name} recent matches:")
                
                result = await self.call_mcp_tool("getTeamMatches", {
                    "team_id": team_id,
                    "date_from": date_from,
                    "date_to": date_to,
                    "status": "FINISHED",
                    "limit": 5
                })
                
                test_key = f"recent_{league_key.lower()}_{i}"
                if result:
                    self.results["tests"][test_key] = {
                        "success": True,
                        "league": league_name,
                        "team_name": team_name,
                        "team_id": team_id,
                        "method": f"recent matches ({date_from} to {date_to})",
                        "raw_data": result
                    }
                    matches = self.analyze_team_matches_result(result, f"{team_name} - Recent")
                    
                    if matches:
                        self.results["team_data"][f"recent_{team_name}"] = matches
                else:
                    self.results["tests"][test_key] = {
                        "success": False,
                        "team_name": team_name,
                        "error": "No data returned"
                    }
    
    def analyze_team_matches_result(self, result: Dict[str, Any], test_name: str) -> Optional[List]:
        """Analyze and display team matches result"""
        print(f"\n    [*] Analyzing: {test_name}")
        
        if not result.get("ok"):
            print(f"    [!] ERROR: Result indicates failure")
            return None
        
        data = result.get("data", {})
        matches = data.get("matches", [])
        count = data.get("count", len(matches))
        team_id = data.get("team_id", "unknown")
        source = data.get("source", "unknown")
        
        print(f"        Source: {source}")
        print(f"        Team ID: {team_id}")
        print(f"        Match count: {count}")
        print(f"        Actual matches: {len(matches)}")
        
        if matches:
            # Group by venue
            home_matches = [m for m in matches if m.get("homeTeam", {}).get("id") == team_id]
            away_matches = [m for m in matches if m.get("awayTeam", {}).get("id") == team_id]
            
            print(f"        Home matches: {len(home_matches)}")
            print(f"        Away matches: {len(away_matches)}")
            
            # Show first few matches
            print(f"        Match details:")
            for i, match in enumerate(matches[:3]):
                utc_date = match.get("utcDate", "Unknown")
                status = match.get("status", "Unknown")
                
                home_team = match.get("homeTeam", {})
                away_team = match.get("awayTeam", {})
                home_name = home_team.get("shortName", home_team.get("name", "Unknown"))
                away_name = away_team.get("shortName", away_team.get("name", "Unknown"))
                
                # Highlight our target team
                if home_team.get("id") == team_id:
                    home_name = f"**{home_name}**"
                elif away_team.get("id") == team_id:
                    away_name = f"**{away_name}**"
                
                score = match.get("score", {})
                full_time = score.get("fullTime", {})
                home_score = full_time.get("home", "")
                away_score = full_time.get("away", "")
                
                print(f"          {i+1}. {away_name} vs {home_name}")
                print(f"             Date: {utc_date[:10]}")  # Just the date part
                print(f"             Status: {status}")
                if home_score is not None and away_score is not None:
                    print(f"             Score: {away_score} - {home_score}")
            
            if len(matches) > 3:
                print(f"        ... and {len(matches) - 3} more matches")
            
            return matches
        else:
            print(f"        [!] No matches found")
            return None
    
    async def generate_summary(self):
        """Generate test summary"""
        print(f"\n{'=' * 60}")
        print("TEST #4 SUMMARY - Team Matches")
        print(f"{'=' * 60}")
        
        summary = {
            "status": "UNKNOWN",
            "teams_found": 0,
            "teams_tested": 0,
            "successful_tests": 0,
            "total_tests": len(self.results["tests"]),
            "leagues_summary": {}
        }
        
        # Count teams found
        for league_key, found_teams in self.results["found_teams"].items():
            league_name = self.leagues[league_key]["name"]
            target_count = len(self.target_teams.get(league_key, []))
            found_count = len(found_teams)
            
            summary["teams_found"] += found_count
            summary["leagues_summary"][league_name] = {
                "target_teams": target_count,
                "found_teams": found_count,
                "found_names": [t["found_name"] for t in found_teams]
            }
            
            print(f"[+] {league_name}: Found {found_count}/{target_count} target teams")
            for team_info in found_teams:
                print(f"    - {team_info['found_name']} (ID: {team_info['team_id']})")
        
        # Count successful tests
        successful_tests = 0
        teams_tested = 0
        
        for test_name, test_data in self.results["tests"].items():
            if test_data.get("success", False):
                successful_tests += 1
                if "team_name" in test_data:
                    teams_tested += 1
        
        summary["successful_tests"] = successful_tests
        summary["teams_tested"] = teams_tested
        
        # Overall status
        if summary["teams_found"] > 0 and summary["successful_tests"] > 0:
            if summary["teams_found"] >= 4:  # Found most target teams
                summary["status"] = "SUCCESS"
                print(f"[+] SUCCESS: Found {summary['teams_found']} teams, {summary['successful_tests']} tests passed")
            else:
                summary["status"] = "PARTIAL"
                print(f"[!] PARTIAL: Found {summary['teams_found']} teams, {summary['successful_tests']} tests passed")
        else:
            summary["status"] = "FAILED"
            print(f"[-] FAILED: Limited team data or test failures")
        
        print(f"[+] Team matches tool: {'WORKING' if successful_tests > 0 else 'NEEDS WORK'}")
        
        self.results["summary"] = summary
    
    async def export_results(self):
        """Export test results to JSON file"""
        output_dir = "C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\soccer\\tools"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"team_matches_test_results_{timestamp}.json"
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
            teams_found = summary.get("teams_found", 0)
            successful_tests = summary.get("successful_tests", 0)
            
            print(f"[+] Test status: {status}")
            print(f"[+] Teams found: {teams_found}")
            print(f"[+] Successful tests: {successful_tests}")
            
            # Show found teams summary
            leagues_summary = summary.get("leagues_summary", {})
            for league, info in leagues_summary.items():
                found_names = info.get("found_names", [])
                if found_names:
                    print(f"[+] {league} teams: {', '.join(found_names[:2])}{'...' if len(found_names) > 2 else ''}")
            
        except Exception as e:
            print(f"[!] Failed to export results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Run the team matches test"""
    tester = SoccerTeamMatchesTester()
    
    print("Soccer MCP - Team Matches Test")
    print("Testing fixtures for specific EPL and La Liga teams")
    print("NOTE: Update server_url in script with your deployed Soccer MCP URL")
    
    try:
        await tester.test_team_matches()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())