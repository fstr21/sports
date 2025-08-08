# Standalone version of sports AI functions without MCP server dependency
import asyncio
import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import httpx

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/auto")
MAX_INPUT_BYTES = int(os.getenv("MAX_INPUT_BYTES", "8000"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "700"))
REQUEST_CONNECT_TIMEOUT = float(os.getenv("REQUEST_CONNECT_TIMEOUT", "5"))
REQUEST_READ_TIMEOUT = float(os.getenv("REQUEST_READ_TIMEOUT", "15"))

ESPN_BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"
USER_AGENT = "sports-ai-analyzer/1.2"
PROMPT_VERSION = "v1.2"

# Allowed routes
ALLOWED_ROUTES: Dict[Tuple[str, str], Dict[str, str]] = {
    ("basketball", "wnba"): {
        "scoreboard": "/basketball/wnba/scoreboard",
        "teams": "/basketball/wnba/teams",
        "news": "/basketball/wnba/news",
    },
    ("basketball", "nba"): {
        "scoreboard": "/basketball/nba/scoreboard",
        "teams": "/basketball/nba/teams",
        "news": "/basketball/nba/news",
    },
    ("baseball", "mlb"): {
        "scoreboard": "/baseball/mlb/scoreboard",
        "teams": "/baseball/mlb/teams",
        "news": "/baseball/mlb/news",
    },
    ("hockey", "nhl"): {
        "scoreboard": "/hockey/nhl/scoreboard",
        "teams": "/hockey/nhl/teams", 
        "news": "/hockey/nhl/news",
    },
    ("football", "nfl"): {
        "scoreboard": "/football/nfl/scoreboard",
        "teams": "/football/nfl/teams",
        "news": "/football/nfl/news",
    },
    ("football", "college-football"): {
        "scoreboard": "/football/college-football/scoreboard",
        "teams": "/football/college-football/teams",
        "news": "/football/college-football/news",
    },
    ("basketball", "mens-college-basketball"): {
        "scoreboard": "/basketball/mens-college-basketball/scoreboard",
        "teams": "/basketball/mens-college-basketball/teams",
        "news": "/basketball/mens-college-basketball/news",
    },
    ("soccer", "usa.1"): {
        "scoreboard": "/soccer/usa.1/scoreboard",
        "teams": "/soccer/usa.1/teams",
        "news": "/soccer/usa.1/news",
    },
    ("soccer", "eng.1"): {
        "scoreboard": "/soccer/eng.1/scoreboard",
        "teams": "/soccer/eng.1/teams",
        "news": "/soccer/eng.1/news",
    },
}

def truncate_utf8(text: str) -> str:
    """Truncate text to MAX_INPUT_BYTES while preserving UTF-8 encoding"""
    if len(text.encode("utf-8")) <= MAX_INPUT_BYTES:
        return text
    
    encoded = text.encode("utf-8")
    truncated = encoded[:MAX_INPUT_BYTES]
    
    # Find the last valid UTF-8 character boundary
    while truncated and (truncated[-1] & 0x80):
        if (truncated[-1] & 0xC0) == 0xC0:
            break
        truncated = truncated[:-1]
    
    return truncated.decode("utf-8", errors="ignore")

def compute_data_age_seconds(newest_event_time_str: Optional[str]) -> Optional[int]:
    """Compute how old the data is in seconds"""
    if not newest_event_time_str:
        return None
    try:
        newest_time = datetime.fromisoformat(newest_event_time_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return int((now - newest_time).total_seconds())
    except Exception:
        return None

async def call_openrouter_chat(payload_json: str, analysis_prompt: str) -> Tuple[bool, str]:
    """Call OpenRouter API for analysis"""
    if not OPENROUTER_API_KEY:
        return False, "Missing OpenRouter API key"
    
    client = httpx.AsyncClient(
        timeout=httpx.Timeout(REQUEST_CONNECT_TIMEOUT, read=REQUEST_READ_TIMEOUT)
    )
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
        await client.aclose()
        return True, content.strip()
    except httpx.RequestError as e:
        await client.aclose()
        return False, f"OpenRouter request error: {e}"

def envelope_ok(markdown: str, games_summary: Dict[str, Any], meta_extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create successful response envelope"""
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

def envelope_error(message: str) -> Dict[str, Any]:
    """Create error response envelope"""
    return {"ok": False, "error": message}

async def fetch_espn_data(url: str) -> Tuple[bool, Any]:
    """Fetch data from ESPN API"""
    client = httpx.AsyncClient(
        timeout=httpx.Timeout(REQUEST_CONNECT_TIMEOUT, read=REQUEST_READ_TIMEOUT)
    )
    headers = {"User-Agent": USER_AGENT}
    try:
        r = await client.get(url, headers=headers)
        if r.status_code >= 400:
            await client.aclose()
            return False, f"ESPN API error {r.status_code}: {r.text[:300]}"
        data = r.json()
        await client.aclose()
        return True, data
    except httpx.RequestError as e:
        await client.aclose()
        return False, f"ESPN request error: {e}"

def summarize_games(data: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize game data"""
    events = data.get("events", [])
    summary = {
        "events": events,
        "count": len(events),
        "newest_event_time": None,
    }
    
    if events:
        # Find newest event time
        newest_time = None
        for event in events:
            event_time_str = event.get("date")
            if event_time_str:
                try:
                    event_time = datetime.fromisoformat(event_time_str.replace("Z", "+00:00"))
                    if newest_time is None or event_time > newest_time:
                        newest_time = event_time
                except Exception:
                    pass
        if newest_time:
            summary["newest_event_time"] = newest_time.isoformat()
    
    return summary

async def get_scoreboard(sport: str, league: str, dates: Optional[str] = None, limit: Optional[int] = None, week: Optional[int] = None, seasontype: Optional[int] = None) -> Dict[str, Any]:
    """Get scoreboard data"""
    route_key = (sport, league)
    if route_key not in ALLOWED_ROUTES:
        return envelope_error(f"Unsupported sport/league: {sport}/{league}")
    
    scoreboard_path = ALLOWED_ROUTES[route_key].get("scoreboard")
    if not scoreboard_path:
        return envelope_error(f"No scoreboard route for {sport}/{league}")
    
    url = ESPN_BASE_URL + scoreboard_path
    params = []
    if dates:
        params.append(f"dates={dates}")
    if limit:
        params.append(f"limit={limit}")
    if week:
        params.append(f"week={week}")
    if seasontype:
        params.append(f"seasontype={seasontype}")
    
    if params:
        url += "?" + "&".join(params)
    
    success, data = await fetch_espn_data(url)
    if not success:
        return envelope_error(str(data))
    
    games_summary = summarize_games(data)
    
    # Generate analysis
    analysis_prompt = f"Analyze these {sport} {league} games briefly. Focus on key matchups, scores, and notable events."
    success, analysis = await call_openrouter_chat(json.dumps(data, indent=2), analysis_prompt)
    
    if not success:
        analysis = f"Analysis unavailable: {analysis}"
    
    return envelope_ok(analysis, games_summary)

async def get_teams(sport: str, league: str) -> Dict[str, Any]:
    """Get team data"""
    route_key = (sport, league)
    if route_key not in ALLOWED_ROUTES:
        return envelope_error(f"Unsupported sport/league: {sport}/{league}")
    
    teams_path = ALLOWED_ROUTES[route_key].get("teams")
    if not teams_path:
        return envelope_error(f"No teams route for {sport}/{league}")
    
    url = ESPN_BASE_URL + teams_path
    
    success, data = await fetch_espn_data(url)
    if not success:
        return envelope_error(str(data))
    
    teams = data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
    teams_summary = {"events": teams, "count": len(teams)}
    
    analysis_prompt = f"List and briefly describe these {sport} {league} teams."
    success, analysis = await call_openrouter_chat(json.dumps(teams, indent=2), analysis_prompt)
    
    if not success:
        analysis = f"Analysis unavailable: {analysis}"
    
    return envelope_ok(analysis, teams_summary)

async def get_news(sport: str, league: str) -> Dict[str, Any]:
    """Get news data"""
    route_key = (sport, league)
    if route_key not in ALLOWED_ROUTES:
        return envelope_error(f"Unsupported sport/league: {sport}/{league}")
    
    news_path = ALLOWED_ROUTES[route_key].get("news")
    if not news_path:
        return envelope_error(f"No news route for {sport}/{league}")
    
    url = ESPN_BASE_URL + news_path
    
    success, data = await fetch_espn_data(url)
    if not success:
        return envelope_error(str(data))
    
    articles = data.get("articles", [])
    news_summary = {"events": articles, "count": len(articles)}
    
    analysis_prompt = f"Summarize the key news stories for {sport} {league}."
    success, analysis = await call_openrouter_chat(json.dumps(articles, indent=2), analysis_prompt)
    
    if not success:
        analysis = f"Analysis unavailable: {analysis}"
    
    return envelope_ok(analysis, news_summary)

async def analyze_wnba_games(dates: Optional[str] = None, limit: Optional[int] = None, analysis_type: str = "general", custom_prompt: Optional[str] = None) -> Dict[str, Any]:
    """Analyze WNBA games"""
    # Get WNBA scoreboard data first
    scoreboard_result = await get_scoreboard("basketball", "wnba", dates=dates, limit=limit)
    
    if not scoreboard_result.get("ok"):
        return scoreboard_result
    
    games_data = scoreboard_result.get("games", [])
    
    if custom_prompt:
        analysis_prompt = custom_prompt
    else:
        analysis_prompt = f"Provide a detailed {analysis_type} analysis of these WNBA games. Include key player performances, team strategies, and notable trends."
    
    success, analysis = await call_openrouter_chat(json.dumps(games_data, indent=2), analysis_prompt)
    
    if not success:
        analysis = f"Analysis unavailable: {analysis}"
    
    return envelope_ok(analysis, {"events": games_data, "count": len(games_data)})