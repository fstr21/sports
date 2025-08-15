#!/usr/bin/env python3
"""
MLB MCP Server for Sports AI

A dedicated MCP implementation focused on MLB statistics and analytics.
Uses MLB Stats API for comprehensive baseball data.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

# Configuration
MLB_STATS_API_BASE = "https://statsapi.mlb.com/api/v1"
USER_AGENT = "sports-ai-mlb-mcp/1.0"

# Eastern Time zone for MLB games
ET = ZoneInfo("America/New_York")

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

def to_et_from_api(iso_or_date: str) -> datetime:
    """Convert API date/datetime to ET timezone"""
    if not iso_or_date:
        raise ValueError("empty datetime")
    s = iso_or_date.strip()
    
    # Handle date-only format (YYYY-MM-DD)
    if len(s) == 10 and s.count("-") == 2:
        dt = datetime.fromisoformat(s)
        return dt.replace(tzinfo=ET)
    
    # Handle ISO datetime
    dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(ET)

# MLB API functions
async def mlb_api_get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make MLB Stats API request"""
    url = f"{MLB_STATS_API_BASE}/{endpoint}"
    query_params = params or {}
    
    client = await get_http_client()
    try:
        r = await client.get(url, params=query_params)
        if r.status_code >= 400:
            return {"ok": False, "error": f"MLB API error {r.status_code}: {r.text[:200]}"}
        return {"ok": True, "data": r.json()}
    except Exception as e:
        return {"ok": False, "error": f"MLB API request failed: {str(e)}"}

# MLB Tool implementations

async def handle_get_mlb_schedule_et(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get MLB games for a specific ET date"""
    now_et = datetime.now(ET)
    date_str = str(args.get("date") or now_et.strftime("%Y-%m-%d"))
    
    params = {"sportId": "1", "date": date_str}
    resp = await mlb_api_get("schedule", params)
    if not resp.get("ok"):
        return resp
    
    payload = resp["data"]
    dates = payload.get("dates") or []
    
    if not dates:
        return {
            "ok": True,
            "content_md": f"## MLB Schedule for {date_str} (ET)\n\nNo games scheduled",
            "data": {"source": "mlb_stats_api", "date_et": date_str, "games": [], "count": 0},
            "meta": {"timestamp": now_iso()}
        }
    
    games_out = []
    for g in (dates[0].get("games") or []):
        iso = g.get("gameDate") or g.get("officialDate")
        dt_et = None
        if iso:
            try:
                dt_et = to_et_from_api(iso)
            except:
                dt_et = None
        
        status = ((g.get("status") or {}).get("detailedState")
                  or (g.get("status") or {}).get("abstractGameState"))
        
        home_team = (g.get("teams") or {}).get("home") or {}
        away_team = (g.get("teams") or {}).get("away") or {}
        
        games_out.append({
            "gamePk": g.get("gamePk"),
            "start_et": dt_et.isoformat() if dt_et else None,
            "status": status,
            "home": {
                "teamId": (home_team.get("team") or {}).get("id"),
                "name": (home_team.get("team") or {}).get("name"),
                "abbrev": (home_team.get("team") or {}).get("abbreviation"),
            },
            "away": {
                "teamId": (away_team.get("team") or {}).get("id"),
                "name": (away_team.get("team") or {}).get("name"),
                "abbrev": (away_team.get("team") or {}).get("abbreviation"),
            },
            "venue": (g.get("venue") or {}).get("name"),
        })
    
    games_out.sort(key=lambda x: x["start_et"] or "9999-12-31T00:00:00-04:00")
    
    return {
        "ok": True,
        "content_md": f"## MLB Schedule for {date_str} (ET)\n\nFound {len(games_out)} games",
        "data": {"source": "mlb_stats_api", "date_et": date_str, "games": games_out, "count": len(games_out)},
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_mlb_teams(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get active MLB teams for a season"""
    now_et = datetime.now(ET)
    season = int(args.get("season") or now_et.year)
    
    params = {"sportId": "1", "season": season, "activeStatus": "Yes"}
    resp = await mlb_api_get("teams", params)
    if not resp.get("ok"):
        return resp
    
    payload = resp["data"]
    teams_raw = payload.get("teams") or []
    
    teams = []
    for t in teams_raw:
        if isinstance(t, dict):
            teams.append({
                "teamId": t.get("id"),
                "name": t.get("name"),
                "teamName": t.get("teamName"),
                "abbrev": t.get("abbreviation"),
                "locationName": t.get("locationName"),
                "league": (t.get("league") or {}).get("name"),
                "division": (t.get("division") or {}).get("name"),
                "venue": (t.get("venue") or {}).get("name"),
            })
    
    teams.sort(key=lambda x: x.get("abbrev") or "")
    
    return {
        "ok": True,
        "content_md": f"## MLB Teams ({season})\n\nFound {len(teams)} active teams",
        "data": {"source": "mlb_stats_api", "season": season, "count": len(teams), "teams": teams},
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_mlb_team_roster(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get team roster for a specific team"""
    team_id = args.get("teamId")
    if not team_id:
        return {"ok": False, "error": "teamId is required"}
    
    now_et = datetime.now(ET)
    season = int(args.get("season") or now_et.year)
    
    params = {"season": season}
    resp = await mlb_api_get(f"teams/{team_id}/roster", params)
    if not resp.get("ok"):
        return resp
    
    payload = resp["data"]
    roster_raw = payload.get("roster") or []
    
    roster = []
    for p in roster_raw:
        person = p.get("person") or {}
        position = p.get("position") or {}
        roster.append({
            "playerId": person.get("id"),
            "fullName": person.get("fullName"),
            "primaryNumber": p.get("jerseyNumber") or person.get("primaryNumber"),
            "position": position.get("abbreviation"),
            "status": (p.get("status") or {}).get("description"),
        })
    
    return {
        "ok": True,
        "content_md": f"## Team Roster (Team {team_id}, {season})\n\nFound {len(roster)} players",
        "data": {"source": "mlb_stats_api", "season": season, "teamId": team_id, "count": len(roster), "players": roster},
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_mlb_player_last_n(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get last N games for MLB players"""
    player_ids = args.get("player_ids") or []
    if not isinstance(player_ids, list) or not player_ids:
        return {"ok": False, "error": "player_ids (list[int]) is required"}
    
    now_et = datetime.now(ET)
    season = int(args.get("season") or now_et.year)
    group = str(args.get("group") or "hitting").lower()
    if group not in ("hitting", "pitching"):
        return {"ok": False, "error": "group must be 'hitting' or 'pitching'"}
    
    stats_req = args.get("stats") or (["hits", "homeRuns"] if group == "hitting" else ["strikeOuts"])
    count = int(args.get("count") or 5)
    
    # Process players concurrently
    sem = asyncio.Semaphore(15)  # Rate limiting
    results, errors = {}, {}
    
    async def fetch_player_stats(player_id: int):
        async with sem:
            params = {
                "stats": "gameLog",
                "group": group,
                "season": season,
                "sportId": "1",
                "gameType": "R"
            }
            resp = await mlb_api_get(f"people/{player_id}/stats", params)
            if not resp.get("ok"):
                return {"error": resp.get("error", "Unknown error")}
            
            payload = resp["data"]
            stats = payload.get("stats", [])
            splits = stats[0].get("splits", []) if stats and isinstance(stats[0], dict) else []
            
            games = []
            # MLB API returns games chronologically (oldest first), so we need the LAST N games
            recent_splits = splits[-count:] if len(splits) > count else splits
            for s in recent_splits:
                stat = s.get("stat", {}) or {}
                game_iso = (s.get("game") or {}).get("gameDate")
                official = (s.get("game") or {}).get("officialDate") or s.get("date")
                
                # Prioritize gameDate (has actual time) over officialDate (date only)
                primary_time = game_iso if game_iso else official
                if not primary_time:
                    continue
                
                try:
                    et_datetime = to_et_from_api(primary_time)
                except:
                    continue
                
                row = {
                    "et_datetime": et_datetime.isoformat(),
                    "date_et": et_datetime.strftime("%Y-%m-%d"),
                }
                
                for k in stats_req:
                    v = stat.get(k)
                    if isinstance(v, (int, float)):
                        row[k] = v
                    elif isinstance(v, str) and v.isdigit():
                        row[k] = int(v)
                    else:
                        row[k] = v
                
                games.append(row)
            
            # Sort games by date (most recent first)
            games.sort(key=lambda x: (x["date_et"], x["et_datetime"]), reverse=True)
            
            # Calculate aggregates
            aggs = {}
            for k in stats_req:
                vals = [g.get(k) for g in games if isinstance(g.get(k), (int, float))]
                aggs[f"{k}_avg"] = (sum(vals) / len(vals)) if vals else 0.0
                aggs[f"{k}_sum"] = sum(vals) if vals else 0
            
            return {
                "player_id": player_id,
                "season": season,
                "group": group,
                "timezone": "America/New_York",
                "games": games,
                "aggregates": aggs,
                "count": len(games),
            }
    
    # Execute all player requests
    async with httpx.AsyncClient(headers={"user-agent": USER_AGENT}) as client:
        tasks = [fetch_player_stats(int(pid)) for pid in player_ids]
        res_list = await asyncio.gather(*tasks, return_exceptions=True)
    
    for pid, res in zip(player_ids, res_list):
        if isinstance(res, Exception):
            errors[str(pid)] = str(res)
        elif isinstance(res, dict) and "error" in res:
            errors[str(pid)] = res["error"]
        else:
            results[str(pid)] = res
    
    return {
        "ok": True,
        "content_md": f"## Player Stats (Last {count} Games)\n\nProcessed {len(player_ids)} players",
        "data": {
            "source": "mlb_stats_api",
            "timezone": "America/New_York",
            "season": season,
            "group": group,
            "requested_stats": stats_req,
            "results": results,
            "errors": errors
        },
        "meta": {"timestamp": now_iso()}
    }

# New MLB Tools

async def handle_get_mlb_pitcher_matchup(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get pitcher's recent performance and matchup data"""
    pitcher_id = args.get("pitcher_id")
    if not pitcher_id:
        return {"ok": False, "error": "pitcher_id is required"}
    
    now_et = datetime.now(ET)
    season = int(args.get("season") or now_et.year)
    count = int(args.get("count") or 5)
    opponent_team_id = args.get("opponent_team_id")  # Optional
    
    # Get pitcher's recent starts
    params = {
        "stats": "gameLog",
        "group": "pitching", 
        "season": season,
        "sportId": "1",
        "gameType": "R"
    }
    
    resp = await mlb_api_get(f"people/{pitcher_id}/stats", params)
    if not resp.get("ok"):
        return resp
    
    payload = resp["data"]
    stats = payload.get("stats", [])
    splits = stats[0].get("splits", []) if stats and isinstance(stats[0], dict) else []
    
    recent_splits = splits[-count:] if len(splits) > count else splits
    games = []
    
    for s in recent_splits:
        stat = s.get("stat", {}) or {}
        game_iso = (s.get("game") or {}).get("gameDate")
        official = (s.get("game") or {}).get("officialDate") or s.get("date")
        
        primary_time = game_iso if game_iso else official
        if not primary_time:
            continue
        
        try:
            et_datetime = to_et_from_api(primary_time)
        except:
            continue
        
        # Get opposing team info
        opposing_team = (s.get("opponent") or {})
        
        row = {
            "et_datetime": et_datetime.isoformat(),
            "date_et": et_datetime.strftime("%Y-%m-%d"),
            "innings_pitched": stat.get("inningsPitched", 0),
            "earned_runs": stat.get("earnedRuns", 0),
            "strikeouts": stat.get("strikeOuts", 0),
            "walks": stat.get("baseOnBalls", 0),
            "hits_allowed": stat.get("hits", 0),
            "home_runs_allowed": stat.get("homeRuns", 0),
            "pitch_count": stat.get("pitchCount", 0),
            "opponent_team_id": opposing_team.get("id"),
            "opponent_name": opposing_team.get("name")
        }
        
        # Calculate ERA for this game (if innings > 0)
        ip = float(stat.get("inningsPitched", 0))
        er = int(stat.get("earnedRuns", 0))
        row["game_era"] = (er * 9.0 / ip) if ip > 0 else 0.0
        
        # Calculate WHIP for this game
        hits = int(stat.get("hits", 0))
        walks = int(stat.get("baseOnBalls", 0))
        row["game_whip"] = ((hits + walks) / ip) if ip > 0 else 0.0
        
        games.append(row)
    
    # Sort by date (most recent first)
    games.sort(key=lambda x: (x["date_et"], x["et_datetime"]), reverse=True)
    
    # Calculate aggregates
    total_ip = sum(float(g.get("innings_pitched", 0)) for g in games)
    total_er = sum(int(g.get("earned_runs", 0)) for g in games)
    total_k = sum(int(g.get("strikeouts", 0)) for g in games)
    total_bb = sum(int(g.get("walks", 0)) for g in games)
    total_hits = sum(int(g.get("hits_allowed", 0)) for g in games)
    
    aggs = {
        "era": (total_er * 9.0 / total_ip) if total_ip > 0 else 0.0,
        "whip": ((total_hits + total_bb) / total_ip) if total_ip > 0 else 0.0,
        "k_per_9": (total_k * 9.0 / total_ip) if total_ip > 0 else 0.0,
        "innings_pitched": total_ip,
        "strikeouts": total_k,
        "walks": total_bb,
        "hits_allowed": total_hits
    }
    
    # Filter games vs specific opponent if requested
    vs_opponent_games = []
    if opponent_team_id:
        vs_opponent_games = [g for g in games if g.get("opponent_team_id") == opponent_team_id]
    
    return {
        "ok": True,
        "content_md": f"## Pitcher Matchup Analysis\n\nLast {len(games)} starts for Pitcher {pitcher_id}",
        "data": {
            "source": "mlb_stats_api",
            "pitcher_id": pitcher_id,
            "season": season,
            "recent_starts": games,
            "aggregates": aggs,
            "vs_opponent": vs_opponent_games if opponent_team_id else None,
            "count": len(games)
        },
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_mlb_team_scoring_trends(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get team's recent scoring patterns and trends"""
    team_id = args.get("team_id")
    if not team_id:
        return {"ok": False, "error": "team_id is required"}
    
    now_et = datetime.now(ET)
    season = int(args.get("season") or now_et.year)
    count = int(args.get("count") or 10)
    
    # Use simplified approach - get team standings for basic info
    resp = await mlb_api_get(f"standings", {"leagueId": "103,104", "season": season})
    if not resp.get("ok"):
        return resp
    
    # Find the specific team in standings
    standings = resp["data"]
    team_record = None
    
    for league in standings.get("records", []):
        for division in league.get("teamRecords", []):
            if division.get("team", {}).get("id") == int(team_id):
                team_record = division
                break
        if team_record:
            break
    
    if not team_record:
        return {"ok": False, "error": f"Team {team_id} not found in standings"}
    
    # Extract scoring trends from standings data
    runs_scored = team_record.get("runsScored", 0)
    runs_allowed = team_record.get("runsAllowed", 0)
    games_played = team_record.get("gamesPlayed", 1)
    
    trends = {
        "runs_per_game": round(runs_scored / max(games_played, 1), 2),
        "runs_allowed_per_game": round(runs_allowed / max(games_played, 1), 2),
        "run_differential": runs_scored - runs_allowed,
        "run_differential_per_game": round((runs_scored - runs_allowed) / max(games_played, 1), 2),
        "total_runs_scored": runs_scored,
        "total_runs_allowed": runs_allowed,
        "games_played": games_played
    }
    
    return {
        "ok": True,
        "content_md": f"## Team Scoring Trends\n\nTeam {team_id} season scoring analysis",
        "data": {
            "source": "mlb_stats_api",
            "team_id": team_id,
            "season": season,
            "team_name": team_record.get("team", {}).get("name", "Unknown"),
            "trends": trends,
            "note": "Season-long scoring averages from standings data"
        },
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_mlb_team_form(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get team's recent form and win/loss patterns"""
    team_id = args.get("team_id")
    if not team_id:
        return {"ok": False, "error": "team_id is required"}
    
    now_et = datetime.now(ET)
    season = int(args.get("season") or now_et.year)
    
    # Get team standings/record
    resp = await mlb_api_get(f"standings", {"leagueId": "103,104", "season": season})
    if not resp.get("ok"):
        return resp
    
    # Find the specific team in standings
    standings = resp["data"]
    team_record = None
    
    for league in standings.get("records", []):
        for division in league.get("teamRecords", []):
            if division.get("team", {}).get("id") == int(team_id):
                team_record = division
                break
        if team_record:
            break
    
    if not team_record:
        return {"ok": False, "error": f"Team {team_id} not found in standings"}
    
    form_data = {
        "wins": team_record.get("wins", 0),
        "losses": team_record.get("losses", 0),
        "win_percentage": team_record.get("winningPercentage", "0.000"),
        "games_back": team_record.get("gamesBack", "0.0"),
        "streak": team_record.get("streak", {}).get("streakCode", ""),
        "last_10": team_record.get("last10", "0-0"),
        "home_record": f"{team_record.get('home', {}).get('wins', 0)}-{team_record.get('home', {}).get('losses', 0)}",
        "away_record": f"{team_record.get('away', {}).get('wins', 0)}-{team_record.get('away', {}).get('losses', 0)}"
    }
    
    return {
        "ok": True,
        "content_md": f"## Team Form Analysis\n\nTeam {team_id} current season record",
        "data": {
            "source": "mlb_stats_api",
            "team_id": team_id,
            "season": season,
            "form": form_data,
            "team_name": team_record.get("team", {}).get("name", "Unknown")
        },
        "meta": {"timestamp": now_iso()}
    }

async def handle_get_mlb_player_streaks(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get player's current streaks and consistency patterns"""
    player_ids = args.get("player_ids") or []
    if not isinstance(player_ids, list) or not player_ids:
        return {"ok": False, "error": "player_ids (list[int]) is required"}
    
    now_et = datetime.now(ET)
    season = int(args.get("season") or now_et.year)
    lookback = int(args.get("lookback") or 20)  # Games to analyze for streaks
    
    results = {}
    errors = {}
    
    for player_id in player_ids:
        try:
            # Get player's recent games
            params = {
                "stats": "gameLog",
                "group": "hitting",
                "season": season,
                "sportId": "1", 
                "gameType": "R"
            }
            
            resp = await mlb_api_get(f"people/{player_id}/stats", params)
            if not resp.get("ok"):
                errors[str(player_id)] = resp.get("error", "Failed to get player data")
                continue
            
            payload = resp["data"]
            stats = payload.get("stats", [])
            splits = stats[0].get("splits", []) if stats and isinstance(stats[0], dict) else []
            
            recent_splits = splits[-lookback:] if len(splits) > lookback else splits
            
            # Analyze streaks
            current_hit_streak = 0
            current_multi_hit_streak = 0
            current_hr_streak = 0
            longest_hit_streak = 0
            multi_hit_games = 0
            total_games = 0
            
            for s in reversed(recent_splits):  # Most recent first
                stat = s.get("stat", {}) or {}
                hits = int(stat.get("hits", 0))
                hrs = int(stat.get("homeRuns", 0))
                
                total_games += 1
                
                # Hit streak (consecutive games with at least 1 hit)
                if hits > 0:
                    current_hit_streak += 1
                    longest_hit_streak = max(longest_hit_streak, current_hit_streak)
                else:
                    if current_hit_streak > longest_hit_streak:
                        longest_hit_streak = current_hit_streak
                    current_hit_streak = 0
                
                # Multi-hit games
                if hits >= 2:
                    multi_hit_games += 1
                    current_multi_hit_streak += 1
                else:
                    current_multi_hit_streak = 0
                
                # Home run streak
                if hrs > 0:
                    current_hr_streak += 1
                else:
                    current_hr_streak = 0
            
            streak_data = {
                "current_hit_streak": current_hit_streak,
                "longest_hit_streak_in_period": longest_hit_streak,
                "current_multi_hit_streak": current_multi_hit_streak,
                "current_hr_streak": current_hr_streak,
                "multi_hit_games": multi_hit_games,
                "multi_hit_frequency": f"{multi_hit_games}/{total_games}" if total_games > 0 else "0/0",
                "games_analyzed": total_games
            }
            
            results[str(player_id)] = {
                "player_id": player_id,
                "season": season,
                "streaks": streak_data,
                "lookback_games": lookback
            }
            
        except Exception as e:
            errors[str(player_id)] = str(e)
    
    return {
        "ok": True,
        "content_md": f"## Player Streaks Analysis\n\nAnalyzed {len(player_ids)} players",
        "data": {
            "source": "mlb_stats_api",
            "season": season,
            "results": results,
            "errors": errors
        },
        "meta": {"timestamp": now_iso()}
    }

# MCP Tool registry
TOOLS = {
    "getMLBScheduleET": {
        "description": "Get MLB games for a specific ET date",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format (ET timezone)", "optional": True}
            }
        },
        "handler": handle_get_mlb_schedule_et
    },
    "getMLBTeams": {
        "description": "Get active MLB teams for a season",
        "parameters": {
            "type": "object",
            "properties": {
                "season": {"type": "integer", "description": "Season year (default: current year)", "optional": True}
            }
        },
        "handler": handle_get_mlb_teams
    },
    "getMLBTeamRoster": {
        "description": "Get team roster for a specific team",
        "parameters": {
            "type": "object",
            "properties": {
                "teamId": {"type": "integer", "description": "MLB team ID"},
                "season": {"type": "integer", "description": "Season year (default: current year)", "optional": True}
            },
            "required": ["teamId"]
        },
        "handler": handle_get_mlb_team_roster
    },
    "getMLBPlayerLastN": {
        "description": "Get last N games stats for MLB players",
        "parameters": {
            "type": "object",
            "properties": {
                "player_ids": {"type": "array", "description": "List of MLB player IDs"},
                "season": {"type": "integer", "description": "Season year (default: current year)", "optional": True},
                "group": {"type": "string", "description": "Stats group: 'hitting' or 'pitching'", "optional": True},
                "stats": {"type": "array", "description": "List of stat names to retrieve", "optional": True},
                "count": {"type": "integer", "description": "Number of recent games (default: 5)", "optional": True}
            },
            "required": ["player_ids"]
        },
        "handler": handle_get_mlb_player_last_n
    },
    "getMLBPitcherMatchup": {
        "description": "Get pitcher's recent performance and matchup analysis",
        "parameters": {
            "type": "object",
            "properties": {
                "pitcher_id": {"type": "integer", "description": "MLB pitcher ID"},
                "season": {"type": "integer", "description": "Season year (default: current year)", "optional": True},
                "count": {"type": "integer", "description": "Number of recent starts (default: 5)", "optional": True},
                "opponent_team_id": {"type": "integer", "description": "Optional team ID for head-to-head analysis", "optional": True}
            },
            "required": ["pitcher_id"]
        },
        "handler": handle_get_mlb_pitcher_matchup
    },
    "getMLBTeamScoringTrends": {
        "description": "Get team's recent scoring patterns and trends",
        "parameters": {
            "type": "object", 
            "properties": {
                "team_id": {"type": "integer", "description": "MLB team ID"},
                "season": {"type": "integer", "description": "Season year (default: current year)", "optional": True},
                "count": {"type": "integer", "description": "Number of recent games (default: 10)", "optional": True}
            },
            "required": ["team_id"]
        },
        "handler": handle_get_mlb_team_scoring_trends
    },
    "getMLBTeamForm": {
        "description": "Get team's recent form and win/loss patterns",
        "parameters": {
            "type": "object",
            "properties": {
                "team_id": {"type": "integer", "description": "MLB team ID"},
                "season": {"type": "integer", "description": "Season year (default: current year)", "optional": True}
            },
            "required": ["team_id"]
        },
        "handler": handle_get_mlb_team_form
    },
    "getMLBPlayerStreaks": {
        "description": "Get player's current streaks and consistency patterns",
        "parameters": {
            "type": "object",
            "properties": {
                "player_ids": {"type": "array", "description": "List of MLB player IDs"},
                "season": {"type": "integer", "description": "Season year (default: current year)", "optional": True},
                "lookback": {"type": "integer", "description": "Games to analyze for streaks (default: 20)", "optional": True}
            },
            "required": ["player_ids"]
        },
        "handler": handle_get_mlb_player_streaks
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
            "name": "mlb-mcp",
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
    Route("/mcp/", handle_mcp_request, methods=["POST"]),
]

app = Starlette(routes=routes)

@app.on_event("startup")
async def startup():
    print("=" * 60)
    print("MLB MCP Server Starting - v1.0")
    print(f"MLB Tools: {len(TOOLS)}")
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