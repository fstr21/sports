#!/usr/bin/env python3
"""
Test Eastern Time conversion fix
"""
import asyncio
import sys
import os
from datetime import datetime, timezone, timedelta

# Add the discord bot path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp_leagues', 'discord_bot'))

from sports.mlb_handler import MLBHandler
from core.mcp_client import MCPClient

async def test_timezone_fix():
    """Test Eastern Time conversion"""
    print("Testing Eastern Time Conversion Fix...")
    
    # Create mock MCP client and configuration
    mcp_client = MCPClient()
    config = {
        'mcp_url': 'https://mlbmcp-production.up.railway.app/mcp',
        'embed_color': 0x0066cc
    }
    
    # Create MLB handler
    mlb_handler = MLBHandler("mlb", config, mcp_client)
    
    try:
        # Get today's games
        today = datetime.now().strftime('%Y-%m-%d')
        matches = await mlb_handler.get_matches(today)
        
        if not matches:
            print("No games found for today")
            return
        
        print(f"Found {len(matches)} games")
        
        # Find the Blue Jays game specifically 
        target_game = None
        for match in matches:
            if "Blue Jays" in match.away_team or "Marlins" in match.home_team:
                target_game = match
                break
        
        if not target_game:
            # Just use first 3 games if no Blue Jays game found
            games_to_check = matches[:3]
        else:
            games_to_check = [target_game] + [m for m in matches[:2] if m != target_game]
            
        # Check time conversion for each game
        for i, match in enumerate(games_to_check):
            print(f"\nGame {i+1}: {match.away_team} @ {match.home_team}")
            
            raw_time = match.additional_data.get('time', 'TBD')
            print(f"Raw time from API: {raw_time}")
            
            if raw_time != 'TBD' and 'T' in raw_time:
                try:
                    # Parse the ISO format time
                    dt_utc = datetime.fromisoformat(raw_time.replace('Z', '+00:00'))
                    print(f"UTC time: {dt_utc}")
                    
                    # Convert to Eastern (EDT = UTC-4)
                    eastern_tz = timezone(timedelta(hours=-4))
                    dt_eastern = dt_utc.astimezone(eastern_tz)
                    formatted_time = dt_eastern.strftime("%I:%M %p ET").lstrip('0')
                    formatted_date = dt_eastern.strftime("%B %d, %Y")
                    
                    print(f"Eastern time (EDT): {dt_eastern}")
                    print(f"Formatted for Discord: {formatted_time}")
                    print(f"Date: {formatted_date}")
                    
                    # Manual verification
                    hour_et = dt_eastern.hour
                    minute_et = dt_eastern.minute
                    print(f"Manual check: {hour_et:02d}:{minute_et:02d} ET")
                    
                except Exception as e:
                    print(f"Error parsing time: {e}")
            
            # Create embed to verify
            embed = await mlb_handler.format_match_analysis_new(match)
            if embed and embed.description:
                print(f"Embed description: {embed.description}")
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_timezone_fix())