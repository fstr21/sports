# Soccer MCP - Complete Data Analysis & Capabilities

## 🔍 Overview
The Soccer MCP (`https://soccermcp-production.up.railway.app/mcp`) provides comprehensive access to soccer/football data via the Football-Data.org API v4. This analysis documents **all available data categories and specific tools** for soccer betting intelligence and analytics.

## 📊 Available Data Categories & Tool Capabilities

### 1. 🏆 **Competition Information**
**API Endpoint**: `/v4/competitions`

**Available Data Points**:
- Competition IDs and names (Premier League, La Liga, etc.)
- Competition types (LEAGUE, CUP, PLAYOFFS)
- Area/country information
- Season details and current status
- Competition emblems and codes

**MCP Tool**: `getCompetitions`
- Lists all available soccer competitions
- Filters by area/country if specified
- Returns competition metadata for further queries

### 2. 📅 **Match Schedules & Results**
**API Endpoint**: `/v4/competitions/{id}/matches`

**Available Data Points**:
- Match IDs and UTC timestamps
- Team information (home/away)
- Match status (SCHEDULED, LIVE, FINISHED, etc.)
- Final scores and half-time scores
- Matchday numbers and competition stages
- Venue information (when available)
- Referee assignments

**MCP Tool**: `getCompetitionMatches`
- Flexible date range filtering
- Status-based filtering (finished, upcoming, live)
- Matchday-specific queries
- Competition-wide match listings

### 3. 📊 **League Standings & Tables**
**API Endpoint**: `/v4/competitions/{id}/standings`

**Available Data Points**:
- Team positions and points
- Games played, won, drawn, lost
- Goals for, goals against, goal difference
- Form indicators (recent results)
- Home/away record splits
- League table progression

**MCP Tool**: `getCompetitionStandings`
- Current league tables
- Historical standings by matchday
- Season-specific standings
- Complete team performance metrics

### 4. 👥 **Team Information**
**API Endpoint**: `/v4/competitions/{id}/teams`

**Available Data Points**:
- Team IDs, names, and abbreviations
- Team crests and colors
- Founded dates and venues
- Squad information (when available)
- Competition participation
- Team addresses and websites

**MCP Tool**: `getCompetitionTeams`
- Teams by competition
- Season-specific team lists
- Complete team metadata

### 5. 🎯 **Individual Team Analysis**
**API Endpoint**: `/v4/teams/{id}/matches`

**Available Data Points**:
- Team-specific match history
- Home/away performance splits
- Results against specific opponents
- Seasonal performance tracking
- Venue-specific results
- Competition-filtered matches

**MCP Tool**: `getTeamMatches`
- Team-specific fixture lists
- Date range filtering
- Home/away venue filtering
- Competition-specific results
- Status-based match filtering

### 6. 🔍 **Detailed Match Analysis**
**API Endpoint**: `/v4/matches/{id}`

**Available Data Points**:
- Complete match information
- Score details (full-time, half-time)
- Match officials (referees)
- Competition and season context
- Team lineup information (limited)
- Match venue details

**MCP Tool**: `getMatchDetails`
- Individual match deep-dive
- Complete match context
- Official match data

**⚠️ Limitations**: Detailed statistics (shots, corners, possession) not available on free tier

### 7. 🥅 **Top Scorers & Player Performance**
**API Endpoint**: `/v4/competitions/{id}/scorers`

**Available Data Points**:
- Player names and goal counts
- Team affiliations
- Season-specific scoring records
- Player IDs for further analysis
- Goal-per-game ratios
- Competition-specific rankings

**MCP Tool**: `getTopScorers`
- Leading goalscorers by competition
- Configurable result limits
- Season-specific data
- Player performance rankings

## 🛠️ **Recommended Tool Set for Soccer Betting Intelligence**

### **Core Tools (Essential)**
1. **`getCompetitions`** - Available leagues and competitions
2. **`getCompetitionStandings`** - Team strength and form analysis
3. **`getCompetitionMatches`** - Fixture lists and results
4. **`getTopScorers`** - Player performance for goalscorer bets

### **Enhanced Tools (High Value)**
5. **`getTeamMatches`** - Team-specific performance analysis
6. **`getMatchDetails`** - Individual match context
7. **`getCompetitionTeams`** - Team directory and metadata

## 📋 **Data Sampling Examples**

### Competition Standings (Premier League)
```json
{
  "competition_id": "2021",
  "standings": [
    {
      "position": 1,
      "team": {
        "id": 64,
        "name": "Liverpool FC",
        "shortName": "Liverpool",
        "tla": "LIV"
      },
      "playedGames": 1,
      "won": 1,
      "draw": 0,
      "lost": 0,
      "points": 3,
      "goalsFor": 4,
      "goalsAgainst": 2,
      "goalDifference": 2
    }
  ]
}
```

### Match Results Sample
```json
{
  "matches": [
    {
      "id": 537785,
      "utcDate": "2025-08-15T19:00:00Z",
      "status": "FINISHED",
      "homeTeam": {
        "id": 64,
        "name": "Liverpool FC"
      },
      "awayTeam": {
        "id": 1044,
        "name": "AFC Bournemouth"
      },
      "score": {
        "winner": "HOME_TEAM",
        "fullTime": {"home": 4, "away": 2},
        "halfTime": {"home": 1, "away": 0}
      }
    }
  ]
}
```

### Top Scorers Sample
```json
{
  "scorers": [
    {
      "player": {
        "id": 123456,
        "name": "Antoine Semenyo"
      },
      "team": {
        "id": 1044,
        "name": "AFC Bournemouth"
      },
      "goals": 2
    }
  ]
}
```

## 🎲 **Betting Integration Opportunities**

### **Match Outcome Markets**
- **1X2 (Win/Draw/Win)**: Use league standings and team form
- **Double Chance**: Combine with head-to-head records
- **Draw No Bet**: Analyze draw frequency patterns

### **Goal Markets**
- **Over/Under Goals**: Team averages from standings data
- **Both Teams to Score**: Goal-scoring consistency analysis
- **Exact Score**: Historical score pattern analysis

### **Player Markets**
- **Anytime Goalscorer**: Top scorer data and form
- **First Goalscorer**: Player scoring patterns
- **Player to Score 2+**: Multi-goal frequency analysis

### **Team Performance Markets**
- **Clean Sheet**: Defensive records from standings
- **Team Total Goals**: Offensive averages and trends
- **Win to Nil**: Combined offensive/defensive analysis

## 🚫 **Data Limitations (Free Tier)**

### **Not Available**
- Detailed match statistics (shots, corners, possession)
- Player-level match performance data
- Card and booking information
- Substitution and lineup details
- Advanced tactical metrics

### **Workarounds**
- Use team-level aggregates from standings
- Focus on goal-based analysis
- Leverage historical patterns
- Combine multiple data points for insights

## 🎯 **Betting Analysis Strategies**

### **Team Strength Assessment**
1. **League Position**: Current standings position
2. **Points Per Game**: Efficiency metric
3. **Goal Difference**: Offensive vs defensive balance
4. **Form Analysis**: Recent win/loss patterns
5. **Home/Away Splits**: Venue-specific performance

### **Goal Pattern Analysis**
1. **Team Averages**: Goals for/against per game
2. **High/Low Scoring**: Games with 3+ goals frequency
3. **Both Teams Score**: Mutual goal-scoring rate
4. **Clean Sheet Rate**: Defensive consistency
5. **Score Draw Frequency**: 0-0, 1-1, 2-2 patterns

### **Player Performance Analysis**
1. **Top Scorer Form**: Current goal-scoring leaders
2. **Goals Per Game**: Individual scoring rates
3. **Team Distribution**: Goal spread across players
4. **Competition Specific**: Performance in specific leagues

## 🚀 **Implementation Priority**

### **Phase 1: Core Data Pipeline**
1. **Competitions** → Identify available leagues
2. **Standings** → Team strength assessment
3. **Matches** → Recent results and upcoming fixtures
4. **Top Scorers** → Player performance data

### **Phase 2: Advanced Analysis**
1. **Team-specific analysis** → Historical performance
2. **Head-to-head records** → Direct matchup analysis
3. **Form trends** → Recent performance patterns
4. **Venue analysis** → Home advantage factors

### **Phase 3: Predictive Models**
1. **Goal expectation models** → Over/Under predictions
2. **Result probability** → 1X2 outcome forecasting
3. **Player scoring models** → Goalscorer predictions
4. **Form-based adjustments** → Recent performance weighting

## 📈 **Available Competitions**

### **Major European Leagues**
- **Premier League (EPL)** - ID: 2021
- **La Liga (Spain)** - ID: 2014
- **Bundesliga (Germany)** - ID: 2002
- **Serie A (Italy)** - ID: 2019
- **Ligue 1 (France)** - ID: 2015

### **International Competitions**
- **UEFA Champions League** - ID: 2001
- **UEFA Europa League** - ID: 2146
- **European Championship** - ID: 2018

### **Other Leagues**
- **Championship (England)** - ID: 2016
- **Eredivisie (Netherlands)** - ID: 2003
- **Primeira Liga (Portugal)** - ID: 2017

## 💡 **Best Practices for Betting Analysis**

### **Data Quality**
- Focus on recent form (last 5-10 games)
- Weight home/away performance differently
- Consider competition-specific performance
- Account for seasonal variations

### **Market Selection**
- Prioritize markets with good data coverage
- Avoid prop bets requiring detailed statistics
- Focus on team-level and goal-based markets
- Use player data for goalscorer markets only

### **Analysis Approach**
- Combine multiple data points for insights
- Use historical patterns for context
- Consider external factors (injuries, suspensions)
- Validate predictions against actual results

---

**Bottom Line**: The Soccer MCP provides **comprehensive access** to competition standings, match results, team performance, and top scorer data. This enables **intelligent betting analysis** for fundamental soccer markets including match outcomes, goal totals, and anytime goalscorer bets, while avoiding markets that require detailed match statistics not available on the free tier.