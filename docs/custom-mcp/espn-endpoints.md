# ESPN API Data Extraction Checklist
## Complete Guide to Available Data via Custom MCP

**Base URL:** `http://site.api.espn.com/apis/site/v2/sports`  
**Access Method:** Your Custom MCP `customSportsAnalysis` tool  
**Date:** August 2025

---

## 🏀 GAME DATA (Scoreboard Endpoint)
### Example: `/basketball/wnba/scoreboard`

### ✅ **Basic Game Information**
- [ ] **Game ID** - Unique identifier for the game
- [ ] **Matchup** - Team names and vs format
- [ ] **Date & Time** - Game date/time in UTC
- [ ] **Game Status** - Scheduled, In Progress, Final, Postponed
- [ ] **Season Info** - Year, season type (regular, playoffs, preseason)
- [ ] **Week/Period** - Week number (NFL), game number
- [ ] **Venue Details** - Stadium name, city, state, indoor/outdoor
- [ ] **Attendance** - Actual attendance numbers
- [ ] **Neutral Site** - Whether game is at neutral venue

### ✅ **Team Information (Per Team)**
- [ ] **Team ID** - Unique team identifier
- [ ] **Team Names** - Full name, short name, abbreviation, location
- [ ] **Team Colors** - Primary and alternate hex colors
- [ ] **Team Logos** - Multiple logo URLs (default, dark, scoreboard)
- [ ] **Home/Away Status** - Which team is home/away
- [ ] **Current Score** - Live or final score
- [ ] **Winner Status** - Which team won (if final)

### ✅ **Team Records & Performance**
- [ ] **Overall Record** - Wins-losses (e.g., "15-14")
- [ ] **Home Record** - Home wins-losses
- [ ] **Road Record** - Away wins-losses
- [ ] **Conference Record** - Conference wins-losses (if applicable)
- [ ] **Division Record** - Division wins-losses (if applicable)
- [ ] **Recent Form** - Last 10 games, streaks

### ✅ **Team Statistics (Season Totals)**
- [ ] **Scoring** - Total points, average points per game
- [ ] **Field Goals** - Made, attempted, percentage
- [ ] **Three-Pointers** - Made, attempted, percentage, ranking
- [ ] **Free Throws** - Made, attempted, percentage
- [ ] **Rebounds** - Total rebounds, average per game, ranking
- [ ] **Assists** - Total assists, average per game, ranking
- [ ] **Advanced Stats** - Offensive rating, defensive rating, pace

### ✅ **Player Leaders (Per Team)**
- [ ] **Points Per Game Leader** - Player name, average, value
- [ ] **Rebounds Per Game Leader** - Player name, average, value  
- [ ] **Assists Per Game Leader** - Player name, average, value
- [ ] **Player Details** - Full name, jersey number, position
- [ ] **Player Photos** - Headshot URLs
- [ ] **Player Links** - ESPN profile links
- [ ] **Overall Rating** - Combined statistical rating

### ✅ **Betting Information**
- [ ] **Point Spread** - Favorite, underdog, line (e.g., "LV -5.5")
- [ ] **Moneyline Odds** - Favorite and underdog odds
- [ ] **Total Points** - Over/under line (e.g., "157.5")
- [ ] **Spread Odds** - Odds for each side of spread
- [ ] **Opening Lines** - Original betting lines
- [ ] **Line Movement** - How lines have changed
- [ ] **Betting Provider** - Sportsbook information (ESPN BET)
- [ ] **Featured Bets** - Parlays, prop bets, special offers

### ✅ **Broadcast Information**
- [ ] **TV Networks** - National and local broadcasters
- [ ] **Streaming** - Available streaming platforms
- [ ] **Radio** - Radio broadcast information
- [ ] **Market Coverage** - National, home, away markets

### ✅ **Game Context**
- [ ] **Playoff Implications** - Seeding, elimination scenarios
- [ ] **Rivalry Information** - Historical matchups
- [ ] **Special Notes** - Milestone games, ceremonies
- [ ] **Weather** - For outdoor sports
- [ ] **Ticket Information** - Availability, pricing

---

## 🏈 TEAM DATA (Teams Endpoint)
### Example: `/basketball/wnba/teams`

### ✅ **Team Profile Information**
- [ ] **Team Identifiers** - ID, UID, slug, abbreviation
- [ ] **Team Names** - Display name, short name, nickname, location
- [ ] **Team Branding** - Colors (hex codes), logos (multiple sizes)
- [ ] **Team Status** - Active, all-star eligibility
- [ ] **Conference/Division** - League structure placement

### ✅ **Team Links & Resources**
- [ ] **Clubhouse Link** - Main team page
- [ ] **Roster Link** - Current roster page
- [ ] **Statistics Link** - Team stats page
- [ ] **Schedule Link** - Team schedule page
- [ ] **Tickets Link** - Ticket purchasing page

### ✅ **Historical Information**
- [ ] **Franchise History** - Team origins, relocations
- [ ] **Championships** - Titles won, years
- [ ] **Notable Players** - Hall of famers, retired numbers

---

## 📰 NEWS & INJURY DATA (News Endpoint)
### Example: `/basketball/wnba/news`

### ✅ **News Articles**
- [ ] **Article ID** - Unique identifier
- [ ] **Headline** - Article title
- [ ] **Description** - Article summary/excerpt
- [ ] **Publication Date** - When article was published
- [ ] **Last Modified** - When article was last updated
- [ ] **Article Type** - News, story, analysis, video
- [ ] **Author** - Writer byline
- [ ] **Premium Status** - Whether article requires subscription

### ✅ **Injury Reports**
- [ ] **Player Name** - Injured player identification
- [ ] **Injury Type** - Specific injury description
- [ ] **Injury Status** - Out, questionable, probable, day-to-day
- [ ] **Expected Return** - Timeline for return
- [ ] **Impact Assessment** - How injury affects team

### ✅ **Breaking News**
- [ ] **Trade Information** - Player movements, draft picks
- [ ] **Roster Changes** - Signings, releases, waivers
- [ ] **Coaching Changes** - Hirings, firings, promotions
- [ ] **League Announcements** - Rule changes, schedule updates
- [ ] **Disciplinary Actions** - Suspensions, fines

### ✅ **Media Content**
- [ ] **Images** - Article photos, player headshots
- [ ] **Videos** - Highlights, interviews, analysis
- [ ] **Photo Galleries** - Game photos, behind-scenes
- [ ] **Social Media** - Embedded tweets, posts

---

## 🏆 STANDINGS DATA (Standings Endpoint)
### Example: `/basketball/wnba/standings`

### ✅ **League Standings**
- [ ] **Team Rankings** - Current position in standings
- [ ] **Win-Loss Records** - Overall, conference, division
- [ ] **Winning Percentage** - Calculated win percentage
- [ ] **Games Behind** - Games behind division/conference leader
- [ ] **Streak Information** - Current winning/losing streaks
- [ ] **Home/Road Splits** - Performance by venue
- [ ] **Conference Standings** - Eastern/Western conference ranks
- [ ] **Division Standings** - Division-specific rankings
- [ ] **Playoff Positioning** - Current playoff seeding
- [ ] **Elimination Numbers** - Magic numbers for playoffs/elimination

---

## 📊 ADVANCED ANALYTICS (Derived from Game Data)

### ✅ **Team Performance Metrics**
- [ ] **Offensive Efficiency** - Points per possession
- [ ] **Defensive Efficiency** - Points allowed per possession  
- [ ] **Net Rating** - Point differential per 100 possessions
- [ ] **Pace** - Possessions per game
- [ ] **Four Factors** - eFG%, TOV%, ORB%, FT Rate
- [ ] **Clutch Performance** - Performance in close games
- [ ] **Strength of Schedule** - Opponent difficulty rating

### ✅ **Player Performance Metrics**
- [ ] **Usage Rate** - Percentage of team possessions used
- [ ] **Player Efficiency Rating** - Overall efficiency metric
- [ ] **True Shooting Percentage** - Shooting efficiency including 3PT/FT
- [ ] **Assist-to-Turnover Ratio** - Ball handling efficiency
- [ ] **Plus/Minus** - Point differential when player is on court
- [ ] **Win Shares** - Player's contribution to team wins

---

## 🎯 BETTING-SPECIFIC DATA EXTRACTION

### ✅ **Line Analysis**
- [ ] **Opening vs Current Lines** - Line movement tracking
- [ ] **Line Shopping** - Multiple sportsbook comparisons
- [ ] **Sharp vs Public Money** - Betting market indicators
- [ ] **Reverse Line Movement** - Lines moving against public
- [ ] **Steam Moves** - Sudden line movements
- [ ] **Closing Line Value** - Final line vs opening

### ✅ **Prop Bet Opportunities**
- [ ] **Player Props** - Points, rebounds, assists over/unders
- [ ] **Team Props** - Team totals, first half lines
- [ ] **Game Props** - First basket, largest lead, etc.
- [ ] **Season Props** - Awards, playoff odds, win totals
- [ ] **Live Betting** - In-game line movements

### ✅ **Value Identification**
- [ ] **Market Inefficiencies** - Mispriced lines
- [ ] **Injury Impact** - How injuries affect lines
- [ ] **Weather Impact** - For outdoor sports
- [ ] **Rest Advantages** - Days off between games
- [ ] **Travel Factors** - Cross-country trips, time zones
- [ ] **Motivation Factors** - Playoff implications, revenge games

---

## 🔧 CUSTOM MCP TOOLS AVAILABLE

### ✅ **analyzeWnbaGames**
- **Endpoint:** `/basketball/wnba/scoreboard`
- **Parameters:** dates, limit, analysis_type
- **Analysis Types:** general, betting, performance, predictions

### ✅ **analyzeNflGames**  
- **Endpoint:** `/football/nfl/scoreboard`
- **Parameters:** week, analysis_type
- **Analysis Types:** general, betting, fantasy, predictions

### ✅ **customSportsAnalysis**
- **Endpoint:** `/{sport}/{league}/{endpoint}`
- **Sports:** basketball, football, baseball, hockey, soccer
- **Leagues:** wnba, nfl, nba, mlb, nhl, mls, college
- **Endpoints:** scoreboard, teams, news, standings
- **Custom Prompts:** Any analysis request

---

## 📋 EXAMPLE DATA EXTRACTION REQUESTS

### **Single Game Analysis:**
```
"Analyze the Las Vegas Aces vs Golden State Valkyries game including:
- Current team records and recent form
- Key player matchups and statistical leaders  
- Betting lines and value opportunities
- Injury reports and player availability
- Venue factors and travel considerations
- Historical head-to-head performance"
```

### **Team Deep Dive:**
```
"Provide comprehensive analysis of the Las Vegas Aces including:
- Current season statistics and rankings
- Key player performances and roles
- Strengths and weaknesses analysis
- Playoff positioning and scenarios
- Recent news and injury updates
- Betting market perception and value"
```

### **Player Focus:**
```
"Analyze A'ja Wilson's current season including:
- Statistical performance and league rankings
- Recent game-by-game performance trends
- Injury status and availability
- Prop bet opportunities and historical performance
- Impact on team success and betting lines
- Award candidacy and season outlook"
```

### **League-Wide Analysis:**
```
"Provide WNBA league overview including:
- Current standings and playoff picture
- Top performers in major statistical categories
- Major storylines and news updates
- Betting market trends and opportunities
- Injury report across all teams
- Schedule analysis and key upcoming games"
```

---

## ⚠️ LIMITATIONS & NOTES

### **Data NOT Available:**
- ❌ Individual player career statistics endpoints
- ❌ Historical game-by-game player stats
- ❌ Advanced player tracking data (SportVU, etc.)
- ❌ Salary/contract information
- ❌ Draft information and prospects
- ❌ Minor league/developmental league data

### **Data Quality Notes:**
- ✅ Real-time updates during games
- ✅ Comprehensive current season data
- ✅ Accurate betting lines from ESPN BET
- ✅ Up-to-date injury information via news
- ⚠️ Some advanced metrics calculated from basic stats
- ⚠️ Historical data limited to current season

### **Best Practices:**
- Use `customSportsAnalysis` for maximum flexibility
- Combine multiple endpoints for comprehensive analysis
- Include specific prompts for betting-focused insights
- Cross-reference news endpoint for injury updates
- Monitor line movements through repeated calls
- Use date parameters for historical game analysis

---

**Last Updated:** August 6, 2025  
**API Version:** ESPN API v2  
**Custom MCP Version:** sports-ai-analyzer v1.0