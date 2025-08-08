#!/usr/bin/env python3
"""
MCP debugging utility for testing logging and troubleshooting MCP calls.

This utility provides debugging features for MCP server interactions:
- Test MCP server connectivity
- Log detailed request/response information
- Measure response times
- Test error handling scenarios
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from typing import Dict, Any, Optional

from core_mcp import (
    scoreboard, teams, game_summary, analyze_game_strict, probe_league_support,
    MCPError, LEAGUE_MAPPING
)
from logging_config import setup_logging, get_mcp_logger

# Configure logging
logger = logging.getLogger(__name__)
mcp_logger = get_mcp_logger(__name__)


async def test_connectivity() -> bool:
    """
    Test basic MCP server connectivity.
    
    Returns:
        True if server is reachable, False otherwise
    """
    logger.info("Testing MCP server connectivity...")
    
    try:
        # Try a simple probe operation
        result = await probe_league_support('nfl')
        logger.info("✅ MCP server connectivity test passed")
        return True
    except Exception as e:
        logger.error(f"❌ MCP server connectivity test failed: {e}")
        return False


async def test_scoreboard_timing(league: str, date: Optional[str] = None) -> Dict[str, Any]:
    """
    Test scoreboard operation with detailed timing.
    
    Args:
        league: League to test
        date: Optional date
        
    Returns:
        Test results with timing information
    """
    logger.info(f"Testing scoreboard timing for {league}" + (f" on {date}" if date else ""))
    
    start_time = time.time()
    
    try:
        result = await scoreboard(league, date)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Extract event count
        events = result.get('data', {}).get('scoreboard', {}).get('events', [])
        event_count = len(events)
        
        # Extract ESPN URL
        espn_url = result.get('meta', {}).get('url', 'N/A')
        
        test_result = {
            'success': True,
            'response_time_ms': round(response_time, 2),
            'event_count': event_count,
            'espn_url': espn_url,
            'league': league,
            'date': date
        }
        
        logger.info(f"✅ Scoreboard test completed: {response_time:.2f}ms, {event_count} events")
        return test_result
        
    except Exception as e:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        test_result = {
            'success': False,
            'response_time_ms': round(response_time, 2),
            'error': str(e),
            'error_type': type(e).__name__,
            'league': league,
            'date': date
        }
        
        logger.error(f"❌ Scoreboard test failed: {e}")
        return test_result


async def test_game_summary_timing(league: str, event_id: str) -> Dict[str, Any]:
    """
    Test game summary operation with detailed timing.
    
    Args:
        league: League to test
        event_id: Event ID to test
        
    Returns:
        Test results with timing information
    """
    logger.info(f"Testing game summary timing for {league} event {event_id}")
    
    start_time = time.time()
    
    try:
        result = await game_summary(league, event_id)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        # Extract basic game info
        summary = result.get('data', {}).get('summary', {})
        status = summary.get('status', 'N/A')
        
        # Extract ESPN URL
        espn_url = result.get('meta', {}).get('url', 'N/A')
        
        test_result = {
            'success': True,
            'response_time_ms': round(response_time, 2),
            'game_status': status,
            'espn_url': espn_url,
            'league': league,
            'event_id': event_id
        }
        
        logger.info(f"✅ Game summary test completed: {response_time:.2f}ms, status: {status}")
        return test_result
        
    except Exception as e:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        test_result = {
            'success': False,
            'response_time_ms': round(response_time, 2),
            'error': str(e),
            'error_type': type(e).__name__,
            'league': league,
            'event_id': event_id
        }
        
        logger.error(f"❌ Game summary test failed: {e}")
        return test_result


async def run_comprehensive_test(league: str) -> Dict[str, Any]:
    """
    Run comprehensive test suite for a league.
    
    Args:
        league: League to test
        
    Returns:
        Comprehensive test results
    """
    logger.info(f"Running comprehensive test suite for {league}")
    
    results = {
        'league': league,
        'tests': {},
        'summary': {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'total_time_ms': 0
        }
    }
    
    suite_start = time.time()
    
    # Test 1: Probe league support
    logger.info("Test 1: Probe league support")
    try:
        probe_result = await probe_league_support(league)
        results['tests']['probe_support'] = {
            'success': True,
            'supported': probe_result.get('data', {}).get('supported', False)
        }
        results['summary']['passed'] += 1
    except Exception as e:
        results['tests']['probe_support'] = {
            'success': False,
            'error': str(e)
        }
        results['summary']['failed'] += 1
    results['summary']['total_tests'] += 1
    
    # Test 2: Get teams
    logger.info("Test 2: Get teams")
    try:
        teams_result = await teams(league)
        team_count = len(teams_result.get('data', {}).get('teams', []))
        results['tests']['teams'] = {
            'success': True,
            'team_count': team_count
        }
        results['summary']['passed'] += 1
    except Exception as e:
        results['tests']['teams'] = {
            'success': False,
            'error': str(e)
        }
        results['summary']['failed'] += 1
    results['summary']['total_tests'] += 1
    
    # Test 3: Get scoreboard
    logger.info("Test 3: Get scoreboard")
    scoreboard_result = await test_scoreboard_timing(league)
    results['tests']['scoreboard'] = scoreboard_result
    if scoreboard_result['success']:
        results['summary']['passed'] += 1
    else:
        results['summary']['failed'] += 1
    results['summary']['total_tests'] += 1
    
    suite_end = time.time()
    results['summary']['total_time_ms'] = round((suite_end - suite_start) * 1000, 2)
    
    logger.info(f"Comprehensive test completed: {results['summary']['passed']}/{results['summary']['total_tests']} passed")
    
    return results


def print_test_results(results: Dict[str, Any]) -> None:
    """
    Print formatted test results.
    
    Args:
        results: Test results dictionary
    """
    print(f"\n{'='*60}")
    print(f"MCP Test Results for {results['league'].upper()}")
    print(f"{'='*60}")
    
    for test_name, test_result in results['tests'].items():
        status = "✅ PASS" if test_result['success'] else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        if test_result['success']:
            if 'response_time_ms' in test_result:
                print(f"  Response time: {test_result['response_time_ms']}ms")
            if 'event_count' in test_result:
                print(f"  Events found: {test_result['event_count']}")
            if 'team_count' in test_result:
                print(f"  Teams found: {test_result['team_count']}")
            if 'espn_url' in test_result:
                print(f"  ESPN URL: {test_result['espn_url']}")
        else:
            print(f"  Error: {test_result['error']}")
    
    print(f"\nSummary: {results['summary']['passed']}/{results['summary']['total_tests']} tests passed")
    print(f"Total time: {results['summary']['total_time_ms']}ms")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='MCP debugging and testing utility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Supported leagues:
  {', '.join(sorted(LEAGUE_MAPPING.keys()))}

Examples:
  %(prog)s connectivity                 # Test MCP server connectivity
  %(prog)s scoreboard nfl              # Test NFL scoreboard timing
  %(prog)s game nfl 401547439          # Test specific game summary
  %(prog)s comprehensive nfl           # Run full test suite for NFL

Environment variables:
  LOG_LEVEL=DEBUG                      # Enable debug logging with ESPN URLs
  LOG_FORMAT=json                      # Output structured JSON logs
        """
    )
    
    parser.add_argument(
        'command',
        choices=['connectivity', 'scoreboard', 'game', 'comprehensive'],
        help='Test command to execute'
    )
    
    parser.add_argument(
        'league',
        nargs='?',
        help='League code (required for most commands)'
    )
    
    parser.add_argument(
        'event_id',
        nargs='?',
        help='Event ID (required for game command)'
    )
    
    parser.add_argument(
        '--date',
        help='Date in YYYYMMDD format (for scoreboard test)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Set logging level'
    )
    
    parser.add_argument(
        '--log-format',
        choices=['text', 'json'],
        help='Set log format'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level=args.log_level, log_format=args.log_format)
    
    # Validate arguments
    if args.command != 'connectivity' and not args.league:
        print("❌ Error: League is required for this command", file=sys.stderr)
        sys.exit(1)
    
    if args.command == 'game' and not args.event_id:
        print("❌ Error: Event ID is required for game command", file=sys.stderr)
        sys.exit(1)
    
    if args.league and args.league not in LEAGUE_MAPPING:
        supported = ', '.join(sorted(LEAGUE_MAPPING.keys()))
        print(f"❌ Error: Unsupported league '{args.league}'. Supported: {supported}", file=sys.stderr)
        sys.exit(1)
    
    # Run the appropriate test
    try:
        if args.command == 'connectivity':
            result = asyncio.run(test_connectivity())
            if args.json:
                print(json.dumps({'connectivity': result}, indent=2))
            else:
                print("✅ Connectivity test passed" if result else "❌ Connectivity test failed")
        
        elif args.command == 'scoreboard':
            result = asyncio.run(test_scoreboard_timing(args.league, args.date))
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                status = "✅ PASS" if result['success'] else "❌ FAIL"
                print(f"Scoreboard test: {status}")
                print(f"Response time: {result['response_time_ms']}ms")
                if result['success']:
                    print(f"Events found: {result['event_count']}")
                    print(f"ESPN URL: {result['espn_url']}")
                else:
                    print(f"Error: {result['error']}")
        
        elif args.command == 'game':
            result = asyncio.run(test_game_summary_timing(args.league, args.event_id))
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                status = "✅ PASS" if result['success'] else "❌ FAIL"
                print(f"Game summary test: {status}")
                print(f"Response time: {result['response_time_ms']}ms")
                if result['success']:
                    print(f"Game status: {result['game_status']}")
                    print(f"ESPN URL: {result['espn_url']}")
                else:
                    print(f"Error: {result['error']}")
        
        elif args.command == 'comprehensive':
            result = asyncio.run(run_comprehensive_test(args.league))
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print_test_results(result)
    
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()