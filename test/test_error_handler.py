"""
Unit tests for the Daily Betting Intelligence error handler.

Tests comprehensive error handling scenarios, graceful degradation,
error aggregation, and recovery strategies.
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from daily_betting_intelligence.error_handler import (
    ErrorHandler,
    ErrorContext,
    ErrorSummary
)
from daily_betting_intelligence.exceptions import (
    ESPNMCPError,
    WagyuMCPError,
    LLMAnalysisError,
    OpenRouterError,
    TimeoutError,
    RateLimitError,
    ValidationError,
    ConfigurationError
)


class TestErrorContext:
    """Test ErrorContext data class."""
    
    def test_error_context_creation(self):
        """Test ErrorContext creation with default values."""
        context = ErrorContext(operation="test_operation")
        
        assert context.operation == "test_operation"
        assert context.league is None
        assert context.event_id is None
        assert context.retry_count == 0
        assert context.duration_ms is None
        assert isinstance(context.timestamp, datetime)
        assert context.additional_data == {}
    
    def test_error_context_with_all_fields(self):
        """Test ErrorContext creation with all fields."""
        timestamp = datetime.now()
        additional_data = {"key": "value"}
        
        context = ErrorContext(
            operation="fetch_games",
            timestamp=timestamp,
            league="nba",
            event_id="12345",
            retry_count=2,
            duration_ms=1500,
            additional_data=additional_data
        )
        
        assert context.operation == "fetch_games"
        assert context.timestamp == timestamp
        assert context.league == "nba"
        assert context.event_id == "12345"
        assert context.retry_count == 2
        assert context.duration_ms == 1500
        assert context.additional_data == additional_data


class TestErrorSummary:
    """Test ErrorSummary data class."""
    
    def test_error_summary_defaults(self):
        """Test ErrorSummary default values."""
        summary = ErrorSummary()
        
        assert summary.total_errors == 0
        assert summary.mcp_server_errors == 0
        assert summary.llm_analysis_errors == 0
        assert summary.timeout_errors == 0
        assert summary.rate_limit_errors == 0
        assert summary.validation_errors == 0
        assert summary.other_errors == 0
        assert summary.errors_by_league == {}
        assert summary.errors_by_operation == {}
        assert summary.critical_failures == []
        assert summary.warnings == []
        assert summary.successful_retries == 0
        assert summary.failed_retries == 0
        assert summary.degraded_operations == 0


@pytest.fixture
def error_handler():
    """Create ErrorHandler instance for testing."""
    return ErrorHandler(max_retries=2, retry_delay=0.1)


@pytest.fixture
def mock_logger():
    """Create mock logger."""
    with patch('daily_betting_intelligence.error_handler.logging.getLogger') as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        yield mock_logger


class TestErrorHandler:
    """Test ErrorHandler class functionality."""
    
    def test_error_handler_initialization(self):
        """Test ErrorHandler initialization."""
        handler = ErrorHandler(max_retries=5, retry_delay=2.0)
        
        assert handler.max_retries == 5
        assert handler.retry_delay == 2.0
        assert isinstance(handler.error_summary, ErrorSummary)
        assert handler.error_history == []
        assert len(handler.fallback_strategies) > 0
    
    @pytest.mark.asyncio
    async def test_handle_espn_mcp_error(self, error_handler, mock_logger):
        """Test handling ESPN MCP server errors."""
        error = ESPNMCPError("ESPN server unavailable")
        context = ErrorContext(operation="fetch_scoreboard", league="nba")
        
        result = await error_handler.handle_mcp_error(error, context)
        
        assert result['success'] is False
        assert result['error'] == "ESPN server unavailable"
        assert result['server_type'] == "ESPN"
        assert result['degraded'] is True
        assert error_handler.error_summary.mcp_server_errors == 1
        assert error_handler.error_summary.total_errors == 1
    
    @pytest.mark.asyncio
    async def test_handle_wagyu_mcp_error(self, error_handler, mock_logger):
        """Test handling Wagyu MCP server errors."""
        error = WagyuMCPError("Wagyu server timeout")
        context = ErrorContext(operation="fetch_odds", event_id="12345")
        fallback_data = {"odds": []}
        
        result = await error_handler.handle_mcp_error(error, context, fallback_data)
        
        assert result['success'] is False
        assert result['error'] == "Wagyu server timeout"
        assert result['server_type'] == "Wagyu"
        assert result['fallback_data'] == fallback_data
        assert error_handler.error_summary.degraded_operations == 1
    
    @pytest.mark.asyncio
    async def test_handle_llm_error_with_retry(self, error_handler, mock_logger):
        """Test handling LLM errors with retry logic."""
        error = LLMAnalysisError("Analysis failed")
        context = ErrorContext(operation="analyze_game", event_id="12345")
        
        result = await error_handler.handle_llm_error(error, context, retry_count=0)
        
        assert result['success'] is False
        assert result['retry'] is True
        assert result['retry_count'] == 1
        assert 'retry_delay' in result
        assert error_handler.error_summary.llm_analysis_errors == 1
    
    @pytest.mark.asyncio
    async def test_handle_llm_error_max_retries(self, error_handler, mock_logger):
        """Test handling LLM errors after max retries."""
        error = LLMAnalysisError("Analysis failed permanently")
        context = ErrorContext(operation="analyze_game", event_id="12345")
        
        result = await error_handler.handle_llm_error(error, context, retry_count=2)
        
        assert result['success'] is False
        assert 'retry' not in result
        assert result['degraded'] is True
        assert 'fallback_analysis' in result
        assert result['fallback_analysis']['analysis_type'] == 'fallback'
    
    @pytest.mark.asyncio
    async def test_handle_openrouter_error_no_retry(self, error_handler, mock_logger):
        """Test handling OpenRouter errors (no retry)."""
        error = OpenRouterError("API key invalid")
        context = ErrorContext(operation="analyze_game", event_id="12345")
        
        result = await error_handler.handle_llm_error(error, context, retry_count=0)
        
        assert result['success'] is False
        assert 'retry' not in result
        assert result['degraded'] is True
    
    @pytest.mark.asyncio
    async def test_handle_timeout_error(self, error_handler, mock_logger):
        """Test handling timeout errors."""
        error = TimeoutError("Operation timed out", timeout_seconds=30)
        context = ErrorContext(operation="fetch_data", league="mlb")
        
        success, result = await error_handler.handle_error(error, context)
        
        assert success is False
        assert result is None
        assert error_handler.error_summary.timeout_errors == 1
        assert error_handler.error_summary.total_errors == 1
    
    @pytest.mark.asyncio
    async def test_handle_rate_limit_error(self, error_handler, mock_logger):
        """Test handling rate limit errors."""
        error = RateLimitError("Rate limit exceeded", service="wagyu", retry_after=60)
        context = ErrorContext(operation="fetch_odds", league="nfl")
        
        success, result = await error_handler.handle_error(error, context)
        
        assert success is False
        assert result is None
        assert error_handler.error_summary.rate_limit_errors == 1
    
    @pytest.mark.asyncio
    async def test_handle_validation_error(self, error_handler, mock_logger):
        """Test handling validation errors."""
        error = ValidationError("Invalid date format", field="date", value="2024-13-01")
        context = ErrorContext(operation="validate_input")
        
        success, result = await error_handler.handle_error(error, context)
        
        assert success is False
        assert result is None
        assert error_handler.error_summary.validation_errors == 1
        assert len(error_handler.error_summary.critical_failures) == 1
    
    def test_error_classification(self, error_handler):
        """Test error classification for recovery strategies."""
        test_cases = [
            (ESPNMCPError("test"), 'espn_mcp_failure'),
            (WagyuMCPError("test"), 'wagyu_mcp_failure'),
            (LLMAnalysisError("test"), 'llm_analysis_failure'),
            (TimeoutError("test"), 'timeout_failure'),
            (RateLimitError("test"), 'rate_limit_failure'),
            (ValidationError("test"), 'validation_failure'),
            (Exception("test"), 'unknown_error')
        ]
        
        for error, expected_type in test_cases:
            error_type = error_handler._classify_error(error)
            assert error_type == expected_type
    
    def test_error_recording(self, error_handler):
        """Test error recording and tracking."""
        error = ESPNMCPError("Test error")
        context = ErrorContext(operation="test_op", league="nba", event_id="123")
        
        error_handler._record_error(error, context)
        
        assert error_handler.error_summary.total_errors == 1
        assert error_handler.error_summary.errors_by_league["nba"] == 1
        assert error_handler.error_summary.errors_by_operation["test_op"] == 1
        assert len(error_handler.error_history) == 1
        assert error_handler.error_history[0] == (error, context)
    
    def test_fallback_analysis_generation(self, error_handler):
        """Test fallback analysis generation."""
        context = ErrorContext(operation="analyze_game", event_id="12345")
        
        fallback = error_handler._generate_fallback_analysis(context)
        
        assert fallback['analysis_type'] == 'fallback'
        assert fallback['predictions']['winner'] == 'Unable to determine'
        assert fallback['predictions']['confidence'] == 0.0
        assert fallback['key_players'] == []
        assert fallback['betting_recommendations'] == []
        assert fallback['value_bets'] == []
        assert 'error' in fallback
    
    def test_error_aggregation(self, error_handler):
        """Test error aggregation for reporting."""
        # Add various errors
        errors = [
            (ESPNMCPError("ESPN error"), ErrorContext("op1", league="nba")),
            (WagyuMCPError("Wagyu error"), ErrorContext("op2", league="nfl")),
            (LLMAnalysisError("LLM error"), ErrorContext("op1", league="nba")),
            (TimeoutError("Timeout"), ErrorContext("op3", league="mlb"))
        ]
        
        for error, context in errors:
            error_handler._record_error(error, context)
        
        # Add some recovery stats
        error_handler.error_summary.successful_retries = 2
        error_handler.error_summary.failed_retries = 1
        error_handler.error_summary.degraded_operations = 3
        
        aggregated = error_handler.aggregate_errors()
        
        assert aggregated['summary']['total_errors'] == 4
        assert aggregated['summary']['error_breakdown']['mcp_server_errors'] == 2
        assert aggregated['summary']['error_breakdown']['llm_analysis_errors'] == 1
        assert aggregated['summary']['error_breakdown']['timeout_errors'] == 1
        assert aggregated['summary']['recovery_stats']['successful_retries'] == 2
        
        # Check details
        assert 'error_rates_by_league' in aggregated['details']
        assert 'problematic_operations' in aggregated['details']
        assert len(aggregated['recommendations']) > 0
    
    def test_recommendations_generation(self, error_handler):
        """Test recommendation generation based on error patterns."""
        # Simulate high error counts
        error_handler.error_summary.total_errors = 15
        error_handler.error_summary.mcp_server_errors = 8
        error_handler.error_summary.llm_analysis_errors = 5
        error_handler.error_summary.timeout_errors = 3
        error_handler.error_summary.rate_limit_errors = 2
        
        recommendations = error_handler._generate_recommendations()
        
        assert len(recommendations) > 0
        assert any("caching" in rec.lower() for rec in recommendations)
        assert any("mcp server" in rec.lower() for rec in recommendations)
        assert any("llm" in rec.lower() for rec in recommendations)
        assert any("timeout" in rec.lower() for rec in recommendations)
        assert any("rate limit" in rec.lower() for rec in recommendations)
    
    @pytest.mark.asyncio
    async def test_concurrent_error_handling(self, error_handler, mock_logger):
        """Test handling multiple concurrent errors."""
        errors_and_contexts = [
            (ESPNMCPError("ESPN error 1"), ErrorContext("op1", league="nba")),
            (WagyuMCPError("Wagyu error 1"), ErrorContext("op2", league="nfl")),
            (LLMAnalysisError("LLM error 1"), ErrorContext("op3", league="mlb"))
        ]
        
        # Handle errors concurrently
        tasks = [
            error_handler.handle_error(error, context, allow_retry=False)
            for error, context in errors_and_contexts
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should fail without retry
        assert all(not success for success, _ in results)
        assert error_handler.error_summary.total_errors == 3
        assert error_handler.error_summary.mcp_server_errors == 2
        assert error_handler.error_summary.llm_analysis_errors == 1
    
    @pytest.mark.asyncio
    async def test_retry_with_exponential_backoff(self, error_handler, mock_logger):
        """Test retry logic with exponential backoff."""
        error = ESPNMCPError("Temporary failure")
        context = ErrorContext(operation="fetch_data", retry_count=1)
        
        start_time = asyncio.get_event_loop().time()
        success, result = await error_handler._handle_espn_mcp_failure(
            error, context, allow_retry=True
        )
        end_time = asyncio.get_event_loop().time()
        
        # Should have waited for exponential backoff
        expected_delay = error_handler.retry_delay * (2 ** context.retry_count)
        actual_delay = end_time - start_time
        
        assert success is False  # Indicates retry should be attempted
        assert result is None
        assert actual_delay >= expected_delay * 0.9  # Allow for timing variance
    
    def test_error_context_in_logs(self, error_handler, mock_logger):
        """Test that error context is properly logged."""
        error = ValidationError("Test validation error", field="date", value="invalid")
        context = ErrorContext(
            operation="validate_date",
            league="nba",
            event_id="12345",
            duration_ms=150,
            additional_data={"user_input": "invalid_date"}
        )
        
        error_handler._log_error(error, context)
        
        # Verify logger was called with proper extra data
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        
        assert "Error in validate_date" in call_args[0][0]
        extra_data = call_args[1]['extra']
        assert extra_data['operation'] == "validate_date"
        assert extra_data['error_type'] == "ValidationError"
        assert extra_data['league'] == "nba"
        assert extra_data['event_id'] == "12345"
        assert extra_data['duration_ms'] == 150
        assert extra_data['user_input'] == "invalid_date"


@pytest.mark.asyncio
async def test_error_handler_integration():
    """Integration test for complete error handling workflow."""
    handler = ErrorHandler(max_retries=1, retry_delay=0.01)
    
    # Simulate a series of errors during report generation
    errors_to_handle = [
        (ESPNMCPError("ESPN unavailable"), ErrorContext("fetch_games", league="nba")),
        (WagyuMCPError("Wagyu timeout"), ErrorContext("fetch_odds", event_id="123")),
        (LLMAnalysisError("Analysis failed"), ErrorContext("analyze_game", event_id="123")),
        (ValidationError("Invalid input"), ErrorContext("validate_params"))
    ]
    
    results = []
    for error, context in errors_to_handle:
        if isinstance(error, (ESPNMCPError, WagyuMCPError)):
            result = await handler.handle_mcp_error(error, context)
            results.append(result)
        elif isinstance(error, LLMAnalysisError):
            result = await handler.handle_llm_error(error, context)
            results.append(result)
        else:
            success, result = await handler.handle_error(error, context)
            results.append({'success': success, 'result': result})
    
    # Verify error tracking
    assert handler.error_summary.total_errors == 4
    assert handler.error_summary.mcp_server_errors == 2
    assert handler.error_summary.llm_analysis_errors == 1
    assert handler.error_summary.validation_errors == 1
    
    # Verify aggregation
    aggregated = handler.aggregate_errors()
    assert aggregated['summary']['total_errors'] == 4
    assert len(aggregated['recommendations']) > 0
    
    # Verify all operations had some form of handling
    assert len(results) == 4
    assert all('success' in result or 'error' in result for result in results)