"""
Soccer Discord Integration - Comprehensive Error Handling and Logging System
Provides robust error handling, retry logic, and user-friendly error messages
"""

import asyncio
import logging
import traceback
import functools
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass
from enum import Enum
import discord
import httpx

# ============================================================================
# ERROR HANDLING CONFIGURATION
# ============================================================================

# Retry configuration
MAX_RETRIES = 3
BASE_RETRY_DELAY = 1.0  # seconds
MAX_RETRY_DELAY = 30.0  # seconds
EXPONENTIAL_BACKOFF_MULTIPLIER = 2.0

# Timeout configuration
DEFAULT_MCP_TIMEOUT = 30.0
DISCORD_API_TIMEOUT = 15.0

# Rate limiting configuration
RATE_LIMIT_RETRY_DELAY = 60.0  # seconds
MAX_RATE_LIMIT_RETRIES = 3

# ============================================================================
# ERROR SEVERITY LEVELS
# ============================================================================

class ErrorSeverity(Enum):
    """Error severity levels for logging and user notification"""
    LOW = "low"           # Minor issues, graceful degradation possible
    MEDIUM = "medium"     # Significant issues, partial functionality affected
    HIGH = "high"         # Major issues, core functionality affected
    CRITICAL = "critical" # System-breaking issues, immediate attention required

# ============================================================================
# ENHANCED EXCEPTION CLASSES
# ============================================================================

@dataclass
class ErrorContext:
    """Context information for error handling"""
    operation: str
    user_id: Optional[int] = None
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    match_id: Optional[int] = None
    team_ids: Optional[List[int]] = None
    league_id: Optional[int] = None
    timestamp: datetime = None
    additional_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.additional_data is None:
            self.additional_data = {}

class SoccerBotError(Exception):
    """Base exception for Soccer Discord Bot operations"""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 context: Optional[ErrorContext] = None, user_message: Optional[str] = None):
        super().__init__(message)
        self.severity = severity
        self.context = context or ErrorContext("unknown")
        self.user_message = user_message or self._generate_user_message()
        self.timestamp = datetime.utcnow()
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly error message"""
        return "An error occurred while processing your request. Please try again later."

class MCPConnectionError(SoccerBotError):
    """MCP server connection issues with retry logic"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 retry_count: int = 0, context: Optional[ErrorContext] = None):
        self.status_code = status_code
        self.retry_count = retry_count
        
        user_msg = self._generate_connection_user_message(status_code, retry_count)
        super().__init__(message, ErrorSeverity.HIGH, context, user_msg)
    
    def _generate_connection_user_message(self, status_code: Optional[int], retry_count: int) -> str:
        """Generate user-friendly message for connection errors"""
        if retry_count >= MAX_RETRIES:
            return ("⚠️ **Soccer data service is currently unavailable**\n"
                   "Please try again in a few minutes. If the issue persists, contact an administrator.")
        elif status_code == 429:
            return ("⏳ **Rate limit reached**\n"
                   "Too many requests to the soccer data service. Please wait a moment and try again.")
        elif status_code and status_code >= 500:
            return ("🔧 **Soccer data service is experiencing issues**\n"
                   "The service is temporarily down. Please try again shortly.")
        else:
            return ("🌐 **Connection issue**\n"
                   "Unable to connect to soccer data service. Retrying automatically...")

class MCPTimeoutError(SoccerBotError):
    """MCP server timeout with retry suggestions"""
    
    def __init__(self, message: str, timeout_duration: float, context: Optional[ErrorContext] = None):
        self.timeout_duration = timeout_duration
        user_msg = (f"⏱️ **Request timed out**\n"
                   f"The soccer data service took too long to respond ({timeout_duration}s). "
                   f"Please try again with a smaller date range or specific teams.")
        super().__init__(message, ErrorSeverity.MEDIUM, context, user_msg)

class MCPDataError(SoccerBotError):
    """Invalid or missing data from MCP with graceful degradation"""
    
    def __init__(self, message: str, data_type: str = "unknown", 
                 partial_data_available: bool = False, context: Optional[ErrorContext] = None):
        self.data_type = data_type
        self.partial_data_available = partial_data_available
        
        user_msg = self._generate_data_error_message(data_type, partial_data_available)
        severity = ErrorSeverity.LOW if partial_data_available else ErrorSeverity.MEDIUM
        super().__init__(message, severity, context, user_msg)
    
    def _generate_data_error_message(self, data_type: str, partial_available: bool) -> str:
        """Generate user-friendly message for data errors"""
        if partial_available:
            return (f"📊 **Partial {data_type} data available**\n"
                   f"Some information may be missing, but displaying what's available.")
        else:
            return (f"📋 **{data_type.title()} data unavailable**\n"
                   f"Unable to retrieve {data_type} information. Please try again later.")

class DiscordAPIError(SoccerBotError):
    """Discord API errors with permission and rate limit handling"""
    
    def __init__(self, message: str, error_code: Optional[int] = None, 
                 retry_after: Optional[float] = None, context: Optional[ErrorContext] = None):
        self.error_code = error_code
        self.retry_after = retry_after
        
        user_msg = self._generate_discord_error_message(error_code, retry_after)
        severity = ErrorSeverity.HIGH if error_code in [403, 404] else ErrorSeverity.MEDIUM
        super().__init__(message, severity, context, user_msg)
    
    def _generate_discord_error_message(self, error_code: Optional[int], retry_after: Optional[float]) -> str:
        """Generate user-friendly message for Discord API errors"""
        if error_code == 403:
            return ("🔒 **Permission denied**\n"
                   "The bot doesn't have permission to perform this action. "
                   "Please contact an administrator to check bot permissions.")
        elif error_code == 404:
            return ("🔍 **Channel or resource not found**\n"
                   "The requested channel or resource no longer exists.")
        elif error_code == 429:
            wait_time = int(retry_after) if retry_after else 60
            return (f"⏳ **Rate limited**\n"
                   f"Discord API rate limit reached. Please wait {wait_time} seconds and try again.")
        elif error_code and error_code >= 500:
            return ("🔧 **Discord service issues**\n"
                   "Discord is experiencing technical difficulties. Please try again later.")
        else:
            return ("⚠️ **Discord API error**\n"
                   "An error occurred while communicating with Discord. Please try again.")

class ValidationError(SoccerBotError):
    """Input validation errors with helpful guidance"""
    
    def __init__(self, message: str, field_name: str, provided_value: Any, 
                 expected_format: str, context: Optional[ErrorContext] = None):
        self.field_name = field_name
        self.provided_value = provided_value
        self.expected_format = expected_format
        
        user_msg = self._generate_validation_message(field_name, provided_value, expected_format)
        super().__init__(message, ErrorSeverity.LOW, context, user_msg)
    
    def _generate_validation_message(self, field_name: str, provided_value: Any, expected_format: str) -> str:
        """Generate user-friendly validation error message"""
        return (f"❌ **Invalid {field_name}**\n"
               f"You provided: `{provided_value}`\n"
               f"Expected format: `{expected_format}`\n"
               f"Please check your input and try again.")

# ============================================================================
# RETRY DECORATOR WITH EXPONENTIAL BACKOFF
# ============================================================================

def retry_with_backoff(
    max_retries: int = MAX_RETRIES,
    base_delay: float = BASE_RETRY_DELAY,
    max_delay: float = MAX_RETRY_DELAY,
    backoff_multiplier: float = EXPONENTIAL_BACKOFF_MULTIPLIER,
    exceptions: tuple = (MCPConnectionError, MCPTimeoutError, httpx.RequestError, httpx.TimeoutException)
):
    """
    Decorator for implementing retry logic with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_multiplier: Multiplier for exponential backoff
        exceptions: Tuple of exceptions that should trigger retries
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        # Final attempt failed, raise the last exception
                        if isinstance(e, MCPConnectionError):
                            e.retry_count = attempt
                        raise e
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (backoff_multiplier ** attempt), max_delay)
                    
                    # Add jitter to prevent thundering herd
                    import random
                    jitter = random.uniform(0.1, 0.3) * delay
                    total_delay = delay + jitter
                    
                    # Log retry attempt
                    logger = logging.getLogger(f"{func.__module__}.{func.__name__}")
                    logger.warning(f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                                 f"Retrying in {total_delay:.2f}s...")
                    
                    await asyncio.sleep(total_delay)
                except Exception as e:
                    # Non-retryable exception, raise immediately
                    raise e
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator

# ============================================================================
# GRACEFUL DEGRADATION UTILITIES
# ============================================================================

class GracefulDegradation:
    """Utilities for handling partial data availability and graceful degradation"""
    
    @staticmethod
    def create_partial_match_data(match_data: Dict[str, Any], missing_fields: List[str]) -> Dict[str, Any]:
        """
        Create match data with graceful handling of missing fields
        
        Args:
            match_data: Original match data (potentially incomplete)
            missing_fields: List of fields that are missing or invalid
            
        Returns:
            Match data with default values for missing fields
        """
        defaults = {
            'odds': None,
            'h2h_summary': None,
            'venue': 'TBD',
            'time': 'TBD',
            'league_position': None,
            'recent_form': None
        }
        
        # Apply defaults for missing fields
        for field in missing_fields:
            if field in defaults:
                match_data[field] = defaults[field]
        
        # Add metadata about missing data
        match_data['_partial_data'] = True
        match_data['_missing_fields'] = missing_fields
        
        return match_data
    
    @staticmethod
    def create_fallback_embed(title: str, error_message: str, 
                            suggestions: Optional[List[str]] = None) -> discord.Embed:
        """
        Create a fallback embed for error scenarios
        
        Args:
            title: Error title
            error_message: User-friendly error message
            suggestions: Optional list of suggestions for the user
            
        Returns:
            Discord embed with error information and suggestions
        """
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=error_message,
            color=0xff6b6b,  # Red color for errors
            timestamp=datetime.utcnow()
        )
        
        if suggestions:
            suggestions_text = "\n".join([f"• {suggestion}" for suggestion in suggestions])
            embed.add_field(
                name="💡 Suggestions",
                value=suggestions_text,
                inline=False
            )
        
        embed.set_footer(text="If the issue persists, please contact an administrator")
        return embed
    
    @staticmethod
    def extract_available_data(data: Dict[str, Any], required_fields: List[str]) -> tuple[Dict[str, Any], List[str]]:
        """
        Extract available data and identify missing fields
        
        Args:
            data: Raw data dictionary
            required_fields: List of required field names
            
        Returns:
            Tuple of (available_data, missing_fields)
        """
        available_data = {}
        missing_fields = []
        
        for field in required_fields:
            if field in data and data[field] is not None:
                available_data[field] = data[field]
            else:
                missing_fields.append(field)
        
        return available_data, missing_fields

# ============================================================================
# ENHANCED LOGGING SYSTEM
# ============================================================================

class SoccerBotLogger:
    """Enhanced logging system for soccer bot operations"""
    
    def __init__(self, name: str = "soccer_bot"):
        self.logger = logging.getLogger(name)
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup comprehensive logging configuration"""
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # File handler for errors
        error_handler = logging.FileHandler('soccer_bot_errors.log')
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        
        # File handler for all logs
        debug_handler = logging.FileHandler('soccer_bot_debug.log')
        debug_handler.setFormatter(formatter)
        debug_handler.setLevel(logging.DEBUG)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(debug_handler)
        
        # Set logger level
        self.logger.setLevel(logging.DEBUG)
    
    def log_operation_start(self, operation: str, context: ErrorContext):
        """Log the start of an operation"""
        self.logger.info(f"Starting operation: {operation}", extra={
            'operation': operation,
            'user_id': context.user_id,
            'guild_id': context.guild_id,
            'channel_id': context.channel_id,
            'additional_data': context.additional_data
        })
    
    def log_operation_success(self, operation: str, context: ErrorContext, 
                            duration: Optional[float] = None, result_summary: Optional[str] = None):
        """Log successful operation completion"""
        message = f"Operation completed successfully: {operation}"
        if duration:
            message += f" (took {duration:.2f}s)"
        if result_summary:
            message += f" - {result_summary}"
        
        self.logger.info(message, extra={
            'operation': operation,
            'user_id': context.user_id,
            'guild_id': context.guild_id,
            'duration': duration,
            'result_summary': result_summary
        })
    
    def log_operation_error(self, operation: str, error: Exception, context: ErrorContext):
        """Log operation error with full context"""
        self.logger.error(f"Operation failed: {operation} - {str(error)}", extra={
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'user_id': context.user_id,
            'guild_id': context.guild_id,
            'channel_id': context.channel_id,
            'traceback': traceback.format_exc(),
            'additional_data': context.additional_data
        })
    
    def log_retry_attempt(self, operation: str, attempt: int, max_attempts: int, 
                         error: Exception, delay: float):
        """Log retry attempt"""
        self.logger.warning(f"Retry {attempt}/{max_attempts} for {operation}: {str(error)}. "
                          f"Waiting {delay:.2f}s before next attempt.")
    
    def log_graceful_degradation(self, operation: str, missing_data: List[str], 
                               available_data: List[str], context: ErrorContext):
        """Log graceful degradation scenario"""
        self.logger.warning(f"Graceful degradation for {operation}: "
                          f"Missing {missing_data}, Available {available_data}", extra={
            'operation': operation,
            'missing_data': missing_data,
            'available_data': available_data,
            'user_id': context.user_id,
            'guild_id': context.guild_id
        })

# ============================================================================
# ERROR HANDLING UTILITIES
# ============================================================================

class ErrorHandler:
    """Central error handling utilities"""
    
    def __init__(self):
        self.logger = SoccerBotLogger("error_handler")
    
    async def handle_mcp_error(self, error: Exception, context: ErrorContext) -> Dict[str, Any]:
        """
        Handle MCP server errors with appropriate response
        
        Args:
            error: The exception that occurred
            context: Error context information
            
        Returns:
            Dictionary with error handling result and user message
        """
        if isinstance(error, httpx.TimeoutException):
            mcp_error = MCPTimeoutError(
                f"MCP server timeout during {context.operation}",
                DEFAULT_MCP_TIMEOUT,
                context
            )
        elif isinstance(error, httpx.HTTPStatusError):
            mcp_error = MCPConnectionError(
                f"MCP server HTTP error: {error.response.status_code}",
                error.response.status_code,
                context=context
            )
        elif isinstance(error, httpx.RequestError):
            mcp_error = MCPConnectionError(
                f"MCP server connection error: {str(error)}",
                context=context
            )
        else:
            mcp_error = MCPDataError(
                f"MCP server data error: {str(error)}",
                context.operation,
                context=context
            )
        
        self.logger.log_operation_error(context.operation, mcp_error, context)
        
        return {
            'success': False,
            'error': mcp_error,
            'user_message': mcp_error.user_message,
            'retry_recommended': isinstance(mcp_error, (MCPConnectionError, MCPTimeoutError))
        }
    
    async def handle_discord_error(self, error: discord.DiscordException, 
                                 context: ErrorContext) -> Dict[str, Any]:
        """
        Handle Discord API errors
        
        Args:
            error: Discord exception
            context: Error context information
            
        Returns:
            Dictionary with error handling result and user message
        """
        if isinstance(error, discord.HTTPException):
            if error.status == 429:  # Rate limited
                discord_error = DiscordAPIError(
                    f"Discord rate limit during {context.operation}",
                    429,
                    getattr(error, 'retry_after', None),
                    context
                )
            elif error.status == 403:  # Forbidden
                discord_error = DiscordAPIError(
                    f"Discord permission error during {context.operation}",
                    403,
                    context=context
                )
            elif error.status == 404:  # Not found
                discord_error = DiscordAPIError(
                    f"Discord resource not found during {context.operation}",
                    404,
                    context=context
                )
            else:
                discord_error = DiscordAPIError(
                    f"Discord HTTP error during {context.operation}: {error.status}",
                    error.status,
                    context=context
                )
        else:
            discord_error = DiscordAPIError(
                f"Discord API error during {context.operation}: {str(error)}",
                context=context
            )
        
        self.logger.log_operation_error(context.operation, discord_error, context)
        
        return {
            'success': False,
            'error': discord_error,
            'user_message': discord_error.user_message,
            'retry_recommended': isinstance(discord_error, DiscordAPIError) and discord_error.error_code == 429
        }
    
    def create_error_embed(self, error: SoccerBotError, 
                          suggestions: Optional[List[str]] = None) -> discord.Embed:
        """
        Create a user-friendly error embed
        
        Args:
            error: The soccer bot error
            suggestions: Optional suggestions for the user
            
        Returns:
            Discord embed with error information
        """
        # Color based on severity
        colors = {
            ErrorSeverity.LOW: 0xffd93d,      # Yellow
            ErrorSeverity.MEDIUM: 0xff6b35,   # Orange
            ErrorSeverity.HIGH: 0xff4757,     # Red
            ErrorSeverity.CRITICAL: 0x8b0000  # Dark red
        }
        
        embed = discord.Embed(
            title="⚠️ Error",
            description=error.user_message,
            color=colors.get(error.severity, 0xff4757),
            timestamp=error.timestamp
        )
        
        # Add operation context if available
        if error.context and error.context.operation != "unknown":
            embed.add_field(
                name="Operation",
                value=error.context.operation.replace("_", " ").title(),
                inline=True
            )
        
        # Add suggestions if provided
        if suggestions:
            suggestions_text = "\n".join([f"• {suggestion}" for suggestion in suggestions])
            embed.add_field(
                name="💡 What you can try",
                value=suggestions_text,
                inline=False
            )
        
        # Add footer based on severity
        if error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            embed.set_footer(text="If this error persists, please contact an administrator")
        else:
            embed.set_footer(text="This is usually a temporary issue")
        
        return embed

# ============================================================================
# GLOBAL ERROR HANDLER INSTANCE
# ============================================================================

# Global instances for easy access
error_handler = ErrorHandler()
bot_logger = SoccerBotLogger()