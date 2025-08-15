#!/usr/bin/env python3
"""
Test #3: NFL MCP - Player Stats Testing
Test NFL player statistics functionality
"""

import httpx
import json
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, Optional

class NFLPlayerStatsTester:
    """Test NFL MCP player stats functionality"""
    
    def __init__(self):
        self.server_url = "https://nflmcp-production.up.railway.app/mcp"
        self.client = httpx.AsyncClient(timeout=30.0)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "server_url": self.server_url,
            "tests": {},
            "stats_data": {},
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
    
    async def test_nfl_player_stats(self):
        """Test NFL player stats functionality"""
        print("=" * 60)
        print("TEST #3: NFL MCP - Player Stats Testing")
        print("=" * 60)
        print("Target: 2024 NFL player statistics")
        
        # Test 3A: Top passers (2024)
        print("\n--- Test 3A: Top Passing Stats (2024) ---")
        await self.test_passing_stats()
        
        # Test 3B: Top rushers (2024)
        print("\n--- Test 3B: Top Rushing Stats (2024) ---")
        await self.test_rushing_stats()
        
        # Test 3C: Top receivers (2024)
        print("\n--- Test 3C: Top Receiving Stats (2024) ---")
        await self.test_receiving_stats()
        
        # Test 3D: Team-specific stats (Chiefs)
        print("\n--- Test 3D: Team-Specific Stats (Chiefs) ---")
        await self.test_team_stats()
        
        # Test 3E: Specific player search
        print("\n--- Test 3E: Player Search (Mahomes) ---")
        await self.test_player_search()
        
        # Summary and export
        await self.generate_summary()
        await self.export_results()
    
    async def test_passing_stats(self):
        """Test passing statistics"""
        print("Testing Top Passing Stats:")
        
        result = await self.call_mcp_tool("getNFLPlayerStats", {
            "season": 2024,
            "stat_type": "passing",
            "limit": 20
        })
        
        test_key = "passing_stats"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "passing stats 2024",
                "raw_data": result
            }
            players = self.analyze_stats_result(result, "Top Passers 2024")
            
            if players:
                self.results["stats_data"]["passing"] = players
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    async def test_rushing_stats(self):
        """Test rushing statistics"""
        print("Testing Top Rushing Stats:")
        
        result = await self.call_mcp_tool("getNFLPlayerStats", {
            "season": 2024,
            "stat_type": "rushing",
            "limit": 20
        })
        
        test_key = "rushing_stats"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "rushing stats 2024",
                "raw_data": result
            }
            players = self.analyze_stats_result(result, "Top Rushers 2024")
            
            if players:
                self.results["stats_data"]["rushing"] = players
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    async def test_receiving_stats(self):
        """Test receiving statistics"""
        print("Testing Top Receiving Stats:")
        
        result = await self.call_mcp_tool("getNFLPlayerStats", {
            "season": 2024,
            "stat_type": "receiving",
            "limit": 20
        })
        
        test_key = "receiving_stats"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "receiving stats 2024",
                "raw_data": result
            }
            players = self.analyze_stats_result(result, "Top Receivers 2024")
            
            if players:
                self.results["stats_data"]["receiving"] = players
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    async def test_team_stats(self):
        """Test team-specific player stats"""
        print("Testing Chiefs Player Stats:")
        
        result = await self.call_mcp_tool("getNFLPlayerStats", {
            "season": 2024,
            "team": "KC",
            "stat_type": "passing",
            "limit": 10
        })
        
        test_key = "chiefs_stats"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "Chiefs passing stats",
                "raw_data": result
            }
            players = self.analyze_stats_result(result, "Chiefs Passing Stats")
            
            if players:
                self.results["stats_data"]["chiefs"] = players
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    async def test_player_search(self):
        """Test specific player search"""
        print("Testing Player Search - Mahomes:")
        
        result = await self.call_mcp_tool("getNFLPlayerStats", {
            "season": 2024,
            "player_name": "Mahomes",
            "stat_type": "passing"
        })
        
        test_key = "mahomes_search"
        if result:
            self.results["tests"][test_key] = {
                "success": True,
                "method": "player name search",
                "raw_data": result
            }
            players = self.analyze_stats_result(result, "Mahomes Search")
            
            if players:
                self.results["stats_data"]["mahomes"] = players
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No data returned"
            }
    
    def analyze_stats_result(self, result: Dict[str, Any], test_name: str) -> Optional[list]:
        """Analyze and display stats result"""
        print(f"\n[*] Analyzing: {test_name}")
        
        if not result.get("ok"):
            print(f"[!] ERROR: Result indicates failure")
            return None
        
        data = result.get("data", {})
        players = data.get("players", [])
        source = data.get("source", "unknown")
        stat_type = data.get("stat_type", "unknown")
        
        print(f"    Source: {source}")
        print(f"    Stat Type: {stat_type}")
        print(f"    Players found: {len(players)}")
        
        if players:
            print(f"    Top players:")
            
            for i, player in enumerate(players[:10]):  # Show top 10
                name = player.get("player_name", "Unknown")
                team = player.get("team", "?")
                position = player.get("position", "?")
                
                # Display stats based on type
                if stat_type == "passing":
                    yards = player.get("passing_yards", 0)
                    tds = player.get("passing_tds", 0)
                    ints = player.get("interceptions", 0)
                    print(f"      {i+1:2d}. {name:<20} ({team}) - {yards:,} yards, {tds} TDs, {ints} INTs")
                
                elif stat_type == "rushing":
                    yards = player.get("rushing_yards", 0)
                    tds = player.get("rushing_tds", 0)
                    carries = player.get("carries", 0)
                    avg = yards / carries if carries > 0 else 0
                    print(f"      {i+1:2d}. {name:<20} ({team}) - {yards:,} yards, {tds} TDs, {avg:.1f} YPC")
                
                elif stat_type == "receiving":
                    yards = player.get("receiving_yards", 0)
                    tds = player.get("receiving_tds", 0)
                    recs = player.get("receptions", 0)
                    targets = player.get("targets", 0)
                    print(f"      {i+1:2d}. {name:<20} ({team}) - {recs} rec, {yards:,} yards, {tds} TDs")
            
            if len(players) > 10:
                print(f"      ... and {len(players) - 10} more players")
            
            return players
        
        print(f"    [!] No players found")
        return None
    
    async def generate_summary(self):
        """Generate test summary"""
        print(f"\n{'=' * 60}")
        print("TEST #3 SUMMARY - NFL Player Stats")
        print(f"{'=' * 60}")
        
        summary = {
            "status": "UNKNOWN",
            "total_tests": len(self.results["tests"]),
            "successful_tests": 0,
            "stats_info": {}
        }
        
        # Count successful tests
        for test_name, test_data in self.results["tests"].items():
            if test_data.get("success", False):
                summary["successful_tests"] += 1
        
        # Analyze stats data
        for stat_type in ["passing", "rushing", "receiving"]:
            if stat_type in self.results["stats_data"]:
                players = self.results["stats_data"][stat_type]
                summary["stats_info"][f"{stat_type}_players"] = len(players)
                
                # Get top performer
                if players:
                    top_player = players[0]
                    summary["stats_info"][f"top_{stat_type}"] = {
                        "name": top_player.get("player_name"),
                        "team": top_player.get("team")
                    }
        
        # Check specific searches
        if "mahomes" in self.results["stats_data"]:
            mahomes_data = self.results["stats_data"]["mahomes"]
            if mahomes_data:
                summary["stats_info"]["mahomes_found"] = True
                summary["stats_info"]["mahomes_stats"] = mahomes_data[0]
        
        # Overall status
        if summary["successful_tests"] >= 4:
            summary["status"] = "SUCCESS"
            print(f"[+] SUCCESS: NFL player stats working")
        elif summary["successful_tests"] >= 2:
            summary["status"] = "PARTIAL"
            print(f"[!] PARTIAL: {summary['successful_tests']}/{summary['total_tests']} tests passed")
        else:
            summary["status"] = "FAILED"
            print(f"[-] FAILED: NFL player stats not working")
        
        print(f"[+] Overall: {summary['successful_tests']}/{summary['total_tests']} tests passed")
        
        # Show key findings
        stats_info = summary["stats_info"]
        for stat_type in ["passing", "rushing", "receiving"]:
            if f"top_{stat_type}" in stats_info:
                top = stats_info[f"top_{stat_type}"]
                count = stats_info.get(f"{stat_type}_players", 0)
                print(f"[+] Top {stat_type.title()}: {top['name']} ({top['team']}) - {count} players total")
        
        if stats_info.get("mahomes_found"):
            mahomes = stats_info["mahomes_stats"]
            yards = mahomes.get("passing_yards", 0)
            tds = mahomes.get("passing_tds", 0)
            print(f"[+] Mahomes 2024: {yards:,} yards, {tds} TDs")
        
        self.results["summary"] = summary
    
    async def export_results(self):
        """Export test results to JSON file"""
        output_dir = "C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\nfl\\tools"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"player_stats_test_results_{timestamp}.json"
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
    """Run the NFL player stats test"""
    tester = NFLPlayerStatsTester()
    
    print("NFL MCP - Player Stats Test")
    print("Testing NFL player statistics")
    print(f"Server: nflmcp-production.up.railway.app")
    
    try:
        await tester.test_nfl_player_stats()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())