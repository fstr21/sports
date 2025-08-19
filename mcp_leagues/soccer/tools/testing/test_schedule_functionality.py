#!/usr/bin/env python3
"""
Test script to verify schedule.py functionality without interactive input
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from schedule import (
    mcp_call, 
    get_h2h_analysis, 
    get_enhanced_h2h_data,
    get_custom_h2h_analysis,
    print_h2h_summary,
    print_custom_h2h_analysis,
    validate_date_format,
    convert_to_american_odds
)

async def test_functionality():
    """Test the core functionality of schedule.py"""
    print("=" * 60)
    print("TESTING SCHEDULE.PY FUNCTIONALITY")
    print("=" * 60)
    
    # Test 1: Date validation
    print("\n1. Testing date validation...")
    test_dates = ["19-08-2025", "19/08/2025", "2025-08-19", "invalid-date"]
    for date in test_dates:
        result = validate_date_format(date)
        print(f"  {date} -> {result}")
    
    # Test 2: American odds conversion
    print("\n2. Testing American odds conversion...")
    test_odds = [1.5, 2.0, 2.5, 3.0, 1.1]
    for odds in test_odds:
        american = convert_to_american_odds(odds)
        print(f"  {odds} -> {american}")
    
    # Test 3: MCP call (get betting matches)
    print("\n3. Testing MCP call for betting matches...")
    try:
        result = await mcp_call("get_betting_matches", {
            "date": "19-08-2025",
            "league_filter": "EPL"
        })
        print(f"  Result type: {type(result)}")
        if "error" in result:
            print(f"  Error: {result['error']}")
        else:
            matches_count = result.get('total_matches', 0)
            print(f"  Found {matches_count} matches")
    except Exception as e:
        print(f"  Exception: {e}")
    
    # Test 4: H2H analysis (if we can find valid team IDs)
    print("\n4. Testing H2H analysis...")
    # Use known team IDs - West Ham vs Chelsea
    home_team_id = 3059  # West Ham
    away_team_id = 2916  # Chelsea
    home_team_name = "West Ham United"
    away_team_name = "Chelsea"
    
    try:
        print("  Testing standard H2H endpoint...")
        h2h_data = await get_h2h_analysis(home_team_id, away_team_id, home_team_name, away_team_name)
        if "error" not in h2h_data:
            print("  [OK] Standard H2H analysis successful")
        else:
            print(f"  [ERROR] Standard H2H error: {h2h_data['error']}")
        
        print("  Testing enhanced H2H data...")
        enhanced_data = await get_enhanced_h2h_data(home_team_id, away_team_id)
        if "error" not in enhanced_data:
            print("  [OK] Enhanced H2H data successful")
        else:
            print(f"  [ERROR] Enhanced H2H error: {enhanced_data['error']}")
        
        print("  Testing custom H2H analysis...")
        custom_data = await get_custom_h2h_analysis(
            home_team_id, away_team_id, home_team_name, away_team_name, 228  # EPL league ID
        )
        if custom_data:
            home_matches = len(custom_data.get('home_recent_matches', []))
            away_matches = len(custom_data.get('away_recent_matches', []))
            h2h_meetings = len(custom_data.get('h2h_recent_meetings', []))
            print(f"  [OK] Custom H2H analysis: {home_matches} home matches, {away_matches} away matches, {h2h_meetings} H2H meetings")
        else:
            print("  [ERROR] Custom H2H analysis failed")
            
    except Exception as e:
        print(f"  Exception in H2H testing: {e}")
    
    print("\n" + "=" * 60)
    print("FUNCTIONALITY TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_functionality())