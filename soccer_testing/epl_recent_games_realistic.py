#!/usr/bin/env python3
"""
EPL Recent Games - REALISTIC Data

Show only the data we ACTUALLY have from SoccerDataAPI events:
- Game-level: REAL scores from goal events, cards, substitutions
- Player-level: Goals, assists, cards, substitutions

Honest about what data is NOT available (corners, shots, etc.)
"""

import sys
import os
import asyncio
import json
from datetime import datetime, timedelta
from collections import defaultdict

# Add the MCP server to Python path
mcp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mcp-soccer-data', 'src')
sys.path.insert(0, mcp_path)

# Set environment variable
os.environ['AUTH_KEY'] = 'a9f37754a540df435e8c40ed89c08565166524ed'

def parse_date(date_str):
    """Parse date string to datetime object"""
    try:
        return datetime.strptime(date_str, "%d/%m/%Y")
    except:
        return None

def is_recent_game(match_date_str, days_back=10):
    """Check if match is within the past X days from 08/17/2025"""
    current_date = datetime(2025, 8, 17)
    cutoff_date = current_date - timedelta(days=days_back)
    
    match_date = parse_date(match_date_str)
    if not match_date:
        return False
    
    return match_date >= cutoff_date and match_date <= current_date

async def get_recent_epl_games():
    """Get recent EPL games using MCP tools"""
    print("🔄 Fetching EPL data...")
    
    try:
        from enhanced_server import get_league_matches
        result = await get_league_matches(228)  # EPL
        data = json.loads(result)
        
        recent_games = []
        
        if isinstance(data, list):
            for league_entry in data:
                if isinstance(league_entry, dict):
                    for stage in league_entry.get("stage", []):
                        if isinstance(stage, dict):
                            for match in stage.get("matches", []):
                                if isinstance(match, dict):
                                    match_date = match.get("date", "")
                                    
                                    if (is_recent_game(match_date) and 
                                        len(match.get("events", [])) > 0):
                                        recent_games.append(match)
        
        print(f"✅ Found {len(recent_games)} recent games with events")
        return recent_games
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def analyze_available_data(match):
    """Extract ONLY the data we actually have from events"""
    
    teams = match.get("teams", {})
    home_team = teams.get("home", {}).get("name", "Unknown")
    away_team = teams.get("away", {}).get("name", "Unknown")
    
    # Initialize counters for data we ACTUALLY have
    stats = {
        "home_team": home_team,
        "away_team": away_team,
        "date": match.get("date"),
        "status": "COMPLETED",
        "home_goals": 0,
        "away_goals": 0,
        "total_events": 0,
        "events_breakdown": {
            "goals": 0,
            "cards": 0,
            "substitutions": 0,
            "other": 0
        }
    }
    
    # Analyze events to get what we actually have
    events = match.get("events", [])
    stats["total_events"] = len(events)
    
    for event in events:
        if isinstance(event, dict):
            event_type = event.get("event_type", "").lower()
            team_side = event.get("team", "")
            
            # Count REAL GOALS from events
            if "goal" in event_type:
                stats["events_breakdown"]["goals"] += 1
                if team_side == "home":
                    stats["home_goals"] += 1
                elif team_side == "away":
                    stats["away_goals"] += 1
            
            # Count cards
            elif "card" in event_type:
                stats["events_breakdown"]["cards"] += 1
            
            # Count substitutions
            elif "substitution" in event_type:
                stats["events_breakdown"]["substitutions"] += 1
            
            # Everything else
            else:
                stats["events_breakdown"]["other"] += 1
    
    stats["score"] = f"{stats['home_goals']}-{stats['away_goals']}"
    stats["total_goals"] = stats['home_goals'] + stats['away_goals']
    
    return stats

def analyze_player_data(match):
    """Extract player data from events"""
    
    players = defaultdict(lambda: {
        'name': '',
        'team': '',
        'goals': 0,
        'assists': 0,
        'cards': 0,
        'substitutions': 0
    })
    
    teams = match.get("teams", {})
    home_team = teams.get("home", {}).get("name", "")
    away_team = teams.get("away", {}).get("name", "")
    
    events = match.get("events", [])
    
    for event in events:
        if isinstance(event, dict):
            event_type = event.get("event_type", "")
            team_side = event.get("team", "")
            team_name = home_team if team_side == "home" else away_team
            
            # Process goals
            if "goal" in event_type and "player" in event:
                player = event["player"]
                if isinstance(player, dict):
                    player_id = player.get("id")
                    player_name = player.get("name")
                    
                    if player_id and player_name:
                        players[player_id]['name'] = player_name
                        players[player_id]['team'] = team_name
                        players[player_id]['goals'] += 1
            
            # Process assists
            if "assist_player" in event and event["assist_player"]:
                assist_player = event["assist_player"]
                if isinstance(assist_player, dict):
                    player_id = assist_player.get("id")
                    player_name = assist_player.get("name")
                    
                    if player_id and player_name:
                        players[player_id]['name'] = player_name
                        players[player_id]['team'] = team_name
                        players[player_id]['assists'] += 1
            
            # Process cards
            if "card" in event_type and "player" in event:
                player = event["player"]
                if isinstance(player, dict):
                    player_id = player.get("id")
                    player_name = player.get("name")
                    
                    if player_id and player_name:
                        players[player_id]['name'] = player_name
                        players[player_id]['team'] = team_name
                        players[player_id]['cards'] += 1
            
            # Process substitutions
            if event_type == "substitution":
                # Player coming in
                if "player_in" in event:
                    player_in = event["player_in"]
                    if isinstance(player_in, dict):
                        player_id = player_in.get("id")
                        player_name = player_in.get("name")
                        
                        if player_id and player_name:
                            players[player_id]['name'] = player_name
                            players[player_id]['team'] = team_name
                            players[player_id]['substitutions'] += 1  # Mark as substitute
                
                # Player going out
                if "player_out" in event:
                    player_out = event["player_out"]
                    if isinstance(player_out, dict):
                        player_id = player_out.get("id")
                        player_name = player_out.get("name")
                        
                        if player_id and player_name:
                            players[player_id]['name'] = player_name
                            players[player_id]['team'] = team_name
                            # Don't increment substitutions for player going out
    
    # Filter players with actual stats
    return {pid: pdata for pid, pdata in players.items() 
            if pdata['goals'] > 0 or pdata['assists'] > 0 or pdata['cards'] > 0 or pdata['substitutions'] > 0}

def print_realistic_output(games_data):
    """Print realistic output showing only available data"""
    
    print("\n" + "="*90)
    print("🏆 EPL GAMES - PAST 10 DAYS (REALISTIC DATA ONLY)")
    print("📊 Showing: Goals, Cards, Substitutions (from actual match events)")
    print("❌ NOT Available: Corners, Shots, Possession, etc.")
    print("="*90)
    
    if not games_data:
        print("❌ No recent games found with events")
        return
    
    # Sort games by date (most recent first)
    sorted_games = sorted(games_data, 
                         key=lambda x: parse_date(x['game_stats']['date']) or datetime.min, 
                         reverse=True)
    
    for i, game in enumerate(sorted_games, 1):
        game_stats = game['game_stats']
        player_stats = game['player_stats']
        
        print(f"\n┌─ GAME {i} ─────────────────────────────────────────────────────────────┐")
        print(f"│ {game_stats['date']} │ {game_stats['home_team']} vs {game_stats['away_team']}")
        print(f"│ FINAL SCORE: {game_stats['score']} │ STATUS: {game_stats['status']}")
        
        # Show available event data
        events = game_stats['events_breakdown']
        print(f"│")
        print(f"│ 📋 MATCH EVENTS ({game_stats['total_events']} total):")
        print(f"│    ⚽ Goals: {events['goals']}")
        print(f"│    🟨 Cards: {events['cards']}")
        print(f"│    🔄 Substitutions: {events['substitutions']}")
        if events['other'] > 0:
            print(f"│    📝 Other Events: {events['other']}")
        
        # Player performance
        if player_stats:
            print(f"│")
            print(f"│ ⭐ PLAYER PERFORMANCE:")
            
            # Sort by impact: goals > assists > cards > substitutions
            def player_impact(pdata):
                return (pdata['goals'] * 10 + pdata['assists'] * 5 + 
                       pdata['cards'] * 2 + pdata['substitutions'] * 1)
            
            sorted_players = sorted(player_stats.items(), 
                                  key=lambda x: player_impact(x[1]), 
                                  reverse=True)
            
            shown = 0
            for player_id, pdata in sorted_players:
                if shown >= 10:  # Top 10 performers
                    break
                
                # Build performance string
                performance = []
                if pdata['goals']: performance.append(f"{pdata['goals']} GOALS")
                if pdata['assists']: performance.append(f"{pdata['assists']} ASSISTS")
                if pdata['cards']: performance.append(f"{pdata['cards']} CARDS")
                if pdata['substitutions']: performance.append("SUB IN")
                
                if performance:
                    perf_str = " | ".join(performance)
                    team_short = pdata['team'][:20] + "..." if len(pdata['team']) > 23 else pdata['team']
                    
                    print(f"│    {pdata['name']:<22} ({team_short:<23}) │ {perf_str}")
                    shown += 1
        else:
            print(f"│    No significant player events recorded")
        
        print(f"└─────────────────────────────────────────────────────────────────────────┘")
    
    # Realistic summary
    print(f"\n📈 REALISTIC SUMMARY:")
    total_goals = sum(game['game_stats']['total_goals'] for game in games_data)
    total_events = sum(game['game_stats']['total_events'] for game in games_data)
    total_games = len(games_data)
    
    print(f"   🎯 {total_games} completed games analyzed")
    print(f"   ⚽ {total_goals} total goals scored")
    print(f"   📊 {total_events} total match events tracked")
    
    if total_games > 0:
        avg_goals = total_goals / total_games
        avg_events = total_events / total_games
        print(f"   📈 Average: {avg_goals:.1f} goals per game, {avg_events:.1f} events per game")
    
    # Top performers across all games
    all_players = {}
    for game in games_data:
        for pid, pdata in game['player_stats'].items():
            if pid not in all_players:
                all_players[pid] = pdata.copy()
            else:
                all_players[pid]['goals'] += pdata['goals']
                all_players[pid]['assists'] += pdata['assists']
                all_players[pid]['cards'] += pdata['cards']
    
    if all_players:
        # Top scorer
        top_scorer = max(all_players.items(), key=lambda x: x[1]['goals'])
        if top_scorer[1]['goals'] > 0:
            print(f"   👑 Top scorer: {top_scorer[1]['name']} ({top_scorer[1]['goals']} goals)")
        
        # Top assist provider
        top_assister = max(all_players.items(), key=lambda x: x[1]['assists'])
        if top_assister[1]['assists'] > 0:
            print(f"   🎯 Most assists: {top_assister[1]['name']} ({top_assister[1]['assists']} assists)")
    
    print(f"\n💡 DATA LIMITATIONS:")
    print(f"   • SoccerDataAPI events only include: goals, cards, substitutions")
    print(f"   • Missing: corners, shots, possession, fouls, etc.")
    print(f"   • For complete stats, would need different data source")
    
    print("="*90)

async def main():
    print("🚀 EPL RECENT GAMES - REALISTIC DATA VERSION")
    print("Showing only the data we actually have from match events")
    print("Current date: 08/17/2025")
    
    recent_games = await get_recent_epl_games()
    
    if not recent_games:
        print("❌ No recent games found")
        return
    
    # Analyze with realistic expectations
    games_data = []
    
    for match in recent_games:
        game_stats = analyze_available_data(match)
        player_stats = analyze_player_data(match)
        
        games_data.append({
            'game_stats': game_stats,
            'player_stats': player_stats,
            'raw_match': match
        })
    
    # Print realistic output
    print_realistic_output(games_data)
    
    # Save data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"epl_recent_games_realistic_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(games_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Data saved to: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())