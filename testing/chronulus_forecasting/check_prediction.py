#!/usr/bin/env python3
"""
Check Status of Queued Prediction
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

def check_prediction_status(request_id):
    """Check the status of a specific prediction request"""
    api_key = load_api_key()
    if not api_key:
        print("ERROR: No API key found")
        return
    
    print(f"Checking prediction status for: {request_id}")
    
    try:
        # Use static method to check prediction status
        predictions = BinaryPredictor.get_request_predictions_static(
            request_id=request_id,
            try_every=1,  # Check immediately
            max_tries=1,  # Don't wait, just check once
            env=dict(CHRONULUS_API_KEY=api_key),
            verbose=True
        )
        
        if predictions:
            print("SUCCESS: Prediction completed!")
            
            # Analyze the response
            print(f"\nResponse Type: {type(predictions)}")
            
            if hasattr(predictions, 'predictions'):
                print(f"Found {len(predictions.predictions)} expert predictions:")
                
                for i, pred in enumerate(predictions.predictions):
                    print(f"\nExpert {i+1}:")
                    
                    # Get probability/estimate
                    if hasattr(pred, 'probability'):
                        print(f"  Probability: {pred.probability:.3f} ({pred.probability:.1%})")
                    elif hasattr(pred, 'estimate'):
                        print(f"  Estimate: {pred.estimate:.3f} ({pred.estimate:.1%})")
                    
                    # Get explanation
                    if hasattr(pred, 'text'):
                        print(f"  Explanation: {pred.text[:150]}...")
                    elif hasattr(pred, 'note'):
                        print(f"  Note: {pred.note[:150]}...")
                
                # Calculate consensus if multiple experts
                if len(predictions.predictions) > 1:
                    probs = []
                    for pred in predictions.predictions:
                        if hasattr(pred, 'probability'):
                            probs.append(pred.probability)
                        elif hasattr(pred, 'estimate'):
                            probs.append(pred.estimate)
                    
                    if probs:
                        avg_prob = sum(probs) / len(probs)
                        print(f"\nCONSENSUS: {avg_prob:.3f} ({avg_prob:.1%})")
                        print(f"Range: {min(probs):.3f} - {max(probs):.3f}")
            
            return predictions
        else:
            print("Prediction still pending or failed")
            return None
            
    except Exception as e:
        print(f"ERROR checking prediction: {e}")
        return None

if __name__ == "__main__":
    print("PREDICTION STATUS CHECKER")
    print("="*40)
    
    # Your last request ID from the error message
    last_request_id = "4c883c8d-4e4f-4a6b-9061-06c59c22d51d"
    
    print(f"Checking your last prediction...")
    result = check_prediction_status(last_request_id)
    
    if not result:
        print("\nThat prediction may still be processing.")
        print("Try running manual_single_test.py again to continue waiting.")
    
    print("\nTo check a different prediction, edit this script with the new request_id")