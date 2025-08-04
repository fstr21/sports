#!/usr/bin/env python3
"""
ESPN API Explorer - Discover all available endpoints and data
"""

import asyncio
import json
import os
from pathlib import Path
import httpx
from datetime import datetime

# Load environment
def load_env():
    env_path = Path("C:/Users/fstr2/Desktop/sports/.env.local")
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k] = v

load_env()

ESPN_BASE = "https://site.api.espn.com"
HEADERS = {
    "User-Agent": "ESPN-API-Explorer/1.0",
    "Accept": "application/json",
}

class ESPNExplorer:
    def __init__(self):
        self.client = httpx.AsyncClient(headers=HEADERS, timeout=20.0)
        self.endpoints = {
            "scoreboard": "/apis/site/v2/sports/basketball/wnba/scoreboard",
            "teams": "/apis/site/v2/sports/basketball/wnba/teams",
            "standings": "/apis/site/v2/sports/basketball/wnba/standings",
            "injuries": "/apis/site/v2/sports/basketball/wnba/injuries",
            "news": "/apis/site/v2/sports/basketball/wnba/news",
            "schedule": "/apis/site/v2/sports/basketball/wnba/schedule",
            "athletes": "/apis/site/v2/sports/basketball/wnba/athletes",
            "stats": "/apis/site/v2/sports/basketball/wnba/statistics",
            "playoffs": "/apis/site/v2/sports/basketball/wnba/playoffs",
        }
    
    async def explore_endpoint(self, name, endpoint):
        """Explore a single endpoint and show what data is available"""
        print(f"\n🔍 **{name.upper()}** - {endpoint}")
        print("=" * 60)
        
        try:
            response = await self.client.get(f"{ESPN_BASE}{endpoint}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.analyze_structure(data, name)
            else:
                print(f"❌ Error: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
    
    def analyze_structure(self, data, endpoint_name):
        """Analyze and display the structure of the response"""
        print(f"📊 Data Structure for {endpoint_name}:")
        
        # Show top-level keys
        if isinstance(data, dict):
            print(f"  Top-level keys: {list(data.keys())}")
            
            # Specific analysis for each endpoint
            if endpoint_name == "scoreboard":
                self.analyze_scoreboard(data)
            elif endpoint_name == "teams":
                self.analyze_teams(data)
            elif endpoint_name == "standings":
                self.analyze_standings(data)
            elif endpoint_name == "injuries":
                self.analyze_injuries(data)
            elif endpoint_name == "news":
                self.analyze_news(data)
            elif endpoint_name == "athletes":
                self.analyze_athletes(data)
            elif endpoint_name == "stats":
                self.analyze_stats(data)
            else:
                self.show_sample_data(data)
    
    def analyze_scoreboard(self, data):
        """Analyze scoreboard data structure"""
        events = data.get("events", [])
        print(f"  📅 Found {len(events)} games")
        
        if events:
            sample_event = events[0]
            print(f"  🏀 Sample game data keys: {list(sample_event.keys())}")
            print(f"  📍 Game: {sample_event.get('name', 'Unknown')}")
            print(f"  📊 Status: {sample_event.get('status', {}).get('type', {}).get('description', 'Unknown')}")
            
            # Show competitor data
            competitions = sample_event.get("competitions", [])
            if competitions:
                competitors = competitions[0].get("competitors", [])
                if competitors:
                    print(f"  👥 Team data keys: {list(competitors[0].keys())}")
                    team = competitors[0].get("team", {})
                    print(f"  🏆 Sample team keys: {list(team.keys())}")
    
    def analyze_teams(self, data):
        """Analyze teams data structure"""
        sports = data.get("sports", [])
        if sports and sports[0].get("leagues"):
            teams = sports[0]["leagues"][0].get("teams", [])
            print(f"  🏆 Found {len(teams)} teams")
            
            if teams:
                sample_team = teams[0].get("team", teams[0])
                print(f"  📋 Team data keys: {list(sample_team.keys())}")
                print(f"  🏀 Sample team: {sample_team.get('displayName', 'Unknown')}")
                
                # Check for roster data
                if "athletes" in sample_team:
                    athletes = sample_team["athletes"]
                    print(f"  👥 Roster available: {len(athletes)} players")
                    if athletes:
                        print(f"  🏃 Player data keys: {list(athletes[0].keys())}")
    
    def analyze_standings(self, data):
        """Analyze standings data structure"""
        if "children" in data:
            conferences = data["children"]
            print(f"  🏆 Found {len(conferences)} conferences/divisions")
            
            for conf in conferences:
                standings = conf.get("standings", {}).get("entries", [])
                print(f"  📊 {conf.get('name', 'Unknown')}: {len(standings)} teams")
                
                if standings:
                    sample = standings[0]
                    print(f"  📈 Standing entry keys: {list(sample.keys())}")
    
    def analyze_injuries(self, data):
        """Analyze injury data structure"""
        injuries = data.get("injuries", [])
        print(f"  🏥 Found {len(injuries)} injury reports")
        
        if injuries:
            sample = injuries[0]
            print(f"  📋 Injury data keys: {list(sample.keys())}")
            athlete = sample.get("athlete", {})
            print(f"  🏃 Athlete keys: {list(athlete.keys())}")
            print(f"  👤 Sample: {athlete.get('displayName', 'Unknown')} - {sample.get('status', 'Unknown')}")
    
    def analyze_news(self, data):
        """Analyze news data structure"""
        articles = data.get("articles", [])
        print(f"  📰 Found {len(articles)} articles")
        
        if articles:
            sample = articles[0]
            print(f"  📄 Article data keys: {list(sample.keys())}")
            print(f"  📰 Sample: {sample.get('headline', 'No headline')}")
    
    def analyze_athletes(self, data):
        """Analyze athletes data structure"""
        if "athletes" in data:
            athletes = data["athletes"]
            print(f"  🏃 Found {len(athletes)} athletes")
            
            if athletes:
                sample = athletes[0]
                print(f"  👤 Athlete data keys: {list(sample.keys())}")
                print(f"  🏀 Sample: {sample.get('displayName', 'Unknown')}")
        else:
            print(f"  📋 Top-level keys: {list(data.keys())}")
    
    def analyze_stats(self, data):
        """Analyze statistics data structure"""
        print(f"  📊 Stats data keys: {list(data.keys())}")
        
        # Look for different stat categories
        for key, value in data.items():
            if isinstance(value, list) and value:
                print(f"  📈 {key}: {len(value)} entries")
                if isinstance(value[0], dict):
                    print(f"    Keys: {list(value[0].keys())}")
    
    def show_sample_data(self, data, max_depth=2, current_depth=0):
        """Show sample data structure for unknown endpoints"""
        if current_depth >= max_depth:
            return
            
        if isinstance(data, dict):
            for key, value in list(data.items())[:5]:  # Show first 5 keys
                if isinstance(value, (dict, list)):
                    if isinstance(value, list) and value:
                        print(f"  {'  ' * current_depth}📋 {key}: [{len(value)} items]")
                        if isinstance(value[0], dict):
                            print(f"  {'  ' * current_depth}   Sample keys: {list(value[0].keys())[:5]}")
                    else:
                        print(f"  {'  ' * current_depth}📁 {key}: {type(value).__name__}")
                else:
                    print(f"  {'  ' * current_depth}📄 {key}: {str(value)[:50]}")
    
    async def explore_team_details(self):
        """Explore individual team endpoints"""
        print(f"\n🔍 **TEAM DETAILS EXPLORATION**")
        print("=" * 60)
        
        # First get team list
        try:
            response = await self.client.get(f"{ESPN_BASE}/apis/site/v2/sports/basketball/wnba/teams")
            if response.status_code == 200:
                data = response.json()
                sports = data.get("sports", [])
                if sports and sports[0].get("leagues"):
                    teams = sports[0]["leagues"][0].get("teams", [])
                    
                    if teams:
                        # Test first team's detailed endpoint
                        sample_team = teams[0].get("team", teams[0])
                        team_id = sample_team.get("id")
                        team_name = sample_team.get("displayName", "Unknown")
                        
                        print(f"🏆 Testing detailed data for: {team_name} (ID: {team_id})")
                        
                        # Test team detail endpoint
                        detail_url = f"/apis/site/v2/sports/basketball/wnba/teams/{team_id}"
                        detail_response = await self.client.get(f"{ESPN_BASE}{detail_url}")
                        
                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()
                            team_detail = detail_data.get("team", {})
                            print(f"  📋 Team detail keys: {list(team_detail.keys())}")
                            
                            # Check for roster
                            if "athletes" in team_detail:
                                athletes = team_detail["athletes"]
                                print(f"  👥 Roster: {len(athletes)} players")
                                if athletes:
                                    player = athletes[0]
                                    print(f"  🏃 Player data keys: {list(player.keys())}")
                                    print(f"  👤 Sample player: {player.get('displayName', 'Unknown')}")
                        else:
                            print(f"  ❌ Team detail error: {detail_response.status_code}")
                            
        except Exception as e:
            print(f"❌ Team exploration failed: {str(e)}")
    
    async def explore_all(self):
        """Explore all endpoints"""
        print("🚀 ESPN WNBA API EXPLORER")
        print("=" * 60)
        print("This tool will show you ALL available data from ESPN's WNBA API")
        print("Use this to understand what you can ask your MCP server for!")
        
        # Explore basic endpoints
        for name, endpoint in self.endpoints.items():
            await self.explore_endpoint(name, endpoint)
            await asyncio.sleep(0.5)  # Be nice to the API
        
        # Explore team details
        await self.explore_team_details()
        
        print(f"\n🎯 **SUMMARY: What You Can Ask For**")
        print("=" * 60)
        print("Based on this exploration, you can ask your MCP server for:")
        print("📊 Game scores and schedules")
        print("🏆 Team information and rosters")  
        print("📈 League standings")
        print("🏥 Injury reports")
        print("📰 Latest news")
        print("🏃 Player information (when available)")
        print("📊 Team statistics")
        print("🏀 Playoff information")
        
        await self.client.aclose()

async def main():
    explorer = ESPNExplorer()
    await explorer.explore_all()

if __name__ == "__main__":
    asyncio.run(main())