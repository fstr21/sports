#!/usr/bin/env python3
"""
Test Enhanced Pitcher Integration
Validate the improved pitcher panel in MLB handler
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the discord bot path to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mcp_leagues', 'discord_bot'))

from sports.mlb_handler import MLBHandler
from core.mcp_client import MCPClient

async def test_enhanced_pitcher_integration():
    """Test the enhanced pitcher panel integration"""
    
    print("🥎 TESTING ENHANCED PITCHER PANEL INTEGRATION")
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
        print("🔍 Testing enhanced pitcher context method...")
        
        # Test with real teams
        test_teams = [
            ("New York Yankees", "Boston Red Sox"),
            ("Los Angeles Dodgers", "San Diego Padres"),
            ("Houston Astros", "Seattle Mariners")
        ]
        
        for home_team, away_team in test_teams:
            print(f"\n📊 Testing: {away_team} @ {home_team}")
            print("-" * 40)
            
            # Test enhanced pitcher context
            pitcher_context = await mlb_handler._get_pitcher_context(home_team, away_team)
            
            if pitcher_context:
                print(f"✅ Pitcher context generated: {len(pitcher_context)} characters")
                
                # Check for key elements of enhanced panel
                enhanced_features = {
                    "Comprehensive format": "STARTING PITCHER MATCHUP INTELLIGENCE" in pitcher_context,
                    "Team sections": all(team in pitcher_context for team in [home_team, away_team]),
                    "Statistics": any(term in pitcher_context for term in ["ERA", "WHIP", "K/9"]),
                    "Recent form": "Recent Form:" in pitcher_context,
                    "Matchup analysis": "MATCHUP ANALYSIS:" in pitcher_context,
                    "Betting implications": "BETTING IMPLICATIONS:" in pitcher_context,
                    "Visual indicators": any(emoji in pitcher_context for emoji in ["🔥", "✅", "⚠️", "❌"])
                }
                
                print("🎯 Enhanced Panel Features:")
                for feature, detected in enhanced_features.items():
                    status = "✅" if detected else "❌"
                    print(f"  {status} {feature}: {'DETECTED' if detected else 'MISSING'}")
                
                # Show sample of the panel
                if len(pitcher_context) > 300:
                    print(f"\n📖 Sample Panel (first 300 chars):")
                    print("-" * 30)
                    print(pitcher_context[:300] + "...")
                else:
                    print(f"\n📖 Full Panel:")
                    print("-" * 30)
                    print(pitcher_context)
                
                # Test with Custom Chronulus
                print(f"\n🧪 Testing panel with Custom Chronulus...")
                
                game_data = {
                    "home_team": f"{home_team} (Season Record TBD)",
                    "away_team": f"{away_team} (Season Record TBD)",
                    "venue": "Stadium TBD",
                    "game_date": datetime.now().strftime("%B %d, %Y"),
                    "additional_context": f"MLB Game Analysis with Enhanced Pitcher Intelligence:\n\n{pitcher_context}"
                }
                
                # Call Custom Chronulus
                chronulus_result = await test_chronulus_with_panel(game_data)
                
                if chronulus_result:
                    print("✅ Custom Chronulus analysis successful!")
                    
                    # Analyze pitcher intelligence in response
                    analysis_text = chronulus_result.get('analysis', {}).get('expert_analysis', '')
                    
                    pitcher_intelligence = {
                        "ERA mentions": analysis_text.upper().count('ERA'),
                        "WHIP mentions": analysis_text.upper().count('WHIP'),
                        "Strikeout mentions": sum(analysis_text.upper().count(term) for term in ['K/9', 'STRIKEOUT']),
                        "Pitcher names": sum(analysis_text.lower().count(team.lower().split()[-1]) for team in [home_team, away_team]),
                        "Recent form": sum(analysis_text.lower().count(term) for term in ['recent', 'form', 'last start'])
                    }
                    
                    print("📋 Pitcher Intelligence Detected:")
                    total_mentions = sum(pitcher_intelligence.values())
                    for metric, count in pitcher_intelligence.items():
                        print(f"  📊 {metric}: {count} mentions")
                    
                    print(f"\n🎯 Total Pitcher Intelligence Score: {total_mentions} mentions")
                    
                    if total_mentions >= 5:
                        print("🎉 EXCELLENT! Rich pitcher intelligence detected in analysis")
                    elif total_mentions >= 2:
                        print("✅ GOOD! Some pitcher intelligence present")
                    else:
                        print("⚠️ LIMITED! Pitcher intelligence may need enhancement")
                
                else:
                    print("❌ Custom Chronulus analysis failed")
                
                # Save results for review
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"enhanced_pitcher_test_{home_team.replace(' ', '')}_{away_team.replace(' ', '')}_{timestamp}.json"
                
                with open(filename, 'w') as f:
                    json.dump({
                        "timestamp": datetime.now().isoformat(),
                        "teams": {"home": home_team, "away": away_team},
                        "pitcher_context": pitcher_context,
                        "enhanced_features": enhanced_features,
                        "chronulus_result": chronulus_result,
                        "pitcher_intelligence": pitcher_intelligence if 'pitcher_intelligence' in locals() else {}
                    }, f, indent=2)
                
                print(f"💾 Test results saved to: {filename}")
                
            else:
                print(f"❌ No pitcher context generated for {away_team} @ {home_team}")
            
            print()  # Spacing between tests
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_chronulus_with_panel(game_data):
    """Test Custom Chronulus with enhanced pitcher panel"""
    
    try:
        import httpx
        
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": "getCustomChronulusAnalysis",
                "arguments": {
                    "game_data": game_data,
                    "expert_count": 5,
                    "analysis_depth": "comprehensive"
                }
            }
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://customchronpredictormcp-production.up.railway.app/mcp", 
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    content = result["result"]["content"][0]["text"]
                    analysis_data = json.loads(content)
                    return analysis_data
                else:
                    print(f"❌ Custom Chronulus error: {result}")
                    return None
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Error testing with Custom Chronulus: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_enhanced_pitcher_integration())