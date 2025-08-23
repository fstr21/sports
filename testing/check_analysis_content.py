#!/usr/bin/env python3
"""
Check actual analysis content for real odds usage
"""
import asyncio
import sys
import os

# Add the discord bot path to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mcp_leagues', 'discord_bot'))

from sports.mlb_handler import MLBHandler
from core.mcp_client import MCPClient

async def check_analysis_content():
    """Check if analysis contains real odds"""
    print("Checking Analysis Content for Real Odds...")
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
        # Get the Athletics @ Seattle game
        today = "2025-08-23"
        matches = await mlb_handler.get_matches(today)
        test_match = matches[0]
        
        # Get real betting odds
        betting_odds = await mlb_handler.get_betting_odds_for_game(test_match)
        
        # Call Chronulus
        chronulus_data = await mlb_handler.call_chronulus_analysis(
            test_match.home_team,
            test_match.away_team, 
            betting_odds
        )
        
        if chronulus_data and "analysis" in chronulus_data:
            analysis = chronulus_data["analysis"]
            expert_text = analysis.get('expert_analysis', '')
            
            print("FULL EXPERT ANALYSIS TEXT:")
            print("=" * 50)
            print(expert_text)
            print("=" * 50)
            
            # Look for specific odds patterns
            print("\nODDS ANALYSIS:")
            if "144" in expert_text:
                print("✓ Found '144' in text")
            if "-172" in expert_text:
                print("✓ Found '-172' in text")
            if "+144" in expert_text:
                print("✓ Found '+144' in text")
            if "Athletics 144" in expert_text:
                print("✓ Found 'Athletics 144' pattern")
            if "Seattle Mariners -172" in expert_text or "Mariners -172" in expert_text:
                print("✓ Found 'Mariners -172' pattern")
            if "-100" in expert_text and "+100" in expert_text:
                print("⚠ Still contains placeholder odds (-100/+100)")
            
            # Check the prompt format that was sent
            print(f"\nWin probabilities:")
            print(f"Home (Seattle): {analysis.get('home_team_win_probability', 0):.1%}")
            print(f"Away (Athletics): {analysis.get('away_team_win_probability', 0):.1%}")
            
            # This should show if Seattle is properly favored
            home_prob = analysis.get('home_team_win_probability', 0.5)
            if home_prob > 0.6:
                print("SUCCESS: Seattle heavily favored (as expected with -172 odds)")
            elif home_prob > 0.52:
                print("PARTIAL: Seattle slightly favored")
            else:
                print("WARNING: Not reflecting Seattle as favorite")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_analysis_content())