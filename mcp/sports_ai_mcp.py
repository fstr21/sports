import asyncio
import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple, List

import httpx
from fastmcp import FastMCP

# =========================== Config ===========================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/auto")
MAX_INPUT_BYTES = int(os.getenv("MAX_INPUT_BYTES", "10000"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "700"))
REQUEST_CONNECT_TIMEOUT = float(os.getenv("REQUEST_CONNECT_TIMEOUT", "5"))
REQUEST_READ_TIMEOUT = float(os.getenv("REQUEST_READ_TIMEOUT", "20"))
USER_AGENT = "sports-ai-mcp/2.0"
PROMPT_VERSION = "v2.0"

ESPN_BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

# Supported leagues (expand as needed)
ALLOWED_ROUTES: Dict[Tuple[str, str], Dict[str, str]] = {
    ("baseball", "mlb"): {
        "scoreboard": "/baseball/mlb/scoreboard",
        "teams": "/baseball/mlb/teams",
        "summary": "/baseball/mlb/summary",
    },
    ("basketball", "nba"): {
        "scoreboard": "/basketball/nba/scoreboard",
        "teams": "/basketball/nba/teams",
        "summary": "/basketball/nba/summary",
    },
    ("basketball", "wnba"): {
        "scoreboard": "/basketball/wnba/scoreboard",
        "teams": "/basketball/wnba/teams",
        "summary": "/basketball/wnba/summary",
    },
    ("football", "nfl"): {
        "scoreboard": "/football/nfl/scoreboard",
        "teams": "/football/nfl/teams",
        "summary": "/football/nfl/summary",
    },
    ("football", "college-football"): {
        "scoreboard": "/football/college-football/scoreboard",
        "teams": "/football/college-football/teams",
        "summary": "/football/college-football/summary",
    },
    ("basketball", "mens-college-basketball"): {
        "scoreboard": "/basketball/mens-college-basketball/scoreboard",
        "teams": "/basketball/mens-college-basketball/teams",
        "summary": "/basketball/mens-college-basketball/summary",
    },
    ("hockey", "nhl"): {
        "scoreboard": "/hockey/nhl/scoreboard",
        "teams": "/hockey/nhl/teams",
        "summary": "/hockey/nhl/summary",
    },
    ("soccer", "eng.1"): {
        "scoreboard": "/soccer/eng.1/scoreboard",
        "teams": "/soccer/eng.1/teams",
        "summary": "/soccer/eng.1/summary",
    },
    ("soccer", "esp.1"): {
        "scoreboard": "/soccer/esp.1/scoreboard",
        "teams": "/soccer/esp.1/teams",
        "summary": "/soccer/esp.1/summary",
    },
    ("soccer", "usa.1"): {
        "scoreboard": "/soccer/usa.1/scoreboard",
        "teams": "/soccer/usa.1/teams",
        "summary": "/soccer/usa.1/summary",
    },
}

# =========================== HTTP ===========================
_http_client: Optional[httpx.AsyncClient] = None
_or_client: Optional[httpx.AsyncClient] = None

async def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            timeout=REQUEST_READ_TIMEOUT,  # Simple timeout value
            headers={"user-agent": USER_AGENT, "accept": "application/json"},
        )
    return _http_client

async def get_or_client() -> httpx.AsyncClient:
    global _or_client
    if _or_client is None:
        _or_client = httpx.AsyncClient(
            timeout=REQUEST_READ_TIMEOUT,  # Simple timeout value
            headers={"user-agent": USER_AGENT},
        )
    return _or_client

def sanitize_segment(s: str) -> str:
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

async def espn_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = f"{ESPN_BASE_URL}{path}"
    client = await get_http_client()
    try:
        r = await client.get(url, params=params or {})
        if r.status_code >= 400:
            return {
                "ok": False,
                "error_type": "upstream_error",
                "source": "ESPN",
                "status": r.status_code,
                "url": str(r.request.url),
                "body_excerpt": r.text[:500],
            }
        return {"ok": True, "data": r.json(), "url": str(r.request.url)}
    except httpx.RequestError as e:
        return {"ok": False, "error_type": "request_error", "source": "ESPN", "url": url, "message": str(e)}

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def compute_data_age_seconds(iso_timestamp: Optional[str]) -> Optional[int]:
    if not iso_timestamp:
        return None
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        return int((datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds())
    except Exception:
        return None

# =========================== Normalizers ===========================
def summarize_events(scoreboard: Dict[str, Any]) -> Dict[str, Any]:
    events = scoreboard.get("events") or []
    out: List[Dict[str, Any]] = []
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
    competitions = summary_json.get("competitions") or []
    game = competitions[0] if competitions else {}
    status = (game.get("status") or {}).get("type", {}).get("state")
    boxscore = summary_json.get("boxscore")
    leaders = summary_json.get("leaders")
    teams_meta: List[Dict[str, Any]] = []
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

# =========================== OpenRouter ===========================
def truncate_utf8(s: str, limit: int = MAX_INPUT_BYTES) -> str:
    b = s.encode("utf-8")
    return b[:limit].decode("utf-8", "ignore")

async def ask_openrouter(payload: Dict[str, Any], prompt: str) -> Tuple[bool, str]:
    if not OPENROUTER_API_KEY:
        return False, "OpenRouter API key not configured. Set OPENROUTER_API_KEY."
    client = await get_or_client()
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "X-Title": "Sports AI MCP",
    }
    body = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": (
                "You are a precise sports analyst. "
                "Only summarize numeric/text fields present in the provided JSON. "
                "If a stat is missing, say 'unavailable'. Never infer or fabricate."
            )},
            {"role": "user", "content": truncate_utf8(json.dumps(payload, ensure_ascii=False))},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": MAX_OUTPUT_TOKENS,
        "temperature": 0.1,
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

# =========================== Envelopes ===========================
def ok_envelope(content_md: str, data: Dict[str, Any], meta_extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    meta = {
        "source": "espn",
        "generated_at": now_iso(),
        "prompt_version": PROMPT_VERSION,
    }
    if meta_extra:
        meta.update(meta_extra)
    return {"ok": True, "content_md": content_md, "data": data, "meta": meta}

def err(msg: str, **extra: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {"ok": False, "message": msg}
    out.update(extra)
    return out

# =========================== MCP Server ===========================
server = FastMCP("sports-ai-mcp")

@server.tool(name="getScoreboard", description="Get scoreboard for a league. Params: sport, league, dates?, limit?, week?, seasontype? (NFL/NCAAF only)")
async def get_scoreboard(sport: str, league: str, dates: Optional[str] = None, limit: Optional[int] = None, week: Optional[int] = None, seasontype: Optional[int] = None) -> Dict[str, Any]:
    try:
        path = resolve_route(sport, league, "scoreboard")
    except Exception as e:
        return err(str(e), error_type="validation_error")
    params: Dict[str, Any] = {}
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
    if (sport.lower(), league.lower()) not in [("football", "nfl"), ("football", "college-football")]:
        for k in ("week", "seasontype"):
            if k in params:
                return err("'week'/'seasontype' only for NFL/NCAAF", error_type="validation_error")

    resp = await espn_get(path, params)
    if not resp.get("ok"):
        return resp
    summary = summarize_events(resp["data"])
    md = f"## Scoreboard {sport}/{league}\n\nEvents: {len(summary['events'])}"
    return ok_envelope(md, {"scoreboard": summary}, {"league": league, "sport": sport, "url": resp.get("url")})

@server.tool(name="getTeams", description="List teams for a league. Params: sport, league")
async def get_teams(sport: str, league: str) -> Dict[str, Any]:
    try:
        path = resolve_route(sport, league, "teams")
    except Exception as e:
        return err(str(e), error_type="validation_error")
    resp = await espn_get(path)
    if not resp.get("ok"):
        return resp
    teams = resp["data"].get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
    norm: List[Dict[str, Any]] = []
    for t in teams:
        info = t.get("team") or {}
        norm.append({
            "id": info.get("id"),
            "displayName": info.get("displayName"),
            "abbrev": info.get("abbreviation"),
            "location": info.get("location"),
        })
    md = f"## Teams {sport}/{league}\n\nCount: {len(norm)}"
    return ok_envelope(md, {"teams": norm}, {"league": league, "sport": sport, "url": resp.get("url")})

@server.tool(name="getGameSummary", description="Game summary/boxscore for a single event. Params: sport, league, event_id")
async def get_game_summary(sport: str, league: str, event_id: str) -> Dict[str, Any]:
    try:
        path = resolve_route(sport, league, "summary")
    except Exception as e:
        return err(str(e), error_type="validation_error")
    if not event_id:
        return err("event_id is required", error_type="validation_error")
    resp = await espn_get(path, {"event": event_id})
    if not resp.get("ok"):
        return resp
    core = extract_summary_core(resp["data"])
    md = f"## Game Summary {sport}/{league} event={event_id}\n\nStatus: {core.get('status') or 'unknown'}"
    return ok_envelope(md, {"summary": core}, {"league": league, "sport": sport, "event_id": event_id, "url": resp.get("url")})

# -------- Season stats tools (Option A: strict availability only) --------
@server.tool(name="getTeamSeasonStats", description="Team season stats if ESPN JSON exposes them cleanly; else supported:false. Params: sport, league, team_id, season?")
async def get_team_season_stats(sport: str, league: str, team_id: str, season: Optional[str] = None) -> Dict[str, Any]:
    return ok_envelope(
        "## Team Season Stats\n\nSeason aggregates are not consistently available via ESPN JSON for this league.",
        {"supported": False, "team_id": team_id, "season": season},
        {"league": league, "sport": sport}
    )

@server.tool(name="getPlayerSeasonStats", description="Player season stats if ESPN JSON exposes them; else supported:false. Params: sport, league, player_id, season?")
async def get_player_season_stats(sport: str, league: str, player_id: str, season: Optional[str] = None) -> Dict[str, Any]:
    return ok_envelope(
        "## Player Season Stats\n\nSeason aggregates are not reliably available via ESPN JSON for this league.",
        {"supported": False, "player_id": player_id, "season": season},
        {"league": league, "sport": sport}
    )

# -------- Probe tool to validate capability quickly --------
@server.tool(name="probeLeagueSupport", description="Probe scoreboard and one game summary for a league/date. Params: sport, league, date(YYYYMMDD)")
async def probe_league_support(sport: str, league: str, date: Optional[str] = None) -> Dict[str, Any]:
    date = date or datetime.utcnow().strftime("%Y%m%d")
    sb = await get_scoreboard(sport=sport, league=league, dates=date)
    if not sb.get("ok"):
        return sb
    events = (sb["data"].get("scoreboard") or {}).get("events", [])
    capability = {
        "scoreboard": True,
        "summary": False,
        "game_player_stats": False,
        "checked_event_id": None,
    }
    if not events:
        md = f"## Probe {sport}/{league} {date}\n\nNo events on this date."
        return ok_envelope(md, {"capability": capability}, {"league": league, "sport": sport})

    event_id = events[0].get("event_id")
    capability["checked_event_id"] = event_id
    gs = await get_game_summary(sport=sport, league=league, event_id=event_id)
    if not gs.get("ok"):
        md = f"## Probe {sport}/{league} {date}\n\nSummary failed for event {event_id}."
        return ok_envelope(md, {"capability": capability, "summary_error": gs}, {"league": league, "sport": sport})
    capability["summary"] = True

    box = ((gs.get("data") or {}).get("summary") or {}).get("boxscore") or {}
    has_players = False
    if isinstance(box.get("players"), list) and box["players"]:
        has_players = True
    if isinstance(box.get("teams"), list) and box["teams"]:
        for t in box["teams"]:
            if t.get("statistics") or t.get("players"):
                has_players = True
                break
    capability["game_player_stats"] = has_players

    md = f"## Probe {sport}/{league} {date}\n\nScoreboard ✅  Summary {'✅' if capability['summary'] else '❌'}  PlayerStats {'✅' if has_players else '❌'}"
    return ok_envelope(md, {"capability": capability}, {"league": league, "sport": sport, "event_id": event_id})

# -------- Strict analysis (no inference) --------
@server.tool(name="analyzeGameStrict", description="Summarize a game using only fetched stats. Params: sport, league, event_id, question")
async def analyze_game_strict(sport: str, league: str, event_id: str, question: str) -> Dict[str, Any]:
    gs = await get_game_summary(sport=sport, league=league, event_id=event_id)
    if not gs.get("ok"):
        return gs
    payload = {"summary": gs["data"]["summary"]}
    ok, content = await ask_openrouter(payload, f"Answer strictly from the JSON. Question: {question}")
    md = content if ok else f"OpenRouter error: {content}"
    return ok_envelope(md, payload, {"league": league, "sport": sport, "event_id": event_id})

# =========================== Entrypoint ===========================
async def amain() -> None:
    await server.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(amain())