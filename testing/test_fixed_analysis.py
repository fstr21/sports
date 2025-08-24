#!/usr/bin/env python3
"""
Test Fixed Analysis - Concise Expert Prompting & Real Game Data
Validate that experts are no longer cut off and actual game data is used
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

async def test_fixed_analysis():
    """Test the fixed analysis with concise expert prompting and real game data"""
    
    print("🔧 TESTING FIXED ANALYSIS - CONCISE EXPERTS & REAL GAME DATA")
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
        # Create a mock match object with real game data (simulating Yankees vs Red Sox)
        mock_match = Match(
            id="test_game_001",
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
        
        print("🏟️ Mock Game Setup:")
        print(f"   📍 Venue: {mock_match.additional_data['venue']}")
        print(f"   📅 Time: {mock_match.datetime}")
        print(f"   🏠 {mock_match.home_team} ({mock_match.additional_data['home_record']})")
        print(f"   ✈️ {mock_match.away_team} ({mock_match.additional_data['away_record']})")
        
        # Test the fixed call_chronulus_analysis method with real game data
        print(f"\n🧪 Testing Chronulus analysis with real game data...")
        
        # Mock betting odds
        betting_odds = {
            "moneyline": "New York Yankees -168 | Boston Red Sox +142"
        }
        
        analysis_result = await mlb_handler.call_chronulus_analysis(
            home_team=mock_match.home_team,
            away_team=mock_match.away_team,
            betting_odds=betting_odds,
            match=mock_match
        )
        
        if analysis_result:
            print("✅ Chronulus analysis completed successfully!")
            
            # Analyze the response for improvements
            analysis_text = ""
            if isinstance(analysis_result, dict):
                if "analysis_text" in analysis_result:
                    analysis_text = analysis_result["analysis_text"]
                elif "analysis" in analysis_result and "expert_analysis" in analysis_result["analysis"]:
                    analysis_text = analysis_result["analysis"]["expert_analysis"]
                else:
                    analysis_text = str(analysis_result)
            
            # Check for improvements
            improvements = {
                "No TBD references": "TBD" not in analysis_text,
                "Actual venue mentioned": "Yankee Stadium" in analysis_text,
                "Real records used": any(record in analysis_text for record in ["69-60", "71-59"]),
                "No speculation words": not any(word in analysis_text.lower() for word in ["might", "could", "assuming", "needs to be confirmed"]),
                "Concise format": len(analysis_text) < 2000,  # Should be much shorter now
                "Clear recommendations": any(word in analysis_text.upper() for word in ["BET", "FADE", "PASS"])
            }
            
            print("\n📊 Analysis Improvements:")
            total_score = sum(improvements.values())
            for improvement, detected in improvements.items():
                status = "✅" if detected else "❌"
                print(f"  {status} {improvement}: {'FIXED' if detected else 'STILL NEEDS WORK'}")
            
            print(f"\n🎯 Improvement Score: {total_score}/{len(improvements)} ({total_score/len(improvements)*100:.1f}%)")
            
            if total_score >= 4:
                print("🎉 EXCELLENT! Major improvements detected")
            elif total_score >= 3:
                print("✅ GOOD! Most issues resolved")
            else:
                print("⚠️ NEEDS MORE WORK! Several issues remain")
            
            # Show character count comparison
            print(f"\n📏 Analysis Length: {len(analysis_text)} characters")
            if len(analysis_text) < 1500:
                print("✅ Good length for Discord (unlikely to be cut off)")
            elif len(analysis_text) < 2000:
                print("⚠️ Moderate length (might be cut off in Discord)")
            else:
                print("❌ Too long (likely to be cut off in Discord)")
            
            # Show sample of concise analysis
            print(f"\n📖 Sample Analysis (first 500 chars):")
            print("-" * 50)
            print(analysis_text[:500] + ("..." if len(analysis_text) > 500 else ""))
            
            # Save results for review
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fixed_analysis_test_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "game": {
                        "home_team": mock_match.home_team,
                        "away_team": mock_match.away_team,
                        "venue": mock_match.additional_data["venue"],
                        "home_record": mock_match.additional_data["home_record"],
                        "away_record": mock_match.additional_data["away_record"]
                    },
                    "improvements": improvements,
                    "improvement_score": f"{total_score}/{len(improvements)}",
                    "analysis_length": len(analysis_text),
                    "analysis_result": analysis_result
                }, f, indent=2)
            
            print(f"\n💾 Test results saved to: {filename}")
            
        else:
            print("❌ Chronulus analysis failed")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fixed_analysis())
    if success:
        print("\n🎉 FIXED ANALYSIS TEST COMPLETED SUCCESSFULLY!")
    else:
        print("\n❌ FIXED ANALYSIS TEST FAILED!")