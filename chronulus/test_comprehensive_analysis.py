#!/usr/bin/env python3
"""
Comprehensive Analysis Test - Full Game Data with Markdown Output
Test Custom Chronulus MCP with complete baseball game information
"""
import asyncio
import json
import httpx
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for .env access
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.local')

# Custom Chronulus MCP Server URL
CUSTOM_CHRONULUS_MCP_URL = "https://customchronpredictormcp-production.up.railway.app/mcp"

async def test_comprehensive_analysis():
    """Test with comprehensive game data and output to markdown"""
    
    print("🏟️ COMPREHENSIVE ANALYSIS TEST - FULL GAME DATA")
    print("=" * 60)
    print("Goal: Test with complete baseball game information")
    print("Output: Professional markdown analysis report")
    print()
    
    # COMPREHENSIVE GAME DATA - Yankees vs Red Sox
    comprehensive_game_data = {
        "home_team": "New York Yankees (82-58, .586 win%, AL East leaders)",
        "away_team": "Boston Red Sox (75-65, .536 win%, Wild Card contention)",
        "sport": "Baseball",
        "venue": "Yankee Stadium (49,642 capacity, pitcher-friendly dimensions, iconic atmosphere)",
        "game_date": "August 24, 2025 - 7:05 PM ET",
        "home_record": "82-58 (.586 win%), +89 run differential, 4.12 ERA, 7-3 L10, 43-26 home record",
        "away_record": "75-65 (.536 win%), +42 run differential, 4.38 ERA, 6-4 L10, 35-35 road record", 
        "home_moneyline": -165,
        "away_moneyline": +145,
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
    
    print("📊 COMPREHENSIVE INPUT DATA:")
    print(f"  Home: {comprehensive_game_data['home_team']}")
    print(f"  Away: {comprehensive_game_data['away_team']}")
    print(f"  Venue: {comprehensive_game_data['venue']}")
    print(f"  Date: {comprehensive_game_data['game_date']}")
    print(f"  Home Record: {comprehensive_game_data['home_record']}")
    print(f"  Away Record: {comprehensive_game_data['away_record']}")
    print(f"  Moneylines: Yankees {comprehensive_game_data['home_moneyline']}, Red Sox {comprehensive_game_data['away_moneyline']}")
    print(f"  Context Length: {len(comprehensive_game_data['additional_context'])} characters")
    print()
    
    # MCP request with comprehensive data and natural language format
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getCustomChronulusAnalysis",
            "arguments": {
                "game_data": comprehensive_game_data,
                "expert_count": 5,  # Full expert panel as per specifications
                "analysis_depth": "comprehensive"  # Most detailed analysis
            }
        }
    }
    
    try:
        print("🚀 SENDING COMPREHENSIVE REQUEST TO CUSTOM CHRONULUS MCP")
        print("-" * 60)
        print("Expert Panel: 5 AI specialists with natural language summaries")
        print("Analysis Depth: Comprehensive (detailed insights)")
        print("Data Quality: Complete game context with all available metrics")
        print("Output Format: Professional markdown report")
        
        async with httpx.AsyncClient(timeout=180.0) as client:  # Extended timeout for comprehensive analysis
            print("\n⏳ Requesting comprehensive analysis...")
            response = await client.post(CUSTOM_CHRONULUS_MCP_URL, json=mcp_request)
            response.raise_for_status()
            result = response.json()
            
            if "result" not in result:
                error_msg = result.get('error', 'Unknown error')
                print(f"❌ MCP Error: {error_msg}")
                return None
            
            # Parse response
            mcp_result = result["result"]
            if "content" not in mcp_result or not isinstance(mcp_result["content"], list):
                print(f"❌ Unexpected response format: {mcp_result}")
                return None
            
            analysis_text = mcp_result["content"][0]["text"]
            
            print("✅ SUCCESS: Comprehensive analysis completed!")
            
            try:
                # Parse JSON response
                analysis_data = json.loads(analysis_text)
                
                # Create comprehensive markdown report
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                markdown_file = f"c:/Users/fstr2/Desktop/sports/chronulus/results/comprehensive_analysis_{timestamp}.md"
                
                os.makedirs("c:/Users/fstr2/Desktop/sports/chronulus/results", exist_ok=True)
                
                # Generate markdown content
                with open(markdown_file, 'w', encoding='utf-8') as f:
                    f.write("# Comprehensive Baseball Analysis Report\n\n")
                    f.write(f"**Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}\n")
                    f.write(f"**Analysis System**: Enhanced Custom Chronulus MCP\n")
                    f.write(f"**Cost**: ~$0.15-0.30 (85% savings vs paid services)\n\n")
                    
                    f.write("---\n\n")
                    
                    # Game Information
                    f.write("## 🏟️ Game Information\n\n")
                    f.write(f"**Matchup**: {comprehensive_game_data['away_team']} @ {comprehensive_game_data['home_team']}\n\n")
                    f.write(f"**Venue**: {comprehensive_game_data['venue']}\n\n")
                    f.write(f"**Date & Time**: {comprehensive_game_data['game_date']}\n\n")
                    
                    # Team Records
                    f.write("## 📊 Team Performance\n\n")
                    f.write(f"**New York Yankees**\n")
                    f.write(f"- {comprehensive_game_data['home_record']}\n\n")
                    f.write(f"**Boston Red Sox**\n") 
                    f.write(f"- {comprehensive_game_data['away_record']}\n\n")
                    
                    # Betting Market
                    f.write("## 💰 Betting Market\n\n")
                    f.write(f"| Market | Yankees | Red Sox |\n")
                    f.write(f"|--------|---------|----------|\n")
                    f.write(f"| Moneyline | {comprehensive_game_data['home_moneyline']} | {comprehensive_game_data['away_moneyline']} |\n")
                    f.write(f"| Implied Probability | 62.3% | 40.8% |\n")
                    f.write(f"| Run Line | -1.5 (+115) | +1.5 (-135) |\n")
                    f.write(f"| Total | Over 9.0 (-108) | Under 9.0 (-112) |\n\n")
                    
                    # AI Analysis Results
                    if "analysis" in analysis_data:
                        analysis = analysis_data["analysis"]
                        
                        f.write("## 🤖 AI Analysis Results\n\n")
                        
                        # Win Probabilities
                        if "away_team_win_probability" in analysis and "home_team_win_probability" in analysis:
                            away_prob = analysis["away_team_win_probability"] * 100
                            home_prob = analysis["home_team_win_probability"] * 100
                            
                            f.write("### 🎯 Win Probability Assessment\n\n")
                            f.write(f"| Team | AI Probability | Market Implied | Edge |\n")
                            f.write(f"|------|----------------|----------------|------|\n")
                            f.write(f"| **Red Sox** | {away_prob:.1f}% | 40.8% | {away_prob - 40.8:+.1f}pp |\n")
                            f.write(f"| **Yankees** | {home_prob:.1f}% | 62.3% | {home_prob - 62.3:+.1f}pp |\n\n")
                        
                        # Betting Recommendation
                        if "betting_recommendation" in analysis:
                            f.write(f"### 💡 Recommendation\n\n")
                            f.write(f"**{analysis['betting_recommendation']}**\n\n")
                            
                            if "market_edge" in analysis:
                                edge = analysis["market_edge"] * 100
                                f.write(f"*Market Edge*: {edge:+.2f}%\n\n")
                        
                        # Expert Analysis
                        if "expert_analysis" in analysis:
                            f.write("## 👥 Expert Panel Analysis\n\n")
                            expert_text = analysis["expert_analysis"]
                            
                            # Parse expert sections
                            lines = expert_text.split('\n')
                            current_section = ""
                            
                            for line in lines:
                                if line.startswith('[') and ']' in line:
                                    # Expert header
                                    expert_name = line.split(']')[0].replace('[', '').strip()
                                    if expert_name:
                                        f.write(f"### {expert_name}\n\n")
                                    if ']' in line and len(line.split(']', 1)) > 1:
                                        content = line.split(']', 1)[1].strip()
                                        if content:
                                            f.write(f"{content}\n\n")
                                elif line.strip() and not line.startswith('ENHANCED') and not line.startswith('Expert Consensus'):
                                    # Regular content
                                    f.write(f"{line}\n\n")
                                elif 'FINAL CONSENSUS' in line:
                                    f.write("### 🎯 Final Consensus\n\n")
                                elif line.strip() and ('consensus' in line.lower() or 'probability' in line.lower()):
                                    f.write(f"{line}\n\n")
                        
                        # Technical Details
                        f.write("## 🔧 Technical Details\n\n")
                        f.write(f"- **Expert Count**: {analysis.get('expert_count', 'N/A')}\n")
                        f.write(f"- **Analysis Depth**: {analysis.get('analysis_depth', 'N/A')}\n")
                        f.write(f"- **AI Model**: {analysis.get('model_used', 'N/A')}\n")
                        f.write(f"- **Cost Estimate**: {analysis.get('cost_estimate', 'N/A')}\n")
                        
                        if "beta_params" in analysis:
                            beta = analysis["beta_params"]
                            f.write(f"- **Statistical Parameters**: α={beta.get('alpha', 0):.2f}, β={beta.get('beta', 0):.2f}\n")
                            f.write(f"- **Confidence Interval**: Mean={beta.get('mean', 0):.3f}, Variance={beta.get('variance', 0):.6f}\n")
                        
                        f.write("\n")
                    
                    # Raw Data Section
                    f.write("## 📋 Complete Game Context\n\n")
                    f.write("### Comprehensive Data Used in Analysis\n\n")
                    f.write("```\n")
                    f.write(comprehensive_game_data['additional_context'])
                    f.write("\n```\n\n")
                    
                    # Footer
                    f.write("---\n\n")
                    f.write("*This analysis was generated using the Enhanced Custom Chronulus MCP system, providing institutional-quality sports betting insights at 85% cost savings compared to traditional services.*\n\n")
                    f.write(f"*Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}*\n")
                
                print(f"\n📄 COMPREHENSIVE MARKDOWN REPORT CREATED")
                print("=" * 60)
                print(f"File: {markdown_file}")
                
                # Show summary
                if "analysis" in analysis_data:
                    analysis = analysis_data["analysis"]
                    if "away_team_win_probability" in analysis:
                        away_prob = analysis["away_team_win_probability"] * 100
                        home_prob = analysis["home_team_win_probability"] * 100
                        print(f"Red Sox Win Probability: {away_prob:.1f}%")
                        print(f"Yankees Win Probability: {home_prob:.1f}%")
                    
                    if "betting_recommendation" in analysis:
                        print(f"Recommendation: {analysis['betting_recommendation']}")
                
                print(f"\n✅ SUCCESS: Comprehensive analysis with full data complete!")
                return markdown_file
                
            except json.JSONDecodeError:
                # Handle text response
                print("📝 Received text response (not JSON)")
                
                # Create simpler markdown for text response
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                markdown_file = f"c:/Users/fstr2/Desktop/sports/chronulus/results/comprehensive_text_{timestamp}.md"
                
                with open(markdown_file, 'w', encoding='utf-8') as f:
                    f.write("# Comprehensive Baseball Analysis Report\n\n")
                    f.write(f"**Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}\n")
                    f.write(f"**Game**: {comprehensive_game_data['away_team']} @ {comprehensive_game_data['home_team']}\n\n")
                    f.write("## AI Analysis\n\n")
                    f.write("```\n")
                    f.write(analysis_text)
                    f.write("\n```\n")
                
                print(f"Text analysis saved to: {markdown_file}")
                return markdown_file
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    async def main():
        print("🏟️ COMPREHENSIVE CUSTOM CHRONULUS MCP TEST")
        print("Yankees vs Red Sox - Complete Game Analysis")
        print("=" * 70)
        
        result = await test_comprehensive_analysis()
        
        if result:
            print(f"\n🎉 SUCCESS!")
            print(f"Comprehensive markdown analysis report created: {result}")
            print(f"View the file for complete professional analysis with all data included.")
        else:
            print(f"\n❌ Analysis failed - check server configuration")
    
    asyncio.run(main())