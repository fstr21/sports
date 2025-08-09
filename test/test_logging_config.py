"""
Unit tests for daily_betting_intelligence.logging_config module.

Tests the enhanced logging configuration, custom formatters, and specialized
logging methods for daily betting intelligence operations.
"""

import json
import logging
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from daily_betting_intelligence.logging_config import (
    DailyBettingFormatter,
    DailyBettingLogger,
    setup_daily_betting_logging,
    setup_performance_logging,
    get_daily_betting_logger,
    log_performance_metric
)


class TestDailyBettingFormatter:
    """Test the enhanced formatter for daily betting intelligence."""
    
    def test_json_format_basic(self):
        """Test basic JSON formatting."""
        formatter = DailyBettingFormatter(use_json=True)
        
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Test message',
            args=(),
            exc_info=None
        )
        record.module = 'test_module'
        record.funcName = 'test_function'
        
        result = formatter.format(record)
        log_data = json.loads(result)
        
        assert log_data['level'] == 'INFO'
        assert log_data['logger'] == 'test_logger'
        assert log_data['message'] == 'Test message'
        assert log_data['module'] == 'test_module'
        assert log_data['function'] == 'test_function'
        assert log_data['line'] == 10
        assert 'timestamp' in log_data
    
    def test_json_format_with_betting_fields(self):
        """Test JSON formatting with betting-specific fields."""
        formatter = DailyBettingFormatter(use_json=True)
        
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Game analysis complete',
            args=(),
            exc_info=None
        )
        record.module = 'test_module'
        record.funcName = 'test_function'
        record.league = 'NBA'
        record.event_id = '12345'
        record.confidence_score = 0.85
        record.response_time_ms = 250
        
        result = formatter.format(record)
        log_data = json.loads(result)
        
        assert log_data['league'] == 'NBA'
        assert log_data['event_id'] == '12345'
        assert log_data['confidence_score'] == 0.85
        assert log_data['response_time_ms'] == 250
    
    def test_text_format_basic(self):
        """Test basic text formatting."""
        formatter = DailyBettingFormatter(use_json=False)
        
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Test message',
            args=(),
            exc_info=None
        )
        record.module = 'test_module'
        record.funcName = 'test_function'
        
        result = formatter.format(record)
        
        assert 'INFO' in result
        assert 'Test message' in result
    
    def test_text_format_with_context(self):
        """Test text formatting with betting context."""
        formatter = DailyBettingFormatter(use_json=False)
        
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Processing game',
            args=(),
            exc_info=None
        )
        record.module = 'test_module'
        record.funcName = 'test_function'
        record.league = 'NBA'
        record.event_id = '12345'
        record.market_type = 'moneyline'
        record.confidence_score = 0.75
        
        result = formatter.format(record)
        
        assert '[league=NBA, event=12345, market=moneyline, confidence=0.75]' in result


class TestDailyBettingLogger:
    """Test the enhanced logger for daily betting intelligence."""
    
    @pytest.fixture
    def logger(self):
        """Create a test logger instance."""
        return DailyBettingLogger('test_module')
    
    def test_start_daily_report(self, logger, caplog):
        """Test daily report start logging."""
        with caplog.at_level(logging.INFO):
            logger.start_daily_report('2024-01-15', ['NBA', 'NFL'], ['moneyline', 'spreads'])
        
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert 'Starting daily report for 2024-01-15' in record.message
        assert record.operation == 'daily_report'
        assert record.date == '2024-01-15'
        assert record.leagues_count == 2
        assert record.markets_count == 2
    
    def test_log_league_processing(self, logger, caplog):
        """Test league processing logging."""
        start_time = time.time() - 0.5  # 500ms ago
        
        with caplog.at_level(logging.INFO):
            logger.log_league_processing('NBA', 10, start_time)
        
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert 'Processed NBA: 10 games' in record.message
        assert record.operation == 'league_processing'
        assert record.league == 'NBA'
        assert record.games_processed == 10
        assert record.response_time_ms > 400  # Should be around 500ms
    
    def test_log_game_analysis(self, logger, caplog):
        """Test game analysis logging."""
        with caplog.at_level(logging.DEBUG):
            logger.log_game_analysis('NBA', '12345', 'outcome_prediction', 0.85, 150)
        
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert 'Analyzed NBA game 12345' in record.message
        assert record.operation == 'game_analysis'
        assert record.league == 'NBA'
        assert record.event_id == '12345'
        assert record.analysis_type == 'outcome_prediction'
        assert record.confidence_score == 0.85
        assert record.response_time_ms == 150
    
    def test_log_odds_processing_success(self, logger, caplog):
        """Test successful odds processing logging."""
        with caplog.at_level(logging.DEBUG):
            logger.log_odds_processing('12345', 'DraftKings', 'moneyline', 2, True)
        
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert 'Processed moneyline odds from DraftKings: 2 lines' in record.message
        assert record.operation == 'odds_processing'
        assert record.event_id == '12345'
        assert record.sportsbook == 'DraftKings'
        assert record.market_type == 'moneyline'
        assert record.odds_count == 2
        assert record.status == 'OK'
    
    def test_log_odds_processing_failure(self, logger, caplog):
        """Test failed odds processing logging."""
        with caplog.at_level(logging.WARNING):
            logger.log_odds_processing('12345', 'DraftKings', 'moneyline', 0, False)
        
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert 'Failed to process moneyline odds from DraftKings' in record.message
        assert record.status == 'ERR'
    
    def test_log_player_props(self, logger, caplog):
        """Test player props logging."""
        with caplog.at_level(logging.DEBUG):
            logger.log_player_props('LeBron James', 'points', 25.5, 'FanDuel', True)
        
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert 'Player prop LeBron James points 25.5 (FanDuel)' in record.message
        assert record.operation == 'player_props'
        assert record.player_name == 'LeBron James'
        assert record.prop_type == 'points'
        assert record.sportsbook == 'FanDuel'
        assert record.status == 'OK'
    
    def test_log_betting_recommendation(self, logger, caplog):
        """Test betting recommendation logging."""
        with caplog.at_level(logging.INFO):
            logger.log_betting_recommendation(
                '12345', 'moneyline', 'Take Lakers +150', 0.75, 0.85
            )
        
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert 'Betting recommendation for 12345 moneyline: Take Lakers +150' in record.message
        assert record.operation == 'betting_recommendation'
        assert record.event_id == '12345'
        assert record.bet_type == 'moneyline'
        assert record.confidence_score == 0.75
        assert record.value_score == 0.85
    
    def test_log_error_recovery_success(self, logger, caplog):
        """Test successful error recovery logging."""
        with caplog.at_level(logging.INFO):
            logger.log_error_recovery('fetch_odds', 'timeout', 'retry_with_backoff', True, 2)
        
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert 'Error recovery for fetch_odds (timeout): retry_with_backoff - SUCCESS' in record.message
        assert record.operation == 'error_recovery'
        assert record.original_operation == 'fetch_odds'
        assert record.error_type == 'timeout'
        assert record.recovery_strategy == 'retry_with_backoff'
        assert record.retry_count == 2
        assert record.status == 'OK'
    
    def test_log_error_recovery_failure(self, logger, caplog):
        """Test failed error recovery logging."""
        with caplog.at_level(logging.ERROR):
            logger.log_error_recovery('fetch_odds', 'server_error', 'skip_source', False, 3)
        
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert 'Error recovery for fetch_odds (server_error): skip_source - FAILED after 3 retries' in record.message
        assert record.status == 'ERR'
    
    def test_complete_daily_report_success(self, logger, caplog):
        """Test successful daily report completion logging."""
        # Start a report first to set timing
        logger.start_daily_report('2024-01-15', ['NBA'], ['moneyline'])
        # Add a small delay to ensure timing works
        time.sleep(0.01)
        logger.log_league_processing('NBA', 5, time.time())
        
        with caplog.at_level(logging.INFO):
            logger.complete_daily_report(True, 0)
        
        # Find the completion record (should be the last one)
        completion_record = None
        for record in caplog.records:
            if hasattr(record, 'operation') and record.operation == 'daily_report_complete':
                completion_record = record
                break
        
        assert completion_record is not None
        assert 'Daily report completed: 5 games, 1 leagues, 0 errors' in completion_record.message
        assert completion_record.leagues_processed == 1
        assert completion_record.games_processed == 5
        assert completion_record.error_count == 0
        assert completion_record.status == 'OK'
        assert completion_record.response_time_ms >= 0  # Allow 0 for very fast execution
    
    def test_complete_daily_report_with_errors(self, logger, caplog):
        """Test daily report completion with errors."""
        logger.start_daily_report('2024-01-15', ['NBA'], ['moneyline'])
        
        with caplog.at_level(logging.ERROR):
            logger.complete_daily_report(False, 3)
        
        # Find the completion record
        completion_record = None
        for record in caplog.records:
            if hasattr(record, 'operation') and record.operation == 'daily_report_complete':
                completion_record = record
                break
        
        assert completion_record is not None
        assert completion_record.error_count == 3
        assert completion_record.status == 'ERR'


class TestLoggingSetup:
    """Test logging setup functions."""
    
    def test_setup_daily_betting_logging_defaults(self):
        """Test default logging setup."""
        with patch.dict(os.environ, {}, clear=True):
            setup_daily_betting_logging()
        
        logger = logging.getLogger('daily_betting_intelligence')
        assert logger.level == logging.INFO
        assert len(logger.handlers) >= 1  # At least console handler
    
    def test_setup_daily_betting_logging_with_file(self):
        """Test logging setup with file handler."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / 'test.log'
            
            setup_daily_betting_logging(
                level='DEBUG',
                log_format='json',
                log_file=str(log_file)
            )
            
            logger = logging.getLogger('daily_betting_intelligence')
            assert logger.level == logging.DEBUG
            assert len(logger.handlers) >= 2  # Console + file handlers
            
            # Test that log file is created
            logger.info('Test message')
            assert log_file.exists()
            
            # Clean up handlers to avoid file lock issues on Windows
            for handler in logger.handlers[:]:
                if hasattr(handler, 'close'):
                    handler.close()
                logger.removeHandler(handler)
    
    def test_setup_daily_betting_logging_environment_vars(self):
        """Test logging setup with environment variables."""
        env_vars = {
            'DAILY_BETTING_LOG_LEVEL': 'WARNING',
            'DAILY_BETTING_LOG_FORMAT': 'json'
        }
        
        with patch.dict(os.environ, env_vars):
            setup_daily_betting_logging()
        
        logger = logging.getLogger('daily_betting_intelligence')
        assert logger.level == logging.WARNING
    
    def test_setup_performance_logging(self):
        """Test performance logging setup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perf_log_file = Path(temp_dir) / 'performance.log'
            
            setup_performance_logging(str(perf_log_file))
            
            perf_logger = logging.getLogger('daily_betting_intelligence.performance')
            assert perf_logger.level == logging.INFO
            assert len(perf_logger.handlers) >= 1
            
            # Clean up handlers to avoid file lock issues on Windows
            for handler in perf_logger.handlers[:]:
                if hasattr(handler, 'close'):
                    handler.close()
                perf_logger.removeHandler(handler)
    
    def test_get_daily_betting_logger(self):
        """Test getting a daily betting logger instance."""
        logger = get_daily_betting_logger('test_module')
        
        assert isinstance(logger, DailyBettingLogger)
        assert logger.logger.name == 'daily_betting_intelligence.test_module'
    
    def test_log_performance_metric(self, caplog):
        """Test performance metric logging."""
        # Set up performance logging
        setup_performance_logging()
        
        with caplog.at_level(logging.INFO, logger='daily_betting_intelligence.performance'):
            log_performance_metric('test_operation', 150, games_count=5, league='NBA')
        
        assert len(caplog.records) == 1
        record = caplog.records[0]
        
        # Parse the JSON log message
        metric_data = json.loads(record.message)
        assert metric_data['operation'] == 'test_operation'
        assert metric_data['duration_ms'] == 150
        assert metric_data['games_count'] == 5
        assert metric_data['league'] == 'NBA'
        assert 'timestamp' in metric_data


class TestLoggingIntegration:
    """Test logging integration scenarios."""
    
    def test_full_daily_report_logging_flow(self, caplog):
        """Test complete daily report logging flow."""
        logger = get_daily_betting_logger('integration_test')
        
        with caplog.at_level(logging.DEBUG, logger='daily_betting_intelligence.integration_test'):
            # Start daily report
            logger.start_daily_report('2024-01-15', ['NBA', 'NFL'], ['moneyline', 'spreads'])
            
            # Process leagues
            start_time = time.time()
            logger.log_league_processing('NBA', 8, start_time)
            logger.log_league_processing('NFL', 12, start_time)
            
            # Log some game analysis
            logger.log_game_analysis('NBA', '12345', 'outcome_prediction', 0.85, 120)
            logger.log_game_analysis('NFL', '67890', 'betting_analysis', 0.75, 200)
            
            # Log odds processing
            logger.log_odds_processing('12345', 'DraftKings', 'moneyline', 2, True)
            logger.log_odds_processing('67890', 'FanDuel', 'spreads', 2, True)
            
            # Log betting recommendations
            logger.log_betting_recommendation('12345', 'moneyline', 'Take Lakers +150', 0.80, 0.75)
            
            # Complete report
            logger.complete_daily_report(True, 0)
        
        # Verify we have all expected log entries
        operations = [record.operation for record in caplog.records if hasattr(record, 'operation')]
        
        expected_operations = [
            'daily_report',
            'league_processing',
            'league_processing',
            'game_analysis',
            'game_analysis',
            'odds_processing',
            'odds_processing',
            'betting_recommendation',
            'daily_report_complete'
        ]
        
        assert operations == expected_operations
    
    def test_error_scenarios_logging(self, caplog):
        """Test logging during error scenarios."""
        logger = get_daily_betting_logger('error_test')
        
        with caplog.at_level(logging.WARNING):
            # Log failed odds processing
            logger.log_odds_processing('12345', 'BetMGM', 'totals', 0, False)
            
            # Log failed player props
            logger.log_player_props('Stephen Curry', 'assists', 7.5, 'Caesars', False)
            
            # Log error recovery attempts
            logger.log_error_recovery('fetch_game_data', 'timeout', 'retry', False, 3)
            
            # Complete report with errors
            logger.complete_daily_report(False, 3)
        
        # Verify error logging
        error_records = [r for r in caplog.records if r.levelno >= logging.WARNING]
        assert len(error_records) == 4  # 2 failed operations + 1 failed recovery + 1 failed completion
        
        # Check that all error records have status='ERR'
        for record in error_records:
            if hasattr(record, 'status'):
                assert record.status == 'ERR'