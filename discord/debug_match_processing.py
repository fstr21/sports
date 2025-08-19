#!/usr/bin/env python3
"""
Debug the match data processing to see why 0 matches are processed
"""

import asyncio
import os
import json

# Set up test environment
os.environ.setdefault('DISCORD_BOT_TOKEN', 'test_bot_token_' + 'x' * 50)
os.environ.setdefault('SOCCER_MCP_URL', 'https://soccermcp-production.up.railway.app/mcp')

async def debug_match_processing():
    """Debug the match data processing"""
    print("🔍 Debugging Match Data Processing")
    print("=" * 50)
    
    from soccer_integration import SoccerMCPClient, SoccerDataProcessor
    
    client = SoccerMCPClient()
    processor = SoccerDataProcessor()
    
    # Get matches for a date that has data
    test_date = "2025-08-19"
    
    print(f"📅 Testing with date: {test_date}")
    
    try:
        # Get raw matches data
        matches_data = await client.get_matches_for_date(test_date)
        
        print(f"📊 Raw matches data structure:")
        print(f"   Type: {type(matches_data)}")
        print(f"   Keys: {list(matches_data.keys()) if isinstance(matches_data, dict) else 'Not a dict'}")
        
        if "matches_by_league" in matches_data:
            leagues = matches_data["matches_by_league"]
            print(f"   Leagues found: {list(leagues.keys())}")
            
            for league, matches in leagues.items():
                print(f"\n🏆 {league}:")
                print(f"   Type: {type(matches)}")
                
                if isinstance(matches, list):
                    print(f"   Count: {len(matches)}")
                    if matches:
                        print(f"   First match keys: {list(matches[0].keys()) if isinstance(matches[0], dict) else 'Not a dict'}")
                        print(f"   First match sample: {json.dumps(matches[0], indent=2)[:500]}...")
                elif isinstance(matches, dict):
                    print(f"   Keys: {list(matches.keys())}")
                    print(f"   Sample: {json.dumps(matches, indent=2)[:500]}...")
                else:
                    print(f"   Value: {matches}")
        
        # Try processing
        print(f"\n🔄 Processing matches...")
        processed_matches = processor.process_match_data(matches_data)
        print(f"   Processed count: {len(processed_matches)}")
        
        if processed_matches:
            for i, match in enumerate(processed_matches[:2]):
                print(f"   Match {i+1}: {match.away_team.name} vs {match.home_team.name} ({match.league.name})")
        else:
            print("   ❌ No matches were processed successfully")
            
            # Let's see what the processor expects vs what it gets
            print(f"\n🔍 Debugging processor expectations...")
            
            # Check if the processor has any specific format expectations
            if "matches_by_league" in matches_data:
                for league, matches in matches_data["matches_by_league"].items():
                    if matches:  # If there are matches
                        print(f"\n   Checking {league} format:")
                        if isinstance(matches, list) and matches:
                            sample_match = matches[0]
                            required_fields = ["id", "teams", "date", "time", "status"]
                            for field in required_fields:
                                has_field = field in sample_match
                                print(f"     {field}: {'✅' if has_field else '❌'}")
                                
                            # Check teams structure
                            if "teams" in sample_match:
                                teams = sample_match["teams"]
                                print(f"     teams structure: {type(teams)}")
                                if isinstance(teams, dict):
                                    print(f"     teams keys: {list(teams.keys())}")
                                    if "home" in teams and "away" in teams:
                                        print(f"     home team: {teams['home']}")
                                        print(f"     away team: {teams['away']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_match_processing())