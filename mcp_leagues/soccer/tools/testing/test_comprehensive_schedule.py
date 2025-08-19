#!/usr/bin/env python3
"""
Test the comprehensive data integration in schedule.py
"""
import asyncio
import sys
import os

# Add current directory to path so we can import
sys.path.append(os.path.dirname(__file__))

from schedule import get_custom_h2h_analysis, print_custom_h2h_analysis

async def test_comprehensive_data():
    """Test the comprehensive H2H analysis"""
    print("=" * 80)
    print("TESTING COMPREHENSIVE DATA INTEGRATION")
    print("=" * 80)
    
    # Test with Real Madrid vs Osasuna (known working teams)
    home_team_id = 4883  # Real Madrid
    away_team_id = 4937  # Osasuna 
    home_team_name = "Real Madrid"
    away_team_name = "Osasuna"
    league_id = 297  # La Liga
    
    print(f"Testing comprehensive H2H analysis for {home_team_name} vs {away_team_name}...")
    
    try:
        # Get comprehensive analysis
        comprehensive_data = await get_custom_h2h_analysis(
            home_team_id, away_team_id, home_team_name, away_team_name, league_id
        )
        
        if comprehensive_data:
            home_matches = len(comprehensive_data.get('home_comprehensive_matches', []))
            away_matches = len(comprehensive_data.get('away_comprehensive_matches', []))
            h2h_meetings = len(comprehensive_data.get('h2h_recent_meetings', []))
            
            print(f"\nComprehensive data extracted:")
            print(f"  {home_team_name}: {home_matches} matches with full data")
            print(f"  {away_team_name}: {away_matches} matches with full data")
            print(f"  H2H meetings: {h2h_meetings}")
            
            # Show the comprehensive analysis
            print_custom_h2h_analysis(comprehensive_data)
            
        else:
            print("No comprehensive data returned")
            
    except Exception as e:
        print(f"Error in comprehensive analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_comprehensive_data())