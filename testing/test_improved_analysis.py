#!/usr/bin/env python3
"""
Test Improved Analysis - Specific Insights & Real Game Data
Verify that the fixes provide much better, specific analysis
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

async def test_improved_analysis():
    """Test the improved analysis with specific insights and real game data"""
    
    print("TESTING IMPROVED ANALYSIS - SPECIFIC INSIGHTS & REAL DATA")
    print("=" * 65)
    
    # Create mock MCP client and configuration
    mcp_client = MCPClient()
    config = {
        'mcp_url': 'https://mlbmcp-production.up.railway.app/mcp',
        'embed_color': 0x0066cc
    }
    
    # Create MLB handler
    mlb_handler = MLBHandler("mlb", config, mcp_client)
    
    try:
        # Create a realistic match object with complete real game data
        mock_match = Match(
            id="yankees_redsox_082325",
            home_team="New York Yankees",
            away_team="Boston Red Sox",
            league="MLB",
            datetime=datetime.fromisoformat("2025-08-23T19:05:00+00:00"),
            odds=None,
            status="scheduled",
            additional_data={
                "venue": "Yankee Stadium",
                "home_team_id": "147",
                "away_team_id": "111", 
                "home_record": "69-60 (.535)",
                "away_record": "71-59 (.546)",
                "time": "2025-08-23T19:05:00Z"
            }
        )
        
        print("REALISTIC GAME SETUP:")
        print(f"   Venue: {mock_match.additional_data['venue']}")
        print(f"   Date: August 23, 2025")
        print(f"   Home: {mock_match.home_team} ({mock_match.additional_data['home_record']})")
        print(f"   Away: {mock_match.away_team} ({mock_match.additional_data['away_record']})")
        
        # Realistic betting odds
        betting_odds = {
            "moneyline": "New York Yankees -168 | Boston Red Sox +142"
        }
        
        print(f"   Odds: Yankees -168, Red Sox +142")
        print(f"\nTesting improved Chronulus analysis...")
        
        # Test the improved call_chronulus_analysis method with match parameter
        analysis_result = await mlb_handler.call_chronulus_analysis(
            home_team=mock_match.home_team,
            away_team=mock_match.away_team,
            betting_odds=betting_odds,
            match=mock_match  # This should now pass real game data
        )
        
        if analysis_result:
            print("SUCCESS! Analysis completed")
            
            # Extract analysis text
            analysis_text = ""
            if isinstance(analysis_result, dict):
                if "analysis_text" in analysis_result:
                    analysis_text = analysis_result["analysis_text"]
                elif "analysis" in analysis_result and "expert_analysis" in analysis_result["analysis"]:
                    analysis_text = analysis_result["analysis"]["expert_analysis"]
                else:
                    analysis_text = str(analysis_result)
            
            # Check for major improvements
            improvements = {
                "Uses real venue": "Yankee Stadium" in analysis_text,
                "Uses real records": any(record in analysis_text for record in ["69-60", "71-59", ".535", ".546"]),
                "No TBD placeholders": "TBD" not in analysis_text and "Record TBD" not in analysis_text,
                "Specific insights": not any(generic in analysis_text.lower() for generic in ["favored at home", "odds suggest", "underdog team"]),
                "Shorter length": len(analysis_text) < 1500,  # Should be much shorter with 50-word limit
                "Clear picks": any(word in analysis_text.upper() for word in ["BET", "FADE", "PASS"])
            }
            
            print("\nANALYSIS IMPROVEMENTS:")
            total_score = sum(improvements.values())
            for improvement, detected in improvements.items():
                status = "FIXED" if detected else "NEEDS WORK"
                print(f"  {status:10} | {improvement}")
            
            improvement_percent = total_score / len(improvements) * 100
            print(f"\nIMPROVEMENT SCORE: {total_score}/{len(improvements)} ({improvement_percent:.1f}%)")
            
            if improvement_percent >= 83:
                print("EXCELLENT! Major improvements achieved")
            elif improvement_percent >= 67:
                print("GOOD! Most issues resolved")
            else:
                print("NEEDS MORE WORK! Issues remain")
            
            # Character analysis
            print(f"\nANALYSIS LENGTH: {len(analysis_text)} characters")
            if len(analysis_text) < 1000:
                print("Perfect for Discord (no truncation risk)")
            elif len(analysis_text) < 1500:
                print("Good for Discord (low truncation risk)")
            else:
                print("Still too long for Discord")
            
            # Show improved analysis sample
            print(f"\nIMPROVED ANALYSIS SAMPLE (first 600 chars):")
            print("-" * 60)
            print(analysis_text[:600] + ("..." if len(analysis_text) > 600 else ""))
            
            # Look for specific quality indicators
            quality_check = {
                "Team names used": mock_match.home_team in analysis_text and mock_match.away_team in analysis_text,
                "Venue mentioned": mock_match.additional_data['venue'] in analysis_text,
                "Records referenced": any(record in analysis_text for record in ["69-60", "71-59"]),
                "Confidence levels": any(conf in analysis_text for conf in ["%", "confidence", "Confidence"]),
                "Unit sizing": any(unit in analysis_text for unit in ["Units", "units", "Unit"])
            }
            
            print(f"\nQUALITY INDICATORS:")
            for indicator, present in quality_check.items():
                status = "YES" if present else "NO"
                print(f"  {status:3} | {indicator}")
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"improved_analysis_test_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "test_type": "improved_analysis_with_real_data",
                    "game": {
                        "home_team": mock_match.home_team,
                        "away_team": mock_match.away_team,
                        "venue": mock_match.additional_data["venue"],
                        "home_record": mock_match.additional_data["home_record"],
                        "away_record": mock_match.additional_data["away_record"],
                        "odds": betting_odds
                    },
                    "improvements": improvements,
                    "improvement_score": f"{total_score}/{len(improvements)} ({improvement_percent:.1f}%)",
                    "quality_check": quality_check,
                    "analysis_length": len(analysis_text),
                    "analysis_result": analysis_result
                }, f, indent=2)
            
            print(f"\nResults saved to: {filename}")
            
        else:
            print("FAILED! Analysis did not complete")
            return False
        
        return True
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_improved_analysis())
    if success:
        print("\nIMPROVED ANALYSIS TEST COMPLETED!")
    else:
        print("\nIMPROVED ANALYSIS TEST FAILED!")