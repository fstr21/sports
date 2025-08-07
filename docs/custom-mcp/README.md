# Sports AI MCP Documentation
## Your Custom Sports Analysis & Betting Intelligence Server

**Server Name:** `sports-ai`  
**File:** `mcp/sports_ai_mcp.py`  
**Status:** ✅ Active and Verified  
**Success Rate:** 86.2% data availability  

---

## 🎯 **Overview**

The Sports AI MCP is your custom-built sports analysis server that combines live ESPN data with AI-powered insights using your OpenRouter API. It's specifically designed for sports betting analysis and provides professional-grade intelligence for your betting platform.

### **What Makes It Special:**
- ✅ **AI-Powered Analysis** - Uses OpenRouter API for intelligent insights
- ✅ **Multi-Sport Support** - WNBA, NFL, NBA, MLB, NHL, and more
- ✅ **Betting-Focused** - Specialized prompts for betting analysis
- ✅ **Real-Time Data** - Live ESPN API integration
- ✅ **Flexible Queries** - Custom prompts for any analysis need

---

## 🛠️ **Available Tools**

### **1. analyzeWnbaGames**
**Purpose:** Fetch WNBA games and provide AI-powered analysis

**Parameters:**
- `dates` (optional) - Date in YYYYMMDD format (e.g., "20250803")
- `limit` (optional) - Number of games to analyze
- `analysis_type` (optional) - Type of analysis:
  - `"general"` - General game analysis
  - `"betting"` - Betting-focused analysis
  - `"performance"` - Player/team performance focus
  - `"predictions"` - Future predictions and trends

**Example Usage:**
```python
analyzeWnbaGames({
    "dates": "20250807",
    "analysis_type": "betting",
    "limit": 3
})
```

### **2. analyzeNflGames**
**Purpose:** Fetch NFL games and provide AI-powered analysis

**Parameters:**
- `week` (optional) - NFL week number
- `analysis_type` (optional) - Type of analysis:
  - `"general"` - General game analysis
  - `"betting"` - Betting-focused analysis
  - `"fantasy"` - Fantasy football focus
  - `"predictions"` - Future predictions and trends

**Example Usage:**
```python
analyzeNflGames({
    "week": 1,
    "analysis_type": "fantasy"
})
```

### **3. customSportsAnalysis** ⭐ **Most Flexible**
**Purpose:** Fetch any sports data and analyze with custom prompts

**Parameters:**
- `sport` (optional) - Sport type: basketball, football, baseball, hockey, etc.
- `league` (optional) - League: wnba, nfl, nba, mlb, nhl, etc.
- `endpoint` (optional) - Data endpoint: scoreboard, teams, news, standings
- `prompt` (optional) - Your custom analysis request

**Example Usage:**
```python
customSportsAnalysis({
    "sport": "basketball",
    "league": "nba",
    "endpoint": "scoreboard", 
    "prompt": "Analyze tonight's games for betting value and identify potential upsets"
})
```

---

## 📊 **Data Sources & Capabilities**

### **ESPN API Integration**
- **Base URL:** `http://site.api.espn.com/apis/site/v2/sports`
- **Coverage:** All major US sports leagues
- **Update Frequency:** Real-time during games
- **Data Types:** Scores, stats, news, team info, player data

### **Verified Data Availability (86.2% Success Rate)**
- ✅ **Live Game Data** - Real-time scores, player stats, game status
- ✅ **Team Information** - Complete profiles, records, branding
- ✅ **Player Leaders** - Current performers with photos and stats
- ✅ **News & Injuries** - Breaking news and injury reports
- ✅ **Broadcast Info** - TV networks and streaming platforms
- ❌ **Betting Lines** - Not available via ESPN API during live games
- ❌ **Detailed Standings** - Limited data, external links only

---

## 🎯 **Specialized Analysis Types**

### **Betting Analysis**
When you use `analysis_type: "betting"`, the AI provides:
- Point spread analysis and recommendations
- Over/under insights and trends
- Moneyline value identification
- Player prop opportunities
- Line movement predictions
- Market inefficiency detection

### **Performance Analysis**
When you use `analysis_type: "performance"`, the AI provides:
- Individual player statistical breakdowns
- Team strength/weakness analysis
- Matchup advantages and disadvantages
- Trend identification and momentum
- Injury impact assessment

### **Fantasy Analysis** (NFL)
When you use `analysis_type: "fantasy"`, the AI provides:
- Start/sit recommendations
- Breakout candidate identification
- Matchup-based projections
- Waiver wire targets
- DFS lineup construction help

---

## 🚀 **Quick Start Guide**

### **1. Basic Game Analysis**
```python
# Get current WNBA games with betting focus
analyzeWnbaGames({
    "analysis_type": "betting"
})
```

### **2. Historical Game Review**
```python
# Analyze specific date
analyzeWnbaGames({
    "dates": "20250803",
    "analysis_type": "performance"
})
```

### **3. Custom Multi-Sport Analysis**
```python
# Analyze any sport with custom prompt
customSportsAnalysis({
    "sport": "basketball",
    "league": "nba",
    "endpoint": "news",
    "prompt": "Find all injury reports and assess impact on tonight's betting lines"
})
```

### **4. NFL Fantasy Focus**
```python
# Weekly fantasy analysis
analyzeNflGames({
    "week": 1,
    "analysis_type": "fantasy"
})
```

---

## 📋 **Best Practices**

### **For Betting Analysis:**
1. **Use specific dates** for historical context
2. **Combine with news endpoint** for injury updates
3. **Focus on recent games** for current form
4. **Request specific betting metrics** in custom prompts

### **For Performance Analysis:**
1. **Limit games analyzed** for focused insights
2. **Use player-specific prompts** for prop bets
3. **Compare team statistics** across multiple games
4. **Track trends over time** with date ranges

### **For Custom Analysis:**
1. **Be specific in prompts** for better results
2. **Combine multiple endpoints** for comprehensive view
3. **Use betting terminology** for relevant insights
4. **Request actionable recommendations**

---

## ⚙️ **Configuration**

### **MCP Server Setup**
Your server is configured in both Kiro and Claude:

**Kiro:** `.kiro/settings/mcp.json`
**Claude:** `.claude/mcp.json`

```json
{
  "mcpServers": {
    "sports-ai": {
      "command": "python",
      "args": ["mcp/sports_ai_mcp.py"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### **Environment Variables**
Required in `.env.local`:
```
OPENROUTER_API_KEY=sk-or-v1-[your-key]
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openrouter/horizon-beta
```

---

## 🔧 **Advanced Usage**

### **Multi-Sport Betting Dashboard**
```python
# Analyze multiple sports for tonight
customSportsAnalysis({
    "sport": "basketball",
    "league": "wnba", 
    "endpoint": "scoreboard",
    "prompt": "Provide betting recommendations for all games tonight including spreads, totals, and best value plays"
})

customSportsAnalysis({
    "sport": "football",
    "league": "nfl",
    "endpoint": "scoreboard", 
    "prompt": "Analyze this week's games for upset potential and underdog value"
})
```

### **Injury Impact Analysis**
```python
# Monitor injury reports across leagues
customSportsAnalysis({
    "sport": "basketball",
    "league": "wnba",
    "endpoint": "news",
    "prompt": "Extract all injury reports from the last 24 hours and assess betting line impact for affected teams"
})
```

### **Team Research Deep Dive**
```python
# Comprehensive team analysis
customSportsAnalysis({
    "sport": "basketball", 
    "league": "wnba",
    "endpoint": "teams",
    "prompt": "Provide detailed analysis of Las Vegas Aces including recent form, key players, strengths/weaknesses, and betting trends"
})
```

---

## 📈 **Performance & Reliability**

### **Data Accuracy**
- **Success Rate:** 86.2% (94/109 data points verified)
- **Update Frequency:** Real-time during games
- **Historical Data:** Current season available
- **Coverage:** All major US sports leagues

### **Response Times**
- **Live Data:** 1-3 seconds
- **AI Analysis:** 5-15 seconds
- **Complex Queries:** 10-30 seconds
- **News Updates:** 1-2 seconds

### **Limitations**
- **Betting Lines:** Not available via ESPN API
- **Historical Stats:** Limited to current season
- **International Sports:** Limited coverage
- **Rate Limits:** ESPN API has usage limits

---

## 🆘 **Troubleshooting**

### **Common Issues**

**"OpenRouter API key not configured"**
- Check `.env.local` file exists
- Verify `OPENROUTER_API_KEY` is set correctly
- Ensure no extra spaces or quotes

**"No game data available"**
- Try different date formats (YYYYMMDD)
- Check if games exist for that date
- Verify league/sport combination is valid

**"Analysis timeout"**
- Reduce number of games analyzed
- Simplify custom prompts
- Check OpenRouter API status

### **Getting Help**
- Check the data availability documentation
- Use the ESPN data validator tool
- Test with simpler queries first
- Verify MCP server is running

---

## 📚 **Related Documentation**
- [Data Availability Reference](data-availability.md)
- [ESPN API Endpoints](espn-endpoints.md)
- [Example Queries](example-queries.md)
- [Troubleshooting Guide](troubleshooting.md)

---

**Last Updated:** August 6, 2025  
**Version:** 1.0  
**Status:** Production Ready ✅