# Soccer MCP Server

A dedicated MCP (Model Context Protocol) server for soccer/football data using the Football-Data.org API.

## Features

Comprehensive soccer data across major leagues including:
- **Premier League** (England)
- **La Liga** (Spain)  
- **Bundesliga** (Germany)
- **Serie A** (Italy)
- **Ligue 1** (France)
- **UEFA Champions League**
- And many more competitions

## Available Tools

### 1. `getCompetitions`
Get available soccer competitions from Football-Data.org
- **Parameters**: 
  - `areas` (optional): Comma-separated area IDs to filter by
  - `use_test_mode` (optional): Use mock data for testing

### 2. `getCompetitionMatches`
Get matches for a specific competition
- **Parameters**: 
  - `competition_id` (required): Competition ID (e.g., 'PL', '2021')
  - `date_from` (optional): Start date (YYYY-MM-DD)
  - `date_to` (optional): End date (YYYY-MM-DD)
  - `matchday` (optional): Specific matchday
  - `status` (optional): Match status (SCHEDULED, LIVE, FINISHED, etc.)

### 3. `getCompetitionStandings`
Get standings/table for a specific competition
- **Parameters**:
  - `competition_id` (required): Competition ID
  - `season` (optional): Season year (e.g., 2024)
  - `matchday` (optional): Specific matchday

### 4. `getCompetitionTeams`
Get teams in a specific competition
- **Parameters**:
  - `competition_id` (required): Competition ID
  - `season` (optional): Season year

### 5. `getTeamMatches`
Get matches for a specific team
- **Parameters**:
  - `team_id` (required): Team ID
  - `date_from` (optional): Start date (YYYY-MM-DD)
  - `date_to` (optional): End date (YYYY-MM-DD)
  - `season` (optional): Season year
  - `status` (optional): Match status
  - `venue` (optional): HOME or AWAY
  - `limit` (optional): Number of matches to return

### 6. `getMatchDetails`
Get details for a specific match
- **Parameters**:
  - `match_id` (required): Match ID

### 7. `getTopScorers`
Get top scorers for a specific competition
- **Parameters**:
  - `competition_id` (required): Competition ID
  - `season` (optional): Season year
  - `limit` (optional): Number of top scorers (default: 10)

## Environment Variables

- `FOOTBALL_DATA_API_KEY`: Your Football-Data.org API key
- `PORT`: Server port (default: 8080)

## Testing

Run the test suite to verify functionality:

```bash
python test_soccer_mcp.py
```

## API Data Source

This MCP uses the [Football-Data.org API](https://www.football-data.org/) which provides:
- Real-time match data
- Comprehensive league standings
- Team and player information
- Historical match results
- Top scorer statistics

## Deployment

Configured for Railway deployment with:
- `railway.toml` - Railway configuration
- `requirements.txt` - Python dependencies
- Health check endpoint at `/`
- MCP endpoint at `/mcp`

## Usage Examples

### Get Premier League standings
```json
{
  "name": "getCompetitionStandings",
  "arguments": {
    "competition_id": "PL"
  }
}
```

### Get today's matches for a competition
```json
{
  "name": "getCompetitionMatches", 
  "arguments": {
    "competition_id": "PL",
    "date_from": "2025-08-15",
    "date_to": "2025-08-15"
  }
}
```

### Get Arsenal's recent matches
```json
{
  "name": "getTeamMatches",
  "arguments": {
    "team_id": 57,
    "limit": 5,
    "status": "FINISHED"
  }
}
```

## Test Mode

All tools support `use_test_mode: true` parameter to return mock data for development and testing without using API quota.