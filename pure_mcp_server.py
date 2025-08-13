#!/usr/bin/env python3
"""
Pure MCP Server for Sports AI - Odds Only

A clean MCP implementation focused solely on sports odds functionality.
Uses standard MCP protocol for maximum compatibility.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.routing import Route

# Configuration
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "").strip()
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
USER_AGENT = "sports-ai-mcp/4.0"

# HTTP client
_http_client: Optional[httpx.AsyncClient] = None

async def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            timeout=20.0,
            headers={"user-agent": USER_AGENT, "accept": "application/json"}
        )
    return _http_client

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# Odds API functions
async def odds_api_get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make Odds API request"""
    if not ODDS_API_KEY:
        return {"ok": False, "error": "ODDS_API_KEY not configured"}
    
    url = f"{ODDS_API_BASE_URL}/{endpoint}"
    query_params = params or {}
    query_params["apiKey"] = ODDS_API_KEY
    
    client = await get_http_client()
    try:
        r = await client.get(url, params=query_params)
        if r.status_code >= 400:
            return {"ok": False, "error": f"Odds API error {r.status_code}: {r.text[:200]}"}
        return {"ok": True, "data": r.json()}
    except Exception as e:
        return {"ok": False, "error": f"Odds API request failed: {str(e)}"}

# Mock data for test mode
def get_mock_sports_data():
    return [
        {"key": "baseball_mlb", "title": "MLB", "group": "Baseball", "active": True},
        {"key": "basketball_nba", "title": "NBA", "group": "Basketball", "active": True},
        {"key": "basketball_wnba", "title": "WNBA", "group": "Basketball", "active": True},
        {"key": "americanfootball_nfl", "title": "NFL", "group": "American Football", "active": True},
        {"key": "icehockey_nhl", "title": "NHL", "group": "Ice Hockey", "active": True}
    ]

def get_mock_odds_data(sport: str):
    if sport == "baseball_mlb":
        return [{
            "id": "mock_game_1",
            "sport_key": "baseball_mlb",
            "commence_time": "2025-08-12T19:00:00Z",
            "home_team": "New York Yankees",
            "away_team": "Boston Red Sox",
            "bookmakers": [{
                "key": "fanduel",
                "title": "FanDuel",
                "markets": [{
                    "key": "h2h",
                    "outcomes": [
                        {"name": "New York Yankees", "price": -150},
                        {"name": "Boston Red Sox", "price": 130}
                    ]
                }]
            }]
        }]
    return []

# MCP Tool implementations - Odds Only

async def handle_get_sports(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get available sports from Odds API"""
    use_test_mode = args.get("use_test_mode", False)  # Default to live data
    all_sports = args.get("all_sports", False)
    
    if use_test_mode:
        sports_data = get_mock_sports_data()
        return {
            "ok": True,
            "content_md": f"## Available Sports (Test Mode)\n\nFound {len(sports_data)} sports",
            "data": {"sports": sports_data, "total": len(sports_data)},
            "meta": {"source": "odds_api_mock", "test_mode": True, "timestamp": now_iso()}
        }
    
    params = {}
    if all_sports:
        params["all"] = "true"
    
    resp = await odds_api_get("sports", params)
    if not resp.get("ok"):
        return resp
    
    sports_data = resp["data"]
    return {
        "ok": True,
        "content_md": f"## Available Sports\n\nFound {len(sports_data)} sports",
        "data": {"sports": sports_data, "total": len(sports_data)},
        "meta": {"source": "odds_api", "test_mode": False, "timestamp": now_iso()}
    }

async def handle_get_odds(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get odds for a specific sport"""
    sport = args.get("sport", "")
    use_test_mode = args.get("use_test_mode", False)  # Default to live data
    regions = args.get("regions", "us")
    markets = args.get("markets", "h2h")
    odds_format = args.get("odds_format", "american")
    
    if use_test_mode:
        odds_data = get_mock_odds_data(sport)
        return {
            "ok": True,
            "content_md": f"## Odds for {sport} (Test Mode)\n\nFound {len(odds_data)} games",
            "data": {"odds": odds_data, "total": len(odds_data)},
            "meta": {"source": "odds_api_mock", "sport": sport, "test_mode": True, "timestamp": now_iso()}
        }
    
    params = {
        "regions": regions,
        "markets": markets,
        "oddsFormat": odds_format
    }
    
    resp = await odds_api_get(f"sports/{sport}/odds", params)
    if not resp.get("ok"):
        return resp
    
    odds_data = resp["data"]
    return {
        "ok": True,
        "content_md": f"## Odds for {sport}\n\nFound {len(odds_data)} games",
        "data": {"odds": odds_data, "total": len(odds_data)},
        "meta": {"source": "odds_api", "sport": sport, "test_mode": False, "timestamp": now_iso()}
    }

async def handle_get_quota_info(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get API quota info"""
    use_test_mode = args.get("use_test_mode", False)  # Default to live data
    
    if use_test_mode:
        quota_data = {"used": 45, "remaining": 455, "total": 500}
        return {
            "ok": True,
            "content_md": f"## API Quota (Test Mode)\n\nUsed: {quota_data['used']}, Remaining: {quota_data['remaining']}",
            "data": {"quota": quota_data},
            "meta": {"source": "odds_api_mock", "test_mode": True, "timestamp": now_iso()}
        }
    
    # Make a minimal API call to check quota
    resp = await odds_api_get("sports", {"all": "false"})
    if not resp.get("ok"):
        return resp
    
    quota_data = {"status": "valid", "sports_available": len(resp["data"])}
    return {
        "ok": True,
        "content_md": f"## API Quota\n\nAPI key is valid. {quota_data['sports_available']} sports available",
        "data": {"quota": quota_data},
        "meta": {"source": "odds_api", "test_mode": False, "timestamp": now_iso()}
    }

async def handle_get_event_odds(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get odds for a specific event (for player props)"""
    sport = args.get("sport", "")
    event_id = args.get("event_id", "")
    use_test_mode = args.get("use_test_mode", False)  # Default to live data
    regions = args.get("regions", "us")
    markets = args.get("markets", "h2h")
    odds_format = args.get("odds_format", "american")
    
    if not event_id:
        return {"ok": False, "error": "event_id is required"}
    
    if use_test_mode:
        # Mock player props data
        event_data = {
            "id": event_id,
            "sport_key": sport,
            "commence_time": "2025-08-12T00:00:00Z",
            "home_team": "Test Home Team",
            "away_team": "Test Away Team",
            "bookmakers": [{
                "key": "fanduel",
                "title": "FanDuel",
                "markets": [{
                    "key": "batter_home_runs",
                    "outcomes": [
                        {"name": "Over", "description": "Test Player", "price": -110, "point": 0.5},
                        {"name": "Under", "description": "Test Player", "price": -110, "point": 0.5}
                    ]
                }]
            }]
        }
        return {
            "ok": True,
            "content_md": f"## Event Odds for {event_id} (Test Mode)\n\nMock player props data",
            "data": {"event": event_data},
            "meta": {"source": "odds_api_mock", "event_id": event_id, "test_mode": True, "timestamp": now_iso()}
        }
    
    # Build the endpoint path for event-specific odds
    params = {
        "regions": regions,
        "markets": markets,
        "oddsFormat": odds_format
    }
    
    resp = await odds_api_get(f"sports/{sport}/events/{event_id}/odds", params)
    if not resp.get("ok"):
        return resp
    
    event_data = resp["data"]
    return {
        "ok": True,
        "content_md": f"## Event Odds for {event_id}\n\nPlayer props and event-specific odds",
        "data": {"event": event_data},
        "meta": {"source": "odds_api", "event_id": event_id, "test_mode": False, "timestamp": now_iso()}
    }


# MCP Tool registry
TOOLS = {
    "getSports": {
        "description": "Get available sports from Odds API",
        "parameters": {
            "type": "object",
            "properties": {
                "all_sports": {"type": "boolean", "description": "Include inactive sports", "optional": True},
                "use_test_mode": {"type": "boolean", "description": "Use mock data", "optional": True}
            }
        },
        "handler": handle_get_sports
    },
    "getOdds": {
        "description": "Get odds for a specific sport",
        "parameters": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "Sport key (e.g. 'baseball_mlb')"},
                "regions": {"type": "string", "description": "Regions (default: 'us')", "optional": True},
                "markets": {"type": "string", "description": "Markets (default: 'h2h')", "optional": True},
                "odds_format": {"type": "string", "description": "Odds format (default: 'american')", "optional": True},
                "use_test_mode": {"type": "boolean", "description": "Use mock data", "optional": True}
            },
            "required": ["sport"]
        },
        "handler": handle_get_odds
    },
    "getQuotaInfo": {
        "description": "Get Odds API quota information",
        "parameters": {
            "type": "object",
            "properties": {
                "use_test_mode": {"type": "boolean", "description": "Use mock data", "optional": True}
            }
        },
        "handler": handle_get_quota_info
    },
    "getEventOdds": {
        "description": "Get odds for a specific event (for player props)",
        "parameters": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "Sport key (e.g. 'baseball_mlb')"},
                "event_id": {"type": "string", "description": "Event ID from odds API"},
                "regions": {"type": "string", "description": "Regions (default: 'us')", "optional": True},
                "markets": {"type": "string", "description": "Markets (default: 'h2h')", "optional": True},
                "odds_format": {"type": "string", "description": "Odds format (default: 'american')", "optional": True},
                "use_test_mode": {"type": "boolean", "description": "Use mock data", "optional": True}
            },
            "required": ["sport", "event_id"]
        },
        "handler": handle_get_event_odds
    }
}

# MCP Protocol handlers
async def handle_initialize(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP initialize"""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "sports-ai-mcp-odds-only",
            "version": "4.0.0"
        }
    }

async def handle_tools_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tools/list"""
    tools_list = []
    for name, tool_info in TOOLS.items():
        tools_list.append({
            "name": name,
            "description": tool_info["description"],
            "inputSchema": tool_info["parameters"]
        })
    
    return {"tools": tools_list}

async def handle_tools_call(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tools/call"""
    name = params.get("name", "")
    arguments = params.get("arguments", {})
    
    if name not in TOOLS:
        return {"error": {"code": -32602, "message": f"Unknown tool: {name}"}}
    
    try:
        handler = TOOLS[name]["handler"]
        result = await handler(arguments)
        return result
    except Exception as e:
        return {"error": {"code": -32603, "message": f"Tool execution failed: {str(e)}"}}

# HTTP handlers
async def handle_mcp_request(request: Request) -> Response:
    """Handle MCP requests"""
    try:
        body = await request.json()
    except:
        return Response(
            json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}}),
            status_code=400,
            media_type="application/json"
        )
    
    method = body.get("method", "")
    params = body.get("params", {})
    request_id = body.get("id", "1")
    
    # Handle different MCP methods
    if method == "initialize":
        result = await handle_initialize(params)
    elif method == "tools/list":
        result = await handle_tools_list(params)
    elif method == "tools/call":
        result = await handle_tools_call(params)
    else:
        result = {"error": {"code": -32601, "message": f"Method not found: {method}"}}
    
    # Create response
    response_data = {
        "jsonrpc": "2.0",
        "id": request_id
    }
    
    if "error" in result:
        response_data["error"] = result["error"]
    else:
        response_data["result"] = result
    
    return Response(
        json.dumps(response_data, ensure_ascii=False),
        media_type="application/json"
    )

# Create Starlette app
routes = [
    Route("/mcp", handle_mcp_request, methods=["POST"]),
    Route("/mcp/", handle_mcp_request, methods=["POST"]),  # Handle trailing slash
]

app = Starlette(routes=routes)

@app.on_event("startup")
async def startup():
    print("=" * 60)
    print("Pure MCP Odds Server Starting - Odds Only v4.0")
    print(f"Odds Tools: {len(TOOLS)}")
    print(f"Total Tools: {len(TOOLS)}")
    print("Server URL: http://0.0.0.0:8080/mcp")
    print("=" * 60)
    
    for tool_name in sorted(TOOLS.keys()):
        print(f"Registered tool: {tool_name}")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown():
    global _http_client
    if _http_client:
        await _http_client.aclose()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")