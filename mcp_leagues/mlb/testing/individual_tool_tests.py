#!/usr/bin/env python3
"""
Individual MLB MCP Tool Tests

Focused tests for specific MLB MCP tools with detailed parameter exploration.
Useful for testing specific functionality or debugging individual tools.

Usage:
    python individual_tool_tests.py --tool schedule
    python individual_tool_tests.py --tool teams
    python individual_tool_tests.py --tool roster --team-id 147
    python individual_tool_tests.py --tool player-stats --player-id 592450
    python individual_tool_tests.py --tool all
"""

import asyncio
import argparse
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import httpx

class IndividualToolTester:
    """Individual MLB MCP tool testing"""
    
    def __init__(self):
        self.server_url = "https://mlbmcp-production.up.railway.app/mcp"
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # Known good test data
        self.known_teams = {
            "yankees": {"id": 147, "name": "New York Yankees"},
            "dodgers": {"id": 119, "name": "Los Angeles Dodgers"},
            "guardians": {"id": 114, "name": "Cleveland Guardians"},
            "marlins": {"id": 146, "name": "Miami Marlins"},
            "mariners": {"id": 136, "name": "Seattle Mariners"}
        }
        
        self.known_players = {
            "aaron_judge": {"id": 592450, "name": "Aaron Judge", "team": "Yankees"},
            "mookie_betts": {"id": 605141, "name": "Mookie Betts", "team": "Dodgers"},
            "julio_rodriguez": {"id": 677594, "name": "Julio Rodriguez", "team": "Mariners"},
            "jose_altuve": {"id": 514888, "name": "Jose Altuve", "team": "Astros"}
        }
        
        self.known_pitchers = {
            "gerrit_cole": {"id": 543037, "name": "Gerrit Cole", "team": "Yankees"},
            "clayton_kershaw": {"id": 477132, "name": "Clayton Kershaw", "team": "Dodgers"},
            "shane_bieber": {"id": 669456, "name": "Shane Bieber", "team": "Guardians"}
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
        
        print(f"🔧 Calling: {tool_name}")
        print(f"📝 Arguments: {json.dumps(arguments, indent=2)}")
        
        try:
            response = await self.client.post(self.server_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                return {"ok": False, "error": result["error"]}
            
            return result.get("result", {})
            
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return {"ok": False, "error": str(e)}
    
    async def test_schedule_tool(self, date: str = None):
        """Test getMLBScheduleET tool in detail"""
        print("=" * 60)
        print("🗓️  TESTING: getMLBScheduleET")
        print("=" * 60)
        
        tests = []
        
        # Test scenarios
        scenarios = [
            {"name": "Default (today)", "args": {}},
            {"name": "Explicit today", "args": {"date": datetime.now().strftime("%Y-%m-%d")}},
            {"name": "Yesterday", "args": {"date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")}},
            {"name": "Tomorrow", "args": {"date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")}},
            {"name": "Peak season date", "args": {"date": "2025-07-15"}},
            {"name": "Off-season date", "args": {"date": "2025-01-15"}}
        ]
        
        if date:
            scenarios = [{"name": f"Custom date ({date})", "args": {"date": date}}]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n[{i}] {scenario['name']}")
            print(f"    Arguments: {scenario['args']}")
            
            result = await self.call_mcp_tool("getMLBScheduleET", scenario["args"])
            
            if result and result.get("ok"):
                data = result.get("data", {})
                games = data.get("games", [])
                count = data.get("count", 0)
                date_et = data.get("date_et", "Unknown")
                
                print(f"    ✅ Success: {count} games on {date_et}")
                
                # Show first 3 games
                for j, game in enumerate(games[:3]):
                    away = game.get("away", {}).get("name", "Unknown")
                    home = game.get("home", {}).get("name", "Unknown")
                    time = game.get("start_et", "Unknown")
                    status = game.get("status", "Unknown")
                    venue = game.get("venue", "Unknown")
                    
                    print(f"      Game {j+1}: {away} @ {home}")
                    print(f"               Time: {time}")
                    print(f"               Status: {status}")
                    print(f"               Venue: {venue}")
                
                if len(games) > 3:
                    print(f"      ... and {len(games) - 3} more games")
                
                tests.append({"scenario": scenario["name"], "success": True, "games": count})
            else:
                error = result.get("error", "Unknown error") if result else "No response"
                print(f"    ❌ Failed: {error}")
                tests.append({"scenario": scenario["name"], "success": False, "error": error})
        
        return tests
    
    async def test_teams_tool(self, season: int = None):
        """Test getMLBTeams tool in detail"""
        print("=" * 60)
        print("⚾ TESTING: getMLBTeams")
        print("=" * 60)
        
        tests = []
        current_year = datetime.now().year
        
        # Test scenarios
        scenarios = [
            {"name": "Default season", "args": {}},
            {"name": f"Current season ({current_year})", "args": {"season": current_year}},
            {"name": f"Previous season ({current_year-1})", "args": {"season": current_year-1}},
            {"name": "Historical season (2020)", "args": {"season": 2020}}
        ]
        
        if season:
            scenarios = [{"name": f"Custom season ({season})", "args": {"season": season}}]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n[{i}] {scenario['name']}")
            print(f"    Arguments: {scenario['args']}")
            
            result = await self.call_mcp_tool("getMLBTeams", scenario["args"])
            
            if result and result.get("ok"):
                data = result.get("data", {})
                teams = data.get("teams", [])
                count = data.get("count", 0)
                season_tested = data.get("season", "Unknown")
                
                print(f"    ✅ Success: {count} teams for {season_tested}")
                
                # Analyze teams by league/division
                al_teams = [t for t in teams if t.get("league") == "American League"]
                nl_teams = [t for t in teams if t.get("league") == "National League"]
                
                print(f"      American League: {len(al_teams)} teams")
                print(f"      National League: {len(nl_teams)} teams")
                
                # Show sample teams from each league
                if al_teams:
                    sample_al = al_teams[0]
                    print(f"      AL Sample: {sample_al.get('name')} ({sample_al.get('abbrev')}) - {sample_al.get('division')}")
                
                if nl_teams:
                    sample_nl = nl_teams[0]
                    print(f"      NL Sample: {sample_nl.get('name')} ({sample_nl.get('abbrev')}) - {sample_nl.get('division')}")
                
                tests.append({"scenario": scenario["name"], "success": True, "teams": count})
            else:
                error = result.get("error", "Unknown error") if result else "No response"
                print(f"    ❌ Failed: {error}")
                tests.append({"scenario": scenario["name"], "success": False, "error": error})
        
        return tests
    
    async def test_roster_tool(self, team_id: int = None):
        """Test getMLBTeamRoster tool in detail"""
        print("=" * 60)
        print("👥 TESTING: getMLBTeamRoster")
        print("=" * 60)
        
        tests = []
        teams_to_test = [team_id] if team_id else [147, 119, 114]  # Yankees, Dodgers, Guardians
        
        for i, test_team_id in enumerate(teams_to_test, 1):
            team_name = next((name for name, data in self.known_teams.items() if data["id"] == test_team_id), f"Team {test_team_id}")
            
            print(f"\n[{i}] Testing {team_name} roster (ID: {test_team_id})")
            
            result = await self.call_mcp_tool("getMLBTeamRoster", {"teamId": test_team_id})
            
            if result and result.get("ok"):
                data = result.get("data", {})
                players = data.get("players", [])
                count = data.get("count", 0)
                season = data.get("season", "Unknown")
                
                print(f"    ✅ Success: {count} players for {season}")
                
                # Analyze by position
                positions = {}
                for player in players:
                    pos = player.get("position", "Unknown")
                    positions[pos] = positions.get(pos, 0) + 1
                
                print(f"    Position breakdown:")
                for pos, count_pos in sorted(positions.items()):
                    print(f"      {pos}: {count_pos} players")
                
                # Show notable players
                print(f"    Sample players:")
                for j, player in enumerate(players[:5]):
                    name = player.get("fullName", "Unknown")
                    number = player.get("primaryNumber", "N/A")
                    position = player.get("position", "N/A")
                    status = player.get("status", "Unknown")
                    
                    print(f"      {j+1}. {name} (#{number} {position}) - {status}")
                
                tests.append({"team": team_name, "success": True, "players": len(players)})
            else:
                error = result.get("error", "Unknown error") if result else "No response"
                print(f"    ❌ Failed: {error}")
                tests.append({"team": team_name, "success": False, "error": error})
        
        return tests
    
    async def test_player_stats_tool(self, player_id: int = None, pitcher_mode: bool = False):
        """Test getMLBPlayerLastN tool in detail"""
        print("=" * 60)
        print("📊 TESTING: getMLBPlayerLastN")
        print("=" * 60)
        
        tests = []
        
        if player_id:
            # Test specific player
            player_name = f"Player {player_id}"
            for name, data in {**self.known_players, **self.known_pitchers}.items():
                if data["id"] == player_id:
                    player_name = data["name"]
                    break
            
            group = "pitching" if pitcher_mode else "hitting"
            stats = ["strikeOuts", "walks", "hits"] if pitcher_mode else ["hits", "homeRuns", "atBats"]
            
            print(f"\n[1] Testing {player_name} {group} stats (ID: {player_id})")
            
            result = await self.call_mcp_tool("getMLBPlayerLastN", {
                "player_ids": [player_id],
                "group": group,
                "stats": stats,
                "count": 10
            })
            
            if result and result.get("ok"):
                data = result.get("data", {})
                results = data.get("results", {})
                errors = data.get("errors", {})
                
                if str(player_id) in results:
                    player_data = results[str(player_id)]
                    games = player_data.get("games", [])
                    aggregates = player_data.get("aggregates", {})
                    
                    print(f"    ✅ Success: {len(games)} games found")
                    print(f"    Aggregates:")
                    for stat_key, value in aggregates.items():
                        print(f"      {stat_key}: {value}")
                    
                    print(f"    Recent games:")
                    for i, game in enumerate(games[:5]):
                        date = game.get("date_et", "Unknown")
                        game_stats = []
                        for stat in stats:
                            value = game.get(stat, 0)
                            game_stats.append(f"{stat}:{value}")
                        print(f"      Game {i+1} ({date}): {', '.join(game_stats)}")
                    
                    tests.append({"player": player_name, "success": True, "games": len(games)})
                else:
                    error = errors.get(str(player_id), "Player not found in results")
                    print(f"    ❌ Failed: {error}")
                    tests.append({"player": player_name, "success": False, "error": error})
            else:
                error = result.get("error", "Unknown error") if result else "No response"
                print(f"    ❌ Failed: {error}")
                tests.append({"player": player_name, "success": False, "error": error})
        
        else:
            # Test multiple scenarios
            scenarios = [
                {
                    "name": "Aaron Judge hitting (last 5 games)",
                    "args": {
                        "player_ids": [592450],
                        "group": "hitting",
                        "stats": ["hits", "homeRuns", "atBats", "runsBattedIn"],
                        "count": 5
                    }
                },
                {
                    "name": "Multiple players hitting",
                    "args": {
                        "player_ids": [592450, 677594],  # Judge + Julio
                        "group": "hitting",
                        "stats": ["hits", "homeRuns"],
                        "count": 3
                    }
                },
                {
                    "name": "Gerrit Cole pitching (last 5 starts)",
                    "args": {
                        "player_ids": [543037],
                        "group": "pitching",
                        "stats": ["strikeOuts", "walks", "hits", "earnedRuns"],
                        "count": 5
                    }
                }
            ]
            
            for i, scenario in enumerate(scenarios, 1):
                print(f"\n[{i}] {scenario['name']}")
                print(f"    Arguments: {json.dumps(scenario['args'], indent=6)}")
                
                result = await self.call_mcp_tool("getMLBPlayerLastN", scenario["args"])
                
                if result and result.get("ok"):
                    data = result.get("data", {})
                    results = data.get("results", {})
                    errors = data.get("errors", {})
                    
                    print(f"    ✅ Success: {len(results)} players processed")
                    
                    for player_id, player_data in results.items():
                        games = player_data.get("games", [])
                        aggregates = player_data.get("aggregates", {})
                        print(f"      Player {player_id}: {len(games)} games")
                        
                        # Show key aggregates
                        if aggregates:
                            key_stats = [(k, v) for k, v in aggregates.items() if "avg" in k][:3]
                            for stat, value in key_stats:
                                print(f"        {stat}: {value:.3f}")
                    
                    if errors:
                        print(f"      Errors: {len(errors)} players had errors")
                    
                    tests.append({"scenario": scenario["name"], "success": True, "players": len(results)})
                else:
                    error = result.get("error", "Unknown error") if result else "No response"
                    print(f"    ❌ Failed: {error}")
                    tests.append({"scenario": scenario["name"], "success": False, "error": error})
        
        return tests
    
    async def test_advanced_tools(self):
        """Test the 4 advanced MLB tools"""
        print("=" * 60)
        print("🔬 TESTING: Advanced MLB Tools")
        print("=" * 60)
        
        tests = []
        
        # Test 1: Pitcher Matchup
        print("\n[1] Testing getMLBPitcherMatchup")
        pitcher_id = 543037  # Gerrit Cole
        result1 = await self.call_mcp_tool("getMLBPitcherMatchup", {
            "pitcher_id": pitcher_id,
            "count": 5
        })
        
        if result1 and result1.get("ok"):
            data = result1.get("data", {})
            aggregates = data.get("aggregates", {})
            recent_starts = data.get("recent_starts", [])
            
            print(f"    ✅ Success: {len(recent_starts)} starts analyzed")
            print(f"    Season stats:")
            print(f"      ERA: {aggregates.get('era', 'N/A')}")
            print(f"      WHIP: {aggregates.get('whip', 'N/A')}")
            print(f"      K/9: {aggregates.get('k_per_9', 'N/A')}")
            
            tests.append({"tool": "getMLBPitcherMatchup", "success": True})
        else:
            error = result1.get("error", "Unknown error") if result1 else "No response"
            print(f"    ❌ Failed: {error}")
            tests.append({"tool": "getMLBPitcherMatchup", "success": False, "error": error})
        
        # Test 2: Team Form
        print("\n[2] Testing getMLBTeamForm")
        team_id = 147  # Yankees
        result2 = await self.call_mcp_tool("getMLBTeamForm", {"team_id": team_id})
        
        if result2 and result2.get("ok"):
            data = result2.get("data", {})
            form = data.get("form", {})
            team_name = data.get("team_name", "Unknown")
            
            print(f"    ✅ Success: {team_name} form data")
            print(f"    Record: {form.get('wins', 0)}-{form.get('losses', 0)}")
            print(f"    Win %: {form.get('win_percentage', 'N/A')}")
            print(f"    Streak: {form.get('streak', 'N/A')}")
            print(f"    Last 10: {form.get('last_10', 'N/A')}")
            
            tests.append({"tool": "getMLBTeamForm", "success": True})
        else:
            error = result2.get("error", "Unknown error") if result2 else "No response"
            print(f"    ❌ Failed: {error}")
            tests.append({"tool": "getMLBTeamForm", "success": False, "error": error})
        
        # Test 3: Player Streaks
        print("\n[3] Testing getMLBPlayerStreaks")
        player_id = 592450  # Aaron Judge
        result3 = await self.call_mcp_tool("getMLBPlayerStreaks", {
            "player_ids": [player_id],
            "lookback": 20
        })
        
        if result3 and result3.get("ok"):
            data = result3.get("data", {})
            results = data.get("results", {})
            
            if str(player_id) in results:
                player_data = results[str(player_id)]
                streaks = player_data.get("streaks", {})
                
                print(f"    ✅ Success: Player {player_id} streaks")
                print(f"    Current hit streak: {streaks.get('current_hit_streak', 0)}")
                print(f"    Longest hit streak: {streaks.get('longest_hit_streak_in_period', 0)}")
                print(f"    Multi-hit games: {streaks.get('multi_hit_frequency', 'N/A')}")
                
                tests.append({"tool": "getMLBPlayerStreaks", "success": True})
            else:
                print(f"    ❌ Failed: Player {player_id} not found in results")
                tests.append({"tool": "getMLBPlayerStreaks", "success": False, "error": "Player not found"})
        else:
            error = result3.get("error", "Unknown error") if result3 else "No response"
            print(f"    ❌ Failed: {error}")
            tests.append({"tool": "getMLBPlayerStreaks", "success": False, "error": error})
        
        # Test 4: Team Scoring Trends
        print("\n[4] Testing getMLBTeamScoringTrends")
        result4 = await self.call_mcp_tool("getMLBTeamScoringTrends", {"team_id": team_id})
        
        if result4 and result4.get("ok"):
            data = result4.get("data", {})
            trends = data.get("trends", {})
            team_name = data.get("team_name", "Unknown")
            
            print(f"    ✅ Success: {team_name} scoring trends")
            print(f"    Runs per game: {trends.get('runs_per_game', 'N/A')}")
            print(f"    Runs allowed per game: {trends.get('runs_allowed_per_game', 'N/A')}")
            print(f"    Run differential: {trends.get('run_differential', 'N/A')}")
            
            tests.append({"tool": "getMLBTeamScoringTrends", "success": True})
        else:
            error = result4.get("error", "Unknown error") if result4 else "No response"
            print(f"    ❌ Failed: {error}")
            tests.append({"tool": "getMLBTeamScoringTrends", "success": False, "error": error})
        
        return tests
    
    async def save_results(self, tool_name: str, test_results: List[Dict[str, Any]]):
        """Save individual test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\mlb\\testing\\{tool_name}_test_{timestamp}.json"
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "tool_tested": tool_name,
            "server_url": self.server_url,
            "tests": test_results,
            "summary": {
                "total_tests": len(test_results),
                "successful_tests": sum(1 for t in test_results if t.get("success", False)),
                "failed_tests": sum(1 for t in test_results if not t.get("success", False))
            }
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
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
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(description="Individual MLB MCP Tool Tests")
    parser.add_argument("--tool", choices=["schedule", "teams", "roster", "player-stats", "advanced", "all"], 
                       default="all", help="Tool to test")
    parser.add_argument("--date", help="Date for schedule test (YYYY-MM-DD)")
    parser.add_argument("--season", type=int, help="Season for teams test")
    parser.add_argument("--team-id", type=int, help="Team ID for roster test")
    parser.add_argument("--player-id", type=int, help="Player ID for player stats test")
    parser.add_argument("--pitcher-mode", action="store_true", help="Test pitcher stats instead of hitting")
    
    args = parser.parse_args()
    
    tester = IndividualToolTester()
    
    try:
        if args.tool == "schedule" or args.tool == "all":
            results = await tester.test_schedule_tool(args.date)
            await tester.save_results("schedule", results)
        
        if args.tool == "teams" or args.tool == "all":
            results = await tester.test_teams_tool(args.season)
            await tester.save_results("teams", results)
        
        if args.tool == "roster" or args.tool == "all":
            results = await tester.test_roster_tool(args.team_id)
            await tester.save_results("roster", results)
        
        if args.tool == "player-stats" or args.tool == "all":
            results = await tester.test_player_stats_tool(args.player_id, args.pitcher_mode)
            await tester.save_results("player_stats", results)
        
        if args.tool == "advanced" or args.tool == "all":
            results = await tester.test_advanced_tools()
            await tester.save_results("advanced_tools", results)
        
        print("\n✅ Individual tool testing completed!")
        
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())