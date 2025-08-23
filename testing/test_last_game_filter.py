#!/usr/bin/env python3
"""
Test last game filtering for Chronulus testing
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the discord bot path to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mcp_leagues', 'discord_bot'))

from sports.mlb_handler import MLBHandler
from core.mcp_client import MCPClient

async def test_last_game_filter():
    """Test filtering to only last game of the day"""
    print("Testing Last Game Filter for Chronulus...")
    print("=" * 50)
    
    # Create mock MCP client and configuration
    mcp_client = MCPClient()
    config = {
        'mcp_url': 'https://mlbmcp-production.up.railway.app/mcp',
        'embed_color': 0x0066cc
    }
    
    # Create MLB handler
    mlb_handler = MLBHandler("mlb", config, mcp_client)
    
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"Fetching MLB games for {today}...")
        
        # This should now return only the LAST game of the day
        matches = await mlb_handler.get_matches(today)
        
        if not matches:
            print("No games found")
            return
        
        print(f"Filtered to {len(matches)} game(s) for testing:")
        print("-" * 30)
        
        for match in matches:
            raw_time = match.additional_data.get('time', 'TBD')
            venue = match.additional_data.get('venue', 'Unknown Venue')
            
            print(f"Game: {match.away_team} @ {match.home_team}")
            print(f"Time: {raw_time}")
            print(f"Venue: {venue}")
            
            # Parse and display in Eastern Time
            if raw_time != 'TBD' and 'T' in raw_time:
                try:
                    if raw_time.endswith('Z'):
                        dt = datetime.fromisoformat(raw_time.replace('Z', '+00:00'))
                        from datetime import timezone, timedelta
                        eastern_tz = timezone(timedelta(hours=-4))
                        dt_eastern = dt.astimezone(eastern_tz)
                    else:
                        dt = datetime.fromisoformat(raw_time)
                        dt_eastern = dt
                    
                    formatted_time = dt_eastern.strftime("%I:%M %p ET").lstrip('0')
                    print(f"Eastern Time: {formatted_time}")
                except Exception as e:
                    print(f"Time parsing error: {e}")
            
            print()
        
        # Test the full 3-embed generation for this game
        if matches:
            test_match = matches[0]
            print("Testing 3-embed generation for selected game...")
            print(f"Creating analysis for: {test_match.away_team} @ {test_match.home_team}")
            
            embeds = await mlb_handler.create_comprehensive_game_analysis(test_match)
            
            print(f"Generated {len(embeds)} embeds:")
            for i, embed in enumerate(embeds, 1):
                title = embed.title or "Untitled"
                if "AI Expert" in title or "Expert Analysis" in title:
                    print(f"  {i}. AI Expert Analysis (Chronulus)")
                elif "Player Props" in title:
                    print(f"  {i}. Player Props + Stats")
                else:
                    print(f"  {i}. Game Analysis")
            
            if len(embeds) == 3:
                print("\nSUCCESS: Full 3-embed integration ready for testing!")
                print("Run /create-channels mlb to see the complete analysis")
            else:
                print(f"\nPARTIAL: {len(embeds)} embeds generated")
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_last_game_filter())