# La Liga Game Summary Data Checklist

This checklist outlines every piece of data you can reliably get for a completed Spanish La Liga game using ESPN's soccer API. Use this as a guide for designing queries for your MCP.

---

### **Data Source Details**

* **Method**: `GET` (REST API)
* **Base URL**: `http://site.api.espn.com/apis/site/v2/sports/soccer/`
* **League Code**: `esp.1` (Spanish La Liga)
* **Endpoint**: `/summary`
* **Parameters**: 
  - `event`: Game ID (e.g., "704884")
* **Full URL Example**: `http://site.api.espn.com/apis/site/v2/sports/soccer/esp.1/summary?event=704884`
* **Data Format**: JSON
* **Update Frequency**: Real-time during games, final after completion

---

### **Game Metadata**
- [ ] **Game ID**: "704884"
- [ ] **Game UID**: "s:600~l:740~e:704884"
- [ ] **Season Info**: 
    - Year: 2024
    - Name: "2024-25 LALIGA"
    - Type: 12655
- [ ] **Game Date**: "2025-02-10T20:00Z" (ISO format)
- [ ] **Venue Information**:
    - Stadium Name: "Son Moix"
    - Location: "Palma, Spain"
    - Capacity: 23,142
    - Grass surface type
- [ ] **Competition Details**:
    - Neutral Site: false
    - Boxscore Available: true
    - Commentary Available: true
    - Play-by-Play Available: true
    - ESPN+ Available: true

---

### **Team Information**

#### **Team Identification & Metadata**
- [ ] **Team ID**: "84" (Mallorca), "97" (Osasuna)
- [ ] **Team UID**: "s:600~t:84"
- [ ] **Team GUID**: "aac87b2a-e910-4080-a8a8-b42a2050b2e0"
- [ ] **Location**: "Mallorca"
- [ ] **Team Name**: "Mallorca"
- [ ] **Abbreviation**: "MLL"
- [ ] **Display Names**: 
    - Full: "Mallorca"
    - Short: "Mallorca"
- [ ] **Team Colors**:
    - Primary: "C8142F" (Red)
    - Alternate: "ccff00" (Yellow)
- [ ] **Team Form**: "DLLWL" (last 5 games: W=Win, L=Loss, D=Draw)
- [ ] **Home/Away Status**: "home" or "away"
- [ ] **Winner Status**: true/false

#### **Team Logos & Links**
- [ ] **Team Logos**:
    - Default: "https://a.espncdn.com/i/teamlogos/soccer/500/84.png"
    - Dark Mode: "https://a.espncdn.com/i/teamlogos/soccer/500-dark/84.png"
    - Dimensions: 500x500
- [ ] **Team Links**:
    - Clubhouse: "https://www.espn.com/soccer/club/_/id/84/mallorca"

---

### **Match Results & Scoring**

#### **Final Score**
- [ ] **Team Scores**: "1" vs "2"
- [ ] **Half-Time Scores**: 
    - First Half: "0" vs "1"
    - Second Half: "1" vs "1"

#### **Team Records**
- [ ] **Season Record**: "9-4-10" (Wins-Draws-Losses)
- [ ] **Home Record**: "6-2-4"
- [ ] **Away Record**: "3-2-6"
- [ ] **Points**: Total league points accumulated

---

### **Player Rosters & Squad Information**

#### **Squad Lists (Per Team)**
- [ ] **Home Squad**: Complete player roster
- [ ] **Away Squad**: Complete player roster
- [ ] **Player Details**:
    - Player ID: Unique ESPN identifier
    - Full Name: "Ante Budimir"
    - Jersey Number: "#17"
    - Position: "Forward"
    - Age: 33
    - Height: "6'3\""
    - Weight: "187 lbs"
    - Nationality: "Croatia"

#### **Coaching Staff**
- [ ] **Manager Information**:
    - Name: "Vicente Moreno"
    - Nationality: "Spain"
    - Age: 50

---

### **Recent Form & Head-to-Head**

#### **Team Form (Last 5 Games)**
- [ ] **Recent Results**: Array of last 5 games per team
- [ ] **Game Details**:
    - Game ID: "704870"
    - Date: "2025-02-01T17:30Z"
    - Opponent: Team details with ID and logos
    - Score: "2-0"
    - Result: "L" (Loss), "W" (Win), "D" (Draw)
    - Home/Away: "@" or "vs"
    - League: "Spanish LALIGA"
    - Additional Competitions: "Spanish Copa del Rey", "Spanish Supercopa"

#### **Head-to-Head History**
- [ ] **Historical Matchups**: Previous games between teams
- [ ] **H2H Statistics**: Win/loss records between teams

---

### **Match Events & Key Moments**

#### **Key Events**
- [ ] **Event ID**: Unique identifier for each event
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
- [ ] **Commentary Text**: Detailed match descriptions in Spanish and English

#### **Play-by-Play Data**
- [ ] **Individual Plays**: Detailed breakdown of match events
- [ ] **Player Actions**: 
    - Shots: "Attempt blocked. Lucas Torró (Osasuna) header from the centre of the box is blocked"
    - Passes: Successful and unsuccessful pass attempts
    - Tackles: Defensive actions
    - Fouls: Disciplinary events
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
- [ ] **Related News**: La Liga news articles
- [ ] **Article Links**: Direct links to ESPN articles
- [ ] **Headlines**: Current news headlines
- [ ] **Player News**: Transfer rumors, injury updates

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
- [ ] **League Table**: Full La Liga standings
- [ ] **Team Positions**: Current league position
- [ ] **Points**: Total points accumulated
- [ ] **Goal Difference**: Goals for minus goals against
- [ ] **Form Guide**: Recent performance indicators
- [ ] **Champions League Qualification**: Top 4 positions
- [ ] **Europa League Spots**: 5th-7th positions
- [ ] **Relegation Zone**: Bottom 3 positions

#### **Season Statistics**
- [ ] **Games Played**: Total matches in season
- [ ] **Goals For/Against**: Season totals
- [ ] **Home/Away Splits**: Performance by venue

---

### **Spanish-Specific Features**

#### **Multi-Competition Tracking**
- [ ] **La Liga**: Primary league competition
- [ ] **Copa del Rey**: Spanish domestic cup
- [ ] **Spanish Supercopa**: Super cup competition
- [ ] **European Competitions**: Champions League, Europa League

#### **Cultural Elements**
- [ ] **Spanish Commentary**: Native language play-by-play
- [ ] **Local Time Zones**: CET/CEST time references
- [ ] **Regional Rivalries**: El Clásico, Madrid Derby, etc.

---

### **Technical Metadata**

#### **API Response Details**
- [ ] **Response Size**: ~20,351 lines of JSON
- [ ] **Data Freshness**: Real-time updates during matches
- [ ] **Sync URL**: Live data synchronization endpoint
- [ ] **Game Switcher**: Navigation between related games

#### **ESPN Integration**
- [ ] **ESPN+ Availability**: Streaming information (often available)
- [ ] **Watch ESPN**: Viewing options
- [ ] **Mobile App**: Deep linking capabilities
- [ ] **International Coverage**: Global accessibility

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
⚠️ **Player Names**: Accented characters and Spanish naming conventions

#### **Real-Time Data**
📊 **Live Updates**: Scores, events, commentary during matches  
📊 **Post-Match**: Complete statistics and final data  
📊 **Historical**: Archived data for completed seasons  

---

### **Sample Data Structures**

#### **Team Record**
```json
{
  "id": "84",
  "name": "Mallorca",
  "abbreviation": "MLL",
  "displayName": "Mallorca",
  "color": "C8142F",
  "form": "DLLWL",
  "score": "1",
  "record": {
    "total": "9-4-10",
    "home": "6-2-4",
    "away": "3-2-6"
  },
  "logos": [
    {
      "href": "https://a.espncdn.com/i/teamlogos/soccer/500/84.png",
      "width": 500,
      "height": 500
    }
  ]
}
```

#### **Game Header**
```json
{
  "id": "704884",
  "uid": "s:600~l:740~e:704884",
  "season": {
    "year": 2024,
    "name": "2024-25 LALIGA"
  },
  "date": "2025-02-10T20:00Z",
  "venue": {
    "fullName": "Son Moix",
    "address": {
      "city": "Palma",
      "country": "Spain"
    },
    "capacity": 23142
  }
}
```

#### **Player Record**
```json
{
  "id": "4567",
  "fullName": "Ante Budimir",
  "jersey": "17",
  "position": {
    "name": "Forward",
    "abbreviation": "F"
  },
  "age": 33,
  "height": "6'3\"",
  "weight": "187 lbs",
  "birthPlace": {
    "country": "Croatia"
  }
}
```

#### **Play-by-Play Example**
```json
{
  "id": "44674467",
  "clock": {
    "displayValue": "14'"
  },
  "text": "Attempt blocked. Lucas Torró (Osasuna) header from the centre of the box is blocked. Assisted by Rubén García with a cross.",
  "play": {
    "type": {
      "text": "Shot Blocked"
    }
  },
  "shortText": "Lucas Torró Shot Blocked"
}
```

---

### **Use Cases for Sports Analysis & Betting**

#### **Match Analysis**
- [ ] Team form and momentum tracking using 5-game form strings
- [ ] Head-to-head historical performance analysis
- [ ] Home/away performance splits for venue advantages
- [ ] Multi-competition performance (Liga vs Copa del Rey)

#### **Betting Applications**
- [ ] **Match Result Betting**: Winner predictions using form and H2H data
- [ ] **Goal Markets**: Over/under betting using team scoring records
- [ ] **Player Props**: Individual player performance betting
- [ ] **Live Betting**: Real-time odds and in-game wagering
- [ ] **Spanish Market Specifics**: Local betting preferences and patterns

#### **Fantasy Sports**
- [ ] **Player Selection**: Squad information for fantasy lineups
- [ ] **Form Analysis**: Recent performance for captain choices
- [ ] **Fixture Difficulty**: Opponent strength assessment
- [ ] **Injury Updates**: Player availability tracking
- [ ] **La Liga Fantasy**: Spanish fantasy football applications

#### **Database Integration**
- [ ] **Unique Identifiers**: Consistent ESPN IDs for data relationships
- [ ] **Historical Tracking**: Season-long performance monitoring
- [ ] **Cross-Reference**: Link to other ESPN soccer APIs
- [ ] **Multi-League**: Compare with other European leagues
- [ ] **International Players**: Track players across national teams

---

**Last Updated**: February 5, 2025  
**Data Source**: ESPN Soccer API  
**League**: Spanish La Liga (esp.1)  
**Endpoint**: `/summary` with event parameter  
**Reliability**: High for completed games, real-time updates during live matches