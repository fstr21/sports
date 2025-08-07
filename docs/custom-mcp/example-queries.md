# Sports AI MCP Example Queries
## Real-World Usage Examples for Your Custom MCP

**Purpose:** Practical examples showing how to use your Sports AI MCP for different betting and analysis scenarios.

---

## 🏀 **WNBA Analysis Examples**

### **Basic Game Analysis**
```python
# Get current WNBA games with general analysis
analyzeWnbaGames({
    "analysis_type": "general"
})
```

### **Betting-Focused Analysis**
```python
# Analyze today's games for betting opportunities
analyzeWnbaGames({
    "analysis_type": "betting",
    "limit": 3
})
```

### **Historical Game Review**
```python
# Analyze specific completed game
analyzeWnbaGames({
    "dates": "20250803",
    "analysis_type": "performance",
    "limit": 1
})
```

### **Player Performance Focus**
```python
# Focus on individual player performances
analyzeWnbaGames({
    "analysis_type": "performance",
    "limit": 2
})
```

### **Predictions and Trends**
```python
# Get predictions for upcoming games
analyzeWnbaGames({
    "analysis_type": "predictions"
})
```

---

## 🏈 **NFL Analysis Examples**

### **Weekly Fantasy Analysis**
```python
# Analyze current NFL week for fantasy
analyzeNflGames({
    "analysis_type": "fantasy"
})
```

### **Specific Week Analysis**
```python
# Analyze NFL Week 1 for betting
analyzeNflGames({
    "week": 1,
    "analysis_type": "betting"
})
```

### **General Game Overview**
```python
# Get general overview of current NFL games
analyzeNflGames({
    "analysis_type": "general"
})
```

### **Predictions Focus**
```python
# Get NFL predictions and trends
analyzeNflGames({
    "analysis_type": "predictions"
})
```

---

## 🎯 **Custom Sports Analysis Examples**

### **Multi-Sport Betting Dashboard**
```python
# NBA games analysis
customSportsAnalysis({
    "sport": "basketball",
    "league": "nba",
    "endpoint": "scoreboard",
    "prompt": "Analyze tonight's NBA games for betting value including spreads, totals, and best moneyline plays"
})

# MLB games analysis  
customSportsAnalysis({
    "sport": "baseball",
    "league": "mlb", 
    "endpoint": "scoreboard",
    "prompt": "Identify MLB betting opportunities focusing on run totals and pitcher matchups"
})
```

### **Injury Impact Analysis**
```python
# Monitor WNBA injuries
customSportsAnalysis({
    "sport": "basketball",
    "league": "wnba",
    "endpoint": "news",
    "prompt": "Extract all injury reports from the last 48 hours and assess impact on upcoming games and betting lines"
})

# Monitor NFL injuries
customSportsAnalysis({
    "sport": "football", 
    "league": "nfl",
    "endpoint": "news",
    "prompt": "Find all quarterback and key player injury updates and analyze fantasy football impact"
})
```

### **Team Research Deep Dives**
```python
# WNBA team analysis
customSportsAnalysis({
    "sport": "basketball",
    "league": "wnba",
    "endpoint": "teams", 
    "prompt": "Provide comprehensive analysis of Las Vegas Aces including recent form, key players, home/road splits, and betting trends"
})

# NFL team analysis
customSportsAnalysis({
    "sport": "football",
    "league": "nfl",
    "endpoint": "teams",
    "prompt": "Analyze Kansas City Chiefs roster, coaching changes, and Super Bowl odds for the upcoming season"
})
```

### **Upset and Value Identification**
```python
# Find WNBA upsets
customSportsAnalysis({
    "sport": "basketball",
    "league": "wnba",
    "endpoint": "scoreboard",
    "prompt": "Identify potential upset opportunities in today's games based on recent form, injuries, and historical matchups"
})

# Find NFL value bets
customSportsAnalysis({
    "sport": "football",
    "league": "nfl", 
    "endpoint": "scoreboard",
    "prompt": "Find undervalued teams this week based on public betting trends and actual team strength"
})
```

### **Player Prop Analysis**
```python
# WNBA player props
customSportsAnalysis({
    "sport": "basketball",
    "league": "wnba",
    "endpoint": "scoreboard",
    "prompt": "Analyze A'ja Wilson's recent performance and identify over/under opportunities for points, rebounds, and assists in tonight's game"
})

# NFL player props
customSportsAnalysis({
    "sport": "football",
    "league": "nfl",
    "endpoint": "scoreboard", 
    "prompt": "Evaluate Patrick Mahomes passing yards prop based on opponent defense, weather conditions, and recent performance trends"
})
```

---

## 📊 **Advanced Analysis Examples**

### **Line Movement Analysis**
```python
# Track betting market sentiment
customSportsAnalysis({
    "sport": "basketball",
    "league": "wnba",
    "endpoint": "news",
    "prompt": "Analyze recent news and identify factors that could cause betting line movements for tonight's games"
})
```

### **Matchup-Specific Analysis**
```python
# Head-to-head analysis
customSportsAnalysis({
    "sport": "basketball",
    "league": "wnba", 
    "endpoint": "scoreboard",
    "prompt": "Analyze the Las Vegas Aces vs Connecticut Sun matchup focusing on pace of play, defensive matchups, and historical scoring trends"
})
```

### **Season-Long Trends**
```python
# Identify season trends
customSportsAnalysis({
    "sport": "basketball",
    "league": "wnba",
    "endpoint": "scoreboard",
    "prompt": "Identify teams that consistently perform better/worse than expected and explain the underlying factors"
})
```

### **Weather and Venue Analysis**
```python
# Outdoor sports weather impact
customSportsAnalysis({
    "sport": "baseball",
    "league": "mlb",
    "endpoint": "scoreboard",
    "prompt": "Analyze how weather conditions and ballpark factors will impact tonight's games, especially for over/under bets"
})
```

---

## 🎲 **Specific Betting Scenarios**

### **Same Game Parlays**
```python
# SGP analysis
customSportsAnalysis({
    "sport": "basketball",
    "league": "wnba",
    "endpoint": "scoreboard",
    "prompt": "For the Aces vs Valkyries game, identify correlated bets for a same-game parlay including team total, player props, and game outcome"
})
```

### **Live Betting Opportunities**
```python
# In-game analysis
customSportsAnalysis({
    "sport": "basketball", 
    "league": "wnba",
    "endpoint": "scoreboard",
    "prompt": "Analyze the current live game momentum and identify second-half betting opportunities based on first-half performance"
})
```

### **Futures and Season Bets**
```python
# Championship analysis
customSportsAnalysis({
    "sport": "basketball",
    "league": "wnba",
    "endpoint": "teams",
    "prompt": "Evaluate WNBA championship futures odds and identify value bets based on current team strength, remaining schedule, and playoff positioning"
})
```

### **Arbitrage Opportunities**
```python
# Market inefficiency detection
customSportsAnalysis({
    "sport": "football",
    "league": "nfl",
    "endpoint": "news",
    "prompt": "Identify any news or developments that might create temporary market inefficiencies or arbitrage opportunities"
})
```

---

## 🔍 **Research and Preparation Examples**

### **Weekly Preparation**
```python
# Monday preparation for the week
customSportsAnalysis({
    "sport": "football",
    "league": "nfl",
    "endpoint": "news",
    "prompt": "Summarize all key developments from this weekend's games and identify early value for next week's betting lines"
})
```

### **Daily Betting Card**
```python
# Daily game analysis
customSportsAnalysis({
    "sport": "basketball",
    "league": "wnba", 
    "endpoint": "scoreboard",
    "prompt": "Create a daily betting card with best bets, value plays, and games to avoid for today's WNBA slate"
})
```

### **Bankroll Management**
```python
# Risk assessment
customSportsAnalysis({
    "sport": "basketball",
    "league": "wnba",
    "endpoint": "scoreboard",
    "prompt": "Assess the confidence level and risk factors for today's games and recommend appropriate bet sizing"
})
```

---

## 🎯 **Prompt Engineering Tips**

### **For Better Results**
1. **Be Specific:** Instead of "analyze the game," ask for "betting analysis focusing on point spread value"
2. **Request Actions:** Ask for "recommendations" not just "information"
3. **Include Context:** Mention "recent form," "injuries," "historical matchups"
4. **Specify Metrics:** Request "shooting percentages," "pace of play," "defensive efficiency"

### **Effective Prompt Patterns**
```python
# Pattern 1: Analysis + Recommendation
"prompt": "Analyze [specific aspect] and provide actionable betting recommendations"

# Pattern 2: Context + Focus
"prompt": "Based on recent form and injury reports, focus on [specific betting market]"

# Pattern 3: Comparison + Value
"prompt": "Compare [teams/players] and identify the best value betting opportunities"

# Pattern 4: Trend + Prediction  
"prompt": "Identify trends in [specific area] and predict impact on [betting market]"
```

---

## 📈 **Performance Optimization**

### **Faster Queries**
```python
# Limit scope for speed
analyzeWnbaGames({
    "limit": 1,  # Analyze fewer games
    "analysis_type": "betting"  # Specific analysis type
})
```

### **Comprehensive Analysis**
```python
# Multiple related queries
customSportsAnalysis({
    "sport": "basketball",
    "league": "wnba",
    "endpoint": "scoreboard", 
    "prompt": "Provide comprehensive betting analysis including spreads, totals, props, and live betting opportunities for tonight's slate"
})
```

---

## 🆘 **Troubleshooting Examples**

### **When No Games Are Found**
```python
# Check different dates
analyzeWnbaGames({
    "dates": "20250807",  # Try specific date
    "analysis_type": "general"
})
```

### **When Analysis Is Too General**
```python
# Use more specific prompts
customSportsAnalysis({
    "sport": "basketball",
    "league": "wnba",
    "endpoint": "scoreboard",
    "prompt": "Focus specifically on the Las Vegas Aces game tonight and provide point spread analysis with reasoning"
})
```

---

**Pro Tip:** Start with simple queries and gradually add complexity as you learn what works best for your specific betting strategy and analysis needs.