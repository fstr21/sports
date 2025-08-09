#!/usr/bin/env python3
"""
Pytest configuration and fixtures for sports MCP testing.

Provides shared fixtures, test configuration, and utilities
for testing the MCP-only client architecture.
"""

import os
import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock

# Add project paths to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "clients"))
sys.path.insert(0, str(PROJECT_ROOT / "adapters"))


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests that don't require network access"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests that require MCP server"
    )
    config.addinivalue_line(
        "markers", "smoke: Basic smoke tests for functionality verification"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take a long time to run"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their names and content."""
    for item in items:
        # Mark integration tests
        if "integration" in item.name.lower() or "live" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        
        # Mark smoke tests
        if "smoke" in item.name.lower() or item.fspath.basename.startswith("test_smoke"):
            item.add_marker(pytest.mark.smoke)
        
        # Mark unit tests (most adapter tests)
        if "adapter" in item.fspath.basename:
            item.add_marker(pytest.mark.unit)


@pytest.fixture
def project_root():
    """Provide project root path."""
    return PROJECT_ROOT


@pytest.fixture
def clients_dir():
    """Provide clients directory path."""
    return PROJECT_ROOT / "clients"


@pytest.fixture
def adapters_dir():
    """Provide adapters directory path."""
    return PROJECT_ROOT / "adapters"


@pytest.fixture
def test_fixtures_dir():
    """Provide test fixtures directory path."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_nfl_data():
    """Load sample NFL game data for testing."""
    import json
    fixtures_path = Path(__file__).parent / "fixtures" / "nfl_game_summary.json"
    if fixtures_path.exists():
        with open(fixtures_path, 'r') as f:
            return json.load(f)
    else:
        # Return minimal structure if fixture doesn't exist
        return {
            "ok": True,
            "data": {
                "summary": {
                    "boxscore": {
                        "players": []
                    }
                }
            }
        }


@pytest.fixture
def sample_nba_data():
    """Load sample NBA game data for testing."""
    import json
    fixtures_path = Path(__file__).parent / "fixtures" / "nba_game_summary.json"
    if fixtures_path.exists():
        with open(fixtures_path, 'r') as f:
            return json.load(f)
    else:
        return {
            "ok": True,
            "data": {
                "summary": {
                    "boxscore": {
                        "players": []
                    }
                }
            }
        }


@pytest.fixture
def mock_mcp_response():
    """Provide a mock MCP response for testing."""
    return {
        "ok": True,
        "data": {
            "scoreboard": {
                "events": [
                    {
                        "event_id": "123",
                        "status": "Final",
                        "home": {"displayName": "Home Team", "score": "21"},
                        "away": {"displayName": "Away Team", "score": "14"}
                    }
                ]
            }
        },
        "meta": {"league": "nfl", "sport": "football"}
    }


@pytest.fixture
def mock_mcp_error():
    """Provide a mock MCP error response."""
    return {
        "ok": False,
        "message": "Test error message",
        "error_type": "test_error"
    }


@pytest.fixture
def skip_if_no_mcp():
    """Skip test if MCP dependencies are not available."""
    try:
        import core_mcp
        return False
    except ImportError:
        return True


@pytest.fixture
def skip_if_no_integration_env():
    """Skip test if integration test environment is not set up."""
    return not os.getenv('RUN_INTEGRATION_TESTS')


@pytest.fixture(autouse=True)
def clean_imports():
    """Clean up module imports between tests."""
    # Store original modules
    original_modules = sys.modules.copy()
    
    yield
    
    # Remove any modules that were imported during the test
    modules_to_remove = []
    for module_name in sys.modules:
        if module_name not in original_modules:
            if any(name in module_name for name in ['core_mcp', 'core_llm', 'adapters']):
                modules_to_remove.append(module_name)
    
    for module_name in modules_to_remove:
        del sys.modules[module_name]


@pytest.fixture
def network_available():
    """Check if network is available for integration tests."""
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def pytest_runtest_setup(item):
    """Set up individual test runs."""
    # Skip integration tests if environment variables not set
    if item.get_closest_marker("integration"):
        if not os.getenv('RUN_INTEGRATION_TESTS'):
            pytest.skip("Integration tests require RUN_INTEGRATION_TESTS=1")
    
    # Skip network tests if no network available
    if "network" in item.name.lower():
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
        except OSError:
            pytest.skip("Network not available for network-dependent test")


def pytest_sessionstart(session):
    """Print test session information."""
    print(f"\nStarting test session")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Python path includes: clients/, adapters/")
    
    # Check if integration tests will run
    if os.getenv('RUN_INTEGRATION_TESTS'):
        print("Integration tests enabled (RUN_INTEGRATION_TESTS=1)")
    else:
        print("Integration tests disabled (set RUN_INTEGRATION_TESTS=1 to enable)")


def pytest_sessionfinish(session, exitstatus):
    """Print test session summary."""
    if exitstatus == 0:
        print(f"\nTest session completed successfully")
    else:
        print(f"\nTest session failed with exit status {exitstatus}")