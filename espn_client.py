#!/usr/bin/env python3
"""
Standalone ESPN API client for sports analysis
Extracted from MCP server for direct use
"""

import requests
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List

ESPN_BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

# Supported leagues
ALLOWED_ROUTES = {
    ("baseball", "mlb"): {
        "scoreboard": "/baseball/mlb/scoreboard",
        "summary": "/baseball/mlb/summary",
    },
    ("basketball", "nba"): {
        "scoreboard": "/basketball/nba/scoreboard",
        "summary": "/basketball/nba/summary",
    },
    ("basketball", "wnba"): {
        "scoreboard": "/basketball/wnba/scoreboard",
        "summary": "/basketball/wnba/summary",
    },
    ("football", "nfl"): {
        "scoreboard": "/football/nfl/scoreboard",
        "summary": "/football/nfl/summary",
    },
    ("hockey", "nhl"): {
        "scoreboard": "/hockey/nhl/scoreboard",
        "summary": "/hockey/nhl/summary",
    },
    ("soccer", "usa.1"): {
        "scoreboard": "/soccer/usa.1/scoreboard",
        "summary": "/soccer/usa.1/summary",
    },
}

def espn_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make a request to ESPN API."""
    url = f"{ESPN_BASE_URL}{path}"
    try:
        response = requests.get(url, params=params or {}, timeout=10)
        if response.status_code >= 400:
            return {
                "ok": False,
                "error_type": "upstream_error",
                "source": "ESPN",
                "status": response.status_code,
                "url": str(response.url),
                "body_excerpt": response.text[:500],
            }
        return {"ok": True, "data": response.json(), "url": str(response.url)}
    except requests.RequestException as e:
        return {"ok": False, "error_type": "request_error", "source": "ESPN", "url": url, "message": str(e)}

def summarize_events(scoreboard: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize scoreboard events."""
    events = scoreboard.get("events") or []
    out = []
    newest = None
    
    for ev in events:
        date = ev.get("date")
        if date and (newest is None or date > newest):
            newest = date
        
        comp = (ev.get("competitions") or [{}])[0]
        competitors = comp.get("competitors") or []
        
        def tinfo(c: Dict[str, Any]) -> Dict[str, Any]:
            t = c.get("team") or {}
            return {
                "id": t.get("id"),
                "displayName": t.get("displayName"),
                "abbrev": t.get("abbreviation"),
                "score": c.get("score"),
                "homeAway": c.get("homeAway"),
            }
        
        if len(competitors) >= 2:
            home = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
            away = next((c for c in competitors if c.get("homeAway") == "away"), competitors[-1])
        else:
            home, away = (competitors + [{}, {}])[:2]
        
        out.append({
            "event_id": ev.get("id"),
            "date": date,
            "status": (comp.get("status") or {}).get("type", {}).get("state"),
            "home": tinfo(home),
            "away": tinfo(away),
        })
    
    return {"events": out, "newest_event_time": newest}

def extract_summary_core(summary_json: Dict[str, Any]) -> Dict[str, Any]:
    """Extract core summary data."""
    competitions = summary_json.get("competitions") or []
    game = competitions[0] if competitions else {}
    status = (game.get("status") or {}).get("type", {}).get("state")
    boxscore = summary_json.get("boxscore")
    leaders = summary_json.get("leaders")
    
    teams_meta = []
    for c in (game.get("competitors") or []):
        t = c.get("team") or {}
        teams_meta.append({
            "team_id": t.get("id"),
            "displayName": t.get("displayName"),
            "abbrev": t.get("abbreviation"),
            "score": c.get("score"),
            "homeAway": c.get("homeAway"),
        })
    
    return {
        "status": status,
        "teams_meta": teams_meta,
        "leaders": leaders,
        "boxscore": boxscore,
    }

def get_scoreboard(sport: str, league: str, dates: Optional[str] = None, 
                  limit: Optional[int] = None, week: Optional[int] = None, 
                  seasontype: Optional[int] = None) -> Dict[str, Any]:
    """Get scoreboard for a league."""
    try:
        route_key = (sport.lower(), league.lower())
        if route_key not in ALLOWED_ROUTES:
            return {"ok": False, "message": f"Unsupported route: {sport}/{league}"}
        
        path = ALLOWED_ROUTES[route_key]["scoreboard"]
        params = {}
        
        if dates:
            params["dates"] = dates
        if limit is not None:
            params["limit"] = limit
        if week is not None:
            params["week"] = week
        if seasontype is not None:
            params["seasontype"] = seasontype
        
        resp = espn_get(path, params)
        if not resp.get("ok"):
            return resp
        
        summary = summarize_events(resp["data"])
        return {
            "ok": True,
            "data": {"scoreboard": summary},
            "meta": {"league": league, "sport": sport, "url": resp.get("url")}
        }
        
    except Exception as e:
        return {"ok": False, "message": str(e)}

def get_game_summary(sport: str, league: str, event_id: str) -> Dict[str, Any]:
    """Get game summary/boxscore for a single event."""
    try:
        route_key = (sport.lower(), league.lower())
        if route_key not in ALLOWED_ROUTES:
            return {"ok": False, "message": f"Unsupported route: {sport}/{league}"}
        
        if not event_id:
            return {"ok": False, "message": "event_id is required"}
        
        path = ALLOWED_ROUTES[route_key]["summary"]
        resp = espn_get(path, {"event": event_id})
        
        if not resp.get("ok"):
            return resp
        
        core = extract_summary_core(resp["data"])
        return {
            "ok": True,
            "data": {"summary": core},
            "meta": {"league": league, "sport": sport, "event_id": event_id, "url": resp.get("url")}
        }
        
    except Exception as e:
        return {"ok": False, "message": str(e)}