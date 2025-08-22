#!/usr/bin/env python3
"""
Team Form Data Test Script

This script tests the current MLB MCP server to see what team form data 
we actually get back and explores if we have access to enhanced form data.

Focus: Test both getMLBTeamForm and any enhanced versions to understand
what recent form data is available for Discord integration.
"""

import asyncio
import json
from datetime import datetime
import httpx

class TeamFormTester:
    """Test team form data from MLB MCP server"""
    
    def __init__(self):
        self.server_url = "https://mlbmcp-production.up.railway.app/mcp"
        self.client = None
        
        # Test with current teams that should have good data
        self.test_teams = {
            "Yankees": 147,
            "Dodgers": 119, 
            "Guardians": 114,
            "Astros": 117,
            "Rockies": 115,  # From your screenshot
            "Pirates": 134   # From your screenshot
        }
    
    async def init_client(self):
        """Initialize HTTP client"""
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def call_tool(self, tool_name: str, arguments: dict = None) -> dict:
        """Call an MLB MCP tool and return the result"""
        if not self.client:
            await self.init_client()
        
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
        
        print(f"\n🔧 Testing: {tool_name}")
        print(f"📋 Arguments: {json.dumps(arguments, indent=2)}")
        print("-" * 50)
        
        try:
            response = await self.client.post(self.server_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(f"❌ Error Response:")
                print(json.dumps(result["error"], indent=2))
                return {"error": result["error"]}
            
            return result.get("result", {})
            
        except Exception as e:
            print(f"❌ Request Failed: {e}")
            return {"error": str(e)}
    
    async def test_available_tools(self):
        """Test what tools are available on the server"""
        print("\n🔍 TESTING AVAILABLE TOOLS")
        print("=" * 60)
        
        # Try to list available tools
        list_result = await self.call_tool("tools/list")
        
        if "error" not in list_result:
            print("✅ Available tools:")
            tools = list_result.get("tools", [])
            team_form_tools = [tool for tool in tools if "team" in tool.get("name", "").lower() and "form" in tool.get("name", "").lower()]
            
            print(f"\n📊 Team Form related tools found: {len(team_form_tools)}")
            for tool in team_form_tools:
                print(f"  - {tool.get('name', 'Unknown')}")
                print(f"    Description: {tool.get('description', 'No description')}")
        else:
            print("❌ Could not list available tools")
    
    async def test_basic_team_form(self, team_name: str, team_id: int):
        """Test basic getMLBTeamForm tool"""
        print(f"\n📊 Testing Basic Team Form: {team_name} (ID: {team_id})")
        print("-" * 50)
        
        result = await self.call_tool("getMLBTeamForm", {"team_id": team_id})
        
        if "error" not in result:
            print("✅ Basic Team Form - SUCCESS")
            
            # Extract and analyze the data structure
            data = result.get("data", {})
            form = data.get("form", {})
            
            print(f"\n📋 Data Structure Analysis:")
            print(f"  - Team Name: {data.get('team_name', 'Not found')}")
            print(f"  - Record: {form.get('wins', 'N/A')}-{form.get('losses', 'N/A')}")
            print(f"  - Win %: {form.get('win_percentage', 'N/A')}")
            print(f"  - Streak: {form.get('streak', 'N/A')}")
            print(f"  - Last 10: {form.get('last_10', 'N/A')}")
            print(f"  - Games Back: {form.get('games_back', 'N/A')}")
            
            # Check for enhanced fields
            enhanced_fields = [
                "recent_form", "enhanced_records", "streak_info", 
                "home_record", "away_record", "recent_games"
            ]
            
            print(f"\n🔍 Enhanced Fields Check:")
            for field in enhanced_fields:
                if field in data or field in form:
                    print(f"  ✅ {field}: Found")
                else:
                    print(f"  ❌ {field}: Not found")
            
            # Full data dump for analysis
            print(f"\n📄 Full Response:")
            print(json.dumps(result, indent=2))
            
        else:
            print("❌ Basic Team Form - FAILED")
        
        return result
    
    async def test_enhanced_team_form(self, team_name: str, team_id: int):
        """Test if enhanced team form tools exist"""
        print(f"\n🔥 Testing Enhanced Team Form: {team_name} (ID: {team_id})")
        print("-" * 50)
        
        # Try different possible enhanced tool names
        enhanced_names = [
            "getMLBTeamFormEnhanced",
            "getMLBTeamFormDetailed", 
            "getMLBEnhancedTeamForm",
            "getMLBTeamFormWithRecent",
            "getTeamFormEnhanced"
        ]
        
        for tool_name in enhanced_names:
            print(f"\n🧪 Trying: {tool_name}")
            result = await self.call_tool(tool_name, {"team_id": team_id})
            
            if "error" not in result:
                print(f"✅ {tool_name} - SUCCESS!")
                
                # Analyze enhanced data
                data = result.get("data", {})
                print(f"\n📋 Enhanced Data Analysis:")
                
                # Look for recent form data
                if "enhanced_records" in data:
                    enhanced = data["enhanced_records"]
                    print(f"  📈 Enhanced Records Found:")
                    print(f"    - Total recent games: {enhanced.get('total_recent_games', 'N/A')}")
                    print(f"    - Home games count: {enhanced.get('home_games_count', 'N/A')}")
                    print(f"    - Away games count: {enhanced.get('away_games_count', 'N/A')}")
                
                if "streak_info" in data:
                    streak = data["streak_info"]
                    print(f"  🔥 Streak Info Found:")
                    print(f"    - Type: {streak.get('type', 'N/A')}")
                    print(f"    - Count: {streak.get('count', 'N/A')}")
                    print(f"    - Display: {streak.get('display', 'N/A')}")
                    print(f"    - Emoji: {streak.get('emoji', 'N/A')}")
                
                if "recent_games" in data:
                    recent = data["recent_games"]
                    print(f"  🎮 Recent Games: {len(recent) if isinstance(recent, list) else 'Not a list'}")
                
                # Full enhanced data dump
                print(f"\n📄 Full Enhanced Response:")
                print(json.dumps(result, indent=2))
                
                return result
            else:
                print(f"❌ {tool_name} - Not available")
        
        print("❌ No enhanced team form tools found")
        return None
    
    async def test_multiple_teams_comparison(self):
        """Test team form data for multiple teams to compare data consistency"""
        print(f"\n⚖️  MULTI-TEAM COMPARISON TEST")
        print("=" * 60)
        
        team_results = {}
        
        for team_name, team_id in list(self.test_teams.items())[:3]:  # Test first 3 teams
            print(f"\n🏟️  Testing {team_name}...")
            result = await self.test_basic_team_form(team_name, team_id)
            
            if "error" not in result:
                team_results[team_name] = result
        
        # Compare results
        print(f"\n📊 COMPARISON SUMMARY:")
        print("-" * 40)
        
        for team_name, result in team_results.items():
            data = result.get("data", {})
            form = data.get("form", {})
            
            wins = form.get("wins", "N/A")
            losses = form.get("losses", "N/A") 
            streak = form.get("streak", "N/A")
            last_10 = form.get("last_10", "N/A")
            
            print(f"{team_name:<15}: {wins}-{losses}, Streak: {streak}, Last 10: {last_10}")
    
    async def run_comprehensive_test(self):
        """Run all team form tests"""
        print("🏟️  MLB TEAM FORM DATA COMPREHENSIVE TEST")
        print("=" * 70)
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 Server: {self.server_url}")
        print("=" * 70)
        
        await self.init_client()
        
        # Test 1: Available tools
        await self.test_available_tools()
        
        # Test 2: Basic team form for a couple teams
        test_team_name = "Rockies"
        test_team_id = self.test_teams[test_team_name]
        
        basic_result = await self.test_basic_team_form(test_team_name, test_team_id)
        
        # Test 3: Enhanced team form
        enhanced_result = await self.test_enhanced_team_form(test_team_name, test_team_id)
        
        # Test 4: Multi-team comparison
        await self.test_multiple_teams_comparison()
        
        # Summary
        print(f"\n🎯 TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Basic Team Form: {'Working' if 'error' not in basic_result else 'Failed'}")
        print(f"🔥 Enhanced Team Form: {'Available' if enhanced_result else 'Not Available'}")
        
        if enhanced_result:
            print(f"\n💡 RECOMMENDATION: Use enhanced team form data!")
            print("   Enhanced data includes recent games, streak emojis, and better structure.")
        else:
            print(f"\n💡 RECOMMENDATION: Use basic team form data with estimates.")
            print("   Need to calculate home/away splits and recent form from basic data.")
        
        print(f"\n🏁 Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()

async def main():
    """Main test function"""
    tester = TeamFormTester()
    
    try:
        await tester.run_comprehensive_test()
    finally:
        await tester.close()

if __name__ == "__main__":
    print("🚀 Starting Team Form Data Test...")
    asyncio.run(main())