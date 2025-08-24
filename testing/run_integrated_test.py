#!/usr/bin/env python3
"""
Quick Test Runner for Integrated Custom Chronulus
Runs the integrated test and displays results
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from test_integrated_custom_chronulus import IntegratedChronulusTest

async def main():
    """Run the test with better formatting"""
    print("🚀 INTEGRATED CUSTOM CHRONULUS TEST")
    print("=" * 60)
    print("Testing custom Chronulus with real MLB MCP data")
    print("Comparing against paid Chronulus quality")
    print("-" * 60)
    
    tester = IntegratedChronulusTest()
    
    try:
        results = await tester.run_test()
        
        if results.get("status") == "success":
            print("\n🎯 ANALYSIS PREVIEW:")
            print("-" * 40)
            
            analysis = results.get("chronulus_analysis", {}).get("analysis", {})
            if analysis:
                away_prob = analysis.get("away_team_win_probability", 0)
                home_prob = analysis.get("home_team_win_probability", 0) 
                
                print(f"Away Team Win: {away_prob:.1%}")
                print(f"Home Team Win: {home_prob:.1%}")
                print(f"Expert Count: {analysis.get('expert_count', 'N/A')}")
                print(f"Cost Estimate: {analysis.get('cost_estimate', 'N/A')}")
                
                expert_analysis = analysis.get("expert_analysis", "")
                if expert_analysis and len(expert_analysis) > 200:
                    print(f"\nExpert Preview: {expert_analysis[:200]}...")
                
            print("\n✅ Test completed successfully!")
            print("📄 Check the generated JSON file for full results")
            
        else:
            print(f"\n❌ Test failed: {results.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n💥 Test crashed: {e}")
        
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())