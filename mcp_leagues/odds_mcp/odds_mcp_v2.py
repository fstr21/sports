#!/usr/bin/env python3
"""
Odds MCP Server v2 - Using the-odds Python Package

A clean MCP implementation using the 'the-odds' Python package
for more reliable access to The Odds API data.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

# Use direct HTTP calls instead of the-odds package due to URL encoding bug
import httpx
ODDS_PACKAGE_AVAILABLE = True  # We'll use httpx for direct HTTP calls

# Configuration
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "").strip()
USER_AGENT = "sports-ai-odds-mcp-v2/1.0"

# Initialize HTTP client for direct API calls
_http_client: Optional[httpx.AsyncClient] = None
BASE_URL = "https://api.the-odds-api.com/v4"

async def get_http_client() -> httpx.AsyncClient:
    """Get the HTTP client instance"""
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=30.0)
    return _http_client

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

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
            "commence_time": "2025-08-14T23:40:00Z",
            "home_team": "Colorado Rockies",
            "away_team": "Arizona Diamondbacks",
            "bookmakers": [{
                "key": "fanduel",
                "title": "FanDuel",
                "markets": [{
                    "key": "h2h",
                    "outcomes": [
                        {"name": "Colorado Rockies", "price": -120},
                        {"name": "Arizona Diamondbacks", "price": 105}
                    ]
                }, {
                    "key": "spreads",
                    "outcomes": [
                        {"name": "Colorado Rockies", "price": -110, "point": -1.5},
                        {"name": "Arizona Diamondbacks", "price": -110, "point": 1.5}
                    ]
                }, {
                    "key": "totals",
                    "outcomes": [
                        {"name": "Over", "price": -110, "point": 9.5},
                        {"name": "Under", "price": -110, "point": 9.5}
                    ]
                }]
            }]
        }]
    return []

# MCP Tool implementations

async def handle_get_sports(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get available sports from Odds API"""
    use_test_mode = args.get("use_test_mode", False)
    all_sports = args.get("all_sports", False)
    
    if use_test_mode:
        sports_data = get_mock_sports_data()
        return {
            "ok": True,
            "content_md": f"## Available Sports (Test Mode)\n\nFound {len(sports_data)} sports",
            "data": {"sports": sports_data, "total": len(sports_data)},
            "meta": {"source": "the_odds_mock", "test_mode": True, "timestamp": now_iso()}
        }
    
    if not ODDS_API_KEY:
        return {
            "ok": False,
            "error": "ODDS_API_KEY not configured"
        }
    
    try:
        # Use direct HTTP calls instead of the-odds package
        client = await get_http_client()
        
        url = f"{BASE_URL}/sports"
        params = {"apiKey": ODDS_API_KEY}
        if all_sports:
            params["all"] = "true"
        
        response = await client.get(url, params=params)
        
        if response.status_code == 200:
            sports_data = response.json()
            return {
                "ok": True,
                "content_md": f"## Available Sports\n\nFound {len(sports_data)} sports",
                "data": {"sports": sports_data, "total": len(sports_data)},
                "meta": {"source": "direct_http", "test_mode": False, "timestamp": now_iso()}
            }
        else:
            return {
                "ok": False,
                "error": f"API returned {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {
            "ok": False,
            "error": f"Failed to get sports: {str(e)}"
        }

async def handle_get_odds(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get odds for a specific sport"""
    sport = args.get("sport", "")
    use_test_mode = args.get("use_test_mode", False)
    regions = args.get("regions", "us")  # Default to "us" now that we're using direct HTTP
    markets = args.get("markets", "h2h")
    odds_format = args.get("odds_format", "american")
    
    if use_test_mode:
        odds_data = get_mock_odds_data(sport)
        return {
            "ok": True,
            "content_md": f"## Odds for {sport} (Test Mode)\n\nFound {len(odds_data)} games",
            "data": {"odds": odds_data, "total": len(odds_data)},
            "meta": {"source": "the_odds_mock", "sport": sport, "test_mode": True, "timestamp": now_iso()}
        }
    
    if not ODDS_API_KEY:
        return {
            "ok": False,
            "error": "ODDS_API_KEY not configured"
        }
    
    try:
        # Use direct HTTP calls instead of the-odds package (which has URL encoding bugs)
        client = await get_http_client()
        
        url = f"{BASE_URL}/sports/{sport}/odds"
        params = {
            "apiKey": ODDS_API_KEY,
            "regions": regions,
            "markets": markets,
            "oddsFormat": odds_format
        }
        
        response = await client.get(url, params=params)
        
        if response.status_code == 200:
            odds_data = response.json()
            
            # Direct HTTP returns a list of games on success
            if isinstance(odds_data, list):
                return {
                    "ok": True,
                    "content_md": f"## Odds for {sport}\n\nFound {len(odds_data)} games",
                    "data": {"odds": odds_data, "total": len(odds_data)},
                    "meta": {"source": "direct_http", "sport": sport, "test_mode": False, "timestamp": now_iso()}
                }
            else:
                return {
                    "ok": True,
                    "content_md": f"## Odds for {sport}\n\nUnexpected response format",
                    "data": {"odds": odds_data, "total": 0},
                    "meta": {"source": "direct_http", "sport": sport, "test_mode": False, "timestamp": now_iso()}
                }
        else:
            # Handle API errors
            try:
                error_data = response.json()
                return {
                    "ok": True,  # Keep ok=True since the MCP call succeeded, but indicate API error in data
                    "content_md": f"## Odds for {sport}\n\nAPI Error: {error_data.get('message', 'Unknown error')}",
                    "data": {"odds": error_data, "total": 0},
                    "meta": {"source": "direct_http", "sport": sport, "test_mode": False, "timestamp": now_iso()}
                }
            except:
                return {
                    "ok": False,
                    "error": f"API returned {response.status_code}: {response.text}"
                }
    except Exception as e:
        return {
            "ok": False,
            "error": f"Failed to get odds for {sport}: {str(e)}"
        }

async def handle_get_quota_info(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get API quota information"""
    use_test_mode = args.get("use_test_mode", False)
    
    if use_test_mode:
        quota_data = {"used": 45, "remaining": 455, "total": 500}
        return {
            "ok": True,
            "content_md": f"## API Quota (Test Mode)\n\nUsed: {quota_data['used']}, Remaining: {quota_data['remaining']}",
            "data": {"quota": quota_data},
            "meta": {"source": "the_odds_mock", "test_mode": True, "timestamp": now_iso()}
        }
    
    client = get_odds_client()
    if not client:
        return {
            "ok": False,
            "error": "Odds client not available. Check ODDS_API_KEY and 'the-odds' package installation."
        }
    
    try:
        # Get sports to check quota (the-odds package doesn't have direct quota endpoint)
        sports_data = client.v4.get_sports(all=False)
        quota_data = {"status": "valid", "sports_available": len(sports_data)}
        
        return {
            "ok": True,
            "content_md": f"## API Quota\n\nAPI key is valid. {quota_data['sports_available']} sports available",
            "data": {"quota": quota_data},
            "meta": {"source": "the_odds_package", "test_mode": False, "timestamp": now_iso()}
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"Failed to check quota: {str(e)}"
        }

async def handle_get_event_odds(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get odds for a specific event using direct HTTP calls"""
    sport = args.get("sport", "")
    event_id = args.get("event_id", "")
    use_test_mode = args.get("use_test_mode", False)
    regions = args.get("regions", "us")
    markets = args.get("markets", "h2h")
    odds_format = args.get("odds_format", "american")
    
    if not event_id:
        return {"ok": False, "error": "event_id is required"}
    
    if use_test_mode:
        event_data = {
            "id": event_id,
            "sport_key": sport,
            "commence_time": "2025-08-14T23:40:00Z",
            "home_team": "Test Home Team",
            "away_team": "Test Away Team",
            "bookmakers": [{
                "key": "fanduel",
                "title": "FanDuel",
                "markets": [{
                    "key": "batter_hits",
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
            "meta": {"source": "the_odds_mock", "event_id": event_id, "test_mode": True, "timestamp": now_iso()}
        }
    
    if not ODDS_API_KEY:
        return {
            "ok": False,
            "error": "ODDS_API_KEY not configured"
        }
    
    try:
        # Use direct HTTP calls to event-specific endpoint
        client = await get_http_client()
        
        url = f"{BASE_URL}/sports/{sport}/events/{event_id}/odds"
        params = {
            "apiKey": ODDS_API_KEY,
            "regions": regions,
            "markets": markets,
            "oddsFormat": odds_format
        }
        
        response = await client.get(url, params=params)
        
        if response.status_code == 200:
            event_data = response.json()
            
            return {
                "ok": True,
                "content_md": f"## Event Odds for {event_id}\n\nEvent-specific odds data",
                "data": {"event": event_data},
                "meta": {"source": "direct_http", "event_id": event_id, "test_mode": False, "timestamp": now_iso()}
            }
        else:
            # Handle API errors
            try:
                error_data = response.json()
                return {
                    "ok": True,  # Keep ok=True since the MCP call succeeded, but indicate API error in data
                    "content_md": f"## Event Odds for {event_id}\n\nAPI Error: {error_data.get('message', 'Unknown error')}",
                    "data": {"event": error_data, "total": 0},
                    "meta": {"source": "direct_http", "event_id": event_id, "test_mode": False, "timestamp": now_iso()}
                }
            except:
                return {
                    "ok": False,
                    "error": f"API returned {response.status_code}: {response.text}"
                }
    except Exception as e:
        return {
            "ok": False,
            "error": f"Failed to get event odds: {str(e)}"
        }

async def handle_get_events(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get upcoming events for a specific sport"""
    sport = args.get("sport", "")
    use_test_mode = args.get("use_test_mode", False)
    
    if use_test_mode:
        events_data = [{
            "id": "mock_event_1",
            "sport_key": sport,
            "commence_time": "2025-08-14T23:40:00Z",
            "home_team": "Test Home Team",
            "away_team": "Test Away Team"
        }]
        return {
            "ok": True,
            "content_md": f"## Events for {sport} (Test Mode)\n\nFound {len(events_data)} events",
            "data": {"events": events_data, "total": len(events_data)},
            "meta": {"source": "the_odds_mock", "sport": sport, "test_mode": True, "timestamp": now_iso()}
        }
    
    if not ODDS_API_KEY:
        return {
            "ok": False,
            "error": "ODDS_API_KEY not configured"
        }
    
    try:
        # Use direct HTTP calls to get events
        client = await get_http_client()
        
        url = f"{BASE_URL}/sports/{sport}/events"
        params = {"apiKey": ODDS_API_KEY}
        
        response = await client.get(url, params=params)
        
        if response.status_code == 200:
            events_data = response.json()
            
            return {
                "ok": True,
                "content_md": f"## Events for {sport}\n\nFound {len(events_data)} upcoming events",
                "data": {"events": events_data, "total": len(events_data)},
                "meta": {"source": "direct_http", "sport": sport, "test_mode": False, "timestamp": now_iso()}
            }
        else:
            # Handle API errors
            try:
                error_data = response.json()
                return {
                    "ok": True,  # Keep ok=True since the MCP call succeeded, but indicate API error in data
                    "content_md": f"## Events for {sport}\n\nAPI Error: {error_data.get('message', 'Unknown error')}",
                    "data": {"events": error_data, "total": 0},
                    "meta": {"source": "direct_http", "sport": sport, "test_mode": False, "timestamp": now_iso()}
                }
            except:
                return {
                    "ok": False,
                    "error": f"API returned {response.status_code}: {response.text}"
                }
    except Exception as e:
        return {
            "ok": False,
            "error": f"Failed to get events for {sport}: {str(e)}"
        }

# MCP Tool registry
TOOLS = {
    "getSports": {
        "description": "Get available sports from Odds API using the-odds package",
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
        "description": "Get odds for a specific sport using the-odds package",
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
        "description": "Get odds for a specific event (placeholder)",
        "parameters": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "Sport key (e.g. 'baseball_mlb')"},
                "event_id": {"type": "string", "description": "Event ID"},
                "regions": {"type": "string", "description": "Regions (default: 'us')", "optional": True},
                "markets": {"type": "string", "description": "Markets (default: 'h2h')", "optional": True},
                "odds_format": {"type": "string", "description": "Odds format (default: 'american')", "optional": True},
                "use_test_mode": {"type": "boolean", "description": "Use mock data", "optional": True}
            },
            "required": ["sport", "event_id"]
        },
        "handler": handle_get_event_odds
    },
    "getEvents": {
        "description": "Get upcoming events for a specific sport",
        "parameters": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "Sport key (e.g. 'baseball_mlb')"},
                "use_test_mode": {"type": "boolean", "description": "Use mock data", "optional": True}
            },
            "required": ["sport"]
        },
        "handler": handle_get_events
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
            "name": "odds-mcp-v2",
            "version": "2.0.0"
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

# Health check handler for Railway
async def handle_health_check(request: Request) -> Response:
    """Health check endpoint for Railway deployment"""
    return Response(
        json.dumps({
            "status": "ok",
            "server": "odds-mcp-v2",
            "version": "2.0.0",
            "timestamp": now_iso(),
            "package_available": ODDS_PACKAGE_AVAILABLE,
            "api_key_configured": bool(ODDS_API_KEY),
            "endpoints": {
                "mcp": "/mcp (POST)",
                "health": "/ (GET)"
            }
        }),
        media_type="application/json"
    )

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
    Route("/", handle_health_check, methods=["GET"]),  # Health check for Railway
    Route("/mcp", handle_mcp_request, methods=["POST"]),
    Route("/mcp/", handle_mcp_request, methods=["POST"]),  # Handle trailing slash
]

app = Starlette(routes=routes)

@app.on_event("startup")
async def startup():
    print("=" * 60)
    print("Odds MCP Server v2 Starting - Using the-odds Package")
    print(f"Odds Tools: {len(TOOLS)}")
    print(f"Total Tools: {len(TOOLS)}")
    print("Server URL: http://0.0.0.0:8080/mcp")
    print(f"Package Available: {ODDS_PACKAGE_AVAILABLE}")
    print(f"API Key Configured: {bool(ODDS_API_KEY)}")
    print("=" * 60)
    
    for tool_name in sorted(TOOLS.keys()):
        print(f"Registered tool: {tool_name}")
    print("=" * 60)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")