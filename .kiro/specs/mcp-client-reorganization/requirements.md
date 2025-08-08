# Requirements Document

## Introduction

This feature involves reorganizing the sports data client architecture to enforce strict separation between data access (via MCP tools) and client functionality. The goal is to eliminate direct ESPN API calls from client code, organize clients by data type rather than sport, and ensure all ESPN data flows through the sports_ai_mcp.py tools with strict OpenRouter usage for LLM interactions.

## Requirements

### Requirement 1

**User Story:** As a developer, I want client code organized by data type rather than sport, so that I have a clean separation of concerns and can handle all sports uniformly.

#### Acceptance Criteria

1. WHEN clients are organized THEN the system SHALL have separate clients for each data type: scoreboard, game, season, odds, and chat
2. WHEN any data type client is used THEN the system SHALL work with all supported sports (NFL, NBA, WNBA, MLB, NHL, MLS, EPL, La Liga, NCAAF, NCAAB)
3. WHEN clients are implemented THEN the system SHALL NOT have sport-specific client files (no nfl_client.py, nba_client.py, etc.)
4. WHEN data type clients are used THEN the system SHALL accept league parameters to specify which sport to query

### Requirement 2

**User Story:** As a developer, I want all ESPN data access to flow through MCP tools only, so that I have a consistent and controlled data access layer.

#### Acceptance Criteria

1. WHEN any client code is executed THEN the system SHALL NOT make direct requests to ESPN APIs via requests.get() calls
2. WHEN data is needed from ESPN THEN the system SHALL use only MCP tools (getScoreboard, getTeams, getGameSummary, analyzeGameStrict, probeLeagueSupport)
3. IF a grep search is performed for "site.api.espn.com" in the clients directory THEN the system SHALL return no matches
4. WHEN the current espn_client.py direct API usage is replaced THEN the system SHALL use MCP server calls instead

### Requirement 3

**User Story:** As a developer, I want core wrapper functions for MCP interactions, so that I have a clean abstraction layer for data access.

#### Acceptance Criteria

1. WHEN core_mcp.py is implemented THEN the system SHALL provide functions for scoreboard, teams, game_summary, analyze_game_strict, and probe_league_support
2. WHEN league keys are provided (nfl, college-football, nba, wnba, mens-college-basketball, mlb, nhl, usa.1, eng.1, esp.1) THEN the system SHALL map them to appropriate (sport, league) pairs matching the existing MCP server routes
3. WHEN MCP functions are called THEN the system SHALL handle errors gracefully and return structured responses
4. WHEN core_mcp.py calls the MCP server THEN the system SHALL use the existing sports_ai_mcp.py server running locally

### Requirement 4

**User Story:** As a developer, I want strict OpenRouter integration, so that LLM responses are based only on provided JSON data without fabrication.

#### Acceptance Criteria

1. WHEN core_llm.py is implemented THEN the system SHALL use environment variables (OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL) from .env.local
2. WHEN an LLM query is made THEN the system SHALL use a system prompt that prohibits inference or fabrication
3. IF a statistic is not present in the JSON data THEN the system SHALL respond with "unavailable"
4. WHEN making OpenRouter calls THEN the system SHALL use low temperature (0.0-0.2) and max_tokens around 700

### Requirement 5

**User Story:** As a user, I want specialized CLI clients organized by data type (not sport), so that I can efficiently access scoreboard, game, season, odds, and chat functionality across all sports.

#### Acceptance Criteria

1. WHEN scoreboard_cli.py is executed with "events <league> [YYYYMMDD]" THEN the system SHALL display event_id, teams, and status in tabular format for any supported league using MCP getScoreboard
2. WHEN game_cli.py is executed with "game <league> <event_id>" THEN the system SHALL fetch and display game summary data for any sport using MCP getGameSummary
3. WHEN game_cli.py is executed with "--ask <question>" flag THEN the system SHALL use MCP analyzeGameStrict to answer questions about the game data regardless of sport
4. WHEN season_cli.py is executed with "team-season <league> <team_id>" or "player-season <league> <player_id>" THEN the system SHALL use MCP getTeamSeasonStats/getPlayerSeasonStats and clearly indicate "supported:false" when MCP returns this status
5. WHEN odds_cli.py is executed with "odds <sport> [filters...]" THEN the system SHALL use only Wagyu Odds MCP tools and not ESPN data
6. WHEN chat_cli.py is executed with "ask <league> <date|today> <TEAM1> vs <TEAM2> <question>" THEN the system SHALL use MCP analyzeGameStrict tool for natural language queries

### Requirement 6

**User Story:** As a developer, I want sport-specific adapters for consistent data formatting, so that different sports data can be presented uniformly.

#### Acceptance Criteria

1. WHEN adapters are implemented for each sport (nfl.py, nba.py, wnba.py, mlb.py, nhl.py, soccer.py) THEN each SHALL provide a normalize() function that works with MCP response data
2. WHEN normalize() is called on MCP summary JSON THEN the system SHALL return a consistent dictionary structure appropriate for that sport (NFL: passing/rushing/receiving; NBA: players[pts,reb,ast,fg,3p,ft]; etc.)
3. WHEN adapter logic is implemented THEN the system SHALL keep it minimal and not calculate totals unless the MCP response provides them
4. WHEN adapters process data THEN the system SHALL work with the existing MCP server's data structure (boxscore, leaders, teams_meta)

### Requirement 7

**User Story:** As a developer, I want comprehensive testing coverage, so that I can ensure the refactored system works correctly.

#### Acceptance Criteria

1. WHEN unit tests are implemented THEN the system SHALL test adapters with frozen JSON samples without network calls
2. WHEN integration tests are implemented THEN the system SHALL test live MCP functionality for scoreboard and game summary
3. WHEN smoke tests are run THEN the system SHALL verify each data type CLI works with MCP locally
4. WHEN tests are executed THEN the system SHALL be rate-limit aware and skip live tests if no network or API key is available

### Requirement 8

**User Story:** As a user, I want enhanced CLI user experience features, so that I can work more efficiently with the sports data.

#### Acceptance Criteria

1. WHEN any feature CLI is executed with "--json" flag THEN the system SHALL output raw MCP data for debugging
2. WHEN game_cli.py is executed with "--fields" flag THEN the system SHALL output only selected columns
3. WHEN CLIs are executed without special flags THEN the system SHALL default to pretty-printed, human-readable output with aligned columns
4. WHEN timezone handling is implemented THEN the system SHALL use a canonical timezone for "today" and return meta.date_used in responses

### Requirement 9

**User Story:** As a developer, I want to migrate the existing sports_analysis.py to use the new MCP-only architecture, so that the current functionality is preserved while eliminating direct ESPN API calls.

#### Acceptance Criteria

1. WHEN sports_analysis.py is refactored THEN the system SHALL replace all espn_client.py imports with core_mcp.py calls
2. WHEN the SportsAnalysisSystem class is updated THEN the system SHALL use MCP tools instead of direct ESPN API calls
3. WHEN existing functionality is preserved THEN the system SHALL maintain the same user interface and output format
4. WHEN the migration is complete THEN the system SHALL mark espn_client.py as legacy and not use it in new clients

### Requirement 10

**User Story:** As a developer, I want proper logging and debugging capabilities, so that I can troubleshoot issues effectively.

#### Acceptance Criteria

1. WHEN DEBUG logging level is set THEN the system SHALL show full ESPN URLs and timing information from MCP responses
2. WHEN INFO logging level is set THEN the system SHALL show only league/date/event and OK/ERR status
3. IF LOG_FORMAT=json is set THEN the system SHALL output structured JSON logs for integration with log aggregation systems
4. WHEN MCP calls are made THEN the system SHALL log the MCP server responses for debugging