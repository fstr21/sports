# NFL Schedule Data Checklist

This checklist outlines every piece of data you can reliably get for NFL schedule information using ESPN's API. Use this as a guide for designing queries for your MCP.

---

### **Data Source Details**

* **Method**: `GET` (REST API)
* **Base URL**: `http://site.api.espn.com/apis/site/v2/sports/football/`
* **League Code**: `nfl` (National Football League)
* **Endpoint**: `/scoreboard`
* **Parameters**: 
  - `dates`: Date in YYYYMMDD format (e.g., "20250904")
* **Full URL Example**: `http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=20250904`
* **Data Format**: JSON
* **Update Frequency**: Real-time updates as games are scheduled/rescheduled

---

### **League Metadata**

#### **League Information**
- [ ] **League ID**: "28"
- [ ] **League UID**: "s:20~l:28"
- [ ] **League Name**: "National Football League"
- [ ] **League Abbreviation**: "NFL"
- [ ] **League Slug**: "nfl"

#### **Season Information**
- [ ] **Season Year**: 2025
- [ ] **Season Start Date**: "2025-07-31T07:00Z"
- [ ] **Season End Date**: "2026-02-12T07:59Z"
- [ ] **Season Display Name**: "2025"
- [ ] **Season Type**: Preseason, Regular Season, Postseason, Off Season

#### **League Logos**
- [ ] **Default Logo**: "https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png"
- [ ] **Dark Logo**: "https://a.espncdn.com/i/teamlogos/leagues/500-dark/nfl.png"
- [ ] **Logo Dimensions**: 500x500 pixels

---

### **Season Calendar Structure**

#### **Preseason (Type 1)**
- [ ] **Duration**: July 31 - September 4
- [ ] **Hall of Fame Weekend**: Jul 31-Aug 6
- [ ] **Preseason Week 1**: Aug 7-13
- [ ] **Preseason Week 2**: Aug 14-20
- [ ] **Preseason Week 3**: Aug 21-Sep 3

#### **Regular Season (Type 2)**
- [ ] **Duration**: September 4 - January 8
- [ ] **Week 1**: Sep 4-10
- [ ] **Week 2**: Sep 11-17
- [ ] **Week 3**: Sep 18-24
- [ ] **Week 4**: Sep 25-Oct 1
- [ ] **Week 5**: Oct 2-8
- [ ] **Week 6**: Oct 9-15
- [ ] **Week 7**: Oct 16-22
- [ ] **Week 8**: Oct 23-29
- [ ] **Week 9**: Oct 30-Nov 5
- [ ] **Week 10**: Nov 6-12
- [ ] **Week 11**: Nov 13-19
- [ ] **Week 12**: Nov 20-26
- [ ] **Week 13**: Nov 27-Dec 3
- [ ] **Week 14**: Dec 4-10
- [ ] **Week 15**: Dec 11-17
- [ ] **Week 16**: Dec 18-24
- [ ] **Week 17**: Dec 25-31
- [ ] **Week 18**: Jan 1-7

#### **Postseason (Type 3)**
- [ ] **Duration**: January 8 - February 12
- [ ] **Wild Card**: Jan 8-14
- [ ] **Divisional Round**: Jan 15-21
- [ ] **Conference Championship**: Jan 22-28
- [ ] **Pro Bowl**: Jan 29-Feb 4
- [ ] **Super Bowl**: Feb 5-11

#### **Off Season (Type 4)**
- [ ] **Duration**: February 12 - August 1

---

### **Game Information**

#### **Game Metadata**
- [ ] **Game ID**: "401772510"
- [ ] **Game UID**: "s:20~l:28~e:401772510"
- [ ] **Game Date**: "2025-09-05T00:20Z" (ISO format)
- [ ] **Game Name**: "Dallas Cowboys at Philadelphia Eagles"
- [ ] **Short Name**: "DAL @ PHI"
- [ ] **Week Number**: 1
- [ ] **Season Type**: 2 (Regular Season)

#### **Competition Details**
- [ ] **Competition ID**: "401772510"
- [ ] **Competition UID**: "s:20~l:28~e:401772510~c:401772510"
- [ ] **Attendance**: 0 (pre-game)
- [ ] **Type**: "STD" (Standard)
- [ ] **Time Valid**: true
- [ ] **Neutral Site**: false
- [ ] **Conference Competition**: false
- [ ] **Play-by-Play Available**: false (pre-game)

---

### **Venue Information**

#### **Stadium Details**
- [ ] **Venue ID**: "3806"
- [ ] **Full Name**: "Lincoln Financial Field"
- [ ] **City**: "Philadelphia"
- [ ] **State**: "PA"
- [ ] **Country**: "USA"
- [ ] **Indoor**: false (outdoor stadium)

---

### **Team Information**

#### **Team Details (Per Team)**
- [ ] **Team ID**: "21" (Philadelphia Eagles)
- [ ] **Team UID**: "s:20~l:28~t:21"
- [ ] **Location**: "Philadelphia"
- [ ] **Team Name**: "Eagles"
- [ ] **Abbreviation**: "PHI"
- [ ] **Display Name**: "Philadelphia Eagles"
- [ ] **Short Display Name**: "Eagles"
- [ ] **Primary Color**: "06424d"
- [ ] **Alternate Color**: "000000"
- [ ] **Home/Away**: "home" or "away"
- [ ] **Active Status**: true

#### **Team Links**
- [ ] **Clubhouse**: "https://www.espn.com/nfl/team/_/name/phi/philadelphia-eagles"
- [ ] **Roster**: "https://www.espn.com/nfl/team/roster/_/name/phi/philadelphia-eagles"
- [ ] **Statistics**: "https://www.espn.com/nfl/team/stats/_/name/phi/philadelphia-eagles"
- [ ] **Schedule**: "https://www.espn.com/nfl/team/schedule/_/name/phi"

#### **Team Logos**
- [ ] **Team Logo**: "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/phi.png"
- [ ] **Logo Dimensions**: 500x500 pixels

#### **Team Records**
- [ ] **Overall Record**: "0-0" (season start)
- [ ] **Home Record**: "0-0"
- [ ] **Road Record**: "0-0"

---

### **Game Status Information**

#### **Game Status**
- [ ] **Clock**: 0.0 (pre-game)
- [ ] **Display Clock**: "0:00"
- [ ] **Period**: 0 (pre-game)
- [ ] **Status Type ID**: "1"
- [ ] **Status Name**: "STATUS_SCHEDULED"
- [ ] **Status State**: "pre"
- [ ] **Completed**: false
- [ ] **Description**: "Scheduled"
- [ ] **Detail**: "Thu, September 4th at 8:20 PM EDT"
- [ ] **Short Detail**: "9/4 - 8:20 PM EDT"
- [ ] **TBD Flex**: false

---

### **Broadcasting Information**

#### **TV/Streaming Coverage**
- [ ] **Market**: "national"
- [ ] **Networks**: ["NBC", "Peacock"]
- [ ] **Broadcast String**: "NBC/Peacock"

#### **Geo-Specific Broadcasts**
- [ ] **TV Broadcast**:
    - Type: "TV"
    - Market: "National"
    - Media: "NBC"
    - Language: "en"
    - Region: "us"
- [ ] **Streaming Broadcast**:
    - Type: "Streaming"
    - Market: "National"
    - Media: "Peacock"
    - Language: "en"
    - Region: "us"

---

### **Betting Information**

#### **ESPN BET Integration**
- [ ] **Provider ID**: "58"
- [ ] **Provider Name**: "ESPN BET"
- [ ] **Priority**: 1
- [ ] **Light Logo**: "https://a.espncdn.com/i/espnbet/ESPN_Bet_Sportsbook_Light.svg"
- [ ] **Dark Logo**: "https://a.espncdn.com/i/espnbet/ESPN_Bet_Sportsbook_Dark.svg"

#### **Betting Lines**
- [ ] **Spread**: PHI -7.0
- [ ] **Over/Under**: 46.5
- [ ] **Details**: "PHI -7"

#### **Team Odds**
- [ ] **Home Team (PHI)**:
    - Favorite: true
    - Money Line: -340
    - Spread Odds: -105.0
    - Favorite at Open: true
- [ ] **Away Team (DAL)**:
    - Underdog: true
    - Money Line: +270
    - Spread Odds: -115.0
    - Favorite at Open: false

#### **Detailed Betting Markets**
- [ ] **Moneyline**:
    - Home: -340 (close), -340 (open)
    - Away: +270 (close), +270 (open)
- [ ] **Point Spread**:
    - Home: -7 (-105), -7 (-105) open
    - Away: +7 (-115), +7 (-115) open
- [ ] **Total Points**:
    - Over: o46.5 (-110), o46.5 (-110) open
    - Under: u46.5 (-110), u46.5 (-110) open

#### **Featured Parlays**
- [ ] **Week One Chaos**: +4340 odds, 3-leg parlay
- [ ] **Primetime Parlay**: +688 odds, 4-leg parlay
- [ ] **Never In Doubt**: +681 odds, 3-leg parlay
- [ ] **Super Bowl Favorites**: +340 odds, 3-leg parlay

---

### **Ticketing Information**

#### **Ticket Availability**
- [ ] **Summary**: "Tickets as low as $551"
- [ ] **Number Available**: 5,531
- [ ] **Vendor Links**: VividSeats integration
- [ ] **Venue-Specific Links**: Lincoln Financial Field tickets

---

### **Game Format**

#### **Regulation Structure**
- [ ] **Periods**: 4 quarters
- [ ] **Standard Format**: NFL regulation game structure

---

### **Technical Implementation**

#### **Required Libraries**
- [ ] **requests**: HTTP requests to ESPN API
- [ ] **json**: JSON response parsing
- [ ] **typing**: Type hints for better code structure
- [ ] **sys**: System-specific parameters and functions

#### **Request Configuration**
- [ ] **Timeout**: 15 seconds
- [ ] **Error Handling**: HTTP status code validation
- [ ] **Response Processing**: JSON parsing and data extraction
- [ ] **Date Format**: YYYYMMDD format required

#### **Data Processing**
- [ ] **Event Extraction**: Parse events array from response
- [ ] **Game Counting**: Track number of games found
- [ ] **File Output**: Save complete JSON response
- [ ] **Error Reporting**: Clear error messages for failures

---

### **Sample Data Structures**

#### **Game Event Structure**
```json
{
  "id": "401772510",
  "uid": "s:20~l:28~e:401772510",
  "date": "2025-09-05T00:20Z",
  "name": "Dallas Cowboys at Philadelphia Eagles",
  "shortName": "DAL @ PHI",
  "season": {
    "year": 2025,
    "type": 2,
    "slug": "regular-season"
  },
  "week": {
    "number": 1
  }
}
```

#### **Team Competitor Structure**
```json
{
  "id": "21",
  "uid": "s:20~l:28~t:21",
  "type": "team",
  "order": 0,
  "homeAway": "home",
  "team": {
    "id": "21",
    "location": "Philadelphia",
    "name": "Eagles",
    "abbreviation": "PHI",
    "displayName": "Philadelphia Eagles",
    "color": "06424d",
    "alternateColor": "000000"
  },
  "score": "0",
  "records": [
    {
      "name": "overall",
      "type": "total",
      "summary": "0-0"
    }
  ]
}
```

#### **Betting Odds Structure**
```json
{
  "provider": {
    "id": "58",
    "name": "ESPN BET"
  },
  "details": "PHI -7",
  "overUnder": 46.5,
  "spread": -7.0,
  "homeTeamOdds": {
    "favorite": true,
    "moneyLine": -340,
    "spreadOdds": -105.0
  },
  "awayTeamOdds": {
    "favorite": false,
    "moneyLine": 270,
    "spreadOdds": -115.0
  }
}
```

---

### **Data Quality & Reliability**

#### **Highly Reliable Data**
✅ **Game Scheduling**: Accurate dates, times, and matchups  
✅ **Team Information**: Complete team details with IDs and colors  
✅ **Venue Details**: Stadium information and locations  
✅ **Season Structure**: Complete calendar with all weeks and phases  
✅ **Broadcasting**: TV and streaming coverage information  

#### **Moderately Reliable Data**
⚠️ **Betting Odds**: Real-time odds that change frequently  
⚠️ **Ticket Prices**: Dynamic pricing based on demand  
⚠️ **Featured Parlays**: Promotional betting content that updates  

#### **Pre-Game vs Live Data**
📊 **Pre-Game**: Complete scheduling and setup information  
📊 **Live**: Real-time scores, statistics, and play-by-play  
📊 **Post-Game**: Final scores, statistics, and highlights  

---

### **Use Cases for Sports Analysis**

#### **Schedule Planning**
- [ ] **Weekly Schedule**: Complete NFL weekly game schedule
- [ ] **Primetime Games**: Thursday, Sunday, Monday night games
- [ ] **Playoff Schedule**: Postseason tournament bracket
- [ ] **Season Calendar**: Full season timeline with key dates

#### **Betting Applications**
- [ ] **Game Lines**: Spread, moneyline, and total betting
- [ ] **Parlay Building**: Multi-game betting combinations
- [ ] **Live Odds**: Real-time betting line movements
- [ ] **Featured Bets**: Promotional and special betting offers

#### **Fantasy Football**
- [ ] **Matchup Analysis**: Team vs team performance
- [ ] **Player Availability**: Injury reports and roster status
- [ ] **Game Environment**: Weather, venue, and timing factors
- [ ] **Playoff Implications**: Standings and seeding impact

#### **Media & Broadcasting**
- [ ] **TV Schedule**: National and regional broadcast coverage
- [ ] **Streaming Options**: Digital viewing platforms
- [ ] **Market Coverage**: Geographic broadcast restrictions
- [ ] **Language Options**: Multi-language broadcast support

---

### **Integration Examples**

#### **MCP Tool Integration**
```python
def get_nfl_schedule(date="20250904"):
    """Get NFL schedule for a specific date"""
    url = f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    params = {"dates": date}
    
    response = requests.get(url, params=params, timeout=15)
    data = response.json()
    
    return {
        "games": data.get("events", []),
        "league_info": data.get("leagues", []),
        "date": date,
        "total_games": len(data.get("events", [])),
        "last_updated": datetime.now().isoformat()
    }
```

#### **Database Schema**
```sql
CREATE TABLE nfl_schedule (
    game_id VARCHAR(20) PRIMARY KEY,
    game_date DATETIME,
    home_team_id VARCHAR(10),
    away_team_id VARCHAR(10),
    home_team_name VARCHAR(100),
    away_team_name VARCHAR(100),
    venue_id VARCHAR(10),
    venue_name VARCHAR(100),
    week_number INT,
    season_type INT,
    season_year INT,
    broadcast_networks TEXT,
    spread DECIMAL(4,1),
    over_under DECIMAL(4,1),
    home_moneyline INT,
    away_moneyline INT,
    game_status VARCHAR(50),
    created_at TIMESTAMP
);
```

---

**Last Updated**: February 5, 2025  
**Data Source**: ESPN NFL API  
**League**: National Football League (nfl)  
**Endpoint**: `/scoreboard` with dates parameter  
**Reliability**: High for scheduled games, comprehensive betting and broadcast data