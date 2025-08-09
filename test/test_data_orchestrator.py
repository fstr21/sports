"""
Unit tests for the DataOrchestrator class.

Tests cover date validation, timezone handling, data extraction,
concurrent processing, and error handling with mock MCP responses.
"""

import asyncio
import pytest
from datetime import datetime, date
from unittest.mock import AsyncMock, MagicMock, patch
import pytz

from daily_betting_intelligence.data_orchestrator import DataOrchestrator, LeagueDataResult
from daily_betting_intelligence.config_manager import ConfigManager, SystemConfig
from daily_betting_intelligence.models import GameData, ErrorReport
from clients.core_mcp import MCPError, MCPServerError, MCPValidationError


class TestDataOrchestrator:
    """Test suite for DataOrchestrator class."""
    
    @pytest.fixture
    def config_manager(self):
        """Create a test configuration manager."""
        config = SystemConfig()
        config.max_concurrent_requests = 3
        config.leagues = ['nba', 'nfl', 'wnba']
        
        config_manager = MagicMock(spec=ConfigManager)
        config_manager.get_config.return_value = config
        config_manager.validate_leagues.return_value = ['nba', 'nfl', 'wnba']
        
        return config_manager
    
    @pytest.fixture
    def orchestrator(self, config_manager):
        """Create a DataOrchestrator instance for testing."""
        return DataOrchestrator(config_manager)
    
    @pytest.fixture
    def sample_scoreboard_data(self):
        """Sample ESPN scoreboard data for testing."""
        return {
            "events": [
                {
                    "id": "401547401",
                    "name": "Los Angeles Lakers at Boston Celtics",
                    "date": "2025-08-09T23:30:00Z",
                    "status": {
                        "type": {
                            "name": "scheduled"
                        }
                    },
                    "competitions": [
                        {
                            "venue": {
                                "fullName": "TD Garden",
                                "name": "TD Garden"
                            },
                            "competitors": [
                                {
                                    "homeAway": "home",
                                    "team": {
                                        "displayName": "Boston Celtics"
                                    },
                                    "score": None
                                },
                                {
                                    "homeAway": "away", 
                                    "team": {
                                        "displayName": "Los Angeles Lakers"
                                    },
                                    "score": None
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "401547402",
                    "name": "Miami Heat vs Golden State Warriors",
                    "date": "2025-08-10T02:00:00Z",
                    "status": {
                        "type": {
                            "name": "final"
                        }
                    },
                    "competitions": [
                        {
                            "venue": {
                                "fullName": "Chase Center"
                            },
                            "competitors": [
                                {
                                    "homeAway": "home",
                                    "team": {
                                        "displayName": "Golden State Warriors"
                                    },
                                    "score": "112"
                                },
                                {
                                    "homeAway": "away",
                                    "team": {
                                        "displayName": "Miami Heat"
                                    },
                                    "score": "108"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    
    def test_init(self, config_manager):
        """Test DataOrchestrator initialization."""
        orchestrator = DataOrchestrator(config_manager)
        
        assert orchestrator.config_manager == config_manager
        assert orchestrator.config == config_manager.get_config()
        assert orchestrator.eastern_tz.zone == 'US/Eastern'
        assert orchestrator._semaphore._value == 3  # max_concurrent_requests
    
    def test_init_default_config(self):
        """Test DataOrchestrator initialization with default config."""
        orchestrator = DataOrchestrator()
        
        assert orchestrator.config_manager is not None
        assert orchestrator.config is not None
        assert orchestrator.eastern_tz.zone == 'US/Eastern'
    
    def test_validate_date_yyyymmdd_format(self, orchestrator):
        """Test date validation with YYYYMMDD format."""
        is_valid, formatted, parsed = orchestrator.validate_date("20250809")
        
        assert is_valid is True
        assert formatted == "20250809"
        assert parsed == date(2025, 8, 9)
    
    def test_validate_date_yyyy_mm_dd_format(self, orchestrator):
        """Test date validation with YYYY-MM-DD format."""
        is_valid, formatted, parsed = orchestrator.validate_date("2025-08-09")
        
        assert is_valid is True
        assert formatted == "20250809"
        assert parsed == date(2025, 8, 9)
    
    def test_validate_date_invalid_format(self, orchestrator):
        """Test date validation with invalid format."""
        is_valid, formatted, parsed = orchestrator.validate_date("2025/08/09")
        
        assert is_valid is False
        assert formatted == ""
        assert parsed is None
    
    def test_validate_date_too_far_past(self, orchestrator):
        """Test date validation with date too far in the past."""
        past_date = "20230101"  # More than 1 year ago
        is_valid, formatted, parsed = orchestrator.validate_date(past_date)
        
        assert is_valid is False
        assert formatted == ""
        assert parsed is None
    
    def test_validate_date_too_far_future(self, orchestrator):
        """Test date validation with date too far in the future."""
        future_date = "20270101"  # More than 1 year in future
        is_valid, formatted, parsed = orchestrator.validate_date(future_date)
        
        assert is_valid is False
        assert formatted == ""
        assert parsed is None
    
    def test_convert_to_eastern_time_utc(self, orchestrator):
        """Test timezone conversion from UTC."""
        utc_time = "2025-08-09T23:30:00Z"
        eastern_time = orchestrator.convert_to_eastern_time(utc_time)
        
        assert eastern_time.tzinfo.zone == 'US/Eastern'
        # UTC 23:30 should be Eastern 19:30 (EDT in August)
        assert eastern_time.hour == 19
        assert eastern_time.minute == 30
    
    def test_convert_to_eastern_time_with_offset(self, orchestrator):
        """Test timezone conversion with timezone offset."""
        time_with_offset = "2025-08-09T20:30:00-03:00"
        eastern_time = orchestrator.convert_to_eastern_time(time_with_offset)
        
        assert eastern_time.tzinfo.zone == 'US/Eastern'
        # -03:00 20:30 should be Eastern 19:30 (EDT in August)
        assert eastern_time.hour == 19
        assert eastern_time.minute == 30
    
    def test_convert_to_eastern_time_invalid(self, orchestrator):
        """Test timezone conversion with invalid time string."""
        invalid_time = "invalid-time-string"
        eastern_time = orchestrator.convert_to_eastern_time(invalid_time)
        
        # Should return current time in Eastern as fallback
        assert eastern_time.tzinfo.zone == 'US/Eastern'
        assert isinstance(eastern_time, datetime)
    
    def test_extract_games_from_scoreboard(self, orchestrator, sample_scoreboard_data):
        """Test game extraction from ESPN scoreboard data."""
        games = orchestrator._extract_games_from_scoreboard(sample_scoreboard_data, 'nba')
        
        assert len(games) == 2
        
        # Test first game
        game1 = games[0]
        assert game1.event_id == "401547401"
        assert game1.league == "nba"
        assert game1.home_team == "Boston Celtics"
        assert game1.away_team == "Los Angeles Lakers"
        assert game1.venue == "TD Garden"
        assert game1.status == "pre-game"
        assert game1.home_score is None
        assert game1.away_score is None
        
        # Test second game
        game2 = games[1]
        assert game2.event_id == "401547402"
        assert game2.home_team == "Golden State Warriors"
        assert game2.away_team == "Miami Heat"
        assert game2.venue == "Chase Center"
        assert game2.status == "final"
        assert game2.home_score == 112
        assert game2.away_score == 108
    
    def test_extract_games_empty_data(self, orchestrator):
        """Test game extraction with empty scoreboard data."""
        empty_data = {"events": []}
        games = orchestrator._extract_games_from_scoreboard(empty_data, 'nba')
        
        assert len(games) == 0
    
    def test_extract_games_malformed_data(self, orchestrator):
        """Test game extraction with malformed data."""
        malformed_data = {
            "events": [
                {
                    "id": "401547401",
                    # Missing required fields
                }
            ]
        }
        games = orchestrator._extract_games_from_scoreboard(malformed_data, 'nba')
        
        # Should handle gracefully and extract what it can
        assert len(games) == 1
        game = games[0]
        assert game.event_id == "401547401"
        assert game.league == "nba"
    
    @pytest.mark.asyncio
    async def test_fetch_league_data_success(self, orchestrator, sample_scoreboard_data):
        """Test successful league data fetching."""
        with patch('daily_betting_intelligence.data_orchestrator.scoreboard') as mock_scoreboard, \
             patch('daily_betting_intelligence.data_orchestrator.teams') as mock_teams:
            
            mock_scoreboard.return_value = sample_scoreboard_data
            mock_teams.return_value = {"teams": []}
            
            result = await orchestrator.fetch_league_data('nba', '20250809')
            
            assert result.success is True
            assert result.league == 'nba'
            assert len(result.games) == 2
            assert result.teams_data is not None
            assert result.error is None
    
    @pytest.mark.asyncio
    async def test_fetch_league_data_validation_error(self, orchestrator):
        """Test league data fetching with validation error."""
        with patch('daily_betting_intelligence.data_orchestrator.scoreboard') as mock_scoreboard:
            mock_scoreboard.side_effect = MCPValidationError("Invalid league")
            
            result = await orchestrator.fetch_league_data('invalid', '20250809')
            
            assert result.success is False
            assert result.league == 'invalid'
            assert len(result.games) == 0
            assert result.error_type == 'validation_error'
            assert "Validation error" in result.error
    
    @pytest.mark.asyncio
    async def test_fetch_league_data_server_error(self, orchestrator):
        """Test league data fetching with server error."""
        with patch('daily_betting_intelligence.data_orchestrator.scoreboard') as mock_scoreboard:
            mock_scoreboard.side_effect = MCPServerError("Server unavailable")
            
            result = await orchestrator.fetch_league_data('nba', '20250809')
            
            assert result.success is False
            assert result.league == 'nba'
            assert len(result.games) == 0
            assert result.error_type == 'server_error'
            assert "Server error" in result.error
    
    @pytest.mark.asyncio
    async def test_fetch_league_data_teams_error(self, orchestrator, sample_scoreboard_data):
        """Test league data fetching when teams call fails."""
        with patch('daily_betting_intelligence.data_orchestrator.scoreboard') as mock_scoreboard, \
             patch('daily_betting_intelligence.data_orchestrator.teams') as mock_teams:
            
            mock_scoreboard.return_value = sample_scoreboard_data
            mock_teams.side_effect = MCPServerError("Teams data unavailable")
            
            result = await orchestrator.fetch_league_data('nba', '20250809')
            
            # Should still succeed with games data, just no teams data
            assert result.success is True
            assert result.league == 'nba'
            assert len(result.games) == 2
            assert result.teams_data is None
            assert result.error is None
    
    @pytest.mark.asyncio
    async def test_fetch_all_leagues_data_success(self, orchestrator, sample_scoreboard_data):
        """Test successful multi-league data fetching."""
        with patch('daily_betting_intelligence.data_orchestrator.scoreboard') as mock_scoreboard, \
             patch('daily_betting_intelligence.data_orchestrator.teams') as mock_teams:
            
            mock_scoreboard.return_value = sample_scoreboard_data
            mock_teams.return_value = {"teams": []}
            
            # Mock validate_leagues to return only the requested leagues
            orchestrator.config_manager.validate_leagues.return_value = ['nba', 'nfl']
            
            results = await orchestrator.fetch_all_leagues_data('2025-08-09', ['nba', 'nfl'])
            
            assert len(results) == 2
            assert 'nba' in results
            assert 'nfl' in results
            assert results['nba'].success is True
            assert results['nfl'].success is True
            assert len(results['nba'].games) == 2
            assert len(results['nfl'].games) == 2
    
    @pytest.mark.asyncio
    async def test_fetch_all_leagues_data_invalid_date(self, orchestrator):
        """Test multi-league data fetching with invalid date."""
        with pytest.raises(ValueError, match="Invalid date format"):
            await orchestrator.fetch_all_leagues_data('invalid-date')
    
    @pytest.mark.asyncio
    async def test_fetch_all_leagues_data_no_valid_leagues(self, orchestrator):
        """Test multi-league data fetching with no valid leagues."""
        orchestrator.config_manager.validate_leagues.return_value = []
        
        with pytest.raises(ValueError, match="No valid leagues specified"):
            await orchestrator.fetch_all_leagues_data('2025-08-09', ['invalid'])
    
    @pytest.mark.asyncio
    async def test_fetch_all_leagues_data_mixed_results(self, orchestrator, sample_scoreboard_data):
        """Test multi-league data fetching with mixed success/failure."""
        with patch('daily_betting_intelligence.data_orchestrator.scoreboard') as mock_scoreboard, \
             patch('daily_betting_intelligence.data_orchestrator.teams') as mock_teams:
            
            # NBA succeeds, NFL fails
            def scoreboard_side_effect(league, **kwargs):
                if league == 'nba':
                    return sample_scoreboard_data
                else:
                    raise MCPServerError("Server error")
            
            mock_scoreboard.side_effect = scoreboard_side_effect
            mock_teams.return_value = {"teams": []}
            
            # Mock validate_leagues to return only the requested leagues
            orchestrator.config_manager.validate_leagues.return_value = ['nba', 'nfl']
            
            results = await orchestrator.fetch_all_leagues_data('2025-08-09', ['nba', 'nfl'])
            
            assert len(results) == 2
            assert results['nba'].success is True
            assert results['nfl'].success is False
            assert len(results['nba'].games) == 2
            assert len(results['nfl'].games) == 0
    
    @pytest.mark.asyncio
    async def test_fetch_all_leagues_data_default_leagues(self, orchestrator, sample_scoreboard_data):
        """Test multi-league data fetching with default leagues from config."""
        with patch('daily_betting_intelligence.data_orchestrator.scoreboard') as mock_scoreboard, \
             patch('daily_betting_intelligence.data_orchestrator.teams') as mock_teams:
            
            mock_scoreboard.return_value = sample_scoreboard_data
            mock_teams.return_value = {"teams": []}
            
            # Don't specify leagues, should use config default
            results = await orchestrator.fetch_all_leagues_data('2025-08-09')
            
            # Should use config.leagues = ['nba', 'nfl', 'wnba']
            assert len(results) == 3
            assert 'nba' in results
            assert 'nfl' in results
            assert 'wnba' in results
    
    @pytest.mark.asyncio
    async def test_concurrent_request_limiting(self, orchestrator, sample_scoreboard_data):
        """Test that concurrent requests are properly limited."""
        with patch('daily_betting_intelligence.data_orchestrator.scoreboard') as mock_scoreboard, \
             patch('daily_betting_intelligence.data_orchestrator.teams') as mock_teams:
            
            # Track concurrent calls
            active_calls = 0
            max_concurrent = 0
            
            async def slow_scoreboard(*args, **kwargs):
                nonlocal active_calls, max_concurrent
                active_calls += 1
                max_concurrent = max(max_concurrent, active_calls)
                
                # Simulate slow response
                await asyncio.sleep(0.1)
                
                active_calls -= 1
                return sample_scoreboard_data
            
            mock_scoreboard.side_effect = slow_scoreboard
            mock_teams.return_value = {"teams": []}
            
            # Request more leagues than the semaphore limit (3)
            leagues = ['nba', 'nfl', 'wnba', 'mlb', 'nhl']
            # Mock validate_leagues to return all requested leagues
            orchestrator.config_manager.validate_leagues.return_value = leagues
            
            results = await orchestrator.fetch_all_leagues_data('2025-08-09', leagues)
            
            # Should have limited concurrent requests to 3
            assert max_concurrent <= 3
            assert len(results) == 5
    
    def test_get_supported_leagues(self, orchestrator):
        """Test getting supported leagues list."""
        with patch('daily_betting_intelligence.data_orchestrator.LEAGUE_MAPPING') as mock_mapping:
            mock_mapping.keys.return_value = ['nba', 'nfl', 'mlb']
            
            leagues = orchestrator.get_supported_leagues()
            
            assert leagues == ['nba', 'nfl', 'mlb']
    
    def test_aggregate_errors(self, orchestrator):
        """Test error aggregation from league results."""
        results = {
            'nba': LeagueDataResult(
                league='nba',
                success=True,
                games=[]
            ),
            'nfl': LeagueDataResult(
                league='nfl',
                success=False,
                games=[],
                error='Server error',
                error_type='server_error'
            ),
            'mlb': LeagueDataResult(
                league='mlb',
                success=False,
                games=[],
                error='Validation error',
                error_type='validation_error'
            )
        }
        
        errors = orchestrator.aggregate_errors(results)
        
        assert len(errors) == 2
        
        # Check NFL error
        nfl_error = next(e for e in errors if 'nfl' in e.context)
        assert nfl_error.error_type == 'server_error'
        assert nfl_error.error_message == 'Server error'
        assert nfl_error.severity == 'high'
        
        # Check MLB error
        mlb_error = next(e for e in errors if 'mlb' in e.context)
        assert mlb_error.error_type == 'validation_error'
        assert mlb_error.error_message == 'Validation error'
        assert mlb_error.severity == 'medium'


if __name__ == '__main__':
    pytest.main([__file__])