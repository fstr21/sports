#!/usr/bin/env python3
"""
Test #2: NFL MCP - Teams Testing
Test NFL teams and divisions data
"""

import httpx
import json
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, Optional

class NFLTeamsTester:
    """Test NFL MCP teams functionality"""
    
    def __init__(self):
        self.server_url = "https://nflmcp-production.up.railway.app/mcp"
        self.client = httpx.AsyncClient(timeout=30.0)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "server_url": self.server_url,
            "tests": {},
            "teams_data": {},
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
    
    async def test_nfl_teams(self):
        """Test NFL teams functionality"""
        print("=" * 60)
        print("TEST #2: NFL MCP - Teams Testing")
        print("=" * 60)
        print("Target: All 32 NFL teams and divisions")
        
        # Test 2A: All teams
        print("\n--- Test 2A: All NFL Teams ---")
        await self.test_all_teams()
        
        # Test 2B: AFC teams
        print("\n--- Test 2B: AFC Conference ---")
        await self.test_afc_teams()
        
        # Test 2C: NFC teams
        print("\n--- Test 2C: NFC Conference ---")
        await self.test_nfc_teams()
        
        # Test 2D: Specific divisions
        print("\n--- Test 2D: Division Testing ---")
        await self.test_divisions()
        
        # Summary and export
        await self.generate_summary()
        await self.export_results()
    
    async def test_all_teams(self):
        """Test getting all NFL teams"""
        print("Testing All NFL Teams:")
        
        result = await self.call_mcp_tool("getNFLTeams")
        
        test_key = "all_teams"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "all teams",
                "raw_data": result
            }
            teams = self.analyze_teams_result(result, "All NFL Teams")
            
            if teams:
                self.results["teams_data"]["all_teams"] = teams
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    async def test_afc_teams(self):
        """Test AFC conference teams"""
        print("Testing AFC Conference Teams:")
        
        result = await self.call_mcp_tool("getNFLTeams", {
            "conference": "AFC"
        })
        
        test_key = "afc_teams"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "AFC conference filter",
                "raw_data": result
            }
            teams = self.analyze_teams_result(result, "AFC Teams")
            
            if teams:
                self.results["teams_data"]["afc_teams"] = teams
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    async def test_nfc_teams(self):
        """Test NFC conference teams"""
        print("Testing NFC Conference Teams:")
        
        result = await self.call_mcp_tool("getNFLTeams", {
            "conference": "NFC"
        })
        
        test_key = "nfc_teams"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "NFC conference filter",
                "raw_data": result
            }
            teams = self.analyze_teams_result(result, "NFC Teams")
            
            if teams:
                self.results["teams_data"]["nfc_teams"] = teams
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    async def test_divisions(self):
        """Test specific divisions"""
        divisions = ["AFC East", "AFC North", "AFC South", "AFC West", 
                    "NFC East", "NFC North", "NFC South", "NFC West"]
        
        for division in divisions:
            print(f"Testing {division}:")
            
            result = await self.call_mcp_tool("getNFLTeams", {
                "division": division
            })
            
            test_key = f"division_{division.lower().replace(' ', '_')}"
            if result:
                self.results["tests"][test_key] = {
                    "success": True,
                    "method": f"division filter: {division}",
                    "raw_data": result
                }
                teams = self.analyze_teams_result(result, division, show_details=False)
                
                if teams:
                    self.results["teams_data"][test_key] = teams
            else:
                self.results["tests"][test_key] = {
                    "success": False,
                    "error": "No data returned"
                }
    
    def analyze_teams_result(self, result: Dict[str, Any], test_name: str, show_details: bool = True) -> Optional[list]:
        """Analyze and display teams result"""
        print(f"\n[*] Analyzing: {test_name}")
        
        if not result.get("ok"):
            print(f"[!] ERROR: Result indicates failure")
            return None
        
        data = result.get("data", {})
        teams = data.get("teams", [])
        source = data.get("source", "unknown")
        
        print(f"    Source: {source}")
        print(f"    Teams found: {len(teams)}")
        
        if teams and show_details:
            print(f"    Team listing:")
            
            # Group by division for better display
            by_division = {}
            for team in teams:
                division = team.get("division", "Unknown")
                if division not in by_division:
                    by_division[division] = []
                by_division[division].append(team)
            
            for division, division_teams in sorted(by_division.items()):
                print(f"      {division}:")
                for team in sorted(division_teams, key=lambda x: x.get("team_abbr", "")):
                    abbr = team.get("team_abbr", "?")
                    name = team.get("team_name", "Unknown")
                    print(f"        {abbr}: {name}")
        elif teams:
            # Just show count for division tests
            team_names = [f"{t.get('team_abbr')} ({t.get('team_name')})" for t in teams]
            print(f"    Teams: {', '.join(team_names)}")
        
        return teams if teams else None
    
    async def generate_summary(self):
        """Generate test summary"""
        print(f"\n{'=' * 60}")
        print("TEST #2 SUMMARY - NFL Teams")
        print(f"{'=' * 60}")
        
        summary = {
            "status": "UNKNOWN",
            "total_tests": len(self.results["tests"]),
            "successful_tests": 0,
            "teams_info": {}
        }
        
        # Count successful tests
        for test_name, test_data in self.results["tests"].items():
            if test_data.get("success", False):
                summary["successful_tests"] += 1
        
        # Analyze teams data
        if "all_teams" in self.results["teams_data"]:
            all_teams = self.results["teams_data"]["all_teams"]
            summary["teams_info"]["total_teams"] = len(all_teams)
            
            # Count by conference
            afc_count = len([t for t in all_teams if t.get("conference") == "AFC"])
            nfc_count = len([t for t in all_teams if t.get("conference") == "NFC"])
            summary["teams_info"]["afc_teams"] = afc_count
            summary["teams_info"]["nfc_teams"] = nfc_count
            
            # Count divisions
            divisions = set([t.get("division") for t in all_teams if t.get("division")])
            summary["teams_info"]["total_divisions"] = len(divisions)
        
        # Check division tests
        division_tests = [k for k in self.results["tests"].keys() if k.startswith("division_")]
        successful_divisions = [k for k in division_tests if self.results["tests"][k].get("success")]
        summary["teams_info"]["divisions_working"] = len(successful_divisions)
        summary["teams_info"]["divisions_total"] = len(division_tests)
        
        # Overall status
        if summary["successful_tests"] >= summary["total_tests"] * 0.8:
            summary["status"] = "SUCCESS"
            print(f"[+] SUCCESS: NFL teams working")
        elif summary["successful_tests"] >= summary["total_tests"] * 0.5:
            summary["status"] = "PARTIAL"
            print(f"[!] PARTIAL: {summary['successful_tests']}/{summary['total_tests']} tests passed")
        else:
            summary["status"] = "FAILED"
            print(f"[-] FAILED: NFL teams not working")
        
        print(f"[+] Overall: {summary['successful_tests']}/{summary['total_tests']} tests passed")
        
        # Show key findings
        teams_info = summary["teams_info"]
        if "total_teams" in teams_info:
            print(f"[+] Total Teams: {teams_info['total_teams']}")
            print(f"[+] AFC: {teams_info.get('afc_teams', 0)}, NFC: {teams_info.get('nfc_teams', 0)}")
            print(f"[+] Divisions: {teams_info.get('divisions_working', 0)}/{teams_info.get('divisions_total', 0)} working")
        
        self.results["summary"] = summary
    
    async def export_results(self):
        """Export test results to JSON file"""
        output_dir = "C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\nfl\\tools"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"teams_test_results_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"\n[+] Results exported to: {filename}")
            
            summary = self.results.get("summary", {})
            status = summary.get("status", "UNKNOWN")
            print(f"[+] Test status: {status}")
            
        except Exception as e:
            print(f"[!] Failed to export results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Run the NFL teams test"""
    tester = NFLTeamsTester()
    
    print("NFL MCP - Teams Test")
    print("Testing NFL teams and divisions")
    print(f"Server: nflmcp-production.up.railway.app")
    
    try:
        await tester.test_nfl_teams()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())