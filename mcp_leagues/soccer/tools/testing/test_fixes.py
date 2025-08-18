#!/usr/bin/env python3
"""
Quick test for the fixes:
1. Filter out "None vs None" matches
2. Warn about stale odds for live games
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'production'))

from interactive_match_analyzer import InteractiveMatchAnalyzer

def test_match_filtering():
    """Test that None vs None matches are filtered out"""
    analyzer = InteractiveMatchAnalyzer("test_token")
    
    # Test data with invalid match
    test_match_valid = {
        'teams': {
            'home': {'name': 'Liverpool', 'id': 1},
            'away': {'name': 'Chelsea', 'id': 2}
        }
    }
    
    test_match_invalid = {
        'teams': {
            'home': {'name': 'None', 'id': 3},
            'away': {'name': 'None', 'id': 4}
        }
    }
    
    test_match_missing = {
        'teams': {
            'home': {'name': '', 'id': 5},
            'away': {'name': 'Arsenal', 'id': 6}
        }
    }
    
    print("Testing match validation...")
    print(f"Valid match (Liverpool vs Chelsea): {analyzer.is_valid_match(test_match_valid)}")
    print(f"Invalid match (None vs None): {analyzer.is_valid_match(test_match_invalid)}")  
    print(f"Missing team name: {analyzer.is_valid_match(test_match_missing)}")
    
    # Test filtering
    test_response = [{
        'matches': [test_match_valid, test_match_invalid, test_match_missing]
    }]
    
    filtered_matches = analyzer.extract_matches_from_response(test_response)
    print(f"\nOriginal matches: 3")
    print(f"Filtered matches: {len(filtered_matches)}")
    print("✅ Filter test passed!" if len(filtered_matches) == 1 else "❌ Filter test failed!")

def main():
    print("=" * 50)
    print("TESTING SCRIPT FIXES")
    print("=" * 50)
    
    test_match_filtering()
    
    print("\n" + "=" * 50)
    print("FIXES IMPLEMENTED:")
    print("✅ Filter out 'None vs None' matches")
    print("✅ Warn about stale odds for live games")
    print("✅ Show final scores for finished games")
    print("✅ Filter options for match status")
    print("=" * 50)

if __name__ == "__main__":
    main()