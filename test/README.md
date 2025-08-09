# Testing Documentation

This directory contains comprehensive tests for the MCP-only sports client architecture.

## Test Structure

### Test Types

1. **Smoke Tests** (`test_smoke_e2e.py`)
   - End-to-end verification of core requirements
   - No direct ESPN API calls in client code
   - MCP server connectivity
   - CLI command functionality
   - Rate limiting awareness

2. **Unit Tests** (`test_adapters_*.py`)
   - Test sport data adapters with frozen JSON samples
   - No network calls required
   - Test data normalization functions
   - Handle missing/malformed data gracefully

3. **Integration Tests** (`test_feature_*.py`)
   - Test CLI clients with live MCP server
   - Network-aware and rate-limit conscious
   - Skip if MCP server unavailable

## Running Tests

### Quick Smoke Tests
```bash
# Run essential smoke tests only
python test/run_smoke_tests.py
```

### All Unit Tests (Default)
```bash
# Run all unit tests (no network required)
pytest test/
```

### Integration Tests
```bash
# Enable integration tests (requires MCP server)
RUN_INTEGRATION_TESTS=1 pytest test/ -m integration
```

### Specific Test Categories
```bash
# Run only adapter unit tests
pytest test/ -k "adapter"

# Run only CLI integration tests
pytest test/ -k "cli" -m integration

# Run smoke tests with pytest
pytest test/test_smoke_e2e.py -m smoke
```

### All Tests (Including Integration)
```bash
# Run everything (requires MCP server and network)
RUN_INTEGRATION_TESTS=1 pytest test/ -m "not slow"
```

## Test Configuration

- **pytest.ini**: Main pytest configuration
- **conftest.py**: Shared fixtures and test setup
- **fixtures/**: Sample JSON data for unit tests

## Test Markers

- `@pytest.mark.unit`: Unit tests (no network)
- `@pytest.mark.integration`: Integration tests (requires MCP)
- `@pytest.mark.smoke`: Basic functionality tests
- `@pytest.mark.slow`: Long-running tests

## Environment Variables

- `RUN_INTEGRATION_TESTS=1`: Enable integration tests
- `LOG_LEVEL=DEBUG`: Verbose logging during tests

## Test Files

### Smoke Tests
- `test_smoke_e2e.py`: End-to-end architecture verification

### Unit Tests
- `test_adapters_nfl.py`: NFL data adapter tests
- `test_adapters_nba.py`: NBA data adapter tests

### Integration Tests
- `test_feature_scoreboard_cli.py`: Scoreboard CLI integration tests
- `test_feature_game_cli.py`: Game CLI integration tests

### Test Data
- `fixtures/nfl_game_summary.json`: Sample NFL game data
- `fixtures/nba_game_summary.json`: Sample NBA game data

## Expected Test Results

### Smoke Tests (Always Should Pass)
- ✅ No direct ESPN API calls in clients directory
- ✅ MCP server file exists
- ✅ CLI commands show help without errors
- ✅ All modules import successfully

### Unit Tests (Always Should Pass)
- ✅ Adapter normalize functions work with sample data
- ✅ Handle missing data gracefully
- ✅ Return expected data structures

### Integration Tests (Require MCP Server)
- ✅ Live MCP calls return valid data
- ✅ CLI scripts execute without crashes
- ✅ Error handling works with invalid inputs

## Troubleshooting

### Tests Fail to Import Modules
```bash
# Ensure you're running from project root
cd /path/to/sports
pytest test/
```

### Integration Tests Always Skip
```bash
# Enable integration tests
export RUN_INTEGRATION_TESTS=1
pytest test/ -m integration
```

### MCP Server Not Found
```bash
# Verify MCP server exists
ls sports_mcp/sports_ai_mcp.py
# or
ls mcp/sports_ai_mcp.py
```

### Network-Related Test Failures
- Integration tests require network access
- Some tests may be rate-limited by ESPN API
- Set environment variables to control test behavior

## Coverage

Run with coverage to see test coverage:
```bash
pytest test/ --cov=clients --cov=adapters --cov-report=html
```

## Continuous Integration

For CI environments:
```bash
# Run only unit and smoke tests (no network required)
pytest test/ -m "not integration" --tb=short
```