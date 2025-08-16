# Soccer MCP Tool: getTopScorers

## Overview
The `getTopScorers` tool retrieves leading goalscorers for a specific soccer competition. This is the primary tool for player performance analysis and anytime goalscorer betting intelligence.

**Server URL**: `https://soccermcp-production.up.railway.app/mcp`  
**Tool Name**: `getTopScorers`

---

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `competition_id` | string | Yes | - | Competition ID (e.g., "2021" for Premier League) |
| `season` | integer | No | Current | Season year (e.g., 2025) |
| `limit` | integer | No | 10 | Number of top scorers to return |

---

## Usage Examples

### Get Top 10 Premier League Scorers (Default)
```python
import httpx
import json

payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
        "name": "getTopScorers",
        "arguments": {
            "competition_id": "2021"  # Premier League
        }
    }
}

async with httpx.AsyncClient() as client:
    response = await client.post("https://soccermcp-production.up.railway.app/mcp", json=payload)
    result = response.json()
```

### Get Top 5 Scorers
```python
payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
        "name": "getTopScorers",
        "arguments": {
            "competition_id": "2021",
            "limit": 5
        }
    }
}
```

### Get Specific Season Scorers
```python
payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
        "name": "getTopScorers",
        "arguments": {
            "competition_id": "2021",
            "season": 2024,
            "limit": 15
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
        },
        {
          "player": {
            "id": 789012,
            "name": "Hugo Ekitike",
            "position": "Centre-Forward",
            "dateOfBirth": "2002-06-20",
            "nationality": "France"
          },
          "team": {
            "id": 64,
            "name": "Liverpool FC",
            "shortName": "Liverpool",
            "tla": "LIV",
            "crest": "https://crests.football-data.org/64.png"
          },
          "goals": 1
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
- `count` (integer): Number of scorers returned
- `scorers` (array): List of scorer objects

### Scorer Object
- `player` (object): Player information
- `team` (object): Team information
- `goals` (integer): Total goals scored in competition

### Player Object
- `id` (integer): Unique player identifier
- `name` (string): Player's full name
- `position` (string): Playing position
- `dateOfBirth` (string): Birth date (YYYY-MM-DD)
- `nationality` (string): Player nationality

### Team Object
- `id` (integer): Team identifier
- `name` (string): Full team name
- `shortName` (string): Abbreviated team name
- `tla` (string): Three-letter abbreviation
- `crest` (string): Team logo URL

---

## Player Positions

| Position | Description | Typical Role |
|----------|-------------|--------------|
| `Centre-Forward` | Central striker | Primary goalscorer |
| `Left Winger` | Left wing forward | Wide attacking player |
| `Right Winger` | Right wing forward | Wide attacking player |
| `Attacking Midfield` | Advanced midfielder | Creative/scoring midfielder |
| `Central Midfield` | Central midfielder | Box-to-box player |
| `Defensive Midfield` | Defensive midfielder | Holding midfielder |
| `Left-Back` | Left fullback | Defensive/attacking fullback |
| `Right-Back` | Right fullback | Defensive/attacking fullback |
| `Centre-Back` | Central defender | Primary defender |
| `Goalkeeper` | Goalkeeper | Shot stopper |

---

## Common Competition IDs

| Competition | ID | Typical Top Scorer Goals |
|-------------|----|-----------------------|
| Premier League | 2021 | 15-30 goals |
| La Liga | 2014 | 20-35 goals |
| Bundesliga | 2002 | 20-40 goals |
| Serie A | 2019 | 15-30 goals |
| Ligue 1 | 2015 | 20-35 goals |
| Champions League | 2001 | 8-15 goals |
| Europa League | 2146 | 6-12 goals |

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

### No Scorer Data Available
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": true,
    "content_md": "## Top Scorers\n\nNo scorer data available for competition 2021",
    "data": {
      "source": "football_data_api",
      "competition_id": "2021",
      "scorers": [],
      "count": 0
    }
  }
}
```

---

## Testing Notes

### Verified Functionality ✅
- **Premier League scorers**: Successfully retrieved current season leaders
- **Antoine Semenyo**: Leading with 2 goals for AFC Bournemouth
- **Multiple players**: Hugo Ekitike (Liverpool), Cody Gakpo (Liverpool), others
- **Complete player data**: Names, positions, nationalities, birth dates
- **Team affiliations**: Full team information with crests
- **Goal counts**: Accurate scoring tallies for current season

### Data Quality Verification
- **Current season**: 2025-26 Premier League data
- **Player positions**: Accurate position classifications
- **Team data**: Complete team information with logos
- **Goal accuracy**: Verified against match results
- **Player details**: Complete biographical information

---

## Integration Examples

### Anytime Goalscorer Analysis
```python
import httpx
import json
import asyncio

async def analyze_goalscorers(competition_id: str, min_goals: int = 1):
    """Analyze top scorers for anytime goalscorer betting"""
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getTopScorers",
            "arguments": {
                "competition_id": competition_id,
                "limit": 20  # Get more players for analysis
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
            scorers = result["result"]["data"]["scorers"]
            
            # Filter by minimum goals
            active_scorers = [s for s in scorers if s["goals"] >= min_goals]
            
            print(f"Anytime Goalscorer Analysis ({len(active_scorers)} players):")
            print("=" * 60)
            
            # Group by team for team analysis
            teams = {}
            for scorer in active_scorers:
                team_name = scorer["team"]["name"]
                if team_name not in teams:
                    teams[team_name] = []
                teams[team_name].append(scorer)
            
            # Analyze by scoring tier
            prolific = [s for s in active_scorers if s["goals"] >= 5]
            consistent = [s for s in active_scorers if 2 <= s["goals"] < 5]
            emerging = [s for s in active_scorers if s["goals"] == 1]
            
            print(f"Prolific Scorers (5+ goals): {len(prolific)}")
            for scorer in prolific:
                name = scorer["player"]["name"]
                team = scorer["team"]["shortName"]
                goals = scorer["goals"]
                position = scorer["player"]["position"]
                print(f"  ⭐ {name} ({team}) - {goals} goals, {position}")
            
            print(f"\nConsistent Scorers (2-4 goals): {len(consistent)}")
            for scorer in consistent:
                name = scorer["player"]["name"]
                team = scorer["team"]["shortName"]
                goals = scorer["goals"]
                position = scorer["player"]["position"]
                print(f"  📈 {name} ({team}) - {goals} goals, {position}")
            
            print(f"\nEmerging Scorers (1 goal): {len(emerging)}")
            for scorer in emerging[:5]:  # Show top 5
                name = scorer["player"]["name"]
                team = scorer["team"]["shortName"]
                position = scorer["player"]["position"]
                print(f"  🎯 {name} ({team}) - 1 goal, {position}")
            
            # Team goal distribution
            print(f"\nTeam Goal Distribution:")
            for team_name, team_scorers in sorted(teams.items()):
                total_goals = sum(s["goals"] for s in team_scorers)
                top_scorer = max(team_scorers, key=lambda x: x["goals"])
                print(f"  {team_name}: {total_goals} goals ({len(team_scorers)} scorers)")
                print(f"    Top: {top_scorer['player']['name']} ({top_scorer['goals']} goals)")
        
        return active_scorers

# Run it
asyncio.run(analyze_goalscorers("2021"))  # Premier League
```

### Position-Based Analysis
```python
async def analyze_by_position(competition_id: str):
    """Analyze goalscorers by playing position"""
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getTopScorers",
            "arguments": {
                "competition_id": competition_id,
                "limit": 50  # Get comprehensive list
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
            scorers = result["result"]["data"]["scorers"]
            
            # Group by position
            positions = {}
            for scorer in scorers:
                pos = scorer["player"]["position"]
                if pos not in positions:
                    positions[pos] = []
                positions[pos].append(scorer)
            
            print("Goalscorers by Position:")
            print("=" * 40)
            
            for position, players in sorted(positions.items()):
                total_goals = sum(p["goals"] for p in players)
                avg_goals = total_goals / len(players) if players else 0
                
                print(f"\n{position} ({len(players)} players, {total_goals} total goals):")
                print(f"  Average: {avg_goals:.1f} goals per player")
                
                # Show top 3 in position
                top_players = sorted(players, key=lambda x: x["goals"], reverse=True)[:3]
                for i, player in enumerate(top_players, 1):
                    name = player["player"]["name"]
                    team = player["team"]["shortName"]
                    goals = player["goals"]
                    print(f"  {i}. {name} ({team}) - {goals} goals")
        
        return positions

# Run it
asyncio.run(analyze_by_position("2021"))  # Premier League
```

---

## Betting Intelligence Use Cases

### Anytime Goalscorer Markets
- **Prolific scorers**: Players with 5+ goals (reliable bets)
- **Consistent scorers**: Players with 2-4 goals (value bets)
- **Form players**: Recent goal-scoring trends
- **Position analysis**: Forwards vs midfielders vs defenders

### First Goalscorer Markets
- **Top scorers**: Higher probability of opening scoring
- **Team's main threat**: Primary goalscoring option
- **Recent form**: Hot streaks and cold spells
- **Opposition analysis**: Performance against specific defenses

### Player Props & Specials
- **Goals per game**: Individual scoring rates
- **Team distribution**: Goal spread across squad
- **Position-based props**: Midfielder to score, defender to score
- **Nationality props**: Country-specific scoring markets

### Team Analysis
- **Goal distribution**: Reliance on individual players
- **Scoring depth**: Multiple goal threats vs one-man teams
- **Position balance**: Forward-heavy vs midfield goals
- **Squad rotation**: Impact of key player absence

---

## Seasonal Patterns

### Early Season (Matchdays 1-10)
- **Small sample sizes**: Limited goal data
- **Form establishment**: Players finding rhythm
- **New signings**: Adaptation period
- **Injury returns**: Players regaining fitness

### Mid Season (Matchdays 11-25)
- **Established patterns**: Reliable scoring trends
- **Peak fitness**: Players at optimal performance
- **Consistent selection**: Regular starting lineups
- **Form streaks**: Hot and cold periods

### Late Season (Matchdays 26-38)
- **Fatigue factors**: Physical and mental tiredness
- **Rotation policies**: Squad management
- **Motivation levels**: League position impact
- **Final push**: Top scorer race intensifies

---

## Performance Notes

### Response Times
- **Top 10**: 1-2 seconds typical
- **Top 20**: 2-3 seconds typical
- **Full list (50+)**: 3-4 seconds typical

### Data Accuracy
- **Real-time updates**: Goals updated after each matchday
- **Verified counts**: Cross-referenced with match results
- **Complete records**: All competition goals included
- **Historical data**: Previous seasons available

---

## Summary

**Primary Use**: Player goalscoring analysis and anytime goalscorer betting intelligence  
**Reliability**: ✅ Production ready with accurate goal counts  
**Response Time**: 1-3 seconds typical  
**Data Source**: Football-Data.org API v4 (official)  
**Coverage**: Complete player information with team affiliations  
**Betting Focus**: Optimized for anytime goalscorer, first goalscorer, and player prop markets  
**Analysis Depth**: Position-based analysis, team distribution, and seasonal patterns supported