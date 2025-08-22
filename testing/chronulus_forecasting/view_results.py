#!/usr/bin/env python3
"""
Simple Results Viewer
Shows you exactly what Chronulus returns
"""

def analyze_binary_prediction_response(predictions):
    """Analyze the BinaryPrediction response structure"""
    print("ANALYZING CHRONULUS RESPONSE")
    print("="*50)
    
    print(f"Response Type: {type(predictions)}")
    
    # Check if it's a BinaryPredictionSet
    if hasattr(predictions, 'predictions'):
        print(f"Found prediction set with {len(predictions.predictions)} expert predictions")
        
        # Analyze each expert prediction
        for i, pred in enumerate(predictions.predictions):
            print(f"\nEXPERT {i+1} PREDICTION:")
            print(f"  Object Type: {type(pred)}")
            
            # Check all possible attributes
            attrs = [attr for attr in dir(pred) if not attr.startswith('_')]
            print(f"  Available attributes: {attrs}")
            
            # Try common probability fields
            for prob_field in ['probability', 'estimate', 'prediction', 'value']:
                if hasattr(pred, prob_field):
                    value = getattr(pred, prob_field)
                    print(f"  {prob_field}: {value}")
            
            # Try common text fields
            for text_field in ['text', 'note', 'explanation', 'reasoning']:
                if hasattr(pred, text_field):
                    value = getattr(pred, text_field)
                    if isinstance(value, str):
                        print(f"  {text_field}: {value[:100]}...")
                    else:
                        print(f"  {text_field}: {value}")
        
        # Check for consensus/summary data
        summary_attrs = ['consensus', 'summary', 'beta_distribution', 'confidence']
        for attr in summary_attrs:
            if hasattr(predictions, attr):
                value = getattr(predictions, attr)
                print(f"\nSUMMARY {attr}: {value}")
    
    # Check for direct prediction attributes
    direct_attrs = ['probability', 'estimate', 'confidence', 'alpha', 'beta']
    for attr in direct_attrs:
        if hasattr(predictions, attr):
            value = getattr(predictions, attr)
            print(f"\nDIRECT {attr}: {value}")
    
    return predictions

def calculate_betting_value(probability, odds):
    """Calculate betting value from probability and odds"""
    if odds > 0:
        # American odds format (+160)
        implied_prob = 100 / (odds + 100)
        decimal_odds = (odds / 100) + 1
    else:
        # American odds format (-190)
        implied_prob = abs(odds) / (abs(odds) + 100)
        decimal_odds = (100 / abs(odds)) + 1
    
    expected_value = (probability * decimal_odds) - 1
    edge = probability - implied_prob
    
    print(f"\nBETTING VALUE ANALYSIS:")
    print(f"  Chronulus Probability: {probability:.1%}")
    print(f"  Market Implied Prob: {implied_prob:.1%}")
    print(f"  Edge: {edge:+.1%}")
    print(f"  Expected Value: {expected_value:+.1%}")
    
    if edge > 0.10:
        print(f"  Recommendation: STRONG BET")
    elif edge > 0.05:
        print(f"  Recommendation: MODERATE BET")
    else:
        print(f"  Recommendation: NO BET")

# Example usage functions for your data
def example_soccer_analysis():
    """Example of how to analyze soccer results"""
    print("EXAMPLE: Soccer Match Analysis")
    print("="*40)
    print("Alaves @ Real Betis")
    print("Alaves odds: 4.2 (away team)")
    print("Your system: 65% confidence Alaves wins")
    print()
    
    # Simulate getting a probability from Chronulus
    chronulus_probability = 0.72  # Example: 72% chance Alaves wins
    
    print(f"If Chronulus returns {chronulus_probability:.1%} probability:")
    calculate_betting_value(chronulus_probability, 420)  # 4.2 decimal = +320 American
    
    print(f"\nComparison with your system:")
    your_confidence = 0.65
    agreement = abs(chronulus_probability - your_confidence)
    print(f"  Your system: {your_confidence:.1%}")
    print(f"  Chronulus: {chronulus_probability:.1%}")
    print(f"  Difference: {agreement:.1%}")
    
    if agreement < 0.10:
        print(f"  Agreement: HIGH")
    elif agreement < 0.20:
        print(f"  Agreement: MODERATE")
    else:
        print(f"  Agreement: LOW")

def example_mlb_analysis():
    """Example of how to analyze MLB results"""
    print("EXAMPLE: MLB Game Analysis")
    print("="*40)
    print("Rockies @ Pirates")
    print("Rockies odds: +160 (away team)")
    print("Recent form: Rockies 7-3 L10, Pirates 3-7 L10")
    print()
    
    # Simulate getting a probability from Chronulus
    chronulus_probability = 0.42  # Example: 42% chance Rockies win
    
    print(f"If Chronulus returns {chronulus_probability:.1%} probability:")
    calculate_betting_value(chronulus_probability, 160)  # +160 American odds
    
    # Market analysis
    print(f"\nMarket Context:")
    print(f"  Pirates favored despite recent struggles (3-7 L10)")
    print(f"  Rockies undervalued despite hot streak (7-3 L10)")
    print(f"  Form vs overall record creates betting opportunity")

if __name__ == "__main__":
    print("CHRONULUS RESULTS ANALYSIS TOOL")
    print("="*50)
    print("This shows you how to interpret Chronulus responses")
    print()
    
    print("1. Example Soccer Analysis")
    example_soccer_analysis()
    
    print("\n" + "="*50)
    print("2. Example MLB Analysis") 
    example_mlb_analysis()
    
    print("\n" + "="*50)
    print("3. How to use analyze_binary_prediction_response():")
    print("   # After getting Chronulus response:")
    print("   # result = analyze_binary_prediction_response(predictions)")
    print("   # calculate_betting_value(probability, odds)")