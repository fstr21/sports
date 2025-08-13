Project layout
bash
Copy
Edit
sports/
├─ runserver.py                      # run from ROOT (lazy-friendly)
├─ test_clients/
│  ├─ test_nfl_schedule.py
│  ├─ test_nfl_roster.py
│  ├─ test_nfl_players_lastN.py
└─ mcp-nfl/
   ├─ requirements.txt
   ├─ server.py                      # FastAPI JSON-RPC endpoint
   ├─ nfl_tools/
   │  ├─ __init__.py
   │  ├─ utils.py                    # ET helpers, backoff (even if light), schema helpers
   │  ├─ schedule.py                 # getNFLScheduleET
   │  ├─ teams.py                    # getNFLTeams
   │  ├─ roster.py                   # getNFLTeamRoster (via nfl_data_py.import_rosters)
   │  └─ players.py                  # getNFLPlayerLastN (joins weekly↔schedule; ET cutoff)
   └─ .vscode/launch.json
Requirements
mcp-nfl/requirements.txt

makefile
Copy
Edit
fastapi==0.111.0
uvicorn[standard]==0.30.1
httpx==0.27.2
nfl-data-py==0.3.2
pandas==2.2.2
pyarrow==16.1.0
python-dateutil==2.9.0.post0
tzdata==2024.1
requests==2.32.3
Root runner (run from sports/)
runserver.py

python
Copy
Edit
from pathlib import Path
import sys, uvicorn

HERE = Path(__file__).resolve().parent
NFL_DIR = HERE / "mcp-nfl"
sys.path.insert(0, str(NFL_DIR))

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=8011,                 # NFL on 8011 (so it won't collide with MLB on 8000)
        reload=True,
        reload_dirs=[str(NFL_DIR)],
    )
Core server
mcp-nfl/server.py

python
Copy
Edit
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Any, Dict

TOOLS: Dict[str, Any] = {}

# Register tools
from nfl_tools.schedule import register as register_schedule
from nfl_tools.teams    import register as register_teams
from nfl_tools.roster   import register as register_roster
from nfl_tools.players  import register as register_players

register_schedule(TOOLS)
register_teams(TOOLS)
register_roster(TOOLS)
register_players(TOOLS)

app = FastAPI()

@app.post("/mcp")
async def mcp(req: Request):
    payload = await req.json()
    rpc_id = payload.get("id")
    if payload.get("method") != "tools/call":
        return JSONResponse({"jsonrpc":"2.0","id":rpc_id,
                             "error":{"code":-32601,"message":"Method not found"}})
    name = (payload.get("params") or {}).get("name")
    args = (payload.get("params") or {}).get("arguments") or {}
    tool = TOOLS.get(name)
    if not tool:
        return JSONResponse({"jsonrpc":"2.0","id":rpc_id,
                             "error":{"code":-32601,"message":f"Unknown tool: {name}"}})
    try:
        result = await tool["handler"](args)
        return JSONResponse({"jsonrpc":"2.0","id":rpc_id,"result":result})
    except Exception as e:
        return JSONResponse({"jsonrpc":"2.0","id":rpc_id,
                             "error":{"code":-32000,"message":f"Server error: {e}"}}, status_code=500)

@app.get("/healthz")
async def healthz():
    return {"ok": True}
Shared utils (ET safety + column helpers)
mcp-nfl/nfl_tools/utils.py

python
Copy
Edit
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, List, Any
import pandas as pd

ET = ZoneInfo("America/New_York")

def to_et_midnight(ymd: str) -> pd.Timestamp:
    """Treat YYYY-MM-DD as ET midnight of that calendar day."""
    ts = pd.to_datetime(ymd, errors="coerce")
    return ts.tz_localize(ET, nonexistent="NaT", ambiguous="NaT")

def normalize_schedule_dates(sched: pd.DataFrame) -> pd.DataFrame:
    """Add gameday_dt (ET tz-aware) and a sortable string, keep original columns."""
    out = sched.copy()
    out["gameday_dt"] = pd.to_datetime(out["gameday"], errors="coerce").dt.tz_localize(ET, nonexistent="NaT", ambiguous="NaT")
    out["gameday_str"] = out["gameday_dt"].dt.date.astype(str)
    return out

def pick_first_present(df: pd.DataFrame, candidates: List[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None
Tool 1: Schedule (ET calendar day)
mcp-nfl/nfl_tools/schedule.py

python
Copy
Edit
from typing import Dict, Any
import nfl_data_py as nfl
import pandas as pd
from .utils import normalize_schedule_dates

async def handle_get_nfl_schedule_et(args: Dict[str, Any]) -> Dict[str, Any]:
    # Args: { date: "YYYY-MM-DD", season?: int }  (season optional; default=year(date))
    date = str(args.get("date"))
    season = int(args.get("season") or date.split("-")[0])

    sched = nfl.import_schedules(years=[season])
    if "gameday" not in sched.columns:
        return {"ok": True, "data": {"date_et": date, "games": [], "count": 0}}

    sched = normalize_schedule_dates(sched)
    day = sched[sched["gameday_str"] == date].copy()

    games = []
    for _, g in day.iterrows():
        games.append({
            "game_id": g.get("game_id"),
            "game_type": g.get("game_type"),
            "week": g.get("week"),
            "start_et": g.get("gameday_dt").isoformat() if pd.notna(g.get("gameday_dt")) else None,
            "away_team": g.get("away_team"),
            "home_team": g.get("home_team"),
            "stadium": g.get("stadium") or g.get("location"),
        })

    games.sort(key=lambda x: x["start_et"] or "9999-12-31T00:00:00-04:00")
    return {"ok": True, "data": {"source":"nfl-data-py", "date_et": date, "season": season, "count": len(games), "games": games}}

def register(TOOLS):
    TOOLS["getNFLScheduleET"] = {
        "description": "List NFL games for an ET day via nfl-data-py schedules.",
        "handler": handle_get_nfl_schedule_et,
    }
Tool 2: Teams
mcp-nfl/nfl_tools/teams.py

python
Copy
Edit
from typing import Dict, Any
import nfl_data_py as nfl

async def handle_get_nfl_teams(args: Dict[str, Any]) -> Dict[str, Any]:
    season = int(args.get("season") or 2024)
    # nfl-data-py provides team info through schedules/rosters; we’ll derive unique teams from the season schedule
    sched = nfl.import_schedules(years=[season])
    if sched.empty:
        return {"ok": True, "data": {"season": season, "teams": [], "count": 0}}

    teams = sorted(set(sched["home_team"].dropna().astype(str))) | sorted(set(sched["away_team"].dropna().astype(str)))
    teams = sorted(set(list(sched["home_team"].dropna().astype(str)) + list(sched["away_team"].dropna().astype(str))))
    data = [{"name": t} for t in teams]
    return {"ok": True, "data": {"source":"nfl-data-py","season": season, "count": len(data), "teams": data}}

def register(TOOLS):
    TOOLS["getNFLTeams"] = {
        "description": "List NFL teams observed in the season schedule (nfl-data-py).",
        "handler": handle_get_nfl_teams,
    }
If you want official team IDs/logos, we can enrich this later from the players/teams reference tables; for now names are enough for joins.

Tool 3: Roster (active for a date / season)
mcp-nfl/nfl_tools/roster.py

python
Copy
Edit
from typing import Dict, Any
import nfl_data_py as nfl
import pandas as pd

async def handle_get_nfl_team_roster(args: Dict[str, Any]) -> Dict[str, Any]:
    team = str(args.get("team"))
    season = int(args.get("season") or 2024)

    rosters = nfl.import_rosters(years=[season])  # columns: team, season, player_id, position, player_name, ...
    if rosters.empty:
        return {"ok": True, "data": {"source":"nfl-data-py","team":team,"season":season,"players":[],"count":0}}

    sub = rosters[rosters["team"].astype(str) == team].copy()
    # Choose a minimal surface
    cols = [c for c in ["player_id","player_name","position","jersey_number","status"] if c in sub.columns]
    players = sub[cols].drop_duplicates().to_dict("records")
    return {"ok": True, "data": {"source":"nfl-data-py","team": team,"season":season,"players": players,"count": len(players)}}

def register(TOOLS):
    TOOLS["getNFLTeamRoster"] = {
        "description": "Get team roster for a season via nfl-data-py.import_rosters.",
        "handler": handle_get_nfl_team_roster,
    }
Tool 4: Player last-N (ET cutoff, position-aware stats)
mcp-nfl/nfl_tools/players.py

python
Copy
Edit
from typing import Dict, Any, List
import nfl_data_py as nfl
import pandas as pd
from .utils import normalize_schedule_dates, ET

# Position → your requested fields (canonical → candidates to match weekly schema)
STAT_CANDIDATES = {
    "QB": {
        "attempts":        ["attempts","pass_attempts","player_pass_attempts"],
        "completions":     ["completions","pass_completions","player_pass_completions"],
        "passing_yards":   ["passing_yards","pass_yards","player_pass_yds"],
        "rushing_yards":   ["rushing_yards","rush_yards","player_rush_yds"],
    },
    "RB": {
        "receiving_yards": ["receiving_yards","rec_yards","player_reception_yds"],
        "receptions":      ["receptions","rec","player_receptions"],
        "carries":         ["carries","rushing_attempts","player_rush_attempts"],
        "rushing_yards":   ["rushing_yards","rush_yards","player_rush_yds"],
    },
    "TE": {
        "receiving_yards": ["receiving_yards","rec_yards","player_reception_yds"],
        "receptions":      ["receptions","rec","player_receptions"],
        "carries":         ["carries","rushing_attempts","player_rush_attempts"],
        "rushing_yards":   ["rushing_yards","rush_yards","player_rush_yds"],
    },
    "WR": {
        "receiving_yards": ["receiving_yards","rec_yards","player_reception_yds"],
        "receptions":      ["receptions","rec","player_receptions"],
    },
}

def _resolve_name_to_ids(weekly: pd.DataFrame, names: List[str]) -> Dict[str, str | None]:
    cols = [c for c in ["player_id","player_name","player_display_name"] if c in weekly.columns]
    uniq = weekly[cols].drop_duplicates()
    uniq["__name_l"]  = uniq.get("player_name", pd.Series([""]*len(uniq))).astype(str).str.lower().str.strip()
    uniq["__dname_l"] = uniq.get("player_display_name", pd.Series([""]*len(uniq))).astype(str).str.lower().str.strip()
    out = {}
    for nm in names:
        key = nm.lower().strip()
        hit = uniq[(uniq["__name_l"] == key) | (uniq["__dname_l"] == key)]
        if hit.empty:
            # contains fallback
            hit = uniq[uniq["__name_l"].str.contains(key, na=False) | uniq["__dname_l"].str.contains(key, na=False)]
        out[nm] = (hit.iloc[0]["player_id"] if not hit.empty else None)
    return out

def _choose_cols(df: pd.DataFrame, pos: str) -> Dict[str, str | None]:
    chosen = {}
    for canon, cands in STAT_CANDIDATES[pos].items():
        chosen[canon] = next((c for c in cands if c in df.columns), None)
    return chosen

async def handle_get_nfl_player_lastN(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Args:
      players: list of {"name": str, "pos": "QB"|"RB"|"WR"|"TE"}  OR player_ids: list[str]
      season: int (default 2024)
      count: int (default 5)
      cutoff_iso_et: str (ET ISO; default now ET) — exclude games on/after this ET date
    """
    players = args.get("players") or []
    player_ids = args.get("player_ids") or []
    season = int(args.get("season") or 2024)
    count = int(args.get("count") or 5)

    cutoff_arg = args.get("cutoff_iso_et")
    cutoff_et = pd.Timestamp.now(tz=ET) if not cutoff_arg else pd.Timestamp(cutoff_arg).tz_convert(ET) if pd.Timestamp(cutoff_arg).tzinfo else pd.Timestamp(cutoff_arg).tz_localize(ET)

    weekly = nfl.import_weekly_data(years=[season]).copy()
    sched  = nfl.import_schedules(years=[season])[["game_id","season","week","gameday"]].copy()
    sched  = normalize_schedule_dates(sched)

    df = weekly.merge(sched, on=["game_id","season","week"], how="left", validate="many_to_one")

    # If only names provided, resolve to ids using weekly
    name_to_id = {}
    if players and not player_ids:
        name_to_id = _resolve_name_to_ids(weekly, [p["name"] for p in players])
        player_ids = [pid for pid in name_to_id.values() if pid]

    results, errors = {}, {}

    for p in (players or []):
        pname, ppos = p["name"], p["pos"].upper()
        pid = name_to_id.get(pname)
        if not pid:
            errors[pname] = "unresolved player name"
            continue
        sub = df[(df["player_id"] == pid) & (df["gameday_dt"].notna()) & (df["gameday_dt"] < cutoff_et)].copy()
        if sub.empty:
            results[pname] = {"player_id": pid, "games": [], "aggregates": {}, "count": 0, "timezone": "America/New_York"}
            continue
        sub = sub.sort_values(["season","week"], ascending=[False, False]).head(count)
        colmap = _choose_cols(sub, ppos)

        show_cols = ["season","week","gameday_dt","opponent_team"] + [c for c in colmap.values() if c]
        rows = sub[show_cols].to_dict("records")

        aggs = {}
        for canon, actual in colmap.items():
            if actual and pd.api.types.is_numeric_dtype(sub[actual]):
                aggs[f"{canon}_sum"] = float(sub[actual].sum())

        results[pname] = {
            "player_id": pid,
            "position": ppos,
            "timezone": "America/New_York",
            "count": len(rows),
            "games": rows,
            "aggregates": aggs,
        }

    return {"ok": True, "data": {"source":"nfl-data-py","season": season,"results": results,"errors": errors}}

def register(TOOLS):
    TOOLS["getNFLPlayerLastN"] = {
        "description": "Last N games (before ET cutoff) for players via nfl-data-py weekly + schedules.",
        "handler": handle_get_nfl_player_lastN,
    }
The selection & cutoff logic mirrors your working prototype and keeps column names flexible.

How to call the tools
PowerShell (JSON-RPC → /mcp)
Schedule (ET)

powershell
Copy
Edit
$body = @{
  jsonrpc="2.0"; id="sched"; method="tools/call";
  params=@{ name="getNFLScheduleET"; arguments=@{ date="2024-09-15"; season=2024 } }
} | ConvertTo-Json -Depth 5
curl http://127.0.0.1:8011/mcp -Method POST -Body $body -ContentType "application/json"
Teams (season)

powershell
Copy
Edit
$body = @{
  jsonrpc="2.0"; id="teams"; method="tools/call";
  params=@{ name="getNFLTeams"; arguments=@{ season=2024 } }
} | ConvertTo-Json -Depth 5
curl http://127.0.0.1:8011/mcp -Method POST -Body $body -ContentType "application/json"
Roster (by team name, e.g., "CIN")

powershell
Copy
Edit
$body = @{
  jsonrpc="2.0"; id="roster"; method="tools/call";
  params=@{ name="getNFLTeamRoster"; arguments=@{ team="CIN"; season=2024 } }
} | ConvertTo-Json -Depth 5
curl http://127.0.0.1:8011/mcp -Method POST -Body $body -ContentType "application/json"
Players last-5 (names + positions, cutoff before 2024-11-07 ET)

powershell
Copy
Edit
$players = @(
  @{ name="Joe Burrow";     pos="QB" },
  @{ name="Derrick Henry";  pos="RB" },
  @{ name="Ja'Marr Chase";  pos="WR" }
)

$body = @{
  jsonrpc="2.0"; id="lastN"; method="tools/call";
  params=@{ name="getNFLPlayerLastN"; arguments=@{
    players=$players; season=2024; count=5; cutoff_iso_et="2024-11-07T23:59:59-05:00"
  } }
} | ConvertTo-Json -Depth 6
curl http://127.0.0.1:8011/mcp -Method POST -Body $body -ContentType "application/json"
Tiny Python clients
test_clients/test_nfl_schedule.py

python
Copy
Edit
import requests, json
MCP="http://127.0.0.1:8011/mcp"
payload={"jsonrpc":"2.0","id":"sched","method":"tools/call",
         "params":{"name":"getNFLScheduleET","arguments":{"date":"2024-09-15","season":2024}}}
r=requests.post(MCP,json=payload,timeout=60); r.raise_for_status()
print(json.dumps(r.json(), indent=2))
test_clients/test_nfl_players_lastN.py

python
Copy
Edit
import requests, json
MCP="http://127.0.0.1:8011/mcp"
players=[{"name":"Joe Burrow","pos":"QB"},
         {"name":"Derrick Henry","pos":"RB"},
         {"name":"Ja'Marr Chase","pos":"WR"}]
payload={"jsonrpc":"2.0","id":"p","method":"tools/call",
 "params":{"name":"getNFLPlayerLastN","arguments":{
   "players": players, "season": 2024, "count": 5,
   "cutoff_iso_et": "2024-11-07T23:59:59-05:00"
 }}}
r=requests.post(MCP,json=payload,timeout=90); r.raise_for_status()
print(json.dumps(r.json(), indent=2))
Notes / caveats
Preseason coverage: nfl-data-py schedules may omit upcoming PRE rows for the newest season snapshot. Use regular season / past seasons for reliable stats; the tool won’t fabricate PRE if it’s absent in the dataset.

Team identifiers: Roster tool uses team as the three-letter code (e.g., CIN, BAL). If your odds feed uses names (“Bengals”), keep a small map or derive from schedules.

Column drift: Weekly schema changes over time. The STAT_CANDIDATES map keeps the tool resilient. If you see None fields, send me list(weekly.columns) and I’ll add aliases.

Performance: nfl-data-py reads Parquet/CSV locally (downloaded once). For 100–300 players/day, this is trivial. No external rate limits.