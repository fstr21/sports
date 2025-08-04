# ESPN WNBA API Capabilities

## ✅ Available Endpoints

### 🏀 **Scoreboard** - Game Data
- **What it provides**: Live scores, game schedules, team matchups
- **Sample queries**: 
  - "Show me today's WNBA scores"
  - "What games are scheduled?"
  - "Dallas Wings vs New York Liberty score"
- **Data includes**: Game status, team names, scores, venue, date/time

### 🏆 **Teams** - Team Information  
- **What it provides**: All 13 WNBA teams basic info
- **Sample queries**:
  - "Tell me about the Las Vegas Aces"
  - "What teams are in the WNBA?"
  - "Seattle Storm team info"
- **Data includes**: Team names, colors, logos, abbreviations

### 🏥 **Injuries** - Injury Reports
- **What it provides**: Current injury status for players
- **Sample queries**:
  - "Any injuries for the Liberty?"
  - "WNBA injury report"
  - "Who's hurt on the Aces?"
- **Data includes**: Player names, injury status, team info

### 📰 **News** - Latest Articles
- **What it provides**: Recent WNBA news and articles
- **Sample queries**:
  - "Latest WNBA news"
  - "What's happening in the WNBA?"
  - "Recent articles"
- **Data includes**: Headlines, descriptions, publish dates

### 📊 **Statistics** - League Stats
- **What it provides**: Team and league statistics
- **Sample queries**:
  - "WNBA team stats"
  - "League statistics"
  - "Team performance data"
- **Data includes**: Various statistical categories

### 🏆 **Team Details** - Individual Team Data
- **What it provides**: Detailed info for specific teams
- **Sample queries**:
  - "Atlanta Dream roster"
  - "Team record for the Storm"
  - "Liberty team details"
- **Data includes**: Records, standings, next games

## ❌ Not Available Endpoints
- Individual player statistics (athletes endpoint returns 404)
- Detailed schedule endpoint (404)
- Playoff bracket data (404)

## 🎯 What You CAN Ask Your MCP Server

### Game Information
- "Show me today's games"
- "WNBA scores"
- "Who's playing tonight?"
- "Dallas Wings schedule"

### Team Information  
- "Tell me about the Las Vegas Aces"
- "All WNBA teams"
- "Liberty team info"
- "Storm team colors"

### Injury Reports
- "Any injuries in the WNBA?"
- "Aces injury report" 
- "Who's hurt on the Liberty?"

### News & Updates
- "Latest WNBA news"
- "Recent articles"
- "What's new in the WNBA?"

### Statistics
- "WNBA team stats"
- "League statistics"
- "Team performance"

## 🚫 What You CANNOT Ask For
- Individual player career stats
- Detailed player profiles
- Historical game data
- Playoff brackets (currently)
- Player comparison stats

## 💡 Pro Tips
1. **Be specific with team names**: Use full names like "Las Vegas Aces" or abbreviations like "LV"
2. **Current season focus**: Data is primarily for the current 2025 season
3. **Real-time updates**: Scores and injury data are current
4. **Natural language**: Your MCP server uses AI to understand casual questions

## 🔧 Technical Details
- **Base URL**: https://site.api.espn.com
- **Response Format**: JSON
- **Rate Limits**: Be respectful with requests
- **Data Freshness**: Updated regularly by ESPN