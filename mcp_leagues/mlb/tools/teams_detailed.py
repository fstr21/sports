#!/usr/bin/env python3
"""
MLB Teams Tool - Detailed Team Data

Gets all active MLB teams for the 2025 season with complete information
including names, abbreviations, leagues, divisions, and venues.

Usage:
    python teams_detailed.py
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx

# Configuration
TARGET_SEASON = 2025
MLB_MCP_URL = "https://mlbmcp-production.up.railway.app/mcp"

class MLBTeamsDetailer:
    """Detailed MLB teams retriever"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.teams_data = {
            "season": TARGET_SEASON,
            "timestamp": datetime.now().isoformat(),
            "teams": [],
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
    
    async def get_teams(self):
        """Get all MLB teams for the target season"""
        print("⚾ MLB TEAMS RETRIEVER")
        print("=" * 60)
        print(f"📅 Season: {TARGET_SEASON}")
        print(f"🔗 Server: {MLB_MCP_URL}")
        print("=" * 60)
        
        # Get teams
        print(f"\n🔍 Fetching teams for {TARGET_SEASON} season...")
        result = await self.call_mcp_tool("getMLBTeams", {"season": TARGET_SEASON})
        
        if not result or not result.get("ok"):
            print("❌ Failed to get teams data")
            return
        
        data = result.get("data", {})
        teams = data.get("teams", [])
        count = data.get("count", 0)
        season = data.get("season", TARGET_SEASON)
        
        print(f"✅ Found {count} teams for {season} season")
        
        if not teams:
            print("\n📋 No teams found")
            await self.save_results()
            return
        
        # Organize teams by league and division
        al_teams = [t for t in teams if "American" in t.get("league", "")]
        nl_teams = [t for t in teams if "National" in t.get("league", "")]
        
        # Further organize by division
        al_divisions = {}
        nl_divisions = {}
        
        for team in al_teams:
            div = team.get("division", "Unknown")
            if div not in al_divisions:
                al_divisions[div] = []
            al_divisions[div].append(team)
        
        for team in nl_teams:
            div = team.get("division", "Unknown")
            if div not in nl_divisions:
                nl_divisions[div] = []
            nl_divisions[div].append(team)
        
        # Display teams by league and division
        print(f"\n📋 TEAM DETAILS:")
        print("=" * 80)
        
        # American League
        print(f"\n🇺🇸 AMERICAN LEAGUE ({len(al_teams)} teams)")
        print("-" * 50)
        
        for division, div_teams in sorted(al_divisions.items()):
            print(f"\n📂 {division} ({len(div_teams)} teams):")
            for team in sorted(div_teams, key=lambda x: x.get("name", "")):
                self.display_team(team)
        
        # National League
        print(f"\n🌎 NATIONAL LEAGUE ({len(nl_teams)} teams)")
        print("-" * 50)
        
        for division, div_teams in sorted(nl_divisions.items()):
            print(f"\n📂 {division} ({len(div_teams)} teams):")
            for team in sorted(div_teams, key=lambda x: x.get("name", "")):
                self.display_team(team)
        
        # Store all teams in data
        for team in teams:
            team_detail = {
                "team_id": team.get("teamId"),
                "name": team.get("name"),
                "team_name": team.get("teamName"),
                "location_name": team.get("locationName"),
                "abbreviation": team.get("abbrev"),
                "league": team.get("league"),
                "division": team.get("division"),
                "venue": team.get("venue")
            }
            self.teams_data["teams"].append(team_detail)
        
        # Generate summary
        venues = list(set(team.get("venue", "Unknown") for team in teams if team.get("venue")))
        
        self.teams_data["summary"] = {
            "total_teams": count,
            "american_league": len(al_teams),
            "national_league": len(nl_teams),
            "divisions": {
                "american_league": list(al_divisions.keys()),
                "national_league": list(nl_divisions.keys())
            },
            "total_venues": len(venues),
            "sample_venues": venues[:10]  # First 10 venues
        }
        
        # Print summary
        print(f"\n📊 SUMMARY")
        print("=" * 40)
        print(f"📅 Season: {season}")
        print(f"⚾ Total Teams: {count}")
        print(f"🇺🇸 American League: {len(al_teams)} teams")
        print(f"🌎 National League: {len(nl_teams)} teams")
        
        print(f"\n📂 AL Divisions: {len(al_divisions)}")
        for div in sorted(al_divisions.keys()):
            print(f"   • {div} ({len(al_divisions[div])} teams)")
        
        print(f"\n📂 NL Divisions: {len(nl_divisions)}")
        for div in sorted(nl_divisions.keys()):
            print(f"   • {div} ({len(nl_divisions[div])} teams)")
        
        print(f"\n🏟️ Unique Venues: {len(venues)}")
        for venue in venues[:5]:
            print(f"   • {venue}")
        if len(venues) > 5:
            print(f"   ... and {len(venues) - 5} more venues")
        
        await self.save_results()
    
    def display_team(self, team: Dict[str, Any]):
        """Display a single team's information"""
        team_id = team.get("teamId", "N/A")
        name = team.get("name", "Unknown")
        team_name = team.get("teamName", "Unknown")
        location = team.get("locationName", "Unknown")
        abbrev = team.get("abbrev", "N/A")
        venue = team.get("venue", "Unknown")
        
        # Format display
        full_name = f"{location} {team_name}" if location != "Unknown" and team_name != "Unknown" else name
        
        print(f"    🏟️  {full_name}")
        print(f"        ID: {team_id} | Abbrev: {abbrev}")
        print(f"        Venue: {venue}")
        print()
    
    async def save_results(self):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\mlb\\tools\\teams_detailed_{TARGET_SEASON}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.teams_data, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(filename)
            size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} bytes"
            
            print(f"\n💾 RESULTS SAVED")
            print("=" * 40)
            print(f"📁 File: {os.path.basename(filename)}")
            print(f"📊 Size: {size_str}")
            print(f"⚾ Teams: {len(self.teams_data['teams'])}")
            print(f"📍 Full path: {filename}")
            
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main function"""
    teams_detailer = MLBTeamsDetailer()
    
    try:
        await teams_detailer.get_teams()
    finally:
        await teams_detailer.close()

if __name__ == "__main__":
    asyncio.run(main())