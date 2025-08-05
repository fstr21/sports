# EPL Game Summary Data Checklist

This checklist outlines every piece of data you can reliably get for a completed English Premier League game using ESPN's soccer API. Use this as a guide for designing queries for your MCP.

---

### **Data Source Details**

* **Method**: `GET` (REST API)
* **Base URL**: `http://site.api.espn.com/apis/site/v2/sports/soccer/`
* **League Code**: `eng.1` (English Premier League)
* **Endpoint**: `/summary`
* **Parameters**: 
  - `event`: Game ID (e.g., "704513")
* **Full URL Example**: `http://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/summary?event=704513`
* **Data Format**: JSON
* **Update Frequency**: Real-time during games, final after completion

---

### **Game Metadata**
- [ ] **Game ID**: "704513"
- [ ] **Game UID**: "s:600~l:700~e:704513"
- [ ] **Season Info**: 
    - Year: 2024
    - Name: "2024-25 English Premier League"
    - Type: 12654
- [ ] **Game Date**: "2025-02-03T20:00Z" (ISO format)
- [ ] **Venue Information**:
    - Venue ID: "249"
    - Stadium Name: "Stamford Bridge"
    - Location: "London, England"
    - Capacity: 40,834
    - Grass surface type
- [ ] **Competition Details**:
    - Neutral Site: false
    - Boxscore Available: true
    - Commentary Available: true
    - Play-by-Play Available: true

---

### **Team Information**

#### **Team Identification & Metadata**
- [ ] **Team ID**: "363" (Chelsea), "371" (West Ham United)
- [ ] **Team UID**: "s:600~t:363"
- [ ] **Team GUID**: "c43a00b9-2826-72b3-77a0-62730abc936e"
- [ ] **Location**: "Chelsea"
- [ ] **Team Name**: "Chelsea"
- [ ] **Nickname**: "Blues"
- [ ] **Abbreviation**: "CHE"
- [ ] **Display Names**: 
    - Full: "Chelsea"
    - Short: "Chelsea"
- [ ] **Team Colors**:
    - Primary: "144992"
    - Alternate: "ffeeee"
- [ ] **Team Form**: "WWWWW" (last 5 games: W=Win, L=Loss, D=Draw)
- [ ] **Home/Away Status**: "home" or "away"
- [ ] **Winner Status**: true/false

#### **Team Logos & Links**
- [ ] **Team Logos**:
    - Default: "https://a.espncdn.com/i/teamlogos/soccer/500/363.png"
    - Dark Mode: "https://a.espncdn.com/i/teamlogos/soccer/500-dark/363.png"
    - Dimensions: 500x500
- [ ] **Team Links**:
    - Clubhouse: "https://www.espn.com/soccer/club/_/id/363/chelsea"

---

### **Match Results & Scoring**

#### **Final Score**
- [ ] **Team Scores**: "2" vs "0"
- [ ] **Half-Time Scores**: 
    - First Half: "0" vs "0"
    - Second Half: "2" vs "0"

#### **Team Records**
- [ ] **Season Record**: "12-7-5" (Wins-Draws-Losses)
- [ ] **Home Record**: "7-3-2"
- [ ] **Away Record**: "5-4-3"

---

### **Player Rosters & Squad Information**

#### **Squad Lists (Per Team)**
- [ ] **Home Squad**: Complete player roster
- [ ] **Away Squad**: Complete player roster
- [ ] **Player Details**:
    - Player ID: Unique ESPN identifier
    - Full Name: "Cole Palmer"
    - Jersey Number: "#10"
    - Position: "Midfielder"
    - Age: 22
    - Height: "6'1\""
    - Weight: "161 lbs"
    - Nationality: "England"

#### **Coaching Staff**
- [ ] **Manager Information**:
    - Name: "Enzo Maresca"
    - Nationality: "Italy"
    - Age: 44

---

### **Recent Form & Head-to-Head**

#### **Team Form (Last 5 Games)**
- [ ] **Recent Results**: Array of last 5 games per team
- [ ] **Game Details**:
    - Game ID: "704502"
    - Date: "2025-01-25T17:30Z"
    - Opponent: Team details with ID and logos
    - Score: "3-1"
    - Result: "L" (Loss), "W" (Win), "D" (Draw)
    - Home/Away: "@" or "vs"
    - League: "English Premier League"

#### **Head-to-Head History**
- [ ] **Historical Matchups**: Previous games between teams
- [ ] **H2H Statistics**: Win/loss records between teams

---

### **Match Events & Key Moments**

#### **Key Events**
- [ ] **Event ID**: "44633857"
- [ ] **Event Type**: "goal", "yellow-card", "red-card", "substitution"
- [ ] **Time**: Clock time and period
- [ ] **Player Involved**: Player name and ID
- [ ] **Team**: Which team the event belongs to
- [ ] **Description**: Text description of the event

#### **Goals & Scoring**
- [ ] **Goal Details**:
    - Scorer: Player name and ID
    - Assist: Player name and ID (if applicable)
    - Time: Minute of the goal
    - Score at time: Running score
    - Goal type: Regular, penalty, own goal, etc.

---

### **Live Commentary & Play-by-Play**

#### **Commentary Feed**
- [ ] **Commentary Entries**: Chronological match commentary
- [ ] **Sequence Number**: Order of commentary entries
- [ ] **Time Stamps**: When each commentary was made
- [ ] **Commentary Text**: Detailed match descriptions

#### **Play-by-Play Data**
- [ ] **Individual Plays**: Detailed breakdown of match events
- [ ] **Player Actions**: Passes, shots, tackles, etc.
- [ ] **Location Data**: Where on the pitch events occurred
- [ ] **Success/Failure**: Whether actions were successful

---

### **Betting & Odds Information**

#### **Betting Lines**
- [ ] **Odds Providers**: Multiple sportsbook odds
- [ ] **Bet Types**:
    - Moneyline (Match Winner)
    - Spread/Handicap
    - Over/Under (Total Goals)
- [ ] **Opening Lines**: Initial odds
- [ ] **Closing Lines**: Final odds before kickoff

#### **Pick Center**
- [ ] **Expert Predictions**: Professional picks
- [ ] **Consensus Data**: Popular betting choices
- [ ] **Betting Percentages**: Public betting distribution

---

### **Media & Content**

#### **News Articles**
- [ ] **Related News**: Premier League news articles
- [ ] **Article Links**: Direct links to ESPN articles
- [ ] **Headlines**: Current news headlines

#### **Videos**
- [ ] **Match Highlights**: Video content
- [ ] **Video IDs**: Unique identifiers for video content
- [ ] **Video Metadata**: Duration, description, thumbnails

#### **Images**
- [ ] **Match Photos**: Game photography
- [ ] **Player Images**: Individual player photos
- [ ] **Team Logos**: High-resolution team graphics

---

### **League Standings & Context**

#### **Current Standings**
- [ ] **League Table**: Full Premier League standings
- [ ] **Team Positions**: Current league position
- [ ] **Points**: Total points accumulated
- [ ] **Goal Difference**: Goals for minus goals against
- [ ] **Form Guide**: Recent performance indicators

#### **Season Statistics**
- [ ] **Games Played**: Total matches in season
- [ ] **Goals For/Against**: Season totals
- [ ] **Home/Away Splits**: Performance by venue

---

### **Technical Metadata**

#### **API Response Details**
- [ ] **Response Size**: ~21,431 lines of JSON
- [ ] **Data Freshness**: Real-time updates during matches
- [ ] **Sync URL**: Live data synchronization endpoint
- [ ] **Game Switcher**: Navigation between related games

#### **ESPN Integration**
- [ ] **ESPN+ Availability**: Streaming information
- [ ] **Watch ESPN**: Viewing options
- [ ] **Mobile App**: Deep linking capabilities

---

### **Data Quality & Reliability**

#### **Highly Reliable Data**
✅ **Team Information**: Names, IDs, logos, colors consistently formatted  
✅ **Match Results**: Final scores, records, standings data  
✅ **Player Rosters**: Complete squad lists with detailed player info  
✅ **Game Metadata**: Dates, venues, competition details  
✅ **Historical Data**: Form, head-to-head, season records  

#### **Moderately Reliable Data**
⚠️ **Live Commentary**: May vary in detail and timing  
⚠️ **Betting Odds**: Dependent on sportsbook availability  
⚠️ **Media Content**: Video/image availability may change  

#### **Real-Time Data**
📊 **Live Updates**: Scores, events, commentary during matches  
📊 **Post-Match**: Complete statistics and final data  
📊 **Historical**: Archived data for completed seasons  

---

### **Sample Data Structures**

#### **Team Record**
```json
{
  "id": "363",
  "name": "Chelsea",
  "abbreviation": "CHE",
  "displayName": "Chelsea",
  "color": "144992",
  "form": "WWWWW",
  "score": "2",
  "record": {
    "total": "12-7-5",
    "home": "7-3-2",
    "away": "5-4-3"
  },
  "logos": [
    {
      "href": "https://a.espncdn.com/i/teamlogos/soccer/500/363.png",
      "width": 500,
      "height": 500
    }
  ]
}
```

#### **Game Header**
```json
{
  "id": "704513",
  "uid": "s:600~l:700~e:704513",
  "season": {
    "year": 2024,
    "name": "2024-25 English Premier League"
  },
  "date": "2025-02-03T20:00Z",
  "venue": {
    "id": "249",
    "fullName": "Stamford Bridge",
    "address": {
      "city": "London",
      "country": "England"
    },
    "capacity": 40834
  }
}
```

#### **Player Record**
```json
{
  "id": "4262",
  "fullName": "Cole Palmer",
  "jersey": "10",
  "position": {
    "name": "Midfielder",
    "abbreviation": "M"
  },
  "age": 22,
  "height": "6'1\"",
  "weight": "161 lbs",
  "birthPlace": {
    "country": "England"
  }
}
```

---

### **Use Cases for Sports Analysis & Betting**

#### **Match Analysis**
- [ ] Team form and momentum tracking using 5-game form strings
- [ ] Head-to-head historical performance analysis
- [ ] Home/away performance splits for venue advantages
- [ ] Player availability and squad rotation patterns

#### **Betting Applications**
- [ ] **Match Result Betting**: Winner predictions using form and H2H data
- [ ] **Goal Markets**: Over/under betting using team scoring records
- [ ] **Player Props**: Individual player performance betting
- [ ] **Live Betting**: Real-time odds and in-game wagering

#### **Fantasy Sports**
- [ ] **Player Selection**: Squad information for fantasy lineups
- [ ] **Form Analysis**: Recent performance for captain choices
- [ ] **Fixture Difficulty**: Opponent strength assessment
- [ ] **Injury Updates**: Player availability tracking

#### **Database Integration**
- [ ] **Unique Identifiers**: Consistent ESPN IDs for data relationships
- [ ] **Historical Tracking**: Season-long performance monitoring
- [ ] **Cross-Reference**: Link to other ESPN soccer APIs
- [ ] **Data Normalization**: Standardized formats across leagues

---

**Last Updated**: February 5, 2025  
**Data Source**: ESPN Soccer API  
**League**: English Premier League (eng.1)  
**Endpoint**: `/summary` with event parameter  
**Reliability**: High for completed games, real-time updates during live matches