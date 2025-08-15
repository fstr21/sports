# CFB Roster Tool - README

## Overview
The `roster.py` tool tests the **getCFBRoster** MCP endpoint, which retrieves complete team rosters with detailed player information from the deployed CFB MCP server. This tool validates player data, positions, and team composition.

## MCP Tool: getCFBRoster

### Description
Retrieves complete team rosters including player names, positions, physical attributes, and biographical information from the College Football Data API.

### Parameters
- **team** (string, required): Team name (e.g., "Kansas State", "Iowa State")
- **year** (integer, optional): Season year (default: current year)

### Example Usage

#### Get Current Team Roster
```json
{
  "method": "tools/call",
  "params": {
    "name": "getCFBRoster",
    "arguments": {
      "team": "Kansas State"
    }
  }
}
```

#### Get Historical Roster
```json
{
  "method": "tools/call",
  "params": {
    "name": "getCFBRoster",
    "arguments": {
      "team": "Kansas State",
      "year": 2024
    }
  }
}
```

## Test Cases

### 1. Kansas State 2024 Roster
- **Purpose**: Test comprehensive roster data for major program
- **Expected**: ~124 players across all positions
- **Includes**: Complete depth chart, position groups
- **Special**: Big 12 conference team with detailed data

### 2. Iowa State 2024 Roster
- **Purpose**: Test another Big 12 program for comparison
- **Expected**: ~133 players with position breakdowns
- **Includes**: Full roster with player details
- **Analysis**: Position distribution and team composition

### 3. Stanford 2024 Roster
- **Purpose**: Test Pac-12/ACC program (conference transition)
- **Expected**: ~109 players with academic focus
- **Includes**: Complete roster with player information
- **Special**: Academic-focused program roster analysis

## Response Format

### Player Data Structure
```json
{
  "id": 4426517,
  "first_name": "Keenan",
  "last_name": "Garber",
  "team": "Kansas State",
  "weight": 187,
  "height": 72,
  "jersey": 1,
  "year": 4,
  "position": "CB",
  "home_city": "Lawrence",
  "home_state": "KS",
  "home_country": "USA"
}
```

### Key Fields
- **id**: Unique player identifier for cross-referencing
- **first_name/last_name**: Player's full name
- **team**: Team affiliation
- **weight**: Player weight in pounds
- **height**: Player height in inches
- **jersey**: Jersey number (may be null)
- **year**: Class year (1=FR, 2=SO, 3=JR, 4=SR, 5=5Y)
- **position**: Position abbreviation (QB, RB, WR, etc.)
- **home_city/state/country**: Recruiting location

### Position Abbreviations
- **Offense**: QB (Quarterback), RB (Running Back), WR (Wide Receiver), TE (Tight End), OL (Offensive Line)
- **Defense**: DL (Defensive Line), DE (Defensive End), DT (Defensive Tackle), LB (Linebacker), CB (Cornerback), S (Safety), DB (Defensive Back)
- **Special Teams**: K (Kicker), P (Punter), LS (Long Snapper)

## Running the Test

### Command
```bash
python roster.py
```

### Expected Output
1. **Test Results**: Each roster with player counts
2. **Position Breakdown**: Players grouped by position
3. **Sample Players**: First 5 players with details
4. **JSON Export**: Complete results saved to `roster.json`

### Success Indicators
- ✅ All 3 test cases return roster data
- ✅ Player counts match expectations (100+ players each)
- ✅ Position breakdowns show proper distribution
- ✅ JSON file created with detailed results

## Position Analysis

### Typical Position Distribution
- **Quarterbacks (QB)**: 3-6 players
- **Running Backs (RB)**: 6-10 players
- **Wide Receivers (WR)**: 12-20 players
- **Tight Ends (TE)**: 6-10 players
- **Offensive Line (OL)**: 15-25 players
- **Defensive Line (DL/DE/DT)**: 15-25 players
- **Linebackers (LB)**: 15-20 players
- **Defensive Backs (CB/S/DB)**: 20-30 players
- **Special Teams (K/P/LS)**: 3-6 players

### Sample Output
```
📊 Position breakdown:
   CB: 11 players
   DE: 9 players
   DL: 1 players
   DT: 7 players
   LB: 17 players
   OL: 20 players
   P: 2 players
   QB: 5 players
   RB: 7 players
   S: 13 players
   TE: 8 players
   WR: 19 players
```

## JSON Output File

### File: `roster.json`
Contains complete test results including:
- **Test metadata**: Timestamps, server URL, test names
- **HTTP responses**: Full MCP server responses
- **Extracted data**: Complete player rosters
- **Summary statistics**: Player counts, position breakdowns
- **Sample data**: Representative player information

### Sample JSON Structure
```json
{
  "test_name": "CFB Roster MCP Test",
  "timestamp": "2025-08-15T00:25:30.123456",
  "server_url": "https://cfbmcp-production.up.railway.app/mcp",
  "tests": [
    {
      "name": "Kansas State 2024 Roster",
      "tool": "getCFBRoster",
      "args": {"team": "Kansas State", "year": 2024},
      "success": true,
      "summary": {
        "players_count": 124,
        "positions": {
          "QB": 5,
          "RB": 7,
          "WR": 19,
          "TE": 8,
          "OL": 20
        },
        "sample_players": [...]
      }
    }
  ]
}
```

## Use Cases

### 1. Recruiting Analysis
- Track player origins and recruiting regions
- Analyze class composition (FR, SO, JR, SR)
- Compare roster construction across programs

### 2. Depth Chart Analysis
- Evaluate position depth and experience
- Identify key players and potential starters
- Analyze roster balance and needs

### 3. Physical Attributes Study
- Compare player sizes across positions
- Analyze height/weight trends by position
- Study regional recruiting patterns

### 4. Team Comparison
- Compare roster sizes across programs
- Analyze position group strengths
- Study conference recruiting patterns

## Player Information Details

### Physical Attributes
- **Height**: Stored in inches (convert to feet-inches for display)
- **Weight**: Stored in pounds
- **Jersey Numbers**: May be null or duplicate (practice squad)

### Academic Information
- **Year**: Class standing (1-5, with 5 being 5th year seniors)
- **Eligibility**: Inferred from year and transfer status

### Geographic Data
- **Home Location**: City, state, country of origin
- **Recruiting Regions**: Track where teams recruit from
- **International Players**: Identify non-US players

## Error Handling

### Common Issues
- **Team name variations**: Use exact team names from CFBD API
- **Historical data limits**: Some years may have limited data
- **Player data completeness**: Some fields may be null
- **Network timeouts**: 30-second timeout for requests

### Troubleshooting
1. **Verify team names**: Use exact spelling from CFBD database
2. **Check year validity**: Ensure year has available data
3. **Handle null values**: Some player fields may be incomplete
4. **Review position codes**: Standardize position abbreviations

## Integration

### With Player Stats
Use player IDs to cross-reference with statistics endpoints for complete player profiles.

### With Game Analysis
Combine roster data with game performance for player impact analysis.

### With Recruiting Tools
Track player origins and recruiting success by region and position.

### Data Export
JSON output can be imported into:
- Recruiting databases
- Depth chart analysis tools
- Player comparison systems
- Team composition studies

Perfect for college football recruiting analysis and team evaluation! 👥🏈