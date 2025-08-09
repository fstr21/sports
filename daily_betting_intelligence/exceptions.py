"""
Custom exceptions for the Daily Betting Intelligence system.

This module defines specific exception types for different error conditions
that can occur during data fetching, analysis, and report generation.
"""


class DailyBettingIntelligenceError(Exception):
    """Base exception for all Daily Betting Intelligence system errors."""
    
    def __init__(self, message: str, context: dict = None):
        super().__init__(message)
        self.message = message
        self.context = context or {}


class DataFetchError(DailyBettingIntelligenceError):
    """Raised when data fetching operations fail."""
    
    def __init__(self, message: str, source: str = None, context: dict = None):
        super().__init__(message, context)
        self.source = source


class MCPServerError(DataFetchError):
    """Raised when MCP server operations fail."""
    
    def __init__(self, message: str, server_type: str = None, context: dict = None):
        super().__init__(message, server_type, context)
        self.server_type = server_type


class ESPNMCPError(MCPServerError):
    """Raised when ESPN MCP server operations fail."""
    
    def __init__(self, message: str, context: dict = None):
        super().__init__(message, "ESPN", context)


class WagyuMCPError(MCPServerError):
    """Raised when Wagyu MCP server operations fail."""
    
    def __init__(self, message: str, context: dict = None):
        super().__init__(message, "Wagyu", context)


class AnalysisError(DailyBettingIntelligenceError):
    """Raised when analysis operations fail."""
    
    def __init__(self, message: str, analysis_type: str = None, context: dict = None):
        super().__init__(message, context)
        self.analysis_type = analysis_type


class LLMAnalysisError(AnalysisError):
    """Raised when LLM analysis operations fail."""
    
    def __init__(self, message: str, context: dict = None):
        super().__init__(message, "LLM", context)


class OpenRouterError(LLMAnalysisError):
    """Raised when OpenRouter API operations fail."""
    
    def __init__(self, message: str, context: dict = None):
        super().__init__(message, context)


class ConfigurationError(DailyBettingIntelligenceError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_key: str = None, context: dict = None):
        super().__init__(message, context)
        self.config_key = config_key


class ValidationError(DailyBettingIntelligenceError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: str = None, value: str = None, context: dict = None):
        super().__init__(message, context)
        self.field = field
        self.value = value


class DateValidationError(ValidationError):
    """Raised when date validation fails."""
    
    def __init__(self, message: str, date_value: str = None, context: dict = None):
        super().__init__(message, "date", date_value, context)


class LeagueValidationError(ValidationError):
    """Raised when league validation fails."""
    
    def __init__(self, message: str, league_value: str = None, context: dict = None):
        super().__init__(message, "league", league_value, context)


class MarketValidationError(ValidationError):
    """Raised when betting market validation fails."""
    
    def __init__(self, message: str, market_value: str = None, context: dict = None):
        super().__init__(message, "market", market_value, context)


class ReportGenerationError(DailyBettingIntelligenceError):
    """Raised when report generation fails."""
    
    def __init__(self, message: str, report_type: str = None, context: dict = None):
        super().__init__(message, context)
        self.report_type = report_type


class FormattingError(ReportGenerationError):
    """Raised when report formatting fails."""
    
    def __init__(self, message: str, format_type: str = None, context: dict = None):
        super().__init__(message, format_type, context)


class CacheError(DailyBettingIntelligenceError):
    """Raised when cache operations fail."""
    
    def __init__(self, message: str, operation: str = None, context: dict = None):
        super().__init__(message, context)
        self.operation = operation


class TimeoutError(DailyBettingIntelligenceError):
    """Raised when operations exceed timeout limits."""
    
    def __init__(self, message: str, timeout_seconds: int = None, context: dict = None):
        super().__init__(message, context)
        self.timeout_seconds = timeout_seconds


class RateLimitError(DailyBettingIntelligenceError):
    """Raised when API rate limits are exceeded."""
    
    def __init__(self, message: str, service: str = None, retry_after: int = None, context: dict = None):
        super().__init__(message, context)
        self.service = service
        self.retry_after = retry_after


class InsufficientDataError(DailyBettingIntelligenceError):
    """Raised when insufficient data is available for analysis."""
    
    def __init__(self, message: str, required_data: str = None, context: dict = None):
        super().__init__(message, context)
        self.required_data = required_data


class OddsDataError(DataFetchError):
    """Raised when betting odds data is invalid or unavailable."""
    
    def __init__(self, message: str, event_id: str = None, context: dict = None):
        super().__init__(message, "odds", context)
        self.event_id = event_id


class PlayerPropError(DataFetchError):
    """Raised when player prop data is invalid or unavailable."""
    
    def __init__(self, message: str, player_name: str = None, prop_type: str = None, context: dict = None):
        super().__init__(message, "player_props", context)
        self.player_name = player_name
        self.prop_type = prop_type


class ConcurrencyError(DailyBettingIntelligenceError):
    """Raised when concurrent processing fails."""
    
    def __init__(self, message: str, max_concurrent: int = None, context: dict = None):
        super().__init__(message, context)
        self.max_concurrent = max_concurrent