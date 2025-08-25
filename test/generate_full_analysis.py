#!/usr/bin/env python3
"""
Standalone script to generate FULL Custom Chronulus analysis and save as .md file
Run this locally to get complete untruncated analysis saved to test directory
"""

import asyncio
import httpx
import json
import os
from datetime import datetime

# Custom Chronulus MCP Configuration
CUSTOM_CHRONULUS_URL = "https://customchronpredictormcp-production.up.railway.app/mcp"

async def generate_full_analysis():
    """Generate complete analysis with no truncation and save as markdown file"""
    
    # Comprehensive game data (same as Discord bot)
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
    
    # MCP request for 5-expert analysis with player focus
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getCustomChronulusAnalysis",
            "arguments": {
                "game_data": game_data,
                "expert_count": 5,
                "analysis_depth": "comprehensive",
                "player_analysis_required": True,
                "specific_instructions": "Must analyze individual player matchups, especially Gerrit Cole vs Brayan Bello pitching comparison with ERA analysis"
            }
        }
    }
    
    print(f"🚀 Starting FULL Enhanced Chronulus Analysis (no truncation)...")
    print(f"⚾ Game: {game_data['away_team']} @ {game_data['home_team']}")
    print(f"🌐 Endpoint: {CUSTOM_CHRONULUS_URL}")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            print("📡 Calling Custom Chronulus MCP...")
            response = await client.post(CUSTOM_CHRONULUS_URL, json=mcp_request)
            response.raise_for_status()
            result = response.json()
            
            if "result" not in result:
                error_msg = result.get('error', 'Unknown error')
                print(f"❌ MCP Error: {error_msg}")
                return
            
            # Extract analysis text
            mcp_result = result["result"]
            analysis_text = mcp_result["content"][0]["text"] if "content" in mcp_result and mcp_result["content"] else "No analysis returned"
            
            print(f"✅ Received response: {len(analysis_text)} characters")
            
            # Parse the JSON analysis
            try:
                analysis_data = json.loads(analysis_text)
                analysis = analysis_data.get("analysis", {})
                
                # Generate timestamp for filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"full_chronulus_analysis_{timestamp}.md"
                
                # Get current script directory (test folder)
                script_dir = os.path.dirname(os.path.abspath(__file__))
                filepath = os.path.join(script_dir, filename)
                
                print(f"📄 Generating markdown file: {filename}")
                
                # Create comprehensive markdown content (NO TRUNCATION)
                markdown_content = f"""# Enhanced Chronulus Analysis - FULL Report

**Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}  
**Configuration**: {analysis.get('expert_count', 5)} Expert Panel Analysis  
**Game**: {game_data['away_team']} @ {game_data['home_team']}  
**Venue**: {game_data['venue']}  
**Date**: {game_data['game_date']}  

## Game Overview

### Teams
- **Away Team**: {game_data['away_team']}
  - Record: {game_data['away_record']}
  - Moneyline: +{game_data['away_moneyline']} (40.8% implied probability)

- **Home Team**: {game_data['home_team']}
  - Record: {game_data['home_record']}
  - Moneyline: {game_data['home_moneyline']} (62.3% implied probability)

## Win Probability Analysis

- **{game_data['away_team'].split(' (')[0]} Win Probability**: {analysis.get('away_team_win_probability', 0) * 100:.1f}%
- **{game_data['home_team'].split(' (')[0]} Win Probability**: {analysis.get('home_team_win_probability', 0) * 100:.1f}%

## Betting Recommendation

**Final Recommendation**: {analysis.get('betting_recommendation', 'N/A')}  
**Market Edge**: {analysis.get('market_edge', 0):.4f}  

## Complete Expert Analysis

{analysis.get('expert_analysis', 'No detailed analysis available')}

## Statistical Model Parameters

"""
                
                # Add beta parameters if available
                if "beta_params" in analysis:
                    beta = analysis["beta_params"]
                    markdown_content += f"""- **Alpha**: {beta.get('alpha', 0):.4f}
- **Beta**: {beta.get('beta', 0):.4f}
- **Mean**: {beta.get('mean', 0):.6f}
- **Variance**: {beta.get('variance', 0):.8f}

"""
                
                # Add model metadata
                markdown_content += f"""## Model Information

- **Model Used**: {analysis.get('model_used', 'N/A')}
- **Cost Estimate**: {analysis.get('cost_estimate', 'N/A')}
- **Session ID**: {analysis_data.get('session_id', 'N/A')}
- **Request ID**: {analysis_data.get('request_id', 'N/A')}
- **Timestamp**: {analysis_data.get('timestamp', 'N/A')}

## Raw Game Data Context

```json
{json.dumps(game_data, indent=2)}
```

## Quality Indicators

"""
                
                # Add quality indicators
                expert_analysis_text = analysis.get('expert_analysis', '')
                quality_indicators = [
                    "MARKET BASELINE",
                    "FINAL ASSESSMENT", 
                    "Win Probability:",
                    "Analyst Confidence:",
                    "Recommendation:"
                ]
                found_indicators = [indicator for indicator in quality_indicators if indicator in expert_analysis_text]
                
                markdown_content += f"""- **Indicators Found**: {len(found_indicators)}/5
- **Complete Analysis**: {'✅ Yes' if len(found_indicators) == 5 else '❌ No'}
- **Found Elements**: {', '.join(found_indicators)}

## Analysis Statistics

- **Total Characters**: {len(expert_analysis_text):,}
- **Analysis Depth**: {analysis.get('analysis_depth', 'N/A')}
- **Expert Count**: {analysis.get('expert_count', 'N/A')}

## Player Analysis Check

- **Gerrit Cole Mentioned**: {'✅ Yes' if 'Gerrit Cole' in expert_analysis_text or 'Cole' in expert_analysis_text else '❌ No'}
- **Brayan Bello Mentioned**: {'✅ Yes' if 'Bello' in expert_analysis_text else '❌ No'}
- **ERA Comparison**: {'✅ Yes' if 'ERA' in expert_analysis_text and ('3.41' in expert_analysis_text or '4.15' in expert_analysis_text) else '❌ No'}

---

*This analysis was generated by the Enhanced Custom Chronulus MCP Server*  
*Endpoint: {CUSTOM_CHRONULUS_URL}*  
*Report saved: {filepath}*
"""

                # Write the complete analysis to file (NO TRUNCATION!)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                print(f"✅ SUCCESS: Full analysis saved to {filepath}")
                print(f"📊 Analysis Statistics:")
                print(f"   - Expert Count: {analysis.get('expert_count', 'N/A')}")
                print(f"   - Model Used: {analysis.get('model_used', 'N/A')}")
                print(f"   - Total Characters: {len(expert_analysis_text):,}")
                print(f"   - Quality Indicators: {len(found_indicators)}/5")
                print(f"   - Gerrit Cole Mentioned: {'✅' if 'Cole' in expert_analysis_text else '❌'}")
                print(f"   - Brayan Bello Mentioned: {'✅' if 'Bello' in expert_analysis_text else '❌'}")
                print(f"   - File Size: {len(markdown_content):,} characters")
                
                return filepath
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parse Error: {e}")
                # Handle non-JSON response
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"raw_chronulus_output_{timestamp}.md"
                script_dir = os.path.dirname(os.path.abspath(__file__))
                filepath = os.path.join(script_dir, filename)
                
                markdown_content = f"""# Raw Chronulus Output

**Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}  
**Game**: {game_data['away_team']} @ {game_data['home_team']}  

## Raw Response

{analysis_text}

## Game Data

```json
{json.dumps(game_data, indent=2)}
```
"""
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                print(f"⚠️  Saved raw output to {filepath}")
                return filepath
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function to run the analysis"""
    print("🏈 Enhanced Chronulus Full Analysis Generator")
    print("=" * 50)
    
    # Run the async analysis
    result = asyncio.run(generate_full_analysis())
    
    if result:
        print(f"\n🎉 Analysis complete! Check the file: {result}")
        print("\nNext steps:")
        print("1. Review the generated .md file")
        print("2. If satisfied, proceed with image generation")
        print("3. Then implement the hybrid Discord approach")
    else:
        print("\n❌ Analysis failed. Check the error messages above.")

if __name__ == "__main__":
    main()