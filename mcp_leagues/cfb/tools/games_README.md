# CFB Games Tool - README

## Overview
The `games.py` tool tests the **getCFBGames** MCP endpoint, which retrieves college football game data from the deployed CFB MCP server. This tool validates game schedules, scores, and matchup information.

## MCP Tool: getCFBGames

### Description
Retrieves college football games for specific years, weeks, teams, or conferences from the College Football Data API.

### Parameters
- **year** (integer, optional): Season year (default: current year)
- **week** (integer, optional): Week number (1-15 for regular season)
- **team** (string, optional): Specific team name (e.g., "Kansas State")
- **conference** (string, optional): Conference name (e.g., "Big 12", "SEC")

### Example Usage

#### Get Games for Specific Week
```json
{
  "method": "tools/call",
  "params": {
    "name": "getCFBGames",
    "arguments": {
      "year": 2025,
      "week": 1
    }
  }
}
```

#### Get Team's Season Games
```json
{
  "method": "tools/call",
  "params": {
    "name": "getCFBGames",
    "arguments": {
      "year": 2024,
      "team": "Kansas State"
    }
  }
}
```

#### Get Conference Games
```json
{
  "method": "tools/call",
  "params": {
    "name": "getCFBGames",
    "arguments": {
      "year": 2025,
      "week": 1,
      "conference": "Big 12"
    }
  }
}
```

## Test Cases

### 1. August 23, 2025 Games
- **Purpose**: Test Week 1 games for 2025 season
- **Expected**: ~197 games including major matchups
- **Key Game**: Iowa State @ Kansas State in Dublin, Ireland

### 2. Kansas State 2024 Season
- **Purpose**: Test team-specific game retrieval
- **Expected**: ~13 games for Kansas State's 2024 season
- **Includes**: Home/away games, conference matchups

### 3. Big 12 Conference Week 1 2025
- **Purpose**: Test conference filtering
- **Expected**: Big 12 games only for specified week
- **Filters**: Conference-specific matchups

### 4. Power 5 Teams (getCFBTeams)
- **Purpose**: Test team information retrieval
- **Expected**: Big 12 team roster and details
- **Data**: Team logos, colors, locations

## Response Format

### Game Data Structure
```json
{
  "id": 401756846,
  "season": 2025,
  "week": 1,
  "season_type": "regular",
  "start_date": "2025-08-23T16:00:00.000Z",
  "completed": false,
  "neutral_site": true,
  "conference_game": true,
  "attendance": null,
  "venue": "Aviva Stadium",
  "home_team": "Kansas State",
  "home_conference": "Big 12",
  "home_points": null,
  "away_team": "Iowa State",
  "away_conference": "Big 12",
  "away_points": null,
  "excitement_index": null
}
```

### Key Fields
- **id**: Unique game identifier
- **start_date**: Game date/time in ISO format
- **venue**: Stadium/location name
- **neutral_site**: Boolean for neutral site games
- **conference_game**: Boolean for conference matchups
- **home/away_team**: Team names
- **home/away_conference**: Conference affiliations
- **home/away_points**: Final scores (null if not completed)

## Running the Test

### Command
```bash
python games.py
```

### Expected Output
1. **Health Check**: Server connectivity verification
2. **Test Results**: Each test case with success/failure status
3. **Sample Data**: First 3 games from each result set
4. **JSON Export**: Complete results saved to `games.json`

### Success Indicators
- ✅ Health check passes
- ✅ All 4 test cases return data
- ✅ Game counts match expectations
- ✅ JSON file created with detailed results

## JSON Output File

### File: `games.json`
Contains complete test results including:
- **Test metadata**: Timestamps, server URL, test names
- **HTTP responses**: Full MCP server responses
- **Extracted data**: Parsed game information
- **Summary statistics**: Game counts, sample data
- **Error handling**: Any failures or issues

### Sample JSON Structure
```json
{
  "test_name": "CFB Games MCP Test",
  "timestamp": "2025-08-15T00:20:46.121860",
  "server_url": "https://cfbmcp-production.up.railway.app/mcp",
  "health_check": {
    "success": true,
    "response": {"status": "healthy", "service": "cfb-mcp-server"}
  },
  "tests": [
    {
      "name": "August 23, 2025 Games",
      "tool": "getCFBGames",
      "args": {"year": 2025, "week": 1},
      "success": true,
      "summary": {
        "games_count": 197,
        "sample_games": [...]
      }
    }
  ]
}
```

## Use Cases

### 1. Schedule Analysis
- Get upcoming games for specific dates
- Analyze matchup strength and importance
- Track conference vs non-conference games

### 2. Team Tracking
- Monitor specific team's season schedule
- Analyze home/away game distribution
- Track rivalry games and key matchups

### 3. Conference Analysis
- Compare conference strength of schedule
- Analyze inter-conference matchups
- Track conference championship implications

### 4. Venue Analysis
- Identify neutral site games
- Track games at specific venues
- Analyze attendance patterns

## Error Handling

### Common Issues
- **Network timeouts**: 30-second timeout for requests
- **Invalid parameters**: Server validates input parameters
- **No data found**: Empty results for invalid queries
- **Server errors**: HTTP error codes and messages

### Troubleshooting
1. **Check server health**: Verify MCP server is running
2. **Validate parameters**: Ensure team names and years are correct
3. **Check network**: Verify internet connectivity
4. **Review logs**: Check console output for detailed errors

## Integration

### With MCP Clients
Use the server endpoint `https://cfbmcp-production.up.railway.app/mcp` with standard JSON-RPC 2.0 protocol.

### With Analysis Tools
The JSON output can be imported into data analysis tools for:
- Game prediction modeling
- Schedule strength analysis
- Conference comparison studies
- Attendance and venue analysis

Perfect for college football analytics and game prediction systems! 🏈