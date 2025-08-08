#!/usr/bin/env python3
"""
Game CLI client for sports data.

This client provides game summary functionality for all supported sports
using the MCP server. It supports raw JSON output and will be extended
with adapter integration and natural language queries.
"""

import argparse
import asyncio
import json
import logging
import sys
from typing import Any, Dict, Optional

from core_mcp import game_summary, MCPError, MCPServerError, MCPValidationError
from core_llm import strict_answer, LLMError, LLMConfigurationError, LLMAPIError

# Import sport adapters
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'adapters'))
    
    import nfl
    import nba
    import wnba
    import mlb
    import nhl
    import soccer
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Could not import adapters: {e}. Adapter functionality will be disabled.")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# League to adapter mapping
LEAGUE_ADAPTERS = {
    'nfl': nfl,
    'ncaaf': nfl,  # College football uses same stats as NFL
    'nba': nba,
    'wnba': wnba,
    'ncaab': nba,  # College basketball uses same stats as NBA
    'mlb': mlb,
    'nhl': nhl,
    'mls': soccer,
    'epl': soccer,
    'laliga': soccer
}

def get_adapter_for_league(league: str):
    """
    Get the appropriate adapter for a league.
    
    Args:
        league: League key
        
    Returns:
        Adapter module or None if not available
    """
    return LEAGUE_ADAPTERS.get(league.lower())

def apply_adapter_normalization(data: Dict[str, Any], league: str) -> Dict[str, Any]:
    """
    Apply sport-specific adapter normalization to MCP response data.
    
    Args:
        data: Raw MCP response data
        league: League key
        
    Returns:
        Normalized data or original data if adapter fails
    """
    try:
        adapter = get_adapter_for_league(league)
        if not adapter:
            logger.debug(f"No adapter available for league {league}")
            return data
        
        if not hasattr(adapter, 'normalize'):
            logger.warning(f"Adapter for {league} missing normalize function")
            return data
        
        logger.debug(f"Applying {league} adapter normalization")
        normalized = adapter.normalize(data)
        
        if normalized.get('error'):
            logger.warning(f"Adapter normalization failed: {normalized['error']}")
            return data
        
        return normalized
        
    except Exception as e:
        logger.warning(f"Adapter normalization failed for {league}: {e}")
        return data

def filter_fields(data: Dict[str, Any], fields: list, league: str) -> Dict[str, Any]:
    """
    Filter normalized data to only include specified fields.
    
    Args:
        data: Normalized data from adapter
        fields: List of field names to include
        league: League key for context
        
    Returns:
        Filtered data with only specified fields
    """
    try:
        if not fields:
            return data
        
        # Convert fields to lowercase for case-insensitive matching
        fields_lower = [f.lower().strip() for f in fields]
        
        filtered_data = {}
        
        # Handle different data structures
        if 'players' in data:
            filtered_players = []
            for player in data['players']:
                filtered_player = {}
                # Always include name and team for context
                filtered_player['name'] = player.get('name', 'Unknown')
                filtered_player['team'] = player.get('team', 'Unknown')
                
                # Add requested fields
                for field in fields_lower:
                    if field in player:
                        filtered_player[field] = player[field]
                    else:
                        # Check for common field aliases
                        aliases = {
                            'points': 'pts',
                            'rebounds': 'reb',
                            'assists': 'ast',
                            'touchdowns': 'td',
                            'yards': 'yds'
                        }
                        alias_field = aliases.get(field)
                        if alias_field and alias_field in player:
                            filtered_player[field] = player[alias_field]
                        else:
                            filtered_player[field] = 'unavailable'
                
                filtered_players.append(filtered_player)
            
            filtered_data['players'] = filtered_players
        
        # Handle NFL-specific structure
        for category in ['passing', 'rushing', 'receiving']:
            if category in data:
                filtered_category = []
                for player in data[category]:
                    filtered_player = {}
                    # Always include name and team
                    filtered_player['name'] = player.get('name', 'Unknown')
                    filtered_player['team'] = player.get('team', 'Unknown')
                    
                    # Add requested fields
                    for field in fields_lower:
                        if field in player:
                            filtered_player[field] = player[field]
                        else:
                            filtered_player[field] = 'unavailable'
                    
                    filtered_category.append(filtered_player)
                
                filtered_data[category] = filtered_category
        
        return filtered_data if filtered_data else data
        
    except Exception as e:
        logger.warning(f"Field filtering failed: {e}")
        return data

def format_normalized_data(normalized_data: Dict[str, Any], league: str, fields: Optional[list] = None) -> str:
    """
    Format normalized adapter data for display with optional field filtering.
    
    Args:
        normalized_data: Data normalized by sport adapter
        league: League key
        fields: Optional list of fields to display
        
    Returns:
        Formatted string for display
    """
    try:
        # Apply field filtering if requested
        if fields:
            normalized_data = filter_fields(normalized_data, fields, league)
        
        output = []
        
        # Handle NFL data
        if league.lower() in ['nfl', 'ncaaf']:
            if 'passing' in normalized_data:
                output.append("PASSING STATS:")
                output.append("-" * 40)
                for player in normalized_data['passing']:
                    if fields:
                        # Custom field display
                        stats = []
                        for field in fields:
                            value = player.get(field.lower(), 'unavailable')
                            stats.append(f"{field}: {value}")
                        output.append(f"  {player['name']} ({player['team']}): {', '.join(stats)}")
                    else:
                        # Default display
                        output.append(f"  {player['name']} ({player['team']}): {player.get('completions_attempts', 'N/A')}, {player.get('yards', 'N/A')} yds, {player.get('touchdowns', 'N/A')} TD")
            
            if 'rushing' in normalized_data:
                if output:
                    output.append("")
                output.append("RUSHING STATS:")
                output.append("-" * 40)
                for player in normalized_data['rushing']:
                    if fields:
                        stats = []
                        for field in fields:
                            value = player.get(field.lower(), 'unavailable')
                            stats.append(f"{field}: {value}")
                        output.append(f"  {player['name']} ({player['team']}): {', '.join(stats)}")
                    else:
                        output.append(f"  {player['name']} ({player['team']}): {player.get('carries', 'N/A')} car, {player.get('yards', 'N/A')} yds, {player.get('touchdowns', 'N/A')} TD")
            
            if 'receiving' in normalized_data:
                if output:
                    output.append("")
                output.append("RECEIVING STATS:")
                output.append("-" * 40)
                for player in normalized_data['receiving']:
                    if fields:
                        stats = []
                        for field in fields:
                            value = player.get(field.lower(), 'unavailable')
                            stats.append(f"{field}: {value}")
                        output.append(f"  {player['name']} ({player['team']}): {', '.join(stats)}")
                    else:
                        output.append(f"  {player['name']} ({player['team']}): {player.get('receptions', 'N/A')} rec, {player.get('yards', 'N/A')} yds, {player.get('touchdowns', 'N/A')} TD")
        
        # Handle NBA/WNBA data
        elif league.lower() in ['nba', 'wnba', 'ncaab']:
            if 'players' in normalized_data:
                output.append("PLAYER STATS:")
                output.append("-" * 50)
                for player in normalized_data['players'][:15]:  # Show top 15 players
                    if fields:
                        stats = []
                        for field in fields:
                            value = player.get(field.lower(), 'unavailable')
                            stats.append(f"{field}: {value}")
                        output.append(f"  {player['name']} ({player['team']}): {', '.join(stats)}")
                    else:
                        output.append(f"  {player['name']} ({player['team']}): {player.get('pts', 'N/A')} pts, {player.get('reb', 'N/A')} reb, {player.get('ast', 'N/A')} ast")
        
        # Handle other sports (basic format)
        else:
            if 'players' in normalized_data:
                output.append("PLAYER STATS:")
                output.append("-" * 40)
                for player in normalized_data['players'][:15]:
                    if fields:
                        stats = []
                        for field in fields:
                            value = player.get(field.lower(), 'unavailable')
                            stats.append(f"{field}: {value}")
                        output.append(f"  {player['name']} ({player['team']}): {', '.join(stats)}")
                    else:
                        player_info = f"  {player.get('name', 'Unknown')} ({player.get('team', 'Unknown')})"
                        # Add key stats if available
                        key_stats = []
                        for key in ['pts', 'goals', 'assists', 'saves']:
                            if key in player and player[key] != 'N/A':
                                key_stats.append(f"{key}: {player[key]}")
                        if key_stats:
                            player_info += ": " + ", ".join(key_stats)
                        output.append(player_info)
        
        return "\n".join(output) if output else "No formatted stats available"
        
    except Exception as e:
        logger.error(f"Error formatting normalized data: {e}")
        return f"Error formatting normalized data: {e}"

def format_game_summary(data: Dict[str, Any], league: str, event_id: str, use_adapter: bool = True, fields: Optional[list] = None) -> str:
    """
    Format game summary data for human-readable display.
    
    Args:
        data: Game summary data from MCP server
        league: League key
        event_id: Event ID
        use_adapter: Whether to use sport-specific adapter formatting
        
    Returns:
        Formatted string for display
    """
    try:
        # Extract basic game info
        summary = data.get('data', {}).get('summary', {})
        if not summary:
            return f"No game summary data available for {league} event {event_id}"
        
        # Get game status and teams
        status = summary.get('status', 'Unknown')
        teams_meta = summary.get('teams_meta', [])
        
        output = []
        output.append(f"Game Summary - {league.upper()} Event {event_id}")
        output.append("=" * 50)
        output.append(f"Status: {status}")
        
        # Display teams if available
        if teams_meta and len(teams_meta) >= 2:
            away_team = teams_meta[0]
            home_team = teams_meta[1]
            
            away_name = away_team.get('displayName', 'Unknown')
            home_name = home_team.get('displayName', 'Unknown')
            away_score = away_team.get('score', 'N/A')
            home_score = home_team.get('score', 'N/A')
            
            output.append(f"Teams: {away_name} @ {home_name}")
            output.append(f"Score: {away_name} {away_score} - {home_name} {home_score}")
        
        # Try to use adapter for detailed stats if requested
        if use_adapter:
            try:
                normalized_data = apply_adapter_normalization(data, league)
                if normalized_data != data:  # Adapter was applied successfully
                    formatted_stats = format_normalized_data(normalized_data, league, fields)
                    if formatted_stats and formatted_stats != "No formatted stats available":
                        output.append(f"\n{formatted_stats}")
                        return "\n".join(output)
            except Exception as e:
                logger.warning(f"Adapter formatting failed, falling back to basic format: {e}")
        
        # Fallback to basic format
        # Display leaders if available
        leaders = summary.get('leaders', [])
        if leaders:
            output.append("\nGame Leaders:")
            for leader in leaders[:3]:  # Show top 3 leaders
                name = leader.get('displayName', 'Unknown')
                value = leader.get('displayValue', 'N/A')
                output.append(f"  {name}: {value}")
        
        # Display basic boxscore info if available
        boxscore = summary.get('boxscore', {})
        if boxscore:
            players = boxscore.get('players', [])
            if players:
                output.append(f"\nBoxscore: {len(players)} player entries available")
            
            teams = boxscore.get('teams', [])
            if teams:
                output.append(f"Team stats: {len(teams)} team entries available")
        
        return "\n".join(output)
        
    except Exception as e:
        logger.error(f"Error formatting game summary: {e}")
        return f"Error formatting game summary data: {e}"

async def ask_question_about_game(data: Dict[str, Any], question: str) -> str:
    """
    Ask a natural language question about game data using OpenRouter.
    
    Args:
        data: Game summary data from MCP server
        question: Natural language question to ask
        
    Returns:
        AI response based on the game data
        
    Raises:
        LLMError: If LLM operation fails
    """
    try:
        logger.debug(f"Asking question about game data: {question}")
        success, response = await strict_answer(data, question)
        
        if not success:
            raise LLMAPIError(f"Failed to get AI response: {response}")
        
        logger.debug(f"AI response received, {len(response)} characters")
        return response
        
    except LLMConfigurationError as e:
        logger.error(f"LLM configuration error: {e}")
        raise
    except LLMAPIError as e:
        logger.error(f"LLM API error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in ask_question_about_game: {e}")
        raise LLMError(f"Unexpected error: {e}")

async def get_game_summary_data(league: str, event_id: str) -> Dict[str, Any]:
    """
    Get game summary data from MCP server.
    
    Args:
        league: League key (e.g., 'nfl', 'nba')
        event_id: ESPN event ID
        
    Returns:
        Game summary data
        
    Raises:
        MCPError: If MCP operation fails
    """
    try:
        logger.debug(f"Fetching game summary for {league} event {event_id}")
        data = await game_summary(league, event_id)
        logger.debug(f"Successfully fetched game summary")
        return data
        
    except MCPValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except MCPServerError as e:
        logger.error(f"MCP server error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise MCPError(f"Unexpected error: {e}")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Get game summary data for any sport',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s nfl 401547439                    # Get NFL game summary
  %(prog)s nba 401584123 --json             # Get NBA game summary as JSON
  %(prog)s wnba 401584456                   # Get WNBA game summary
  %(prog)s mlb 401581234                    # Get MLB game summary
  %(prog)s nfl 401547439 --ask "Who had the most rushing yards?"  # Ask AI question
  %(prog)s nba 401584123 --fields pts,reb,ast  # Show only points, rebounds, assists

Supported leagues:
  nfl, ncaaf, nba, wnba, ncaab, mlb, nhl, mls, epl, laliga
        """
    )
    
    parser.add_argument('league', help='League key (e.g., nfl, nba, wnba)')
    parser.add_argument('event_id', help='ESPN event ID')
    parser.add_argument('--json', action='store_true', 
                       help='Output raw JSON data from MCP server')
    parser.add_argument('--no-adapter', action='store_true',
                       help='Disable sport-specific adapter formatting')
    parser.add_argument('--ask', type=str, metavar='QUESTION',
                       help='Ask a natural language question about the game data')
    parser.add_argument('--fields', type=str, metavar='FIELD1,FIELD2,...',
                       help='Comma-separated list of fields to display (e.g., pts,reb,ast for NBA)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    try:
        # Parse fields if provided
        fields = None
        if args.fields:
            fields = [f.strip() for f in args.fields.split(',') if f.strip()]
            logger.debug(f"Field filtering enabled: {fields}")
        
        # Get game summary data
        data = asyncio.run(get_game_summary_data(args.league, args.event_id))
        
        if args.ask:
            # Ask natural language question about the game
            try:
                response = asyncio.run(ask_question_about_game(data, args.ask))
                print(f"Question: {args.ask}")
                print(f"Answer: {response}")
            except LLMConfigurationError as e:
                print(f"❌ LLM configuration error: {e}", file=sys.stderr)
                print("💡 Make sure OPENROUTER_API_KEY is set in .env.local", file=sys.stderr)
                sys.exit(1)
            except LLMAPIError as e:
                print(f"❌ AI service error: {e}", file=sys.stderr)
                sys.exit(1)
            except LLMError as e:
                print(f"❌ AI error: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.json:
            # Output raw JSON
            print(json.dumps(data, indent=2))
        else:
            # Output formatted summary
            use_adapter = not args.no_adapter
            formatted = format_game_summary(data, args.league, args.event_id, use_adapter, fields)
            print(formatted)
            
    except MCPValidationError as e:
        print(f"❌ Invalid parameters: {e}", file=sys.stderr)
        sys.exit(1)
    except MCPServerError as e:
        print(f"❌ Server error: {e}", file=sys.stderr)
        sys.exit(1)
    except MCPError as e:
        print(f"❌ MCP error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()