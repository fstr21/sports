#!/usr/bin/env python3
"""
Comprehensive Test for Enhanced Chronulus Discord Integration
Tests the exact same logic as /textonly but with detailed output analysis
"""
import asyncio
import json
import httpx
import os
from datetime import datetime

# Custom Chronulus MCP Server URL
CUSTOM_CHRONULUS_MCP_URL = "https://customchronpredictormcp-production.up.railway.app/mcp"

async def test_enhanced_chronulus_integration():
    """Test the enhanced Chronulus integration with comprehensive data"""
    
    print("🧪 ENHANCED CHRONULUS DISCORD INTEGRATION TEST")
    print("=" * 70)
    print("Testing comprehensive data structure and 5-expert analysis")
    print()
    
    # Enhanced comprehensive game data (exactly as used in Discord bot)
    game_data = {
        "home_team": "New York Yankees (82-58, .586 win%, AL East leaders)",
        "away_team": "Boston Red Sox (75-65, .536 win%, Wild Card contention)", 
        "sport": "Baseball",
        "venue": "Yankee Stadium (49,642 capacity, pitcher-friendly dimensions, iconic atmosphere)",
        "game_date": "August 24, 2025 - 7:05 PM ET",
        "home_record": "82-58 (.586 win%), +89 run differential, 4.12 ERA, 7-3 L10, 43-26 home record",
        "away_record": "75-65 (.536 win%), +42 run differential, 4.38 ERA, 6-4 L10, 35-35 road record",
        "home_moneyline": -165,
        "away_moneyline": 145,
        "additional_context": (
            "COMPLETE MARKET DATA: "
            "Moneyline - Yankees -165 (62.3% implied), Red Sox +145 (40.8% implied). "
            "Run Line - Yankees -1.5 (+115), Red Sox +1.5 (-135). "
            "Total - Over 9.0 (-108), Under 9.0 (-112). "
            "TEAM PERFORMANCE: "
            "Yankees: 82-58 record, +89 run differential (5.21 scored, 4.32 allowed), "
            "43-26 home record, 7-3 in last 10, currently 2.5 games ahead in AL East. "
            "Key players: Aaron Judge (.312 BA, 48 HR), Juan Soto (.288 BA, 35 HR). "
            "Red Sox: 75-65 record, +42 run differential (4.89 scored, 4.38 allowed), "
            "35-35 road record, 6-4 in last 10, fighting for Wild Card spot. "
            "Key players: Rafael Devers (.287 BA, 28 HR), Trevor Story (.251 BA, 15 HR). "
            "PITCHING MATCHUP: "
            "Yankees starter: Gerrit Cole (12-7, 3.41 ERA, 1.09 WHIP, 198 K). "
            "Red Sox starter: Brayan Bello (11-9, 4.15 ERA, 1.31 WHIP, 156 K). "
            "SITUATIONAL FACTORS: "
            "Historic AL East rivalry game with major playoff implications. "
            "Yankees need wins to secure division title. Red Sox need wins for Wild Card. "
            "Late season pressure, national TV audience, sellout crowd expected. "
            "Weather: 72°F, clear skies, 8mph wind from left field. "
            "Recent head-to-head: Yankees 7-6 this season vs Red Sox. "
            "BETTING TRENDS: "
            "Yankees 54-86 ATS this season, 21-48 ATS as home favorites. "
            "Red Sox 73-67 ATS this season, 34-31 ATS as road underdogs. "
            "Over/Under: Yankees games 68-72 O/U, Red Sox games 71-69 O/U. "
            "INJURY REPORT: "
            "Yankees: Giancarlo Stanton (hamstring, questionable). "
            "Red Sox: All key players healthy and available. "
            "PUBLIC BETTING: 67% of bets on Yankees, 33% on Red Sox."
        )
    }
    
    print("📊 GAME DATA ANALYSIS:")
    print(f"  Home Team: {game_data['home_team']}")
    print(f"  Away Team: {game_data['away_team']}")
    print(f"  Venue: {game_data['venue']}")
    print(f"  Moneylines: Yankees {game_data['home_moneyline']}, Red Sox +{game_data['away_moneyline']}")
    print(f"  Context Length: {len(game_data['additional_context'])} characters")
    print()
    
    # Test both 1-expert and 5-expert configurations
    expert_configs = [
        {"count": 1, "description": "Single Chief Analyst (current Discord)"},
        {"count": 5, "description": "5-Expert Panel (specification requirement)"}
    ]
    
    for config in expert_configs:
        print(f"🔬 TESTING {config['count']}-EXPERT CONFIGURATION")
        print(f"   {config['description']}")
        print("-" * 50)
        
        # MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": "getCustomChronulusAnalysis",
                "arguments": {
                    "game_data": game_data,
                    "expert_count": config["count"],
                    "analysis_depth": "comprehensive"
                }
            }
        }
        
        try:
            print(f"📡 Calling Custom Chronulus MCP (expert_count={config['count']})...")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(CUSTOM_CHRONULUS_MCP_URL, json=mcp_request)
                response.raise_for_status()
                result = response.json()
                
                if "result" not in result:
                    error_msg = result.get('error', 'Unknown error')
                    print(f"❌ MCP Error: {error_msg}")
                    continue
                
                # Extract analysis text
                mcp_result = result["result"]
                analysis_text = mcp_result["content"][0]["text"] if "content" in mcp_result and mcp_result["content"] else "No analysis returned"
                
                print(f"✅ Analysis received ({len(analysis_text)} characters)")
                
                # Export results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"enhanced_chronulus_test_{config['count']}expert_{timestamp}.md"
                export_path = f"c:\\Users\\fstr2\\Desktop\\sports\\{filename}"
                
                try:
                    with open(export_path, 'w', encoding='utf-8') as f:
                        f.write(f"# Enhanced Chronulus Test - {config['count']} Expert(s)\\n\\n")
                        f.write(f"**Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}\\n")
                        f.write(f"**Configuration**: {config['description']}\\n")
                        f.write(f"**Game**: {game_data['away_team']} @ {game_data['home_team']}\\n\\n")
                        f.write("## Raw MCP Response\\n\\n")
                        f.write("```json\\n")
                        f.write(json.dumps(result, indent=2))
                        f.write("\\n```\\n\\n")
                        f.write("## Analysis Text\\n\\n")
                        f.write(analysis_text)
                        f.write("\\n\\n---\\n\\n")
                        f.write("*This test validates the enhanced Chronulus integration for Discord bot deployment.*\\n")
                    
                    print(f"📄 Results exported to: {filename}")
                    
                    # Parse analysis for quality assessment
                    try:
                        analysis_data = json.loads(analysis_text)
                        if "analysis" in analysis_data:
                            analysis = analysis_data["analysis"]
                            
                            print("📈 ANALYSIS QUALITY METRICS:")
                            print(f"   Expert Count: {analysis.get('expert_count', 'N/A')}")
                            print(f"   Model Used: {analysis.get('model_used', 'N/A')}")
                            print(f"   Cost Estimate: {analysis.get('cost_estimate', 'N/A')}")
                            
                            if "away_team_win_probability" in analysis:
                                away_prob = analysis["away_team_win_probability"] * 100
                                home_prob = analysis.get("home_team_win_probability", 0) * 100
                                print(f"   Win Probabilities: Red Sox {away_prob:.1f}%, Yankees {home_prob:.1f}%")
                            
                            if "betting_recommendation" in analysis:
                                print(f"   Recommendation: {analysis['betting_recommendation']}")
                            
                            expert_analysis = analysis.get("expert_analysis", "")
                            if expert_analysis:
                                print(f"   Expert Analysis Length: {len(expert_analysis)} characters")
                                # Check for key quality indicators
                                quality_indicators = [
                                    "MARKET BASELINE",
                                    "FINAL ASSESSMENT",
                                    "Win Probability:",
                                    "Analyst Confidence:",
                                    "Recommendation:"
                                ]
                                found_indicators = [indicator for indicator in quality_indicators if indicator in expert_analysis]
                                print(f"   Quality Indicators Found: {len(found_indicators)}/5")
                                print(f"   Indicators: {', '.join(found_indicators)}")
                        else:
                            print("⚠️  Analysis data not in expected JSON format")
                            
                    except json.JSONDecodeError:
                        print("ℹ️  Analysis returned as text format (not JSON)")
                        # Check for quality indicators in raw text
                        quality_indicators = [
                            "MARKET BASELINE",
                            "FINAL ASSESSMENT", 
                            "Win Probability:",
                            "Analyst Confidence:",
                            "Recommendation:"
                        ]
                        found_indicators = [indicator for indicator in quality_indicators if indicator in analysis_text]
                        print(f"   Quality Indicators Found: {len(found_indicators)}/5")
                        print(f"   Indicators: {', '.join(found_indicators)}")
                    
                except Exception as file_error:
                    print(f"❌ Failed to export results: {file_error}")
                
                print()
                
        except Exception as e:
            print(f"❌ Test failed for {config['count']}-expert configuration: {e}")
            print()
    
    print("🎯 TEST COMPLETION")
    print("=" * 70)
    print("Compare the exported files to evaluate:")
    print("1. Analysis quality difference between 1-expert vs 5-expert")
    print("2. Whether comprehensive data is being utilized effectively")
    print("3. Discord formatting requirements vs full analysis content")
    print()

if __name__ == "__main__":
    asyncio.run(test_enhanced_chronulus_integration())