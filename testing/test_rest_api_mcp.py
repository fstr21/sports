#!/usr/bin/env python3
"""
Smart ESPN WNBA MCP Server with OpenRouter Integration
- Natural language interface: ask_espn(query)
- Connectivity check: test_connection()
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

# -------------------- env loading --------------------
def load_env():
    env_path = Path("C:/Users/fstr2/Desktop/sports/.env.local")
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k] = v
        print(f"✅ Loaded environment from {env_path}")
    else:
        print(f"⚠️ Environment file not found: {env_path}")

load_env()

# -------------------- config --------------------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/horizon-beta")

ESPN_SITE_BASE = "https://site.api.espn.com"
HEADERS = {
    "User-Agent": "Smart-WNBA-MCP/1.0",
    "Accept": "application/json, text/plain, */*",
}

TEAM_MAPPING = {
    "aces": "LV", "las vegas": "LV", "vegas": "LV",
    "liberty": "NY", "new york": "NY", "brooklyn": "NY",
    "storm": "SEA", "seattle": "SEA",
    "sun": "CONN", "connecticut": "CONN",
    "sky": "CHI", "chicago": "CHI",
    "fever": "IND", "indiana": "IND",
    "wings": "DAL", "dallas": "DAL",
    "dream": "ATL", "atlanta": "ATL",
    "mercury": "PHX", "phoenix": "PHX",
    "lynx": "MIN", "minnesota": "MIN",
    "sparks": "LA", "los angeles": "LA",
    "mystics": "WAS", "washington": "WAS",
}

# -------------------- clients --------------------
class OpenRouterClient:
    def __init__(self):
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not found in environment")
        self.model = OPENROUTER_MODEL
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def parse_query(self, user_query: str) -> Dict[str, Any]:
        system_prompt = (
            "You are a WNBA data query parser. Parse user requests into structured ESPN API calls.\n\n"
            "RESPOND ONLY WITH VALID JSON in this format:\n"
            "{\n"
            '  "intent": "scores|injuries|roster|team_info|news",\n'
            '  "teams": ["team_abbreviation"],\n'
            '  "players": ["player_name"],\n'
            '  "time_frame": "today|recent|season|specific_date",\n'
            '  "specific_date": "YYYY-MM-DD",\n'
            '  "additional_filters": {}\n'
            "}\n\n"
            "TEAM ABBREVIATIONS: LV, NY, SEA, CONN, CHI, IND, DAL, ATL, PHX, MIN, LA, WAS"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query},
            ],
            "max_tokens": 200,
            "temperature": 0.1,
        }

        try:
            resp = await self.client.post(
                "https://openrouter.ai/api/v1/chat/completions", json=payload
            )
            resp.raise_for_status()
            result = resp.json()
            content = result["choices"][0]["message"]["content"].strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception:
            return self._fallback_parse(user_query)

    def _fallback_parse(self, query: str) -> Dict[str, Any]:
        q = query.lower()
        if any(w in q for w in ["injury", "injured", "hurt"]):
            intent = "injuries"
        elif any(w in q for w in ["roster", "team", "players"]):
            # prefer roster/team info
            intent = "roster" if "roster" in q else "team_info"
        elif any(w in q for w in ["news", "article"]):
            intent = "news"
        else:
            intent = "scores"

        teams = []
        for name, abbr in TEAM_MAPPING.items():
            if name in q:
                teams.append(abbr)
                break

        return {
            "intent": intent,
            "teams": teams,
            "players": [],
            "time_frame": "recent",
            "specific_date": "",
            "additional_filters": {},
        }


class ESPNClient:
    def __init__(self):
        self.client = httpx.AsyncClient(headers=HEADERS, timeout=15.0)
        self._teams_cache: Optional[Dict[str, Any]] = None

    async def _get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict:
        r = await self.client.get(url, params=params)
        r.raise_for_status()
        return r.json()

    async def get_scoreboard(self, date: Optional[str] = None) -> Dict:
        url = f"{ESPN_SITE_BASE}/apis/site/v2/sports/basketball/wnba/scoreboard"
        params = {"dates": date} if date else None
        return await self._get(url, params)

    async def get_teams(self) -> Dict:
        if self._teams_cache is None:
            url = f"{ESPN_SITE_BASE}/apis/site/v2/sports/basketball/wnba/teams"
            self._teams_cache = await self._get(url)
        return self._teams_cache

    async def get_team_info(self, team_id: str) -> Dict:
        url = f"{ESPN_SITE_BASE}/apis/site/v2/sports/basketball/wnba/teams/{team_id}"
        return await self._get(url)

    async def get_injuries(self, teams: Optional[List[str]] = None) -> Dict:
        base = f"{ESPN_SITE_BASE}/apis/site/v2/sports/basketball/wnba/injuries"
        if teams:
            params = [("team", t) for t in teams]
            # httpx can take list of tuples for repeated params
            url = base
            return await self._get(url, params=dict(params))
        return await self._get(base)

    async def get_news(self) -> Dict:
        url = f"{ESPN_SITE_BASE}/apis/site/v2/sports/basketball/wnba/news"
        return await self._get(url)


# -------------------- helpers: formatters --------------------
def find_team_id(teams_data: Dict, team_abbr: str) -> Optional[str]:
    for sport in teams_data.get("sports", []):
        for league in sport.get("leagues", []):
            for t in league.get("teams", []):
                team = t.get("team") or t
                if team.get("abbreviation") == team_abbr:
                    tid = team.get("id")
                    return str(tid) if tid is not None else None
    return None

def fmt_dt(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %I:%M %p")
    except Exception:
        return iso or "TBD"

def format_scoreboard(data: Dict) -> str:
    events = data.get("events", [])
    if not events:
        return "📭 No WNBA games found"
    lines = ["🏀 WNBA Scoreboard", ""]
    for ev in events[:12]:
        name = ev.get("name", "Unknown matchup")
        status = ev.get("status", {}).get("type", {}).get("description", "Unknown")
        date = fmt_dt(ev.get("date", ""))
        lines.append(f"{name}")
        lines.append(f"📅 {date} | 📊 {status}")
        lines.append("")
    return "\n".join(lines).strip()

def format_injuries(data: Dict, teams: List[str]) -> str:
    tag = f" for {', '.join(teams)}" if teams else ""
    injuries = data.get("injuries", [])
    if not injuries:
        return f"✅ No injuries reported{tag}"
    lines = [f"🏥 WNBA Injury Report{tag}", ""]
    for inj in injuries[:12]:
        player = inj.get("athlete", {}).get("displayName", "Unknown Player")
        team = inj.get("team", {}).get("displayName", "Unknown Team")
        status = inj.get("status", "Unknown")
        detail = inj.get("details", {}).get("detail", "")
        lines.append(f"{player} ({team}) — {status}")
        if detail:
            lines.append(detail)
        lines.append("")
    return "\n".join(lines).strip()

def format_team_info(data: Dict) -> str:
    team = data.get("team", {})
    disp = team.get("displayName", "Unknown Team")
    location = team.get("location", "")
    nickname = team.get("nickname", "")
    lines = [f"🏆 {disp}", ""]
    if location or nickname:
        lines.append(f"📍 {location} {nickname}".strip())
    # roster block if present on detail (often not; roster is separate endpoint typically)
    athletes = team.get("athletes", [])
    if athletes:
        lines.append("")
        lines.append("👥 Roster:")
        for a in athletes[:18]:
            name = a.get("displayName", "Unknown")
            pos = a.get("position", {}).get("abbreviation", "")
            jersey = a.get("jersey", "")
            comp = name
            if jersey:
                comp = f"#{jersey} {comp}"
            if pos:
                comp += f" ({pos})"
            lines.append(f"• {comp}")
    return "\n".join(lines).strip()

def format_all_teams(data: Dict) -> str:
    lines = ["🏀 WNBA Teams", ""]
    for sport in data.get("sports", []):
        for league in sport.get("leagues", []):
            for t in league.get("teams", []):
                team = t.get("team") or t
                name = team.get("displayName", "Unknown")
                abbr = team.get("abbreviation", "")
                lines.append(f"• {name} ({abbr})")
    return "\n".join(lines).strip()

def format_news(data: Dict) -> str:
    arts = data.get("articles", [])
    if not arts:
        return "📰 No WNBA news available"
    lines = ["📰 Latest WNBA News", ""]
    for a in arts[:6]:
        head = a.get("headline", "No headline")
        desc = a.get("description", "")
        pub = a.get("published", "")
        try:
            if pub:
                dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                pub_fmt = dt.strftime("%b %d, %Y")
            else:
                pub_fmt = "Unknown date"
        except Exception:
            pub_fmt = pub or "Unknown date"
        lines.append(f"{head}")
        if desc:
            lines.append(desc if len(desc) <= 220 else desc[:220] + "…")
        lines.append(f"📅 {pub_fmt}")
        lines.append("")
    return "\n".join(lines).strip()

# -------------------- MCP server --------------------
mcp = FastMCP("Smart ESPN WNBA Server")

openrouter_client = OpenRouterClient()
espn_client = ESPNClient()

@mcp.tool()
async def ask_espn(query: str) -> str:
    """
    Ask natural language questions about WNBA data from ESPN.
    Examples:
    - "Show me today's WNBA scores"
    - "Any injuries for the Las Vegas Aces?"
    - "What's the Seattle Storm roster?"
    - "Latest WNBA news"
    """
    try:
        parsed = await openrouter_client.parse_query(query)
        intent = parsed.get("intent", "scores")
        teams = parsed.get("teams", [])
        timeframe = parsed.get("time_frame", "recent")
        specific_date = parsed.get("specific_date", "")

        # date handling for scoreboard
        date_str: Optional[str] = None
        if intent == "scores":
            if timeframe in ("today", "recent"):
                date_str = datetime.utcnow().strftime("%Y%m%d")
            elif timeframe == "specific_date" and specific_date:
                try:
                    dt = datetime.fromisoformat(specific_date)
                    date_str = dt.strftime("%Y%m%d")
                except Exception:
                    date_str = None

        if intent == "scores":
            data = await espn_client.get_scoreboard(date_str)
            return format_scoreboard(data)

        if intent == "injuries":
            data = await espn_client.get_injuries(teams if teams else None)
            return format_injuries(data, teams)

        if intent in ("roster", "team_info"):
            if teams:
                teams_idx = await espn_client.get_teams()
                tid = find_team_id(teams_idx, teams[0])
                if not tid:
                    return f"❌ Could not find team: {teams[0]}"
                data = await espn_client.get_team_info(tid)
                return format_team_info(data)
            else:
                data = await espn_client.get_teams()
                return format_all_teams(data)

        if intent == "news":
            data = await espn_client.get_news()
            return format_news(data)

        # default
        data = await espn_client.get_scoreboard(date_str)
        return format_scoreboard(data)

    except httpx.HTTPStatusError as e:
        return f"❌ HTTP error from ESPN/OpenRouter: {e.response.status_code}"
    except httpx.RequestError as e:
        return f"❌ Network error: {str(e)}"
    except Exception as e:
        return f"❌ Error processing query: {str(e)}"

@mcp.tool()
async def test_connection() -> str:
    """Test connectivity to OpenRouter and ESPN"""
    checks: List[str] = []
    # OpenRouter
    try:
        parsed = await openrouter_client.parse_query("Show me WNBA scores")
        if isinstance(parsed, dict) and parsed.get("intent"):
            checks.append("✅ OpenRouter connection working")
        else:
            checks.append("❌ OpenRouter parse returned unexpected format")
    except Exception as e:
        checks.append(f"❌ OpenRouter error: {str(e)}")

    # ESPN
    try:
        data = await espn_client.get_scoreboard()
        if isinstance(data, dict):
            checks.append("✅ ESPN API connection working")
        else:
            checks.append("❌ ESPN returned unexpected format")
    except httpx.HTTPStatusError as e:
        checks.append(f"❌ ESPN HTTP error: {e.response.status_code}")
    except Exception as e:
        checks.append(f"❌ ESPN error: {str(e)}")

    return "\n".join(checks)

# -------------------- entry --------------------
async def main():
    print("🏀 Starting Smart ESPN WNBA MCP Server...")
    print(f"🤖 Using OpenRouter model: {OPENROUTER_MODEL}")
    await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())