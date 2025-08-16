#!/usr/bin/env python3
"""
Soccer MCP Comprehensive Testing Script

This script tests all Soccer MCP server functionality by testing each tool
with real data and providing detailed analysis with JSON output capabilities.

Server: https://soccermcp-production.up.railway.app/mcp
Tools: 7 soccer-focused tools for betting intelligence
"""

import asyncio
import json
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os

class SoccerMCPTester:
    def __init__(self):
        self.server_url = "https://soccermcp-production.up.railway.app/mcp"
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "test_name": "Soccer MCP Comprehensive Test",
            "server_url": self.server_url,
            "tools_tested": [],
            "summary": {}
        }
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool and return result"""
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
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

    async def test_competitions(self):
        """Test getCompetitions tool"""
        print("--- Step 1: Testing Competitions Discovery ---")
        
        result = await self.call_mcp_tool("getCompetitions", {})
        
        test_data = {
            "tool_name": "getCompetitions",
            "status": "FAILED",
            "competitions_found": 0,
            "major_leagues": [],
            "international_competitions": [],
            "error": None
        }
        
        if "result" in result and result["result"].get("ok"):
            competitions = result["result"]["data"]["competitions"]
            test_data["status"] = "SUCCESS"
            test_data["competitions_found"] = len(competitions)
            
            # Identify major leagues
            major_leagues = ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"]
            found_leagues = []
            
            # Identify international competitions
            international_comps = ["UEFA Champions League", "UEFA Europa League", "European Championship"]
            found_international = []
            
            for comp in competitions:
                comp_name = comp["name"]
                if any(league in comp_name for league in major_leagues):
                    found_leagues.append({
                        "name": comp_name,
                        "id": comp["id"],
                        "code": comp["code"],
                        "country": comp["area"]["name"]
                    })
                
                if any(intl in comp_name for intl in international_comps):
                    found_international.append({
                        "name": comp_name,
                        "id": comp["id"],
                        "code": comp["code"]
                    })
            
            test_data["major_leagues"] = found_leagues
            test_data["international_competitions"] = found_international
            
            print(f"[+] Found {len(competitions)} competitions")
            print(f"[+] Major leagues found: {len(found_leagues)}")
            for league in found_leagues:
                print(f"    • {league['name']} (ID: {league['id']}, {league['country']})")
            
            print(f"[+] International competitions: {len(found_international)}")
            for comp in found_international:
                print(f"    • {comp['name']} (ID: {comp['id']})")
        else:
            error_msg = result.get("result", {}).get("error", result.get("error", "Unknown error"))
            test_data["error"] = error_msg
            print(f"[-] Competitions test failed: {error_msg}")
        
        self.test_results["tools_tested"].append(test_data)
        return test_data

    async def test_premier_league_standings(self):
        """Test getCompetitionStandings with Premier League"""
        print("\n--- Step 2: Testing Premier League Standings ---")
        
        result = await self.call_mcp_tool("getCompetitionStandings", {
            "competition_id": "2021"  # Premier League
        })
        
        test_data = {
            "tool_name": "getCompetitionStandings",
            "competition": "Premier League",
            "competition_id": "2021",
            "status": "FAILED",
            "teams_found": 0,
            "top_3_teams": [],
            "bottom_3_teams": [],
            "league_stats": {},
            "error": None
        }
        
        if "result" in result and result["result"].get("ok"):
            standings_data = result["result"]["data"]["standings"]
            
            if "standings" in standings_data and standings_data["standings"]:
                table = standings_data["standings"][0]["table"]
                test_data["status"] = "SUCCESS"
                test_data["teams_found"] = len(table)
                
                # Get top 3 teams
                top_3 = table[:3]
                test_data["top_3_teams"] = []
                
                for i, team in enumerate(top_3, 1):
                    team_data = {
                        "position": i,
                        "name": team["team"]["name"],
                        "points": team["points"],
                        "played": team["playedGames"],
                        "won": team["won"],
                        "drawn": team["draw"],
                        "lost": team["lost"],
                        "goals_for": team["goalsFor"],
                        "goals_against": team["goalsAgainst"],
                        "goal_difference": team["goalDifference"]
                    }
                    test_data["top_3_teams"].append(team_data)
                
                # Get bottom 3 teams
                bottom_3 = table[-3:]
                test_data["bottom_3_teams"] = []
                
                for team in bottom_3:
                    team_data = {
                        "position": team["position"],
                        "name": team["team"]["name"],
                        "points": team["points"],
                        "played": team["playedGames"]
                    }
                    test_data["bottom_3_teams"].append(team_data)
                
                # Calculate league statistics
                total_games = sum(team["playedGames"] for team in table)
                total_goals = sum(team["goalsFor"] for team in table)
                avg_goals_per_game = (total_goals / total_games) if total_games > 0 else 0
                
                test_data["league_stats"] = {
                    "total_games_played": total_games,
                    "total_goals_scored": total_goals,
                    "average_goals_per_game": round(avg_goals_per_game, 2)
                }
                
                print(f"[+] Premier League table retrieved: {len(table)} teams")
                print("Top 3 teams:")
                for team_data in test_data["top_3_teams"]:
                    name = team_data["name"]
                    points = team_data["points"]
                    played = team_data["played"]
                    gf = team_data["goals_for"]
                    ga = team_data["goals_against"]
                    gd = team_data["goal_difference"]
                    print(f"  {team_data['position']}. {name} - {points} pts ({played} games, GF:{gf} GA:{ga} GD:{gd:+d})")
                
                print(f"League stats: {total_goals} goals in {total_games} games ({avg_goals_per_game:.2f} per game)")
            else:
                test_data["error"] = "No standings data in response"
                print("[-] No standings data found in response")
        else:
            error_msg = result.get("result", {}).get("error", result.get("error", "Unknown error"))
            test_data["error"] = error_msg
            print(f"[-] Standings test failed: {error_msg}")
        
        self.test_results["tools_tested"].append(test_data)
        return test_data

    async def test_recent_matches(self):
        """Test getCompetitionMatches with recent Premier League matches"""
        print("\n--- Step 3: Testing Recent Matches ---")
        
        # Get matches from last 2 weeks
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
        
        result = await self.call_mcp_tool("getCompetitionMatches", {
            "competition_id": "2021",
            "date_from": start_date,
            "date_to": end_date,
            "status": "FINISHED"
        })
        
        test_data = {
            "tool_name": "getCompetitionMatches",
            "competition": "Premier League",
            "date_range": f"{start_date} to {end_date}",
            "status": "FAILED",
            "matches_found": 0,
            "sample_matches": [],
            "goal_analysis": {},
            "error": None
        }
        
        if "result" in result and result["result"].get("ok"):
            matches = result["result"]["data"]["matches"]
            test_data["status"] = "SUCCESS"
            test_data["matches_found"] = len(matches)
            
            # Analyze matches
            total_goals = []
            high_scoring_games = 0
            both_teams_scored = 0
            sample_matches = []
            
            for match in matches[:5]:  # Sample first 5 matches
                home_team = match["homeTeam"]["name"]
                away_team = match["awayTeam"]["name"]
                match_date = match["utcDate"][:10]
                score = match.get("score", {}).get("fullTime", {})
                
                match_data = {
                    "date": match_date,
                    "home_team": home_team,
                    "away_team": away_team,
                    "score": None,
                    "total_goals": 0,
                    "winner": None
                }
                
                if score and score.get("home") is not None:
                    home_goals = score["home"]
                    away_goals = score["away"]
                    total = home_goals + away_goals
                    
                    match_data["score"] = f"{home_goals}-{away_goals}"
                    match_data["total_goals"] = total
                    
                    if home_goals > away_goals:
                        match_data["winner"] = "HOME"
                    elif away_goals > home_goals:
                        match_data["winner"] = "AWAY"
                    else:
                        match_data["winner"] = "DRAW"
                    
                    total_goals.append(total)
                    
                    if total >= 3:
                        high_scoring_games += 1
                    if home_goals > 0 and away_goals > 0:
                        both_teams_scored += 1
                
                sample_matches.append(match_data)
            
            test_data["sample_matches"] = sample_matches
            
            # Calculate goal statistics
            if total_goals:
                avg_goals = sum(total_goals) / len(total_goals)
                high_scoring_rate = (high_scoring_games / len(total_goals)) * 100
                btts_rate = (both_teams_scored / len(total_goals)) * 100
                
                test_data["goal_analysis"] = {
                    "total_matches_analyzed": len(total_goals),
                    "average_goals_per_game": round(avg_goals, 2),
                    "high_scoring_games_3plus": high_scoring_games,
                    "high_scoring_percentage": round(high_scoring_rate, 1),
                    "both_teams_scored": both_teams_scored,
                    "btts_percentage": round(btts_rate, 1)
                }
            
            print(f"[+] Found {len(matches)} recent matches")
            print("Sample matches:")
            for match_data in sample_matches:
                if match_data["score"]:
                    print(f"  {match_data['date']}: {match_data['home_team']} {match_data['score']} {match_data['away_team']} ({match_data['winner']})")
                else:
                    print(f"  {match_data['date']}: {match_data['home_team']} vs {match_data['away_team']} (No score)")
            
            if total_goals:
                analysis = test_data["goal_analysis"]
                print(f"Goal analysis: {analysis['average_goals_per_game']} avg, {analysis['high_scoring_percentage']}% high-scoring, {analysis['btts_percentage']}% BTTS")
        else:
            error_msg = result.get("result", {}).get("error", result.get("error", "Unknown error"))
            test_data["error"] = error_msg
            print(f"[-] Recent matches test failed: {error_msg}")
        
        self.test_results["tools_tested"].append(test_data)
        return test_data

    async def test_top_scorers(self):
        """Test getTopScorers with Premier League"""
        print("\n--- Step 4: Testing Top Scorers ---")
        
        result = await self.call_mcp_tool("getTopScorers", {
            "competition_id": "2021",
            "limit": 10
        })
        
        test_data = {
            "tool_name": "getTopScorers",
            "competition": "Premier League",
            "status": "FAILED",
            "scorers_found": 0,
            "top_scorers": [],
            "position_analysis": {},
            "team_analysis": {},
            "error": None
        }
        
        if "result" in result and result["result"].get("ok"):
            scorers = result["result"]["data"]["scorers"]
            test_data["status"] = "SUCCESS"
            test_data["scorers_found"] = len(scorers)
            
            # Process top scorers
            top_scorers = []
            positions = {}
            teams = {}
            
            for i, scorer in enumerate(scorers, 1):
                player_name = scorer["player"]["name"]
                team_name = scorer["team"]["name"]
                team_short = scorer["team"]["shortName"]
                goals = scorer["goals"]
                position = scorer["player"]["position"]
                nationality = scorer["player"]["nationality"]
                
                scorer_data = {
                    "rank": i,
                    "name": player_name,
                    "team": team_name,
                    "team_short": team_short,
                    "goals": goals,
                    "position": position,
                    "nationality": nationality
                }
                top_scorers.append(scorer_data)
                
                # Position analysis
                if position not in positions:
                    positions[position] = {"count": 0, "total_goals": 0}
                positions[position]["count"] += 1
                positions[position]["total_goals"] += goals
                
                # Team analysis
                if team_short not in teams:
                    teams[team_short] = {"players": 0, "total_goals": 0}
                teams[team_short]["players"] += 1
                teams[team_short]["total_goals"] += goals
            
            test_data["top_scorers"] = top_scorers
            test_data["position_analysis"] = positions
            test_data["team_analysis"] = teams
            
            print(f"[+] Found {len(scorers)} top scorers")
            print("Top 5 scorers:")
            for scorer_data in top_scorers[:5]:
                name = scorer_data["name"]
                team = scorer_data["team_short"]
                goals = scorer_data["goals"]
                position = scorer_data["position"]
                nationality = scorer_data["nationality"]
                print(f"  {scorer_data['rank']}. {name} ({team}) - {goals} goals, {position}, {nationality}")
            
            # Position breakdown
            print("Goals by position:")
            for pos, data in positions.items():
                avg_goals = data["total_goals"] / data["count"] if data["count"] > 0 else 0
                print(f"  {pos}: {data['count']} players, {data['total_goals']} goals ({avg_goals:.1f} avg)")
        else:
            error_msg = result.get("result", {}).get("error", result.get("error", "Unknown error"))
            test_data["error"] = error_msg
            print(f"[-] Top scorers test failed: {error_msg}")
        
        self.test_results["tools_tested"].append(test_data)
        return test_data

    async def test_team_matches(self):
        """Test getTeamMatches with Liverpool"""
        print("\n--- Step 5: Testing Team-Specific Matches ---")
        
        # Liverpool FC ID: 64
        result = await self.call_mcp_tool("getTeamMatches", {
            "team_id": 64,
            "limit": 5
        })
        
        test_data = {
            "tool_name": "getTeamMatches",
            "team": "Liverpool FC",
            "team_id": 64,
            "status": "FAILED",
            "matches_found": 0,
            "recent_matches": [],
            "performance_summary": {},
            "error": None
        }
        
        if "result" in result and result["result"].get("ok"):
            matches = result["result"]["data"]["matches"]
            test_data["status"] = "SUCCESS"
            test_data["matches_found"] = len(matches)
            
            # Process matches
            recent_matches = []
            wins = 0
            draws = 0
            losses = 0
            goals_for = 0
            goals_against = 0
            
            for match in matches:
                home_team = match["homeTeam"]["name"]
                away_team = match["awayTeam"]["name"]
                match_date = match["utcDate"][:10]
                status = match["status"]
                
                match_data = {
                    "date": match_date,
                    "opponent": away_team if home_team == "Liverpool FC" else home_team,
                    "venue": "Home" if home_team == "Liverpool FC" else "Away",
                    "status": status,
                    "score": None,
                    "result": None
                }
                
                if status == "FINISHED":
                    score = match.get("score", {}).get("fullTime", {})
                    if score and score.get("home") is not None:
                        home_goals = score["home"]
                        away_goals = score["away"]
                        
                        match_data["score"] = f"{home_goals}-{away_goals}"
                        
                        # Determine result from Liverpool's perspective
                        if home_team == "Liverpool FC":
                            liverpool_goals = home_goals
                            opponent_goals = away_goals
                        else:
                            liverpool_goals = away_goals
                            opponent_goals = home_goals
                        
                        goals_for += liverpool_goals
                        goals_against += opponent_goals
                        
                        if liverpool_goals > opponent_goals:
                            match_data["result"] = "WIN"
                            wins += 1
                        elif liverpool_goals < opponent_goals:
                            match_data["result"] = "LOSS"
                            losses += 1
                        else:
                            match_data["result"] = "DRAW"
                            draws += 1
                
                recent_matches.append(match_data)
            
            test_data["recent_matches"] = recent_matches
            
            # Performance summary
            total_finished = wins + draws + losses
            if total_finished > 0:
                win_rate = (wins / total_finished) * 100
                test_data["performance_summary"] = {
                    "games_played": total_finished,
                    "wins": wins,
                    "draws": draws,
                    "losses": losses,
                    "win_percentage": round(win_rate, 1),
                    "goals_for": goals_for,
                    "goals_against": goals_against,
                    "goal_difference": goals_for - goals_against,
                    "goals_per_game": round(goals_for / total_finished, 2) if total_finished > 0 else 0
                }
            
            print(f"[+] Found {len(matches)} Liverpool matches")
            print("Recent matches:")
            for match_data in recent_matches:
                venue = match_data["venue"]
                opponent = match_data["opponent"]
                score = match_data["score"] or "TBD"
                result = match_data["result"] or match_data["status"]
                print(f"  {match_data['date']}: {venue} vs {opponent} - {score} ({result})")
            
            if total_finished > 0:
                perf = test_data["performance_summary"]
                print(f"Performance: {perf['wins']}W-{perf['draws']}D-{perf['losses']}L ({perf['win_percentage']}%), {perf['goals_per_game']} goals/game")
        else:
            error_msg = result.get("result", {}).get("error", result.get("error", "Unknown error"))
            test_data["error"] = error_msg
            print(f"[-] Team matches test failed: {error_msg}")
        
        self.test_results["tools_tested"].append(test_data)
        return test_data

    async def test_match_details(self):
        """Test getMatchDetails with a specific match"""
        print("\n--- Step 6: Testing Match Details ---")
        
        # Use Liverpool vs Bournemouth match ID: 537785
        result = await self.call_mcp_tool("getMatchDetails", {
            "match_id": 537785
        })
        
        test_data = {
            "tool_name": "getMatchDetails",
            "match_id": 537785,
            "status": "FAILED",
            "match_info": {},
            "available_data": {},
            "limitations": [],
            "error": None
        }
        
        if "result" in result and result["result"].get("ok"):
            match = result["result"]["data"]["match"]
            test_data["status"] = "SUCCESS"
            
            # Extract match information
            match_info = {
                "home_team": match["homeTeam"]["name"],
                "away_team": match["awayTeam"]["name"],
                "date": match["utcDate"][:10],
                "time": match["utcDate"][11:16],
                "status": match["status"],
                "matchday": match.get("matchday"),
                "stage": match.get("stage")
            }
            
            # Score information
            score = match.get("score", {})
            if score:
                full_time = score.get("fullTime", {})
                half_time = score.get("halfTime", {})
                
                if full_time and full_time.get("home") is not None:
                    match_info["final_score"] = f"{full_time['home']}-{full_time['away']}"
                    match_info["total_goals"] = full_time["home"] + full_time["away"]
                
                if half_time and half_time.get("home") is not None:
                    match_info["halftime_score"] = f"{half_time['home']}-{half_time['away']}"
            
            # Officials
            referees = match.get("referees", [])
            if referees:
                match_info["referee"] = referees[0].get("name", "Unknown")
            
            test_data["match_info"] = match_info
            
            # Check what data is available vs limitations
            available_data = {
                "basic_info": True,
                "final_score": bool(match_info.get("final_score")),
                "halftime_score": bool(match_info.get("halftime_score")),
                "referee_info": bool(match_info.get("referee")),
                "venue_info": bool(match.get("venue")),
                "detailed_stats": bool(match.get("homeTeam", {}).get("statistics")),
                "player_stats": bool(match.get("goals")),
                "cards_bookings": bool(match.get("bookings"))
            }
            
            test_data["available_data"] = available_data
            
            # Identify limitations
            limitations = []
            if not available_data["detailed_stats"]:
                limitations.append("No detailed match statistics (shots, corners, possession)")
            if not available_data["player_stats"]:
                limitations.append("No player-level performance data")
            if not available_data["cards_bookings"]:
                limitations.append("No card/booking information")
            
            test_data["limitations"] = limitations
            
            print(f"[+] Match details retrieved successfully")
            print(f"Match: {match_info['home_team']} vs {match_info['away_team']}")
            print(f"Date: {match_info['date']} {match_info['time']} UTC")
            print(f"Status: {match_info['status']}")
            
            if match_info.get("final_score"):
                print(f"Final Score: {match_info['final_score']} ({match_info['total_goals']} goals)")
            
            if match_info.get("halftime_score"):
                print(f"Half-time: {match_info['halftime_score']}")
            
            if match_info.get("referee"):
                print(f"Referee: {match_info['referee']}")
            
            print("Data availability:")
            for data_type, available in available_data.items():
                status = "✅" if available else "❌"
                print(f"  {status} {data_type.replace('_', ' ').title()}")
            
            if limitations:
                print("Limitations (Free Tier):")
                for limitation in limitations:
                    print(f"  ⚠️  {limitation}")
        else:
            error_msg = result.get("result", {}).get("error", result.get("error", "Unknown error"))
            test_data["error"] = error_msg
            print(f"[-] Match details test failed: {error_msg}")
        
        self.test_results["tools_tested"].append(test_data)
        return test_data

    async def test_competition_teams(self):
        """Test getCompetitionTeams with Premier League"""
        print("\n--- Step 7: Testing Competition Teams ---")
        
        result = await self.call_mcp_tool("getCompetitionTeams", {
            "competition_id": "2021"
        })
        
        test_data = {
            "tool_name": "getCompetitionTeams",
            "competition": "Premier League",
            "status": "FAILED",
            "teams_found": 0,
            "sample_teams": [],
            "team_metadata": {},
            "error": None
        }
        
        if "result" in result and result["result"].get("ok"):
            teams = result["result"]["data"]["teams"]
            test_data["status"] = "SUCCESS"
            test_data["teams_found"] = len(teams)
            
            # Sample teams (first 5)
            sample_teams = []
            founded_years = []
            
            for team in teams[:5]:
                team_data = {
                    "id": team["id"],
                    "name": team["name"],
                    "short_name": team["shortName"],
                    "tla": team["tla"],
                    "founded": team.get("founded"),
                    "venue": team.get("venue"),
                    "colors": team.get("clubColors"),
                    "website": team.get("website")
                }
                sample_teams.append(team_data)
                
                if team.get("founded"):
                    founded_years.append(team["founded"])
            
            test_data["sample_teams"] = sample_teams
            
            # Team metadata analysis
            if founded_years:
                avg_founded = sum(founded_years) / len(founded_years)
                oldest_year = min(founded_years)
                newest_year = max(founded_years)
                
                test_data["team_metadata"] = {
                    "average_founded_year": round(avg_founded),
                    "oldest_club_year": oldest_year,
                    "newest_club_year": newest_year,
                    "teams_with_founding_data": len(founded_years)
                }
            
            print(f"[+] Found {len(teams)} Premier League teams")
            print("Sample teams:")
            for team_data in sample_teams:
                name = team_data["name"]
                tla = team_data["tla"]
                founded = team_data["founded"] or "Unknown"
                venue = team_data["venue"] or "Unknown"
                print(f"  {name} ({tla}) - Founded: {founded}, Venue: {venue}")
            
            if test_data["team_metadata"]:
                meta = test_data["team_metadata"]
                print(f"Team history: Average founded {meta['average_founded_year']}, oldest {meta['oldest_club_year']}, newest {meta['newest_club_year']}")
        else:
            error_msg = result.get("result", {}).get("error", result.get("error", "Unknown error"))
            test_data["error"] = error_msg
            print(f"[-] Competition teams test failed: {error_msg}")
        
        self.test_results["tools_tested"].append(test_data)
        return test_data

    def generate_summary(self):
        """Generate test summary"""
        successful_tools = [t for t in self.test_results["tools_tested"] if t["status"] == "SUCCESS"]
        failed_tools = [t for t in self.test_results["tools_tested"] if t["status"] == "FAILED"]
        
        self.test_results["summary"] = {
            "total_tools_tested": len(self.test_results["tools_tested"]),
            "successful_tools": len(successful_tools),
            "failed_tools": len(failed_tools),
            "success_rate": round((len(successful_tools) / len(self.test_results["tools_tested"])) * 100, 1) if self.test_results["tools_tested"] else 0,
            "successful_tool_names": [t["tool_name"] for t in successful_tools],
            "failed_tool_names": [t["tool_name"] for t in failed_tools]
        }

    async def run_comprehensive_test(self):
        """Run all tests"""
        print("============================================================")
        print("SOCCER MCP COMPREHENSIVE TEST")
        print("============================================================")
        print(f"Server: {self.server_url}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("============================================================")
        
        try:
            # Run all tests
            await self.test_competitions()
            await self.test_premier_league_standings()
            await self.test_recent_matches()
            await self.test_top_scorers()
            await self.test_team_matches()
            await self.test_match_details()
            await self.test_competition_teams()
            
            # Generate summary
            self.generate_summary()
            
            print("\n============================================================")
            print("TEST SUMMARY")
            print("============================================================")
            
            summary = self.test_results["summary"]
            print(f"Tools tested: {summary['total_tools_tested']}")
            print(f"Successful: {summary['successful_tools']}")
            print(f"Failed: {summary['failed_tools']}")
            print(f"Success rate: {summary['success_rate']}%")
            
            if summary["successful_tool_names"]:
                print(f"\n✅ Working tools:")
                for tool in summary["successful_tool_names"]:
                    print(f"   • {tool}")
            
            if summary["failed_tool_names"]:
                print(f"\n❌ Failed tools:")
                for tool in summary["failed_tool_names"]:
                    print(f"   • {tool}")
            
            # Save results to JSON
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"soccer_comprehensive_test_results_{timestamp}.json"
            
            # Get the directory of this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(script_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 Results saved to: {filepath}")
            
            # Overall status
            if summary["success_rate"] >= 80:
                print(f"\n🎉 OVERALL STATUS: EXCELLENT ({summary['success_rate']}% success rate)")
            elif summary["success_rate"] >= 60:
                print(f"\n✅ OVERALL STATUS: GOOD ({summary['success_rate']}% success rate)")
            else:
                print(f"\n⚠️  OVERALL STATUS: NEEDS ATTENTION ({summary['success_rate']}% success rate)")
            
        except Exception as e:
            print(f"\n❌ Test execution failed: {str(e)}")
            self.test_results["summary"] = {
                "status": "EXECUTION_FAILED",
                "error": str(e)
            }

async def main():
    """Main function"""
    async with SoccerMCPTester() as tester:
        await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())