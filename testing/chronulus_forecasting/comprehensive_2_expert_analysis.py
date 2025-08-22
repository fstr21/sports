#!/usr/bin/env python3
"""
Comprehensive 2-Expert Sports Analysis with Maximum Detail
Saves results to both MD and JSON formats with extensive expert reasoning
"""
import json
import os
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field

try:
    from chronulus import Session
    from chronulus.estimator import BinaryPredictor
    print("SUCCESS: Chronulus SDK loaded")
except ImportError:
    print("ERROR: Chronulus SDK not found")
    exit(1)

class ComprehensiveSportsData(BaseModel):
    """Comprehensive sports game data for detailed expert analysis"""
    # Basic game info
    home_team: str = Field(description="Pittsburgh Pirates - home team with detailed context")
    away_team: str = Field(description="Colorado Rockies - away team with detailed context")
    sport: str = Field(description="Major League Baseball - professional sport")
    game_date: str = Field(description="August 22, 2025 - specific game date")
    game_time: str = Field(description="5:40 PM ET start time")
    venue: str = Field(description="PNC Park in Pittsburgh - home venue advantage")
    
    # Season performance
    home_record: str = Field(description="Pirates season record 54-74 (.422 win percentage)")
    away_record: str = Field(description="Rockies season record 37-91 (.289 win percentage)")
    home_win_pct: float = Field(description="Pirates win percentage 0.422 - below average season")
    away_win_pct: float = Field(description="Rockies win percentage 0.289 - poor season performance")
    
    # Advanced analytics
    home_run_differential: int = Field(description="Pirates run differential -87 (scored 543, allowed 630)")
    away_run_differential: int = Field(description="Rockies run differential -339 (scored 437, allowed 776)")
    home_runs_allowed_pg: float = Field(description="Pirates allow 4.19 runs per game - decent pitching")
    away_runs_allowed_pg: float = Field(description="Rockies allow 6.42 runs per game - terrible pitching")
    home_runs_scored_pg: float = Field(description="Pirates score 4.54 runs per game - below average offense")
    away_runs_scored_pg: float = Field(description="Rockies score 3.62 runs per game - poor offense")
    
    # Recent form (critical factor)
    home_recent_form: str = Field(description="Pirates last 10 games: 3-7 record (struggling badly)")
    away_recent_form: str = Field(description="Rockies last 10 games: 7-3 record (surprisingly hot)")
    home_last_5: str = Field(description="Pirates last 5 games: 1-4 (terrible recent form)")
    away_last_5: str = Field(description="Rockies last 5 games: 4-1 (excellent recent form)")
    
    # Contextual factors
    form_divergence: str = Field(description="Recent form completely opposite of season trends - creates betting opportunity")
    home_field_advantage: str = Field(description="PNC Park provides moderate home advantage, especially for pitching")
    weather_conditions: str = Field(description="Expected clear weather, temperature 78°F, no wind factor")
    
    # Betting market
    home_moneyline: int = Field(description="Pirates favored at -190 (65.5% implied probability)")
    away_moneyline: int = Field(description="Rockies underdog at +160 (38.5% implied probability)")
    run_line_home: str = Field(description="Pirates -1.5 runs at +104 odds")
    run_line_away: str = Field(description="Rockies +1.5 runs at -125 odds")
    total_runs: str = Field(description="Over/Under 8.5 runs")
    
    # Key analysis points for experts
    momentum_factor: str = Field(description="Rockies riding 7-game winning streak vs Pirates 7-game losing streak")
    pitching_matchup: str = Field(description="Starting pitchers TBD - analyze based on team ERA trends")
    injury_report: str = Field(description="No major injuries reported for either team")
    historical_h2h: str = Field(description="Season series tied 3-3, but recent games favor hot team")
    
    # Strategic considerations
    playoff_implications: str = Field(description="Neither team in playoff contention - playing for pride only")
    motivation_levels: str = Field(description="Rockies may have higher motivation due to recent success")
    coaching_decisions: str = Field(description="Both teams likely to rest key players as season winds down")
    
    # Market inefficiency indicators
    public_betting: str = Field(description="Public likely betting Pirates due to better season record")
    sharp_money: str = Field(description="Professional bettors may target recent form divergence")
    line_movement: str = Field(description="Monitor for any line movement toward Rockies")
    value_proposition: str = Field(description="Potential value on Rockies if experts see recent form as sustainable")

def load_api_key():
    """Load API key from .env.local"""
    env_file = Path(__file__).parent.parent.parent / '.env.local'
    try:
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('CHRONULUS_API_KEY='):
                    key = line.split('=', 1)[1].strip().strip('"\'')
                    print(f"API Key loaded: ...{key[-4:]}")
                    return key
    except Exception as e:
        print(f"ERROR loading API key: {e}")
    return None

def create_comprehensive_session(api_key):
    """Create detailed Chronulus session for maximum expert insight"""
    session = Session(
        name="Comprehensive MLB Expert Analysis - 2 Experts",
        
        situation="""You're a seasoned sports bettor with 15+ years of experience 
        analyzing MLB games for profit. You've made your living finding edges in the 
        market and you talk like it - direct, confident, and cutting through the BS.
        
        You're looking at a classic situation where the books might be getting it wrong. 
        The Rockies are garbage this year (37-91) but they're absolutely scorching hot 
        right now (7-3 L10), while the Pirates have been decent all season (54-74) but 
        can't buy a win lately (3-7 L10).
        
        This screams potential value bet if the recent form is real and the market 
        is still stuck on season-long stats. You've seen this movie before.""",
        
        task="""Break down whether there's real money to be made on Rockies +160 
        in this spot. Talk like you're explaining it to another sharp bettor.
        
        Hit these points but keep it conversational:
        - Is this Rockies hot streak legit or are they due for a crash?
        - Are the Pirates' recent struggles real or just bad luck?
        - How much does PNC Park actually matter here?
        - Is the market asleep on this recent form flip?
        - What's your honest read on Rockies +160 - is there juice or not?
        - Where's your confidence level and what keeps you up at night about this bet?
        - What would make you flip your opinion completely?
        
        Don't write like a textbook. Write like you're breaking down tape with someone 
        who knows baseball and betting. Use your gut along with the numbers.""",
        
        env=dict(CHRONULUS_API_KEY=api_key)
    )
    
    return session

def create_comprehensive_game_data():
    """Create detailed game data with all available information"""
    return ComprehensiveSportsData(
        home_team="Pittsburgh Pirates",
        away_team="Colorado Rockies",
        sport="Major League Baseball",
        game_date="August 22, 2025",
        game_time="5:40 PM ET",
        venue="PNC Park",
        home_record="54-74",
        away_record="37-91",
        home_win_pct=0.422,
        away_win_pct=0.289,
        home_run_differential=-87,
        away_run_differential=-339,
        home_runs_allowed_pg=4.19,
        away_runs_allowed_pg=6.42,
        home_runs_scored_pg=4.54,
        away_runs_scored_pg=3.62,
        home_recent_form="3-7 in last 10 games",
        away_recent_form="7-3 in last 10 games", 
        home_last_5="1-4 in last 5 games",
        away_last_5="4-1 in last 5 games",
        form_divergence="Recent form opposite of season trends",
        home_field_advantage="PNC Park moderate advantage",
        weather_conditions="Clear, 78°F, no wind",
        home_moneyline=-190,
        away_moneyline=160,
        run_line_home="Pirates -1.5 (+104)",
        run_line_away="Rockies +1.5 (-125)",
        total_runs="Over/Under 8.5 runs",
        momentum_factor="Rockies hot vs Pirates cold",
        pitching_matchup="Based on team ERA trends",
        injury_report="No major injuries",
        historical_h2h="Season series 3-3",
        playoff_implications="Neither in contention",
        motivation_levels="Rockies higher due to success",
        coaching_decisions="May rest key players",
        public_betting="Public likely on Pirates",
        sharp_money="Sharps may target form divergence",
        line_movement="Monitor for Rockies movement",
        value_proposition="Potential Rockies value"
    )

def run_comprehensive_prediction(session, game_data):
    """Run 2-expert prediction with maximum detail length"""
    print(f"\nRUNNING COMPREHENSIVE 2-EXPERT ANALYSIS")
    print(f"="*60)
    print(f"Requesting MAXIMUM detail from experts (10-15 sentence explanations)")
    print(f"This will provide institutional-quality analysis depth")
    
    try:
        predictor = BinaryPredictor(session=session, input_type=ComprehensiveSportsData)
        predictor.create()
        
        print(f"\nQueuing prediction with 2 experts...")
        print(f"Note length: 10-15 sentences (maximum allowed detail)")
        
        # Request maximum detail explanations
        request = predictor.queue(
            item=game_data, 
            num_experts=2,
            note_length=(10, 15)  # Maximum detailed explanations
        )
        print(f"Request ID: {request.request_id}")
        
        print(f"\nWaiting for expert analysis...")
        print(f"Experts are conducting deep-dive analysis of all factors...")
        
        predictions = predictor.get_request_predictions(
            request_id=request.request_id, 
            try_every=15, 
            max_tries=20  # Extended timeout for detailed analysis
        )
        
        if predictions:
            print(f"SUCCESS: Comprehensive analysis completed!")
            return predictions, request.request_id
        else:
            print("ERROR: Analysis timed out")
            return None, request.request_id
            
    except Exception as e:
        print(f"ERROR: {e}")
        return None, None

def save_comprehensive_results(predictions, game_data, request_id, output_dir):
    """Save detailed results to both MD and JSON formats"""
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Prepare data structures
    results_data = {
        "analysis_metadata": {
            "timestamp": timestamp,
            "request_id": request_id,
            "game": f"{game_data.away_team} @ {game_data.home_team}",
            "date": game_data.game_date,
            "experts_count": 2,
            "detail_level": "Maximum (10-15 sentences per expert)"
        },
        "game_details": game_data.dict(),
        "expert_analyses": [],
        "consensus_analysis": {},
        "betting_recommendation": {}
    }
    
    expert_probs = []
    
    if predictions and hasattr(predictions, 'predictions'):
        for i, pred in enumerate(predictions.predictions):
            expert_analysis = {
                "expert_id": i + 1,
                "probability": None,
                "confidence": None,
                "detailed_reasoning": None
            }
            
            # Extract probability
            if hasattr(pred, 'prob') and isinstance(pred.prob, tuple):
                probability = pred.prob[0]
                expert_probs.append(probability)
                expert_analysis["probability"] = probability
                expert_analysis["win_percentage"] = f"{probability:.1%}"
            
            # Extract detailed reasoning
            if hasattr(pred, 'text'):
                expert_analysis["detailed_reasoning"] = pred.text
            
            results_data["expert_analyses"].append(expert_analysis)
    
    # Calculate consensus if we have probabilities
    if expert_probs:
        avg_prob = sum(expert_probs) / len(expert_probs)
        min_prob = min(expert_probs)
        max_prob = max(expert_probs)
        range_prob = max_prob - min_prob
        
        # Market analysis
        market_implied = 100 / (game_data.away_moneyline + 100)
        edge = avg_prob - market_implied
        decimal_odds = (game_data.away_moneyline / 100) + 1
        expected_value = (avg_prob * decimal_odds) - 1
        
        results_data["consensus_analysis"] = {
            "average_probability": avg_prob,
            "probability_range": {
                "minimum": min_prob,
                "maximum": max_prob,
                "spread": range_prob
            },
            "expert_agreement": "HIGH" if range_prob < 0.05 else "MODERATE",
            "market_comparison": {
                "chronulus_probability": avg_prob,
                "market_implied_probability": market_implied,
                "edge": edge,
                "expected_value": expected_value
            }
        }
        
        # Betting recommendation
        if edge > 0.05:
            recommendation = "STRONG BET"
        elif edge > 0.02:
            recommendation = "MODERATE BET"
        elif edge > 0:
            recommendation = "SLIGHT BET"
        else:
            recommendation = "NO BET"
            
        results_data["betting_recommendation"] = {
            "action": recommendation,
            "edge_percentage": f"{edge:+.1%}",
            "expected_value_percentage": f"{expected_value:+.1%}",
            "reasoning": "Based on consensus probability vs market odds"
        }
    
    # Save JSON file
    json_file = output_dir / f"comprehensive_analysis_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(results_data, f, indent=2, default=str)
    
    # Create detailed Markdown report
    md_file = output_dir / f"comprehensive_analysis_{timestamp}.md"
    
    md_content = f"""# Comprehensive MLB Analysis: {game_data.away_team} @ {game_data.home_team}

**Generated**: {timestamp}  
**Request ID**: {request_id}  
**Analysis Level**: Maximum Detail (2 Experts, 10-15 sentences each)

---

## Executive Summary

**Game**: {game_data.away_team} @ {game_data.home_team}  
**Date**: {game_data.game_date} at {game_data.game_time}  
**Venue**: {game_data.venue}  
**Key Factor**: Recent form divergence (7-3 vs 3-7 last 10 games)

"""

    if expert_probs:
        consensus = results_data["consensus_analysis"]
        recommendation = results_data["betting_recommendation"]
        
        md_content += f"""
**Chronulus Consensus**: {consensus['average_probability']:.1%} Rockies win probability  
**Market Implied**: {consensus['market_comparison']['market_implied_probability']:.1%} at +{game_data.away_moneyline} odds  
**Edge**: {consensus['market_comparison']['edge']:+.1%}  
**Expected Value**: {consensus['market_comparison']['expected_value']:+.1%}  
**Recommendation**: **{recommendation['action']}**

---

## Season Context

### Pittsburgh Pirates (Home)
- **Record**: {game_data.home_record} ({game_data.home_win_pct:.1%})
- **Run Differential**: {game_data.home_run_differential}
- **Runs Scored/Game**: {game_data.home_runs_scored_pg}
- **Runs Allowed/Game**: {game_data.home_runs_allowed_pg}
- **Recent Form**: {game_data.home_recent_form}
- **Last 5 Games**: {game_data.home_last_5}

### Colorado Rockies (Away)
- **Record**: {game_data.away_record} ({game_data.away_win_pct:.1%})
- **Run Differential**: {game_data.away_run_differential}
- **Runs Scored/Game**: {game_data.away_runs_scored_pg}
- **Runs Allowed/Game**: {game_data.away_runs_allowed_pg}
- **Recent Form**: {game_data.away_recent_form}
- **Last 5 Games**: {game_data.away_last_5}

---

## Expert Panel Analysis

"""
        
        for i, analysis in enumerate(results_data["expert_analyses"]):
            md_content += f"""
### Expert {analysis['expert_id']} Analysis

**Rockies Win Probability**: {analysis['win_percentage']}

**Detailed Expert Reasoning**:

{analysis['detailed_reasoning']}

---
"""

        md_content += f"""
## Consensus Analysis

### Probability Assessment
- **Average Probability**: {consensus['average_probability']:.4f} ({consensus['average_probability']:.1%})
- **Expert Range**: {consensus['probability_range']['minimum']:.1%} - {consensus['probability_range']['maximum']:.1%}
- **Probability Spread**: {consensus['probability_range']['spread']:.1%}
- **Expert Agreement**: {consensus['expert_agreement']}

### Market Value Analysis
- **Current Rockies Odds**: +{game_data.away_moneyline}
- **Market Implied Probability**: {consensus['market_comparison']['market_implied_probability']:.1%}
- **Chronulus Consensus**: {consensus['market_comparison']['chronulus_probability']:.1%}
- **Edge**: {consensus['market_comparison']['edge']:+.1%}
- **Expected Value**: {consensus['market_comparison']['expected_value']:+.1%}

### Betting Recommendation
- **Action**: {recommendation['action']}
- **Edge**: {recommendation['edge_percentage']}
- **Expected Value**: {recommendation['expected_value_percentage']}
- **Reasoning**: {recommendation['reasoning']}

---

## Key Insights

### Form vs Fundamentals
The central tension in this game is between season-long performance metrics heavily favoring the Pirates and recent form strongly favoring the Rockies. The experts analyzed:

- **Season Records**: Pirates 54-74 vs Rockies 37-91 (clear Pirates advantage)
- **Run Differentials**: Pirates -87 vs Rockies -339 (massive Pirates advantage)
- **Recent Form**: Rockies 7-3 vs Pirates 3-7 last 10 games (strong Rockies momentum)
- **Very Recent**: Rockies 4-1 vs Pirates 1-4 last 5 games (extreme divergence)

### Market Efficiency
The betting line of Pirates -190 / Rockies +160 implies the market is primarily weighting:
1. Season-long performance differentials
2. Home field advantage
3. Historical team strength

The question is whether recent momentum creates value in the underdog Rockies.

### Risk Factors
- **Rockies**: Poor season fundamentals, terrible road record, regression risk
- **Pirates**: Recent slump may continue, motivation questions, home advantage limited
- **General**: Late season baseball variance, potential rest days for key players

---

## Data Sources and Methodology

This analysis utilized comprehensive MLB data including:
- Season records and win percentages
- Advanced metrics (run differentials, per-game averages)
- Recent form analysis (10-game and 5-game samples)
- Betting market data and implied probabilities
- Contextual factors (venue, weather, motivation)

The Chronulus expert panel provided independent assessments with 10-15 sentence detailed explanations, creating institutional-quality analysis depth.

---

## Technical Details

**Analysis Parameters**:
- Experts: 2 independent AI analysts
- Detail Level: Maximum (10-15 sentences per expert)
- Consensus Method: Simple average of expert probabilities
- Market Analysis: Edge calculation using American odds conversion
- Expected Value: (Probability × Decimal Odds) - 1

**File Outputs**:
- Comprehensive Markdown Report: `{md_file.name}`
- Structured JSON Data: `{json_file.name}`
- Analysis Timestamp: {timestamp}
- Request ID: {request_id}

---

*Generated by Chronulus AI Expert Panel Analysis*
"""
    
    else:
        md_content += "\n**ERROR**: No expert predictions received\n"
    
    # Save Markdown file
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return md_file, json_file

def main():
    """Run comprehensive 2-expert analysis with maximum detail"""
    print("COMPREHENSIVE 2-EXPERT MLB ANALYSIS")
    print("Maximum detail explanations (10-15 sentences per expert)")
    print("Results saved to both MD and JSON formats")
    print("="*70)
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("ERROR: Cannot proceed without API key")
        return
    
    # Create comprehensive session and data
    session = create_comprehensive_session(api_key)
    game_data = create_comprehensive_game_data()
    
    # Display key information
    print(f"\nGAME ANALYSIS: {game_data.away_team} @ {game_data.home_team}")
    print(f"CRITICAL FACTOR: {game_data.form_divergence}")
    print(f"RECENT FORM: Rockies {game_data.away_recent_form} vs Pirates {game_data.home_recent_form}")
    print(f"SEASON RECORDS: Rockies {game_data.away_record} vs Pirates {game_data.home_record}")
    print(f"BETTING LINE: Rockies +{game_data.away_moneyline} vs Pirates {game_data.home_moneyline}")
    
    # Confirm before running
    proceed = input(f"\nProceed with comprehensive 2-expert analysis? (y/N): ").strip().lower()
    if proceed != 'y':
        print("Analysis cancelled.")
        return
    
    # Run prediction
    predictions, request_id = run_comprehensive_prediction(session, game_data)
    
    if not predictions:
        print("Analysis failed. No results to save.")
        return
    
    # Save comprehensive results
    output_dir = Path(__file__).parent / "results"
    md_file, json_file = save_comprehensive_results(predictions, game_data, request_id, output_dir)
    
    print(f"\n" + "="*70)
    print(f"COMPREHENSIVE ANALYSIS COMPLETE")
    print(f"="*70)
    print(f"Markdown Report: {md_file}")
    print(f"JSON Data: {json_file}")
    print(f"Request ID: {request_id}")
    print(f"\nBoth files contain maximum detail expert analysis!")

if __name__ == "__main__":
    main()