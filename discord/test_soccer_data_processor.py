"""
Unit tests for SoccerDataProcessor class
Tests odds conversion, team name cleaning, data processing, and date validation
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json

# Import the classes we're testing
from soccer_integration import (
    SoccerDataProcessor, 
    ProcessedMatch, 
    BettingOdds, 
    H2HInsights,
    H2HSummary,
    Team, 
    League, 
    OddsFormat,
    MCPDataError
)


class TestSoccerDataProcessor(unittest.TestCase):
    """Test cases for SoccerDataProcessor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = SoccerDataProcessor()
    
    def test_convert_to_american_odds_positive(self):
        """Test conversion of decimal odds >= 2.0 to positive American odds"""
        # Test cases: (decimal, expected_american)
        test_cases = [
            (2.0, 100),    # Even odds
            (2.5, 150),    # +150
            (3.0, 200),    # +200
            (4.5, 350),    # +350
            (10.0, 900),   # +900
        ]
        
        for decimal, expected in test_cases:
            with self.subTest(decimal=decimal):
                result = self.processor.convert_to_american_odds(decimal)
                self.assertEqual(result, expected)
    
    def test_convert_to_american_odds_negative(self):
        """Test conversion of decimal odds < 2.0 to negative American odds"""
        # Test cases: (decimal, expected_american)
        test_cases = [
            (1.5, -200),   # -200
            (1.8, -125),   # -125
            (1.25, -400),  # -400
            (1.1, -1000),  # -1000
        ]
        
        for decimal, expected in test_cases:
            with self.subTest(decimal=decimal):
                result = self.processor.convert_to_american_odds(decimal)
                self.assertEqual(result, expected)
    
    def test_convert_to_american_odds_invalid(self):
        """Test error handling for invalid decimal odds"""
        invalid_odds = [0, -1.5, 0.5, -10]
        
        for odds in invalid_odds:
            with self.subTest(odds=odds):
                with self.assertRaises(ValueError):
                    self.processor.convert_to_american_odds(odds)
    
    def test_clean_team_name_for_channel_basic(self):
        """Test basic team name cleaning"""
        test_cases = [
            ("Manchester United", "manchester-united"),
            ("Real Madrid", "real-madrid"),
            ("FC Barcelona", "fc-barcelona"),
            ("Liverpool FC", "liverpool-fc"),
        ]
        
        for original, expected in test_cases:
            with self.subTest(original=original):
                result = self.processor.clean_team_name_for_channel(original)
                self.assertEqual(result, expected)
    
    def test_clean_team_name_for_channel_special_chars(self):
        """Test team name cleaning with special characters"""
        test_cases = [
            ("Atlético Madrid", "atletico-madrid"),
            ("Bayern München", "bayern-munchen"),
            ("AC Milan & Co.", "ac-milan-and-co"),
            ("Real Madrid C.F.", "real-madrid-cf"),
            ("Manchester City F.C.", "manchester-city-fc"),
            ("Borussia Dortmund (BVB)", "borussia-dortmund-bv"),
            ("Inter Miami CF", "inter-miami-cf"),
        ]
        
        for original, expected in test_cases:
            with self.subTest(original=original):
                result = self.processor.clean_team_name_for_channel(original)
                self.assertEqual(result, expected)
    
    def test_clean_team_name_for_channel_edge_cases(self):
        """Test team name cleaning edge cases"""
        # Empty or None input
        self.assertEqual(self.processor.clean_team_name_for_channel(""), "team")
        self.assertEqual(self.processor.clean_team_name_for_channel(None), "team")
        
        # Very long name
        long_name = "A" * 50
        result = self.processor.clean_team_name_for_channel(long_name)
        self.assertLessEqual(len(result), 20)
        
        # Multiple spaces and dashes
        messy_name = "Real---Madrid   FC"
        result = self.processor.clean_team_name_for_channel(messy_name)
        self.assertEqual(result, "real-madrid-fc")
        
        # Leading/trailing dashes
        dash_name = "-Manchester-United-"
        result = self.processor.clean_team_name_for_channel(dash_name)
        self.assertEqual(result, "manchester-united")
    
    def test_validate_date_format_valid_formats(self):
        """Test date validation with valid formats"""
        from datetime import datetime, timedelta
        
        # Use a date within the valid range (next week)
        future_date = datetime.now() + timedelta(days=7)
        test_date_str = future_date.strftime("%m/%d/%Y")
        expected_result = future_date.strftime("%Y-%m-%d")
        
        # Test MM/DD/YYYY format
        result = self.processor.validate_date_format(test_date_str)
        self.assertEqual(result, expected_result)
        
        # Test DD-MM-YYYY format
        test_date_str_dd = future_date.strftime("%d-%m-%Y")
        result = self.processor.validate_date_format(test_date_str_dd)
        self.assertEqual(result, expected_result)
        
        # Test YYYY-MM-DD format
        test_date_str_iso = future_date.strftime("%Y-%m-%d")
        result = self.processor.validate_date_format(test_date_str_iso)
        self.assertEqual(result, expected_result)
    
    def test_validate_date_format_invalid_formats(self):
        """Test date validation with invalid formats"""
        invalid_dates = [
            "",
            None,
            "invalid-date",
            "2024/25/12",  # Invalid day
            "13/01/2024",  # Invalid month for MM/DD format
            "2024-13-01",  # Invalid month
            "32-01-2024",  # Invalid day
        ]
        
        for invalid_date in invalid_dates:
            with self.subTest(date=invalid_date):
                with self.assertRaises(ValueError):
                    self.processor.validate_date_format(invalid_date)
    
    def test_validate_date_format_date_range(self):
        """Test date validation with date range limits"""
        now = datetime.now()
        
        # Date too far in the past (more than 30 days)
        old_date = (now - timedelta(days=35)).strftime("%Y-%m-%d")
        with self.assertRaises(ValueError):
            self.processor.validate_date_format(old_date)
        
        # Date too far in the future (more than 1 year)
        future_date = (now + timedelta(days=400)).strftime("%Y-%m-%d")
        with self.assertRaises(ValueError):
            self.processor.validate_date_format(future_date)
        
        # Valid date within range
        valid_date = (now + timedelta(days=30)).strftime("%Y-%m-%d")
        result = self.processor.validate_date_format(valid_date)
        self.assertEqual(result, valid_date)
    
    def test_process_match_data_valid_data(self):
        """Test processing valid match data"""
        from datetime import datetime, timedelta
        
        # Use a valid future date
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        raw_matches = {
            "matches": [
                {
                    "id": 12345,
                    "home_team": {
                        "id": 1,
                        "name": "Manchester United",
                        "short_name": "MUN",
                        "logo_url": "https://example.com/logo1.png",
                        "country": "England"
                    },
                    "away_team": {
                        "id": 2,
                        "name": "Liverpool FC",
                        "short_name": "LIV",
                        "logo_url": "https://example.com/logo2.png",
                        "country": "England"
                    },
                    "league": {
                        "id": 228,
                        "name": "Premier League",
                        "country": "England",
                        "season": "2024-25"
                    },
                    "date": future_date,
                    "time": "15:00",
                    "venue": "Old Trafford",
                    "status": "scheduled",
                    "odds": {
                        "home_win": 2.5,
                        "draw": 3.2,
                        "away_win": 2.8
                    }
                }
            ]
        }
        
        result = self.processor.process_match_data(raw_matches)
        
        self.assertEqual(len(result), 1)
        match = result[0]
        
        self.assertIsInstance(match, ProcessedMatch)
        self.assertEqual(match.match_id, 12345)
        self.assertEqual(match.home_team.name, "Manchester United")
        self.assertEqual(match.away_team.name, "Liverpool FC")
        self.assertEqual(match.league.name, "Premier League")
        self.assertEqual(match.date, future_date)
        self.assertEqual(match.time, "15:00")
        self.assertEqual(match.venue, "Old Trafford")
        self.assertEqual(match.status, "scheduled")
        
        # Check odds processing
        self.assertIsNotNone(match.odds)
        self.assertIsNotNone(match.odds.home_win)
        self.assertEqual(match.odds.home_win.decimal, 2.5)
        self.assertEqual(match.odds.home_win.american, 150)
    
    def test_process_match_data_content_format(self):
        """Test processing match data in content format"""
        from datetime import datetime, timedelta
        
        # Use a valid future date
        future_date = (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d")
        
        raw_matches = {
            "content": [
                {
                    "text": json.dumps({
                        "matches": [
                            {
                                "id": 67890,
                                "home_team": {
                                    "id": 3,
                                    "name": "Real Madrid",
                                    "short_name": "RMA"
                                },
                                "away_team": {
                                    "id": 4,
                                    "name": "FC Barcelona",
                                    "short_name": "BAR"
                                },
                                "league": {
                                    "id": 297,
                                    "name": "La Liga",
                                    "country": "Spain"
                                },
                                "date": future_date,
                                "time": "20:00",
                                "venue": "Santiago Bernabéu",
                                "status": "scheduled"
                            }
                        ]
                    })
                }
            ]
        }
        
        result = self.processor.process_match_data(raw_matches)
        
        self.assertEqual(len(result), 1)
        match = result[0]
        self.assertEqual(match.match_id, 67890)
        self.assertEqual(match.home_team.name, "Real Madrid")
        self.assertEqual(match.away_team.name, "FC Barcelona")
    
    def test_process_match_data_empty_data(self):
        """Test processing empty match data"""
        empty_data_cases = [
            {},
            {"matches": []},
            {"content": []},
            {"content": [{"text": "{}"}]}
        ]
        
        for empty_data in empty_data_cases:
            with self.subTest(data=empty_data):
                result = self.processor.process_match_data(empty_data)
                self.assertEqual(len(result), 0)
    
    def test_process_match_data_invalid_data(self):
        """Test processing invalid match data"""
        # Non-dictionary input
        with self.assertRaises(MCPDataError):
            self.processor.process_match_data("invalid")
        
        with self.assertRaises(MCPDataError):
            self.processor.process_match_data(None)
        
        with self.assertRaises(MCPDataError):
            self.processor.process_match_data([])
    
    def test_process_match_data_missing_required_fields(self):
        """Test processing match data with missing required fields"""
        # Match without ID
        from datetime import datetime, timedelta
        future_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        
        raw_matches = {
            "matches": [
                {
                    "home_team": {"id": 1, "name": "Team A"},
                    "away_team": {"id": 2, "name": "Team B"},
                    "league": {"id": 1, "name": "League"},
                    "date": future_date,
                    "time": "15:00",
                    "venue": "Stadium",
                    "status": "scheduled"
                }
            ]
        }
        
        result = self.processor.process_match_data(raw_matches)
        self.assertEqual(len(result), 0)  # Should skip invalid matches
        
        # Match without teams
        raw_matches = {
            "matches": [
                {
                    "id": 12345,
                    "league": {"id": 1, "name": "League"},
                    "date": future_date,
                    "time": "15:00",
                    "venue": "Stadium",
                    "status": "scheduled"
                }
            ]
        }
        
        result = self.processor.process_match_data(raw_matches)
        self.assertEqual(len(result), 0)  # Should skip invalid matches
    
    def test_extract_betting_insights_with_odds(self):
        """Test betting insights extraction with odds"""
        odds = BettingOdds(
            home_win=OddsFormat.from_decimal(2.0),  # Even odds
            draw=OddsFormat.from_decimal(3.5),
            away_win=OddsFormat.from_decimal(4.0)
        )
        
        insights = self.processor.extract_betting_insights(odds)
        
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)
        self.assertTrue(any("Home team favored" in insight for insight in insights))
    
    def test_extract_betting_insights_no_odds(self):
        """Test betting insights extraction without odds"""
        insights = self.processor.extract_betting_insights(None)
        self.assertEqual(insights, ["No betting odds available"])
        
        empty_odds = BettingOdds()
        insights = self.processor.extract_betting_insights(empty_odds)
        self.assertEqual(insights, ["No betting odds available"])
    
    def test_extract_betting_insights_with_h2h(self):
        """Test betting insights extraction with H2H data"""
        odds = BettingOdds(
            home_win=OddsFormat.from_decimal(2.0),
            draw=OddsFormat.from_decimal(3.5),
            away_win=OddsFormat.from_decimal(4.0)
        )
        
        h2h_data = H2HInsights(
            total_meetings=10,
            home_team_wins=6,
            away_team_wins=2,
            draws=2,
            avg_goals_per_game=2.8
        )
        
        insights = self.processor.extract_betting_insights(odds, h2h_data)
        
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)
        self.assertTrue(any("Home team dominates" in insight for insight in insights))


class TestOddsFormatIntegration(unittest.TestCase):
    """Test OddsFormat integration with SoccerDataProcessor"""
    
    def setUp(self):
        self.processor = SoccerDataProcessor()
    
    def test_odds_format_from_decimal(self):
        """Test OddsFormat creation from decimal odds"""
        # Test positive American odds
        odds = OddsFormat.from_decimal(3.0)
        self.assertEqual(odds.decimal, 3.0)
        self.assertEqual(odds.american, 200)
        
        # Test negative American odds
        odds = OddsFormat.from_decimal(1.5)
        self.assertEqual(odds.decimal, 1.5)
        self.assertEqual(odds.american, -200)
    
    def test_betting_odds_has_odds_property(self):
        """Test BettingOdds has_odds property"""
        # Empty odds
        empty_odds = BettingOdds()
        self.assertFalse(empty_odds.has_odds)
        
        # Odds with home win only
        odds_with_home = BettingOdds(home_win=OddsFormat.from_decimal(2.0))
        self.assertTrue(odds_with_home.has_odds)
        
        # Odds with all markets
        full_odds = BettingOdds(
            home_win=OddsFormat.from_decimal(2.0),
            draw=OddsFormat.from_decimal(3.5),
            away_win=OddsFormat.from_decimal(4.0)
        )
        self.assertTrue(full_odds.has_odds)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)