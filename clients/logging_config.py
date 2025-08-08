"""
Logging configuration for sports MCP clients.

This module provides structured logging with configurable verbosity levels:
- DEBUG: Full ESPN URLs and timing from MCP responses
- INFO: League/date/event and OK/ERR status only
- JSON format support for structured logs
"""

import json
import logging
import os
import sys
import time
from typing import Any, Dict, Optional
from datetime import datetime


class MCPFormatter(logging.Formatter):
    """Custom formatter for MCP client logging with structured output support."""
    
    def __init__(self, use_json: bool = False):
        self.use_json = use_json
        if use_json:
            super().__init__()
        else:
            # Human-readable format
            super().__init__(
                fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
    
    def format(self, record: logging.LogRecord) -> str:
        if self.use_json:
            # Structured JSON format
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            
            # Add extra fields if present
            if hasattr(record, 'mcp_operation'):
                log_entry['mcp_operation'] = record.mcp_operation
            if hasattr(record, 'league'):
                log_entry['league'] = record.league
            if hasattr(record, 'event_id'):
                log_entry['event_id'] = record.event_id
            if hasattr(record, 'espn_url'):
                log_entry['espn_url'] = record.espn_url
            if hasattr(record, 'response_time_ms'):
                log_entry['response_time_ms'] = record.response_time_ms
            if hasattr(record, 'status'):
                log_entry['status'] = record.status
            if hasattr(record, 'error_type'):
                log_entry['error_type'] = record.error_type
            
            return json.dumps(log_entry)
        else:
            return super().format(record)


class MCPLogger:
    """
    Centralized logger for MCP operations with timing and structured logging support.
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._operation_start_times: Dict[str, float] = {}
    
    def start_operation(self, operation: str, league: str, **kwargs) -> str:
        """
        Start timing an MCP operation.
        
        Args:
            operation: Operation name (e.g., 'scoreboard', 'game_summary')
            league: League being queried
            **kwargs: Additional context (event_id, date, etc.)
            
        Returns:
            Operation ID for tracking
        """
        operation_id = f"{operation}_{league}_{int(time.time() * 1000)}"
        self._operation_start_times[operation_id] = time.time()
        
        # Log operation start at DEBUG level
        extra = {
            'mcp_operation': operation,
            'league': league,
            **kwargs
        }
        
        if self.logger.isEnabledFor(logging.DEBUG):
            context_str = f" with {kwargs}" if kwargs else ""
            self.logger.debug(f"Starting MCP {operation} for {league}{context_str}", extra=extra)
        
        return operation_id
    
    def log_success(self, operation_id: str, operation: str, league: str, 
                   espn_url: Optional[str] = None, response_data: Optional[Dict] = None, **kwargs):
        """
        Log successful MCP operation completion.
        
        Args:
            operation_id: Operation ID from start_operation
            operation: Operation name
            league: League that was queried
            espn_url: ESPN URL that was called (if available in response)
            response_data: MCP response data for extracting metadata
            **kwargs: Additional context
        """
        # Calculate timing
        start_time = self._operation_start_times.pop(operation_id, time.time())
        response_time_ms = int((time.time() - start_time) * 1000)
        
        extra = {
            'mcp_operation': operation,
            'league': league,
            'status': 'OK',
            'response_time_ms': response_time_ms,
            **kwargs
        }
        
        if espn_url:
            extra['espn_url'] = espn_url
        
        # DEBUG level: Full details including URLs and timing
        if self.logger.isEnabledFor(logging.DEBUG):
            url_info = f" (ESPN: {espn_url})" if espn_url else ""
            self.logger.debug(
                f"MCP {operation} for {league} completed in {response_time_ms}ms{url_info}",
                extra=extra
            )
        # INFO level: Just operation status
        elif self.logger.isEnabledFor(logging.INFO):
            context_str = f"/{kwargs.get('event_id', '')}" if kwargs.get('event_id') else ""
            date_str = f" on {kwargs.get('date', '')}" if kwargs.get('date') else ""
            self.logger.info(
                f"{league}{context_str}{date_str}: OK ({response_time_ms}ms)",
                extra=extra
            )
    
    def log_error(self, operation_id: str, operation: str, league: str, 
                  error: Exception, error_type: str = 'unknown_error', 
                  espn_url: Optional[str] = None, **kwargs):
        """
        Log failed MCP operation.
        
        Args:
            operation_id: Operation ID from start_operation
            operation: Operation name
            league: League that was queried
            error: Exception that occurred
            error_type: Type of error (upstream_error, validation_error, etc.)
            espn_url: ESPN URL that failed (if available)
            **kwargs: Additional context
        """
        # Calculate timing
        start_time = self._operation_start_times.pop(operation_id, time.time())
        response_time_ms = int((time.time() - start_time) * 1000)
        
        extra = {
            'mcp_operation': operation,
            'league': league,
            'status': 'ERR',
            'error_type': error_type,
            'response_time_ms': response_time_ms,
            **kwargs
        }
        
        if espn_url:
            extra['espn_url'] = espn_url
        
        # DEBUG level: Full error details
        if self.logger.isEnabledFor(logging.DEBUG):
            url_info = f" (ESPN: {espn_url})" if espn_url else ""
            self.logger.error(
                f"MCP {operation} for {league} failed after {response_time_ms}ms{url_info}: {error}",
                extra=extra,
                exc_info=True
            )
        # INFO level: Just error status
        elif self.logger.isEnabledFor(logging.INFO):
            context_str = f"/{kwargs.get('event_id', '')}" if kwargs.get('event_id') else ""
            date_str = f" on {kwargs.get('date', '')}" if kwargs.get('date') else ""
            self.logger.error(
                f"{league}{context_str}{date_str}: ERR ({error_type})",
                extra=extra
            )
    
    def log_mcp_response(self, operation: str, response: Dict[str, Any]):
        """
        Log raw MCP response for debugging purposes.
        
        Args:
            operation: Operation name
            response: Raw MCP response
        """
        if self.logger.isEnabledFor(logging.DEBUG):
            # Truncate very large responses for readability
            response_str = json.dumps(response, indent=2)
            if len(response_str) > 2000:
                response_str = response_str[:2000] + "... [truncated]"
            
            self.logger.debug(f"Raw MCP response for {operation}:\n{response_str}")


def setup_logging(level: str = None, log_format: str = None) -> None:
    """
    Configure logging for MCP clients.
    
    Args:
        level: Log level override (DEBUG, INFO, WARNING, ERROR)
        log_format: Format override ('json' for structured logs)
    """
    # Get configuration from environment variables
    log_level = level or os.getenv('LOG_LEVEL', 'INFO').upper()
    log_format_env = log_format or os.getenv('LOG_FORMAT', 'text').lower()
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Set formatter based on format preference
    use_json = log_format_env == 'json'
    formatter = MCPFormatter(use_json=use_json)
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    # MCP client loggers
    for logger_name in ['clients.core_mcp', 'clients.scoreboard_cli', 'clients.game_cli', 
                       'clients.season_cli', 'clients.odds_cli', 'clients.chat_cli']:
        logger = logging.getLogger(logger_name)
        logger.setLevel(numeric_level)
    
    # Suppress noisy third-party loggers unless DEBUG
    if numeric_level > logging.DEBUG:
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.WARNING)
    
    # Log configuration
    config_logger = logging.getLogger('clients.logging_config')
    config_logger.info(f"Logging configured: level={log_level}, format={log_format_env}")


def get_mcp_logger(name: str) -> MCPLogger:
    """
    Get an MCPLogger instance for the given module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        MCPLogger instance
    """
    return MCPLogger(name)


# Auto-configure logging when module is imported
if not logging.getLogger().handlers:
    setup_logging()