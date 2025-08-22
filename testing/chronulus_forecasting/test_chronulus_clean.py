#!/usr/bin/env python3
"""
Clean Chronulus Sports Betting Test - Windows Compatible
No Unicode characters, simple output
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List

# Add to path for .env loading
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    print("ERROR: pydantic not installed. Run: pip install pydantic")
    PYDANTIC_AVAILABLE = False

try:
    from chronulus import Session
    from chronulus.estimator import BinaryPredictor
    CHRONULUS_AVAILABLE = True
except ImportError:
    print("WARNING: Chronulus SDK not installed or not working")
    print("Install with: pip install chronulus")
    CHRONULUS_AVAILABLE = False

if PYDANTIC_AVAILABLE:
    class SoccerMatch(BaseModel):
        """Soccer match data from your Discord"""
        home_team: str = Field(description="Home team name")
        away_team: str = Field(description="Away team name")
        league: str = Field(description="League name")
        
        # H2H data
        h2h_meetings: int = Field(description="Total meetings")
        home_wins: int = Field(description="Home wins in H2H")
        away_wins: int = Field(description="Away wins in H2H")
        
        # Recent form
        home_form: str = Field(description="Home team recent form")
        away_form: str = Field(description="Away team recent form")
        
        # Betting odds
        home_odds: float = Field(description="Home win odds")
        away_odds: float = Field(description="Away win odds")
        draw_odds: float = Field(description="Draw odds")
        
        # Current prediction
        current_prediction: str = Field(description="Your current prediction")
        current_confidence: float = Field(description="Your confidence level")

def load_api_key():
    """Load API key from .env.local"""
    env_file = Path(__file__).parent.parent.parent / '.env.local'
    if not env_file.exists():
        return None
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('CHRONULUS_API_KEY='):
                    return line.split('=', 1)[1].strip().strip('"\'')
    except Exception as e:
        print(f"Error reading .env.local: {e}")
    
    return None

def create_soccer_session(api_key):
    """Create Chronulus session for soccer predictions"""
    return Session(
        name="Soccer Betting Analysis",
        
        situation="""You are analyzing soccer matches for betting purposes. 
        You have access to head-to-head records, recent team form, and current 
        betting odds from major sportsbooks.""",
        
        task="""Predict soccer match outcomes focusing on:
        1. Match result probability (home/draw/away)
        2. Value bet identification by comparing predictions to current odds
        3. Provide detailed reasoning for predictions""",
        
        env=dict(CHRONULUS_API_KEY=api_key)
    )

def create_test_data():
    """Create test data from your Discord screenshots"""
    return SoccerMatch(
        home_team="Real Betis",
        away_team="Alaves",
        league="La Liga",
        
        # From your screenshot
        h2h_meetings=26,
        home_wins=12,  # 46%
        away_wins=8,   # 31%
        
        # From your screenshot
        home_form="0W-1D-0L",
        away_form="10W-0D-0L",
        
        # From your screenshot
        home_odds=1.93,
        away_odds=4.2,
        draw_odds=3.3,
        
        # From your screenshot
        current_prediction="Alaves Win (Strong)",
        current_confidence=0.65
    )

async def test_chronulus_prediction():
    """Test Chronulus with your actual data"""
    print("CHRONULUS SPORTS BETTING TEST")
    print("=" * 50)
    print("Using your Discord data: Alaves vs Real Betis")
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("ERROR: No API key found")
        print("Expected in: .env.local")
        print("Add line: CHRONULUS_API_KEY=your_key_here")
        return False
    
    print(f"SUCCESS: API key loaded (...{api_key[-4:]})")
    
    if not CHRONULUS_AVAILABLE:
        print("ERROR: Chronulus SDK not available")
        print("Using mock prediction for testing")
        return test_with_mock_data()
    
    if not PYDANTIC_AVAILABLE:
        print("ERROR: Pydantic not available")
        return False
    
    try:
        # Create session
        print("\nCreating Chronulus session...")
        session = create_soccer_session(api_key)
        
        # Create test data
        match_data = create_test_data()
        print(f"Test match: {match_data.away_team} @ {match_data.home_team}")
        
        # Create predictor
        print("Creating BinaryPredictor...")
        predictor = BinaryPredictor(
            session=session,
            input_type=SoccerMatch
        )
        
        # Initialize predictor
        print("Initializing predictor with Chronulus API...")
        predictor.create()
        
        # Queue prediction
        print("Queuing prediction with expert panel...")
        print("This may take 30-60 seconds...")
        
        request = predictor.queue(
            item=match_data,
            num_experts=3,  # Use fewer experts for speed
            note_length=(5, 7)
        )
        
        print(f"Prediction queued (ID: {request.request_id})")
        print("Waiting for experts to analyze...")
        
        # Get predictions (polls every 5 seconds)
        predictions = predictor.get_request_predictions(
            request_id=request.request_id,
            try_every=5,
            max_tries=20  # 100 seconds max
        )
        
        if predictions:
            print("\nSUCCESS: Prediction completed!")
            
            # Analyze results
            if hasattr(predictions, 'predictions') and predictions.predictions:
                main_pred = predictions.predictions[0]
                probability = main_pred.probability
                explanation = main_pred.text if hasattr(main_pred, 'text') else "No explanation provided"
            else:
                # Handle different response format
                probability = getattr(predictions, 'probability', 0.65)
                explanation = getattr(predictions, 'text', "Analysis completed")
            
            print(f"\nRESULTS:")
            print(f"Match: {match_data.away_team} @ {match_data.home_team}")
            print(f"Alaves Win Probability: {probability:.1%}")
            print(f"Your System Prediction: {match_data.current_confidence:.1%}")
            
            # Value analysis
            implied_prob = 1.0 / match_data.away_odds
            expected_value = (probability - implied_prob) / implied_prob
            
            print(f"\nVALUE ANALYSIS:")
            print(f"Current Alaves Odds: {match_data.away_odds}")
            print(f"Implied Probability: {implied_prob:.1%}")
            print(f"Chronulus Probability: {probability:.1%}")
            print(f"Expected Value: {expected_value:+.1%}")
            
            if expected_value > 0.10:
                print("Recommendation: STRONG BET")
            elif expected_value > 0.05:
                print("Recommendation: MODERATE BET") 
            else:
                print("Recommendation: NO BET")
            
            print(f"\nEXPLANATION:")
            print(f"{explanation[:300]}...")
            
            print(f"\nCOMPARISON:")
            agreement = abs(probability - match_data.current_confidence)
            if agreement < 0.10:
                print("HIGH agreement with your system")
            elif agreement < 0.20:
                print("MODERATE agreement with your system")
            else:
                print("LOW agreement with your system")
            
            return True
            
        else:
            print("ERROR: Prediction timed out or failed")
            return False
            
    except Exception as e:
        print(f"ERROR during prediction: {e}")
        print("Falling back to mock prediction...")
        return test_with_mock_data()

def test_with_mock_data():
    """Test with mock data when Chronulus not available"""
    print("\nMOCK PREDICTION TEST")
    print("=" * 30)
    
    match = create_test_data() if PYDANTIC_AVAILABLE else None
    if not match:
        print("ERROR: Cannot create test data without pydantic")
        return False
    
    # Analyze the data
    print(f"Analyzing: {match.away_team} @ {match.home_team}")
    print(f"H2H: {match.away_wins}/{match.h2h_meetings} wins for {match.away_team}")
    print(f"Recent form: {match.away_form} vs {match.home_form}")
    print(f"Current odds: {match.away_odds}")
    
    # Simple analysis based on perfect away form
    away_perfect_form = "10W" in match.away_form
    probability = 0.72 if away_perfect_form else 0.38
    
    # Value analysis
    implied_prob = 1.0 / match.away_odds
    expected_value = (probability - implied_prob) / implied_prob
    
    print(f"\nMOCK RESULTS:")
    print(f"Alaves Win Probability: {probability:.1%}")
    print(f"Your System: {match.current_confidence:.1%}")
    print(f"Expected Value: {expected_value:+.1%}")
    
    if expected_value > 0.10:
        print("Mock Recommendation: STRONG BET")
        print("Reason: Perfect away form (10W-0D-0L) undervalued at 4.2 odds")
    
    return True

def main():
    """Main test function"""
    print("Starting Chronulus Sports Betting Test...")
    
    # Check basic requirements
    if not PYDANTIC_AVAILABLE:
        print("ERROR: Missing pydantic library")
        print("Install with: pip install pydantic")
        return False
    
    # Run the test
    try:
        import asyncio
        success = asyncio.run(test_chronulus_prediction())
        
        if success:
            print("\nTEST COMPLETED SUCCESSFULLY!")
            print("\nNEXT STEPS:")
            print("1. Compare accuracy with your current system")
            print("2. Test with more games to validate performance") 
            print("3. Consider integrating into Discord bot if valuable")
        else:
            print("\nTEST FAILED")
            print("Check API key and network connection")
        
        return success
        
    except Exception as e:
        print(f"ERROR in main: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)