# Implementation Plan

- [x] 1. Set up project structure and core MCP wrapper

  - Create clients directory structure with core_mcp.py and core_llm.py
  - Implement league mapping and MCP server communication functions
  - Add error handling and response validation for MCP calls
  - _Requirements: 2.1, 2.2, 3.1, 3.4_

- [x] 2. Implement core MCP integration layer

- [x] 2.1 Create core_mcp.py with MCP server communication

  - Write functions for scoreboard, teams, game_summary, analyze_game_strict, probe_league_support
  - Implement league key mapping (nfl→football/nfl, nba→basketball/nba, etc.)
  - Add comprehensive error handling for MCP server responses
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 2.2 Create core_llm.py with strict OpenRouter integration

  - Implement strict_answer function with system prompt that prevents fabrication
  - Load configuration from .env.local (OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL)
  - Set low temperature (0.0-0.2) and max_tokens ~700 for controlled responses
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 3. Create sport-specific data adapters

- [x] 3.1 Implement NFL adapter with passing/rushing/receiving normalization

  - Write nfl.py with normalize() function that processes MCP boxscore data
  - Extract passing stats (completions/attempts, yards, TDs, INTs, rating)
  - Extract rushing stats (carries, yards, average, TDs, long)
  - Extract receiving stats (receptions, yards, average, TDs, long, targets)
  - _Requirements: 6.1, 6.2, 6.4_

- [x] 3.2 Implement NBA/WNBA adapters with player statistics normalization

  - Write nba.py and wnba.py with normalize() functions for basketball data
  - Extract player stats (points, rebounds, assists, field goals, 3-pointers, free throws)
  - Handle team statistics and game flow data from MCP responses
  - _Requirements: 6.1, 6.2, 6.4_

- [x] 3.3 Implement MLB, NHL, and Soccer adapters

  - Write mlb.py with batting/pitching statistics normalization
  - Write nhl.py with skater/goalie statistics normalization
  - Write soccer.py with player statistics (minutes, goals, assists, cards, saves)
  - Keep adapter logic minimal and work with existing MCP data structure
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 4. Build scoreboard CLI client

- [x] 4.1 Create scoreboard_cli.py with events listing functionality

  - Implement "events <league> [YYYYMMDD]" command using core_mcp.scoreboard()
  - Display event_id, teams, status in tabular format for any supported league
  - Add --json flag for raw MCP output and --pretty flag for formatted display
  - _Requirements: 1.1, 1.2, 5.1, 8.1_

- [x] 4.2 Add command-line argument parsing and error handling

  - Parse league parameter and optional date parameter
  - Validate league codes against supported leagues
  - Handle MCP server errors gracefully with user-friendly messages
  - _Requirements: 5.1, 8.1_

- [x] 5. Build game CLI client with adapter integration

- [x] 5.1 Create game_cli.py with basic game summary functionality

  - Implement "game <league> <event_id>" command using core_mcp.game_summary()
  - Display game summary data for any sport using MCP getGameSummary
  - Add --json flag for raw MCP output
  - _Requirements: 1.1, 1.2, 5.2, 8.1_

- [x] 5.2 Integrate sport adapters for consistent data formatting

  - Import and use appropriate adapter (nfl.py, nba.py, etc.) based on league
  - Apply adapter normalization to MCP response data before display
  - Handle cases where adapter normalization fails gracefully
  - _Requirements: 6.1, 6.2, 6.4_

- [x] 5.3 Add OpenRouter integration for natural language questions

  - Implement --ask flag that uses core_llm.strict_answer()
  - Pass MCP game summary data to OpenRouter with user question
  - Display AI analysis based only on provided JSON data
  - _Requirements: 4.1, 4.2, 4.3, 5.3_

- [x] 5.4 Add field filtering and enhanced display options

  - Implement --fields flag to output only selected statistics columns
  - Add pretty-printed, human-readable output with aligned columns as default
  - Handle missing statistics gracefully with "unavailable" responses
  - _Requirements: 8.2, 8.3_

- [x] 6. Build season and odds CLI clients

- [x] 6. Build season and odds CLI clients

- [x] 6.1 Create season_cli.py with team and player season stats

  - Implement "team-season <league> <team_id>" and "player-season <league> <player_id>" commands
  - Use core_mcp functions to call MCP getTeamSeasonStats/getPlayerSeasonStats
  - Clearly display "supported:false" when MCP returns this status
  - _Requirements: 5.4_

- [x] 6.2 Create odds_cli.py using only Wagyu Odds MCP

  - Implement "odds <sport> [filters...]" command
  - Use only Wagyu Odds MCP tools, completely separate from ESPN data
  - Handle odds data formatting and display
  - _Requirements: 5.5_

- [x] 7. Build chat CLI for natural language interface

- [x] 7.1 Create chat_cli.py with natural language query processing

  - Implement "ask <league> <date|today> <TEAM1> vs <TEAM2> <question>" command
  - Use core_mcp.analyze_game_strict() for contextual responses
  - Add team name matching and resolution logic
  - _Requirements: 5.6_

- [x] 7.2 Add date handling and team name resolution

  - Handle "today" parameter with proper timezone conversion
  - Implement fuzzy team name matching for user convenience
  - Return meta.date_used in responses for clarity
  - _Requirements: 8.4_

- [x] 8. Migrate existing sports_analysis.py to MCP-only architecture

- [x] 8.1 Replace espn_client.py imports with core_mcp.py calls

  - Update all ESPN API calls to use core_mcp wrapper functions
  - Remove direct requests.get() calls to ESPN APIs
  - Maintain existing SportsAnalysisSystem class interface
  - _Requirements: 9.1, 9.2_

- [x] 8.2 Preserve existing functionality and user interface

  - Ensure all existing methods work with MCP data instead of direct ESPN calls
  - Maintain same output format and user experience
  - Test that existing usage patterns continue to work
  - _Requirements: 9.3_

- [x] 8.3 Mark espn_client.py as legacy and update documentation

  - Add deprecation notice to espn_client.py
  - Update imports and references to use new MCP-only clients
  - Document migration path for any remaining direct ESPN usage
  - _Requirements: 9.4_

- [-] 9. Add comprehensive testing coverage

- [x] 9.1 Create unit tests for adapters with frozen JSON samples

  - Write test_adapters_nfl.py, test_adapters_nba.py, etc.
  - Use frozen ESPN JSON samples from actual MCP responses
  - Test normalization functions with various data scenarios and missing data
  - _Requirements: 7.1_

- [x] 9.2 Create integration tests for CLI clients with live MCP


  - Write test_feature_game_cli.py and test_scoreboard_cli.py
  - Test live MCP functionality for scoreboard and game summary
  - Verify each data type CLI works with MCP server locally
  - _Requirements: 7.2, 7.3_

- [x] 9.3 Add smoke tests and end-to-end verification






  - Create tests that verify no direct ESPN API calls in clients directory
  - Test MCP server connectivity and error handling
  - Make tests rate-limit aware and skip if no network/API keys available
  - _Requirements: 7.4_

- [x] 10. Implement logging and debugging capabilities





- [x] 10.1 Add structured logging with configurable verbosity levels



  - Implement DEBUG level logging showing full ESPN URLs and timing from MCP responses
  - Implement INFO level logging showing only league/date/event and OK/ERR status
  - Add LOG_FORMAT=json support for structured logs
  - _Requirements: 10.1, 10.2, 10.3_


- [x] 10.2 Add MCP call logging and debugging features


  - Log MCP server responses for debugging purposes
  - Add request/response timing information
  - Include error context and troubleshooting information
  - _Requirements: 10.4_

- [x] 11. Final integration and validation
- [x] 11.1 Verify complete elimination of direct ESPN API calls

  - Run grep search for "site.api.espn.com" in clients directory to confirm no matches
  - Test all CLI clients work with MCP server only
  - Validate that all requirements are met through end-to-end testing
  - _Requirements: 2.3_

- [x] 11.2 Performance testing and optimization
  - Test CLI response times with MCP server
  - Verify memory usage is reasonable for command-line tools
  - Ensure error handling is robust across all failure scenarios
  - _Requirements: All requirements validation_
