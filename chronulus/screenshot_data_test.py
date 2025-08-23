#!/usr/bin/env python3
"""
Simple test script using hard-coded game data from screenshot
Athletics @ SEA Mariners - chrome_64sxt2O9sA.png
"""
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.local')

# Define GameData model for Chronulus
class GameData(BaseModel):
    """Pydantic model for game data input to Chronulus"""
    home_team: str
    away_team: str
    sport: str
    venue: str
    game_date: str
    home_record: str
    away_record: str
    home_moneyline: int
    away_moneyline: int
    additional_context: str

# Test data from screenshot
SCREENSHOT_GAME_DATA = {
    "away_team": "Athletics",
    "home_team": "SEA Mariners", 
    "away_moneyline": +143,
    "home_moneyline": -175,
    "run_line_away": +1.5,
    "run_line_away_odds": +122,
    "run_line_home": -1.5, 
    "run_line_home_odds": +122,
    "total_over": 8,
    "total_over_odds": -110,
    "total_under": 8,
    "total_under_odds": -111,
    "game_time": "9:40 PM",
    "key_players": {
        "athletics": "Jeffrey Springs",
        "sea_mariners": "George Kirby"
    }
}

def print_game_data():
    """Print the hard-coded game data from screenshot"""
    print("🏟️  GAME DATA FROM SCREENSHOT")
    print("=" * 50)
    print(f"Matchup: {SCREENSHOT_GAME_DATA['away_team']} @ {SCREENSHOT_GAME_DATA['home_team']}")
    print(f"Game Time: {SCREENSHOT_GAME_DATA['game_time']}")
    print()
    print("📊 BETTING LINES:")
    print(f"  Moneyline: {SCREENSHOT_GAME_DATA['away_team']} {SCREENSHOT_GAME_DATA['away_moneyline']:+d}")
    print(f"  Moneyline: {SCREENSHOT_GAME_DATA['home_team']} {SCREENSHOT_GAME_DATA['home_moneyline']:+d}")
    print()
    print(f"  Run Line: {SCREENSHOT_GAME_DATA['away_team']} {SCREENSHOT_GAME_DATA['run_line_away']:+.1f} ({SCREENSHOT_GAME_DATA['run_line_away_odds']:+d})")
    print(f"  Run Line: {SCREENSHOT_GAME_DATA['home_team']} {SCREENSHOT_GAME_DATA['run_line_home']:+.1f} ({SCREENSHOT_GAME_DATA['run_line_home_odds']:+d})")
    print()
    print(f"  Total: Over {SCREENSHOT_GAME_DATA['total_over']} ({SCREENSHOT_GAME_DATA['total_over_odds']:+d})")
    print(f"  Total: Under {SCREENSHOT_GAME_DATA['total_under']} ({SCREENSHOT_GAME_DATA['total_under_odds']:+d})")
    print()
    print("⚾ KEY PLAYERS:")
    print(f"  {SCREENSHOT_GAME_DATA['away_team']}: {SCREENSHOT_GAME_DATA['key_players']['athletics']}")
    print(f"  {SCREENSHOT_GAME_DATA['home_team']}: {SCREENSHOT_GAME_DATA['key_players']['sea_mariners']}")
    print("=" * 50)

async def test_chronulus_with_screenshot_data():
    """Test Chronulus service with exact screenshot data"""
    
    print("\n🔍 STARTING CHRONULUS TEST WITH SCREENSHOT DATA")
    print("=" * 60)
    
    # Try to import Chronulus with correct imports
    try:
        from chronulus import Session
        from chronulus.estimator import BinaryPredictor
        print("✅ Chronulus SDK imported successfully")
    except ImportError as e:
        print(f"\n❌ ERROR: Chronulus SDK not available")
        print(f"Please install with: pip install chronulus")
        print(f"Error details: {e}")
        print("\n📝 Game data that would be sent to Chronulus:")
        print_game_data()
        print("\n💡 TIP: See chronulus/install.md for setup instructions")
        return None
    
    # Check API key
    api_key = os.getenv("CHRONULUS_API_KEY")
    if not api_key:
        print("\n❌ ERROR: CHRONULUS_API_KEY not found in .env.local")
        print("Please add your API key to .env.local like:")
        print("CHRONULUS_API_KEY=your_api_key_here")
        print("\n📝 Game data that would be sent to Chronulus:")
        print_game_data()
        return None
    
    print(f"\n🔑 Using API key: {api_key[:8]}...")
    print("\n📊 GAME DATA BEING ANALYZED:")
    print_game_data()
    
    try:
        # Create GameData from screenshot
        game_data = GameData(
            home_team=SCREENSHOT_GAME_DATA['home_team'],
            away_team=SCREENSHOT_GAME_DATA['away_team'],
            sport="Baseball",
            venue="Unknown Stadium",
            game_date=datetime.now().strftime("%Y-%m-%d"),
            home_record="Season record unknown",
            away_record="Season record unknown",
            home_moneyline=SCREENSHOT_GAME_DATA['home_moneyline'],
            away_moneyline=SCREENSHOT_GAME_DATA['away_moneyline'],
            additional_context=(
                f"Betting market data from screenshot: "
                f"{SCREENSHOT_GAME_DATA['away_team']} ML {SCREENSHOT_GAME_DATA['away_moneyline']:+d}, "
                f"Run Line {SCREENSHOT_GAME_DATA['run_line_away']:+.1f} ({SCREENSHOT_GAME_DATA['run_line_away_odds']:+d}), "
                f"Total Over {SCREENSHOT_GAME_DATA['total_over']} ({SCREENSHOT_GAME_DATA['total_over_odds']:+d}). "
                f"{SCREENSHOT_GAME_DATA['home_team']} ML {SCREENSHOT_GAME_DATA['home_moneyline']:+d}, "
                f"Run Line {SCREENSHOT_GAME_DATA['run_line_home']:+.1f} ({SCREENSHOT_GAME_DATA['run_line_home_odds']:+d}), "
                f"Total Under {SCREENSHOT_GAME_DATA['total_under']} ({SCREENSHOT_GAME_DATA['total_under_odds']:+d}). "
                f"Key pitchers: {SCREENSHOT_GAME_DATA['key_players']['athletics']} vs {SCREENSHOT_GAME_DATA['key_players']['sea_mariners']}. "
                f"Game time: {SCREENSHOT_GAME_DATA['game_time']}."
            )
        )
        
        # Create session
        print(f"\n🚀 CREATING CHRONULUS SESSION")
        print("-" * 50)
        session_name = f"{SCREENSHOT_GAME_DATA['away_team']} @ {SCREENSHOT_GAME_DATA['home_team']} Analysis"
        print(f"Session Name: {session_name}")
        print(f"Situation: Analyzing MLB game with real betting market data")
        print(f"Task: Provide expert win probability and betting value analysis")
        
        session = Session(
            name=session_name,
            situation="Analyzing MLB game with real betting market data from screenshot",
            task="Provide expert analysis of win probabilities and betting value"
        )
        
        # Create predictor
        print(f"🤖 Creating binary predictor...")
        predictor = BinaryPredictor(session=session, input_type=GameData)
        predictor.create()
        
        # Queue prediction with 2 experts
        print(f"🧠 Queuing prediction with 2 experts...")
        queue_response = predictor.queue(
            item=game_data,
            num_experts=2,
            note_length=(6, 10)
        )
        
        # Get results
        print(f"⏳ Waiting for analysis...")
        result = predictor.get_request_predictions(queue_response.request_id)
        
        # Display results
        print(f"\n📈 CHRONULUS ANALYSIS RESULTS")
        print("=" * 60)
        
        if result is None:
            print("❌ No results received")
            return None
            
        # Check if result has the expected structure
        if hasattr(result, 'predictions') and result.predictions:
            # Get the aggregate prediction
            prediction = result.predictions[0] if result.predictions else None
            if prediction:
                print(f"Away Win Probability ({SCREENSHOT_GAME_DATA['away_team']}): {prediction.prob_a:.1%}")
                print(f"Home Win Probability ({SCREENSHOT_GAME_DATA['home_team']}): {(1-prediction.prob_a):.1%}")
                print(f"Expert Count: {len(result.predictions)}")
                
                if hasattr(prediction, 'beta_params'):
                    print(f"Beta Parameters: α={prediction.beta_params.alpha:.2f}, β={prediction.beta_params.beta:.2f}")
                
                print(f"\n📝 EXPERT ANALYSIS:")
                print("-" * 60)
                if hasattr(prediction, 'note'):
                    print(prediction.note)
                elif hasattr(prediction, 'text'):
                    print(prediction.text)
                else:
                    print("Analysis text not available")
                print("-" * 60)
                
                prob_a = prediction.prob_a
                analysis_text = getattr(prediction, 'note', getattr(prediction, 'text', 'No analysis available'))
            else:
                print("❌ No prediction data available")
                return None
        else:
            print(f"❌ Unexpected result structure: {type(result)}")
            print(f"Available attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")
            return None
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"C:/Users/fstr2/Desktop/sports/chronulus/results/screenshot_test_{timestamp}.txt"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            f.write(f"Chronulus Analysis - Screenshot Data Test\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"=" * 60 + "\n\n")
            f.write(f"Game: {SCREENSHOT_GAME_DATA['away_team']} @ {SCREENSHOT_GAME_DATA['home_team']}\n")
            f.write(f"Time: {SCREENSHOT_GAME_DATA['game_time']}\n\n")
            f.write(f"Win Probabilities:\n")
            f.write(f"- {SCREENSHOT_GAME_DATA['away_team']}: {prediction.prob_a:.1%}\n")
            f.write(f"- {SCREENSHOT_GAME_DATA['home_team']}: {(1-prediction.prob_a):.1%}\n\n")
            f.write(f"Expert Analysis:\n{analysis_text}\n\n")
            f.write(f"Technical Details:\n")
            if hasattr(prediction, 'beta_params'):
                f.write(f"- Alpha: {prediction.beta_params.alpha:.2f}\n")
                f.write(f"- Beta: {prediction.beta_params.beta:.2f}\n")
            else:
                f.write("- Beta parameters not available\n")
        
        print(f"\n💾 RESULTS SAVED TO:")
        print(results_file)
        print("\n✅ TEST COMPLETE")
        print("=" * 60)
        
        return {
            "away_win_prob": result.prob_a,
            "home_win_prob": 1 - result.prob_a,
            "analysis": result.text,
            "expert_count": result.expert_count,
            "results_file": results_file
        }
        
    except Exception as e:
        print(f"❌ Error during Chronulus analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_chronulus_with_screenshot_data())
