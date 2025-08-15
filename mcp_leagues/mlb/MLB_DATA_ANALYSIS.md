# MLB Stats API - Complete Data Extraction Analysis

## 🔍 Overview
The MLB Stats API (`https://statsapi.mlb.com/api/v1/`) provides comprehensive access to official MLB data. Based on the MCP implementation analysis, here are **all the data categories and specific tools** we can build.

## 📊 Available Data Categories & Tool Opportunities

### 1. 🗓️ **Schedule & Game Information**
**API Endpoint**: `/api/v1/schedule`

**Available Data Points**:
- Game IDs (`gamePk`)
- Start times (converted to ET timezone)
- Game status (scheduled, in-progress, completed, postponed)
- Home/away team information
- Venue details
- Official dates vs actual game times
- Doubleheader indicators

**Potential MCP Tools**:
- `getMLBScheduleET` - Daily schedule with ET timezone conversion
- `getMLBWeekSchedule` - Week-long schedule view
- `getMLBTeamSchedule` - Team-specific upcoming games
- `getMLBGameStatus` - Real-time game status updates

### 2. 🏟️ **Team Information**
**API Endpoint**: `/api/v1/teams`

**Available Data Points**:
- Team IDs and names
- Team abbreviations
- Location names (city)
- League (AL/NL) and division
- Home venue information
- Active status by season
- Team colors and logos (via extended endpoints)

**Potential MCP Tools**:
- `getMLBTeams` - Complete team directory
- `getMLBTeamInfo` - Detailed single team data
- `getMLBDivisions` - Division standings structure
- `getMLBVenues` - Stadium/venue information

### 3. 👥 **Player Rosters**
**API Endpoint**: `/api/v1/teams/{teamId}/roster`

**Available Data Points**:
- Player IDs and full names
- Jersey numbers
- Positions (C, 1B, 2B, SS, 3B, OF, P, DH)
- Player status (Active, 60-Day IL, etc.)
- Season-specific roster changes

**Potential MCP Tools**:
- `getMLBTeamRoster` - Active roster by team
- `getMLBPlayerInfo` - Individual player details
- `getMLBPositionPlayers` - Filter by position type
- `getMLBInjuryReport` - Players on disabled lists

### 4. ⚾ **Hitting Statistics** 
**API Endpoint**: `/api/v1/people/{playerId}/stats?stats=gameLog&group=hitting`

**Available Data Points**:
- **Basic**: `hits`, `atBats`, `runs`, `runsBattedIn`
- **Power**: `homeRuns`, `doubles`, `triples`, `totalBases`
- **Discipline**: `baseOnBalls`, `strikeOuts`, `hitByPitches`
- **Situational**: `leftOnBase`, `groundOuts`, `airOuts`
- **Advanced**: `plateAppearances`, `sacBunts`, `sacFlies`
- **Game Context**: ET date/time, opponent, venue

**Potential MCP Tools**:
- `getMLBPlayerLastN` - Last N games hitting stats
- `getMLBPlayerVsTeam` - Performance against specific teams
- `getMLBPlayerHome/Away` - Home/road splits
- `getMLBPlayerTrends` - Recent performance trends
- `getMLBPlayerProps` - Specific prop bet relevant stats

### 5. ⚾ **Pitching Statistics**
**API Endpoint**: `/api/v1/people/{playerId}/stats?stats=gameLog&group=pitching`

**Available Data Points**:
- **Basic**: `strikeOuts`, `baseOnBalls`, `hits`, `earnedRuns`
- **Innings**: `inningsPitched`, `pitchesThrown`
- **Results**: `wins`, `losses`, `saves`, `holds`
- **Advanced**: `homeRuns`, `hitBatsmen`, `wildPitches`
- **Efficiency**: `strikes`, `balls`, `pitchCount`

**Potential MCP Tools**:
- `getMLBPitcherLastN` - Recent pitching performances  
- `getMLBStarterStats` - Starting pitcher specific metrics
- `getMLBBullpenStats` - Relief pitcher performance
- `getMLBPitcherMatchups` - Historical vs specific teams

### 6. 🎯 **Game-Specific Data**
**API Endpoints**: `/api/v1/game/{gamePk}/*` (various sub-endpoints)

**Available Data Points**:
- Live game status and inning
- Box scores and line scores  
- Play-by-play data
- Individual player game performance
- Weather conditions
- Umpire assignments
- Injury updates during games

**Potential MCP Tools**:
- `getMLBGameBoxScore` - Complete game statistics
- `getMLBGameEvents` - Key plays and events
- `getMLBGameLineScore` - Inning-by-inning scoring
- `getMLBGameConditions` - Weather, field conditions

### 7. 📈 **Injury & Player Status**
**API Endpoints**: Team rosters + player status fields

**Available Data Points**:
- Disabled list status (10-Day IL, 60-Day IL, etc.)
- Return timeline estimates
- Injury descriptions
- Roster moves and transactions
- Player availability status

**Potential MCP Tools**:
- `getMLBInjuryReport` - Current injured players
- `getMLBPlayerStatus` - Individual availability  
- `getMLBRosterMoves` - Recent transactions
- `getMLBReturnTimeline` - Expected return dates

## 🛠️ **Recommended MCP Tool Set for Betting Intelligence**

### **Core Tools (Must-Have)**
1. **`getMLBScheduleET`** - Daily games with ET times
2. **`getMLBTeamRoster`** - Player IDs for prop hunting
3. **`getMLBPlayerLastN`** - Recent performance (hitting/pitching)
4. **`getMLBInjuryReport`** - Player availability updates

### **Enhanced Tools (High Value)**
5. **`getMLBPlayerProps`** - Prop-specific stats (hits, HRs, RBIs, Ks)
6. **`getMLBPitcherMatchups`** - Starter vs opposing team history
7. **`getMLBWeatherConditions`** - Game environment factors
8. **`getMLBGameStatus`** - Real-time postponement updates

### **Advanced Tools (Future)**
9. **`getMLBPlayerTrends`** - Hot/cold streak analysis
10. **`getMLBTeamStats`** - Aggregate team performance
11. **`getMLBVenueFactors`** - Stadium-specific impacts
12. **`getMLBUmpireData`** - Umpire tendencies (strike zone)

## 📋 **Data Sampling Examples**

### Player Hitting Stats (Last 5 Games)
```json
{
  "player_id": 677594,
  "games": [
    {
      "date_et": "2025-08-12",
      "hits": 2,
      "homeRuns": 1,
      "runsBattedIn": 3,
      "atBats": 4,
      "strikeOuts": 1
    }
  ],
  "aggregates": {
    "hits_avg": 2.2,
    "homeRuns_sum": 3,
    "runsBattedIn_avg": 1.8
  }
}
```

### Team Roster Sample
```json
{
  "teamId": 136,
  "players": [
    {
      "playerId": 677594,
      "fullName": "Julio Rodríguez", 
      "primaryNumber": "44",
      "position": "OF",
      "status": "Active"
    }
  ]
}
```

### Daily Schedule Sample  
```json
{
  "date_et": "2025-08-13",
  "games": [
    {
      "gamePk": 746789,
      "start_et": "2025-08-13T19:05:00-04:00",
      "status": "Scheduled",
      "home": {"teamId": 136, "name": "Seattle Mariners"},
      "away": {"teamId": 111, "name": "Boston Red Sox"},
      "venue": "T-Mobile Park"
    }
  ]
}
```

## 🎲 **Betting Integration Opportunities**

### **Player Props Data**
- **Hits**: Historical hit totals for over/under bets
- **Home Runs**: Power numbers vs specific pitchers
- **RBIs**: Run production in similar game contexts
- **Strikeouts**: Both hitter (avoiding) and pitcher (achieving)

### **Game Totals Data**
- Team offensive averages vs opposing pitcher types
- Weather impact on scoring (wind, temperature)
- Venue factors (hitter-friendly vs pitcher-friendly parks)
- Recent team offensive/defensive trends

### **Pitching Matchup Data**
- Starter ERA and WHIP trends
- Bullpen usage patterns and effectiveness  
- Team performance against left/right-handed pitching
- Historical head-to-head pitcher vs team performance

## 🚀 **Implementation Priority**

### **Phase 1: Essential Data Pipeline**
1. Schedule → Get daily games
2. Roster → Identify key players  
3. Player Stats → Last 5-10 games for props
4. Injury Status → Player availability

### **Phase 2: Advanced Analytics** 
1. Weather integration
2. Pitcher matchup analysis
3. Venue-specific adjustments
4. Trend analysis (hot/cold streaks)

### **Phase 3: Predictive Models**
1. ML models for prop predictions
2. Game total forecasting
3. Pitcher performance prediction
4. Injury impact analysis

---

**Bottom Line**: The MLB Stats API provides **comprehensive access** to schedules, rosters, detailed player statistics (hitting/pitching), injury reports, and game conditions. This gives us everything needed for **intelligent prop betting analysis** across all major MLB betting markets.