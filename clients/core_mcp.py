"""
Core MCP integration layer for sports data access.

This module provides a clean abstraction layer over the MCP server with league mapping
and comprehensive error handling. All ESPN data access flows through the MCP client.
"""

import json
import logging
from typing import Any, Dict, Optional, Tuple

from mcp_client import MCPClient, MCPClientError, get_server_path
from logging_config import get_mcp_logger

# Configure logging
logger = logging.getLogger(__name__)
mcp_logger = get_mcp_logger(__name__)

# League mapping from user-friendly keys to (sport, league) pairs
LEAGUE_MAPPING = {
    'nfl': ('football', 'nfl'),
    'ncaaf': ('football', 'college-football'),
    'nba': ('basketball', 'nba'),
    'wnba': ('basketball', 'wnba'),
    'ncaab': ('basketball', 'mens-college-basketball'),
    'mlb': ('baseball', 'mlb'),
    'nhl': ('hockey', 'nhl'),
    'mls': ('soccer', 'usa.1'),
    'epl': ('soccer', 'eng.1'),
    'laliga': ('soccer', 'esp.1')
}

class MCPError(Exception):
    """Base exception for MCP-related errors."""
    pass

class MCPServerError(MCPError):
    """Exception raised when MCP server returns an error."""
    pass

class MCPValidationError(MCPError):
    """Exception raised for invalid parameters."""
    pass

def _resolve_league(league: str) -> Tuple[str, str]:
    """
    Resolve user-friendly league key to (sport, league) pair.
    
    Args:
        league: User-friendly league key (e.g., 'nfl', 'nba')
        
    Returns:
        Tuple of (sport, league) for MCP server
        
    Raises:
        MCPValidationError: If league is not supported
    """
    if league not in LEAGUE_MAPPING:
        supported = ', '.join(LEAGUE_MAPPING.keys())
        raise MCPValidationError(f"Unsupported league '{league}'. Supported: {supported}")
    
    return LEAGUE_MAPPING[league]

def _handle_mcp_response(response: Dict[str, Any], operation: str, operation_id: str, 
                        league: str, **context) -> Dict[str, Any]:
    """
    Handle MCP server tool response with comprehensive error handling and logging.
    
    Args:
        response: MCP tool response
        operation: Operation name for logging
        operation_id: Operation ID for timing tracking
        league: League being queried
        **context: Additional context for logging
        
    Returns:
        Processed response data
        
    Raises:
        MCPServerError: If MCP server returns an error
    """
    # Log raw MCP response for debugging
    mcp_logger.log_mcp_response(operation, response)
    
    # MCP tool responses come in the format: {"content": [...]}
    content = response.get("content", [])
    
    if not content:
        error = MCPServerError(f"Empty response from MCP server for {operation}")
        mcp_logger.log_error(operation_id, operation, league, error, 'empty_response', **context)
        raise error
    
    # Extract the actual data from the first content item
    first_content = content[0] if content else {}
    
    if first_content.get("type") == "text":
        # This is a text response, might contain JSON
        text_content = first_content.get("text", "")
        try:
            # Try to parse as JSON if it looks like JSON
            if text_content.strip().startswith("{"):
                data = json.loads(text_content)
            else:
                data = {"content": text_content}
        except json.JSONDecodeError:
            data = {"content": text_content}
    else:
        # Assume it's already structured data
        data = first_content
    
    # Extract ESPN URL from response metadata for logging
    espn_url = None
    if isinstance(data, dict):
        meta = data.get('meta', {})
        espn_url = meta.get('url')
    
    # Check if the data indicates an error
    if isinstance(data, dict) and not data.get('ok', True):
        error_type = data.get('error_type', 'unknown_error')
        message = data.get('message', 'Unknown MCP server error')
        
        # Create appropriate exception
        if error_type == 'upstream_error':
            status = data.get('status')
            url = data.get('url') or espn_url
            error = MCPServerError(f"ESPN API error (status {status}): {message}. URL: {url}")
        elif error_type == 'validation_error':
            error = MCPValidationError(f"Validation error: {message}")
        elif error_type == 'request_error':
            url = data.get('url') or espn_url
            error = MCPServerError(f"Network error: {message}. URL: {url}")
        else:
            error = MCPServerError(f"MCP server error: {message}")
        
        # Log the error with context
        mcp_logger.log_error(operation_id, operation, league, error, error_type, espn_url, **context)
        raise error
    
    # Log successful operation
    mcp_logger.log_success(operation_id, operation, league, espn_url, data, **context)
    return data

async def scoreboard(league: str, date: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Get scoreboard data for a league.
    
    Args:
        league: League key (e.g., 'nfl', 'nba')
        date: Optional date in YYYYMMDD format
        **kwargs: Additional parameters (limit, week, seasontype for NFL/NCAAF)
        
    Returns:
        Scoreboard data from MCP server
        
    Raises:
        MCPValidationError: If parameters are invalid
        MCPServerError: If MCP server returns an error
    """
    # Start operation timing and logging
    context = {'date': date, **kwargs}
    operation_id = mcp_logger.start_operation('scoreboard', league, **context)
    
    try:
        sport, league_code = _resolve_league(league)
        
        # Prepare arguments for MCP tool
        arguments = {'sport': sport, 'league': league_code}
        if date:
            arguments['dates'] = date
        
        # Add optional parameters
        for key in ['limit', 'week', 'seasontype']:
            if key in kwargs:
                arguments[key] = kwargs[key]
        
        logger.debug(f"Calling MCP getScoreboard with args: {arguments}")
        
        # Connect to MCP server and call tool
        server_path = get_server_path()
        async with MCPClient(server_path) as client:
            response = await client.call_tool("getScoreboard", arguments)
        
        return _handle_mcp_response(response, 'scoreboard', operation_id, league, **context)
        
    except MCPClientError as e:
        error = MCPServerError(f"MCP client error: {e}")
        mcp_logger.log_error(operation_id, 'scoreboard', league, error, 'mcp_client_error', **context)
        raise error
    except Exception as e:
        if isinstance(e, (MCPError,)):
            raise
        error = MCPServerError(f"Unexpected error: {e}")
        mcp_logger.log_error(operation_id, 'scoreboard', league, error, 'unexpected_error', **context)
        raise error

async def teams(league: str) -> Dict[str, Any]:
    """
    Get teams list for a league.
    
    Args:
        league: League key (e.g., 'nfl', 'nba')
        
    Returns:
        Teams data from MCP server
        
    Raises:
        MCPValidationError: If league is invalid
        MCPServerError: If MCP server returns an error
    """
    # Start operation timing and logging
    operation_id = mcp_logger.start_operation('teams', league)
    
    try:
        sport, league_code = _resolve_league(league)
        
        arguments = {'sport': sport, 'league': league_code}
        logger.debug(f"Calling MCP getTeams for {sport}/{league_code}")
        
        server_path = get_server_path()
        async with MCPClient(server_path) as client:
            response = await client.call_tool("getTeams", arguments)
        
        return _handle_mcp_response(response, 'teams', operation_id, league)
        
    except MCPClientError as e:
        error = MCPServerError(f"MCP client error: {e}")
        mcp_logger.log_error(operation_id, 'teams', league, error, 'mcp_client_error')
        raise error
    except Exception as e:
        if isinstance(e, (MCPError,)):
            raise
        error = MCPServerError(f"Unexpected error: {e}")
        mcp_logger.log_error(operation_id, 'teams', league, error, 'unexpected_error')
        raise error

async def game_summary(league: str, event_id: str) -> Dict[str, Any]:
    """
    Get game summary/boxscore for a single event.
    
    Args:
        league: League key (e.g., 'nfl', 'nba')
        event_id: ESPN event ID
        
    Returns:
        Game summary data from MCP server
        
    Raises:
        MCPValidationError: If parameters are invalid
        MCPServerError: If MCP server returns an error
    """
    # Start operation timing and logging
    context = {'event_id': event_id}
    operation_id = mcp_logger.start_operation('game_summary', league, **context)
    
    try:
        if not event_id:
            error = MCPValidationError("event_id is required")
            mcp_logger.log_error(operation_id, 'game_summary', league, error, 'validation_error', **context)
            raise error
            
        sport, league_code = _resolve_league(league)
        
        arguments = {'sport': sport, 'league': league_code, 'event_id': event_id}
        logger.debug(f"Calling MCP getGameSummary for {sport}/{league_code}, event {event_id}")
        
        server_path = get_server_path()
        async with MCPClient(server_path) as client:
            response = await client.call_tool("getGameSummary", arguments)
        
        return _handle_mcp_response(response, 'game_summary', operation_id, league, **context)
        
    except MCPClientError as e:
        error = MCPServerError(f"MCP client error: {e}")
        mcp_logger.log_error(operation_id, 'game_summary', league, error, 'mcp_client_error', **context)
        raise error
    except Exception as e:
        if isinstance(e, (MCPError,)):
            raise
        error = MCPServerError(f"Unexpected error: {e}")
        mcp_logger.log_error(operation_id, 'game_summary', league, error, 'unexpected_error', **context)
        raise error

async def analyze_game_strict(league: str, event_id: str, question: str) -> Dict[str, Any]:
    """
    Analyze a game using only fetched stats with strict OpenRouter integration.
    
    Args:
        league: League key (e.g., 'nfl', 'nba')
        event_id: ESPN event ID
        question: Question to ask about the game
        
    Returns:
        Analysis response from MCP server
        
    Raises:
        MCPValidationError: If parameters are invalid
        MCPServerError: If MCP server returns an error
    """
    # Start operation timing and logging
    context = {'event_id': event_id, 'question': question[:100] + '...' if len(question) > 100 else question}
    operation_id = mcp_logger.start_operation('analyze_game_strict', league, **context)
    
    try:
        if not event_id:
            error = MCPValidationError("event_id is required")
            mcp_logger.log_error(operation_id, 'analyze_game_strict', league, error, 'validation_error', **context)
            raise error
        if not question:
            error = MCPValidationError("question is required")
            mcp_logger.log_error(operation_id, 'analyze_game_strict', league, error, 'validation_error', **context)
            raise error
            
        sport, league_code = _resolve_league(league)
        
        arguments = {'sport': sport, 'league': league_code, 'event_id': event_id, 'question': question}
        logger.debug(f"Calling MCP analyzeGameStrict for {sport}/{league_code}, event {event_id}")
        
        server_path = get_server_path()
        async with MCPClient(server_path) as client:
            response = await client.call_tool("analyzeGameStrict", arguments)
        
        return _handle_mcp_response(response, 'analyze_game_strict', operation_id, league, **context)
        
    except MCPClientError as e:
        error = MCPServerError(f"MCP client error: {e}")
        mcp_logger.log_error(operation_id, 'analyze_game_strict', league, error, 'mcp_client_error', **context)
        raise error
    except Exception as e:
        if isinstance(e, (MCPError,)):
            raise
        error = MCPServerError(f"Unexpected error: {e}")
        mcp_logger.log_error(operation_id, 'analyze_game_strict', league, error, 'unexpected_error', **context)
        raise error

async def probe_league_support(league: str, date: Optional[str] = None) -> Dict[str, Any]:
    """
    Probe scoreboard and game summary capability for a league/date.
    
    Args:
        league: League key (e.g., 'nfl', 'nba')
        date: Optional date in YYYYMMDD format
        
    Returns:
        Capability probe results from MCP server
        
    Raises:
        MCPValidationError: If league is invalid
        MCPServerError: If MCP server returns an error
    """
    # Start operation timing and logging
    context = {'date': date} if date else {}
    operation_id = mcp_logger.start_operation('probe_league_support', league, **context)
    
    try:
        sport, league_code = _resolve_league(league)
        
        arguments = {'sport': sport, 'league': league_code}
        if date:
            arguments['date'] = date
            
        logger.debug(f"Calling MCP probeLeagueSupport for {sport}/{league_code}")
        
        server_path = get_server_path()
        async with MCPClient(server_path) as client:
            response = await client.call_tool("probeLeagueSupport", arguments)
        
        return _handle_mcp_response(response, 'probe_league_support', operation_id, league, **context)
        
    except MCPClientError as e:
        error = MCPServerError(f"MCP client error: {e}")
        mcp_logger.log_error(operation_id, 'probe_league_support', league, error, 'mcp_client_error', **context)
        raise error
    except Exception as e:
        if isinstance(e, (MCPError,)):
            raise
        error = MCPServerError(f"Unexpected error: {e}")
        mcp_logger.log_error(operation_id, 'probe_league_support', league, error, 'unexpected_error', **context)
        raise error

# Convenience functions for season stats (these return supported:false as per MCP server)
async def team_season_stats(league: str, team_id: str, season: Optional[str] = None) -> Dict[str, Any]:
    """
    Get team season stats (returns supported:false as per MCP server design).
    
    Args:
        league: League key (e.g., 'nfl', 'nba')
        team_id: Team ID
        season: Optional season
        
    Returns:
        Season stats response (supported:false)
    """
    # Start operation timing and logging
    context = {'team_id': team_id, 'season': season} if season else {'team_id': team_id}
    operation_id = mcp_logger.start_operation('team_season_stats', league, **context)
    
    try:
        sport, league_code = _resolve_league(league)
        
        arguments = {'sport': sport, 'league': league_code, 'team_id': team_id}
        if season:
            arguments['season'] = season
            
        logger.debug(f"Calling MCP getTeamSeasonStats for {sport}/{league_code}, team {team_id}")
        
        server_path = get_server_path()
        async with MCPClient(server_path) as client:
            response = await client.call_tool("getTeamSeasonStats", arguments)
        
        return _handle_mcp_response(response, 'team_season_stats', operation_id, league, **context)
        
    except MCPClientError as e:
        error = MCPServerError(f"MCP client error: {e}")
        mcp_logger.log_error(operation_id, 'team_season_stats', league, error, 'mcp_client_error', **context)
        raise error
    except Exception as e:
        if isinstance(e, (MCPError,)):
            raise
        error = MCPServerError(f"Unexpected error: {e}")
        mcp_logger.log_error(operation_id, 'team_season_stats', league, error, 'unexpected_error', **context)
        raise error

async def player_season_stats(league: str, player_id: str, season: Optional[str] = None) -> Dict[str, Any]:
    """
    Get player season stats (returns supported:false as per MCP server design).
    
    Args:
        league: League key (e.g., 'nfl', 'nba')
        player_id: Player ID
        season: Optional season
        
    Returns:
        Season stats response (supported:false)
    """
    # Start operation timing and logging
    context = {'player_id': player_id, 'season': season} if season else {'player_id': player_id}
    operation_id = mcp_logger.start_operation('player_season_stats', league, **context)
    
    try:
        sport, league_code = _resolve_league(league)
        
        arguments = {'sport': sport, 'league': league_code, 'player_id': player_id}
        if season:
            arguments['season'] = season
            
        logger.debug(f"Calling MCP getPlayerSeasonStats for {sport}/{league_code}, player {player_id}")
        
        server_path = get_server_path()
        async with MCPClient(server_path) as client:
            response = await client.call_tool("getPlayerSeasonStats", arguments)
        
        return _handle_mcp_response(response, 'player_season_stats', operation_id, league, **context)
        
    except MCPClientError as e:
        error = MCPServerError(f"MCP client error: {e}")
        mcp_logger.log_error(operation_id, 'player_season_stats', league, error, 'mcp_client_error', **context)
        raise error
    except Exception as e:
        if isinstance(e, (MCPError,)):
            raise
        error = MCPServerError(f"Unexpected error: {e}")
        mcp_logger.log_error(operation_id, 'player_season_stats', league, error, 'unexpected_error', **context)
        raise error