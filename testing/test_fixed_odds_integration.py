#!/usr/bin/env python3
"""
Test fixed odds integration with proper game_data structure
"""
import asyncio
import sys
import os

# Add the discord bot path to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mcp_leagues', 'discord_bot'))

from sports.mlb_handler import MLBHandler
from core.mcp_client import MCPClient

async def test_fixed_integration():
    """Test fixed odds integration"""
    print("Testing Fixed Odds Integration with Proper MCP Structure...")
    print("=" * 70)
    
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
        today = "2025-08-23"
        matches = await mlb_handler.get_matches(today)
        
        if not matches:
            print("No games found")
            return
        
        test_match = matches[0]
        print(f"Testing with: {test_match.away_team} @ {test_match.home_team}")
        
        # Get real betting odds
        betting_odds = await mlb_handler.get_betting_odds_for_game(test_match)
        
        if betting_odds:
            print("\nReal betting odds:")
            for key, value in betting_odds.items():
                print(f"  {key}: {value}")
        
        # Test Chronulus call with new structure
        print("\n1. Testing Chronulus call with proper game_data structure...")
        chronulus_data = await mlb_handler.call_chronulus_analysis(
            test_match.home_team,
            test_match.away_team, 
            betting_odds
        )
        
        if chronulus_data and "analysis" in chronulus_data:
            analysis = chronulus_data["analysis"]
            print("SUCCESS: Chronulus analysis received")
            print(f"Home win probability: {analysis.get('home_team_win_probability', 0):.1%}")
            print(f"Expert analysis length: {len(analysis.get('expert_analysis', ''))}")
            
            # Check if analysis mentions real odds
            expert_text = analysis.get('expert_analysis', '')
            if expert_text:
                if "+144" in expert_text or "-172" in expert_text:
                    print("SUCCESS: Real odds found in analysis text!")
                elif "Moneylines: Athletics 144 vs Seattle Mariners -172" in expert_text:
                    print("SUCCESS: Proper moneyline format found!")
                elif "-100" in expert_text and "+100" in expert_text:
                    print("WARNING: Still seeing placeholder odds")
                    print(f"Sample text: {expert_text[:200]}...")
                else:
                    print("UNKNOWN: Odds format unclear in analysis")
                    print(f"Sample text: {expert_text[:200]}...")
        
        # Test full embed creation
        print("\n2. Testing full 3-embed creation...")
        embeds = await mlb_handler.create_comprehensive_game_analysis(test_match)
        
        ai_embed = None
        for embed in embeds:
            if embed.title and ("AI Expert" in embed.title or "Expert Analysis" in embed.title):
                ai_embed = embed
                break
        
        if ai_embed:
            print("SUCCESS: AI embed created")
            
            for field in ai_embed.fields:
                if "Expert Consensus" in field.name:
                    field_length = len(field.value)
                    print(f"Expert Consensus field: {field_length} characters")
                    
                    if field_length > 1000:
                        print("WARNING: Field exceeds Discord limit!")
                    elif field_length < 100:
                        print("WARNING: Field too short, missing content")
                    else:
                        print("SUCCESS: Field length appropriate")
                    
                    # Check for real odds in consensus
                    if "+144" in field.value or "-172" in field.value:
                        print("SUCCESS: Real odds in consensus!")
                    else:
                        print("Status: Checking odds format...")
        
        print("\n3. Expected results:")
        print("- Expert analysis should reference Athletics +144, Seattle -172")
        print("- Consensus field should be 300-900 characters (within Discord limit)")
        print("- Analysis should show market favors Seattle heavily")
        print("- Recommendation might change based on real odds vs placeholders")
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fixed_integration())