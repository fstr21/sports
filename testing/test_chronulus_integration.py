#!/usr/bin/env python3
"""
Test Custom Chronulus AI integration with Discord MLB handler
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the discord bot path to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mcp_leagues', 'discord_bot'))

from sports.mlb_handler import MLBHandler
from core.mcp_client import MCPClient

async def test_chronulus_integration():
    """Test Custom Chronulus integration with MLB handler"""
    print("Testing Custom Chronulus AI Integration...")
    
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
        # Test 1: Direct Chronulus call
        print("\n1. Testing direct Chronulus call...")
        chronulus_data = await mlb_handler.call_chronulus_analysis("New York Yankees", "Boston Red Sox")
        
        if chronulus_data:
            print("SUCCESS: Chronulus analysis received")
            if chronulus_data.get("format") == "text":
                text_len = len(chronulus_data.get("analysis_text", ""))
                print(f"Text format: {text_len} characters")
                print(f"Preview: {chronulus_data.get('analysis_text', '')[:200]}...")
            else:
                print(f"JSON format keys: {list(chronulus_data.keys())}")
                if "win_probability" in chronulus_data:
                    print(f"Win probability: {chronulus_data['win_probability']}%")
                if "expert_analyses" in chronulus_data:
                    print(f"Expert count: {len(chronulus_data['expert_analyses'])}")
        else:
            print("WARNING: No Chronulus data received")
        
        # Test 2: AI embed creation
        print("\n2. Testing AI embed creation...")
        if chronulus_data:
            # Create a mock match object
            from core.base_sport_handler import Match
            mock_match = Match(
                id="test",
                home_team="New York Yankees", 
                away_team="Boston Red Sox",
                league="MLB",
                datetime=None,
                odds=None,
                status="Scheduled",
                additional_data={}
            )
            
            ai_embed = await mlb_handler.create_ai_analysis_embed(mock_match, chronulus_data)
            if ai_embed:
                print("SUCCESS: AI embed created")
                print(f"Title: [AI Expert Analysis embed]")  # Avoid emoji encoding issues
                print(f"Description: {ai_embed.description[:50]}...")
                print(f"Fields: {len(ai_embed.fields)}")
                for field in ai_embed.fields:
                    field_name_safe = field.name.replace('🧠', '[BRAIN]').replace('🎲', '[DICE]').replace('👥', '[PEOPLE]')
                    print(f"  - {field_name_safe}: {len(field.value)} chars")
                print(f"Footer: {ai_embed.footer.text[:50] if ai_embed.footer else 'None'}...")
            else:
                print("ERROR: Failed to create AI embed")
        
        # Test 3: Full integration test
        print("\n3. Testing full integration with real game...")
        today = datetime.now().strftime('%Y-%m-%d')
        matches = await mlb_handler.get_matches(today)
        
        if matches:
            test_match = matches[0]
            print(f"Testing with: {test_match.away_team} @ {test_match.home_team}")
            
            # Create comprehensive analysis (should include AI embed)
            embeds = await mlb_handler.create_comprehensive_game_analysis(test_match)
            
            print(f"Generated {len(embeds)} embeds:")
            for i, embed in enumerate(embeds, 1):
                title = embed.title or "No title"
                print(f"  {i}. {title}")
                if "AI Expert" in title or "🧠" in title:
                    print("     ✓ AI Analysis embed found!")
            
            if len(embeds) == 3:
                print("SUCCESS: Full 3-embed integration working (Game + Props + AI)")
            elif len(embeds) == 2:
                print("PARTIAL: 2-embed format (Game + Props, no AI)")
            else:
                print(f"UNEXPECTED: {len(embeds)} embeds generated")
        else:
            print("No games found for testing")
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chronulus_integration())