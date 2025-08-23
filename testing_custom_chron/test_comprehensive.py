#!/usr/bin/env python3
"""
Custom Chronulus Comprehensive Testing - Maximum Quality Settings

This script runs our custom implementation with settings that match the 
comprehensive Chronulus test:
- 5 experts for multi-perspective analysis
- Detailed 15-20 sentence analysis per expert  
- Same game data for direct comparison
"""

import asyncio
import os
from dotenv import load_dotenv
from custom_chronulus_openrouter import (
    CustomChronulusSession, 
    CustomBinaryPredictor,
    RedSoxYankeesGameData
)
from datetime import datetime
import json

# Load environment variables
load_dotenv(".env.local")
load_dotenv("../.env.local")

async def test_comprehensive_custom_chronulus():
    """Test custom implementation with comprehensive settings"""
    
    print("🚀 CUSTOM CHRONULUS - COMPREHENSIVE TESTING")
    print("=" * 60)
    print("🔥 REAL GAME DATA: Boston Red Sox @ New York Yankees")
    print(f"🤖 MODEL: {os.getenv('OPENROUTER_MODEL', 'Default')}")
    print("👨‍⚖️ EXPERTS: 5 (matching comprehensive Chronulus test)")
    print("📝 ANALYSIS: 15-20 sentences per expert (detailed)")
    print("⚡ QUALITY: Maximum - institutional level analysis")
    print("🌐 API: OpenRouter")
    
    # Create comprehensive session - matching Chronulus expert persona
    session = CustomChronulusSession(
        name="Comprehensive MLB Expert Analysis: Red Sox @ Yankees",
        situation="You're a seasoned sports bettor with 15+ years of experience analyzing MLB games for profit. You've made your living finding edges in the market and you talk like it - direct, confident, and cutting through the BS. You're looking at a classic AL East rivalry matchup between two teams fighting for playoff positioning. The Red Sox are road favorites at -132 despite playing at Yankee Stadium, suggesting the market believes they have a significant edge. The Yankees have better recent form (7-3 vs 5-5 L10) but worse overall run prevention (4.30 vs 4.22 allowed/game). This is the type of game where advanced analysis can find edges the market might miss.",
        
        task="Give me your expert betting analysis on ALL THREE markets for this AL East rivalry game like you're talking to another experienced bettor at the sportsbook. Break down the key angles, market inefficiencies, and where you see real betting value. Focus on: 1) MONEYLINE: Red Sox -132 vs Yankees +112 - which side has value? 2) RUN LINE: Red Sox -1.5 (+118) vs Yankees +1.5 (-142) - is the spread right? 3) TOTAL: Over/Under runs - what does the venue and pitching suggest? For each market give me your pick, confidence level, key factors that drive your decision, what would make you change your mind, and your honest assessment of betting value. Write like you're breaking down the game with another sharp bettor who knows baseball. Use your analysis along with your gut feel. Give me 15-20 sentences of real insight, not fluff."
    )
    
    session.create()
    
    # Create predictor
    predictor = CustomBinaryPredictor(
        session=session,
        input_type=RedSoxYankeesGameData
    )
    
    predictor.create()
    
    # Same game data structure
    game_data = RedSoxYankeesGameData(
        home_team="New York Yankees (69-59, .539 win%, hot recent form 7-3 L10)",
        away_team="Boston Red Sox (70-59, .543 win%, road favorites but inconsistent 5-5 L10)",
        venue="Yankee Stadium (AL East rivalry atmosphere, home field advantage)",
        game_date="August 23, 2025",
        game_time="TBD",
        home_moneyline=112,
        away_moneyline=-132,
        home_run_line="Yankees +1.5 (-142)",
        away_run_line="Red Sox -1.5 (+118)", 
        over_under="Available in comprehensive betting analysis",
        home_record="69-59 (.539 win percentage)",
        away_record="70-59 (.543 win percentage)", 
        home_run_diff="+107 run differential (strong offense)",
        away_run_diff="+94 run differential (balanced team)",
        home_allowed_per_game=4.30,
        away_allowed_per_game=4.22,
        home_l10_form="7-3 in last 10 games (hot streak)",
        away_l10_form="5-5 in last 10 games (inconsistent)",
        division_rivalry="Classic AL East rivalry with playoff implications",
        playoff_implications="Both teams fighting for wild card spots - high stakes game",
        market_analysis="Red Sox favored on road suggests strong underlying metrics despite Yankees momentum"
    )
    
    print("\n📊 COMPREHENSIVE GAME DETAILS:")
    print(f"🏟️ Venue: {game_data.venue}")
    print(f"💰 Moneyline: Red Sox {game_data.away_moneyline} vs Yankees +{game_data.home_moneyline}")
    print(f"📈 Run Line: {game_data.away_run_line} vs {game_data.home_run_line}")
    print(f"📋 Records: Red Sox {game_data.away_record} vs Yankees {game_data.home_record}")
    print(f"🔥 Recent Form: Red Sox {game_data.away_l10_form} vs Yankees {game_data.home_l10_form}")
    
    # Queue prediction with 5 experts for comprehensive analysis
    print(f"\n🤖 Starting 5-Expert Comprehensive Analysis...")
    print(f"💰 Expected Cost: ~$0.05-0.15 (OpenRouter pricing)")
    print(f"⏱️ Expected Runtime: 90-180 seconds")
    
    request = await predictor.queue(
        item=game_data,
        num_experts=5,  # Match comprehensive Chronulus test
        note_length=(15, 20)  # Match comprehensive analysis depth
    )
    
    # Get predictions
    predictions = await predictor.get_request_predictions(request.request_id)
    
    if predictions and predictions[0]:
        result = request.result  # Get the actual result from the request
        
        print("\n🎯 COMPREHENSIVE ANALYSIS COMPLETE")
        print("=" * 50)
        print(f"🔴 Red Sox Win Probability: {result.prob_a:.1%}")
        print(f"⚾ Yankees Win Probability: {1-result.prob_a:.1%}")
        print(f"👥 Expert Panel Size: {result.expert_count}")
        print(f"📊 Beta Parameters: α={result.beta_params.alpha:.2f}, β={result.beta_params.beta:.2f}")
        print(f"🎲 Beta Mean: {result.beta_params.mean():.3f}")
        print(f"📈 Beta Variance: {result.beta_params.variance():.5f}")
        
        # Calculate betting edge
        implied_prob = 132 / (132 + 100)  # From -132 moneyline
        expert_edge = result.prob_a - implied_prob
        
        print(f"\n💰 COMPREHENSIVE BETTING ANALYSIS:")
        print(f"📈 Market Implied Prob: {implied_prob:.1%} (from -132)")
        print(f"🧠 Expert Consensus: {result.prob_a:.1%}")
        print(f"⚡ Edge: {expert_edge:+.2%} {'(POSITIVE EDGE)' if expert_edge > 0 else '(NEGATIVE EDGE)'}")
        print(f"🎯 Recommendation: {'BET RED SOX' if expert_edge > 0.02 else 'PASS - NO EDGE' if abs(expert_edge) <= 0.02 else 'BET YANKEES'}")
        
        print(f"\n📝 COMPREHENSIVE EXPERT PANEL ANALYSIS:")
        print("-" * 60)
        print(result.text)
        
        # Save comprehensive results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results = {
            "status": "success",
            "test_type": "comprehensive",
            "timestamp": timestamp,
            "session_id": session.session_id,
            "request_id": request.request_id,
            "game": "Boston Red Sox @ New York Yankees",
            "model_used": os.getenv('OPENROUTER_MODEL', 'Default'),
            "expert_count": result.expert_count,
            "analysis": {
                "red_sox_win_probability": result.prob_a,
                "yankees_win_probability": 1 - result.prob_a,
                "market_edge": expert_edge,
                "betting_recommendation": "BET RED SOX" if expert_edge > 0.02 else "PASS - NO EDGE" if abs(expert_edge) <= 0.02 else "BET YANKEES",
                "expert_analysis": result.text,
                "beta_params": {
                    "alpha": result.beta_params.alpha,
                    "beta": result.beta_params.beta
                }
            }
        }
        
        # Save comprehensive results
        import os as path_os
        results_dir = path_os.path.join(path_os.path.dirname(__file__), "results")
        path_os.makedirs(results_dir, exist_ok=True)
        
        json_filename = path_os.path.join(results_dir, f"comprehensive_custom_chronulus_{timestamp}.json")
        with open(json_filename, "w") as f:
            json.dump(results, f, indent=2)
        
        md_filename = path_os.path.join(results_dir, f"comprehensive_custom_chronulus_{timestamp}.md")
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(f"""# 🧠 Comprehensive Custom Chronulus Analysis Report

**Test Type**: Comprehensive (Maximum Quality)  
**Game**: Boston Red Sox @ New York Yankees  
**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Model**: {os.getenv('OPENROUTER_MODEL', 'Default')}  
**Session ID**: {session.session_id}  
**Expert Count**: {result.expert_count} (Comprehensive Panel)  

## 📊 Game Setup

- **Venue**: Yankee Stadium (AL East rivalry atmosphere)
- **Moneyline**: Red Sox -132 vs Yankees +112
- **Run Line**: Red Sox -1.5 (+118) vs Yankees +1.5 (-142)
- **Records**: Red Sox 70-59 (.543) vs Yankees 69-59 (.539)
- **Recent Form**: Red Sox 5-5 L10 vs Yankees 7-3 L10

## 🎯 Comprehensive AI Expert Analysis Results

### Probability Assessment
- **Red Sox Win Probability**: {result.prob_a:.1%}
- **Yankees Win Probability**: {1-result.prob_a:.1%}
- **Expert Panel Size**: {result.expert_count} AI experts (comprehensive analysis)

### Market Analysis
- **Market Implied Probability**: {implied_prob:.1%} (from -132 moneyline)
- **Expert Consensus**: {result.prob_a:.1%}
- **Betting Edge**: {expert_edge:+.2%}
- **Recommendation**: {results['analysis']['betting_recommendation']}

### Statistical Parameters
- **Beta Distribution**: α={result.beta_params.alpha:.2f}, β={result.beta_params.beta:.2f}
- **Beta Mean**: {result.beta_params.mean():.3f}
- **Beta Variance**: {result.beta_params.variance():.5f}

## 📝 Comprehensive Expert Panel Analysis

{result.text}

## 🔧 Technical Details

- **System**: Custom Chronulus Implementation with OpenRouter
- **API**: OpenRouter ({os.getenv('OPENROUTER_MODEL', 'Default')})
- **Analysis Depth**: 15-20 sentences per expert (comprehensive)
- **Expert Count**: 5 experts with different perspectives
- **Processing Time**: Real-time comprehensive analysis
- **Cost**: Estimated $0.05-0.15 per analysis (vs $0.75-1.50 for real Chronulus)
- **Accuracy**: Uses same Beta distribution consensus as original Chronulus

## 🎯 Comprehensive Conclusion

This comprehensive analysis used 5 AI experts with detailed 15-20 sentence analysis per expert to provide institutional-quality sports betting insights. The consensus probability of {result.prob_a:.1%} for a Red Sox victory suggests {"positive betting value" if expert_edge > 0.02 else "no clear betting edge" if abs(expert_edge) <= 0.02 else "negative betting value"} compared to the market's implied probability.

The comprehensive approach provides multiple analytical perspectives including statistical, situational, contrarian, and sharp bettor viewpoints for complete market analysis.

---
*Generated by Custom Chronulus AI - Comprehensive Analysis Mode*  
*Files saved: `{json_filename}` and `{md_filename}`*
""")
        
        print(f"\n📁 Comprehensive Results saved:")
        print(f"   JSON: results/{path_os.path.basename(json_filename)}")
        print(f"   MD:   results/{path_os.path.basename(md_filename)}")
        
        print(f"\n🚀 COMPREHENSIVE CUSTOM CHRONULUS SUCCESS!")
        print("-" * 60)
        print(f"✅ OpenRouter Integration: Working with {result.expert_count} experts")
        print(f"✅ Model Used: {os.getenv('OPENROUTER_MODEL', 'Default')}")
        print(f"✅ Analysis Depth: Comprehensive institutional-quality")
        print(f"✅ Expert Consensus: {result.expert_count} experts with detailed reasoning")
        print(f"✅ Cost Efficiency: ~90% cheaper than real Chronulus comprehensive")
        print(f"✅ Railway Ready: Can be deployed as high-quality MCP server")
        
        return results
    else:
        return {"status": "error", "message": "No comprehensive predictions received"}

if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Please set OPENROUTER_API_KEY in .env.local")
        exit(1)
        
    print("🧪 Starting Comprehensive Custom Chronulus Testing...")
    print("⏱️ This may take 90-180 seconds for comprehensive AI analysis...")
    print(f"🤖 Using Model: {os.getenv('OPENROUTER_MODEL', 'openai/gpt-oss-20b:free')}")
    print("👨‍⚖️ Expert Panel: 5 experts with detailed analysis")
    
    # Run the comprehensive test
    result = asyncio.run(test_comprehensive_custom_chronulus())
    
    print(f"\n✅ Comprehensive Testing Complete!")
    print(f"📊 Status: {result.get('status', 'unknown')}")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Compare with real Chronulus comprehensive analysis")  
    print("2. Evaluate quality differences vs cost savings")
    print("3. Deploy as Railway MCP server")
    print("4. Integration with Discord bot")