#!/usr/bin/env python3
"""
College Football MCP Server for Sports AI

A dedicated MCP implementation focused on college football statistics and analytics.
Uses College Football Data API for comprehensive college football data.
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
CFBD_API_BASE = "https://api.collegefootballdata.com"
USER_AGENT = "sports-ai-cfb-mcp/1.0"

# HTTP client
_http_client: Optional[httpx.AsyncClient] = None

async def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        # Get API key from environment
        api_key = os.getenv("CFBD_API_KEY")
        if not api_key:
            raise ValueError("CFBD_API_KEY environment variable is required")
        
        headers = {
            "user-agent": USER_AGENT,
            "accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        _http_client = httpx.AsyncClient(
            timeout=20.0,
            headers=headers
        )
    return _http_client

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# CFBD API functions
async def cfbd_api_get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make CFBD API request"""
    url = f"{CFBD_API_BASE}/{endpoint}"
    query_params = params or {}
    
    client = await get_http_client()
    try:
        r = await client.get(url, params=query_params)
        if r.status_code >= 400:
            return {"ok": False, "error": f"CFBD API error {r.status_code}: {r.text[:200]}"}
        return {"ok": True, "data": r.json()}
    except Exception as e:
        return {"ok": False, "error": f"CFBD API request failed: {str(e)}"}

# CFB Tool implementations

async def handle_get_cfb_games(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get college football games for a specific year/week"""
    year = int(args.get("year") or datetime.now().year)
    week = args.get("week")
    team = args.get("team")
    conference = args.get("conference")
    
    params = {"year": year}
    if week is not None:
        params["week"] = int(week)
    if team:
        params["team"] = team
    if conference:
        params["conference"] = conference
    
    resp = await cfbd_api_get("games", params)
    if not resp.get("ok"):
        return resp
    
    games = resp["data"]
    
    # Process games data
    games_out = []
    for g in games:
        games_out.append({
            "id": g.get("id"),
            "season": g.get("season"),
            "week": g.get("week"),
            "season_type": g.get("seasonType"),
            "start_date": g.get("startDate"),
            "completed": g.get("completed"),
            "neutral_site": g.get("neutralSite"),
            "conference_game": g.get("conferenceGame"),
            "attendance": g.get("attendance"),
            "venue": g.get("venue"),
            "home_team": g.get("homeTeam"),
            "home_conference": g.get("homeConference"),
            "home_points": g.get("homePoints"),
            "away_team": g.get("awayTeam"),
            "away_conference": g.get("awayConference"),
            "away_points": g.get("awayPoints"),
            "excitement_index": g.get("excitementIndex")
        })
    
    return {
        "ok": True,
        "content_md": f"## CFB Games ({year})\n\nFound {len(games_out)} games",
        "data": {
            "source": "cfbd_api",
            "year": year,
            "week": week,
            "team": team,
            "conference": conference,
            "games": games_out,
            "count": len(games_out)
        },
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_cfb_teams(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get college football teams"""
    year = args.get("year")
    conference = args.get("conference")
    
    params = {}
    if year:
        params["year"] = int(year)
    if conference:
        params["conference"] = conference
    
    resp = await cfbd_api_get("teams", params)
    if not resp.get("ok"):
        return resp
    
    teams = resp["data"]
    
    teams_out = []
    for t in teams:
        teams_out.append({
            "id": t.get("id"),
            "school": t.get("school"),
            "mascot": t.get("mascot"),
            "abbreviation": t.get("abbreviation"),
            "conference": t.get("conference"),
            "division": t.get("division"),
            "classification": t.get("classification"),
            "color": t.get("color"),
            "alternate_color": t.get("alternateColor"),
            "logos": t.get("logos", []),
            "location": t.get("location", {})
        })
    
    return {
        "ok": True,
        "content_md": f"## CFB Teams\n\nFound {len(teams_out)} teams",
        "data": {
            "source": "cfbd_api",
            "year": year,
            "conference": conference,
            "teams": teams_out,
            "count": len(teams_out)
        },
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_cfb_roster(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get team roster"""
    team = args.get("team")
    if not team:
        return {"ok": False, "error": "team is required"}
    
    year = args.get("year")
    
    params = {"team": team}
    if year:
        params["year"] = int(year)
    
    resp = await cfbd_api_get("roster", params)
    if not resp.get("ok"):
        return resp
    
    roster = resp["data"]
    
    players_out = []
    for p in roster:
        players_out.append({
            "id": p.get("id"),
            "first_name": p.get("firstName"),
            "last_name": p.get("lastName"),
            "team": p.get("team"),
            "weight": p.get("weight"),
            "height": p.get("height"),
            "jersey": p.get("jersey"),
            "year": p.get("year"),
            "position": p.get("position"),
            "home_city": p.get("homeCity"),
            "home_state": p.get("homeState"),
            "home_country": p.get("homeCountry")
        })
    
    return {
        "ok": True,
        "content_md": f"## CFB Roster - {team}\n\nFound {len(players_out)} players",
        "data": {
            "source": "cfbd_api",
            "team": team,
            "year": year,
            "players": players_out,
            "count": len(players_out)
        },
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_cfb_player_stats(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get player season statistics"""
    year = int(args.get("year") or datetime.now().year)
    team = args.get("team")
    player = args.get("player")
    category = args.get("category")
    
    params = {"year": year}
    if team:
        params["team"] = team
    if player:
        params["player"] = player
    if category:
        params["category"] = category
    
    resp = await cfbd_api_get("stats/player/season", params)
    if not resp.get("ok"):
        return resp
    
    stats = resp["data"]
    
    stats_out = []
    for s in stats:
        stats_out.append({
            "season": s.get("season"),
            "player_id": s.get("playerId"),
            "player": s.get("player"),
            "position": s.get("position"),
            "team": s.get("team"),
            "conference": s.get("conference"),
            "category": s.get("category"),
            "stat_type": s.get("statType"),
            "stat": s.get("stat")
        })
    
    return {
        "ok": True,
        "content_md": f"## CFB Player Stats ({year})\n\nFound {len(stats_out)} stat records",
        "data": {
            "source": "cfbd_api",
            "year": year,
            "team": team,
            "player": player,
            "category": category,
            "stats": stats_out,
            "count": len(stats_out)
        },
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_cfb_rankings(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get college football rankings"""
    year = int(args.get("year") or datetime.now().year)
    week = args.get("week")
    season_type = args.get("season_type", "regular")
    
    params = {"year": year, "seasonType": season_type}
    if week is not None:
        params["week"] = int(week)
    
    resp = await cfbd_api_get("rankings", params)
    if not resp.get("ok"):
        return resp
    
    rankings = resp["data"]
    
    rankings_out = []
    for r in rankings:
        polls_out = []
        for poll in r.get("polls", []):
            ranks_out = []
            for rank in poll.get("ranks", []):
                ranks_out.append({
                    "rank": rank.get("rank"),
                    "school": rank.get("school"),
                    "conference": rank.get("conference"),
                    "first_place_votes": rank.get("firstPlaceVotes"),
                    "points": rank.get("points")
                })
            
            polls_out.append({
                "poll": poll.get("poll"),
                "ranks": ranks_out
            })
        
        rankings_out.append({
            "season": r.get("season"),
            "season_type": r.get("seasonType"),
            "week": r.get("week"),
            "polls": polls_out
        })
    
    return {
        "ok": True,
        "content_md": f"## CFB Rankings ({year}, Week {week})\n\nFound {len(rankings_out)} ranking periods",
        "data": {
            "source": "cfbd_api",
            "year": year,
            "week": week,
            "season_type": season_type,
            "rankings": rankings_out,
            "count": len(rankings_out)
        },
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_cfb_conferences(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get college football conferences"""
    resp = await cfbd_api_get("conferences", {})
    if not resp.get("ok"):
        return resp
    
    conferences = resp["data"]
    
    conferences_out = []
    for c in conferences:
        conferences_out.append({
            "id": c.get("id"),
            "name": c.get("name"),
            "short_name": c.get("shortName"),
            "abbreviation": c.get("abbreviation"),
            "classification": c.get("classification")
        })
    
    return {
        "ok": True,
        "content_md": f"## CFB Conferences\n\nFound {len(conferences_out)} conferences",
        "data": {
            "source": "cfbd_api",
            "conferences": conferences_out,
            "count": len(conferences_out)
        },
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_cfb_team_records(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get team season records"""
    year = args.get("year")
    team = args.get("team")
    conference = args.get("conference")
    
    params = {}
    if year:
        params["year"] = int(year)
    if team:
        params["team"] = team
    if conference:
        params["conference"] = conference
    
    resp = await cfbd_api_get("records", params)
    if not resp.get("ok"):
        return resp
    
    records = resp["data"]
    
    records_out = []
    for r in records:
        records_out.append({
            "year": r.get("year"),
            "team_id": r.get("teamId"),
            "team": r.get("team"),
            "conference": r.get("conference"),
            "division": r.get("division"),
            "expected_wins": r.get("expectedWins"),
            "total": r.get("total", {}),
            "conference_games": r.get("conferenceGames", {}),
            "home_games": r.get("homeGames", {}),
            "away_games": r.get("awayGames", {})
        })
    
    return {
        "ok": True,
        "content_md": f"## CFB Team Records\n\nFound {len(records_out)} team records",
        "data": {
            "source": "cfbd_api",
            "year": year,
            "team": team,
            "conference": conference,
            "records": records_out,
            "count": len(records_out)
        },
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_cfb_game_stats(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get team game statistics"""
    year = int(args.get("year") or datetime.now().year)
    week = args.get("week")
    team = args.get("team")
    conference = args.get("conference")
    
    params = {"year": year}
    if week is not None:
        params["week"] = int(week)
    if team:
        params["team"] = team
    if conference:
        params["conference"] = conference
    
    resp = await cfbd_api_get("games/teams", params)
    if not resp.get("ok"):
        return resp
    
    game_stats = resp["data"]
    
    stats_out = []
    for gs in game_stats:
        teams_out = []
        for team_stat in gs.get("teams", []):
            stats_dict = {}
            for stat in team_stat.get("stats", []):
                stats_dict[stat.get("category")] = stat.get("stat")
            
            teams_out.append({
                "school": team_stat.get("school"),
                "conference": team_stat.get("conference"),
                "home_away": team_stat.get("homeAway"),
                "points": team_stat.get("points"),
                "stats": stats_dict
            })
        
        stats_out.append({
            "id": gs.get("id"),
            "season": gs.get("season"),
            "week": gs.get("week"),
            "season_type": gs.get("seasonType"),
            "start_date": gs.get("startDate"),
            "neutral_site": gs.get("neutralSite"),
            "conference_game": gs.get("conferenceGame"),
            "attendance": gs.get("attendance"),
            "venue": gs.get("venue"),
            "teams": teams_out
        })
    
    return {
        "ok": True,
        "content_md": f"## CFB Game Stats ({year})\n\nFound {len(stats_out)} games with stats",
        "data": {
            "source": "cfbd_api",
            "year": year,
            "week": week,
            "team": team,
            "conference": conference,
            "game_stats": stats_out,
            "count": len(stats_out)
        },
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_cfb_plays(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get play-by-play data"""
    year = int(args.get("year") or datetime.now().year)
    week = int(args.get("week"))
    team = args.get("team")
    offense = args.get("offense")
    defense = args.get("defense")
    
    if not week:
        return {"ok": False, "error": "week is required"}
    
    params = {"year": year, "week": week}
    if team:
        params["team"] = team
    if offense:
        params["offense"] = offense
    if defense:
        params["defense"] = defense
    
    resp = await cfbd_api_get("plays", params)
    if not resp.get("ok"):
        return resp
    
    plays = resp["data"]
    
    plays_out = []
    for p in plays:
        plays_out.append({
            "id": p.get("id"),
            "offense": p.get("offense"),
            "defense": p.get("defense"),
            "home": p.get("home"),
            "away": p.get("away"),
            "offense_score": p.get("offenseScore"),
            "defense_score": p.get("defenseScore"),
            "drive_id": p.get("driveId"),
            "period": p.get("period"),
            "clock": p.get("clock"),
            "yard_line": p.get("yardLine"),
            "down": p.get("down"),
            "distance": p.get("distance"),
            "yards_gained": p.get("yardsGained"),
            "play_type": p.get("playType"),
            "play_text": p.get("playText")
        })
    
    return {
        "ok": True,
        "content_md": f"## CFB Plays ({year}, Week {week})\n\nFound {len(plays_out)} plays",
        "data": {
            "source": "cfbd_api",
            "year": year,
            "week": week,
            "team": team,
            "offense": offense,
            "defense": defense,
            "plays": plays_out,
            "count": len(plays_out)
        },
        "meta": {"timestamp": now_iso()}
    }

# MCP Tool registry
TOOLS = {
    "getCFBGames": {
        "description": "Get college football games for a specific year/week/team",
        "parameters": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Season year (default: current year)", "optional": True},
                "week": {"type": "integer", "description": "Week number", "optional": True},
                "team": {"type": "string", "description": "Team name", "optional": True},
                "conference": {"type": "string", "description": "Conference name", "optional": True}
            }
        },
        "handler": handle_get_cfb_games
    },
    "getCFBTeams": {
        "description": "Get college football teams",
        "parameters": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Season year", "optional": True},
                "conference": {"type": "string", "description": "Conference name", "optional": True}
            }
        },
        "handler": handle_get_cfb_teams
    },
    "getCFBRoster": {
        "description": "Get team roster for a specific team",
        "parameters": {
            "type": "object",
            "properties": {
                "team": {"type": "string", "description": "Team name"},
                "year": {"type": "integer", "description": "Season year", "optional": True}
            },
            "required": ["team"]
        },
        "handler": handle_get_cfb_roster
    },
    "getCFBPlayerStats": {
        "description": "Get player season statistics",
        "parameters": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Season year (default: current year)", "optional": True},
                "team": {"type": "string", "description": "Team name", "optional": True},
                "player": {"type": "string", "description": "Player name", "optional": True},
                "category": {"type": "string", "description": "Stat category (passing, rushing, receiving, etc.)", "optional": True}
            }
        },
        "handler": handle_get_cfb_player_stats
    },
    "getCFBRankings": {
        "description": "Get college football rankings",
        "parameters": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Season year (default: current year)", "optional": True},
                "week": {"type": "integer", "description": "Week number", "optional": True},
                "season_type": {"type": "string", "description": "Season type (regular, postseason)", "optional": True}
            }
        },
        "handler": handle_get_cfb_rankings
    },
    "getCFBConferences": {
        "description": "Get college football conferences",
        "parameters": {
            "type": "object",
            "properties": {}
        },
        "handler": handle_get_cfb_conferences
    },
    "getCFBTeamRecords": {
        "description": "Get team season records",
        "parameters": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Season year", "optional": True},
                "team": {"type": "string", "description": "Team name", "optional": True},
                "conference": {"type": "string", "description": "Conference name", "optional": True}
            }
        },
        "handler": handle_get_cfb_team_records
    },
    "getCFBGameStats": {
        "description": "Get team game statistics",
        "parameters": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Season year (default: current year)", "optional": True},
                "week": {"type": "integer", "description": "Week number", "optional": True},
                "team": {"type": "string", "description": "Team name", "optional": True},
                "conference": {"type": "string", "description": "Conference name", "optional": True}
            }
        },
        "handler": handle_get_cfb_game_stats
    },
    "getCFBPlays": {
        "description": "Get play-by-play data for games",
        "parameters": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Season year (default: current year)", "optional": True},
                "week": {"type": "integer", "description": "Week number"},
                "team": {"type": "string", "description": "Team name", "optional": True},
                "offense": {"type": "string", "description": "Offensive team name", "optional": True},
                "defense": {"type": "string", "description": "Defensive team name", "optional": True}
            },
            "required": ["week"]
        },
        "handler": handle_get_cfb_plays
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
            "name": "cfb-mcp-server",
            "version": "1.0.0"
        }
    }

async def handle_list_tools(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP list_tools"""
    tools = []
    for name, config in TOOLS.items():
        tools.append({
            "name": name,
            "description": config["description"],
            "inputSchema": config["parameters"]
        })
    
    return {"tools": tools}

async def handle_call_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP call_tool"""
    name = params.get("name")
    arguments = params.get("arguments", {})
    
    if name not in TOOLS:
        return {
            "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
            "isError": True
        }
    
    try:
        handler = TOOLS[name]["handler"]
        result = await handler(arguments)
        
        if not result.get("ok"):
            return {
                "content": [{"type": "text", "text": f"Error: {result.get('error', 'Unknown error')}"}],
                "isError": True
            }
        
        # Format response
        content = []
        if result.get("content_md"):
            content.append({"type": "text", "text": result["content_md"]})
        
        # Add JSON data
        if result.get("data"):
            content.append({
                "type": "text", 
                "text": f"```json\n{json.dumps(result['data'], indent=2)}\n```"
            })
        
        return {"content": content}
        
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Tool execution error: {str(e)}"}],
            "isError": True
        }

# HTTP handlers for MCP over HTTP
async def mcp_handler(request: Request) -> Response:
    """Handle MCP requests over HTTP"""
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        
        if method == "initialize":
            result = await handle_initialize(params)
        elif method == "tools/list":
            result = await handle_list_tools(params)
        elif method == "tools/call":
            result = await handle_call_tool(params)
        else:
            result = {"error": f"Unknown method: {method}"}
        
        response_body = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        
        return Response(
            content=json.dumps(response_body),
            media_type="application/json"
        )
        
    except Exception as e:
        error_response = {
            "jsonrpc": "2.0",
            "id": body.get("id") if 'body' in locals() else None,
            "error": {"code": -32603, "message": str(e)}
        }
        return Response(
            content=json.dumps(error_response),
            media_type="application/json",
            status_code=500
        )

# Health check endpoint
async def health_check(request: Request) -> Response:
    """Health check endpoint"""
    return Response(
        content=json.dumps({"status": "healthy", "service": "cfb-mcp-server"}),
        media_type="application/json"
    )

# Create Starlette app
app = Starlette(
    routes=[
        Route("/mcp", mcp_handler, methods=["POST"]),
        Route("/health", health_check, methods=["GET"]),
        Route("/", health_check, methods=["GET"])
    ]
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)