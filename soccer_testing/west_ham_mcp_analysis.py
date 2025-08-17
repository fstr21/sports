#!/usr/bin/env python3
"""
West Ham MCP Analysis

Get West Ham's most recent game and extract game-level and player-level stats
using the MCP server tools.
"""

import sys
import os
import asyncio
import json
from datetime import datetime
from collections import defaultdict

# Add the MCP server to Python path with absolute path
mcp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mcp-soccer-data', 'src')
sys.path.insert(0, mcp_path)

# Set environment variable
os.environ['AUTH_KEY'] = 'a9f37754a540df435e8c40ed89c08565166524ed'

async def find_west_ham_matches():
    """Find all West Ham matches using MCP tools"""
    
    print("Getting EPL matches using MCP tools...")
    
    try:
        from enhanced_server import get_league_matches
        
        # Get EPL matches
        result = await get_league_matches(228)  # EPL
        data = json.loads(result)
        
        print("✅ Successfully got EPL matches from MCP server")
        
        west_ham_matches = []
        
        if isinstance(data, list):
            for league_entry in data:
                if isinstance(league_entry, dict):
                    for stage in league_entry.get("stage", []):
                        if isinstance(stage, dict):
                            for match in stage.get("matches", []):
                                if isinstance(match, dict):
                                    teams = match.get("teams", {})
                                    home_team = teams.get("home", {})
                                    away_team = teams.get("away", {})
                                    
                                    home_name = home_team.get("name", "")
                                    away_name = away_team.get("name", "")
                                    
                                    # Check if West Ham is playing
                                    if ("west ham" in home_name.lower() or 
                                        "west ham" in away_name.lower()):
                                        
                                        west_ham_matches.append({
                                            "match_data": match,
                                            "home": home_name,
                                            "away": away_name,
                                            "date": match.get("date"),
                                            "status": match.get("status"),
                                            "events_count": len(match.get("events", []))
                                        })
        
        print(f"Found {len(west_ham_matches)} West Ham matches")
        
        if west_ham_matches:
            print("West Ham matches found:")
            for i, match in enumerate(west_ham_matches, 1):
                print(f"  {i}. {match['home']} vs {match['away']} ({match['date']}) - {match['events_count']} events")
        
        return west_ham_matches
        
    except ImportError as e:
        print(f"❌ Failed to import MCP server: {e}")
        print(f"❌ Make sure you're running from the soccer_testing directory")
        print(f"❌ Current working directory: {os.getcwd()}")
        print(f"❌ Looking for MCP server at: {mcp_path}")
        return None
    except Exception as e:
        print(f"❌ Error using MCP tools: {e}")
        return None

def analyze_game_level_stats(match_data):
    """Extract game-level statistics from match data"""
    
    print(f"\n🏟️  GAME-LEVEL STATISTICS ANALYSIS")
    print("=" * 50)
    
    # Basic match info
    teams = match_data.get("teams", {})
    home_team = teams.get("home", {})
    away_team = teams.get("away", {})
    
    # Score information
    goals_data = match_data.get("goals", {})
    
    game_stats = {
        "basic_info": {
            "home_team": home_team.get("name"),
            "away_team": away_team.get("name"),
            "date": match_data.get("date"),
            "time": match_data.get("time"),
            "status": match_data.get("status"),
            "match_id": match_data.get("id")
        },
        "score": {
            "home_ft": goals_data.get("home_ft_goals", 0),
            "away_ft": goals_data.get("away_ft_goals", 0),
            "home_ht": goals_data.get("home_ht_goals", 0),
            "away_ht": goals_data.get("away_ht_goals", 0)
        },
        "events_summary": {
            "total_events": 0,
            "goals": 0,
            "yellow_cards": 0,
            "red_cards": 0,
            "substitutions": 0,
            "other_events": 0
        },
        "detailed_events": {
            "goals": [],
            "cards": [],
            "substitutions": [],
            "other": []
        }
    }
    
    # Analyze events
    events = match_data.get("events", [])
    game_stats["events_summary"]["total_events"] = len(events)
    
    print(f"MATCH: {game_stats['basic_info']['home_team']} vs {game_stats['basic_info']['away_team']}")
    print(f"DATE: {game_stats['basic_info']['date']} at {game_stats['basic_info']['time']}")
    print(f"STATUS: {game_stats['basic_info']['status']}")
    print(f"MATCH ID: {game_stats['basic_info']['match_id']}")
    print(f"SCORE: {game_stats['score']['home_ft']}-{game_stats['score']['away_ft']} (HT: {game_stats['score']['home_ht']}-{game_stats['score']['away_ht']})")
    print(f"TOTAL EVENTS: {len(events)}")
    
    for event in events:
        if isinstance(event, dict):
            event_type = event.get("event_type", "")
            minute = event.get("event_minute", "")
            player = event.get("player", {})
            team = event.get("team", "")
            
            # Determine team name
            team_name = ""
            if team == "home":
                team_name = home_team.get("name", "")
            elif team == "away":
                team_name = away_team.get("name", "")
            
            # Categorize events
            if "goal" in event_type:
                game_stats["events_summary"]["goals"] += 1
                goal_info = {
                    "minute": minute,
                    "type": event_type,
                    "player": player.get("name", "Unknown"),
                    "team": team_name,
                    "assist": event.get("assist_player", {}).get("name") if event.get("assist_player") else None
                }
                game_stats["detailed_events"]["goals"].append(goal_info)
                
            elif "yellow_card" in event_type:
                game_stats["events_summary"]["yellow_cards"] += 1
                card_info = {
                    "minute": minute,
                    "type": "yellow_card",
                    "player": player.get("name", "Unknown"),
                    "team": team_name
                }
                game_stats["detailed_events"]["cards"].append(card_info)
                
            elif "red_card" in event_type:
                game_stats["events_summary"]["red_cards"] += 1
                card_info = {
                    "minute": minute,
                    "type": "red_card",
                    "player": player.get("name", "Unknown"),
                    "team": team_name
                }
                game_stats["detailed_events"]["cards"].append(card_info)
                
            elif "substitution" in event_type:
                game_stats["events_summary"]["substitutions"] += 1
                sub_info = {
                    "minute": minute,
                    "team": team_name,
                    "player_in": event.get("player_in", {}).get("name", "Unknown"),
                    "player_out": event.get("player_out", {}).get("name", "Unknown")
                }
                game_stats["detailed_events"]["substitutions"].append(sub_info)
                
            else:
                game_stats["events_summary"]["other_events"] += 1
                other_info = {
                    "minute": minute,
                    "type": event_type,
                    "player": player.get("name", "Unknown") if player else "Unknown",
                    "team": team_name
                }
                game_stats["detailed_events"]["other"].append(other_info)
    
    # Print detailed events
    print(f"\nEVENT SUMMARY:")
    print(f"  Goals: {game_stats['events_summary']['goals']}")
    print(f"  Yellow Cards: {game_stats['events_summary']['yellow_cards']}")
    print(f"  Red Cards: {game_stats['events_summary']['red_cards']}")
    print(f"  Substitutions: {game_stats['events_summary']['substitutions']}")
    print(f"  Other Events: {game_stats['events_summary']['other_events']}")
    
    # Show detailed events
    if game_stats["detailed_events"]["goals"]:
        print(f"\nGOALS ({len(game_stats['detailed_events']['goals'])}):")
        for goal in game_stats["detailed_events"]["goals"]:
            assist_text = f" [Assist: {goal['assist']}]" if goal['assist'] else ""
            print(f"  {goal['minute']}' - {goal['player']} ({goal['team']}) - {goal['type']}{assist_text}")
    
    if game_stats["detailed_events"]["cards"]:
        print(f"\nCARDS ({len(game_stats['detailed_events']['cards'])}):")
        for card in game_stats["detailed_events"]["cards"]:
            print(f"  {card['minute']}' - {card['player']} ({card['team']}) - {card['type']}")
    
    if game_stats["detailed_events"]["substitutions"]:
        print(f"\nSUBSTITUTIONS ({len(game_stats['detailed_events']['substitutions'])}):")
        for sub in game_stats["detailed_events"]["substitutions"]:
            print(f"  {sub['minute']}' - {sub['team']}: {sub['player_out']} OFF, {sub['player_in']} ON")
    
    return game_stats

def analyze_player_level_stats(match_data):
    """Extract player-level statistics from match events"""
    
    print(f"\n👥 PLAYER-LEVEL STATISTICS ANALYSIS")
    print("=" * 50)
    
    # Initialize player stats tracking
    players = defaultdict(lambda: {
        'name': '',
        'team': '',
        'team_side': '',  # home or away
        'stats': {
            'goals': 0,
            'assists': 0,
            'yellow_cards': 0,
            'red_cards': 0,
            'substituted_in': False,
            'substituted_out': False,
            'substitution_minute': None
        },
        'events': []
    })
    
    # Get team info
    teams = match_data.get("teams", {})
    home_team = teams.get("home", {})
    away_team = teams.get("away", {})
    
    # Process events
    events = match_data.get("events", [])
    
    for event in events:
        if isinstance(event, dict):
            event_type = event.get("event_type", "")
            minute = event.get("event_minute", "")
            team_side = event.get("team", "")
            
            # Determine team name
            team_name = ""
            if team_side == "home":
                team_name = home_team.get("name", "")
            elif team_side == "away":
                team_name = away_team.get("name", "")
            
            # Process main player
            if "player" in event:
                player = event["player"]
                if isinstance(player, dict):
                    player_id = player.get("id")
                    player_name = player.get("name")
                    
                    if player_id and player_name:
                        players[player_id]['name'] = player_name
                        players[player_id]['team'] = team_name
                        players[player_id]['team_side'] = team_side
                        
                        # Record event
                        event_record = {
                            "minute": minute,
                            "type": event_type
                        }
                        players[player_id]['events'].append(event_record)
                        
                        # Update stats
                        if "goal" in event_type:
                            players[player_id]['stats']['goals'] += 1
                        elif "yellow_card" in event_type:
                            players[player_id]['stats']['yellow_cards'] += 1
                        elif "red_card" in event_type:
                            players[player_id]['stats']['red_cards'] += 1
            
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
                            players[player_id]['team_side'] = team_side
                            players[player_id]['stats']['substituted_in'] = True
                            players[player_id]['stats']['substitution_minute'] = minute
                            players[player_id]['events'].append({
                                "minute": minute,
                                "type": "substituted_in"
                            })
                
                # Player going out
                if "player_out" in event:
                    player_out = event["player_out"]
                    if isinstance(player_out, dict):
                        player_id = player_out.get("id")
                        player_name = player_out.get("name")
                        
                        if player_id and player_name:
                            players[player_id]['name'] = player_name
                            players[player_id]['team'] = team_name
                            players[player_id]['team_side'] = team_side
                            players[player_id]['stats']['substituted_out'] = True
                            players[player_id]['stats']['substitution_minute'] = minute
                            players[player_id]['events'].append({
                                "minute": minute,
                                "type": "substituted_out"
                            })
            
            # Process assists
            if "assist_player" in event and event["assist_player"]:
                assist_player = event["assist_player"]
                if isinstance(assist_player, dict):
                    player_id = assist_player.get("id")
                    player_name = assist_player.get("name")
                    
                    if player_id and player_name:
                        players[player_id]['name'] = player_name
                        players[player_id]['team'] = team_name
                        players[player_id]['team_side'] = team_side
                        players[player_id]['stats']['assists'] += 1
                        players[player_id]['events'].append({
                            "minute": minute,
                            "type": "assist"
                        })
    
    # Convert to regular dict and organize by team
    players_dict = dict(players)
    
    # Organize by team
    home_players = {}
    away_players = {}
    
    for player_id, player_data in players_dict.items():
        if player_data['team_side'] == 'home':
            home_players[player_id] = player_data
        elif player_data['team_side'] == 'away':
            away_players[player_id] = player_data
    
    # Print player summaries
    print(f"\n{home_team.get('name', 'Home Team')} Players ({len(home_players)}):")
    if home_players:
        for player_id, player_data in home_players.items():
            print_player_summary(player_id, player_data)
    else:
        print("  No player events recorded")
    
    print(f"\n{away_team.get('name', 'Away Team')} Players ({len(away_players)}):")
    if away_players:
        for player_id, player_data in away_players.items():
            print_player_summary(player_id, player_data)
    else:
        print("  No player events recorded")
    
    return {
        "home_team": {
            "name": home_team.get('name'),
            "players": home_players
        },
        "away_team": {
            "name": away_team.get('name'),
            "players": away_players
        },
        "total_players": len(players_dict)
    }

def print_player_summary(player_id, player_data):
    """Print a summary of player's performance"""
    name = player_data['name']
    stats = player_data['stats']
    
    # Build stats string
    stat_parts = []
    if stats['goals']: stat_parts.append(f"{stats['goals']} goals")
    if stats['assists']: stat_parts.append(f"{stats['assists']} assists")
    if stats['yellow_cards']: stat_parts.append(f"{stats['yellow_cards']} yellow")
    if stats['red_cards']: stat_parts.append(f"{stats['red_cards']} red")
    
    stats_str = ", ".join(stat_parts) if stat_parts else "No major events"
    
    sub_status = ""
    if stats['substituted_in']:
        sub_status = f" (Sub IN {stats['substitution_minute']}')"
    elif stats['substituted_out']:
        sub_status = f" (Sub OUT {stats['substitution_minute']}')"
    
    print(f"  {name} (ID: {player_id}){sub_status}")
    print(f"    Stats: {stats_str}")
    
    # Show event timeline
    if player_data['events']:
        events_str = []
        for event in player_data['events']:
            events_str.append(f"{event['minute']}' {event['type']}")
        print(f"    Events: {', '.join(events_str)}")

async def main():
    print("🏟️  WEST HAM GAME AND PLAYER ANALYSIS (MCP VERSION)")
    print("=" * 60)
    print("This will find West Ham's most recent game and analyze:")
    print("1. Game-level statistics (score, events, timeline)")
    print("2. Player-level statistics (individual performance)")
    print("Using MCP server tools for data access")
    print("=" * 60)
    
    # Step 1: Find West Ham matches using MCP
    west_ham_matches = await find_west_ham_matches()
    if not west_ham_matches:
        print("❌ No West Ham matches found")
        return
    
    # Step 2: Select match with most events (likely most recent completed)
    target_match = max(west_ham_matches, key=lambda x: x["events_count"])
    
    print(f"\n🎯 ANALYZING TARGET MATCH:")
    print(f"   {target_match['home']} vs {target_match['away']}")
    print(f"   Date: {target_match['date']}")
    print(f"   Status: {target_match['status']}")
    print(f"   Events: {target_match['events_count']}")
    
    # Step 3: Analyze the match
    match_data = target_match["match_data"]
    
    game_stats = analyze_game_level_stats(match_data)
    player_stats = analyze_player_level_stats(match_data)
    
    # Step 4: Save comprehensive analysis
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_file = f"west_ham_mcp_analysis_{timestamp}.json"
    
    complete_analysis = {
        "match_info": {
            "home_team": target_match['home'],
            "away_team": target_match['away'],
            "date": target_match['date'],
            "status": target_match['status'],
            "match_id": match_data.get("id")
        },
        "game_level_stats": game_stats,
        "player_level_stats": player_stats,
        "raw_match_data": match_data
    }
    
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(complete_analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 COMPLETE ANALYSIS SAVED TO: {analysis_file}")
    print(f"\n✅ MCP ANALYSIS COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())