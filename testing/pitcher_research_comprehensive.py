#!/usr/bin/env python3
"""
Pitcher Research Script - Comprehensive MLB Pitcher Data Analysis

This script explores all available pitcher data from the MLB MCP server including:
- Team rosters and pitcher identification
- Detailed pitcher performance analysis 
- Recent game statistics and trends
- Aggregated metrics (ERA, WHIP, K/9)
- Pitcher matchup analysis

Usage: python pitcher_research_comprehensive.py
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx

# Configuration
MLB_MCP_URL = "https://mlbmcp-production.up.railway.app/mcp"
OUTPUT_DIR = "pitcher_research_results"
TARGET_SEASON = 2025

class PitcherResearcher:
    """Comprehensive MLB pitcher research tool"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.research_data = {
            "timestamp": datetime.now().isoformat(),
            "season": TARGET_SEASON,
            "mlb_teams": {},
            "all_pitchers": {},
            "pitcher_performance": {},
            "research_summary": {}
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
    
    async def discover_all_teams(self) -> List[Dict[str, Any]]:
        """Get all MLB teams"""
        print("🏟️  Discovering all MLB teams...")
        
        result = await self.call_mcp_tool("getMLBTeams", {"season": TARGET_SEASON})
        
        if not result or not result.get("ok"):
            print("❌ Failed to get MLB teams")
            return []
        
        data = result.get("data", {})
        teams = data.get("teams", [])
        
        print(f"✅ Found {len(teams)} MLB teams")
        
        self.research_data["mlb_teams"] = {
            "count": len(teams),
            "teams": teams
        }
        
        return teams
    
    async def discover_team_pitchers(self, team: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all pitchers from a specific team"""
        team_id = team.get("teamId")
        team_name = team.get("name", "Unknown")
        
        print(f"🔍 Getting pitchers for {team_name} (ID: {team_id})...")
        
        result = await self.call_mcp_tool("getMLBTeamRoster", {
            "teamId": team_id,
            "season": TARGET_SEASON
        })
        
        if not result or not result.get("ok"):
            print(f"❌ Failed to get roster for {team_name}")
            return []
        
        data = result.get("data", {})
        players = data.get("players", [])
        
        # Filter to only pitchers
        pitchers = []
        for player in players:
            position = player.get("position", "")
            if position and ("P" in position or position == "P"):
                pitcher_data = {
                    **player,
                    "team_id": team_id,
                    "team_name": team_name,
                    "team_abbrev": team.get("abbrev", "")
                }
                pitchers.append(pitcher_data)
        
        print(f"✅ Found {len(pitchers)} pitchers on {team_name}")
        
        # Store in all_pitchers
        for pitcher in pitchers:
            pitcher_id = pitcher.get("playerId")
            if pitcher_id:
                self.research_data["all_pitchers"][pitcher_id] = pitcher
        
        return pitchers
    
    async def analyze_pitcher_performance(self, pitcher: Dict[str, Any], sample_count: int = 5) -> Dict[str, Any]:
        """Get detailed performance analysis for a pitcher"""
        pitcher_id = pitcher.get("playerId")
        pitcher_name = pitcher.get("fullName", "Unknown")
        team_name = pitcher.get("team_name", "Unknown")
        
        print(f"🥎 Analyzing {pitcher_name} (ID: {pitcher_id}) from {team_name}...")
        
        result = await self.call_mcp_tool("getMLBPitcherMatchup", {
            "pitcher_id": pitcher_id,
            "season": TARGET_SEASON,
            "count": sample_count
        })
        
        if not result or not result.get("ok"):
            print(f"❌ Failed to get analysis for {pitcher_name}")
            return {}
        
        data = result.get("data", {})
        
        analysis = {
            "pitcher_info": pitcher,
            "recent_starts": data.get("recent_starts", []),
            "aggregates": data.get("aggregates", {}),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Store in pitcher_performance
        self.research_data["pitcher_performance"][pitcher_id] = analysis
        
        return analysis
    
    async def research_sample_pitchers_per_team(self, teams: List[Dict[str, Any]], sample_size: int = 3):
        """Research a sample of pitchers from each team"""
        print(f"\n🔬 RESEARCHING SAMPLE PITCHERS ({sample_size} per team)")
        print("=" * 80)
        
        total_pitchers_analyzed = 0
        
        for team in teams[:5]:  # Limit to first 5 teams for testing
            team_name = team.get("name", "Unknown")
            print(f"\n📊 Team: {team_name}")
            
            # Get team's pitchers
            pitchers = await self.discover_team_pitchers(team)
            
            if not pitchers:
                continue
            
            # Analyze sample pitchers
            sample_pitchers = pitchers[:sample_size]
            
            for pitcher in sample_pitchers:
                try:
                    analysis = await self.analyze_pitcher_performance(pitcher)
                    if analysis:
                        total_pitchers_analyzed += 1
                        
                        # Display key stats
                        aggregates = analysis.get("aggregates", {})
                        era = aggregates.get("era", "N/A")
                        whip = aggregates.get("whip", "N/A")
                        k9 = aggregates.get("k_per_9", "N/A")
                        
                        print(f"  ✅ {pitcher.get('fullName', 'Unknown')}: ERA {era}, WHIP {whip}, K/9 {k9}")
                    
                    # Add delay to be respectful to API
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"  ❌ Error analyzing {pitcher.get('fullName', 'Unknown')}: {e}")
        
        print(f"\n✅ Total pitchers analyzed: {total_pitchers_analyzed}")
        return total_pitchers_analyzed
    
    async def generate_research_summary(self):
        """Generate comprehensive research summary"""
        print("\n📋 GENERATING RESEARCH SUMMARY")
        print("=" * 60)
        
        # Count totals
        total_teams = len(self.research_data["mlb_teams"].get("teams", []))
        total_pitchers = len(self.research_data["all_pitchers"])
        analyzed_pitchers = len(self.research_data["pitcher_performance"])
        
        # Calculate performance stats
        performance_data = list(self.research_data["pitcher_performance"].values())
        eras = []
        whips = []
        k9s = []
        
        for perf in performance_data:
            aggregates = perf.get("aggregates", {})
            if aggregates.get("era") is not None:
                eras.append(aggregates["era"])
            if aggregates.get("whip") is not None:
                whips.append(aggregates["whip"])
            if aggregates.get("k_per_9") is not None:
                k9s.append(aggregates["k_per_9"])
        
        # Generate summary
        summary = {
            "research_completed": datetime.now().isoformat(),
            "data_coverage": {
                "total_mlb_teams": total_teams,
                "total_pitchers_discovered": total_pitchers,
                "pitchers_analyzed": analyzed_pitchers,
                "analysis_completion_rate": f"{(analyzed_pitchers/total_pitchers*100):.1f}%" if total_pitchers > 0 else "0%"
            },
            "performance_insights": {
                "era_stats": {
                    "sample_size": len(eras),
                    "average": sum(eras) / len(eras) if eras else 0,
                    "min": min(eras) if eras else 0,
                    "max": max(eras) if eras else 0
                },
                "whip_stats": {
                    "sample_size": len(whips),
                    "average": sum(whips) / len(whips) if whips else 0,
                    "min": min(whips) if whips else 0,
                    "max": max(whips) if whips else 0
                },
                "k9_stats": {
                    "sample_size": len(k9s),
                    "average": sum(k9s) / len(k9s) if k9s else 0,
                    "min": min(k9s) if k9s else 0,
                    "max": max(k9s) if k9s else 0
                }
            },
            "available_data_fields": {
                "pitcher_info": ["playerId", "fullName", "primaryNumber", "position", "status", "team_name", "team_abbrev"],
                "recent_starts": ["et_datetime", "date_et", "innings_pitched", "earned_runs", "strikeouts", "walks", "hits_allowed", "home_runs_allowed", "opponent_name", "game_era", "game_whip"],
                "aggregates": ["era", "whip", "k_per_9", "innings_pitched", "strikeouts", "walks", "hits_allowed"]
            },
            "mcp_tools_tested": [
                "getMLBTeams",
                "getMLBTeamRoster", 
                "getMLBPitcherMatchup"
            ]
        }
        
        self.research_data["research_summary"] = summary
        
        # Display summary
        print(f"📊 Teams: {total_teams}")
        print(f"🥎 Pitchers discovered: {total_pitchers}")
        print(f"📈 Pitchers analyzed: {analyzed_pitchers}")
        print(f"✅ Completion rate: {summary['data_coverage']['analysis_completion_rate']}")
        
        if eras:
            print(f"📉 Average ERA: {summary['performance_insights']['era_stats']['average']:.2f}")
            print(f"📊 Average WHIP: {summary['performance_insights']['whip_stats']['average']:.3f}")
            print(f"⚡ Average K/9: {summary['performance_insights']['k9_stats']['average']:.1f}")
    
    def save_results(self):
        """Save all research results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{OUTPUT_DIR}/pitcher_research_comprehensive_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.research_data, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        return filename
    
    async def run_comprehensive_research(self):
        """Run complete pitcher research workflow"""
        print("🥎 MLB PITCHER RESEARCH - COMPREHENSIVE ANALYSIS")
        print("=" * 80)
        print(f"🔗 Server: {MLB_MCP_URL}")
        print(f"📅 Season: {TARGET_SEASON}")
        print(f"📁 Output: {OUTPUT_DIR}/")
        print("=" * 80)
        
        try:
            # Step 1: Discover all teams
            teams = await self.discover_all_teams()
            if not teams:
                print("❌ Failed to discover teams. Aborting.")
                return
            
            # Step 2: Research sample pitchers
            await self.research_sample_pitchers_per_team(teams, sample_size=2)
            
            # Step 3: Generate summary
            await self.generate_research_summary()
            
            # Step 4: Save results
            filename = self.save_results()
            
            print(f"\n🎉 RESEARCH COMPLETE!")
            print(f"📊 View results in: {filename}")
            
        except Exception as e:
            print(f"❌ Research failed: {e}")
        finally:
            await self.client.aclose()

async def main():
    """Main research execution"""
    researcher = PitcherResearcher()
    await researcher.run_comprehensive_research()

if __name__ == "__main__":
    asyncio.run(main())