#!/usr/bin/env python3
"""
Real-Life MLB Betting Analysis Script

This script demonstrates a complete betting workflow:
1. Get today's MLB games
2. Pick a random game 
3. Get moneyline, spread, and total odds
4. Get hit/HR prop lines for 3 players in the game
5. Analyze those players' last 5 games for hits/HRs
"""

import requests
import json
import random
from datetime import datetime

# API URLs
MLB_MCP_URL = "https://mlbmcp-production.up.railway.app/mcp"
ODDS_MCP_URL = "https://web-production-b939f.up.railway.app/mcp"

def call_mlb_tool(name, args=None):
    """Call MLB MCP tool"""
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call", 
        "id": 1,
        "params": {"name": name, "arguments": args or {}}
    }
    try:
        r = requests.post(MLB_MCP_URL, json=payload, timeout=30)
        result = r.json()
        if result.get("result", {}).get("ok"):
            return result["result"]["data"]
        else:
            print(f"MLB Tool Error: {result}")
            return None
    except Exception as e:
        print(f"MLB API Error: {e}")
        return None

def call_odds_tool(name, args=None):
    """Call Odds MCP tool"""
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1, 
        "params": {"name": name, "arguments": args or {}}
    }
    try:
        r = requests.post(ODDS_MCP_URL, json=payload, timeout=30)
        result = r.json()
        if result.get("result", {}).get("ok"):
            return result["result"]["data"]
        else:
            print(f"Odds Tool Error: {result}")
            return None
    except Exception as e:
        print(f"Odds API Error: {e}")
        return None

def get_team_roster_sample(team_id):
    """Get 3 random players from team roster"""
    roster_data = call_mlb_tool("getMLBTeamRoster", {"teamId": team_id})
    if not roster_data or not roster_data.get("players"):
        return []
    
    players = roster_data["players"]
    # Filter for position players (not pitchers)
    position_players = [p for p in players if p.get("position") not in ["P", "RP", "SP", "CP"]]
    
    if len(position_players) >= 3:
        return random.sample(position_players, 3)
    else:
        return position_players[:3]

def analyze_player_trends(player_id, player_name):
    """Analyze player's last 5 games for hits and home runs"""
    print(f"\nAnalyzing {player_name} (ID: {player_id}):")
    print("-" * 50)
    
    # Get last 5 games
    player_data = call_mlb_tool("getMLBPlayerLastN", {
        "player_ids": [player_id],
        "count": 5,
        "stats": ["hits", "homeRuns", "atBats"]
    })
    
    if not player_data or not player_data.get("results"):
        print("ERROR: No player data available")
        return None
    
    player_result = player_data["results"].get(str(player_id))
    if not player_result:
        print("ERROR: Player not found in results")
        return None
    
    games = player_result.get("games", [])
    aggregates = player_result.get("aggregates", {})
    
    print(f"Last {len(games)} games analysis:")
    
    # Game by game breakdown
    for i, game in enumerate(games, 1):
        hits = game.get("hits", 0)
        hrs = game.get("homeRuns", 0) 
        abs = game.get("atBats", 0)
        date = game.get("date_et", "Unknown")
        
        print(f"  Game {i} ({date}): {hits}-for-{abs}, {hrs} HR")
    
    # Aggregates and trends
    print(f"\nTrends:")
    print(f"  Hits Average: {aggregates.get('hits_avg', 0):.2f}")
    print(f"  Total Hits: {aggregates.get('hits_sum', 0)}")
    print(f"  Total HRs: {aggregates.get('homeRuns_sum', 0)}")
    print(f"  HR Rate: {aggregates.get('homeRuns_sum', 0)}/{len(games)} games")
    
    # Calculate hit rate for betting
    hit_rate = sum(1 for g in games if g.get("hits", 0) >= 1) / len(games) if games else 0
    multi_hit_rate = sum(1 for g in games if g.get("hits", 0) >= 2) / len(games) if games else 0
    
    print(f"  1+ Hit Rate: {hit_rate:.1%} ({sum(1 for g in games if g.get('hits', 0) >= 1)}/{len(games)} games)")
    print(f"  2+ Hit Rate: {multi_hit_rate:.1%} ({sum(1 for g in games if g.get('hits', 0) >= 2)}/{len(games)} games)")
    
    return {
        "games": games,
        "aggregates": aggregates,
        "hit_rate": hit_rate,
        "multi_hit_rate": multi_hit_rate,
        "total_hrs": aggregates.get("homeRuns_sum", 0)
    }

def main():
    print("=" * 80)
    print("REAL-LIFE MLB BETTING ANALYSIS")
    print("=" * 80)
    
    # Step 1: Get today's MLB games
    print("\nStep 1: Getting MLB games for 8/14/2025...")
    games_data = call_mlb_tool("getMLBScheduleET", {"date": "2025-08-14"})
    
    if not games_data or not games_data.get("games"):
        print("ERROR: No games found for today")
        return
    
    games = games_data["games"]
    print(f"SUCCESS: Found {len(games)} games scheduled")
    
    # Step 2: Pick a random game
    if not games:
        print("ERROR: No games available")
        return
        
    selected_game = random.choice(games)
    home_team = selected_game["home"]
    away_team = selected_game["away"] 
    game_time = selected_game.get("start_et", "TBD")
    
    print(f"\nStep 2: Randomly selected game:")
    print(f"   {away_team['name']} @ {home_team['name']}")
    print(f"   Game Time: {game_time}")
    print(f"   Venue: {selected_game.get('venue', 'TBD')}")
    
    # Step 3: Get game odds (moneyline, spread, total)
    print(f"\nStep 3: Getting odds for this game...")
    
    # Try to get odds - note: this may not work if odds aren't available
    odds_data = call_odds_tool("getOdds", {
        "sport": "baseball_mlb",
        "markets": "h2h,spreads,totals"
    })
    
    if odds_data and odds_data.get("odds"):
        odds_list = odds_data["odds"]
        if odds_list:
            print("SUCCESS: Found live odds data:")
            # Find matching game (simplified - would need better matching logic)
            game_odds = odds_list[0]  # Take first game as example
            print(f"   Game: {game_odds.get('away_team', 'Away')} @ {game_odds.get('home_team', 'Home')}")
            
            # Extract bookmaker odds
            bookmakers = game_odds.get("bookmakers", [])
            if bookmakers:
                bookmaker = bookmakers[0]
                markets = bookmaker.get("markets", [])
                for market in markets:
                    if market.get("key") == "h2h":
                        outcomes = market.get("outcomes", [])
                        if len(outcomes) >= 2:
                            print(f"   Moneyline: {outcomes[0]['name']} {outcomes[0]['price']} / {outcomes[1]['name']} {outcomes[1]['price']}")
                    elif market.get("key") == "spreads":
                        outcomes = market.get("outcomes", [])
                        if len(outcomes) >= 2:
                            print(f"   Run Line: {outcomes[0]['name']} {outcomes[0]['point']} ({outcomes[0]['price']})")
                    elif market.get("key") == "totals":
                        outcomes = market.get("outcomes", [])
                        if len(outcomes) >= 2:
                            print(f"   Total: O/U {outcomes[0]['point']} ({outcomes[0]['price']}/{outcomes[1]['price']})")
            else:
                print("   No bookmaker data available")
        else:
            print("WARNING: No odds found for MLB")
    else:
        print("WARNING: Unable to get live odds data")
        print("   This could be due to:")
        print("   - Odds MCP not deployed yet")
        print("   - Missing API key")
        print("   - No current MLB games with odds")
        print("   - API quota exceeded")
    
    # Step 4: Get 3 players from each team
    print(f"\nStep 4: Getting players for analysis...")
    
    away_players = get_team_roster_sample(away_team["teamId"])
    home_players = get_team_roster_sample(home_team["teamId"])
    
    # Select 3 total players (mix from both teams)
    all_players = away_players + home_players
    selected_players = random.sample(all_players, min(3, len(all_players)))
    
    print(f"SUCCESS: Selected {len(selected_players)} players for prop analysis:")
    for player in selected_players:
        print(f"   - {player['fullName']} ({player.get('position', 'N/A')})")
    
    # Step 5: Get player prop lines (using odds MCP)
    print(f"\nStep 5: Player prop lines:")
    
    # For now, note that player props require specific event IDs
    print("   NOTE: Player props require specific game event IDs from odds API")
    print("   This step would typically:")
    print("   1. Find the specific game event ID from the odds data")
    print("   2. Call getEventOdds with markets like 'batter_hits', 'batter_home_runs'")
    print("   3. Extract actual betting lines for each player")
    
    # Show the selected players for analysis
    print(f"\n   Selected players for prop analysis:")
    for player in selected_players:
        print(f"   - {player['fullName']} ({player.get('position', 'N/A')})")
    
    # Step 6: Analyze each player's last 5 games
    print(f"\nStep 6: Player Performance Analysis")
    print("=" * 80)
    
    player_analyses = []
    for player in selected_players:
        analysis = analyze_player_trends(player["playerId"], player["fullName"])
        if analysis:
            player_analyses.append({
                "player": player,
                "analysis": analysis
            })
    
    # Step 7: Betting Summary
    print(f"\nBETTING ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Game: {away_team['name']} @ {home_team['name']}")
    print(f"Time: {game_time}")
    
    print(f"\nPlayer Prop Recommendations:")
    for pa in player_analyses:
        player_name = pa["player"]["fullName"] 
        analysis = pa["analysis"]
        hit_rate = analysis["hit_rate"]
        total_hrs = analysis["total_hrs"]
        
        print(f"\n{player_name}:")
        if hit_rate >= 0.6:
            print(f"  HITS 1+ OVER: LEAN OVER (hitting {hit_rate:.1%} in last 5)")
        else:
            print(f"  HITS 1+ UNDER: LEAN UNDER (hitting {hit_rate:.1%} in last 5)")
            
        if total_hrs >= 2:
            print(f"  HOME RUN: LEAN OVER ({total_hrs} HRs in last 5)")
        else:
            print(f"  HOME RUN: LEAN UNDER ({total_hrs} HRs in last 5)")
    
    print(f"\nAnalysis Complete! Use this data for your betting decisions.")
    print("WARNING: This is for research purposes only. Gamble responsibly.")

if __name__ == "__main__":
    main()