#!/usr/bin/env python3
"""
MLB Pitcher Matchup Tool - Detailed Pitcher Analysis

Gets detailed pitcher analysis for pitchers from teams 135 (Padres) and 137 (Giants)
including recent starts, ERA, WHIP, strikeout rates, and matchup data.

Usage:
    python pitcher_matchup_detailed.py
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
STARTS_COUNT = 5
MLB_MCP_URL = "https://mlbmcp-production.up.railway.app/mcp"

class MLBPitcherMatchupDetailer:
    """Detailed MLB pitcher matchup analyzer"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.matchup_data = {
            "teams": TARGET_TEAMS,
            "season": TARGET_SEASON,
            "starts_requested": STARTS_COUNT,
            "timestamp": datetime.now().isoformat(),
            "team_rosters": {},
            "pitcher_analysis": {},
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
    
    def format_era(self, era: float) -> str:
        """Format ERA for display"""
        if era is None:
            return "N/A"
        return f"{era:.2f}"
    
    def format_whip(self, whip: float) -> str:
        """Format WHIP for display"""
        if whip is None:
            return "N/A"
        return f"{whip:.3f}"
    
    def format_k_per_9(self, k9: float) -> str:
        """Format K/9 for display"""
        if k9 is None:
            return "N/A"
        return f"{k9:.1f}"
    
    def format_innings(self, innings) -> str:
        """Format innings pitched"""
        if innings is None:
            return "0.0"
        try:
            # Convert to float if it's a string
            if isinstance(innings, str):
                innings = float(innings)
            return f"{innings:.1f}"
        except (ValueError, TypeError):
            return str(innings) if innings is not None else "0.0"
    
    async def get_team_pitchers(self, team_id: int) -> List[Dict[str, Any]]:
        """Get pitchers from a specific team"""
        print(f"\n🔍 Getting pitchers for {self.get_team_name(team_id)} (ID: {team_id})...")
        
        result = await self.call_mcp_tool("getMLBTeamRoster", {
            "teamId": team_id,
            "season": TARGET_SEASON
        })
        
        if not result or not result.get("ok"):
            print(f"❌ Failed to get roster for team {team_id}")
            return []
        
        data = result.get("data", {})
        players = data.get("players", [])
        
        # Filter to only pitchers
        pitchers = []
        for player in players:
            position = player.get("position", "")
            if position and ("P" in position or position == "P"):
                pitchers.append(player)
        
        print(f"✅ Found {len(players)} total players, {len(pitchers)} pitchers")
        
        self.matchup_data["team_rosters"][team_id] = {
            "team_name": self.get_team_name(team_id),
            "total_players": len(players),
            "pitchers": len(pitchers),
            "pitcher_list": pitchers
        }
        
        return pitchers
    
    async def get_pitcher_analysis(self, pitcher_id: int, pitcher_name: str, team_name: str) -> Dict[str, Any]:
        """Get detailed analysis for a specific pitcher"""
        print(f"\n🥎 Analyzing {pitcher_name} (ID: {pitcher_id}) from {team_name}...")
        
        result = await self.call_mcp_tool("getMLBPitcherMatchup", {
            "pitcher_id": pitcher_id,
            "season": TARGET_SEASON,
            "count": STARTS_COUNT
        })
        
        if not result or not result.get("ok"):
            print(f"❌ Failed to get analysis for {pitcher_name}")
            return {}
        
        data = result.get("data", {})
        recent_starts = data.get("recent_starts", [])
        aggregates = data.get("aggregates", {})
        
        print(f"✅ Found {len(recent_starts)} recent starts for {pitcher_name}")
        
        return {
            "pitcher_id": pitcher_id,
            "pitcher_name": pitcher_name,
            "team_name": team_name,
            "recent_starts": recent_starts,
            "aggregates": aggregates,
            "analysis_success": True
        }
    
    async def analyze_all_pitchers(self):
        """Analyze pitchers from both teams"""
        print("🥎 MLB PITCHER MATCHUP ANALYZER")
        print("=" * 60)
        print(f"🏟️  Teams: {[self.get_team_name(tid) for tid in TARGET_TEAMS]}")
        print(f"📅 Season: {TARGET_SEASON}")
        print(f"🎯 Starts: Last {STARTS_COUNT} starts per pitcher")
        print(f"🔗 Server: {MLB_MCP_URL}")
        print("=" * 60)
        
        all_pitcher_analysis = {}
        
        # Process each team
        for team_id in TARGET_TEAMS:
            team_name = self.get_team_name(team_id)
            
            # Get pitchers
            pitchers = await self.get_team_pitchers(team_id)
            
            if not pitchers:
                continue
            
            # Analyze first 4 pitchers to avoid too many API calls
            selected_pitchers = pitchers[:4]
            team_analysis = []
            
            for pitcher in selected_pitchers:
                pitcher_id = pitcher.get("playerId")
                pitcher_name = pitcher.get("fullName", "Unknown")
                
                if not pitcher_id:
                    continue
                
                analysis = await self.get_pitcher_analysis(pitcher_id, pitcher_name, team_name)
                
                if analysis:
                    team_analysis.append(analysis)
            
            if team_analysis:
                all_pitcher_analysis[team_id] = {
                    "team_name": team_name,
                    "pitchers": team_analysis
                }
        
        if not all_pitcher_analysis:
            print("\n❌ No pitcher analysis retrieved")
            await self.save_results()
            return
        
        # Display analysis
        print(f"\n🥎 PITCHER ANALYSIS RESULTS")
        print("=" * 80)
        
        total_pitchers = 0
        team_summaries = {}
        
        for team_id, team_data in all_pitcher_analysis.items():
            team_name = team_data["team_name"]
            pitchers_analysis = team_data["pitchers"]
            
            print(f"\n🏟️  {team_name.upper()}")
            print("-" * 50)
            
            team_summary = {
                "pitchers_analyzed": len(pitchers_analysis),
                "team_averages": {
                    "era": 0, "whip": 0, "k_per_9": 0, "innings": 0
                },
                "best_pitcher": {},
                "total_starts": 0
            }
            
            era_sum = whip_sum = k9_sum = ip_sum = 0
            valid_pitchers = 0
            best_era = float('inf')
            
            for pitcher_data in pitchers_analysis:
                pitcher_name = pitcher_data["pitcher_name"]
                pitcher_id = pitcher_data["pitcher_id"]
                recent_starts = pitcher_data["recent_starts"]
                aggregates = pitcher_data["aggregates"]
                
                # Display pitcher performance
                self.display_pitcher_analysis(pitcher_name, pitcher_id, recent_starts, aggregates)
                
                # Calculate team averages
                era = aggregates.get("era", 0)
                whip = aggregates.get("whip", 0)
                k9 = aggregates.get("k_per_9", 0)
                ip = aggregates.get("innings_pitched", 0)
                
                if era > 0:  # Valid ERA
                    era_sum += era
                    whip_sum += whip
                    k9_sum += k9
                    ip_sum += ip
                    valid_pitchers += 1
                    
                    # Track best pitcher by ERA
                    if era < best_era:
                        best_era = era
                        team_summary["best_pitcher"] = {
                            "name": pitcher_name,
                            "era": era,
                            "whip": whip,
                            "k_per_9": k9
                        }
                
                team_summary["total_starts"] += len(recent_starts)
            
            # Calculate averages
            if valid_pitchers > 0:
                team_summary["team_averages"] = {
                    "era": era_sum / valid_pitchers,
                    "whip": whip_sum / valid_pitchers,
                    "k_per_9": k9_sum / valid_pitchers,
                    "innings": ip_sum
                }
            
            team_summaries[team_id] = team_summary
            total_pitchers += len(pitchers_analysis)
        
        # Store analysis data
        self.matchup_data["pitcher_analysis"] = all_pitcher_analysis
        self.matchup_data["summary"] = {
            "total_pitchers_analyzed": total_pitchers,
            "teams_analyzed": len(all_pitcher_analysis),
            "team_summaries": team_summaries
        }
        
        # Print team comparison
        print(f"\n📊 TEAM PITCHING COMPARISON")
        print("=" * 40)
        
        for team_id, summary in team_summaries.items():
            team_name = self.get_team_name(team_id)
            averages = summary["team_averages"]
            best = summary["best_pitcher"]
            
            print(f"\n🏟️  {team_name}:")
            print(f"   Pitchers Analyzed: {summary['pitchers_analyzed']}")
            print(f"   Total Starts: {summary['total_starts']}")
            print(f"   Team ERA: {self.format_era(averages['era'])}")
            print(f"   Team WHIP: {self.format_whip(averages['whip'])}")
            print(f"   Team K/9: {self.format_k_per_9(averages['k_per_9'])}")
            
            if best:
                print(f"   Best Pitcher: {best['name']} ({self.format_era(best['era'])} ERA)")
        
        await self.save_results()
    
    def display_pitcher_analysis(self, name: str, pitcher_id: int, starts: List[Dict], aggregates: Dict[str, Any]):
        """Display individual pitcher analysis"""
        era = aggregates.get("era", 0)
        whip = aggregates.get("whip", 0)
        k9 = aggregates.get("k_per_9", 0)
        innings = aggregates.get("innings_pitched", 0)
        strikeouts = aggregates.get("strikeouts", 0)
        walks = aggregates.get("walks", 0)
        
        print(f"\n    🥎 {name} (ID: {pitcher_id})")
        print(f"        Starts: {len(starts)} | IP: {self.format_innings(innings)}")
        print(f"        ERA: {self.format_era(era)} | WHIP: {self.format_whip(whip)} | K/9: {self.format_k_per_9(k9)}")
        print(f"        Totals: {strikeouts} K, {walks} BB")
        
        # Show recent starts
        if starts:
            print(f"        Recent starts:")
            for i, start in enumerate(starts[:3]):
                date = start.get("date_et", "Unknown")
                ip_game = start.get("innings_pitched", 0)
                k_game = start.get("strikeouts", 0)
                bb_game = start.get("walks", 0)
                era_game = start.get("game_era", 0)
                opponent = start.get("opponent_name", "Unknown")
                
                print(f"          {date} vs {opponent}: {self.format_innings(ip_game)} IP, {k_game} K, {bb_game} BB, {self.format_era(era_game)} ERA")
    
    async def save_results(self):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\mlb\\tools\\pitcher_matchup_detailed_teams{'-'.join(map(str, TARGET_TEAMS))}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.matchup_data, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(filename)
            size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} bytes"
            
            print(f"\n💾 RESULTS SAVED")
            print("=" * 40)
            print(f"📁 File: {os.path.basename(filename)}")
            print(f"📊 Size: {size_str}")
            print(f"🥎 Pitchers: {self.matchup_data['summary'].get('total_pitchers_analyzed', 0)}")
            print(f"📍 Full path: {filename}")
            
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main function"""
    matchup_detailer = MLBPitcherMatchupDetailer()
    
    try:
        await matchup_detailer.analyze_all_pitchers()
    finally:
        await matchup_detailer.close()

if __name__ == "__main__":
    asyncio.run(main())