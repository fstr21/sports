"""
Unit tests for the report formatter module.

Tests the ReportFormatter class functionality including markdown generation,
data formatting, and template rendering for daily betting intelligence reports.
"""

import pytest
from datetime import datetime, timezone
import pytz
from unittest.mock import Mock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from daily_betting_intelligence.report_formatter import ReportFormatter
from daily_betting_intelligence.models import (
    ReportData, GameData, BettingOdds, PlayerProp, 
    GameAnalysis, PlayerAnalysis
)


class TestReportFormatter:
    """Test suite for ReportFormatter class."""
    
    @pytest.fixture
    def formatter(self):
        """Create a ReportFormatter instance for testing."""
        return ReportFormatter(timezone="US/Eastern")
    
    @pytest.fixture
    def sample_game_data(self):
        """Create sample game data for testing."""
        return GameData(
            event_id="test_game_1",
            league="nba",
            home_team="Lakers",
            away_team="Warriors",
            game_time=datetime(2025, 8, 9, 20, 0, tzinfo=pytz.UTC),
            venue="Crypto.com Arena",
            status="pre-game",
            weather="Clear, 75°F",
            additional_metadata={"tv_network": "ESPN", "referee": "Tony Brothers"}
        )
    
    @pytest.fixture
    def sample_betting_odds(self):
        """Create sample betting odds for testing."""
        return [
            BettingOdds(
                event_id="test_game_1",
                sportsbook="DraftKings",
                moneyline_home=-150,
                moneyline_away=+130,
                spread_line=-3.5,
                spread_home_odds=-110,
                spread_away_odds=-110,
                total_line=225.5,
                total_over_odds=-105,
                total_under_odds=-115,
                last_updated=datetime.now(timezone.utc)
            ),
            BettingOdds(
                event_id="test_game_1",
                sportsbook="FanDuel",
                moneyline_home=-145,
                moneyline_away=+125,
                spread_line=-3.5,
                spread_home_odds=-108,
                spread_away_odds=-112,
                total_line=225.5,
                total_over_odds=-110,
                total_under_odds=-110
            )
        ]
    
    @pytest.fixture
    def sample_player_props(self):
        """Create sample player props for testing."""
        return [
            PlayerProp(
                player_name="LeBron James",
                prop_type="points",
                line=25.5,
                over_odds=-110,
                under_odds=-110,
                sportsbook="DraftKings",
                event_id="test_game_1",
                player_position="F",
                season_average=26.2
            ),
            PlayerProp(
                player_name="LeBron James",
                prop_type="rebounds",
                line=7.5,
                over_odds=-105,
                under_odds=-115,
                sportsbook="DraftKings",
                event_id="test_game_1"
            ),
            PlayerProp(
                player_name="Stephen Curry",
                prop_type="points",
                line=28.5,
                over_odds=-115,
                under_odds=-105,
                sportsbook="FanDuel",
                event_id="test_game_1"
            )
        ]
    
    @pytest.fixture
    def sample_game_analysis(self):
        """Create sample game analysis for testing."""
        return GameAnalysis(
            event_id="test_game_1",
            predicted_winner="Lakers",
            confidence_score=0.75,
            key_factors=[
                "Lakers have home court advantage",
                "Warriors missing key player due to injury",
                "Lakers won last 3 meetings"
            ],
            value_bets=[
                {
                    "bet_type": "moneyline",
                    "description": "Lakers moneyline at -150",
                    "confidence": 0.8,
                    "reasoning": "Strong home record"
                }
            ],
            risk_level="medium",
            reasoning="Lakers have been strong at home this season and Warriors are dealing with injuries."
        )
    
    @pytest.fixture
    def sample_player_analysis(self):
        """Create sample player analysis for testing."""
        return [
            PlayerAnalysis(
                player_name="LeBron James",
                projected_stats={"points": 26.5, "rebounds": 8.2, "assists": 7.1},
                confidence_score=0.85,
                prop_recommendations=[
                    {
                        "prop_type": "points",
                        "recommendation": "Over 25.5",
                        "reasoning": "Averaging 28 points in last 5 games"
                    }
                ],
                reasoning="LeBron has been in excellent form recently and matches up well against Warriors defense.",
                event_id="test_game_1"
            )
        ]
    
    @pytest.fixture
    def sample_report_data(self, sample_game_data, sample_betting_odds, 
                          sample_player_props, sample_game_analysis, sample_player_analysis):
        """Create complete sample report data for testing."""
        return ReportData(
            target_date="20250809",
            leagues_analyzed=["nba"],
            total_games=1,
            games_data=[sample_game_data],
            betting_odds={"test_game_1": sample_betting_odds},
            player_props={"test_game_1": sample_player_props},
            game_analyses={"test_game_1": sample_game_analysis},
            player_analyses={"test_game_1": sample_player_analysis},
            generation_timestamp=datetime(2025, 8, 9, 15, 30, tzinfo=pytz.UTC),
            errors=["Sample error for testing"],
            warnings=["Sample warning for testing"]
        )

    def test_format_daily_report_structure(self, formatter, sample_report_data):
        """Test that daily report has correct overall structure."""
        report = formatter.format_daily_report(sample_report_data)
        
        # Check main sections are present
        assert "# Daily Betting Intelligence Report - August 09, 2025" in report
        assert "## Executive Summary" in report
        assert "## NBA Analysis" in report
        assert "### Warriors @ Lakers" in report
        assert "#### Game Overview" in report
        assert "#### Betting Lines" in report
        assert "#### Player Props" in report
        assert "#### Analysis & Predictions" in report
        assert "#### Key Players Analysis" in report
        assert "---" in report  # Footer separator
    
    def test_format_header(self, formatter, sample_report_data):
        """Test header formatting with correct date."""
        header = formatter._format_header(sample_report_data)
        assert header == "# Daily Betting Intelligence Report - August 09, 2025"
    
    def test_format_executive_summary(self, formatter, sample_report_data):
        """Test executive summary formatting with all key metrics."""
        summary = formatter._format_executive_summary(sample_report_data)
        
        assert "## Executive Summary" in summary
        assert "**Total games analyzed:** 1" in summary
        assert "**Leagues covered:** nba" in summary
        assert "**Report generated:** August 09, 2025 at 11:30 AM EDT" in summary  # EDT during summer
        assert "**High-confidence recommendations:** 1" in summary  # LeBron analysis has 0.85 confidence
        assert "**Errors encountered:** 1" in summary
        assert "**Warnings:** 1" in summary
    
    def test_format_league_section(self, formatter, sample_report_data):
        """Test league section formatting."""
        games = sample_report_data.games_data
        league_section = formatter._format_league_section("nba", games, sample_report_data)
        
        assert "## NBA Analysis" in league_section
        assert "### Warriors @ Lakers" in league_section
    
    def test_format_league_section_empty(self, formatter, sample_report_data):
        """Test league section with no games."""
        league_section = formatter._format_league_section("nfl", [], sample_report_data)
        
        assert "## NFL Analysis" in league_section
        assert "No games scheduled for this league." in league_section
    
    def test_format_game_overview(self, formatter, sample_game_data):
        """Test game overview formatting with metadata."""
        overview = formatter._format_game_overview(sample_game_data)
        
        assert "#### Game Overview" in overview
        assert "**Venue:** Crypto.com Arena" in overview
        assert "**Status:** Pre-Game" in overview
        assert "**Weather:** Clear, 75°F" in overview
        assert "**Tv Network:** ESPN" in overview
        assert "**Referee:** Tony Brothers" in overview
    
    def test_format_game_overview_with_scores(self, formatter, sample_game_data):
        """Test game overview with live/final scores."""
        sample_game_data.status = "final"
        sample_game_data.home_score = 112
        sample_game_data.away_score = 108
        
        overview = formatter._format_game_overview(sample_game_data)
        
        assert "**Score:** Warriors 108 - 112 Lakers" in overview
    
    def test_format_betting_lines(self, formatter, sample_betting_odds):
        """Test betting lines formatting with best odds identification."""
        betting_section = formatter._format_betting_lines(sample_betting_odds)
        
        assert "#### Betting Lines" in betting_section
        assert "**Moneyline:**" in betting_section
        assert "Home: -145 (FanDuel)" in betting_section  # FanDuel has better home odds
        assert "Away: +130 (DraftKings)" in betting_section  # DraftKings has better away odds
        assert "**Point Spread:**" in betting_section
        assert "**Total (Over/Under):**" in betting_section
    
    def test_format_betting_lines_empty(self, formatter):
        """Test betting lines with no odds available."""
        betting_section = formatter._format_betting_lines([])
        
        assert "#### Betting Lines" in betting_section
        assert "No betting lines available." in betting_section
    
    def test_format_player_props(self, formatter, sample_player_props):
        """Test player props formatting grouped by player."""
        props_section = formatter._format_player_props(sample_player_props)
        
        assert "#### Player Props" in props_section
        assert "**LeBron James:**" in props_section
        assert "Points: O/U 25.5 (-110/-110) - DraftKings" in props_section
        assert "Rebounds: O/U 7.5 (-105/-115) - DraftKings" in props_section
        assert "**Stephen Curry:**" in props_section
        assert "Points: O/U 28.5 (-115/-105) - FanDuel" in props_section
    
    def test_format_player_props_empty(self, formatter):
        """Test player props with no props available."""
        props_section = formatter._format_player_props([])
        
        assert "#### Player Props" in props_section
        assert "No player props available." in props_section
    
    def test_format_game_analysis(self, formatter, sample_game_analysis):
        """Test game analysis formatting with predictions and recommendations."""
        analysis_section = formatter._format_game_analysis(sample_game_analysis)
        
        assert "#### Analysis & Predictions" in analysis_section
        assert "**Predicted Winner:** Lakers" in analysis_section
        assert "**Confidence:** 75.0%" in analysis_section
        assert "**Risk Level:** Medium" in analysis_section
        assert "**Key Factors:**" in analysis_section
        assert "Lakers have home court advantage" in analysis_section
        assert "**Value Opportunities:**" in analysis_section
        assert "moneyline: Lakers moneyline at -150 (Confidence: 80.0%)" in analysis_section
        assert "**Analysis:** Lakers have been strong at home" in analysis_section
    
    def test_format_player_analyses(self, formatter, sample_player_analysis):
        """Test player analyses formatting with recommendations."""
        player_section = formatter._format_player_analyses(sample_player_analysis)
        
        assert "#### Key Players Analysis" in player_section
        assert "**LeBron James** (Confidence: 85.0%)" in player_section
        assert "Projected: 26.5 points, 8.2 rebounds, 7.1 assists" in player_section
        assert "Recommendations:" in player_section
        assert "points: Over 25.5 (Averaging 28 points in last 5 games)" in player_section
        assert "Analysis: LeBron has been in excellent form recently" in player_section
    
    def test_format_player_analyses_empty(self, formatter):
        """Test player analyses with no analyses available."""
        player_section = formatter._format_player_analyses([])
        
        assert player_section == ""
    
    def test_format_footer(self, formatter, sample_report_data):
        """Test footer formatting with generation info and errors."""
        footer = formatter._format_footer(sample_report_data)
        
        assert "---" in footer
        assert "*Report generated at August 09, 2025 at 11:30 AM EDT*" in footer  # EDT during summer
        assert "### Issues Encountered" in footer
        assert "**Errors:**" in footer
        assert "Sample error for testing" in footer
        assert "**Warnings:**" in footer
        assert "Sample warning for testing" in footer
    
    def test_format_footer_no_issues(self, formatter, sample_report_data):
        """Test footer with no errors or warnings."""
        sample_report_data.errors = []
        sample_report_data.warnings = []
        
        footer = formatter._format_footer(sample_report_data)
        
        assert "---" in footer
        assert "*Report generated at August 09, 2025 at 11:30 AM EDT*" in footer  # EDT during summer
        assert "### Issues Encountered" not in footer
    
    def test_group_games_by_league(self, formatter, sample_report_data):
        """Test games grouping by league."""
        # Add another game from different league
        nfl_game = GameData(
            event_id="nfl_game_1",
            league="nfl",
            home_team="Chiefs",
            away_team="Bills",
            game_time=datetime.now(pytz.UTC),
            venue="Arrowhead Stadium",
            status="pre-game"
        )
        
        all_games = sample_report_data.games_data + [nfl_game]
        grouped = formatter._group_games_by_league(all_games)
        
        assert "nba" in grouped
        assert "nfl" in grouped
        assert len(grouped["nba"]) == 1
        assert len(grouped["nfl"]) == 1
        assert grouped["nba"][0].league == "nba"
        assert grouped["nfl"][0].league == "nfl"
    
    def test_format_league_name(self, formatter):
        """Test league name formatting."""
        assert formatter._format_league_name("nba") == "NBA"
        assert formatter._format_league_name("nfl") == "NFL"
        assert formatter._format_league_name("epl") == "English Premier League"
        assert formatter._format_league_name("laliga") == "La Liga"
        assert formatter._format_league_name("unknown") == "UNKNOWN"
    
    def test_format_game_time(self, formatter):
        """Test game time formatting in Eastern timezone."""
        utc_time = datetime(2025, 8, 9, 20, 0, tzinfo=pytz.UTC)
        formatted_time = formatter._format_game_time(utc_time)
        
        assert formatted_time == "04:00 PM EDT"  # EDT during summer
    
    def test_format_game_time_no_timezone(self, formatter):
        """Test game time formatting with naive datetime (assumes UTC)."""
        naive_time = datetime(2025, 8, 9, 20, 0)
        formatted_time = formatter._format_game_time(naive_time)
        
        assert formatted_time == "04:00 PM EDT"  # EDT during summer
    
    def test_format_timestamp(self, formatter):
        """Test timestamp formatting."""
        utc_timestamp = datetime(2025, 8, 9, 15, 30, tzinfo=pytz.UTC)
        formatted_timestamp = formatter._format_timestamp(utc_timestamp)
        
        assert formatted_timestamp == "August 09, 2025 at 11:30 AM EDT"  # EDT during summer
    
    def test_format_odds(self, formatter):
        """Test odds formatting."""
        assert formatter._format_odds(150) == "+150"
        assert formatter._format_odds(-150) == "-150"
        assert formatter._format_odds(None) == "N/A"
    
    def test_format_spread(self, formatter):
        """Test spread formatting."""
        assert formatter._format_spread(3.5) == "+3.5"
        assert formatter._format_spread(-3.5) == "-3.5"
        assert formatter._format_spread(0) == "0"
    
    def test_find_best_odds(self, formatter, sample_betting_odds):
        """Test best odds identification across sportsbooks."""
        best_odds = formatter._find_best_odds(sample_betting_odds)
        
        # Check moneyline - FanDuel has better home odds (-145 vs -150)
        assert best_odds["moneyline"]["home_odds"] == -145
        assert best_odds["moneyline"]["home_book"] == "FanDuel"
        # DraftKings has better away odds (+130 vs +125)
        assert best_odds["moneyline"]["away_odds"] == +130
        assert best_odds["moneyline"]["away_book"] == "DraftKings"
        
        # Check that spread and total are present
        assert "spread" in best_odds
        assert "total" in best_odds
    
    def test_count_high_confidence_recommendations(self, formatter, sample_report_data):
        """Test counting high-confidence recommendations."""
        count = formatter._count_high_confidence_recommendations(sample_report_data)
        
        # Game analysis has 0.75 confidence (below 0.8 threshold)
        # Player analysis has 0.85 confidence (above 0.8 threshold)
        assert count == 1
    
    def test_count_high_confidence_recommendations_multiple(self, formatter, sample_report_data):
        """Test counting with multiple high-confidence recommendations."""
        # Add high-confidence game analysis
        sample_report_data.game_analyses["test_game_1"].confidence_score = 0.9
        
        count = formatter._count_high_confidence_recommendations(sample_report_data)
        
        # Now both game and player analysis are high confidence
        assert count == 2
    
    def test_timezone_configuration(self):
        """Test formatter with different timezone configuration."""
        pacific_formatter = ReportFormatter(timezone="US/Pacific")
        
        utc_time = datetime(2025, 8, 9, 20, 0, tzinfo=pytz.UTC)
        formatted_time = pacific_formatter._format_game_time(utc_time)
        
        assert "PT" in formatted_time or "PDT" in formatted_time or "PST" in formatted_time
    
    def test_complete_report_integration(self, formatter, sample_report_data):
        """Test complete report generation integration."""
        report = formatter.format_daily_report(sample_report_data)
        
        # Verify report is a complete string
        assert isinstance(report, str)
        assert len(report) > 1000  # Should be substantial content
        
        # Verify all major sections are present and in order
        header_pos = report.find("# Daily Betting Intelligence Report")
        summary_pos = report.find("## Executive Summary")
        nba_pos = report.find("## NBA Analysis")
        footer_pos = report.find("---")
        
        assert header_pos < summary_pos < nba_pos < footer_pos
        
        # Verify no template placeholders remain
        assert "[DATE]" not in report
        assert "[SPORT]" not in report
        assert "[Team A]" not in report
        assert "[Team B]" not in report