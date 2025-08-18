#!/usr/bin/env python3
"""
H2H Strategy Testing Script
Quick test runner for the comprehensive future game analyzer
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from comprehensive_future_game_analyzer import FutureGameAnalyzer

def quick_test():
    """Run a quick test of the H2H strategy framework"""
    print("🧪 QUICK H2H STRATEGY TEST")
    print("=" * 50)
    
    # Initialize analyzer
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    analyzer = FutureGameAnalyzer(auth_token)
    
    print("✅ Analyzer initialized successfully")
    print("🔍 Testing with EPL matches only (faster)")
    
    # Test with limited scope for quick validation
    try:
        analyzer.run_comprehensive_test(['EPL'], max_matches_to_analyze=2)
        print("\n✅ Test completed successfully!")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

def validate_api_access():
    """Validate API access and basic functionality"""
    print("🔐 VALIDATING API ACCESS")
    print("=" * 40)
    
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    analyzer = FutureGameAnalyzer(auth_token)
    
    # Test basic API call
    leagues_data = analyzer.api_call('league/', {'country_id': 8})  # England
    
    if leagues_data:
        print("✅ API access working")
        print(f"📊 Found {len(leagues_data)} leagues in England")
        return True
    else:
        print("❌ API access failed")
        return False

if __name__ == "__main__":
    print("🚀 H2H STRATEGY TESTING SUITE")
    print("=" * 60)
    
    # Step 1: Validate API access
    if not validate_api_access():
        print("❌ Aborting: API access validation failed")
        sys.exit(1)
    
    # Step 2: Run quick test
    print("\n" + "=" * 60)
    if quick_test():
        print("\n🎉 ALL TESTS PASSED!")
        print("💡 The H2H strategy framework is ready for comprehensive analysis")
    else:
        print("\n💥 TESTS FAILED!")
        print("🔧 Check the error messages above and fix any issues")