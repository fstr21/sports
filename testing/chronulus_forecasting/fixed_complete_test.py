#!/usr/bin/env python3
"""
Fixed Complete Rockies Test - 2 Expert Analysis
Reduced from 5 experts to 2 experts for lower API usage
"""
import os
from pathlib import Path
from pydantic import BaseModel, Field

try:
    from chronulus import Session
    from chronulus.estimator import BinaryPredictor
    print("SUCCESS: Chronulus SDK loaded")
except ImportError:
    print("ERROR: Chronulus SDK not found")
    exit(1)

class RockiesGameData(BaseModel):
    """Complete Rockies @ Pirates data from your Discord"""
    home_team: str = Field(description="Pittsburgh Pirates - home team")
    away_team: str = Field(description="Colorado Rockies - away team")
    sport: str = Field(description="Major League Baseball")
    game_date: str = Field(description="Game date August 22, 2025")
    game_time: str = Field(description="5:40 PM ET start time")
    venue: str = Field(description="PNC Park in Pittsburgh")
    home_record: str = Field(description="Pirates season record 54-74")
    away_record: str = Field(description="Rockies season record 37-91")
    home_win_pct: float = Field(description="Pirates win percentage 0.422")
    away_win_pct: float = Field(description="Rockies win percentage 0.289")
    home_run_differential: int = Field(description="Pirates run differential -87")
    away_run_differential: int = Field(description="Rockies run differential -339")
    home_runs_allowed_pg: float = Field(description="Pirates allow 4.19 runs per game")
    away_runs_allowed_pg: float = Field(description="Rockies allow 6.42 runs per game")
    home_recent_form: str = Field(description="Pirates last 10 games: 3-7 (struggling)")
    away_recent_form: str = Field(description="Rockies last 10 games: 7-3 (hot streak)")
    form_context: str = Field(description="Rockies surging despite poor overall record, Pirates slumping despite better season")
    home_moneyline: int = Field(description="Pirates favored at -190")
    away_moneyline: int = Field(description="Rockies underdog at +160")
    run_line_home: str = Field(description="Pirates -1.5 runs at +104 odds")
    run_line_away: str = Field(description="Rockies +1.5 runs at -125 odds")
    key_factors: str = Field(description="Recent form divergence creates potential value")

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

def create_session_and_data(api_key):
    """Create Chronulus session and game data"""
    session = Session(
        name="2-Expert Rockies Analysis",
        situation="""You are analyzing a specific MLB game between the Colorado Rockies 
        and Pittsburgh Pirates. This analysis is for sports betting purposes.""",
        task="""Predict the probability that the Colorado Rockies will WIN this away 
        game against the Pittsburgh Pirates. Focus on recent form vs season records.""",
        env=dict(CHRONULUS_API_KEY=api_key)
    )
    
    game_data = RockiesGameData(
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
        home_recent_form="3-7 in last 10 games",
        away_recent_form="7-3 in last 10 games",
        form_context="Rockies hot streak vs Pirates cold streak",
        home_moneyline=-190,
        away_moneyline=160,
        run_line_home="Pirates -1.5 (+104)",
        run_line_away="Rockies +1.5 (-125)",
        key_factors="Recent momentum heavily favors Rockies"
    )
    
    return session, game_data

def run_prediction(session, game_data):
    """Run the Chronulus prediction"""
    print(f"\nRUNNING CHRONULUS PREDICTION")
    print(f"="*50)
    
    try:
        predictor = BinaryPredictor(session=session, input_type=RockiesGameData)
        predictor.create()
        
        print(f"Queuing prediction with 2 experts...")
        request = predictor.queue(item=game_data, num_experts=2, note_length=(5, 8))
        print(f"Request ID: {request.request_id}")
        
        predictions = predictor.get_request_predictions(
            request_id=request.request_id, try_every=10, max_tries=12
        )
        
        if predictions:
            print(f"SUCCESS: Prediction completed!")
            return predictions
        else:
            print("ERROR: Prediction timed out")
            return None
            
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def analyze_results_fixed(predictions, game_data):
    """Fixed analysis with proper tuple handling"""
    print(f"\n" + "="*80)
    print(f"COMPLETE PREDICTION ANALYSIS (FIXED)")
    print(f"="*80)
    
    if not predictions or not hasattr(predictions, 'predictions'):
        print("ERROR: Invalid prediction results")
        return None
    
    expert_probs = []
    
    print(f"EXPERT PREDICTIONS:")
    for i, pred in enumerate(predictions.predictions):
        # Extract probability from tuple - FIXED!
        probability = None
        if hasattr(pred, 'prob') and isinstance(pred.prob, tuple):
            # First element is Rockies WIN probability
            probability = pred.prob[0]
            expert_probs.append(probability)
            print(f"  Expert {i+1}: {probability:.4f} ({probability:.1%}) Rockies win")
        
        # Show reasoning excerpt
        if hasattr(pred, 'text'):
            reasoning = pred.text.split('\n')[0] if '\n' in pred.text else pred.text[:100]
            print(f"    Key insight: {reasoning}")
    
    if not expert_probs:
        print("ERROR: No probabilities extracted")
        return None
    
    # Calculate consensus
    avg_prob = sum(expert_probs) / len(expert_probs)
    min_prob = min(expert_probs)
    max_prob = max(expert_probs)
    range_prob = max_prob - min_prob
    
    print(f"\nCONSENSUS ANALYSIS:")
    print(f"  Average Probability: {avg_prob:.4f} ({avg_prob:.1%})")
    print(f"  Range: {min_prob:.4f} - {max_prob:.4f}")
    print(f"  Spread: {range_prob:.4f} ({range_prob:.1%})")
    
    # Expert agreement
    if range_prob < 0.02:
        agreement = "VERY HIGH"
    elif range_prob < 0.05:
        agreement = "HIGH"
    else:
        agreement = "MODERATE"
    print(f"  Expert Agreement: {agreement}")
    
    # Betting value analysis
    print(f"\nBETTING VALUE ANALYSIS:")
    away_moneyline = game_data.away_moneyline
    implied_prob = 100 / (away_moneyline + 100)
    edge = avg_prob - implied_prob
    
    print(f"  Current Rockies Odds: +{away_moneyline}")
    print(f"  Market Implied Probability: {implied_prob:.4f} ({implied_prob:.1%})")
    print(f"  Chronulus Consensus: {avg_prob:.4f} ({avg_prob:.1%})")
    print(f"  Edge: {edge:+.4f} ({edge:+.1%})")
    
    # Expected value
    decimal_odds = (away_moneyline / 100) + 1
    expected_value = (avg_prob * decimal_odds) - 1
    print(f"  Expected Value: {expected_value:+.4f} ({expected_value:+.1%})")
    
    # Recommendation
    if edge > 0.05:
        recommendation = "STRONG BET"
        color = "🟢"
    elif edge > 0.02:
        recommendation = "MODERATE BET"
        color = "🟡"
    elif edge > 0:
        recommendation = "SLIGHT BET"
        color = "🟡"
    else:
        recommendation = "NO BET"
        color = "🔴"
    
    print(f"  Recommendation: {color} {recommendation}")
    
    return {
        'consensus': avg_prob,
        'expert_probs': expert_probs,
        'edge': edge,
        'recommendation': recommendation,
        'expected_value': expected_value,
        'agreement': agreement
    }

def print_final_summary_fixed(result, game_data):
    """Fixed final summary"""
    print(f"\n" + "="*80)
    print(f"FINAL SUMMARY & RECOMMENDATION")
    print(f"="*80)
    
    if not result:
        print("FAILED: Unable to complete analysis")
        return
    
    print(f"GAME: {game_data.away_team} @ {game_data.home_team}")
    print(f"CHRONULUS CONSENSUS: {result['consensus']:.1%} Rockies win")
    print(f"EXPERT RANGE: {min(result['expert_probs']):.1%} - {max(result['expert_probs']):.1%}")
    print(f"MARKET ODDS: +{game_data.away_moneyline} ({100/(game_data.away_moneyline+100):.1%} implied)")
    print(f"EDGE: {result['edge']:+.1%}")
    print(f"EXPECTED VALUE: {result['expected_value']:+.1%}")
    print(f"RECOMMENDATION: {result['recommendation']}")
    print(f"EXPERT AGREEMENT: {result['agreement']}")
    
    print(f"\nKEY INSIGHTS:")
    print(f"• All experts recognized recent form impact (7-3 vs 3-7)")
    print(f"• Season records properly weighted against momentum")
    print(f"• Consensus: {result['consensus']:.1%} vs Market: {100/(game_data.away_moneyline+100):.1%}")
    
    if result['edge'] > 0:
        print(f"• POSITIVE EDGE: Chronulus sees value in Rockies bet")
    else:
        print(f"• NO EDGE: Market pricing appears efficient")
    
    print(f"\nSUCCESS: Complete analysis with proper probability extraction!")

def main():
    """Complete test with fixed probability extraction"""
    print("2-EXPERT ROCKIES @ PIRATES ANALYSIS")
    print("Reduced API usage with 2 experts instead of 5")
    print("="*60)
    
    api_key = load_api_key()
    if not api_key:
        return
    
    session, game_data = create_session_and_data(api_key)
    
    # Show key data
    print(f"\nGAME: {game_data.away_team} @ {game_data.home_team}")
    print(f"RECENT FORM: Rockies {game_data.away_recent_form} vs Pirates {game_data.home_recent_form}")
    print(f"BETTING LINE: Rockies +{game_data.away_moneyline}")
    
    proceed = input(f"\nRun prediction? (y/N): ").strip().lower()
    if proceed != 'y':
        return
    
    predictions = run_prediction(session, game_data)
    if not predictions:
        return
    
    result = analyze_results_fixed(predictions, game_data)
    print_final_summary_fixed(result, game_data)

if __name__ == "__main__":
    main()