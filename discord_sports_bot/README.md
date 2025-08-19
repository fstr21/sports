# Discord Sports Bot - Enhanced Multi-Sport Architecture

A modular, scalable Discord bot for managing sports channels with comprehensive analysis and betting information.

## Architecture Overview

This bot follows a modular architecture that makes it easy to add new sports while maintaining consistent functionality across all sports.

### Core Components

- **BaseSportHandler**: Abstract base class that all sport implementations inherit from
- **MCPClient**: Unified HTTP client for all MCP services with connection pooling and retry logic
- **SportManager**: Dynamically loads and manages sport handlers
- **SyncManager**: Handles Discord command synchronization with detailed feedback
- **CommandRouter**: Routes sport-specific commands to appropriate handlers
- **ErrorHandler**: Provides comprehensive error handling with user-friendly messages
- **ConfigManager**: Centralized configuration management with environment variable support

### Project Structure

```
discord_sports_bot/
├── __init__.py
├── README.md
├── core/
│   ├── __init__.py
│   ├── base_sport_handler.py      # Abstract base class for all sports
│   ├── mcp_client.py              # Unified MCP client
│   ├── sport_manager.py           # Dynamic sport loading
│   ├── sync_manager.py            # Command synchronization
│   ├── command_router.py          # Command routing
│   └── error_handler.py           # Error handling
├── sports/
│   ├── __init__.py
│   ├── soccer_handler.py          # Soccer implementation (to be created)
│   ├── mlb_handler.py             # MLB implementation (to be created)
│   ├── nfl_handler.py             # NFL implementation (to be created)
│   └── nba_handler.py             # NBA implementation (to be created)
├── formatters/
│   ├── __init__.py
│   └── base_formatter.py          # Common formatting utilities
├── config/
│   ├── __init__.py
│   ├── models.py                  # Configuration data models
│   ├── manager.py                 # Configuration management
│   └── example.env                # Example configuration
└── main.py                        # Main bot file (to be created)
```

## Configuration

The bot uses environment variables for configuration. Copy `config/example.env` to `.env` and fill in your values.

### Required Configuration

- `DISCORD_TOKEN`: Your Discord bot token
- `{SPORT}_MCP_URL`: MCP service URL for each sport (e.g., `SOCCER_MCP_URL`)

### Optional Configuration

- `{SPORT}_CATEGORY_NAME`: Discord category name for each sport
- `{SPORT}_CATEGORY_ID`: Discord category ID (if you want to use a specific category)
- `{SPORT}_EMBED_COLOR`: Hex color for embeds (e.g., `0x00ff00`)
- Various MCP client and formatting settings

## Adding New Sports

To add a new sport:

1. Create a new handler class in `sports/` that inherits from `BaseSportHandler`
2. Implement the required abstract methods:
   - `create_channels()`
   - `clear_channels()`
   - `get_matches()`
   - `format_match_analysis()`
3. Add the sport to the `SportManager._create_sport_handler()` method
4. Add configuration variables for the new sport

## Key Features

### Modular Architecture
- Each sport has its own handler with consistent interface
- Easy to add new sports without modifying existing code
- Shared utilities for common functionality

### Robust Error Handling
- User-friendly error messages with troubleshooting suggestions
- Comprehensive logging for debugging
- Graceful degradation when services are unavailable

### Configuration Management
- Environment variable based configuration
- Validation and error reporting for invalid configurations
- Sport-specific settings with sensible defaults

### Command Synchronization
- Built-in `/sync` command for updating Discord commands
- Detailed feedback on sync operations
- Permission validation

### MCP Client Management
- Connection pooling and retry logic
- Standardized error handling across all MCP calls
- Timeout and rate limiting protection

## Usage

The bot provides the following commands:

- `/create-channels <sport>` - Create channels for today's games
- `/clear-channels <sport>` - Clear all channels for a sport
- `/sync` - Synchronize Discord commands (Admin only)
- `/help` - Show help information

## Requirements

- Python 3.8+
- discord.py 2.0+
- httpx for HTTP requests
- Environment variables for configuration

## Development Status

This is the core infrastructure implementation. Sport-specific handlers need to be implemented in subsequent tasks.

### Completed
- ✅ Core architecture and base classes
- ✅ Configuration management system
- ✅ MCP client with connection pooling
- ✅ Error handling system
- ✅ Command routing and synchronization

### Next Steps
- Implement sport-specific handlers (Soccer, MLB, NFL, NBA)
- Create enhanced formatting system
- Build main bot file
- Add comprehensive testing