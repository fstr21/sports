# MLB MCP Testing Suite

Comprehensive testing tools for the MLB MCP server. These scripts allow you to test all 8 MLB MCP tools and see their actual output data.

## 🚀 Quick Start

### Simple Interactive Runner (Recommended for exploring)
```bash
cd C:\Users\fstr2\Desktop\sports\mcp_leagues\mlb\testing
python simple_tool_runner.py
```

This provides an interactive menu where you can:
- Test each tool individually
- See raw JSON responses
- Get human-readable summaries
- Use sample team/player IDs

### Comprehensive Test Suite (For full validation)
```bash
python comprehensive_mlb_test.py
```

Runs all tools with multiple scenarios and saves detailed results to JSON files.

### Individual Tool Tests (For specific testing)
```bash
python individual_tool_tests.py --tool schedule
python individual_tool_tests.py --tool teams --season 2024
python individual_tool_tests.py --tool roster --team-id 147
python individual_tool_tests.py --tool player-stats --player-id 592450
```

## 📋 Available MLB MCP Tools

### 1. getMLBScheduleET
**Purpose**: Get MLB game schedules for specific dates (Eastern Time)

**Test Examples**:
```bash
# Today's games
python simple_tool_runner.py
# Choose option 1

# Specific date
python individual_tool_tests.py --tool schedule --date 2025-08-21
```

**Sample Output**:
- Game matchups (Away @ Home)
- Start times in Eastern Time
- Game status (Scheduled, Live, Final)
- Venue information

### 2. getMLBTeams  
**Purpose**: Get active MLB teams for a season

**Test Examples**:
```bash
# Current season teams
python simple_tool_runner.py
# Choose option 2

# Specific season
python individual_tool_tests.py --tool teams --season 2024
```

**Sample Output**:
- 30 MLB teams
- Team IDs, names, abbreviations
- League/division information
- Home venues

### 3. getMLBTeamRoster
**Purpose**: Get team rosters with player details

**Test Examples**:
```bash
# Yankees roster (Team ID: 147)
python simple_tool_runner.py
# Choose option 3, enter: 147

# Command line
python individual_tool_tests.py --tool roster --team-id 147
```

**Sample Output**:
- Player names and IDs
- Jersey numbers
- Positions
- Roster status

### 4. getMLBPlayerLastN
**Purpose**: Get last N games statistics for players

**Test Examples**:
```bash
# Aaron Judge hitting stats (Player ID: 592450)
python simple_tool_runner.py
# Choose option 4, then option 1, enter: 592450

# Command line
python individual_tool_tests.py --tool player-stats --player-id 592450
```

**Sample Output**:
- Game-by-game statistics
- Aggregate totals and averages
- Hitting: hits, home runs, RBIs, at-bats
- Pitching: strikeouts, walks, ERA, WHIP

### 5. getMLBPitcherMatchup
**Purpose**: Detailed pitcher analysis and matchup data

**Test Examples**:
```bash
# Gerrit Cole analysis (Pitcher ID: 543037)
python simple_tool_runner.py
# Choose option 5, enter: 543037
```

**Sample Output**:
- Recent start performance
- ERA, WHIP, K/9 rates
- Game-by-game pitching lines
- Advanced metrics

### 6. getMLBTeamForm
**Purpose**: Team standings and recent form

**Test Examples**:
```bash
# Yankees form (Team ID: 147)
python simple_tool_runner.py
# Choose option 6, enter: 147
```

**Sample Output**:
- Win-loss record
- Win percentage
- Current streak
- Games back from division lead
- Home/away splits

### 7. getMLBPlayerStreaks
**Purpose**: Player streak analysis and consistency patterns

**Test Examples**:
```bash
# Aaron Judge streaks (Player ID: 592450)
python simple_tool_runner.py
# Choose option 7, enter: 592450
```

**Sample Output**:
- Current hit streak
- Multi-hit game frequency
- Home run streaks
- Consistency metrics

### 8. getMLBTeamScoringTrends
**Purpose**: Team offensive and defensive scoring patterns

**Test Examples**:
```bash
# Yankees scoring trends (Team ID: 147)
python simple_tool_runner.py
# Choose option 8, enter: 147
```

**Sample Output**:
- Runs per game (offense)
- Runs allowed per game (pitching)
- Run differential
- Season totals

## 🎯 Sample IDs for Testing

### Teams
- **Yankees**: 147
- **Dodgers**: 119
- **Guardians**: 114
- **Marlins**: 146
- **Mariners**: 136
- **Red Sox**: 111
- **Astros**: 117
- **Mets**: 121

### Players (Batters)
- **Aaron Judge**: 592450
- **Mookie Betts**: 605141
- **Julio Rodriguez**: 677594
- **Jose Altuve**: 514888
- **Freddie Freeman**: 518692

### Pitchers
- **Gerrit Cole**: 543037
- **Clayton Kershaw**: 477132
- **Shane Bieber**: 669456
- **Jacob deGrom**: 594798

## 🔍 What You'll See

### Terminal Output Format
Each tool shows:
1. **Call Information**: Tool name and arguments
2. **Raw JSON Response**: Complete API response
3. **Human-Readable Summary**: Key data points extracted

### Example Terminal Output
```
🔧 Calling: getMLBScheduleET
📋 Arguments: {"date": "2025-08-21"}
--------------------------------------------------

✅ SUCCESS - Raw Response:
============================================================
{
  "ok": true,
  "content_md": "## MLB Schedule for 2025-08-21 (ET)\n\nFound 15 games",
  "data": {
    "source": "mlb_stats_api",
    "date_et": "2025-08-21",
    "count": 15,
    "games": [
      {
        "gamePk": 776759,
        "start_et": "2025-08-21T13:10:00-04:00",
        "status": "Scheduled",
        "home": {"teamId": 118, "name": "Kansas City Royals"},
        "away": {"teamId": 120, "name": "Washington Nationals"},
        "venue": "Kauffman Stadium"
      }
      // ... more games
    ]
  }
}
============================================================

📊 QUICK SUMMARY:
------------------------------
📅 Schedule for 2025-08-21: 15 games
  1. Washington Nationals @ Kansas City Royals (2025-08-21T13:10:00-04:00) - Scheduled
  2. Miami Marlins @ Cleveland Guardians (2025-08-21T18:10:00-04:00) - Scheduled
  3. Toronto Blue Jays @ Los Angeles Angels (2025-08-21T21:38:00-04:00) - Scheduled
  ... and 12 more games
------------------------------
```

## 💾 Saved Results

### JSON Output Files
Test results are saved to timestamped JSON files:
- `comprehensive_test_results_YYYYMMDD_HHMMSS.json`
- `schedule_test_YYYYMMDD_HHMMSS.json`
- `teams_test_YYYYMMDD_HHMMSS.json`
- etc.

### File Contents
Each JSON file contains:
- Test metadata (timestamp, server URL)
- Raw API responses
- Test success/failure status
- Summary statistics

## 🛠️ Dependencies

Install required Python packages:
```bash
pip install httpx asyncio
```

## ⚡ Quick Testing Workflow

1. **Start with Simple Runner**:
   ```bash
   python simple_tool_runner.py
   ```

2. **Choose a tool** from the menu (1-8)

3. **Follow prompts** to enter team/player IDs

4. **Review output** - both raw JSON and summary

5. **Try different scenarios** with various IDs/dates

6. **Run comprehensive tests** when ready:
   ```bash
   python comprehensive_mlb_test.py
   ```

## 🎯 Testing Goals

These scripts help you:
- **Understand data structure**: See exactly what each tool returns
- **Validate functionality**: Confirm tools work with real data
- **Explore capabilities**: Test different parameters and scenarios
- **Debug issues**: Identify problems with specific tools
- **Performance testing**: See response times and data volumes

## 📞 Support

If any tool fails or returns unexpected data:
1. Check the error message in the terminal output
2. Verify team/player IDs are correct
3. Test with known working IDs from the samples above
4. Check network connectivity to the MCP server
5. Review the saved JSON files for detailed error information