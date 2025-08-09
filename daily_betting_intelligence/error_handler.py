"""
Comprehensive error handler for the Daily Betting Intelligence system.

This module provides centralized error handling with graceful degradation,
error aggregation, and detailed reporting for MCP server failures and other issues.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, field

from .exceptions import (
    DailyBettingIntelligenceError,
    MCPServerError,
    ESPNMCPError,
    WagyuMCPError,
    LLMAnalysisError,
    OpenRouterError,
    TimeoutError,
    RateLimitError,
    ConfigurationError,
    ValidationError,
    ReportGenerationError,
    ConcurrencyError,
    InsufficientDataError
)


@dataclass
class ErrorContext:
    """Context information for error tracking and reporting."""
    
    operation: str
    timestamp: datetime = field(default_factory=datetime.now)
    league: Optional[str] = None
    event_id: Optional[str] = None
    retry_count: int = 0
    duration_ms: Optional[int] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorSummary:
    """Summary of errors encountered during report generation."""
    
    total_errors: int = 0
    mcp_server_errors: int = 0
    llm_analysis_errors: int = 0
    timeout_errors: int = 0
    rate_limit_errors: int = 0
    validation_errors: int = 0
    other_errors: int = 0
    
    # Detailed error tracking
    errors_by_league: Dict[str, int] = field(default_factory=dict)
    errors_by_operation: Dict[str, int] = field(default_factory=dict)
    critical_failures: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Recovery statistics
    successful_retries: int = 0
    failed_retries: int = 0
    degraded_operations: int = 0


class ErrorHandler:
    """
    Centralized error handler with graceful degradation and recovery strategies.
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize error handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)
        
        # Error tracking
        self.error_summary = ErrorSummary()
        self.error_history: List[Tuple[Exception, ErrorContext]] = []
        
        # Recovery strategies
        self.fallback_strategies = {
            'espn_mcp_failure': self._handle_espn_mcp_failure,
            'wagyu_mcp_failure': self._handle_wagyu_mcp_failure,
            'llm_analysis_failure': self._handle_llm_analysis_failure,
            'timeout_failure': self._handle_timeout_failure,
            'rate_limit_failure': self._handle_rate_limit_failure,
            'validation_failure': self._handle_validation_failure
        }
    
    async def handle_error(
        self,
        error: Exception,
        context: ErrorContext,
        allow_retry: bool = True
    ) -> Tuple[bool, Optional[Any]]:
        """
        Handle an error with appropriate recovery strategy.
        
        Args:
            error: Exception that occurred
            context: Error context information
            allow_retry: Whether retry is allowed for this error
            
        Returns:
            Tuple of (success, result) where success indicates if error was recovered
        """
        # Record error
        self._record_error(error, context)
        
        # Log error with context
        self._log_error(error, context)
        
        # Determine error type and strategy
        error_type = self._classify_error(error)
        strategy = self.fallback_strategies.get(error_type)
        
        if strategy:
            try:
                # Attempt recovery
                success, result = await strategy(error, context, allow_retry)
                if success:
                    self.error_summary.successful_retries += 1
                    self.logger.info(
                        f"Successfully recovered from {error_type} in {context.operation}",
                        extra={'operation': context.operation, 'error_type': error_type}
                    )
                    return True, result
                else:
                    self.error_summary.failed_retries += 1
            except Exception as recovery_error:
                self.logger.error(
                    f"Recovery strategy failed for {error_type}: {recovery_error}",
                    extra={'operation': context.operation, 'error_type': error_type}
                )
        
        # No recovery possible
        return False, None
    
    async def handle_mcp_error(
        self,
        error: MCPServerError,
        context: ErrorContext,
        fallback_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle MCP server errors with graceful degradation.
        
        Args:
            error: MCP server error
            context: Error context
            fallback_data: Optional fallback data to use
            
        Returns:
            Result dictionary with error information and fallback data
        """
        self._record_error(error, context)
        self.error_summary.mcp_server_errors += 1
        
        # Determine server type
        server_type = "unknown"
        if isinstance(error, ESPNMCPError):
            server_type = "ESPN"
        elif isinstance(error, WagyuMCPError):
            server_type = "Wagyu"
        
        self.logger.error(
            f"{server_type} MCP server error in {context.operation}: {error.message}",
            extra={
                'operation': context.operation,
                'server_type': server_type,
                'league': context.league,
                'event_id': context.event_id
            }
        )
        
        # Return degraded result
        result = {
            'success': False,
            'error': error.message,
            'server_type': server_type,
            'operation': context.operation,
            'degraded': True
        }
        
        if fallback_data:
            result['fallback_data'] = fallback_data
            self.error_summary.degraded_operations += 1
            self.error_summary.warnings.append(
                f"{server_type} MCP unavailable for {context.operation}, using fallback data"
            )
        else:
            self.error_summary.critical_failures.append(
                f"{server_type} MCP failure in {context.operation} with no fallback"
            )
        
        return result
    
    async def handle_llm_error(
        self,
        error: LLMAnalysisError,
        context: ErrorContext,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Handle LLM analysis errors with retry logic.
        
        Args:
            error: LLM analysis error
            context: Error context
            retry_count: Current retry attempt
            
        Returns:
            Result dictionary with error information
        """
        self._record_error(error, context)
        self.error_summary.llm_analysis_errors += 1
        
        # Check if we should retry
        if retry_count < self.max_retries and not isinstance(error, OpenRouterError):
            delay = self.retry_delay * (2 ** retry_count)  # Exponential backoff
            self.logger.warning(
                f"LLM analysis failed, retrying in {delay}s (attempt {retry_count + 1}/{self.max_retries})",
                extra={'operation': context.operation, 'retry_count': retry_count}
            )
            
            await asyncio.sleep(delay)
            return {
                'success': False,
                'retry': True,
                'retry_delay': delay,
                'retry_count': retry_count + 1
            }
        
        # No more retries, return fallback
        self.logger.error(
            f"LLM analysis failed permanently in {context.operation}: {error.message}",
            extra={'operation': context.operation, 'retry_count': retry_count}
        )
        
        return {
            'success': False,
            'error': error.message,
            'operation': context.operation,
            'fallback_analysis': self._generate_fallback_analysis(context),
            'degraded': True
        }
    
    def aggregate_errors(self) -> Dict[str, Any]:
        """
        Aggregate all errors for final report summary.
        
        Returns:
            Dictionary containing error summary and statistics
        """
        # Calculate error rates by league
        total_operations = sum(self.error_summary.errors_by_league.values()) or 1
        error_rates = {
            league: (count / total_operations) * 100
            for league, count in self.error_summary.errors_by_league.items()
        }
        
        # Identify most problematic operations
        problematic_operations = sorted(
            self.error_summary.errors_by_operation.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'summary': {
                'total_errors': self.error_summary.total_errors,
                'error_breakdown': {
                    'mcp_server_errors': self.error_summary.mcp_server_errors,
                    'llm_analysis_errors': self.error_summary.llm_analysis_errors,
                    'timeout_errors': self.error_summary.timeout_errors,
                    'rate_limit_errors': self.error_summary.rate_limit_errors,
                    'validation_errors': self.error_summary.validation_errors,
                    'other_errors': self.error_summary.other_errors
                },
                'recovery_stats': {
                    'successful_retries': self.error_summary.successful_retries,
                    'failed_retries': self.error_summary.failed_retries,
                    'degraded_operations': self.error_summary.degraded_operations
                }
            },
            'details': {
                'error_rates_by_league': error_rates,
                'problematic_operations': problematic_operations,
                'critical_failures': self.error_summary.critical_failures,
                'warnings': self.error_summary.warnings
            },
            'recommendations': self._generate_recommendations()
        }
    
    def _record_error(self, error: Exception, context: ErrorContext):
        """Record error in tracking systems."""
        self.error_summary.total_errors += 1
        self.error_history.append((error, context))
        
        # Update league-specific counts
        if context.league:
            self.error_summary.errors_by_league[context.league] = (
                self.error_summary.errors_by_league.get(context.league, 0) + 1
            )
        
        # Update operation-specific counts
        self.error_summary.errors_by_operation[context.operation] = (
            self.error_summary.errors_by_operation.get(context.operation, 0) + 1
        )
    
    def _log_error(self, error: Exception, context: ErrorContext):
        """Log error with structured information."""
        extra = {
            'operation': context.operation,
            'error_type': type(error).__name__,
            'league': context.league,
            'event_id': context.event_id,
            'retry_count': context.retry_count
        }
        
        if context.duration_ms:
            extra['duration_ms'] = context.duration_ms
        
        if context.additional_data:
            extra.update(context.additional_data)
        
        self.logger.error(
            f"Error in {context.operation}: {str(error)}",
            extra=extra,
            exc_info=True
        )
    
    def _classify_error(self, error: Exception) -> str:
        """Classify error type for recovery strategy selection."""
        if isinstance(error, ESPNMCPError):
            return 'espn_mcp_failure'
        elif isinstance(error, WagyuMCPError):
            return 'wagyu_mcp_failure'
        elif isinstance(error, LLMAnalysisError):
            return 'llm_analysis_failure'
        elif isinstance(error, TimeoutError):
            return 'timeout_failure'
        elif isinstance(error, RateLimitError):
            return 'rate_limit_failure'
        elif isinstance(error, ValidationError):
            return 'validation_failure'
        else:
            return 'unknown_error'
    
    async def _handle_espn_mcp_failure(
        self,
        error: ESPNMCPError,
        context: ErrorContext,
        allow_retry: bool
    ) -> Tuple[bool, Optional[Any]]:
        """Handle ESPN MCP server failures."""
        if allow_retry and context.retry_count < self.max_retries:
            # Exponential backoff retry
            delay = self.retry_delay * (2 ** context.retry_count)
            await asyncio.sleep(delay)
            return False, None  # Indicate retry should be attempted
        
        # Return minimal fallback data
        fallback = {
            'games': [],
            'error': 'ESPN MCP server unavailable',
            'degraded': True
        }
        return True, fallback
    
    async def _handle_wagyu_mcp_failure(
        self,
        error: WagyuMCPError,
        context: ErrorContext,
        allow_retry: bool
    ) -> Tuple[bool, Optional[Any]]:
        """Handle Wagyu MCP server failures."""
        if allow_retry and context.retry_count < self.max_retries:
            delay = self.retry_delay * (2 ** context.retry_count)
            await asyncio.sleep(delay)
            return False, None
        
        # Return empty odds data
        fallback = {
            'odds': [],
            'player_props': [],
            'error': 'Wagyu MCP server unavailable',
            'degraded': True
        }
        return True, fallback
    
    async def _handle_llm_analysis_failure(
        self,
        error: LLMAnalysisError,
        context: ErrorContext,
        allow_retry: bool
    ) -> Tuple[bool, Optional[Any]]:
        """Handle LLM analysis failures."""
        if allow_retry and context.retry_count < self.max_retries:
            delay = self.retry_delay * (2 ** context.retry_count)
            await asyncio.sleep(delay)
            return False, None
        
        # Return basic analysis template
        fallback = self._generate_fallback_analysis(context)
        return True, fallback
    
    async def _handle_timeout_failure(
        self,
        error: TimeoutError,
        context: ErrorContext,
        allow_retry: bool
    ) -> Tuple[bool, Optional[Any]]:
        """Handle timeout failures."""
        self.error_summary.timeout_errors += 1
        
        if allow_retry and context.retry_count < 2:  # Fewer retries for timeouts
            delay = self.retry_delay * 2  # Longer delay for timeouts
            await asyncio.sleep(delay)
            return False, None
        
        return False, None  # No fallback for timeouts
    
    async def _handle_rate_limit_failure(
        self,
        error: RateLimitError,
        context: ErrorContext,
        allow_retry: bool
    ) -> Tuple[bool, Optional[Any]]:
        """Handle rate limit failures."""
        self.error_summary.rate_limit_errors += 1
        
        if allow_retry and hasattr(error, 'retry_after') and error.retry_after:
            # Wait for the specified retry period
            await asyncio.sleep(error.retry_after)
            return False, None
        
        return False, None  # No fallback for rate limits
    
    async def _handle_validation_failure(
        self,
        error: ValidationError,
        context: ErrorContext,
        allow_retry: bool
    ) -> Tuple[bool, Optional[Any]]:
        """Handle validation failures."""
        self.error_summary.validation_errors += 1
        
        # Validation errors typically don't benefit from retries
        self.error_summary.critical_failures.append(
            f"Validation error in {context.operation}: {error.message}"
        )
        
        return False, None
    
    def _generate_fallback_analysis(self, context: ErrorContext) -> Dict[str, Any]:
        """Generate basic fallback analysis when LLM fails."""
        return {
            'analysis_type': 'fallback',
            'predictions': {
                'winner': 'Unable to determine',
                'confidence': 0.0,
                'reasoning': 'LLM analysis unavailable'
            },
            'key_players': [],
            'betting_recommendations': [],
            'value_bets': [],
            'error': 'LLM analysis failed, using fallback template'
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on error patterns."""
        recommendations = []
        
        # High error rate recommendations
        if self.error_summary.total_errors > 10:
            recommendations.append(
                "Consider implementing additional caching to reduce API calls"
            )
        
        # MCP server specific recommendations
        if self.error_summary.mcp_server_errors > 5:
            recommendations.append(
                "Check MCP server connectivity and consider implementing circuit breakers"
            )
        
        # LLM error recommendations
        if self.error_summary.llm_analysis_errors > 3:
            recommendations.append(
                "Review LLM prompts and consider implementing more robust fallback analysis"
            )
        
        # Timeout recommendations
        if self.error_summary.timeout_errors > 2:
            recommendations.append(
                "Consider increasing timeout values or implementing request prioritization"
            )
        
        # Rate limit recommendations
        if self.error_summary.rate_limit_errors > 0:
            recommendations.append(
                "Implement more aggressive rate limiting and request batching"
            )
        
        return recommendations