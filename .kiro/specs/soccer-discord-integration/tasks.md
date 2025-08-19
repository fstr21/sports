# Implementation Plan

- [x] 1. Create soccer integration foundation module




  - Create `discord/soccer_integration.py` with base classes and MCP client
  - Implement `SoccerMCPClient` class with connection handling and basic MCP communication
  - Add configuration constants for Soccer MCP server URL and supported leagues
  - Create data models (`ProcessedMatch`, `BettingOdds`, `H2HInsights`) using dataclasses
  - Write unit tests for MCP client connection and basic data structures
  - _Requirements: 1.3, 2.1, 6.1_

- [x] 2. Implement core soccer data processing functionality





  - Create `SoccerDataProcessor` class with odds conversion and team name cleaning
  - Implement `convert_to_american_odds()` method for decimal to American odds conversion
  - Add `clean_team_name_for_channel()` method following MLB naming patterns
  - Create `process_match_data()` method to normalize MCP responses into `ProcessedMatch` objects
  - Implement `validate_date_format()` supporting MM/DD/YYYY, DD-MM-YYYY, and YYYY-MM-DD formats
  - Write comprehensive unit tests for data processing methods
  - _Requirements: 1.2, 2.2, 5.5_

- [x] 3. Build soccer channel management system





  - Create `SoccerChannelManager` class extending existing channel management patterns
  - Implement `create_match_channels()` method following MLB channel creation logic
  - Add `generate_channel_name()` method using format: `📊 {date_short}-{away_team}-vs-{home_team}`
  - Create `get_or_create_soccer_category()` method for "⚽ SOCCER" category management
  - Implement channel cleanup logic with 3-day retention policy
  - Write integration tests for channel creation and management
  - _Requirements: 1.4, 4.1, 4.2, 4.3_

- [x] 4. Create dual-endpoint Discord embed builders matching schedule.py output format








  - Create `SoccerEmbedBuilder` class with league-specific color schemes and multi-embed generation capability
  - Implement `create_match_preview_embed()` with basic match info (teams, time, venue, odds) as first embed
  - Add `create_h2h_historical_record_embed()` displaying H2H endpoint data (total meetings, wins/losses/draws, historical goals)
  - Create `create_team_analysis_embed()` for individual team analysis from matches endpoint (recent form, goals per game, clean sheets, card discipline, advanced metrics)
  - Implement `create_comprehensive_betting_insights_embed()` combining H2H patterns with team form for enhanced recommendations
  - Add `create_comprehensive_analysis_embed_set()` method that generates all 4-5 embeds for a match using dual-endpoint data
  - Port schedule.py's text formatting logic to Discord embed fields (team breakdowns, betting insights, advanced metrics display)
  - Implement error handling for missing data with graceful embed degradation (show available data, indicate missing sections)
  - Create embed content validation to ensure consistency with schedule.py analysis output
  - Write unit tests comparing embed content with schedule.py console output for accuracy verification
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.4, 3.5, 7.1, 7.4, 7.5_

- [-] 5. Enhance /create-channels command with automatic dual-endpoint analysis population



  - Modify existing `/create-channels` slash command to include soccer dropdown option with date input validation
  - Implement `create_match_channels_with_comprehensive_analysis()` method in SoccerChannelManager that creates channels AND automatically populates them
  - Create automatic population workflow: for each match → create channel → make 3 MCP calls (1 H2H + 2 matches) → post 4-5 embeds
  - Add `populate_channel_with_dual_endpoint_analysis()` method that orchestrates H2H endpoint call + 2 matches endpoint calls per channel
  - Implement sequential embed posting: Match Preview → H2H Historical Record → Home Team Analysis → Away Team Analysis → Betting Insights
  - Add comprehensive error handling for MCP server failures, partial data scenarios, and Discord API rate limits during bulk channel creation
  - Create progress feedback messages showing channel creation status and analysis population progress
  - Implement graceful degradation when some endpoints fail (e.g., show H2H data even if matches data unavailable)
  - Test integration with existing MLB functionality to ensure no conflicts during simultaneous sport channel creation
  - _Requirements: 1.1, 1.2, 1.4, 1.5, 1.6, 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 6. Implement soccer-specific slash commands





  - Create `/soccer-schedule` command to display upcoming matches for current day
  - Implement `/soccer-odds [team1] [team2]` command for specific matchup betting lines
  - Add `/soccer-h2h [team1] [team2]` command for comprehensive head-to-head analysis
  - Create `/soccer-standings [league]` command for current league table display
  - Implement proper parameter validation and error handling for all commands
  - Add command usage examples and help text for user guidance
  - Write integration tests for all new slash commands
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [-] 7. Integrate dual-endpoint analysis system using BOTH H2H endpoint AND matches endpoint






  - Implement `get_h2h_direct_analysis()` method in `SoccerMCPClient` to fetch direct head-to-head record using H2H endpoint
  - Create `get_team_recent_matches()` method to fetch recent 10 matches for individual teams using matches endpoint
  - Add `get_comprehensive_match_analysis()` method that combines H2H endpoint data with matches endpoint data for both teams
  - Implement `analyze_team_comprehensive_data()` method in `SoccerDataProcessor` for detailed individual team statistics from matches data
  - Create `process_h2h_historical_record()` method to handle H2H endpoint response and extract direct head-to-head statistics
  - Add `generate_combined_betting_recommendations()` method using both H2H patterns and individual team form for enhanced insights
  - Implement comprehensive error handling for partial data scenarios (H2H available but matches missing, or vice versa)
  - Write unit tests for dual-endpoint data processing and combined analysis calculations
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 8. Add multi-league support and league-specific handling





  - Implement league filtering in MCP calls for EPL, La Liga, MLS, Bundesliga, Serie A, UEFA
  - Add league identification and context in channel creation and embeds
  - Create league priority ordering for channel organization when multiple leagues have matches
  - Implement tournament stage handling for UEFA Champions League (group stage, knockout)
  - Add league-specific data enrichment (standings position, points, goal difference)
  - Create league-specific embed colors and branding elements
  - Write integration tests for multi-league match retrieval and processing
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 9. Implement robust error handling and logging system





  - Add comprehensive exception handling for MCP server connection failures
  - Implement retry logic with exponential backoff for failed MCP requests
  - Create graceful degradation for partial data availability (missing odds, incomplete H2H)
  - Add Discord API error handling for rate limits and permission issues
  - Implement detailed logging for debugging and monitoring channel creation and data processing
  - Create user-friendly error messages with actionable guidance
  - Write error scenario tests for network failures, invalid data, and API limits
  - _Requirements: 1.5, 4.5, 5.5_

- [x] 10. Add automated channel cleanup and maintenance system





  - Implement scheduled cleanup task for channels older than 3 days
  - Add logic to preserve channels with recent activity or pinned messages
  - Create cleanup logging and administrator notification system
  - Implement channel limit management with priority-based retention
  - Add manual cleanup command for administrators with configurable retention period
  - Create cleanup statistics and reporting for server management
  - Write integration tests for cleanup logic and edge cases
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 11. Create comprehensive configuration and environment setup





  - Add soccer-specific configuration to existing bot configuration system
  - Implement environment variable validation for Soccer MCP URL and AUTH_KEY
  - Create league configuration with IDs, names, and display preferences
  - Add rate limiting configuration for MCP server requests
  - Implement feature flags for enabling/disabling soccer functionality
  - Create configuration validation and startup checks
  - Write configuration tests and documentation for deployment
  - _Requirements: 1.3, 6.1_

- [x] 12. Write comprehensive test suite and documentation



  - Create unit tests for all soccer integration classes and methods
  - Implement integration tests for end-to-end channel creation workflow
  - Add performance tests for bulk channel creation and MCP server communication
  - Create mock MCP server responses for reliable testing
  - Write user documentation for all new slash commands and features
  - Create administrator guide for configuration and troubleshooting
  - Add code documentation and inline comments for maintainability
  - _Requirements: All requirements - comprehensive testing coverage_

- [ ] 13. Port schedule.py dual-endpoint methodology to Discord bot automatic population
  - Create `get_h2h_direct_analysis()` method in SoccerMCPClient that calls H2H endpoint (replicating schedule.py's `get_h2h_analysis()`)
  - Implement `get_team_recent_matches()` method that calls matches endpoint for individual team analysis (replicating schedule.py's `get_comprehensive_team_matches()`)
  - Port `analyze_team_comprehensive_data()` function from schedule.py to SoccerDataProcessor for processing recent 10 matches with full event data
  - Create `generate_combined_betting_recommendations()` method that merges H2H patterns with team form analysis (replicating schedule.py's enhanced betting insights)
  - Implement `create_comprehensive_analysis_embeds()` in SoccerEmbedBuilder that converts schedule.py's text output to Discord embeds
  - Add automatic population workflow in SoccerChannelManager that makes 3 MCP calls per channel and posts 4-5 embeds
  - Create error handling for partial data scenarios (H2H available but matches missing, or vice versa) with graceful degradation
  - Write integration tests that compare Discord bot embed content with schedule.py console output for consistency validation
  - _Requirements: 1.5, 1.6, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 14. Validate Discord bot output against schedule.py baseline for consistency
  - Create test script that runs same match analysis through both schedule.py and Discord bot integration
  - Compare H2H analysis output between schedule.py console output and Discord H2H embed content
  - Validate team analysis consistency between schedule.py team breakdowns and Discord team analysis embeds
  - Verify betting recommendations match between schedule.py insights and Discord betting insights embed
  - Test edge cases: matches with no H2H data, teams with limited recent matches, partial MCP server responses
  - Create automated comparison tests that flag discrepancies between schedule.py and Discord bot analysis
  - Document any intentional differences (e.g., Discord character limits, embed formatting constraints)
  - Ensure Discord bot provides same analytical value as working schedule.py script
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 15. Integration testing and deployment preparation
  - Test soccer integration with existing MLB functionality to ensure no conflicts during simultaneous sport operations
  - Perform load testing with multiple simultaneous soccer channel creation requests (10+ matches with 3 MCP calls each)
  - Validate Discord API rate limit compliance during bulk channel creation with automatic analysis population
  - Test error recovery scenarios with MCP server downtime, partial endpoint failures, and network issues
  - Validate graceful degradation when H2H endpoint fails but matches endpoint works (and vice versa)
  - Create deployment checklist including MCP server health checks and Discord bot permission validation
  - Perform user acceptance testing comparing Discord bot analysis with schedule.py output for same matches
  - Prepare rollback procedures and monitoring for production deployment with dual-endpoint functionality
  - _Requirements: All requirements - production readiness validation with schedule.py consistency_