# Soccer Standings Test Tool

**Purpose**: Test the `getCompetitionStandings` tool to retrieve league tables/standings for EPL and La Liga.

## 🎯 What This Tool Tests

The `standings_test.py` script validates your Soccer MCP's ability to fetch **league tables** and **standings** for:
- **EPL (Premier League)** - Competition ID: `PL`
- **La Liga (Primera División)** - Competition ID: `PD`

## 🛠️ How to Run

```bash
python standings_test.py
```

## 📋 Test Scenarios

### 1. **Mock Data Test**
Tests with simulated league table data to verify tool functionality without using API quota.

### 2. **Current Season Standings**
Gets the live current league table:
```json
{
  "competition_id": "PL"
}
```

### 3. **Specific Season**
Gets historical league table for a specific year:
```json
{
  "competition_id": "PL",
  "season": 2025
}
```

### 4. **Standings After Matchday**
Gets league table as it stood after a specific round:
```json
{
  "competition_id": "PL",
  "matchday": 10
}
```

## 📊 Example API Call

### Input
```python
await self.call_mcp_tool("getCompetitionStandings", {
    "competition_id": "PL"
})
```

### Output
```json
{
  "ok": true,
  "content_md": "## Competition Standings\n\nStandings for competition PL",
  "data": {
    "source": "football_data_api",
    "competition_id": "PL",
    "standings": {
      "season": {
        "startDate": "2025-08-15",
        "endDate": "2026-05-24",
        "currentMatchday": 1
      },
      "standings": [{
        "stage": "REGULAR_SEASON",
        "type": "TOTAL",
        "table": [
          {
            "position": 1,
            "team": {
              "id": 65,
              "name": "Manchester City FC",
              "shortName": "Man City"
            },
            "playedGames": 10,
            "won": 8,
            "draw": 1,
            "lost": 1,
            "points": 25,
            "goalsFor": 24,
            "goalsAgainst": 8,
            "goalDifference": 16
          }
        ]
      }]
    }
  }
}
```

## 🏆 League Table Format

### Table Columns Explained
| Column | Description | Example |
|--------|-------------|---------|
| `position` | Current league position | 1, 2, 3... |
| `team.name` | Full team name | "Manchester City FC" |
| `team.shortName` | Abbreviated name | "Man City" |
| `playedGames` | Matches played | 10 |
| `won` | Games won | 8 |
| `draw` | Games drawn | 1 |
| `lost` | Games lost | 1 |
| `points` | Total points (3 for win, 1 for draw) | 25 |
| `goalsFor` | Goals scored | 24 |
| `goalsAgainst` | Goals conceded | 8 |
| `goalDifference` | Goal difference (+/-) | +16 |

### Example League Table Display
```
Pos Team                      P   W  D  L  GF GA  GD   Pts
--- ------------------------- --- -- -- -- -- -- ---- ---
1   Manchester City FC        10  8  1  1  24 8  +16  25
2   Arsenal FC                10  7  2  1  21 9  +12  23
3   Liverpool FC              10  6  3  1  18 7  +11  21
4   Chelsea FC                10  6  2  2  20 12 +8   20
5   Tottenham Hotspur FC      10  5  3  2  17 11 +6   18
```

## 📈 Success Metrics

### ✅ What Success Looks Like
- **Mock tests pass**: Tool handles test standings data correctly
- **Live API works**: Returns real league tables from Football-Data.org
- **Both leagues**: EPL and La Liga standings available
- **Complete tables**: All 20 teams with full statistics
- **Season context**: Correct season dates and current matchday

### 📊 Expected Test Results
```
✅ Mock EPL: SUCCESS (sample table data)
✅ Mock La Liga: SUCCESS (sample table data)
✅ Live EPL: SUCCESS (20 teams, current positions)
✅ Live La Liga: SUCCESS (20 teams, current positions)
✅ Specific Season: SUCCESS (historical data if available)
✅ After Matchday: SUCCESS (table after specific round)
```

**Overall**: **6/8 tests should pass** ✅

## 🎯 Use Cases

### For Betting Analysis
- **Top 4 race**: Identify Champions League qualification contenders
- **Relegation battle**: Spot teams fighting to avoid drop
- **Form analysis**: Recent points per game trends
- **Goal statistics**: High/low scoring teams for O/U bets

### For Sports Coverage
- **League summaries**: Current state of title race
- **Team comparisons**: Head-to-head in table
- **Milestone tracking**: Teams approaching records
- **Season narratives**: Surprise packages vs disappointments

### For Fantasy Sports
- **Team strength**: Pick players from top-scoring teams
- **Fixture difficulty**: Target players facing weak defenses
- **Clean sheet potential**: Goalkeepers from tight defenses
- **Captaincy**: Players from in-form teams

## 🏅 Key Table Insights

### **Championship Race Indicators**
- **Top 4**: Champions League qualification positions
- **Points gap**: Distance between title contenders
- **Goal difference**: Tiebreaker importance
- **Games in hand**: Potential points available

### **Relegation Battle Signs**
- **Bottom 3**: Automatic relegation zone
- **Safety margin**: Points needed to avoid drop
- **Form trends**: Recent wins/losses crucial
- **Goal difference**: Often decides relegation

### **European Competition**
- **Positions 1-4**: Champions League
- **Positions 5-6**: Europa League  
- **Position 7**: Conference League (depending on cup results)

## 🔄 Season Phases

### **Early Season** (Matchdays 1-10)
- Tables not fully representative
- Small sample sizes
- Focus on goal difference trends

### **Mid Season** (Matchdays 11-25)
- Patterns becoming clearer
- True contenders emerging
- Form more meaningful

### **Business End** (Matchdays 26-38)
- Every point crucial
- Real table positions
- Pressure situations

## 💡 Pro Tips

1. **Check `currentMatchday`** to understand how many games played
2. **Goal difference matters** - often decides final positions
3. **Points per game** more meaningful than total points early season
4. **Home/Away splits** available in detailed standings
5. **Recent form** (last 6 games) often more important than overall position

## 🚨 Troubleshooting

**Empty standings**:
- Season might not have started yet
- Check if competition is currently active
- Early season might have limited data

**Missing teams**:
- Verify 20 teams expected for EPL/La Liga
- Check if league restructuring occurred
- API might have data delays

**Outdated positions**:
- Standings update after match completion
- Check `lastUpdated` timestamp in response
- Live matches won't reflect in table until finished

## 📊 Data Freshness

- **Updates**: After each completed match
- **Delay**: Usually within 1-2 hours of final whistle  
- **Live matches**: Positions don't change until match ends
- **Weekend updates**: Major changes after weekend fixtures

## 🎯 Integration Ideas

### **Alerts & Notifications**
- Position changes after matchdays
- Teams entering/leaving relegation zone
- Gap changes in title race

### **Trend Analysis**
- Points per game over time
- Goal scoring trends
- Defensive record improvements

### **Betting Applications**
- Outright winner odds correlation
- Relegation market insights
- European qualification chances

## 📝 Next Steps

After successful standings testing:
1. **Test team matches**: Run `team_matches_test.py`
2. **Test competitions**: Run `competitions_test.py` 
3. **Cross-reference**: Compare with schedule data
4. **Historical analysis**: Use specific season/matchday data
5. **Integration**: Build league table tracking features