# College Football MCP Server

A dedicated MCP (Model Context Protocol) server for college football data, providing comprehensive access to college football statistics, game data, player information, and analytics through the College Football Data API.

## Features

### 🏈 Game Data
- **Games**: Get games by year, week, team, or conference
- **Game Statistics**: Detailed team performance stats for games
- **Play-by-Play**: Individual play data with down, distance, and results

### 👥 Team & Player Data
- **Teams**: Complete team information with logos, colors, and locations
- **Rosters**: Full team rosters with player details
- **Player Stats**: Individual player statistics by category
- **Team Records**: Win/loss records and performance metrics

### 🏆 Rankings & Conferences
- **Rankings**: AP Poll, Coaches Poll, and other ranking systems
- **Conferences**: Complete conference information and classifications

## Available Tools

### Core Game Tools
1. **getCFBGames** - Get college football games
   - Parameters: year, week, team, conference
   - Returns: Game schedules, scores, and basic info

2. **getCFBGameStats** - Get detailed team game statistics
   - Parameters: year, week, team, conference
   - Returns: Advanced team performance metrics

3. **getCFBPlays** - Get play-by-play data
   - Parameters: year, week (required), team, offense, defense
   - Returns: Individual play details and outcomes

### Team & Player Tools
4. **getCFBTeams** - Get team information
   - Parameters: year, conference
   - Returns: Team details, logos, colors, locations

5. **getCFBRoster** - Get team roster
   - Parameters: team (required), year
   - Returns: Complete player roster with positions and details

6. **getCFBPlayerStats** - Get player statistics
   - Parameters: year, team, player, category
   - Returns: Individual player performance data

7. **getCFBTeamRecords** - Get team season records
   - Parameters: year, team, conference
   - Returns: Win/loss records and performance metrics

### Rankings & Structure Tools
8. **getCFBRankings** - Get college football rankings
   - Parameters: year, week, season_type
   - Returns: AP Poll, Coaches Poll, and other rankings

9. **getCFBConferences** - Get conference information
   - Parameters: none
   - Returns: All conferences with classifications

## Example Usage

### Get Games for August 23, 2025
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

### Get Kansas State Roster
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

### Get Player Statistics
```json
{
  "method": "tools/call",
  "params": {
    "name": "getCFBPlayerStats",
    "arguments": {
      "year": 2024,
      "team": "Kansas State",
      "player": "Avery Johnson",
      "category": "passing"
    }
  }
}
```

### Get Power 5 Conference Teams
```json
{
  "method": "tools/call",
  "params": {
    "name": "getCFBTeams",
    "arguments": {
      "conference": "Big 12"
    }
  }
}
```

## Data Sources

- **Primary**: College Football Data API (collegefootballdata.com)
- **Coverage**: All FBS and FCS teams
- **Historical Data**: Multiple seasons available
- **Real-time**: Current season data updated regularly

## Power 5 Conferences Supported

- **SEC** (Southeastern Conference)
- **Big Ten** (Big Ten Conference)
- **Big 12** (Big 12 Conference)
- **ACC** (Atlantic Coast Conference)
- **Pac-12** (Pacific-12 Conference)

Plus all Group of 5 conferences and FCS divisions.

## Deployment

This server is designed for Railway deployment with:
- Environment variable for CFBD API key
- HTTP-based MCP protocol
- Health check endpoints
- Automatic scaling support

## API Key

Requires a College Football Data API key from collegefootballdata.com (free registration).

## Response Format

All tools return structured data with:
- **ok**: Success indicator
- **content_md**: Markdown formatted summary
- **data**: Complete JSON data payload
- **meta**: Timestamp and metadata

Perfect for analyzing college football matchups, player performance, and game predictions! 🏈