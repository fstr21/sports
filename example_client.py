#!/usr/bin/env python3
"""
Example Client for Sports HTTP Server

This shows how to use your HTTP server from any Python script,
Discord bot, web app, or other client.
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

class SportsClient:
    """Simple client for the Sports HTTP Server"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv('SPORTS_API_KEY')
        
        if not self.api_key:
            raise ValueError("API key required. Set SPORTS_API_KEY environment variable or pass api_key parameter.")
        
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a POST request to the server"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}", "success": False}
    
    def _get(self, endpoint: str) -> Dict[str, Any]:
        """Make a GET request to the server"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}", "success": False}
    
    def health_check(self) -> Dict[str, Any]:
        """Check server health (no auth required)"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Health check failed: {str(e)}", "status": "unhealthy"}
    
    def get_scoreboard(self, sport: str, league: str, dates: str = None) -> Dict[str, Any]:
        """Get scoreboard for a league"""
        data = {"sport": sport, "league": league}
        if dates:
            data["dates"] = dates
        return self._post("/espn/scoreboard", data)
    
    def get_teams(self, sport: str, league: str) -> Dict[str, Any]:
        """Get teams for a league"""
        return self._post("/espn/teams", {"sport": sport, "league": league})
    
    def get_game_summary(self, sport: str, league: str, event_id: str) -> Dict[str, Any]:
        """Get detailed game summary"""
        return self._post("/espn/game-summary", {
            "sport": sport,
            "league": league,
            "event_id": event_id
        })
    
    def analyze_game(self, sport: str, league: str, event_id: str, question: str) -> Dict[str, Any]:
        """Analyze a game with AI"""
        return self._post("/espn/analyze-game", {
            "sport": sport,
            "league": league,
            "event_id": event_id,
            "question": question
        })
    
    def get_odds(self, sport: str, regions: str = "us", markets: str = "h2h") -> Dict[str, Any]:
        """Get odds for a sport"""
        return self._post("/odds/get-odds", {
            "sport": sport,
            "regions": regions,
            "markets": markets
        })
    
    def get_daily_intelligence(self, leagues: List[str], include_odds: bool = True) -> Dict[str, Any]:
        """Get comprehensive daily intelligence for multiple leagues"""
        return self._post("/daily-intelligence", {
            "leagues": leagues,
            "include_odds": include_odds
        })

# Example usage functions
def example_basic_usage():
    """Basic usage examples"""
    print("🏀 Basic Usage Examples")
    print("=" * 30)
    
    client = SportsClient()
    
    # Check server health
    health = client.health_check()
    print(f"Server Status: {health.get('status', 'unknown')}")
    
    # Get NBA teams
    teams = client.get_teams("basketball", "nba")
    if teams.get("ok"):
        team_count = len(teams["data"]["teams"])
        print(f"NBA Teams: {team_count}")
        # Show first 3 teams
        for team in teams["data"]["teams"][:3]:
            print(f"  - {team['displayName']} ({team['abbrev']})")
    else:
        print(f"Error getting teams: {teams.get('message', 'Unknown error')}")
    
    # Get today's NBA games
    today = datetime.now().strftime("%Y%m%d")
    scoreboard = client.get_scoreboard("basketball", "nba", today)
    if scoreboard.get("ok"):
        events = scoreboard["data"]["scoreboard"]["events"]
        print(f"NBA Games Today: {len(events)}")
        for game in events[:3]:  # Show first 3 games
            home = game["home"]["displayName"]
            away = game["away"]["displayName"]
            status = game["status"]
            print(f"  - {away} @ {home} ({status})")
    else:
        print(f"Error getting games: {scoreboard.get('message', 'Unknown error')}")

def example_daily_intelligence():
    """Daily intelligence example"""
    print("\n📊 Daily Intelligence Example")
    print("=" * 35)
    
    client = SportsClient()
    
    # Get comprehensive data for multiple leagues
    leagues = ["basketball/nba", "football/nfl", "hockey/nhl"]
    intelligence = client.get_daily_intelligence(leagues, include_odds=False)
    
    if intelligence.get("status") == "success":
        print(f"Successfully got data for {len(intelligence['data'])} leagues:")
        
        for league, data in intelligence["data"].items():
            if data.get("error"):
                print(f"\n❌ {league}: {data['error']}")
                continue
                
            games = data.get("games", {}).get("events", [])
            teams = data.get("teams", [])
            
            print(f"\n✅ {league}:")
            print(f"  - Teams: {len(teams)}")
            print(f"  - Games: {len(games)}")
            
            if games:
                print("  - Upcoming games:")
                for game in games[:2]:  # Show first 2 games
                    home = game["home"]["displayName"]
                    away = game["away"]["displayName"]
                    print(f"    • {away} @ {home}")
    else:
        print(f"Error: {intelligence.get('error', 'Unknown error')}")

def example_discord_bot_usage():
    """Example of how you'd use this in a Discord bot"""
    print("\n🤖 Discord Bot Usage Example")
    print("=" * 35)
    
    # This is how you'd use it in a Discord bot
    bot_code = '''
# In your Discord bot:
import discord
from example_client import SportsClient

client = SportsClient("http://your-server:8000")

@bot.command(name='nba')
async def nba_games(ctx):
    """Get today's NBA games"""
    try:
        today = datetime.now().strftime("%Y%m%d")
        games = client.get_scoreboard("basketball", "nba", today)
        
        if games.get("ok"):
            events = games["data"]["scoreboard"]["events"]
            if events:
                embed = discord.Embed(title="NBA Games Today", color=0x00ff00)
                for game in events[:5]:  # Show up to 5 games
                    home = game["home"]["displayName"]
                    away = game["away"]["displayName"]
                    status = game["status"]
                    embed.add_field(
                        name=f"{away} @ {home}",
                        value=f"Status: {status}",
                        inline=False
                    )
                await ctx.send(embed=embed)
            else:
                await ctx.send("No NBA games today!")
        else:
            await ctx.send("Error getting NBA games")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command(name='daily')
async def daily_intelligence(ctx):
    """Get daily sports intelligence"""
    try:
        leagues = ["basketball/nba", "football/nfl"]
        intel = client.get_daily_intelligence(leagues)
        
        if intel.get("status") == "success":
            embed = discord.Embed(title="Daily Sports Intelligence", color=0x0099ff)
            for league, data in intel["data"].items():
                if not data.get("error"):
                    games_count = len(data.get("games", {}).get("events", []))
                    embed.add_field(
                        name=league.upper(),
                        value=f"{games_count} games today",
                        inline=True
                    )
            await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")
    '''
    
    print("Here's how you'd use the client in a Discord bot:")
    print(bot_code)

def main():
    """Run examples"""
    try:
        example_basic_usage()
        example_daily_intelligence()
        example_discord_bot_usage()
        
        print(f"\n🎉 Examples completed!")
        print(f"💡 Copy this client code to your Discord bot, web app, or other projects")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print(f"Make sure:")
        print(f"  1. SPORTS_API_KEY environment variable is set")
        print(f"  2. sports_http_server.py is running")
        print(f"  3. Your MCPs are working properly")

if __name__ == "__main__":
    main()