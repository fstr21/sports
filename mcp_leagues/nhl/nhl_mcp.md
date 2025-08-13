Project layout
graphql
Copy
Edit
sports/
├─ runserver_nhl.py                    # run from ROOT (lazy-friendly)
├─ test_clients/
│  ├─ test_nhl_schedule.py
│  ├─ test_nhl_roster.py
│  ├─ test_nhl_players_lastN.py
└─ mcp-nhl/
   ├─ requirements.txt
   ├─ server.py                        # FastAPI JSON-RPC endpoint /mcp
   ├─ nhl_tools/
   │  ├─ __init__.py
   │  ├─ utils.py                      # ET helpers, column pickers
   │  ├─ schedule.py                   # getNHLScheduleET
   │  ├─ teams.py                      # getNHLTeams
   │  ├─ roster.py                     # getNHLTeamRoster
   │  └─ players.py                    # getNHLPlayerLastN
   └─ .vscode/launch.json
Requirements (mcp-nhl/requirements.txt)
makefile
Copy
Edit
fastapi==0.111.0
uvicorn[standard]==0.30.1
httpx==0.27.2
nhl-api-py==0.7.1
pandas==2.2.2
python-dateutil==2.9.0.post0
tzdata==2024.1    # Windows timezone data
nhl-api-py import name is nhlpy.

ET/time + game types
All start times from NHL endpoints are typically UTC → convert to America/New_York.

Support gameType:

1 = Preseason

2 = Regular season

3 = Playoffs

Your ET “sports day” is a plain calendar day in ET. We filter by ET date.

Tools (MCP)
1) getNHLScheduleET
Purpose: games for a given ET date, with ET start times
Args:

date (YYYY-MM-DD, optional: defaults to today ET)

game_type (int in {1,2,3}, optional; default 2)
Returns:

json
Copy
Edit
{
  "ok": true,
  "data": {
    "source": "nhlpy",
    "date_et": "YYYY-MM-DD",
    "game_type": 2,
    "count": 7,
    "games": [
      {
        "gameId": 2024020012,
        "start_et": "2024-10-10T19:00:00-04:00",
        "home": {"abbr":"TOR","name":"Maple Leafs","id":10},
        "away": {"abbr":"MTL","name":"Canadiens","id":8},
        "venue": "Scotiabank Arena",
        "status": "Scheduled"
      }
    ]
  }
}
2) getNHLTeams
Purpose: list NHL teams (id, name, abbr)
Args: none (or optional season string like 20242025)
Returns: array of {id, name, abbr, conference, division}

3) getNHLTeamRoster
Purpose: roster for a team in a season (forwards, defense, goalies)
Args: team_abbr (e.g., "TOR"), season_id (e.g., "20242025")
Returns: list of {id, firstName, lastName, fullName, position, shoots, number}

4) getNHLPlayerLastN
Purpose: last N games before a cutoff ET for one/many players; position-aware stat selection
Args:

Provide one of:

players: [{ "name":"Auston Matthews", "team_abbr":"TOR", "pos":"F|D|G"}]

player_ids: ["8479318", ...] (string IDs as NHL uses)

season_id: "20242025"

count: default 5

cutoff_iso_et: ISO string in ET; default = now ET

game_type: default 2 (regular season)
Returns: per player {player_id, position, games:[{date_et, opp_abbr, ...stats...}], aggregates}

Stat picks (simple, extendable):

F (forwards / wings / centers): goals, assists, points, shots, toi (time on ice)

D (defense): same as above (you can add blocks/hits later)

G (goalies): saves, shotsAgainst, savePct, goalsAgainst

Code skeletons (short)
runserver (root): runserver_nhl.py
python
Copy
Edit
from pathlib import Path
import sys, uvicorn

ROOT = Path(__file__).resolve().parent
NHLDIR = ROOT / "mcp-nhl"
sys.path.insert(0, str(NHLDIR))

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8012, reload=True, reload_dirs=[str(NHLDIR)])
server: mcp-nhl/server.py
python
Copy
Edit
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any

TOOLS: Dict[str, Any] = {}
from nhl_tools.schedule import register as reg_sched
from nhl_tools.teams    import register as reg_teams
from nhl_tools.roster   import register as reg_roster
from nhl_tools.players  import register as reg_players
reg_sched(TOOLS); reg_teams(TOOLS); reg_roster(TOOLS); reg_players(TOOLS)

app = FastAPI()

@app.post("/mcp")
async def mcp(req: Request):
    p = await req.json()
    rid = p.get("id")
    if p.get("method") != "tools/call":
        return JSONResponse({"jsonrpc":"2.0","id":rid,"error":{"code":-32601,"message":"Method not found"}})
    name = (p.get("params") or {}).get("name")
    args = (p.get("params") or {}).get("arguments") or {}
    tool = TOOLS.get(name)
    if not tool:
        return JSONResponse({"jsonrpc":"2.0","id":rid,"error":{"code":-32601,"message":f"Unknown tool: {name}"}})
    try:
        data = await tool["handler"](args)
        return JSONResponse({"jsonrpc":"2.0","id":rid,"result":data})
    except Exception as e:
        return JSONResponse({"jsonrpc":"2.0","id":rid,"error":{"code":-32000,"message":f"{e}"}}, status_code=500)
utils: mcp-nhl/nhl_tools/utils.py
python
Copy
Edit
from datetime import datetime, date
from zoneinfo import ZoneInfo
import pandas as pd

ET = ZoneInfo("America/New_York")

def to_et(iso_utc: str | None) -> str | None:
    if not iso_utc:
        return None
    try:
        return datetime.fromisoformat(iso_utc.replace("Z","+00:00")).astimezone(ET).isoformat()
    except Exception:
        return iso_utc

def full_name(first: dict|str, last: dict|str) -> str:
    def pick(x):
        if isinstance(x, dict):
            return x.get("default") or x.get("en") or next(iter(x.values()), "")
        return str(x or "")
    return (pick(first) + " " + pick(last)).strip()
schedule tool: mcp-nhl/nhl_tools/schedule.py
python
Copy
Edit
from typing import Dict, Any
from nhlpy import NHLClient
from .utils import to_et

client = NHLClient()

async def handle(args: Dict[str, Any]) -> Dict[str, Any]:
    date = args.get("date")  # YYYY-MM-DD
    gtype = int(args.get("game_type") or 2)
    raw = client.schedule.daily_schedule(date=date)  # NHL API returns all; we'll keep gtype if present

    games_out = []
    for g in raw.get("games", []):
        # gameType may be inside gameType or gameTypeId depending on endpoint; keep if matches or if no filter needed
        gt = g.get("gameType") or g.get("gameTypeId")
        if gtype and gt not in (gtype, str(gtype)):
            # if API doesn't include type here, you can skip filtering or add a season-level filter later
            pass
        home = g.get("homeTeam", {}) ; away = g.get("awayTeam", {})
        games_out.append({
            "gameId": g.get("id") or g.get("gamePk") or g.get("gameId"),
            "start_et": to_et(g.get("startTimeUTC") or g.get("gameDate")),
            "home": {"abbr": home.get("abbrev"), "name": home.get("name"), "id": home.get("id")},
            "away": {"abbr": away.get("abbrev"), "name": away.get("name"), "id": away.get("id")},
            "venue": (g.get("venue",{}) or {}).get("default") or g.get("venueName"),
            "status": (g.get("gameState") or g.get("status") or "Scheduled")
        })
    games_out.sort(key=lambda x: x["start_et"] or "")
    return {"ok": True, "data": {"source":"nhlpy","date_et": date,"game_type": gtype,"count": len(games_out),"games": games_out}}

def register(TOOLS): TOOLS["getNHLScheduleET"] = {"description":"NHL games for an ET day","handler": handle}
teams tool: mcp-nhl/nhl_tools/teams.py
python
Copy
Edit
from typing import Dict, Any
from nhlpy import NHLClient
client = NHLClient()

async def handle(args: Dict[str, Any]) -> Dict[str, Any]:
    t = client.teams.teams()
    teams = [{"id":x.get("id"),"name":x.get("name"),"abbr":x.get("triCode") or x.get("abbrev"),
              "conference": (x.get("conference") or {}).get("name"),
              "division": (x.get("division") or {}).get("name")} for x in t or []]
    return {"ok": True, "data": {"source":"nhlpy","count": len(teams),"teams": teams}}

def register(TOOLS): TOOLS["getNHLTeams"] = {"description":"List NHL teams","handler": handle}
roster tool: mcp-nhl/nhl_tools/roster.py
python
Copy
Edit
from typing import Dict, Any
from nhlpy import NHLClient
from .utils import full_name
client = NHLClient()

async def handle(args: Dict[str, Any]) -> Dict[str, Any]:
    abbr = str(args.get("team_abbr"))
    season = str(args.get("season_id"))  # e.g. "20242025"
    r = client.teams.team_roster(team_abbr=abbr, season=season)
    out=[]
    for group in ("forwards","defensemen","goalies"):
        for p in r.get(group, []):
            out.append({
                "id": str(p.get("id")),
                "position": group[:1].upper(),  # F/D/G
                "firstName": (p.get("firstName") or {}).get("default"),
                "lastName": (p.get("lastName") or {}).get("default"),
                "fullName": full_name(p.get("firstName"), p.get("lastName")),
                "number": p.get("sweaterNumber"),
                "shootsCatches": p.get("shootsCatches")
            })
    return {"ok": True, "data": {"source":"nhlpy","team_abbr":abbr,"season_id":season,"count":len(out),"players":out}}

def register(TOOLS): TOOLS["getNHLTeamRoster"] = {"description":"NHL team roster","handler": handle}
players last-N tool: mcp-nhl/nhl_tools/players.py
python
Copy
Edit
from typing import Dict, Any, List
from nhlpy import NHLClient
from datetime import datetime
from zoneinfo import ZoneInfo
from .utils import to_et
client = NHLClient()
ET = ZoneInfo("America/New_York")

def _resolve_ids_by_roster(players: List[dict], season: str):
    # players: [{"name":"...", "team_abbr":"TOR", "pos":"F|D|G"}]
    out, errors = {}, {}
    for p in players:
        abbr = p["team_abbr"]; name = p["name"].lower().strip()
        r = client.teams.team_roster(team_abbr=abbr, season=season)
        pid=None
        for group in ("forwards","defensemen","goalies"):
            for x in r.get(group, []):
                full = ((x.get("firstName",{}).get("default","")+" "+x.get("lastName",{}).get("default","")).strip()).lower()
                if full==name:
                    pid=str(x.get("id")); break
            if pid: break
        if pid: out[p["name"]] = {"player_id": pid, "pos": p.get("pos","F")}
        else: errors[p["name"]] = "not found on roster"
    return out, errors

async def handle(args: Dict[str, Any]) -> Dict[str, Any]:
    players  = args.get("players") or []
    player_ids = args.get("player_ids") or []
    season = str(args.get("season_id") or "20242025")
    count = int(args.get("count") or 5)
    game_type = int(args.get("game_type") or 2)
    cutoff = args.get("cutoff_iso_et")
    cutoff_dt = datetime.now(tz=ET) if not cutoff else datetime.fromisoformat(cutoff).astimezone(ET)

    name_map, errors = ({}, {})
    if players and not player_ids:
        name_map, errors = _resolve_ids_by_roster(players, season)
        player_ids = [v["player_id"] for v in name_map.values()]

    results = {}
    for pid in player_ids:
        log = client.stats.player_game_log(player_id=str(pid), season_id=season, game_type=game_type)
        games = log.get("gameLog") or log.get("gameLogInfo") or []
        # filter strictly before cutoff ET
        rows=[]
        for g in games:
            iso = g.get("gameDate") or g.get("startTimeUTC") or g.get("gameDateUTC")
            if not iso: continue
            et = datetime.fromisoformat(iso.replace("Z","+00:00")).astimezone(ET)
            if et >= cutoff_dt: continue
            rows.append({
                "date_et": et.isoformat(),
                "opp_abbr": g.get("opponentTeamAbbrev") or (g.get("opponent") or {}).get("abbrev"),
                # common stat keys (will vary; pick safe basics)
                "goals": g.get("goals") or 0,
                "assists": g.get("assists") or 0,
                "points": g.get("points") if g.get("points") is not None else ( (g.get("goals") or 0) + (g.get("assists") or 0) ),
                "shots": g.get("shots") or 0,
                "toi": g.get("timeOnIce") or g.get("toi"),
                "saves": g.get("saves") if "saves" in g else None,
                "shotsAgainst": g.get("shotsAgainst") if "shotsAgainst" in g else None,
                "savePct": g.get("savePct") if "savePct" in g else None,
                "gaa": g.get("goalsAgainstAverage") if "goalsAgainstAverage" in g else None,
            })
        rows.sort(key=lambda r: r["date_et"], reverse=True)
        rows = rows[:count]

        # aggregates (simple sums; ignore None)
        agg = {
          "goals_sum": sum((r["goals"] or 0) for r in rows),
          "assists_sum": sum((r["assists"] or 0) for r in rows),
          "points_sum": sum((r["points"] or 0) for r in rows),
          "shots_sum": sum((r["shots"] or 0) for r in rows),
          "saves_sum": sum((r["saves"] or 0) for r in rows if r["saves"] is not None),
        }

        results[str(pid)] = {"player_id": str(pid), "season_id": season, "game_type": game_type,
                             "timezone": "America/New_York", "count": len(rows),
                             "games": rows, "aggregates": agg}

    return {"ok": True, "data": {"source":"nhlpy","season_id": season,"game_type": game_type,
                                  "results": results,"errors": errors}}

def register(TOOLS): TOOLS["getNHLPlayerLastN"] = {"description":"Last N games before ET cutoff","handler": handle}
Example calls
PowerShell → /mcp
Schedule

powershell
Copy
Edit
$body = @{
  jsonrpc="2.0"; id="sched"; method="tools/call";
  params=@{ name="getNHLScheduleET"; arguments=@{ date="2024-10-10"; game_type=2 } }
} | ConvertTo-Json -Depth 5
curl http://127.0.0.1:8012/mcp -Method POST -Body $body -ContentType "application/json"
Teams

powershell
Copy
Edit
$body = @{
  jsonrpc="2.0"; id="teams"; method="tools/call";
  params=@{ name="getNHLTeams"; arguments=@{} }
} | ConvertTo-Json -Depth 4
curl http://127.0.0.1:8012/mcp -Method POST -Body $body -ContentType "application/json"
Roster

powershell
Copy
Edit
$body = @{
  jsonrpc="2.0"; id="roster"; method="tools/call";
  params=@{ name="getNHLTeamRoster"; arguments=@{ team_abbr="EDM"; season_id="20242025" } }
} | ConvertTo-Json -Depth 5
curl http://127.0.0.1:8012/mcp -Method POST -Body $body -ContentType "application/json"
Players last-N (names)

powershell
Copy
Edit
$players = @(
  @{ name="Connor McDavid"; team_abbr="EDM"; pos="F" },
  @{ name="Leon Draisaitl"; team_abbr="EDM"; pos="F" }
)
$body = @{
  jsonrpc="2.0"; id="lastN"; method="tools/call";
  params=@{ name="getNHLPlayerLastN"; arguments=@{
    players=$players; season_id="20242025"; game_type=2; count=5; cutoff_iso_et="2025-01-15T23:59:59-05:00"
  } }
} | ConvertTo-Json -Depth 6
curl http://127.0.0.1:8012/mcp -Method POST -Body $body -ContentType "application/json"
Players last-N (IDs)

powershell
Copy
Edit
$body = @{
  jsonrpc="2.0"; id="lastN"; method="tools/call";
  params=@{ name="getNHLPlayerLastN"; arguments=@{
    player_ids=@("8478402"); season_id="20242025"; game_type=2; count=5; cutoff_iso_et="2025-01-15T23:59:59-05:00"
  } }
} | ConvertTo-Json -Depth 5
curl http://127.0.0.1:8012/mcp -Method POST -Body $body -ContentType "application/json"
Tiny Python client: test_clients/test_nhl_players_lastN.py
python
Copy
Edit
import requests, json
MCP="http://127.0.0.1:8012/mcp"
players=[{"name":"Connor McDavid","team_abbr":"EDM","pos":"F"},
         {"name":"Leon Draisaitl","team_abbr":"EDM","pos":"F"}]
payload={"jsonrpc":"2.0","id":"p","method":"tools/call",
 "params":{"name":"getNHLPlayerLastN","arguments":{
   "players": players, "season_id": "20242025", "game_type": 2, "count": 5,
   "cutoff_iso_et": "2025-01-15T23:59:59-05:00"
 }}}
r=requests.post(MCP,json=payload,timeout=60); r.raise_for_status()
print(json.dumps(r.json(), indent=2))
Practical notes
Stability: nhl-api-py is a wrapper over NHL’s unofficial endpoints; schemas can change. Keep the stat keys in players.py defensive (NULL-tolerant).

Rate/Politeness: You’re mostly doing 1–3 calls per tool execution (very light). If you later batch many players, add a tiny concurrency cap/backoff.

Preseason: Set game_type=1 for PRE. The daily schedule endpoint usually returns all games for that day; we keep a game_type arg to filter logic as needed.

IDs & names: We resolve names → IDs via roster for the specific season. That’s reliable for current season; for historical seasons you might pass IDs directly.