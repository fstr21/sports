import asyncio
import re
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta

import httpx
from mcp.server import FastMCP

# ESPN API endpoints
ESPN_WNBA_SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard"
ESPN_WNBA_TEAMS_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/teams"
ESPN_WNBA_BOXSCORE_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/summary"
ESPN_WNBA_SCHEDULE_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/teams/{team_id}/schedule"
ESPN_WNBA_STANDINGS_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/standings"

date_re = re.compile(r"^\d{8}$")
server = FastMCP("wnba-comprehensive")

@server.tool(
    name="getWnbaScoreboard",
    description="Get WNBA scoreboard for a specific date. Optional: dates (YYYYMMDD), limit (number)"
)
async def get_wnba_scoreboard(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get WNBA scoreboard data for a specific date"""
    args = args or {}
    dates = args.get("dates")
    limit = args.get("limit")

    qs = []
    if dates is not None:
        if not isinstance(dates, str) or not date_re.match(dates):
            raise ValueError("dates must be a string in YYYYMMDD format")
        qs.append(f"dates={dates}")

    if limit is not None:
        try:
            n = float(limit)
        except Exception:
            raise ValueError("limit must be a number")
        if not (n > 0 and n == int(n)):
            raise ValueError("limit must be a positive integer")
        qs.append(f"limit={int(n)}")

    url = ESPN_WNBA_SCOREBOARD_URL if not qs else f"{ESPN_WNBA_SCOREBOARD_URL}?{'&'.join(qs)}"

    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.get(url, headers={"user-agent": "wnba-comprehensive/1.0", "accept": "application/json"})
        res.raise_for_status()
        data = res.json()

    return {"content": [{"type": "json", "data": data}]}

@server.tool(
    name="getWnbaGameBoxScore",
    description="Get detailed box score for a specific WNBA game. Requires game_id parameter."
)
async def get_wnba_game_boxscore(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get detailed box score including all player stats for a specific game"""
    args = args or {}
    game_id = args.get("game_id")
    
    if not game_id:
        raise ValueError("game_id is required")

    url = f"{ESPN_WNBA_BOXSCORE_URL}?event={game_id}"

    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.get(url, headers={"user-agent": "wnba-comprehensive/1.0", "accept": "application/json"})
        res.raise_for_status()
        data = res.json()

    return {"content": [{"type": "json", "data": data}]}

@server.tool(
    name="getWnbaTeams",
    description="Get all WNBA teams with basic information"
)
async def get_wnba_teams(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get list of all WNBA teams"""
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.get(ESPN_WNBA_TEAMS_URL, headers={"user-agent": "wnba-comprehensive/1.0", "accept": "application/json"})
        res.raise_for_status()
        data = res.json()

    return {"content": [{"type": "json", "data": data}]}

@server.tool(
    name="getWnbaTeamSchedule",
    description="Get full season schedule for a specific WNBA team. Requires team_id parameter."
)
async def get_wnba_team_schedule(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get complete schedule for a specific team"""
    args = args or {}
    team_id = args.get("team_id")
    
    if not team_id:
        raise ValueError("team_id is required")

    url = ESPN_WNBA_SCHEDULE_URL.format(team_id=team_id)

    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.get(url, headers={"user-agent": "wnba-comprehensive/1.0", "accept": "application/json"})
        res.raise_for_status()
        data = res.json()

    return {"content": [{"type": "json", "data": data}]}

@server.tool(
    name="getWnbaStandings",
    description="Get current WNBA standings"
)
async def get_wnba_standings(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get current league standings"""
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.get(ESPN_WNBA_STANDINGS_URL, headers={"user-agent": "wnba-comprehensive/1.0", "accept": "application/json"})
        res.raise_for_status()
        data = res.json()

    return {"content": [{"type": "json", "data": data}]}

@server.tool(
    name="getWnbaUpcomingGames",
    description="Get upcoming WNBA games for the next N days. Optional: days (default 7)"
)
async def get_wnba_upcoming_games(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get upcoming games for the next several days"""
    args = args or {}
    days = args.get("days", 7)
    
    try:
        days = int(days)
    except (ValueError, TypeError):
        days = 7
    
    if days < 1 or days > 30:
        days = 7

    # Get games for the next N days
    games_data = []
    today = datetime.now()
    
    async with httpx.AsyncClient(timeout=15) as client:
        for i in range(days):
            date = today + timedelta(days=i)
            date_str = date.strftime("%Y%m%d")
            
            url = f"{ESPN_WNBA_SCOREBOARD_URL}?dates={date_str}"
            
            try:
                res = await client.get(url, headers={"user-agent": "wnba-comprehensive/1.0", "accept": "application/json"})
                res.raise_for_status()
                day_data = res.json()
                
                if day_data.get("events"):
                    games_data.append({
                        "date": date_str,
                        "games": day_data["events"]
                    })
            except Exception as e:
                # Continue if one day fails
                continue

    return {"content": [{"type": "json", "data": {"upcoming_games": games_data, "days_searched": days}}]}

async def amain():
    await server.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(amain())