#!/usr/bin/env python3
"""
Debug why expert analysis text is missing from Discord display
"""
import asyncio
import sys
import os
import json

# Add the discord bot path to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mcp_leagues', 'discord_bot'))

from sports.mlb_handler import MLBHandler
from core.mcp_client import MCPClient
from core.base_sport_handler import Match

async def debug_missing_analysis():
    """Debug missing expert analysis text"""
    print("Debugging Missing Expert Analysis Text...")
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
        # Get real Chronulus data
        chronulus_data = await mlb_handler.call_chronulus_analysis("Seattle Mariners", "Athletics")
        
        if not chronulus_data:
            print("ERROR: No Chronulus data")
            return
        
        print("1. RAW CHRONULUS DATA:")
        print("-" * 40)
        analysis = chronulus_data.get("analysis", {})
        expert_analysis_text = analysis.get("expert_analysis", "")
        
        print(f"Keys in chronulus_data: {list(chronulus_data.keys())}")
        print(f"Keys in analysis: {list(analysis.keys())}")
        print(f"Expert analysis text length: {len(expert_analysis_text)}")
        
        if expert_analysis_text:
            print("\nExpert analysis text (first 500 chars):")
            print("=" * 50)
            print(expert_analysis_text[:500])
            print("=" * 50)
        else:
            print("ERROR: No expert_analysis text found!")
        
        # Test what the Discord parsing extracts
        print("\n2. DISCORD PARSING SIMULATION:")
        print("-" * 40)
        
        # Simulate the Discord bot parsing logic
        if expert_analysis_text:
            # Current parsing logic from Discord bot
            if "Expert Consensus:" in expert_analysis_text:
                consensus_section = expert_analysis_text.split("Expert Consensus:")[1].split("[")[0].strip()
                print("Found 'Expert Consensus:' section")
                print(f"Extracted: '{consensus_section[:200]}...'")
            else:
                # Get first section if no explicit consensus
                consensus_section = expert_analysis_text.split("\n\n")[0]
                print("No 'Expert Consensus:' found, using first section")
                print(f"Extracted: '{consensus_section[:200]}...'")
            
            # Clean and truncate appropriately for Discord embed
            consensus = consensus_section[:800] + "..." if len(consensus_section) > 800 else consensus_section
            print(f"\nFinal consensus for Discord: '{consensus[:200]}...'")
            print(f"Final consensus length: {len(consensus)}")
        
        # Test AI embed creation
        print("\n3. AI EMBED CREATION TEST:")
        print("-" * 40)
        
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
            print("AI embed created successfully")
            print(f"Number of fields: {len(ai_embed.fields)}")
            
            for field in ai_embed.fields:
                field_name = field.name.replace('👥', 'Expert Consensus').replace('💡', 'Key Insights')
                field_value = field.value[:150].replace('\n', ' ')
                print(f"Field: {field_name}")
                print(f"Value: '{field_value}...'")
                print()
        else:
            print("ERROR: Failed to create AI embed")
        
        print("4. EXPECTED vs ACTUAL:")
        print("-" * 40)
        print("Expected: Rich expert analysis with betting insights")
        print("Expected: 'Expert Consensus' field with actual analysis text")
        print("Expected: 'Key Expert Insights' with real expert reasoning")
        print()
        print("Actual: Empty fields with just placeholders")
        print("Issue: Expert analysis text not making it to Discord display")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_missing_analysis())