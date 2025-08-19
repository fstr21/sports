#!/usr/bin/env python3
"""
Comprehensive Unit Tests for SoccerEmbedBuilder
Tests dual-endpoint Discord embed builders matching schedule.py output format
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os

# Add the discord directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock discord module for testing
class MockEmbed:
    def __init__(self, title=None, description=None, color=None, timestamp=None):
        self.title = title
        self.description = description
        self.color = color
        self.timestamp = timestamp
        self.fields = []
        self.footer = Mock()
        self.footer.text = ""
    
    def add_field(self, name, value, inline=False):
        field = Mock()
        field.name = name
        field.value = value
        field.inline = inline
        self.fields.append(field)
        return self
    
    def set_footer(self, text):
        self.footer.text = text
        return self

class MockDiscord:
    Embed = MockEmbed

# Mock the discord module
sys.modules['discord'] = MockDiscord()

from soccer_embed_builder import (
    SoccerEmbedBuilder, Team, League, BettingOdds, OddsFormat, OverUnder,
    H2HHistoricalRecord, TeamAnalysis, ComprehensiveInsights, ProcessedMatch,
    H2HSummary
)

class TestSoccerEmbedBuilderComprehensive(unittest.TestCase):
    """Comprehensive test cases for SoccerEmbedBuilder dual-endpoint functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.embed_builder = SoccerEmbedBuilder()
        
        # Create test teams
        self.home_team = Team(
            id=1,
            name="Manchester United",
            short_name="MAN UTD",
            country="England"
        )
        
        self.away_team = Team(
            id=2,
            name="Liverpool FC",
            short_name="LIV",
            country="England"
        )
        
        # Create test league
        self.league = League(
            id=228,
            name="Premier League",
            country="England",
            season="2024-25"
        )
        
        # Create test betting odds
        self.betting_odds = BettingOdds(
            home_win=OddsFormat.from_decimal(2.50),
            draw=OddsFormat.from_decimal(3.20),
            away_win=OddsFormat.from_decimal(2.80),
            over_under=OverUnder(
                line=2.5,
                over_odds=OddsFormat.from_decimal(1.85),
                under_odds=OddsFormat.from_decimal(1.95)
            ),
            both_teams_score=OddsFormat.from_decimal(1.70)
        )
        
        # Create test H2H historical record (from H2H endpoint)
        self.h2h_record = H2HHistoricalRecord(
            total_meetings=25,
            home_team_wins=10,
            away_team_wins=8,
            draws=7,
            home_team_goals_total=32,
            away_team_goals_total=28,
            avg_goals_per_game=2.4,
            last_meeting_date="15-03-2024",
            last_meeting_result="Manchester United 2-1 Liverpool FC"
        )
        
        # Create test team analyses (from matches endpoint)
        self.home_team_analysis = TeamAnalysis(
            team_name="Manchester United",
            recent_matches_count=10,
            form_record={"wins": 6, "draws": 2, "losses": 2},
            form_string="W-W-D-L-W-W-D-W-L-W",
            goals_per_game=2.1,
            goals_against_per_game=1.3,
            clean_sheet_percentage=40.0,
            btts_percentage=60.0,
            high_scoring_percentage=50.0,
            card_discipline={"yellow_per_game": 2.3, "red_total": 1},
            advanced_metrics={
                "early_goals_frequency": 0.4,
                "late_goals_frequency": 0.3,
                "comeback_wins": 2,
                "home_win_rate": 70.0,
                "away_win_rate": 50.0
            }
        )
        
        self.away_team_analysis = TeamAnalysis(
            team_name="Liverpool FC",
            recent_matches_count=10,
            form_record={"wins": 7, "draws": 1, "losses": 2},
            form_string="W-W-W-D-L-W-W-W-L-W",
            goals_per_game=2.3,
            goals_against_per_game=1.1,
            clean_sheet_percentage=50.0,
            btts_percentage=70.0,
            high_scoring_percentage=60.0,
            card_discipline={"yellow_per_game": 1.9, "red_total": 0},
            advanced_metrics={
                "early_goals_frequency": 0.5,
                "late_goals_frequency": 0.4,
                "comeback_wins": 1,
                "home_win_rate": 80.0,
                "away_win_rate": 60.0
            }
        )
        
        # Create comprehensive insights (combining H2H + team form)
        self.comprehensive_insights = ComprehensiveInsights(
            h2h_dominance="balanced",
            h2h_goals_trend="high_scoring",
            form_momentum="away_advantage",
            expected_goals_total=3.2,
            btts_probability=75.0,
            over_under_recommendation="Over 2.5",
            btts_recommendation="BTTS Yes",
            match_outcome_lean="Away Win",
            cards_market_insight="Average",
            recommendation_reasoning=[
                "Liverpool in excellent form with 70% win rate",
                "Both teams average 2+ goals per game recently",
                "H2H meetings typically high-scoring (2.4 avg)",
                "Both teams have strong attacking records"
            ],
            confidence_level="High"
        )
        
        # Create processed match with all dual-endpoint data
        self.processed_match = ProcessedMatch(
            match_id=12345,
            home_team=self.home_team,
            away_team=self.away_team,
            league=self.league,
            date="2025-08-19",
            time="15:00",
            venue="Old Trafford",
            status="scheduled",
            odds=self.betting_odds,
            h2h_summary=H2HSummary(
                total_meetings=25,
                home_team_wins=10,
                away_team_wins=8,
                draws=7,
                last_meeting_result="Manchester United 2-1 Liverpool FC"
            ),
            h2h_historical_record=self.h2h_record,
            home_team_analysis=self.home_team_analysis,
            away_team_analysis=self.away_team_analysis,
            comprehensive_insights=self.comprehensive_insights
        )
    
    def test_create_match_preview_embed(self):
        """Test match preview embed creation with basic match info"""
        embed = self.embed_builder.create_match_preview_embed(self.processed_match)
        
        # Basic structure tests
        self.assertIsInstance(embed, MockEmbed)
        self.assertIn("Liverpool FC vs Manchester United", embed.title)
        self.assertEqual(embed.color, 0x3d195b)  # Premier League purple
        
        # Field content tests
        field_names = [field.name for field in embed.fields]
        self.assertIn("🏆 Competition", field_names)
        self.assertIn("📅 Date", field_names)
        self.assertIn("⏰ Time", field_names)
        self.assertIn("🏟️ Venue", field_names)
        self.assertIn("💰 Betting Odds", field_names)
        self.assertIn("📊 Head-to-Head", field_names)
        
        # Content validation
        venue_field = next(field for field in embed.fields if field.name == "🏟️ Venue")
        self.assertEqual(venue_field.value, "Old Trafford")
        
        # Odds format validation (should include both decimal and American)
        odds_field = next(field for field in embed.fields if field.name == "💰 Betting Odds")
        self.assertIn("2.50", odds_field.value)  # Decimal odds
        self.assertIn("(+150)", odds_field.value)  # American odds
    
    def test_create_h2h_historical_record_embed(self):
        """Test H2H historical record embed displaying H2H endpoint data"""
        embed = self.embed_builder.create_h2h_historical_record_embed(
            self.h2h_record, self.home_team, self.away_team, self.league
        )
        
        # Basic structure tests
        self.assertIsInstance(embed, MockEmbed)
        self.assertIn("Historical H2H Record", embed.title)
        self.assertIn("Liverpool FC", embed.description)
        self.assertIn("Manchester United", embed.description)
        
        # Field content tests
        field_names = [field.name for field in embed.fields]
        self.assertIn("📈 Overall Record", field_names)
        self.assertIn("🎯 Goals Analysis", field_names)
        self.assertIn("📊 Historical Trend", field_names)
        # Note: Betting insights are only added if certain thresholds are met
        
        # Content validation - should match schedule.py H2H format
        overall_record_field = next(field for field in embed.fields if field.name == "📈 Overall Record")
        self.assertIn("25", overall_record_field.value)  # Total meetings
        self.assertIn("40.0%", overall_record_field.value)  # Home win percentage
        self.assertIn("32.0%", overall_record_field.value)  # Away win percentage
        
        # Goals analysis validation
        goals_field = next(field for field in embed.fields if field.name == "🎯 Goals Analysis")
        self.assertIn("2.40", goals_field.value)  # Average goals per game
        self.assertIn("1.3 per game", goals_field.value)  # Goals per game calculation
    
    def test_create_team_analysis_embed_home(self):
        """Test team analysis embed for home team (matches endpoint data)"""
        embed = self.embed_builder.create_team_analysis_embed(
            self.home_team_analysis, self.home_team, self.league, is_home=True
        )
        
        # Basic structure tests
        self.assertIsInstance(embed, MockEmbed)
        self.assertIn("🏠 Manchester United Analysis", embed.title)
        self.assertIn("Recent 10 matches analysis", embed.description)
        
        # Field content tests - should match schedule.py team analysis format
        field_names = [field.name for field in embed.fields]
        self.assertIn("📋 Basic Form Summary", field_names)
        self.assertIn("📊 Advanced Metrics", field_names)
        self.assertIn("🃏 Card Discipline", field_names)
        self.assertIn("🎲 Team Betting Insights", field_names)
        
        # Content validation - schedule.py style metrics
        form_field = next(field for field in embed.fields if field.name == "📋 Basic Form Summary")
        self.assertIn("6W-2D-2L", form_field.value)  # Record format
        self.assertIn("60.0% win rate", form_field.value)  # Win percentage
        self.assertIn("2.1 for, 1.3 against", form_field.value)  # Goals per game
        
        # Advanced metrics validation
        advanced_field = next(field for field in embed.fields if field.name == "📊 Advanced Metrics")
        self.assertIn("40.0%", advanced_field.value)  # Clean sheet percentage
        self.assertIn("60.0%", advanced_field.value)  # BTTS percentage
        
        # Betting insights validation - should match schedule.py recommendations
        betting_field = next(field for field in embed.fields if field.name == "🎲 Team Betting Insights")
        self.assertIn("Strong Attack", betting_field.value)  # Goals > 2.0
        self.assertIn("BTTS Yes", betting_field.value)  # BTTS > 60%
    
    def test_create_team_analysis_embed_away(self):
        """Test team analysis embed for away team (matches endpoint data)"""
        embed = self.embed_builder.create_team_analysis_embed(
            self.away_team_analysis, self.away_team, self.league, is_home=False
        )
        
        # Basic structure tests
        self.assertIsInstance(embed, MockEmbed)
        self.assertIn("✈️ Liverpool FC Analysis", embed.title)
        
        # Content validation - away team specific
        form_field = next(field for field in embed.fields if field.name == "📋 Basic Form Summary")
        self.assertIn("7W-1D-2L", form_field.value)  # Away team record
        self.assertIn("70.0% win rate", form_field.value)  # Away team win percentage
        
        # Performance assessment
        performance_field = next(field for field in embed.fields if field.name == "📈 Current Form Assessment")
        self.assertIn("Excellent form", performance_field.value)  # Win rate >= 60%
    
    def test_create_comprehensive_betting_insights_embed(self):
        """Test comprehensive betting insights embed combining H2H + team form"""
        embed = self.embed_builder.create_comprehensive_betting_insights_embed(
            self.comprehensive_insights, self.home_team, self.away_team, self.league,
            h2h_record=self.h2h_record, home_analysis=self.home_team_analysis, 
            away_analysis=self.away_team_analysis
        )
        
        # Basic structure tests
        self.assertIsInstance(embed, MockEmbed)
        self.assertIn("Comprehensive Betting Insights", embed.title)
        self.assertIn("Liverpool FC @ Manchester United", embed.description)
        self.assertIn("Combining H2H history + current form", embed.description)
        
        # Field content tests - should match schedule.py betting methodology
        field_names = [field.name for field in embed.fields]
        self.assertIn("🎯 Primary Recommendations", field_names)
        self.assertIn("📊 Market Analysis", field_names)
        self.assertIn("📈 Form & H2H Momentum", field_names)
        self.assertIn("📋 Supporting Evidence", field_names)
        self.assertIn("🎯 Confidence Assessment", field_names)
        
        # Primary recommendations validation
        primary_field = next(field for field in embed.fields if field.name == "🎯 Primary Recommendations")
        self.assertIn("🟢 Over 2.5 Goals", primary_field.value)  # High confidence over
        self.assertIn("🟢 BTTS Yes", primary_field.value)  # High confidence BTTS
        self.assertIn("🟢 Away Win", primary_field.value)  # High confidence outcome
        
        # Market analysis validation - schedule.py style
        market_field = next(field for field in embed.fields if field.name == "📊 Market Analysis")
        self.assertIn("Expected Total Goals: 3.2", market_field.value)
        self.assertIn("BTTS Probability: 75.0%", market_field.value)
        self.assertIn("Over 2.5 Goals favored", market_field.value)
        
        # Supporting evidence validation
        evidence_field = next(field for field in embed.fields if field.name == "📋 Supporting Evidence")
        self.assertIn("Liverpool in excellent form", evidence_field.value)
        self.assertIn("Both teams average 2+ goals", evidence_field.value)
    
    def test_create_comprehensive_analysis_embed_set(self):
        """Test generation of all 4-5 embeds for comprehensive analysis"""
        embeds = self.embed_builder.create_comprehensive_analysis_embed_set(self.processed_match)
        
        # Should generate 5 embeds with all data available
        self.assertEqual(len(embeds), 5)
        
        # Verify embed order and types
        embed_titles = [embed.title for embed in embeds]
        
        # 1. Match Preview
        self.assertIn("Liverpool FC vs Manchester United", embed_titles[0])
        
        # 2. H2H Historical Record
        self.assertIn("Historical H2H Record", embed_titles[1])
        
        # 3. Home Team Analysis
        self.assertIn("🏠 Manchester United Analysis", embed_titles[2])
        
        # 4. Away Team Analysis
        self.assertIn("✈️ Liverpool FC Analysis", embed_titles[3])
        
        # 5. Comprehensive Betting Insights
        self.assertIn("Comprehensive Betting Insights", embed_titles[4])
        
        # Verify embed numbering
        for i, embed in enumerate(embeds, 1):
            self.assertIn(f"Embed {i}/5", embed.footer.text)
        
        # Verify data source indicators
        self.assertIn("Basic Match Data", embeds[0].footer.text)
        self.assertIn("H2H Endpoint Data", embeds[1].footer.text)
        self.assertIn("Matches Endpoint Data", embeds[2].footer.text)
        self.assertIn("Matches Endpoint Data", embeds[3].footer.text)
        self.assertIn("Combined Analysis", embeds[4].footer.text)
    
    def test_graceful_degradation_missing_data(self):
        """Test graceful degradation when some dual-endpoint data is missing"""
        # Create match with missing H2H data
        incomplete_match = ProcessedMatch(
            match_id=12346,
            home_team=self.home_team,
            away_team=self.away_team,
            league=self.league,
            date="2025-08-19",
            time="15:00",
            venue="Old Trafford",
            status="scheduled",
            odds=self.betting_odds,
            h2h_summary=None,  # Missing H2H data
            h2h_historical_record=None,  # Missing H2H endpoint data
            home_team_analysis=self.home_team_analysis,  # Has matches endpoint data
            away_team_analysis=None,  # Missing away team data
            comprehensive_insights=None  # Missing combined insights
        )
        
        embeds = self.embed_builder.create_comprehensive_analysis_embed_set(incomplete_match)
        
        # Should still generate embeds with available data
        self.assertGreaterEqual(len(embeds), 2)  # At least match preview + home team analysis
        
        # Should include warning embed for missing data
        embed_titles = [embed.title for embed in embeds]
        warning_embed_present = any("Partial Analysis Available" in title for title in embed_titles)
        self.assertTrue(warning_embed_present)
        
        # Verify graceful degradation message
        warning_embed = next(embed for embed in embeds if "Partial Analysis Available" in embed.title)
        self.assertIn("Missing Data Components", [field.name for field in warning_embed.fields])
    
    def test_validate_embed_content_consistency(self):
        """Test validation of embed content against schedule.py output"""
        embeds = self.embed_builder.create_comprehensive_analysis_embed_set(self.processed_match)
        
        # Mock schedule.py output for comparison
        mock_schedule_output = """
        COMPREHENSIVE CUSTOM H2H ANALYSIS (All Available Data)
        ======================================================================
        Manchester United vs Liverpool FC
        
        [RECENT HEAD-TO-HEAD MEETINGS]:
        Total meetings: 25
        Manchester United: 10 wins (40.0% win rate)
        Liverpool FC: 8 wins (32.0% win rate)
        Draws: 7 (28.0%)
        Average goals per game: 2.40
        
        [COMPREHENSIVE TEAM ANALYSIS] - All Available Data:
        MANCHESTER UNITED - COMPLETE DATA BREAKDOWN:
        Record: 6W-2D-2L (60.0% win rate)
        Form: W-W-D-L-W-W-D-W-L-W
        Goals per game: 2.1 for, 1.3 against
        Clean sheets: 4/10 (40.0%)
        Both teams scored: 6/10 games
        High scoring (3+ goals): 5/10 games
        Yellow cards per game: 2.3
        
        LIVERPOOL FC - COMPLETE DATA BREAKDOWN:
        Record: 7W-1D-2L (70.0% win rate)
        Form: W-W-W-D-L-W-W-W-L-W
        Goals per game: 2.3 for, 1.1 against
        Clean sheets: 5/10 (50.0%)
        
        [ENHANCED BETTING RECOMMENDATIONS]:
        [STRONG BET] 'Over 2.5 Goals' (Expected: 3.2)
        [STRONG BET] 'BTTS Yes' (Probability: 75.0%)
        Liverpool in excellent form with 70% win rate
        Both teams average 2+ goals per game recently
        """
        
        validation_results = self.embed_builder.validate_embed_content_consistency(
            embeds, mock_schedule_output
        )
        
        # Validation should pass with high consistency
        self.assertTrue(validation_results["overall_consistency"])
        self.assertGreaterEqual(validation_results["consistency_score"], 70.0)
        
        # Check specific validations
        self.assertTrue(validation_results["team_names_match"])
        self.assertTrue(validation_results["h2h_data_consistent"])
        self.assertTrue(validation_results["team_analysis_consistent"])
        self.assertTrue(validation_results["betting_insights_similar"])
        
        # Check that key schedule.py keywords were found
        keywords_found = validation_results["schedule_py_keywords_found"]
        self.assertGreater(len(keywords_found), 10)  # Should find many matching keywords
        
        # Check detailed comparison
        detailed = validation_results["detailed_comparison"]
        self.assertEqual(detailed["embed_count"], 5)
        self.assertGreater(detailed["total_keywords_found"], 10)
    
    def test_error_handling_invalid_data(self):
        """Test error handling with invalid or corrupted data"""
        # Test with None data
        embed = self.embed_builder.create_h2h_historical_record_embed(
            None, self.home_team, self.away_team, self.league
        )
        self.assertIn("No H2H History", embed.title)
        
        # Test with zero meetings
        empty_h2h = H2HHistoricalRecord(
            total_meetings=0,
            home_team_wins=0,
            away_team_wins=0,
            draws=0,
            home_team_goals_total=0,
            away_team_goals_total=0,
            avg_goals_per_game=0.0
        )
        
        embed = self.embed_builder.create_h2h_historical_record_embed(
            empty_h2h, self.home_team, self.away_team, self.league
        )
        self.assertIn("No H2H History", embed.title)
    
    def test_league_specific_styling(self):
        """Test league-specific colors and emojis"""
        # Test Premier League styling
        embed = self.embed_builder.create_match_preview_embed(self.processed_match)
        self.assertEqual(embed.color, 0x3d195b)  # Premier League purple
        self.assertIn("🏴󠁧󠁢󠁥󠁮󠁧󠁿", embed.title)  # England flag emoji
        
        # Test La Liga styling
        la_liga_league = League(id=297, name="La Liga", country="Spain")
        la_liga_match = ProcessedMatch(
            match_id=12347,
            home_team=self.home_team,
            away_team=self.away_team,
            league=la_liga_league,
            date="2025-08-19",
            time="15:00",
            venue="Santiago Bernabéu",
            status="scheduled"
        )
        
        embed = self.embed_builder.create_match_preview_embed(la_liga_match)
        self.assertEqual(embed.color, 0xff6900)  # La Liga orange
    
    def test_odds_format_conversion(self):
        """Test proper odds format conversion (decimal to American)"""
        # Test various odds conversions
        test_cases = [
            (2.50, "+150"),  # Positive American odds
            (1.50, "-200"),  # Negative American odds
            (2.00, "+100"),  # Even odds
            (1.10, "-1000")  # Heavy favorite
        ]
        
        for decimal, expected_american in test_cases:
            odds_format = OddsFormat.from_decimal(decimal)
            formatted = self.embed_builder._format_odds(odds_format)
            self.assertIn(expected_american, formatted)
            self.assertIn(str(decimal), formatted)
    
    def test_confidence_emoji_mapping(self):
        """Test confidence level emoji mapping"""
        self.assertEqual(self.embed_builder._get_confidence_emoji("High"), "🟢")
        self.assertEqual(self.embed_builder._get_confidence_emoji("Medium"), "🟡")
        self.assertEqual(self.embed_builder._get_confidence_emoji("Low"), "🔴")
        self.assertEqual(self.embed_builder._get_confidence_emoji("Unknown"), "⚪")

class TestSchedulePyConsistency(unittest.TestCase):
    """Test consistency with schedule.py output format and methodology"""
    
    def setUp(self):
        """Set up test fixtures for schedule.py consistency testing"""
        self.embed_builder = SoccerEmbedBuilder()
        
        # Create realistic test data that matches schedule.py output
        self.realistic_match = self._create_realistic_match_data()
    
    def _create_realistic_match_data(self):
        """Create realistic match data that would come from schedule.py analysis"""
        home_team = Team(id=228, name="Arsenal", short_name="ARS", country="England")
        away_team = Team(id=229, name="Chelsea", short_name="CHE", country="England")
        league = League(id=228, name="Premier League", country="England")
        
        # Realistic H2H data
        h2h_record = H2HHistoricalRecord(
            total_meetings=58,
            home_team_wins=22,
            away_team_wins=20,
            draws=16,
            home_team_goals_total=78,
            away_team_goals_total=74,
            avg_goals_per_game=2.62,
            last_meeting_date="29-04-2024",
            last_meeting_result="Arsenal 5-0 Chelsea"
        )
        
        # Realistic team analyses
        home_analysis = TeamAnalysis(
            team_name="Arsenal",
            recent_matches_count=10,
            form_record={"wins": 7, "draws": 2, "losses": 1},
            form_string="W-W-D-W-L-W-W-D-W-W",
            goals_per_game=2.4,
            goals_against_per_game=0.9,
            clean_sheet_percentage=60.0,
            btts_percentage=40.0,
            high_scoring_percentage=50.0,
            card_discipline={"yellow_per_game": 1.8, "red_total": 0},
            advanced_metrics={
                "early_goals_frequency": 0.6,
                "late_goals_frequency": 0.2,
                "comeback_wins": 1,
                "home_win_rate": 85.0,
                "away_win_rate": 65.0
            }
        )
        
        away_analysis = TeamAnalysis(
            team_name="Chelsea",
            recent_matches_count=10,
            form_record={"wins": 4, "draws": 3, "losses": 3},
            form_string="L-D-W-L-D-W-W-L-D-W",
            goals_per_game=1.6,
            goals_against_per_game=1.4,
            clean_sheet_percentage=30.0,
            btts_percentage=70.0,
            high_scoring_percentage=30.0,
            card_discipline={"yellow_per_game": 2.5, "red_total": 2},
            advanced_metrics={
                "early_goals_frequency": 0.2,
                "late_goals_frequency": 0.5,
                "comeback_wins": 0,
                "home_win_rate": 50.0,
                "away_win_rate": 30.0
            }
        )
        
        # Realistic comprehensive insights
        insights = ComprehensiveInsights(
            h2h_dominance="balanced",
            h2h_goals_trend="high_scoring",
            form_momentum="home_advantage",
            expected_goals_total=2.8,
            btts_probability=55.0,
            over_under_recommendation="Over 2.5",
            btts_recommendation="Neutral",
            match_outcome_lean="Home Win",
            cards_market_insight="High Cards",
            recommendation_reasoning=[
                "Arsenal in excellent home form (85% win rate)",
                "Chelsea struggling away from home (30% win rate)",
                "H2H meetings average 2.62 goals per game",
                "Arsenal's solid defense vs Chelsea's inconsistent attack"
            ],
            confidence_level="High"
        )
        
        return ProcessedMatch(
            match_id=99999,
            home_team=home_team,
            away_team=away_team,
            league=league,
            date="2025-08-19",
            time="16:30",
            venue="Emirates Stadium",
            status="scheduled",
            h2h_historical_record=h2h_record,
            home_team_analysis=home_analysis,
            away_team_analysis=away_analysis,
            comprehensive_insights=insights
        )
    
    def test_schedule_py_format_consistency(self):
        """Test that embed output matches schedule.py format and content"""
        embeds = self.embed_builder.create_comprehensive_analysis_embed_set(self.realistic_match)
        
        # Extract all embed content
        all_content = ""
        for embed in embeds:
            all_content += f"{embed.title}\n{embed.description or ''}\n"
            for field in embed.fields:
                all_content += f"{field.name}: {field.value}\n"
        
        # Test for schedule.py key elements
        schedule_py_elements = [
            # H2H Analysis elements
            "58",  # Total meetings
            "22",  # Home wins
            "20",  # Away wins
            "16",  # Draws
            "2.62",  # Average goals per game
            
            # Team analysis elements
            "7W-2D-1L",  # Arsenal record
            "4W-3D-3L",  # Chelsea record
            "70.0% win rate",  # Arsenal win percentage
            "40.0% win rate",  # Chelsea win percentage
            "2.4 for, 0.9 against",  # Arsenal goals
            "1.6 for, 1.4 against",  # Chelsea goals
            
            # Advanced metrics
            "Clean sheets",
            "Both teams scored",
            "Yellow cards per game",
            "Early goals",
            "Late drama",
            
            # Betting insights
            "Over 2.5",
            "Home Win",
            "High Cards",
            "Arsenal in excellent home form",
            "Chelsea struggling away from home"
        ]
        
        missing_elements = []
        for element in schedule_py_elements:
            if element not in all_content:
                missing_elements.append(element)
        
        # Should have most schedule.py elements present
        consistency_rate = (len(schedule_py_elements) - len(missing_elements)) / len(schedule_py_elements)
        self.assertGreaterEqual(consistency_rate, 0.8, 
                               f"Missing schedule.py elements: {missing_elements}")
    
    def test_betting_insights_match_schedule_py(self):
        """Test that betting insights match schedule.py methodology"""
        betting_embed = None
        embeds = self.embed_builder.create_comprehensive_analysis_embed_set(self.realistic_match)
        
        for embed in embeds:
            if "Betting Insights" in embed.title:
                betting_embed = embed
                break
        
        self.assertIsNotNone(betting_embed, "Betting insights embed not found")
        
        # Extract betting content
        betting_content = ""
        for field in betting_embed.fields:
            betting_content += f"{field.name}: {field.value}\n"
        
        # Test schedule.py betting methodology elements
        betting_elements = [
            "Over 2.5",  # Goals recommendation
            "Home Win",  # Outcome recommendation
            "High Cards",  # Cards market
            "Expected Total Goals: 2.8",  # Expected goals calculation
            "Arsenal in excellent home form",  # Form analysis
            "High confidence",  # Confidence assessment
            "Supporting Evidence"  # Reasoning section
        ]
        
        for element in betting_elements:
            self.assertIn(element, betting_content, 
                         f"Missing betting element: {element}")

if __name__ == '__main__':
    # Run the comprehensive tests
    unittest.main(verbosity=2)