#!/usr/bin/env python3
"""
Soccer MCP Server for Sports AI

A dedicated MCP implementation focused on soccer/football data and analytics.
Uses Football-Data.org API for comprehensive soccer data across major leagues.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

# Configuration
FOOTBALL_DATA_API_BASE = "https://api.football-data.org/v4"
USER_AGENT = "sports-ai-soccer-mcp/1.0"
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "").strip()

# HTTP client
_http_client: Optional[httpx.AsyncClient] = None

async def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json"
        }
        if FOOTBALL_DATA_API_KEY:
            headers["X-Auth-Token"] = FOOTBALL_DATA_API_KEY
        
        _http_client = httpx.AsyncClient(
            timeout=20.0,
            headers=headers
        )
    return _http_client

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# Soccer API functions
async def football_data_api_get(endpoint: str, params: Optional[Dict[str, Any]] = None, unfold_details: bool = False) -> Dict[str, Any]:
    """Make Football-Data.org API request"""
    url = f"{FOOTBALL_DATA_API_BASE}/{endpoint}"
    query_params = params or {}
    
    # Build headers
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    if FOOTBALL_DATA_API_KEY:
        headers["X-Auth-Token"] = FOOTBALL_DATA_API_KEY
    
    # Add unfolding headers for detailed match statistics
    if unfold_details:
        headers.update({
            "X-Unfold-Lineups": "true",
            "X-Unfold-Bookings": "true", 
            "X-Unfold-Goals": "true",
            "X-Unfold-Subs": "true"
        })
    
    # Create a new client with the correct headers
    async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
        try:
            r = await client.get(url, params=query_params)
            if r.status_code >= 400:
                return {"ok": False, "error": f"Football-Data API error {r.status_code}: {r.text[:200]}"}
            return {"ok": True, "data": r.json()}
        except Exception as e:
            return {"ok": False, "error": f"Football-Data API request failed: {str(e)}"}

# Soccer Tool implementations

async def handle_get_competitions(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get available soccer competitions"""
    areas = args.get("areas")  # Optional filter by area IDs
    
    if not FOOTBALL_DATA_API_KEY:
        return {
            "ok": False,
            "error": "FOOTBALL_DATA_API_KEY not configured"
        }
    
    params = {}
    if areas:
        params["areas"] = areas
    
    resp = await football_data_api_get("competitions", params)
    if not resp.get("ok"):
        return resp
    
    payload = resp["data"]
    competitions = payload.get("competitions", [])
    
    return {
        "ok": True,
        "content_md": f"## Available Soccer Competitions\n\nFound {len(competitions)} competitions",
        "data": {"source": "football_data_api", "competitions": competitions, "count": len(competitions)},
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_competition_matches(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get matches for a specific competition"""
    competition_id = args.get("competition_id")
    if not competition_id:
        return {"ok": False, "error": "competition_id is required"}
    
    date_from = args.get("date_from")  # YYYY-MM-DD
    date_to = args.get("date_to")      # YYYY-MM-DD
    matchday = args.get("matchday")    # Specific matchday
    status = args.get("status")        # SCHEDULED, LIVE, IN_PLAY, FINISHED, etc.
    
    if not FOOTBALL_DATA_API_KEY:
        return {
            "ok": False,
            "error": "FOOTBALL_DATA_API_KEY not configured"
        }
    
    params = {}
    if date_from:
        params["dateFrom"] = date_from
    if date_to:
        params["dateTo"] = date_to
    if matchday:
        params["matchday"] = matchday
    if status:
        params["status"] = status
    
    resp = await football_data_api_get(f"competitions/{competition_id}/matches", params)
    if not resp.get("ok"):
        return resp
    
    payload = resp["data"]
    matches = payload.get("matches", [])
    
    return {
        "ok": True,
        "content_md": f"## Competition Matches\n\nFound {len(matches)} matches for competition {competition_id}",
        "data": {"source": "football_data_api", "competition_id": competition_id, "matches": matches, "count": len(matches)},
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_competition_standings(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get standings/table for a specific competition"""
    competition_id = args.get("competition_id")
    if not competition_id:
        return {"ok": False, "error": "competition_id is required"}
    
    season = args.get("season")      # Year (e.g., 2024)
    matchday = args.get("matchday")  # Specific matchday
    
    if not FOOTBALL_DATA_API_KEY:
        return {
            "ok": False,
            "error": "FOOTBALL_DATA_API_KEY not configured"
        }
    
    params = {}
    if season:
        params["season"] = season
    if matchday:
        params["matchday"] = matchday
    
    resp = await football_data_api_get(f"competitions/{competition_id}/standings", params)
    if not resp.get("ok"):
        return resp
    
    payload = resp["data"]
    
    return {
        "ok": True,
        "content_md": f"## Competition Standings\n\nStandings for competition {competition_id}",
        "data": {"source": "football_data_api", "competition_id": competition_id, "standings": payload},
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_competition_teams(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get teams in a specific competition"""
    competition_id = args.get("competition_id")
    if not competition_id:
        return {"ok": False, "error": "competition_id is required"}
    
    season = args.get("season")  # Year (e.g., 2024)
    
    if not FOOTBALL_DATA_API_KEY:
        return {
            "ok": False,
            "error": "FOOTBALL_DATA_API_KEY not configured"
        }
    
    params = {}
    if season:
        params["season"] = season
    
    resp = await football_data_api_get(f"competitions/{competition_id}/teams", params)
    if not resp.get("ok"):
        return resp
    
    payload = resp["data"]
    teams = payload.get("teams", [])
    
    return {
        "ok": True,
        "content_md": f"## Competition Teams\n\nFound {len(teams)} teams in competition {competition_id}",
        "data": {"source": "football_data_api", "competition_id": competition_id, "teams": teams, "count": len(teams)},
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_team_matches(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get matches for a specific team"""
    team_id = args.get("team_id")
    if not team_id:
        return {"ok": False, "error": "team_id is required"}
    
    date_from = args.get("date_from")  # YYYY-MM-DD
    date_to = args.get("date_to")      # YYYY-MM-DD
    season = args.get("season")        # Year
    status = args.get("status")        # SCHEDULED, LIVE, IN_PLAY, FINISHED, etc.
    venue = args.get("venue")          # HOME, AWAY
    limit = args.get("limit")          # Number of matches
    
    if not FOOTBALL_DATA_API_KEY:
        return {
            "ok": False,
            "error": "FOOTBALL_DATA_API_KEY not configured"
        }
    
    params = {}
    if date_from:
        params["dateFrom"] = date_from
    if date_to:
        params["dateTo"] = date_to
    if season:
        params["season"] = season
    if status:
        params["status"] = status
    if venue:
        params["venue"] = venue
    if limit:
        params["limit"] = limit
    
    resp = await football_data_api_get(f"teams/{team_id}/matches", params)
    if not resp.get("ok"):
        return resp
    
    payload = resp["data"]
    matches = payload.get("matches", [])
    
    return {
        "ok": True,
        "content_md": f"## Team Matches\n\nFound {len(matches)} matches for team {team_id}",
        "data": {"source": "football_data_api", "team_id": team_id, "matches": matches, "count": len(matches)},
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_match_details(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get details for a specific match with full statistics"""
    match_id = args.get("match_id")
    if not match_id:
        return {"ok": False, "error": "match_id is required"}
    
    if not FOOTBALL_DATA_API_KEY:
        return {
            "ok": False,
            "error": "FOOTBALL_DATA_API_KEY not configured"
        }
    
    # Use unfolding headers to get detailed statistics
    resp = await football_data_api_get(f"matches/{match_id}", unfold_details=True)
    if not resp.get("ok"):
        return resp
    
    payload = resp["data"]
    
    return {
        "ok": True,
        "content_md": f"## Match Details\n\nDetails for match {match_id} with full statistics",
        "data": {"source": "football_data_api", "match": payload},
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_top_scorers(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get top scorers for a specific competition"""
    competition_id = args.get("competition_id")
    if not competition_id:
        return {"ok": False, "error": "competition_id is required"}
    
    season = args.get("season")  # Year
    limit = args.get("limit", 10)  # Default to top 10
    
    if not FOOTBALL_DATA_API_KEY:
        return {
            "ok": False,
            "error": "FOOTBALL_DATA_API_KEY not configured"
        }
    
    params = {"limit": limit}
    if season:
        params["season"] = season
    
    resp = await football_data_api_get(f"competitions/{competition_id}/scorers", params)
    if not resp.get("ok"):
        return resp
    
    payload = resp["data"]
    scorers = payload.get("scorers", [])
    
    return {
        "ok": True,
        "content_md": f"## Top Scorers\n\nFound {len(scorers)} top scorers for competition {competition_id}",
        "data": {"source": "football_data_api", "competition_id": competition_id, "scorers": scorers, "count": len(scorers)},
        "meta": {"timestamp": now_iso()}
    }

# MCP Tool registry
TOOLS = {
    "getCompetitions": {
        "description": "Get available soccer competitions from Football-Data.org",
        "parameters": {
            "type": "object",
            "properties": {
                "areas": {"type": "string", "description": "Comma-separated area IDs to filter by", "optional": True}
            }
        },
        "handler": handle_get_competitions
    },
    "getCompetitionMatches": {
        "description": "Get matches for a specific competition",
        "parameters": {
            "type": "object",
            "properties": {
                "competition_id": {"type": "string", "description": "Competition ID (e.g., 'PL', '2021')"},
                "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)", "optional": True},
                "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)", "optional": True},
                "matchday": {"type": "integer", "description": "Specific matchday", "optional": True},
                "status": {"type": "string", "description": "Match status (SCHEDULED, LIVE, FINISHED, etc.)", "optional": True}
            },
            "required": ["competition_id"]
        },
        "handler": handle_get_competition_matches
    },
    "getCompetitionStandings": {
        "description": "Get standings/table for a specific competition",
        "parameters": {
            "type": "object",
            "properties": {
                "competition_id": {"type": "string", "description": "Competition ID (e.g., 'PL', '2021')"},
                "season": {"type": "integer", "description": "Season year (e.g., 2024)", "optional": True},
                "matchday": {"type": "integer", "description": "Specific matchday", "optional": True}
            },
            "required": ["competition_id"]
        },
        "handler": handle_get_competition_standings
    },
    "getCompetitionTeams": {
        "description": "Get teams in a specific competition",
        "parameters": {
            "type": "object",
            "properties": {
                "competition_id": {"type": "string", "description": "Competition ID (e.g., 'PL', '2021')"},
                "season": {"type": "integer", "description": "Season year (e.g., 2024)", "optional": True}
            },
            "required": ["competition_id"]
        },
        "handler": handle_get_competition_teams
    },
    "getTeamMatches": {
        "description": "Get matches for a specific team",
        "parameters": {
            "type": "object",
            "properties": {
                "team_id": {"type": "integer", "description": "Team ID"},
                "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)", "optional": True},
                "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)", "optional": True},
                "season": {"type": "integer", "description": "Season year (e.g., 2024)", "optional": True},
                "status": {"type": "string", "description": "Match status (SCHEDULED, LIVE, FINISHED, etc.)", "optional": True},
                "venue": {"type": "string", "description": "Venue filter (HOME, AWAY)", "optional": True},
                "limit": {"type": "integer", "description": "Number of matches to return", "optional": True}
            },
            "required": ["team_id"]
        },
        "handler": handle_get_team_matches
    },
    "getMatchDetails": {
        "description": "Get details for a specific match",
        "parameters": {
            "type": "object",
            "properties": {
                "match_id": {"type": "integer", "description": "Match ID"}
            },
            "required": ["match_id"]
        },
        "handler": handle_get_match_details
    },
    "getTopScorers": {
        "description": "Get top scorers for a specific competition",
        "parameters": {
            "type": "object",
            "properties": {
                "competition_id": {"type": "string", "description": "Competition ID (e.g., 'PL', '2021')"},
                "season": {"type": "integer", "description": "Season year (e.g., 2024)", "optional": True},
                "limit": {"type": "integer", "description": "Number of top scorers to return (default: 10)", "optional": True}
            },
            "required": ["competition_id"]
        },
        "handler": handle_get_top_scorers
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
            "name": "soccer-mcp",
            "version": "1.0.0"
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
            "server": "soccer-mcp",
            "version": "1.0.0",
            "timestamp": now_iso(),
            "api_key_configured": bool(FOOTBALL_DATA_API_KEY),
            "tools_count": len(TOOLS),
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
    print("Soccer MCP Server Starting - v1.0")
    print(f"Soccer Tools: {len(TOOLS)}")
    print(f"Total Tools: {len(TOOLS)}")
    print("Server URL: http://0.0.0.0:8080/mcp")
    print(f"API Key Configured: {bool(FOOTBALL_DATA_API_KEY)}")
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