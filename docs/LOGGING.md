# MCP Client Logging System

The MCP client logging system provides structured logging with configurable verbosity levels and JSON format support for debugging and monitoring MCP operations.

## Features

- **Configurable verbosity levels**: DEBUG, INFO, WARNING, ERROR
- **Structured JSON logging** for log aggregation systems
- **MCP operation timing** with request/response measurement
- **ESPN URL logging** for debugging API calls
- **Error context** with troubleshooting information
- **CLI integration** with logging flags

## Configuration

### Environment Variables

```bash
# Set log level (DEBUG, INFO, WARNING, ERROR)
export LOG_LEVEL=DEBUG

# Set log format (text, json)
export LOG_FORMAT=json
```

### CLI Arguments

Most CLI clients support logging configuration:

```bash
# Set log level via CLI
python scoreboard_cli.py events nfl --log-level DEBUG

# Set log format via CLI
python scoreboard_cli.py events nfl --log-format json
```

## Log Levels

### DEBUG Level
Shows full ESPN URLs and timing from MCP responses:

```bash
LOG_LEVEL=DEBUG python scoreboard_cli.py events nfl
```

Output:
```
2024-08-08 17:00:00 [DEBUG] clients.core_mcp: Starting MCP scoreboard for nfl
2024-08-08 17:00:01 [DEBUG] clients.core_mcp: MCP scoreboard for nfl completed in 1250ms (ESPN: https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard)
```

### INFO Level
Shows only league/date/event and OK/ERR status:

```bash
LOG_LEVEL=INFO python scoreboard_cli.py events nfl
```

Output:
```
2024-08-08 17:00:00 [INFO] clients.core_mcp: nfl: OK (1250ms)
```

### JSON Format
Structured logs for log aggregation:

```bash
LOG_FORMAT=json LOG_LEVEL=INFO python scoreboard_cli.py events nfl
```

Output:
```json
{
  "timestamp": "2024-08-08T17:00:00.123456",
  "level": "INFO",
  "logger": "clients.core_mcp",
  "message": "nfl: OK (1250ms)",
  "mcp_operation": "scoreboard",
  "league": "nfl",
  "status": "OK",
  "response_time_ms": 1250,
  "espn_url": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
}
```

## Debugging Tools

### Debug MCP Utility

Test MCP server connectivity and performance:

```bash
cd clients

# Test connectivity
python debug_mcp.py connectivity

# Test scoreboard timing
python debug_mcp.py scoreboard nfl

# Test game summary timing
python debug_mcp.py game nfl 401547439

# Run comprehensive test suite
python debug_mcp.py comprehensive nfl
```

### Logging Example

See logging in action:

```bash
cd clients

# Demo different log levels
python logging_example.py

# Demo specific logging level
python logging_example.py debug
python logging_example.py json
```

## Integration in Code

### Using MCPLogger

```python
from logging_config import get_mcp_logger

# Get logger for your module
mcp_logger = get_mcp_logger(__name__)

# Start timing an operation
operation_id = mcp_logger.start_operation('scoreboard', 'nfl', date='20240815')

# Log successful completion
mcp_logger.log_success(
    operation_id, 'scoreboard', 'nfl',
    espn_url='https://site.api.espn.com/...',
    date='20240815'
)

# Log errors
mcp_logger.log_error(
    operation_id, 'scoreboard', 'nfl', error,
    error_type='upstream_error',
    espn_url='https://site.api.espn.com/...'
)
```

### Setup Logging in CLI

```python
from logging_config import setup_logging

# Configure logging with CLI arguments
setup_logging(level=args.log_level, log_format=args.log_format)
```

## Log Fields

### Standard Fields
- `timestamp`: ISO format timestamp
- `level`: Log level (DEBUG, INFO, WARNING, ERROR)
- `logger`: Logger name
- `message`: Human-readable message
- `module`: Python module name
- `function`: Function name
- `line`: Line number

### MCP-Specific Fields
- `mcp_operation`: Operation name (scoreboard, game_summary, etc.)
- `league`: League being queried
- `status`: Operation status (OK, ERR)
- `response_time_ms`: Response time in milliseconds
- `espn_url`: ESPN API URL that was called
- `error_type`: Type of error (upstream_error, validation_error, etc.)
- `event_id`: Event ID (for game operations)
- `date`: Date parameter (for date-specific operations)

## Troubleshooting

### Enable Debug Logging

```bash
LOG_LEVEL=DEBUG python your_script.py
```

### Check MCP Server Connectivity

```bash
python debug_mcp.py connectivity
```

### Test Specific Operations

```bash
# Test NFL scoreboard
LOG_LEVEL=DEBUG python debug_mcp.py scoreboard nfl

# Test with JSON output
LOG_FORMAT=json python debug_mcp.py scoreboard nfl --json
```

### Monitor Performance

```bash
# Run comprehensive test with timing
python debug_mcp.py comprehensive nfl
```

## Log Aggregation

For production environments, use JSON format with log aggregation systems:

```bash
# Output structured logs
LOG_FORMAT=json LOG_LEVEL=INFO python your_app.py | your_log_aggregator
```

The JSON format includes all necessary fields for filtering, alerting, and analysis in systems like ELK Stack, Splunk, or CloudWatch.