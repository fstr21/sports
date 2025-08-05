# EPL Team Stats & Standings Data Checklist

This checklist outlines every piece of data you can reliably get for English Premier League team statistics and league standings using ESPN's API. Use this as a guide for designing queries for your MCP.

---

### **Data Source Details**

* **Method**: `GET` (REST API)
* **Base URL**: `https://site.api.espn.com/apis/v2/sports/soccer/`
* **League Code**: `eng.1` (English Premier League)
* **Endpoint**: `/standings`
* **Parameters**: 
  - `season`: Season year (e.g., "2024" for 2024-25 season)
* **Full URL Example**: `https://site.api.espn.com/apis/v2/sports/soccer/eng.1/standings?season=2024`
* **Data Format**: JSON
* **Headers Required**: User-Agent header to mimic browser request
* **Update Frequency**: Updated after each matchday

---

### **Season Metadata**
- [ ] **Season Year**: "2024" (represents 2024-25 season)
- [ ] **League Name**: "English Premier League"
- [ ] **Total Teams**: 20 teams
- [ ] **Total Games**: 38 games per team (380 total matches)
- [ ] **Competition Format**: Round-robin, home and away
- [ ] **Points System**: 3 points for win, 1 for draw, 0 for loss

---

### **Team Information**

#### **Team Identification**
- [ ] **Team Name**: "Liverpool" (full display name)
- [ ] **Team ID**: "364" (unique ESPN identifier)
- [ ] **League Position**: 1-20 ranking
- [ ] **Qualification Status**: Champions League, Europa League, etc.

#### **Complete Team List (2024-25)**
- [ ] **Liverpool** (ID: 364) - Champions League
- [ ] **Arsenal** (ID: 359) - Champions League  
- [ ] **Manchester City** (ID: 382) - Champions League
- [ ] **Chelsea** (ID: 363) - Champions League
- [ ] **Newcastle United** (ID: 361) - Champions League
- [ ] **Aston Villa** (ID: 362) - Europa League
- [ ] **Nottingham Forest** (ID: 393) - Conference League qualifying
- [ ] **Brighton & Hove Albion** (ID: 331)
- [ ] **AFC Bournemouth** (ID: 349)
- [ ] **Brentford** (ID: 337)
- [ ] **Fulham** (ID: 370)
- [ ] **Crystal Palace** (ID: 384) - Europa League
- [ ] **Everton** (ID: 368)
- [ ] **West Ham United** (ID: 371)
- [ ] **Manchester United** (ID: 360)
- [ ] **Wolverhampton Wanderers** (ID: 380)
- [ ] **Tottenham Hotspur** (ID: 367) - Champions League
- [ ] **Leicester City** (ID: 375) - Relegation
- [ ] **Ipswich Town** (ID: 373) - Relegation
- [ ] **Southampton** (ID: 376) - Relegation

---

### **League Statistics (Per Team)**

#### **Core Statistics**
- [ ] **Position (#)**: League ranking (1-20)
- [ ] **Games Played (P)**: Total matches played (38)
- [ ] **Wins (W)**: Total victories
- [ ] **Draws (D)**: Total draws
- [ ] **Losses (L)**: Total defeats
- [ ] **Points (Pts)**: Total points accumulated
- [ ] **Goals For (GF)**: Total goals scored
- [ ] **Goals Against (GA)**: Total goals conceded
- [ ] **Goal Difference (GD)**: Goals for minus goals against

#### **Sample Team Record**
```
1   Liverpool                 364   38   25   9    4    86    41    +45   84    Champions League
```

#### **Statistical Breakdown**
- [ ] **Win Percentage**: Calculated from wins/games played
- [ ] **Points Per Game**: Average points per match
- [ ] **Goals Per Game**: Average goals scored per match
- [ ] **Goals Conceded Per Game**: Average goals allowed per match
- [ ] **Clean Sheets**: Matches without conceding (derived)
- [ ] **Form Guide**: Recent performance (available in other endpoints)

---

### **Qualification & Competition Notes**

#### **European Competition Qualification**
- [ ] **Champions League**: Top 4 positions (1st-4th)
- [ ] **Europa League**: 5th-6th positions + cup winners
- [ ] **Conference League**: 7th position qualifying
- [ ] **Special Cases**: Cup winners may alter qualification

#### **Relegation Information**
- [ ] **Relegation Zone**: Bottom 3 positions (18th-20th)
- [ ] **Championship Promotion**: Teams relegated to Championship
- [ ] **Survival**: Teams finishing 17th and above stay up

#### **Note Descriptions**
- [ ] **"Champions League"**: Automatic qualification for UCL
- [ ] **"Europa League"**: Qualification for UEL
- [ ] **"Conference League qualifying"**: UECL qualifying rounds
- [ ] **"Relegation"**: Relegated to Championship

---

### **Data Structure & API Response**

#### **JSON Structure**
```json
{
  "children": [
    {
      "standings": {
        "entries": [
          {
            "team": {
              "id": "364",
              "displayName": "Liverpool"
            },
            "stats": [
              {
                "name": "rank",
                "displayValue": "1"
              },
              {
                "abbreviation": "GP",
                "displayValue": "38"
              },
              {
                "abbreviation": "W",
                "displayValue": "25"
              }
            ],
            "note": {
              "description": "Champions League"
            }
          }
        ]
      }
    }
  ]
}
```

#### **Statistics Mapping**
- [ ] **GP**: Games Played
- [ ] **W**: Wins
- [ ] **D**: Draws  
- [ ] **L**: Losses
- [ ] **P**: Points
- [ ] **F**: Goals For
- [ ] **A**: Goals Against
- [ ] **GD**: Goal Difference

---

### **Historical Context & Analysis**

#### **Season Performance Indicators**
- [ ] **Title Race**: Top teams competing for championship
- [ ] **European Spots**: Competition for continental qualification
- [ ] **Relegation Battle**: Teams fighting to avoid drop
- [ ] **Mid-Table**: Teams with no specific objectives

#### **Notable 2024-25 Season Trends**
- [ ] **Liverpool Dominance**: Leading with 84 points
- [ ] **Top 4 Race**: Tight competition for Champions League spots
- [ ] **Relegation Fight**: Clear bottom 3 teams
- [ ] **Goal Scoring**: High-scoring teams vs defensive sides

---

### **Technical Implementation**

#### **Required Libraries**
- [ ] **requests**: HTTP requests to ESPN API
- [ ] **json**: JSON response parsing
- [ ] **Standard Libraries**: Built-in Python modules

#### **Request Configuration**
- [ ] **User-Agent Header**: Required to avoid API blocking
- [ ] **Season Parameter**: Specify which season to retrieve
- [ ] **Error Handling**: HTTP status code validation
- [ ] **Response Processing**: JSON parsing and data extraction

#### **Data Processing**
- [ ] **Statistics Extraction**: Parse stats array for each team
- [ ] **Ranking Calculation**: Extract position from stats
- [ ] **Note Processing**: Extract qualification/relegation status
- [ ] **Table Formatting**: Display in readable format

---

### **Error Handling & Reliability**

#### **Common Issues**
- [ ] **API Blocking**: User-Agent header prevents blocking
- [ ] **Season Parameter**: Must specify correct season year
- [ ] **Data Structure Changes**: ESPN may modify JSON structure
- [ ] **Rate Limiting**: Avoid too many rapid requests

#### **Fallback Strategies**
- [ ] **Default Values**: Use "-" for missing statistics
- [ ] **Error Messages**: Clear indication of API failures
- [ ] **Data Validation**: Verify expected data structure
- [ ] **Graceful Degradation**: Continue processing despite errors

---

### **Data Quality & Reliability**

#### **Highly Reliable Data**
✅ **Team Names**: Consistent official team names  
✅ **Team IDs**: Stable ESPN identifiers  
✅ **League Positions**: Accurate current standings  
✅ **Match Statistics**: Complete win/draw/loss records  
✅ **Goal Statistics**: Accurate goals for/against data  
✅ **Points Totals**: Correct points calculations  

#### **Moderately Reliable Data**
⚠️ **Qualification Notes**: May change based on cup results  
⚠️ **API Availability**: Dependent on ESPN service status  
⚠️ **Real-time Updates**: May have slight delays after matches  

---

### **Use Cases for Sports Analysis**

#### **League Analysis**
- [ ] **Title Race Tracking**: Monitor championship contenders
- [ ] **Form Analysis**: Compare team performances
- [ ] **Goal Statistics**: Analyze attacking and defensive strength
- [ ] **Points Projections**: Predict final league positions

#### **Betting Applications**
- [ ] **Outright Markets**: Season-long betting opportunities
- [ ] **Relegation Betting**: Bottom 3 predictions
- [ ] **Top 4 Betting**: Champions League qualification
- [ ] **Over/Under Season Points**: Team total points betting

#### **Fantasy Premier League**
- [ ] **Team Strength**: Assess team quality for player selection
- [ ] **Fixture Difficulty**: Use league position for difficulty rating
- [ ] **Goal Expectations**: Predict clean sheets and goals
- [ ] **Form Indicators**: Recent performance trends

#### **Database Integration**
- [ ] **Historical Tracking**: Store season-by-season data
- [ ] **Team Performance**: Long-term team analysis
- [ ] **League Evolution**: Track changes over time
- [ ] **Cross-Season Comparison**: Compare different seasons

---

### **Advanced Analytics**

#### **Derived Metrics**
- [ ] **Points Per Game**: Total points ÷ games played
- [ ] **Win Percentage**: (Wins ÷ games played) × 100
- [ ] **Goals Per Game**: Goals for ÷ games played
- [ ] **Defensive Record**: Goals against ÷ games played
- [ ] **Goal Difference Per Game**: Goal difference ÷ games played

#### **Performance Categories**
- [ ] **Elite Teams**: Top 6 traditional "Big Six"
- [ ] **European Contenders**: Teams 7th-10th
- [ ] **Mid-Table**: Teams 11th-14th
- [ ] **Relegation Candidates**: Teams 15th-20th

---

### **Integration Examples**

#### **MCP Tool Integration**
```python
def get_epl_standings(season="2024"):
    """Get current EPL standings with team stats"""
    url = f"https://site.api.espn.com/apis/v2/sports/soccer/eng.1/standings"
    params = {"season": season}
    headers = {"User-Agent": "Mozilla/5.0..."}
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    return {
        "standings": parse_standings(data),
        "season": season,
        "last_updated": datetime.now().isoformat()
    }
```

#### **Database Schema**
```sql
CREATE TABLE epl_standings (
    season VARCHAR(10),
    team_id VARCHAR(10),
    team_name VARCHAR(100),
    position INT,
    games_played INT,
    wins INT,
    draws INT,
    losses INT,
    goals_for INT,
    goals_against INT,
    goal_difference INT,
    points INT,
    qualification_note VARCHAR(100),
    updated_at TIMESTAMP,
    PRIMARY KEY (season, team_id)
);
```

---

**Last Updated**: February 5, 2025  
**Data Source**: ESPN Soccer API  
**League**: English Premier League (eng.1)  
**Endpoint**: `/standings` with season parameter  
**Reliability**: High for completed matches, updated after each matchday