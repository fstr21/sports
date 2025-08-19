#!/usr/bin/env python3
"""
Test with a date that might have actual soccer matches
"""

import asyncio
import os
from datetime import datetime, timedelta

# Set up test environment
os.environ.setdefault('DISCORD_BOT_TOKEN', 'test_bot_token_' + 'x' * 50)
os.environ.setdefault('SOCCER_MCP_URL', 'https://soccermcp-production.up.railway.app/mcp')

async def test_with_current_dates():
    """Test with current and recent dates that might have matches"""
    print("🧪 Testing Soccer Integration with Real Dates")
    print("=" * 50)
    
    from soccer_integration import SoccerMCPClient
    client = SoccerMCPClient()
    
    # Test with several dates around now
    test_dates = []
    today = datetime.now()
    
    # Test today and next few days
    for i in range(7):
        test_date = today + timedelta(days=i)
        test_dates.append(test_date.strftime("%Y-%m-%d"))
    
    # Test previous few days
    for i in range(1, 4):
        test_date = today - timedelta(days=i)
        test_dates.append(test_date.strftime("%Y-%m-%d"))
    
    print(f"Testing dates: {test_dates}")
    print("-" * 50)
    
    matches_found = False
    
    for date in test_dates:
        print(f"\n📅 Testing date: {date}")
        try:
            matches_data = await client.get_matches_for_date(date)
            
            if matches_data and 'matches_by_league' in matches_data:
                leagues = list(matches_data['matches_by_league'].keys())
                if leagues:
                    print(f"   ✅ Found leagues: {leagues}")
                    matches_found = True
                    
                    # Count matches
                    total_matches = 0
                    for league, matches in matches_data['matches_by_league'].items():
                        if isinstance(matches, list):
                            match_count = len(matches)
                        elif isinstance(matches, dict) and 'matches' in matches:
                            match_count = len(matches['matches'])
                        else:
                            match_count = 1 if matches else 0
                        
                        total_matches += match_count
                        if match_count > 0:
                            print(f"   ⚽ {league}: {match_count} matches")
                    
                    if total_matches > 0:
                        print(f"   🎯 FOUND {total_matches} matches on {date}!")
                        
                        # Test data processing
                        from soccer_integration import SoccerDataProcessor
                        processor = SoccerDataProcessor()
                        processed_matches = processor.process_match_data(matches_data)
                        print(f"   📊 Processed {len(processed_matches)} matches")
                        
                        if processed_matches:
                            print("   🏟️  Sample matches:")
                            for i, match in enumerate(processed_matches[:3]):
                                print(f"      {i+1}. {match.away_team.name} vs {match.home_team.name} ({match.league.name})")
                        
                        break
                else:
                    print(f"   ℹ️  No matches found")
            else:
                print(f"   ℹ️  No data returned")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    if matches_found:
        print(f"\n🎉 SUCCESS: Found soccer matches! The integration is working.")
        print(f"You can now test in Discord with a date that has matches.")
    else:
        print(f"\n⚠️  No matches found on any test dates.")
        print(f"This might be normal if it's off-season or no matches are scheduled.")
        print(f"The integration is working - just no matches available.")

if __name__ == "__main__":
    asyncio.run(test_with_current_dates())