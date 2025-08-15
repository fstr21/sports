# MLB MCP Tool: getMLBScheduleET

## Overview
The `getMLBScheduleET` tool retrieves MLB games for a specific Eastern Time calendar date. This is the primary tool for getting daily game schedules with complete game information including teams, start times, status, and venues.

**Server URL**: `https://mlbmcp-production.up.railway.app/mcp`  
**Tool Name**: `getMLBScheduleET`

---

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date` | string | No | Today | Date in YYYY-MM-DD format (ET timezone) |

---

## Usage Examples

### Get Today's Schedule (Default)
```python
import httpx
import json

payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
        "name": "getMLBScheduleET",
        "arguments": {}
    }
}

async with httpx.AsyncClient() as client:
    response = await client.post("https://mlbmcp-production.up.railway.app/mcp", json=payload)
    result = response.json()
```

### Get Specific Date
```python
payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
        "name": "getMLBScheduleET",
        "arguments": {
            "date": "2025-08-14"
        }
    }
}
```

---

## Response Structure

### Success Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": true,
    "content_md": "## MLB Schedule for 2025-08-14 (ET)\n\nFound 7 games",
    "data": {
      "source": "mlb_stats_api",
      "date_et": "2025-08-14",
      "count": 7,
      "games": [
        {
          "gamePk": 776123,
          "start_et": "2025-08-14T13:05:00-04:00",
          "status": "Scheduled",
          "home": {
            "teamId": 110,
            "name": "Baltimore Orioles",
            "abbrev": "BAL"
          },
          "away": {
            "teamId": 136,
            "name": "Seattle Mariners",
            "abbrev": "SEA"
          },
          "venue": "Oriole Park at Camden Yards"
        }
      ]
    },
    "meta": {
      "timestamp": "2025-08-14T15:30:00.123456+00:00"
    }
  }
}
```

### No Games Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": true,
    "content_md": "## MLB Schedule for 2025-12-25 (ET)\n\nNo games scheduled",
    "data": {
      "source": "mlb_stats_api",
      "date_et": "2025-12-25",
      "games": [],
      "count": 0
    },
    "meta": {
      "timestamp": "2025-08-14T15:30:00.123456+00:00"
    }
  }
}
```

---

## Data Fields

### Root Level
- `ok` (boolean): Success indicator
- `content_md` (string): Markdown summary of results
- `data` (object): Main data payload
- `meta` (object): Request metadata

### Data Object
- `source` (string): Always "mlb_stats_api"
- `date_et` (string): Requested date in YYYY-MM-DD format
- `count` (integer): Number of games found
- `games` (array): List of game objects

### Game Object
- `gamePk` (integer): MLB's unique game identifier
- `start_et` (string): Game start time in ISO 8601 format (ET timezone)
- `status` (string): Game status ("Scheduled", "In Progress", "Final", "Delayed", "Pre-Game")
- `home` (object): Home team information
- `away` (object): Away team information
- `venue` (string): Stadium name

### Team Object (home/away)
- `teamId` (integer): MLB's unique team identifier
- `name` (string): Full team name (e.g., "Baltimore Orioles")
- `abbrev` (string): Team abbreviation (e.g., "BAL")

---

## Game Status Values

| Status | Description |
|--------|-------------|
| `Scheduled` | Game is scheduled but not yet started |
| `Pre-Game` | Game is about to start (warm-ups, etc.) |
| `In Progress` | Game is currently being played |
| `Final` | Game has completed |
| `Delayed` | Game start delayed due to weather/other issues |

---

## Common Team IDs

| Team | ID | Team | ID |
|------|----|----- |----|
| Angels | 108 | Astros | 117 |
| Athletics | 133 | Blue Jays | 141 |
| Braves | 144 | Brewers | 158 |
| Cardinals | 138 | Cubs | 112 |
| Diamondbacks | 109 | Dodgers | 119 |
| Giants | 137 | Guardians | 114 |
| Mariners | 136 | Marlins | 146 |
| Mets | 121 | Nationals | 120 |
| Orioles | 110 | Padres | 135 |
| Phillies | 143 | Pirates | 134 |
| Rangers | 140 | Rays | 139 |
| Red Sox | 111 | Reds | 113 |
| Rockies | 115 | Royals | 118 |
| Tigers | 116 | Twins | 142 |
| White Sox | 145 | Yankees | 147 |

---

## Error Handling

### Invalid Date Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": false,
    "error": "Invalid date format. Use YYYY-MM-DD"
  }
}
```

### API Failure
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": false,
    "error": "MLB API error: Unable to fetch schedule data"
  }
}
```

---

## Testing Notes

### Verified Functionality ✅
- **Default date**: Successfully retrieves today's games
- **Explicit date**: Works with specific date parameters
- **No games**: Handles off-season dates gracefully
- **Game count**: Typically 7-15 games on active days
- **Time zones**: All times correctly converted to Eastern Time
- **Real-time updates**: Status updates reflect live game states

### Data Consistency
- Both default and explicit date calls return identical results for same date
- Game count matches actual games array length
- All games include complete team information
- Start times are properly formatted in ISO 8601 with ET timezone

---

## Integration Example

```python
import httpx
import json
import asyncio
from datetime import datetime

async def get_todays_games():
    """Get today's MLB games"""
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getMLBScheduleET",
            "arguments": {}
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://mlbmcp-production.up.railway.app/mcp", 
            json=payload
        )
        result = response.json()
        
        if result["result"]["ok"]:
            games = result["result"]["data"]["games"]
            
            print(f"Found {len(games)} games today:")
            for game in games:
                away = game["away"]["name"]
                home = game["home"]["name"]
                time = game["start_et"]
                status = game["status"]
                
                print(f"  {away} @ {home} - {time} ({status})")
        
        return games

# Run it
asyncio.run(get_todays_games())
```

---

## Summary

**Primary Use**: Daily MLB game schedule retrieval  
**Reliability**: ✅ Production ready  
**Response Time**: < 2 seconds typical  
**Data Source**: MLB Stats API (official)  
**Rate Limits**: Managed by server  
**Timezone**: Eastern Time (America/New_York)