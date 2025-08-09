#!/usr/bin/env python3
"""
Test script to verify MCP logging functionality.

This script tests the logging configuration and ensures that:
1. Different log levels work correctly
2. JSON format logging works
3. MCP operation timing is captured
4. Error logging includes proper context
"""

import asyncio
import json
import logging
import os
import sys
import tempfile
from io import StringIO
from unittest.mock import patch

# Add clients directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'clients'))

from logging_config import setup_logging, get_mcp_logger, MCPLogger


def test_logging_configuration():
    """Test basic logging configuration."""
    print("Testing logging configuration...")
    
    # Test INFO level
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        setup_logging(level='INFO', log_format='text')
        logger = logging.getLogger('test')
        logger.info("Test INFO message")
        output = mock_stdout.getvalue()
        assert "Test INFO message" in output
        assert "[INFO]" in output
    
    # Test JSON format
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        setup_logging(level='INFO', log_format='json')
        logger = logging.getLogger('test')
        logger.info("Test JSON message")
        output = mock_stdout.getvalue()
        
        # Should be valid JSON - get the last line which should be our test message
        lines = output.strip().split('\n')
        last_line = lines[-1]
        
        try:
            log_entry = json.loads(last_line)
            assert log_entry['level'] == 'INFO'
            assert log_entry['message'] == 'Test JSON message'
        except json.JSONDecodeError:
            assert False, f"Invalid JSON output: {last_line}"
    
    print("✅ Logging configuration tests passed")


def test_mcp_logger():
    """Test MCP logger functionality."""
    print("Testing MCP logger...")
    
    # Create a temporary logger to avoid interference
    import logging
    test_logger = logging.getLogger('test_mcp_logger')
    test_logger.setLevel(logging.DEBUG)
    
    # Create string handler
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.DEBUG)
    
    from logging_config import MCPFormatter
    formatter = MCPFormatter(use_json=False)
    handler.setFormatter(formatter)
    
    test_logger.addHandler(handler)
    
    # Test MCP logger functionality
    mcp_logger = MCPLogger('test_mcp_logger')
    
    # Test operation timing
    operation_id = mcp_logger.start_operation('test_operation', 'nfl', event_id='12345')
    
    # Simulate successful operation
    mcp_logger.log_success(
        operation_id, 'test_operation', 'nfl',
        espn_url='https://site.api.espn.com/test',
        event_id='12345'
    )
    
    output = log_stream.getvalue()
    
    # Clean up
    test_logger.removeHandler(handler)
    
    # Verify output contains expected content
    assert "Starting MCP test_operation for nfl" in output
    assert "MCP test_operation for nfl completed" in output
    assert "https://site.api.espn.com/test" in output
    
    print("✅ MCP logger tests passed")


def test_error_logging():
    """Test error logging functionality."""
    print("Testing error logging...")
    
    # Create a temporary logger to avoid interference
    import logging
    test_logger = logging.getLogger('test_error_logger')
    test_logger.setLevel(logging.DEBUG)
    
    # Create string handler
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.DEBUG)
    
    from logging_config import MCPFormatter
    formatter = MCPFormatter(use_json=False)
    handler.setFormatter(formatter)
    
    test_logger.addHandler(handler)
    
    # Test MCP logger functionality
    mcp_logger = MCPLogger('test_error_logger')
    
    # Test error logging
    operation_id = mcp_logger.start_operation('test_operation', 'nfl')
    
    test_error = Exception("Test error message")
    mcp_logger.log_error(
        operation_id, 'test_operation', 'nfl', test_error,
        error_type='test_error',
        espn_url='https://site.api.espn.com/test'
    )
    
    output = log_stream.getvalue()
    
    # Clean up
    test_logger.removeHandler(handler)
    
    # Verify output contains expected content
    assert "MCP test_operation for nfl failed" in output
    assert "Test error message" in output
    assert "https://site.api.espn.com/test" in output
    
    print("✅ Error logging tests passed")


def test_json_logging_structure():
    """Test JSON logging structure."""
    print("Testing JSON logging structure...")
    
    # Create a temporary logger to avoid interference
    import logging
    test_logger = logging.getLogger('test_json_logger')
    test_logger.setLevel(logging.INFO)
    
    # Create string handler
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.INFO)
    
    from logging_config import MCPFormatter
    formatter = MCPFormatter(use_json=True)
    handler.setFormatter(formatter)
    
    test_logger.addHandler(handler)
    
    # Test MCP logger functionality
    mcp_logger = MCPLogger('test_json_logger')
    
    operation_id = mcp_logger.start_operation('scoreboard', 'nfl', date='20240815')
    mcp_logger.log_success(
        operation_id, 'scoreboard', 'nfl',
        espn_url='https://site.api.espn.com/test',
        date='20240815'
    )
    
    output = log_stream.getvalue()
    
    # Clean up
    test_logger.removeHandler(handler)
    
    lines = output.strip().split('\n')
    
    # Should have at least one JSON log entry
    assert len(lines) >= 1
    
    # Parse the last line (success log)
    log_entry = json.loads(lines[-1])
    
    # Verify required fields
    assert log_entry['level'] == 'INFO'
    assert log_entry['mcp_operation'] == 'scoreboard'
    assert log_entry['league'] == 'nfl'
    assert log_entry['status'] == 'OK'
    assert log_entry['espn_url'] == 'https://site.api.espn.com/test'
    assert 'response_time_ms' in log_entry
    assert 'timestamp' in log_entry
    
    print("✅ JSON logging structure tests passed")


def test_log_level_filtering():
    """Test that log levels filter correctly."""
    print("Testing log level filtering...")
    
    # Create a temporary logger to avoid interference
    import logging
    test_logger = logging.getLogger('test_filter_logger')
    test_logger.setLevel(logging.WARNING)
    
    # Create string handler
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.WARNING)
    
    from logging_config import MCPFormatter
    formatter = MCPFormatter(use_json=False)
    handler.setFormatter(formatter)
    
    test_logger.addHandler(handler)
    
    # Test that INFO messages are filtered out at WARNING level
    test_logger.info("This should not appear")
    test_logger.warning("This should appear")
    
    output = log_stream.getvalue()
    
    # Clean up
    test_logger.removeHandler(handler)
    
    # Verify filtering works
    assert "This should not appear" not in output
    assert "This should appear" in output
    
    print("✅ Log level filtering tests passed")


def main():
    """Run all logging tests."""
    print("MCP Logging System Tests")
    print("=" * 30)
    print()
    
    try:
        test_logging_configuration()
        test_mcp_logger()
        test_error_logging()
        test_json_logging_structure()
        test_log_level_filtering()
        
        print("\n" + "=" * 30)
        print("✅ All logging tests passed!")
        print("\nLogging system is working correctly.")
        print("\nTo test with real MCP calls:")
        print("cd clients && python debug_mcp.py connectivity")
        print("cd clients && LOG_LEVEL=DEBUG python scoreboard_cli.py events nfl")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()