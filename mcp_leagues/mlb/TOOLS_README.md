# MLB MCP Tools Documentation

## Overview
The MLB MCP provides 4 specialized tools for accessing Major League Baseball data via the MLB Stats API. All tools return data in Eastern Time (ET) and provide comprehensive baseball statistics and schedules.

**Server URL**: `https://mlbmcp-production.up.railway.app/mcp`

---

## Tool 1: getMLBScheduleET

### Description
Get MLB games for a specific Eastern Time calendar date. Returns complete game information including teams, start times, status, and venues.

### Parameters
- `date` (optional): Date in YYYY-MM-DD format (ET timezone). Defaults to today.

### Usage Examples

#### Get Today's Schedule
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getMLBScheduleET","arguments":{}}}'
Invoke-RestMethod -Uri "https://mlbmcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

**Python:**
```python
import requests

payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
        "name": "getMLBScheduleET",
        "arguments": {}
    }
}

response = requests.post("https://mlbmcp-production.up.railway.app/mcp", json=payload)
print(response.json())
```

#### Get Specific Date
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getMLBScheduleET","arguments":{"date":"2025-08-14"}}}'
Invoke-RestMethod -Uri "https://mlbmcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

### Example Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": true,
    "content_md": "## MLB Schedule for 2025-08-13 (ET)\n\nFound 15 games",
    "data": {
      "source": "mlb_stats_api",
      "date_et": "2025-08-13",
      "count": 15,
      "games": [
        {
          "gamePk": 776759,
          "start_et": "2025-08-13T14:10:00-04:00",
          "status": "Final",
          "home": {
            "teamId": 118,
            "name": "Kansas City Royals",
            "abbrev": null
          },
          "away": {
            "teamId": 120,
            "name": "Washington Nationals",
            "abbrev": null
          },
          "venue": "Kauffman Stadium"
        }
      ]
    },
    "meta": {
      "timestamp": "2025-08-14T01:41:23.489588+00:00"
    }
  }
}
```

### Test Results ✅
- **Today's games**: Successfully retrieved 15 games with live status updates
- **Specific date**: Successfully retrieved 7 games for tomorrow
- **Off-season date**: Gracefully handled with 0 games and appropriate message
- **Time zones**: All times properly converted to Eastern Time
- **Game status**: Shows real-time status (Final, In Progress, Scheduled, Pre-Game)

---

## Tool 2: getMLBTeams

### Description
Get active MLB teams for a specific season. Returns complete team information including names, abbreviations, leagues, divisions, and venues.

### Parameters
- `season` (optional): Season year (integer). Defaults to current year.

### Usage Examples

#### Get Current Season Teams
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getMLBTeams","arguments":{}}}'
Invoke-RestMethod -Uri "https://mlbmcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

#### Get Specific Season Teams
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getMLBTeams","arguments":{"season":2024}}}'
Invoke-RestMethod -Uri "https://mlbmcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

### Example Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": true,
    "content_md": "## MLB Teams (2025)\n\nFound 30 active teams",
    "data": {
      "source": "mlb_stats_api",
      "season": 2025,
      "count": 30,
      "teams": [
        {
          "teamId": 133,
          "name": "Athletics",
          "teamName": "Athletics",
          "abbrev": "ATH",
          "locationName": "Oakland",
          "league": "American League",
          "division": "American League West",
          "venue": "Sutter Health Park"
        }
      ]
    },
    "meta": {
      "timestamp": "2025-08-14T01:41:33.589717+00:00"
    }
  }
}
```

### Test Results ✅
- **Current season**: Successfully retrieved 30 active MLB teams
- **League breakdown**: 15 American League + 15 National League teams
- **Complete data**: Team IDs, names, abbreviations, divisions, venues
- **Sorted output**: Teams sorted alphabetically by abbreviation

---

## Tool 3: getMLBTeamRoster

### Description
Get the active roster for a specific MLB team, including player names, positions, jersey numbers, and status.

### Parameters
- `teamId` (required): MLB team ID (integer)
- `season` (optional): Season year (integer). Defaults to current year.

### Usage Examples

#### Get Yankees Roster (Team ID 147)
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getMLBTeamRoster","arguments":{"teamId":147}}}'
Invoke-RestMethod -Uri "https://mlbmcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

#### Get Specific Season Roster
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getMLBTeamRoster","arguments":{"teamId":147,"season":2024}}}'
Invoke-RestMethod -Uri "https://mlbmcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

### Example Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": true,
    "content_md": "## Team Roster (Team 147, 2025)\n\nFound 26 players",
    "data": {
      "source": "mlb_stats_api",
      "season": 2025,
      "teamId": 147,
      "count": 26,
      "players": [
        {
          "playerId": 592450,
          "fullName": "Aaron Judge",
          "primaryNumber": "99",
          "position": "RF",
          "status": "Active"
        }
      ]
    },
    "meta": {
      "timestamp": "2025-08-14T01:41:41.853418+00:00"
    }
  }
}
```

### Test Results ✅
- **Yankees roster**: Successfully retrieved 26 active players
- **Complete player data**: Names, jersey numbers, positions, status
- **Star players**: Includes Aaron Judge (#99 RF), Anthony Volpe (#11 SS), Austin Wells (C)
- **All positions**: Pitchers, catchers, infielders, outfielders properly categorized

---

## Tool 4: getMLBPlayerLastN

### Description
Get the last N games statistics for specific MLB players. Supports both hitting and pitching statistics with configurable stat types and game counts.

### Parameters
- `player_ids` (required): Array of MLB player IDs (integers)
- `season` (optional): Season year (integer). Defaults to current year.
- `group` (optional): Stats group - "hitting" or "pitching". Defaults to "hitting".
- `stats` (optional): Array of stat names to retrieve. Defaults to ["hits", "homeRuns"] for hitting or ["strikeOuts"] for pitching.
- `count` (optional): Number of recent games (integer). Defaults to 5.

### Usage Examples

#### Get Last 5 Games for Multiple Players
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getMLBPlayerLastN","arguments":{"player_ids":[677594,669003],"count":5,"stats":["hits","homeRuns","atBats"]}}}'
Invoke-RestMethod -Uri "https://mlbmcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

#### Get Pitching Stats
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getMLBPlayerLastN","arguments":{"player_ids":[545361],"group":"pitching","stats":["strikeOuts","walks","hits"],"count":3}}}'
Invoke-RestMethod -Uri "https://mlbmcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

### Example Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": true,
    "content_md": "## Player Stats (Last 5 Games)\n\nProcessed 2 players",
    "data": {
      "source": "mlb_stats_api",
      "timezone": "America/New_York",
      "season": 2025,
      "group": "hitting",
      "requested_stats": ["hits", "homeRuns", "atBats"],
      "results": {
        "677594": {
          "player_id": 677594,
          "season": 2025,
          "group": "hitting",
          "timezone": "America/New_York",
          "games": [
            {
              "et_datetime": "2025-08-12T00:00:00-04:00",
              "date_et": "2025-08-12",
              "hits": 1,
              "homeRuns": 1,
              "atBats": 2
            }
          ],
          "aggregates": {
            "hits_avg": 0.80,
            "hits_sum": 4,
            "homeRuns_avg": 0.20,
            "homeRuns_sum": 1,
            "atBats_avg": 3.40,
            "atBats_sum": 17
          },
          "count": 5
        }
      },
      "errors": {}
    },
    "meta": {
      "note": "ET calendar day semantics; future ET days excluded."
    }
  }
}
```

### Available Stats

#### Hitting Stats
- `hits` - Base hits
- `homeRuns` - Home runs
- `atBats` - At bats
- `runsBattedIn` - RBIs
- `runs` - Runs scored
- `doubles` - Double hits
- `triples` - Triple hits
- `walks` - Walks (BB)
- `strikeOuts` - Strikeouts
- `stolenBases` - Stolen bases

#### Pitching Stats
- `strikeOuts` - Strikeouts recorded
- `walks` - Walks allowed (BB)
- `hits` - Hits allowed
- `runs` - Runs allowed
- `earnedRuns` - Earned runs
- `homeRuns` - Home runs allowed
- `pitchCount` - Total pitches
- `strikes` - Strikes thrown

### Test Results ✅
- **Multi-player support**: Successfully retrieved stats for multiple players simultaneously
- **Statistical aggregates**: Provides both individual games and calculated averages/totals
- **Real player data**: Aaron Judge (592450) recent games showing accurate hit/HR/RBI data
- **Flexible stats**: Supports custom stat combinations (hits, homeRuns, atBats, doubles, triples, etc.)
- **Recent games**: Shows last 10 games in reverse chronological order (most recent first)
- **Accurate statistics**: Game-by-game data matches MLB.com official records

#### Verified Game Data (Aaron Judge - Last 10 Games)
```
Game 1 (2025-08-13): 0-for-2, 0 HR, 0 2B, 0 3B, 0 RBI
Game 2 (2025-08-12): 1-for-2, 1 HR, 0 2B, 0 3B, 0 RBI  
Game 3 (2025-08-11): 1-for-4, 0 HR, 0 2B, 0 3B, 0 RBI
Game 4 (2025-08-10): 0-for-3, 0 HR, 0 2B, 0 3B, 0 RBI
Game 5 (2025-08-09): 1-for-2, 0 HR, 0 2B, 0 3B, 0 RBI
...continuing with accurate daily performance
```

#### 📝 **Known Limitation: Game Times**
Player game logs currently display `00:00:00-04:00` (midnight ET) for all games. This is a limitation of the MLB Stats API player endpoints, which provide game dates but not actual start times. The statistical data (hits, home runs, at-bats, etc.) is completely accurate. Only the game time display shows midnight instead of actual game times like 7:10 PM ET.

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

All tools return a consistent error format:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": false,
    "error": "Error description here"
  }
}
```

Common error scenarios:
- **Missing required parameters**: `teamId is required`
- **Invalid parameters**: `group must be 'hitting' or 'pitching'`
- **API failures**: `MLB API error 500: Internal server error`
- **Network issues**: `MLB API request failed: timeout`

---

## Testing

Use the provided test script to verify all tools:

```bash
python test_mlb_tools.py
```

This script tests all 4 tools with various parameters and provides formatted output for easy verification.

---

## Notes

- All times are returned in Eastern Time (America/New_York)
- The MLB Stats API is free and requires no authentication
- Player and team IDs are consistent across all MLB Stats API endpoints
- Game data includes real-time status updates
- Historical data is available for past seasons
- Concurrent requests are limited to 15 simultaneous connections for API politeness