#!/usr/bin/env python3
"""
MLB Team Scoring Trends Tool - Detailed Scoring Analysis

Gets detailed scoring trends and patterns for teams 135 (Padres) and 137 (Giants)
including runs per game, runs allowed, run differential, and offensive/defensive analysis.

Usage:
    python scoring_trends_detailed.py
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx

# Configuration
TARGET_TEAMS = [135, 137]  # Padres and Giants
TARGET_SEASON = 2025
MLB_MCP_URL = "https://mlbmcp-production.up.railway.app/mcp"

class MLBScoringTrendsDetailer:
    """Detailed MLB scoring trends analyzer"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.trends_data = {
            "teams": TARGET_TEAMS,
            "season": TARGET_SEASON,
            "timestamp": datetime.now().isoformat(),
            "team_trends": {},
            "comparison": {},
            "summary": {}
        }
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Call MLB MCP tool"""
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
            response = await self.client.post(MLB_MCP_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(f"❌ MCP Error: {result['error']}")
                return None
            
            return result.get("result", {})
            
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def get_team_name(self, team_id: int) -> str:
        """Get team name from ID"""
        team_names = {
            135: "San Diego Padres",
            137: "San Francisco Giants"
        }
        return team_names.get(team_id, f"Team {team_id}")
    
    def analyze_offensive_rating(self, runs_per_game: float) -> Dict[str, str]:
        """Analyze offensive performance rating"""
        if runs_per_game >= 5.5:
            return {"rating": "🔥 Elite", "description": "Explosive offense"}
        elif runs_per_game >= 4.8:
            return {"rating": "💪 Strong", "description": "Above average offense"}
        elif runs_per_game >= 4.2:
            return {"rating": "📊 Average", "description": "League average offense"}
        elif runs_per_game >= 3.5:
            return {"rating": "📉 Below Average", "description": "Struggling offense"}
        else:
            return {"rating": "❄️ Poor", "description": "Offensive struggles"}
    
    def analyze_defensive_rating(self, runs_allowed_per_game: float) -> Dict[str, str]:
        """Analyze defensive/pitching performance rating"""
        if runs_allowed_per_game <= 3.5:
            return {"rating": "🛡️ Elite", "description": "Lockdown pitching"}
        elif runs_allowed_per_game <= 4.0:
            return {"rating": "💪 Strong", "description": "Good pitching staff"}
        elif runs_allowed_per_game <= 4.5:
            return {"rating": "📊 Average", "description": "League average pitching"}
        elif runs_allowed_per_game <= 5.0:
            return {"rating": "📉 Below Average", "description": "Pitching concerns"}
        else:
            return {"rating": "🆘 Poor", "description": "Major pitching issues"}
    
    def analyze_run_differential(self, run_diff: float, games_played: int) -> Dict[str, str]:
        """Analyze run differential performance"""
        if games_played == 0:
            return {"rating": "❓ Unknown", "description": "No games played"}
        
        diff_per_game = run_diff / games_played
        
        if diff_per_game >= 1.5:
            return {"rating": "🏆 Dominant", "description": "Championship caliber"}
        elif diff_per_game >= 0.8:
            return {"rating": "🌟 Excellent", "description": "Playoff contender"}
        elif diff_per_game >= 0.3:
            return {"rating": "✅ Good", "description": "Above .500 team"}
        elif diff_per_game >= -0.3:
            return {"rating": "📊 Average", "description": "Around .500 team"}
        elif diff_per_game >= -0.8:
            return {"rating": "📉 Poor", "description": "Below .500 team"}
        else:
            return {"rating": "🆘 Terrible", "description": "Bottom-tier team"}
    
    async def get_team_scoring_trends(self, team_id: int) -> Dict[str, Any]:
        """Get scoring trends for a specific team"""
        team_name = self.get_team_name(team_id)
        print(f"\n🔍 Getting scoring trends for {team_name} (ID: {team_id})...")
        
        result = await self.call_mcp_tool("getMLBTeamScoringTrends", {
            "team_id": team_id,
            "season": TARGET_SEASON
        })
        
        if not result or not result.get("ok"):
            print(f"❌ Failed to get scoring trends for {team_name}")
            return {}
        
        data = result.get("data", {})
        trends = data.get("trends", {})
        team_name_from_api = data.get("team_name", team_name)
        
        print(f"✅ Retrieved scoring trends for {team_name_from_api}")
        
        # Extract trend data
        runs_per_game = trends.get("runs_per_game", 0)
        runs_allowed_per_game = trends.get("runs_allowed_per_game", 0)
        run_differential = trends.get("run_differential", 0)
        run_diff_per_game = trends.get("run_differential_per_game", 0)
        total_runs_scored = trends.get("total_runs_scored", 0)
        total_runs_allowed = trends.get("total_runs_allowed", 0)
        games_played = trends.get("games_played", 0)
        
        # Analyze performance
        offensive_analysis = self.analyze_offensive_rating(runs_per_game)
        defensive_analysis = self.analyze_defensive_rating(runs_allowed_per_game)
        differential_analysis = self.analyze_run_differential(run_differential, games_played)
        
        return {
            "team_id": team_id,
            "team_name": team_name_from_api,
            "basic_trends": {
                "runs_per_game": runs_per_game,
                "runs_allowed_per_game": runs_allowed_per_game,
                "run_differential": run_differential,
                "run_differential_per_game": run_diff_per_game,
                "games_played": games_played
            },
            "season_totals": {
                "total_runs_scored": total_runs_scored,
                "total_runs_allowed": total_runs_allowed
            },
            "performance_analysis": {
                "offense": offensive_analysis,
                "defense": defensive_analysis,
                "overall": differential_analysis
            },
            "raw_trends": trends
        }
    
    async def analyze_scoring_trends(self):
        """Analyze scoring trends for both teams"""
        print("📈 MLB TEAM SCORING TRENDS ANALYZER")
        print("=" * 60)
        print(f"🏟️  Teams: {[self.get_team_name(tid) for tid in TARGET_TEAMS]}")
        print(f"📅 Season: {TARGET_SEASON}")
        print(f"🔗 Server: {MLB_MCP_URL}")
        print("=" * 60)
        
        team_trends = {}
        
        # Get scoring trends for each team
        for team_id in TARGET_TEAMS:
            trends_data = await self.get_team_scoring_trends(team_id)
            if trends_data:
                team_trends[team_id] = trends_data
        
        if not team_trends:
            print("\n❌ No scoring trends data retrieved")
            await self.save_results()
            return
        
        # Display detailed trends analysis
        print(f"\n📊 SCORING TRENDS ANALYSIS")
        print("=" * 80)
        
        for team_id, team_data in team_trends.items():
            self.display_team_trends(team_data)
        
        # Compare teams if we have both
        if len(team_trends) == 2:
            print(f"\n⚖️  HEAD-TO-HEAD SCORING COMPARISON")
            print("=" * 50)
            self.compare_scoring_trends(list(team_trends.values()))
        
        # Store data
        self.trends_data["team_trends"] = team_trends
        
        # Generate summary
        total_runs_scored = sum(data["season_totals"]["total_runs_scored"] for data in team_trends.values())
        total_runs_allowed = sum(data["season_totals"]["total_runs_allowed"] for data in team_trends.values())
        total_games = sum(data["basic_trends"]["games_played"] for data in team_trends.values())
        
        # Find best offensive and defensive teams
        best_offense = max(team_trends.values(), key=lambda x: x["basic_trends"]["runs_per_game"])
        best_defense = min(team_trends.values(), key=lambda x: x["basic_trends"]["runs_allowed_per_game"])
        best_differential = max(team_trends.values(), key=lambda x: x["basic_trends"]["run_differential"])
        
        self.trends_data["summary"] = {
            "teams_analyzed": len(team_trends),
            "combined_stats": {
                "total_runs_scored": total_runs_scored,
                "total_runs_allowed": total_runs_allowed,
                "total_games": total_games,
                "combined_differential": total_runs_scored - total_runs_allowed
            },
            "best_performers": {
                "offense": {
                    "team": best_offense["team_name"],
                    "runs_per_game": best_offense["basic_trends"]["runs_per_game"]
                },
                "defense": {
                    "team": best_defense["team_name"],
                    "runs_allowed_per_game": best_defense["basic_trends"]["runs_allowed_per_game"]
                },
                "overall": {
                    "team": best_differential["team_name"],
                    "run_differential": best_differential["basic_trends"]["run_differential"]
                }
            }
        }
        
        # Print league comparison
        print(f"\n🏆 PERFORMANCE LEADERS")
        print("=" * 30)
        print(f"Best Offense: {best_offense['team_name']} ({best_offense['basic_trends']['runs_per_game']:.2f} R/G)")
        print(f"Best Defense: {best_defense['team_name']} ({best_defense['basic_trends']['runs_allowed_per_game']:.2f} RA/G)")
        print(f"Best Overall: {best_differential['team_name']} ({best_differential['basic_trends']['run_differential']:+d} run diff)")
        
        await self.save_results()
    
    def display_team_trends(self, team_data: Dict[str, Any]):
        """Display detailed trends for a single team"""
        team_name = team_data["team_name"]
        trends = team_data["basic_trends"]
        totals = team_data["season_totals"]
        analysis = team_data["performance_analysis"]
        
        print(f"\n🏟️  {team_name.upper()}")
        print("-" * 40)
        
        # Basic scoring stats
        print(f"📊 Scoring Averages ({trends['games_played']} games):")
        print(f"   Runs Scored: {trends['runs_per_game']:.2f} per game")
        print(f"   Runs Allowed: {trends['runs_allowed_per_game']:.2f} per game")
        print(f"   Run Differential: {trends['run_differential']:+d} ({trends['run_differential_per_game']:+.2f} per game)")
        
        # Season totals
        print(f"\n🎯 Season Totals:")
        print(f"   Total Runs Scored: {totals['total_runs_scored']}")
        print(f"   Total Runs Allowed: {totals['total_runs_allowed']}")
        
        # Performance analysis
        print(f"\n📈 Performance Analysis:")
        print(f"   Offensive Rating: {analysis['offense']['rating']}")
        print(f"   Defensive Rating: {analysis['defense']['rating']}")
        print(f"   Overall Rating: {analysis['overall']['rating']}")
        
        # Additional insights
        if trends['games_played'] > 0:
            win_projection = self.project_wins(trends['run_differential_per_game'], trends['games_played'])
            print(f"   Projected Wins: ~{win_projection} (based on run differential)")
        
        # Strengths and weaknesses
        print(f"\n💡 Analysis:")
        print(f"   {analysis['offense']['description']}")
        print(f"   {analysis['defense']['description']}")
        print(f"   {analysis['overall']['description']}")
    
    def project_wins(self, run_diff_per_game: float, games_played: int) -> int:
        """Project season wins based on run differential"""
        # Simple projection based on run differential
        # Roughly +1 run differential per game = ~62% win rate
        if run_diff_per_game >= 1.0:
            win_rate = 0.62
        elif run_diff_per_game >= 0.5:
            win_rate = 0.56
        elif run_diff_per_game >= 0:
            win_rate = 0.52
        elif run_diff_per_game >= -0.5:
            win_rate = 0.48
        elif run_diff_per_game >= -1.0:
            win_rate = 0.44
        else:
            win_rate = 0.38
        
        # Project to 162 games
        projected_wins = int(win_rate * 162)
        return projected_wins
    
    def compare_scoring_trends(self, teams: List[Dict[str, Any]]):
        """Compare scoring trends between two teams"""
        if len(teams) != 2:
            return
        
        team1, team2 = teams
        
        # Offensive comparison
        rpg1 = team1["basic_trends"]["runs_per_game"]
        rpg2 = team2["basic_trends"]["runs_per_game"]
        
        print(f"⚔️  Offensive Battle:")
        print(f"   {team1['team_name']}: {rpg1:.2f} R/G {team1['performance_analysis']['offense']['rating']}")
        print(f"   {team2['team_name']}: {rpg2:.2f} R/G {team2['performance_analysis']['offense']['rating']}")
        
        if rpg1 > rpg2:
            print(f"   🥇 {team1['team_name']} leads offense by {rpg1 - rpg2:.2f} R/G")
        elif rpg2 > rpg1:
            print(f"   🥇 {team2['team_name']} leads offense by {rpg2 - rpg1:.2f} R/G")
        else:
            print(f"   🤝 Offenses are equal")
        
        # Defensive comparison
        rapg1 = team1["basic_trends"]["runs_allowed_per_game"]
        rapg2 = team2["basic_trends"]["runs_allowed_per_game"]
        
        print(f"\n🛡️  Defensive Battle:")
        print(f"   {team1['team_name']}: {rapg1:.2f} RA/G {team1['performance_analysis']['defense']['rating']}")
        print(f"   {team2['team_name']}: {rapg2:.2f} RA/G {team2['performance_analysis']['defense']['rating']}")
        
        if rapg1 < rapg2:
            print(f"   🥇 {team1['team_name']} has better defense by {rapg2 - rapg1:.2f} RA/G")
        elif rapg2 < rapg1:
            print(f"   🥇 {team2['team_name']} has better defense by {rapg1 - rapg2:.2f} RA/G")
        else:
            print(f"   🤝 Defenses are equal")
        
        # Overall comparison
        diff1 = team1["basic_trends"]["run_differential"]
        diff2 = team2["basic_trends"]["run_differential"]
        
        print(f"\n🏆 Overall Comparison:")
        print(f"   {team1['team_name']}: {diff1:+d} run differential {team1['performance_analysis']['overall']['rating']}")
        print(f"   {team2['team_name']}: {diff2:+d} run differential {team2['performance_analysis']['overall']['rating']}")
        
        if diff1 > diff2:
            print(f"   🏆 {team1['team_name']} is superior by {diff1 - diff2} runs overall")
        elif diff2 > diff1:
            print(f"   🏆 {team2['team_name']} is superior by {diff2 - diff1} runs overall")
        else:
            print(f"   🤝 Teams are evenly matched")
        
        # Store comparison
        self.trends_data["comparison"] = {
            "team1": team1['team_name'],
            "team2": team2['team_name'],
            "offensive_leader": team1['team_name'] if rpg1 > rpg2 else team2['team_name'] if rpg2 > rpg1 else "Tied",
            "defensive_leader": team1['team_name'] if rapg1 < rapg2 else team2['team_name'] if rapg2 < rapg1 else "Tied",
            "overall_leader": team1['team_name'] if diff1 > diff2 else team2['team_name'] if diff2 > diff1 else "Tied"
        }
    
    async def save_results(self):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\mlb\\tools\\scoring_trends_detailed_teams{'-'.join(map(str, TARGET_TEAMS))}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.trends_data, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(filename)
            size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} bytes"
            
            print(f"\n💾 RESULTS SAVED")
            print("=" * 40)
            print(f"📁 File: {os.path.basename(filename)}")
            print(f"📊 Size: {size_str}")
            print(f"🏟️  Teams: {self.trends_data['summary'].get('teams_analyzed', 0)}")
            print(f"📍 Full path: {filename}")
            
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main function"""
    trends_detailer = MLBScoringTrendsDetailer()
    
    try:
        await trends_detailer.analyze_scoring_trends()
    finally:
        await trends_detailer.close()

if __name__ == "__main__":
    asyncio.run(main())