# Sports Betting Recommendation System

## Project Overview
I am building a sports betting recommendation system that will eventually become:
1. **Discord bot** - For initial subscriber recommendations
2. **Web application** - For broader user access

## Core Workflow
The system follows this data pipeline:

1. **Fetch Daily Games** - ESPN MCP gets today's games and teams
2. **Get Player Props** - Odds API MCP fetches betting lines for players
3. **Collect Player Stats** - ESPN provides last 5 games stats for relevant metrics
4. **Calculate Value** - Compare recent performance vs betting lines
5. **Present Recommendations** - Format and deliver to subscribers

## Technical Architecture

### Data Sources
- **ESPN API** - Games, teams, players, statistics
- **The Odds API** - Betting lines and player props
- Both APIs accessed via **MCP servers hosted on Railway**

### Data Storage
- **File-based connections** between teams and players
- **Player IDs and Team IDs** stored locally for mapping
- **Reference directories**: 
  - `C:\Users\fstr2\Desktop\sports\espn ids\` 
  - `C:\Users\fstr2\Desktop\sports\stats\`

### Current Challenges
- **Different sports have different API endpoints** for statistics
- **Solving sport-by-sport** to handle varying data structures
- **Player matching** between ESPN and betting sites

## Current Status (Updated August 2024)

### ✅ Completed
- **MCP servers deployed** on Railway and accessible remotely
- **100% MCP integration** - All ESPN and Odds API calls through Railway server
- **Interactive testing script** with league selection menu
- **Game fetching** with event IDs for MLB, NBA, WNBA, MLS, EPL, NFL, NHL
- **Eastern Time focus** - all times displayed in ET
- **Clean project structure** - removed complex testing code, focused on step-by-step approach
- **Odds integration** - Full betting odds (moneylines, spreads, totals) with team matching
- **API call tracking** - Monitor Odds API usage with running counter
- **Complete game + odds pipeline** - Games matched with betting lines from multiple sportsbooks
- **Player props integration** - Direct game selection with sport-specific prop markets
- **Smart data reuse** - Event ID matching from existing odds data (no extra API calls)

### 🔄 In Progress  
- **Testing complete pipeline** across active leagues (MLB, WNBA focus)
- **Validating player props display** for different sports

### ⏳ Next Steps
1. Integrate player statistics collection (ESPN MCP)
2. Build player matching system (ESPN players ↔ Odds API players)
3. Add value calculation algorithms (recent stats vs betting lines)
4. Create recommendation engine
5. Build automated daily analysis pipeline

## Testing Script
Primary development happens in: `C:\Users\fstr2\Desktop\sports\interactive_sports_test.py`

**Complete 3-Step Pipeline:**
1. **Games**: ESPN MCP → Today's games with Eastern Time
2. **Odds**: Odds API MCP → Moneylines, spreads, totals for matched games  
3. **Player Props**: Direct game selection → Sport-specific prop markets

**Key Features:**
- **Interactive league selection** (MLB, NBA, WNBA, MLS, EPL, NFL, NHL)
- **Direct game selection** - Type game number to view player props
- **Sport-specific markets** - MLB (hits, HRs, Ks), WNBA (points, rebounds, assists, 3PM)
- **Smart data reuse** - Event ID matching from existing odds data
- **100% MCP integration** - All API calls through Railway server
- **API usage tracking** - Running counter for cost management
- **Eastern Time display** - All game times converted to ET