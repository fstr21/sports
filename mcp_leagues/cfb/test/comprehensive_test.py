#!/usr/bin/env python3
"""
CFB MCP Comprehensive Test Suite
Tests all available tools and suggests additional useful tools

Current Tools Available:
1. getCFBGames - Get games by year/week/team/conference
2. getCFBTeams - Get team information
3. getCFBRoster - Get team rosters
4. getCFBPlayerStats - Get player statistics
5. getCFBRankings - Get rankings
6. getCFBConferences - Get conference information
7. getCFBTeamRecords - Get team records
8. getCFBGameStats - Get game statistics
9. getCFBPlays - Get play-by-play data
"""

import asyncio
import json
import httpx
import os
from datetime import datetime
from pathlib import Path

# CFB MCP Server URL
CFB_MCP_URL = "https://cfbmcp-production.up.railway.app/mcp"

class CFBMCPTester:
    def __init__(self):
        self.results = {
            "test_suite": "CFB MCP Comprehensive Test",
            "timestamp": datetime.now().isoformat(),
            "server_url": CFB_MCP_URL,
            "tools_tested": [],
            "health_check": {},
            "test_results": {},
            "suggested_tools": []
        }
    
    async def test_health_check(self):
        """Test server health"""
        print("🏥 Testing Server Health...")
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"https://cfbmcp-production.up.railway.app/health")
                
                if response.status_code == 200:
                    health_data = response.json()
                    self.results["health_check"] = {
                        "status": "healthy",
                        "response": health_data,
                        "success": True
                    }
                    print(f"✅ Server is healthy: {health_data}")
                    return True
                else:
                    self.results["health_check"] = {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}",
                        "success": False
                    }
                    print(f"❌ Health check failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            self.results["health_check"] = {
                "status": "error",
                "error": str(e),
                "success": False
            }
            print(f"❌ Health check error: {e}")
            return False
    
    async def test_tool(self, tool_name, args, description):
        """Test a specific MCP tool"""
        print(f"\n🏈 Testing {tool_name}: {description}")
        print("-" * 50)
        
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": args
            }
        }
        
        test_result = {
            "tool": tool_name,
            "description": description,
            "args": args,
            "success": False,
            "data_count": 0,
            "sample_data": {},
            "error": None
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    CFB_MCP_URL,
                    json=mcp_request,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if "result" in result and "content" in result["result"]:
                        content = result["result"]["content"]
                        
                        # Parse JSON data from content
                        for item in content:
                            if item.get("type") == "text" and item.get("text", "").startswith("```json"):
                                json_text = item["text"].replace("```json\n", "").replace("\n```", "")
                                data = json.loads(json_text)
                                
                                test_result["success"] = True
                                test_result["full_data"] = data
                                
                                # Extract specific metrics based on tool
                                if tool_name == "getCFBGames":
                                    games = data.get("games", [])
                                    test_result["data_count"] = len(games)
                                    test_result["sample_data"] = {
                                        "total_games": len(games),
                                        "sample_games": [
                                            {
                                                "away": g.get("away_team"),
                                                "home": g.get("home_team"),
                                                "week": g.get("week"),
                                                "date": g.get("start_date", "").split("T")[0]
                                            } for g in games[:3]
                                        ]
                                    }
                                    print(f"✅ Found {len(games)} games")
                                    for i, game in enumerate(games[:3]):
                                        print(f"   {i+1}. {game.get('away_team')} @ {game.get('home_team')} (Week {game.get('week')})")
                                
                                elif tool_name == "getCFBTeams":
                                    teams = data.get("teams", [])
                                    test_result["data_count"] = len(teams)
                                    test_result["sample_data"] = {
                                        "total_teams": len(teams),
                                        "sample_teams": [
                                            {
                                                "school": t.get("school"),
                                                "conference": t.get("conference"),
                                                "division": t.get("division")
                                            } for t in teams[:5]
                                        ]
                                    }
                                    print(f"✅ Found {len(teams)} teams")
                                    for i, team in enumerate(teams[:5]):
                                        print(f"   {i+1}. {team.get('school')} ({team.get('conference')})")
                                
                                elif tool_name == "getCFBRoster":
                                    players = data.get("players", [])
                                    test_result["data_count"] = len(players)
                                    positions = {}
                                    for player in players:
                                        pos = player.get("position", "Unknown")
                                        positions[pos] = positions.get(pos, 0) + 1
                                    test_result["sample_data"] = {
                                        "total_players": len(players),
                                        "position_breakdown": positions,
                                        "sample_players": [
                                            {
                                                "name": f"{p.get('first_name', '')} {p.get('last_name', '')}",
                                                "position": p.get("position"),
                                                "year": p.get("year")
                                            } for p in players[:5]
                                        ]
                                    }
                                    print(f"✅ Found {len(players)} players")
                                    print(f"   Position breakdown: {dict(list(positions.items())[:5])}")
                                
                                elif tool_name == "getCFBPlayerStats":
                                    player_stats = data.get("player_stats", [])
                                    test_result["data_count"] = len(player_stats)
                                    test_result["sample_data"] = {
                                        "total_stat_entries": len(player_stats),
                                        "sample_stats": player_stats[:3] if player_stats else []
                                    }
                                    print(f"✅ Found {len(player_stats)} stat entries")
                                
                                elif tool_name == "getCFBRankings":
                                    rankings = data.get("rankings", [])
                                    test_result["data_count"] = len(rankings)
                                    polls = {}
                                    for ranking in rankings:
                                        poll = ranking.get("poll", "Unknown")
                                        polls[poll] = polls.get(poll, 0) + 1
                                    test_result["sample_data"] = {
                                        "total_rankings": len(rankings),
                                        "polls_available": list(polls.keys()),
                                        "sample_rankings": [
                                            {
                                                "team": r.get("team"),
                                                "rank": r.get("rank"),
                                                "poll": r.get("poll")
                                            } for r in rankings[:5]
                                        ]
                                    }
                                    print(f"✅ Found {len(rankings)} rankings across {len(polls)} polls")
                                
                                elif tool_name == "getCFBConferences":
                                    conferences = data.get("conferences", [])
                                    test_result["data_count"] = len(conferences)
                                    test_result["sample_data"] = {
                                        "total_conferences": len(conferences),
                                        "conference_names": [c.get("name") for c in conferences[:10]]
                                    }
                                    print(f"✅ Found {len(conferences)} conferences")
                                
                                elif tool_name == "getCFBTeamRecords":
                                    records = data.get("records", [])
                                    test_result["data_count"] = len(records)
                                    test_result["sample_data"] = {
                                        "total_records": len(records),
                                        "sample_records": [
                                            {
                                                "team": r.get("team"),
                                                "wins": r.get("total", {}).get("wins"),
                                                "losses": r.get("total", {}).get("losses")
                                            } for r in records[:5]
                                        ]
                                    }
                                    print(f"✅ Found records for {len(records)} teams")
                                
                                elif tool_name == "getCFBGameStats":
                                    game_stats = data.get("game_stats", [])
                                    test_result["data_count"] = len(game_stats)
                                    test_result["sample_data"] = {
                                        "total_games": len(game_stats),
                                        "sample_games": game_stats[:3] if game_stats else []
                                    }
                                    print(f"✅ Found stats for {len(game_stats)} games")
                                
                                elif tool_name == "getCFBPlays":
                                    plays = data.get("plays", [])
                                    test_result["data_count"] = len(plays)
                                    play_types = {}
                                    for play in plays:
                                        play_type = play.get("play_type", "Unknown")
                                        play_types[play_type] = play_types.get(play_type, 0) + 1
                                    test_result["sample_data"] = {
                                        "total_plays": len(plays),
                                        "play_types": dict(list(play_types.items())[:10]),
                                        "sample_plays": [
                                            {
                                                "offense": p.get("offense"),
                                                "play_type": p.get("play_type"),
                                                "yards_gained": p.get("yards_gained")
                                            } for p in plays[:5]
                                        ]
                                    }
                                    print(f"✅ Found {len(plays)} plays with {len(play_types)} different play types")
                                
                                break
                        
                        if not test_result["success"]:
                            test_result["error"] = "No JSON data found in response"
                            print("❌ No valid JSON data found")
                    else:
                        test_result["error"] = f"Unexpected response format: {result}"
                        print(f"❌ Unexpected response: {result}")
                else:
                    test_result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                    print(f"❌ HTTP Error: {response.status_code}")
                    
        except Exception as e:
            test_result["error"] = str(e)
            print(f"❌ Exception: {e}")
        
        self.results["test_results"][tool_name] = test_result
        return test_result["success"]
    
    async def run_comprehensive_tests(self):
        """Run all tool tests"""
        
        print("🏈 CFB MCP COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        
        # Health check first
        health_ok = await self.test_health_check()
        if not health_ok:
            print("❌ Server health check failed, aborting tests")
            return
        
        # Define all test cases
        test_cases = [
            {
                "tool": "getCFBGames",
                "args": {"year": 2024, "week": 1},
                "description": "Week 1 2024 Games"
            },
            {
                "tool": "getCFBTeams", 
                "args": {"conference": "Big 12"},
                "description": "Big 12 Conference Teams"
            },
            {
                "tool": "getCFBRoster",
                "args": {"team": "Kansas State", "year": 2024},
                "description": "Kansas State 2024 Roster"
            },
            {
                "tool": "getCFBPlayerStats",
                "args": {"year": 2024, "team": "Kansas State", "category": "passing"},
                "description": "Kansas State 2024 Passing Stats"
            },
            {
                "tool": "getCFBRankings",
                "args": {"year": 2024, "week": 15},
                "description": "Final 2024 Rankings"
            },
            {
                "tool": "getCFBConferences",
                "args": {},
                "description": "All Conferences"
            },
            {
                "tool": "getCFBTeamRecords",
                "args": {"year": 2024, "conference": "Big 12"},
                "description": "Big 12 2024 Records"
            },
            {
                "tool": "getCFBGameStats",
                "args": {"year": 2024, "week": 1, "conference": "Big 12"},
                "description": "Big 12 Week 1 2024 Game Stats"
            },
            {
                "tool": "getCFBPlays",
                "args": {"year": 2024, "week": 1, "team": "Kansas State"},
                "description": "Kansas State Week 1 2024 Plays"
            }
        ]
        
        # Run tests
        success_count = 0
        for test_case in test_cases:
            success = await self.test_tool(
                test_case["tool"],
                test_case["args"], 
                test_case["description"]
            )
            if success:
                success_count += 1
            
            self.results["tools_tested"].append(test_case["tool"])
        
        # Summary
        print(f"\n📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Successful tests: {success_count}/{len(test_cases)}")
        print(f"❌ Failed tests: {len(test_cases) - success_count}/{len(test_cases)}")
        
        # Analyze gaps and suggest additional tools
        await self.analyze_tool_gaps()
    
    async def analyze_tool_gaps(self):
        """Analyze what additional tools would be useful"""
        print(f"\n🔍 ANALYZING TOOL GAPS & SUGGESTIONS")
        print("=" * 60)
        
        current_tools = {
            "getCFBGames": "Game schedules and basic info",
            "getCFBTeams": "Team information",
            "getCFBRoster": "Team rosters",
            "getCFBPlayerStats": "Player statistics",
            "getCFBRankings": "Polls and rankings",
            "getCFBConferences": "Conference info",
            "getCFBTeamRecords": "Season records",
            "getCFBGameStats": "Team game statistics",
            "getCFBPlays": "Play-by-play data"
        }
        
        # Suggested additional tools based on CFBD API capabilities
        suggested_tools = [
            {
                "name": "getCFBCoaches",
                "description": "Get coaching staff information",
                "rationale": "Important for team analysis and recruiting insights",
                "cfbd_endpoint": "/coaches",
                "usefulness": "High - coaching changes affect team performance"
            },
            {
                "name": "getCFBRecruits",
                "description": "Get recruiting class information",
                "rationale": "Critical for understanding future team strength",
                "cfbd_endpoint": "/recruiting/players",
                "usefulness": "High - recruiting drives program success"
            },
            {
                "name": "getCFBVenues",
                "description": "Get stadium and venue information",
                "rationale": "Venue details affect game analysis (capacity, surface, altitude)",
                "cfbd_endpoint": "/venues",
                "usefulness": "Medium - useful for game context"
            },
            {
                "name": "getCFBBettingLines",
                "description": "Get historical betting lines and spreads",
                "rationale": "Essential for sports betting analysis and predictions",
                "cfbd_endpoint": "/lines",
                "usefulness": "Very High - core requirement for betting analysis"
            },
            {
                "name": "getCFBAdvancedStats",
                "description": "Get advanced team statistics (EPA, success rate, etc.)",
                "rationale": "Modern analytics for deeper team evaluation",
                "cfbd_endpoint": "/stats/game/advanced",
                "usefulness": "Very High - advanced metrics are crucial"
            },
            {
                "name": "getCFBTransferPortal",
                "description": "Get transfer portal activity",
                "rationale": "Transfer portal significantly impacts modern CFB",
                "cfbd_endpoint": "/player/portal",
                "usefulness": "High - major factor in team composition"
            },
            {
                "name": "getCFBInjuries",
                "description": "Get injury reports and player availability",
                "rationale": "Critical for accurate game predictions",
                "cfbd_endpoint": "/injuries",
                "usefulness": "Very High - injuries greatly affect outcomes"
            },
            {
                "name": "getCFBWeather",
                "description": "Get game weather conditions",
                "rationale": "Weather significantly impacts game outcomes",
                "cfbd_endpoint": "/weather",
                "usefulness": "Medium-High - affects betting and predictions"
            },
            {
                "name": "getCFBDriveStats",
                "description": "Get drive-level statistics",
                "rationale": "More granular than play-by-play for efficiency analysis",
                "cfbd_endpoint": "/drives",
                "usefulness": "Medium - useful for detailed analysis"
            },
            {
                "name": "getCFBTeamTalent",
                "description": "Get team talent composite ratings",
                "rationale": "Objective measure of roster talent level",
                "cfbd_endpoint": "/talent",
                "usefulness": "High - talent correlates with success"
            }
        ]
        
        print("Current Tools (9 total):")
        for tool, desc in current_tools.items():
            print(f"  ✅ {tool} - {desc}")
        
        print(f"\nSuggested Additional Tools ({len(suggested_tools)} total):")
        for i, tool in enumerate(suggested_tools, 1):
            usefulness_icon = {
                "Very High": "🔥",
                "High": "⭐", 
                "Medium-High": "📈",
                "Medium": "📊"
            }.get(tool["usefulness"], "📋")
            
            print(f"  {usefulness_icon} {tool['name']} - {tool['description']}")
            print(f"      Rationale: {tool['rationale']}")
            print(f"      Usefulness: {tool['usefulness']}")
            print()
        
        # Priority recommendations
        high_priority = [t for t in suggested_tools if "Very High" in t["usefulness"]]
        print(f"🔥 HIGH PRIORITY ADDITIONS ({len(high_priority)} tools):")
        for tool in high_priority:
            print(f"  • {tool['name']} - {tool['rationale']}")
        
        self.results["suggested_tools"] = suggested_tools
    
    async def save_results(self):
        """Save test results to JSON file"""
        os.makedirs("test", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test/cfb_mcp_comprehensive_test_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filename}")
        return filename

async def main():
    """Run comprehensive CFB MCP tests"""
    tester = CFBMCPTester()
    
    await tester.run_comprehensive_tests()
    filename = await tester.save_results()
    
    print(f"\n🎉 CFB MCP COMPREHENSIVE TEST COMPLETE!")
    print(f"📊 Results saved to: {filename}")
    print(f"🔗 Server tested: {CFB_MCP_URL}")

if __name__ == "__main__":
    asyncio.run(main())