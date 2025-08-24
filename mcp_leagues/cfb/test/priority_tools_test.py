#!/usr/bin/env python3
"""
CFB Betting Lines Test - Testing highest priority missing tool
This tool would be essential for sports betting analysis
"""

import asyncio
import json
import httpx
import os
from datetime import datetime

# Test what betting lines data would look like
async def test_betting_lines_concept():
    """Test concept for CFB betting lines tool"""
    
    print("🎯 CFB BETTING LINES TOOL CONCEPT TEST")
    print("=" * 50)
    print("This tool would be essential for sports betting analysis")
    print("Priority: VERY HIGH - Core requirement for betting analysis")
    print()
    
    # Test direct CFBD API for betting lines
    cfbd_url = "https://api.collegefootballdata.com"
    api_key = os.getenv("CFBD_API_KEY")
    
    if not api_key:
        print("❌ CFBD_API_KEY not found in environment")
        print("💡 This tool would require API key configuration")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json"
    }
    
    # Test betting lines endpoint
    test_params = {
        "year": 2024,
        "week": 1,
        "gameId": 401635525  # Florida State @ Georgia Tech from our test
    }
    
    print(f"🔍 Testing CFBD betting lines endpoint...")
    print(f"   Endpoint: {cfbd_url}/lines")
    print(f"   Parameters: {test_params}")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{cfbd_url}/lines",
                params=test_params,
                headers=headers
            )
            
            if response.status_code == 200:
                lines_data = response.json()
                print(f"✅ SUCCESS: Found betting lines data")
                print(f"   Records returned: {len(lines_data)}")
                
                if lines_data:
                    sample_line = lines_data[0]
                    print(f"   Sample data structure:")
                    print(f"     Game ID: {sample_line.get('id')}")
                    print(f"     Home Team: {sample_line.get('homeTeam')}")
                    print(f"     Away Team: {sample_line.get('awayTeam')}")
                    print(f"     Lines available: {len(sample_line.get('lines', []))}")
                    
                    # Show betting providers
                    if sample_line.get('lines'):
                        providers = set()
                        spreads = []
                        totals = []
                        
                        for line in sample_line['lines']:
                            providers.add(line.get('provider', 'Unknown'))
                            if line.get('spread'):
                                spreads.append(f"{line['spread']} ({line.get('provider', 'Unknown')})")
                            if line.get('overUnder'):
                                totals.append(f"{line['overUnder']} ({line.get('provider', 'Unknown')})")
                        
                        print(f"     Providers: {', '.join(providers)}")
                        print(f"     Sample spreads: {', '.join(spreads[:3])}")
                        print(f"     Sample totals: {', '.join(totals[:3])}")
                
                # Save sample data
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"betting_lines_sample_{timestamp}.json"
                
                with open(filename, 'w') as f:
                    json.dump({
                        "test_concept": "CFB Betting Lines Tool",
                        "endpoint": "/lines",
                        "sample_data": lines_data[:3],  # First 3 records
                        "data_structure_analysis": {
                            "total_records": len(lines_data),
                            "providers_found": list(set(line.get('provider', 'Unknown') for game in lines_data for line in game.get('lines', []))),
                            "sample_game": lines_data[0] if lines_data else None
                        }
                    }, indent=2)
                
                print(f"   Sample data saved to: {filename}")
                
            elif response.status_code == 401:
                print("❌ UNAUTHORIZED: Check CFBD API key")
            elif response.status_code == 404:
                print("⚠️  NO DATA: No betting lines for specified parameters")
                print("   This is normal - betting lines may not be available for all games")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
        
        # Demonstrate proposed tool implementation
        print(f"\n📋 PROPOSED TOOL IMPLEMENTATION:")
        print("-" * 30)
        
        proposed_tool = {
            "name": "getCFBBettingLines",
            "description": "Get historical betting lines and spreads for CFB games",
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "Season year"},
                    "week": {"type": "integer", "description": "Week number", "optional": True},
                    "team": {"type": "string", "description": "Team name", "optional": True},
                    "gameId": {"type": "integer", "description": "Specific game ID", "optional": True},
                    "conference": {"type": "string", "description": "Conference name", "optional": True}
                },
                "required": ["year"]
            },
            "usefulness": "VERY HIGH",
            "rationale": "Essential for sports betting analysis, market efficiency studies, and prediction model validation"
        }
        
        print(json.dumps(proposed_tool, indent=2))
        
        print(f"\n💡 IMPLEMENTATION BENEFITS:")
        print("   • Historical line movement analysis")
        print("   • Market efficiency detection")
        print("   • Betting value identification")
        print("   • Prediction model validation")
        print("   • Sharp vs public money tracking")
        
    except Exception as e:
        print(f"❌ Error testing betting lines: {e}")

async def test_advanced_stats_concept():
    """Test concept for advanced CFB statistics"""
    
    print(f"\n🎯 CFB ADVANCED STATS TOOL CONCEPT TEST")
    print("=" * 50)
    print("Advanced metrics for deeper team evaluation")
    print("Priority: VERY HIGH - Modern analytics are crucial")
    print()
    
    cfbd_url = "https://api.collegefootballdata.com"
    api_key = os.getenv("CFBD_API_KEY")
    
    if not api_key:
        print("❌ CFBD_API_KEY not found")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json"
    }
    
    # Test advanced stats endpoint
    test_params = {
        "year": 2024,
        "week": 1,
        "team": "Kansas State"
    }
    
    print(f"🔍 Testing advanced stats endpoint...")
    print(f"   Endpoint: {cfbd_url}/stats/game/advanced")
    print(f"   Parameters: {test_params}")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{cfbd_url}/stats/game/advanced",
                params=test_params,
                headers=headers
            )
            
            if response.status_code == 200:
                stats_data = response.json()
                print(f"✅ SUCCESS: Found advanced stats data")
                print(f"   Records returned: {len(stats_data)}")
                
                if stats_data:
                    sample_stat = stats_data[0]
                    print(f"   Sample advanced metrics:")
                    
                    # Show available advanced metrics
                    offense = sample_stat.get('offense', {})
                    defense = sample_stat.get('defense', {})
                    
                    print(f"     Offensive EPA: {offense.get('totalEPA', 'N/A')}")
                    print(f"     Success Rate: {offense.get('successRate', 'N/A')}")
                    print(f"     Explosiveness: {offense.get('explosiveness', 'N/A')}")
                    print(f"     Defensive EPA: {defense.get('totalEPA', 'N/A')}")
                    print(f"     Havoc Rate: {defense.get('havocRate', 'N/A')}")
                
                # Save sample
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"advanced_stats_sample_{timestamp}.json"
                
                with open(filename, 'w') as f:
                    json.dump({
                        "test_concept": "CFB Advanced Stats Tool",
                        "endpoint": "/stats/game/advanced",
                        "sample_data": stats_data[:2],
                        "metrics_available": {
                            "offensive": list(offense.keys()) if offense else [],
                            "defensive": list(defense.keys()) if defense else []
                        }
                    }, indent=2)
                
                print(f"   Sample saved to: {filename}")
                
            else:
                print(f"❌ HTTP Error: {response.status_code}")
        
        # Proposed implementation
        print(f"\n📋 PROPOSED TOOL IMPLEMENTATION:")
        print("-" * 30)
        
        proposed_tool = {
            "name": "getCFBAdvancedStats",
            "description": "Get advanced team statistics (EPA, success rate, explosiveness, havoc)",
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "Season year"},
                    "week": {"type": "integer", "description": "Week number", "optional": True},
                    "team": {"type": "string", "description": "Team name", "optional": True},
                    "conference": {"type": "string", "description": "Conference name", "optional": True},
                    "gameId": {"type": "integer", "description": "Specific game ID", "optional": True}
                },
                "required": ["year"]
            },
            "usefulness": "VERY HIGH",
            "rationale": "Modern analytics essential for accurate team evaluation and predictions"
        }
        
        print(json.dumps(proposed_tool, indent=2))
        
        print(f"\n💡 KEY METRICS PROVIDED:")
        print("   • EPA (Expected Points Added)")
        print("   • Success Rate")
        print("   • Explosiveness")
        print("   • Havoc Rate")
        print("   • Line Yards")
        print("   • Second Level Yards")
        print("   • Open Field Yards")
        
    except Exception as e:
        print(f"❌ Error testing advanced stats: {e}")

async def main():
    """Test highest priority missing tools"""
    
    print("🚀 CFB MCP - HIGH PRIORITY MISSING TOOLS TEST")
    print("=" * 60)
    print("Testing concepts for the most important missing tools")
    print()
    
    await test_betting_lines_concept()
    await test_advanced_stats_concept()
    
    print(f"\n📊 PRIORITY IMPLEMENTATION SUMMARY")
    print("=" * 60)
    print("🔥 VERY HIGH PRIORITY:")
    print("  1. getCFBBettingLines - Essential for betting analysis")
    print("  2. getCFBAdvancedStats - Modern analytics for predictions")
    print("  3. getCFBInjuries - Critical for accurate game analysis")
    print()
    print("⭐ HIGH PRIORITY:")
    print("  4. getCFBCoaches - Coaching impact on performance")
    print("  5. getCFBRecruits - Future team strength indicator")
    print("  6. getCFBTransferPortal - Modern roster composition factor")
    print("  7. getCFBTeamTalent - Objective talent measurement")
    print()
    print("📈 MEDIUM-HIGH PRIORITY:")
    print("  8. getCFBWeather - Game condition impacts")
    print()
    print("📊 MEDIUM PRIORITY:")
    print("  9. getCFBVenues - Stadium context")
    print("  10. getCFBDriveStats - Granular efficiency metrics")

if __name__ == "__main__":
    asyncio.run(main())