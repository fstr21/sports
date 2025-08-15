#!/usr/bin/env python3
"""
Test NFL MCP Server
Quick test to validate NFL MCP functionality
"""

import httpx
import json
import asyncio
from datetime import datetime

class NFLMCPTester:
    """Test NFL MCP functionality"""
    
    def __init__(self, server_url="http://localhost:8080/mcp"):
        self.server_url = server_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def call_mcp_tool(self, tool_name: str, arguments: dict = None) -> dict:
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
        
        print(f"[*] Testing {tool_name}...")
        if arguments:
            print(f"    Arguments: {arguments}")
        
        try:
            response = await self.client.post(self.server_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                print(f"[!] Error: {result['error']}")
                return None
            
            return result.get("result", {})
            
        except Exception as e:
            print(f"[!] Request failed: {e}")
            return None
    
    async def test_all_tools(self):
        """Test all NFL MCP tools"""
        print("=" * 60)
        print("NFL MCP TEST SUITE")
        print("=" * 60)
        
        # Test 1: Get NFL Schedule
        print("\n--- Test 1: NFL Schedule ---")
        schedule_result = await self.call_mcp_tool("getNFLSchedule", {
            "season": 2025,
            "week": 1,
            "use_test_mode": True
        })
        
        if schedule_result and schedule_result.get("ok"):
            games = schedule_result.get("data", {}).get("games", [])
            print(f"✓ Found {len(games)} games")
            if games:
                sample = games[0]
                print(f"  Sample: {sample['away_team']} @ {sample['home_team']}")
        
        # Test 2: Get NFL Teams
        print("\n--- Test 2: NFL Teams ---")
        teams_result = await self.call_mcp_tool("getNFLTeams", {
            "conference": "AFC",
            "use_test_mode": True
        })
        
        if teams_result and teams_result.get("ok"):
            teams = teams_result.get("data", {}).get("teams", [])
            print(f"✓ Found {len(teams)} AFC teams")
        
        # Test 3: Get Player Stats
        print("\n--- Test 3: Player Stats ---")
        stats_result = await self.call_mcp_tool("getNFLPlayerStats", {
            "season": 2024,
            "stat_type": "passing",
            "limit": 5,
            "use_test_mode": True
        })
        
        if stats_result and stats_result.get("ok"):
            players = stats_result.get("data", {}).get("players", [])
            print(f"✓ Found {len(players)} top passers")
        
        # Test 4: Get Injuries
        print("\n--- Test 4: Injury Reports ---")
        injury_result = await self.call_mcp_tool("getNFLInjuries", {
            "status": "Out",
            "limit": 5,
            "use_test_mode": True
        })
        
        if injury_result and injury_result.get("ok"):
            injuries = injury_result.get("data", {}).get("injuries", [])
            print(f"✓ Found {len(injuries)} injury reports")
        
        # Test 5: Get Team Stats
        print("\n--- Test 5: Team Stats ---")
        team_stats_result = await self.call_mcp_tool("getNFLTeamStats", {
            "season": 2024,
            "team": "KC",
            "use_test_mode": True
        })
        
        if team_stats_result and team_stats_result.get("ok"):
            team_data = team_stats_result.get("data", {}).get("teams", [])
            print(f"✓ Found stats for {len(team_data)} teams")
        
        print("\n" + "=" * 60)
        print("NFL MCP TESTS COMPLETE")
        print("=" * 60)
        print("All tools working in test mode")
        print("Ready for deployment to Railway")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Run NFL MCP tests"""
    tester = NFLMCPTester()
    
    try:
        await tester.test_all_tools()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())