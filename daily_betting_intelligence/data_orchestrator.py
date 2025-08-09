"""
Data orchestrator for the Daily Betting Intelligence system.

This module manages concurrent data fetching across multiple sports leagues
while respecting API rate limits and handling errors gracefully. It coordinates
with the existing ESPN MCP server infrastructure to retrieve game schedules
and team data for specified dates.
"""

import asyncio
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
import pytz
from dataclasses import dataclass

from clients.core_mcp import scoreboard, teams, MCPError, MCPServerError, MCPValidationError, LEAGUE_MAPPING
from daily_betting_intelligence.config_manager import ConfigManager
from daily_betting_intelligence.models import GameData, TeamStats, ErrorReport
from clients.logging_config import get_mcp_logger

logger = logging.getLogger(__name__)
mcp_logger = get_mcp_logger(__name__)


@dataclass
class LeagueDataResult:
    """Result of data fetching for a single league."""
    league: str
    success: bool
    games: List[GameData]
    teams_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_type: Optional[str] = None


class DataOrchestrator:
    """
    Orchestrates concurrent data fetching across multiple sports leagues.
    
    This class manages the retrieval of game schedules and team data from the
    ESPN MCP server, handling rate limiting, timeouts, and error recovery.
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize the data orchestrator.
        
        Args:
            config_manager: Configuration manager instance. If None, creates default.
        """
        self.config_manager = config_manager or ConfigManager()
        self.config = self.config_manager.get_config()
        self.eastern_tz = pytz.timezone('US/Eastern')
        
        # Semaphore to limit concurrent requests
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        
        logger.info(f"DataOrchestrator initialized with max_concurrent_requests={self.config.max_concurrent_requests}")
    
    def validate_date(self, target_date: str) -> Tuple[bool, str, Optional[date]]:
        """
        Validate and parse target date string.
        
        Args:
            target_date: Date string in YYYY-MM-DD or YYYYMMDD format
            
        Returns:
            Tuple of (is_valid, formatted_date_string, parsed_date_object)
        """
        try:
            # Handle both YYYY-MM-DD and YYYYMMDD formats
            if len(target_date) == 8 and target_date.isdigit():
                # YYYYMMDD format
                parsed_date = datetime.strptime(target_date, '%Y%m%d').date()
                formatted_date = target_date
            elif len(target_date) == 10 and target_date.count('-') == 2:
                # YYYY-MM-DD format
                parsed_date = datetime.strptime(target_date, '%Y-%m-%d').date()
                formatted_date = parsed_date.strftime('%Y%m%d')
            else:
                return False, "", None
            
            # Validate date is not too far in the past or future
            today = date.today()
            days_diff = (parsed_date - today).days
            
            if days_diff < -365:
                return False, "", None  # More than 1 year in the past
            if days_diff > 365:
                return False, "", None  # More than 1 year in the future
            
            return True, formatted_date, parsed_date
            
        except ValueError:
            return False, "", None
    
    def convert_to_eastern_time(self, game_time_str: str, source_timezone: str = 'UTC') -> datetime:
        """
        Convert game time to Eastern timezone.
        
        Args:
            game_time_str: Game time string (ISO format expected)
            source_timezone: Source timezone (default: UTC)
            
        Returns:
            datetime object in Eastern timezone
        """
        try:
            # Parse the datetime string
            if 'T' in game_time_str:
                # ISO format with timezone info
                if game_time_str.endswith('Z'):
                    # UTC timezone
                    dt = datetime.fromisoformat(game_time_str.replace('Z', '+00:00'))
                elif '+' in game_time_str or game_time_str.count('-') > 2:
                    # Has timezone offset
                    dt = datetime.fromisoformat(game_time_str)
                else:
                    # No timezone info, assume UTC
                    dt = datetime.fromisoformat(game_time_str)
                    dt = pytz.UTC.localize(dt)
            else:
                # Simple format, assume UTC
                dt = datetime.fromisoformat(game_time_str)
                dt = pytz.UTC.localize(dt)
            
            # Convert to Eastern time
            if dt.tzinfo is None:
                # Naive datetime, assume UTC
                dt = pytz.UTC.localize(dt)
            
            eastern_dt = dt.astimezone(self.eastern_tz)
            return eastern_dt
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Could not parse game time '{game_time_str}': {e}")
            # Return current time in Eastern as fallback
            return datetime.now(self.eastern_tz)
    
    def _extract_games_from_scoreboard(self, scoreboard_data: Dict[str, Any], league: str) -> List[GameData]:
        """
        Extract game data from ESPN scoreboard response.
        
        Args:
            scoreboard_data: Raw scoreboard data from MCP server
            league: League identifier
            
        Returns:
            List of GameData objects
        """
        games = []
        
        try:
            # ESPN scoreboard structure: events array contains games
            events = scoreboard_data.get('events', [])
            
            for event in events:
                try:
                    # Extract basic game information
                    event_id = event.get('id', '')
                    name = event.get('name', '')
                    
                    # Parse teams from name (format: "Team A at Team B" or "Team A vs Team B")
                    if ' at ' in name:
                        away_team, home_team = name.split(' at ', 1)
                    elif ' vs ' in name:
                        teams = name.split(' vs ', 1)
                        away_team, home_team = teams[0], teams[1]
                    else:
                        # Fallback: try to get from competitions
                        competitions = event.get('competitions', [])
                        if competitions:
                            competitors = competitions[0].get('competitors', [])
                            home_team = next((c.get('team', {}).get('displayName', '') 
                                            for c in competitors if c.get('homeAway') == 'home'), 'Unknown')
                            away_team = next((c.get('team', {}).get('displayName', '') 
                                            for c in competitors if c.get('homeAway') == 'away'), 'Unknown')
                        else:
                            away_team, home_team = 'Unknown', 'Unknown'
                    
                    # Extract game time
                    game_date_str = event.get('date', '')
                    game_time = self.convert_to_eastern_time(game_date_str) if game_date_str else datetime.now(self.eastern_tz)
                    
                    # Extract venue information
                    venue = 'Unknown'
                    competitions = event.get('competitions', [])
                    if competitions:
                        venue_info = competitions[0].get('venue', {})
                        venue = venue_info.get('fullName', venue_info.get('name', 'Unknown'))
                    
                    # Extract status
                    status_info = event.get('status', {})
                    status_type = status_info.get('type', {})
                    status = status_type.get('name', 'unknown').lower()
                    
                    # Map ESPN status to our status
                    if status in ['scheduled', 'pre']:
                        status = 'pre-game'
                    elif status in ['in', 'live']:
                        status = 'live'
                    elif status in ['final', 'completed']:
                        status = 'final'
                    
                    # Extract scores if available
                    home_score = None
                    away_score = None
                    if competitions:
                        competitors = competitions[0].get('competitors', [])
                        for competitor in competitors:
                            score = competitor.get('score')
                            if score is not None:
                                try:
                                    score = int(score)
                                    if competitor.get('homeAway') == 'home':
                                        home_score = score
                                    else:
                                        away_score = score
                                except (ValueError, TypeError):
                                    pass
                    
                    # Create GameData object
                    game_data = GameData(
                        event_id=event_id,
                        league=league,
                        home_team=home_team.strip(),
                        away_team=away_team.strip(),
                        game_time=game_time,
                        venue=venue,
                        status=status,
                        home_score=home_score,
                        away_score=away_score,
                        additional_metadata={
                            'raw_event': event,
                            'espn_name': name
                        }
                    )
                    
                    games.append(game_data)
                    
                except Exception as e:
                    logger.warning(f"Error parsing game event in {league}: {e}")
                    continue
            
            logger.info(f"Extracted {len(games)} games from {league} scoreboard")
            return games
            
        except Exception as e:
            logger.error(f"Error extracting games from {league} scoreboard: {e}")
            return []
    
    async def fetch_league_data(self, league: str, target_date: str) -> LeagueDataResult:
        """
        Fetch data for a single league on the target date.
        
        Args:
            league: League identifier (e.g., 'nfl', 'nba')
            target_date: Date in YYYYMMDD format
            
        Returns:
            LeagueDataResult with games and any errors
        """
        async with self._semaphore:
            operation_id = mcp_logger.start_operation('fetch_league_data', league, date=target_date)
            
            try:
                logger.debug(f"Fetching data for {league} on {target_date}")
                
                # Fetch scoreboard data
                scoreboard_data = await scoreboard(league, date=target_date)
                
                # Extract games from scoreboard
                games = self._extract_games_from_scoreboard(scoreboard_data, league)
                
                # Optionally fetch teams data for additional context
                teams_data = None
                try:
                    teams_data = await teams(league)
                except MCPError as e:
                    logger.warning(f"Could not fetch teams data for {league}: {e}")
                
                mcp_logger.log_success(operation_id, 'fetch_league_data', league, 
                                     games_count=len(games))
                
                return LeagueDataResult(
                    league=league,
                    success=True,
                    games=games,
                    teams_data=teams_data
                )
                
            except MCPValidationError as e:
                error_msg = f"Validation error for {league}: {e}"
                logger.error(error_msg)
                mcp_logger.log_error(operation_id, 'fetch_league_data', league, e, 'validation_error')
                
                return LeagueDataResult(
                    league=league,
                    success=False,
                    games=[],
                    error=error_msg,
                    error_type='validation_error'
                )
                
            except MCPServerError as e:
                error_msg = f"Server error for {league}: {e}"
                logger.error(error_msg)
                mcp_logger.log_error(operation_id, 'fetch_league_data', league, e, 'server_error')
                
                return LeagueDataResult(
                    league=league,
                    success=False,
                    games=[],
                    error=error_msg,
                    error_type='server_error'
                )
                
            except Exception as e:
                error_msg = f"Unexpected error for {league}: {e}"
                logger.error(error_msg, exc_info=True)
                mcp_logger.log_error(operation_id, 'fetch_league_data', league, e, 'unexpected_error')
                
                return LeagueDataResult(
                    league=league,
                    success=False,
                    games=[],
                    error=error_msg,
                    error_type='unexpected_error'
                )
    
    async def fetch_all_leagues_data(self, target_date: str, leagues: Optional[List[str]] = None) -> Dict[str, LeagueDataResult]:
        """
        Fetch data for all specified leagues concurrently.
        
        Args:
            target_date: Date in YYYY-MM-DD or YYYYMMDD format
            leagues: List of league identifiers. If None, uses config default.
            
        Returns:
            Dictionary mapping league -> LeagueDataResult
        """
        # Validate and format date
        is_valid, formatted_date, parsed_date = self.validate_date(target_date)
        if not is_valid:
            raise ValueError(f"Invalid date format: {target_date}. Use YYYY-MM-DD or YYYYMMDD")
        
        # Use provided leagues or default from config
        if leagues is None:
            leagues = self.config.leagues
        
        # Validate leagues
        valid_leagues = self.config_manager.validate_leagues(leagues)
        if not valid_leagues:
            raise ValueError("No valid leagues specified")
        
        logger.info(f"Fetching data for {len(valid_leagues)} leagues on {formatted_date}: {valid_leagues}")
        
        # Create tasks for concurrent execution
        tasks = []
        for league in valid_leagues:
            task = asyncio.create_task(
                self.fetch_league_data(league, formatted_date),
                name=f"fetch_{league}_{formatted_date}"
            )
            tasks.append((league, task))
        
        # Wait for all tasks to complete
        results = {}
        completed_tasks = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        for (league, _), result in zip(tasks, completed_tasks):
            if isinstance(result, Exception):
                logger.error(f"Task failed for {league}: {result}")
                results[league] = LeagueDataResult(
                    league=league,
                    success=False,
                    games=[],
                    error=str(result),
                    error_type='task_error'
                )
            else:
                results[league] = result
        
        # Log summary
        successful_leagues = [league for league, result in results.items() if result.success]
        failed_leagues = [league for league, result in results.items() if not result.success]
        total_games = sum(len(result.games) for result in results.values() if result.success)
        
        logger.info(f"Data fetching complete: {len(successful_leagues)} successful, "
                   f"{len(failed_leagues)} failed, {total_games} total games")
        
        if failed_leagues:
            logger.warning(f"Failed leagues: {failed_leagues}")
        
        return results
    
    def get_supported_leagues(self) -> List[str]:
        """
        Get list of supported leagues.
        
        Returns:
            List of supported league identifiers
        """
        return list(LEAGUE_MAPPING.keys())
    
    def aggregate_errors(self, results: Dict[str, LeagueDataResult]) -> List[ErrorReport]:
        """
        Aggregate errors from league data results.
        
        Args:
            results: Dictionary of league results
            
        Returns:
            List of ErrorReport objects
        """
        errors = []
        
        for league, result in results.items():
            if not result.success and result.error:
                error_report = ErrorReport(
                    error_type=result.error_type or 'unknown',
                    error_message=result.error,
                    context=f"League: {league}",
                    severity='medium' if result.error_type == 'validation_error' else 'high',
                    affected_component=f"data_orchestrator.{league}"
                )
                errors.append(error_report)
        
        return errors