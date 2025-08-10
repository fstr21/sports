#!/usr/bin/env python3
"""
Final comprehensive test of the fully working MCP server.
"""
import sys
import os
import json
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sports_mcp'))

from interactive_sports_test import SportsTestInterface

def test_angel_reese_final():
    """Final test of Angel Reese through complete MCP server"""
    print("FINAL TEST: Angel Reese WNBA Stats via MCP Server")
    print("=" * 55)
    
    interface = SportsTestInterface()
    interface.current_sport_league = ("basketball", "wnba")
    
    print("Making request to MCP server...")
    success, result = interface.make_request("POST", "/espn/player-stats", {
        "sport": "basketball",
        "league": "wnba", 
        "player_id": "4433402",
        "limit": 5
    })
    
    if success and result.get("ok"):
        data = result.get("data", {})
        
        # Player profile
        athlete = data.get("player_profile", {}).get("athlete", {})
        name = athlete.get("displayName", "Unknown")
        position = athlete.get("position", {}).get("abbreviation", "N/A")
        height = athlete.get("height", "Unknown")
        weight = athlete.get("weight", "Unknown")
        
        print(f"\nPLAYER PROFILE:")
        print(f"  Name: {name}")
        print(f"  Position: {position}")
        print(f"  Physical: {height}, {weight}")
        
        # Check for parsed statistics
        parsed_stats = data.get("parsed_statistics", {})
        basketball_stats = data.get("basketball_specification_stats", {})
        debug_info = data.get("debug_info", {})
        
        print(f"\nSTATISTICS RESULTS:")
        print(f"  Parsed stats found: {len(parsed_stats)} stats")
        print(f"  Basketball stats found: {len(basketball_stats)} stats") 
        print(f"  Debug info: {debug_info}")
        
        if parsed_stats:
            print(f"\n📊 ANGEL REESE 2025 WNBA SEASON STATS:")
            print(f"  {'='*40}")
            
            # Show in basketball specification order
            basketball_order = ["Points", "Rebounds", "Assists", "3PM", "Steals", "Blocks", "FG%", "Minutes"]
            
            for stat_name in basketball_order:
                if stat_name in parsed_stats:
                    print(f"  {stat_name:15}: {parsed_stats[stat_name]}")
            
            # Show any additional stats
            other_stats = {k: v for k, v in parsed_stats.items() if k not in basketball_order}
            if other_stats:
                print(f"\n  Additional Stats:")
                for stat_name, value in other_stats.items():
                    print(f"  {stat_name:15}: {value}")
        
        # Recent games context
        recent_games = data.get("recent_games", {}).get("events", [])
        print(f"\n  Recent games context: {len(recent_games)} games")
        
        # Save the complete response
        save_data = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "final_mcp_server_test",
            "player_name": name,
            "parsed_statistics": parsed_stats,
            "full_response": result
        }
        
        filename = f"test/final_mcp_test_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        print(f"\n💾 Complete test results saved to: {filename}")
        
        return len(parsed_stats) > 0
    else:
        print(f"❌ FAILED: {result}")
        return False

def test_multiple_sports_final():
    """Final test across multiple sports"""
    print(f"\n{'='*55}")
    print("FINAL TEST: Multiple Sports via MCP Server")
    print("=" * 55)
    
    interface = SportsTestInterface()
    
    test_cases = [
        ("basketball", "wnba", "4433402", "Angel Reese"),
        ("basketball", "nba", "1966", "LeBron James"),
        ("football", "nfl", "4361093", "Kyler Gordon"),
        ("baseball", "mlb", "32655", "Byron Buxton")
    ]
    
    results = {}
    
    for sport, league, player_id, name in test_cases:
        print(f"\nTesting {sport.upper()}: {name}")
        interface.current_sport_league = (sport, league)
        
        success, result = interface.make_request("POST", "/espn/player-stats", {
            "sport": sport,
            "league": league,
            "player_id": player_id,
            "limit": 3
        })
        
        if success and result.get("ok"):
            data = result.get("data", {})
            parsed_stats = data.get("parsed_statistics", {})
            debug_info = data.get("debug_info", {})
            
            print(f"  ✓ SUCCESS: {len(parsed_stats)} stats parsed")
            print(f"  Debug: {debug_info.get('parsed_stats_count', 0)} stats, splits: {debug_info.get('has_splits', False)}")
            
            # Show top 3 stats
            for i, (stat_name, value) in enumerate(list(parsed_stats.items())[:3]):
                print(f"    {stat_name}: {value}")
            
            results[f"{sport}/{league}"] = len(parsed_stats)
        else:
            print(f"  ❌ FAILED: {result.get('message', 'Unknown error') if isinstance(result, dict) else result}")
            results[f"{sport}/{league}"] = 0
    
    return results

if __name__ == "__main__":
    print("🏆 FINAL COMPREHENSIVE MCP SERVER TEST")
    print("=" * 60)
    
    # Test Angel Reese specifically
    angel_success = test_angel_reese_final()
    
    # Test multiple sports  
    multi_results = test_multiple_sports_final()
    
    # Final summary
    print(f"\n{'='*60}")
    print("🎯 FINAL RESULTS SUMMARY:")
    print("=" * 60)
    
    print(f"Angel Reese WNBA Stats: {'✓ SUCCESS' if angel_success else '❌ FAILED'}")
    
    total_stats = 0
    for sport_league, stat_count in multi_results.items():
        status = "✓ SUCCESS" if stat_count > 0 else "❌ FAILED"
        print(f"{sport_league:<20}: {status} ({stat_count} stats)")
        total_stats += stat_count
    
    print(f"\nOverall Statistics Extracted: {total_stats} total stats")
    
    successful_tests = sum(1 for count in multi_results.values() if count > 0) + (1 if angel_success else 0)
    total_tests = len(multi_results) + 1
    
    print(f"Successful API Calls: {successful_tests}/{total_tests}")
    
    if successful_tests == total_tests and total_stats > 0:
        print(f"\n🎉 COMPLETE SUCCESS!")
        print("✅ MCP Server fully operational")
        print("✅ ESPN Core API integration working")
        print("✅ Sport-specific statistics parsing working") 
        print("✅ All sports supported per specification")
        print("✅ No more 404 errors")
        print("✅ Comprehensive player statistics available")
    else:
        print(f"\n⚠️ Partial success - some issues remain")
        print(f"Stats extraction: {'✓' if total_stats > 0 else '❌'}")
        print(f"API calls: {'✓' if successful_tests == total_tests else '❌'}")