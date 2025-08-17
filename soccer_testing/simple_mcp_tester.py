#!/usr/bin/env python3
"""
Simple MCP Tools Tester

Test specific MCP tools to see what data we can get.
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add the MCP server to Python path
sys.path.append(os.path.join(os.getcwd(), 'mcp-soccer-data', 'src'))

# Set environment variable
os.environ['AUTH_KEY'] = 'a9f37754a540df435e8c40ed89c08565166524ed'

async def test_1_live_scores():
    """Test live scores"""
    print("TEST 1: Live Scores")
    print("Getting current live matches worldwide...")
    
    try:
        from enhanced_server import get_livescores
        result = await get_livescores()
        data = json.loads(result)
        
        if isinstance(data, list):
            print(f"SUCCESS: Found {len(data)} live match entries")
            
            # Count live matches
            live_matches = 0
            sample_matches = []
            
            for entry in data[:5]:  # Check first 5 entries
                if isinstance(entry, dict):
                    league_name = entry.get("league_name", "Unknown")
                    matches = entry.get("matches", [])
                    
                    for match in matches[:3]:  # Check first 3 matches
                        if isinstance(match, dict):
                            status = match.get("status", "")
                            teams = match.get("teams", {})
                            home = teams.get("home", {}).get("name", "Unknown")
                            away = teams.get("away", {}).get("name", "Unknown")
                            
                            sample_matches.append(f"{home} vs {away} ({status})")
                            
                            if status in ["live", "in-progress", "1st-half", "2nd-half", "finished"]:
                                live_matches += 1
            
            print(f"Live/Recent matches: {live_matches}")
            print("Sample matches:")
            for match in sample_matches[:5]:
                print(f"  - {match}")
        
        # Save result
        with open('live_scores_test.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("SAVED: live_scores_test.json")
        
    except Exception as e:
        print(f"ERROR: {e}")

async def test_2_search_player():
    """Search for a specific player"""
    print("\nTEST 2: Search for Salah in EPL")
    print("Extracting all EPL players and searching...")
    
    try:
        from enhanced_server import extract_players_from_league
        
        result = await extract_players_from_league(228)  # EPL
        data = json.loads(result)
        
        if "error" in data:
            print(f"ERROR: {data['error']}")
            return
        
        players = data.get("players", {})
        total_players = data.get("total_players_found", 0)
        
        print(f"SUCCESS: Extracted {total_players} total players")
        
        # Search for Salah
        found_players = []
        for player_id, player_info in players.items():
            name = player_info.get("name", "")
            if "salah" in name.lower():
                found_players.append((player_id, player_info))
        
        if found_players:
            print(f"FOUND {len(found_players)} players matching 'Salah':")
            for player_id, player_info in found_players:
                name = player_info.get("name")
                teams = ", ".join(player_info.get("teams", []))
                stats = player_info.get("stats", {})
                
                print(f"  {name} (ID: {player_id})")
                print(f"    Teams: {teams}")
                print(f"    Goals: {stats.get('goals', 0)}")
                print(f"    Assists: {stats.get('assists', 0)}")
                print(f"    Cards: {stats.get('yellow_cards', 0)} yellow")
        else:
            print("No players found matching 'Salah'")
            
            # Show sample names
            print("Sample player names:")
            sample_players = list(players.items())[:10]
            for player_id, player_info in sample_players:
                print(f"  - {player_info.get('name', 'Unknown')}")
    
    except Exception as e:
        print(f"ERROR: {e}")

async def test_3_epl_standings():
    """Test EPL standings"""
    print("\nTEST 3: EPL Standings")
    print("Getting Premier League table...")
    
    try:
        from enhanced_server import get_league_standings
        
        result = await get_league_standings(228)  # EPL
        data = json.loads(result)
        
        if isinstance(data, list) and data:
            print(f"SUCCESS: Found {len(data)} teams in EPL")
            
            print("Top 5 teams:")
            for i, team in enumerate(data[:5]):
                if isinstance(team, dict):
                    name = team.get("name", "Unknown")
                    points = team.get("points", 0)
                    position = team.get("position", i+1)
                    played = team.get("played", 0)
                    print(f"  {position}. {name} - {points} pts ({played} games)")
        
        # Save result
        with open('epl_standings_test.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("SAVED: epl_standings_test.json")
        
    except Exception as e:
        print(f"ERROR: {e}")

async def test_4_team_info():
    """Test team information"""
    print("\nTEST 4: Team Information")
    print("Getting Fulham and Liverpool team info...")
    
    try:
        from enhanced_server import get_team_info
        
        # Test Fulham
        fulham_result = await get_team_info(4145)
        fulham_data = json.loads(fulham_result)
        
        print(f"FULHAM:")
        print(f"  Name: {fulham_data.get('name', 'Unknown')}")
        print(f"  Stadium: {fulham_data.get('stadium', 'Unknown')}")
        print(f"  Country: {fulham_data.get('country', 'Unknown')}")
        
        # Test Liverpool  
        liverpool_result = await get_team_info(61826)
        liverpool_data = json.loads(liverpool_result)
        
        print(f"LIVERPOOL:")
        print(f"  Name: {liverpool_data.get('name', 'Unknown')}")
        print(f"  Stadium: {liverpool_data.get('stadium', 'Unknown')}")
        print(f"  Country: {liverpool_data.get('country', 'Unknown')}")
        
    except Exception as e:
        print(f"ERROR: {e}")

async def test_5_recent_matches():
    """Test recent match data"""
    print("\nTEST 5: Recent EPL Matches with Events")
    print("Getting EPL matches with player events...")
    
    try:
        from enhanced_server import get_league_matches
        
        result = await get_league_matches(228)  # EPL
        data = json.loads(result)
        
        total_matches = 0
        total_events = 0
        recent_matches = []
        
        if isinstance(data, list):
            for league_entry in data:
                if isinstance(league_entry, dict):
                    for stage in league_entry.get("stage", []):
                        if isinstance(stage, dict):
                            matches = stage.get("matches", [])
                            total_matches += len(matches)
                            
                            for match in matches:
                                if isinstance(match, dict):
                                    events = match.get("events", [])
                                    total_events += len(events)
                                    
                                    # Check for interesting matches with events
                                    if len(events) > 5:
                                        teams = match.get("teams", {})
                                        home = teams.get("home", {}).get("name", "Unknown")
                                        away = teams.get("away", {}).get("name", "Unknown")
                                        date = match.get("date", "Unknown")
                                        status = match.get("status", "Unknown")
                                        
                                        recent_matches.append({
                                            "match": f"{home} vs {away}",
                                            "date": date,
                                            "status": status,
                                            "events": len(events)
                                        })
        
        print(f"SUCCESS: Found {total_matches} total matches")
        print(f"Total events: {total_events}")
        
        print("Matches with most events:")
        for match in sorted(recent_matches, key=lambda x: x["events"], reverse=True)[:5]:
            print(f"  {match['match']} ({match['date']}) - {match['events']} events - {match['status']}")
        
        # Save result
        with open('epl_matches_test.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("SAVED: epl_matches_test.json")
        
    except Exception as e:
        print(f"ERROR: {e}")

async def run_all_tests():
    """Run all tests"""
    print("SIMPLE MCP TOOLS TESTER")
    print("Testing SoccerDataAPI MCP tools")
    print("API calls used so far: 13/75 (62 remaining)")
    print("=" * 50)
    
    await test_1_live_scores()
    await test_2_search_player()
    await test_3_epl_standings()
    await test_4_team_info()
    await test_5_recent_matches()
    
    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETED")
    print("Check the generated JSON files for detailed data!")

def main():
    asyncio.run(run_all_tests())

if __name__ == "__main__":
    main()