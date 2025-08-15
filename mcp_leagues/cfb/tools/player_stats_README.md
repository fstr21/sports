# CFB Player Stats Tool - README

## Overview
The `player_stats.py` tool tests the **getCFBPlayerStats** MCP endpoint, which retrieves individual player statistics from the deployed CFB MCP server. This tool validates player performance data across multiple categories and seasons.

## MCP Tool: getCFBPlayerStats

### Description
Retrieves individual player season statistics including passing, rushing, receiving, defensive, and special teams performance from the College Football Data API.

### Parameters
- **year** (integer, optional): Season year (default: current year)
- **team** (string, optional): Team name filter (e.g., "Kansas State")
- **player** (string, optional): Specific player name (e.g., "Avery Johnson")
- **category** (string, optional): Stat category filter (passing, rushing, receiving, defensive, etc.)

### Example Usage

#### Get Specific Player Stats
```json
{
  "method": "tools/call",
  "params": {
    "name": "getCFBPlayerStats",
    "arguments": {
      "year": 2024,
      "team": "Kansas State",
      "player": "Avery Johnson"
    }
  }
}
```

#### Get Team Category Stats
```json
{
  "method": "tools/call",
  "params": {
    "name": "getCFBPlayerStats",
    "arguments": {
      "year": 2024,
      "team": "Kansas State",
      "category": "passing"
    }
  }
}
```

#### Get Conference Category Stats
```json
{
  "method": "tools/call",
  "params": {
    "name": "getCFBPlayerStats",
    "arguments": {
      "year": 2024,
      "conference": "Big 12",
      "category": "rushing"
    }
  }
}
```

## Test Cases

### 1. Avery Johnson 2024 Stats
- **Purpose**: Test individual player comprehensive statistics
- **Player**: Kansas State QB #2 (Junior)
- **Expected**: Complete passing, rushing, and fumble statistics
- **Categories**: Multiple stat categories for single player

### 2. Kansas State 2024 Passing Stats
- **Purpose**: Test team-specific category filtering
- **Expected**: All Kansas State quarterbacks' passing statistics
- **Categories**: Passing-specific metrics only
- **Analysis**: Team passing game evaluation

### 3. Big 12 2024 Rushing Stats
- **Purpose**: Test conference-wide category analysis
- **Expected**: All Big 12 rushing statistics
- **Scope**: Conference-wide player comparison
- **Analysis**: Conference rushing leaders and trends

## Statistical Categories

### Offensive Categories
- **passing**: Completions, attempts, yards, TDs, INTs, rating
- **rushing**: Carries, yards, TDs, long, yards per carry
- **receiving**: Receptions, yards, TDs, long, yards per reception
- **fumbles**: Fumbles, fumbles lost, fumbles recovered

### Defensive Categories
- **defensive**: Tackles, TFL, sacks, QB hurries, pass deflections
- **interceptions**: INTs, return yards, return TDs, long return
- **punting**: Punts, yards, average, long, inside 20
- **kicking**: FG made/attempted, XP made/attempted, long FG

### Special Teams Categories
- **puntReturns**: Returns, yards, TDs, long, average
- **kickReturns**: Returns, yards, TDs, long, average

## Response Format

### Player Stat Structure
```json
{
  "season": 2024,
  "player_id": 4870857,
  "player": "Avery Johnson",
  "position": "QB",
  "team": "Kansas State",
  "conference": "Big 12",
  "category": "passing",
  "stat_type": "ATT",
  "stat": 372
}
```

### Key Fields
- **season**: Year of statistics
- **player_id**: Unique player identifier
- **player**: Player's full name
- **position**: Position abbreviation
- **team**: Team name
- **conference**: Conference affiliation
- **category**: Statistical category
- **stat_type**: Specific statistic type
- **stat**: Statistical value

### Common Stat Types

#### Passing Stats
- **ATT**: Attempts
- **COMPLETIONS**: Completed passes
- **PCT**: Completion percentage
- **YDS**: Passing yards
- **YPA**: Yards per attempt
- **TD**: Touchdown passes
- **INT**: Interceptions
- **RATING**: Passer rating

#### Rushing Stats
- **CAR**: Carries
- **YDS**: Rushing yards
- **YPC**: Yards per carry
- **TD**: Rushing touchdowns
- **LONG**: Longest rush

#### Receiving Stats
- **REC**: Receptions
- **YDS**: Receiving yards
- **YPR**: Yards per reception
- **TD**: Receiving touchdowns
- **LONG**: Longest reception

## Running the Test

### Command
```bash
python player_stats.py
```

### Expected Output
1. **Test Results**: Each query with stat record counts
2. **Category Breakdown**: Statistics grouped by category
3. **Player Analysis**: Top players by statistical category
4. **JSON Export**: Complete results saved to `player_stats.json`

### Success Indicators
- ✅ All 3 test cases return statistical data
- ✅ Avery Johnson stats show multiple categories
- ✅ Team stats show multiple players
- ✅ Conference stats show league-wide data
- ✅ JSON file created with detailed results

## Sample Player Performance

### Avery Johnson 2024 Statistics
```
PASSING:
- 372 attempts, 217 completions (58.3%)
- 2,712 yards, 25 TDs, 10 INTs
- 7.3 yards per attempt

RUSHING:
- 113 carries for 605 yards (5.4 YPC)
- 7 rushing TDs, 33-yard long

FUMBLES:
- 2 fumbles, 2 lost
```

## JSON Output File

### File: `player_stats.json`
Contains complete test results including:
- **Test metadata**: Timestamps, server URL, test names
- **HTTP responses**: Full MCP server responses
- **Extracted data**: Complete statistical records
- **Summary statistics**: Player counts, category breakdowns
- **Sample data**: Representative statistical records

### Sample JSON Structure
```json
{
  "test_name": "CFB Player Stats MCP Test",
  "timestamp": "2025-08-15T00:30:15.789012",
  "server_url": "https://cfbmcp-production.up.railway.app/mcp",
  "tests": [
    {
      "name": "Avery Johnson 2024 Stats",
      "tool": "getCFBPlayerStats",
      "args": {
        "year": 2024,
        "team": "Kansas State",
        "player": "Avery Johnson"
      },
      "success": true,
      "summary": {
        "stats_count": 15,
        "categories": {
          "passing": 8,
          "rushing": 5,
          "fumbles": 2
        },
        "sample_stats": [...]
      }
    }
  ]
}
```

## Use Cases

### 1. Player Evaluation
- Analyze individual player performance across categories
- Compare players within same position group
- Track player development across seasons

### 2. Team Analysis
- Evaluate team strength by position group
- Identify statistical leaders and contributors
- Analyze offensive and defensive efficiency

### 3. Conference Comparison
- Compare player performance across conferences
- Identify conference statistical leaders
- Analyze conference strength and depth

### 4. Recruiting Analysis
- Evaluate player production for recruiting purposes
- Compare statistical output across programs
- Identify undervalued or overperforming players

## Statistical Analysis

### Performance Metrics
- **Efficiency**: Yards per attempt, completion percentage
- **Volume**: Total attempts, carries, receptions
- **Impact**: Touchdowns, big plays, game-changing stats
- **Consistency**: Games played, statistical reliability

### Comparative Analysis
- **Position Groups**: Compare players at same position
- **Conference Leaders**: Top performers by category
- **Team Contributors**: Key players for each team
- **Breakout Players**: Improved performance year-over-year

## Error Handling

### Common Issues
- **Player name variations**: Use exact names from CFBD database
- **Limited historical data**: Some seasons may have incomplete stats
- **Category filtering**: Ensure valid category names
- **Network timeouts**: 30-second timeout for requests

### Troubleshooting
1. **Verify player names**: Use exact spelling from roster data
2. **Check category validity**: Use standard CFBD categories
3. **Handle missing data**: Some players may have limited stats
4. **Review team names**: Ensure correct team identification

## Integration

### With Roster Data
Combine with roster information for complete player profiles including physical attributes and biographical data.

### With Game Data
Cross-reference with game results for context on statistical performance and game impact.

### With Rankings
Compare statistical leaders with team rankings and success metrics.

### Data Export
JSON output can be imported into:
- Player evaluation systems
- Fantasy football analysis tools
- Recruiting databases
- Statistical modeling platforms
- Performance tracking systems

Perfect for college football player analysis and performance evaluation! 📊🏈