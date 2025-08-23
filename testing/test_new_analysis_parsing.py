#!/usr/bin/env python3
"""
Test new analysis text parsing
"""
import asyncio
import sys
import os

# Add the discord bot path to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mcp_leagues', 'discord_bot'))

from sports.mlb_handler import MLBHandler
from core.mcp_client import MCPClient
from core.base_sport_handler import Match

async def test_new_parsing():
    """Test new analysis parsing"""
    print("Testing New Expert Analysis Parsing...")
    print("=" * 60)
    
    # Create mock MCP client and configuration
    mcp_client = MCPClient()
    config = {
        'mcp_url': 'https://mlbmcp-production.up.railway.app/mcp',
        'embed_color': 0x0066cc
    }
    
    # Create MLB handler
    mlb_handler = MLBHandler("mlb", config, mcp_client)
    
    try:
        # Get the Athletics @ Seattle game
        today = "2025-08-23"  # Use specific date
        matches = await mlb_handler.get_matches(today)
        
        if not matches:
            print("No games found")
            return
        
        test_match = matches[0]
        print(f"Testing with: {test_match.away_team} @ {test_match.home_team}")
        
        # Create full comprehensive analysis with new parsing
        embeds = await mlb_handler.create_comprehensive_game_analysis(test_match)
        
        print(f"\nGenerated {len(embeds)} embeds")
        
        # Find the AI embed
        ai_embed = None
        for embed in embeds:
            if embed.title and ("AI Expert" in embed.title or "Expert Analysis" in embed.title):
                ai_embed = embed
                break
        
        if ai_embed:
            print("SUCCESS: AI Expert Analysis embed found!")
            print(f"Fields: {len(ai_embed.fields)}")
            
            for field in ai_embed.fields:
                field_name = field.name
                field_value = field.value
                
                # Check for Expert Consensus content
                if "Expert Consensus" in field_name or "Consensus" in field_name:
                    print(f"\nExpert Consensus Field:")
                    print(f"Length: {len(field_value)} characters")
                    preview = field_value[:200].replace('\n', ' ')
                    print(f"Preview: {preview}...")
                    
                    if "Statistical Expert:" in field_value:
                        print("SUCCESS: Real statistical expert analysis found!")
                    elif len(field_value) < 50:
                        print("WARNING: Expert consensus still too short")
                    else:
                        print("PARTIAL: Some expert content found")
                
                # Check for Key Insights content
                elif "Key Expert" in field_name or "Insights" in field_name:
                    print(f"\nKey Expert Insights Field:")
                    print(f"Length: {len(field_value)} characters")
                    preview = field_value[:200].replace('\n', ' ')
                    print(f"Preview: {preview}...")
                    
                    if "Statistical:" in field_value or "Situational:" in field_value:
                        print("SUCCESS: Real expert insights found!")
                    elif "Analysis 1 of 3" in field_value:
                        print("WARNING: Still showing placeholder insights")
                    else:
                        print("PARTIAL: Some insight content found")
        else:
            print("ERROR: No AI Expert Analysis embed found")
        
        print(f"\n{'='*60}")
        print("EXPECTED IMPROVEMENTS:")
        print("- Expert Consensus should show actual statistical analysis")
        print("- Key Expert Insights should show real betting insights")
        print("- No more 'Analysis 1 of 3...' placeholders")
        print("- Rich, detailed expert commentary on the game")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_new_parsing())