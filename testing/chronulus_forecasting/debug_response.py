#!/usr/bin/env python3
"""
Debug Response Structure
Check your completed prediction to see the exact response format
"""
from pathlib import Path
from chronulus.estimator import BinaryPredictor

def load_api_key():
    """Load API key from .env.local"""
    env_file = Path(__file__).parent.parent.parent / '.env.local'
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('CHRONULUS_API_KEY='):
                    return line.split('=', 1)[1].strip().strip('"\'')
    except Exception:
        pass
    return None

def debug_prediction_response(request_id):
    """Debug the structure of your completed prediction"""
    print("DEBUGGING PREDICTION RESPONSE STRUCTURE")
    print("="*60)
    
    api_key = load_api_key()
    if not api_key:
        print("ERROR: No API key found")
        return
    
    print(f"Checking prediction: {request_id}")
    
    try:
        # Get the completed prediction
        predictions = BinaryPredictor.get_request_predictions_static(
            request_id=request_id,
            try_every=1,
            max_tries=1,
            env=dict(CHRONULUS_API_KEY=api_key),
            verbose=False
        )
        
        if not predictions:
            print("ERROR: No predictions returned")
            return
        
        print(f"SUCCESS: Got prediction response")
        print(f"Response Type: {type(predictions)}")
        print(f"Response Attributes: {[attr for attr in dir(predictions) if not attr.startswith('_')]}")
        
        # Check if it has predictions attribute
        if hasattr(predictions, 'predictions'):
            print(f"\nFound predictions list with {len(predictions.predictions)} items")
            
            for i, pred in enumerate(predictions.predictions):
                print(f"\nPREDICTION {i+1}:")
                print(f"  Type: {type(pred)}")
                print(f"  Attributes: {[attr for attr in dir(pred) if not attr.startswith('_')]}")
                
                # Check all possible probability fields
                prob_fields = ['probability', 'estimate', 'prediction', 'value', 'p', 'prob']
                found_prob = False
                
                for field in prob_fields:
                    if hasattr(pred, field):
                        value = getattr(pred, field)
                        print(f"  {field}: {value} (type: {type(value)})")
                        found_prob = True
                
                if not found_prob:
                    print(f"  No probability field found!")
                
                # Check text fields
                text_fields = ['text', 'note', 'explanation', 'reasoning']
                for field in text_fields:
                    if hasattr(pred, field):
                        value = getattr(pred, field)
                        if isinstance(value, str) and len(value) > 0:
                            print(f"  {field}: {value[:100]}...")
                
                # Show the full object
                print(f"  Full object: {pred}")
        
        # Check for direct attributes on main object
        direct_fields = ['probability', 'estimate', 'consensus', 'mean', 'average']
        for field in direct_fields:
            if hasattr(predictions, field):
                value = getattr(predictions, field)
                print(f"\nDirect {field}: {value}")
        
        # Try to find any numeric values that might be probabilities
        print(f"\nFull predictions object:")
        print(f"{predictions}")
        
        return predictions
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Your last request ID from the log
    last_request_id = "2829dbe2-722b-4aea-8aee-bb64516f0cb6"
    
    print("Debugging your completed Rockies prediction...")
    result = debug_prediction_response(last_request_id)
    
    if result:
        print("\nDEBUG COMPLETE - Check output above for probability extraction method")
    else:
        print("\nDEBUG FAILED - Prediction may not be accessible")