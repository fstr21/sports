#!/usr/bin/env python3
"""
Quick Results Checker
Check results for request ID: 5d9e32df-1e55-475f-b682-838df3cc8d3b
"""
from pathlib import Path
from chronulus.estimator import BinaryPredictor

def load_api_key():
    env_file = Path(__file__).parent.parent.parent / '.env.local'
    try:
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('CHRONULUS_API_KEY='):
                    return line.split('=', 1)[1].strip().strip('"\'')
    except Exception:
        pass
    return None

def check_prediction():
    api_key = load_api_key()
    if not api_key:
        print("ERROR: No API key")
        return
    
    request_id = "5d9e32df-1e55-475f-b682-838df3cc8d3b"
    print(f"Checking results for: {request_id}")
    
    try:
        predictions = BinaryPredictor.get_request_predictions_static(
            request_id=request_id,
            try_every=1,
            max_tries=1,
            env=dict(CHRONULUS_API_KEY=api_key)
        )
        
        if predictions and hasattr(predictions, 'predictions'):
            print(f"SUCCESS: Found {len(predictions.predictions)} expert predictions!")
            
            expert_probs = []
            for i, pred in enumerate(predictions.predictions):
                if hasattr(pred, 'prob') and isinstance(pred.prob, tuple):
                    prob = pred.prob[0]
                    expert_probs.append(prob)
                    print(f"Expert {i+1}: {prob:.1%} Rockies win")
            
            if expert_probs:
                avg = sum(expert_probs) / len(expert_probs)
                market_implied = 100 / (160 + 100)  # +160 odds
                edge = avg - market_implied
                
                print(f"\nConsensus: {avg:.1%}")
                print(f"Market: {market_implied:.1%}")
                print(f"Edge: {edge:+.1%}")
                print(f"Recommendation: {'BET' if edge > 0 else 'NO BET'}")
        else:
            print("Still pending or no results yet")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_prediction()