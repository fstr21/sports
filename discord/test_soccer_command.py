#!/usr/bin/env python3
"""
Quick test to see what happens when we try to create soccer channels
"""

import asyncio
import os
from datetime import datetime

# Set up test environment
os.environ.setdefault('DISCORD_BOT_TOKEN', 'test_bot_token_' + 'x' * 50)
os.environ.setdefault('SOCCER_MCP_URL', 'https://soccermcp-production.up.railway.app/mcp')

async def test_soccer_workflow():
    """Test the soccer channel creation workflow"""
    print("🧪 Testing Soccer Channel Creation Workflow")
    print("=" * 50)
    
    try:
        # Test 1: Import components
        print("1. Testing component imports...")
        from soccer_integration import SoccerMCPClient, SoccerDataProcessor
        from soccer_channel_manager import SoccerChannelManager
        print("   ✅ All components imported successfully")
        
        # Test 2: Initialize MCP client
        print("2. Testing MCP client initialization...")
        client = SoccerMCPClient()
        print("   ✅ MCP client initialized")
        
        # Test 3: Test MCP server connection
        print("3. Testing MCP server connection...")
        test_date = "2025-08-19"
        matches_data = await client.get_matches_for_date(test_date)
        print(f"   ✅ MCP server responded with data: {type(matches_data)}")
        
        if matches_data and 'matches_by_league' in matches_data:
            leagues = list(matches_data['matches_by_league'].keys())
            print(f"   📊 Found leagues: {leagues}")
            
            total_matches = 0
            for league, matches in matches_data['matches_by_league'].items():
                if isinstance(matches, list):
                    match_count = len(matches)
                elif isinstance(matches, dict) and 'matches' in matches:
                    match_count = len(matches['matches'])
                else:
                    match_count = 1 if matches else 0
                
                total_matches += match_count
                print(f"   ⚽ {league}: {match_count} matches")
            
            print(f"   📈 Total matches found: {total_matches}")
        else:
            print("   ⚠️  No matches found or invalid response format")
            print(f"   📋 Response keys: {list(matches_data.keys()) if matches_data else 'None'}")
        
        # Test 4: Test data processing
        print("4. Testing data processing...")
        processor = SoccerDataProcessor()
        processed_matches = processor.process_match_data(matches_data)
        print(f"   ✅ Processed {len(processed_matches)} matches")
        
        if processed_matches:
            for i, match in enumerate(processed_matches[:3]):  # Show first 3
                print(f"   🏟️  Match {i+1}: {match.away_team.name} vs {match.home_team.name} ({match.league.name})")
        
        # Test 5: Test embed creation
        print("5. Testing embed creation...")
        if processed_matches:
            from soccer_integration import SoccerEmbedBuilder
            builder = SoccerEmbedBuilder()
            embed = builder.create_match_preview_embed(processed_matches[0])
            print(f"   ✅ Embed created: {embed.title}")
            print(f"   🎨 Embed color: {embed.color}")
            print(f"   📝 Embed fields: {len(embed.fields)}")
        else:
            print("   ⚠️  No matches to create embeds for")
        
        print("\n" + "=" * 50)
        print("🎉 Soccer workflow test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error in soccer workflow: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_soccer_workflow())
    if success:
        print("\n✅ The soccer integration should work in Discord!")
        print("Try the command: /create-channels sport:Soccer date:08/19/2025")
    else:
        print("\n❌ There are issues that need to be fixed first.")