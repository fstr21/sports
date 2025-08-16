# Soccer MCP Tools Documentation

## Overview
The Soccer MCP provides 7 specialized tools for accessing soccer/football data via the Football-Data.org API v4. All tools return comprehensive soccer analytics for major European leagues and international competitions.

**Server URL**: `https://soccermcp-production.up.railway.app/mcp`

---

## Tool 1: getCompetitions

### Description
Get available soccer competitions from Football-Data.org. Returns comprehensive competition information including leagues, cups, and international tournaments.

### Parameters
- `areas` (optional): Comma-separated area IDs to filter by specific countries/regions

### Usage Examples

#### Get All Available Competitions
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getCompetitions","arguments":{}}}'
Invoke-RestMethod -Uri "https://soccermcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

**Python:**
```python
import requests

payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
        "name": "getCompetitions",
        "arguments": {}
    }
}

response = requests.post("https://soccermcp-production.up.railway.app/mcp", json=payload)
print(response.json())
```

#### Filter by Area (England)
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getCompetitions","arguments":{"areas":"2072"}}}'
Invoke-RestMethod -Uri "https://soccermcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

### Example Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": true,
    "content_md": "## Available Soccer Competitions\n\nFound 13 competitions",
    "data": {
      "source": "football_data_api",
      "competitions": [
        {
          "id": 2021,
          "name": "Premier League",
          "code": "PL",
          "type": "LEAGUE",
          "emblem": "https://crests.football-data.org/PL.png",
          "area": {
            "id": 2072,
            "name": "England",
            "code": "ENG",
            "flag": "https://crests.football-data.org/770.svg"
          }
        }
      ],
      "count": 13
    },
    "meta": {
      "timestamp": "2025-08-16T04:00:00.000000+00:00"
    }
  }
}
```

### Test Results ✅
- **Total competitions**: Successfully retrieved 13 available competitions
- **Major leagues**: Premier League, La Liga, Bundesliga, Serie A, Ligue 1
- **International**: UEFA Champions League, Europa League, European Championship
- **Competition types**: LEAGUE, CUP, PLAYOFFS properly categorized

---

## Tool 2: getCompetitionMatches

### Description
Get matches for a specific competition with flexible filtering options. Supports date ranges, match status filtering, and matchday-specific queries.

### Parameters
- `competition_id` (required): Competition ID (e.g., "2021" for Premier League)
- `date_from` (optional): Start date in YYYY-MM-DD format
- `date_to` (optional): End date in YYYY-MM-DD format
- `matchday` (optional): Specific matchday number
- `status` (optional): Match status (SCHEDULED, LIVE, FINISHED, etc.)

### Usage Examples

#### Get Recent Finished Matches
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getCompetitionMatches","arguments":{"competition_id":"2021","date_from":"2025-08-01","date_to":"2025-08-16","status":"FINISHED"}}}'
Invoke-RestMethod -Uri "https://soccermcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

#### Get Upcoming Matches
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getCompetitionMatches","arguments":{"competition_id":"2021","status":"SCHEDULED"}}}'
Invoke-RestMethod -Uri "https://soccermcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

### Example Response
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
            "fullTime": {"home": 4, "away": 2},
            "halfTime": {"home": 1, "away": 0}
          }
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

### Match Status Values

| Status | Description |
|--------|-------------|
| `SCHEDULED` | Match is scheduled but not yet started |
| `TIMED` | Match has confirmed start time |
| `IN_PLAY` | Match is currently being played |
| `PAUSED` | Match temporarily paused |
| `FINISHED` | Match has completed |
| `POSTPONED` | Match postponed to later date |
| `SUSPENDED` | Match suspended |
| `CANCELLED` | Match cancelled |

### Test Results ✅
- **Recent matches**: Successfully retrieved Liverpool 4-2 Bournemouth
- **Complete data**: Full team information, scores, timestamps
- **Status filtering**: FINISHED matches properly filtered
- **Date ranges**: Flexible date filtering working correctly

---

## Tool 3: getCompetitionStandings

### Description
Get current league standings/table for a specific competition. Provides comprehensive team performance metrics including points, goals, and form data.

### Parameters
- `competition_id` (required): Competition ID (e.g., "2021" for Premier League)
- `season` (optional): Season year (e.g., 2025)
- `matchday` (optional): Specific matchday for historical standings

### Usage Examples

#### Get Current Premier League Table
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getCompetitionStandings","arguments":{"competition_id":"2021"}}}'
Invoke-RestMethod -Uri "https://soccermcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

#### Get Specific Season Standings
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getCompetitionStandings","arguments":{"competition_id":"2021","season":2024}}}'
Invoke-RestMethod -Uri "https://soccermcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

### Example Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": true,
    "content_md": "## Competition Standings\n\nStandings for competition 2021",
    "data": {
      "source": "football_data_api",
      "competition_id": "2021",
      "standings": {
        "stage": "REGULAR_SEASON",
        "type": "TOTAL",
        "group": null,
        "table": [
          {
            "position": 1,
            "team": {
              "id": 64,
              "name": "Liverpool FC",
              "shortName": "Liverpool",
              "tla": "LIV",
              "crest": "https://crests.football-data.org/64.png"
            },
            "playedGames": 1,
            "form": null,
            "won": 1,
            "draw": 0,
            "lost": 0,
            "points": 3,
            "goalsFor": 4,
            "goalsAgainst": 2,
            "goalDifference": 2
          }
        ]
      }
    },
    "meta": {
      "timestamp": "2025-08-16T04:00:00.000000+00:00"
    }
  }
}
```

### Standings Data Fields

#### Team Performance Metrics
- `position` (integer): Current league position
- `playedGames` (integer): Total games played
- `won` (integer): Games won
- `draw` (integer): Games drawn
- `lost` (integer): Games lost
- `points` (integer): Total points (3 for win, 1 for draw)
- `goalsFor` (integer): Goals scored
- `goalsAgainst` (integer): Goals conceded
- `goalDifference` (integer): Goal difference (GF - GA)
- `form` (string): Recent form pattern (W/D/L)

### Test Results ✅
- **Liverpool top**: 1st position with 3 points from 1 game
- **Complete metrics**: All performance data available
- **Goal data**: 4 goals for, 2 against, +2 difference
- **20 teams**: Full Premier League table structure

---

## Tool 4: getCompetitionTeams

### Description
Get all teams participating in a specific competition. Returns comprehensive team information including names, crests, and venue details.

### Parameters
- `competition_id` (required): Competition ID (e.g., "2021" for Premier League)
- `season` (optional): Season year (e.g., 2025)

### Usage Examples

#### Get Premier League Teams
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getCompetitionTeams","arguments":{"competition_id":"2021"}}}'
Invoke-RestMethod -Uri "https://soccermcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

### Example Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": true,
    "content_md": "## Competition Teams\n\nFound 20 teams in competition 2021",
    "data": {
      "source": "football_data_api",
      "competition_id": "2021",
      "teams": [
        {
          "id": 57,
          "name": "Arsenal FC",
          "shortName": "Arsenal",
          "tla": "ARS",
          "crest": "https://crests.football-data.org/57.png",
          "address": "75 Drayton Park London N5 1BU",
          "website": "http://www.arsenal.com",
          "founded": 1886,
          "clubColors": "Red / White",
          "venue": "Emirates Stadium"
        }
      ],
      "count": 20
    },
    "meta": {
      "timestamp": "2025-08-16T04:00:00.000000+00:00"
    }
  }
}
```

### Team Data Fields
- `id` (integer): Unique team identifier
- `name` (string): Full team name
- `shortName` (string): Abbreviated team name
- `tla` (string): Three-letter abbreviation
- `crest` (string): Team logo URL
- `address` (string): Team address
- `website` (string): Official website
- `founded` (integer): Year founded
- `clubColors` (string): Team colors
- `venue` (string): Home stadium name

### Test Results ✅
- **20 teams**: Complete Premier League team list
- **Full metadata**: Names, crests, venues, founding dates
- **Arsenal example**: Complete team information available

---

## Tool 5: getTeamMatches

### Description
Get matches for a specific team with flexible filtering options. Supports date ranges, venue filtering, and competition-specific queries.

### Parameters
- `team_id` (required): Team ID (integer)
- `date_from` (optional): Start date in YYYY-MM-DD format
- `date_to` (optional): End date in YYYY-MM-DD format
- `season` (optional): Season year
- `status` (optional): Match status filter
- `venue` (optional): HOME or AWAY filter
- `limit` (optional): Maximum number of matches to return

### Usage Examples

#### Get Team's Recent Matches
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getTeamMatches","arguments":{"team_id":64,"date_from":"2025-08-01","date_to":"2025-08-16"}}}'
Invoke-RestMethod -Uri "https://soccermcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

#### Get Home Matches Only
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getTeamMatches","arguments":{"team_id":64,"venue":"HOME","limit":10}}}'
Invoke-RestMethod -Uri "https://soccermcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

### Example Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": true,
    "content_md": "## Team Matches\n\nFound 1 matches for team 64",
    "data": {
      "source": "football_data_api",
      "team_id": 64,
      "matches": [
        {
          "id": 537785,
          "utcDate": "2025-08-15T19:00:00Z",
          "status": "FINISHED",
          "homeTeam": {
            "id": 64,
            "name": "Liverpool FC"
          },
          "awayTeam": {
            "id": 1044,
            "name": "AFC Bournemouth"
          },
          "score": {
            "winner": "HOME_TEAM",
            "fullTime": {"home": 4, "away": 2},
            "halfTime": {"home": 1, "away": 0}
          }
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

### Test Results ✅
- **Liverpool matches**: Successfully retrieved team-specific fixtures
- **Date filtering**: Proper date range filtering
- **Complete match data**: Scores, opponents, timestamps

---

## Tool 6: getMatchDetails

### Description
Get comprehensive details for a specific match. Provides complete match information including scores, officials, and available statistics.

### Parameters
- `match_id` (required): Match ID (integer)

### Usage Examples

#### Get Match Details
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getMatchDetails","arguments":{"match_id":537785}}}'
Invoke-RestMethod -Uri "https://soccermcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

### Example Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": true,
    "content_md": "## Match Details\n\nDetails for match 537785 with full statistics",
    "data": {
      "source": "football_data_api",
      "match": {
        "id": 537785,
        "utcDate": "2025-08-15T19:00:00Z",
        "status": "FINISHED",
        "matchday": 1,
        "stage": "REGULAR_SEASON",
        "homeTeam": {
          "id": 64,
          "name": "Liverpool FC",
          "shortName": "Liverpool",
          "tla": "LIV"
        },
        "awayTeam": {
          "id": 1044,
          "name": "AFC Bournemouth",
          "shortName": "Bournemouth",
          "tla": "BOU"
        },
        "score": {
          "winner": "HOME_TEAM",
          "duration": "REGULAR",
          "fullTime": {"home": 4, "away": 2},
          "halfTime": {"home": 1, "away": 0}
        },
        "referees": [
          {
            "id": 11580,
            "name": "Anthony Taylor",
            "type": "REFEREE",
            "nationality": "England"
          }
        ]
      }
    },
    "meta": {
      "timestamp": "2025-08-16T04:00:00.000000+00:00"
    }
  }
}
```

### Available Match Data
- **Basic Info**: Teams, date, status, matchday
- **Scores**: Full-time and half-time scores
- **Officials**: Referee information
- **Competition Context**: League, season, stage

### Data Limitations ⚠️
**Not Available on Free Tier**:
- Detailed match statistics (shots, corners, possession)
- Player-level performance data
- Card and booking information
- Lineup and substitution details

### Test Results ✅
- **Liverpool 4-2 Bournemouth**: Complete match information
- **Referee data**: Anthony Taylor (England) officiating
- **Score details**: Full-time and half-time scores available
- **Competition context**: Premier League matchday 1

---

## Tool 7: getTopScorers

### Description
Get top goalscorers for a specific competition. Returns player names, teams, and goal counts for leading scorers.

### Parameters
- `competition_id` (required): Competition ID (e.g., "2021" for Premier League)
- `season` (optional): Season year
- `limit` (optional): Number of top scorers to return (default: 10)

### Usage Examples

#### Get Top 10 Premier League Scorers
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getTopScorers","arguments":{"competition_id":"2021","limit":10}}}'
Invoke-RestMethod -Uri "https://soccermcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

#### Get Top 5 Scorers
**PowerShell:**
```powershell
$body = '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"getTopScorers","arguments":{"competition_id":"2021","limit":5}}}'
Invoke-RestMethod -Uri "https://soccermcp-production.up.railway.app/mcp" -Method POST -Body $body -ContentType "application/json"
```

### Example Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": true,
    "content_md": "## Top Scorers\n\nFound 5 top scorers for competition 2021",
    "data": {
      "source": "football_data_api",
      "competition_id": "2021",
      "scorers": [
        {
          "player": {
            "id": 123456,
            "name": "Antoine Semenyo",
            "position": "Centre-Forward",
            "dateOfBirth": "2000-01-07",
            "nationality": "Ghana"
          },
          "team": {
            "id": 1044,
            "name": "AFC Bournemouth",
            "shortName": "Bournemouth",
            "tla": "BOU",
            "crest": "https://crests.football-data.org/bournemouth.png"
          },
          "goals": 2
        }
      ],
      "count": 5
    },
    "meta": {
      "timestamp": "2025-08-16T04:00:00.000000+00:00"
    }
  }
}
```

### Scorer Data Fields
- `player` (object): Player information
  - `id` (integer): Player ID
  - `name` (string): Player name
  - `position` (string): Playing position
  - `dateOfBirth` (string): Birth date
  - `nationality` (string): Player nationality
- `team` (object): Team information
- `goals` (integer): Total goals scored

### Test Results ✅
- **Antoine Semenyo**: Leading with 2 goals for Bournemouth
- **Complete player data**: Names, positions, nationalities
- **Team affiliations**: Full team information included
- **Goal counts**: Accurate scoring tallies

---

## Common Competition IDs

| Competition | ID | Type |
|-------------|----|----- |
| Premier League (England) | 2021 | LEAGUE |
| La Liga (Spain) | 2014 | LEAGUE |
| Bundesliga (Germany) | 2002 | LEAGUE |
| Serie A (Italy) | 2019 | LEAGUE |
| Ligue 1 (France) | 2015 | LEAGUE |
| UEFA Champions League | 2001 | CUP |
| UEFA Europa League | 2146 | CUP |
| European Championship | 2018 | CUP |
| Championship (England) | 2016 | LEAGUE |
| Eredivisie (Netherlands) | 2003 | LEAGUE |

---

## Common Team IDs (Premier League)

| Team | ID | Team | ID |
|------|----|----- |----|
| Arsenal | 57 | Aston Villa | 58 |
| Brighton | 397 | Burnley | 328 |
| Chelsea | 61 | Crystal Palace | 354 |
| Everton | 62 | Fulham | 63 |
| Liverpool | 64 | Luton Town | 389 |
| Manchester City | 65 | Manchester United | 66 |
| Newcastle | 67 | Nottingham Forest | 351 |
| Sheffield United | 356 | Tottenham | 73 |
| West Ham | 563 | Wolves | 76 |
| AFC Bournemouth | 1044 | Brentford | 402 |

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
- **Missing required parameters**: `competition_id is required`
- **Invalid parameters**: `Invalid competition ID`
- **API failures**: `Football-Data API error 429: Rate limit exceeded`
- **Network issues**: `Football-Data API request failed: timeout`
- **Authentication**: `FOOTBALL_DATA_API_KEY not configured`

---

## Data Quality & Limitations

### ✅ **Available Data (High Quality)**
- **Competition information**: Complete league and tournament data
- **Match results**: Accurate scores and timestamps
- **League standings**: Real-time team performance metrics
- **Team information**: Comprehensive team metadata
- **Top scorers**: Current goal-scoring leaders
- **Match schedules**: Upcoming fixtures and dates

### ⚠️ **Limited Data (Free Tier Restrictions)**
- **Match statistics**: No shots, corners, possession data
- **Player performance**: No individual match statistics
- **Tactical data**: No formation or tactical information
- **Injury reports**: No player availability data
- **Betting odds**: No bookmaker odds integration

### 🎯 **Optimal Use Cases**
- **League table analysis**: Team strength assessment
- **Form analysis**: Recent results and patterns
- **Goal pattern analysis**: Over/Under market insights
- **Player goalscorer bets**: Top scorer performance
- **Head-to-head analysis**: Historical matchup data
- **Fixture planning**: Upcoming match schedules

---

## Testing Summary

### Core Functionality ✅
- **getCompetitions**: 13 competitions retrieved successfully
- **getCompetitionMatches**: Liverpool 4-2 Bournemouth match data
- **getCompetitionStandings**: Complete Premier League table
- **getCompetitionTeams**: 20 Premier League teams with full data
- **getTeamMatches**: Team-specific fixture filtering
- **getMatchDetails**: Complete match information with officials
- **getTopScorers**: Antoine Semenyo leading with 2 goals

### Data Accuracy ✅
- **Real-time updates**: Current season data (2025-26)
- **Score accuracy**: Match results verified
- **Team information**: Complete metadata available
- **Competition coverage**: Major European leagues included

### Performance ✅
- **Response time**: < 3 seconds typical
- **Reliability**: Deployed on Railway with high uptime
- **Rate limiting**: Built-in API politeness
- **Error handling**: Graceful failure management

---

## Summary

**Complete Soccer MCP Implementation**: 7 specialized tools providing comprehensive soccer analytics

**Core Features**:
- Competition discovery and information
- Real-time match results and schedules
- League standings and team performance
- Team-specific analysis and history
- Individual match details and context
- Top scorer tracking and player performance

**Technical Details**:
- Football-Data.org API v4 integration
- Deployed on Railway at `https://soccermcp-production.up.railway.app/mcp`
- JSON-RPC 2.0 protocol support
- Comprehensive error handling and validation
- Free tier limitations clearly documented

**Betting Intelligence Ready**: Optimized for fundamental soccer betting markets including match outcomes, goal totals, and anytime goalscorer bets while avoiding markets requiring detailed statistics not available on the free tier.

**Production Status**: ✅ All tools tested and verified with real soccer data including Liverpool FC performance, Premier League standings, and current top scorers.