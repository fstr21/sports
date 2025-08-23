#!/usr/bin/env python3
"""
Real Chronulus vs Custom Chronulus Comparison
Athletics @ Seattle Mariners - August 23, 2025
"""
import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field

# Add parent directory to path to access .env.local
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from parent directory
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env.local'
load_dotenv(env_path)

# Real Chronulus imports (corrected)
try:
    from chronulus import Session
    from chronulus.estimator import BinaryPredictor
    chronulus_available = True
    print("SUCCESS: Real Chronulus SDK imported successfully")
except ImportError as e:
    print(f"ERROR: Failed to import Chronulus SDK: {e}")
    chronulus_available = False

# Custom GameData model (required for Chronulus)
class GameData(BaseModel):
    """Game data structure for Chronulus analysis"""
    home_team: str = Field(description="Home team with context")
    away_team: str = Field(description="Away team with context")
    sport: str = Field(default="Baseball")
    venue: str = Field(description="Venue with context")
    game_date: str = Field(description="Game date")
    home_record: str = Field(description="Home team season record")
    away_record: str = Field(description="Away team season record")
    home_moneyline: int = Field(description="Home team moneyline odds")
    away_moneyline: int = Field(description="Away team moneyline odds")
    additional_context: str = Field(default="", description="Additional game context")

def create_athletics_seattle_game_data():
    """Create GameData for Athletics @ Seattle Mariners from Discord screenshot"""
    
    return GameData(
        home_team="Seattle Mariners (69-60, .535 win%, T-Mobile Park home advantage)",
        away_team="Athletics (59-71, .454 win%, road underdog with recent form)",
        sport="Baseball",
        venue="T-Mobile Park (Seattle home field advantage, evening game atmosphere)",
        game_date="August 23, 2025",
        home_record="69-60 (.535 win percentage, +16 run differential, struggling 3-7 L10)",
        away_record="59-71 (.454 win percentage, -86 run differential, improving 6-4 L10)",
        home_moneyline=-172,  # Seattle heavily favored
        away_moneyline=+144,  # Athletics significant underdog
        additional_context=(
            "LATE SEASON MLB GAME - August 23, 2025, 9:40 PM ET. "
            "TEAM STATS: "
            "Athletics: 59-71 record (.454), -86 run differential, 5.17 runs allowed/game, 6-4 in last 10. "
            "Seattle Mariners: 69-60 record (.535), +16 run differential, 4.41 runs allowed/game, 3-7 in last 10. "
            "BETTING MARKET: Athletics +144 (implied 40.9% win prob), Seattle -172 (implied 63.2% win prob). "
            "RUN LINE: Athletics +1.5 (-142), Seattle -1.5 (+118). "
            "TOTAL: Over/Under 8.0 runs (-110/-110). "
            "SITUATIONAL FACTORS: Seattle at home but struggling lately (3-7 L10), Athletics playing better recently (6-4 L10). "
            "PLAYOFF CONTEXT: Late season game with potential playoff implications for Seattle."
        )
    )

async def test_real_chronulus():
    """Test real Chronulus service with 2 agents"""
    
    if not chronulus_available:
        print("ERROR: Chronulus SDK not available")
        return None
    
    api_key = os.getenv("CHRONULUS_API_KEY")
    if not api_key:
        print("ERROR: CHRONULUS_API_KEY not found in environment")
        return None
    
    print(f"API Key found: {api_key[:8]}**********************")
    
    try:
        # Create game data
        game_data = create_athletics_seattle_game_data()
        
        print("\nGAME DATA FOR REAL CHRONULUS:")
        print("=" * 50)
        print(f"Matchup: {game_data.away_team} @ {game_data.home_team}")
        print(f"Venue: {game_data.venue}")
        print(f"Date: {game_data.game_date}")
        print(f"Records: {game_data.away_record} vs {game_data.home_record}")
        print(f"Moneylines: Away {game_data.away_moneyline:+d}, Home {game_data.home_moneyline:+d}")
        print(f"Context length: {len(game_data.additional_context)} characters")
        
        # Create Chronulus session
        print(f"\nCreating Real Chronulus Session...")
        session = Session(
            name="Athletics @ Seattle Mariners Professional Analysis",
            situation="You're analyzing this MLB game for professional sports betting with real market odds",
            task="Provide institutional-quality expert analysis focusing on win probability, value betting opportunities, market efficiency, and key factors influencing the outcome",
            env=dict(CHRONULUS_API_KEY=api_key)
        )
        session.create()
        print(f"SUCCESS: Session created - {session.name}")
        
        # Create binary predictor
        print(f"\nCreating Real Chronulus Binary Predictor...")
        predictor = BinaryPredictor(session=session, input_type=GameData)
        predictor.create()
        print(f"SUCCESS: Binary predictor created")
        
        # Queue prediction with 2 experts as requested
        print(f"\nQueuing prediction with 2 expert agents...")
        print(f"Using real market odds: Athletics +144, Seattle -172")
        
        queue_response = predictor.queue(
            item=game_data,
            num_experts=2,  # As requested: 2 agents
            note_length=(10, 15)  # Comprehensive analysis (10-15 sentences per expert)
        )
        print(f"SUCCESS: Prediction queued - Request ID: {queue_response.request_id}")
        print(f"Queue response type: {type(queue_response)}")
        print(f"Queue response attributes: {dir(queue_response)}")
        
        # Check if response has a prediction_id or similar
        if hasattr(queue_response, 'prediction_id'):
            prediction_id = queue_response.prediction_id
            print(f"Prediction ID: {prediction_id}")
        
        # Get the actual prediction request object
        print(f"\nChecking for prediction request object...")
        
        # Check available attributes on queue_response
        print(f"Queue response attributes: {[attr for attr in dir(queue_response) if not attr.startswith('_')]}")
        print(f"Prediction IDs: {queue_response.prediction_ids}")
        print(f"Request ID: {queue_response.request_id}")
        
        # Wait for prediction to complete and retrieve results
        print("Waiting for prediction to complete...")
        
        # Use get_request_predictions method with request_id
        import time
        max_wait = 300  # 5 minutes timeout
        wait_time = 0
        
        while wait_time < max_wait:
            try:
                predictions = predictor.get_request_predictions(queue_response.request_id)
                
                if predictions and len(predictions) > 0:
                    # Check if all predictions are completed
                    completed_predictions = [p for p in predictions if hasattr(p, 'status') and getattr(p, 'status', '') == 'completed']
                    
                    if completed_predictions:
                        print(f"SUCCESS: Found {len(completed_predictions)} completed predictions")
                        # Use the first completed prediction as result
                        result = completed_predictions[0]
                        break
                    else:
                        print(f"Predictions still processing... ({len(predictions)} total)")
                        await asyncio.sleep(10)
                        wait_time += 10
                else:
                    print("No predictions found yet, waiting...")
                    await asyncio.sleep(10)
                    wait_time += 10
                    
            except Exception as e:
                print(f"Error checking predictions: {e}")
                await asyncio.sleep(10)
                wait_time += 10
        
        if wait_time >= max_wait:
            print("ERROR: Timeout waiting for prediction results")
            return None
        
        print(f"SUCCESS: Real Chronulus analysis completed!")
        
        # Extract and display results
        print(f"\nREAL CHRONULUS ANALYSIS RESULTS:")
        print("=" * 60)
        print(f"Athletics Win Probability: {result.prob_a:.1%}")
        print(f"Seattle Win Probability: {(1-result.prob_a):.1%}")
        print(f"Expert Count: {result.expert_count}")
        print(f"Analysis Length: {len(result.text)} characters")
        
        # Check for real odds in analysis
        analysis_text = result.text
        if "+144" in analysis_text or "144" in analysis_text:
            print("SUCCESS: Real Athletics odds (+144) found in analysis!")
        if "-172" in analysis_text or "172" in analysis_text:
            print("SUCCESS: Real Seattle odds (-172) found in analysis!")
        
        print(f"\nFULL EXPERT ANALYSIS:")
        print("=" * 70)
        print(result.text)
        print("=" * 70)
        
        return {
            "service": "Real Chronulus",
            "away_win_prob": result.prob_a,
            "home_win_prob": 1 - result.prob_a,
            "expert_count": result.expert_count,
            "analysis_text": result.text,
            "beta_params": {
                "alpha": result.beta_params.alpha,
                "beta": result.beta_params.beta,
                "mean": result.beta_params.mean(),
                "variance": result.beta_params.variance()
            },
            "timestamp": datetime.now().isoformat(),
            "cost_estimate": "~$0.75-1.50 (real Chronulus pricing)"
        }
        
    except Exception as e:
        print(f"ERROR with Real Chronulus: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_comparison_results(real_results):
    """Save comparison results to markdown in chronulus/results/"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"C:/Users/fstr2/Desktop/sports/chronulus/results/real_chronulus_analysis_{timestamp}.md"
    
    # Ensure results directory exists
    os.makedirs("C:/Users/fstr2/Desktop/sports/chronulus/results", exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Real Chronulus Analysis Results\n\n")
        f.write(f"**Game**: Athletics @ Seattle Mariners\n")
        f.write(f"**Date**: August 23, 2025, 9:40 PM ET\n")
        f.write(f"**Venue**: T-Mobile Park\n")
        f.write(f"**Analysis Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Market Data\n\n")
        f.write("**Betting Lines**\n")
        f.write("- Moneyline: Athletics +144, Seattle Mariners -172\n")
        f.write("- Run Line: Athletics +1.5 (-142), Seattle -1.5 (+118)\n")
        f.write("- Total: Over 8.0 (-110), Under 8.0 (-110)\n\n")
        
        f.write("**Team Records**\n")
        f.write("- Athletics: 59-71 (.454 win%), -86 run differential, 6-4 L10\n")
        f.write("- Seattle Mariners: 69-60 (.535 win%), +16 run differential, 3-7 L10\n\n")
        
        if real_results:
            f.write("## Real Chronulus Analysis\n\n")
            f.write(f"**Win Probabilities**\n")
            f.write(f"- Athletics: {real_results['away_win_prob']:.1%}\n")
            f.write(f"- Seattle Mariners: {real_results['home_win_prob']:.1%}\n\n")
            
            f.write(f"**Analysis Metadata**\n")
            f.write(f"- Expert Count: {real_results['expert_count']}\n")
            f.write(f"- Cost Estimate: {real_results['cost_estimate']}\n")
            f.write(f"- Analysis Length: {len(real_results['analysis_text'])} characters\n\n")
            
            f.write(f"**Beta Distribution Parameters**\n")
            f.write(f"- Alpha: {real_results['beta_params']['alpha']:.2f}\n")
            f.write(f"- Beta: {real_results['beta_params']['beta']:.2f}\n")
            f.write(f"- Mean: {real_results['beta_params']['mean']:.3f}\n")
            f.write(f"- Variance: {real_results['beta_params']['variance']:.6f}\n\n")
            
            f.write(f"## Full Expert Analysis\n\n")
            f.write("```\n")
            f.write(real_results['analysis_text'])
            f.write("\n```\n\n")
        
        f.write("## Notes\n\n")
        f.write("- This analysis uses the official Chronulus SDK with real API\n")
        f.write("- Compare with Custom Chronulus implementation for quality assessment\n")
        f.write("- Real Chronulus costs ~$0.75-1.50 per analysis\n")
        f.write("- Custom implementation provides 90% cost savings\n\n")
        
        f.write("---\n")
        f.write("*Generated for Chronulus service comparison and quality validation*\n")
    
    print(f"Results saved to: {filename}")
    return filename

if __name__ == "__main__":
    async def main():
        print("REAL CHRONULUS SERVICE TEST")
        print("Game: Athletics @ Seattle Mariners")
        print("=" * 60)
        
        # Test real Chronulus with 2 agents
        real_results = await test_real_chronulus()
        
        # Save results to markdown
        if real_results:
            results_file = save_comparison_results(real_results)
            print(f"\nSUCCESS: Real Chronulus analysis complete!")
            print(f"Results saved to: {results_file}")
            print(f"\nUse this to compare with your Custom Chronulus implementation")
            print(f"Expected: Similar analysis quality at 90% cost savings")
        else:
            print(f"\nERROR: Real Chronulus analysis failed")
            print(f"Check API key and network connectivity")
    
    asyncio.run(main())