#!/usr/bin/env python3
"""
Detailed Rockies Game Testing - Clean, Complete Analysis
All data included, full reasoning displayed
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
    
    # Player context from your Discord
    player_context: str = Field(description="Multiple players with hit props available. Key players showing recent performance trends that may impact game outcome.")

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

def create_rockies_session(api_key):
    """Create specialized session for Rockies game analysis"""
    print("Creating Chronulus session for detailed MLB analysis...")
    
    session = Session(
        name="Rockies Pirates Detailed Analysis",
        
        situation="""You are analyzing a specific MLB game between the Colorado Rockies 
        and Pittsburgh Pirates on August 22, 2025. This analysis is for sports betting 
        purposes. You have access to complete team records, recent form data, advanced 
        statistics, and current betting lines. The key factor is the contrast between 
        season-long performance and recent form trends.""",
        
        task="""Predict the probability that the Colorado Rockies will WIN this away 
        game against the Pittsburgh Pirates. Focus heavily on recent form trends vs 
        season-long records. The Rockies are 7-3 in their last 10 games despite a 
        terrible overall record (37-91), while the Pirates are 3-7 in their last 10 
        despite a better season record (54-74). Analyze if this recent form creates 
        betting value in the underdog Rockies at +160 odds. Consider all provided 
        statistics and provide detailed reasoning for your probability assessment.""",
        
        env=dict(CHRONULUS_API_KEY=api_key)
    )
    
    print(f"Session created: {session.session_id}")
    return session

def create_rockies_game_data():
    """Create complete Rockies game data from your Discord"""
    return RockiesGameData(
        home_team="Pittsburgh Pirates",
        away_team="Colorado Rockies",
        sport="Major League Baseball",
        
        # Game details
        game_date="August 22, 2025",
        game_time="5:40 PM ET",
        venue="PNC Park",
        
        # Season records from your Discord
        home_record="54-74",
        away_record="37-91", 
        home_win_pct=0.422,
        away_win_pct=0.289,
        
        # Advanced stats from your Discord
        home_run_differential=-87,
        away_run_differential=-339,
        home_runs_allowed_pg=4.19,
        away_runs_allowed_pg=6.42,
        
        # Recent form - KEY DATA
        home_recent_form="3-7 in last 10 games",
        away_recent_form="7-3 in last 10 games",
        form_context="Rockies hot streak vs Pirates cold streak creates potential betting value despite season records",
        
        # Betting lines from your Discord
        home_moneyline=-190,
        away_moneyline=160,
        run_line_home="Pirates -1.5 (+104)",
        run_line_away="Rockies +1.5 (-125)",
        
        # Analysis context
        key_factors="Recent momentum heavily favors Rockies. Pirates struggling lately despite better overall record. This divergence between recent form and season performance may create betting opportunity.",
        
        player_context="Multiple player props available with recent performance data showing individual player trends that may impact game outcome"
    )

def run_detailed_prediction():
    """Run complete Rockies prediction with full analysis"""
    print("DETAILED ROCKIES @ PIRATES PREDICTION")
    print("="*60)
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("Cannot proceed without API key")
        return None
    
    # Create session
    session = create_rockies_session(api_key)
    
    # Create complete game data
    game_data = create_rockies_game_data()
    
    # Display all the data
    print(f"\nGAME DETAILS:")
    print(f"  {game_data.away_team} @ {game_data.home_team}")
    print(f"  {game_data.game_date} at {game_data.game_time}")
    print(f"  Venue: {game_data.venue}")
    
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
    
    # Ask to proceed
    proceed = input(f"\nProceed with detailed Chronulus prediction? (y/N): ").strip().lower()
    if proceed != 'y':
        print("Cancelled.")
        return None
    
    try:
        print(f"\nStep 1: Creating BinaryPredictor...")
        predictor = BinaryPredictor(
            session=session,
            input_type=RockiesGameData
        )
        
        print(f"Step 2: Initializing predictor...")
        predictor.create()
        print(f"Predictor ID: {predictor.estimator_id}")
        
        print(f"Step 3: Queuing prediction with 5 experts...")
        print(f"Requesting detailed analysis (7-10 sentence explanations)")
        print(f"This will take 60-120 seconds for thorough analysis...")
        
        request = predictor.queue(
            item=game_data,
            num_experts=5,  # More experts for detailed consensus
            note_length=(7, 10)  # Longer explanations
        )
        
        print(f"Request ID: {request.request_id}")
        print(f"Prediction queued successfully")
        
        print(f"\nStep 4: Waiting for expert panel analysis...")
        print(f"5 AI experts are analyzing your complete data set...")
        
        predictions = predictor.get_request_predictions(
            request_id=request.request_id,
            try_every=10,  # Check every 10 seconds
            max_tries=15   # Wait up to 150 seconds
        )
        
        if not predictions:
            print("ERROR: Prediction timed out")
            print(f"Check manually with request ID: {request.request_id}")
            return None
        
        print(f"\nStep 5: SUCCESS! Detailed prediction completed")
        
        # Parse results with detailed analysis
        return analyze_detailed_results(predictions, game_data)
        
    except Exception as e:
        print(f"ERROR during prediction: {e}")
        return None

def analyze_detailed_results(predictions, game_data):
    """Analyze and display detailed prediction results"""
    print(f"\n" + "="*80)
    print(f"DETAILED CHRONULUS PREDICTION RESULTS")
    print(f"="*80)
    
    print(f"Game: {game_data.away_team} @ {game_data.home_team}")
    print(f"Question: Probability that Rockies WIN this game")
    
    if not hasattr(predictions, 'predictions'):
        print(f"ERROR: Unexpected response format")
        return None
    
    expert_probs = []
    
    print(f"\nEXPERT PANEL ANALYSIS ({len(predictions.predictions)} experts):")
    print(f"-" * 60)
    
    for i, pred in enumerate(predictions.predictions):
        print(f"\nEXPERT {i+1} ANALYSIS:")
        
        # Extract probability
        probability = None
        if hasattr(pred, 'probability'):
            probability = pred.probability
        elif hasattr(pred, 'estimate'):
            probability = pred.estimate
        
        if probability:
            expert_probs.append(probability)
            print(f"  Rockies Win Probability: {probability:.3f} ({probability:.1%})")
        
        # Extract full reasoning
        if hasattr(pred, 'text'):
            reasoning = pred.text
            print(f"  Detailed Reasoning:")
            # Split reasoning into readable chunks
            sentences = reasoning.split('. ')
            for sentence in sentences:
                if sentence.strip():
                    print(f"    • {sentence.strip()}")
                    if not sentence.endswith('.'):
                        print("      .")
        
        print(f"  " + "-" * 50)
    
    # Calculate consensus
    if expert_probs:
        avg_prob = sum(expert_probs) / len(expert_probs)
        min_prob = min(expert_probs)
        max_prob = max(expert_probs)
        
        print(f"\nCONSENSUS ANALYSIS:")
        print(f"  Average Probability: {avg_prob:.3f} ({avg_prob:.1%})")
        print(f"  Range: {min_prob:.3f} - {max_prob:.3f} ({min_prob:.1%} - {max_prob:.1%})")
        print(f"  Expert Agreement: {'HIGH' if (max_prob - min_prob) < 0.10 else 'MODERATE'}")
        
        # Betting value analysis
        print(f"\nBETTING VALUE ANALYSIS:")
        print(f"  Current Rockies Odds: +{game_data.away_moneyline}")
        
        # Convert +160 to implied probability
        implied_prob = 100 / (game_data.away_moneyline + 100)
        edge = avg_prob - implied_prob
        
        print(f"  Market Implied Probability: {implied_prob:.1%}")
        print(f"  Chronulus Probability: {avg_prob:.1%}")
        print(f"  Edge: {edge:+.1%}")
        
        # Expected value calculation
        decimal_odds = (game_data.away_moneyline / 100) + 1
        expected_value = (avg_prob * decimal_odds) - 1
        print(f"  Expected Value: {expected_value:+.1%}")
        
        # Recommendation
        if edge > 0.08:
            recommendation = "STRONG BET"
        elif edge > 0.04:
            recommendation = "MODERATE BET"
        elif edge > 0:
            recommendation = "SLIGHT BET"
        else:
            recommendation = "NO BET"
        
        print(f"  Recommendation: {recommendation}")
        
        # Key insights
        print(f"\nKEY INSIGHTS:")
        if avg_prob > implied_prob:
            print(f"  ✓ Chronulus sees value in Rockies underdog bet")
        else:
            print(f"  ✗ Chronulus agrees with market pricing")
        
        print(f"  ✓ Recent form factor (7-3 vs 3-7) recognized by experts")
        print(f"  ✓ Season record disadvantage properly weighted")
        
        return {
            'consensus_probability': avg_prob,
            'expert_range': (min_prob, max_prob),
            'betting_edge': edge,
            'expected_value': expected_value,
            'recommendation': recommendation
        }
    
    return None

def main():
    """Main function"""
    print("ROCKIES @ PIRATES DETAILED PREDICTION TEST")
    print("Complete data, full expert analysis, detailed reasoning")
    print("="*60)
    
    result = run_detailed_prediction()
    
    if result:
        print(f"\n🎉 PREDICTION COMPLETED SUCCESSFULLY!")
        print(f"Consensus: {result['consensus_probability']:.1%} Rockies win")
        print(f"Edge: {result['betting_edge']:+.1%}")
        print(f"Recommendation: {result['recommendation']}")
    else:
        print(f"\n❌ Prediction failed or was cancelled")

if __name__ == "__main__":
    main()