Daily Betting Intelligence Report - Technical Specification
Objective
Transform existing MCP-based sports data platform into an automated daily betting analysis system that generates comprehensive reports for all games happening on a given date.
Current Architecture (Proven & Working)

ESPN MCP Server: Game schedules, player stats, historical performance data
Wagyu MCP Server: Team betting odds + player prop lines from multiple sportsbooks
OpenRouter LLM Integration: Fact-based analysis using provided JSON data
Proven Data Retrieval: Can successfully fetch both team-level and player-level betting data

Target Output: Structured Daily Report
For Each Game on Target Date:

Game Metadata

Teams, kickoff/tip-off time, venue, league
Current game status (pre-game, live, final)


Team Betting Lines

Moneyline odds from multiple sportsbooks
Point spreads with odds
Over/under totals with odds
Best available odds identification


LLM-Identified Key Players

2-3 most impactful players per game
Justification based on recent performance data and matchup analysis
Player prop betting lines (points, rebounds, assists, etc.)


Data-Driven Predictions

Team outcome predictions with reasoning
Player performance predictions with reasoning
Betting value identification and recommendations



Technical Requirements
Input Parameters

Target date (e.g., "2025-08-09")
Sports leagues to include (MLB, WNBA, NBA, NFL, MLS, etc.)
Betting markets to analyze (moneyline, spreads, totals, player props)

Data Sources (Existing)

ESPN API via MCP for game/player data
The Odds API via Wagyu MCP for betting lines
OpenRouter LLM for analysis and predictions

Output Format

Structured markdown report
Organized by sport and game
Include confidence levels and reasoning for all predictions
Export capability (console output, file save, etc.)

Implementation Scope
Phase 1: Single Sport Prototype

Implement for one sport (e.g., WNBA) on target date
Validate data retrieval → analysis → report generation pipeline
Ensure all MCP integrations work correctly

Phase 2: Multi-Sport Expansion

Extend to all available sports leagues
Handle varying data structures across sports
Optimize for performance with multiple concurrent API calls

Phase 3: Automation & Scheduling

Daily automated report generation
Historical tracking and accuracy measurement
Enhanced LLM prompting for better predictions

Success Criteria

Generate complete report for all games on specified date
Include both team-level and player-level betting analysis
Provide actionable betting recommendations with clear reasoning
Maintain data accuracy and proper timezone handling
Process efficiently without API rate limit issues

Key Constraint
Must leverage existing MCP architecture without requiring new data sources or major architectural changes.