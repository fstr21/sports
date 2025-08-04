import asyncio
import re
from typing import Any, Dict, Optional

import httpx
from mcp.server import FastMCP

ESPN_WNBA_SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard"
date_re = re.compile(r"^\d{8}$")

server = FastMCP("mcp-wnba-espn")

@server.tool(
    name="fetchWnbaScoreboard",
    description="Fetch WNBA scoreboard JSON from ESPN. Optional inputs: dates (YYYYMMDD), limit (number)."
)
async def fetch_wnba_scoreboard(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
        res = await client.get(url, headers={"user-agent": "mcp-wnba-espn/1.0", "accept": "application/json"})
        res.raise_for_status()
        data = res.json()

    return {"content": [{"type": "json", "data": data}]}

async def amain():
    await server.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(amain())