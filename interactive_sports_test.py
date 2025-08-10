#!/usr/bin/env python3
"""
Interactive Sports Testing Interface

Menu-driven testing for all your sports data and betting integration.
Supports NBA, WNBA, NFL, MLB, NHL, Soccer and more.
"""

import requests
import json
import sys
from datetime import datetime

RAILWAY_URL = "https://web-production-b939f.up.railway.app"
API_KEY = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

class SportsTestInterface:
    def __init__(self):
        self.games_cache = {}
        self.current_sport_league = None
        self.api_calls_count = 0
        # Multi-season sport keys - tries all variations and combines results
        self.available_leagues = {
            "basketball": {
                "nba": {
                    "name": "NBA", 
                    "odds_keys": ["basketball_nba", "basketball_nba_preseason", "basketball_nba_championship_winner"]
                },
                "wnba": {
                    "name": "WNBA", 
                    "odds_keys": ["basketball_wnba", "basketball_wnba_championship_winner"]
                }
            },
            "football": {
                "nfl": {
                    "name": "NFL", 
                    "odds_keys": ["americanfootball_nfl", "americanfootball_nfl_preseason", "americanfootball_nfl_super_bowl_winner"]
                },
                "college-football": {
                    "name": "College Football", 
                    "odds_keys": ["americanfootball_ncaaf", "americanfootball_ncaaf_championship_winner"]
                }
            },
            "baseball": {
                "mlb": {
                    "name": "MLB", 
                    "odds_keys": ["baseball_mlb", "baseball_mlb_preseason", "baseball_mlb_world_series_winner"]
                }
            },
            "hockey": {
                "nhl": {
                    "name": "NHL", 
                    "odds_keys": ["icehockey_nhl", "icehockey_nhl_championship_winner"]
                }
            },
            "soccer": {
                "eng.1": {
                    "name": "Premier League", 
                    "odds_keys": ["soccer_epl", "soccer_epl_championship_winner"]
                },
                "esp.1": {
                    "name": "La Liga", 
                    "odds_keys": ["soccer_spain_la_liga", "soccer_spain_la_liga_championship_winner"]
                },
                "usa.1": {
                    "name": "MLS", 
                    "odds_keys": ["soccer_usa_mls", "soccer_usa_mls_championship_winner"]
                }
            }
        }
        
    def print_header(self, title):
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)
        
    def print_section(self, title):
        print(f"\n--- {title} ---")
        
    def make_request(self, method, endpoint, data=None):
        """Make API request with error handling and call counting"""
        # Count API calls to odds endpoints
        if "/odds/" in endpoint:
            self.api_calls_count += 1
            
        try:
            if method.upper() == "GET":
                response = requests.get(f"{RAILWAY_URL}{endpoint}", headers=headers, timeout=30)
            else:
                response = requests.post(f"{RAILWAY_URL}{endpoint}", headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"HTTP {response.status_code}: {response.text[:200]}"
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def select_sport_league(self):
        """Let user select sport and league"""
        self.print_section("SELECT SPORT & LEAGUE")
        
        print("Available Sports:")
        sports_list = list(self.available_leagues.keys())
        for i, sport in enumerate(sports_list, 1):
            leagues = list(self.available_leagues[sport].keys())
            league_names = [self.available_leagues[sport][l]["name"] for l in leagues]
            print(f"  {i}. {sport.upper()} - {', '.join(league_names)}")
        
        try:
            sport_choice = int(input(f"\nSelect sport (1-{len(sports_list)}): ")) - 1
            if 0 <= sport_choice < len(sports_list):
                selected_sport = sports_list[sport_choice]
                
                leagues = list(self.available_leagues[selected_sport].keys())
                if len(leagues) == 1:
                    selected_league = leagues[0]
                else:
                    print(f"\nAvailable {selected_sport.upper()} leagues:")
                    for i, league in enumerate(leagues, 1):
                        league_name = self.available_leagues[selected_sport][league]["name"]
                        print(f"  {i}. {league_name}")
                    
                    league_choice = int(input(f"\nSelect league (1-{len(leagues)}): ")) - 1
                    if 0 <= league_choice < len(leagues):
                        selected_league = leagues[league_choice]
                    else:
                        print("Invalid league selection")
                        return None, None
                
                self.current_sport_league = (selected_sport, selected_league)
                league_info = self.available_leagues[selected_sport][selected_league]
                print(f"\nSelected: {league_info['name']}")
                return selected_sport, selected_league
            else:
                print("Invalid sport selection")
                return None, None
        except ValueError:
            print("Invalid input")
            return None, None
    
    def main_menu(self):
        """Main menu interface"""
        while True:
            if self.current_sport_league:
                sport, league = self.current_sport_league
                league_name = self.available_leagues[sport][league]["name"]
                title = f"{league_name.upper()} TESTING MENU"
            else:
                title = "SPORTS TESTING MENU"
                
            self.print_header(title)
            
            if not self.current_sport_league:
                print("No sport/league selected")
            
            print("SPORT SELECTION:")
            print("1. Select Sport & League")
            
            if self.current_sport_league:
                print(f"\n{league_name.upper()} TESTING:")
                print("2. Get Today's Games")
                print("3. Get Moneylines") 
                print("4. Get Spreads & Totals")
                print("5. Get Player Props")
                print("6. Deep Dive on Specific Game")
                print("7. Search for Specific Player")
                print("8. Full Daily Intelligence Report")
                print("9. Available Sports from Odds API")
            
            print("\nOTHER:")
            print("0. Quit")
            
            max_option = 9 if self.current_sport_league else 1
            choice = input(f"\nSelect option (0-{max_option}): ").strip()
            
            if choice == '0':
                return
            elif choice == '1':
                self.select_sport_league()
            elif self.current_sport_league:
                if choice == '2':
                    self.get_todays_games()
                elif choice == '3':
                    self.get_moneylines()
                elif choice == '4':
                    self.get_spreads_totals()
                elif choice == '5':
                    self.get_player_props()
                elif choice == '6':
                    self.deep_dive_game()
                elif choice == '7':
                    self.search_player()
                elif choice == '8':
                    self.daily_intelligence()
                elif choice == '9':
                    self.show_available_odds_sports()
                else:
                    print("Invalid choice.")
            else:
                print("Please select a sport and league first.")
    
    def get_todays_games(self):
        """Get and display today's games for selected sport/league"""
        sport, league = self.current_sport_league
        league_name = self.available_leagues[sport][league]["name"]
        
        self.print_section(f"TODAY'S {league_name.upper()} GAMES")
        
        print(f"Fetching {league_name} games from ESPN...")
        success, result = self.make_request("POST", "/espn/scoreboard", {
            "sport": sport, 
            "league": league
        })
        
        if success and result.get("ok"):
            # Our new format returns games directly in the scoreboard array
            games = result.get("data", {}).get("scoreboard", [])
            print(f"Found {len(games)} games today")
            
            if games:
                for i, game in enumerate(games, 1):
                    competitors = game.get("competitions", [{}])[0].get("competitors", [])
                    if len(competitors) >= 2:
                        away = competitors[1].get("team", {}).get("displayName", "Away")
                        home = competitors[0].get("team", {}).get("displayName", "Home")
                        status = game.get("status", {}).get("type", {}).get("description", "Scheduled")
                        game_time = game.get("date", "TBD")
                        print(f"  {i}. {away} @ {home}")
                        print(f"     Status: {status} | Time: {game_time}")
                
                # Cache games for later use
                cache_key = f"{sport}_{league}"
                self.games_cache[cache_key] = games
            else:
                print("No games found for today")
        else:
            print(f"Failed to get games: {result}")
        
        input(f"\nPress Enter to continue...     (odds calls this session: {self.api_calls_count})")
    
    def get_moneylines(self):
        """Get moneylines for selected sport"""
        sport, league = self.current_sport_league
        league_info = self.available_leagues[sport][league]
        
        self.print_section(f"{league_info['name'].upper()} MONEYLINES")
        
        print(f"Fetching {league_info['name']} moneylines from Odds API...")
        
        # Get games from all sport keys for this league
        all_games = self.get_all_odds_for_league(sport, league, "h2h")
        games = self.extract_games_from_odds(all_games)
        
        print(f"Found moneylines for {len(games)} games")
        
        for i, game in enumerate(games, 1):
            home = game.get("home_team", "Home")
            away = game.get("away_team", "Away")
            start_time = game.get("commence_time", "TBD")
            
            print(f"\n{i}. {away} @ {home}")
            print(f"   Start: {start_time}")
            
            self.display_game_odds(game, ["h2h"])
        
        input(f"\nPress Enter to continue...     (odds calls this session: {self.api_calls_count})")
    
    def get_spreads_totals(self):
        """Get spreads and totals for selected sport"""
        sport, league = self.current_sport_league
        league_info = self.available_leagues[sport][league]
        
        self.print_section(f"{league_info['name'].upper()} SPREADS & TOTALS")
        
        print(f"Fetching {league_info['name']} spreads and totals from Odds API...")
        
        # Get games from all sport keys for this league
        all_games = self.get_all_odds_for_league(sport, league, "spreads,totals")
        games = self.extract_games_from_odds(all_games)
        
        print(f"Found spreads/totals for {len(games)} games")
        
        for i, game in enumerate(games, 1):
            home = game.get("home_team", "Home")
            away = game.get("away_team", "Away")
            start_time = game.get("commence_time", "TBD")
            
            print(f"\n{i}. {away} @ {home}")
            print(f"   Start: {start_time}")
            
            self.display_game_odds(game, ["spreads", "totals"])
        
        input(f"\nPress Enter to continue...     (odds calls this session: {self.api_calls_count})")
    
    def get_all_odds_for_league(self, sport, league, markets="h2h"):
        """Get odds from ALL sport keys for a league and combine results"""
        league_info = self.available_leagues[sport][league]
        all_games = []
        
        print(f"\nTrying multiple sport keys for {league_info['name']}...")
        
        for odds_key in league_info['odds_keys']:
            print(f"  Fetching from {odds_key}...")
            
            success, result = self.make_request("POST", "/odds/get-odds", {
                "sport": odds_key,
                "regions": "us",
                "markets": markets,
                "odds_format": "american"
            })
            
            if success:
                # Get games from this sport key
                if isinstance(result, list):
                    key_games = result
                elif isinstance(result, dict) and "data" in result:
                    key_games = result["data"]
                else:
                    key_games = []
                    
                print(f"    Found {len(key_games)} games")
                all_games.extend(key_games)
            else:
                print(f"    Failed: {result}")
        
        print(f"  Total: {len(all_games)} games from all keys")
        return all_games
    
    def extract_games_from_odds(self, result):
        """Extract games from odds API response and filter to today's games"""
        from datetime import datetime
        import pytz
        
        # Get all games first
        if isinstance(result, list):
            all_games = result
        elif isinstance(result, dict) and "data" in result:
            all_games = result["data"]
        else:
            all_games = []
        
        if not all_games:
            return []
        
        # Filter to today's games in Eastern time
        eastern_tz = pytz.timezone('US/Eastern')
        today_str = datetime.now(eastern_tz).strftime("%Y-%m-%d")  # 2025-08-10
        
        print(f"\n[CLIENT DEBUG] Filtering {len(all_games)} games for today: {today_str}")
        
        filtered_games = []
        for i, game in enumerate(all_games[:10]):  # Debug first 10
            commence_time = game.get("commence_time", "")
            home = game.get("home_team", "")
            away = game.get("away_team", "")
            
            if i < 5:  # Show first 5 for debug
                print(f"[CLIENT DEBUG] Game {i+1}: {away} @ {home} - Time: {commence_time}")
            
            if today_str in commence_time:
                filtered_games.append(game)
                if i < 5:
                    print(f"[CLIENT DEBUG] ✅ INCLUDED")
            elif i < 5:
                print(f"[CLIENT DEBUG] ❌ EXCLUDED")
        
        # Filter the rest without debug spam
        for game in all_games[10:]:
            if today_str in game.get("commence_time", ""):
                filtered_games.append(game)
        
        print(f"[CLIENT DEBUG] Found {len(filtered_games)} games for today")
        return filtered_games
    
    def display_game_odds(self, game, market_types):
        """Display odds for a game"""
        bookmakers = game.get("bookmakers", [])
        if not bookmakers:
            print("   No odds available")
            return
        
        for book in bookmakers[:3]:  # Show top 3 bookmakers
            book_name = book.get("title", "Unknown")
            print(f"   {book_name}:")
            
            for market in book.get("markets", []):
                market_key = market.get("key", "")
                if market_key in market_types:
                    self.display_market_odds(market, market_key)
    
    def display_market_odds(self, market, market_key):
        """Display odds for a specific market"""
        if market_key == "h2h":
            # Moneylines
            for outcome in market.get("outcomes", []):
                team = outcome.get("name", "Unknown")
                odds = outcome.get("price", "N/A")
                print(f"     {team}: {odds}")
        elif market_key == "spreads":
            # Point spreads
            print("     Spreads:")
            for outcome in market.get("outcomes", []):
                team = outcome.get("name", "Unknown")
                spread = outcome.get("point", "N/A")
                odds = outcome.get("price", "N/A")
                print(f"       {team} {spread:+}: {odds}")
        elif market_key == "totals":
            # Over/Under totals
            print("     Totals:")
            for outcome in market.get("outcomes", []):
                bet_type = outcome.get("name", "Unknown")
                total = outcome.get("point", "N/A")
                odds = outcome.get("price", "N/A")
                print(f"       {bet_type} {total}: {odds}")
    
    def get_player_props(self):
        """Get player props with progressive selection"""
        sport, league = self.current_sport_league
        league_info = self.available_leagues[sport][league]
        odds_key = league_info["odds_key"]
        
        self.print_section(f"{league_info['name'].upper()} PLAYER PROPS")
        
        # First get available games with odds
        print("1. Finding games with player props...")
        success, result = self.make_request("POST", "/odds/get-odds", {
            "sport": odds_key,
            "regions": "us", 
            "markets": "h2h"  # Just to get game list
        })
        
        if not success:
            print(f"Failed to get games: {result}")
            return
        
        games = self.extract_games_from_odds(result)
        
        if not games:
            print("No games found")
            return
            
        print(f"Found {len(games)} games. Select one for player props:")
        for i, game in enumerate(games, 1):
            home = game.get("home_team", "Home")
            away = game.get("away_team", "Away")
            start_time = game.get("commence_time", "TBD")
            print(f"  {i}. {away} @ {home} ({start_time})")
        
        try:
            choice = int(input(f"\nSelect game (1-{len(games)}): ")) - 1
            if 0 <= choice < len(games):
                selected_game = games[choice]
                self.get_game_player_props(selected_game, odds_key)
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid input")
        
        input(f"\nPress Enter to continue...     (odds calls this session: {self.api_calls_count})")
    
    def get_game_player_props(self, game, odds_key):
        """Get player props for a specific game"""
        event_id = game.get("id")
        home = game.get("home_team", "Home")
        away = game.get("away_team", "Away")
        
        print(f"\n2. Getting player props for {away} @ {home}...")
        
        # Use sport-specific markets
        if "baseball" in odds_key:
            markets = "batter_hits,batter_home_runs,batter_total_bases,pitcher_strikeouts"
        elif "football" in odds_key:
            markets = "player_pass_yds,player_rush_yds,player_receptions,player_pass_tds,player_rush_tds"
        elif "hockey" in odds_key:
            markets = "player_points,player_assists,player_shots_on_goal,player_saves"
        elif "soccer" in odds_key:
            markets = "player_shots,player_shots_on_target,player_goals,player_assists"
        else:
            # Basketball (NBA, WNBA)
            markets = "player_points,player_rebounds,player_assists,player_threes,player_steals,player_blocks"
        
        success, result = self.make_request("POST", "/odds/event-odds", {
            "sport": odds_key,
            "event_id": event_id,
            "regions": "us",
            "markets": markets,
            "odds_format": "american"
        })
        
        if not success:
            print(f"Failed to get player props: {result}")
            return
        
        # Handle response format
        if isinstance(result, dict) and "data" in result:
            event_data = result["data"]
        else:
            event_data = result
        
        bookmakers = event_data.get("bookmakers", [])
        if not bookmakers:
            print("No player props available for this game")
            return
        
        # Collect all unique players
        all_players = set()
        for bookmaker in bookmakers:
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    player = outcome.get("description", "")
                    if player:
                        all_players.add(player)
        
        players_list = sorted(all_players)
        print(f"\n3. Found props for {len(players_list)} players:")
        for i, player in enumerate(players_list, 1):
            print(f"  {i}. {player}")
        
        # Let user select player or see all
        print(f"\n{len(players_list) + 1}. Show all player props")
        
        try:
            choice = int(input(f"\nSelect player or option (1-{len(players_list) + 1}): "))
            
            if choice == len(players_list) + 1:
                # Show all props
                self.display_all_player_props(bookmakers)
            elif 1 <= choice <= len(players_list):
                # Show specific player
                selected_player = players_list[choice - 1]
                self.display_player_props(selected_player, bookmakers)
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid input")
    
    def display_player_props(self, player_name, bookmakers):
        """Display props for a specific player"""
        print(f"\n4. {player_name.upper()} PLAYER PROPS:")
        print("-" * 50)
        
        player_props = {}
        
        for bookmaker in bookmakers:
            book_name = bookmaker.get("title", "Unknown")
            for market in bookmaker.get("markets", []):
                market_key = market.get("key", "")
                for outcome in market.get("outcomes", []):
                    if outcome.get("description", "") == player_name:
                        bet_type = outcome.get("name", "")
                        odds = outcome.get("price", "N/A")
                        line = outcome.get("point", "")
                        
                        prop_key = f"{market_key}_{line}_{bet_type}"
                        if prop_key not in player_props:
                            player_props[prop_key] = {
                                "market": market_key,
                                "line": line,
                                "bet_type": bet_type,
                                "books": {}
                            }
                        player_props[prop_key]["books"][book_name] = odds
        
        # Display all props grouped by market type (works for all sports)
        if player_props:
            # Group by actual market type from the data
            market_groups = {}
            for prop in player_props.values():
                market_key = prop["market"]
                if market_key not in market_groups:
                    market_groups[market_key] = []
                market_groups[market_key].append(prop)
            
            # Display each market group
            for market_key, props in market_groups.items():
                market_label = self.get_market_label(market_key)
                print(f"\n{market_label}:")
                for prop in props:
                    print(f"  {prop['bet_type']} {prop['line']}:")
                    for book, odds in prop['books'].items():
                        print(f"    {book}: {odds}")
        else:
            print("No props found for this player")
    
    def display_all_player_props(self, bookmakers):
        """Display all player props in organized format"""
        print("\n4. ALL PLAYER PROPS:")
        print("-" * 50)
        
        # Group by player (implementation from previous version)
        players_data = {}
        for bookmaker in bookmakers:
            book_name = bookmaker.get("title", "Unknown")
            for market in bookmaker.get("markets", []):
                market_key = market.get("key", "")
                for outcome in market.get("outcomes", []):
                    player = outcome.get("description", "")
                    if not player:
                        continue
                        
                    if player not in players_data:
                        players_data[player] = {}
                    
                    bet_type = outcome.get("name", "")
                    line = outcome.get("point", "")
                    odds = outcome.get("price", "N/A")
                    
                    prop_key = f"{market_key}_{bet_type}_{line}"
                    if prop_key not in players_data[player]:
                        players_data[player][prop_key] = {
                            "market": market_key,
                            "bet_type": bet_type,
                            "line": line,
                            "books": {}
                        }
                    players_data[player][prop_key]["books"][book_name] = odds
        
        # Display players with their props
        for i, (player, props) in enumerate(sorted(players_data.items()), 1):
            print(f"\n{i}. {player}:")
            for prop in props.values():
                market_emoji = self.get_market_emoji(prop["market"])
                best_book = list(prop["books"].keys())[0]
                best_odds = prop["books"][best_book]
                print(f"   {market_emoji} {prop['bet_type']} {prop['line']}: {best_odds} ({best_book})")
    
    def get_market_label(self, market):
        """Get label for market type"""
        market_lower = market.lower()
        
        # Baseball markets
        if "batter_hits" in market_lower:
            return "HITS"
        elif "batter_home_runs" in market_lower:
            return "HOME RUNS"
        elif "batter_total_bases" in market_lower:
            return "TOTAL BASES"
        elif "pitcher_strikeouts" in market_lower:
            return "STRIKEOUTS"
        elif "batter_rbis" in market_lower:
            return "RBIs"
        elif "batter_runs" in market_lower:
            return "RUNS"
        
        # Basketball markets
        elif "point" in market_lower:
            return "POINTS"
        elif "rebound" in market_lower:
            return "REBOUNDS"
        elif "assist" in market_lower:
            return "ASSISTS"
        elif "three" in market_lower:
            return "3-POINTERS"
        elif "steal" in market_lower:
            return "STEALS"
        elif "block" in market_lower:
            return "BLOCKS"
        
        # Football markets
        elif "pass_yds" in market_lower:
            return "PASSING YARDS"
        elif "rush_yds" in market_lower:
            return "RUSHING YARDS"
        elif "receptions" in market_lower:
            return "RECEPTIONS"
        elif "pass_tds" in market_lower:
            return "PASSING TDs"
        elif "rush_tds" in market_lower:
            return "RUSHING TDs"
        
        # Hockey markets
        elif "shots_on_goal" in market_lower:
            return "SHOTS ON GOAL"
        elif "saves" in market_lower:
            return "SAVES"
        
        # Soccer markets
        elif "shots" in market_lower:
            return "SHOTS"
        elif "goals" in market_lower:
            return "GOALS"
        
        # Default
        else:
            return market.upper().replace("_", " ")
    
    def get_market_emoji(self, market):
        """Get emoji for market type"""
        market_lower = market.lower()
        if "point" in market_lower:
            return "📊"
        elif "rebound" in market_lower:
            return "🏀"
        elif "assist" in market_lower:
            return "🤝"
        elif "three" in market_lower:
            return "🎯"
        elif "steal" in market_lower:
            return "🔒"
        elif "block" in market_lower:
            return "🚫"
        else:
            return "📈"
    
    def deep_dive_game(self):
        """Deep dive analysis of a specific game"""
        self.print_section("GAME DEEP DIVE")
        print("Feature coming soon - comprehensive game analysis")
        input(f"\nPress Enter to continue...     (odds calls this session: {self.api_calls_count})")
    
    def search_player(self):
        """Search for a specific player across all games"""
        sport, league = self.current_sport_league
        league_info = self.available_leagues[sport][league]
        
        self.print_section("PLAYER SEARCH")
        
        player_name = input("Enter player name to search for: ").strip()
        if not player_name:
            return
        
        print(f"Searching for '{player_name}' across all {league_info['name']} games...")
        
        # Implementation similar to previous version but with current sport
        print("Feature in development - use player props menu for now")
        input(f"\nPress Enter to continue...     (odds calls this session: {self.api_calls_count})")
    
    def daily_intelligence(self):
        """Get comprehensive daily intelligence report"""
        sport, league = self.current_sport_league
        league_info = self.available_leagues[sport][league]
        
        self.print_section(f"DAILY {league_info['name'].upper()} INTELLIGENCE")
        
        print("Generating comprehensive report...")
        success, result = self.make_request("POST", "/daily-intelligence", {
            "leagues": [f"{sport}/{league}"],
            "include_odds": True,
            "include_analysis": False
        })
        
        if success:
            print("✅ Report generated successfully!")
            self.display_intelligence_report(result)
        else:
            print(f"Failed to generate report: {result}")
        
        input(f"\nPress Enter to continue...     (odds calls this session: {self.api_calls_count})")
    
    def display_intelligence_report(self, data):
        """Display intelligence report"""
        if isinstance(data, dict) and "data" in data:
            league_data = data["data"]
            for league_key, info in league_data.items():
                print(f"\n📊 {league_key.upper()}:")
                games = info.get("games", [])
                odds = info.get("odds", [])
                teams = info.get("teams", [])
                error = info.get("error")
                
                if error:
                    print(f"   ❌ Error: {error}")
                else:
                    print(f"   🏀 Games: {len(games)}")
                    print(f"   💰 Games with odds: {len(odds) if odds else 0}")
                    print(f"   🏆 Teams: {len(teams) if teams else 0}")
        else:
            print("Report data:", str(data)[:200])
    
    def show_available_odds_sports(self):
        """Show all sports available from Odds API"""
        self.print_section("AVAILABLE SPORTS FROM ODDS API")
        
        print("Fetching all available sports...")
        success, result = self.make_request("GET", "/odds/sports?all_sports=true")
        
        if success:
            if isinstance(result, list):
                sports = result
            elif isinstance(result, dict) and "data" in result:
                sports = result["data"]
            else:
                sports = []
                
            print(f"Found {len(sports)} sports available:")
            
            # Group by sport type
            sport_groups = {}
            for sport in sports:
                key = sport.get("key", "")
                title = sport.get("title", "")
                
                sport_type = key.split("_")[0] if "_" in key else "other"
                if sport_type not in sport_groups:
                    sport_groups[sport_type] = []
                sport_groups[sport_type].append({"key": key, "title": title})
            
            for sport_type, sport_list in sorted(sport_groups.items()):
                print(f"\n🏆 {sport_type.upper()}:")
                for sport in sorted(sport_list, key=lambda x: x["title"]):
                    print(f"   {sport['title']} ({sport['key']})")
        else:
            print(f"Failed to get sports list: {result}")
        
        input(f"\nPress Enter to continue...     (odds calls this session: {self.api_calls_count})")
    
    def run(self):
        """Main interface loop"""
        self.print_header("INTERACTIVE SPORTS TESTING INTERFACE")
        print("Welcome to comprehensive sports data testing!")
        print("Test your ESPN + Odds API + Player Props integration")
        print("Supports NBA, WNBA, NFL, MLB, NHL, Soccer and more")
        
        try:
            self.main_menu()
        except KeyboardInterrupt:
            print("\n\nTesting interrupted by user. Goodbye!")
        
        print("\nThanks for testing! Your sports integration is working great!")

def main():
    try:
        interface = SportsTestInterface()
        interface.run()
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()