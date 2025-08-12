#!/usr/bin/env python3
"""
Interactive Sports Test Script - MCP Version

Updated to use the Pure MCP Server with proper tool calls.
Now uses real ESPN and Odds data via MCP protocol.
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
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}

# League configurations with MCP tool mappings
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

# Global API call counter
api_calls = 0

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def call_mcp_tool(tool_name, arguments):
    """Call an MCP tool and return the result"""
    global api_calls
    api_calls += 1
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": str(api_calls),
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    try:
        response = requests.post(f"{RAILWAY_URL}/mcp", headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            if "result" in result:
                return True, result["result"]
            elif "error" in result:
                return False, f"MCP Error: {result['error']}"
            else:
                return False, f"Unexpected response: {result}"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Request failed: {str(e)}"

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
        print("ERROR Invalid choice. Please try again.")

def fetch_games(league_config):
    """Fetch today's games using MCP getScoreboard tool"""
    print_header(f"TODAY'S {league_config['name']} GAMES")
    
    print(f"Fetching {league_config['name']} games via MCP...")
    print(f"Sport: {league_config['sport']}, League: {league_config['league']}")
    
    # Get today's date in Eastern time for sports scheduling
    current_eastern = get_current_eastern_time()
    today_date = current_eastern.strftime("%Y%m%d")
    print(f"Requesting games for date: {today_date}")
    
    success, result = call_mcp_tool("getScoreboard", {
        "sport": league_config["sport"], 
        "league": league_config["league"],
        "dates": today_date
    })
    
    if success and result.get("ok"):
        # Extract games from MCP response
        games_data = result.get("data", {})
        games = games_data.get("events", [])
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
    """Fetch odds using MCP getOdds tool"""
    print_header(f"{league_config['name']} ODDS")
    
    print(f"Fetching odds for {league_config['name']} via MCP...")
    print(f"Using sport key: {league_config['odds_key']}")
    
    # Get odds using MCP tool
    success, result = call_mcp_tool("getOdds", {
        "sport": league_config["odds_key"],
        "regions": "us",
        "markets": "h2h,spreads,totals",
        "odds_format": "american",
        "use_test_mode": False  # Use real data
    })
    
    if not success or not result.get("ok"):
        print(f"FAILED to get odds: {result}")
        return False, None, None
    
    # Extract odds data
    odds_data = result.get("data", {})
    odds_games = odds_data.get("odds", [])
    
    print(f"SUCCESS: Found odds for {len(odds_games)} games")
    
    if not odds_games:
        print("No odds available for this sport today")
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
    else:
        print("\nNo games could be matched between ESPN and Odds data")
        print("This could be due to:")
        print("- Different team name formats")
        print("- Games not yet available for betting")
        print("- Timing differences between data sources")
    
    # Add player props selection for active leagues
    active_leagues = ["MLB", "WNBA"]
    if league_config["name"] in active_leagues and matched_games:
        print(f"\n" + "=" * 70)
        print(f"Enter a game number (1-{len(matched_games)}) to view player props")
        print("   Or press Enter to continue...")
        
        choice = input("Select game for player props (or Enter to skip): ").strip()
        
        if choice.isdigit():
            game_num = int(choice) - 1
            if 0 <= game_num < len(matched_games):
                selected_game = matched_games[game_num]
                espn_game = selected_game["espn_data"]
                odds_game = selected_game["odds_data"]
                
                # Get Odds API event ID for this game
                print("\nFinding Odds API event ID...")
                odds_event_id = odds_game.get("id")
                
                if odds_event_id:
                    print("Fetching player props...")
                    fetch_player_props_for_game(league_config, espn_game, odds_event_id)
                else:
                    print("Cannot fetch player props without Odds API event ID")
            else:
                print("Invalid game number")
        else:
            print("Skipping player props")
    
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
            print("   Moneyline:")
            for outcome in market.get("outcomes", []):
                team = outcome.get("name", "Unknown")
                odds = outcome.get("price", "N/A")
                print(f"      {team}: {odds}")
                
        elif market_key == "spreads":
            print("   Spreads:")
            for outcome in market.get("outcomes", []):
                team = outcome.get("name", "Unknown")
                spread = outcome.get("point", "N/A")
                odds = outcome.get("price", "N/A")
                spread_str = f"{spread:+}" if isinstance(spread, (int, float)) else spread
                print(f"      {team} {spread_str}: {odds}")
                
        elif market_key == "totals":
            print("   Totals:")
            for outcome in market.get("outcomes", []):
                bet_type = outcome.get("name", "Unknown")  # Over/Under
                total = outcome.get("point", "N/A")
                odds = outcome.get("price", "N/A")
                print(f"      {bet_type} {total}: {odds}")

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
    
    # Fetch player props using the event-specific MCP tool
    success, result = call_mcp_tool("getEventOdds", {
        "sport": league_config["odds_key"],
        "event_id": odds_event_id,
        "regions": "us",
        "markets": league_config["prop_markets"],
        "odds_format": "american",
        "use_test_mode": False  # Use real data
    })
    
    if not success:
        print(f"FAILED to get player props: {result}")
        return False, None
    
    # Handle response format
    if not result.get("ok"):
        print(f"FAILED to get player props: {result.get('error', 'Unknown error')}")
        return False, None
    
    event_data = result.get("data", {}).get("event", {})
    bookmakers = event_data.get("bookmakers", [])
    
    if not bookmakers:
        print("No player props available for this game")
        return False, None
    
    print(f"SUCCESS: Found player props from {len(bookmakers)} bookmaker(s)")
    
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
        print("No player props found in the data")
        return False, None
    
    # Fetch ESPN player IDs for matching
    print(f"\nFetching ESPN roster data...")
    espn_players = fetch_espn_rosters_for_game(league_config, espn_game)
    
    # Display players and their props with ESPN IDs
    display_player_props_with_espn_ids(players_props, espn_players, league_config["sport"])
    
    return True, players_props

def fetch_espn_rosters_for_game(league_config, espn_game):
    """Fetch ESPN roster data for both teams in the game"""
    
    competitions = espn_game.get("competitions", [{}])
    competitors = competitions[0].get("competitors", [])
    
    if len(competitors) < 2:
        print("Could not find team data for roster lookup")
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
        
        success, result = call_mcp_tool("getTeamRoster", {
            "sport": league_config["sport"],
            "league": league_config["league"],
            "team_id": str(team_id)
        })
        
        if success and result.get("ok"):
            roster_data = result.get("data", {})
            athletes = roster_data.get("athletes", [])
            
            print(f"   SUCCESS: Found {len(athletes)} players for {team_name}")
            
            # Sport-specific ESPN roster parsing (DO NOT modify MLB logic)
            sport = league_config.get("sport", "").lower()
            
            if sport == "baseball":
                # MLB structure: athletes -> position groups -> items (players)
                for position_group in athletes:
                    players_in_position = position_group.get("items", [])
                    for player_data in players_in_position:
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
                                
            elif sport == "basketball":
                # WNBA/NBA structure: athletes -> direct player list (flat)
                for player_data in athletes:
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
                # Future sports - will need individual implementation
                print(f"   WARNING: Player parsing not yet implemented for {sport}")
                print(f"   Skipping player ID extraction for this sport")
        else:
            print(f"   FAILED to get roster for {team_name}: {result}")
    
    print(f"   SUCCESS: Total unique players found: {len(set(espn_players.values()))}")
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
    """Display formatted player props with ESPN player IDs and recent stats"""
    
    print(f"\nPLAYER PROPS WITH ESPN IDS & STATS:")
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
            
            # Fetch and display recent stats for this market if we have ESPN ID
            if espn_id:
                print(f"\n      Recent {market_label} Stats (Last 10 Games):")
                fetch_and_display_player_stats(espn_id, sport, market_key)

def fetch_and_display_player_stats(espn_id, sport, market_key):
    """Fetch and display recent player statistics for a specific market"""
    
    # Map market key to ESPN stat names
    stat_mapping = {
        # Baseball
        "batter_home_runs": "homeRuns",
        "batter_hits": "hits",
        "pitcher_strikeouts": "strikeouts",
        
        # Basketball  
        "player_points": "points",
        "player_rebounds": "rebounds", 
        "player_assists": "assists",
        "player_threes": "threePointFieldGoalsMade",
        
        # Football
        "player_pass_yds": "passingYards",
        "player_rush_yds": "rushingYards", 
        "player_receptions": "receptions",
        
        # Hockey
        "player_goals": "goals",
        "player_assists": "assists",
        "player_shots_on_goal": "shotsOnGoal",
        
        # Soccer
        "player_shots": "shots",
        "player_shots_on_target": "shotsOnTarget"
    }
    
    # Determine league based on sport
    league_mapping = {
        "baseball": "mlb",
        "basketball": "wnba",  # We'll handle NBA separately if needed
        "football": "nfl",
        "hockey": "nhl",
        "soccer": "mls"
    }
    
    league = league_mapping.get(sport, sport)
    
    print(f"        Fetching {get_market_label(market_key)} stats for player {espn_id}...")
    
    # Fetch player game log using new MCP tool
    success, result = call_mcp_tool("getPlayerStats", {
        "sport": sport,
        "league": league,
        "player_id": str(espn_id),
        "stat_type": "gamelog",
        "limit": 10
    })
    
    if not success or not result.get("ok"):
        print(f"        ERROR: Could not fetch stats - {result}")
        return
    
    games_data = result.get("data", {}).get("games", [])
    
    if not games_data:
        print("        No recent game data available")
        return
    
    # Extract and display relevant stats using new data structure
    stat_name = stat_mapping.get(market_key, market_key)
    total_stat = 0
    games_with_stat = 0
    
    print(f"        Game-by-game {get_market_label(market_key)}:")
    
    for i, game in enumerate(games_data[:10], 1):
        date = game.get("date", "Unknown Date")[:10]  # YYYY-MM-DD format
        opponent = game.get("opponent", "Unknown")
        game_stats = game.get("stats", {})
        
        # Find the specific stat in the game stats dictionary
        stat_value = "N/A"
        
        # Look for the stat using the mapped name
        if stat_name.lower() in game_stats:
            stat_value = game_stats[stat_name.lower()]
        else:
            # Try alternative names
            alt_names = {
                "hits": ["hits"],
                "homeRuns": ["homeruns", "home runs"],
                "strikeouts": ["strikeouts"],
                "points": ["points"],
                "rebounds": ["rebounds"],
                "assists": ["assists"]
            }
            
            for alt_name in alt_names.get(stat_name, [stat_name]):
                if alt_name.lower() in game_stats:
                    stat_value = game_stats[alt_name.lower()]
                    break
        
        print(f"        Game {i}: {date} vs {opponent} - {stat_value}")
        
        # Track for average calculation
        if stat_value != "N/A" and str(stat_value).replace(".", "").isdigit():
            total_stat += float(stat_value)
            games_with_stat += 1
    
    # Calculate and display average
    if games_with_stat > 0:
        average = total_stat / games_with_stat
        print(f"        Average {get_market_label(market_key)} over {games_with_stat} games: {average:.2f}")
    else:
        print(f"        No statistical data available for {get_market_label(market_key)}")

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
    print_header("SPORTS GAME & ODDS FETCHER - MCP VERSION")
    print("Interactive league selection with REAL game data and betting odds")
    print("Now powered by Pure MCP Server with live ESPN + Odds API data!")
    
    global api_calls
    api_calls = 0  # Reset counter
    
    try:
        # Step 1: Select league
        league_config = select_league()
        
        # Step 2: Fetch games via MCP
        print("\n" + "=" * 20)
        print("STEP 1: Fetching games via MCP...")
        success, games = fetch_games(league_config)
        
        if not success:
            print(f"\nERROR Failed to retrieve games for {league_config['name']}")
            print("Check your MCP server connection and try again")
            return
        
        if not games:
            print(f"\nINFO No games found for {league_config['name']} today")
            print("This could be an off-season or off-day for this league")
            return
        
        # Step 3: Fetch odds via MCP
        print("\n" + "=" * 20)
        print("STEP 2: Fetching odds via MCP...")
        odds_success, matched_games, odds_games = fetch_odds_for_games(league_config, games)
        
        # Summary
        print_header("SESSION SUMMARY")
        print(f"League: {league_config['name']}")
        print(f"Games found: {len(games)} (via ESPN MCP)")
        
        if odds_success and matched_games:
            print(f"Games with odds: {len(matched_games)} (via Odds API MCP)")
            print(f"Odds games total: {len(odds_games)} available")
        else:
            print("Odds: Failed to fetch or no matches found")
        
        print(f"Total MCP API calls: {api_calls}")
        
        print("\nNEXT STEPS:")
        print("- All data is now REAL (no mock data)")
        print("- ESPN games: Live schedules and team info")  
        print("- Odds data: Live betting lines from real sportsbooks")
        print("- Ready for player props and statistics integration")
        print("- Ready for recommendation engine development")
            
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        if api_calls > 0:
            print(f"Total MCP API calls this session: {api_calls}")
    except Exception as e:
        print(f"\nERROR Unexpected error: {e}")
        if api_calls > 0:
            print(f"Total MCP API calls this session: {api_calls}")

if __name__ == "__main__":
    main()