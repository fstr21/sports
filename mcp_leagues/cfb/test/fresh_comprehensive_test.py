#!/usr/bin/env python3
"""
Fresh CFB MCP Comprehensive Test - August 24, 2025
Test all current tools and analyze additional useful tools needed
"""

import asyncio
import json
import httpx
import os
from datetime import datetime

# CFB MCP Server URL
CFB_MCP_URL = "https://cfbmcp-production.up.railway.app/mcp"

class CFBMCPFreshTester:
    def __init__(self):
        self.results = {
            "test_suite": "CFB MCP Fresh Comprehensive Test",
            "timestamp": datetime.now().isoformat(),
            "server_url": CFB_MCP_URL,
            "current_tools": {},
            "health_status": {},
            "tool_test_results": {},
            "gaps_identified": [],
            "high_priority_missing": [],
            "recommendations": []
        }
    
    async def test_health_check(self):
        """Test server health and get basic info"""
        print("🏥 TESTING CFB MCP SERVER HEALTH")
        print("=" * 50)
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                health_response = await client.get("https://cfbmcp-production.up.railway.app/health")
                
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    self.results["health_status"] = {
                        "status": "healthy",
                        "details": health_data,
                        "success": True
                    }
                    print(f"✅ Server Status: HEALTHY")
                    print(f"   Response: {health_data}")
                    return True
                else:
                    print(f"❌ Health Check Failed: HTTP {health_response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Health Check Error: {e}")
            return False
    
    async def list_available_tools(self):
        """Get list of available tools from MCP server"""
        print(f"\n🛠️ DISCOVERING AVAILABLE TOOLS")
        print("=" * 50)
        
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(CFB_MCP_URL, json=mcp_request)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if "result" in result and "tools" in result["result"]:
                        tools = result["result"]["tools"]
                        self.results["current_tools"] = tools
                        
                        print(f"✅ Found {len(tools)} available tools:")
                        for i, tool in enumerate(tools, 1):
                            name = tool.get("name", "Unknown")
                            description = tool.get("description", "No description")
                            print(f"   {i}. {name} - {description}")
                        
                        return tools
                    else:
                        print(f"❌ Unexpected response format: {result}")
                        return []
                else:
                    print(f"❌ Failed to list tools: HTTP {response.status_code}")
                    return []
                    
        except Exception as e:
            print(f"❌ Error listing tools: {e}")
            return []
    
    async def test_tool_functionality(self, tool_name, test_args, description):
        """Test a specific tool with given arguments"""
        print(f"\n🧪 Testing {tool_name}")
        print(f"   {description}")
        print(f"   Args: {test_args}")
        print("-" * 40)
        
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": test_args
            }
        }
        
        test_result = {
            "tool": tool_name,
            "description": description,
            "test_args": test_args,
            "success": False,
            "data_quality": "unknown",
            "record_count": 0,
            "sample_data": {},
            "error": None,
            "response_time": 0
        }
        
        start_time = datetime.now()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(CFB_MCP_URL, json=mcp_request)
                end_time = datetime.now()
                test_result["response_time"] = (end_time - start_time).total_seconds()
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if "result" in result and "content" in result["result"]:
                        content = result["result"]["content"]
                        
                        # Parse response data
                        for item in content:
                            if item.get("type") == "text" and "```json" in item.get("text", ""):
                                json_text = item["text"]
                                # Extract JSON from markdown code block
                                start_idx = json_text.find("```json") + 7
                                end_idx = json_text.find("```", start_idx)
                                if end_idx > start_idx:
                                    json_data = json_text[start_idx:end_idx].strip()
                                    data = json.loads(json_data)
                                    
                                    test_result["success"] = True
                                    test_result["full_response"] = data
                                    
                                    # Analyze data quality and extract key metrics
                                    await self.analyze_tool_data(tool_name, data, test_result)
                                    break
                        
                        if test_result["success"]:
                            print(f"✅ {tool_name} SUCCESS")
                            print(f"   Records: {test_result['record_count']}")
                            print(f"   Quality: {test_result['data_quality']}")
                            print(f"   Response Time: {test_result['response_time']:.2f}s")
                        else:
                            print(f"❌ {tool_name} - Could not parse response data")
                            test_result["error"] = "Could not parse JSON response"
                    else:
                        print(f"❌ {tool_name} - Invalid response format")
                        test_result["error"] = f"Invalid response format: {result}"
                else:
                    print(f"❌ {tool_name} - HTTP Error {response.status_code}")
                    test_result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                    
        except Exception as e:
            print(f"❌ {tool_name} - Exception: {e}")
            test_result["error"] = str(e)
        
        self.results["tool_test_results"][tool_name] = test_result
        return test_result
    
    async def analyze_tool_data(self, tool_name, data, test_result):
        """Analyze the quality and structure of tool data"""
        
        if tool_name == "getCFBGames":
            games = data.get("games", [])
            test_result["record_count"] = len(games)
            if games:
                sample_game = games[0]
                has_venue = bool(sample_game.get("venue"))
                has_scores = bool(sample_game.get("home_points") is not None)
                has_excitement = bool(sample_game.get("excitement_index") is not None)
                test_result["data_quality"] = "excellent" if all([has_venue, has_scores, has_excitement]) else "good"
                test_result["sample_data"] = {
                    "sample_games": [f"{g.get('away_team')} @ {g.get('home_team')}" for g in games[:3]],
                    "has_venues": has_venue,
                    "has_scores": has_scores,
                    "has_excitement_index": has_excitement
                }
        
        elif tool_name == "getCFBTeams":
            teams = data.get("teams", [])
            test_result["record_count"] = len(teams)
            if teams:
                sample_team = teams[0]
                has_logos = bool(sample_team.get("logos"))
                has_colors = bool(sample_team.get("color"))
                has_location = bool(sample_team.get("location"))
                test_result["data_quality"] = "excellent" if all([has_logos, has_colors, has_location]) else "good"
                test_result["sample_data"] = {
                    "conferences": list(set(t.get("conference") for t in teams if t.get("conference")))[:5],
                    "has_logos": has_logos,
                    "has_colors": has_colors
                }
        
        elif tool_name == "getCFBRoster":
            players = data.get("players", [])
            test_result["record_count"] = len(players)
            if players:
                positions = {}
                for player in players:
                    pos = player.get("position", "Unknown")
                    positions[pos] = positions.get(pos, 0) + 1
                test_result["data_quality"] = "excellent" if len(players) > 50 else "good"
                test_result["sample_data"] = {
                    "total_players": len(players),
                    "position_breakdown": dict(list(positions.items())[:6]),
                    "has_details": bool(players[0].get("height") and players[0].get("weight"))
                }
        
        elif tool_name == "getCFBPlayerStats":
            stats = data.get("stats", []) or data.get("player_stats", [])
            test_result["record_count"] = len(stats)
            if stats:
                categories = set(s.get("category") for s in stats if s.get("category"))
                test_result["data_quality"] = "excellent" if len(categories) > 3 else "good"
                test_result["sample_data"] = {
                    "stat_categories": list(categories)[:5],
                    "total_entries": len(stats)
                }
        
        elif tool_name == "getCFBRankings":
            rankings = data.get("rankings", [])
            test_result["record_count"] = len(rankings)
            if rankings:
                polls = set(r.get("poll") for r in rankings if r.get("poll"))
                test_result["data_quality"] = "excellent" if len(polls) > 2 else "good"
                test_result["sample_data"] = {
                    "polls_available": list(polls),
                    "total_rankings": len(rankings)
                }
        
        elif tool_name == "getCFBConferences":
            conferences = data.get("conferences", [])
            test_result["record_count"] = len(conferences)
            test_result["data_quality"] = "excellent" if len(conferences) > 50 else "good"
            test_result["sample_data"] = {
                "total_conferences": len(conferences),
                "sample_names": [c.get("name") for c in conferences[:5]]
            }
        
        elif tool_name == "getCFBTeamRecords":
            records = data.get("records", [])
            test_result["record_count"] = len(records)
            if records:
                has_expected_wins = bool(records[0].get("expected_wins"))
                test_result["data_quality"] = "excellent" if has_expected_wins else "good"
                test_result["sample_data"] = {
                    "total_records": len(records),
                    "has_advanced_metrics": has_expected_wins
                }
        
        elif tool_name == "getCFBGameStats":
            game_stats = data.get("game_stats", [])
            test_result["record_count"] = len(game_stats)
            if game_stats:
                has_detailed_stats = len(game_stats[0].get("teams", [])) > 0
                test_result["data_quality"] = "excellent" if has_detailed_stats else "good"
                test_result["sample_data"] = {
                    "games_with_stats": len(game_stats),
                    "has_team_breakdowns": has_detailed_stats
                }
        
        elif tool_name == "getCFBPlays":
            plays = data.get("plays", [])
            test_result["record_count"] = len(plays)
            if plays:
                play_types = set(p.get("play_type") for p in plays if p.get("play_type"))
                test_result["data_quality"] = "excellent" if len(play_types) > 10 else "good"
                test_result["sample_data"] = {
                    "total_plays": len(plays),
                    "play_types": list(play_types)[:8]
                }
    
    async def identify_missing_tools(self):
        """Identify high-priority missing tools based on industry needs"""
        print(f"\n🎯 IDENTIFYING HIGH-PRIORITY MISSING TOOLS")
        print("=" * 50)
        
        # Critical missing tools for sports betting and advanced analytics
        critical_missing = [
            {
                "name": "getCFBBettingLines",
                "priority": "VERY HIGH",
                "description": "Historical betting lines, spreads, and totals",
                "cfbd_endpoint": "/lines",
                "use_case": "Essential for sports betting analysis, market efficiency studies",
                "impact": "Enables value betting identification and prediction validation"
            },
            {
                "name": "getCFBAdvancedStats", 
                "priority": "VERY HIGH",
                "description": "Advanced metrics (EPA, success rate, explosiveness, havoc)",
                "cfbd_endpoint": "/stats/game/advanced",
                "use_case": "Modern analytics for accurate team evaluation",
                "impact": "Provides cutting-edge metrics for superior predictions"
            },
            {
                "name": "getCFBInjuries",
                "priority": "VERY HIGH", 
                "description": "Injury reports and player availability",
                "cfbd_endpoint": "/injuries",
                "use_case": "Critical for game prediction accuracy",
                "impact": "Injuries dramatically affect game outcomes and betting lines"
            }
        ]
        
        high_priority_missing = [
            {
                "name": "getCFBCoaches",
                "priority": "HIGH",
                "description": "Coaching staff information and history",
                "cfbd_endpoint": "/coaches",
                "use_case": "Coaching changes affect team performance",
                "impact": "Coach experience and scheme changes impact outcomes"
            },
            {
                "name": "getCFBRecruits",
                "priority": "HIGH",
                "description": "Recruiting class rankings and commits",
                "cfbd_endpoint": "/recruiting/players",
                "use_case": "Future team strength prediction",
                "impact": "Recruiting classes indicate future competitive level"
            },
            {
                "name": "getCFBTransferPortal",
                "priority": "HIGH", 
                "description": "Transfer portal activity and player movement",
                "cfbd_endpoint": "/player/portal",
                "use_case": "Modern roster composition analysis",
                "impact": "Transfer portal significantly affects team dynamics"
            },
            {
                "name": "getCFBTeamTalent",
                "priority": "HIGH",
                "description": "Team talent composite ratings",
                "cfbd_endpoint": "/talent", 
                "use_case": "Objective talent measurement",
                "impact": "Talent ratings correlate strongly with performance"
            }
        ]
        
        medium_priority = [
            {
                "name": "getCFBWeather",
                "priority": "MEDIUM-HIGH",
                "description": "Game weather conditions",
                "cfbd_endpoint": "/weather",
                "use_case": "Weather impact on game outcomes",
                "impact": "Weather affects scoring and betting totals"
            },
            {
                "name": "getCFBVenues",
                "priority": "MEDIUM",
                "description": "Stadium details (capacity, surface, altitude)",
                "cfbd_endpoint": "/venues",
                "use_case": "Venue context for analysis",
                "impact": "Stadium characteristics affect game dynamics"
            },
            {
                "name": "getCFBDriveStats",
                "priority": "MEDIUM",
                "description": "Drive-level efficiency statistics", 
                "cfbd_endpoint": "/drives",
                "use_case": "Granular efficiency analysis",
                "impact": "Drive efficiency provides detailed team analysis"
            }
        ]
        
        self.results["gaps_identified"] = critical_missing + high_priority_missing + medium_priority
        self.results["high_priority_missing"] = critical_missing
        
        print("🔥 CRITICAL MISSING (Very High Priority):")
        for tool in critical_missing:
            print(f"   • {tool['name']} - {tool['description']}")
            print(f"     Use Case: {tool['use_case']}")
        
        print(f"\n⭐ HIGH PRIORITY MISSING:")
        for tool in high_priority_missing:
            print(f"   • {tool['name']} - {tool['description']}")
        
        print(f"\n📈 MEDIUM PRIORITY MISSING:")
        for tool in medium_priority:
            print(f"   • {tool['name']} - {tool['description']}")
    
    async def generate_recommendations(self):
        """Generate actionable recommendations based on analysis"""
        print(f"\n📋 RECOMMENDATIONS")
        print("=" * 50)
        
        # Count successful tools
        successful_tools = sum(1 for result in self.results["tool_test_results"].values() if result["success"])
        total_tools = len(self.results["tool_test_results"])
        
        recommendations = [
            f"✅ Current Status: {successful_tools}/{total_tools} tools working ({successful_tools/total_tools*100:.0f}%)",
            f"🎯 Foundation Quality: Excellent - comprehensive core CFB data coverage",
            f"🚀 Priority Actions:",
            f"   1. Implement getCFBBettingLines (CRITICAL for sports betting)",
            f"   2. Implement getCFBAdvancedStats (CRITICAL for modern analytics)", 
            f"   3. Implement getCFBInjuries (CRITICAL for prediction accuracy)",
            f"📊 Strategic Impact:",
            f"   • Current tools provide solid foundation for CFB analysis",
            f"   • Missing tools would transform platform into industry leader",
            f"   • 3 critical additions would enable advanced betting analysis",
            f"💡 Development Priority:",
            f"   • Phase 1: Implement 3 critical missing tools",
            f"   • Phase 2: Add 4 high-priority tools for enhanced intelligence",
            f"   • Phase 3: Add remaining tools for comprehensive coverage"
        ]
        
        self.results["recommendations"] = recommendations
        
        for rec in recommendations:
            print(rec)
    
    async def save_results(self):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cfb_mcp_fresh_test_{timestamp}.json"
        filepath = os.path.join("c:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\cfb\\test", filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 RESULTS SAVED")
        print("=" * 50)
        print(f"File: {filepath}")
        print(f"Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    async def run_comprehensive_test(self):
        """Run the complete test suite"""
        print("🏈 CFB MCP FRESH COMPREHENSIVE TEST")
        print("=" * 60)
        print("Testing all current tools and identifying gaps")
        print(f"Target: {CFB_MCP_URL}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test server health
        if not await self.test_health_check():
            print("❌ Server health check failed - aborting tests")
            return
        
        # Get available tools
        available_tools = await self.list_available_tools()
        if not available_tools:
            print("❌ Could not retrieve tool list - aborting tests")
            return
        
        # Test each tool with realistic parameters
        test_scenarios = [
            ("getCFBGames", {"year": 2024, "week": 1}, "Week 1 2024 games"),
            ("getCFBTeams", {"conference": "Big 12"}, "Big 12 teams"), 
            ("getCFBRoster", {"team": "Kansas State", "year": 2024}, "Kansas State 2024 roster"),
            ("getCFBPlayerStats", {"year": 2024, "team": "Kansas State", "category": "passing"}, "Kansas State passing stats"),
            ("getCFBRankings", {"year": 2024, "week": 1}, "Week 1 2024 rankings"),
            ("getCFBConferences", {}, "All conferences"),
            ("getCFBTeamRecords", {"year": 2024, "team": "Kansas State"}, "Kansas State 2024 record"),
            ("getCFBGameStats", {"year": 2024, "week": 1, "team": "Kansas State"}, "Kansas State Week 1 stats"),
            ("getCFBPlays", {"year": 2024, "week": 1, "team": "Kansas State"}, "Kansas State Week 1 plays")
        ]
        
        # Test all tools
        for tool_name, args, description in test_scenarios:
            await self.test_tool_functionality(tool_name, args, description)
        
        # Identify missing tools
        await self.identify_missing_tools()
        
        # Generate recommendations
        await self.generate_recommendations()
        
        # Save results
        await self.save_results()

async def main():
    """Main test execution"""
    tester = CFBMCPFreshTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())