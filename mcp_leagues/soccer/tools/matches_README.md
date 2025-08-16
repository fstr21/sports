# Soccer MCP Tool: getCompetitionMatches

## Overview
The `getCompetitionMatches` tool retrieves matches for a specific soccer competition with flexible filtering options. This is the primary tool for getting fixture lists, recent results, and upcoming matches with complete match information.

**Server URL**: `https://soccermcp-production.up.railway.app/mcp`  
**Tool Name**: `getCompetitionMatches`

---

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `competition_id` | string | Yes | - | Competition ID (e.g., "2021" for Premier League) |
| `date_from` | string | No | - | Start date in YYYY-MM-DD format |
| `date_to` | string | No | - | End date in YYYY-MM-DD format |
| `matchday` | integer | No | - | Specific matchday number |
| `status` | string | No | - | Match status filter (SCHEDULED, LIVE, FINISHED, etc.) |

---

## Usage Examples

### Get All Recent Matches (No Filters)
```python
import httpx
import json

payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
        "name": "getCompetitionMatches",
        "arguments": {
            "competition_id": "2021"  # Premier League
        }
    }
}

async with httpx.AsyncClient() as client:
    response = await client.post("https://soccermcp-production.up.railway.app/mcp", json=payload)
    result = response.json()
```

### Get Finished Matches in Date Range
```python
payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
        "name": "getCompetitionMatches",
        "arguments": {
            "competition_id": "2021",
            "date_from": "2025-08-01",
            "date_to": "2025-08-16",
            "status": "FINISHED"
        }
    }
}
```

### Get Upcoming Matches Only
```python
payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
        "name": "getCompetitionMatches",
        "arguments": {
            "competition_id": "2021",
            "status": "SCHEDULED"
        }
    }
}
```

### Get Specific Matchday
```python
payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
        "name": "getCompetitionMatches",
        "arguments": {
            "competition_id": "2021",
            "matchday": 1
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
    "content_md": "## Competition Matches\n\nFound 1 matches for competition 2021",
    "data": {
      "source": "football_data_api",
      "competition_id": "2021",
      "matches": [
        {
          "id": 537785,
          "utcDate": "2025-08-15T19:00:00Z",
          "status": "FINISHED",
          "matchday": 1,
          "stage": "REGULAR_SEASON",
          "group": null,
          "lastUpdated": "2025-08-16T00:20:48Z",
          "homeTeam": {
            "id": 64,
            "name": "Liverpool FC",
            "shortName": "Liverpool",
            "tla": "LIV",
            "crest": "https://crests.football-data.org/64.png"
          },
          "awayTeam": {
            "id": 1044,
            "name": "AFC Bournemouth",
            "shortName": "Bournemouth",
            "tla": "BOU",
            "crest": "https://crests.football-data.org/bournemouth.png"
          },
          "score": {
            "winner": "HOME_TEAM",
            "duration": "REGULAR",
            "fullTime": {
              "home": 4,
              "away": 2
            },
            "halfTime": {
              "home": 1,
              "away": 0
            }
          },
          "venue": null
        }
      ],
      "count": 1
    },
    "meta": {
      "timestamp": "2025-08-16T04:00:00.000000+00:00"
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
- `source` (string): Always "football_data_api"
- `competition_id` (string): Requested competition ID
- `count` (integer): Number of matches found
- `matches` (array): List of match objects

### Match Object
- `id` (integer): Unique match identifier
- `utcDate` (string): Match date/time in UTC (ISO 8601)
- `status` (string): Current match status
- `matchday` (integer): Matchday number in competition
- `stage` (string): Competition stage
- `group` (string): Group identifier (for group stages)
- `lastUpdated` (string): Last data update timestamp
- `homeTeam` (object): Home team information
- `awayTeam` (object): Away team information
- `score` (object): Match score information
- `venue` (string): Stadium name (when available)

### Team Object (homeTeam/awayTeam)
- `id` (integer): Team identifier
- `name` (string): Full team name
- `shortName` (string): Abbreviated team name
- `tla` (string): Three-letter abbreviation
- `crest` (string): Team logo URL

### Score Object
- `winner` (string): Match winner ("HOME_TEAM", "AWAY_TEAM", "DRAW", null)
- `duration` (string): Match duration type ("REGULAR", "EXTRA_TIME", "PENALTY_SHOOTOUT")
- `fullTime` (object): Full-time score
- `halfTime` (object): Half-time score
- `extraTime` (object): Extra-time score (when applicable)
- `penalties` (object): Penalty shootout score (when applicable)

### Score Detail Objects (fullTime/halfTime/extraTime/penalties)
- `home` (integer): Home team score
- `away` (integer): Away team score

---

## Match Status Values

| Status | Description | Use Case |
|--------|-------------|----------|
| `SCHEDULED` | Match scheduled but not started | Upcoming fixtures |
| `TIMED` | Match has confirmed start time | Confirmed fixtures |
| `IN_PLAY` | Match currently being played | Live matches |
| `PAUSED` | Match temporarily paused | Live match interruption |
| `FINISHED` | Match completed | Historical results |
| `POSTPONED` | Match postponed to later date | Fixture changes |
| `SUSPENDED` | Match suspended | Match interruption |
| `CANCELLED` | Match cancelled | Fixture cancellation |

---

## Competition Stage Values

| Stage | Description |
|-------|-------------|
| `REGULAR_SEASON` | Regular league matches |
| `GROUP_STAGE` | Group phase (tournaments) |
| `ROUND_OF_16` | Round of 16 (knockout) |
| `QUARTER_FINALS` | Quarter-final matches |
| `SEMI_FINALS` | Semi-final matches |
| `FINAL` | Final match |
| `THIRD_PLACE` | Third place playoff |

---

## Common Competition IDs

| Competition | ID | Typical Matchdays |
|-------------|----|--------------------|
| Premier League | 2021 | 1-38 |
| La Liga | 2014 | 1-38 |
| Bundesliga | 2002 | 1-34 |
| Serie A | 2019 | 1-38 |
| Ligue 1 | 2015 | 1-34 |
| Champions League | 2001 | 1-6 (group), then knockout |
| Europa League | 2146 | 1-6 (group), then knockout |

---

## Error Handling

### Missing Competition ID
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": false,
    "error": "competition_id is required"
  }
}
```

### Invalid Competition ID
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": false,
    "error": "Football-Data API error 404: Competition not found"
  }
}
```

### Invalid Date Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": false,
    "error": "Football-Data API error 400: Invalid date format"
  }
}
```

### API Rate Limit
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": false,
    "error": "Football-Data API error 429: Rate limit exceeded"
  }
}
```

---

## Testing Notes

### Verified Functionality ✅
- **Premier League matches**: Successfully retrieved Liverpool 4-2 Bournemouth
- **Date filtering**: Proper date range filtering (2025-08-01 to 2025-08-16)
- **Status filtering**: FINISHED matches properly filtered
- **Complete match data**: Full team information, scores, timestamps
- **Matchday filtering**: Specific matchday queries working
- **Multiple competitions**: Tested across Premier League, La Liga, Champions League

### Data Quality Verification
- **Liverpool 4-2 Bournemouth**: Match ID 537785, August 15, 2025
- **Score accuracy**: Full-time 4-2, half-time 1-0 verified
- **Team data**: Complete team information with crests
- **Timestamps**: UTC timestamps properly formatted
- **Status updates**: Real-time status updates (FINISHED, IN_PLAY, etc.)

---

## Integration Examples

### Get Recent Results for Analysis
```python
import httpx
import json
import asyncio
from datetime import datetime, timedelta

async def get_recent_results(competition_id: str, days_back: int = 7):
    """Get recent finished matches for betting analysis"""
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getCompetitionMatches",
            "arguments": {
                "competition_id": competition_id,
                "date_from": start_date,
                "date_to": end_date,
                "status": "FINISHED"
            }
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://soccermcp-production.up.railway.app/mcp", 
            json=payload
        )
        result = response.json()
        
        if result["result"]["ok"]:
            matches = result["result"]["data"]["matches"]
            
            print(f"Recent results ({len(matches)} matches):")
            
            total_goals = []
            high_scoring = 0
            both_teams_scored = 0
            
            for match in matches:
                home_team = match["homeTeam"]["name"]
                away_team = match["awayTeam"]["name"]
                score = match.get("score", {}).get("fullTime", {})
                
                if score and score.get("home") is not None:
                    home_goals = score["home"]
                    away_goals = score["away"]
                    total = home_goals + away_goals
                    total_goals.append(total)
                    
                    if total >= 3:
                        high_scoring += 1
                    if home_goals > 0 and away_goals > 0:
                        both_teams_scored += 1
                    
                    winner = "Draw" if home_goals == away_goals else (
                        home_team if home_goals > away_goals else away_team
                    )
                    
                    print(f"  {home_team} {home_goals}-{away_goals} {away_team} ({winner})")
            
            # Betting insights
            if total_goals:
                avg_goals = sum(total_goals) / len(total_goals)
                high_scoring_rate = (high_scoring / len(total_goals)) * 100
                btts_rate = (both_teams_scored / len(total_goals)) * 100
                
                print(f"\nBetting Insights:")
                print(f"  Average goals per game: {avg_goals:.1f}")
                print(f"  High-scoring games (3+): {high_scoring_rate:.1f}%")
                print(f"  Both teams score rate: {btts_rate:.1f}%")
        
        return matches

# Run it
asyncio.run(get_recent_results("2021"))  # Premier League
```

### Get Upcoming Fixtures
```python
async def get_upcoming_fixtures(competition_id: str, days_ahead: int = 7):
    """Get upcoming matches for betting preparation"""
    
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getCompetitionMatches",
            "arguments": {
                "competition_id": competition_id,
                "date_from": start_date,
                "date_to": end_date,
                "status": "SCHEDULED"
            }
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://soccermcp-production.up.railway.app/mcp", 
            json=payload
        )
        result = response.json()
        
        if result["result"]["ok"]:
            matches = result["result"]["data"]["matches"]
            
            print(f"Upcoming fixtures ({len(matches)} matches):")
            
            for match in matches:
                home_team = match["homeTeam"]["name"]
                away_team = match["awayTeam"]["name"]
                date = match["utcDate"][:10]
                time = match["utcDate"][11:16]
                matchday = match.get("matchday", "?")
                
                print(f"  Matchday {matchday}: {home_team} vs {away_team}")
                print(f"    Date: {date} {time} UTC")
        
        return matches

# Run it
asyncio.run(get_upcoming_fixtures("2021"))  # Premier League
```

---

## Betting Intelligence Use Cases

### Form Analysis
- **Recent results**: Last 5-10 matches for team form assessment
- **Goal patterns**: Over/Under market analysis
- **Home/away splits**: Venue-specific performance
- **Head-to-head**: Direct matchup history

### Market Preparation
- **Upcoming fixtures**: Betting opportunity identification
- **Fixture congestion**: Team fatigue analysis
- **Matchday analysis**: Specific round performance
- **Competition stage**: Tournament progression betting

### Pattern Recognition
- **High-scoring trends**: 3+ goals frequency
- **Both teams score**: Mutual goal-scoring patterns
- **Draw frequency**: 1X2 market insights
- **Score patterns**: Exact score betting data

### Live Betting
- **IN_PLAY status**: Live match identification
- **Real-time updates**: Score progression tracking
- **Match flow**: Momentum analysis opportunities

---

## Performance Notes

### Response Times
- **No filters**: 1-2 seconds (returns recent matches)
- **Date range**: 2-3 seconds (filtered results)
- **Status filter**: 1-2 seconds (status-specific)
- **Matchday filter**: 1-2 seconds (specific round)

### Data Volume
- **Full season**: 380 matches (Premier League)
- **Matchday**: 10 matches typical
- **Date range**: Variable based on period
- **Recent results**: 10-50 matches typical

---

## Summary

**Primary Use**: Soccer match data retrieval and fixture analysis  
**Reliability**: ✅ Production ready with comprehensive filtering  
**Response Time**: 1-3 seconds typical  
**Data Source**: Football-Data.org API v4 (official)  
**Flexibility**: Multiple filter combinations supported  
**Coverage**: Complete match information with scores and team data  
**Betting Focus**: Optimized for form analysis, pattern recognition, and market preparation