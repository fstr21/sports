#!/usr/bin/env python3
"""
Test fixed Chronulus parsing with real response data
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the discord bot path to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mcp_leagues', 'discord_bot'))

from sports.mlb_handler import MLBHandler
from core.mcp_client import MCPClient
from core.base_sport_handler import Match

async def test_fixed_parsing():
    """Test fixed Chronulus parsing"""
    print("Testing Fixed Chronulus Parsing...")
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
        # Test with real Chronulus call
        print("1. Testing Chronulus analysis call...")
        chronulus_data = await mlb_handler.call_chronulus_analysis("Seattle Mariners", "Athletics")
        
        if not chronulus_data:
            print("ERROR: No Chronulus data received")
            return
        
        print("SUCCESS: Chronulus data received")
        print(f"Keys: {list(chronulus_data.keys())}")
        
        # Check analysis content
        if "analysis" in chronulus_data:
            analysis = chronulus_data["analysis"]
            print(f"Analysis keys: {list(analysis.keys())}")
            print(f"Expert count: {analysis.get('expert_count', 'N/A')}")
            print(f"Home win prob: {analysis.get('home_team_win_probability', 'N/A')}")
            print(f"Recommendation: {analysis.get('betting_recommendation', 'N/A')}")
        
        # Test AI embed creation
        print("\n2. Testing AI embed creation...")
        
        # Create mock match
        mock_match = Match(
            id="test",
            home_team="Seattle Mariners",
            away_team="Athletics", 
            league="MLB",
            datetime=None,
            odds=None,
            status="Scheduled",
            additional_data={}
        )
        
        ai_embed = await mlb_handler.create_ai_analysis_embed(mock_match, chronulus_data)
        
        if ai_embed:
            print("SUCCESS: AI embed created with fixed parsing!")
            print(f"Title: AI Expert Analysis embed")
            print(f"Description: {ai_embed.description[:50]}...")
            print(f"Fields: {len(ai_embed.fields)}")
            
            # Check key fields
            for field in ai_embed.fields:
                field_name = field.name.replace('🎲', 'Win Probability').replace('👥', 'Expert Consensus').replace('💰', 'Betting Rec')
                field_value = field.value[:100].replace('\n', ' ')
                print(f"  - {field_name}: {field_value}...")
            
            print(f"Footer: Custom Chronulus AI footer")
        else:
            print("ERROR: Failed to create AI embed")
        
        print("\n3. Expected Results:")
        print("- Win Probability: Should show ~51.3% Seattle Mariners")
        print("- Expert Consensus: Should show actual expert analysis text")
        print("- Betting Recommendation: Should show 'NO CLEAR EDGE'")
        print("- Analysis Stats: Should show '3 AI analysts'")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fixed_parsing())