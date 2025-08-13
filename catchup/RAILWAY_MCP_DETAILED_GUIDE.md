# Railway MCP Server - Detailed Technical Guide

## 🚀 Deployment Overview

### Live Production Server
- **URL**: `https://web-production-b939f.up.railway.app`
- **MCP Endpoint**: `https://web-production-b939f.up.railway.app/mcp`
- **Server Name**: `odds-mcp`
- **Version**: `4.0.0`
- **Protocol**: MCP 2024-11-05
- **Status**: ✅ Active and responding

### Railway Configuration
- **Project Name**: helpful-emotion
- **Environment**: production
- **Service**: web
- **Port**: 8080 (Railway auto-maps to HTTPS)
- **Host**: 0.0.0.0 (Railway requirement)

## 🔧 Environment Variables

### Required Configuration
```env
# Primary API Keys
ODDS_API_KEY=76823225714dfa4618643fd701de3d3b
OPENROUTER_API_KEY=sk-or-v1-5c5c2733407d9e9f8d2a596eeafb5ccfb00815bcf485609bae6a6b856b7cbc7
SPORTS_API_KEY=89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ

# Railway Configuration  
RAILWAY_ENVIRONMENT=production
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

### API Key Details
- **ODDS_API_KEY**: Authentication for The Odds API (primary data source)
- **OPENROUTER_API_KEY**: For AI analysis capabilities (currently unused in this server)
- **SPORTS_API_KEY**: For general authentication (currently unused in this server)

## 🛠️ MCP Tools Available (4 Total)

### 1. getSports
**Purpose**: Get list of available sports for betting from The Odds API

**Parameters**:
```json
{
  "all_sports": {
    "type": "boolean", 
    "description": "Include inactive/out-of-season sports",
    "optional": true,
    "default": false
  },
  "use_test_mode": {
    "type": "boolean",
    "description": "Use mock data instead of live API call", 
    "optional": true,
    "default": false
  }
}
```

**Example Call**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call", 
  "id": 1,
  "params": {
    "name": "getSports",
    "arguments": {
      "all_sports": false,
      "use_test_mode": true
    }
  }
}
```

**Mock Data Returns**:
- NFL (americanfootball_nfl)
- NBA (basketball_nba) 
- MLB (baseball_mlb)
- NHL (icehockey_nhl)
- WNBA (basketball_wnba)

### 2. getOdds
**Purpose**: Get betting odds for a specific sport

**Parameters**:
```json
{
  "sport": {
    "type": "string",
    "description": "Sport key from getSports (e.g., 'baseball_mlb')",
    "required": true
  },
  "regions": {
    "type": "string", 
    "description": "Comma-separated regions (e.g., 'us,uk')",
    "optional": true,
    "default": "us"
  },
  "markets": {
    "type": "string",
    "description": "Comma-separated markets (e.g., 'h2h,spreads,totals')", 
    "optional": true,
    "default": "h2h"
  },
  "odds_format": {
    "type": "string",
    "description": "Format for odds display ('american' or 'decimal')",
    "optional": true, 
    "default": "american"
  },
  "use_test_mode": {
    "type": "boolean",
    "description": "Use mock data instead of live API call",
    "optional": true,
    "default": false
  }
}
```

**Supported Markets**:
- `h2h` - Moneyline (head-to-head) bets
- `spreads` - Point spread bets  
- `totals` - Over/under total points
- `outrights` - Season/championship futures

**Example Call**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 1, 
  "params": {
    "name": "getOdds",
    "arguments": {
      "sport": "baseball_mlb",
      "markets": "h2h,spreads,totals",
      "use_test_mode": true
    }
  }
}
```

### 3. getEventOdds  
**Purpose**: Get detailed odds for a specific event/game (required for player props)

**Parameters**:
```json
{
  "sport": {
    "type": "string", 
    "description": "Sport key (e.g., 'basketball_nba')",
    "required": true
  },
  "event_id": {
    "type": "string",
    "description": "Specific event/game ID from getOdds response", 
    "required": true
  },
  "regions": {
    "type": "string",
    "description": "Comma-separated regions",
    "optional": true,
    "default": "us"  
  },
  "markets": {
    "type": "string",
    "description": "Player prop markets (e.g., 'player_points,player_rebounds')",
    "optional": true,
    "default": "h2h"
  },
  "odds_format": {
    "type": "string", 
    "description": "Odds format ('american' or 'decimal')",
    "optional": true,
    "default": "american"
  },
  "use_test_mode": {
    "type": "boolean",
    "description": "Use mock data for testing",
    "optional": true,
    "default": false
  }
}
```

**Player Prop Markets**:
- Basketball: `player_points`, `player_rebounds`, `player_assists`
- Football: `player_pass_yds`, `player_rush_yds`, `player_pass_tds` 
- Baseball: `batter_home_runs`, `pitcher_strikeouts`, `batter_rbis`
- Hockey: `player_shots_on_goal`, `player_blocked_shots`

### 4. getQuotaInfo
**Purpose**: Check The Odds API usage and quota information

**Parameters**:
```json
{
  "use_test_mode": {
    "type": "boolean",
    "description": "Return mock quota data for testing", 
    "optional": true,
    "default": false
  }
}
```

**Returns**: API usage statistics, remaining requests, rate limits

## 🔌 MCP Protocol Implementation

### Supported Methods

#### 1. initialize
**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "initialize", 
  "id": 1,
  "params": {}
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    },
    "serverInfo": {
      "name": "odds-mcp", 
      "version": "4.0.0"
    }
  }
}
```

#### 2. tools/list
**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 1, 
  "params": {}
}
```

**Response**: Returns array of all 4 available tools with full schemas

#### 3. tools/call
**Request Format**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 1,
  "params": {
    "name": "TOOL_NAME",
    "arguments": {
      // Tool-specific parameters
    }
  }
}
```

## 🏗️ Server Architecture

### Technology Stack
- **Framework**: Starlette (lightweight ASGI)
- **Server**: Uvicorn (production ASGI server)
- **HTTP Client**: httpx (async requests)
- **Protocol**: JSON-RPC over HTTP POST

### File Structure
```
odds_mcp_server.py          # Main server implementation (414 lines)
├── MCP Protocol Handlers   # initialize, tools/list, tools/call
├── Tool Implementations    # 4 odds-focused tools  
├── HTTP Client Management  # Async connection pooling
├── Mock Data System       # Test mode support
└── Starlette ASGI App     # HTTP server framework
```

### Error Handling
- **Timeout Protection**: 20 second request timeout
- **API Error Handling**: Graceful degradation for upstream failures
- **Mock Data Fallback**: Test mode for development without API consumption
- **JSON-RPC Compliance**: Standard error codes and messages

## 📡 Data Sources & APIs

### The Odds API Integration
- **Base URL**: `https://api.the-odds-api.com/v4`
- **Authentication**: API key in query parameter  
- **Rate Limits**: Managed via quota tracking
- **Regions Supported**: US, UK, AU, EU
- **Update Frequency**: Live (sub-minute for major events)

### Mock Data System
All tools support `use_test_mode` parameter that returns realistic mock data:
- **Sports List**: 6 major sports (NFL, NBA, MLB, NHL, WNBA, MLS)
- **Game Odds**: Sample Yankees vs Red Sox game with full market coverage
- **Player Props**: Mock basketball player points over/under
- **Quota Info**: Simulated usage statistics

## 🧪 Testing the Server

### Health Check
```bash
curl -X POST https://web-production-b939f.up.railway.app/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {}}'
```

### Get Available Tools
```bash
curl -X POST https://web-production-b939f.up.railway.app/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1, "params": {}}'
```

### Test getSports Tool
```bash
curl -X POST https://web-production-b939f.up.railway.app/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0", 
    "method": "tools/call", 
    "id": 1, 
    "params": {
      "name": "getSports", 
      "arguments": {"use_test_mode": true}
    }
  }'
```

## 📊 Railway Management Commands

### Deployment Commands
```bash
# Check deployment status
railway status

# View live server logs  
railway logs

# Get current domain URL
railway domain  

# List environment variables
railway variables

# Deploy code changes
railway up

# Redeploy current version
railway up --detach
```

### Log Analysis
Look for these startup indicators:
```
Odds MCP Server Starting - v4.0
Odds Tools: 4
Total Tools: 4
Server URL: http://0.0.0.0:8080/mcp
Registered tool: getEventOdds
Registered tool: getOdds  
Registered tool: getQuotaInfo
Registered tool: getSports
```

## 🔄 Development Workflow

### Local Development
```bash
cd "C:\Users\fstr2\Desktop\sports"
python odds_mcp_server.py
# Server runs on http://localhost:8080/mcp
```

### Deployment Process
1. **Code Changes**: Edit `odds_mcp_server.py`
2. **Local Testing**: Test with mock data locally
3. **Commit**: `git add . && git commit -m "description"`  
4. **Deploy**: `railway up`
5. **Monitor**: `railway logs`
6. **Verify**: Test live endpoints

### Troubleshooting
- **Unicode Issues**: Fixed in v4.0 (ensure ASCII=False in JSON responses)
- **Timeout Errors**: 20s timeout should handle most API calls
- **API Quota**: Monitor via `getQuotaInfo` tool
- **CORS Issues**: Server accepts all origins for MCP clients

## 🎯 Key Design Decisions

### Why Odds-Only?
The Railway deployment was **streamlined to focus solely on odds functionality** to:
- Reduce complexity and improve reliability
- Minimize API dependencies and quota usage  
- Provide specialized betting data service
- Allow local development server to handle comprehensive ESPN integration

### MCP Protocol Benefits
- **Standardized Interface**: Works with any MCP-compatible AI system
- **Tool Discovery**: Dynamic capability advertisement
- **Type Safety**: JSON schema validation for all parameters
- **Error Handling**: Structured error responses with debugging info

### Cloud-Native Design
- **Stateless**: No persistent storage required
- **Scalable**: Horizontal scaling via Railway
- **Resilient**: Graceful error handling and timeouts
- **Observable**: Comprehensive logging for monitoring

---

*This MCP server provides a robust, production-ready interface for accessing real-time betting odds data through a standardized protocol, designed for integration with AI systems requiring sports betting intelligence.*