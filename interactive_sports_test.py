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
                print("6. Get Team Statistics")
                print("7. Get Player Statistics") 
                print("8. Deep Dive on Specific Game")
                print("9. Search for Specific Player")
                print("10. Full Daily Intelligence Report")
                print("11. Available Sports from Odds API")
                print("\n🎯 VALUE BETTING:")
                print("12. Game Analysis (Stats vs Props)")
                print("13. Player Matching Review")
                print("14. Confirm Player Matches")
                print("15. Full Value Betting Analysis (Advanced)")
            
            print("\nOTHER:")
            print("0. Quit")
            
            max_option = 15 if self.current_sport_league else 1
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
                    self.get_team_stats()
                elif choice == '7':
                    self.get_player_stats()
                elif choice == '8':
                    self.deep_dive_game()
                elif choice == '9':
                    self.search_player()
                elif choice == '10':
                    self.daily_intelligence()
                elif choice == '11':
                    self.show_available_odds_sports()
                elif choice == '12':
                    self.game_analysis_stats_vs_props()
                elif choice == '13':
                    self.player_matching_review()
                elif choice == '14':
                    self.confirm_player_matches()
                elif choice == '15':
                    self.value_betting_analysis()
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
        
        self.print_section(f"{league_info['name'].upper()} PLAYER PROPS")
        
        # First get available games with odds using multi-key system
        print("1. Finding games with player props...")
        
        all_games = self.get_all_odds_for_league(sport, league, "h2h")
        games = self.extract_games_from_odds(all_games)
        
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
                self.get_game_player_props(selected_game, sport, league)
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid input")
        
        input(f"\nPress Enter to continue...     (odds calls this session: {self.api_calls_count})")
    
    def get_game_player_props(self, game, sport, league):
        """Get player props for a specific game"""
        event_id = game.get("id")
        home = game.get("home_team", "Home")
        away = game.get("away_team", "Away")
        
        print(f"\n2. Getting player props for {away} @ {home}...")
        
        # Use sport-specific markets based on specification
        if sport == "baseball":
            markets = "batter_hits,batter_home_runs,batter_total_bases,pitcher_strikeouts"
        elif sport == "football":
            markets = "player_pass_yds,player_rush_yds,player_receptions,player_pass_tds,player_rush_tds"
        elif sport == "hockey":
            markets = "player_points,player_assists,player_shots_on_goal,player_saves"
        elif sport == "soccer":
            markets = "player_shots,player_shots_on_target,player_goals,player_assists"
        else:
            # Basketball (NBA, WNBA)
            markets = "player_points,player_rebounds,player_assists,player_threes,player_steals,player_blocks"
        
        # Try each odds key until we find one with player props
        league_info = self.available_leagues[sport][league]
        success = False
        result = None
        
        for odds_key in league_info['odds_keys']:
            success, result = self.make_request("POST", "/odds/event-odds", {
                "sport": odds_key,
                "event_id": event_id,
                "regions": "us",
                "markets": markets,
                "odds_format": "american"
            })
            
            if success:
                # Check if we actually got player props data
                if isinstance(result, dict) and "data" in result:
                    event_data = result["data"]
                elif isinstance(result, dict):
                    event_data = result
                else:
                    continue
                    
                if event_data.get("bookmakers"):
                    print(f"   Found player props using {odds_key}")
                    break
            
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
    
    def get_team_stats(self):
        """Get team statistics for the selected league"""
        sport, league = self.current_sport_league
        league_info = self.available_leagues[sport][league]
        
        self.print_section(f"{league_info['name'].upper()} TEAM STATISTICS")
        
        print(f"Fetching {league_info['name']} team statistics from ESPN...")
        
        success, result = self.make_request("POST", "/espn/team-stats", {
            "sport": sport,
            "league": league
        })
        
        if success and result.get("ok"):
            team_data = result.get("data", {})
            team_stats = team_data.get("team_stats", {})
            
            if isinstance(team_stats, dict) and "sports" in team_stats:
                # Extract teams from ESPN structure
                sports = team_stats.get("sports", [])
                if sports and len(sports) > 0:
                    leagues = sports[0].get("leagues", [])
                    if leagues and len(leagues) > 0:
                        teams = leagues[0].get("teams", [])
                        
                        print(f"Found statistics for {len(teams)} teams")
                        
                        # Show first 5 teams as examples
                        for i, team in enumerate(teams[:5]):
                            team_info = team.get("team", {})
                            name = team_info.get("displayName", "Unknown Team")
                            print(f"\n{i+1}. {name}")
                            
                            # Show basic team info
                            if "record" in team_info:
                                record = team_info["record"]
                                if "items" in record and record["items"]:
                                    wins = record["items"][0].get("stats", [])
                                    if len(wins) >= 2:
                                        w = wins[0].get("value", 0)
                                        l = wins[1].get("value", 0)
                                        print(f"   Record: {w}-{l}")
                        
                        if len(teams) > 5:
                            print(f"\n... and {len(teams) - 5} more teams")
                    else:
                        print("No team data found in league structure")
                else:
                    print("No sports data found")
            else:
                print("No team statistics available")
        else:
            error_msg = result.get("message", "Unknown error") if isinstance(result, dict) else str(result)
            print(f"Failed to get team stats: {error_msg}")
        
        input(f"\nPress Enter to continue...     (odds calls this session: {self.api_calls_count})")
    
    def get_player_stats(self):
        """Get player statistics based on sport specification"""
        sport, league = self.current_sport_league
        league_info = self.available_leagues[sport][league]
        
        self.print_section(f"{league_info['name'].upper()} PLAYER STATISTICS")
        
        # Get sport-specific player metrics based on specification
        sport_metrics = self.get_sport_specific_metrics(sport)
        
        print(f"Target metrics for {league_info['name']}:")
        for metric in sport_metrics:
            print(f"  • {metric}")
        
        print(f"\nTo get player stats, you need a specific player ID.")
        print("This would typically come from team rosters or game summaries.")
        print("\nExample player IDs:")
        
        # Show example player IDs based on sport
        if sport == "basketball":
            print("  • LeBron James: 1966")
            print("  • Stephen Curry: 3975")
        elif sport == "football":
            print("  • Patrick Mahomes: 3139477")
            print("  • Josh Allen: 3918298")
        elif sport == "baseball":
            print("  • Aaron Judge: 11579")
            print("  • Mike Trout: 9961")
        
        player_id = input("\nEnter player ID to test (or press Enter to skip): ").strip()
        
        if player_id:
            print(f"\nFetching stats for player ID {player_id}...")
            
            success, result = self.make_request("POST", "/espn/player-stats", {
                "sport": sport,
                "league": league,
                "player_id": player_id,
                "limit": 10  # Last 10 games per specification
            })
            
            if success and result.get("ok"):
                player_data = result.get("data", {})
                profile = player_data.get("player_profile", {})
                recent_games = player_data.get("recent_games", {})
                
                # Display player info
                if "athlete" in profile:
                    athlete = profile["athlete"]
                    name = athlete.get("displayName", "Unknown Player")
                    position = athlete.get("position", {}).get("abbreviation", "N/A")
                    
                    print(f"\n=== {name} ({position}) ===")
                    
                    # Show recent games stats
                    if recent_games and "events" in recent_games:
                        games = recent_games["events"]
                        print(f"\nRecent {len(games)} games:")
                        
                        for i, game in enumerate(games[:5], 1):
                            opponent = game.get("opponent", {}).get("displayName", "vs Unknown")
                            date = game.get("date", "Unknown date")
                            print(f"  Game {i}: {opponent} on {date}")
                            
                            # Parse sport-specific statistics
                            self.parse_game_stats(game, sport, name, position)
                    else:
                        print("No recent games data available")
                else:
                    print("Player profile not found")
            else:
                error_msg = result.get("message", "Unknown error") if isinstance(result, dict) else str(result)
                print(f"Failed to get player stats: {error_msg}")
        
        input(f"\nPress Enter to continue...     (odds calls this session: {self.api_calls_count})")
    
    def get_sport_specific_metrics(self, sport):
        """Return sport-specific metrics from specification"""
        metrics = {
            "basketball": [
                "Points", "Rebounds", "Assists", "3-Pointers Made", 
                "Steals", "Blocks", "Field Goal %", "Minutes Played"
            ],
            "football": [
                "QB: Passing Yards, Pass TDs, Completions, Interceptions",
                "RB: Rushing Yards, Rushing TDs, Receiving Yards, Receptions", 
                "WR: Receiving Yards, Receptions, Receiving TDs, Targets"
            ],
            "baseball": [
                "Batters: Hits, Home Runs, RBIs, Runs, Total Bases, AVG",
                "Pitchers: Strikeouts, Walks, Hits Allowed, ERA, Innings"
            ],
            "hockey": [
                "Goals", "Assists", "Points", "Shots on Goal", 
                "Plus/Minus", "Penalty Minutes", "Time on Ice"
            ],
            "soccer": [
                "Goals", "Assists", "Shots", "Shots on Target",
                "Passes", "Tackles", "Cards"
            ]
        }
        
        return metrics.get(sport, ["General statistics"])
    
    def parse_game_stats(self, game, sport, player_name, position):
        """Parse game statistics based on sport specification"""
        if not game.get("statistics"):
            print("    No statistics available for this game")
            return
        
        stats = game.get("statistics", [])
        if not isinstance(stats, list):
            print("    Statistics format not recognized")
            return
        
        print(f"    Statistics for {player_name}:")
        
        # Parse based on sport specification
        if sport == "basketball":
            self.parse_basketball_stats(stats)
        elif sport == "football":
            self.parse_football_stats(stats, position)
        elif sport == "baseball":
            self.parse_baseball_stats(stats, position)
        elif sport == "hockey":
            self.parse_hockey_stats(stats)
        elif sport == "soccer":
            self.parse_soccer_stats(stats)
        else:
            print(f"    Raw stats: {stats[:3] if len(stats) > 3 else stats}")
    
    def parse_basketball_stats(self, stats):
        """Parse basketball statistics according to specification"""
        # Target: Points, Rebounds, Assists, 3PM, Steals, Blocks, FG%, Minutes
        target_stats = {
            "points": "Points",
            "rebounds": "Rebounds", 
            "assists": "Assists",
            "threePointFieldGoalsMade": "3-Pointers Made",
            "steals": "Steals",
            "blocks": "Blocks",
            "fieldGoalPct": "Field Goal %",
            "minutes": "Minutes Played"
        }
        
        found_stats = {}
        for stat in stats:
            if isinstance(stat, dict):
                name = stat.get("name", "")
                value = stat.get("value", 0)
                
                for key, label in target_stats.items():
                    if key.lower() in name.lower():
                        found_stats[label] = value
        
        if found_stats:
            for label, value in found_stats.items():
                print(f"      {label}: {value}")
        else:
            print(f"      Available stats: {[stat.get('name', 'Unknown') for stat in stats[:5]]}")
    
    def parse_football_stats(self, stats, position):
        """Parse football statistics by position according to specification"""
        if not position:
            position = "Unknown"
        
        position = position.upper()
        
        if "QB" in position or "QUARTERBACK" in position:
            # QB stats: Passing Yards, Pass TDs, Completions, Interceptions, Rush Yards
            target_stats = {
                "passingYards": "Passing Yards",
                "passingTouchdowns": "Passing TDs", 
                "completions": "Completions",
                "interceptions": "Interceptions",
                "rushingYards": "Rushing Yards"
            }
        elif "RB" in position or "RUNNING" in position:
            # RB stats: Rush Yards, Rush TDs, Rec Yards, Receptions, Total TDs
            target_stats = {
                "rushingYards": "Rushing Yards",
                "rushingTouchdowns": "Rushing TDs",
                "receivingYards": "Receiving Yards", 
                "receptions": "Receptions",
                "touchdowns": "Total TDs"
            }
        elif "WR" in position or "WIDE" in position or "TE" in position:
            # WR/TE stats: Rec Yards, Receptions, Rec TDs, Targets
            target_stats = {
                "receivingYards": "Receiving Yards",
                "receptions": "Receptions",
                "receivingTouchdowns": "Receiving TDs",
                "targets": "Targets"
            }
        else:
            # General football stats
            target_stats = {
                "yards": "Yards",
                "touchdowns": "Touchdowns"
            }
        
        found_stats = {}
        for stat in stats:
            if isinstance(stat, dict):
                name = stat.get("name", "")
                value = stat.get("value", 0)
                
                for key, label in target_stats.items():
                    if key.lower() in name.lower():
                        found_stats[label] = value
        
        print(f"      Position: {position}")
        if found_stats:
            for label, value in found_stats.items():
                print(f"      {label}: {value}")
        else:
            print(f"      Available stats: {[stat.get('name', 'Unknown') for stat in stats[:5]]}")
    
    def parse_baseball_stats(self, stats, position):
        """Parse baseball statistics according to specification"""
        if position and ("P" in position.upper() or "PITCHER" in position.upper()):
            # Pitcher stats: Strikeouts, Walks, Hits Allowed, ERA, Innings
            target_stats = {
                "strikeouts": "Strikeouts",
                "walks": "Walks Allowed",
                "hitsAllowed": "Hits Allowed",
                "era": "ERA",
                "inningsPitched": "Innings Pitched"
            }
        else:
            # Batter stats: Hits, HRs, RBIs, Runs, Total Bases, AVG
            target_stats = {
                "hits": "Hits",
                "homeRuns": "Home Runs",
                "rbi": "RBIs", 
                "runs": "Runs Scored",
                "totalBases": "Total Bases",
                "battingAverage": "Batting Average"
            }
        
        found_stats = {}
        for stat in stats:
            if isinstance(stat, dict):
                name = stat.get("name", "")
                value = stat.get("value", 0)
                
                for key, label in target_stats.items():
                    if key.lower() in name.lower():
                        found_stats[label] = value
        
        if found_stats:
            for label, value in found_stats.items():
                print(f"      {label}: {value}")
        else:
            print(f"      Available stats: {[stat.get('name', 'Unknown') for stat in stats[:5]]}")
    
    def parse_hockey_stats(self, stats):
        """Parse hockey statistics according to specification"""
        # Goals, Assists, Points, Shots on Goal, +/-, PIM, TOI
        target_stats = {
            "goals": "Goals",
            "assists": "Assists",
            "points": "Points",
            "shotsOnGoal": "Shots on Goal",
            "plusMinus": "Plus/Minus",
            "penaltyMinutes": "Penalty Minutes",
            "timeOnIce": "Time on Ice"
        }
        
        found_stats = {}
        for stat in stats:
            if isinstance(stat, dict):
                name = stat.get("name", "")
                value = stat.get("value", 0)
                
                for key, label in target_stats.items():
                    if key.lower() in name.lower():
                        found_stats[label] = value
        
        if found_stats:
            for label, value in found_stats.items():
                print(f"      {label}: {value}")
        else:
            print(f"      Available stats: {[stat.get('name', 'Unknown') for stat in stats[:5]]}")
    
    def parse_soccer_stats(self, stats):
        """Parse soccer statistics according to specification"""
        # Goals, Assists, Shots, Shots on Target, Passes, Tackles, Cards
        target_stats = {
            "goals": "Goals",
            "assists": "Assists", 
            "shots": "Shots",
            "shotsOnTarget": "Shots on Target",
            "passes": "Passes",
            "tackles": "Tackles",
            "cards": "Cards"
        }
        
        found_stats = {}
        for stat in stats:
            if isinstance(stat, dict):
                name = stat.get("name", "")
                value = stat.get("value", 0)
                
                for key, label in target_stats.items():
                    if key.lower() in name.lower():
                        found_stats[label] = value
        
        if found_stats:
            for label, value in found_stats.items():
                print(f"      {label}: {value}")
        else:
            print(f"      Available stats: {[stat.get('name', 'Unknown') for stat in stats[:5]]}")
    
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
    
    def game_analysis_stats_vs_props(self):
        """Focused analysis: Pick a game, see stats vs props for individual players"""
        sport, league = self.current_sport_league
        league_info = self.available_leagues[sport][league]
        
        self.print_section(f"{league_info['name'].upper()} GAME ANALYSIS - STATS VS PROPS")
        
        print(f"This will help you manually spot value bets by comparing stats to props")
        print(f"Much more accurate than automated analysis")
        
        # Step 1: Get games for today with odds
        print(f"\n1. Getting today's {league_info['name']} games with odds...")
        
        all_games = self.get_all_odds_for_league(sport, league, "h2h")
        games = self.extract_games_from_odds(all_games)
        
        if not games:
            print("No games with odds found for today")
            input("Press Enter to continue...")
            return
        
        print(f"Found {len(games)} games today. Select one to analyze:")
        
        # Step 2: Let user pick a game
        for i, game in enumerate(games, 1):
            home = game.get("home_team", "Home")
            away = game.get("away_team", "Away")
            start_time = game.get("commence_time", "TBD")
            print(f"  {i}. {away} @ {home} ({start_time})")
        
        try:
            choice = int(input(f"\nSelect game (1-{len(games)}): ")) - 1
            if not (0 <= choice < len(games)):
                print("Invalid selection")
                input("Press Enter to continue...")
                return
                
            selected_game = games[choice]
            
        except ValueError:
            print("Invalid input")
            input("Press Enter to continue...")
            return
        
        # Step 3: Show game odds (moneyline, spread, total)
        home = selected_game.get("home_team", "Home")
        away = selected_game.get("away_team", "Away")
        start_time = selected_game.get("commence_time", "TBD")
        
        print(f"\n2. GAME ODDS: {away} @ {home}")
        print(f"   Start Time: {start_time}")
        print("   " + "=" * 50)
        
        self.display_game_odds(selected_game, ["h2h", "spreads", "totals"])
        
        # Step 4: Get player props for this specific game
        print(f"\n3. Getting player props for this game...")
        
        event_id = selected_game.get("id")
        if not event_id:
            print("No event ID found for this game")
            input("Press Enter to continue...")
            return
        
        # Use sport-specific markets
        if sport == "baseball":
            markets = "batter_hits,batter_home_runs,batter_total_bases,pitcher_strikeouts"
        elif sport == "football":
            markets = "player_pass_yds,player_rush_yds,player_receptions,player_pass_tds"
        elif sport == "hockey":
            markets = "player_points,player_assists,player_shots_on_goal"
        elif sport == "soccer":
            markets = "player_shots,player_goals,player_assists"
        else:
            # Basketball
            markets = "player_points,player_rebounds,player_assists,player_threes"
        
        # Try to get player props
        props_data = None
        
        for odds_key in league_info['odds_keys']:
            success, result = self.make_request("POST", "/odds/event-odds", {
                "sport": odds_key,
                "event_id": event_id,
                "regions": "us",
                "markets": markets,
                "odds_format": "american"
            })
            
            if success and result:
                if isinstance(result, dict) and "data" in result:
                    props_data = result["data"]
                else:
                    props_data = result
                    
                if props_data and props_data.get("bookmakers"):
                    print(f"   Found player props using {odds_key}")
                    break
                    
        if not props_data or not props_data.get("bookmakers"):
            print("No player props available for this game")
            input("Press Enter to continue...")
            return
        
        # Step 5: Extract all unique players
        all_players = {}  # player_name: {props: [...], books: [...]}
        
        for bookmaker in props_data.get("bookmakers", []):
            book_name = bookmaker.get("title", "Unknown")
            
            for market in bookmaker.get("markets", []):
                market_key = market.get("key", "")
                
                for outcome in market.get("outcomes", []):
                    player_name = outcome.get("description", "")
                    if not player_name:
                        continue
                    
                    if player_name not in all_players:
                        all_players[player_name] = {"props": [], "books": set()}
                    
                    prop_info = {
                        "market": market_key,
                        "bet_type": outcome.get("name", ""),
                        "line": outcome.get("point", ""),
                        "odds": outcome.get("price", "N/A"),
                        "bookmaker": book_name
                    }
                    
                    all_players[player_name]["props"].append(prop_info)
                    all_players[player_name]["books"].add(book_name)
        
        if not all_players:
            print("No player props found")
            input("Press Enter to continue...")
            return
        
        # Step 6: Show players and let user select
        players_list = sorted(all_players.keys())
        print(f"\n4. PLAYERS WITH PROPS ({len(players_list)} found):")
        
        for i, player in enumerate(players_list, 1):
            prop_count = len(all_players[player]["props"])
            books = ", ".join(list(all_players[player]["books"])[:2])
            print(f"  {i}. {player} ({prop_count} props at {books})")
        
        print(f"\n{len(players_list) + 1}. Show props for all players")
            
        try:
            choice = int(input(f"\nSelect player or option (1-{len(players_list) + 1}): "))
            
            if choice == len(players_list) + 1:
                # Show all players' props
                for player, player_data in all_players.items():
                    print(f"\n=== {player.upper()} ===")
                    for prop in player_data["props"]:
                        market_label = self.get_market_label(prop["market"])
                        print(f"  {market_label}: {prop['bet_type']} {prop['line']} at {prop['odds']} ({prop['bookmaker']})")
                input("Press Enter to continue...")
                return
                
            elif 1 <= choice <= len(players_list):
                selected_player = players_list[choice - 1]
                # Step 7: Show player props AND recent stats side by side
                self.show_player_stats_vs_props(selected_player, all_players[selected_player], sport, league)
            else:
                print("Invalid selection")
                
        except ValueError:
            print("Invalid input")
        
        input(f"\nPress Enter to continue...     (odds calls this session: {self.api_calls_count})")
    
    def show_player_stats_vs_props(self, player_name, player_data, sport, league):
        """Show player's recent stats alongside their betting props"""
        self.print_section(f"{player_name.upper()} - STATS vs PROPS")
        
        print(f"Manual value analysis for {player_name}")
        print(f"Compare recent performance to betting lines")
        
        # Show props first
        print(f"\n1. BETTING PROPS:")
        props = player_data["props"]
        
        # Group props by market
        props_by_market = {}
        for prop in props:
            market = prop["market"]
            if market not in props_by_market:
                props_by_market[market] = []
            props_by_market[market].append(prop)
        
        for market, market_props in props_by_market.items():
            market_label = self.get_market_label(market)
            print(f"\n   {market_label}:")
            
            for prop in market_props:
                bet_type = prop["bet_type"]
                line = prop["line"]
                odds = prop["odds"]
                book = prop["bookmaker"]
                print(f"      {bet_type} {line}: {odds} ({book})")
        
        # Try to get player stats
        print(f"\n2. RECENT STATS:")
        
        # First try to match player to ESPN ID if using new system
        sport_key_map = {
            "basketball": "basketball_nba" if league == "nba" else "basketball_wnba",
            "football": "americanfootball_nfl",
            "baseball": "baseball_mlb",
            "hockey": "icehockey_nhl"
        }
        
        sport_key = sport_key_map.get(sport, f"{sport}_{league}")
        
        # Try player matching
        match_success, match_result = self.make_request("POST", "/player/match", {
            "odds_player_name": player_name,
            "sport_key": sport_key
        })
        
        recent_stats = None
        if match_success and match_result.get("match_found"):
            match = match_result.get("match", {})
            espn_id = match.get("espn_id")
            espn_name = match.get("espn_name")
            team = match.get("team", "Unknown")
            
            print(f"   Matched: {player_name} -> {espn_name} (ID: {espn_id})")
            print(f"   Team: {team}")
            
            # Get recent stats
            stats_success, stats_result = self.make_request("POST", "/espn/player-stats", {
                "sport": sport,
                "league": league,
                "player_id": espn_id,
                "limit": 10
            })
            
            if stats_success and stats_result.get("ok"):
                recent_stats = stats_result.get("data", {})
                recent_games = recent_stats.get("recent_games", {})
                
                if recent_games and "events" in recent_games:
                    games = recent_games["events"]
                    print(f"   Found {len(games)} recent games")
                    
                    # Show basic stats if available
                    self.display_simplified_stats(games, sport)
                else:
                    print(f"   No recent games data available")
            else:
                print(f"   Could not get stats")
        else:
            print(f"   No ESPN match found for {player_name}")
            print(f"   Manual stats lookup needed")
        
        print(f"\n3. VALUE ANALYSIS:")
        print(f"   Compare the recent averages above to the betting lines")
        print(f"   Look for lines significantly below recent performance")
        
    def display_simplified_stats(self, games, sport):
        """Display simplified recent stats for manual comparison"""
        if not games:
            return
            
        # Track stats across games
        stat_totals = {}
        valid_games = 0
        
        for game in games[:10]:  # Last 10 games
            stats = game.get("statistics", [])
            if not isinstance(stats, list):
                continue
                
            valid_games += 1
            
            for stat in stats:
                if not isinstance(stat, dict):
                    continue
                    
                stat_name = stat.get("name", "").lower()
                stat_value = stat.get("value", 0)
                
                try:
                    stat_value = float(stat_value)
                except:
                    continue
                
                # Map stat names to common categories based on sport
                key = None
                if sport == "baseball":
                    if "hits" in stat_name:
                        key = "hits"
                    elif "home runs" in stat_name or "homeruns" in stat_name:
                        key = "home_runs"
                    elif "rbi" in stat_name:
                        key = "rbis"
                    elif "strikeouts" in stat_name:
                        key = "strikeouts"
                    elif "total bases" in stat_name:
                        key = "total_bases"
                elif sport in ["basketball"]:
                    if "points" in stat_name:
                        key = "points"
                    elif "rebounds" in stat_name:
                        key = "rebounds"
                    elif "assists" in stat_name:
                        key = "assists"
                elif sport == "football":
                    if "passing yards" in stat_name:
                        key = "pass_yds"
                    elif "rushing yards" in stat_name:
                        key = "rush_yds"
                    elif "receptions" in stat_name:
                        key = "receptions"
                
                if key:
                    if key not in stat_totals:
                        stat_totals[key] = []
                    stat_totals[key].append(stat_value)
        
        if stat_totals and valid_games > 0:
            print(f"   Recent averages ({valid_games} games):")
            for key, values in stat_totals.items():
                if values:
                    avg = sum(values) / len(values)
                    print(f"      {key.replace('_', ' ').title()}: {avg:.1f}")
        else:
            print(f"   Could not extract key stats - manual lookup recommended")
    
    def value_betting_analysis(self):
        """Analyze player props for value betting opportunities"""
        sport, league = self.current_sport_league
        league_info = self.available_leagues[sport][league]
        
        self.print_section(f"🎯 {league_info['name'].upper()} VALUE BETTING ANALYSIS")
        
        # Get sport key for odds API
        sport_key = league_info['odds_keys'][0]  # Use primary odds key
        
        print(f"🔍 Analyzing {league_info['name']} player props vs recent performance...")
        print(f"📊 Using sport key: {sport_key}")
        
        # Set sport-specific player markets
        if sport == "baseball":
            markets = "batter_hits,batter_home_runs,batter_total_bases,pitcher_strikeouts"
        elif sport == "football":
            markets = "player_pass_yds,player_rush_yds,player_receptions,player_pass_tds,player_rush_tds"
        elif sport == "hockey":
            markets = "player_points,player_assists,player_shots_on_goal"
        elif sport == "soccer":
            markets = "player_shots,player_shots_on_target,player_goals,player_assists"
        else:
            # Basketball (NBA, WNBA)
            markets = "player_points,player_rebounds,player_assists,player_threes"
        
        print(f"🎯 Analyzing markets: {markets.replace(',', ', ')}")
        
        # Get value analysis from API
        success, result = self.make_request("POST", "/value-betting/analyze", {
            "sport_key": sport_key,
            "player_markets": markets,
            "min_confidence": 0.8,
            "value_threshold": 1.1,  # Need 10% edge
            "regions": "us",
            "odds_format": "american"
        })
        
        if success and result.get("status") == "success":
            value_bets = result.get("value_bets", [])
            unmatched_players = result.get("unmatched_players", [])
            analysis_params = result.get("analysis_params", {})
            
            print(f"\n📈 ANALYSIS RESULTS:")
            print(f"   Min Confidence: {analysis_params.get('min_confidence', 0.8)}")
            print(f"   Value Threshold: {analysis_params.get('value_threshold', 1.1)}")
            print(f"   Markets: {analysis_params.get('markets', 'N/A')}")
            
            # Display value bets
            if value_bets:
                print(f"\n✅ FOUND {len(value_bets)} VALUE BETS:")
                print("=" * 60)
                
                for i, bet in enumerate(value_bets, 1):
                    player_name = bet.get("player_name", "Unknown")
                    espn_name = bet.get("espn_name", "Unknown") 
                    market = bet.get("market", "unknown")
                    betting_line = bet.get("betting_line", 0)
                    odds = bet.get("odds", "N/A")
                    bookmaker = bet.get("bookmaker", "Unknown")
                    team = bet.get("team", "Unknown")
                    position = bet.get("position", "")
                    
                    value_analysis = bet.get("value_analysis", {})
                    recent_avg = value_analysis.get("recent_average", 0)
                    difference = value_analysis.get("difference", 0)
                    percentage_above = value_analysis.get("percentage_above", 0)
                    confidence = value_analysis.get("confidence", "unknown")
                    games_analyzed = value_analysis.get("games_analyzed", 0)
                    
                    # Format market display
                    market_display = self.get_market_label(market)
                    
                    print(f"\n{i}. 🏆 {espn_name} ({team})")
                    if position:
                        print(f"   Position: {position}")
                    print(f"   📊 Market: {market_display}")
                    print(f"   🎯 Bet: Over {betting_line} at {odds} ({bookmaker})")
                    print(f"   📈 Recent Average: {recent_avg} ({games_analyzed} games)")
                    print(f"   💡 Edge: +{difference} ({percentage_above:+.1f}% above line)")
                    print(f"   🎪 Confidence: {confidence.upper()}")
                    
                    # Game context if available
                    game_info = bet.get("game", {})
                    if game_info.get("home_team") and game_info.get("away_team"):
                        home = game_info["home_team"]
                        away = game_info["away_team"]
                        print(f"   🏟️  Game: {away} @ {home}")
            else:
                print(f"\n❌ NO VALUE BETS FOUND")
                print("   All player props appear to be fairly priced or overpriced")
                
            # Display unmatched players  
            if unmatched_players:
                print(f"\n🤔 UNMATCHED PLAYERS ({len(unmatched_players)}):")
                print("   (These players need manual matching review)")
                print("-" * 50)
                
                for i, unmatched in enumerate(unmatched_players[:10], 1):  # Show first 10
                    player_name = unmatched.get("player_name", "Unknown")
                    match_result = unmatched.get("match_result")
                    game_info = unmatched.get("game", {})
                    
                    if match_result:
                        confidence = match_result.get("confidence", 0)
                        espn_name = match_result.get("espn_name", "Unknown")
                        print(f"   {i}. {player_name} → {espn_name} ({confidence:.0%} confidence)")
                    else:
                        print(f"   {i}. {player_name} → No ESPN match found")
                        
                    if game_info.get("home_team") and game_info.get("away_team"):
                        print(f"      Game: {game_info['away_team']} @ {game_info['home_team']}")
                
                if len(unmatched_players) > 10:
                    print(f"   ... and {len(unmatched_players) - 10} more")
                    
                print(f"\n💡 Use menu option 13 (Player Matching Review) to confirm matches")
                
        else:
            error_msg = result.get("message", "Unknown error") if isinstance(result, dict) else str(result)
            print(f"\n❌ Analysis failed: {error_msg}")
            
        input(f"\nPress Enter to continue...     (odds calls this session: {self.api_calls_count})")
    
    def player_matching_review(self):
        """Review and confirm pending player matches"""
        self.print_section("🔍 PLAYER MATCHING REVIEW")
        
        print("📋 Getting pending player matches...")
        success, result = self.make_request("GET", "/player/pending")
        
        if success and result.get("status") == "success":
            pending_matches = result.get("pending_matches", {})
            stats = result.get("stats", {})
            
            print(f"\n📊 MATCH STATISTICS:")
            print(f"   ✅ Confirmed matches: {stats.get('confirmed_matches', 0)}")
            print(f"   ⏳ Pending matches: {stats.get('pending_matches', 0)}")
            print(f"   🏆 Sports covered: {', '.join(stats.get('sports_covered', []))}")
            
            if not pending_matches:
                print(f"\n🎉 No pending matches to review!")
                print("   All player matches have been confirmed.")
                input(f"\nPress Enter to continue...")
                return
            
            # Display pending matches by sport
            total_pending = 0
            for sport_key, players in pending_matches.items():
                if not players:
                    continue
                    
                sport_display = sport_key.replace("_", " ").title()
                print(f"\n🏈 {sport_display}:")
                print("-" * 40)
                
                for i, (odds_name, match_info) in enumerate(players.items(), 1):
                    espn_name = match_info.get("espn_name", "Unknown")
                    espn_id = match_info.get("espn_id", "Unknown")
                    team = match_info.get("team", "Unknown Team")
                    position = match_info.get("position", "")
                    confidence = match_info.get("confidence", 0)
                    status = match_info.get("status", "pending")
                    
                    if status == "rejected":
                        continue  # Skip rejected matches
                    
                    total_pending += 1
                    print(f"   {total_pending}. \"{odds_name}\" → {espn_name} (ID: {espn_id})")
                    print(f"      Team: {team}")
                    if position:
                        print(f"      Position: {position}")
                    print(f"      Confidence: {confidence:.0%}")
            
            if total_pending == 0:
                print(f"\n✅ All matches have been processed!")
            else:
                print(f"\n💡 Found {total_pending} pending matches")
                print("   Use menu option 14 (Confirm Player Matches) to confirm them")
                
        else:
            error_msg = result.get("message", "Unknown error") if isinstance(result, dict) else str(result)
            print(f"\n❌ Failed to get pending matches: {error_msg}")
            
        input(f"\nPress Enter to continue...")
    
    def confirm_player_matches(self):
        """Confirm or reject pending player matches"""
        self.print_section("✅ CONFIRM PLAYER MATCHES")
        
        # Get pending matches first
        success, result = self.make_request("GET", "/player/pending")
        
        if not success or result.get("status") != "success":
            print("❌ Could not retrieve pending matches")
            input("Press Enter to continue...")
            return
            
        pending_matches = result.get("pending_matches", {})
        
        # Collect all pending matches
        all_matches = []
        for sport_key, players in pending_matches.items():
            for odds_name, match_info in players.items():
                if match_info.get("status") != "rejected":
                    all_matches.append({
                        "sport_key": sport_key,
                        "odds_name": odds_name,
                        "match_info": match_info
                    })
        
        if not all_matches:
            print("🎉 No pending matches to confirm!")
            input("Press Enter to continue...")
            return
            
        print(f"📋 Found {len(all_matches)} pending matches to review:")
        print("=" * 60)
        
        # Display matches for confirmation
        for i, match in enumerate(all_matches, 1):
            sport_key = match["sport_key"]
            odds_name = match["odds_name"]
            match_info = match["match_info"]
            
            espn_name = match_info.get("espn_name", "Unknown")
            espn_id = match_info.get("espn_id", "Unknown")
            team = match_info.get("team", "Unknown")
            position = match_info.get("position", "")
            confidence = match_info.get("confidence", 0)
            
            sport_display = sport_key.replace("_", " ").title()
            
            print(f"\n{i}. {sport_display}")
            print(f"   Odds Name: \"{odds_name}\"")
            print(f"   ESPN Match: {espn_name} (ID: {espn_id})")
            print(f"   Team: {team}")
            if position:
                print(f"   Position: {position}")
            print(f"   Confidence: {confidence:.0%}")
            
            # Ask for confirmation
            while True:
                choice = input(f"   ✅ Confirm this match? (y/n/s=skip): ").lower().strip()
                
                if choice == 'y':
                    # Confirm the match
                    success, result = self.make_request("POST", "/player/confirm", {
                        "odds_player_name": odds_name,
                        "sport_key": sport_key,
                        "espn_id": espn_id,
                        "verified_by": "interactive_client"
                    })
                    
                    if success and result.get("status") == "success":
                        print(f"   ✅ Confirmed: {odds_name} → {espn_name}")
                    else:
                        error_msg = result.get("message", "Unknown error") if isinstance(result, dict) else str(result)
                        print(f"   ❌ Failed to confirm: {error_msg}")
                    break
                    
                elif choice == 'n':
                    # Reject the match
                    success, result = self.make_request("POST", "/player/reject", {
                        "odds_player_name": odds_name,
                        "sport_key": sport_key
                    })
                    
                    if success:
                        print(f"   ❌ Rejected match for {odds_name}")
                    else:
                        print(f"   ⚠️  Could not reject match (continuing anyway)")
                    break
                    
                elif choice == 's':
                    print(f"   ⏭️  Skipped {odds_name}")
                    break
                    
                else:
                    print("   Please enter 'y' (yes), 'n' (no), or 's' (skip)")
        
        print(f"\n🎉 Match confirmation complete!")
        print("   Confirmed matches will be used in future value betting analysis")
        
        input(f"\nPress Enter to continue...")
    
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