"""
Enhanced logging configuration for the Daily Betting Intelligence system.

This module extends the base MCP logging with specific configurations for
daily report generation, error tracking, and performance monitoring.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from clients.logging_config import MCPFormatter, MCPLogger


class DailyBettingFormatter(MCPFormatter):
    """Enhanced formatter for daily betting intelligence with additional context."""
    
    def format(self, record: logging.LogRecord) -> str:
        if self.use_json:
            # Enhanced JSON format with betting-specific fields
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            
            # Add betting intelligence specific fields
            betting_fields = [
                'operation', 'league', 'event_id', 'date', 'market_type',
                'sportsbook', 'player_name', 'prop_type', 'analysis_type',
                'confidence_score', 'error_type', 'retry_count', 'degraded',
                'response_time_ms', 'espn_url', 'odds_count', 'games_processed'
            ]
            
            for field in betting_fields:
                if hasattr(record, field):
                    log_entry[field] = getattr(record, field)
            
            return json.dumps(log_entry)
        else:
            # Enhanced human-readable format
            base_format = super().format(record)
            
            # Add context information if available
            context_parts = []
            if hasattr(record, 'league'):
                context_parts.append(f"league={record.league}")
            if hasattr(record, 'event_id'):
                context_parts.append(f"event={record.event_id}")
            if hasattr(record, 'market_type'):
                context_parts.append(f"market={record.market_type}")
            if hasattr(record, 'confidence_score'):
                context_parts.append(f"confidence={record.confidence_score:.2f}")
            
            if context_parts:
                context_str = f" [{', '.join(context_parts)}]"
                return base_format + context_str
            
            return base_format


class DailyBettingLogger(MCPLogger):
    """
    Enhanced logger for daily betting intelligence operations with specialized methods.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self._report_start_time: Optional[float] = None
        self._games_processed = 0
        self._leagues_processed = 0
    
    def start_daily_report(self, target_date: str, leagues: list, markets: list):
        """
        Start timing a daily report generation.
        
        Args:
            target_date: Target date for report
            leagues: List of leagues to process
            markets: List of betting markets to analyze
        """
        self._report_start_time = time.time()
        self._games_processed = 0
        self._leagues_processed = 0
        
        extra = {
            'operation': 'daily_report',
            'date': target_date,
            'leagues_count': len(leagues),
            'markets_count': len(markets)
        }
        
        self.logger.info(
            f"Starting daily report for {target_date} - {len(leagues)} leagues, {len(markets)} markets",
            extra=extra
        )
    
    def log_league_processing(self, league: str, games_count: int, start_time: float):
        """
        Log league processing completion.
        
        Args:
            league: League that was processed
            games_count: Number of games processed
            start_time: When league processing started
        """
        duration_ms = int((time.time() - start_time) * 1000)
        self._leagues_processed += 1
        self._games_processed += games_count
        
        extra = {
            'operation': 'league_processing',
            'league': league,
            'games_processed': games_count,
            'response_time_ms': duration_ms
        }
        
        self.logger.info(
            f"Processed {league}: {games_count} games in {duration_ms}ms",
            extra=extra
        )
    
    def log_game_analysis(self, league: str, event_id: str, analysis_type: str, 
                         confidence: float, duration_ms: int):
        """
        Log game analysis completion.
        
        Args:
            league: League of the game
            event_id: Game event ID
            analysis_type: Type of analysis performed
            confidence: Analysis confidence score
            duration_ms: Analysis duration
        """
        extra = {
            'operation': 'game_analysis',
            'league': league,
            'event_id': event_id,
            'analysis_type': analysis_type,
            'confidence_score': confidence,
            'response_time_ms': duration_ms
        }
        
        self.logger.debug(
            f"Analyzed {league} game {event_id}: {analysis_type} (confidence: {confidence:.2f})",
            extra=extra
        )
    
    def log_odds_processing(self, event_id: str, sportsbook: str, market_type: str, 
                           odds_count: int, success: bool):
        """
        Log odds data processing.
        
        Args:
            event_id: Game event ID
            sportsbook: Sportsbook name
            market_type: Type of betting market
            odds_count: Number of odds processed
            success: Whether processing was successful
        """
        extra = {
            'operation': 'odds_processing',
            'event_id': event_id,
            'sportsbook': sportsbook,
            'market_type': market_type,
            'odds_count': odds_count,
            'status': 'OK' if success else 'ERR'
        }
        
        level = logging.DEBUG if success else logging.WARNING
        message = f"Processed {market_type} odds from {sportsbook}: {odds_count} lines"
        if not success:
            message = f"Failed to process {market_type} odds from {sportsbook}"
        
        self.logger.log(level, message, extra=extra)
    
    def log_player_props(self, player_name: str, prop_type: str, line_value: float, 
                        sportsbook: str, success: bool):
        """
        Log player prop processing.
        
        Args:
            player_name: Player name
            prop_type: Type of prop bet
            line_value: Prop line value
            sportsbook: Sportsbook offering the prop
            success: Whether processing was successful
        """
        extra = {
            'operation': 'player_props',
            'player_name': player_name,
            'prop_type': prop_type,
            'sportsbook': sportsbook,
            'status': 'OK' if success else 'ERR'
        }
        
        level = logging.DEBUG if success else logging.WARNING
        message = f"Player prop {player_name} {prop_type} {line_value} ({sportsbook})"
        
        self.logger.log(level, message, extra=extra)
    
    def log_betting_recommendation(self, event_id: str, bet_type: str, 
                                  recommendation: str, confidence: float, 
                                  value_score: float):
        """
        Log betting recommendation generation.
        
        Args:
            event_id: Game event ID
            bet_type: Type of bet
            recommendation: Recommendation text
            confidence: Confidence score
            value_score: Value bet score
        """
        extra = {
            'operation': 'betting_recommendation',
            'event_id': event_id,
            'bet_type': bet_type,
            'confidence_score': confidence,
            'value_score': value_score
        }
        
        self.logger.info(
            f"Betting recommendation for {event_id} {bet_type}: {recommendation} "
            f"(confidence: {confidence:.2f}, value: {value_score:.2f})",
            extra=extra
        )
    
    def log_error_recovery(self, operation: str, error_type: str, recovery_strategy: str, 
                          success: bool, retry_count: int = 0):
        """
        Log error recovery attempts.
        
        Args:
            operation: Operation that failed
            error_type: Type of error
            recovery_strategy: Recovery strategy used
            success: Whether recovery was successful
            retry_count: Number of retries attempted
        """
        extra = {
            'operation': 'error_recovery',
            'original_operation': operation,
            'error_type': error_type,
            'recovery_strategy': recovery_strategy,
            'retry_count': retry_count,
            'status': 'OK' if success else 'ERR'
        }
        
        level = logging.INFO if success else logging.ERROR
        message = f"Error recovery for {operation} ({error_type}): {recovery_strategy}"
        if success:
            message += " - SUCCESS"
        else:
            message += f" - FAILED after {retry_count} retries"
        
        self.logger.log(level, message, extra=extra)
    
    def complete_daily_report(self, success: bool, error_count: int = 0):
        """
        Log daily report completion.
        
        Args:
            success: Whether report generation was successful
            error_count: Number of errors encountered
        """
        if self._report_start_time:
            duration_ms = int((time.time() - self._report_start_time) * 1000)
        else:
            duration_ms = 0
        
        extra = {
            'operation': 'daily_report_complete',
            'leagues_processed': self._leagues_processed,
            'games_processed': self._games_processed,
            'error_count': error_count,
            'response_time_ms': duration_ms,
            'status': 'OK' if success else 'ERR'
        }
        
        level = logging.INFO if success else logging.ERROR
        message = (f"Daily report completed: {self._games_processed} games, "
                  f"{self._leagues_processed} leagues, {error_count} errors "
                  f"in {duration_ms}ms")
        
        self.logger.log(level, message, extra=extra)


def setup_daily_betting_logging(
    level: str = None,
    log_format: str = None,
    log_file: str = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Configure enhanced logging for daily betting intelligence system.
    
    Args:
        level: Log level override (DEBUG, INFO, WARNING, ERROR)
        log_format: Format override ('json' for structured logs)
        log_file: Optional log file path
        max_file_size: Maximum log file size in bytes
        backup_count: Number of backup log files to keep
    """
    # Get configuration from environment variables
    log_level = level or os.getenv('DAILY_BETTING_LOG_LEVEL', 'INFO').upper()
    log_format_env = log_format or os.getenv('DAILY_BETTING_LOG_FORMAT', 'text').lower()
    log_file_path = log_file or os.getenv('DAILY_BETTING_LOG_FILE')
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger('daily_betting_intelligence')
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    use_json = log_format_env == 'json'
    formatter = DailyBettingFormatter(use_json=use_json)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file_path:
        log_dir = Path(log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Use rotating file handler
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    betting_loggers = [
        'daily_betting_intelligence.data_orchestrator',
        'daily_betting_intelligence.report_formatter',
        'daily_betting_intelligence.error_handler',
        'daily_betting_intelligence.config_manager',
        'daily_betting_intelligence.models'
    ]
    
    for logger_name in betting_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(numeric_level)
        logger.propagate = True  # Propagate to parent logger
    
    # Suppress noisy third-party loggers unless DEBUG
    if numeric_level > logging.DEBUG:
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    # Log configuration
    config_logger = logging.getLogger('daily_betting_intelligence.logging_config')
    config_logger.info(
        f"Daily betting logging configured: level={log_level}, format={log_format_env}, "
        f"file={'enabled' if log_file_path else 'disabled'}"
    )


def setup_performance_logging(log_file: str = None) -> None:
    """
    Set up separate performance logging for monitoring and optimization.
    
    Args:
        log_file: Optional performance log file path
    """
    perf_logger = logging.getLogger('daily_betting_intelligence.performance')
    perf_logger.setLevel(logging.INFO)
    
    # Performance log format
    perf_formatter = logging.Formatter(
        '%(asctime)s [PERF] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler for performance logs
    if log_file:
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Daily rotating handler for performance logs
        perf_handler = TimedRotatingFileHandler(
            log_file,
            when='midnight',
            interval=1,
            backupCount=30  # Keep 30 days of performance logs
        )
        perf_handler.setFormatter(perf_formatter)
        perf_logger.addHandler(perf_handler)
    
    # Console handler for performance logs (only if DEBUG)
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(perf_formatter)
        perf_logger.addHandler(console_handler)


def get_daily_betting_logger(name: str) -> DailyBettingLogger:
    """
    Get a DailyBettingLogger instance for the given module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        DailyBettingLogger instance
    """
    return DailyBettingLogger(f'daily_betting_intelligence.{name}')


def log_performance_metric(operation: str, duration_ms: int, **kwargs):
    """
    Log a performance metric.
    
    Args:
        operation: Operation name
        duration_ms: Duration in milliseconds
        **kwargs: Additional metric data
    """
    perf_logger = logging.getLogger('daily_betting_intelligence.performance')
    
    metric_data = {
        'operation': operation,
        'duration_ms': duration_ms,
        'timestamp': datetime.now().isoformat(),
        **kwargs
    }
    
    perf_logger.info(json.dumps(metric_data))


# Auto-configure logging when module is imported
if not logging.getLogger('daily_betting_intelligence').handlers:
    setup_daily_betting_logging()