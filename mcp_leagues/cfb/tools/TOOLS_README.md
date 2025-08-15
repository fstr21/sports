# CFB MCP Server - Tools Testing

This directory contains individual tool test scripts for the College Football MCP Server.

## Available Test Tools

### 🏈 games.py
Tests the games endpoint with various scenarios:
- August 23, 2025 games (Week 1)
- Kansas State games for 2024
- Big 12 conference games

**Usage:**
```bash
python tools/games.py
```

### 👥 roster.py
Tests the roster endpoint for team rosters:
- Kansas State 2024 roster
- Iowa State 2024 roster
- Stanford 2024 roster

**Usage:**
```bash
python tools/roster.py
```

### 📊 player_stats.py
Tests player statistics endpoints:
- Individual player stats (Avery Johnson)
- Team category stats (Kansas State passing)
- Conference category stats (Big 12 rushing)

**Usage:**
```bash
python tools/player_stats.py
```

### 🏆 rankings.py
Tests college football rankings:
- Final 2024 rankings
- Week 1 2024 rankings
- Postseason rankings

**Usage:**
```bash
python tools/rankings.py
```

## Running All Tests

To run all tool tests:

```bash
cd mcp_leagues/cfb
python tools/games.py
python tools/roster.py
python tools/player_stats.py
python tools/rankings.py
```

## Test Results

Each test script will:
- ✅ Show successful API calls with data counts
- 📊 Display sample data and breakdowns
- ❌ Report any errors or issues
- 📈 Provide insights into data structure

## API Key

All tests use the embedded API key for College Football Data API. The tests verify:
- API connectivity
- Data availability
- Response formats
- Error handling

## Expected Output

Each test provides detailed output showing:
- Number of records found
- Sample data entries
- Data categorization
- Success/failure status

Perfect for validating the MCP server functionality before deployment! 🚀