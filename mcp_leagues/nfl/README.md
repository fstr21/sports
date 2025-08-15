# NFL MCP Server

NFL data via Model Context Protocol using the `nfl_data_py` package.

## 🏈 Overview

Provides comprehensive NFL data including:
- **Game schedules** with built-in betting odds
- **Team information** and divisions
- **Player statistics** (passing, rushing, receiving)
- **Injury reports** with current status
- **Team performance** metrics

## 🛠️ Available Tools

### `getNFLSchedule`
Get NFL game schedule with optional filters.

**Parameters**:
- `season` (int): NFL season year (default: current year)
- `week` (int): Specific week number (1-18 regular, 19+ playoffs)
- `team` (string): Team abbreviation filter (e.g., 'KC', 'PHI')
- `date_from/date_to` (string): Date range filter (YYYY-MM-DD)
- `game_type` (string): Game type (REG, POST, WC, DIV, CON, SB)
- `use_test_mode` (bool): Use mock data for testing

**Returns**: Games with betting odds, scores, team info, stadium details

### `getNFLTeams`
Get NFL teams information.

**Parameters**:
- `division` (string): Filter by division (e.g., 'AFC East')
- `conference` (string): Filter by conference ('AFC' or 'NFC')
- `use_test_mode` (bool): Use mock data

**Returns**: Team details, divisions, conferences, colors, logos

### `getNFLPlayerStats`
Get NFL player statistics.

**Parameters**:
- `season` (int): NFL season year
- `player_name` (string): Player name (partial match)
- `team` (string): Team abbreviation filter
- `position` (string): Position filter (QB, RB, WR, etc.)
- `stat_type` (string): Stats type (passing, rushing, receiving)
- `limit` (int): Max players to return (default: 50)
- `use_test_mode` (bool): Use mock data

**Returns**: Player performance stats aggregated by season

### `getNFLInjuries`
Get current NFL injury reports.

**Parameters**:
- `season` (int): NFL season year (default: 2024)
- `team` (string): Team abbreviation filter
- `status` (string): Injury status (Out, Questionable, Doubtful)
- `position` (string): Position filter
- `limit` (int): Max reports to return (default: 100)
- `use_test_mode` (bool): Use mock data

**Returns**: Detailed injury reports with status and timeline

### `getNFLTeamStats`
Get NFL team statistics.

**Parameters**:
- `season` (int): NFL season year
- `team` (string): Team abbreviation filter
- `stat_category` (string): Category (offense, defense, special_teams)
- `use_test_mode` (bool): Use mock data

**Returns**: Team performance metrics aggregated by season

## 📊 Data Source

**nfl_data_py**: Open-source package from nflverse
- **GitHub**: https://github.com/nflverse/nfl_data_py
- **Data**: Comprehensive NFL data with built-in betting odds
- **Coverage**: Regular season and playoffs (no preseason)
- **Free**: No API keys or rate limits required

## 🚀 Deployment

### Railway Configuration

**Environment Variables**: None required (all data from nfl_data_py)

**Build Settings**:
- Builder: NIXPACKS
- Build Command: `pip install -r requirements.txt`
- Start Command: `python nfl_mcp_server.py`

### Local Development

```bash
pip install -r requirements.txt
python nfl_mcp_server.py
```

Server runs on `http://localhost:8080`

## 🔗 Integration

### With Odds MCP
The NFL MCP includes basic betting odds but can be enhanced by cross-referencing with the Odds MCP for live betting markets.

### Example Integration
```python
# Get NFL games
nfl_games = await nfl_mcp.call_tool("getNFLSchedule", {
    "week": 1,
    "season": 2025
})

# Get enhanced odds from Odds MCP
live_odds = await odds_mcp.call_tool("getOdds", {
    "sport": "americanfootball_nfl"
})

# Combine for comprehensive analysis
```

## 📅 Season Coverage

**Regular Season**: September - January
- **272 games** per season
- **18 weeks** regular season
- **Playoffs**: Wild Card, Divisional, Conference, Super Bowl

**Current Status**: 
- **2025 season** data available (schedule with betting odds)
- **2024 historical data** complete with results
- **Live updates** during season

## 🎯 Use Cases

### Betting Analysis
- **Game schedules** with built-in betting context
- **Player performance** for prop bet analysis
- **Injury reports** for line movement prediction
- **Team statistics** for spread and total analysis

### Fantasy Sports
- **Player stats** for lineup decisions
- **Injury tracking** for player availability
- **Team matchups** for streaming defenses
- **Historical performance** for trend analysis

## ⚠️ Limitations

- **No preseason data** (regular season starts Sept 4, 2025)
- **Batch updates** (not real-time during games)
- **Historical focus** rather than live game data

## 🔄 Caching

- **Schedule data**: 6 hours
- **Team data**: 24 hours
- **Player stats**: 6 hours
- **Injury reports**: 2 hours (more frequent updates)

## 📈 Performance

**Response Times**:
- Schedule queries: < 500ms
- Player stats: < 1s (large dataset)
- Team/injury data: < 300ms

**Data Volume**:
- **272 games** per season
- **5,000+ player records**
- **6,000+ injury reports**
- **32 teams** with full metadata