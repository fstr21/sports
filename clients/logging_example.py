#!/usr/bin/env python3
"""
Example script demonstrating MCP logging functionality.

This script shows how to use the structured logging system with different
verbosity levels and formats.
"""

import asyncio
import os
import sys

from core_mcp import scoreboard, game_summary, MCPError
from logging_config import setup_logging


async def demo_logging_levels():
    """Demonstrate different logging levels."""
    print("=== MCP Logging Demo ===\n")
    
    # Demo 1: INFO level logging
    print("1. INFO Level Logging (default)")
    print("Shows: league/date/event and OK/ERR status with timing")
    print("Command: LOG_LEVEL=INFO python logging_example.py")
    print("-" * 50)
    
    setup_logging(level='INFO')
    
    try:
        result = await scoreboard('nfl')
        print("✅ NFL scoreboard request completed")
    except MCPError as e:
        print(f"❌ NFL scoreboard request failed: {e}")
    
    print("\n")
    
    # Demo 2: DEBUG level logging
    print("2. DEBUG Level Logging")
    print("Shows: Full ESPN URLs, timing, and detailed MCP responses")
    print("Command: LOG_LEVEL=DEBUG python logging_example.py")
    print("-" * 50)
    
    setup_logging(level='DEBUG')
    
    try:
        result = await scoreboard('nba')
        print("✅ NBA scoreboard request completed")
    except MCPError as e:
        print(f"❌ NBA scoreboard request failed: {e}")
    
    print("\n")
    
    # Demo 3: JSON format logging
    print("3. JSON Format Logging")
    print("Shows: Structured JSON logs for log aggregation")
    print("Command: LOG_FORMAT=json LOG_LEVEL=INFO python logging_example.py")
    print("-" * 50)
    
    setup_logging(level='INFO', log_format='json')
    
    try:
        result = await scoreboard('mlb')
        print("✅ MLB scoreboard request completed")
    except MCPError as e:
        print(f"❌ MLB scoreboard request failed: {e}")


async def demo_error_logging():
    """Demonstrate error logging."""
    print("\n=== Error Logging Demo ===\n")
    
    setup_logging(level='DEBUG')
    
    # Try an invalid league to trigger error logging
    try:
        result = await scoreboard('invalid_league')
    except MCPError as e:
        print(f"✅ Error logging demonstrated: {e}")
    
    # Try an invalid event ID to trigger error logging
    try:
        result = await game_summary('nfl', 'invalid_event_id')
    except MCPError as e:
        print(f"✅ Error logging demonstrated: {e}")


def main():
    """Main demo function."""
    print("MCP Logging System Demonstration")
    print("=" * 40)
    print()
    
    # Check if specific demo is requested
    if len(sys.argv) > 1:
        demo_type = sys.argv[1]
        
        if demo_type == 'info':
            setup_logging(level='INFO')
            asyncio.run(demo_logging_levels())
        elif demo_type == 'debug':
            setup_logging(level='DEBUG')
            asyncio.run(demo_logging_levels())
        elif demo_type == 'json':
            setup_logging(level='INFO', log_format='json')
            asyncio.run(demo_logging_levels())
        elif demo_type == 'errors':
            asyncio.run(demo_error_logging())
        else:
            print(f"Unknown demo type: {demo_type}")
            print("Available demos: info, debug, json, errors")
            sys.exit(1)
    else:
        # Run all demos
        asyncio.run(demo_logging_levels())
        asyncio.run(demo_error_logging())
    
    print("\n=== Demo Complete ===")
    print("\nTo test different logging configurations:")
    print("LOG_LEVEL=DEBUG python logging_example.py")
    print("LOG_FORMAT=json LOG_LEVEL=INFO python logging_example.py")
    print("LOG_LEVEL=WARNING python logging_example.py  # Minimal output")


if __name__ == '__main__':
    main()