#!/usr/bin/env python3
"""
Debug script to test Sports AI MCP consistency.
Calls the Sports AI MCP multiple times to see data variation.
"""

import os
import sys
import json
import asyncio
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append('mcp')

from dotenv import load_dotenv
from sports_ai_mcp import analyze_wnba_games

# Load environment variables
load_dotenv('.env.local')

async def test_sports_ai_consistency():
    """Test Sports AI MCP multiple times to check for consistency."""
    
    print("=" * 80)
    print("Sports AI MCP Consistency Test")
    print("=" * 80)
    
    results = []
    
    for i in range(5):  # Run 5 tests
        print(f"\n--- Test {i+1}/5 ---")
        start_time = time.time()
        
        try:
            result = await analyze_wnba_games({})
            end_time = time.time()
            
            print(f"Response time: {end_time - start_time:.2f} seconds")
            print(f"Result type: {type(result)}")
            print(f"Result length: {len(str(result))}")
            
            # Parse the result
            if isinstance(result, str):
                try:
                    parsed = json.loads(result)
                    print(f"Parsed successfully: {type(parsed)}")
                    
                    # Look for game information
                    if isinstance(parsed, dict):
                        if 'games' in parsed:
                            games = parsed['games']
                            print(f"Found {len(games)} games")
                            for j, game in enumerate(games):
                                if isinstance(game, dict):
                                    home = game.get('home_team', 'Unknown')
                                    away = game.get('away_team', 'Unknown')
                                    print(f"  Game {j+1}: {away} at {home}")
                        elif 'analysis' in parsed:
                            print("Found analysis section")
                            analysis = str(parsed['analysis'])[:200] + "..."
                            print(f"Analysis preview: {analysis}")
                        else:
                            print(f"Top-level keys: {list(parsed.keys())}")
                    
                    results.append({
                        'test': i+1,
                        'success': True,
                        'data': parsed,
                        'response_time': end_time - start_time
                    })
                    
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Raw result preview: {str(result)[:500]}...")
                    results.append({
                        'test': i+1,
                        'success': False,
                        'error': 'JSON decode error',
                        'raw_preview': str(result)[:500]
                    })
            else:
                print(f"Non-string result: {result}")
                results.append({
                    'test': i+1,
                    'success': False,
                    'error': 'Non-string result',
                    'result': result
                })
                
        except Exception as e:
            end_time = time.time()
            print(f"Error: {str(e)}")
            results.append({
                'test': i+1,
                'success': False,
                'error': str(e),
                'response_time': end_time - start_time
            })
        
        # Wait between tests
        if i < 4:
            print("Waiting 2 seconds...")
            await asyncio.sleep(2)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"Successful tests: {len(successful_tests)}/5")
    print(f"Failed tests: {len(failed_tests)}/5")
    
    if successful_tests:
        avg_time = sum(r['response_time'] for r in successful_tests) / len(successful_tests)
        print(f"Average response time: {avg_time:.2f} seconds")
        
        # Check for data consistency
        print("\nData consistency check:")
        if len(successful_tests) > 1:
            first_data = successful_tests[0]['data']
            consistent = True
            for test in successful_tests[1:]:
                if test['data'] != first_data:
                    consistent = False
                    break
            
            if consistent:
                print("✅ All successful tests returned identical data")
            else:
                print("❌ Tests returned different data - INCONSISTENCY DETECTED")
                
                # Show differences
                for i, test in enumerate(successful_tests):
                    print(f"\nTest {test['test']} data structure:")
                    if isinstance(test['data'], dict):
                        print(f"  Keys: {list(test['data'].keys())}")
                    else:
                        print(f"  Type: {type(test['data'])}")
        else:
            print("Only one successful test - cannot check consistency")
    
    if failed_tests:
        print(f"\nFailed test errors:")
        for test in failed_tests:
            print(f"  Test {test['test']}: {test['error']}")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"test/logs/sports_ai_debug_{timestamp}.json"
    
    os.makedirs("test/logs", exist_ok=True)
    with open(log_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: {log_file}")

if __name__ == "__main__":
    asyncio.run(test_sports_ai_consistency())