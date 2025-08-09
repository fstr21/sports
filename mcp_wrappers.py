#!/usr/bin/env python3
"""
MCP Function Wrappers

This module provides simple function wrappers around your MCP tools
that can be called directly from the HTTP server.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add sports_mcp to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "sports_mcp"))

# Import the MCP modules but not the server parts - just the core functions
try:
    from sports_ai_mcp import (
        ESPN_BASE_URL, ALLOWED_ROUTES, espn_get, 
        summarize_events, extract_summary_core,
        ask_openrouter, ok_envelope, err, now_iso
    )
    SPORTS_AI_CORE_AVAILABLE = True
    print("[OK] Sports AI core functions imported")
except ImportError as e:
    print(f"[ERROR] Could not import Sports AI core: {e}")
    SPORTS_AI_CORE_AVAILABLE = False

async def get_scoreboard_wrapper(sport: str, league: str, dates: Optional[str] = None, 
                               limit: Optional[int] = None, week: Optional[int] = None, 
                               seasontype: Optional[int] = None) -> Dict[str, Any]:
    """Wrapper for getScoreboard functionality"""
    if not SPORTS_AI_CORE_AVAILABLE:
        return err("Sports AI core not available", error_type="service_unavailable")
    
    try:
        # Resolve route (same logic as original MCP)
        sport = sport.lower()
        league = league.lower()
        
        if (sport, league) not in ALLOWED_ROUTES:
            return err(f"Unsupported route: {sport}/{league}", error_type="validation_error")
        
        path = ALLOWED_ROUTES[(sport, league)]["scoreboard"]
        
        # Build params
        params = {}
        if dates:
            params["dates"] = dates
        if limit is not None:
            if not isinstance(limit, int) or limit <= 0:
                return err("limit must be positive integer", error_type="validation_error")
            params["limit"] = limit
        if week is not None:
            params["week"] = week
        if seasontype is not None:
            params["seasontype"] = seasontype
            
        # Validate NFL/NCAAF specific params
        if (sport, league) not in [("football", "nfl"), ("football", "college-football")]:
            for k in ("week", "seasontype"):
                if k in params:
                    return err("'week'/'seasontype' only for NFL/NCAAF", error_type="validation_error")
        
        # Make ESPN API call
        resp = await espn_get(path, params)
        if not resp.get("ok"):
            return resp
        
        # Summarize events
        summary = summarize_events(resp["data"])
        md = f"## Scoreboard {sport}/{league}\n\nEvents: {len(summary['events'])}"
        
        return ok_envelope(md, {"scoreboard": summary}, 
                          {"league": league, "sport": sport, "url": resp.get("url")})
        
    except Exception as e:
        return err(f"Error in scoreboard wrapper: {str(e)}", error_type="internal_error")

async def get_teams_wrapper(sport: str, league: str) -> Dict[str, Any]:
    """Wrapper for getTeams functionality"""
    if not SPORTS_AI_CORE_AVAILABLE:
        return err("Sports AI core not available", error_type="service_unavailable")
    
    try:
        # Resolve route
        sport = sport.lower()
        league = league.lower()
        
        if (sport, league) not in ALLOWED_ROUTES:
            return err(f"Unsupported route: {sport}/{league}", error_type="validation_error")
        
        path = ALLOWED_ROUTES[(sport, league)]["teams"]
        
        # Make ESPN API call
        resp = await espn_get(path)
        if not resp.get("ok"):
            return resp
        
        # Extract teams data
        teams = resp["data"].get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
        norm = []
        for t in teams:
            info = t.get("team") or {}
            norm.append({
                "id": info.get("id"),
                "displayName": info.get("displayName"),
                "abbrev": info.get("abbreviation"),
                "location": info.get("location"),
            })
        
        md = f"## Teams {sport}/{league}\n\nCount: {len(norm)}"
        return ok_envelope(md, {"teams": norm}, 
                          {"league": league, "sport": sport, "url": resp.get("url")})
        
    except Exception as e:
        return err(f"Error in teams wrapper: {str(e)}", error_type="internal_error")

async def get_game_summary_wrapper(sport: str, league: str, event_id: str) -> Dict[str, Any]:
    """Wrapper for getGameSummary functionality"""
    if not SPORTS_AI_CORE_AVAILABLE:
        return err("Sports AI core not available", error_type="service_unavailable")
    
    try:
        # Resolve route
        sport = sport.lower()
        league = league.lower()
        
        if (sport, league) not in ALLOWED_ROUTES:
            return err(f"Unsupported route: {sport}/{league}", error_type="validation_error")
        
        if not event_id:
            return err("event_id is required", error_type="validation_error")
        
        path = ALLOWED_ROUTES[(sport, league)]["summary"]
        
        # Make ESPN API call
        resp = await espn_get(path, {"event": event_id})
        if not resp.get("ok"):
            return resp
        
        # Extract summary core
        core = extract_summary_core(resp["data"])
        md = f"## Game Summary {sport}/{league} event={event_id}\n\nStatus: {core.get('status') or 'unknown'}"
        
        return ok_envelope(md, {"summary": core}, 
                          {"league": league, "sport": sport, "event_id": event_id, "url": resp.get("url")})
        
    except Exception as e:
        return err(f"Error in game summary wrapper: {str(e)}", error_type="internal_error")

async def analyze_game_wrapper(sport: str, league: str, event_id: str, question: str) -> Dict[str, Any]:
    """Wrapper for analyzeGameStrict functionality"""
    if not SPORTS_AI_CORE_AVAILABLE:
        return err("Sports AI core not available", error_type="service_unavailable")
    
    try:
        # First get the game summary
        gs = await get_game_summary_wrapper(sport, league, event_id)
        if not gs.get("ok"):
            return gs
        
        # Use OpenRouter for analysis
        payload = {"summary": gs["data"]["summary"]}
        ok_result, content = await ask_openrouter(payload, f"Answer strictly from the JSON. Question: {question}")
        
        md = content if ok_result else f"OpenRouter error: {content}"
        return ok_envelope(md, payload, {"league": league, "sport": sport, "event_id": event_id})
        
    except Exception as e:
        return err(f"Error in analyze game wrapper: {str(e)}", error_type="internal_error")

# Simple test function
async def test_wrappers():
    """Test the wrappers"""
    print("Testing MCP wrappers...")
    
    # Test teams
    result = await get_teams_wrapper("basketball", "nba")
    if result.get("ok"):
        team_count = len(result["data"]["teams"])
        print(f"[OK] Found {team_count} NBA teams")
    else:
        print(f"[ERROR] Teams test failed: {result.get('message')}")

if __name__ == "__main__":
    asyncio.run(test_wrappers())