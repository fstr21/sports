#!/usr/bin/env python3
"""
Test Comprehensive Game Analysis - Single Deep Analysis vs Multiple Experts
Validate that the new approach provides better, more detailed insights
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the discord bot path to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mcp_leagues', 'discord_bot'))

from sports.mlb_handler import MLBHandler, Match
from core.mcp_client import MCPClient

async def test_comprehensive_analysis():
    """Test the new comprehensive game analysis approach"""
    
    print("TESTING COMPREHENSIVE GAME ANALYSIS - DEEPER INSIGHTS")
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
        # Test with different teams to prove it's data-driven
        test_games = [
            {
                "home_team": "Los Angeles Dodgers",
                "away_team": "San Diego Padres", 
                "venue": "Dodger Stadium",
                "home_record": "74-55 (.574)",
                "away_record": "68-61 (.527)",
                "home_ml": -150,
                "away_ml": +130
            },
            {
                "home_team": "Houston Astros",
                "away_team": "Seattle Mariners",
                "venue": "Minute Maid Park", 
                "home_record": "71-58 (.550)",
                "away_record": "66-63 (.512)",
                "home_ml": -120,
                "away_ml": +105
            }
        ]
        
        for i, game_data in enumerate(test_games, 1):
            print(f"\nTEST GAME {i}: {game_data['away_team']} @ {game_data['home_team']}")
            print(f"Venue: {game_data['venue']}")
            print(f"Records: {game_data['away_record']} vs {game_data['home_record']}")
            print(f"Odds: {game_data['home_team']} {game_data['home_ml']}, {game_data['away_team']} {game_data['away_ml']}")
            
            # Create match object
            mock_match = Match(
                id=f"test_game_{i}",
                home_team=game_data["home_team"],
                away_team=game_data["away_team"],
                league="MLB",
                datetime=datetime.fromisoformat("2025-08-23T19:05:00+00:00"),
                odds=None,
                status="scheduled",
                additional_data={
                    "venue": game_data["venue"],
                    "home_team_id": "100",
                    "away_team_id": "200", 
                    "home_record": game_data["home_record"],
                    "away_record": game_data["away_record"],
                    "time": "2025-08-23T19:05:00Z"
                }
            )
            
            # Mock betting odds
            betting_odds = {
                "moneyline": f"{game_data['home_team']} {game_data['home_ml']} | {game_data['away_team']} {game_data['away_ml']}"
            }
            
            print(f"\nGenerating comprehensive analysis...")
            
            # Test the new comprehensive analysis
            analysis_result = await mlb_handler.call_chronulus_analysis(
                home_team=game_data["home_team"],
                away_team=game_data["away_team"],
                betting_odds=betting_odds,
                match=mock_match
            )
            
            if analysis_result:
                print("SUCCESS! Comprehensive analysis generated")
                
                # Extract analysis text
                analysis_text = ""
                if isinstance(analysis_result, dict):
                    if "analysis_text" in analysis_result:
                        analysis_text = analysis_result["analysis_text"]
                    elif "analysis" in analysis_result and "expert_analysis" in analysis_result["analysis"]:
                        analysis_text = analysis_result["analysis"]["expert_analysis"]
                    else:
                        analysis_text = str(analysis_result)
                
                # Analyze quality of comprehensive analysis
                quality_metrics = {
                    "Uses actual teams": game_data["home_team"] in analysis_text and game_data["away_team"] in analysis_text,
                    "Uses actual venue": game_data["venue"] in analysis_text,
                    "Uses actual records": any(record in analysis_text for record in [game_data["home_record"], game_data["away_record"]]),
                    "Detailed insights": len(analysis_text.split()) > 100,  # Should be substantial
                    "Specific analysis": not any(generic in analysis_text.lower() for generic in ["generic", "basic", "simple"]),
                    "Clear recommendation": any(rec in analysis_text.upper() for rec in ["BET", "FADE", "PASS"]),
                    "Confidence levels": "%" in analysis_text,
                    "No TBD content": "TBD" not in analysis_text
                }
                
                print(f"\nQUALITY ANALYSIS:")
                quality_score = sum(quality_metrics.values())
                for metric, passed in quality_metrics.items():
                    status = "PASS" if passed else "FAIL"
                    print(f"  {status:4} | {metric}")
                
                quality_percent = quality_score / len(quality_metrics) * 100
                print(f"\nQUALITY SCORE: {quality_score}/{len(quality_metrics)} ({quality_percent:.1f}%)")
                
                # Length analysis
                word_count = len(analysis_text.split())
                char_count = len(analysis_text)
                print(f"\nANALYSIS DEPTH:")
                print(f"  Words: {word_count}")
                print(f"  Characters: {char_count}")
                
                if word_count >= 150:
                    print("  EXCELLENT depth - comprehensive analysis")
                elif word_count >= 100:
                    print("  GOOD depth - substantial analysis")
                else:
                    print("  NEEDS MORE depth - analysis too brief")
                
                # Show sample analysis
                print(f"\nSAMPLE ANALYSIS (first 400 chars):")
                print("-" * 50)
                print(analysis_text[:400] + ("..." if len(analysis_text) > 400 else ""))
                
                # Check for data-driven content
                data_driven_elements = {
                    "Record differential mentioned": any(term in analysis_text.lower() for term in ["record", "winning percentage", ".5"]),
                    "Venue impact discussed": game_data["venue"] in analysis_text,
                    "Odds analysis included": any(odd in analysis_text for odd in [str(game_data["home_ml"]), str(game_data["away_ml"])]),
                    "Team-specific insights": len([team for team in [game_data["home_team"], game_data["away_team"]] if analysis_text.count(team) >= 2]) >= 1
                }
                
                print(f"\nDATA-DRIVEN ANALYSIS:")
                for element, present in data_driven_elements.items():
                    status = "YES" if present else "NO"
                    print(f"  {status:3} | {element}")
                
            else:
                print("FAILED! No analysis generated")
            
            print("\n" + "="*60)
        
        return True
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_comprehensive_analysis())
    if success:
        print("\nCOMPREHENSIVE ANALYSIS TEST COMPLETED!")
    else:
        print("\nCOMPREHENSIVE ANALYSIS TEST FAILED!")