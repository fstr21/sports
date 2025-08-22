#!/usr/bin/env python3
"""
Manual Single Game Testing Script
You control each prediction, see exactly what happens
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

class GameData(BaseModel):
    """Simple game data structure"""
    home_team: str = Field(description="Home team name")
    away_team: str = Field(description="Away team name")
    sport: str = Field(description="Sport type")
    
    # Your Discord data
    away_recent_form: str = Field(description="Away team recent form")
    home_recent_form: str = Field(description="Home team recent form")
    away_odds: float = Field(description="Away team win odds")
    home_odds: float = Field(description="Home team win odds")
    
    # Context
    key_factors: str = Field(description="Key factors for this match")

def load_api_key():
    """Load your API key"""
    env_file = Path(__file__).parent.parent.parent / '.env.local'
    
    if not env_file.exists():
        print(f"ERROR: .env.local not found at {env_file}")
        return None
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('CHRONULUS_API_KEY='):
                    key = line.split('=', 1)[1].strip().strip('"\'')
                    print(f"SUCCESS: API key loaded (...{key[-4:]})")
                    return key
    except Exception as e:
        print(f"ERROR reading .env.local: {e}")
    
    return None

def create_session(api_key):
    """Create Chronulus session"""
    print("\nCreating Chronulus session...")
    
    session = Session(
        name="Manual Sports Betting Test",
        
        situation="""You are a sports betting expert analyzing individual games.
        You have access to recent team form, betting odds, and key situational factors.""",
        
        task="""Predict the probability that the AWAY team will WIN this specific game.
        Consider recent form, betting odds context, and any special factors.
        Focus on identifying if there's betting value in the away team.""",
        
        env=dict(CHRONULUS_API_KEY=api_key)
    )
    
    print(f"Session created: {session.session_id}")
    return session

def test_alaves_real_betis():
    """Test your exact Discord data: Alaves @ Real Betis"""
    return GameData(
        home_team="Real Betis",
        away_team="Alaves",
        sport="Soccer",
        
        # From your Discord screenshot
        away_recent_form="10W-0D-0L (Perfect record)",
        home_recent_form="0W-1D-0L (Poor form)", 
        away_odds=4.2,
        home_odds=1.93,
        
        key_factors="Alaves on 10-game winning streak vs Real Betis struggling. H2H historically favors Real Betis (46% vs 31%) but current form heavily favors Alaves."
    )

def test_rockies_pirates():
    """Test your exact Discord data: Rockies @ Pirates"""
    return GameData(
        home_team="Pittsburgh Pirates",
        away_team="Colorado Rockies", 
        sport="Baseball",
        
        # From your Discord screenshot
        away_recent_form="7-3 L10 (Hot streak)",
        home_recent_form="3-7 L10 (Struggling)",
        away_odds=160,  # +160
        home_odds=-190,
        
        key_factors="Rockies recent surge (7-3) despite poor overall record (37-91). Pirates struggling recently (3-7) despite better season record (54-74)."
    )

def run_single_prediction(game_data, session):
    """Run one prediction and show everything"""
    print(f"\n" + "="*60)
    print(f"TESTING: {game_data.away_team} @ {game_data.home_team}")
    print(f"="*60)
    
    print(f"Away Team: {game_data.away_team}")
    print(f"  Recent Form: {game_data.away_recent_form}")
    print(f"  Win Odds: {game_data.away_odds}")
    
    print(f"Home Team: {game_data.home_team}")
    print(f"  Recent Form: {game_data.home_recent_form}")
    print(f"  Win Odds: {game_data.home_odds}")
    
    print(f"Key Factors: {game_data.key_factors}")
    
    # Ask user to proceed
    proceed = input(f"\nProceed with Chronulus prediction? (y/N): ").strip().lower()
    if proceed != 'y':
        print("Skipped.")
        return None
    
    try:
        print(f"\nStep 1: Creating BinaryPredictor...")
        predictor = BinaryPredictor(
            session=session,
            input_type=GameData
        )
        
        print(f"Step 2: Initializing predictor with API...")
        predictor.create()
        print(f"Predictor ID: {predictor.estimator_id}")
        
        print(f"Step 3: Queuing prediction with expert panel...")
        print(f"Using 3 experts, detailed explanations")
        print(f"This will take 30-90 seconds...")
        
        request = predictor.queue(
            item=game_data,
            num_experts=3,
            note_length=(5, 8)
        )
        
        print(f"Request ID: {request.request_id}")
        
        # Check what attributes the request object has
        request_attrs = [attr for attr in dir(request) if not attr.startswith('_')]
        print(f"Request attributes: {request_attrs}")
        
        # Try to get status if it exists
        if hasattr(request, 'status'):
            print(f"Status: {request.status}")
        elif hasattr(request, 'state'):
            print(f"State: {request.state}")
        else:
            print("Request queued successfully")
        
        print(f"\nStep 4: Waiting for expert analysis...")
        predictions = predictor.get_request_predictions(
            request_id=request.request_id,
            try_every=5,  # Check every 5 seconds
            max_tries=18  # 90 seconds max
        )
        
        if not predictions:
            print("ERROR: Prediction timed out or failed")
            return None
            
        print(f"\nStep 5: SUCCESS! Prediction completed")
        
        # Parse the actual response structure
        print(f"\nRaw Response Type: {type(predictions)}")
        print(f"Response Attributes: {dir(predictions)}")
        
        # Try different ways to extract data
        if hasattr(predictions, 'predictions') and predictions.predictions:
            print(f"Found predictions list with {len(predictions.predictions)} items")
            
            for i, pred in enumerate(predictions.predictions):
                print(f"\nExpert {i+1} Prediction:")
                print(f"  Type: {type(pred)}")
                print(f"  Attributes: {dir(pred)}")
                
                # Try to get probability
                if hasattr(pred, 'probability'):
                    print(f"  Probability: {pred.probability}")
                elif hasattr(pred, 'estimate'):
                    print(f"  Estimate: {pred.estimate}")
                
                # Try to get explanation
                if hasattr(pred, 'text'):
                    print(f"  Explanation: {pred.text[:200]}...")
                elif hasattr(pred, 'note'):
                    print(f"  Note: {pred.note[:200]}...")
                elif hasattr(pred, 'explanation'):
                    print(f"  Explanation: {pred.explanation[:200]}...")
        
        # Try alternative response structure
        if hasattr(predictions, 'probability'):
            print(f"Direct probability: {predictions.probability}")
        
        if hasattr(predictions, 'estimate'):
            print(f"Direct estimate: {predictions.estimate}")
            
        if hasattr(predictions, 'text'):
            print(f"Direct text: {predictions.text[:200]}...")
        
        # Show the full object structure
        print(f"\nFull Response Object:")
        print(f"{predictions}")
        
        return predictions
        
    except Exception as e:
        print(f"ERROR during prediction: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Manual testing interface"""
    print("CHRONULUS MANUAL TESTING")
    print("One prediction at a time, you control everything")
    print("="*60)
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("Cannot proceed without API key")
        return
    
    # Create session
    session = create_session(api_key)
    
    while True:
        print(f"\n" + "="*40)
        print("AVAILABLE TESTS:")
        print("1. Soccer: Alaves @ Real Betis (your Discord data)")
        print("2. MLB: Rockies @ Pirates (your Discord data)")
        print("0. Exit")
        
        choice = input("\nSelect test (0-2): ").strip()
        
        if choice == '0':
            print("Goodbye!")
            break
        elif choice == '1':
            game_data = test_alaves_real_betis()
            result = run_single_prediction(game_data, session)
            
            if result:
                print(f"\nPREDICTION COMPLETE FOR SOCCER MATCH")
                input("Press Enter to continue...")
            
        elif choice == '2':
            game_data = test_rockies_pirates()
            result = run_single_prediction(game_data, session)
            
            if result:
                print(f"\nPREDICTION COMPLETE FOR MLB GAME")
                input("Press Enter to continue...")
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()