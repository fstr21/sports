# MLB Player Props Tool: player_props.py

## Overview

The `player_props.py` tool retrieves MLB player prop betting odds for a specific game matchup. This script focuses on three key player prop markets: batter home runs, batter hits, and pitcher strikeouts. It combines data from both the MLB MCP server and Odds MCP server to find and extract player prop odds for the Miami Marlins @ Cleveland Guardians game.

**MLB MCP Server**: `https://mlbmcp-production.up.railway.app/mcp`  
**Odds MCP Server**: `https://odds-mcp-v2-production.up.railway.app/mcp`  
**Script Name**: `player_props.py`

---

## Target Markets

| Market               | Description                     | Example                                            |
| -------------------- | ------------------------------- | -------------------------------------------------- |
| `batter_home_runs`   | Batter home runs (Over/Under)   | Player Over 0.5 HR (+200), Under 0.5 HR (-250)     |
| `batter_hits`        | Batter hits (Over/Under)        | Player Over 1.5 hits (+150), Under 1.5 hits (-180) |
| `pitcher_strikeouts` | Pitcher strikeouts (Over/Under) | Pitcher Over 6.5 K (-110), Under 6.5 K (-110)      |

---

## Target Game

- **Away Team**: Miami Marlins
- **Home Team**: Cleveland Guardians
- **Game Format**: Marlins @ Guardians

---

## Usage

### Basic Execution

```bash
python player_props.py
```

### Requirements

```bash
pip install httpx
```

---

## Script Workflow

### 1. Game Discovery

- Calls `getOdds` on Odds MCP server to find all MLB games
- Searches for Miami Marlins @ Cleveland Guardians matchup
- Extracts event ID for the target game

### 2. Player Props Retrieval

- Uses event ID to call `getEventOdds` with specific markets
- Requests: `batter_home_runs,batter_hits,pitcher_strikeouts`
- Retrieves odds from multiple sportsbooks

### 3. Data Processing

- Groups outcomes by player and market type
- Pairs Over/Under odds for each player prop
- Organizes data by market category

### 4. Output Generation

- Saves complete data to timestamped JSON file
- Displays formatted props in console
- Provides summary statistics

---

## Output Structure

### JSON File Format

```json
{
  "timestamp": "2025-08-14T16:06:03.123456",
  "date": "2025-08-14",
  "game": "Miami Marlins @ Cleveland Guardians",
  "target_markets": ["batter_home_runs", "batter_hits", "pitcher_strikeouts"],
  "game_data": {
    "event_id": "abc123def456",
    "home_team": "Cleveland Guardians",
    "away_team": "Miami Marlins",
    "commence_time": "2025-08-14T19:10:00Z",
    "player_props": {
      "batter_home_runs": [
        {
          "player": "José Ramírez",
          "bookmaker": "FanDuel",
          "over_price": 200,
          "over_point": 0.5,
          "under_price": -250,
          "under_point": 0.5
        }
      ],
      "batter_hits": [
        {
          "player": "José Ramírez",
          "bookmaker": "FanDuel",
          "over_price": 150,
          "over_point": 1.5,
          "under_price": -180,
          "under_point": 1.5
        }
      ],
      "pitcher_strikeouts": [
        {
          "player": "Shane Bieber",
          "bookmaker": "FanDuel",
          "over_price": -110,
          "over_point": 6.5,
          "under_price": -110,
          "under_point": 6.5
        }
      ]
    }
  }
}
```

### Console Output Format

```
🎯 Looking for Miami Marlins @ Cleveland Guardians game...
✅ Found 7 MLB events with odds
🎲 Found target game: Miami Marlins @ Cleveland Guardians
⏰ Game time: 2025-08-14T19:10:00Z

============================================================
📊 SUMMARY
   Game: Miami Marlins @ Cleveland Guardians
   Total player props: 25
   Saved to: testing/marlins_guardians_props_20250814_160603.json
============================================================
   batter_home_runs: 8 props
   batter_hits: 12 props
   pitcher_strikeouts: 5 props

🏠 BATTER HOME RUNS:
   José Ramírez: Over 0.5 (+200) / Under 0.5 (-250) - FanDuel
   Josh Naylor: Over 0.5 (+250) / Under 0.5 (-300) - FanDuel

🎯 BATTER HITS:
   José Ramírez: Over 1.5 (+150) / Under 1.5 (-180) - FanDuel
   Josh Naylor: Over 1.5 (+170) / Under 1.5 (-200) - FanDuel

⚾ PITCHER STRIKEOUTS:
   Shane Bieber: Over 6.5 (-110) / Under 6.5 (-110) - FanDuel
   Jesús Luzardo: Over 5.5 (+105) / Under 5.5 (-125) - FanDuel
```

---

## Data Fields

### Player Prop Object

- `player` (string): Player's full name
- `bookmaker` (string): Sportsbook name (FanDuel, DraftKings, etc.)
- `over_price` (integer): American odds for Over bet
- `over_point` (float): Over threshold (e.g., 1.5 hits)
- `under_price` (integer): American odds for Under bet
- `under_point` (float): Under threshold (same as over_point)

### Game Data Object

- `event_id` (string): Unique identifier from odds API
- `home_team` (string): Home team name
- `away_team` (string): Away team name
- `commence_time` (string): Game start time in UTC ISO 8601
- `player_props` (object): Props organized by market type

---

## Market-Specific Details

### Batter Home Runs

- **Typical Lines**: 0.5, 1.5 (rarely 2.5 for power hitters)
- **Player Count**: 6-10 batters per game
- **Odds Range**: +150 to +400 (Over), -200 to -500 (Under)
- **Focus**: Starting lineup hitters with power potential

### Batter Hits

- **Typical Lines**: 0.5, 1.5, 2.5 (top hitters)
- **Player Count**: 10-15 batters per game
- **Odds Range**: -200 to +200 depending on player and line
- **Focus**: Regular starters and key bench players

### Pitcher Strikeouts

- **Typical Lines**: 4.5, 5.5, 6.5, 7.5+ (ace pitchers)
- **Player Count**: 2-4 pitchers per game (starters + key relievers)
- **Odds Range**: -150 to +150 for most lines
- **Focus**: Starting pitchers and high-strikeout relievers

---

## Common Sportsbooks

| Bookmaker  | Availability | Prop Coverage |
| ---------- | ------------ | ------------- |
| FanDuel    | Very High    | Comprehensive |
| DraftKings | Very High    | Comprehensive |
| BetMGM     | High         | Good          |
| Caesars    | High         | Good          |
| PointsBet  | Medium       | Limited       |

---

## Error Handling

### Game Not Found

```
❌ Could not find Miami Marlins @ Cleveland Guardians game
Available games:
   New York Yankees @ Boston Red Sox
   Los Angeles Dodgers @ San Francisco Giants
```

### No Player Props Available

```
❌ No player props available for this game
```

### API Connection Issues

```
❌ Failed to get odds events: MCP call failed: Connection timeout
```

### No MLB Games Today

```
❌ No MLB games with odds found for today
```

---

## File Output

### Filename Pattern

- Format: `marlins_guardians_props_YYYYMMDD_HHMMSS.json`
- Example: `marlins_guardians_props_20250814_160603.json`
- Location: Same directory as script

### File Contents

- Complete game and prop data in JSON format
- Timestamp and date metadata
- Organized by market type for easy parsing
- Preserves all bookmaker information

---

## Integration Notes

### MCP Server Dependencies

- **MLB MCP**: Not directly used but available for schedule verification
- **Odds MCP v2**: Primary data source for game events and player props
- **API Keys**: Managed by Railway deployment

### Rate Limiting

- Built-in 0.5 second delays between API calls
- Respects The Odds API rate limits
- Single game focus minimizes API usage

### Data Freshness

- Player props update frequently (every 5-15 minutes)
- Best results 2-4 hours before game time
- Props may be limited for games starting soon

---

## Testing Notes

### Verified Functionality ✅

- **Game Discovery**: Successfully finds Marlins @ Guardians matchup
- **Event ID Extraction**: Properly extracts unique event identifier
- **Multi-Market Retrieval**: Gets all three target prop markets
- **Data Organization**: Correctly groups props by market and player
- **JSON Export**: Creates valid, well-structured output files
- **Console Display**: Formatted, readable prop listings

### Data Quality

- **Player Names**: Full names as provided by sportsbooks
- **Odds Format**: American odds (-110, +150, etc.)
- **Point Values**: Decimal format (0.5, 1.5, 6.5)
- **Bookmaker Info**: Preserved for each prop

---

## Customization Options

### Change Target Game

```python
# Modify these constants at top of script
TARGET_AWAY_TEAM = "New York Yankees"
TARGET_HOME_TEAM = "Boston Red Sox"
```

### Add/Remove Markets

```python
# Modify TARGET_MARKETS list
TARGET_MARKETS = ["batter_home_runs", "batter_hits", "pitcher_strikeouts", "batter_rbis"]
```

### Change Output Location

```python
# Modify filename in save section
filename = f"output/custom_props_{timestamp}.json"
```

---

## Performance Metrics

### Typical Execution Time

- **Game Discovery**: 1-2 seconds
- **Props Retrieval**: 2-3 seconds
- **Data Processing**: < 1 second
- **Total Runtime**: 3-6 seconds

### Data Volume

- **Typical Props**: 20-30 total props per game
- **JSON File Size**: 5-15 KB
- **Console Output**: 30-50 lines

---

## Summary

**Primary Use**: Miami Marlins @ Cleveland Guardians player prop odds retrieval  
**Reliability**: ✅ Production ready  
**Response Time**: 3-6 seconds typical  
**Data Sources**: The Odds API via Railway MCP servers  
**Markets Supported**: Batter home runs, batter hits, pitcher strikeouts  
**Output Formats**: JSON file + formatted console display  
**Sportsbook Coverage**: 3-6 major US sportsbooks per game
</content>
</file>
