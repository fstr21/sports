# Odds MCP v2 - Live Sports Betting Odds with Player Props

## Overview
Advanced MCP server providing **LIVE sports betting odds** including player props using direct HTTP calls to The Odds API. Fully operational for MLB betting markets.

**Server URL**: `https://odds-mcp-v2-production.up.railway.app/mcp`

## Features
- 🎯 **Live Player Props**: Real-time batter hits, home runs, pitcher strikeouts
- 🚀 **Direct HTTP**: Fixed URL encoding bugs by replacing faulty packages
- ✅ **Event-Specific Odds**: Uses `/events/{id}/odds` endpoint for player props
- 🔧 **Dual Architecture**: Works with MLB MCP for complete sports betting platform
- 📊 **5 Core Tools**: Sports, odds, events, event odds, and quota data

## Supported Markets

### Game Markets (All Sports)
- **h2h** - Moneyline (Head-to-Head)
- **spreads** - Point/Run spreads  
- **totals** - Over/Under totals

### Player Props (MLB Only)
- **batter_hits** - Player hits over/under (18+ players, 54+ props)
- **batter_home_runs** - Player home runs over/under (18 players)
- **pitcher_strikeouts** - Starting pitcher strikeouts (2 pitchers, 4 props)

## Tools Available

### 1. getSports
Get available sports from The Odds API
- **Parameters**: `all_sports` (boolean), `use_test_mode` (boolean)
- **Returns**: List of active sports (MLB, NBA, NFL, NHL, etc.)

### 2. getOdds  
Get betting odds for specific sport (game-level markets)
- **Parameters**: `sport` (required), `regions`, `markets`, `odds_format`, `use_test_mode`
- **Returns**: Game odds with moneyline, spreads, totals
- **Example**: `{"sport": "baseball_mlb", "markets": "h2h,spreads,totals"}`

### 3. getEvents
Get upcoming events/games for a sport
- **Parameters**: `sport` (required), `use_test_mode` (boolean)
- **Returns**: List of upcoming games with event IDs needed for player props
- **Example**: `{"sport": "baseball_mlb"}` → Returns event IDs for getEventOdds

### 4. getEventOdds ⭐ **NEW**
Get event-specific odds including player props
- **Parameters**: `sport`, `event_id` (required), `regions`, `markets`, `use_test_mode`
- **Returns**: Detailed event odds including player props
- **Player Props**: `batter_hits`, `batter_home_runs`, `pitcher_strikeouts`
- **Example**: `{"sport": "baseball_mlb", "event_id": "3406dc4194a80b6152139f93aa99e771", "markets": "batter_hits"}`

### 5. getQuotaInfo
Check API usage and quota status
- **Parameters**: `use_test_mode` (boolean)
- **Returns**: API quota information and status

## Deployment Configuration

### Railway Settings
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python odds_mcp_v2.py"
healthcheckPath = "/"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

### Environment Variables
```
ODDS_API_KEY=your_actual_api_key_here
PORT=8080
```

### Root Directory Setting
```
mcp_leagues/odds_mcp
```

## Dependencies
- `uvicorn[standard]>=0.24.0`
- `starlette>=0.27.0` 
- `httpx>=0.25.0` (for direct HTTP calls)

*Note: Removed `the-odds` package due to URL encoding bugs*

## Player Props Workflow

### Step 1: Get Event ID
```python
# Get upcoming MLB games to find event ID
events = call_odds_tool("getEvents", {"sport": "baseball_mlb"})
event_id = events["result"]["data"]["events"][0]["id"]
```

### Step 2: Get Player Props
```python
# Get batter hits for specific game
player_hits = call_odds_tool("getEventOdds", {
    "sport": "baseball_mlb",
    "event_id": event_id,
    "markets": "batter_hits"
})

# Get home run props
home_runs = call_odds_tool("getEventOdds", {
    "sport": "baseball_mlb", 
    "event_id": event_id,
    "markets": "batter_home_runs"
})

# Get pitcher strikeouts
strikeouts = call_odds_tool("getEventOdds", {
    "sport": "baseball_mlb",
    "event_id": event_id, 
    "markets": "pitcher_strikeouts"
})
```

## Live Data Results
**Real example from Seattle Mariners @ Baltimore Orioles:**

### Batter Hits
- **18 players**, **54 total props**
- Julio Rodriguez: Over 1.5 hits (+145), Over 0.5 (-370)
- Gunnar Henderson: Over 1.5 hits (+170), Over 0.5 (-320)

### Batter Home Runs  
- **18 players** with home run props
- Cal Raleigh: Over 0.5 HR (+168)
- Julio Rodriguez: Over 0.5 HR (+300)

### Pitcher Strikeouts
- **2 starting pitchers**
- Tomoyuki Sugano: Over 3.5 K (-152)
- Logan Evans: Over 4.5 K (+140)

## Usage Examples

### Python Helper Function
```python
import requests

def call_odds_tool(name, args=None):
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {"name": name, "arguments": args or {}}
    }
    r = requests.post("https://odds-mcp-v2-production.up.railway.app/mcp", json=payload)
    return r.json()
```

### Game Odds (Traditional)
```python
# Get MLB moneyline, spreads, totals
odds = call_odds_tool("getOdds", {
    "sport": "baseball_mlb", 
    "markets": "h2h,spreads,totals"
})
```

## Key Improvements
- ✅ **Player Props Working**: Full support for batter/pitcher props
- ✅ **Direct HTTP**: Bypassed faulty package URL encoding  
- ✅ **Event-Specific**: Uses `/events/{id}/odds` endpoint
- ✅ **Live Data**: Real bookmaker odds from FanDuel, DraftKings, etc.
- ✅ **Dual MCP Architecture**: Works seamlessly with MLB MCP

## Complete Tools Reference

### Tool Call Format
```python
def call_odds_tool(name, args=None):
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {"name": name, "arguments": args or {}}
    }
    r = requests.post("https://odds-mcp-v2-production.up.railway.app/mcp", json=payload)
    return r.json()
```

### 1. getSports - Available Sports
```python
# Get all active sports
sports = call_odds_tool("getSports")

# Get all sports (including inactive)  
all_sports = call_odds_tool("getSports", {"all_sports": True})

# Test mode
test_sports = call_odds_tool("getSports", {"use_test_mode": True})
```

**Returns**: List of sports with keys like `baseball_mlb`, `basketball_nba`, etc.

### 2. getOdds - Game-Level Betting Odds
```python
# MLB moneyline only
mlb_h2h = call_odds_tool("getOdds", {
    "sport": "baseball_mlb",
    "markets": "h2h"
})

# MLB full markets (moneyline, spreads, totals)
mlb_full = call_odds_tool("getOdds", {
    "sport": "baseball_mlb", 
    "markets": "h2h,spreads,totals",
    "regions": "us"
})

# Multiple regions
multi_region = call_odds_tool("getOdds", {
    "sport": "basketball_nba",
    "markets": "h2h",
    "regions": "us,us2,uk"
})

# Different odds format
decimal_odds = call_odds_tool("getOdds", {
    "sport": "americanfootball_nfl",
    "markets": "h2h,spreads",
    "odds_format": "decimal"
})
```

**Parameters**:
- `sport` (required) - Sport key from getSports
- `regions` (optional) - Default "us", can be "us,us2,uk,au,eu"
- `markets` (optional) - Default "h2h", can be "h2h,spreads,totals"
- `odds_format` (optional) - "american" (default), "decimal", "fractional"

### 3. getEvents - Get Event IDs for Player Props
```python
# Get MLB events (needed for player props)
mlb_events = call_odds_tool("getEvents", {
    "sport": "baseball_mlb"
})

# Extract event ID for specific game
events = mlb_events["result"]["data"]["events"]
orioles_game = next((e for e in events if "Baltimore Orioles" in e.get("home_team", "")), None)
event_id = orioles_game["id"] if orioles_game else events[0]["id"]
```

**Returns**: List of upcoming games with `id`, `home_team`, `away_team`, `commence_time`

### 4. getEventOdds - Player Props & Event-Specific Odds
```python
# Player hits props  
batter_hits = call_odds_tool("getEventOdds", {
    "sport": "baseball_mlb",
    "event_id": "3406dc4194a80b6152139f93aa99e771",
    "markets": "batter_hits"
})

# Player home run props
home_runs = call_odds_tool("getEventOdds", {
    "sport": "baseball_mlb",
    "event_id": "3406dc4194a80b6152139f93aa99e771", 
    "markets": "batter_home_runs"
})

# Pitcher strikeout props
strikeouts = call_odds_tool("getEventOdds", {
    "sport": "baseball_mlb",
    "event_id": "3406dc4194a80b6152139f93aa99e771",
    "markets": "pitcher_strikeouts" 
})

# Game markets via event (alternative to getOdds)
event_h2h = call_odds_tool("getEventOdds", {
    "sport": "baseball_mlb",
    "event_id": "3406dc4194a80b6152139f93aa99e771",
    "markets": "h2h,spreads,totals"
})
```

**Parameters**:
- `sport` (required) - Sport key
- `event_id` (required) - Event ID from getEvents
- `markets` (optional) - Player prop markets or game markets
- `regions` (optional) - Bookmaker regions

**Player Prop Markets**:
- `batter_hits` - Player hits over/under
- `batter_home_runs` - Player home runs over/under  
- `pitcher_strikeouts` - Pitcher strikeouts over/under

### 5. getQuotaInfo - API Usage
```python
# Check API quota
quota = call_odds_tool("getQuotaInfo")

# Test mode quota
test_quota = call_odds_tool("getQuotaInfo", {"use_test_mode": True})
```

**Returns**: API usage information and limits

## Complete Workflow Example
```python
# 1. Get available sports
sports = call_odds_tool("getSports")
print(f"Available sports: {[s['key'] for s in sports['result']['data']['sports']]}")

# 2. Get MLB events
events = call_odds_tool("getEvents", {"sport": "baseball_mlb"})
first_game = events["result"]["data"]["events"][0]
event_id = first_game["id"]
print(f"Game: {first_game['away_team']} @ {first_game['home_team']}")

# 3. Get game odds
game_odds = call_odds_tool("getOdds", {
    "sport": "baseball_mlb",
    "markets": "h2h,spreads,totals"
})
print(f"Found {len(game_odds['result']['data']['odds'])} games with betting lines")

# 4. Get player props for specific game
player_hits = call_odds_tool("getEventOdds", {
    "sport": "baseball_mlb", 
    "event_id": event_id,
    "markets": "batter_hits"
})
event = player_hits["result"]["data"]["event"]
bookmaker = event["bookmakers"][0]
hits_market = next(m for m in bookmaker["markets"] if m["key"] == "batter_hits")
print(f"Player hits props: {len(hits_market['outcomes'])} total options")

# 5. Check API usage
quota = call_odds_tool("getQuotaInfo") 
print("API quota checked")
```

## Testing
Health check: `https://odds-mcp-v2-production.up.railway.app/` returns server status and API key configuration.

Test any tool with `"use_test_mode": true` parameter for mock data during development.