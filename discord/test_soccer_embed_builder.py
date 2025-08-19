"""
Unit tests for SoccerEmbedBuilder class
Tests embed formatting, content validation, and error handling
"""

import unittest
from unittest.mock import Mock, patch
import discord
from datetime import datetime
import sys
import os

# Add the parent directory to the path so we can import the soccer integration module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from discord.soccer_embed_builder import (
    SoccerEmbedBuilder,
    ProcessedMatch,
    Team,
    League,
    BettingOdds,
    OddsFormat,
    OverUnder,
    H2HInsights,
    H2HSummary,
    SUPPORTED_LEAGUES
)


class TestSoccerEmbedBuilder(unittest.TestCase):
    """Test cases for SoccerEmbedBuilder class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.embed_builder = SoccerEmbedBuilder()
        
        # Create test teams
        self.home_team = Team(
            id=1,
            name="Arsenal",
            short_name="ARS",
            logo_url="https://example.com/arsenal.png",
            country="England"
        )
        
        self.away_team = Team(
            id=2,
            name="Liverpool",
            short_name="LIV",
            logo_url="https://example.com/liverpool.png",
            country="England"
        )
        
        # Create test league
        self.league = League(
            id=228,
            name="Premier League",
            country="England",
            season="2024-25",
            logo_url="https://example.com/epl.png"
        )
        
        # Create test betting odds
        self.betting_odds = BettingOdds(
            home_win=OddsFormat.from_decimal(2.50),
            draw=OddsFormat.from_decimal(3.20),
            away_win=OddsFormat.from_decimal(2.80),
            over_under=OverUnder(
                line=2.5,
                over_odds=OddsFormat.from_decimal(1.90),
                under_odds=OddsFormat.from_decimal(1.95)
            ),
            both_teams_score=OddsFormat.from_decimal(1.75)
        )
        
        # Create test H2H summary
        self.h2h_summary = H2HSummary(
            total_meetings=10,
            home_team_wins=4,
            away_team_wins=3,
            draws=3,
            last_meeting_result="Arsenal 2-1 Liverpool"
        )
        
        # Create test H2H insights
        self.h2h_insights = H2HInsights(
            total_meetings=10,
            home_team_wins=4,
            away_team_wins=3,
            draws=3,
            avg_goals_per_game=2.8,
            recent_form={
                "Arsenal": ["W", "D", "W", "L", "W"],
                "Liverpool": ["L", "W", "W", "D", "L"]
            },
            betting_recommendations=[
                "Over 2.5 goals likely based on history",
                "Both teams to score probable"
            ],
            key_statistics={
                "avg_cards_per_game": 4.2,
                "clean_sheets_home": 3,
                "clean_sheets_away": 2
            }
        )
        
        # Create test match
        self.test_match = ProcessedMatch(
            match_id=12345,
            home_team=self.home_team,
            away_team=self.away_team,
            league=self.league,
            date="2024-08-17",
            time="15:00",
            venue="Emirates Stadium",
            status="scheduled",
            odds=self.betting_odds,
            h2h_summary=self.h2h_summary
        )
    
    def test_initialization(self):
        """Test SoccerEmbedBuilder initialization"""
        builder = SoccerEmbedBuilder()
        
        # Check colors are properly set
        self.assertIn("EPL", builder.colors)
        self.assertIn("La Liga", builder.colors)
        self.assertIn("default", builder.colors)
        
        # Check emojis are properly set
        self.assertIn("EPL", builder.emojis)
        self.assertIn("UEFA", builder.emojis)
        self.assertIn("default", builder.emojis)
        
        # Check logger is set
        self.assertIsNotNone(builder.logger)
    
    def test_get_league_color(self):
        """Test league color retrieval"""
        # Test with known league
        color = self.embed_builder._get_league_color(self.league)
        self.assertEqual(color, SUPPORTED_LEAGUES["EPL"]["color"])
        
        # Test with unknown league
        unknown_league = League(id=999, name="Unknown League", country="Unknown")
        color = self.embed_builder._get_league_color(unknown_league)
        self.assertEqual(color, self.embed_builder.colors["default"])
    
    def test_get_league_emoji(self):
        """Test league emoji retrieval"""
        # Test with known league
        emoji = self.embed_builder._get_league_emoji(self.league)
        self.assertEqual(emoji, SUPPORTED_LEAGUES["EPL"]["emoji"])
        
        # Test with unknown league
        unknown_league = League(id=999, name="Unknown League", country="Unknown")
        emoji = self.embed_builder._get_league_emoji(unknown_league)
        self.assertEqual(emoji, self.embed_builder.emojis["default"])
    
    def test_format_odds(self):
        """Test odds formatting"""
        odds_format = OddsFormat.from_decimal(2.50)
        formatted = self.embed_builder._format_odds(odds_format)
        
        self.assertIn("2.50", formatted)
        self.assertIn("+150", formatted)
        
        # Test negative odds
        odds_format_negative = OddsFormat.from_decimal(1.50)
        formatted_negative = self.embed_builder._format_odds(odds_format_negative)
        
        self.assertIn("1.50", formatted_negative)
        self.assertIn("-200", formatted_negative)
    
    def test_safe_get_field_value(self):
        """Test safe field value retrieval"""
        # Test with valid value
        result = self.embed_builder._safe_get_field_value("Test Value")
        self.assertEqual(result, "Test Value")
        
        # Test with None
        result = self.embed_builder._safe_get_field_value(None)
        self.assertEqual(result, "N/A")
        
        # Test with empty string
        result = self.embed_builder._safe_get_field_value("")
        self.assertEqual(result, "N/A")
        
        # Test with custom default
        result = self.embed_builder._safe_get_field_value(None, "Custom Default")
        self.assertEqual(result, "Custom Default")
    
    def test_create_match_preview_embed(self):
        """Test match preview embed creation"""
        embed = self.embed_builder.create_match_preview_embed(self.test_match)
        
        # Check embed properties
        self.assertIsInstance(embed, discord.Embed)
        self.assertIn("Liverpool vs Arsenal", embed.title)
        self.assertEqual(embed.color.value, SUPPORTED_LEAGUES["EPL"]["color"])
        
        # Check fields are present
        field_names = [field.name for field in embed.fields]
        self.assertIn("🏆 Competition", field_names)
        self.assertIn("📅 Date", field_names)
        self.assertIn("⏰ Time", field_names)
        self.assertIn("🏟️ Venue", field_names)
        self.assertIn("✈️ Away Team", field_names)
        self.assertIn("🏠 Home Team", field_names)
        self.assertIn("💰 Betting Odds", field_names)
        self.assertIn("📊 Head-to-Head", field_names)
        self.assertIn("📋 Status", field_names)
        
        # Check footer
        self.assertIn("Match ID: 12345", embed.footer.text)
    
    def test_create_match_preview_embed_minimal_data(self):
        """Test match preview embed with minimal data"""
        minimal_match = ProcessedMatch(
            match_id=67890,
            home_team=Team(id=1, name="Team A", short_name="TA"),
            away_team=Team(id=2, name="Team B", short_name="TB"),
            league=League(id=999, name="Unknown League", country="Unknown"),
            date="",
            time="",
            venue="",
            status="scheduled"
        )
        
        embed = self.embed_builder.create_match_preview_embed(minimal_match)
        
        # Should still create embed without errors
        self.assertIsInstance(embed, discord.Embed)
        self.assertIn("Team B vs Team A", embed.title)
        
        # Check that TBD values are used for missing data
        date_field = next((f for f in embed.fields if f.name == "📅 Date"), None)
        self.assertIsNotNone(date_field)
        self.assertEqual(date_field.value, "TBD")
    
    def test_create_betting_odds_embed(self):
        """Test betting odds embed creation"""
        embed = self.embed_builder.create_betting_odds_embed(self.test_match)
        
        # Check embed properties
        self.assertIsInstance(embed, discord.Embed)
        self.assertIn("Betting Odds", embed.title)
        self.assertEqual(embed.color.value, SUPPORTED_LEAGUES["EPL"]["color"])
        
        # Check fields are present
        field_names = [field.name for field in embed.fields]
        self.assertIn("⚽ Match", field_names)
        self.assertIn("💰 Moneyline (1X2)", field_names)
        self.assertIn("🎯 Total Goals", field_names)
        self.assertIn("🥅 BTTS", field_names)
        self.assertIn("⚠️ Disclaimer", field_names)
        
        # Check moneyline odds content
        moneyline_field = next((f for f in embed.fields if f.name == "💰 Moneyline (1X2)"), None)
        self.assertIsNotNone(moneyline_field)
        self.assertIn("Arsenal Win", moneyline_field.value)
        self.assertIn("Draw", moneyline_field.value)
        self.assertIn("Liverpool Win", moneyline_field.value)
    
    def test_create_betting_odds_embed_no_odds(self):
        """Test betting odds embed with no odds available"""
        match_no_odds = ProcessedMatch(
            match_id=12345,
            home_team=self.home_team,
            away_team=self.away_team,
            league=self.league,
            date="2024-08-17",
            time="15:00",
            venue="Emirates Stadium",
            status="scheduled"
        )
        
        embed = self.embed_builder.create_betting_odds_embed(match_no_odds)
        
        # Should return error embed
        self.assertIsInstance(embed, discord.Embed)
        self.assertIn("No Betting Odds", embed.title)
        self.assertEqual(embed.color.value, 0xff0000)  # Red error color
    
    def test_create_h2h_analysis_embed(self):
        """Test H2H analysis embed creation"""
        embed = self.embed_builder.create_h2h_analysis_embed(
            self.h2h_insights, 
            self.away_team, 
            self.home_team, 
            self.league
        )
        
        # Check embed properties
        self.assertIsInstance(embed, discord.Embed)
        self.assertIn("Head-to-Head", embed.title)
        self.assertEqual(embed.color.value, SUPPORTED_LEAGUES["EPL"]["color"])
        
        # Check fields are present
        field_names = [field.name for field in embed.fields]
        self.assertIn("📈 Overall Record", field_names)
        self.assertIn("🎯 Scoring Stats", field_names)
        self.assertIn("📋 Recent Form (W-D-L)", field_names)
        self.assertIn("📊 Key Statistics", field_names)
        self.assertIn("🎲 Betting Insights", field_names)
        self.assertIn("📈 Historical Trend", field_names)
        
        # Check overall record content
        record_field = next((f for f in embed.fields if f.name == "📈 Overall Record"), None)
        self.assertIsNotNone(record_field)
        self.assertIn("**Total Meetings**: 10", record_field.value)
        self.assertIn("**Liverpool Wins**: 3", record_field.value)
        self.assertIn("**Arsenal Wins**: 4", record_field.value)
        self.assertIn("**Draws**: 3", record_field.value)
    
    def test_create_h2h_analysis_embed_no_data(self):
        """Test H2H analysis embed with no data"""
        empty_h2h = H2HInsights(
            total_meetings=0,
            home_team_wins=0,
            away_team_wins=0,
            draws=0,
            avg_goals_per_game=0.0
        )
        
        embed = self.embed_builder.create_h2h_analysis_embed(
            empty_h2h, 
            self.away_team, 
            self.home_team, 
            self.league
        )
        
        # Should return error embed
        self.assertIsInstance(embed, discord.Embed)
        self.assertIn("No H2H Data", embed.title)
        self.assertEqual(embed.color.value, 0xff0000)  # Red error color
    
    def test_create_league_standings_embed(self):
        """Test league standings embed creation"""
        standings_data = {
            "standings": [
                {
                    "position": 1,
                    "team": {"name": "Arsenal"},
                    "played": 10,
                    "wins": 8,
                    "draws": 1,
                    "losses": 1,
                    "goals_for": 25,
                    "goals_against": 8,
                    "points": 25
                },
                {
                    "position": 2,
                    "team": {"name": "Liverpool"},
                    "played": 10,
                    "wins": 7,
                    "draws": 2,
                    "losses": 1,
                    "goals_for": 22,
                    "goals_against": 10,
                    "points": 23
                }
            ]
        }
        
        embed = self.embed_builder.create_league_standings_embed(standings_data, self.league)
        
        # Check embed properties
        self.assertIsInstance(embed, discord.Embed)
        self.assertIn("Premier League Standings", embed.title)
        self.assertEqual(embed.color.value, SUPPORTED_LEAGUES["EPL"]["color"])
        
        # Check fields are present
        field_names = [field.name for field in embed.fields]
        self.assertIn("🏆 Season", field_names)
        self.assertIn("🌍 Country", field_names)
        self.assertIn("📊 League Table", field_names)
        self.assertIn("📝 Legend", field_names)
        
        # Check standings table content
        table_field = next((f for f in embed.fields if f.name == "📊 League Table"), None)
        self.assertIsNotNone(table_field)
        self.assertIn("Arsenal", table_field.value)
        self.assertIn("Liverpool", table_field.value)
        self.assertIn("25", table_field.value)  # Arsenal points
        self.assertIn("23", table_field.value)  # Liverpool points
    
    def test_create_league_standings_embed_no_data(self):
        """Test league standings embed with no data"""
        empty_standings = {}
        
        embed = self.embed_builder.create_league_standings_embed(empty_standings, self.league)
        
        # Should return error embed
        self.assertIsInstance(embed, discord.Embed)
        self.assertIn("No Standings Data", embed.title)
        self.assertEqual(embed.color.value, 0xff0000)  # Red error color
    
    def test_create_odds_summary(self):
        """Test odds summary creation"""
        summary = self.embed_builder._create_odds_summary(self.betting_odds)
        
        self.assertIn("1X2:", summary)
        self.assertIn("2.50", summary)  # Home win odds
        self.assertIn("3.20", summary)  # Draw odds
        self.assertIn("2.80", summary)  # Away win odds
        self.assertIn("O/U 2.5:", summary)
        self.assertIn("BTTS:", summary)
    
    def test_create_h2h_summary_text(self):
        """Test H2H summary text creation"""
        summary = self.embed_builder._create_h2h_summary_text(self.h2h_summary)
        
        self.assertIn("Last 10 meetings:", summary)
        self.assertIn("4W-3D-3L", summary)
        self.assertIn("Arsenal 2-1 Liverpool", summary)
        
        # Test with no meetings
        empty_h2h = H2HSummary(0, 0, 0, 0)
        summary_empty = self.embed_builder._create_h2h_summary_text(empty_h2h)
        self.assertEqual(summary_empty, "No previous meetings")
    
    def test_create_error_embed(self):
        """Test error embed creation"""
        embed = self.embed_builder._create_error_embed("Test Error", "This is a test error")
        
        self.assertIsInstance(embed, discord.Embed)
        self.assertIn("Test Error", embed.title)
        self.assertEqual(embed.description, "This is a test error")
        self.assertEqual(embed.color.value, 0xff0000)  # Red error color
        self.assertIn("Error occurred", embed.footer.text)
    
    def test_embed_field_limits(self):
        """Test that embeds respect Discord field limits"""
        # Create match with very long team names
        long_home_team = Team(
            id=1,
            name="Very Long Team Name That Exceeds Normal Limits",
            short_name="VLTN"
        )
        long_away_team = Team(
            id=2,
            name="Another Very Long Team Name That Also Exceeds Limits",
            short_name="AVLT"
        )
        
        long_match = ProcessedMatch(
            match_id=12345,
            home_team=long_home_team,
            away_team=long_away_team,
            league=self.league,
            date="2024-08-17",
            time="15:00",
            venue="Very Long Stadium Name That Might Cause Issues",
            status="scheduled"
        )
        
        embed = self.embed_builder.create_match_preview_embed(long_match)
        
        # Should still create embed without errors
        self.assertIsInstance(embed, discord.Embed)
        
        # Check that title length is reasonable
        self.assertLessEqual(len(embed.title), 256)  # Discord title limit
    
    def test_betting_odds_embed_with_insights(self):
        """Test betting odds embed includes insights"""
        # Since we have a simple mock SoccerDataProcessor, this test will pass
        # with the default "Sample insight" response
        embed = self.embed_builder.create_betting_odds_embed(self.test_match)
        
        # Check that insights field is present
        field_names = [field.name for field in embed.fields]
        self.assertIn("💡 Betting Insights", field_names)
        
        # Check insights content
        insights_field = next((f for f in embed.fields if f.name == "💡 Betting Insights"), None)
        self.assertIsNotNone(insights_field)
        self.assertIn("Sample insight", insights_field.value)
    
    def test_league_standings_embed_truncation(self):
        """Test that league standings embed handles large datasets"""
        # Create standings with more than 10 teams
        standings_data = {
            "standings": [
                {
                    "position": i,
                    "team": {"name": f"Team {i}"},
                    "played": 10,
                    "wins": 5,
                    "draws": 3,
                    "losses": 2,
                    "goals_for": 15,
                    "goals_against": 10,
                    "points": 18
                }
                for i in range(1, 21)  # 20 teams
            ]
        }
        
        embed = self.embed_builder.create_league_standings_embed(standings_data, self.league)
        
        # Should still create embed
        self.assertIsInstance(embed, discord.Embed)
        
        # Should show note about truncation
        field_names = [field.name for field in embed.fields]
        self.assertIn("ℹ️ Note", field_names)
        
        note_field = next((f for f in embed.fields if f.name == "ℹ️ Note"), None)
        self.assertIn("Showing top 10 of 20 teams", note_field.value)


if __name__ == '__main__':
    unittest.main()