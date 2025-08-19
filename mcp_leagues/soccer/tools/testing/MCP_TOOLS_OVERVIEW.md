# MCP Soccer Betting Tools Overview

Your MCP server provides 5 professional betting analysis tools for soccer matches.

## Server Details
- **Endpoint:** `https://soccermcp-production.up.railway.app/mcp`
- **Status:** Operational
- **Supported Leagues:** EPL (Premier League), La Liga, MLS

## Tool 1: get_h2h_betting_analysis
**Purpose:** Historical head-to-head analysis between two teams

**What it does:**
- Analyzes historical matchups between any two teams
- Provides win/loss records and percentages
- Shows average goals per game
- Identifies high-scoring vs low-scoring fixture patterns
- Gives betting insights for over/under markets

**Status:** Working with real data
**Best for:** Pre-match analysis, understanding team matchup patterns

## Tool 2: get_team_form_analysis
**Purpose:** Analyze individual team's recent performance and form

**What it does:**
- Calculates team form rating (0-10 scale)
- Tracks recent results and momentum
- Analyzes goal-scoring and defensive patterns
- Provides betting trends (over 2.5 goals, both teams score, etc.)
- Shows home vs away performance splits

**Status:** Working with available match data
**Best for:** Assessing team strength before placing bets

## Tool 3: get_betting_matches
**Purpose:** Find available matches for betting analysis

**What it does:**
- Searches for matches by date and league
- Supports multiple date formats
- Filters by specific leagues (EPL, La Liga, MLS)
- Returns match details including teams, time, status
- Provides match IDs for deeper analysis

**Status:** Working, currently shows fixture structure
**Best for:** Finding matches to analyze for betting opportunities

## Tool 4: analyze_match_betting
**Purpose:** Comprehensive betting analysis for specific matches

**What it does:**
- Combines team form analysis for both teams
- Includes head-to-head historical data
- Generates match winner predictions with confidence scores
- Predicts goals (over/under 2.5)
- Provides key betting insights and recommendations
- Assigns risk levels and confidence ratings

**Status:** Code complete, needs real fixture data
**Best for:** Complete pre-match betting intelligence

## Tool 5: get_league_value_bets
**Purpose:** Scan entire leagues for the best betting opportunities

**What it does:**
- Analyzes all matches in a league for a specific date
- Identifies high-confidence betting opportunities
- Filters by minimum confidence threshold
- Ranks opportunities by strength
- Provides summary statistics across all matches
- Acts as an automated betting scout

**Status:** Code complete, needs real fixture data
**Best for:** Finding the best betting opportunities across multiple matches

## Current Data Status

**Working Now:**
- Historical head-to-head data (complete records)
- Team information and basic stats
- Match structure and scheduling

**Coming Soon:**
- Real fixture data for current season (2025-2026)
- Complete team form analysis with recent matches
- Full betting predictions and value bet identification

The tools are professionally built and ready to provide comprehensive betting analysis once real fixture data becomes available.