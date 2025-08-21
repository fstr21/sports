#!/usr/bin/env python3
"""
MLB Player Stats Tool - Detailed Player Game Log Data

Gets the last 10 games statistics for players from teams 135 (Padres) and 137 (Giants)
with detailed hitting statistics and aggregated performance metrics.

Usage:
    python player_stats_detailed.py
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
GAMES_COUNT = 10
MLB_MCP_URL = "https://mlbmcp-production.up.railway.app/mcp"

class MLBPlayerStatsDetailer:
    """Detailed MLB player stats retriever"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.stats_data = {
            "teams": TARGET_TEAMS,
            "season": TARGET_SEASON,
            "games_requested": GAMES_COUNT,
            "timestamp": datetime.now().isoformat(),
            "team_rosters": {},
            "player_stats": {},
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
    
    def format_batting_average(self, hits: int, at_bats: int) -> str:
        """Calculate and format batting average"""
        if at_bats == 0:
            return ".000"
        avg = hits / at_bats
        return f"{avg:.3f}"
    
    async def get_team_roster(self, team_id: int) -> List[Dict[str, Any]]:
        """Get roster for a specific team"""
        print(f"\n🔍 Getting roster for {self.get_team_name(team_id)} (ID: {team_id})...")
        
        result = await self.call_mcp_tool("getMLBTeamRoster", {
            "teamId": team_id,
            "season": TARGET_SEASON
        })
        
        if not result or not result.get("ok"):
            print(f"❌ Failed to get roster for team {team_id}")
            return []
        
        data = result.get("data", {})
        players = data.get("players", [])
        
        # Filter to only position players (non-pitchers) for hitting stats
        position_players = []
        for player in players:
            position = player.get("position", "")
            if position and position != "P" and "P" not in position:
                position_players.append(player)
        
        print(f"✅ Found {len(players)} total players, {len(position_players)} position players")
        
        self.stats_data["team_rosters"][team_id] = {
            "team_name": self.get_team_name(team_id),
            "total_players": len(players),
            "position_players": len(position_players),
            "players": position_players
        }
        
        return position_players
    
    async def get_player_stats(self, player_ids: List[int], team_name: str) -> Dict[str, Any]:
        """Get stats for multiple players"""
        if not player_ids:
            return {}
        
        print(f"\n📊 Getting last {GAMES_COUNT} games stats for {len(player_ids)} {team_name} players...")
        
        result = await self.call_mcp_tool("getMLBPlayerLastN", {
            "player_ids": player_ids,
            "season": TARGET_SEASON,
            "group": "hitting",
            "stats": ["hits", "homeRuns", "atBats", "runsBattedIn", "runs", "doubles", "triples", "walks", "strikeOuts"],
            "count": GAMES_COUNT
        })
        
        if not result or not result.get("ok"):
            print(f"❌ Failed to get player stats")
            return {}
        
        data = result.get("data", {})
        results = data.get("results", {})
        errors = data.get("errors", {})
        
        print(f"✅ Successfully retrieved stats for {len(results)} players")
        if errors:
            print(f"⚠️  Errors for {len(errors)} players")
        
        return results
    
    async def get_all_stats(self):
        """Get player stats for both teams"""
        print("📊 MLB PLAYER STATS RETRIEVER")
        print("=" * 60)
        print(f"🏟️  Teams: {[self.get_team_name(tid) for tid in TARGET_TEAMS]}")
        print(f"📅 Season: {TARGET_SEASON}")
        print(f"🎮 Games: Last {GAMES_COUNT} games")
        print(f"🔗 Server: {MLB_MCP_URL}")
        print("=" * 60)
        
        all_player_stats = {}
        
        # Process each team
        for team_id in TARGET_TEAMS:
            team_name = self.get_team_name(team_id)
            
            # Get roster
            position_players = await self.get_team_roster(team_id)
            
            if not position_players:
                continue
            
            # Get player IDs (limit to first 8 position players to avoid too many API calls)
            player_ids = [p.get("playerId") for p in position_players[:8] if p.get("playerId")]
            
            if not player_ids:
                print(f"⚠️  No valid player IDs found for {team_name}")
                continue
            
            # Get stats
            team_stats = await self.get_player_stats(player_ids, team_name)
            
            if team_stats:
                all_player_stats[team_id] = {
                    "team_name": team_name,
                    "players": team_stats
                }
        
        if not all_player_stats:
            print("\n❌ No player stats retrieved")
            await self.save_results()
            return
        
        # Display and analyze stats
        print(f"\n📈 PLAYER STATISTICS ANALYSIS")
        print("=" * 80)
        
        total_players = 0
        team_summaries = {}
        
        for team_id, team_data in all_player_stats.items():
            team_name = team_data["team_name"]
            players_stats = team_data["players"]
            
            print(f"\n🏟️  {team_name.upper()}")
            print("-" * 50)
            
            team_summary = {
                "players_analyzed": len(players_stats),
                "total_games": 0,
                "team_totals": {
                    "hits": 0, "home_runs": 0, "rbis": 0, "runs": 0,
                    "atBats": 0, "walks": 0, "strikeouts": 0
                },
                "top_performers": {}
            }
            
            # Get player names from roster
            roster_data = self.stats_data["team_rosters"].get(team_id, {})
            roster_players = roster_data.get("players", [])
            player_names = {p.get("playerId"): p.get("fullName", "Unknown") for p in roster_players}
            
            for player_id, player_data in players_stats.items():
                player_name = player_names.get(int(player_id), f"Player {player_id}")
                games = player_data.get("games", [])
                aggregates = player_data.get("aggregates", {})
                
                # Display player performance
                self.display_player_stats(player_name, player_id, games, aggregates)
                
                # Add to team totals
                team_summary["total_games"] += len(games)
                for stat in ["hits", "homeRuns", "runsBattedIn", "runs", "atBats", "walks", "strikeOuts"]:
                    stat_sum = aggregates.get(f"{stat}_sum", 0)
                    if stat == "homeRuns":
                        team_summary["team_totals"]["home_runs"] += stat_sum
                    elif stat == "runsBattedIn":
                        team_summary["team_totals"]["rbis"] += stat_sum
                    elif stat == "strikeOuts":
                        team_summary["team_totals"]["strikeouts"] += stat_sum
                    else:
                        team_summary["team_totals"][stat] += stat_sum
                
                # Track top performer stats
                avg_hits = aggregates.get("hits_avg", 0)
                if avg_hits > team_summary["top_performers"].get("hits_avg", 0):
                    team_summary["top_performers"]["hits_leader"] = player_name
                    team_summary["top_performers"]["hits_avg"] = avg_hits
                
                hr_sum = aggregates.get("homeRuns_sum", 0)
                if hr_sum > team_summary["top_performers"].get("hr_sum", 0):
                    team_summary["top_performers"]["hr_leader"] = player_name
                    team_summary["top_performers"]["hr_sum"] = hr_sum
            
            team_summaries[team_id] = team_summary
            total_players += len(players_stats)
        
        # Store stats data
        self.stats_data["player_stats"] = all_player_stats
        self.stats_data["summary"] = {
            "total_players_analyzed": total_players,
            "teams_analyzed": len(all_player_stats),
            "team_summaries": team_summaries
        }
        
        # Print overall summary
        print(f"\n📊 OVERALL SUMMARY")
        print("=" * 40)
        print(f"👥 Total Players: {total_players}")
        print(f"🏟️  Teams: {len(all_player_stats)}")
        
        for team_id, summary in team_summaries.items():
            team_name = self.get_team_name(team_id)
            totals = summary["team_totals"]
            top = summary["top_performers"]
            
            print(f"\n🏟️  {team_name}:")
            print(f"   Players: {summary['players_analyzed']}")
            print(f"   Team Totals: {totals['hits']} H, {totals['home_runs']} HR, {totals['rbis']} RBI")
            print(f"   Batting Avg: {self.format_batting_average(totals['hits'], totals['atBats'])}")
            if "hits_leader" in top:
                print(f"   Hits Leader: {top['hits_leader']} ({top['hits_avg']:.2f}/game)")
            if "hr_leader" in top:
                print(f"   HR Leader: {top['hr_leader']} ({top['hr_sum']} total)")
        
        await self.save_results()
    
    def display_player_stats(self, name: str, player_id: str, games: List[Dict], aggregates: Dict[str, Any]):
        """Display individual player statistics"""
        hits_avg = aggregates.get("hits_avg", 0)
        hr_sum = aggregates.get("homeRuns_sum", 0)
        rbi_sum = aggregates.get("runsBattedIn_sum", 0)
        runs_sum = aggregates.get("runs_sum", 0)
        ab_sum = aggregates.get("atBats_sum", 0)
        
        # Calculate batting average
        batting_avg = self.format_batting_average(aggregates.get("hits_sum", 0), ab_sum)
        
        print(f"\n    👤 {name} (ID: {player_id})")
        print(f"        Games: {len(games)} | Avg: {batting_avg} | Hits/Game: {hits_avg:.2f}")
        print(f"        Totals: {hr_sum} HR, {rbi_sum} RBI, {runs_sum} R, {ab_sum} AB")
        
        # Show last 3 games
        if games:
            print(f"        Recent games:")
            for i, game in enumerate(games[:3]):
                date = game.get("date_et", "Unknown")
                hits = game.get("hits", 0)
                hrs = game.get("homeRuns", 0)
                rbis = game.get("runsBattedIn", 0)
                abs_game = game.get("atBats", 0)
                
                print(f"          {date}: {hits}/{abs_game}, {hrs} HR, {rbis} RBI")
    
    async def save_results(self):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\mlb\\tools\\player_stats_detailed_teams{'-'.join(map(str, TARGET_TEAMS))}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.stats_data, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(filename)
            size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} bytes"
            
            print(f"\n💾 RESULTS SAVED")
            print("=" * 40)
            print(f"📁 File: {os.path.basename(filename)}")
            print(f"📊 Size: {size_str}")
            print(f"👥 Players: {self.stats_data['summary'].get('total_players_analyzed', 0)}")
            print(f"📍 Full path: {filename}")
            
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main function"""
    stats_detailer = MLBPlayerStatsDetailer()
    
    try:
        await stats_detailer.get_all_stats()
    finally:
        await stats_detailer.close()

if __name__ == "__main__":
    asyncio.run(main())