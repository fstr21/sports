# MCP Methods & Tools Reference

## Overview

This document provides detailed information about all available methods, endpoints, tools, and commands across the MCP implementations in this project.

## MagicTunnel Methods & Tools

### Core Smart Discovery Tool

#### `smart_tool_discovery`
**Description**: The primary intelligent tool that discovers and executes the right tool for any natural language request.

**Parameters**:
- `request` (string, required): Natural language description of what you want to do
- `confidence_threshold` (number, optional): Minimum confidence threshold for tool matching (default: 0.7)
- `max_results` (number, optional): Maximum number of tool matches to return (default: 10)
- `force_execution` (boolean, optional): Execute the best match even if below confidence threshold (default: false)

**Example Usage**:
```json
{
  "name": "smart_tool_discovery",
  "arguments": {
    "request": "ping google.com",
    "confidence_threshold": 0.8
  }
}
```

**Returns**:
```json
{
  "success": true,
  "tool_used": "network_ping",
  "confidence": 0.95,
  "result": "...",
  "discovery_metadata": {
    "matches_found": 3,
    "selection_method": "hybrid",
    "processing_time_ms": 150
  }
}
```

### Tool Management Commands

#### CLI Commands (via `magictunnel-visibility`)

```bash
# Check tool visibility status
cargo run --bin magictunnel-visibility -- -c config.yaml status

# Hide/show individual tools
cargo run --bin magictunnel-visibility -- -c config.yaml hide-tool <tool_name>
cargo run --bin magictunnel-visibility -- -c config.yaml show-tool <tool_name>

# Hide/show entire capability files
cargo run --bin magictunnel-visibility -- -c config.yaml hide-file <file_path>
cargo run --bin magictunnel-visibility -- -c config.yaml show-file <file_path>

# Global visibility management
cargo run --bin magictunnel-visibility -- -c config.yaml hide-all
cargo run --bin magictunnel-visibility -- -c config.yaml show-all
```

### HTTP API Endpoints

#### Health Check
- **Endpoint**: `GET /health`
- **Description**: Check server health status
- **Response**: `{"status": "healthy", "version": "0.2.49"}`

#### MCP Call
- **Endpoint**: `POST /v1/mcp/call`
- **Description**: Execute MCP tool calls via HTTP
- **Content-Type**: `application/json`
- **Body**:
```json
{
  "name": "smart_tool_discovery",
  "arguments": {
    "request": "your request here"
  }
}
```

#### Tool Discovery
- **Endpoint**: `POST /v1/discover`
- **Description**: Discover tools without executing them
- **Body**:
```json
{
  "request": "natural language request",
  "threshold": 0.5,
  "max_results": 5
}
```

#### Tool Registry
- **Endpoint**: `GET /v1/tools`
- **Description**: List all available tools
- **Response**: Array of tool definitions with metadata

#### Configuration
- **Endpoint**: `GET /v1/config`
- **Description**: Get current server configuration
- **Endpoint**: `PUT /v1/config`
- **Description**: Update server configuration (requires admin permissions)

#### Metrics
- **Endpoint**: `GET /v1/metrics`
- **Description**: Get server metrics and usage statistics
- **Response**:
```json
{
  "discovery_stats": {
    "total_requests": 1234,
    "successful_discoveries": 1100,
    "average_confidence": 0.85,
    "most_used_tools": ["network_ping", "filesystem_read"]
  },
  "tool_stats": {
    "total_tools": 83,
    "visible_tools": 1,
    "hidden_tools": 82
  }
}
```

### WebSocket Support

- **Endpoint**: `ws://localhost:3001/ws`
- **Description**: Real-time MCP communication via WebSocket
- **Protocol**: JSON-RPC 2.0 over WebSocket

### gRPC Services

- **Port**: Server port + 1000 (default: 4001)
- **Services**: MCP Protocol Buffer services for high-performance clients

## Sports AI MCP Tools

### Core ESPN Data Tools

#### `getScoreboard`
**Description**: Get scoreboard data for a specific league

**Parameters**:
- `sport` (string, required): Sport category (e.g., "baseball", "basketball", "football", "hockey", "soccer")
- `league` (string, required): League identifier (e.g., "mlb", "nba", "nfl", "nhl", "eng.1")
- `dates` (string, optional): Date filter in YYYYMMDD format
- `limit` (integer, optional): Maximum number of events to return
- `week` (integer, optional): Week number (NFL/NCAAF only)
- `seasontype` (integer, optional): Season type (NFL/NCAAF only)

**Example**:
```json
{
  "name": "getScoreboard",
  "arguments": {
    "sport": "basketball",
    "league": "nba",
    "dates": "20250109"
  }
}
```

**Response**:
```json
{
  "ok": true,
  "content_md": "## Scoreboard basketball/nba\n\nEvents: 12",
  "data": {
    "scoreboard": {
      "events": [
        {
          "event_id": "401704001",
          "date": "2025-01-09T01:00Z",
          "status": "pre",
          "home": {
            "id": "1610612737",
            "displayName": "Atlanta Hawks",
            "abbrev": "ATL",
            "score": null,
            "homeAway": "home"
          },
          "away": {
            "id": "1610612738",
            "displayName": "Boston Celtics", 
            "abbrev": "BOS",
            "score": null,
            "homeAway": "away"
          }
        }
      ],
      "newest_event_time": "2025-01-09T01:00Z"
    }
  }
}
```

#### `getTeams`
**Description**: Get list of teams for a specific league

**Parameters**:
- `sport` (string, required): Sport category
- `league` (string, required): League identifier

**Example**:
```json
{
  "name": "getTeams",
  "arguments": {
    "sport": "basketball",
    "league": "nba"
  }
}
```

**Response**:
```json
{
  "ok": true,
  "content_md": "## Teams basketball/nba\n\nCount: 30",
  "data": {
    "teams": [
      {
        "id": "1610612737",
        "displayName": "Atlanta Hawks",
        "abbrev": "ATL",
        "location": "Atlanta"
      }
    ]
  }
}
```

#### `getGameSummary`
**Description**: Get detailed game summary/boxscore for a specific event

**Parameters**:
- `sport` (string, required): Sport category
- `league` (string, required): League identifier  
- `event_id` (string, required): Event ID from scoreboard

**Example**:
```json
{
  "name": "getGameSummary",
  "arguments": {
    "sport": "basketball",
    "league": "nba",
    "event_id": "401704001"
  }
}
```

**Response**:
```json
{
  "ok": true,
  "content_md": "## Game Summary basketball/nba event=401704001\n\nStatus: pre",
  "data": {
    "summary": {
      "status": "pre",
      "teams_meta": [
        {
          "team_id": "1610612737",
          "displayName": "Atlanta Hawks",
          "abbrev": "ATL",
          "score": null,
          "homeAway": "home"
        }
      ],
      "leaders": null,
      "boxscore": null
    }
  }
}
```

### Analysis Tools

#### `analyzeGameStrict`
**Description**: Analyze a game using AI, strictly from fetched stats (no inference)

**Parameters**:
- `sport` (string, required): Sport category
- `league` (string, required): League identifier
- `event_id` (string, required): Event ID
- `question` (string, required): Analysis question

**Example**:
```json
{
  "name": "analyzeGameStrict",
  "arguments": {
    "sport": "basketball",
    "league": "nba", 
    "event_id": "401704001",
    "question": "What are the key stats from this game?"
  }
}
```

### Utility Tools

#### `probeLeagueSupport`
**Description**: Probe and validate capability support for a league

**Parameters**:
- `sport` (string, required): Sport category
- `league` (string, required): League identifier
- `date` (string, optional): Date in YYYYMMDD format (defaults to today)

**Example**:
```json
{
  "name": "probeLeagueSupport",
  "arguments": {
    "sport": "basketball",
    "league": "nba",
    "date": "20250109"
  }
}
```

**Response**:
```json
{
  "ok": true,
  "content_md": "## Probe basketball/nba 20250109\n\nScoreboard ✅  Summary ✅  PlayerStats ✅",
  "data": {
    "capability": {
      "scoreboard": true,
      "summary": true,
      "game_player_stats": true,
      "checked_event_id": "401704001"
    }
  }
}
```

#### `getTeamSeasonStats`
**Description**: Get team season statistics (limited ESPN support)

**Parameters**:
- `sport` (string, required): Sport category
- `league` (string, required): League identifier
- `team_id` (string, required): Team ID
- `season` (string, optional): Season year

**Note**: Currently returns `supported: false` for most leagues due to ESPN API limitations.

#### `getPlayerSeasonStats`
**Description**: Get player season statistics (limited ESPN support)

**Parameters**:
- `sport` (string, required): Sport category
- `league` (string, required): League identifier
- `player_id` (string, required): Player ID
- `season` (string, optional): Season year

**Note**: Currently returns `supported: false` for most leagues due to ESPN API limitations.

### Supported League Combinations

| Sport | League | Identifier | Supported Endpoints |
|-------|--------|------------|-------------------|
| baseball | MLB | mlb | scoreboard, teams, summary |
| basketball | NBA | nba | scoreboard, teams, summary |
| basketball | WNBA | wnba | scoreboard, teams, summary |
| football | NFL | nfl | scoreboard, teams, summary |
| football | College Football | college-football | scoreboard, teams, summary |
| basketball | Men's College Basketball | mens-college-basketball | scoreboard, teams, summary |
| hockey | NHL | nhl | scoreboard, teams, summary |
| soccer | Premier League | eng.1 | scoreboard, teams, summary |
| soccer | La Liga | esp.1 | scoreboard, teams, summary |
| soccer | MLS | usa.1 | scoreboard, teams, summary |

## Wagyu Sports MCP Tools

### Odds API Tools

#### `get_sports`
**Description**: Get list of available sports from the odds API

**Parameters**:
- `all_sports` (boolean, optional): Include out-of-season sports (default: false)
- `use_test_mode` (boolean, optional): Override server test mode setting

**Example**:
```json
{
  "name": "get_sports",
  "arguments": {
    "all_sports": true,
    "use_test_mode": false
  }
}
```

**Response**: JSON array of sports with keys, names, and availability status

#### `get_odds`
**Description**: Get odds for a specific sport

**Parameters**:
- `sport` (string, required): Sport key (e.g., "basketball_nba")
- `regions` (string, optional): Comma-separated regions (e.g., "us,uk")
- `markets` (string, optional): Comma-separated markets (e.g., "h2h,spreads")
- `odds_format` (string, optional): "decimal" or "american"
- `date_format` (string, optional): "unix" or "iso"
- `use_test_mode` (boolean, optional): Override server test mode setting

**Example**:
```json
{
  "name": "get_odds",
  "arguments": {
    "sport": "basketball_nba",
    "regions": "us",
    "markets": "h2h,spreads",
    "odds_format": "american"
  }
}
```

**Response**: JSON array of games with odds from various bookmakers

#### `get_event_odds`
**Description**: Get odds for a specific event (required for player props)

**Parameters**:
- `sport` (string, required): Sport key
- `event_id` (string, required): Event ID from odds API
- `regions` (string, optional): Comma-separated regions
- `markets` (string, optional): Markets (e.g., "player_points,player_rebounds")
- `odds_format` (string, optional): "decimal" or "american"
- `date_format` (string, optional): "unix" or "iso"
- `use_test_mode` (boolean, optional): Override server test mode

**Example**:
```json
{
  "name": "get_event_odds",
  "arguments": {
    "sport": "basketball_nba",
    "event_id": "abc123xyz789",
    "markets": "player_points,player_rebounds,player_assists",
    "regions": "us"
  }
}
```

**Response**: Event-specific odds including player prop markets

#### `get_quota_info`
**Description**: Get API quota/usage information

**Parameters**:
- `use_test_mode` (boolean, optional): Override server test mode setting

**Example**:
```json
{
  "name": "get_quota_info",
  "arguments": {}
}
```

**Response**:
```json
{
  "remaining_requests": 450,
  "used_requests": 50
}
```

### Available Markets

#### Main Markets
- `h2h` - Head to head (moneyline)
- `spreads` - Point spreads
- `totals` - Over/under totals

#### Player Props (event-specific)
- `player_points` - Player points
- `player_rebounds` - Player rebounds  
- `player_assists` - Player assists
- `player_threes` - Three-pointers made
- `player_blocks` - Player blocks
- `player_steals` - Player steals
- `player_turnovers` - Player turnovers

#### Regions
- `us` - United States bookmakers
- `uk` - United Kingdom bookmakers
- `eu` - European bookmakers
- `au` - Australian bookmakers

## Error Responses

### Common Error Format

All MCP tools return errors in a consistent format:

```json
{
  "ok": false,
  "error_type": "validation_error|upstream_error|request_error",
  "message": "Error description",
  "source": "ESPN|OddsAPI|MagicTunnel",
  "additional_context": {}
}
```

### Error Types

#### Validation Errors
- Invalid parameters
- Unsupported sport/league combinations
- Missing required fields

#### Upstream Errors  
- ESPN API failures
- Odds API failures
- Rate limiting

#### Request Errors
- Network connectivity issues
- Timeout errors
- Authentication failures

## Rate Limits & Quotas

### Sports AI MCP
- Depends on OpenRouter API limits
- ESPN API has no explicit rate limits but may throttle
- Use `probeLeagueSupport` to validate before making multiple calls

### Wagyu Sports MCP
- Odds API typically provides 500 requests/month on free tier
- Use `get_quota_info` to monitor usage
- Test mode available for development without quota usage

### MagicTunnel
- No inherent rate limits
- Dependent on underlying tool rate limits
- Semantic search may have OpenAI API limits if using OpenAI embeddings

## Best Practices

### Smart Discovery
1. Use descriptive natural language requests
2. Set appropriate confidence thresholds based on use case
3. Monitor discovery metrics via `/v1/metrics` endpoint
4. Use hybrid mode for best balance of accuracy and speed

### Sports Data
1. Always check league support with `probeLeagueSupport` first
2. Cache scoreboard data to avoid repeated API calls
3. Use specific date ranges to limit data volume
4. Monitor API quotas regularly

### Performance
1. Enable caching where available
2. Use batch requests when possible
3. Set appropriate timeouts for your use case
4. Monitor memory usage with large datasets