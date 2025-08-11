#!/usr/bin/env python3
"""
Simple Sports Testing Script

Interactive league selection and game fetching.
Focus on getting games with event IDs for today.
"""

import requests
import json
from datetime import datetime
import pytz

# Railway MCP configuration
RAILWAY_URL = "https://web-production-b939f.up.railway.app"
API_KEY = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# League configurations with Odds API sport keys and player prop markets
LEAGUES = {
    "1": {
        "name": "MLB", 
        "sport": "baseball", 
        "league": "mlb", 
        "odds_key": "baseball_mlb",
        "prop_markets": "batter_home_runs,batter_hits,pitcher_strikeouts"
    },
    "2": {
        "name": "NBA", 
        "sport": "basketball", 
        "league": "nba", 
        "odds_key": "basketball_nba",
        "prop_markets": "player_points,player_rebounds,player_assists,player_threes"
    },
    "3": {
        "name": "WNBA", 
        "sport": "basketball", 
        "league": "wnba", 
        "odds_key": "basketball_wnba",
        "prop_markets": "player_points,player_rebounds,player_assists,player_threes"
    },
    "4": {
        "name": "MLS", 
        "sport": "soccer", 
        "league": "usa.1", 
        "odds_key": "soccer_usa_mls",
        "prop_markets": "player_shots,player_shots_on_target"
    },
    "5": {
        "name": "EPL", 
        "sport": "soccer", 
        "league": "eng.1", 
        "odds_key": "soccer_epl",
        "prop_markets": "player_shots,player_shots_on_target"
    },
    "6": {
        "name": "NFL", 
        "sport": "football", 
        "league": "nfl", 
        "odds_key": "americanfootball_nfl",
        "prop_markets": "player_pass_yds,player_rush_yds,player_receptions"
    },
    "7": {
        "name": "NHL", 
        "sport": "hockey", 
        "league": "nhl", 
        "odds_key": "icehockey_nhl",
        "prop_markets": "player_goals,player_assists,player_shots_on_goal"
    }
}

# Global odds API call counter
odds_api_calls = 0

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def make_request(method, endpoint, data=None):
    """Make API request with error handling"""
    global odds_api_calls
    
    # Count odds API calls
    if "/odds/" in endpoint:
        odds_api_calls += 1
    
    try:
        # Handle ESPN API calls directly
        if endpoint == "/espn/scoreboard":
            return make_espn_scoreboard_request(data["sport"], data["league"])
        elif endpoint == "/espn/roster":
            return make_espn_roster_request(data["sport"], data["league"], data["team_id"])
        else:
            # Handle other endpoints (odds API)
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

def make_espn_scoreboard_request(sport, league):
    """Make direct ESPN scoreboard request"""
    try:
        # Map our league codes to ESPN URLs
        espn_path_map = {
            ("baseball", "mlb"): "/baseball/mlb/scoreboard",
            ("basketball", "nba"): "/basketball/nba/scoreboard", 
            ("basketball", "wnba"): "/basketball/wnba/scoreboard",
            ("football", "nfl"): "/football/nfl/scoreboard",
            ("hockey", "nhl"): "/hockey/nhl/scoreboard",
            ("soccer", "usa.1"): "/soccer/usa.1/scoreboard",
            ("soccer", "eng.1"): "/soccer/eng.1/scoreboard"
        }
        
        espn_path = espn_path_map.get((sport, league))
        if not espn_path:
            return False, f"Unsupported league: {sport}/{league}"
        
        url = f"https://site.api.espn.com/apis/site/v2/sports{espn_path}"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            events = data.get("events", [])
            
            # Convert ESPN format to our expected format
            return True, {
                "ok": True,
                "data": {
                    "scoreboard": events  # ESPN events are already in the right format
                }
            }
        else:
            return False, f"ESPN API error: {response.status_code}"
            
    except Exception as e:
        return False, f"ESPN request failed: {str(e)}"

def make_espn_roster_request(sport, league, team_id):
    """Make direct ESPN roster request"""
    try:
        # ESPN roster URL format
        espn_path_map = {
            ("baseball", "mlb"): "/baseball/mlb",
            ("basketball", "nba"): "/basketball/nba", 
            ("basketball", "wnba"): "/basketball/wnba",
            ("football", "nfl"): "/football/nfl",
            ("hockey", "nhl"): "/hockey/nhl",
            ("soccer", "usa.1"): "/soccer/usa.1",
            ("soccer", "eng.1"): "/soccer/eng.1"
        }
        
        espn_path = espn_path_map.get((sport, league))
        if not espn_path:
            return False, f"Unsupported league: {sport}/{league}"
        
        url = f"https://site.api.espn.com/apis/site/v2/sports{espn_path}/teams/{team_id}/roster"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Convert ESPN format to our expected format
            return True, {
                "ok": True,
                "data": data  # Return raw ESPN roster data
            }
        else:
            return False, f"ESPN roster API error: {response.status_code}"
            
    except Exception as e:
        return False, f"ESPN roster request failed: {str(e)}"

def get_current_eastern_time():
    """Get current time in Eastern timezone"""
    eastern_tz = pytz.timezone('US/Eastern')
    return datetime.now(eastern_tz)

def format_time_eastern(time_str):
    """Convert ISO time string to Eastern timezone"""
    if not time_str or time_str == "TBD":
        return "TBD"
    
    try:
        # Parse the ISO time string
        if time_str.endswith('Z'):
            # UTC time
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        else:
            # Try to parse as is
            dt = datetime.fromisoformat(time_str)
        
        # Convert to Eastern timezone
        eastern_tz = pytz.timezone('US/Eastern')
        if dt.tzinfo is None:
            # Assume UTC if no timezone info
            dt = pytz.UTC.localize(dt)
        
        eastern_time = dt.astimezone(eastern_tz)
        return eastern_time.strftime('%I:%M %p ET')
    except:
        # If parsing fails, return original
        return time_str

def select_league():
    """Let user select a league"""
    print_header("SELECT LEAGUE")
    
    current_time = get_current_eastern_time()
    print(f"Current Eastern Time: {current_time.strftime('%Y-%m-%d %I:%M %p ET')}")
    print("Getting games for today in Eastern Time\n")
    
    print("Available Leagues:")
    for key, league in LEAGUES.items():
        print(f"  {key}. {league['name']}")
    
    while True:
        choice = input(f"\nSelect league (1-{len(LEAGUES)}): ").strip()
        if choice in LEAGUES:
            return LEAGUES[choice]
        print("❌ Invalid choice. Please try again.")

def fetch_games(league_config):
    """Fetch today's games for selected league"""
    print_header(f"TODAY'S {league_config['name']} GAMES")
    
    print(f"Fetching {league_config['name']} games from ESPN...")
    print(f"Sport: {league_config['sport']}, League: {league_config['league']}")
    
    success, result = make_request("POST", "/espn/scoreboard", {
        "sport": league_config["sport"], 
        "league": league_config["league"]
    })
    
    if success and result.get("ok"):
        games = result.get("data", {}).get("scoreboard", [])
        print(f"SUCCESS: Found {len(games)} games")
        
        if games:
            print(f"\n{league_config['name']} Games Today:")
            print("-" * 50)
            
            for i, game in enumerate(games, 1):
                # Extract game info
                competitions = game.get("competitions", [{}])
                if not competitions:
                    continue
                    
                competition = competitions[0]
                competitors = competition.get("competitors", [])
                
                if len(competitors) >= 2:
                    away_team = competitors[1].get("team", {})
                    home_team = competitors[0].get("team", {})
                    
                    away = away_team.get("displayName", "Away")
                    home = home_team.get("displayName", "Home")
                    
                    # Get status and time
                    status = game.get("status", {}).get("type", {}).get("description", "Scheduled")
                    game_time = game.get("date", "TBD")
                    formatted_time = format_time_eastern(game_time)
                    
                    # Get event ID from the competition
                    event_id = competition.get("id", "No ID")
                    
                    print(f"  {i}. {away} @ {home}")
                    print(f"     Time: {formatted_time}")
                    print(f"     Status: {status}")
                    print(f"     Event ID: {event_id}")
                    print()
        
        return True, games
    else:
        print(f"FAILED: {result}")
        return False, None

def fetch_odds_for_games(league_config, games):
    """Fetch odds for the games we found"""
    print_header(f"{league_config['name']} ODDS")
    
    print(f"Fetching odds for {len(games)} {league_config['name']} games...")
    print(f"Using Odds API key: {league_config['odds_key']}")
    
    # Get all odds for this sport
    success, result = make_request("POST", "/odds/get-odds", {
        "sport": league_config["odds_key"],
        "regions": "us",
        "markets": "h2h,spreads,totals",  # moneylines, spreads, totals
        "odds_format": "american"
    })
    
    if not success:
        print(f"FAILED to get odds: {result}")
        return False, None, None
    
    # Extract odds games
    if isinstance(result, list):
        odds_games = result
    elif isinstance(result, dict) and "data" in result:
        odds_games = result["data"]
    else:
        odds_games = []
    
    print(f"Found odds for {len(odds_games)} games")
    
    if not odds_games:
        print("No odds available for today's games")
        return True, [], []
    
    # Match ESPN games to Odds games by team names
    matched_games = []
    
    for espn_game in games:
        # Get ESPN team names
        competitions = espn_game.get("competitions", [{}])
        if not competitions:
            continue
            
        competitors = competitions[0].get("competitors", [])
        if len(competitors) < 2:
            continue
            
        espn_away = competitors[1].get("team", {}).get("displayName", "").lower()
        espn_home = competitors[0].get("team", {}).get("displayName", "").lower()
        
        # Find matching odds game
        odds_match = None
        for odds_game in odds_games:
            odds_away = odds_game.get("away_team", "").lower()
            odds_home = odds_game.get("home_team", "").lower()
            
            # Simple team name matching (can be improved later)
            if (espn_away in odds_away or odds_away in espn_away) and \
               (espn_home in odds_home or odds_home in espn_home):
                odds_match = odds_game
                break
        
        if odds_match:
            # Combine ESPN and odds data
            combined_game = {
                "espn_data": espn_game,
                "odds_data": odds_match
            }
            matched_games.append(combined_game)
    
    print(f"Successfully matched {len(matched_games)} games with odds")
    
    # Display games with odds
    if matched_games:
        print(f"\n{league_config['name']} Games with Odds:")
        print("=" * 70)
        
        for i, game in enumerate(matched_games, 1):
            espn = game["espn_data"]
            odds = game["odds_data"]
            
            # Get team info
            competitors = espn.get("competitions", [{}])[0].get("competitors", [])
            away_team = competitors[1].get("team", {}).get("displayName", "Away")
            home_team = competitors[0].get("team", {}).get("displayName", "Home")
            
            # Get game info
            game_time = espn.get("date", "TBD")
            formatted_time = format_time_eastern(game_time)
            status = espn.get("status", {}).get("type", {}).get("description", "Scheduled")
            event_id = espn.get("competitions", [{}])[0].get("id", "No ID")
            
            print(f"\n{i}. {away_team} @ {home_team}")
            print(f"   Time: {formatted_time}")
            print(f"   Status: {status}")
            print(f"   Event ID: {event_id}")
            
            # Display odds
            display_game_odds(odds)
    
    # Add player props selection for active leagues
    active_leagues = ["MLB", "WNBA"]
    if league_config["name"] in active_leagues:
        print(f"\n" + "=" * 70)
        print(f"💡 Enter a game number (1-{len(matched_games)}) to view player props")
        print("   Or press Enter to continue...")
        
        choice = input("Select game for player props (or Enter to skip): ").strip()
        
        if choice.isdigit():
            game_num = int(choice) - 1
            if 0 <= game_num < len(matched_games):
                selected_game = matched_games[game_num]
                espn_game = selected_game["espn_data"]
                
                # Get Odds API event ID for this game
                print("\n⏳ Finding Odds API event ID...")
                odds_event_id = get_odds_event_id(league_config, espn_game, odds_games)
                
                if odds_event_id:
                    print("\n⏳ Fetching player props...")
                    fetch_player_props_for_game(league_config, espn_game, odds_event_id)
                else:
                    print("❌ Cannot fetch player props without Odds API event ID")
            else:
                print("❌ Invalid game number")
        else:
            print("⏭️ Skipping player props")
    
    return True, matched_games, odds_games

def display_game_odds(odds_game):
    """Display formatted odds for a game"""
    bookmakers = odds_game.get("bookmakers", [])
    if not bookmakers:
        print("   No odds available")
        return
    
    # Use first bookmaker for simplicity (can show multiple later)
    bookmaker = bookmakers[0]
    book_name = bookmaker.get("title", "Unknown")
    print(f"   Odds from {book_name}:")
    
    for market in bookmaker.get("markets", []):
        market_key = market.get("key", "")
        
        if market_key == "h2h":
            print("   📊 Moneyline:")
            for outcome in market.get("outcomes", []):
                team = outcome.get("name", "Unknown")
                odds = outcome.get("price", "N/A")
                print(f"      {team}: {odds}")
                
        elif market_key == "spreads":
            print("   🏈 Spreads:")
            for outcome in market.get("outcomes", []):
                team = outcome.get("name", "Unknown")
                spread = outcome.get("point", "N/A")
                odds = outcome.get("price", "N/A")
                spread_str = f"{spread:+}" if isinstance(spread, (int, float)) else spread
                print(f"      {team} {spread_str}: {odds}")
                
        elif market_key == "totals":
            print("   ⬆️⬇️ Totals:")
            for outcome in market.get("outcomes", []):
                bet_type = outcome.get("name", "Unknown")  # Over/Under
                total = outcome.get("point", "N/A")
                odds = outcome.get("price", "N/A")
                print(f"      {bet_type} {total}: {odds}")

def get_odds_event_id(league_config, espn_game, odds_games):
    """Get Odds API event ID from the odds games we already fetched"""
    
    # Get ESPN team names
    competitions = espn_game.get("competitions", [{}])
    if not competitions:
        return None
        
    competitors = competitions[0].get("competitors", [])
    if len(competitors) < 2:
        return None
        
    espn_away = competitors[1].get("team", {}).get("displayName", "").lower()
    espn_home = competitors[0].get("team", {}).get("displayName", "").lower()
    
    print(f"   Looking for Odds API event ID for: {espn_away} @ {espn_home}")
    
    # Use the odds games we already fetched (avoid extra API call)
    for odds_game in odds_games:
        odds_away = odds_game.get("away_team", "").lower()
        odds_home = odds_game.get("home_team", "").lower()
        
        # Simple team name matching
        if (espn_away in odds_away or odds_away in espn_away) and \
           (espn_home in odds_home or odds_home in espn_home):
            event_id = odds_game.get("id")
            print(f"   ✅ Found match: Event ID {event_id}")
            return event_id
    
    print(f"   ❌ No matching Odds API event found")
    return None

def fetch_player_props_for_game(league_config, espn_game, odds_event_id):
    """Fetch player props for a specific game"""
    
    competitions = espn_game.get("competitions", [{}])
    competitors = competitions[0].get("competitors", [])
    away_team = competitors[1].get("team", {}).get("displayName", "Away")
    home_team = competitors[0].get("team", {}).get("displayName", "Home")
    
    print_header(f"PLAYER PROPS: {away_team} @ {home_team}")
    
    print(f"Fetching player props...")
    print(f"Event ID: {odds_event_id}")
    print(f"Markets: {league_config['prop_markets']}")
    
    # Fetch player props using the event-specific endpoint
    success, result = make_request("POST", "/odds/event-odds", {
        "sport": league_config["odds_key"],
        "event_id": odds_event_id,
        "regions": "us",
        "markets": league_config["prop_markets"],
        "odds_format": "american"
    })
    
    if not success:
        print(f"❌ FAILED to get player props: {result}")
        return False, None
    
    # Handle response format
    if isinstance(result, dict) and "data" in result:
        event_data = result["data"]
    else:
        event_data = result
    
    bookmakers = event_data.get("bookmakers", [])
    if not bookmakers:
        print("❌ No player props available for this game")
        return False, None
    
    print(f"✅ Found player props from {len(bookmakers)} bookmaker(s)")
    
    # Extract all unique players and their props
    players_props = {}
    
    for bookmaker in bookmakers:
        book_name = bookmaker.get("title", "Unknown")
        
        for market in bookmaker.get("markets", []):
            market_key = market.get("key", "")
            
            for outcome in market.get("outcomes", []):
                player_name = outcome.get("description", "")
                if not player_name:
                    continue
                
                if player_name not in players_props:
                    players_props[player_name] = {}
                
                if market_key not in players_props[player_name]:
                    players_props[player_name][market_key] = []
                
                prop_info = {
                    "bookmaker": book_name,
                    "side": outcome.get("name", ""),  # Over/Under
                    "line": outcome.get("point", ""),
                    "odds": outcome.get("price", "N/A")
                }
                
                players_props[player_name][market_key].append(prop_info)
    
    if not players_props:
        print("❌ No player props found in the data")
        return False, None
    
    # Fetch ESPN player IDs for matching
    print(f"\n⏳ Fetching ESPN roster data...")
    espn_players = fetch_espn_rosters_for_game(league_config, espn_game)
    
    # Display players and their props with ESPN IDs
    display_player_props_with_espn_ids(players_props, espn_players, league_config["sport"])
    
    return True, players_props

def fetch_espn_rosters_for_game(league_config, espn_game):
    """Fetch ESPN roster data for both teams in the game"""
    
    competitions = espn_game.get("competitions", [{}])
    competitors = competitions[0].get("competitors", [])
    
    if len(competitors) < 2:
        print("❌ Could not find team data for roster lookup")
        return {}
    
    away_team = competitors[1].get("team", {})
    home_team = competitors[0].get("team", {})
    
    away_team_id = away_team.get("id")
    home_team_id = home_team.get("id")
    
    espn_players = {}
    
    # Fetch roster for both teams
    for team_name, team_id in [(away_team.get("displayName", "Away"), away_team_id), 
                               (home_team.get("displayName", "Home"), home_team_id)]:
        if not team_id:
            continue
            
        print(f"   Fetching roster for {team_name} (ID: {team_id})...")
        
        success, result = make_request("POST", "/espn/roster", {
            "sport": league_config["sport"],
            "league": league_config["league"],
            "team_id": str(team_id)
        })
        
        if success and result.get("ok"):
            roster_data = result.get("data", {})
            athletes = roster_data.get("athletes", [])
            
            print(f"   ✅ Found {len(athletes)} players for {team_name}")
            
            for athlete in athletes:
                player_data = athlete.get("athlete", {})
                player_name = player_data.get("displayName", "")
                player_id = player_data.get("id")
                
                if player_name and player_id:
                    # Store both full name and variations for matching
                    espn_players[player_name] = player_id
                    
                    # Also store first+last name for better matching
                    name_parts = player_name.split()
                    if len(name_parts) >= 2:
                        first_last = f"{name_parts[0]} {name_parts[-1]}"
                        espn_players[first_last] = player_id
        else:
            print(f"   ❌ Failed to get roster for {team_name}: {result}")
    
    print(f"   ✅ Total unique players found: {len(set(espn_players.values()))}")
    return espn_players

def match_player_name(betting_name, espn_players):
    """Match betting site player name to ESPN player"""
    
    # Direct match first
    if betting_name in espn_players:
        return espn_players[betting_name]
    
    # Try case-insensitive match
    betting_lower = betting_name.lower()
    for espn_name, espn_id in espn_players.items():
        if espn_name.lower() == betting_lower:
            return espn_id
    
    # Try partial matches (last name)
    betting_parts = betting_name.split()
    if len(betting_parts) >= 2:
        betting_last = betting_parts[-1].lower()
        
        for espn_name, espn_id in espn_players.items():
            espn_parts = espn_name.split()
            if len(espn_parts) >= 2 and espn_parts[-1].lower() == betting_last:
                # Also check if first name matches or starts with same letter
                betting_first = betting_parts[0].lower()
                espn_first = espn_parts[0].lower()
                if espn_first.startswith(betting_first[0]):
                    return espn_id
    
    return None

def display_player_props_with_espn_ids(players_props, espn_players, sport):
    """Display formatted player props with ESPN player IDs"""
    
    print(f"\n📊 PLAYER PROPS WITH ESPN IDS:")
    print("=" * 70)
    
    for i, (player_name, markets) in enumerate(sorted(players_props.items()), 1):
        # Try to match with ESPN player
        espn_id = match_player_name(player_name, espn_players)
        
        if espn_id:
            print(f"\n{i}. {player_name} espn: {espn_id}")
        else:
            print(f"\n{i}. {player_name} espn: NOT FOUND")
            
        print("-" * 50)
        
        for market_key, props in markets.items():
            market_label = get_market_label(market_key)
            print(f"   {market_label}:")
            
            # Group by line value to show Over/Under together
            lines = {}
            for prop in props:
                line = prop["line"]
                if line not in lines:
                    lines[line] = {"over": [], "under": []}
                
                side = prop["side"].lower()
                if "over" in side:
                    lines[line]["over"].append(prop)
                elif "under" in side:
                    lines[line]["under"].append(prop)
            
            for line, sides in lines.items():
                if sides["over"] or sides["under"]:
                    print(f"      Line {line}:")
                    
                    # Show Over props
                    for prop in sides["over"]:
                        print(f"        Over: {prop['odds']} ({prop['bookmaker']})")
                    
                    # Show Under props  
                    for prop in sides["under"]:
                        print(f"        Under: {prop['odds']} ({prop['bookmaker']})")

def display_player_props(players_props, sport):
    """Display formatted player props"""
    
    print(f"\n📊 PLAYER PROPS AVAILABLE:")
    print("=" * 70)
    
    for i, (player_name, markets) in enumerate(sorted(players_props.items()), 1):
        print(f"\n{i}. {player_name}")
        print("-" * 50)
        
        for market_key, props in markets.items():
            market_label = get_market_label(market_key)
            print(f"   {market_label}:")
            
            # Group by line value to show Over/Under together
            lines = {}
            for prop in props:
                line = prop["line"]
                if line not in lines:
                    lines[line] = {"over": [], "under": []}
                
                side = prop["side"].lower()
                if "over" in side:
                    lines[line]["over"].append(prop)
                elif "under" in side:
                    lines[line]["under"].append(prop)
            
            for line, sides in lines.items():
                if sides["over"] or sides["under"]:
                    print(f"      Line {line}:")
                    
                    # Show Over props
                    for prop in sides["over"]:
                        print(f"        Over: {prop['odds']} ({prop['bookmaker']})")
                    
                    # Show Under props  
                    for prop in sides["under"]:
                        print(f"        Under: {prop['odds']} ({prop['bookmaker']})")

def get_market_label(market_key):
    """Convert market key to readable label"""
    labels = {
        # Baseball
        "batter_home_runs": "Home Runs",
        "batter_hits": "Hits", 
        "pitcher_strikeouts": "Strikeouts (Pitcher)",
        
        # Basketball
        "player_points": "Points",
        "player_rebounds": "Rebounds",
        "player_assists": "Assists", 
        "player_threes": "3-Pointers Made",
        
        # Football
        "player_pass_yds": "Passing Yards",
        "player_rush_yds": "Rushing Yards",
        "player_receptions": "Receptions",
        
        # Hockey
        "player_goals": "Goals",
        "player_assists": "Assists",
        "player_shots_on_goal": "Shots on Goal",
        
        # Soccer
        "player_shots": "Shots",
        "player_shots_on_target": "Shots on Target"
    }
    
    return labels.get(market_key, market_key.replace("_", " ").title())


def main():
    """Main function - Select league and fetch games with odds"""
    print_header("SPORTS GAME & ODDS FETCHER")
    print("Interactive league selection with game data and betting odds")
    
    global odds_api_calls
    odds_api_calls = 0  # Reset counter
    
    try:
        # Step 1: Select league
        league_config = select_league()
        
        # Step 2: Fetch games with event IDs
        print("\n" + "⏳" * 20)
        print("STEP 1: Fetching games...")
        success, games = fetch_games(league_config)
        
        if not success:
            print(f"\n❌ Failed to retrieve games for {league_config['name']}")
            print("Check your MCP connection and try again")
            return
        
        if not games:
            print(f"\n🤷 No games found for {league_config['name']} today")
            print("This could be an off-season or off-day for this league")
            return
        
        # Step 3: Fetch odds for these games
        print("\n" + "⏳" * 20)
        print("STEP 2: Fetching odds...")
        odds_success, matched_games, odds_games = fetch_odds_for_games(league_config, games)
        
        # Summary
        print_header("SESSION SUMMARY")
        print(f"🏆 League: {league_config['name']}")
        print(f"🎮 Games found: {len(games)}")
        
        if odds_success and matched_games:
            print(f"💰 Games with odds: {len(matched_games)}")
        else:
            print("💰 Odds: Failed to fetch or no matches found")
        print(f"📡 Total Odds API calls: {odds_api_calls}")
        
        print("\n🎯 Next steps:")
        print("- Add player stats integration")
        print("- Build player matching system")
        print("- Create value calculation pipeline")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        if odds_api_calls > 0:
            print(f"📡 Total Odds API calls this session: {odds_api_calls}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if odds_api_calls > 0:
            print(f"📡 Total Odds API calls this session: {odds_api_calls}")

if __name__ == "__main__":
    main()