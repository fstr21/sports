#!/usr/bin/env python3
"""
Soccer MCP Server for Sports AI

A comprehensive MCP implementation for soccer/football data using SoccerDataAPI.
Provides 15+ tools covering leagues, matches, teams, players, transfers, and betting data.
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
SOCCER_API_BASE = "https://api.soccerdataapi.com"
USER_AGENT = "sports-ai-soccer-mcp/1.0"
AUTH_KEY = os.environ.get("AUTH_KEY")

if not AUTH_KEY:
    raise EnvironmentError("AUTH_KEY environment variable is required")

# HTTP client
_http_client: Optional[httpx.AsyncClient] = None

async def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            headers={
                "User-Agent": USER_AGENT,
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip"
            },
            timeout=30.0
        )
    return _http_client

async def close_http_client():
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None

# MCP Tool Implementations

async def get_countries():
    """Get all available countries (221 countries)"""
    client = await get_http_client()
    response = await client.get(
        f"{SOCCER_API_BASE}/country/",
        params={"auth_token": AUTH_KEY}
    )
    response.raise_for_status()
    return response.json()

async def get_leagues(country_id: Optional[int] = None):
    """Get leagues, optionally filtered by country (129+ leagues available)
    
    Args:
        country_id: Optional country filter (e.g., 8 for England)
    """
    client = await get_http_client()
    params = {"auth_token": AUTH_KEY}
    if country_id:
        params["country_id"] = country_id
    
    response = await client.get(f"{SOCCER_API_BASE}/league/", params=params)
    response.raise_for_status()
    return response.json()

async def get_seasons(league_id: int):
    """Get seasons for a league
    
    Args:
        league_id: League ID (e.g., 228 for Premier League)
    """
    client = await get_http_client()
    response = await client.get(
        f"{SOCCER_API_BASE}/season/",
        params={"league_id": league_id, "auth_token": AUTH_KEY}
    )
    response.raise_for_status()
    return response.json()

async def get_season_stages(league_id: int, season: Optional[str] = None):
    """Get stages for a league season (e.g., Group Stage, Qualifying Rounds)
    
    Args:
        league_id: League ID (e.g., 310 for Champions League)
        season: Optional season (e.g., "2022-2023")
    """
    client = await get_http_client()
    params = {"league_id": league_id, "auth_token": AUTH_KEY}
    if season:
        params["season"] = season
    
    response = await client.get(f"{SOCCER_API_BASE}/stage/", params=params)
    response.raise_for_status()
    return response.json()

async def get_groups(stage_id: int):
    """Get groups for a stage (for tournaments with group stages)
    
    Args:
        stage_id: Stage ID (e.g., 8646 for Champions League Group Stage)
    """
    client = await get_http_client()
    response = await client.get(
        f"{SOCCER_API_BASE}/group/",
        params={"stage_id": stage_id, "auth_token": AUTH_KEY}
    )
    response.raise_for_status()
    return response.json()

async def get_league_standings(league_id: int, season: Optional[str] = None):
    """Get league standings/table
    
    Args:
        league_id: League ID (e.g., 228 for Premier League)
        season: Optional season filter
    """
    client = await get_http_client()
    params = {"league_id": league_id, "auth_token": AUTH_KEY}
    if season:
        params["season"] = season
    
    response = await client.get(f"{SOCCER_API_BASE}/standing/", params=params)
    response.raise_for_status()
    return response.json()

async def get_live_scores():
    """Get live scores for current day (UTC) with comprehensive match data
    
    Returns detailed match info including:
    - Live scores and status
    - Match events (goals, cards, substitutions)
    - Team lineups and formations
    - Betting odds (match winner, over/under, handicap)
    - Weather conditions
    - Injury reports
    """
    client = await get_http_client()
    response = await client.get(
        f"{SOCCER_API_BASE}/livescores/",
        params={"auth_token": AUTH_KEY}
    )
    response.raise_for_status()
    return response.json()

async def get_matches(league_id: Optional[int] = None, date: Optional[str] = None, season: Optional[str] = None):
    """Get matches with comprehensive event data
    
    Args:
        league_id: Optional league filter (e.g., 228 for Premier League)
        date: Optional date filter (format: DD/MM/YYYY)
        season: Optional season filter
    """
    client = await get_http_client()
    params = {"auth_token": AUTH_KEY}
    if league_id:
        params["league_id"] = league_id
    if date:
        params["date"] = date
    if season:
        params["season"] = season
    
    response = await client.get(f"{SOCCER_API_BASE}/matches/", params=params)
    response.raise_for_status()
    return response.json()

async def get_match_details(match_id: int):
    """Get detailed information for a specific match
    
    Args:
        match_id: Match ID
        
    Returns comprehensive match data including:
    - Teams, stadium, officials
    - Full match events timeline
    - Starting lineups and bench players
    - Formation details
    - Betting odds
    - Weather conditions
    """
    client = await get_http_client()
    response = await client.get(
        f"{SOCCER_API_BASE}/match/",
        params={"match_id": match_id, "auth_token": AUTH_KEY}
    )
    response.raise_for_status()
    return response.json()

async def get_match_preview(match_id: int):
    """Get AI-powered match preview with predictions
    
    Args:
        match_id: Match ID
        
    Returns:
    - Weather forecast
    - Excitement rating
    - Match predictions
    - Detailed written preview
    """
    client = await get_http_client()
    response = await client.get(
        f"{SOCCER_API_BASE}/match-preview/",
        params={"match_id": match_id, "auth_token": AUTH_KEY}
    )
    response.raise_for_status()
    return response.json()

async def get_upcoming_match_previews():
    """Get upcoming match previews with AI analysis"""
    client = await get_http_client()
    response = await client.get(
        f"{SOCCER_API_BASE}/match-previews-upcoming/",
        params={"auth_token": AUTH_KEY}
    )
    response.raise_for_status()
    return response.json()

async def get_team_info(team_id: int):
    """Get team information
    
    Args:
        team_id: Team ID (e.g., 4138 for Liverpool)
    """
    client = await get_http_client()
    response = await client.get(
        f"{SOCCER_API_BASE}/team/",
        params={"team_id": team_id, "auth_token": AUTH_KEY}
    )
    response.raise_for_status()
    return response.json()

async def get_stadium_info(team_id: Optional[int] = None, stadium_id: Optional[int] = None):
    """Get stadium information
    
    Args:
        team_id: Team ID (e.g., 4138 for Liverpool)
        stadium_id: Stadium ID (alternative to team_id)
    """
    client = await get_http_client()
    params = {"auth_token": AUTH_KEY}
    if team_id:
        params["team_id"] = team_id
    elif stadium_id:
        params["stadium_id"] = stadium_id
    else:
        raise ValueError("Either team_id or stadium_id must be provided")
    
    response = await client.get(f"{SOCCER_API_BASE}/stadium/", params=params)
    response.raise_for_status()
    return response.json()

async def get_player_info(player_id: int):
    """Get player information
    
    Args:
        player_id: Player ID
    """
    client = await get_http_client()
    response = await client.get(
        f"{SOCCER_API_BASE}/player/",
        params={"player_id": player_id, "auth_token": AUTH_KEY}
    )
    response.raise_for_status()
    return response.json()

async def get_transfers(team_id: int):
    """Get transfer information for a team
    
    Args:
        team_id: Team ID (e.g., 4138 for Liverpool)
        
    Returns:
    - Transfer ins with fees and dates
    - Transfer outs with destinations
    - Transfer types (loan, permanent, etc.)
    """
    client = await get_http_client()
    response = await client.get(
        f"{SOCCER_API_BASE}/transfers/",
        params={"team_id": team_id, "auth_token": AUTH_KEY}
    )
    response.raise_for_status()
    return response.json()

async def get_head_to_head(team_1_id: int, team_2_id: int):
    """Get head-to-head statistics between two teams
    
    Args:
        team_1_id: First team ID
        team_2_id: Second team ID
        
    Returns comprehensive H2H stats:
    - Overall record (wins, draws, losses)
    - Goals scored/conceded
    - Home/away performance splits
    """
    client = await get_http_client()
    response = await client.get(
        f"{SOCCER_API_BASE}/head-to-head/",
        params={
            "team_1_id": team_1_id,
            "team_2_id": team_2_id,
            "auth_token": AUTH_KEY
        }
    )
    response.raise_for_status()
    return response.json()

# Enhanced player extraction from match events
async def extract_league_players(league_id: int):
    """Extract all players from a league with comprehensive statistics
    
    Args:
        league_id: League ID (e.g., 228 for Premier League)
        
    Returns:
    - Player database with stats from match events
    - Goals, assists, cards, substitutions
    - Team associations
    """
    try:
        matches_data = await get_matches(league_id=league_id)
        players_db = {}
        
        if isinstance(matches_data, list):
            for league_entry in matches_data:
                if isinstance(league_entry, dict):
                    matches = league_entry.get("matches", [])
                    
                    for match in matches:
                        if isinstance(match, dict):
                            events = match.get("events", [])
                            teams = match.get("teams", {})
                            home_team = teams.get("home", {})
                            away_team = teams.get("away", {})
                            
                            # Process lineups for team associations
                            lineups = match.get("lineups", {})
                            if lineups:
                                home_lineup = lineups.get("lineups", {}).get("home", [])
                                away_lineup = lineups.get("lineups", {}).get("away", [])
                                
                                for player_data in home_lineup + away_lineup:
                                    if isinstance(player_data, dict):
                                        player = player_data.get("player", {})
                                        if player:
                                            player_id = player.get("id")
                                            player_name = player.get("name")
                                            if player_id and player_name:
                                                if player_id not in players_db:
                                                    players_db[player_id] = {
                                                        "id": player_id,
                                                        "name": player_name,
                                                        "teams": set(),
                                                        "position": player_data.get("position"),
                                                        "stats": {
                                                            "goals": 0, "assists": 0, "yellow_cards": 0,
                                                            "red_cards": 0, "substitutions_in": 0, "substitutions_out": 0
                                                        }
                                                    }
                                                # Add team association
                                                team_name = home_team.get("name") if player_data in home_lineup else away_team.get("name")
                                                if team_name:
                                                    players_db[player_id]["teams"].add(team_name)
                            
                            # Process match events for statistics
                            for event in events:
                                if isinstance(event, dict):
                                    event_type = event.get("event_type")
                                    
                                    # Handle goals
                                    if event_type == "goal" and "player" in event:
                                        player = event["player"]
                                        if isinstance(player, dict):
                                            player_id = player.get("id")
                                            if player_id and player_id in players_db:
                                                players_db[player_id]["stats"]["goals"] += 1
                                    
                                    # Handle cards
                                    elif event_type in ["yellow_card", "red_card"] and "player" in event:
                                        player = event["player"]
                                        if isinstance(player, dict):
                                            player_id = player.get("id")
                                            if player_id and player_id in players_db:
                                                if event_type == "yellow_card":
                                                    players_db[player_id]["stats"]["yellow_cards"] += 1
                                                else:
                                                    players_db[player_id]["stats"]["red_cards"] += 1
                                    
                                    # Handle assists
                                    if "assist_player" in event and event["assist_player"]:
                                        assist_player = event["assist_player"]
                                        if isinstance(assist_player, dict):
                                            player_id = assist_player.get("id")
                                            if player_id and player_id in players_db:
                                                players_db[player_id]["stats"]["assists"] += 1
        
        # Convert sets to lists for JSON serialization
        for player_id, player_data in players_db.items():
            player_data["teams"] = list(player_data["teams"])
        
        return {
            "total_players_found": len(players_db),
            "league_id": league_id,
            "players": players_db
        }
        
    except Exception as e:
        return {"error": str(e), "league_id": league_id}

# MCP Server Implementation

async def handle_request(request: Request) -> Response:
    try:
        body = await request.body()
        if not body:
            return Response(
                json.dumps({"error": "Empty request body"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        data = json.loads(body)
        
        if data.get("method") == "tools/list":
            tools = [
                {
                    "name": "get_countries",
                    "description": "Get all available countries (221 countries)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "get_leagues", 
                    "description": "Get leagues, optionally filtered by country (129+ leagues)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "country_id": {"type": "integer", "description": "Optional country filter (e.g., 8 for England)"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "get_seasons",
                    "description": "Get seasons for a league",
                    "inputSchema": {
                        "type": "object", 
                        "properties": {
                            "league_id": {"type": "integer", "description": "League ID (e.g., 228 for Premier League)"}
                        },
                        "required": ["league_id"]
                    }
                },
                {
                    "name": "get_season_stages",
                    "description": "Get stages for a league season (e.g., Group Stage, Qualifying)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "league_id": {"type": "integer", "description": "League ID (e.g., 310 for Champions League)"},
                            "season": {"type": "string", "description": "Optional season (e.g., '2022-2023')"}
                        },
                        "required": ["league_id"]
                    }
                },
                {
                    "name": "get_groups",
                    "description": "Get groups for a tournament stage",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "stage_id": {"type": "integer", "description": "Stage ID (e.g., 8646 for Champions League Group Stage)"}
                        },
                        "required": ["stage_id"]
                    }
                },
                {
                    "name": "get_league_standings",
                    "description": "Get league standings/table with team statistics",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "league_id": {"type": "integer", "description": "League ID (e.g., 228 for Premier League)"},
                            "season": {"type": "string", "description": "Optional season filter"}
                        },
                        "required": ["league_id"]
                    }
                },
                {
                    "name": "get_live_scores",
                    "description": "Get live scores with match events, lineups, odds, and weather",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "get_matches",
                    "description": "Get matches with comprehensive event data",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "league_id": {"type": "integer", "description": "Optional league filter"},
                            "date": {"type": "string", "description": "Optional date filter (DD/MM/YYYY)"},
                            "season": {"type": "string", "description": "Optional season filter"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "get_match_details",
                    "description": "Get detailed match information with events and lineups",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "match_id": {"type": "integer", "description": "Match ID"}
                        },
                        "required": ["match_id"]
                    }
                },
                {
                    "name": "get_match_preview",
                    "description": "Get AI-powered match preview with predictions and weather",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "match_id": {"type": "integer", "description": "Match ID"}
                        },
                        "required": ["match_id"]
                    }
                },
                {
                    "name": "get_upcoming_match_previews",
                    "description": "Get upcoming match previews with AI analysis",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "get_team_info",
                    "description": "Get team information including stadium and country",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "team_id": {"type": "integer", "description": "Team ID (e.g., 4138 for Liverpool)"}
                        },
                        "required": ["team_id"]
                    }
                },
                {
                    "name": "get_stadium_info",
                    "description": "Get stadium information by team or stadium ID",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "team_id": {"type": "integer", "description": "Team ID"},
                            "stadium_id": {"type": "integer", "description": "Stadium ID (alternative to team_id)"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "get_player_info",
                    "description": "Get player information",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "player_id": {"type": "integer", "description": "Player ID"}
                        },
                        "required": ["player_id"]
                    }
                },
                {
                    "name": "get_transfers",
                    "description": "Get team transfer history with fees and dates",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "team_id": {"type": "integer", "description": "Team ID (e.g., 4138 for Liverpool)"}
                        },
                        "required": ["team_id"]
                    }
                },
                {
                    "name": "get_head_to_head",
                    "description": "Get head-to-head statistics between two teams",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "team_1_id": {"type": "integer", "description": "First team ID"},
                            "team_2_id": {"type": "integer", "description": "Second team ID"}
                        },
                        "required": ["team_1_id", "team_2_id"]
                    }
                },
                {
                    "name": "extract_league_players",
                    "description": "Extract all players from a league with comprehensive statistics from match events",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "league_id": {"type": "integer", "description": "League ID (e.g., 228 for Premier League)"}
                        },
                        "required": ["league_id"]
                    }
                }
            ]
            
            return Response(
                json.dumps({"tools": tools}),
                headers={"Content-Type": "application/json"}
            )
        
        elif data.get("method") == "tools/call":
            tool_name = data.get("params", {}).get("name")
            arguments = data.get("params", {}).get("arguments", {})
            
            # Route to appropriate function
            if tool_name == "get_countries":
                result = await get_countries()
            elif tool_name == "get_leagues":
                result = await get_leagues(arguments.get("country_id"))
            elif tool_name == "get_seasons":
                result = await get_seasons(arguments["league_id"])
            elif tool_name == "get_season_stages":
                result = await get_season_stages(arguments["league_id"], arguments.get("season"))
            elif tool_name == "get_groups":
                result = await get_groups(arguments["stage_id"])
            elif tool_name == "get_league_standings":
                result = await get_league_standings(arguments["league_id"], arguments.get("season"))
            elif tool_name == "get_live_scores":
                result = await get_live_scores()
            elif tool_name == "get_matches":
                result = await get_matches(arguments.get("league_id"), arguments.get("date"), arguments.get("season"))
            elif tool_name == "get_match_details":
                result = await get_match_details(arguments["match_id"])
            elif tool_name == "get_match_preview":
                result = await get_match_preview(arguments["match_id"])
            elif tool_name == "get_upcoming_match_previews":
                result = await get_upcoming_match_previews()
            elif tool_name == "get_team_info":
                result = await get_team_info(arguments["team_id"])
            elif tool_name == "get_stadium_info":
                result = await get_stadium_info(arguments.get("team_id"), arguments.get("stadium_id"))
            elif tool_name == "get_player_info":
                result = await get_player_info(arguments["player_id"])
            elif tool_name == "get_transfers":
                result = await get_transfers(arguments["team_id"])
            elif tool_name == "get_head_to_head":
                result = await get_head_to_head(arguments["team_1_id"], arguments["team_2_id"])
            elif tool_name == "extract_league_players":
                result = await extract_league_players(arguments["league_id"])
            else:
                return Response(
                    json.dumps({"error": f"Unknown tool: {tool_name}"}),
                    status_code=400,
                    headers={"Content-Type": "application/json"}
                )
            
            return Response(
                json.dumps({"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}),
                headers={"Content-Type": "application/json"}
            )
        
        else:
            return Response(
                json.dumps({"error": "Unknown method"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
    
    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

async def health_check(request: Request) -> Response:
    """Health check endpoint for Railway"""
    return Response(
        json.dumps({"status": "healthy", "service": "soccer-mcp"}),
        headers={"Content-Type": "application/json"}
    )

# Application setup
app = Starlette(
    routes=[
        Route("/", health_check, methods=["GET"]),
        Route("/mcp", handle_request, methods=["POST"]),
    ]
)

@app.on_event("startup")
async def startup():
    print(f"Soccer MCP Server starting up...")
    print(f"Available tools: 17 comprehensive soccer tools")
    print(f"API Base: {SOCCER_API_BASE}")

@app.on_event("shutdown")
async def shutdown():
    await close_http_client()
    print("Soccer MCP Server shutting down...")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)