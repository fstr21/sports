#!/usr/bin/env python3
"""
Scoreboard CLI client for sports data.

This client provides scoreboard functionality organized by data type rather than sport.
It works with all supported leagues through the MCP server integration.
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

from core_mcp import scoreboard, MCPError, LEAGUE_MAPPING
from logging_config import setup_logging, get_mcp_logger

# Configure logging
logger = logging.getLogger(__name__)
mcp_logger = get_mcp_logger(__name__)


def format_event_table(events: List[Dict[str, Any]]) -> str:
    """
    Format events data into a readable table.
    
    Args:
        events: List of event dictionaries from MCP response
        
    Returns:
        Formatted table string
    """
    if not events:
        return "No events found."
    
    # Table headers
    headers = ["EVENT_ID", "AWAY @ HOME", "STATUS", "DATE"]
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    
    # Prepare rows and calculate max widths
    rows = []
    for event in events:
        event_id = str(event.get('event_id', 'N/A'))
        
        # Format teams
        away = event.get('away', {})
        home = event.get('home', {})
        away_name = away.get('abbrev', away.get('displayName', 'N/A'))
        home_name = home.get('abbrev', home.get('displayName', 'N/A'))
        
        # Add scores if available
        away_score = away.get('score', '')
        home_score = home.get('score', '')
        if away_score and home_score:
            teams = f"{away_name} {away_score} @ {home_name} {home_score}"
        else:
            teams = f"{away_name} @ {home_name}"
        
        status = event.get('status', 'N/A')
        
        # Format date
        date_str = event.get('date', 'N/A')
        if date_str != 'N/A':
            try:
                # Parse ISO format and convert to readable format
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date_formatted = dt.strftime('%Y-%m-%d %H:%M')
            except:
                date_formatted = date_str
        else:
            date_formatted = 'N/A'
        
        row = [event_id, teams, status, date_formatted]
        rows.append(row)
        
        # Update column widths
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))
    
    # Build table
    lines = []
    
    # Header row
    header_row = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    lines.append(header_row)
    
    # Separator
    separator = "-+-".join("-" * w for w in col_widths)
    lines.append(separator)
    
    # Data rows
    for row in rows:
        data_row = " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row))
        lines.append(data_row)
    
    return "\n".join(lines)


def format_json_output(response: Dict[str, Any]) -> str:
    """
    Format response as pretty JSON.
    
    Args:
        response: MCP response data
        
    Returns:
        Pretty-printed JSON string
    """
    return json.dumps(response, indent=2, ensure_ascii=False)


async def get_events(league: str, date: Optional[str] = None, output_format: str = 'pretty') -> None:
    """
    Get and display events for a league and date.
    
    Args:
        league: League key (e.g., 'nfl', 'nba')
        date: Optional date in YYYYMMDD format
        output_format: Output format ('pretty', 'json')
    """
    logger.info(f"Fetching {league} events" + (f" for {date}" if date else ""))
    
    try:
        # Call MCP scoreboard function
        response = await scoreboard(league, date)
        
        if output_format == 'json':
            print(format_json_output(response))
            return
        
        # Extract events from response
        scoreboard_data = response.get('data', {}).get('scoreboard', {})
        events = scoreboard_data.get('events', [])
        
        if not events:
            logger.info(f"No events found for {league}" + (f" on {date}" if date else ""))
            print(f"No events found for {league.upper()}" + (f" on {date}" if date else ""))
            return
        
        logger.info(f"Found {len(events)} events for {league}" + (f" on {date}" if date else ""))
        
        # Display formatted table
        print(f"\n{league.upper()} Events" + (f" - {date}" if date else ""))
        print("=" * 50)
        print(format_event_table(events))
        
        # Show metadata if available
        meta = response.get('meta', {})
        if meta:
            print(f"\nSource: {meta.get('url', 'N/A')}")
            logger.debug(f"ESPN source URL: {meta.get('url', 'N/A')}")
        
    except MCPError as e:
        logger.error(f"MCP error fetching {league} events: {e}")
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error fetching {league} events: {e}", exc_info=True)
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def validate_date(date_str: str) -> bool:
    """
    Validate date format (YYYYMMDD).
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if len(date_str) != 8:
        return False
    
    try:
        datetime.strptime(date_str, '%Y%m%d')
        return True
    except ValueError:
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Get scoreboard events for any supported league',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Supported leagues:
  {', '.join(sorted(LEAGUE_MAPPING.keys()))}

Examples:
  %(prog)s events nfl                    # Current NFL events
  %(prog)s events nba 20240315          # NBA events for March 15, 2024
  %(prog)s events nfl --json            # Raw JSON output
  %(prog)s events mlb --pretty          # Pretty table output (default)

Environment variables:
  LOG_LEVEL=DEBUG                       # Enable debug logging with ESPN URLs
  LOG_FORMAT=json                       # Output structured JSON logs
        """
    )
    
    parser.add_argument(
        'command',
        choices=['events'],
        help='Command to execute'
    )
    
    parser.add_argument(
        'league',
        help='League code (e.g., nfl, nba, mlb)'
    )
    
    parser.add_argument(
        'date',
        nargs='?',
        help='Date in YYYYMMDD format (optional)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output raw JSON from MCP server'
    )
    
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Output formatted table (default)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Set logging level (overrides LOG_LEVEL env var)'
    )
    
    parser.add_argument(
        '--log-format',
        choices=['text', 'json'],
        help='Set log format (overrides LOG_FORMAT env var)'
    )
    
    args = parser.parse_args()
    
    # Setup logging with CLI overrides
    setup_logging(level=args.log_level, log_format=args.log_format)
    
    # Validate league
    if args.league not in LEAGUE_MAPPING:
        supported = ', '.join(sorted(LEAGUE_MAPPING.keys()))
        print(f"❌ Error: Unsupported league '{args.league}'. Supported: {supported}", file=sys.stderr)
        sys.exit(1)
    
    # Validate date if provided
    if args.date and not validate_date(args.date):
        print(f"❌ Error: Invalid date format '{args.date}'. Use YYYYMMDD format.", file=sys.stderr)
        sys.exit(1)
    
    # Determine output format
    output_format = 'json' if args.json else 'pretty'
    
    # Run async function
    try:
        asyncio.run(get_events(args.league, args.date, output_format))
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()