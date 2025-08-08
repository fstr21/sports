#!/usr/bin/env python3
"""
Season CLI client for team and player season statistics.

This client provides access to team and player season stats across all supported leagues.
Note: Most season stats return "supported:false" as per MCP server design since ESPN
JSON endpoints don't provide comprehensive season statistics.
"""

import argparse
import asyncio
import json
import logging
import sys
from typing import Dict, Any, Optional

from core_mcp import (
    team_season_stats,
    player_season_stats,
    MCPError,
    MCPServerError,
    MCPValidationError,
    LEAGUE_MAPPING
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def format_season_response(data: Dict[str, Any], data_type: str) -> str:
    """
    Format season stats response for display.
    
    Args:
        data: MCP response data
        data_type: Type of data ('team' or 'player')
        
    Returns:
        Formatted string for display
    """
    # Check if this is a supported:false response
    if isinstance(data, dict) and data.get('supported') is False:
        reason = data.get('reason', 'Season stats not available via ESPN JSON endpoints')
        return f"❌ Season stats not supported: {reason}"
    
    # Check if we have actual season data
    if isinstance(data, dict) and 'content' in data:
        content = data['content']
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            return json.dumps(content, indent=2)
    
    # Check for structured season data
    if isinstance(data, dict) and 'data' in data:
        season_data = data['data']
        if season_data:
            return json.dumps(season_data, indent=2)
    
    # Fallback to raw data display
    return json.dumps(data, indent=2)

async def get_team_season(league: str, team_id: str, season: Optional[str] = None, 
                         output_json: bool = False) -> None:
    """
    Get team season statistics.
    
    Args:
        league: League key (e.g., 'nfl', 'nba')
        team_id: Team ID
        season: Optional season
        output_json: Whether to output raw JSON
    """
    try:
        logger.info(f"Fetching team season stats for {league} team {team_id}")
        
        data = await team_season_stats(league, team_id, season)
        
        if output_json:
            print(json.dumps(data, indent=2))
        else:
            print(f"\n🏈 Team Season Stats: {league.upper()} Team {team_id}")
            if season:
                print(f"Season: {season}")
            print("-" * 50)
            print(format_season_response(data, 'team'))
            
    except MCPValidationError as e:
        print(f"❌ Validation Error: {e}")
        sys.exit(1)
    except MCPServerError as e:
        print(f"❌ Server Error: {e}")
        sys.exit(1)
    except MCPError as e:
        print(f"❌ MCP Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

async def get_player_season(league: str, player_id: str, season: Optional[str] = None,
                           output_json: bool = False) -> None:
    """
    Get player season statistics.
    
    Args:
        league: League key (e.g., 'nfl', 'nba')
        player_id: Player ID
        season: Optional season
        output_json: Whether to output raw JSON
    """
    try:
        logger.info(f"Fetching player season stats for {league} player {player_id}")
        
        data = await player_season_stats(league, player_id, season)
        
        if output_json:
            print(json.dumps(data, indent=2))
        else:
            print(f"\n👤 Player Season Stats: {league.upper()} Player {player_id}")
            if season:
                print(f"Season: {season}")
            print("-" * 50)
            print(format_season_response(data, 'player'))
            
    except MCPValidationError as e:
        print(f"❌ Validation Error: {e}")
        sys.exit(1)
    except MCPServerError as e:
        print(f"❌ Server Error: {e}")
        sys.exit(1)
    except MCPError as e:
        print(f"❌ MCP Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description='Season CLI - Team and Player Season Statistics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s team-season nfl 1 --season 2024
  %(prog)s player-season nba 123456 --json
  %(prog)s team-season mlb 2 --season 2023

Supported leagues: {', '.join(sorted(LEAGUE_MAPPING.keys()))}

Note: Most season stats return "supported:false" since ESPN JSON endpoints
don't provide comprehensive season statistics.
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Team season command
    team_parser = subparsers.add_parser('team-season', help='Get team season statistics')
    team_parser.add_argument('league', help='League key (e.g., nfl, nba, mlb)')
    team_parser.add_argument('team_id', help='Team ID')
    team_parser.add_argument('--season', help='Season (optional)')
    team_parser.add_argument('--json', action='store_true', help='Output raw JSON')
    
    # Player season command
    player_parser = subparsers.add_parser('player-season', help='Get player season statistics')
    player_parser.add_argument('league', help='League key (e.g., nfl, nba, mlb)')
    player_parser.add_argument('player_id', help='Player ID')
    player_parser.add_argument('--season', help='Season (optional)')
    player_parser.add_argument('--json', action='store_true', help='Output raw JSON')
    
    return parser

async def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'team-season':
            await get_team_season(args.league, args.team_id, args.season, args.json)
        elif args.command == 'player-season':
            await get_player_season(args.league, args.player_id, args.season, args.json)
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())