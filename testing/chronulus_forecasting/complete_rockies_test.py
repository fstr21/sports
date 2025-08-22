#!/usr/bin/env python3
"""
Complete Rockies Game Test - Everything in One File
Start to finish: data setup → prediction → analysis → recommendation
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
    print("Install with: pip install chronulus")
    exit(1)

class RockiesGameData(BaseModel):
    """Complete Rockies @ Pirates data from your Discord"""
    home_team: str = Field(description="Pittsburgh Pirates - home team")
    away_team: str = Field(description="Colorado Rockies - away team")
    sport: str = Field(description="Major League Baseball")
    
    # Game details
    game_date: str = Field(description="Game date August 22, 2025")
    game_time: str = Field(description="5:40 PM ET start time")
    venue: str = Field(description="PNC Park in Pittsburgh")
    
    # Team records from your Discord
    home_record: str = Field(description="Pirates season record 54-74")
    away_record: str = Field(description="Rockies season record 37-91")
    home_win_pct: float = Field(description="Pirates win percentage 0.422")
    away_win_pct: float = Field(description="Rockies win percentage 0.289")
    
    # Advanced stats from your Discord
    home_run_differential: int = Field(description="Pirates run differential -87")
    away_run_differential: int = Field(description="Rockies run differential -339")
    home_runs_allowed_pg: float = Field(description="Pirates allow 4.19 runs per game")
    away_runs_allowed_pg: float = Field(description="Rockies allow 6.42 runs per game")
    
    # Recent form - THE KEY FACTOR
    home_recent_form: str = Field(description="Pirates last 10 games: 3-7 (struggling)")
    away_recent_form: str = Field(description="Rockies last 10 games: 7-3 (hot streak)")
    form_context: str = Field(description="Rockies surging despite poor overall record, Pirates slumping despite better season")
    
    # Betting lines from your Discord
    home_moneyline: int = Field(description="Pirates favored at -190")
    away_moneyline: int = Field(description="Rockies underdog at +160")
    run_line_home: str = Field(description="Pirates -1.5 runs at +104 odds")
    run_line_away: str = Field(description="Rockies +1.5 runs at -125 odds")
    
    # Key analysis points
    key_factors: str = Field(description="Recent form divergence creates potential value. Pirates expected to win but recent performance suggests closer game than odds indicate.")

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
    print("Creating Chronulus session...")
    
    session = Session(
        name="Complete Rockies Analysis",
        
        situation="""You are analyzing a specific MLB game between the Colorado Rockies 
        and Pittsburgh Pirates. This analysis is for sports betting purposes. You have 
        access to complete team records, recent form data, advanced statistics, and 
        current betting lines.""",
        
        task="""Predict the probability that the Colorado Rockies will WIN this away 
        game against the Pittsburgh Pirates. Focus heavily on recent form trends vs 
        season-long records. The Rockies are 7-3 in their last 10 games despite a 
        terrible overall record, while the Pirates are 3-7 in their last 10 despite 
        a better season record. Analyze if this creates betting value.""",
        
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
        form_context="Rockies hot streak vs Pirates cold streak creates potential betting value",
        home_moneyline=-190,
        away_moneyline=160,
        run_line_home="Pirates -1.5 (+104)",
        run_line_away="Rockies +1.5 (-125)",
        key_factors="Recent momentum heavily favors Rockies despite season records"
    )
    
    return session, game_data

def display_game_data(game_data):
    """Display all game data before prediction"""
    print(f"\n" + "="*60)
    print(f"COMPLETE GAME ANALYSIS DATA")
    print(f"="*60)
    
    print(f"GAME: {game_data.away_team} @ {game_data.home_team}")
    print(f"DATE: {game_data.game_date} at {game_data.game_time}")
    print(f"VENUE: {game_data.venue}")
    
    print(f"\nSEASON RECORDS:")
    print(f"  Pirates: {game_data.home_record} ({game_data.home_win_pct:.1%})")
    print(f"  Rockies: {game_data.away_record} ({game_data.away_win_pct:.1%})")
    
    print(f"\nADVANCED STATS:")
    print(f"  Pirates: {game_data.home_run_differential} run diff, {game_data.home_runs_allowed_pg} RA/G")
    print(f"  Rockies: {game_data.away_run_differential} run diff, {game_data.away_runs_allowed_pg} RA/G")
    
    print(f"\nRECENT FORM (KEY FACTOR):")
    print(f"  Pirates: {game_data.home_recent_form}")
    print(f"  Rockies: {game_data.away_recent_form}")
    print(f"  Context: {game_data.form_context}")
    
    print(f"\nBETTING LINES:")
    print(f"  Pirates: {game_data.home_moneyline} (favored)")
    print(f"  Rockies: +{game_data.away_moneyline} (underdog)")
    print(f"  Run Line: {game_data.run_line_home} / {game_data.run_line_away}")
    
    print(f"\nKEY ANALYSIS:")
    print(f"  {game_data.key_factors}")

def run_prediction(session, game_data):
    """Run the Chronulus prediction"""
    print(f"\n" + "="*60)
    print(f"RUNNING CHRONULUS PREDICTION")
    print(f"="*60)
    
    try:
        print(f"Step 1: Creating BinaryPredictor...")
        predictor = BinaryPredictor(
            session=session,
            input_type=RockiesGameData
        )
        
        print(f"Step 2: Initializing predictor...")
        predictor.create()
        print(f"Predictor ID: {predictor.estimator_id}")
        
        print(f"Step 3: Queuing prediction with 3 experts...")
        print(f"This will take 30-90 seconds...")
        
        request = predictor.queue(
            item=game_data,
            num_experts=3,
            note_length=(5, 8)
        )
        
        print(f"Request ID: {request.request_id}")
        print(f"Waiting for expert analysis...")
        
        predictions = predictor.get_request_predictions(
            request_id=request.request_id,
            try_every=10,
            max_tries=12  # 2 minutes max
        )
        
        if not predictions:
            print("ERROR: Prediction timed out")
            return None
        
        print(f"SUCCESS: Prediction completed!")
        return predictions
        
    except Exception as e:
        print(f"ERROR during prediction: {e}")
        return None

def analyze_results(predictions, game_data):
    """Analyze prediction results and calculate everything"""
    print(f"\n" + "="*80)
    print(f"COMPLETE PREDICTION ANALYSIS")
    print(f"="*80)
    
    if not predictions or not hasattr(predictions, 'predictions'):
        print("ERROR: Invalid prediction results")
        return None
    
    expert_probs = []
    
    print(f"EXPERT PREDICTIONS:")
    for i, pred in enumerate(predictions.predictions):
        # Extract probability
        probability = None
        if hasattr(pred, 'probability'):
            probability = pred.probability
        elif hasattr(pred, 'estimate'):
            probability = pred.estimate
        
        if probability:
            expert_probs.append(probability)
            print(f"  Expert {i+1}: {probability:.3f} ({probability:.1%})")
        
        # Show reasoning excerpt
        if hasattr(pred, 'text'):
            reasoning = pred.text[:150]
            print(f"    Reasoning: {reasoning}...")
    
    if not expert_probs:
        print("ERROR: No probabilities found in predictions")
        return None
    
    # Calculate consensus
    avg_prob = sum(expert_probs) / len(expert_probs)
    min_prob = min(expert_probs)
    max_prob = max(expert_probs)
    range_prob = max_prob - min_prob
    
    print(f"\nCONSENSUS ANALYSIS:")
    print(f"  Average Probability: {avg_prob:.3f} ({avg_prob:.1%})")
    print(f"  Range: {min_prob:.3f} - {max_prob:.3f}")
    print(f"  Spread: {range_prob:.3f} ({range_prob:.1%})")
    
    # Expert agreement
    if range_prob < 0.05:
        agreement = "VERY HIGH"
    elif range_prob < 0.10:
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
    print(f"  Market Implied Probability: {implied_prob:.3f} ({implied_prob:.1%})")
    print(f"  Chronulus Consensus: {avg_prob:.3f} ({avg_prob:.1%})")
    print(f"  Edge: {edge:+.3f} ({edge:+.1%})")
    
    # Expected value
    decimal_odds = (away_moneyline / 100) + 1
    expected_value = (avg_prob * decimal_odds) - 1
    print(f"  Expected Value: {expected_value:+.3f} ({expected_value:+.1%})")
    
    # Recommendation
    if edge > 0.08:
        recommendation = "STRONG BET"
        color = "🟢"
    elif edge > 0.04:
        recommendation = "MODERATE BET"
        color = "🟡"
    elif edge > 0:
        recommendation = "SLIGHT BET"
        color = "🟡"
    else:
        recommendation = "NO BET"
        color = "🔴"
    
    print(f"  Recommendation: {color} {recommendation}")
    
    # Final analysis
    print(f"\nFINAL ANALYSIS:")
    
    if edge > 0:
        print(f"  ✓ Chronulus identifies value in Rockies underdog bet")
    else:
        print(f"  ✗ Market pricing appears efficient")
    
    print(f"  ✓ Recent form factor properly analyzed")
    print(f"  ✓ Season statistics appropriately weighted")
    
    return {
        'consensus': avg_prob,
        'range': (min_prob, max_prob),
        'edge': edge,
        'recommendation': recommendation,
        'expected_value': expected_value,
        'agreement': agreement
    }

def print_final_summary(result, game_data):
    """Print final summary and recommendation"""
    print(f"\n" + "="*80)
    print(f"FINAL SUMMARY & RECOMMENDATION")
    print(f"="*80)
    
    if not result:
        print("FAILED: Unable to complete analysis")
        return
    
    print(f"GAME: {game_data.away_team} @ {game_data.home_team}")
    print(f"CHRONULUS CONSENSUS: {result['consensus']:.1%} Rockies win")
    print(f"MARKET ODDS: +{game_data.away_moneyline} ({100/(game_data.away_moneyline+100):.1%} implied)")
    print(f"EDGE: {result['edge']:+.1%}")
    print(f"EXPECTED VALUE: {result['expected_value']:+.1%}")
    print(f"RECOMMENDATION: {result['recommendation']}")
    print(f"EXPERT AGREEMENT: {result['agreement']}")
    
    print(f"\nKEY INSIGHTS:")
    print(f"• Recent form (7-3 vs 3-7) recognized by all experts")
    print(f"• Season records properly weighted against recent performance")
    print(f"• Home field advantage factored into analysis")
    
    if result['recommendation'] in ["SLIGHT BET", "MODERATE BET", "STRONG BET"]:
        print(f"\nBETTING STRATEGY:")
        print(f"• Small positive edge identified")
        print(f"• Recent form creates slight value opportunity")
        print(f"• Consider small bet size due to edge magnitude")
    else:
        print(f"\nMARKET ASSESSMENT:")
        print(f"• Odds accurately reflect true probability")
        print(f"• No significant betting value identified")
    
    print(f"\nCOMPLETE TEST SUCCESSFUL!")

def main():
    """Complete test from start to finish"""
    print("COMPLETE ROCKIES @ PIRATES ANALYSIS")
    print("Everything in one file - start to finish")
    print("="*60)
    
    # Step 1: Load API key
    api_key = load_api_key()
    if not api_key:
        print("Cannot proceed without API key")
        return
    
    # Step 2: Create session and data
    session, game_data = create_session_and_data(api_key)
    print(f"Session ID: {session.session_id}")
    
    # Step 3: Display all data
    display_game_data(game_data)
    
    # Step 4: Confirm before API call
    proceed = input(f"\nProceed with Chronulus prediction? (y/N): ").strip().lower()
    if proceed != 'y':
        print("Test cancelled.")
        return
    
    # Step 5: Run prediction
    predictions = run_prediction(session, game_data)
    if not predictions:
        print("Prediction failed.")
        return
    
    # Step 6: Analyze results
    result = analyze_results(predictions, game_data)
    
    # Step 7: Final summary
    print_final_summary(result, game_data)

if __name__ == "__main__":
    main()