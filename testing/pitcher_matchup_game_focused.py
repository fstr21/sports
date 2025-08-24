#!/usr/bin/env python3
"""
Pitcher Matchup Test Script - Game-Specific Pitcher Analysis

This script focuses on game-specific pitcher data including:
- Starting pitcher identification for scheduled games
- Head-to-head pitcher matchups
- Recent performance vs specific opponents
- Game context and pitcher history

Usage: python pitcher_matchup_game_focused.py
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import httpx

# Configuration
MLB_MCP_URL = "https://mlbmcp-production.up.railway.app/mcp"
OUTPUT_DIR = "pitcher_research_results"
TARGET_SEASON = 2025

class PitcherMatchupAnalyzer:
    """Game-focused pitcher matchup analyzer"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.matchup_data = {
            "timestamp": datetime.now().isoformat(),
            "season": TARGET_SEASON,
            "games_analyzed": {},
            "pitcher_matchups": {},
            "performance_comparisons": {},
            "game_context": {}
        }
        
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Call MLB MCP tool with error handling"""
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
    
    async def get_todays_games(self, date_offset: int = 0) -> List[Dict[str, Any]]:
        """Get MLB games for a specific date"""
        target_date = datetime.now() + timedelta(days=date_offset)
        date_str = target_date.strftime("%Y-%m-%d")
        
        print(f"🗓️  Getting games for {date_str}...")
        
        result = await self.call_mcp_tool("getMLBScheduleET", {"date": date_str})
        
        if not result or not result.get("ok"):
            print(f"❌ Failed to get schedule for {date_str}")
            return []
        
        data = result.get("data", {})
        games = data.get("games", [])
        
        print(f"✅ Found {len(games)} games on {date_str}")
        
        self.matchup_data["games_analyzed"][date_str] = {
            "date": date_str,
            "game_count": len(games),
            "games": games
        }
        
        return games
    
    async def get_team_roster(self, team_id: int) -> Dict[str, Any]:
        """Get team roster focusing on pitchers"""
        result = await self.call_mcp_tool("getMLBTeamRoster", {
            "teamId": team_id,
            "season": TARGET_SEASON
        })
        
        if not result or not result.get("ok"):
            return {}
        
        data = result.get("data", {})
        players = data.get("players", [])
        
        # Filter to pitchers
        pitchers = [p for p in players if p.get("position", "").find("P") != -1]
        
        return {
            "team_id": team_id,
            "total_players": len(players),
            "pitchers": pitchers,
            "starting_pitchers": [p for p in pitchers if p.get("position") == "P"],  # Likely starters
            "relief_pitchers": [p for p in pitchers if p.get("position") != "P"]     # Likely relievers
        }
    
    async def analyze_pitcher_vs_opponent(self, pitcher_id: int, opponent_team_id: int, pitcher_name: str = "Unknown") -> Dict[str, Any]:
        """Analyze pitcher's recent performance, especially vs specific opponent"""
        print(f"🥎 Analyzing {pitcher_name} (ID: {pitcher_id}) vs Team {opponent_team_id}...")
        
        # Get general pitcher analysis
        result = await self.call_mcp_tool("getMLBPitcherMatchup", {
            "pitcher_id": pitcher_id,
            "season": TARGET_SEASON,
            "count": 10  # Get more starts to find opponent matchups
        })
        
        if not result or not result.get("ok"):
            print(f"❌ Failed to get analysis for {pitcher_name}")
            return {}
        
        data = result.get("data", {})
        recent_starts = data.get("recent_starts", [])
        aggregates = data.get("aggregates", {})
        
        # Filter starts vs specific opponent
        vs_opponent_starts = [
            start for start in recent_starts 
            if start.get("opponent_team_id") == opponent_team_id
        ]
        
        # Calculate vs opponent stats
        vs_opponent_stats = {}
        if vs_opponent_starts:
            total_ip = sum(float(start.get("innings_pitched", 0)) for start in vs_opponent_starts)
            total_er = sum(start.get("earned_runs", 0) for start in vs_opponent_starts)
            total_k = sum(start.get("strikeouts", 0) for start in vs_opponent_starts)
            total_bb = sum(start.get("walks", 0) for start in vs_opponent_starts)
            total_h = sum(start.get("hits_allowed", 0) for start in vs_opponent_starts)
            
            if total_ip > 0:
                vs_opponent_stats = {
                    "games": len(vs_opponent_starts),
                    "innings_pitched": total_ip,
                    "era": (total_er * 9) / total_ip,
                    "whip": (total_bb + total_h) / total_ip,
                    "k_per_9": (total_k * 9) / total_ip,
                    "strikeouts": total_k,
                    "walks": total_bb,
                    "hits_allowed": total_h
                }
        
        analysis = {
            "pitcher_id": pitcher_id,
            "pitcher_name": pitcher_name,
            "opponent_team_id": opponent_team_id,
            "all_recent_starts": recent_starts,
            "overall_aggregates": aggregates,
            "vs_opponent_starts": vs_opponent_starts,
            "vs_opponent_stats": vs_opponent_stats,
            "head_to_head_games": len(vs_opponent_starts)
        }
        
        return analysis
    
    async def analyze_game_pitcher_matchup(self, game: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze pitcher matchup for a specific game"""
        home_team = game.get("home", {})
        away_team = game.get("away", {})
        game_pk = game.get("gamePk")
        
        home_team_id = home_team.get("teamId")
        away_team_id = away_team.get("teamId")
        home_name = home_team.get("name", "Unknown")
        away_name = away_team.get("name", "Unknown")
        
        print(f"\n🏟️  GAME MATCHUP: {away_name} @ {home_name}")
        print(f"📝 Game ID: {game_pk}")
        
        matchup_analysis = {
            "game_info": game,
            "home_team_pitchers": {},
            "away_team_pitchers": {},
            "potential_matchups": [],
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Get pitching staffs
        print(f"🔍 Getting {home_name} pitchers...")
        home_roster = await self.get_team_roster(home_team_id)
        matchup_analysis["home_team_pitchers"] = home_roster
        
        print(f"🔍 Getting {away_name} pitchers...")
        away_roster = await self.get_team_roster(away_team_id)
        matchup_analysis["away_team_pitchers"] = away_roster
        
        # Analyze top pitchers from each team
        home_pitchers = home_roster.get("starting_pitchers", [])[:3]  # Top 3 potential starters
        away_pitchers = away_roster.get("starting_pitchers", [])[:3]  # Top 3 potential starters
        
        print(f"📊 Analyzing potential pitcher matchups...")
        
        for home_pitcher in home_pitchers:
            home_pitcher_id = home_pitcher.get("playerId")
            home_pitcher_name = home_pitcher.get("fullName", "Unknown")
            
            # Analyze home pitcher vs away team
            home_analysis = await self.analyze_pitcher_vs_opponent(
                home_pitcher_id, away_team_id, home_pitcher_name
            )
            
            matchup_analysis["potential_matchups"].append({
                "home_pitcher": home_analysis,
                "type": "home_vs_away_team"
            })
            
            await asyncio.sleep(1)  # Rate limiting
        
        for away_pitcher in away_pitchers:
            away_pitcher_id = away_pitcher.get("playerId")
            away_pitcher_name = away_pitcher.get("fullName", "Unknown")
            
            # Analyze away pitcher vs home team
            away_analysis = await self.analyze_pitcher_vs_opponent(
                away_pitcher_id, home_team_id, away_pitcher_name
            )
            
            matchup_analysis["potential_matchups"].append({
                "away_pitcher": away_analysis,
                "type": "away_vs_home_team"
            })
            
            await asyncio.sleep(1)  # Rate limiting
        
        self.matchup_data["pitcher_matchups"][game_pk] = matchup_analysis
        
        return matchup_analysis
    
    def generate_matchup_summary(self, matchup: Dict[str, Any]) -> str:
        """Generate readable summary of pitcher matchup analysis"""
        game_info = matchup.get("game_info", {})
        home_team = game_info.get("home", {}).get("name", "Home")
        away_team = game_info.get("away", {}).get("name", "Away")
        
        summary = f"\n🎯 PITCHER MATCHUP SUMMARY: {away_team} @ {home_team}\n"
        summary += "=" * 60 + "\n"
        
        # Home team pitchers
        home_pitchers = matchup.get("home_team_pitchers", {})
        summary += f"🏠 {home_team} Pitchers: {len(home_pitchers.get('pitchers', []))}\n"
        summary += f"   Starting Pitchers: {len(home_pitchers.get('starting_pitchers', []))}\n"
        summary += f"   Relief Pitchers: {len(home_pitchers.get('relief_pitchers', []))}\n"
        
        # Away team pitchers
        away_pitchers = matchup.get("away_team_pitchers", {})
        summary += f"✈️  {away_team} Pitchers: {len(away_pitchers.get('pitchers', []))}\n"
        summary += f"   Starting Pitchers: {len(away_pitchers.get('starting_pitchers', []))}\n"
        summary += f"   Relief Pitchers: {len(away_pitchers.get('relief_pitchers', []))}\n\n"
        
        # Potential matchups
        potential_matchups = matchup.get("potential_matchups", [])
        summary += f"📈 Analyzed Matchups: {len(potential_matchups)}\n"
        
        for i, matchup_data in enumerate(potential_matchups[:4], 1):  # Show top 4
            if "home_pitcher" in matchup_data:
                analysis = matchup_data["home_pitcher"]
                pitcher_name = analysis.get("pitcher_name", "Unknown")
                vs_stats = analysis.get("vs_opponent_stats", {})
                overall_stats = analysis.get("overall_aggregates", {})
                
                summary += f"  {i}. {pitcher_name} (vs {away_team})\n"
                if vs_stats:
                    summary += f"     Head-to-head: {vs_stats.get('games', 0)} games, ERA {vs_stats.get('era', 0):.2f}\n"
                else:
                    summary += f"     No recent head-to-head data\n"
                summary += f"     Overall: ERA {overall_stats.get('era', 0):.2f}, WHIP {overall_stats.get('whip', 0):.3f}\n"
            
            elif "away_pitcher" in matchup_data:
                analysis = matchup_data["away_pitcher"]
                pitcher_name = analysis.get("pitcher_name", "Unknown")
                vs_stats = analysis.get("vs_opponent_stats", {})
                overall_stats = analysis.get("overall_aggregates", {})
                
                summary += f"  {i}. {pitcher_name} (vs {home_team})\n"
                if vs_stats:
                    summary += f"     Head-to-head: {vs_stats.get('games', 0)} games, ERA {vs_stats.get('era', 0):.2f}\n"
                else:
                    summary += f"     No recent head-to-head data\n"
                summary += f"     Overall: ERA {overall_stats.get('era', 0):.2f}, WHIP {overall_stats.get('whip', 0):.3f}\n"
        
        return summary
    
    def save_results(self):
        """Save results to timestamped JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{OUTPUT_DIR}/pitcher_matchup_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.matchup_data, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        return filename
    
    async def run_matchup_analysis(self, days_ahead: int = 0):
        """Run pitcher matchup analysis for games"""
        print("🥎 MLB PITCHER MATCHUP ANALYZER")
        print("=" * 80)
        print(f"🔗 Server: {MLB_MCP_URL}")
        print(f"📅 Season: {TARGET_SEASON}")
        print("=" * 80)
        
        try:
            # Get games for target date
            games = await self.get_todays_games(days_ahead)
            
            if not games:
                print("❌ No games found for analysis")
                return
            
            # Analyze first 2 games to avoid overwhelming the API
            sample_games = games[:2]
            print(f"\n📊 Analyzing {len(sample_games)} games (sample)...")
            
            for game in sample_games:
                try:
                    matchup = await self.analyze_game_pitcher_matchup(game)
                    
                    # Display summary
                    summary = self.generate_matchup_summary(matchup)
                    print(summary)
                    
                except Exception as e:
                    print(f"❌ Error analyzing game: {e}")
            
            # Save results
            filename = self.save_results()
            print(f"\n🎉 ANALYSIS COMPLETE! Results saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
        finally:
            await self.client.aclose()

async def main():
    """Main execution"""
    analyzer = PitcherMatchupAnalyzer()
    await analyzer.run_matchup_analysis(days_ahead=0)  # Today's games

if __name__ == "__main__":
    asyncio.run(main())