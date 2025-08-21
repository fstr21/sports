#!/usr/bin/env python3
"""
MLB Player Streaks Tool - Detailed Player Streak Analysis

Gets detailed streak analysis for position players from teams 135 (Padres) and 137 (Giants)
including hit streaks, multi-hit games, home run streaks, and consistency patterns.

Usage:
    python player_streaks_detailed.py
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
LOOKBACK_GAMES = 20
MLB_MCP_URL = "https://mlbmcp-production.up.railway.app/mcp"

class MLBPlayerStreaksDetailer:
    """Detailed MLB player streaks analyzer"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.streaks_data = {
            "teams": TARGET_TEAMS,
            "season": TARGET_SEASON,
            "lookback_games": LOOKBACK_GAMES,
            "timestamp": datetime.now().isoformat(),
            "team_rosters": {},
            "player_streaks": {},
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
    
    def interpret_streak_quality(self, current_hit_streak: int, multi_hit_games: int, total_games: int) -> Dict[str, str]:
        """Interpret the quality of player streaks"""
        # Hit streak quality
        if current_hit_streak >= 10:
            hit_quality = "🔥 Exceptional"
        elif current_hit_streak >= 5:
            hit_quality = "🌟 Hot"
        elif current_hit_streak >= 3:
            hit_quality = "📈 Good"
        elif current_hit_streak >= 1:
            hit_quality = "✅ Active"
        else:
            hit_quality = "❄️ Cold"
        
        # Multi-hit consistency
        if total_games > 0:
            multi_hit_rate = multi_hit_games / total_games
            if multi_hit_rate >= 0.4:
                consistency = "🎯 Elite"
            elif multi_hit_rate >= 0.25:
                consistency = "💪 Strong"
            elif multi_hit_rate >= 0.15:
                consistency = "📊 Average"
            else:
                consistency = "📉 Struggling"
        else:
            consistency = "❓ Unknown"
        
        return {
            "hit_streak_quality": hit_quality,
            "consistency_rating": consistency
        }
    
    async def get_team_position_players(self, team_id: int) -> List[Dict[str, Any]]:
        """Get position players from a specific team"""
        print(f"\n🔍 Getting position players for {self.get_team_name(team_id)} (ID: {team_id})...")
        
        result = await self.call_mcp_tool("getMLBTeamRoster", {
            "teamId": team_id,
            "season": TARGET_SEASON
        })
        
        if not result or not result.get("ok"):
            print(f"❌ Failed to get roster for team {team_id}")
            return []
        
        data = result.get("data", {})
        players = data.get("players", [])
        
        # Filter to only position players (non-pitchers)
        position_players = []
        for player in players:
            position = player.get("position", "")
            if position and position != "P" and "P" not in position:
                position_players.append(player)
        
        print(f"✅ Found {len(players)} total players, {len(position_players)} position players")
        
        self.streaks_data["team_rosters"][team_id] = {
            "team_name": self.get_team_name(team_id),
            "total_players": len(players),
            "position_players": len(position_players),
            "players": position_players
        }
        
        return position_players
    
    async def get_players_streaks(self, player_ids: List[int], team_name: str) -> Dict[str, Any]:
        """Get streak analysis for multiple players"""
        if not player_ids:
            return {}
        
        print(f"\n📈 Getting streak analysis for {len(player_ids)} {team_name} players (last {LOOKBACK_GAMES} games)...")
        
        result = await self.call_mcp_tool("getMLBPlayerStreaks", {
            "player_ids": player_ids,
            "season": TARGET_SEASON,
            "lookback": LOOKBACK_GAMES
        })
        
        if not result or not result.get("ok"):
            print(f"❌ Failed to get player streaks")
            return {}
        
        data = result.get("data", {})
        results = data.get("results", {})
        errors = data.get("errors", {})
        
        print(f"✅ Successfully retrieved streaks for {len(results)} players")
        if errors:
            print(f"⚠️  Errors for {len(errors)} players")
        
        return results
    
    async def analyze_all_streaks(self):
        """Analyze player streaks for both teams"""
        print("📈 MLB PLAYER STREAKS ANALYZER")
        print("=" * 60)
        print(f"🏟️  Teams: {[self.get_team_name(tid) for tid in TARGET_TEAMS]}")
        print(f"📅 Season: {TARGET_SEASON}")
        print(f"📊 Lookback: Last {LOOKBACK_GAMES} games per player")
        print(f"🔗 Server: {MLB_MCP_URL}")
        print("=" * 60)
        
        all_player_streaks = {}
        
        # Process each team
        for team_id in TARGET_TEAMS:
            team_name = self.get_team_name(team_id)
            
            # Get position players
            position_players = await self.get_team_position_players(team_id)
            
            if not position_players:
                continue
            
            # Get player IDs (limit to first 6 position players to avoid too many API calls)
            player_ids = [p.get("playerId") for p in position_players[:6] if p.get("playerId")]
            
            if not player_ids:
                print(f"⚠️  No valid player IDs found for {team_name}")
                continue
            
            # Get streaks
            team_streaks = await self.get_players_streaks(player_ids, team_name)
            
            if team_streaks:
                all_player_streaks[team_id] = {
                    "team_name": team_name,
                    "players": team_streaks
                }
        
        if not all_player_streaks:
            print("\n❌ No player streak data retrieved")
            await self.save_results()
            return
        
        # Display and analyze streaks
        print(f"\n📈 PLAYER STREAK ANALYSIS")
        print("=" * 80)
        
        total_players = 0
        team_summaries = {}
        
        for team_id, team_data in all_player_streaks.items():
            team_name = team_data["team_name"]
            players_streaks = team_data["players"]
            
            print(f"\n🏟️  {team_name.upper()}")
            print("-" * 50)
            
            team_summary = {
                "players_analyzed": len(players_streaks),
                "active_hit_streaks": 0,
                "hot_hitters": 0,
                "cold_streaks": 0,
                "best_streaks": {},
                "team_totals": {
                    "total_hit_streaks": 0,
                    "total_multi_hits": 0,
                    "total_games_analyzed": 0
                }
            }
            
            # Get player names from roster
            roster_data = self.streaks_data["team_rosters"].get(team_id, {})
            roster_players = roster_data.get("players", [])
            player_names = {p.get("playerId"): p.get("fullName", "Unknown") for p in roster_players}
            
            best_hit_streak = 0
            best_hit_streak_player = ""
            most_multi_hits = 0
            most_multi_hits_player = ""
            
            for player_id, player_data in players_streaks.items():
                player_name = player_names.get(int(player_id), f"Player {player_id}")
                streaks = player_data.get("streaks", {})
                games_analyzed = streaks.get("games_analyzed", 0)
                
                # Display player streaks
                self.display_player_streaks(player_name, player_id, streaks)
                
                # Analyze for team summary
                current_hit_streak = streaks.get("current_hit_streak", 0)
                multi_hit_games = streaks.get("multi_hit_games", 0)
                longest_streak = streaks.get("longest_hit_streak_in_period", 0)
                
                # Track team stats
                team_summary["team_totals"]["total_hit_streaks"] += current_hit_streak
                team_summary["team_totals"]["total_multi_hits"] += multi_hit_games
                team_summary["team_totals"]["total_games_analyzed"] += games_analyzed
                
                # Count categories
                if current_hit_streak > 0:
                    team_summary["active_hit_streaks"] += 1
                
                if current_hit_streak >= 3:
                    team_summary["hot_hitters"] += 1
                elif current_hit_streak == 0:
                    team_summary["cold_streaks"] += 1
                
                # Track best performers
                if longest_streak > best_hit_streak:
                    best_hit_streak = longest_streak
                    best_hit_streak_player = player_name
                
                if multi_hit_games > most_multi_hits:
                    most_multi_hits = multi_hit_games
                    most_multi_hits_player = player_name
            
            # Store best performers
            team_summary["best_streaks"] = {
                "longest_hit_streak": {"player": best_hit_streak_player, "games": best_hit_streak},
                "most_multi_hits": {"player": most_multi_hits_player, "games": most_multi_hits}
            }
            
            team_summaries[team_id] = team_summary
            total_players += len(players_streaks)
        
        # Store streaks data
        self.streaks_data["player_streaks"] = all_player_streaks
        self.streaks_data["summary"] = {
            "total_players_analyzed": total_players,
            "teams_analyzed": len(all_player_streaks),
            "team_summaries": team_summaries
        }
        
        # Print team comparison
        print(f"\n📊 TEAM STREAK COMPARISON")
        print("=" * 40)
        
        for team_id, summary in team_summaries.items():
            team_name = self.get_team_name(team_id)
            best = summary["best_streaks"]
            
            print(f"\n🏟️  {team_name}:")
            print(f"   Players Analyzed: {summary['players_analyzed']}")
            print(f"   Active Hit Streaks: {summary['active_hit_streaks']}")
            print(f"   Hot Hitters (3+ game streaks): {summary['hot_hitters']}")
            print(f"   Cold Streaks (0 games): {summary['cold_streaks']}")
            
            if best["longest_hit_streak"]["games"] > 0:
                print(f"   Longest Streak: {best['longest_hit_streak']['player']} ({best['longest_hit_streak']['games']} games)")
            
            if best["most_multi_hits"]["games"] > 0:
                print(f"   Most Multi-Hit Games: {best['most_multi_hits']['player']} ({best['most_multi_hits']['games']} games)")
        
        await self.save_results()
    
    def display_player_streaks(self, name: str, player_id: str, streaks: Dict[str, Any]):
        """Display individual player streak analysis"""
        current_hit_streak = streaks.get("current_hit_streak", 0)
        longest_streak = streaks.get("longest_hit_streak_in_period", 0)
        multi_hit_streak = streaks.get("current_multi_hit_streak", 0)
        hr_streak = streaks.get("current_hr_streak", 0)
        multi_hit_games = streaks.get("multi_hit_games", 0)
        multi_hit_freq = streaks.get("multi_hit_frequency", "0/0")
        games_analyzed = streaks.get("games_analyzed", 0)
        
        # Get quality assessment
        quality = self.interpret_streak_quality(current_hit_streak, multi_hit_games, games_analyzed)
        
        print(f"\n    📊 {name} (ID: {player_id})")
        print(f"        Games Analyzed: {games_analyzed}")
        print(f"        Current Hit Streak: {current_hit_streak} games {quality['hit_streak_quality']}")
        print(f"        Longest Streak (period): {longest_streak} games")
        print(f"        Multi-Hit Games: {multi_hit_freq} {quality['consistency_rating']}")
        
        # Additional streak info
        if multi_hit_streak > 0:
            print(f"        Current Multi-Hit Streak: {multi_hit_streak} games 🔥")
        
        if hr_streak > 0:
            print(f"        Current HR Streak: {hr_streak} games 💥")
        
        # Performance assessment
        if current_hit_streak >= 5:
            print(f"        🌟 Hot hitter alert!")
        elif current_hit_streak == 0 and games_analyzed >= 3:
            print(f"        ❄️ Looking to break hitless streak")
        
        if games_analyzed > 0:
            multi_hit_rate = multi_hit_games / games_analyzed
            if multi_hit_rate >= 0.3:
                print(f"        🎯 Excellent multi-hit consistency ({multi_hit_rate:.1%})")
    
    async def save_results(self):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\mlb\\tools\\player_streaks_detailed_teams{'-'.join(map(str, TARGET_TEAMS))}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.streaks_data, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(filename)
            size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} bytes"
            
            print(f"\n💾 RESULTS SAVED")
            print("=" * 40)
            print(f"📁 File: {os.path.basename(filename)}")
            print(f"📊 Size: {size_str}")
            print(f"👥 Players: {self.streaks_data['summary'].get('total_players_analyzed', 0)}")
            print(f"📍 Full path: {filename}")
            
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main function"""
    streaks_detailer = MLBPlayerStreaksDetailer()
    
    try:
        await streaks_detailer.analyze_all_streaks()
    finally:
        await streaks_detailer.close()

if __name__ == "__main__":
    asyncio.run(main())