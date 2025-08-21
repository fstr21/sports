#!/usr/bin/env python3
"""
Comprehensive MLB MCP Server Test Suite

Tests all 8 MLB MCP tools with various scenarios and parameter combinations.
Generates detailed reports and saves results to JSON files.

Available Tools:
1. getMLBScheduleET - Game schedules 
2. getMLBTeams - Team information
3. getMLBTeamRoster - Team rosters
4. getMLBPlayerLastN - Player game logs
5. getMLBPitcherMatchup - Pitcher analysis  
6. getMLBTeamForm - Team standings/form
7. getMLBPlayerStreaks - Player streaks
8. getMLBTeamScoringTrends - Team scoring patterns

Usage:
    python comprehensive_mlb_test.py
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import httpx

class MLBMCPTester:
    """Comprehensive test suite for MLB MCP server"""
    
    def __init__(self):
        self.server_url = "https://mlbmcp-production.up.railway.app/mcp"
        self.client = httpx.AsyncClient(timeout=60.0)
        self.results = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "server_url": self.server_url,
                "total_tests": 0,
                "successful_tests": 0,
                "failed_tests": 0
            },
            "tool_tests": {},
            "summary": {}
        }
        
        # Known working team/player IDs for testing
        self.test_teams = {
            "yankees": 147,
            "dodgers": 119,
            "guardians": 114,
            "marlins": 146,
            "mariners": 136
        }
        
        self.test_players = {
            "aaron_judge": 592450,
            "julio_rodriguez": 677594,
            "mookie_betts": 605141,
            "jose_altuve": 514888
        }
        
        self.test_pitchers = {
            "gerrit_cole": 543037,
            "clayton_kershaw": 477132,
            "shane_bieber": 669456
        }
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Call an MCP tool and return result"""
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
        
        try:
            response = await self.client.post(self.server_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                return {"ok": False, "error": result["error"]}
            
            return result.get("result", {})
            
        except Exception as e:
            return {"ok": False, "error": f"Request failed: {str(e)}"}
    
    async def test_schedule_tool(self):
        """Test getMLBScheduleET tool"""
        print("=" * 60)
        print("TESTING: getMLBScheduleET")
        print("=" * 60)
        
        tests = []
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Test 1: Default (today)
        print("\n[1] Testing default date (today)...")
        result1 = await self.call_mcp_tool("getMLBScheduleET")
        tests.append(self.analyze_schedule_result(result1, "default_today", {}))
        
        # Test 2: Explicit today
        print(f"\n[2] Testing explicit date ({today})...")
        result2 = await self.call_mcp_tool("getMLBScheduleET", {"date": today})
        tests.append(self.analyze_schedule_result(result2, "explicit_today", {"date": today}))
        
        # Test 3: Yesterday
        print(f"\n[3] Testing yesterday ({yesterday})...")
        result3 = await self.call_mcp_tool("getMLBScheduleET", {"date": yesterday})
        tests.append(self.analyze_schedule_result(result3, "yesterday", {"date": yesterday}))
        
        # Test 4: Tomorrow
        print(f"\n[4] Testing tomorrow ({tomorrow})...")
        result4 = await self.call_mcp_tool("getMLBScheduleET", {"date": tomorrow})
        tests.append(self.analyze_schedule_result(result4, "tomorrow", {"date": tomorrow}))
        
        # Test 5: Off-season date
        print(f"\n[5] Testing off-season date (2025-01-15)...")
        result5 = await self.call_mcp_tool("getMLBScheduleET", {"date": "2025-01-15"})
        tests.append(self.analyze_schedule_result(result5, "offseason", {"date": "2025-01-15"}))
        
        self.results["tool_tests"]["getMLBScheduleET"] = {
            "total_tests": len(tests),
            "successful_tests": sum(1 for t in tests if t["success"]),
            "tests": tests
        }
    
    def analyze_schedule_result(self, result: Optional[Dict[str, Any]], test_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze schedule test result"""
        test_result = {
            "test_name": test_name,
            "arguments": args,
            "success": False,
            "game_count": 0,
            "error": None,
            "sample_games": []
        }
        
        if not result:
            test_result["error"] = "No result returned"
            print(f"    ❌ {test_name}: No result")
            return test_result
        
        if not result.get("ok"):
            test_result["error"] = result.get("error", "Unknown error")
            print(f"    ❌ {test_name}: {test_result['error']}")
            return test_result
        
        data = result.get("data", {})
        games = data.get("games", [])
        count = data.get("count", 0)
        
        test_result["success"] = True
        test_result["game_count"] = count
        
        # Get sample games
        for i, game in enumerate(games[:3]):
            away_team = game.get("away", {}).get("name", "Unknown")
            home_team = game.get("home", {}).get("name", "Unknown")
            start_time = game.get("start_et", "Unknown")
            status = game.get("status", "Unknown")
            
            test_result["sample_games"].append({
                "away_team": away_team,
                "home_team": home_team,
                "start_time": start_time,
                "status": status
            })
        
        print(f"    ✅ {test_name}: {count} games found")
        if games:
            print(f"       Sample: {test_result['sample_games'][0]['away_team']} @ {test_result['sample_games'][0]['home_team']}")
        
        return test_result
    
    async def test_teams_tool(self):
        """Test getMLBTeams tool"""
        print("\n" + "=" * 60)
        print("TESTING: getMLBTeams")
        print("=" * 60)
        
        tests = []
        
        # Test 1: Default season
        print("\n[1] Testing default season...")
        result1 = await self.call_mcp_tool("getMLBTeams")
        tests.append(self.analyze_teams_result(result1, "default_season", {}))
        
        # Test 2: Current season explicit
        print(f"\n[2] Testing current season (2025)...")
        result2 = await self.call_mcp_tool("getMLBTeams", {"season": 2025})
        tests.append(self.analyze_teams_result(result2, "current_season", {"season": 2025}))
        
        # Test 3: Previous season
        print(f"\n[3] Testing previous season (2024)...")
        result3 = await self.call_mcp_tool("getMLBTeams", {"season": 2024})
        tests.append(self.analyze_teams_result(result3, "previous_season", {"season": 2024}))
        
        self.results["tool_tests"]["getMLBTeams"] = {
            "total_tests": len(tests),
            "successful_tests": sum(1 for t in tests if t["success"]),
            "tests": tests
        }
    
    def analyze_teams_result(self, result: Optional[Dict[str, Any]], test_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze teams test result"""
        test_result = {
            "test_name": test_name,
            "arguments": args,
            "success": False,
            "team_count": 0,
            "error": None,
            "sample_teams": []
        }
        
        if not result or not result.get("ok"):
            test_result["error"] = result.get("error", "No result") if result else "No result"
            print(f"    ❌ {test_name}: {test_result['error']}")
            return test_result
        
        data = result.get("data", {})
        teams = data.get("teams", [])
        count = data.get("count", 0)
        
        test_result["success"] = True
        test_result["team_count"] = count
        
        # Get sample teams
        for team in teams[:5]:
            test_result["sample_teams"].append({
                "teamId": team.get("teamId"),
                "name": team.get("name"),
                "abbrev": team.get("abbrev"),
                "league": team.get("league"),
                "division": team.get("division")
            })
        
        print(f"    ✅ {test_name}: {count} teams found")
        if teams:
            print(f"       Sample: {teams[0].get('name')} ({teams[0].get('abbrev')})")
        
        return test_result
    
    async def test_roster_tool(self):
        """Test getMLBTeamRoster tool"""
        print("\n" + "=" * 60)
        print("TESTING: getMLBTeamRoster")
        print("=" * 60)
        
        tests = []
        
        # Test multiple teams
        for team_name, team_id in list(self.test_teams.items())[:3]:
            print(f"\n[{len(tests)+1}] Testing {team_name} roster (ID: {team_id})...")
            result = await self.call_mcp_tool("getMLBTeamRoster", {"teamId": team_id})
            tests.append(self.analyze_roster_result(result, f"{team_name}_roster", {"teamId": team_id}))
        
        # Test with explicit season
        print(f"\n[{len(tests)+1}] Testing Yankees 2024 roster...")
        result = await self.call_mcp_tool("getMLBTeamRoster", {"teamId": 147, "season": 2024})
        tests.append(self.analyze_roster_result(result, "yankees_2024", {"teamId": 147, "season": 2024}))
        
        # Test invalid team ID
        print(f"\n[{len(tests)+1}] Testing invalid team ID...")
        result = await self.call_mcp_tool("getMLBTeamRoster", {"teamId": 999})
        tests.append(self.analyze_roster_result(result, "invalid_team", {"teamId": 999}))
        
        self.results["tool_tests"]["getMLBTeamRoster"] = {
            "total_tests": len(tests),
            "successful_tests": sum(1 for t in tests if t["success"]),
            "tests": tests
        }
    
    def analyze_roster_result(self, result: Optional[Dict[str, Any]], test_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze roster test result"""
        test_result = {
            "test_name": test_name,
            "arguments": args,
            "success": False,
            "player_count": 0,
            "error": None,
            "sample_players": []
        }
        
        if not result or not result.get("ok"):
            test_result["error"] = result.get("error", "No result") if result else "No result"
            print(f"    ❌ {test_name}: {test_result['error']}")
            return test_result
        
        data = result.get("data", {})
        players = data.get("players", [])
        count = data.get("count", 0)
        
        test_result["success"] = True
        test_result["player_count"] = count
        
        # Get sample players
        for player in players[:5]:
            test_result["sample_players"].append({
                "playerId": player.get("playerId"),
                "fullName": player.get("fullName"),
                "primaryNumber": player.get("primaryNumber"),
                "position": player.get("position")
            })
        
        print(f"    ✅ {test_name}: {count} players found")
        if players:
            print(f"       Sample: {players[0].get('fullName')} (#{players[0].get('primaryNumber', 'N/A')} {players[0].get('position', 'N/A')})")
        
        return test_result
    
    async def test_player_stats_tool(self):
        """Test getMLBPlayerLastN tool"""
        print("\n" + "=" * 60)
        print("TESTING: getMLBPlayerLastN")
        print("=" * 60)
        
        tests = []
        
        # Test 1: Single player, hitting stats
        player_id = self.test_players["aaron_judge"]
        print(f"\n[1] Testing Aaron Judge hitting stats (ID: {player_id})...")
        result1 = await self.call_mcp_tool("getMLBPlayerLastN", {
            "player_ids": [player_id],
            "group": "hitting",
            "stats": ["hits", "homeRuns", "atBats", "runsBattedIn"],
            "count": 5
        })
        tests.append(self.analyze_player_stats_result(result1, "judge_hitting", {
            "player_ids": [player_id], "group": "hitting", "count": 5
        }))
        
        # Test 2: Multiple players
        multi_players = [self.test_players["aaron_judge"], self.test_players["julio_rodriguez"]]
        print(f"\n[2] Testing multiple players (Judge + Julio)...")
        result2 = await self.call_mcp_tool("getMLBPlayerLastN", {
            "player_ids": multi_players,
            "group": "hitting", 
            "stats": ["hits", "homeRuns"],
            "count": 3
        })
        tests.append(self.analyze_player_stats_result(result2, "multi_players", {
            "player_ids": multi_players, "group": "hitting", "count": 3
        }))
        
        # Test 3: Pitcher stats
        pitcher_id = self.test_pitchers["gerrit_cole"]
        print(f"\n[3] Testing Gerrit Cole pitching stats (ID: {pitcher_id})...")
        result3 = await self.call_mcp_tool("getMLBPlayerLastN", {
            "player_ids": [pitcher_id],
            "group": "pitching",
            "stats": ["strikeOuts", "walks", "hits", "earnedRuns"],
            "count": 5
        })
        tests.append(self.analyze_player_stats_result(result3, "cole_pitching", {
            "player_ids": [pitcher_id], "group": "pitching", "count": 5
        }))
        
        # Test 4: Invalid player ID
        print(f"\n[4] Testing invalid player ID...")
        result4 = await self.call_mcp_tool("getMLBPlayerLastN", {
            "player_ids": [999999],
            "group": "hitting",
            "count": 5
        })
        tests.append(self.analyze_player_stats_result(result4, "invalid_player", {
            "player_ids": [999999], "group": "hitting", "count": 5
        }))
        
        self.results["tool_tests"]["getMLBPlayerLastN"] = {
            "total_tests": len(tests),
            "successful_tests": sum(1 for t in tests if t["success"]),
            "tests": tests
        }
    
    def analyze_player_stats_result(self, result: Optional[Dict[str, Any]], test_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze player stats test result"""
        test_result = {
            "test_name": test_name,
            "arguments": args,
            "success": False,
            "players_processed": 0,
            "total_games": 0,
            "error": None,
            "sample_stats": []
        }
        
        if not result or not result.get("ok"):
            test_result["error"] = result.get("error", "No result") if result else "No result"
            print(f"    ❌ {test_name}: {test_result['error']}")
            return test_result
        
        data = result.get("data", {})
        results = data.get("results", {})
        errors = data.get("errors", {})
        
        test_result["success"] = True
        test_result["players_processed"] = len(results)
        
        # Analyze each player's data
        for player_id, player_data in results.items():
            games = player_data.get("games", [])
            aggregates = player_data.get("aggregates", {})
            
            test_result["total_games"] += len(games)
            
            # Add sample stats
            if aggregates:
                sample = {"player_id": player_id, "aggregates": {}}
                for key, value in list(aggregates.items())[:4]:  # First 4 stats
                    sample["aggregates"][key] = value
                test_result["sample_stats"].append(sample)
        
        print(f"    ✅ {test_name}: {len(results)} players, {test_result['total_games']} total games")
        if errors:
            print(f"       Errors: {len(errors)} players had errors")
        
        return test_result
    
    async def test_advanced_tools(self):
        """Test the 4 advanced MLB tools"""
        print("\n" + "=" * 60)
        print("TESTING: Advanced MLB Tools")
        print("=" * 60)
        
        # Test getMLBPitcherMatchup
        print("\n[1] Testing getMLBPitcherMatchup...")
        pitcher_id = self.test_pitchers["gerrit_cole"]
        pitcher_result = await self.call_mcp_tool("getMLBPitcherMatchup", {
            "pitcher_id": pitcher_id,
            "count": 5
        })
        pitcher_test = self.analyze_simple_result(pitcher_result, "pitcher_matchup", {"pitcher_id": pitcher_id})
        
        # Test getMLBTeamForm
        print("\n[2] Testing getMLBTeamForm...")
        team_id = self.test_teams["yankees"]
        form_result = await self.call_mcp_tool("getMLBTeamForm", {"team_id": team_id})
        form_test = self.analyze_simple_result(form_result, "team_form", {"team_id": team_id})
        
        # Test getMLBPlayerStreaks
        print("\n[3] Testing getMLBPlayerStreaks...")
        player_id = self.test_players["aaron_judge"]
        streaks_result = await self.call_mcp_tool("getMLBPlayerStreaks", {
            "player_ids": [player_id],
            "lookback": 15
        })
        streaks_test = self.analyze_simple_result(streaks_result, "player_streaks", {"player_ids": [player_id]})
        
        # Test getMLBTeamScoringTrends
        print("\n[4] Testing getMLBTeamScoringTrends...")
        scoring_result = await self.call_mcp_tool("getMLBTeamScoringTrends", {"team_id": team_id})
        scoring_test = self.analyze_simple_result(scoring_result, "scoring_trends", {"team_id": team_id})
        
        # Store results
        self.results["tool_tests"]["getMLBPitcherMatchup"] = {"tests": [pitcher_test]}
        self.results["tool_tests"]["getMLBTeamForm"] = {"tests": [form_test]}
        self.results["tool_tests"]["getMLBPlayerStreaks"] = {"tests": [streaks_test]}
        self.results["tool_tests"]["getMLBTeamScoringTrends"] = {"tests": [scoring_test]}
    
    def analyze_simple_result(self, result: Optional[Dict[str, Any]], test_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze simple tool result"""
        test_result = {
            "test_name": test_name,
            "arguments": args,
            "success": False,
            "error": None,
            "data_summary": {}
        }
        
        if not result or not result.get("ok"):
            test_result["error"] = result.get("error", "No result") if result else "No result"
            print(f"    ❌ {test_name}: {test_result['error']}")
            return test_result
        
        test_result["success"] = True
        data = result.get("data", {})
        
        # Extract key data points based on tool type
        if "pitcher" in test_name:
            aggregates = data.get("aggregates", {})
            test_result["data_summary"] = {
                "era": aggregates.get("era"),
                "whip": aggregates.get("whip"),
                "strikeouts": aggregates.get("strikeouts")
            }
        elif "form" in test_name:
            form = data.get("form", {})
            test_result["data_summary"] = {
                "wins": form.get("wins"),
                "losses": form.get("losses"),
                "win_percentage": form.get("win_percentage"),
                "streak": form.get("streak")
            }
        elif "streaks" in test_name:
            results = data.get("results", {})
            if results:
                first_player = list(results.values())[0]
                streaks = first_player.get("streaks", {})
                test_result["data_summary"] = {
                    "current_hit_streak": streaks.get("current_hit_streak"),
                    "multi_hit_games": streaks.get("multi_hit_games")
                }
        elif "scoring" in test_name:
            trends = data.get("trends", {})
            test_result["data_summary"] = {
                "runs_per_game": trends.get("runs_per_game"),
                "run_differential": trends.get("run_differential")
            }
        
        print(f"    ✅ {test_name}: Success")
        print(f"       Data: {test_result['data_summary']}")
        
        return test_result
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Comprehensive MLB MCP Test Suite")
        print(f"Server: {self.server_url}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Run all tool tests
        await self.test_schedule_tool()
        await self.test_teams_tool()
        await self.test_roster_tool()
        await self.test_player_stats_tool()
        await self.test_advanced_tools()
        
        # Calculate totals
        total_tests = 0
        successful_tests = 0
        
        for tool_name, tool_results in self.results["tool_tests"].items():
            if "tests" in tool_results:
                tests = tool_results["tests"]
                total_tests += len(tests)
                successful_tests += sum(1 for t in tests if t["success"])
        
        self.results["test_run"]["total_tests"] = total_tests
        self.results["test_run"]["successful_tests"] = successful_tests
        self.results["test_run"]["failed_tests"] = total_tests - successful_tests
        
        # Generate summary
        self.generate_summary()
        
        # Save results
        await self.save_results()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total = self.results["test_run"]["total_tests"]
        successful = self.results["test_run"]["successful_tests"]
        failed = self.results["test_run"]["failed_tests"]
        
        print(f"Total Tests: {total}")
        print(f"Successful: {successful} ({successful/total*100:.1f}%)")
        print(f"Failed: {failed} ({failed/total*100:.1f}%)")
        print()
        
        # Tool-by-tool breakdown
        for tool_name, tool_results in self.results["tool_tests"].items():
            if "tests" in tool_results:
                tests = tool_results["tests"]
                tool_successful = sum(1 for t in tests if t["success"])
                print(f"{tool_name}: {tool_successful}/{len(tests)} tests passed")
        
        # Overall status
        if successful == total:
            status = "🟢 ALL TESTS PASSED"
        elif successful > total * 0.8:
            status = "🟡 MOSTLY WORKING"
        else:
            status = "🔴 MULTIPLE FAILURES"
        
        print(f"\nOverall Status: {status}")
        
        self.results["summary"] = {
            "overall_status": status,
            "success_rate": f"{successful/total*100:.1f}%",
            "working_tools": [name for name, results in self.results["tool_tests"].items() 
                            if "tests" in results and any(t["success"] for t in results["tests"])],
            "broken_tools": [name for name, results in self.results["tool_tests"].items() 
                           if "tests" in results and not any(t["success"] for t in results["tests"])]
        }
    
    async def save_results(self):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\mlb\\testing\\comprehensive_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(filename)
            size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} bytes"
            
            print(f"\n💾 Results saved to: {filename}")
            print(f"   File size: {size_str}")
            
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Run the comprehensive test suite"""
    tester = MLBMCPTester()
    
    try:
        await tester.run_all_tests()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())