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

## Current Status (Updated August 11, 2024)

### ✅ Completed
- **MCP servers deployed** on Railway and accessible remotely
- **ESPN Direct API Integration** - Bypassed MCP issues, direct ESPN API calls working perfectly
- **Interactive testing script** with league selection menu  
- **Game fetching** with event IDs for MLB, NBA, WNBA, MLS, EPL, NFL, NHL
- **Eastern Time focus** - all times displayed in ET
- **Clean project structure** - removed complex testing code, focused on step-by-step approach
- **Full ESPN functionality** - Today's games, team info, event IDs, proper time formatting
- **Smart ESPN mapping** - Direct sport/league to ESPN URL path mapping
- **Roster integration** - ESPN roster API calls for player matching (when needed)

### 🚫 Current Blocker: MCP Odds API Integration Issue
**Problem**: FastMCP server requires proper JSON-RPC session initialization before tool calls
- **Error**: `"Bad Request: Missing session ID"` 
- **Root Cause**: MCP is a stateful protocol expecting session-based communication
- **What We Tried**: Simple HTTP POST calls to MCP endpoints
- **What MCP Expects**: 
  1. Initialize session with `{"jsonrpc": "2.0", "method": "initialize"}`
  2. Then make tool calls with session context

**Current ESPN Status**: ✅ **FULLY WORKING** - 11 MLB games fetched successfully today
**Current Odds Status**: ❌ **BLOCKED** - Cannot access MCP odds tools without proper protocol

### 🔄 Next Actions Needed
**Option 1**: Implement proper MCP client protocol (complex)
**Option 2**: Add simple HTTP wrapper to MCP server (easier) 
**Option 3**: Direct Odds API calls if keys available (bypasses MCP)

### ⏳ Next Steps (After Odds Fix)
1. Complete odds integration pipeline
2. Test player props functionality 
3. Build player matching system (ESPN players ↔ Odds API players)
4. Add value calculation algorithms (recent stats vs betting lines)
5. Create recommendation engine

## Testing Script: `interactive_sports_test.py`
Primary development happens in: `C:\Users\fstr2\Desktop\sports\interactive_sports_test.py`

### Current Implementation Status

**✅ Working Pipeline (ESPN Direct):**
1. **Games**: Direct ESPN API → Today's games with Eastern Time ✅
2. **Rosters**: Direct ESPN API → Player data for matching ✅  
3. **Odds**: MCP Server → **BLOCKED by session issue** ❌
4. **Player Props**: MCP Server → **BLOCKED by session issue** ❌

### Key Functions & Architecture

**✅ Working Functions:**
- `make_espn_scoreboard_request()` - Direct ESPN scoreboard API calls
- `make_espn_roster_request()` - Direct ESPN roster API calls  
- `fetch_games()` - Game fetching with proper formatting
- `format_time_eastern()` - Time zone conversion to ET
- League selection and user interface

**❌ Blocked Functions:**
- `fetch_odds_for_games()` - Tries to call `/odds/get-odds` → 404 error
- `fetch_player_props_for_game()` - Tries to call `/odds/event-odds` → 404 error
- All MCP-dependent odds functionality

### Current Data Flow
```
User Input → League Selection → ESPN Direct API → Games Retrieved ✅
                                              ↓
                              MCP Odds Server → SESSION ERROR ❌
```

**Key Features (Working):**
- **Interactive league selection** (MLB, NBA, WNBA, MLS, EPL, NFL, NHL) ✅
- **Eastern Time display** - All game times converted to ET ✅
- **Event ID extraction** - Full game metadata with ESPN event IDs ✅
- **Team and matchup formatting** - Clean display of games ✅

**Key Features (Blocked):**
- **Odds integration** - Cannot access MCP odds tools ❌
- **Player props** - Cannot fetch betting lines ❌
- **Game + odds matching** - ESPN games can't be matched with betting data ❌