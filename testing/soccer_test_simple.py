#!/usr/bin/env python3
"""
Simple Interactive Soccer Testing Script
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List
import httpx
from dotenv import load_dotenv

# Add parent directory to path to load .env
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
load_dotenv(os.path.join(parent_dir, '.env'))

class SimpleSoccerTester:
    def __init__(self):
        self.soccer_mcp_url = "https://soccermcp-production.up.railway.app/mcp"
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Available leagues
        self.leagues = {
            "1": {"id": "2021", "name": "Premier League (EPL)"},
            "2": {"id": "2014", "name": "La Liga (Spain)"},
            "3": {"id": "2002", "name": "Bundesliga (Germany)"},
            "4": {"id": "2015", "name": "Ligue 1 (France)"},
            "5": {"id": "2019", "name": "Serie A (Italy)"},
            "6": {"id": "2001", "name": "UEFA Champions League"},
        }
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def call_soccer_mcp(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call soccer MCP server"""
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
            response = await self.client.post(
                self.soccer_mcp_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                print(f"HTTP Error {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
            result = response.json()
            return result
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return {"error": f"Connection failed: {str(e)}"}

    def select_league(self):
        """Let user select a league"""
        print("\nSelect a League:")
        print("=" * 30)
        for num, league in self.leagues.items():
            print(f"{num}. {league['name']}")
        
        while True:
            choice = input("\nEnter league number (1-6): ").strip()
            if choice in self.leagues:
                return self.leagues[choice]
            print("Invalid choice. Please enter 1-6.")

    def select_game_type(self):
        """Let user select finished or upcoming games"""
        print("\nSelect Game Type:")
        print("=" * 20)
        print("1. Finished Games")
        print("2. Upcoming Games")
        
        while True:
            choice = input("\nEnter choice (1-2): ").strip()
            if choice == "1":
                return "FINISHED"
            elif choice == "2":
                return "SCHEDULED"
            print("Invalid choice. Please enter 1 or 2.")

    async def get_games(self, league_id: str, status: str) -> List[Dict]:
        """Get games for the selected league and status"""
        # Get date range
        if status == "FINISHED":
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")  # Reduced to 15 days
        else:
            start_date = datetime.now().strftime("%Y-%m-%d")
            end_date = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")  # Reduced to 15 days
        
        print(f"Getting games from {start_date} to {end_date}...")
        
        result = await self.call_soccer_mcp("getCompetitionMatches", {
            "competition_id": league_id,
            "date_from": start_date,
            "date_to": end_date,
            "status": status
        })
        
        if "result" in result and result["result"].get("ok"):
            games = result["result"]["data"]["matches"]
            print(f"Found {len(games)} games")
            return games[:10]  # Limit to 10 games max
        else:
            error_msg = result.get("error", "Unknown error")
            print(f"Error getting games: {error_msg}")
            return []

    def select_game(self, games: List[Dict], status: str) -> Dict:
        """Let user select a specific game"""
        game_type = "Finished" if status == "FINISHED" else "Upcoming"
        print(f"\nSelect a {game_type} Game:")
        print("=" * 40)
        
        if not games:
            print(f"No {game_type.lower()} games found.")
            return None
        
        # Show games list (max 10)
        for i, game in enumerate(games, 1):
            home = game["homeTeam"]["name"]
            away = game["awayTeam"]["name"]
            date = game["utcDate"][:10]
            
            if status == "FINISHED":
                score = game.get("score", {}).get("fullTime", {})
                if score and score.get("home") is not None:
                    score_str = f"{score['home']}-{score['away']}"
                else:
                    score_str = "No score"
                print(f"{i}. {date}: {home} {score_str} {away}")
            else:
                time = game["utcDate"][11:16]
                print(f"{i}. {date} {time}: {home} vs {away}")
        
        while True:
            try:
                choice = input(f"\nEnter game number (1-{len(games)}): ").strip()
                game_num = int(choice)
                if 1 <= game_num <= len(games):
                    return games[game_num - 1]
                print(f"Invalid choice. Please enter 1-{len(games)}.")
            except ValueError:
                print("Please enter a valid number.")

    async def show_game_details(self, game: Dict):
        """Show detailed game information"""
        print(f"\n{'='*50}")
        print(f"GAME DETAILS")
        print(f"{'='*50}")
        
        home_team = game["homeTeam"]["name"]
        away_team = game["awayTeam"]["name"]
        date = game["utcDate"][:10]
        time = game["utcDate"][11:16]
        status = game["status"]
        
        print(f"Match: {home_team} vs {away_team}")
        print(f"Date: {date} at {time} UTC")
        print(f"Status: {status}")
        
        # Show score if finished
        if status == "FINISHED":
            score = game.get("score", {})
            if score:
                full_time = score.get("fullTime", {})
                half_time = score.get("halfTime", {})
                
                if full_time and full_time.get("home") is not None:
                    print(f"Final Score: {home_team} {full_time['home']}-{full_time['away']} {away_team}")
                
                if half_time and half_time.get("home") is not None:
                    print(f"Half Time: {half_time['home']}-{half_time['away']}")
        
        # Get detailed match information
        print(f"\nGetting detailed match information...")
        details_result = await self.call_soccer_mcp("getMatchDetails", {
            "match_id": game["id"]
        })
        
        if "result" in details_result and details_result["result"].get("ok"):
            match_details = details_result["result"]["data"]["match"]
            
            # Show betting-relevant team statistics
            print(f"\nBETTING STATISTICS:")
            print("=" * 50)
            
            # Team-level stats for betting props
            home_stats = match_details.get("homeTeam", {}).get("statistics", {})
            away_stats = match_details.get("awayTeam", {}).get("statistics", {})
            
            if home_stats and away_stats:
                print(f"\nTeam Performance Stats:")
                print("-" * 30)
                
                # Key betting metrics
                betting_metrics = [
                    ("Shots", "shots"),
                    ("Shots on Target", "shots_on_goal"), 
                    ("Corners", "corner_kicks"),
                    ("Possession %", "ball_possession"),
                    ("Fouls", "fouls"),
                    ("Yellow Cards", "yellow_cards"),
                    ("Saves", "saves")
                ]
                
                for metric_name, key in betting_metrics:
                    home_val = home_stats.get(key, 0)
                    away_val = away_stats.get(key, 0)
                    print(f"{metric_name:15} | {home_team}: {home_val:2} | {away_team}: {away_val:2}")
            
            # Goals and assists for individual betting props
            goals = match_details.get("goals", [])
            if goals:
                print(f"\nPlayer Goal/Assist Stats:")
                print("-" * 30)
                
                # Count goals and assists per player
                player_stats = {}
                for goal in goals:
                    scorer = goal.get("scorer", {}).get("name")
                    assist = goal.get("assist", {}).get("name") if goal.get("assist") else None
                    
                    if scorer:
                        if scorer not in player_stats:
                            player_stats[scorer] = {"goals": 0, "assists": 0}
                        player_stats[scorer]["goals"] += 1
                    
                    if assist:
                        if assist not in player_stats:
                            player_stats[assist] = {"goals": 0, "assists": 0}
                        player_stats[assist]["assists"] += 1
                
                for player, stats in player_stats.items():
                    goals_str = f"{stats['goals']} goals" if stats['goals'] > 0 else ""
                    assists_str = f"{stats['assists']} assists" if stats['assists'] > 0 else ""
                    performance = ", ".join(filter(None, [goals_str, assists_str]))
                    print(f"  {player}: {performance}")
            
            # Venue and other context
            venue = game.get("venue")
            if venue:
                print(f"\nVenue: {venue}")
            
            return match_details
        else:
            error_msg = details_result.get("error", "Unknown error")
            print(f"Could not get detailed match info: {error_msg}")
            return game

    async def show_player_options(self, game: Dict, league_id: str):
        """Show betting-focused player analysis"""
        print(f"\n{'='*50}")
        print(f"BETTING ANALYSIS OPTIONS")
        print(f"{'='*50}")
        
        print("What betting analysis would you like?")
        print("1. Individual player performance in this match")
        print("2. Team betting trends (corners, shots, cards)")
        print("3. League top performers for prop bets") 
        print("4. Player season averages (for historical analysis)")
        print("5. Exit")
        
        while True:
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == "1":
                await self.show_player_match_performance(game)
                break
            elif choice == "2":
                await self.show_team_betting_trends(game)
                break
            elif choice == "3":
                await self.show_top_scorers(league_id)
                break
            elif choice == "4":
                print("\nPlayer season averages require individual player API calls.")
                print("This would show stats like: avg shots per game, avg assists, etc.")
                break
            elif choice == "5":
                return
            else:
                print("Invalid choice. Please enter 1-5.")

    async def show_player_match_performance(self, game: Dict):
        """Show individual player performance for betting analysis"""
        print(f"\nPLAYER PERFORMANCE ANALYSIS:")
        print("-" * 40)
        
        # Goals and assists
        goals = game.get("goals", [])
        bookings = game.get("bookings", [])
        
        if goals:
            print("Goal/Assist Performance:")
            player_stats = {}
            for goal in goals:
                scorer = goal.get("scorer", {}).get("name")
                assist = goal.get("assist", {}).get("name") if goal.get("assist") else None
                
                if scorer:
                    if scorer not in player_stats:
                        player_stats[scorer] = {"goals": 0, "assists": 0}
                    player_stats[scorer]["goals"] += 1
                
                if assist:
                    if assist not in player_stats:
                        player_stats[assist] = {"goals": 0, "assists": 0}
                    player_stats[assist]["assists"] += 1
            
            for player, stats in player_stats.items():
                print(f"  {player}: {stats['goals']} goals, {stats['assists']} assists")
        
        # Card performance (relevant for discipline props)
        if bookings:
            print("\nDiscipline (Cards):")
            card_players = {}
            for booking in bookings:
                player = booking.get("player", {}).get("name", "Unknown")
                card_type = booking.get("card", "").replace("_CARD", "").replace("_", " ").title()
                minute = booking.get("minute", "?")
                
                if player not in card_players:
                    card_players[player] = []
                card_players[player].append(f"{card_type} ({minute}')")
            
            for player, cards in card_players.items():
                print(f"  {player}: {', '.join(cards)}")
        
        print("\n💡 Betting Tip: Look for patterns in player performance")
        print("   - Goals/assists indicate offensive involvement")
        print("   - Cards indicate discipline issues")

    async def show_team_betting_trends(self, game: Dict):
        """Show team-level statistics for betting trends"""
        print(f"\nTEAM BETTING TRENDS:")
        print("-" * 40)
        
        home_team = game["homeTeam"]["name"]
        away_team = game["awayTeam"]["name"]
        home_stats = game.get("homeTeam", {}).get("statistics", {})
        away_stats = game.get("awayTeam", {}).get("statistics", {})
        
        if not home_stats or not away_stats:
            print("Team statistics not available for this match.")
            return
        
        # Key betting markets analysis
        print("Corner Kicks Analysis:")
        home_corners = home_stats.get("corner_kicks", 0)
        away_corners = away_stats.get("corner_kicks", 0)
        total_corners = home_corners + away_corners
        print(f"  {home_team}: {home_corners} | {away_team}: {away_corners} | Total: {total_corners}")
        
        print("\nShots Analysis:")
        home_shots = home_stats.get("shots", 0)
        away_shots = away_stats.get("shots", 0)
        home_on_target = home_stats.get("shots_on_goal", 0)
        away_on_target = away_stats.get("shots_on_goal", 0)
        print(f"  {home_team}: {home_shots} shots ({home_on_target} on target)")
        print(f"  {away_team}: {away_shots} shots ({away_on_target} on target)")
        
        print("\nCards Analysis:")
        home_cards = home_stats.get("yellow_cards", 0)
        away_cards = away_stats.get("yellow_cards", 0)
        total_cards = home_cards + away_cards
        print(f"  {home_team}: {home_cards} cards | {away_team}: {away_cards} cards | Total: {total_cards}")
        
        print("\nPossession:")
        home_poss = home_stats.get("ball_possession", 0)
        away_poss = away_stats.get("ball_possession", 0)
        print(f"  {home_team}: {home_poss}% | {away_team}: {away_poss}%")
        
        print("\n💡 Betting Analysis:")
        if total_corners >= 10:
            print("   - High corner count (10+) - good for Over corner bets")
        if home_on_target + away_on_target >= 8:
            print("   - High shots on target - indicates attacking play")
        if total_cards >= 6:
            print("   - High card count - indicates physical/aggressive match")

    async def show_top_scorers(self, league_id: str):
        """Show top scorers for the league"""
        print(f"\nGetting top scorers...")
        
        result = await self.call_soccer_mcp("getTopScorers", {
            "competition_id": league_id,
            "limit": 10  # Reduced to 10
        })
        
        if "result" in result and result["result"].get("ok"):
            scorers = result["result"]["data"]["scorers"]
            
            if scorers:
                print(f"\nTop 10 Goal Scorers:")
                print("-" * 40)
                for i, scorer in enumerate(scorers, 1):
                    player_name = scorer["player"]["name"]
                    team_name = scorer["team"]["name"]
                    goals = scorer["goals"]
                    
                    print(f"{i:2d}. {player_name} ({team_name}) - {goals} goals")
            else:
                print("No scorer data available.")
        else:
            error_msg = result.get("error", "Unknown error")
            print(f"Error getting scorers: {error_msg}")

    async def run(self):
        """Main interactive loop"""
        print("Simple Soccer Testing Script")
        print("=" * 30)
        
        try:
            # Step 1: Select league
            league = self.select_league()
            print(f"\nSelected: {league['name']}")
            
            # Step 2: Select game type
            game_status = self.select_game_type()
            game_type_name = "Finished" if game_status == "FINISHED" else "Upcoming"
            print(f"Selected: {game_type_name} Games")
            
            # Step 3: Get games
            print(f"\nGetting {game_type_name.lower()} games...")
            games = await self.get_games(league["id"], game_status)
            
            if not games:
                print("No games found.")
                return
            
            # Step 4: Select specific game
            selected_game = self.select_game(games, game_status)
            if not selected_game:
                return
            
            # Step 5: Show game details
            detailed_game = await self.show_game_details(selected_game)
            
            # Step 6: Player stats options
            if game_status == "FINISHED":
                await self.show_player_options(detailed_game, league["id"])
                    
        except KeyboardInterrupt:
            print("\nExiting...")
        except Exception as e:
            print(f"Error: {e}")

async def main():
    """Main function"""
    async with SimpleSoccerTester() as tester:
        await tester.run()

if __name__ == "__main__":
    asyncio.run(main())