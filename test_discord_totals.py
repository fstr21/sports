#!/usr/bin/env python3
"""
Test Discord bot MLB totals integration
"""
import asyncio
import sys
import os

# Add the discord bot path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp_leagues', 'discord_bot'))

from sports.mlb_handler import MLBHandler
from core.mcp_client import MCPClient
from datetime import datetime, timedelta

async def test_discord_mlb_totals():
    """Test MLB totals integration with Discord bot"""
    print("Testing Discord MLB Totals Integration...")
    
    # Create mock MCP client and configuration
    mcp_client = MCPClient()
    config = {
        'mcp_url': 'https://mlbmcp-production.up.railway.app/mcp',
        'embed_color': 0x0066cc,
        'channel_creation_delay': 1.0
    }
    
    # Create MLB handler
    mlb_handler = MLBHandler("mlb", config, mcp_client)
    
    try:
        # Test with today's date
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"Testing with date: {today}")
        
        # Get matches for today
        matches = await mlb_handler.get_matches(today)
        
        if not matches:
            print("No MLB games found for today, trying tomorrow...")
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            matches = await mlb_handler.get_matches(tomorrow)
            
        if not matches:
            print("No MLB games found for today or tomorrow")
            return
        
        print(f"Found {len(matches)} MLB games")
        
        # Test with first game
        first_match = matches[0]
        print(f"Testing with: {first_match.away_team} @ {first_match.home_team}")
        
        # Create comprehensive analysis embeds
        embeds = await mlb_handler.create_comprehensive_game_analysis(first_match)
        
        print(f"Generated {len(embeds)} embeds")
        
        # Check first embed for betting grid
        if embeds:
            first_embed = embeds[0]
            print("\nFirst embed fields:")
            
            for field in first_embed.fields:
                field_name = field.name
                field_value = field.value
                
                if "Over" in field_name or "Under" in field_name:
                    print(f"SUCCESS: Found totals field - {field_name}: {field_value}")
                elif "Betting Lines" in field_name or "💰" in field_name:
                    print(f"Betting header found: {field_name}")
                elif field_name in ["Moneyline", "Run Line"]:
                    print(f"Other betting field: {field_name}")
        
        # Test betting odds function directly
        betting_odds = await mlb_handler.get_betting_odds_for_game(first_match)
        print(f"\nDirect betting odds result: {betting_odds}")
        
        if betting_odds and 'total' in betting_odds:
            total_raw = betting_odds['total']
            print(f"Raw total format: '{total_raw}'")
            
            # Test parsing logic
            total_line, over_odds, under_odds = "N/A", "N/A", "N/A"
            if total_raw and total_raw != "N/A" and "O/U" in total_raw:
                try:
                    if " " in total_raw:
                        parts = total_raw.split(" ", 2)
                        if len(parts) >= 2:
                            total_line = parts[1]
                            print(f"Parsed total line: {total_line}")
                            
                            if len(parts) >= 3 and "/" in parts[2]:
                                odds_part = parts[2]
                                odds_split = odds_part.split("/")
                                if len(odds_split) >= 2:
                                    over_odds = odds_split[0].strip()
                                    under_odds = odds_split[1].strip()
                                    print(f"Parsed over odds: {over_odds}")
                                    print(f"Parsed under odds: {under_odds}")
                except Exception as e:
                    print(f"Parsing error: {e}")
            
            # Test embed field names
            over_field_name = f"Over {total_line}" if total_line != "N/A" else "Over"
            under_field_name = f"Under {total_line}" if total_line != "N/A" else "Under"
            print(f"Discord field names would be: '{over_field_name}' and '{under_field_name}'")
    
    except Exception as e:
        print(f"ERROR in Discord test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_discord_mlb_totals())