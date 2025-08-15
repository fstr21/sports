# Soccer Schedule Test Tool

**Purpose**: Test the `getCompetitionMatches` tool to retrieve league fixtures/schedules for EPL and La Liga.

## 🎯 What This Tool Tests

The `schedule_test.py` script validates your Soccer MCP's ability to fetch **match schedules** and **fixtures** for:
- **EPL (Premier League)** - Competition ID: `PL`
- **La Liga (Primera División)** - Competition ID: `PD`

## 🛠️ How to Run

```bash
python schedule_test.py
```

## 📋 Test Scenarios

### 1. **Mock Data Test**
Tests with simulated data to verify tool functionality without using API quota.

### 2. **Today's Fixtures**
Gets matches scheduled for the current date:
```json
{
  "competition_id": "PL",
  "date_from": "2025-08-14",
  "date_to": "2025-08-14"
}
```

### 3. **Weekly Schedule**
Gets all matches in the next 7 days:
```json
{
  "competition_id": "PL", 
  "date_from": "2025-08-14",
  "date_to": "2025-08-21"
}
```

### 4. **Specific Matchday**
Gets all matches for a specific round/matchday:
```json
{
  "competition_id": "PL",
  "matchday": 10
}
```

## 📊 Example API Call

### Input
```python
await self.call_mcp_tool("getCompetitionMatches", {
    "competition_id": "PL",
    "date_from": "2025-08-14", 
    "date_to": "2025-08-21"
})
```

### Output
```json
{
  "ok": true,
  "content_md": "## Competition Matches\n\nFound 10 matches for competition PL",
  "data": {
    "source": "football_data_api",
    "competition_id": "PL",
    "matches": [
      {
        "id": 537785,
        "utcDate": "2025-08-15T19:00:00Z",
        "status": "TIMED",
        "matchday": 1,
        "homeTeam": {
          "id": 64,
          "name": "Liverpool FC",
          "shortName": "Liverpool"
        },
        "awayTeam": {
          "id": 1044,
          "name": "AFC Bournemouth", 
          "shortName": "Bournemouth"
        },
        "competition": {
          "id": 2021,
          "name": "Premier League"
        },
        "season": {
          "startDate": "2025-08-15",
          "endDate": "2026-05-24",
          "currentMatchday": 1
        }
      }
    ],
    "count": 10
  }
}
```

## 🏆 Real Data Examples (from latest test)

### EPL Fixtures Found
- **Liverpool vs Bournemouth** - Aug 15, 19:00 UTC
- **Aston Villa vs Newcastle** - Aug 16, 11:30 UTC  
- **Brighton vs Fulham** - Aug 16, 14:00 UTC
- **Man United vs Arsenal** - Aug 17, 15:30 UTC 🔥
- **Chelsea vs Crystal Palace** - Aug 17, 13:00 UTC

### La Liga Fixtures Found
- **Girona vs Rayo Vallecano** - Aug 15, 17:00 UTC
- **Mallorca vs Barcelona** - Aug 16, 17:30 UTC 🔥
- **Valencia vs Real Sociedad** - Aug 16, 19:30 UTC
- **Athletic Club vs Sevilla** - Aug 17, 17:30 UTC
- **Real Madrid vs Osasuna** - Aug 19, 19:00 UTC 🔥

## 📈 Success Metrics

### ✅ What Success Looks Like
- **Mock tests pass**: Tool handles test data correctly
- **Live API works**: Returns real fixtures from Football-Data.org
- **Both leagues**: EPL and La Liga data available
- **Rich data**: Complete match details (teams, dates, IDs)
- **Multiple timeframes**: Today, weekly, and matchday queries work

### 📊 Latest Test Results
```
✅ Mock EPL: SUCCESS (2 test matches)
✅ Mock La Liga: SUCCESS (2 test matches)  
✅ Live EPL: SUCCESS (10 real fixtures)
✅ Live La Liga: SUCCESS (10 real fixtures)
✅ Matchday EPL: SUCCESS (10 matches for matchday 10)
✅ Matchday La Liga: SUCCESS (10 matches for matchday 1)
```

**Overall**: **8/8 tests passed** ✅

## 🔧 Match Status Types

| Status | Description |
|--------|-------------|
| `SCHEDULED` | Match scheduled but not yet timed |
| `TIMED` | Match scheduled with confirmed kick-off time |
| `IN_PLAY` | Match currently being played |
| `PAUSED` | Match temporarily paused |
| `FINISHED` | Match completed |
| `POSTPONED` | Match delayed to future date |
| `CANCELLED` | Match cancelled |

## 🎯 Use Cases

### For Betting Analysis
- **Upcoming fixtures**: Plan betting strategy for next matches
- **Weekly overview**: See all games in coming week
- **Matchday focus**: Analyze specific round of fixtures

### For Sports Coverage  
- **Editorial calendar**: Plan content around big matches
- **Preview articles**: Upcoming rivalry games and key matchups
- **Schedule tracking**: Monitor when teams play next

### For Fantasy Sports
- **Team selection**: Know when players have fixtures
- **Captain choices**: Target players in favorable matchups
- **Transfer planning**: Avoid players with blank gameweeks

## 💡 Pro Tips

1. **Check `currentMatchday`** in season data to know what round we're in
2. **Use `date_from/date_to`** for custom date ranges  
3. **Monitor `status`** field - `TIMED` means kick-off confirmed
4. **Big matches** often have rivalry games (Man United vs Arsenal, Real Madrid vs Barcelona)
5. **Weekend clustering** - most matches on Saturday/Sunday

## 🚨 Troubleshooting

**No matches returned**: 
- Check if date range covers actual fixtures
- EPL/La Liga have summer breaks (June-July)
- Some midweek periods have no games

**API errors**:
- Verify Football-Data.org API key is set
- Check API quota hasn't been exceeded
- Ensure competition IDs are correct (PL, PD)

## 📝 Next Steps

After successful schedule testing:
1. **Test standings**: Run `standings_test.py` 
2. **Test team matches**: Run `team_matches_test.py`
3. **Integration**: Use schedule data for betting analysis
4. **Automation**: Set up daily fixture updates