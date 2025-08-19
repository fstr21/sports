# Comprehensive Soccer Integration Test Suite
"""
Complete test suite for soccer Discord integration
Tests all components without requiring a running Discord bot instance
"""

import unittest
import asyncio
import json
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import discord
import pytest

# Set up test environment before importing modules
os.environ.setdefault('DISCORD_BOT_TOKEN', 'test_bot_token_' + 'x' * 50)

# Import soccer integration components
from soccer_integration import (
    SoccerMCPClient, SoccerDataProcessor, SoccerEmbedBuilder,
    ProcessedMatch, BettingOdds, H2HInsights, League, Team,
    SUPPORTED_LEAGUES
)
from soccer_channel_manager import SoccerChannelManager
from soccer_config import (
    SoccerConfiguration, SoccerLeagueConfig, SoccerConfigManager,
    get_soccer_config, validate_soccer_environment
)

class TestSoccerMCPClient(unittest.TestCase):
    """Test SoccerMCPClient functionality"""
    
    def setUp(self):
        """Set up test client"""
        self.client = SoccerMCPClient()
        self.sample_match_data = {
            "matches_by_league": {
                "EPL": [
                    {
                        "match_id": 12345,
                        "home_team": {"id": 1, "name": "Arsenal", "logo": "arsenal.png"},
                        "away_team": {"id": 2, "name": "Liverpool", "logo": "liverpool.png"},
                        "date": "2025-08-19",
                        "time": "15:00",
                        "venue": "Emirates Stadium",
                        "status": "scheduled",
                        "odds": {
                            "home_win": 2.50,
                            "draw": 3.20,
                            "away_win": 2.80
                        }
                    }
                ]
            }
        }
    
    def test_client_initialization(self):
        """Test client initializes correctly"""
        self.assertIsInstance(self.client, SoccerMCPClient)
        self.assertEqual(self.client.mcp_url, "https://soccermcp-production.up.railway.app/mcp")
        self.assertIsInstance(self.client.supported_tools, list)
        self.assertIn("get_matches", self.client.supported_tools)
    
    @patch('httpx.AsyncClient.post')
    async def test_call_mcp_tool_success(self, mock_post):
        """Test successful MCP tool call"""
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"data": "test"}}
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = await self.client.call_mcp_tool("get_matches", {"date": "2025-08-19"})
        
        self.assertEqual(result, {"data": "test"})
        mock_post.assert_called_once()
    
    @patch('httpx.AsyncClient.post')
    async def test_call_mcp_tool_failure(self, mock_post):
        """Test MCP tool call failure handling"""
        mock_post.side_effect = Exception("Connection failed")
        
        with self.assertRaises(Exception):
            await self.client.call_mcp_tool("get_matches", {"date": "2025-08-19"})
    
    @patch.object(SoccerMCPClient, 'call_mcp_tool')
    async def test_get_matches_for_date(self, mock_call):
        """Test getting matches for a specific date"""
        mock_call.return_value = self.sample_match_data
        
        result = await self.client.get_matches_for_date("2025-08-19")
        
        self.assertEqual(result, self.sample_match_data)
        mock_call.assert_called_once_with("get_matches", {"date": "2025-08-19"})
    
    def test_validate_date_format(self):
        """Test date format validation"""
        # Valid formats
        self.assertEqual(self.client.validate_date_format("08/19/2025"), "19-08-2025")
        self.assertEqual(self.client.validate_date_format("19-08-2025"), "19-08-2025")
        self.assertEqual(self.client.validate_date_format("2025-08-19"), "19-08-2025")
        
        # Invalid formats
        with self.assertRaises(ValueError):
            self.client.validate_date_format("invalid-date")
        
        with self.assertRaises(ValueError):
            self.client.validate_date_format("2020-01-01")  # Too far in past

class TestSoccerDataProcessor(unittest.TestCase):
    """Test SoccerDataProcessor functionality"""
    
    def setUp(self):
        """Set up test processor"""
        self.processor = SoccerDataProcessor()
        self.sample_raw_data = {
            "matches_by_league": {
                "EPL": [
                    {
                        "match_id": 12345,
                        "home_team": {"id": 1, "name": "Arsenal FC", "logo": "arsenal.png"},
                        "away_team": {"id": 2, "name": "Liverpool F.C.", "logo": "liverpool.png"},
                        "date": "2025-08-19",
                        "time": "15:00",
                        "venue": "Emirates Stadium",
                        "status": "scheduled",
                        "odds": {
                            "home_win": 2.50,
                            "draw": 3.20,
                            "away_win": 2.80,
                            "over_under": {"line": 2.5, "over": 1.90, "under": 1.95}
                        }
                    }
                ]
            }
        }
    
    def test_processor_initialization(self):
        """Test processor initializes correctly"""
        self.assertIsInstance(self.processor, SoccerDataProcessor)
    
    def test_convert_to_american_odds(self):
        """Test decimal to American odds conversion"""
        # Favorites (decimal < 2.0)
        self.assertEqual(self.processor.convert_to_american_odds(1.50), -200)
        self.assertEqual(self.processor.convert_to_american_odds(1.80), -125)
        
        # Underdogs (decimal >= 2.0)
        self.assertEqual(self.processor.convert_to_american_odds(2.50), +150)
        self.assertEqual(self.processor.convert_to_american_odds(3.00), +200)
        
        # Edge cases
        self.assertEqual(self.processor.convert_to_american_odds(2.00), +100)
    
    def test_clean_team_name_for_channel(self):
        """Test team name cleaning for Discord channels"""
        # Test various team name formats
        self.assertEqual(self.processor.clean_team_name_for_channel("Arsenal FC"), "arsenal")
        self.assertEqual(self.processor.clean_team_name_for_channel("Liverpool F.C."), "liverpool")
        self.assertEqual(self.processor.clean_team_name_for_channel("Real Madrid CF"), "real-madrid")
        self.assertEqual(self.processor.clean_team_name_for_channel("Atlético Madrid"), "atletico-madrid")
        
        # Test length limits
        long_name = "Very Long Team Name That Exceeds Normal Limits"
        cleaned = self.processor.clean_team_name_for_channel(long_name)
        self.assertLessEqual(len(cleaned), 20)  # Should be truncated
    
    def test_process_match_data(self):
        """Test processing raw match data into ProcessedMatch objects"""
        processed_matches = self.processor.process_match_data(self.sample_raw_data)
        
        self.assertEqual(len(processed_matches), 1)
        match = processed_matches[0]
        
        self.assertIsInstance(match, ProcessedMatch)
        self.assertEqual(match.match_id, 12345)
        self.assertEqual(match.home_team.name, "Arsenal")  # Should be cleaned
        self.assertEqual(match.away_team.name, "Liverpool")  # Should be cleaned
        self.assertEqual(match.league.name, "Premier League")
        self.assertIsInstance(match.odds, BettingOdds)
    
    def test_extract_betting_odds(self):
        """Test betting odds extraction"""
        match_data = self.sample_raw_data["matches_by_league"]["EPL"][0]
        odds = self.processor.extract_betting_odds(match_data)
        
        self.assertIsInstance(odds, BettingOdds)
        self.assertEqual(odds.home_win.decimal, 2.50)
        self.assertEqual(odds.home_win.american, +150)
        self.assertEqual(odds.draw.decimal, 3.20)
        self.assertEqual(odds.away_win.decimal, 2.80)
        self.assertIsNotNone(odds.over_under)
    
    def test_process_match_data_missing_odds(self):
        """Test processing match data with missing odds"""
        data_without_odds = {
            "matches_by_league": {
                "EPL": [
                    {
                        "match_id": 12345,
                        "home_team": {"id": 1, "name": "Arsenal", "logo": "arsenal.png"},
                        "away_team": {"id": 2, "name": "Liverpool", "logo": "liverpool.png"},
                        "date": "2025-08-19",
                        "time": "15:00",
                        "venue": "Emirates Stadium",
                        "status": "scheduled"
                        # No odds data
                    }
                ]
            }
        }
        
        processed_matches = self.processor.process_match_data(data_without_odds)
        self.assertEqual(len(processed_matches), 1)
        self.assertIsNone(processed_matches[0].odds)

class TestSoccerEmbedBuilder(unittest.TestCase):
    """Test SoccerEmbedBuilder functionality"""
    
    def setUp(self):
        """Set up test embed builder"""
        self.builder = SoccerEmbedBuilder()
        self.sample_match = ProcessedMatch(
            match_id=12345,
            home_team=Team(id=1, name="Arsenal", logo="arsenal.png"),
            away_team=Team(id=2, name="Liverpool", logo="liverpool.png"),
            league=League(id=228, name="Premier League", country="England"),
            date="2025-08-19",
            time="15:00",
            venue="Emirates Stadium",
            status="scheduled",
            odds=BettingOdds(
                home_win={"decimal": 2.50, "american": +150},
                draw={"decimal": 3.20, "american": +220},
                away_win={"decimal": 2.80, "american": +180}
            )
        )
    
    def test_builder_initialization(self):
        """Test embed builder initializes correctly"""
        self.assertIsInstance(self.builder, SoccerEmbedBuilder)
        self.assertIn("EPL", self.builder.colors)
        self.assertEqual(self.builder.colors["EPL"], 0x3d195b)
    
    def test_create_match_preview_embed(self):
        """Test creating match preview embed"""
        embed = self.builder.create_match_preview_embed(self.sample_match)
        
        self.assertIsInstance(embed, discord.Embed)
        self.assertIn("Arsenal", embed.title)
        self.assertIn("Liverpool", embed.title)
        self.assertEqual(embed.color, discord.Color(0x3d195b))  # EPL color
        
        # Check that odds are included
        odds_field = next((field for field in embed.fields if "Odds" in field.name), None)
        self.assertIsNotNone(odds_field)
        self.assertIn("+150", odds_field.value)  # American odds
    
    def test_create_match_preview_embed_no_odds(self):
        """Test creating match preview embed without odds"""
        match_no_odds = ProcessedMatch(
            match_id=12345,
            home_team=Team(id=1, name="Arsenal", logo="arsenal.png"),
            away_team=Team(id=2, name="Liverpool", logo="liverpool.png"),
            league=League(id=228, name="Premier League", country="England"),
            date="2025-08-19",
            time="15:00",
            venue="Emirates Stadium",
            status="scheduled",
            odds=None
        )
        
        embed = self.builder.create_match_preview_embed(match_no_odds)
        
        self.assertIsInstance(embed, discord.Embed)
        # Should still create embed without odds
        odds_field = next((field for field in embed.fields if "Odds" in field.name), None)
        if odds_field:
            self.assertIn("unavailable", odds_field.value.lower())
    
    def test_create_h2h_analysis_embed(self):
        """Test creating H2H analysis embed"""
        h2h_data = H2HInsights(
            total_meetings=10,
            home_team_wins=4,
            away_team_wins=3,
            draws=3,
            avg_goals_per_game=2.5,
            recent_form={
                "Arsenal": ["W", "W", "L", "D", "W"],
                "Liverpool": ["L", "W", "W", "W", "D"]
            },
            betting_recommendations=["Over 2.5 goals", "BTTS Yes"],
            key_statistics={"clean_sheets": {"Arsenal": 2, "Liverpool": 3}}
        )
        
        embed = self.builder.create_h2h_analysis_embed(h2h_data, self.sample_match)
        
        self.assertIsInstance(embed, discord.Embed)
        self.assertIn("Head-to-Head", embed.title)
        
        # Check for H2H statistics
        h2h_field = next((field for field in embed.fields if "Overall Record" in field.name), None)
        self.assertIsNotNone(h2h_field)
        self.assertIn("4", h2h_field.value)  # Home team wins
    
    def test_get_league_color(self):
        """Test getting league-specific colors"""
        self.assertEqual(self.builder.get_league_color("EPL"), 0x3d195b)
        self.assertEqual(self.builder.get_league_color("La Liga"), 0xff6900)
        self.assertEqual(self.builder.get_league_color("Unknown"), 0x00ff00)  # Default

class TestSoccerChannelManager(unittest.TestCase):
    """Test SoccerChannelManager functionality"""
    
    def setUp(self):
        """Set up test channel manager"""
        self.mock_bot = Mock()
        self.mock_guild = Mock()
        self.mock_category = Mock()
        self.mock_channel = Mock()
        
        # Set up mock guild structure
        self.mock_guild.categories = [self.mock_category]
        self.mock_category.name = "⚽ SOCCER"
        self.mock_category.channels = []
        
        self.manager = SoccerChannelManager(self.mock_bot)
        
        self.sample_match = ProcessedMatch(
            match_id=12345,
            home_team=Team(id=1, name="Arsenal", logo="arsenal.png"),
            away_team=Team(id=2, name="Liverpool", logo="liverpool.png"),
            league=League(id=228, name="Premier League", country="England"),
            date="2025-08-19",
            time="15:00",
            venue="Emirates Stadium",
            status="scheduled"
        )
    
    def test_manager_initialization(self):
        """Test channel manager initializes correctly"""
        self.assertIsInstance(self.manager, SoccerChannelManager)
        self.assertEqual(self.manager.category_name, "⚽ SOCCER")
        self.assertEqual(self.manager.channel_prefix, "📊")
    
    def test_generate_channel_name(self):
        """Test channel name generation"""
        channel_name = self.manager.generate_channel_name(self.sample_match, "2025-08-19")
        
        self.assertIn("📊", channel_name)
        self.assertIn("arsenal", channel_name.lower())
        self.assertIn("liverpool", channel_name.lower())
        self.assertIn("08-19", channel_name)
        self.assertLessEqual(len(channel_name), 100)  # Discord limit
    
    @patch('discord.utils.get')
    async def test_get_or_create_soccer_category(self, mock_get):
        """Test getting or creating soccer category"""
        mock_get.return_value = self.mock_category
        
        category = await self.manager.get_or_create_soccer_category(self.mock_guild)
        
        self.assertEqual(category, self.mock_category)
        mock_get.assert_called_once()
    
    @patch('discord.utils.get')
    async def test_create_soccer_category_if_not_exists(self, mock_get):
        """Test creating soccer category if it doesn't exist"""
        mock_get.return_value = None  # Category doesn't exist
        self.mock_guild.create_category = AsyncMock(return_value=self.mock_category)
        
        category = await self.manager.get_or_create_soccer_category(self.mock_guild)
        
        self.assertEqual(category, self.mock_category)
        self.mock_guild.create_category.assert_called_once_with("⚽ SOCCER")

class TestSoccerConfiguration(unittest.TestCase):
    """Test soccer configuration system"""
    
    def setUp(self):
        """Set up test configuration"""
        self.config_manager = SoccerConfigManager()
    
    def test_configuration_loading(self):
        """Test configuration loads correctly"""
        config = self.config_manager.get_config()
        
        self.assertIsInstance(config, SoccerConfiguration)
        self.assertIsInstance(config.leagues, dict)
        self.assertIn("EPL", config.leagues)
        self.assertIn("La Liga", config.leagues)
    
    def test_active_leagues(self):
        """Test getting active leagues"""
        config = self.config_manager.get_config()
        active_leagues = config.get_active_leagues()
        
        self.assertIsInstance(active_leagues, list)
        self.assertGreater(len(active_leagues), 0)
        # UEFA should be first (priority 0)
        self.assertEqual(active_leagues[0], "UEFA")
    
    @patch.dict(os.environ, {'DISCORD_BOT_TOKEN': 'test_token_' + 'x' * 50})
    def test_environment_validation_success(self):
        """Test successful environment validation"""
        validation = self.config_manager.validate_environment()
        
        self.assertTrue(validation["valid"])
        self.assertEqual(len(validation["errors"]), 0)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_environment_validation_failure(self):
        """Test environment validation with missing required variables"""
        validation = self.config_manager.validate_environment()
        
        self.assertFalse(validation["valid"])
        self.assertGreater(len(validation["errors"]), 0)

class TestIntegrationWorkflow(unittest.TestCase):
    """Test end-to-end integration workflow"""
    
    def setUp(self):
        """Set up integration test components"""
        self.client = SoccerMCPClient()
        self.processor = SoccerDataProcessor()
        self.builder = SoccerEmbedBuilder()
        
        self.sample_mcp_response = {
            "matches_by_league": {
                "EPL": [
                    {
                        "match_id": 12345,
                        "home_team": {"id": 1, "name": "Arsenal FC", "logo": "arsenal.png"},
                        "away_team": {"id": 2, "name": "Liverpool F.C.", "logo": "liverpool.png"},
                        "date": "2025-08-19",
                        "time": "15:00",
                        "venue": "Emirates Stadium",
                        "status": "scheduled",
                        "odds": {
                            "home_win": 2.50,
                            "draw": 3.20,
                            "away_win": 2.80
                        }
                    }
                ]
            }
        }
    
    @patch.object(SoccerMCPClient, 'get_matches_for_date')
    async def test_full_channel_creation_workflow(self, mock_get_matches):
        """Test complete workflow from MCP data to Discord embed"""
        # Mock MCP response
        mock_get_matches.return_value = self.sample_mcp_response
        
        # Step 1: Get matches from MCP
        raw_matches = await self.client.get_matches_for_date("2025-08-19")
        
        # Step 2: Process match data
        processed_matches = self.processor.process_match_data(raw_matches)
        
        # Step 3: Create embed
        embed = self.builder.create_match_preview_embed(processed_matches[0])
        
        # Verify workflow
        self.assertEqual(len(processed_matches), 1)
        self.assertIsInstance(embed, discord.Embed)
        self.assertIn("Arsenal", embed.title)
        self.assertIn("Liverpool", embed.title)
    
    def test_error_handling_workflow(self):
        """Test error handling throughout the workflow"""
        # Test with invalid data
        invalid_data = {"invalid": "data"}
        
        # Should handle gracefully
        processed_matches = self.processor.process_match_data(invalid_data)
        self.assertEqual(len(processed_matches), 0)
    
    def test_multiple_leagues_workflow(self):
        """Test workflow with multiple leagues"""
        multi_league_data = {
            "matches_by_league": {
                "EPL": [
                    {
                        "match_id": 1,
                        "home_team": {"id": 1, "name": "Arsenal", "logo": "arsenal.png"},
                        "away_team": {"id": 2, "name": "Liverpool", "logo": "liverpool.png"},
                        "date": "2025-08-19",
                        "time": "15:00",
                        "venue": "Emirates Stadium",
                        "status": "scheduled"
                    }
                ],
                "La Liga": [
                    {
                        "match_id": 2,
                        "home_team": {"id": 3, "name": "Real Madrid", "logo": "real.png"},
                        "away_team": {"id": 4, "name": "Barcelona", "logo": "barca.png"},
                        "date": "2025-08-19",
                        "time": "20:00",
                        "venue": "Santiago Bernabéu",
                        "status": "scheduled"
                    }
                ]
            }
        }
        
        processed_matches = self.processor.process_match_data(multi_league_data)
        
        self.assertEqual(len(processed_matches), 2)
        
        # Check league assignment
        epl_match = next(m for m in processed_matches if m.league.name == "Premier League")
        laliga_match = next(m for m in processed_matches if m.league.name == "La Liga")
        
        self.assertIsNotNone(epl_match)
        self.assertIsNotNone(laliga_match)

# Performance and Load Tests
class TestPerformance(unittest.TestCase):
    """Test performance characteristics"""
    
    def setUp(self):
        """Set up performance test components"""
        self.processor = SoccerDataProcessor()
        self.builder = SoccerEmbedBuilder()
    
    def test_bulk_match_processing_performance(self):
        """Test processing large numbers of matches"""
        import time
        
        # Create large dataset
        large_dataset = {
            "matches_by_league": {
                f"League_{i}": [
                    {
                        "match_id": j,
                        "home_team": {"id": j*2, "name": f"Team {j*2}", "logo": "logo.png"},
                        "away_team": {"id": j*2+1, "name": f"Team {j*2+1}", "logo": "logo.png"},
                        "date": "2025-08-19",
                        "time": "15:00",
                        "venue": "Stadium",
                        "status": "scheduled"
                    }
                    for j in range(10)  # 10 matches per league
                ]
                for i in range(5)  # 5 leagues
            }
        }
        
        start_time = time.time()
        processed_matches = self.processor.process_match_data(large_dataset)
        processing_time = time.time() - start_time
        
        self.assertEqual(len(processed_matches), 50)  # 5 leagues * 10 matches
        self.assertLess(processing_time, 1.0)  # Should process in under 1 second
    
    def test_embed_creation_performance(self):
        """Test embed creation performance"""
        import time
        
        sample_match = ProcessedMatch(
            match_id=12345,
            home_team=Team(id=1, name="Arsenal", logo="arsenal.png"),
            away_team=Team(id=2, name="Liverpool", logo="liverpool.png"),
            league=League(id=228, name="Premier League", country="England"),
            date="2025-08-19",
            time="15:00",
            venue="Emirates Stadium",
            status="scheduled"
        )
        
        start_time = time.time()
        for _ in range(100):  # Create 100 embeds
            embed = self.builder.create_match_preview_embed(sample_match)
        creation_time = time.time() - start_time
        
        self.assertLess(creation_time, 1.0)  # Should create 100 embeds in under 1 second

# Test Runner and Utilities
class TestRunner:
    """Custom test runner for soccer integration tests"""
    
    @staticmethod
    def run_all_tests():
        """Run all soccer integration tests"""
        print("🧪 Running Comprehensive Soccer Integration Test Suite")
        print("=" * 60)
        
        # Create test suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add all test classes
        test_classes = [
            TestSoccerMCPClient,
            TestSoccerDataProcessor,
            TestSoccerEmbedBuilder,
            TestSoccerChannelManager,
            TestSoccerConfiguration,
            TestIntegrationWorkflow,
            TestPerformance
        ]
        
        for test_class in test_classes:
            tests = loader.loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"🏁 Test Summary:")
        print(f"   Tests run: {result.testsRun}")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
        print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
        
        if result.failures:
            print(f"\n❌ Failures:")
            for test, traceback in result.failures:
                print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print(f"\n💥 Errors:")
            for test, traceback in result.errors:
                print(f"   - {test}: {traceback.split('Error:')[-1].strip()}")
        
        return result.wasSuccessful()

if __name__ == "__main__":
    # Run tests when executed directly
    success = TestRunner.run_all_tests()
    exit(0 if success else 1)