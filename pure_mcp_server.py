#!/usr/bin/env python3
"""
Pure MCP Server for Sports AI

A clean MCP implementation without FastMCP that combines ESPN and Odds functionality.
Uses standard MCP protocol for maximum compatibility.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.routing import Route

# Configuration
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "").strip()
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
ESPN_BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"
USER_AGENT = "sports-ai-mcp/3.0"

# Timezone configuration
ET = ZoneInfo("America/New_York")

# ESPN league mappings (same as before)
ALLOWED_ROUTES = {
    ("baseball", "mlb"): {"scoreboard": "/baseball/mlb/scoreboard", "teams": "/baseball/mlb/teams"},
    ("basketball", "nba"): {"scoreboard": "/basketball/nba/scoreboard", "teams": "/basketball/nba/teams"},
    ("basketball", "wnba"): {"scoreboard": "/basketball/wnba/scoreboard", "teams": "/basketball/wnba/teams"},
    ("football", "nfl"): {"scoreboard": "/football/nfl/scoreboard", "teams": "/football/nfl/teams"},
    ("hockey", "nhl"): {"scoreboard": "/hockey/nhl/scoreboard", "teams": "/hockey/nhl/teams"},
    ("soccer", "usa.1"): {"scoreboard": "/soccer/usa.1/scoreboard", "teams": "/soccer/usa.1/teams"},
    ("soccer", "eng.1"): {"scoreboard": "/soccer/eng.1/scoreboard", "teams": "/soccer/eng.1/teams"}
}

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

# ESPN API functions
async def espn_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make ESPN API request"""
    url = f"{ESPN_BASE_URL}{path}"
    client = await get_http_client()
    try:
        r = await client.get(url, params=params or {})
        if r.status_code >= 400:
            return {"ok": False, "error": f"ESPN API error {r.status_code}: {r.text[:200]}"}
        return {"ok": True, "data": r.json()}
    except Exception as e:
        return {"ok": False, "error": f"ESPN request failed: {str(e)}"}

def resolve_route(sport: str, league: str, endpoint: str) -> str:
    """Resolve ESPN route"""
    try:
        return ALLOWED_ROUTES[(sport.lower(), league.lower())][endpoint.lower()]
    except KeyError:
        raise ValueError(f"Unsupported route: {sport}/{league}/{endpoint}")

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

# MCP Tool implementations
async def handle_get_scoreboard(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get ESPN scoreboard"""
    sport = args.get("sport", "")
    league = args.get("league", "")
    dates = args.get("dates")
    
    try:
        path = resolve_route(sport, league, "scoreboard")
    except ValueError as e:
        return {"ok": False, "error": str(e)}
    
    params = {}
    if dates:
        params["dates"] = dates
    
    resp = await espn_get(path, params)
    if not resp.get("ok"):
        return resp
    
    events = resp["data"].get("events", [])
    return {
        "ok": True,
        "content_md": f"## {sport}/{league} Scoreboard\n\nFound {len(events)} events",
        "data": {"events": events, "total": len(events)},
        "meta": {"source": "espn", "sport": sport, "league": league, "timestamp": now_iso()}
    }

async def handle_get_teams(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get ESPN teams"""
    sport = args.get("sport", "")
    league = args.get("league", "")
    
    try:
        path = resolve_route(sport, league, "teams")
    except ValueError as e:
        return {"ok": False, "error": str(e)}
    
    resp = await espn_get(path)
    if not resp.get("ok"):
        return resp
    
    teams = resp["data"].get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
    team_list = []
    for t in teams:
        info = t.get("team", {})
        team_list.append({
            "id": info.get("id"),
            "displayName": info.get("displayName"),
            "abbreviation": info.get("abbreviation")
        })
    
    return {
        "ok": True,
        "content_md": f"## {sport}/{league} Teams\n\nFound {len(team_list)} teams",
        "data": {"teams": team_list, "total": len(team_list)},
        "meta": {"source": "espn", "sport": sport, "league": league, "timestamp": now_iso()}
    }

async def handle_get_team_roster(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get ESPN team roster"""
    sport = args.get("sport", "")
    league = args.get("league", "")
    team_id = args.get("team_id", "")
    
    if not team_id:
        return {"ok": False, "error": "team_id is required"}
    
    try:
        # Build roster path directly using the same pattern as teams
        path = resolve_route(sport, league, "teams")
        # Remove the /teams suffix and add specific team roster path
        base_path = path.replace("/teams", "")
        roster_path = f"{base_path}/teams/{team_id}/roster"
    except ValueError as e:
        return {"ok": False, "error": str(e)}
    
    resp = await espn_get(roster_path)
    if not resp.get("ok"):
        return resp
    
    roster_data = resp["data"]
    athletes = roster_data.get("athletes", [])
    
    return {
        "ok": True,
        "content_md": f"## {sport}/{league} Team {team_id} Roster\n\nFound {len(athletes)} players",
        "data": {"athletes": athletes, "total": len(athletes)},
        "meta": {"source": "espn", "sport": sport, "league": league, "team_id": team_id, "timestamp": now_iso()}
    }

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

async def handle_get_player_stats(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get ESPN player statistics using core API eventlog approach"""
    sport = args.get("sport", "")
    league = args.get("league", "")
    player_id = args.get("player_id", "")
    limit = args.get("limit", 10)  # Default last 10 games
    
    if not player_id:
        return {"ok": False, "error": "player_id is required"}
    
    # Use ESPN Core API (like in your working example)
    base_url = f"https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/athletes/{player_id}"
    eventlog_url = f"{base_url}/eventlog"
    
    client = await get_http_client()
    
    try:
        # Step 1: Get eventlog to find total pages
        r = await client.get(eventlog_url)
        if r.status_code >= 400:
            return {"ok": False, "error": f"ESPN Core API error {r.status_code}: {r.text[:200]}"}
        
        eventlog_data = r.json()
        events = eventlog_data.get("events", {})
        total_pages = events.get("pageCount", 1)
        
        # Step 2: Get MULTIPLE recent pages (ESPN eventlog: page 1 = oldest, page N = newest)
        all_recent_events = []
        
        # Start from LAST page (most recent) and work backwards
        pages_to_check = min(3, total_pages)  # Check last 3 pages to ensure we get recent games
        
        for page_num in range(total_pages, max(0, total_pages - pages_to_check), -1):
            page_url = f"{eventlog_url}?page={page_num}"
            page_r = await client.get(page_url)
            
            if page_r.status_code == 200:
                page_data = page_r.json()
                page_events = page_data.get("events", {}).get("items", [])
                all_recent_events.extend(page_events)
        
        last_page_events = all_recent_events
        
        # Step 3: Process ALL games and sort by date to get most recent
        all_games_with_dates = []
        
        for event_item in last_page_events:
            event_ref = event_item.get("event", {}).get("$ref")
            stats_ref = event_item.get("statistics", {}).get("$ref")
            
            if not event_ref:
                continue
            
            try:
                # Get event details for date and opponent
                event_r = await client.get(event_ref)
                if event_r.status_code != 200:
                    continue
                
                event_data = event_r.json()
                game_date = event_data.get("date", "")
                
                if game_date:
                    try:
                        # Parse UTC datetime and convert to Eastern Time
                        utc_dt = datetime.fromisoformat(game_date.replace('Z', '+00:00')).astimezone(timezone.utc)
                        game_time_et = utc_dt.astimezone(ET)
                        now_et = datetime.now(ET)
                        
                        # Get event ID for verification
                        event_id = event_data.get("id", "unknown")
                        
                        # Simple future game filter: Skip only if game hasn't started yet
                        if game_time_et > now_et:
                            print(f"FILTERED future game: Event {event_id} at {game_time_et} (current: {now_et})")
                            continue
                        
                        # Store ET-normalized values for everything downstream
                        display_date_et = game_time_et.date()
                        display_iso_et = game_time_et.isoformat()
                        
                        # Get stats if available
                        game_stats = {"event_id": event_id}  # Add event ID for verification
                        if stats_ref:
                            stats_r = await client.get(stats_ref)
                            if stats_r.status_code == 200:
                                stats_data = stats_r.json()
                                
                                # Extract batting/player stats using your working pattern
                                if "splits" in stats_data and "categories" in stats_data["splits"]:
                                    categories = stats_data["splits"]["categories"]
                                    
                                    # Debug: capture ALL categories and stats to see what's available
                                    if "debug_all_stats" not in game_stats:
                                        game_stats["debug_all_stats"] = []
                                        game_stats["debug_categories"] = []
                                    
                                    for category in categories:
                                        category_name = category.get("name", "").lower()
                                        game_stats["debug_categories"].append(category_name)
                                        category_stats = category.get("stats", [])
                                        
                                        # Capture ALL stats from ALL categories for debugging
                                        for stat in category_stats:
                                            name = stat.get("name", "").lower()
                                            value = stat.get("value", 0)
                                            game_stats["debug_all_stats"].append(f"{category_name}:{name}:{value}")
                                            
                                            # Extract stats only from correct category to avoid conflicts
                                            if category_name == "batting" and name == "hits":
                                                game_stats["hits"] = value
                                            elif category_name == "batting" and name == "homeruns":  # ESPN uses "homeruns", not "home runs" 
                                                game_stats["homeruns"] = value
                                            elif category_name == "batting" and name.lower() == "rbis":  # ESPN uses "RBIs"
                                                game_stats["rbis"] = value
                                            elif category_name == "batting" and name == "runs":
                                                game_stats["runs"] = value
                                            elif category_name == "batting" and name == "strikeouts":
                                                game_stats["strikeouts"] = value
                                            elif category_name == "batting" and name == "walks":
                                                game_stats["walks"] = value
                                            elif category_name in ["scoring", "offense"] and name == "points":
                                                game_stats["points"] = value
                                            elif category_name in ["rebounding", "defense"] and name == "rebounds":
                                                game_stats["rebounds"] = value
                                            elif category_name in ["passing", "offense"] and name == "assists":
                                                game_stats["assists"] = value
                        
                        all_games_with_dates.append({
                            "datetime_obj_et": game_time_et,  # Use ET for sorting
                            "date": display_iso_et,  # ET date for display
                            "opponent": "Recent Game",  # Simplified as requested
                            "stats": game_stats
                        })
                        
                    except Exception:
                        continue
                
            except Exception as e:
                continue
        
        # Sort by date (most recent first) using ET time
        all_games_with_dates.sort(key=lambda x: x["datetime_obj_et"], reverse=True)
        
        # Simple deduplication by ET date and take most recent games
        games_with_stats = []
        seen_dates_et = set()
        
        for game in all_games_with_dates:
            date_key = game["datetime_obj_et"].strftime("%Y-%m-%d")  # ET calendar day
            
            # Take first (most recent) game for each ET date
            if date_key not in seen_dates_et and len(games_with_stats) < limit:
                seen_dates_et.add(date_key)
                games_with_stats.append({
                    "date": date_key,  # Use clean YYYY-MM-DD format in ET
                    "opponent": game["opponent"],
                    "stats": game["stats"]
                })
        
        return {
            "ok": True,
            "content_md": f"## Player Stats for {player_id}\n\nFound {len(games_with_stats)} recent games",
            "data": {
                "player_id": player_id,
                "timezone": "America/New_York",  # Make timezone explicit
                "games": games_with_stats,
                "total_games": len(games_with_stats)
            },
            "meta": {"source": "espn_core", "sport": sport, "league": league, "player_id": player_id, "timestamp": now_iso()}
        }
        
    except Exception as e:
        return {"ok": False, "error": f"ESPN Core API request failed: {str(e)}"}

# MCP Tool registry
TOOLS = {
    "getScoreboard": {
        "description": "Get ESPN scoreboard for a league",
        "parameters": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "Sport (e.g. 'baseball')"},
                "league": {"type": "string", "description": "League (e.g. 'mlb')"},
                "dates": {"type": "string", "description": "Date filter (YYYYMMDD)", "optional": True}
            },
            "required": ["sport", "league"]
        },
        "handler": handle_get_scoreboard
    },
    "getTeams": {
        "description": "Get ESPN teams for a league",
        "parameters": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "Sport (e.g. 'baseball')"},
                "league": {"type": "string", "description": "League (e.g. 'mlb')"}
            },
            "required": ["sport", "league"]
        },
        "handler": handle_get_teams
    },
    "getTeamRoster": {
        "description": "Get ESPN team roster",
        "parameters": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "Sport (e.g. 'baseball')"},
                "league": {"type": "string", "description": "League (e.g. 'mlb')"},
                "team_id": {"type": "string", "description": "Team ID"}
            },
            "required": ["sport", "league", "team_id"]
        },
        "handler": handle_get_team_roster
    },
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
    },
    "getPlayerStats": {
        "description": "Get ESPN player statistics and game log",
        "parameters": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "Sport (e.g. 'baseball')"},
                "league": {"type": "string", "description": "League (e.g. 'mlb')"},
                "player_id": {"type": "string", "description": "ESPN Player ID"},
                "stat_type": {"type": "string", "description": "Type of stats (gamelog, season, career)", "optional": True},
                "limit": {"type": "number", "description": "Number of recent games (default: 10)", "optional": True}
            },
            "required": ["sport", "league", "player_id"]
        },
        "handler": handle_get_player_stats
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
            "name": "sports-ai-mcp-pure",
            "version": "3.0.0"
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
    print("🚀 Pure MCP Sports Server Starting - TIMEZONE FIX v2 🚀")
    print(f"📊 ESPN Tools: {len([t for t in TOOLS if t.startswith('get') and t not in ['getSports', 'getOdds', 'getQuotaInfo']])}")
    print(f"💰 Odds Tools: {len([t for t in TOOLS if t in ['getSports', 'getOdds', 'getQuotaInfo']])}")
    print(f"🔧 Total Tools: {len(TOOLS)}")
    print("🌐 Server URL: http://0.0.0.0:8080/mcp")
    print("🕐 Current time for debugging: Aug 12, 2025 7:54 PM ET")
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