# Sports Betting Platform - Current Status

## Overview
Complete dual-MCP sports betting analytics platform providing **LIVE MLB data** and **LIVE betting odds** including player props. Both MCPs are fully operational on Railway.

## Platform Architecture

### <¯ Dual MCP System
- **MLB MCP**: Live MLB game data, schedules, stats, player info
- **Odds MCP v2**: Live betting odds including player props

## MCP Status

###  MLB MCP - Fully Operational
**Server URL**: `https://mlbmcp-production.up.railway.app/mcp`

**Core Features**:
- Live MLB schedules and scores
- Team rosters and player information  
- Game statistics and matchups
- Eastern Time schedule support
- Comprehensive MLB data coverage

**Key Tools**:
- `getMLBScheduleET` - Live MLB games by date
- `getMLBTeams` - All 30 MLB teams
- `getMLBTeamRoster` - Player rosters by team
- `getMLBPlayerStats` - Individual player statistics
- `getMLBTeamStats` - Team performance metrics

###  Odds MCP v2 - Fully Operational with Player Props  
**Server URL**: `https://odds-mcp-v2-production.up.railway.app/mcp`

**Core Features**:
- **Live betting odds** for all major sports
- **Player prop betting** for MLB (NEW!)
- Event-specific odds using direct HTTP calls
- Fixed URL encoding bugs from v1

**Supported Markets**:

#### Game Markets (All Sports)
- **h2h** - Moneyline odds
- **spreads** - Point/run spreads
- **totals** - Over/under totals

#### Player Props (MLB Only) 
- **batter_hits** - Player hits over/under (18+ players, 54+ props)
- **batter_home_runs** - Player home runs over/under (18 players)
- **pitcher_strikeouts** - Starting pitcher strikeouts (2 pitchers, 4 props)

**Key Tools**:
- `getSports` - Available sports from The Odds API
- `getOdds` - Game-level betting odds
- `getEvents` - Upcoming games with event IDs 
- `getEventOdds` - Event-specific odds for player props (NEW!)
- `getQuotaInfo` - API usage monitoring

## Live Data Examples

### Current MLB Game (Seattle Mariners @ Baltimore Orioles)
**Event ID**: `3406dc4194a80b6152139f93aa99e771`

#### Game Markets
- **Moneyline**: Orioles +112, Mariners -132
- **Run Line**: Orioles +1.5 (-142)
- **Total**: Over/Under 9.5 (-122/+100)

#### Player Props (Live Data)
**Batter Hits**:
- Julio Rodriguez: Over 1.5 hits (+145), Over 0.5 (-370)
- Gunnar Henderson: Over 1.5 hits (+170), Over 0.5 (-320)
- Ryan Mountcastle: Over 1.5 hits (+175), Over 0.5 (-310)

**Home Run Props**:
- Cal Raleigh: Over 0.5 HR (+168)
- Julio Rodriguez: Over 0.5 HR (+300)
- Gunnar Henderson: Over 0.5 HR (+360)

**Pitcher Strikeouts**:
- Tomoyuki Sugano: Over 3.5 K (-152), Under 3.5 K (+120)
- Logan Evans: Over 4.5 K (+140), Under 4.5 K (-188)

## Technical Achievements

###  Odds MCP v2 Fixes
- **Direct HTTP Implementation**: Replaced faulty `the-odds` package
- **URL Encoding Bug Fixed**: Package was encoding "us" ’ "u%2Cs" causing API errors
- **Event-Specific Endpoint**: Uses `/sports/{sport}/events/{event_id}/odds` for player props
- **Railway Deployment**: Auto-deploys via GitHub integration

###  Complete Workflow
1. **MLB MCP** provides game schedules and team/player data
2. **Odds MCP** provides event IDs via `getEvents`
3. **Odds MCP** provides player props via `getEventOdds` with event ID
4. **Live bookmaker data** from FanDuel, DraftKings, BetOnline, etc.

## Data Sources
- **MLB Data**: Live MLB API (official data)
- **Betting Odds**: The Odds API v4 (live bookmaker feeds)
- **Bookmakers**: FanDuel, DraftKings, Fanatics, BetOnline, Bovada
- **Coverage**: 7 live MLB games, 18+ players per game for props

## Development Status

###  Completed Features
- [x] Dual MCP architecture fully operational
- [x] Live MLB game data integration
- [x] Live betting odds for game markets
- [x] Player prop betting markets (hits, home runs, strikeouts)
- [x] Event-specific odds endpoint
- [x] Railway cloud deployment for both MCPs
- [x] Direct HTTP implementation bypassing faulty packages
- [x] Complete testing and validation

### <¯ Platform Ready
The platform is **fully operational** and provides comprehensive sports betting analytics with both MLB data and live betting odds including player props. Both MCPs are deployed, tested, and providing real-time data.

## Usage
Both MCPs can be used independently or together for complete sports betting analysis. The Odds MCP now supports the full spectrum from game-level betting (moneyline, spreads, totals) to granular player prop betting (individual player performance).

**Platform Status**:  **FULLY OPERATIONAL**