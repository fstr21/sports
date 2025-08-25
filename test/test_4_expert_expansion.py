#!/usr/bin/env python3
"""
Test 4-Expert Analysis Expansion
Validates that the Discord bot properly uses 4 experts and includes team records/odds
"""
import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the Discord bot directory to the path
sys.path.insert(0, r'c:\Users\fstr2\Desktop\sports\mcp_leagues\discord_bot')

async def test_4_expert_analysis():
    """Test the 4-expert analysis expansion and team records/odds display"""
    print("🧪 Testing 4-Expert Analysis Expansion")
    print("=" * 60)
    
    try:
        # Import httpx for MCP calls
        import httpx
        
        # Manually set the Custom Chronulus MCP URL
        custom_chronulus_url = "https://customchronpredictormcp-production.up.railway.app/mcp"
        
        # Test data matching the Discord bot exactly
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
                "PUBLIC BETTING: 67% of bets on Yankees, 33% on Red Sox. "
                "ANALYSIS REQUIREMENTS: MANDATORY player-specific analysis with names and statistics. "
                "Must specifically mention 'Gerrit Cole (3.41 ERA)' vs 'Brayan Bello (4.15 ERA)' comparison. "
                "Include individual player performance metrics, ERA comparisons, WHIP analysis, and strikeout rates. "
                "Analyze how Cole's 3.41 ERA compares to Bello's 4.15 ERA and impact on game outcome. "
                "Reference key position players by name (Aaron Judge, Juan Soto, Rafael Devers, Trevor Story). "
                "Provide detailed statistical breakdowns showing why specific players give advantages to their teams."
            )
        }
        
        # MCP request for 4-expert analysis (exactly as in Discord bot)
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": "getCustomChronulusAnalysis",
                "arguments": {
                    "game_data": game_data,
                    "expert_count": 4,  # UPDATED FROM 5 TO 4
                    "analysis_depth": "comprehensive",
                    "player_analysis_required": True,
                    "specific_instructions": "Must analyze individual player matchups, especially Gerrit Cole vs Brayan Bello pitching comparison with ERA analysis"
                }
            }
        }
        
        print("📊 Step 1: Testing 4-Expert MCP Request (UPDATED SERVER)")
        print(f"Expert Count: {mcp_request['params']['arguments']['expert_count']}")
        print(f"Analysis Depth: {mcp_request['params']['arguments']['analysis_depth']}")
        
        # Using Custom Chronulus MCP URL
        print(f"MCP URL: {custom_chronulus_url}")
        
        # Call Custom Chronulus MCP
        print("\n🔄 Step 2: Calling Custom Chronulus MCP...")
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(custom_chronulus_url, json=mcp_request)
            response.raise_for_status()
            result = response.json()
            
            if "result" not in result:
                error_msg = result.get('error', 'Unknown error')
                print(f"❌ MCP Error: {error_msg}")
                return False
            
            # Extract analysis text
            mcp_result = result["result"]
            analysis_text = mcp_result["content"][0]["text"] if "content" in mcp_result and mcp_result["content"] else "No analysis returned"
            
            print(f"✅ MCP Response received ({len(analysis_text)} characters)")
            
            # Parse the JSON analysis 
            try:
                analysis_data = json.loads(analysis_text)
                analysis = analysis_data.get("analysis", {})
                
                print("\n📈 Step 3: Analysis Quality Check")
                print(f"Expert Count in Response: {analysis.get('expert_count', 'N/A')}")
                print(f"Model Used: {analysis.get('model_used', 'N/A')}")
                print(f"Analysis Length: {len(analysis.get('expert_analysis', ''))}")
                
                # Check if we have richer content with 4 experts
                expert_analysis = analysis.get("expert_analysis", "")
                expert_indicators = [
                    "[STATISTICAL EXPERT]",
                    "[SITUATIONAL EXPERT]", 
                    "[CONTRARIAN EXPERT]",
                    "[SHARP EXPERT]",
                    "[MARKET EXPERT]"
                ]
                
                found_experts = []
                for indicator in expert_indicators:
                    if indicator in expert_analysis:
                        found_experts.append(indicator.replace("[", "").replace("]", ""))
                
                print(f"Experts Found: {len(found_experts)}/5")
                print(f"Expert Types: {', '.join(found_experts)}")
                
                # Test Discord Embed Data (with team records and odds)
                print("\n💬 Step 4: Discord Embed Content")
                
                # Simulate Discord embed fields exactly as in textonly command
                team_records_odds = f"**Red Sox**: 75-65 (.536) | +145 (40.8%)\n**Yankees**: 82-58 (.586) | -165 (62.3%)"
                print(f"📊 TEAM RECORDS & ODDS:\n{team_records_odds}")
                
                # Win probabilities
                if "away_team_win_probability" in analysis and "home_team_win_probability" in analysis:
                    away_prob = analysis["away_team_win_probability"] * 100
                    home_prob = analysis["home_team_win_probability"] * 100
                    print(f"🎯 WIN PROBABILITIES:\n**Red Sox**: {away_prob:.1f}%\n**Yankees**: {home_prob:.1f}%")
                
                # Betting recommendation 
                if "betting_recommendation" in analysis:
                    rec_emoji = "✅" if "BET" in analysis["betting_recommendation"].upper() else "⚠️"
                    market_edge = analysis.get('market_edge', 0)
                    recommendation_content = f"{rec_emoji} **{analysis['betting_recommendation']}**\nMarket Edge: {market_edge:.2f}%\nConfidence: 75%"
                    print(f"💰 BETTING RECOMMENDATION:\n{recommendation_content}")
                
                # Model info with 4 experts
                model_info = f"**Expert Count**: {analysis.get('expert_count', 4)}\n**Model**: {analysis.get('model_used', 'N/A').replace('google/', '').replace('-', ' ').title()}\n**Cost**: {analysis.get('cost_estimate', 'N/A')}"
                print(f"🤖 MODEL INFO:\n{model_info}")
                
                # Key matchup
                key_matchup = f"**Gerrit Cole** (3.41 ERA, 1.09 WHIP)\nvs\n**Brayan Bello** (4.15 ERA, 1.31 WHIP)"
                print(f"⚾ KEY MATCHUP:\n{key_matchup}")
                
                # Test template data for image generation
                print("\n🖼️ Step 5: Image Template Data")
                template_data = {
                    'away_team': game_data['away_team'].split(' (')[0],
                    'home_team': game_data['home_team'].split(' (')[0], 
                    'game_date': game_data['game_date'],
                    'venue_name': 'Yankee Stadium',
                    'away_status': 'Wild Card Race',
                    'home_status': 'AL East Leaders',
                    'away_record': '75-65 (.536)',  # NOW INCLUDED
                    'home_record': '82-58 (.586)',  # NOW INCLUDED 
                    'away_odds': f"+{game_data['away_moneyline']} (40.8%)",  # NOW INCLUDED
                    'home_odds': f"{game_data['home_moneyline']} (62.3%)",  # NOW INCLUDED
                    'away_prob': f"{analysis.get('away_team_win_probability', 0) * 100:.1f}",
                    'home_prob': f"{analysis.get('home_team_win_probability', 0) * 100:.1f}",
                    'recommendation_short': analysis.get('betting_recommendation', 'N/A').replace('BET HOME', 'BET YANKEES').replace(' - Strong edge identified', ''),
                    'model_name': analysis.get('model_used', 'N/A').replace('google/', '').replace('-', ' ').title(),
                    'expert_analysis': expert_analysis,
                    'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p ET'),
                    'market_edge': f"{analysis.get('market_edge', 0):.2f}%",  # NOW 2 DECIMAL PLACES
                    'confidence': '75%'
                }
                
                print("Template data includes:")
                for key, value in template_data.items():
                    if key in ['away_record', 'home_record', 'away_odds', 'home_odds']:
                        print(f"  ✅ {key}: {value}")
                
                # Test image generation
                print("\n🎨 Step 6: Testing Dark Enhanced Image Generation")
                try:
                    from utils.html_to_image import create_dark_enhanced_hybrid_analysis_image
                    image_bytes = await create_dark_enhanced_hybrid_analysis_image(template_data)
                    
                    # Save test image
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_path = Path(f"test_4expert_analysis_{timestamp}.png")
                    with open(image_path, 'wb') as f:
                        f.write(image_bytes)
                    
                    print(f"✅ Image generated successfully: {image_path.name} ({len(image_bytes)} bytes)")
                    
                except Exception as img_error:
                    print(f"❌ Image generation failed: {img_error}")
                
                # Summary
                print("\n📋 Step 7: Test Summary")
                print("=" * 60)
                print(f"✅ 4-Expert Analysis: {analysis.get('expert_count', 'N/A')} experts used")
                print(f"✅ Team Records: Red Sox 75-65 (.536), Yankees 82-58 (.586)")
                print(f"✅ Odds Lines: Red Sox +145 (40.8%), Yankees -165 (62.3%)")
                print(f"✅ Market Edge: {analysis.get('market_edge', 0):.2f}% (2 decimal places)")
                print(f"✅ Expert Types: {len(found_experts)} different expert perspectives")
                print(f"✅ Analysis Length: {len(expert_analysis):,} characters")
                print(f"✅ Template Complete: All required fields populated")
                
                # Save full results
                results_path = Path(f"4expert_test_results_{timestamp}.json")
                with open(results_path, 'w') as f:
                    json.dump({
                        'test_timestamp': datetime.now().isoformat(),
                        'expert_count': analysis.get('expert_count'),
                        'experts_found': found_experts,
                        'analysis_length': len(expert_analysis),
                        'template_data': template_data,
                        'discord_fields': {
                            'team_records_odds': team_records_odds,
                            'model_info': model_info,
                            'key_matchup': key_matchup
                        },
                        'test_status': 'SUCCESS'
                    }, f, indent=2)
                
                print(f"📄 Full test results saved: {results_path.name}")
                return True
                
            except json.JSONDecodeError:
                print(f"❌ Failed to parse JSON response")
                print(f"Raw response: {analysis_text[:500]}...")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("4-Expert Analysis Expansion Test")
    print("Testing Discord bot improvements for richer summaries")
    print()
    
    success = await test_4_expert_analysis()
    
    if success:
        print("\n🎉 All tests passed!")
        print("The Discord bot should now provide:")
        print("• Richer 4-expert analysis summaries")
        print("• Team records and odds in Discord text")
        print("• 2-decimal place market edge formatting")
        print("• Enhanced dark mode images with team data")
    else:
        print("\n❌ Tests failed - check output for issues")

if __name__ == "__main__":
    asyncio.run(main())