awesome — here’s a clean, practical blueprint to recreate your MCP around the MLB Stats API, with a focused tool set for your props workflow. I’ll give you:

a minimal file layout

the core server + shared utils (ET-safe dates, backoff, concurrency)

tool implementations (schedule, teams, roster, player last-N)

how to call each tool (PowerShell JSON-RPC and Python)

optional add-ons (caching, rate limiting)

Project layout
graphql
Copy
Edit
players/
├─ runserver.py                 # run from ROOT (lazy-friendly)
├─ test_clients/
│  ├─ test_schedule.py
│  ├─ test_players.py
│  └─ test_roster.py
└─ mcp-local/
   ├─ requirements.txt
   ├─ server.py                 # FastAPI JSON-RPC endpoint
   ├─ mcp_tools/
   │  ├─ __init__.py
   │  ├─ utils.py               # httpx client, ET time helpers, backoff, etc.
   │  ├─ schedule.py            # getMLBScheduleET
   │  ├─ teams.py               # getMLBTeams
   │  ├─ roster.py              # getMLBTeamRoster
   │  └─ players.py             # getMLBPlayerLastN
   └─ .vscode/
      └─ launch.json
Requirements
mcp-local/requirements.txt

makefile
Copy
Edit
fastapi==0.111.0
uvicorn[standard]==0.30.1
httpx==0.27.2
python-dateutil==2.9.0.post0
tzdata==2024.1
requests==2.32.3
Root runner (so you can run from players/)
players/runserver.py

python
Copy
Edit
from pathlib import Path
import sys, uvicorn

HERE = Path(__file__).resolve().parent
MCP_DIR = HERE / "mcp-local"
sys.path.insert(0, str(MCP_DIR))

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(MCP_DIR)],
    )
Core server
mcp-local/server.py

python
Copy
Edit
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Any, Dict

# tools registry will be populated after imports
TOOLS: Dict[str, Any] = {}

# ---- import tool handlers (populate TOOLS) ----
from mcp_tools.schedule import register as register_schedule
from mcp_tools.teams import register as register_teams
from mcp_tools.roster import register as register_roster
from mcp_tools.players import register as register_players

register_schedule(TOOLS)
register_teams(TOOLS)
register_roster(TOOLS)
register_players(TOOLS)

app = FastAPI()

@app.post("/mcp")
async def mcp_endpoint(req: Request):
    payload = await req.json()
    method = payload.get("method")
    rpc_id = payload.get("id")

    if method != "tools/call":
        return JSONResponse({"jsonrpc":"2.0","id":rpc_id,
                             "error":{"code":-32601,"message":"Method not found"}})

    params = payload.get("params") or {}
    name = params.get("name")
    arguments = params.get("arguments") or {}
    tool = TOOLS.get(name)
    if not tool:
        return JSONResponse({"jsonrpc":"2.0","id":rpc_id,
                             "error":{"code":-32601,"message":f"Unknown tool: {name}"}})
    try:
        result = await tool["handler"](arguments)
        return JSONResponse({"jsonrpc":"2.0","id":rpc_id,"result":result})
    except Exception as e:
        return JSONResponse({"jsonrpc":"2.0","id":rpc_id,
                             "error":{"code":-32000,"message":f"Server error: {e}"}}, status_code=500)

@app.get("/healthz")
async def healthz():
    return {"ok": True}
Shared utilities (ET dates, httpx client, backoff)
mcp-local/mcp_tools/utils.py

python
Copy
Edit
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Any, Dict, List
import asyncio, httpx, re

ET = ZoneInfo("America/New_York")
HEADERS = {"User-Agent": "mcp-props/1.0"}

def to_et_from_api(iso_or_date: str) -> datetime:
    """
    - date-only 'YYYY-MM-DD' -> ET midnight ON that date
    - ISO with Z/offset -> convert to ET
    """
    if not iso_or_date:
        raise ValueError("empty datetime")
    s = iso_or_date.strip()
    if len(s) == 10 and s.count("-")==2:
        dt = datetime.fromisoformat(s)
        return dt.replace(tzinfo=ET)
    dt = datetime.fromisoformat(s.replace("Z","+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(ET)

async def fetch_json_with_backoff(client: httpx.AsyncClient, url: str, tries=4, timeout=20) -> Dict[str, Any]:
    delay = 0.8
    for i in range(tries):
        try:
            r = await client.get(url, timeout=timeout)
            if r.status_code < 429 and r.status_code < 500:
                return r.json()
            if r.status_code in (429,500,502,503,504) and i < tries-1:
                await asyncio.sleep(delay); delay *= 2; continue
            raise RuntimeError(f"GET {url} failed {r.status_code}: {r.text[:200]}")
        except httpx.HTTPError as e:
            if i < tries-1:
                await asyncio.sleep(delay); delay *= 2; continue
            raise RuntimeError(f"httpx error: {e}") from e

def is_intlike(v: Any) -> bool:
    return isinstance(v, int) or (isinstance(v, str) and re.fullmatch(r"-?\d+", v or "") is not None)
Tool: Schedule (ET day)
mcp-local/mcp_tools/schedule.py

python
Copy
Edit
from typing import Any, Dict, List
from .utils import ET, HEADERS, to_et_from_api
import httpx
from datetime import datetime

SCHEDULE_URL = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={ymd}"

def _shape_team_ref(t: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "teamId": (t.get("team") or {}).get("id"),
        "name": (t.get("team") or {}).get("name"),
        "abbrev": (t.get("team") or {}).get("abbreviation"),
    }

async def handle_get_mlb_schedule_et(args: Dict[str, Any]) -> Dict[str, Any]:
    now_et = datetime.now(ET)
    date_str = str(args.get("date") or now_et.strftime("%Y-%m-%d"))

    url = SCHEDULE_URL.format(ymd=date_str)
    async with httpx.AsyncClient(headers=HEADERS) as client:
        r = await client.get(url, timeout=20)
        if r.status_code >= 400:
            return {"ok": False, "error": f"schedule fetch {r.status_code}: {r.text[:180]}"}
        payload = r.json()

    dates = payload.get("dates") or []
    if not dates:
        return {"ok": True, "data": {"source":"mlb_stats_api","date_et":date_str,"games":[],"count":0}}

    games_out = []
    for g in (dates[0].get("games") or []):
        iso = g.get("gameDate") or g.get("officialDate")
        dt_et = None
        if iso:
            try: dt_et = to_et_from_api(iso)
            except: dt_et = None
        status = ((g.get("status") or {}).get("detailedState")
                  or (g.get("status") or {}).get("abstractGameState"))
        games_out.append({
            "gamePk": g.get("gamePk"),
            "start_et": dt_et.isoformat() if dt_et else None,
            "status": status,
            "home": _shape_team_ref((g.get("teams") or {}).get("home") or {}),
            "away": _shape_team_ref((g.get("teams") or {}).get("away") or {}),
            "venue": ((g.get("venue") or {}).get("name")),
        })

    games_out.sort(key=lambda x: x["start_et"] or "9999-12-31T00:00:00-04:00")
    return {"ok": True, "data": {"source":"mlb_stats_api","date_et":date_str,"games":games_out,"count":len(games_out)}}

def register(TOOLS: Dict[str, Any]):
    TOOLS["getMLBScheduleET"] = {
        "description": "List MLB games for an ET calendar day (start times normalized to ET).",
        "handler": handle_get_mlb_schedule_et,
    }
Tool: Teams (active clubs)
mcp-local/mcp_tools/teams.py

python
Copy
Edit
from typing import Any, Dict
import httpx
from datetime import datetime
from .utils import ET, HEADERS

TEAMS_URL = "https://statsapi.mlb.com/api/v1/teams?sportId=1&season={season}&activeStatus=Yes"

def _shape_team(t: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "teamId": t.get("id"),
        "name": t.get("name"),
        "teamName": t.get("teamName"),
        "abbrev": t.get("abbreviation"),
        "locationName": t.get("locationName"),
        "league": (t.get("league") or {}).get("name"),
        "division": (t.get("division") or {}).get("name"),
        "venue": (t.get("venue") or {}).get("name"),
    }

async def handle_get_mlb_teams(args: Dict[str, Any]) -> Dict[str, Any]:
    now_et = datetime.now(ET)
    season = int(args.get("season") or now_et.year)
    url = TEAMS_URL.format(season=season)

    async with httpx.AsyncClient(headers=HEADERS) as client:
        r = await client.get(url, timeout=20)
        if r.status_code >= 400:
            return {"ok": False, "error": f"teams fetch {r.status_code}: {r.text[:180]}"}
        payload = r.json()

    teams = [_shape_team(t) for t in (payload.get("teams") or []) if isinstance(t, dict)]
    teams.sort(key=lambda x: (x.get("abbrev") or ""))
    return {"ok": True, "data": {"source":"mlb_stats_api","season":season,"count":len(teams),"teams":teams}}

def register(TOOLS: Dict[str, Any]):
    TOOLS["getMLBTeams"] = {
        "description": "List active MLB teams for a season (MLB Stats API).",
        "handler": handle_get_mlb_teams,
    }
Tool: Roster (active players by team)
mcp-local/mcp_tools/roster.py

python
Copy
Edit
from typing import Any, Dict, List
import httpx
from datetime import datetime
from .utils import ET, HEADERS

ROSTER_URL = "https://statsapi.mlb.com/api/v1/teams/{teamId}/roster?season={season}"

def _shape_player(p: Dict[str, Any]) -> Dict[str, Any]:
    person = p.get("person") or {}
    position = p.get("position") or {}
    return {
        "playerId": person.get("id"),
        "fullName": person.get("fullName"),
        "primaryNumber": p.get("jerseyNumber") or person.get("primaryNumber"),
        "position": position.get("abbreviation"),
        "status": (p.get("status") or {}).get("description"),
    }

async def handle_get_mlb_team_roster(args: Dict[str, Any]) -> Dict[str, Any]:
    team_id = args.get("teamId")
    if not team_id:
        return {"ok": False, "error": "teamId is required"}

    now_et = datetime.now(ET)
    season = int(args.get("season") or now_et.year)

    async with httpx.AsyncClient(headers=HEADERS) as client:
        r = await client.get(ROSTER_URL.format(teamId=team_id, season=season), timeout=20)
        if r.status_code >= 400:
            return {"ok": False, "error": f"roster fetch {r.status_code}: {r.text[:180]}"}
        payload = r.json()

    roster = [_shape_player(p) for p in (payload.get("roster") or [])]
    return {"ok": True, "data": {"source":"mlb_stats_api","season":season,"teamId":team_id,"count":len(roster),"players":roster}}

def register(TOOLS: Dict[str, Any]):
    TOOLS["getMLBTeamRoster"] = {
        "description": "Get active team roster (player IDs, names, positions).",
        "handler": handle_get_mlb_team_roster,
    }
Tool: Player last-N (ET-safe, count configurable)
mcp-local/mcp_tools/players.py

python
Copy
Edit
from typing import Any, Dict, List
import httpx, asyncio, re
from datetime import datetime
from .utils import ET, HEADERS, to_et_from_api, fetch_json_with_backoff, is_intlike

STATS_TMPL = (
    "https://statsapi.mlb.com/api/v1/people/{pid}/stats"
    "?stats=gameLog&group={group}&season={season}&sportId=1&gameType=R"
)

def _extract_last(payload: Dict[str, Any], cutoff_et: datetime, wanted_stats: List[str], count: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    stats = payload.get("stats", [])
    splits = stats[0].get("splits", []) if stats and isinstance(stats[0], dict) else []
    for s in splits:
        stat = s.get("stat", {}) or {}
        official = (s.get("game") or {}).get("officialDate") or s.get("date")
        game_iso = (s.get("game") or {}).get("gameDate")
        try:
            et_date_dt = to_et_from_api(official) if official else to_et_from_api(game_iso)
        except Exception:
            continue
        et_time_dt = None
        if game_iso:
            try: et_time_dt = to_et_from_api(game_iso)
            except: et_time_dt = None

        if et_date_dt.date() > cutoff_et.date():
            continue

        row = {
            "et_datetime": (et_time_dt or et_date_dt).isoformat(),
            "date_et": et_date_dt.strftime("%Y-%m-%d"),
        }
        for k in wanted_stats:
            v = stat.get(k)
            row[k] = int(v) if is_intlike(v) else (None if v is None else v)
        out.append(row)

    out.sort(key=lambda x: (x["date_et"], x["et_datetime"]), reverse=True)
    return out[:count]

async def _get_player_lastN(client: httpx.AsyncClient, pid: int, season: int, group: str, cutoff_et: datetime, stats_req: List[str], count: int) -> Dict[str, Any]:
    url = STATS_TMPL.format(pid=pid, season=season, group=group)
    payload = await fetch_json_with_backoff(client, url)
    games = _extract_last(payload, cutoff_et, stats_req, count)
    aggs: Dict[str, Any] = {}
    for k in stats_req:
        vals = [g.get(k) for g in games if isinstance(g.get(k), int)]
        aggs[f"{k}_avg"] = (sum(vals)/len(vals)) if vals else 0.0
        aggs[f"{k}_sum"] = sum(vals) if vals else 0
    return {
        "player_id": pid,
        "season": season,
        "group": group,
        "timezone": "America/New_York",
        "games": games,
        "aggregates": aggs,
        "count": len(games),
    }

async def handle_get_mlb_player_lastN(args: Dict[str, Any]) -> Dict[str, Any]:
    pids = args.get("player_ids") or []
    if not isinstance(pids, list) or not pids:
        return {"ok": False, "error": "player_ids (list[int]) is required"}

    now_et = datetime.now(ET)
    season = int(args.get("season") or now_et.year)
    group = str(args.get("group") or "hitting").lower()
    if group not in ("hitting","pitching"):
        return {"ok": False, "error": "group must be 'hitting' or 'pitching'"}

    stats_req = args.get("stats") or (["hits","homeRuns"] if group=="hitting" else ["strikeOuts"])
    count = int(args.get("count") or 5)
    cutoff_arg = args.get("cutoff_iso_et")
    cutoff_et = (to_et_from_api(cutoff_arg) if cutoff_arg else now_et)

    sem = asyncio.Semaphore(int(args.get("concurrency") or 15))
    results, errors = {}, {}

    async with httpx.AsyncClient(headers=HEADERS) as client:
        async def worker(pid: int):
            async with sem:
                return await _get_player_lastN(client, int(pid), season, group, cutoff_et, stats_req, count)
        tasks = [worker(pid) for pid in pids]
        res_list = await asyncio.gather(*tasks, return_exceptions=True)

    for pid, res in zip(pids, res_list):
        if isinstance(res, Exception):
            errors[str(pid)] = str(res)
        else:
            results[str(pid)] = res

    return {
        "ok": True,
        "data": {
            "source":"mlb_stats_api",
            "timezone":"America/New_York",
            "season": season,
            "group": group,
            "requested_stats": stats_req,
            "results": results,
            "errors": errors
        },
        "meta": {"note": "ET calendar day semantics; future ET days excluded."}
    }

def register(TOOLS: Dict[str, Any]):
    TOOLS["getMLBPlayerLastN"] = {
        "description": "Fetch last N completed games (ET) for MLB players via MLB Stats API.",
        "handler": handle_get_mlb_player_lastN,
    }
How to call the tools
JSON-RPC (PowerShell / curl)
Schedule (today ET)

powershell
Copy
Edit
$body = @{
  jsonrpc="2.0"; id="sched"; method="tools/call";
  params=@{ name="getMLBScheduleET"; arguments=@{} }
} | ConvertTo-Json -Depth 5
curl http://127.0.0.1:8000/mcp -Method POST -Body $body -ContentType "application/json"
Teams (season=2025)

powershell
Copy
Edit
$body = @{
  jsonrpc="2.0"; id="teams"; method="tools/call";
  params=@{ name="getMLBTeams"; arguments=@{ season=2025 } }
} | ConvertTo-Json -Depth 5
curl http://127.0.0.1:8000/mcp -Method POST -Body $body -ContentType "application/json"
Roster (teamId=136 Mariners example)

powershell
Copy
Edit
$body = @{
  jsonrpc="2.0"; id="roster"; method="tools/call";
  params=@{ name="getMLBTeamRoster"; arguments=@{ teamId=136; season=2025 } }
} | ConvertTo-Json -Depth 5
curl http://127.0.0.1:8000/mcp -Method POST -Body $body -ContentType "application/json"
Player Last-7 (Julio Rodríguez 677594)

powershell
Copy
Edit
$body = @{
  jsonrpc="2.0"; id="julio7"; method="tools/call";
  params=@{ name="getMLBPlayerLastN"; arguments=@{
    player_ids=@(677594); season=2025;
    stats=@("hits","homeRuns"); count=7;
    cutoff_iso_et="2025-08-13T23:59:59-04:00"
  } }
} | ConvertTo-Json -Depth 6
curl http://127.0.0.1:8000/mcp -Method POST -Body $body -ContentType "application/json"
Python client examples
players/test_clients/test_schedule.py

python
Copy
Edit
import requests, json, datetime
MCP="http://127.0.0.1:8000/mcp"
payload={"jsonrpc":"2.0","id":"sched","method":"tools/call",
         "params":{"name":"getMLBScheduleET","arguments":{"date":datetime.date.today().strftime("%Y-%m-%d")}}}
r=requests.post(MCP,json=payload,timeout=60); r.raise_for_status()
print(json.dumps(r.json(), indent=2))
players/test_clients/test_players.py

python
Copy
Edit
import requests, json
MCP="http://127.0.0.1:8000/mcp"
payload={"jsonrpc":"2.0","id":"p","method":"tools/call",
 "params":{"name":"getMLBPlayerLastN","arguments":{
   "player_ids":[677594,669003,664034],
   "season":2025,"stats":["hits","homeRuns"],"count":5
 }}}
r=requests.post(MCP,json=payload,timeout=60); r.raise_for_status()
print(json.dumps(r.json(), indent=2))
players/test_clients/test_roster.py

python
Copy
Edit
import requests, json
MCP="http://127.0.0.1:8000/mcp"
payload={"jsonrpc":"2.0","id":"r","method":"tools/call",
 "params":{"name":"getMLBTeamRoster","arguments":{"teamId":136,"season":2025}}}
r=requests.post(MCP,json=payload,timeout=60); r.raise_for_status()
print(json.dumps(r.json(), indent=2))
Operational notes (for your “once/day” run)
Concurrency: already capped at 15; that’s polite.

Backoff: built into utils.

ET safety: to_et_from_api treats YYYY-MM-DD as ET-midnight on that date; filtering compares calendar dates.

Doubleheaders: both games will appear as separate rows with the same date_et.

Production pass: run getMLBScheduleET → choose ~6 players per team (via roster or your odds feed) → call getMLBPlayerLastN once for all players (180ish).

Nice-to-have add-ons (optional)
In-memory cache (for same-day repeats): wrap the fetch_json_with_backoff with a dict cache keyed by URL; TTL a few minutes.

Rate limiter: small async gate with a sleep between task completions (e.g., 50–100 ms).

Field packs: define common stat packs:
HITTING_BASIC = ["hits","homeRuns","totalBases","runsBattedIn","atBats"], etc.

If you want, I can hand you a zip-ready dump of these files next, but the snippets above are copy-paste ready. Once you paste them into this structure and run python runserver.py, you’ll have:

getMLBScheduleET

getMLBTeams

getMLBTeamRoster

getMLBPlayerLastN

…which covers your slate → players → last-N stats loop with ET correctness.