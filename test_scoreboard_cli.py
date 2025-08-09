#!/usr/bin/env python3
"""
Test script for scoreboard CLI functionality without MCP dependencies.
"""

import asyncio
import sys
from typing import Dict, Any, Optional

# Mock the core_mcp functions for testing
class MockMCPError(Exception):
    pass

async def mock_scoreboard(league: str, date: Optional[str] = None) -> Dict[str, Any]:
    """Mock scoreboard function that returns sample data."""
    
    # Simulate some validation
    valid_leagues = ['nfl', 'nba', 'mlb', 'nhl', 'wnba', 'ncaaf', 'ncaab', 'mls', 'epl', 'laliga']
    if league not in valid_leagues:
        raise MockMCPError(f"Unsupported league '{league}'. Supported: {', '.join(valid_leagues)}")
    
    # Return mock data
    return {
        "ok": True,
        "data": {
            "scoreboard": {
                "events": [
                    {
                        "event_id": "401547439",
                        "away": {
                            "abbrev": "BUF",
                            "displayName": "Buffalo Bills",
                            "score": "21"
                        },
                        "home": {
                            "abbrev": "MIA",
                            "displayName": "Miami Dolphins", 
                            "score": "14"
                        },
                        "status": "Final",
                        "date": "2024-01-15T18:00:00Z"
                    },
                    {
                        "event_id": "401547440",
                        "away": {
                            "abbrev": "KC",
                            "displayName": "Kansas City Chiefs",
                            "score": ""
                        },
                        "home": {
                            "abbrev": "LV",
                            "displayName": "Las Vegas Raiders",
                            "score": ""
                        },
                        "status": "Scheduled",
                        "date": "2024-01-15T21:00:00Z"
                    }
                ]
            }
        },
        "meta": {
            "url": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        }
    }

# Import the CLI functions and replace the core_mcp import
sys.path.append('clients')

# Monkey patch the import
import clients.scoreboard_cli as cli_module
cli_module.scoreboard = mock_scoreboard
cli_module.MCPError = MockMCPError

async def test_basic_functionality():
    """Test basic CLI functionality."""
    print("Testing scoreboard CLI functionality...")
    
    # Test 1: Valid league, pretty format
    print("\n1. Testing NFL events (pretty format):")
    try:
        await cli_module.get_events('nfl', None, 'pretty')
        print("✅ Pretty format test passed")
    except Exception as e:
        print(f"❌ Pretty format test failed: {e}")
    
    # Test 2: Valid league, JSON format  
    print("\n2. Testing NFL events (JSON format):")
    try:
        await cli_module.get_events('nfl', None, 'json')
        print("✅ JSON format test passed")
    except Exception as e:
        print(f"❌ JSON format test failed: {e}")
    
    # Test 3: Invalid league
    print("\n3. Testing invalid league:")
    try:
        await cli_module.get_events('invalid', None, 'pretty')
        print("❌ Invalid league test failed - should have thrown error")
    except MockMCPError as e:
        print(f"✅ Invalid league test passed - caught error: {e}")
    except Exception as e:
        print(f"❌ Invalid league test failed with unexpected error: {e}")
    
    # Test 4: Date validation
    print("\n4. Testing date validation:")
    valid_date = cli_module.validate_date('20240115')
    invalid_date = cli_module.validate_date('invalid')
    
    if valid_date and not invalid_date:
        print("✅ Date validation test passed")
    else:
        print(f"❌ Date validation test failed - valid: {valid_date}, invalid: {invalid_date}")
    
    # Test 5: Table formatting
    print("\n5. Testing table formatting:")
    mock_events = [
        {
            "event_id": "123",
            "away": {"abbrev": "BUF", "score": "21"},
            "home": {"abbrev": "MIA", "score": "14"},
            "status": "Final",
            "date": "2024-01-15T18:00:00Z"
        }
    ]
    
    try:
        table = cli_module.format_event_table(mock_events)
        if "BUF 21 @ MIA 14" in table and "Final" in table:
            print("✅ Table formatting test passed")
        else:
            print(f"❌ Table formatting test failed - output: {table}")
    except Exception as e:
        print(f"❌ Table formatting test failed: {e}")

if __name__ == '__main__':
    asyncio.run(test_basic_functionality())