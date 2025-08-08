# ================= Entrypoint =================
async def amain():
    await server.run_stdio_async()
import asyncio
import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import httpx
from fastmcp import FastMCP

# ================= Configuration =================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/auto")
MAX_INPUT_BYTES = int(os.getenv("MAX_INPUT_BYTES", "8000"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "700"))
REQUEST_CONNECT_TIMEOUT = float(os.getenv("REQUEST_CONNECT_TIMEOUT", "5"))
REQUEST_READ_TIMEOUT = float(os.getenv("REQUEST_READ_TIMEOUT", "15"))

ESPN_BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"
USER_AGENT = "sports-ai-analyzer/1.2"
PROMPT_VERSION = "v1.2"

# ================= Allowed routes (scoreboard/teams/news/standings-link) =================
# League slugs follow ESPN patterns. Add more as needed.
ALLOWED_ROUTES: Dict[Tuple[str, str], Dict[str, str]] = {
    ("basketball", "wnba"): {
        "scoreboard": "/basketball/wnba/scoreboard",
        "teams": "/basketball/wnba/teams",
        "news": "/basketball/wnba/news",
        "standings": "/basketball/wnba/standings",  # returns link metadata only
    },
    ("basketball", "nba"): {
        "scoreboard": "/basketball/nba/scoreboard",
        "teams": "/basketball/nba/teams",
        "news": "/basketball/nba/news",
        "standings": "/basketball/nba/standings",
    },
    ("baseball", "mlb"): {
        "scoreboard": "/baseball/mlb/scoreboard",
        "teams": "/baseball/mlb/teams",
        "news": "/baseball/mlb/news",
        "standings": "/baseball/mlb/standings",
    },
    ("hockey", "nhl"): {
        "scoreboard": "/hockey/nhl/scoreboard",
        "teams": "/hockey/nhl/teams",
        "news": "/hockey/nhl/news",
        "standings": "/hockey/nhl/standings",
    },
    ("football", "nfl"): {
        "scoreboard": "/football/nfl/scoreboard",
        "teams": "/football/nfl/teams",
        "news": "/football/nfl/news",
        "standings": "/football/nfl/standings",
    },
    ("football", "college-football"): {
        "scoreboard": "/football/college-football/scoreboard",
        "teams": "/football/college-football/teams",
        "news": "/football/college-football/news",
        "standings": "/football/college-football/standings",
    },
    ("basketball", "mens-college-basketball"): {
        "scoreboard": "/basketball/mens-college-basketball/scoreboard",
        "teams": "/basketball/mens-college-basketball/teams",
        "news": "/basketball/mens-college-basketball/news",
        "standings": "/basketball/mens-college-basketball/standings",
    },
    ("soccer", "usa.1"): {  # MLS
        "scoreboard": "/soccer/usa.1/scoreboard",
        "teams": "/soccer/usa.1/teams",
        "news": "/soccer/usa.1/news",
        "standings": "/soccer/usa.1/standings",
    },
    ("soccer", "eng.1"): {  # EPL
        "scoreboard": "/soccer/eng.1/scoreboard",
        "teams": "/soccer/eng.1/teams",
        "news": "/soccer/eng.1/news",
        "standings": "/soccer/eng.1/standings",
    },
}

# ================= Shared HTTP clients =================
_http_client: Optional[httpx.AsyncClient] = None
_or_client: Optional[httpx.AsyncClient] = None

async def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=REQUEST_CONNECT_TIMEOUT, read=REQUEST_READ_TIMEOUT),
            headers={"user-agent": USER_AGENT, "accept": "application/json"},
        )
    return _http_client

async def get_or_client() -> httpx.AsyncClient:
    global _or_client
    if _or_client is None:
        _or_client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=REQUEST_CONNECT_TIMEOUT, read=REQUEST_READ_TIMEOUT),
            headers={"user-agent": USER_AGENT},
        )
    return _or_client

# ================= Utilities =================

def sanitize_segment(s: str) -> str:
    # allow dot for soccer (e.g., eng.1)
    if not re.fullmatch(r"[a-z0-9_.-]+", s):
        raise ValueError(f"Invalid segment: {s!r}")
    return s

def resolve_route(sport: str, league: str, endpoint: str) -> str:
    sport = sanitize_segment(sport.lower())
    league = sanitize_segment(league.lower())
    endpoint = sanitize_segment(endpoint.lower())
    try:
        return ALLOWED_ROUTES[(sport, league)][endpoint]
    except KeyError:
        raise ValueError(f"Unsupported route: {sport}/{league}/{endpoint}")

async def fetch_espn(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = f"{ESPN_BASE_URL}{endpoint}"
    client = await get_http_client()
    try:
        r = await client.get(url, params=params or {})
        if r.status_code >= 400:
            excerpt = r.text[:500] if r.text else None
            return {
                "ok": False,
                "error_type": "upstream_error",
                "source": "ESPN",
                "status": r.status_code,
                "url": str(r.request.url),
                "body_excerpt": excerpt,
            }
        return {"ok": True, "data": r.json(), "url": str(r.request.url)}
    except httpx.RequestError as e:
        return {"ok": False, "error_type": "request_error", "source": "ESPN", "url": url, "message": str(e)}


def truncate_utf8(s: str, limit: int = MAX_INPUT_BYTES) -> str:
    b = s.encode("utf-8")
    return b[:limit].decode("utf-8", "ignore")


def compute_data_age_seconds(iso_timestamp: Optional[str]) -> Optional[int]:
    if not iso_timestamp:
        return None
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        return int((datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds())
    except Exception:
        return None


def summarize_events(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Normalize ESPN event payload to a small, stable schema
    events = payload.get("events") or []
    summary = []
    newest_ts = None
    for ev in events:
        ev_id = ev.get("id")
        date = ev.get("date")
        if date and (newest_ts is None or date > newest_ts):
            newest_ts = date
        comps = ev.get("competitions") or []
        comp = comps[0] if comps else {}
        competitors = (comp.get("competitors") or [])[:2]
        if len(competitors) < 2:
            continue
        def tinfo(c):
            t = c.get("team") or {}
            return {
                "id": t.get("id"),
                "displayName": t.get("displayName"),
                "abbrev": t.get("abbreviation"),
                "score": c.get("score"),
                "homeAway": c.get("homeAway"),
            }
        summary.append({
            "id": ev_id,
            "date": date,
            "home": tinfo(next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])),
            "away": tinfo(next((c for c in competitors if c.get("homeAway") == "away"), competitors[-1])),
            "status": (comp.get("status") or {}).get("type", {}).get("state"),
        })
    return {"events": summary, "newest_event_time": newest_ts}


# ================= OpenRouter analysis =================
async def analyze_with_openrouter(payload_json: str, analysis_prompt: str) -> Tuple[bool, str]:
    if not OPENROUTER_API_KEY:
        return False, "OpenRouter API key not configured. Set OPENROUTER_API_KEY."
    client = await get_or_client()
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "X-Title": "Sports AI Analyzer",
    }
    body = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "You are a precise sports analyst. Be concise and factual."},
            {"role": "user", "content": truncate_utf8(payload_json)},
            {"role": "user", "content": analysis_prompt},
        ],
        "max_tokens": MAX_OUTPUT_TOKENS,
        "temperature": 0.2,
        "stream": False,
    }
    try:
        r = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        if r.status_code >= 400:
            return False, f"OpenRouter error {r.status_code}: {r.text[:300]}"
        data = r.json()
        content = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
        return True, content.strip()
    except httpx.RequestError as e:
        return False, f"OpenRouter request error: {e}"


# ================= Envelope helpers =================

def envelope_ok(markdown: str, games_summary: Dict[str, Any], meta_extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    meta = {
        "source": "espn",
        "newest_event_time": games_summary.get("newest_event_time"),
        "data_age_seconds": compute_data_age_seconds(games_summary.get("newest_event_time")),
        "prompt_version": PROMPT_VERSION,
        "model": OPENROUTER_MODEL,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    if meta_extra:
        meta.update(meta_extra)
    return {
        "ok": True,
        "content_md": markdown,
        "games": games_summary.get("events", []),
        "meta": meta,
    }


# ================= Param validation =================

def _validate_params_for_league(sport: str, league: str, params: Dict[str, Any]) -> None:
    allows_week = (sport, league) in [("football", "nfl"), ("football", "college-football")]
    if not allows_week:
        if any(k in params for k in ("week", "seasontype")):
            raise ValueError("'week'/'seasontype' only allowed for NFL or College Football")
    else:
        if "week" in params:
            w = params["week"]
            if not isinstance(w, int) or w <= 0:
                raise ValueError("week must be a positive integer")
        if "seasontype" in params and params["seasontype"] not in (1, 2, 3):
            raise ValueError("seasontype must be 1 (pre), 2 (reg), or 3 (post)")


# ================= MCP Server & Tools =================
server = FastMCP("sports-ai-analyzer")

@server.tool(name="getScoreboard", description="Generic scoreboard for supported leagues. Params: sport, league, dates?, limit?, week?, seasontype? (week/seasontype for NFL/NCAAF only)")
async def get_scoreboard(sport: str, league: str, dates: Optional[str] = None, limit: Optional[int] = None, week: Optional[int] = None, seasontype: Optional[int] = None) -> Dict[str, Any]:
    try:
        route = resolve_route(sport, league, "scoreboard")
    except Exception as e:
        return {"ok": False, "error_type": "validation_error", "message": str(e)}

    params: Dict[str, Any] = {}
    if dates:
        params["dates"] = dates
    if limit is not None:
        if not isinstance(limit, int) or limit <= 0:
            return {"ok": False, "error_type": "validation_error", "message": "limit must be a positive integer"}
        params["limit"] = limit
    if week is not None:
        params["week"] = week
    if seasontype is not None:
        params["seasontype"] = seasontype

    try:
        _validate_params_for_league(sport.lower(), league.lower(), params)
    except Exception as e:
        return {"ok": False, "error_type": "validation_error", "message": str(e)}

    resp = await fetch_espn(route, params)
    if not resp.get("ok"):
        return resp

    summary = summarize_events(resp["data"]) if resp.get("ok") else {}
    md = f"""## Scoreboard: {sport}/{league}

Params: `{json.dumps(params)}`

Events: {len(summary.get('events', []))}"""
    return envelope_ok(md, summary, {"sport": sport.lower(), "league": league.lower(), "resolved": route})


@server.tool(name="getTeams", description="Team directory for supported leagues. Params: sport, league")
async def get_teams(sport: str, league: str) -> Dict[str, Any]:
    try:
        route = resolve_route(sport, league, "teams")
    except Exception as e:
        return {"ok": False, "error_type": "validation_error", "message": str(e)}

    resp = await fetch_espn(route)
    if not resp.get("ok"):
        return resp

    data = resp["data"]
    teams = data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
    # Normalize minimal team info
    norm = []
    for t in teams:
        info = t.get("team") or {}
        norm.append({
            "id": info.get("id"),
            "displayName": info.get("displayName"),
            "abbrev": info.get("abbreviation"),
            "location": info.get("location"),
            "logos": info.get("logos"),
            "links": info.get("links"),
        })
    md = f"""## Teams: {sport}/{league}

Count: {len(norm)}"""
    return {"ok": True, "content_md": md, "teams": norm, "meta": {"resolved": route, "generated_at": datetime.now(timezone.utc).isoformat()}}


@server.tool(name="getNews", description="League news (metadata only). Params: sport, league")
async def get_news(sport: str, league: str) -> Dict[str, Any]:
    try:
        route = resolve_route(sport, league, "news")
    except Exception as e:
        return {"ok": False, "error_type": "validation_error", "message": str(e)}

    resp = await fetch_espn(route)
    if not resp.get("ok"):
        return resp

    articles = (resp["data"].get("articles") or [])
    # Lightly normalize expected fields
    norm = []
    for a in articles:
        norm.append({
            "id": a.get("id"),
            "headline": a.get("headline"),
            "published": a.get("published"),
            "images": a.get("images"),
            "links": a.get("links"),
        })
    md = f"""## News: {sport}/{league}

Articles: {len(norm)}"""
    return {"ok": True, "content_md": md, "news": norm, "meta": {"resolved": route, "generated_at": datetime.now(timezone.utc).isoformat()}}


@server.tool(name="getStandingsLink", description="Returns link metadata for standings (raw standings not available via ESPN JSON for some leagues). Params: sport, league")
async def get_standings_link(sport: str, league: str) -> Dict[str, Any]:
    try:
        route = resolve_route(sport, league, "standings")
    except Exception as e:
        return {"ok": False, "error_type": "validation_error", "message": str(e)}

    resp = await fetch_espn(route)
    if not resp.get("ok"):
        return resp

    # Many standings endpoints return link metadata rather than raw table
    data = resp["data"]
    link = None
    # Heuristic places where ESPN hides the page link
    for k in ("links", "standings", "Leagues", "leagues"):
        v = data.get(k)
        if isinstance(v, list) and v:
            link = v[0]
            break
    md = f"""## Standings Link: {sport}/{league}

Raw standings often unavailable; use returned URL in a browser."""
    return {"ok": True, "content_md": md, "standings": link or data, "meta": {"resolved": route}}


# --------- WNBA-specific analysis tool (preserving original feature set) ---------
ANALYSIS_TYPES_WNBA = {"general", "betting", "performance", "predictions"}

@server.tool(name="analyzeWnbaGames", description="Analyze WNBA games by date with an analysis_type: general|betting|performance|predictions")
async def analyze_wnba_games(dates: Optional[str] = None, limit: Optional[int] = None, analysis_type: str = "general", custom_prompt: Optional[str] = None) -> Dict[str, Any]:
    # Validate
    if analysis_type not in ANALYSIS_TYPES_WNBA:
        return {"ok": False, "error_type": "validation_error", "message": f"analysis_type must be one of {sorted(ANALYSIS_TYPES_WNBA)}"}

    # Fetch scoreboard
    sb = await get_scoreboard("basketball", "wnba", dates=dates, limit=limit)
    if not sb.get("ok"):
        return sb

    # Prepare payload for analysis
    payload = {
        "league": "wnba",
        "params": {"dates": dates, "limit": limit},
        "games": sb.get("games", []),
        "meta": sb.get("meta", {}),
        "analysis_type": analysis_type,
    }

    # Prompt selection
    default_prompts = {
        "general": "Provide a concise, factual summary of today’s WNBA games and notable storylines.",
        "betting": "Identify actionable pre-game or in-game betting insights, based strictly on the data provided. Avoid fabricating odds.",
        "performance": "Analyze team and player performance trends observable in these games. Be specific and avoid speculation.",
        "predictions": "Provide cautious predictions grounded only in the listed data; state confidence qualitatively and note uncertainties.",
    }
    prompt = custom_prompt or default_prompts[analysis_type]

    ok, analysis = await analyze_with_openrouter(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), prompt)

    md = f"""## WNBA Games Analysis ({analysis_type})

Params: `{json.dumps({'dates': dates, 'limit': limit})}`

{analysis if ok else f"Analysis failed: {analysis}"}"""
    return envelope_ok(md, {"events": payload["games"], "newest_event_time": (sb.get('meta') or {}).get('newest_event_time')}, {"league": "wnba"})


# Convenience NFL tool (kept for parity with original)
@server.tool(name="getNFLScoreboard", description="NFL scoreboard convenience wrapper (supports week/dates/seasontype)")
async def get_nfl_scoreboard(week: Optional[int] = None, dates: Optional[str] = None, seasontype: Optional[int] = None) -> Dict[str, Any]:
    return await get_scoreboard("football", "nfl", dates=dates, week=week, seasontype=seasontype)


# General analysis tool across any supported league/endpoint
@server.tool(name="customSportsAnalysis", description="Analyze any supported sport/league endpoint via OpenRouter. endpoint in {scoreboard, teams, news, standings}")
async def custom_sports_analysis(sport: str, league: str, endpoint: str, custom_prompt: str, dates: Optional[str] = None, limit: Optional[int] = None, week: Optional[int] = None, seasontype: Optional[int] = None) -> Dict[str, Any]:
    try:
        route = resolve_route(sport, league, endpoint)
    except Exception as e:
        return {"ok": False, "error_type": "validation_error", "message": str(e)}

    params: Dict[str, Any] = {}
    if dates:
        params["dates"] = dates
    if limit is not None:
        if not isinstance(limit, int) or limit <= 0:
            return {"ok": False, "error_type": "validation_error", "message": "limit must be a positive integer"}
        params["limit"] = limit
    if week is not None:
        params["week"] = week
    if seasontype is not None:
        params["seasontype"] = seasontype

    try:
        _validate_params_for_league(sport.lower(), league.lower(), params)
    except Exception as e:
        return {"ok": False, "error_type": "validation_error", "message": str(e)}

    resp = await fetch_espn(route, params)
    if not resp.get("ok"):
        return resp

    data = resp["data"]
    # prefer events summary if present; otherwise pass raw
    if endpoint == "scoreboard":
        summary = summarize_events(data)
        payload = {"route": {"sport": sport, "league": league, "endpoint": endpoint}, "params": params, "summary": summary}
        md_summary = summary
    else:
        payload = {"route": {"sport": sport, "league": league, "endpoint": endpoint}, "params": params, "data": data}
        md_summary = {"events": [], "newest_event_time": None}

    ok, analysis = await analyze_with_openrouter(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), custom_prompt)

    md = f"## Custom Sports Analysis ({sport}/{league}/{endpoint})\n\nParams: `{json.dumps(params)}`\n\n"
    md += (analysis if ok else f"Analysis failed: {analysis}")
    
    return {"content": [{"type": "text", "text": md}]}

if __name__ == "__main__":
    asyncio.run(amain())