Project Layout
The project follows a structured layout that integrates NBA data into the MCP framework. Here’s how to organize it:

graphql
Copy
Edit
nba_mcp/
├── runserver.py                 # Start the server from the ROOT directory
├── test_clients/                # Contains test scripts for each tool
│   ├── test_nba_schedule.py     # Test NBA schedule endpoint
│   ├── test_nba_roster.py       # Test NBA roster endpoint
│   └── test_nba_players_lastN.py# Test player statistics endpoint
└── mcp-nba/
   ├── requirements.txt          # Project dependencies
   ├── server.py                 # FastAPI JSON-RPC endpoint for MCP
   ├── nba_tools/
   │   ├── __init__.py
   │   ├── utils.py              # Helper functions for ET conversion, backoff, etc.
   │   ├── schedule.py           # NBA schedule tool
   │   ├── teams.py              # NBA teams tool
   │   ├── roster.py             # NBA team roster tool
   │   └── players.py            # NBA player statistics tool
   └── .vscode/
      └── launch.json            # VSCode configuration for debugging
Installation Requirements
Create a requirements.txt for necessary dependencies:

bash
Copy
Edit
fastapi==0.111.0
uvicorn[standard]==0.30.1
httpx==0.27.2
pandas==2.2.2
python-dateutil==2.9.0.post0
tzdata==2024.1
requests==2.32.3
nba_api==1.1.11  # NBA API to fetch game stats
Tools
1) NBA Schedule Tool (getNBAScheduleET)
The NBA schedule tool allows you to get the schedule for NBA games on a specific ET date.

Arguments
date (YYYY-MM-DD): The date for which you want the NBA games scheduled (defaults to today).

season: The season (e.g., "2024-25"). This is optional; it defaults to the current year.

game_type: Integer indicating the type of game (1 = Preseason, 2 = Regular season, 3 = Playoffs). Default is 2.

Example Call
python
Copy
Edit
import requests
import datetime

MCP = "http://127.0.0.1:8000/mcp"
payload = {
    "jsonrpc": "2.0",
    "id": "sched",
    "method": "tools/call",
    "params": {
        "name": "getNBAScheduleET",
        "arguments": {
            "date": datetime.date.today().strftime("%Y-%m-%d")
        }
    }
}

response = requests.post(MCP, json=payload)
print(response.json())
2) NBA Teams Tool (getNBATeams)
Fetches the list of active NBA teams, including their abbreviations and conference/division.

Arguments
season: The season year to get the teams for (e.g., "2024-25"). If not provided, it defaults to the current season.

Example Call
python
Copy
Edit
import requests

MCP = "http://127.0.0.1:8000/mcp"
payload = {
    "jsonrpc": "2.0",
    "id": "teams",
    "method": "tools/call",
    "params": {
        "name": "getNBATeams",
        "arguments": {
            "season": "2024-25"
        }
    }
}

response = requests.post(MCP, json=payload)
print(response.json())
3) NBA Team Roster Tool (getNBATeamRoster)
Retrieves the roster for a specific team, showing players' positions and other relevant details.

Arguments
team_abbr: The team's abbreviation (e.g., "LAL" for Los Angeles Lakers).

season: The season year to fetch the roster for.

Example Call
python
Copy
Edit
import requests

MCP = "http://127.0.0.1:8000/mcp"
payload = {
    "jsonrpc": "2.0",
    "id": "roster",
    "method": "tools/call",
    "params": {
        "name": "getNBATeamRoster",
        "arguments": {
            "team_abbr": "LAL",
            "season": "2024-25"
        }
    }
}

response = requests.post(MCP, json=payload)
print(response.json())
4) NBA Player Last-N Stats Tool (getNBAPlayerLastN)
This tool fetches the last N completed games for a list of players, including relevant stats.

Arguments
players: A list of player names or player IDs.

season: The season year to fetch stats for.

count: The number of last games to fetch (default is 5).

cutoff_iso_et: The cutoff time in ET for the games to consider (optional).

game_type: Type of game (1 for Preseason, 2 for Regular season, 3 for Playoffs). Default is 2.

Example Call
python
Copy
Edit
import requests

players = [{"name": "LeBron James", "team_abbr": "LAL", "pos": "F"}]
MCP = "http://127.0.0.1:8000/mcp"
payload = {
    "jsonrpc": "2.0",
    "id": "lastN",
    "method": "tools/call",
    "params": {
        "name": "getNBAPlayerLastN",
        "arguments": {
            "players": players,
            "season": "2024-25",
            "count": 5,
            "cutoff_iso_et": "2024-11-07T23:59:59-04:00"
        }
    }
}

response = requests.post(MCP, json=payload)
print(response.json())
How to Integrate the NBA Data
1) Fetching the Schedule
You can use the getNBAScheduleET tool to fetch NBA games for a given day. This is useful for applications where you need to know the scheduled games for a specific date.

2) Retrieving Teams Data
Use the getNBATeams tool to get information about the teams in a particular season. This can be used for filtering or analyzing data by team.

3) Retrieving Roster Information
With getNBATeamRoster, you can fetch a team's roster for a given season, which is helpful when you need detailed information about a team’s players.

4) Player Stats
The getNBAPlayerLastN tool provides the last N games' stats for specific players, which can be useful for fantasy sports apps, performance tracking, or historical analysis.

Final Remarks
Once the tools are integrated, you can easily query the NBA data based on your needs (e.g., finding schedules, teams, rosters, player stats). The structure allows for flexibility and scalability as more tools or data sources become available.

Let me know if you'd like me to adjust anything in this draft!








You said:
you didnt do a server.pyu


ChatGPT said:
Thanks for the reminder! Below is the server.py file for the NBA MCP integration. This FastAPI server will expose the NBA tools we’ve discussed through a JSON-RPC interface:

python
Copy
Edit
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Any, Dict

# Register NBA tools here
TOOLS: Dict[str, Any] = {}

# Import tools
from nba_tools.schedule import register as register_schedule
from nba_tools.teams import register as register_teams
from nba_tools.roster import register as register_roster
from nba_tools.players import register as register_players

# Register tools in the TOOLS dictionary
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
        return JSONResponse({"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32601, "message": "Method not found"}})

    params = payload.get("params") or {}
    name = params.get("name")
    arguments = params.get("arguments") or {}
    tool = TOOLS.get(name)
    if not tool:
        return JSONResponse({"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32601, "message": f"Unknown tool: {name}"}})

    try:
        result = await tool["handler"](arguments)
        return JSONResponse({"jsonrpc": "2.0", "id": rpc_id, "result": result})
    except Exception as e:
        return JSONResponse({"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32000, "message": f"Server error: {e}"}}, status_code=500)

@app.get("/healthz")
async def healthz():
    return {"ok": True}
Explanation:
FastAPI: This is used to serve the API with a simple POST endpoint /mcp that listens for JSON-RPC requests.

Tools Registration: The NBA tools (schedule, teams, roster, players) are imported and registered. These tools contain the logic for handling requests related to NBA data.

POST /mcp: This endpoint listens for incoming JSON-RPC requests, processes them, and invokes the appropriate NBA tool handler function.

GET /healthz: A simple health check endpoint to verify the server is running correctly.

To run the server, just execute the runserver.py script in your nba_mcp directory. Make sure all dependencies (e.g., FastAPI, httpx, nba_api) are installed, and your server should be up and running at http://127.0.0.1:8000.

Running the Server
Install dependencies from requirements.txt:

bash
Copy
Edit
pip install -r requirements.txt
Run the FastAPI server:

bash
Copy
Edit
python server.py