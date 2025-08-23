#!/usr/bin/env python3
"""
Test Chronulus with real betting odds and improved text display
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the discord bot path to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mcp_leagues', 'discord_bot'))

from sports.mlb_handler import MLBHandler
from core.mcp_client import MCPClient

async def test_real_odds_chronulus():
    """Test Chronulus with real betting odds"""
    print("Testing Chronulus with Real Betting Odds...")
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
        # Get the last game (Athletics @ Seattle Mariners)
        today = datetime.now().strftime('%Y-%m-%d')
        matches = await mlb_handler.get_matches(today)
        
        if not matches:
            print("No games found")
            return
        
        test_match = matches[0]  # Should be Athletics @ Seattle Mariners
        print(f"Testing with: {test_match.away_team} @ {test_match.home_team}")
        
        # Get real betting odds
        print("\n1. Getting real betting odds...")
        betting_odds = await mlb_handler.get_betting_odds_for_game(test_match)
        
        if betting_odds:
            print("Real betting odds found:")
            for key, value in betting_odds.items():
                print(f"  {key}: {value}")
        else:
            print("WARNING: No betting odds available")
        
        # Test Chronulus with real odds
        print("\n2. Calling Chronulus with real betting odds...")
        chronulus_data = await mlb_handler.call_chronulus_analysis(
            test_match.home_team, 
            test_match.away_team, 
            betting_odds
        )
        
        if chronulus_data and "analysis" in chronulus_data:
            analysis = chronulus_data["analysis"]
            
            print("SUCCESS: Chronulus analysis with real odds received")
            print(f"Expert count: {analysis.get('expert_count', 'N/A')}")
            print(f"Home win probability: {analysis.get('home_team_win_probability', 'N/A'):.1%}")
            print(f"Away win probability: {analysis.get('away_team_win_probability', 'N/A'):.1%}")
            print(f"Recommendation: {analysis.get('betting_recommendation', 'N/A')}")
            
            # Check if analysis mentions real odds
            expert_analysis = analysis.get('expert_analysis', '')
            if expert_analysis:
                print(f"\nAnalysis text length: {len(expert_analysis)} characters")
                
                # Look for real odds in analysis
                if "+144" in expert_analysis or "-172" in expert_analysis:
                    print("SUCCESS: Real odds found in analysis!")
                elif "-100" in expert_analysis and "+100" in expert_analysis:
                    print("WARNING: Still seeing placeholder odds in analysis")
                else:
                    print("Analysis odds format unclear")
                
                # Show first part of analysis
                print("\nAnalysis preview:")
                print("-" * 40)
                print(expert_analysis[:400] + "...")
                print("-" * 40)
        
        print("\n3. Expected improvements:")
        print("- Chronulus should see: Athletics +144, Seattle Mariners -172")
        print("- Analysis should reference actual odds, not -100/+100")
        print("- Expert consensus should be longer and more detailed")
        print("- Should still recommend Athletics if they have value at +144")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_odds_chronulus())