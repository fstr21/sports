#!/usr/bin/env python3
"""
Test Custom Chronulus MCP with Blue Jays @ Marlins game data from Discord screenshot
5-expert comprehensive analysis with results saved to files
"""

import asyncio
import json
import httpx
from datetime import datetime
import os

# Railway deployment URLs
RAILWAY_BASE_URL = "https://customchronpredictormcp-production.up.railway.app"
MCP_URL = f"{RAILWAY_BASE_URL}/mcp"

async def test_blue_jays_marlins_analysis():
    """Test with Blue Jays @ Marlins game data from screenshot"""
    
    print("TESTING BLUE JAYS @ MARLINS ANALYSIS")
    print("=" * 50)
    print("Game: Toronto Blue Jays @ Miami Marlins")
    print("Date: August 23, 2025")
    print("Time: 3:10 PM ET")
    print("Venue: loanDepot park")
    print("Expert Count: 5 (Maximum)")
    print("Analysis Depth: Comprehensive")
    print()
    
    # Game data extracted from Discord screenshot
    game_data = {
        "home_team": "Miami Marlins (60-68, .469 win%, struggling season)",
        "away_team": "Toronto Blue Jays (75-54, .581 win%, strong road team)",
        "venue": "loanDepot park (pitcher-friendly ballpark in Miami)",
        "game_date": "August 23, 2025",
        "home_record": "60-68 (.469 win percentage)",
        "away_record": "75-54 (.581 win percentage)",
        "home_moneyline": 118,  # Marlins underdog
        "away_moneyline": -138,  # Blue Jays favored
        "additional_context": """
        BETTING LINES FROM SCREENSHOT:
        - Moneyline: Blue Jays -138 vs Marlins +118
        - Run Line: Blue Jays -1.5 (+130) vs Marlins +1.5 (-156)
        - Over/Under: N/A (not shown)
        
        TEAM STATISTICS:
        Blue Jays: 75-54 record (.581), Run Diff: +56, Runs/Game: 4.45, L10 Form: 6-4
        Marlins: 60-68 record (.469), Run Diff: -65, Runs/Game: 4.81, L10 Form: 3-7
        
        KEY FACTORS:
        - Blue Jays are significantly better team (15-game advantage in wins)
        - Marlins struggling with poor recent form (3-7 L10)
        - Blue Jays road favorites despite playing away
        - loanDepot park is pitcher-friendly venue
        - Late season game with playoff implications for Blue Jays
        """
    }
    
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "getCustomChronulusAnalysis",
            "arguments": {
                "game_data": game_data,
                "expert_count": 5,  # Maximum experts
                "analysis_depth": "comprehensive"  # Maximum depth
            }
        },
        "id": 1
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("Starting 5-expert comprehensive analysis...")
            print("Expected runtime: 2-4 minutes")
            print("Expected cost: $0.10-0.25")
            print()
            
            start_time = datetime.now()
            response = await client.post(MCP_URL, json=request, timeout=300.0)  # 5 minute timeout
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if response.status_code != 200:
                print(f"HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
            result = response.json()
            
            if 'result' in result and result['result']['content']:
                content = json.loads(result['result']['content'][0]['text'])
                
                print("ANALYSIS COMPLETE!")
                print(f"Runtime: {duration:.1f} seconds")
                print("=" * 50)
                
                if content.get('status') == 'success':
                    analysis = content.get('analysis', {})
                    
                    # Display comprehensive results
                    print("COMPREHENSIVE 5-EXPERT ANALYSIS RESULTS:")
                    print("-" * 40)
                    print(f"Blue Jays Win Probability: {analysis.get('away_team_win_probability', 0):.1%}")
                    print(f"Marlins Win Probability: {analysis.get('home_team_win_probability', 0):.1%}")
                    print(f"Expert Panel Size: {analysis.get('expert_count', 0)}")
                    print(f"Analysis Quality: {analysis.get('analysis_depth', 'unknown')}")
                    
                    # Market analysis
                    market_edge = analysis.get('market_edge', 0)
                    print(f"\nBETTING ANALYSIS:")
                    print(f"Market Edge: {market_edge:+.2%}")
                    print(f"Recommendation: {analysis.get('betting_recommendation', 'unknown')}")
                    print(f"Actual Cost: {analysis.get('cost_estimate', 'unknown')}")
                    print(f"Model Used: {analysis.get('model_used', 'unknown')}")
                    
                    # Beta distribution parameters
                    beta_params = analysis.get('beta_params', {})
                    print(f"\nSTATISTICAL PARAMETERS:")
                    print(f"Beta Alpha: {beta_params.get('alpha', 0):.2f}")
                    print(f"Beta Beta: {beta_params.get('beta', 0):.2f}")
                    print(f"Beta Mean: {beta_params.get('mean', 0):.3f}")
                    print(f"Beta Variance: {beta_params.get('variance', 0):.5f}")
                    
                    # Save results to files
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # Save JSON
                    json_filename = f"blue_jays_marlins_5expert_{timestamp}.json"
                    json_path = os.path.join(os.path.dirname(__file__), json_filename)
                    with open(json_path, 'w') as f:
                        json.dump(content, f, indent=2)
                    
                    # Save Markdown report
                    md_filename = f"blue_jays_marlins_5expert_{timestamp}.md"
                    md_path = os.path.join(os.path.dirname(__file__), md_filename)
                    
                    with open(md_path, 'w', encoding='utf-8') as f:
                        f.write(f"""# Blue Jays @ Marlins - 5-Expert Analysis Report

**Game**: Toronto Blue Jays @ Miami Marlins  
**Date**: August 23, 2025 - 3:10 PM ET  
**Venue**: loanDepot park  
**Analysis**: 5-Expert Comprehensive Panel  
**Runtime**: {duration:.1f} seconds  
**Cost**: {analysis.get('cost_estimate', 'unknown')}  

## Game Setup

- **Records**: Blue Jays 75-54 (.581) vs Marlins 60-68 (.469)
- **Moneyline**: Blue Jays -138 vs Marlins +118  
- **Run Line**: Blue Jays -1.5 (+130) vs Marlins +1.5 (-156)
- **Recent Form**: Blue Jays 6-4 L10 vs Marlins 3-7 L10
- **Run Differential**: Blue Jays +56 vs Marlins -65

## AI Expert Analysis Results

### Probability Assessment
- **Blue Jays Win Probability**: {analysis.get('away_team_win_probability', 0):.1%}
- **Marlins Win Probability**: {analysis.get('home_team_win_probability', 0):.1%}
- **Expert Panel Size**: {analysis.get('expert_count', 0)} AI experts
- **Analysis Depth**: {analysis.get('analysis_depth', 'unknown')}

### Market Analysis  
- **Market Edge**: {market_edge:+.2%}
- **Betting Recommendation**: {analysis.get('betting_recommendation', 'unknown')}
- **Model Used**: {analysis.get('model_used', 'unknown')}

### Statistical Parameters
- **Beta Distribution**: α={beta_params.get('alpha', 0):.2f}, β={beta_params.get('beta', 0):.2f}
- **Beta Mean**: {beta_params.get('mean', 0):.3f}
- **Beta Variance**: {beta_params.get('variance', 0):.5f}

## Expert Panel Analysis

{analysis.get('expert_analysis', 'Analysis not available')}

## Technical Details

- **System**: Custom Chronulus Implementation (Railway MCP)
- **API**: OpenRouter with {analysis.get('model_used', 'unknown')}
- **Expert Count**: 5 comprehensive experts
- **Processing Time**: {duration:.1f} seconds
- **Cost Efficiency**: ~90% cheaper than real Chronulus

## Conclusion

This 5-expert comprehensive analysis provides institutional-quality insights for the Blue Jays @ Marlins matchup. The consensus probability of {analysis.get('away_team_win_probability', 0):.1%} for a Blue Jays victory {'suggests positive betting value' if market_edge > 0.02 else 'indicates no clear edge' if abs(market_edge) <= 0.02 else 'suggests negative betting value'} compared to the market's implied probability.

---
*Generated by Custom Chronulus AI - 5-Expert Comprehensive Analysis*  
*Files: {json_filename} and {md_filename}*
""")
                    
                    print(f"\nFILES SAVED:")
                    print(f"JSON: {json_filename}")
                    print(f"MD Report: {md_filename}")
                    
                    print(f"\nEXPERT ANALYSIS PREVIEW:")
                    expert_text = analysis.get('expert_analysis', '')
                    if expert_text:
                        # Show first 500 characters
                        preview = expert_text[:500] + "..." if len(expert_text) > 500 else expert_text
                        print(f"{preview}")
                    
                    return content
                    
                else:
                    print(f"Analysis failed: {content.get('error', 'unknown error')}")
                    return None
            else:
                print(f"Invalid response format: {result}")
                return None
                
        except Exception as e:
            print(f"Analysis failed: {e}")
            return None

async def main():
    """Run the Blue Jays @ Marlins test"""
    print("CUSTOM CHRONULUS MCP - BLUE JAYS @ MARLINS TEST")
    print("=" * 60)
    print("Testing comprehensive 5-expert analysis with real game data")
    print("From Discord screenshot: Blue Jays -138 @ Marlins +118")
    print()
    
    result = await test_blue_jays_marlins_analysis()
    
    if result:
        print("\nTEST COMPLETED SUCCESSFULLY!")
        print("5-expert comprehensive analysis generated")
        print("Results saved to JSON and Markdown files")
        print("Ready for betting decision analysis")
    else:
        print("\nTEST FAILED - Check error messages above")

if __name__ == "__main__":
    asyncio.run(main())