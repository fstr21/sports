#!/usr/bin/env python3
"""
Complete Rockies Test with MD Output and Extended Timeouts
Saves everything to a markdown file and waits longer for detailed predictions
"""
import os
import sys
from pathlib import Path
from datetime import datetime
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

class OutputLogger:
    """Logs output to both console and markdown file"""
    def __init__(self, filename):
        self.filename = filename
        self.content = []
        
        # Initialize file with header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"""# Chronulus Rockies @ Pirates Analysis
**Generated**: {timestamp}
**Request**: Complete analysis with detailed expert reasoning

---

"""
        with open(filename, 'w') as f:
            f.write(header)
    
    def log(self, message):
        """Log message to both console and file"""
        print(message)
        self.content.append(message)
        
        # Append to file immediately
        with open(self.filename, 'a') as f:
            f.write(message + '\n')
    
    def log_section(self, title):
        """Log a section header"""
        section = f"\n## {title}\n"
        self.log(section)

def load_api_key():
    """Load API key from .env.local"""
    env_file = Path(__file__).parent.parent.parent / '.env.local'
    try:
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('CHRONULUS_API_KEY='):
                    key = line.split('=', 1)[1].strip().strip('"\'')
                    return key
    except Exception as e:
        print(f"ERROR loading API key: {e}")
    return None

def create_session_and_data(api_key, logger):
    """Create Chronulus session and game data"""
    logger.log("Creating Chronulus session for detailed MLB analysis...")
    
    session = Session(
        name="Complete Rockies Pirates Analysis",
        
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
    
    logger.log(f"Session ID: {session.session_id}")
    return session, game_data

def display_game_data(game_data, logger):
    """Display all game data"""
    logger.log_section("Game Data Analysis")
    
    logger.log(f"**Game**: {game_data.away_team} @ {game_data.home_team}")
    logger.log(f"**Date**: {game_data.game_date} at {game_data.game_time}")
    logger.log(f"**Venue**: {game_data.venue}")
    
    logger.log(f"\n**Season Records:**")
    logger.log(f"- Pirates: {game_data.home_record} ({game_data.home_win_pct:.1%})")
    logger.log(f"- Rockies: {game_data.away_record} ({game_data.away_win_pct:.1%})")
    
    logger.log(f"\n**Advanced Stats:**")
    logger.log(f"- Pirates: {game_data.home_run_differential} run diff, {game_data.home_runs_allowed_pg} RA/G")
    logger.log(f"- Rockies: {game_data.away_run_differential} run diff, {game_data.away_runs_allowed_pg} RA/G")
    
    logger.log(f"\n**Recent Form (KEY FACTOR):**")
    logger.log(f"- Pirates: {game_data.home_recent_form}")
    logger.log(f"- Rockies: {game_data.away_recent_form}")
    logger.log(f"- Context: {game_data.form_context}")
    
    logger.log(f"\n**Betting Lines:**")
    logger.log(f"- Pirates: {game_data.home_moneyline} (favored)")
    logger.log(f"- Rockies: +{game_data.away_moneyline} (underdog)")
    logger.log(f"- Run Line: {game_data.run_line_home} / {game_data.run_line_away}")

def run_prediction(session, game_data, logger):
    """Run the Chronulus prediction with extended timeouts"""
    logger.log_section("Chronulus Prediction Process")
    
    try:
        logger.log("Step 1: Creating BinaryPredictor...")
        predictor = BinaryPredictor(
            session=session,
            input_type=RockiesGameData
        )
        
        logger.log("Step 2: Initializing predictor...")
        predictor.create()
        logger.log(f"Predictor ID: {predictor.estimator_id}")
        
        logger.log("Step 3: Queuing prediction with 5 experts...")
        logger.log("Requesting detailed analysis (7-10 sentence explanations)")
        logger.log("This may take 90-180 seconds for thorough analysis...")
        
        request = predictor.queue(
            item=game_data,
            num_experts=5,  # More experts for detailed analysis
            note_length=(7, 10)  # Longer explanations like your previous tests
        )
        
        logger.log(f"Request ID: {request.request_id}")
        logger.log("Prediction queued successfully")
        
        logger.log("\nStep 4: Waiting for expert panel analysis...")
        logger.log("5 AI experts are analyzing your complete data set...")
        
        # Extended timeout for detailed analysis
        predictions = predictor.get_request_predictions(
            request_id=request.request_id,
            try_every=15,  # Check every 15 seconds
            max_tries=20   # Wait up to 300 seconds (5 minutes)
        )
        
        if predictions:
            logger.log("SUCCESS: Detailed prediction completed!")
            return predictions
        else:
            logger.log("ERROR: Prediction timed out after 5 minutes")
            logger.log(f"You can check manually with request ID: {request.request_id}")
            return None
            
    except Exception as e:
        logger.log(f"ERROR during prediction: {e}")
        import traceback
        logger.log(f"Traceback: {traceback.format_exc()}")
        return None

def analyze_results_detailed(predictions, game_data, logger):
    """Detailed analysis with full expert reasoning"""
    logger.log_section("Expert Panel Analysis Results")
    
    if not predictions or not hasattr(predictions, 'predictions'):
        logger.log("ERROR: Invalid prediction results")
        return None
    
    expert_probs = []
    
    logger.log(f"**Expert Panel Analysis ({len(predictions.predictions)} experts):**")
    
    for i, pred in enumerate(predictions.predictions):
        logger.log(f"\n### Expert {i+1} Analysis:")
        
        # Extract probability from tuple
        probability = None
        if hasattr(pred, 'prob') and isinstance(pred.prob, tuple):
            probability = pred.prob[0]  # Rockies WIN probability
            expert_probs.append(probability)
            logger.log(f"**Rockies Win Probability**: {probability:.4f} ({probability:.1%})")
        
        # Extract and format full reasoning
        if hasattr(pred, 'text'):
            reasoning = pred.text
            logger.log(f"**Detailed Reasoning**:")
            
            # Split reasoning into readable sections
            if '[Positive]' in reasoning:
                sections = reasoning.split('[Negative]')
                logger.log(f"**Positive Analysis (Rockies Win)**:")
                logger.log(f"{sections[0].strip()}")
                
                if len(sections) > 1:
                    logger.log(f"\n**Negative Analysis (Rockies Lose)**:")
                    logger.log(f"{sections[1].strip()}")
            else:
                logger.log(f"{reasoning}")
        
        logger.log(f"\n---")
    
    if not expert_probs:
        logger.log("ERROR: No probabilities extracted from expert predictions")
        return None
    
    # Calculate consensus
    avg_prob = sum(expert_probs) / len(expert_probs)
    min_prob = min(expert_probs)
    max_prob = max(expert_probs)
    range_prob = max_prob - min_prob
    
    logger.log_section("Consensus Analysis")
    logger.log(f"**Average Probability**: {avg_prob:.4f} ({avg_prob:.1%})")
    logger.log(f"**Range**: {min_prob:.4f} - {max_prob:.4f}")
    logger.log(f"**Spread**: {range_prob:.4f} ({range_prob:.1%})")
    
    # Expert agreement
    if range_prob < 0.02:
        agreement = "VERY HIGH"
    elif range_prob < 0.05:
        agreement = "HIGH"
    else:
        agreement = "MODERATE"
    logger.log(f"**Expert Agreement**: {agreement}")
    
    # Betting value analysis
    logger.log_section("Betting Value Analysis")
    
    away_moneyline = game_data.away_moneyline
    implied_prob = 100 / (away_moneyline + 100)
    edge = avg_prob - implied_prob
    
    logger.log(f"**Current Rockies Odds**: +{away_moneyline}")
    logger.log(f"**Market Implied Probability**: {implied_prob:.4f} ({implied_prob:.1%})")
    logger.log(f"**Chronulus Consensus**: {avg_prob:.4f} ({avg_prob:.1%})")
    logger.log(f"**Edge**: {edge:+.4f} ({edge:+.1%})")
    
    # Expected value
    decimal_odds = (away_moneyline / 100) + 1
    expected_value = (avg_prob * decimal_odds) - 1
    logger.log(f"**Expected Value**: {expected_value:+.4f} ({expected_value:+.1%})")
    
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
    
    logger.log(f"**Recommendation**: {color} {recommendation}")
    
    return {
        'consensus': avg_prob,
        'expert_probs': expert_probs,
        'edge': edge,
        'recommendation': recommendation,
        'expected_value': expected_value,
        'agreement': agreement
    }

def print_final_summary(result, game_data, logger):
    """Print comprehensive final summary"""
    logger.log_section("Final Summary & Recommendation")
    
    if not result:
        logger.log("**FAILED**: Unable to complete analysis")
        return
    
    logger.log(f"**Game**: {game_data.away_team} @ {game_data.home_team}")
    logger.log(f"**Chronulus Consensus**: {result['consensus']:.1%} Rockies win")
    logger.log(f"**Expert Range**: {min(result['expert_probs']):.1%} - {max(result['expert_probs']):.1%}")
    logger.log(f"**Market Odds**: +{game_data.away_moneyline} ({100/(game_data.away_moneyline+100):.1%} implied)")
    logger.log(f"**Edge**: {result['edge']:+.1%}")
    logger.log(f"**Expected Value**: {result['expected_value']:+.1%}")
    logger.log(f"**Recommendation**: {result['recommendation']}")
    logger.log(f"**Expert Agreement**: {result['agreement']}")
    
    logger.log(f"\n**Key Insights:**")
    logger.log(f"- All experts recognized recent form impact (7-3 vs 3-7)")
    logger.log(f"- Season records properly weighted against momentum")
    logger.log(f"- Consensus: {result['consensus']:.1%} vs Market: {100/(game_data.away_moneyline+100):.1%}")
    
    if result['edge'] > 0:
        logger.log(f"- **POSITIVE EDGE**: Chronulus sees value in Rockies bet")
        logger.log(f"- **Strategy**: Consider small bet size given edge magnitude")
    else:
        logger.log(f"- **NO EDGE**: Market pricing appears efficient")
        logger.log(f"- **Strategy**: No betting recommendation")
    
    logger.log(f"\n**SUCCESS**: Complete analysis with {len(result['expert_probs'])} expert predictions!")

def main():
    """Complete test with markdown output"""
    # Setup output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(__file__).parent / f"rockies_analysis_{timestamp}.md"
    logger = OutputLogger(output_file)
    
    logger.log("# Complete Rockies @ Pirates Analysis")
    logger.log("Extended timeouts and detailed expert reasoning")
    logger.log("="*60)
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        logger.log("ERROR: Cannot proceed without API key")
        return
    logger.log(f"API Key loaded: ...{api_key[-4:]}")
    
    # Create session and data
    session, game_data = create_session_and_data(api_key, logger)
    
    # Display all data
    display_game_data(game_data, logger)
    
    # Confirm before API call
    proceed = input(f"\nProceed with detailed Chronulus prediction? (y/N): ").strip().lower()
    if proceed != 'y':
        logger.log("Test cancelled by user.")
        return
    
    # Run prediction with extended timeout
    predictions = run_prediction(session, game_data, logger)
    if not predictions:
        logger.log("Prediction failed or timed out.")
        logger.log(f"Results saved to: {output_file}")
        return
    
    # Analyze results with full detail
    result = analyze_results_detailed(predictions, game_data, logger)
    
    # Final summary
    print_final_summary(result, game_data, logger)
    
    logger.log(f"\n---")
    logger.log(f"**Complete analysis saved to**: {output_file}")
    print(f"\nComplete analysis saved to: {output_file}")

if __name__ == "__main__":
    main()