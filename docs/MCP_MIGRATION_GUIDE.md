# MCP Migration Guide

## Overview

This guide documents the migration from direct ESPN API calls to the MCP-only architecture. All ESPN data access now flows through the `sports_ai_mcp.py` MCP server.

## Migration Summary

### Before (Deprecated)
```python
# Direct ESPN API calls - NO LONGER USED
from espn_client import get_scoreboard, get_game_summary

scoreboard_result = get_scoreboard(
    sport="football",
    league="nfl",
    dates="20240815"
)
```

### After (Current Architecture)
```python
# MCP-only architecture - CURRENT APPROACH
from clients.core_mcp import scoreboard, game_summary
import asyncio

# Async MCP calls
scoreboard_result = await scoreboard('nfl', date='20240815')

# Or synchronous wrapper (as used in sports_analysis.py)
def _run_async(self, coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

scoreboard_result = self._run_async(scoreboard('nfl', date='20240815'))
```

## Key Changes

### 1. Import Changes
- **OLD**: `from espn_client import get_scoreboard, get_game_summary`
- **NEW**: `from clients.core_mcp import scoreboard, game_summary`

### 2. Function Signatures
- **OLD**: `get_scoreboard(sport="football", league="nfl", dates="20240815")`
- **NEW**: `scoreboard('nfl', date='20240815')`

### 3. League Mapping
The new architecture uses simplified league keys:
```python
LEAGUE_MAPPING = {
    'nfl': ('football', 'nfl'),
    'nba': ('basketball', 'nba'),
    'wnba': ('basketball', 'wnba'),
    'mlb': ('baseball', 'mlb'),
    'nhl': ('hockey', 'nhl'),
    'mls': ('soccer', 'usa.1'),
    'epl': ('soccer', 'eng.1'),
    'laliga': ('soccer', 'esp.1')
}
```

### 4. Error Handling
- **OLD**: HTTP status codes and requests exceptions
- **NEW**: `MCPError`, `MCPServerError`, `MCPValidationError`

## Available MCP Functions

### Core Functions
- `scoreboard(league, date=None, **kwargs)` - Get scoreboard data
- `game_summary(league, event_id)` - Get game summary/boxscore
- `teams(league)` - Get teams list
- `analyze_game_strict(league, event_id, question)` - AI analysis
- `probe_league_support(league, date=None)` - Check capability

### Season Stats (Limited Support)
- `team_season_stats(league, team_id, season=None)` - Returns supported:false
- `player_season_stats(league, player_id, season=None)` - Returns supported:false

## Migration Checklist

### For Existing Code
- [ ] Replace `espn_client` imports with `clients.core_mcp` imports
- [ ] Update function calls to use new signatures
- [ ] Add async/await or synchronous wrappers
- [ ] Update error handling for MCP exceptions
- [ ] Test with MCP server running

### For New Code
- [ ] Use only `clients.core_mcp` functions
- [ ] Never import `espn_client` (deprecated)
- [ ] Follow MCP-only architecture patterns
- [ ] Use league keys from LEAGUE_MAPPING

## Files Updated

### Migrated Files
- `sports_analysis.py` - ✅ Migrated to MCP-only architecture
- `clients/core_mcp.py` - ✅ MCP wrapper functions
- `clients/mcp_client.py` - ✅ MCP communication layer

### Deprecated Files
- `espn_client.py` - ⚠️ DEPRECATED - Legacy compatibility only

## Testing Migration

### Verify No Direct ESPN Calls
```bash
# Should return no matches in clients directory
grep -R "site.api.espn.com" clients/
```

### Test MCP Integration
```python
from sports_analysis import SportsAnalysisSystem
import os

# Set required environment variables
os.environ['ODDS_API_KEY'] = 'your_key'
os.environ['OPENROUTER_API_KEY'] = 'your_key'

# Test initialization
system = SportsAnalysisSystem()
print("✅ MCP integration working")
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'mcp_client'**
   - Fix: Use relative import in core_mcp.py: `from .mcp_client import ...`

2. **MCP server not found**
   - Ensure `sports_mcp/sports_ai_mcp.py` exists
   - Check MCP server path in `get_server_path()`

3. **Async/sync issues**
   - Use `_run_async()` wrapper for synchronous contexts
   - Ensure proper event loop handling

### Support

For issues with the MCP migration:
1. Check MCP server is running: `python sports_mcp/sports_ai_mcp.py`
2. Verify environment variables are set
3. Test with simple MCP calls first
4. Check logs for detailed error messages

## Future Considerations

- All new ESPN data access must use MCP architecture
- Direct ESPN API calls are prohibited in client code
- Consider adding more MCP tools as needed
- Monitor MCP server performance and reliability