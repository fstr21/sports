#!/usr/bin/env python3
"""
Simple H2H Strategy Test Runner
Tests the head-to-head analysis workflow with real data
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def test_api_access():
    """Test basic API access"""
    print("=" * 60)
    print("TESTING API ACCESS")
    print("=" * 60)
    
    try:
        from unified_h2h_intelligence import UnifiedH2HIntelligence
        
        auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
        analyzer = UnifiedH2HIntelligence(auth_token)
        
        # Test basic API call
        leagues_data = analyzer.api_call('league/', {'country_id': 8})  # England
        
        if leagues_data:
            print(f"SUCCESS: API access working")
            print(f"Found {len(leagues_data)} leagues in England")
            return True
        else:
            print("ERROR: API access failed")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to test API access - {e}")
        return False

def test_match_discovery():
    """Test future match discovery"""
    print("\n" + "=" * 60)
    print("TESTING MATCH DISCOVERY")
    print("=" * 60)
    
    try:
        from unified_h2h_intelligence import UnifiedH2HIntelligence
        
        auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
        analyzer = UnifiedH2HIntelligence(auth_token)
        
        # Search for matches in next 3 days (limited for testing)
        upcoming_matches = analyzer.smart_match_finder(days_ahead=3)
        
        total_matches = sum(len(matches) for matches in upcoming_matches.values())
        
        if total_matches > 0:
            print(f"SUCCESS: Found {total_matches} upcoming matches")
            
            # Show first few matches
            for date, matches in list(upcoming_matches.items())[:2]:
                print(f"\n{date}:")
                for match in matches[:3]:  # Show first 3 matches per date
                    teams = match.get('teams', {})
                    home_name = teams.get('home', {}).get('name', 'Unknown')
                    away_name = teams.get('away', {}).get('name', 'Unknown')
                    league_name = match.get('league_info', {}).get('name', 'Unknown')
                    print(f"  {home_name} vs {away_name} ({league_name})")
            
            return True, upcoming_matches
        else:
            print("WARNING: No upcoming matches found (may be normal)")
            return True, {}
            
    except Exception as e:
        print(f"ERROR: Match discovery failed - {e}")
        return False, {}

def test_form_analysis():
    """Test form analysis on known teams"""
    print("\n" + "=" * 60)
    print("TESTING FORM ANALYSIS")
    print("=" * 60)
    
    try:
        from unified_h2h_intelligence import UnifiedH2HIntelligence
        
        auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
        analyzer = UnifiedH2HIntelligence(auth_token)
        
        # Test with known EPL teams (Liverpool and Chelsea)
        liverpool_id = 4138
        chelsea_id = 2916
        epl_league_id = 228
        
        print("Analyzing Liverpool recent form...")
        liverpool_form = analyzer.enhanced_form_analyzer(liverpool_id, "Liverpool", epl_league_id)
        
        print("Analyzing Chelsea recent form...")  
        chelsea_form = analyzer.enhanced_form_analyzer(chelsea_id, "Chelsea", epl_league_id)
        
        # Display basic results
        print(f"\nLiverpool:")
        print(f"  Matches analyzed: {len(liverpool_form['matches'])}")
        print(f"  Win percentage: {liverpool_form['recent_form']['win_percentage']:.1f}%")
        print(f"  Form rating: {liverpool_form['momentum_indicators']['form_rating']}/10")
        
        print(f"\nChelsea:")
        print(f"  Matches analyzed: {len(chelsea_form['matches'])}")
        print(f"  Win percentage: {chelsea_form['recent_form']['win_percentage']:.1f}%")
        print(f"  Form rating: {chelsea_form['momentum_indicators']['form_rating']}/10")
        
        if len(liverpool_form['matches']) > 0 and len(chelsea_form['matches']) > 0:
            print("SUCCESS: Form analysis working")
            return True
        else:
            print("WARNING: Limited form data found")
            return True
            
    except Exception as e:
        print(f"ERROR: Form analysis failed - {e}")
        return False

def test_ultimate_analysis():
    """Test the complete ultimate analysis"""
    print("\n" + "=" * 60)
    print("TESTING ULTIMATE H2H ANALYSIS")
    print("=" * 60)
    
    try:
        from unified_h2h_intelligence import UnifiedH2HIntelligence
        
        auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
        analyzer = UnifiedH2HIntelligence(auth_token)
        
        # Test with known rivalry: Liverpool vs Chelsea
        liverpool_id = 4138
        chelsea_id = 2916
        epl_league_id = 228
        
        print("Running ultimate H2H analysis: Liverpool vs Chelsea")
        
        analysis = analyzer.ultimate_h2h_analysis(
            liverpool_id, chelsea_id,
            "Liverpool", "Chelsea", 
            epl_league_id
        )
        
        # Display key results
        prediction = analysis['prediction']
        confidence_score = analysis['confidence_score']
        
        print(f"\nULTIMATE ANALYSIS RESULTS:")
        print(f"Prediction: {prediction['prediction']}")
        print(f"Confidence: {prediction['confidence']}")
        print(f"Overall Confidence Score: {confidence_score}/100")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_analysis_results_{timestamp}.json"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {filename}")
        print("SUCCESS: Ultimate analysis completed")
        return True
        
    except Exception as e:
        print(f"ERROR: Ultimate analysis failed - {e}")
        return False

def main():
    """Run all tests"""
    print("H2H STRATEGY COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print("Testing the complete head-to-head analysis workflow")
    print()
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: API Access
    if test_api_access():
        tests_passed += 1
    
    # Test 2: Match Discovery
    success, matches = test_match_discovery()
    if success:
        tests_passed += 1
    
    # Test 3: Form Analysis
    if test_form_analysis():
        tests_passed += 1
    
    # Test 4: Ultimate Analysis
    if test_ultimate_analysis():
        tests_passed += 1
    
    # Results
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("STATUS: ALL TESTS PASSED!")
        print("The H2H strategy framework is fully operational")
    elif tests_passed >= 3:
        print("STATUS: MOSTLY WORKING")
        print("Core functionality operational with minor issues")
    else:
        print("STATUS: NEEDS ATTENTION") 
        print("Multiple test failures - check error messages above")
    
    print("\nFRAMEWORK CAPABILITIES:")
    print("- Future match discovery across multiple leagues")
    print("- Enhanced recent form analysis (15 matches)")
    print("- Historical head-to-head statistics")
    print("- Betting intelligence and predictions")
    print("- Confidence scoring and reliability assessment")
    
    print(f"\nTesting completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()