# Sports Betting Platform - Current Status

## Overview
Complete **triple-MCP** sports betting analytics platform providing **LIVE MLB data**, **LIVE soccer data**, and **LIVE betting odds** including player props. All three MCPs are fully operational on Railway with integrated testing.

## Platform Architecture

### ⚡ Triple MCP System
- **MLB MCP**: Live MLB game data, schedules, stats, player info
- **Soccer MCP**: Live EPL and La Liga fixtures, standings, team data (NEW!)
- **Odds MCP v2**: Live betting odds including player props for all sports

### 🌐 Railway Cloud Deployment
All MCPs are deployed on Railway with:
- **Auto-deployment** from GitHub repositories
- **Environment variables** for API keys and configuration
- **Custom domains** with railway.app subdomains
- **railway.toml** configuration files for build/deploy settings
- **Background workers** using async Python frameworks

## MCP Status

### ✅ MLB MCP - Fully Operational
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

### ✅ Soccer MCP - Fully Operational (NEW!)
**Server URL**: `https://soccermcp-production.up.railway.app/mcp`

**Core Features**:
- Live EPL (Premier League) and La Liga fixtures
- Current league standings/tables with full statistics
- Team information and squad details
- Match details with live status updates
- Top scorers and competition data
- Limited to EPL and La Liga due to Football-Data.org plan restrictions

**Key Tools**:
- `getCompetitions` - Available soccer competitions (EPL, La Liga)
- `getCompetitionMatches` - Live fixtures by competition and date range
- `getCompetitionStandings` - Current league tables with full stats
- `getCompetitionTeams` - Teams in each competition
- `getTeamMatches` - Specific team fixtures
- `getMatchDetails` - Individual match information
- `getTopScorers` - Leading goal scorers by competition

**Data Source**: Football-Data.org API v4 (limited plan: EPL + La Liga only)

### ✅ Odds MCP v2 - Fully Operational with Player Props  
**Server URL**: `https://odds-mcp-v2-production.up.railway.app/mcp`

**Core Features**:
- **Live betting odds** for all major sports including soccer
- **Player prop betting** for MLB
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
- `getEventOdds` - Event-specific odds for player props
- `getQuotaInfo` - API usage monitoring

## Integration Examples

### 🏈 Soccer + Odds Integration (TESTED)
**Liverpool vs Bournemouth Example**:

**Fixture Data** (Soccer MCP):
- Match: AFC Bournemouth @ Liverpool FC
- Date: 2025-08-15T19:00:00Z
- Status: TIMED (scheduled)
- Competition: Premier League (PL)

**Betting Odds** (Odds MCP):
- **BetRivers**: Liverpool -315, Bournemouth +750, Draw +540
- **DraftKings**: Liverpool -320, Bournemouth +750, Draw +500
- **Totals**: Over/Under 3.5 goals available

### ⚾ MLB + Odds Integration (ESTABLISHED)
**Seattle Mariners @ Baltimore Orioles Example**:

**Game Data** (MLB MCP):
- Live MLB schedules, team rosters, player stats
- Event identification and team information

**Betting Markets** (Odds MCP):
- **Moneyline**: Orioles +112, Mariners -132
- **Run Line**: Orioles +1.5 (-142)
- **Total**: Over/Under 9.5 runs
- **Player Props**: 54+ individual player betting markets

## Testing Infrastructure

### 🧪 Comprehensive Test Suites
Each MCP has dedicated test scripts that validate:

#### Soccer MCP Tests
- `competitions_test.py` - Verify EPL and La Liga access
- `schedule_test.py` - Live fixture data retrieval
- `standings_test.py` - League table data with full statistics
- `team_matches_test.py` - Team-specific fixture data
- `test_odds_integration.py` - Combined fixture + odds data

#### Test Results Export
- JSON result files with detailed analysis
- Performance metrics and API response validation
- Error handling and edge case testing
- Mock data support for development without API quota usage

## Technical Achievements

### ✅ Soccer MCP Implementation
- **Football-Data.org API v4** integration with proper authentication
- **Async HTTP client** using httpx for optimal performance
- **Comprehensive error handling** with mock data fallbacks
- **Railway deployment** with proper environment configuration
- **7 specialized tools** covering all soccer data needs within plan limits

### ✅ Multi-MCP Integration
- **Cross-MCP communication** tested and validated
- **Team name matching** between Soccer and Odds MCPs
- **Date/time synchronization** across different data sources
- **Unified response formats** for consistent data handling

### ✅ Odds MCP v2 Fixes
- **Direct HTTP Implementation**: Replaced faulty `the-odds` package
- **URL Encoding Bug Fixed**: Package was encoding "us" → "u%2Cs" causing API errors
- **Event-Specific Endpoint**: Uses `/sports/{sport}/events/{event_id}/odds` for player props
- **Railway Deployment**: Auto-deploys via GitHub integration

## Data Sources

### Primary APIs
- **MLB Data**: Live MLB API (official data)
- **Soccer Data**: Football-Data.org API v4 (EPL + La Liga only)
- **Betting Odds**: The Odds API v4 (live bookmaker feeds)

### Bookmaker Coverage
- **FanDuel, DraftKings, Fanatics, BetOnline, Bovada**
- **Coverage**: 7 live MLB games, 10+ EPL/La Liga matches
- **Markets**: Game odds + 18+ players per MLB game for props

## Development Status

### ✅ Completed Features
- [x] Triple MCP architecture fully operational
- [x] Live MLB game data integration
- [x] Live soccer data integration (EPL + La Liga)
- [x] Live betting odds for game markets (all sports)
- [x] Player prop betting markets (MLB)
- [x] Cross-MCP integration (Soccer + Odds tested)
- [x] Event-specific odds endpoint
- [x] Railway cloud deployment for all three MCPs
- [x] Direct HTTP implementation bypassing faulty packages
- [x] Comprehensive testing suites with JSON exports
- [x] Complete validation and live data verification

### 🎯 Platform Ready
The platform is **fully operational** and provides comprehensive sports betting analytics with MLB data, soccer data, and live betting odds including player props. All three MCPs are deployed, tested, and providing real-time data with proven cross-MCP integration.

## Railway Infrastructure

### 🚀 Deployment Configuration
Each MCP is deployed with:

**Build Configuration**:
```toml
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "python server.py"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

**Environment Variables**:
- API keys securely stored in Railway environment
- URL configurations for cross-MCP communication
- Feature flags for testing and production modes

**Auto-Deployment**:
- Connected to GitHub repositories
- Automatic deployment on git push
- Build logs and monitoring available
- Custom railway.app subdomains

## Usage

All three MCPs can be used independently or together for complete sports betting analysis:

1. **Soccer MCP** provides live fixture data and league standings
2. **Odds MCP** provides betting odds for soccer and other sports  
3. **MLB MCP** provides comprehensive baseball data
4. **Cross-integration** combines fixture data with betting odds

The platform now supports the full spectrum from game-level betting (moneyline, spreads, totals) to granular player prop betting (individual player performance) across multiple sports.

**Platform Status**: ✅ **FULLY OPERATIONAL** (Triple MCP Architecture)