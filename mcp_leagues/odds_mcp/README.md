# Odds MCP v2 - Using the-odds Package

## Overview
Advanced MCP server for sports betting odds using the reliable `the-odds` Python package. Provides clean interface to The Odds API with better error handling and game matching.

**Server URL**: `https://odds-mcp-v2-production.up.railway.app/mcp`

## Features
- 🎯 **Reliable Package**: Uses `the-odds` Python package instead of direct HTTP calls
- 🚀 **Railway Deployed**: Subdirectory deployment in `mcp_leagues/odds_mcp/`  
- ✅ **Health Checks**: Built-in Railway health check endpoint
- 🔧 **Test Mode**: Mock data support for development
- 📊 **4 Core Tools**: Sports, odds, quota, and event-specific data

## Tools Available

### 1. getSports
Get available sports from The Odds API
- **Parameters**: `all_sports` (boolean), `use_test_mode` (boolean)
- **Returns**: List of available sports (MLB, NBA, NFL, NHL, etc.)

### 2. getOdds  
Get betting odds for specific sport
- **Parameters**: `sport` (required), `regions`, `markets`, `odds_format`, `use_test_mode`
- **Returns**: Game odds with moneyline, spreads, totals
- **Example**: `{"sport": "baseball_mlb", "markets": "h2h,spreads,totals"}`

### 3. getQuotaInfo
Check API usage and quota status
- **Parameters**: `use_test_mode` (boolean)
- **Returns**: API quota information and status

### 4. getEventOdds
Get event-specific odds (player props)
- **Parameters**: `sport`, `event_id` (required), `regions`, `markets`, `use_test_mode`
- **Returns**: Detailed event odds including player props

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
- `the-odds>=1.0.2`
- `httpx>=0.25.0`

## Usage Examples

### PowerShell
```powershell
# Get available sports
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getSports","arguments":{"use_test_mode":true}}}'
Invoke-RestMethod -Uri "https://odds-mcp-v2-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"

# Get MLB odds
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getOdds","arguments":{"sport":"baseball_mlb","markets":"h2h,spreads,totals"}}}'
Invoke-RestMethod -Uri "https://odds-mcp-v2-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

### Python
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

# Get MLB odds
odds_data = call_odds_tool("getOdds", {
    "sport": "baseball_mlb", 
    "markets": "h2h,spreads,totals"
})
```

## Advantages over v1
- ✅ **Cleaner Code**: Uses `the-odds` package instead of manual HTTP calls
- ✅ **Better Reliability**: Package handles API quirks and errors
- ✅ **Health Checks**: Railway deployment won't fail health checks
- ✅ **Organized Structure**: Proper subdirectory deployment
- ✅ **Game Matching**: Better logic for matching games with odds

## Testing
Health check endpoint available at root path `/` returns server status and configuration info.