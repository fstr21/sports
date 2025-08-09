# Daily Betting Intelligence System

A comprehensive system for generating automated daily betting analysis reports that combines sports data from ESPN MCP, betting odds from Wagyu MCP, and AI-powered analysis from OpenRouter LLM.

## Project Structure

```
daily_betting_intelligence/
├── __init__.py              # Main module exports and version info
├── models.py                # Core data models and structures
├── config_manager.py        # Configuration management system
├── interfaces.py            # Abstract base classes and interfaces
├── utils.py                 # Utility functions and helpers
├── exceptions.py            # Custom exception classes
└── README.md               # This documentation file
```

## Core Components

### Data Models (`models.py`)

- **GameData**: Represents a single game with metadata and team information
- **TeamStats**: Team statistics and performance data
- **BettingOdds**: Betting odds for a game from a specific sportsbook
- **PlayerProp**: Player proposition betting data
- **GameAnalysis**: LLM-generated analysis results for a game
- **PlayerAnalysis**: LLM-generated player analysis and prop recommendations
- **ReportData**: Complete report data structure for daily reports
- **ErrorReport**: Error tracking and reporting structure

### Configuration Management (`config_manager.py`)

- **SystemConfig**: Configuration data structure with all system settings
- **ConfigManager**: Manages system configuration with support for:
  - Environment variable overrides
  - JSON configuration files
  - League and market validation
  - Default settings management

### Base Interfaces (`interfaces.py`)

Abstract base classes that define contracts for all system components:

- **DataFetcher**: Interface for data fetching components
- **OddsProvider**: Interface for betting odds providers
- **GameAnalyzer**: Interface for game analysis components
- **ReportFormatter**: Interface for report formatting components
- **ErrorHandler**: Interface for error handling components
- **CacheManager**: Interface for caching components
- **DataOrchestrator**: Interface for data orchestration components
- **ReportGenerator**: Interface for main report generation

### Utilities (`utils.py`)

Common helper functions for:
- Date validation and timezone conversion
- Odds formatting and probability calculations
- Data validation and sanitization
- Cache key generation
- Value bet scoring

### Exception Handling (`exceptions.py`)

Custom exception hierarchy for specific error conditions:
- **DailyBettingIntelligenceError**: Base exception
- **DataFetchError**: Data fetching failures
- **MCPServerError**: MCP server communication issues
- **AnalysisError**: Analysis operation failures
- **ConfigurationError**: Configuration issues
- **ValidationError**: Data validation failures

## Configuration

### Default Settings

The system comes with sensible defaults for all configuration options:

```python
DEFAULT_CONFIG = {
    "leagues": ["nfl", "nba", "wnba", "mlb", "nhl", "mls", "epl", "laliga", "ncaaf", "ncaab"],
    "betting_markets": ["h2h", "spreads", "totals"],
    "player_prop_markets": ["player_points", "player_rebounds", "player_assists"],
    "timezone": "US/Eastern",
    "timeout_seconds": 30,
    "max_concurrent_requests": 5,
    "confidence_threshold": 0.7,
    "retry_attempts": 3,
    "retry_delay_seconds": 2,
    "cache_duration_minutes": 5,
    "report_output_format": "markdown",
    "include_player_props": True,
    "include_llm_analysis": True,
    "min_odds_threshold": -300,
    "max_odds_threshold": 500
}
```

### Environment Variables

Configuration can be overridden using environment variables:

- `DBI_TIMEZONE`: Target timezone (default: US/Eastern)
- `DBI_TIMEOUT_SECONDS`: Request timeout in seconds
- `DBI_MAX_CONCURRENT`: Maximum concurrent requests
- `DBI_CONFIDENCE_THRESHOLD`: Minimum confidence threshold for recommendations
- `DBI_LEAGUES`: Comma-separated list of leagues to include
- `DBI_BETTING_MARKETS`: Comma-separated list of betting markets
- `DBI_INCLUDE_PROPS`: Include player props (true/false)
- `DBI_INCLUDE_LLM`: Include LLM analysis (true/false)

### Supported Leagues

The system supports the following leagues with full configuration:

- **NFL**: National Football League
- **NBA**: National Basketball Association  
- **WNBA**: Women's National Basketball Association
- **MLB**: Major League Baseball
- **NHL**: National Hockey League
- **MLS**: Major League Soccer
- **EPL**: English Premier League
- **La Liga**: Spanish La Liga
- **NCAAF**: NCAA Football
- **NCAAB**: NCAA Basketball

### Betting Markets

Supported betting markets include:

- **h2h**: Moneyline (head-to-head) betting
- **spreads**: Point spread betting
- **totals**: Over/under total points/goals

## Usage Example

```python
from daily_betting_intelligence import ConfigManager, GameData, BettingOdds

# Initialize configuration
config_manager = ConfigManager()
config = config_manager.get_config()

# Validate leagues
valid_leagues = config_manager.validate_leagues(["nba", "nfl"])

# Create game data
game = GameData(
    event_id="game_123",
    league="nba",
    home_team="Lakers",
    away_team="Warriors",
    game_time=datetime.now(),
    venue="Crypto.com Arena",
    status="pre-game"
)

# Create betting odds
odds = BettingOdds(
    event_id="game_123",
    sportsbook="DraftKings",
    moneyline_home=-150,
    moneyline_away=130
)
```

## Testing

The system includes comprehensive tests for all core components:

```bash
# Run all setup tests
python -m pytest test/test_daily_betting_intelligence_setup.py -v

# Run specific test class
python -m pytest test/test_daily_betting_intelligence_setup.py::TestDataModels -v
```

## Requirements

- Python 3.8+
- pytz>=2023.3 (for timezone handling)
- All existing project dependencies

## Next Steps

This foundation provides the core structure for implementing the remaining system components:

1. **Data Orchestrator**: Manages concurrent data fetching across leagues
2. **Report Formatter**: Generates structured markdown reports
3. **Game Analyzer**: LLM-powered game analysis and predictions
4. **Odds Integration**: Wagyu MCP client integration for betting data
5. **CLI Interface**: Command-line interface for report generation

Each component will implement the appropriate interface defined in `interfaces.py` and use the data models and configuration system established here.