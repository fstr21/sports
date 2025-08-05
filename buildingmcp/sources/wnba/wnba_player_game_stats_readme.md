# WNBA Player Game Stats Data Checklist

This checklist outlines every piece of data you can reliably get for individual player performance in a completed WNBA game based on ESPN boxscore pages. Use this as a guide for designing queries for your MCP.

---

### **Data Source Details**

* **Method**: `GET` (Web Scraping)
* **Source URL**: `https://www.espn.com/wnba/boxscore/_/gameId/{game_id}`
* **Example Game ID**: `401736292`
* **Data Format**: HTML parsing → structured JSON
* **Update Frequency**: Real-time during games, final after completion

---

### **Game Metadata**
- [ ] **Game ID**: "401736292"
- [ ] **Page Title**: "Liberty 87-78 Sun (Aug 3, 2025) Box Score - ESPN"
- [ ] **Scraped Timestamp**: ISO format timestamp
- [ ] **Source URL**: Full ESPN boxscore URL

---

### **Game Summary**
- [ ] **Final Score**: 
    - Home Team: 87 points
    - Away Team: 78 points
- [ ] **Quarter-by-Quarter Scores**:
    - [ ] **Quarter 1**: NY 25, CONN 19
    - [ ] **Quarter 2**: NY 20, CONN 19  
    - [ ] **Quarter 3**: NY 21, CONN 19
    - [ ] **Quarter 4**: NY 21, CONN 21
- [ ] **Team Names**: 
    - "New York Liberty"
    - "Connecticut Sun"

---

### **Individual Player Statistics (Per Team)**

#### **Core Player Stats (Available for each player)**
- [ ] **Player Name**: "Sabrina Ionescu" (cleaned format)
- [ ] **Player ID**: "4066533" (unique ESPN identifier)
- [ ] **Jersey Number**: "#20" (extracted from name data)
- [ ] **Minutes Played**: "30" (MM format)
- [ ] **Points**: 3 (integer)
- [ ] **Field Goals**: "1-7" (made-attempted)
- [ ] **3-Point Shots**: "1-3" (made-attempted)  
- [ ] **Free Throws**: "0-0" (made-attempted)
- [ ] **Offensive Rebounds**: 0
- [ ] **Defensive Rebounds**: 5
- [ ] **Total Rebounds**: 5
- [ ] **Assists**: 4
- [ ] **Steals**: 0
- [ ] **Blocks**: 0
- [ ] **Turnovers**: 4
- [ ] **Personal Fouls**: 4
- [ ] **Plus/Minus**: "+7"

#### **Player Status Categories**
- [ ] **Starters**: Players in starting lineup
- [ ] **Bench Players**: Reserve players who played
- [ ] **DNP Status**: Did Not Play reasons
    - [ ] "DNP-RIGHT KNEE" (injury)
    - [ ] "DNP-RIGHT CALF" (injury)
    - [ ] "DNP-COACH'S DECISION" (coach's choice)

---

### **Team Information & IDs**

#### **Team Identification**
- [ ] **Team Name**: "New York Liberty" (full name)
- [ ] **Team ID**: "ny" (ESPN team identifier)
- [ ] **Team Abbreviation**: "NY" (from quarter scores)

#### **Team Aggregate Stats (Per Team)**
- [ ] **Total Field Goals**: "31-62" (50.0%)
- [ ] **Total 3-Pointers**: "4-17" (23.5%)
- [ ] **Total Free Throws**: "21-23" (91.3%)
- [ ] **Total Rebounds**: 35
    - [ ] Offensive Rebounds: 7
    - [ ] Defensive Rebounds: 28
- [ ] **Total Assists**: 24
- [ ] **Total Steals**: 7
- [ ] **Total Blocks**: 3
- [ ] **Total Turnovers**: 20
- [ ] **Total Personal Fouls**: 20
- [ ] **Total Points**: 87

---

### **Unique Identifiers & Links**

#### **Player Identification System**
- [ ] **ESPN Player IDs**: Unique numerical identifiers (e.g., "4066533" for Sabrina Ionescu)
- [ ] **Player Profile URLs**: Direct links to ESPN player pages
- [ ] **ID Extraction Method**: Parsed from ESPN player profile links in boxscore
- [ ] **ID Reliability**: ~96% success rate (23/24 players in test case)
- [ ] **Missing ID Cases**: Primarily hyphenated names (e.g., "Olivia Nelson-Ododa")

#### **Team Identification System**  
- [ ] **ESPN Team IDs**: Team abbreviation codes (e.g., "ny", "conn")
- [ ] **Team Profile URLs**: Direct links to ESPN team pages
- [ ] **Full Team Names**: Complete team names (e.g., "New York Liberty")
- [ ] **Team Abbreviations**: Short codes for quarter scores (e.g., "NY", "CONN")

#### **Sample ID Mappings**
```
Player Examples:
- Sabrina Ionescu → ID: 4066533
- Tina Charles → ID: 918 (veteran with low ID)
- Jonquel Jones → ID: 2999101
- Breanna Stewart → ID: 2998928

Team Examples:  
- New York Liberty → ID: "ny"
- Connecticut Sun → ID: "conn"
```

---

### **Advanced Data Available**

#### **Page Structure Analysis**
- [ ] **Total HTML Elements**: 1,549
- [ ] **Tables Found**: 6 (structured data tables)
- [ ] **Team Elements**: 33 (team-related HTML elements)
- [ ] **Score Elements**: 138 (score-related elements)
- [ ] **CSS Classes**: 100+ unique classes for styling

#### **Additional Metadata**
- [ ] **All Links**: 50+ links from the page
- [ ] **Images**: 23 images (logos, player photos)
- [ ] **Script Data**: 2 JavaScript sections with potential JSON data
- [ ] **Meta Tags**: SEO and social media metadata

---

### **Data Quality & Reliability**

#### **Highly Reliable Data**
✅ **Player Names & IDs**: Consistently formatted with unique ESPN identifiers  
✅ **Team Names & IDs**: Full names and ESPN team abbreviations  
✅ **Basic Stats**: MIN, PTS, REB, AST, STL, BLK, TO, PF  
✅ **Shooting Stats**: FG, 3PT, FT with made/attempted format  
✅ **Team Totals**: Aggregated team statistics with percentages  
✅ **Quarter Scores**: Period-by-period scoring breakdown  

#### **Moderately Reliable Data**
⚠️ **Plus/Minus**: Available but formatting may vary  
⚠️ **DNP Reasons**: Text-based, may have variations  
⚠️ **Player Status**: Starter/bench designation  
⚠️ **Hyphenated Names**: Some players with hyphens may have missing IDs  

#### **Additional Context Data**
📊 **Page Metadata**: Timestamps, URLs, page structure  
📊 **Player Profile Links**: Direct links to ESPN player pages  
📊 **Team Profile Links**: Direct links to ESPN team pages  
📊 **CSS Classes**: For future scraping improvements  

---

### **Sample Data Structures**

#### **Individual Player Record**
```json
{
  "name": "Sabrina Ionescu",
  "player_id": "4066533",
  "minutes": "30",
  "points": 3,
  "field_goals": "1-7",
  "three_pointers": "1-3", 
  "free_throws": "0-0",
  "offensive_rebounds": 0,
  "defensive_rebounds": 5,
  "rebounds": 5,
  "assists": 4,
  "steals": 0,
  "blocks": 0,
  "turnovers": 4,
  "fouls": 4,
  "plus_minus": "+7"
}
```

#### **Team Record Structure**
```json
{
  "team_name": "Liberty",
  "team_id": "ny",
  "players": [...],
  "team_totals": {
    "field_goals": "31-62",
    "three_pointers": "4-17",
    "free_throws": "21-23",
    "offensive_rebounds": 7,
    "defensive_rebounds": 28,
    "total_rebounds": 35,
    "assists": 24,
    "steals": 7,
    "blocks": 3,
    "turnovers": 20,
    "fouls": 20,
    "points": 87
  }
}
```

#### **Complete Game Data Structure**
```json
{
  "game_id": "401736292",
  "url": "https://www.espn.com/wnba/boxscore/_/gameId/401736292",
  "game_info": {
    "page_title": "Liberty 87-78 Sun (Aug 3, 2025) Box Score - ESPN",
    "game_date": "Aug 3, 2025",
    "away_team": "Liberty",
    "away_score": 87,
    "home_score": 78,
    "home_team": "Sun",
    "final_score": "87-78"
  },
  "quarter_scores": {
    "away_team": {
      "abbreviation": "NY",
      "quarters": {"1": 25, "2": 20, "3": 21, "4": 21, "T": 87}
    },
    "home_team": {
      "abbreviation": "CONN", 
      "quarters": {"1": 19, "2": 19, "3": 19, "4": 21, "T": 78}
    }
  },
  "teams": [...]
}
```

---

### **Use Cases for Sports Betting & Analysis**

#### **Player Props Betting**
- [ ] Points over/under for individual players (with historical ID tracking)
- [ ] Rebounds, assists, steals props with player consistency data
- [ ] Shooting percentage analysis across multiple games
- [ ] Minutes played predictions based on player ID history
- [ ] Cross-game player performance tracking using ESPN IDs

#### **Team Performance Analysis**  
- [ ] Team shooting efficiency with team ID consistency
- [ ] Rebounding advantages and team matchup analysis
- [ ] Turnover differential patterns by team ID
- [ ] Bench vs starter production with individual player tracking
- [ ] Team performance trends using consistent team identifiers

#### **Advanced Analytics**
- [ ] Player impact metrics using plus/minus data
- [ ] Quarter-by-quarter momentum analysis
- [ ] Individual player efficiency ratings
- [ ] Team chemistry analysis through assist/turnover ratios
- [ ] Historical performance correlation using unique IDs

#### **Database Integration Benefits**
- [ ] **Player Tracking**: Consistent ESPN player IDs enable cross-game analysis
- [ ] **Team Analysis**: Stable team IDs for season-long performance tracking  
- [ ] **Relational Data**: Link to other ESPN APIs using same ID system
- [ ] **Historical Trends**: Build comprehensive player/team databases
- [ ] **Predictive Modeling**: Use historical ID-based data for future predictions

---

### **Implementation Notes**

#### **ID Extraction Reliability**
- **Player IDs**: 96% success rate (23/24 players successfully matched)
- **Team IDs**: 100% success rate for standard team names
- **Known Issues**: Hyphenated player names may not match URL slugs perfectly
- **Fallback Strategy**: Players without IDs still have complete statistical data

#### **Data Freshness**
- **Live Games**: Real-time updates during game play
- **Completed Games**: Final statistics immediately after game end
- **Historical Games**: Stable data for past games using same ID system

---

**Last Updated**: August 4, 2025  
**Data Source**: ESPN WNBA Boxscore Pages  
**ID System**: ESPN Player & Team Identifiers  
**Reliability**: High for completed games, includes unique identifiers for database integration