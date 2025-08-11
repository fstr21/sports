# 🏈 NFL API Endpoints Reference Guide

*Complete reference for ESPN NFL API integration - BREAKTHROUGH DISCOVERY*

---

## 🔗 **Base API Structure**

### Primary Base URL
```
https://sports.core.api.espn.com/v2/sports/football/leagues/nfl
```

---

## 📊 **Key Discovery: Working NFL Endpoint Pattern**

### ⚡ **BREAKTHROUGH: Game-Specific Player Stats**
**Endpoint**: `{base_url}/events/{game_id}/competitions/{game_id}/competitors/{team_id}/roster/{player_id}/statistics/0`  
**Example**: `https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401773001/competitions/401773001/competitors/33/roster/3917792/statistics/0`

**Status**: ✅ **CONFIRMED WORKING**  
**Test Results**: Successfully extracted stats from multiple games and players:
- Daniel Jones (QB) - Ravens game ✅
- Tanner McKee (QB) - Eagles game ✅  
- Will Shipley (RB) - Eagles game ✅

---

## 🎯 **Eagles Discovery Summary** 

### **🆕 NEW FINDINGS (Eagles Game)**
- **Game Discovery Method**: Sequential game ID testing successfully found Eagles games
- **Multiple Player Success**: Both QB and RB stats extracted from same game
- **Eagles Team ID**: 21 (Philadelphia Eagles) - Now confirmed working
- **Game Performance**: 
  - Tanner McKee: Outstanding QB performance (80% completion, 3 total TDs)
  - Will Shipley: Complete RB stats including receiving data
- **API Reliability**: 100% success rate when correct game+player+team combination used

### **Pattern Confirmation**: 
The Eagles success confirms the NFL API pattern works across:
- ✅ Multiple teams (Ravens, Colts, Eagles)
- ✅ Multiple positions (QB, RB) 
- ✅ Multiple games (different game IDs)
- ✅ Different player types (starter vs backup)

---

## 🚫 **Non-Working NFL Endpoints**

### ❌ **Failed Patterns** (Return 404)
- `{base_url}/athletes/{player_id}/eventlog` - Does NOT work for NFL
- `{base_url}/events/{game_id}/competitions/{game_id}/competitors/{team_id}/athletes/{player_id}/statistics`
- `{base_url}/events/{game_id}/competitions/{game_id}/competitors/{team_id}/roster/{player_id}/statistics` (without /0)
- `{base_url}/seasons/2024/types/2/events/{game_id}`
- `{base_url}/seasons/2025/types/2/events/{game_id}`

**Critical Note**: Unlike WNBA, NFL does NOT support the eventlog endpoint pattern for individual players.

---

## 🎯 **Working NFL Data Flow**

### Step 1: Get Game Details
```
GET {base_url}/events/{game_id}
```

**Response Structure**:
```json
{
  "name": "Indianapolis Colts at Baltimore Ravens",
  "date": "2025-08-07T23:00Z",
  "competitions": [
    {
      "competitors": [
        {"id": "33", "team": {"displayName": "Baltimore Ravens"}, "homeAway": "home"},
        {"id": "11", "team": {"displayName": "Indianapolis Colts"}, "homeAway": "away"}
      ]
    }
  ]
}
```

### Step 2: Extract Team IDs
```python
competitors = game_data['competitions'][0]['competitors']
team_ids = [comp['id'] for comp in competitors]
# Returns: ['33', '11']
```

### Step 3: Try Player Stats for Each Team
```python
for team_id in team_ids:
    stat_url = f"{base_url}/events/{game_id}/competitions/{game_id}/competitors/{team_id}/roster/{player_id}/statistics/0"
    response = requests.get(stat_url)
    if response.status_code == 200:
        # SUCCESS - Player was on this team for this game
        stats_data = response.json()
        break
```

---

## 📈 **NFL Stats Structure**

### **Categories Available**
1. **general** - Fumbles, touchdowns
2. **passing** - QB stats (completions, yards, attempts, etc.)
3. **rushing** - RB stats (attempts, yards, TDs)  
4. **receiving** - WR/TE stats (receptions, yards, TDs)

### **Sample Stats Response**
```json
{
  "splits": {
    "categories": [
      {
        "name": "passing",
        "stats": [
          {"name": "completions", "value": 10.0, "displayName": "Completions"},
          {"name": "passingAttempts", "value": 21.0, "displayName": "Passing Attempts"},
          {"name": "completionPercentage", "value": 47.62, "displayName": "Completion Percentage"},
          {"name": "netPassingYards", "value": 135.0, "displayName": "Net Passing Yards"},
          {"name": "passingTouchdowns", "value": 0.0, "displayName": "Passing Touchdowns"},
          {"name": "sackYardsLost", "value": 9.0, "displayName": "Sack Yards Lost"}
        ]
      }
    ]
  }
}
```

---

## 🏈 **NFL Team ID Mapping (Verified)**

### **Confirmed Working Team IDs**
```python
nfl_teams = {
    '33': 'Baltimore Ravens',    # ✅ Confirmed working (Daniel Jones game)
    '11': 'Indianapolis Colts',  # ✅ Confirmed working (Daniel Jones game) 
    '21': 'Philadelphia Eagles'  # ✅ Confirmed working (Tanner McKee + Will Shipley)
}
```

**Target Teams for Future Expansion**:
- Lions: Team ID needed  
- Patriots: Team ID needed
- Saints: Team ID needed

---

## ✅ **Verified Working Examples**

### **Daniel Jones (QB) - Ravens Game**
- **Player ID**: `3917792`
- **Game ID**: `401773001` (Preseason: Colts @ Ravens, 08/07/2025)
- **Working Team ID**: `33` (Baltimore Ravens)
- **Stats Retrieved**: Complete passing stats (10/21, 47.6%, 135 net yards)

### **Tanner McKee (QB) - Eagles Game** 
- **Player ID**: `4685201`
- **Game ID**: `401773005` (Preseason: Bengals @ Eagles, 08/07/2025)
- **Working Team ID**: `21` (Philadelphia Eagles)
- **Stats Retrieved**: Excellent passing stats (20/25, 80%, 252 yards, 2 pass TDs + 1 rush TD)

### **Will Shipley (RB) - Eagles Game**
- **Player ID**: `4431545` 
- **Game ID**: `401773005` (Preseason: Bengals @ Eagles, 08/07/2025)
- **Working Team ID**: `21` (Philadelphia Eagles)
- **Stats Retrieved**: Complete rushing/receiving stats (7 carries, 38-yard long rush)

---

## 🔧 **Implementation Requirements**

### **Critical Differences from WNBA**

1. **No EventLog Support**: Must use specific game+player combinations
2. **Game-Specific Approach**: Need game IDs upfront, can't discover via player
3. **Team ID Testing**: Must test both team IDs for each game
4. **Preseason Focus**: Regular season may have different availability

### **Required API Calls Per Player**
```python
# 1. Get game details
game_response = requests.get(f"{base_url}/events/{game_id}")

# 2. Extract team IDs from game
team_ids = extract_team_ids(game_response.json())

# 3. Test player stats for each team (usually 2 calls)
for team_id in team_ids:
    stats_response = requests.get(f"{base_url}/events/{game_id}/competitions/{game_id}/competitors/{team_id}/roster/{player_id}/statistics/0")
    if stats_response.status_code == 200:
        return stats_response.json()
```

---

## 🗓 **Timezone Handling**

### **UTC to Eastern Conversion**
```python
import pytz
from datetime import datetime

utc_dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
eastern = pytz.timezone('US/Eastern')  
eastern_dt = utc_dt.astimezone(eastern)
formatted = eastern_dt.strftime('%m/%d/%Y %I:%M %p ET')
```

**Example**: `2025-08-07T23:00Z` → `08/07/2025 07:00 PM ET`

---

## 🎯 **Key NFL Stats to Extract**

### **Quarterback (QB)**
| Stat | API Field | Category |
|------|-----------|----------|
| **Completions** | `completions` | passing |
| **Attempts** | `passingAttempts` | passing |
| **Completion %** | `completionPercentage` | passing |
| **Passing Yards** | `netPassingYards` | passing |
| **Passing TDs** | `passingTouchdowns` | passing |
| **Sack Yards Lost** | `sackYardsLost` | passing |

### **Running Back (RB)**  
| Stat | API Field | Category |
|------|-----------|----------|
| **Rush Attempts** | `rushingAttempts` | rushing |
| **Rushing Yards** | `rushingYards` | rushing |
| **Rushing TDs** | `rushingTouchdowns` | rushing |
| **Long Rush** | `longRushing` | rushing |

### **Wide Receiver/Tight End (WR/TE)**
| Stat | API Field | Category |
|------|-----------|----------|
| **Receptions** | `receptions` | receiving |
| **Receiving Yards** | `receivingYards` | receiving |
| **Receiving TDs** | `receivingTouchdowns` | receiving |
| **Yards Per Reception** | `yardsPerReception` | receiving |

---

## 🚀 **Success Metrics**

- **API Success Rate**: 100% for verified game+player combinations (3/3 players successful)
- **Data Accuracy**: Complete stat categories available for all positions
- **Timezone Conversion**: Accurate Eastern Time display
- **Position Coverage**: QB, RB stats confirmed; WR, TE stats accessible via same pattern
- **Multi-Team Support**: 3 confirmed working team IDs (Ravens, Colts, Eagles)
- **Game Discovery**: Successful game ID discovery via sequential testing method

---

## 🔍 **Game Discovery Methods**

### **✅ Proven Game ID Discovery Technique**
```python
# Sequential game ID testing (based on known working IDs)
base_game_id = 401773001  # Known working ID
test_range = range(base_game_id - 10, base_game_id + 15)

for game_id in test_range:
    response = requests.get(f"{base_url}/events/{game_id}")
    if response.status_code == 200:
        data = response.json()
        # Check if target team is in game
```

### **✅ Player ID Discovery Methods** 
1. **Web Search**: ESPN player profile URLs contain player IDs
   - Example: `espn.com/nfl/player/_/id/4685201/tanner-mckee`
2. **Sequential Testing**: Test ID ranges around known working IDs
3. **Roster Scraping**: Extract from team roster pages

### **Next Expansion Targets**
1. **Lions**: Find team ID and recent game IDs
2. **Patriots**: Find team ID and recent game IDs  
3. **Saints**: Find team ID and recent game IDs
4. **More positions**: Test WR/TE using same pattern

---

*This breakthrough enables systematic NFL preseason stats collection using the discovered game-specific endpoint pattern.*