#!/usr/bin/env python3
"""
Simple MLB MCP Tool Runner

A straightforward script to quickly test individual MLB MCP tools and see their raw output.
Perfect for exploring what data each tool provides and testing specific scenarios.

Usage:
    python simple_tool_runner.py
    
Then follow the interactive prompts to choose which tool to test.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import httpx

class SimpleMLBRunner:
    """Simple interactive runner for MLB MCP tools"""
    
    def __init__(self):
        self.server_url = "https://mlbmcp-production.up.railway.app/mcp"
        self.client = None
        
        # Quick reference data
        self.sample_teams = {
            "Yankees": 147,
            "Dodgers": 119, 
            "Guardians": 114,
            "Marlins": 146,
            "Mariners": 136,
            "Red Sox": 111,
            "Astros": 117,
            "Mets": 121
        }
        
        self.sample_players = {
            "Aaron Judge": 592450,
            "Mookie Betts": 605141,
            "Julio Rodriguez": 677594,
            "Jose Altuve": 514888,
            "Freddie Freeman": 518692
        }
        
        self.sample_pitchers = {
            "Gerrit Cole": 543037,
            "Clayton Kershaw": 477132,
            "Shane Bieber": 669456,
            "Jacob deGrom": 594798
        }
    
    async def init_client(self):
        """Initialize HTTP client"""
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Call an MLB MCP tool and return the result"""
        if not self.client:
            await self.init_client()
        
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
        
        print(f"\n🔧 Calling: {tool_name}")
        print(f"📋 Arguments: {json.dumps(arguments, indent=2)}")
        print("-" * 50)
        
        try:
            response = await self.client.post(self.server_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(f"❌ Error Response:")
                print(json.dumps(result["error"], indent=2))
                return None
            
            return result.get("result", {})
            
        except Exception as e:
            print(f"❌ Request Failed: {e}")
            return None
    
    def print_result(self, result: Dict[str, Any]):
        """Pretty print the tool result"""
        if not result:
            print("❌ No result to display")
            return
        
        print("✅ SUCCESS - Raw Response:")
        print("=" * 60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("=" * 60)
        
        # Also provide a human-readable summary
        if result.get("data"):
            self.print_summary(result["data"])
    
    def print_summary(self, data: Dict[str, Any]):
        """Print a human-readable summary of the data"""
        print("\n📊 QUICK SUMMARY:")
        print("-" * 30)
        
        # Schedule data
        if "games" in data and isinstance(data["games"], list):
            games = data["games"]
            date_et = data.get("date_et", "Unknown")
            print(f"📅 Schedule for {date_et}: {len(games)} games")
            
            for i, game in enumerate(games[:3], 1):
                away = game.get("away", {}).get("name", "Unknown")
                home = game.get("home", {}).get("name", "Unknown")
                time = game.get("start_et", "TBD")
                status = game.get("status", "Unknown")
                print(f"  {i}. {away} @ {home} ({time}) - {status}")
            
            if len(games) > 3:
                print(f"  ... and {len(games) - 3} more games")
        
        # Teams data  
        elif "teams" in data and isinstance(data["teams"], list):
            teams = data["teams"]
            season = data.get("season", "Unknown")
            print(f"⚾ Teams for {season}: {len(teams)} teams")
            
            # Group by league
            al_teams = [t for t in teams if "American" in t.get("league", "")]
            nl_teams = [t for t in teams if "National" in t.get("league", "")]
            
            print(f"  American League: {len(al_teams)} teams")
            print(f"  National League: {len(nl_teams)} teams")
            
            # Show sample
            for i, team in enumerate(teams[:5], 1):
                name = team.get("name", "Unknown")
                abbrev = team.get("abbrev", "N/A")
                division = team.get("division", "Unknown")
                print(f"  {i}. {name} ({abbrev}) - {division}")
        
        # Roster data
        elif "players" in data and isinstance(data["players"], list):
            players = data["players"]
            team_id = data.get("teamId", "Unknown")
            season = data.get("season", "Unknown")
            print(f"👥 Roster for Team {team_id} ({season}): {len(players)} players")
            
            # Group by position
            positions = {}
            for player in players:
                pos = player.get("position", "Unknown")
                positions[pos] = positions.get(pos, 0) + 1
            
            for pos, count in sorted(positions.items()):
                print(f"  {pos}: {count} players")
            
            # Show sample players
            print("\n  Sample players:")
            for i, player in enumerate(players[:5], 1):
                name = player.get("fullName", "Unknown")
                number = player.get("primaryNumber", "N/A")
                position = player.get("position", "N/A")
                print(f"    {i}. {name} (#{number} {position})")
        
        # Player stats data
        elif "results" in data and isinstance(data["results"], dict):
            results = data["results"]
            group = data.get("group", "Unknown")
            season = data.get("season", "Unknown")
            print(f"📈 Player Stats ({group}, {season}): {len(results)} players")
            
            for player_id, player_data in results.items():
                games = player_data.get("games", [])
                aggregates = player_data.get("aggregates", {})
                
                print(f"  Player {player_id}: {len(games)} games")
                
                # Show key aggregates
                key_stats = [(k, v) for k, v in aggregates.items() if "_avg" in k][:3]
                for stat, value in key_stats:
                    if isinstance(value, (int, float)):
                        print(f"    {stat}: {value:.3f}")
        
        # Team form data
        elif "form" in data:
            form = data["form"]
            team_name = data.get("team_name", "Unknown Team")
            print(f"📊 Team Form: {team_name}")
            print(f"  Record: {form.get('wins', 0)}-{form.get('losses', 0)}")
            print(f"  Win %: {form.get('win_percentage', 'N/A')}")
            print(f"  Current Streak: {form.get('streak', 'N/A')}")
            print(f"  Last 10: {form.get('last_10', 'N/A')}")
        
        # Pitcher matchup data
        elif "aggregates" in data and "recent_starts" in data:
            aggregates = data["aggregates"]
            starts = data["recent_starts"]
            pitcher_id = data.get("pitcher_id", "Unknown")
            print(f"⚾ Pitcher Analysis: Pitcher {pitcher_id}")
            print(f"  Recent starts: {len(starts)}")
            print(f"  ERA: {aggregates.get('era', 'N/A')}")
            print(f"  WHIP: {aggregates.get('whip', 'N/A')}")
            print(f"  K/9: {aggregates.get('k_per_9', 'N/A')}")
        
        # Scoring trends data
        elif "trends" in data:
            trends = data["trends"]
            team_name = data.get("team_name", "Unknown Team")
            print(f"📈 Scoring Trends: {team_name}")
            print(f"  Runs per game: {trends.get('runs_per_game', 'N/A')}")
            print(f"  Runs allowed per game: {trends.get('runs_allowed_per_game', 'N/A')}")
            print(f"  Run differential: {trends.get('run_differential', 'N/A')}")
        
        print("-" * 30)
    
    def show_menu(self):
        """Show the main menu"""
        print("\n" + "=" * 60)
        print("🏟️  MLB MCP TOOL RUNNER")
        print("=" * 60)
        print("\nAvailable Tools:")
        print("1. getMLBScheduleET - Game schedules")
        print("2. getMLBTeams - Team information")  
        print("3. getMLBTeamRoster - Team rosters")
        print("4. getMLBPlayerLastN - Player game logs")
        print("5. getMLBPitcherMatchup - Pitcher analysis")
        print("6. getMLBTeamForm - Team standings/form")
        print("7. getMLBPlayerStreaks - Player streaks")
        print("8. getMLBTeamScoringTrends - Team scoring patterns")
        print("9. Show sample IDs")
        print("0. Exit")
        print("-" * 60)
    
    def show_sample_ids(self):
        """Show sample team and player IDs"""
        print("\n📋 SAMPLE IDs FOR TESTING:")
        print("-" * 40)
        
        print("\n🏟️  Teams:")
        for name, team_id in self.sample_teams.items():
            print(f"  {name}: {team_id}")
        
        print("\n⚾ Players (Batters):")
        for name, player_id in self.sample_players.items():
            print(f"  {name}: {player_id}")
        
        print("\n🥎 Pitchers:")
        for name, pitcher_id in self.sample_pitchers.items():
            print(f"  {name}: {pitcher_id}")
        
        print("-" * 40)
    
    async def handle_schedule(self):
        """Handle schedule tool"""
        print("\n📅 Schedule Tool Options:")
        print("1. Today's games (default)")
        print("2. Yesterday's games")
        print("3. Tomorrow's games")
        print("4. Custom date")
        
        choice = input("Choose option (1-4): ").strip()
        
        if choice == "1" or choice == "":
            result = await self.call_tool("getMLBScheduleET")
        elif choice == "2":
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            result = await self.call_tool("getMLBScheduleET", {"date": yesterday})
        elif choice == "3":
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            result = await self.call_tool("getMLBScheduleET", {"date": tomorrow})
        elif choice == "4":
            date = input("Enter date (YYYY-MM-DD): ").strip()
            if date:
                result = await self.call_tool("getMLBScheduleET", {"date": date})
            else:
                print("❌ Invalid date")
                return
        else:
            print("❌ Invalid choice")
            return
        
        self.print_result(result)
    
    async def handle_teams(self):
        """Handle teams tool"""
        season = input("Enter season year (or press Enter for current): ").strip()
        
        if season:
            try:
                season_int = int(season)
                result = await self.call_tool("getMLBTeams", {"season": season_int})
            except ValueError:
                print("❌ Invalid season year")
                return
        else:
            result = await self.call_tool("getMLBTeams")
        
        self.print_result(result)
    
    async def handle_roster(self):
        """Handle roster tool"""
        print(f"\nSample team IDs: {', '.join([f'{name}={id}' for name, id in list(self.sample_teams.items())[:4]])}")
        team_id = input("Enter team ID: ").strip()
        
        if not team_id:
            print("❌ Team ID required")
            return
        
        try:
            team_id_int = int(team_id)
            result = await self.call_tool("getMLBTeamRoster", {"teamId": team_id_int})
        except ValueError:
            print("❌ Invalid team ID")
            return
        
        self.print_result(result)
    
    async def handle_player_stats(self):
        """Handle player stats tool"""
        print("\n📊 Player Stats Options:")
        print("1. Single player hitting stats")
        print("2. Multiple players hitting stats")
        print("3. Single pitcher stats")
        
        choice = input("Choose option (1-3): ").strip()
        
        if choice == "1":
            print(f"\nSample players: {', '.join([f'{name}={id}' for name, id in list(self.sample_players.items())[:3]])}")
            player_id = input("Enter player ID: ").strip()
            
            if not player_id:
                print("❌ Player ID required")
                return
            
            try:
                player_id_int = int(player_id)
                result = await self.call_tool("getMLBPlayerLastN", {
                    "player_ids": [player_id_int],
                    "group": "hitting",
                    "stats": ["hits", "homeRuns", "atBats", "runsBattedIn"],
                    "count": 10
                })
            except ValueError:
                print("❌ Invalid player ID")
                return
        
        elif choice == "2":
            player_ids = input("Enter player IDs (comma-separated): ").strip()
            
            if not player_ids:
                print("❌ Player IDs required")
                return
            
            try:
                ids = [int(pid.strip()) for pid in player_ids.split(",")]
                result = await self.call_tool("getMLBPlayerLastN", {
                    "player_ids": ids,
                    "group": "hitting",
                    "stats": ["hits", "homeRuns"],
                    "count": 5
                })
            except ValueError:
                print("❌ Invalid player IDs")
                return
        
        elif choice == "3":
            print(f"\nSample pitchers: {', '.join([f'{name}={id}' for name, id in list(self.sample_pitchers.items())[:3]])}")
            pitcher_id = input("Enter pitcher ID: ").strip()
            
            if not pitcher_id:
                print("❌ Pitcher ID required")
                return
            
            try:
                pitcher_id_int = int(pitcher_id)
                result = await self.call_tool("getMLBPlayerLastN", {
                    "player_ids": [pitcher_id_int],
                    "group": "pitching", 
                    "stats": ["strikeOuts", "walks", "hits", "earnedRuns"],
                    "count": 5
                })
            except ValueError:
                print("❌ Invalid pitcher ID")
                return
        
        else:
            print("❌ Invalid choice")
            return
        
        self.print_result(result)
    
    async def handle_pitcher_matchup(self):
        """Handle pitcher matchup tool"""
        print(f"\nSample pitchers: {', '.join([f'{name}={id}' for name, id in list(self.sample_pitchers.items())[:3]])}")
        pitcher_id = input("Enter pitcher ID: ").strip()
        
        if not pitcher_id:
            print("❌ Pitcher ID required")
            return
        
        try:
            pitcher_id_int = int(pitcher_id)
            result = await self.call_tool("getMLBPitcherMatchup", {"pitcher_id": pitcher_id_int, "count": 5})
        except ValueError:
            print("❌ Invalid pitcher ID")
            return
        
        self.print_result(result)
    
    async def handle_team_form(self):
        """Handle team form tool"""
        print(f"\nSample teams: {', '.join([f'{name}={id}' for name, id in list(self.sample_teams.items())[:4]])}")
        team_id = input("Enter team ID: ").strip()
        
        if not team_id:
            print("❌ Team ID required")
            return
        
        try:
            team_id_int = int(team_id)
            result = await self.call_tool("getMLBTeamForm", {"team_id": team_id_int})
        except ValueError:
            print("❌ Invalid team ID")
            return
        
        self.print_result(result)
    
    async def handle_player_streaks(self):
        """Handle player streaks tool"""
        print(f"\nSample players: {', '.join([f'{name}={id}' for name, id in list(self.sample_players.items())[:3]])}")
        player_id = input("Enter player ID: ").strip()
        
        if not player_id:
            print("❌ Player ID required")
            return
        
        try:
            player_id_int = int(player_id)
            result = await self.call_tool("getMLBPlayerStreaks", {
                "player_ids": [player_id_int],
                "lookback": 20
            })
        except ValueError:
            print("❌ Invalid player ID")
            return
        
        self.print_result(result)
    
    async def handle_scoring_trends(self):
        """Handle scoring trends tool"""
        print(f"\nSample teams: {', '.join([f'{name}={id}' for name, id in list(self.sample_teams.items())[:4]])}")
        team_id = input("Enter team ID: ").strip()
        
        if not team_id:
            print("❌ Team ID required")
            return
        
        try:
            team_id_int = int(team_id)
            result = await self.call_tool("getMLBTeamScoringTrends", {"team_id": team_id_int})
        except ValueError:
            print("❌ Invalid team ID")
            return
        
        self.print_result(result)
    
    async def run(self):
        """Main interactive loop"""
        print("🚀 Starting MLB MCP Tool Runner...")
        await self.init_client()
        
        while True:
            self.show_menu()
            choice = input("\nEnter your choice (0-9): ").strip()
            
            try:
                if choice == "0":
                    print("👋 Goodbye!")
                    break
                elif choice == "1":
                    await self.handle_schedule()
                elif choice == "2":
                    await self.handle_teams()
                elif choice == "3":
                    await self.handle_roster()
                elif choice == "4":
                    await self.handle_player_stats()
                elif choice == "5":
                    await self.handle_pitcher_matchup()
                elif choice == "6":
                    await self.handle_team_form()
                elif choice == "7":
                    await self.handle_player_streaks()
                elif choice == "8":
                    await self.handle_scoring_trends()
                elif choice == "9":
                    self.show_sample_ids()
                else:
                    print("❌ Invalid choice. Please enter 0-9.")
                
                if choice != "0" and choice != "9":
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                input("Press Enter to continue...")
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()

async def main():
    """Main function"""
    runner = SimpleMLBRunner()
    
    try:
        await runner.run()
    finally:
        await runner.close()

if __name__ == "__main__":
    asyncio.run(main())