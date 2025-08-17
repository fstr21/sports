#!/usr/bin/env python3
"""
Test MCP Functions Directly

Test the MCP server functions directly without the MCP protocol overhead.
This will help us verify the enhanced server works correctly.
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

async def test_mcp_functions():
    """Test all MCP functions directly"""
    
    print("TESTING MCP FUNCTIONS DIRECTLY")
    print("=" * 60)
    
    try:
        # Import the enhanced server functions
        from enhanced_server import (
            get_livescores, get_leagues, get_league_standings, 
            get_league_matches, get_team_info, get_player_info,
            extract_players_from_league
        )
        
        print("Successfully imported MCP functions!")
        
        # Test 1: Get leagues
        print("\n1. Testing get_leagues()")
        try:
            result = await get_leagues()
            leagues_data = json.loads(result)
            print(f"   SUCCESS: Found {len(leagues_data)} leagues")
            
            # Save result
            with open('mcp_leagues_direct_test.json', 'w') as f:
                json.dump(leagues_data, f, indent=2)
                
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # Test 2: Get EPL standings
        print("\n2. Testing get_league_standings(228) - EPL")
        try:
            result = await get_league_standings(228)
            standings_data = json.loads(result)
            print(f"   SUCCESS: Got EPL standings")
            
            # Save result
            with open('mcp_epl_standings_direct_test.json', 'w') as f:
                json.dump(standings_data, f, indent=2)
                
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # Test 3: Get EPL matches (our best endpoint)
        print("\n3. Testing get_league_matches(228) - EPL with events")
        try:
            result = await get_league_matches(228)
            matches_data = json.loads(result)
            print(f"   SUCCESS: Got EPL matches with events")
            
            # Count total events
            total_events = 0
            if isinstance(matches_data, list):
                for league_entry in matches_data:
                    if isinstance(league_entry, dict):
                        for stage in league_entry.get("stage", []):
                            if isinstance(stage, dict):
                                for match in stage.get("matches", []):
                                    if isinstance(match, dict):
                                        total_events += len(match.get("events", []))
            
            print(f"   Total events found: {total_events}")
            
            # Save result
            with open('mcp_epl_matches_direct_test.json', 'w') as f:
                json.dump(matches_data, f, indent=2)
                
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # Test 4: Get team info
        print("\n4. Testing get_team_info(4145) - Fulham")
        try:
            result = await get_team_info(4145)
            team_data = json.loads(result)
            print(f"   SUCCESS: Got Fulham team info")
            print(f"   Team: {team_data.get('name', 'Unknown')}")
            
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # Test 5: Get player info
        print("\n5. Testing get_player_info(62087) - Rodrigo Muniz")
        try:
            result = await get_player_info(62087)
            player_data = json.loads(result)
            print(f"   SUCCESS: Got player info")
            print(f"   Player: {player_data.get('name', 'Unknown')} (ID: {player_data.get('id')})")
            
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # Test 6: Extract players from league (our enhanced function)
        print("\n6. Testing extract_players_from_league(228) - EPL player extraction")
        try:
            result = await extract_players_from_league(228)
            players_data = json.loads(result)
            
            if "error" in players_data:
                print(f"   ERROR: {players_data['error']}")
            else:
                total_players = players_data.get("total_players_found", 0)
                print(f"   SUCCESS: Extracted {total_players} players from EPL")
                
                # Show some sample players
                players = players_data.get("players", {})
                sample_players = list(players.items())[:5]
                
                print(f"   Sample players:")
                for player_id, player_info in sample_players:
                    name = player_info.get("name", "Unknown")
                    teams = ", ".join(player_info.get("teams", []))
                    stats = player_info.get("stats", {})
                    goals = stats.get("goals", 0)
                    print(f"      {name} (ID: {player_id}) - {teams} - {goals} goals")
                
                # Save result
                with open('mcp_extracted_players_direct_test.json', 'w') as f:
                    json.dump(players_data, f, indent=2)
                
        except Exception as e:
            print(f"   ERROR: {e}")
        
        print(f"\n" + "=" * 60)
        print("MCP DIRECT TESTING COMPLETE")
        print("All functions tested successfully!")
        print("Check the generated JSON files for detailed data")
        
    except ImportError as e:
        print(f"Failed to import MCP functions: {e}")
        print("Make sure the enhanced_server.py is working correctly")

def main():
    print("MCP Functions Direct Testing")
    print("Testing enhanced MCP server functions without MCP protocol")
    
    # Run tests
    asyncio.run(test_mcp_functions())

if __name__ == "__main__":
    main()