#!/usr/bin/env python3
"""
Test #4: NFL MCP - Injuries Testing
Test NFL injury reports functionality
"""

import httpx
import json
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, Optional

class NFLInjuriesTester:
    """Test NFL MCP injuries functionality"""
    
    def __init__(self):
        self.server_url = "https://nflmcp-production.up.railway.app/mcp"
        self.client = httpx.AsyncClient(timeout=30.0)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "server_url": self.server_url,
            "tests": {},
            "injury_data": {},
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
    
    async def test_nfl_injuries(self):
        """Test NFL injuries functionality"""
        print("=" * 60)
        print("TEST #4: NFL MCP - Injuries Testing")
        print("=" * 60)
        print("Target: Current NFL injury reports")
        
        # Test 4A: All injuries
        print("\n--- Test 4A: All Current Injuries ---")
        await self.test_all_injuries()
        
        # Test 4B: Players Out
        print("\n--- Test 4B: Players Listed as Out ---")
        await self.test_out_players()
        
        # Test 4C: Questionable players
        print("\n--- Test 4C: Questionable Players ---")
        await self.test_questionable_players()
        
        # Test 4D: Team-specific injuries (Chiefs)
        print("\n--- Test 4D: Team-Specific Injuries (Chiefs) ---")
        await self.test_team_injuries()
        
        # Test 4E: Position-specific injuries (QB)
        print("\n--- Test 4E: Quarterback Injuries ---")
        await self.test_qb_injuries()
        
        # Summary and export
        await self.generate_summary()
        await self.export_results()
    
    async def test_all_injuries(self):
        """Test getting all injury reports"""
        print("Testing All Current Injuries:")
        
        result = await self.call_mcp_tool("getNFLInjuries", {
            "limit": 100
        })
        
        test_key = "all_injuries"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "all injuries",
                "raw_data": result
            }
            injuries = self.analyze_injuries_result(result, "All Injuries")
            
            if injuries:
                self.results["injury_data"]["all"] = injuries
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    async def test_out_players(self):
        """Test players listed as Out"""
        print("Testing Players Listed as Out:")
        
        result = await self.call_mcp_tool("getNFLInjuries", {
            "status": "Out",
            "limit": 50
        })
        
        test_key = "out_players"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "out status filter",
                "raw_data": result
            }
            injuries = self.analyze_injuries_result(result, "Out Players")
            
            if injuries:
                self.results["injury_data"]["out"] = injuries
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    async def test_questionable_players(self):
        """Test questionable players"""
        print("Testing Questionable Players:")
        
        result = await self.call_mcp_tool("getNFLInjuries", {
            "status": "Questionable",
            "limit": 50
        })
        
        test_key = "questionable_players"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "questionable status filter",
                "raw_data": result
            }
            injuries = self.analyze_injuries_result(result, "Questionable Players")
            
            if injuries:
                self.results["injury_data"]["questionable"] = injuries
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    async def test_team_injuries(self):
        """Test team-specific injuries"""
        print("Testing Chiefs Injuries:")
        
        result = await self.call_mcp_tool("getNFLInjuries", {
            "team": "KC",
            "limit": 20
        })
        
        test_key = "chiefs_injuries"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "team filter (KC)",
                "raw_data": result
            }
            injuries = self.analyze_injuries_result(result, "Chiefs Injuries")
            
            if injuries:
                self.results["injury_data"]["chiefs"] = injuries
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    async def test_qb_injuries(self):
        """Test quarterback injuries"""
        print("Testing Quarterback Injuries:")
        
        result = await self.call_mcp_tool("getNFLInjuries", {
            "position": "QB",
            "limit": 20
        })
        
        test_key = "qb_injuries"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "position filter (QB)",
                "raw_data": result
            }
            injuries = self.analyze_injuries_result(result, "QB Injuries")
            
            if injuries:
                self.results["injury_data"]["qb"] = injuries
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    def analyze_injuries_result(self, result: Dict[str, Any], test_name: str) -> Optional[list]:
        """Analyze and display injuries result"""
        print(f"\n[*] Analyzing: {test_name}")
        
        if not result.get("ok"):
            print(f"[!] ERROR: Result indicates failure")
            return None
        
        data = result.get("data", {})
        injuries = data.get("injuries", [])
        source = data.get("source", "unknown")
        
        print(f"    Source: {source}")
        print(f"    Injury reports found: {len(injuries)}")
        
        if injuries:
            print(f"    Sample injury reports:")
            
            # Group by status for better analysis
            by_status = {}
            for injury in injuries:
                status = injury.get("report_status", "Unknown")
                if status not in by_status:
                    by_status[status] = []
                by_status[status].append(injury)
            
            # Show breakdown by status
            for status, status_injuries in sorted(by_status.items()):
                print(f"      {status}: {len(status_injuries)} players")
            
            # Show sample injuries
            print(f"      Sample reports:")
            for i, injury in enumerate(injuries[:10]):  # Show first 10
                name = injury.get("player_name", "Unknown")
                team = injury.get("team", "?")
                position = injury.get("position", "?")
                status = injury.get("report_status", "?")
                injury_type = injury.get("primary_injury", "Unknown")
                
                print(f"        {i+1:2d}. {name:<20} ({team} {position}) - {status} ({injury_type})")
            
            if len(injuries) > 10:
                print(f"        ... and {len(injuries) - 10} more reports")
            
            return injuries
        
        print(f"    [!] No injury reports found")
        return None
    
    async def generate_summary(self):
        """Generate test summary"""
        print(f"\n{'=' * 60}")
        print("TEST #4 SUMMARY - NFL Injuries")
        print(f"{'=' * 60}")
        
        summary = {
            "status": "UNKNOWN",
            "total_tests": len(self.results["tests"]),
            "successful_tests": 0,
            "injury_info": {}
        }
        
        # Count successful tests
        for test_name, test_data in self.results["tests"].items():
            if test_data.get("success", False):
                summary["successful_tests"] += 1
        
        # Analyze injury data
        if "all" in self.results["injury_data"]:
            all_injuries = self.results["injury_data"]["all"]
            summary["injury_info"]["total_reports"] = len(all_injuries)
            
            # Count by status
            status_counts = {}
            for injury in all_injuries:
                status = injury.get("report_status", "Unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            summary["injury_info"]["by_status"] = status_counts
            
            # Count by position
            position_counts = {}
            for injury in all_injuries:
                position = injury.get("position", "Unknown")
                position_counts[position] = position_counts.get(position, 0) + 1
            
            # Top injured positions
            top_positions = sorted(position_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            summary["injury_info"]["top_injured_positions"] = top_positions
        
        # Check specific categories
        for category in ["out", "questionable", "chiefs", "qb"]:
            if category in self.results["injury_data"]:
                injuries = self.results["injury_data"][category]
                summary["injury_info"][f"{category}_count"] = len(injuries)
        
        # Overall status
        if summary["successful_tests"] >= 4:
            summary["status"] = "SUCCESS"
            print(f"[+] SUCCESS: NFL injuries working")
        elif summary["successful_tests"] >= 2:
            summary["status"] = "PARTIAL"
            print(f"[!] PARTIAL: {summary['successful_tests']}/{summary['total_tests']} tests passed")
        else:
            summary["status"] = "FAILED"
            print(f"[-] FAILED: NFL injuries not working")
        
        print(f"[+] Overall: {summary['successful_tests']}/{summary['total_tests']} tests passed")
        
        # Show key findings
        injury_info = summary["injury_info"]
        if "total_reports" in injury_info:
            print(f"[+] Total Reports: {injury_info['total_reports']}")
            
            # Show status breakdown
            if "by_status" in injury_info:
                status_counts = injury_info["by_status"]
                for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"    {status}: {count}")
            
            # Show category counts
            for category in ["out", "questionable", "chiefs", "qb"]:
                if f"{category}_count" in injury_info:
                    count = injury_info[f"{category}_count"]
                    print(f"[+] {category.title()}: {count} reports")
        
        self.results["summary"] = summary
    
    async def export_results(self):
        """Export test results to JSON file"""
        output_dir = "C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\nfl\\tools"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"injuries_test_results_{timestamp}.json"
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
    """Run the NFL injuries test"""
    tester = NFLInjuriesTester()
    
    print("NFL MCP - Injuries Test")
    print("Testing NFL injury reports")
    print(f"Server: nflmcp-production.up.railway.app")
    
    try:
        await tester.test_nfl_injuries()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())