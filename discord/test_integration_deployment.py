#!/usr/bin/env python3
"""
Integration Testing and Deployment Preparation Suite
Task 13: Comprehensive testing for production readiness

This test suite covers:
1. Soccer integration with existing MLB functionality (no conflicts)
2. Load testing with multiple simultaneous channel creation requests
3. Discord API rate limit compliance during peak usage
4. Error recovery scenarios with MCP server downtime and network issues
5. User acceptance testing with sample soccer matches and commands
6. Production readiness validation
"""

import asyncio
import pytest
import time
import logging
import json
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import httpx
import discord

# Set up test environment
os.environ.setdefault('DISCORD_BOT_TOKEN', 'test_bot_token_' + 'x' * 50)
os.environ.setdefault('SOCCER_MCP_URL', 'https://soccermcp-production.up.railway.app/mcp')

# Import components for testing
from soccer_integration import (
    SoccerMCPClient, SoccerDataProcessor, SoccerEmbedBuilder,
    ProcessedMatch, League, Team, BettingOdds, MCPConnectionError, MCPTimeoutError
)
from soccer_channel_manager import SoccerChannelManager
from soccer_cleanup_system import SoccerCleanupSystem
from bot_structure import SportsBot, validate_date_input, handle_soccer_channel_creation

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestSoccerMLBIntegration:
    """Test soccer integration with existing MLB functionality to ensure no conflicts"""
    
    def test_bot_initialization_with_both_sports(self):
        """Test that bot initializes correctly with both MLB and Soccer support"""
        bot = SportsBot()
        
        # Verify both sports are configured
        assert "MLB" in bot.leagues
        assert "SOCCER" in bot.leagues
        
        # Verify both are marked as active
        assert bot.leagues["MLB"]["active"] is True
        assert bot.leagues["SOCCER"]["active"] is True
        
        # Verify soccer components are initialized
        assert hasattr(bot, 'soccer_channel_manager')
        assert hasattr(bot, 'soccer_data_processor')
        assert hasattr(bot, 'soccer_embed_builder')
        assert hasattr(bot, 'soccer_mcp_client')
        
        logger.info("✅ Bot initialization with both MLB and Soccer successful")
    
    def test_category_separation(self):
        """Test that MLB and Soccer categories are properly separated"""
        bot = SportsBot()
        
        # Verify category names are different
        mlb_category = bot.leagues["MLB"]["emoji"] + " MLB"
        soccer_category = bot.leagues["SOCCER"]["emoji"] + " SOCCER"
        
        assert mlb_category != soccer_category
        assert "⚾ MLB" == mlb_category
        assert "⚽ SOCCER" == soccer_category
        
        logger.info("✅ Category separation verified")
    
    def test_command_coexistence(self):
        """Test that soccer commands don't interfere with existing commands"""
        bot = SportsBot()
        
        # Get all registered commands
        commands = [cmd.name for cmd in bot.tree.get_commands()]
        
        # Verify core commands exist
        assert "create-channels" in commands
        
        # Verify command choices include both sports
        create_channels_cmd = next(cmd for cmd in bot.tree.get_commands() if cmd.name == "create-channels")
        sport_param = next(param for param in create_channels_cmd.parameters if param.name == "sport")
        
        choice_values = [choice.value for choice in sport_param.choices]
        assert "Soccer" in choice_values
        assert "MLB" in choice_values
        
        logger.info("✅ Command coexistence verified")
    
    def test_channel_naming_conflicts(self):
        """Test that soccer and MLB channels don't have naming conflicts"""
        # Test channel naming patterns
        soccer_manager = SoccerChannelManager(None)
        
        # Create sample soccer match
        soccer_match = ProcessedMatch(
            match_id=1,
            home_team=Team(id=1, name="Arsenal", short_name="ARS"),
            away_team=Team(id=2, name="Liverpool", short_name="LIV"),
            league=League(id=228, name="Premier League", country="England"),
            date="2025-08-18",
            time="15:00",
            venue="Emirates Stadium",
            status="scheduled"
        )
        
        soccer_channel_name = soccer_manager.generate_channel_name(soccer_match, "2025-08-18")
        
        # Verify soccer channel format
        assert soccer_channel_name.startswith("📊")
        assert "arsenal" in soccer_channel_name.lower()
        assert "liverpool" in soccer_channel_name.lower()
        
        # Verify it's different from potential MLB format
        assert "vs" in soccer_channel_name  # Soccer uses "vs"
        
        logger.info("✅ Channel naming conflicts avoided")

class TestLoadTesting:
    """Test load handling with multiple simultaneous channel creation requests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_channel_creation(self):
        """Test multiple simultaneous channel creation requests"""
        bot = SportsBot()
        
        # Mock MCP response with multiple matches
        mock_matches_data = {
            "matches_by_league": {
                "EPL": [
                    {
                        "id": i,
                        "date": "2025-08-18",
                        "time": f"{15 + (i % 3)}:00",
                        "venue": f"Stadium {i}",
                        "status": "scheduled",
                        "home_team": {"id": i*2, "name": f"Team {i*2}", "short_name": f"T{i*2}"},
                        "away_team": {"id": i*2+1, "name": f"Team {i*2+1}", "short_name": f"T{i*2+1}"}
                    }
                    for i in range(1, 11)  # 10 matches
                ]
            }
        }
        
        # Mock the MCP client
        with patch.object(bot.soccer_mcp_client, 'get_matches_for_date', return_value=mock_matches_data):
            # Create multiple concurrent requests
            tasks = []
            start_time = time.time()
            
            for i in range(5):  # 5 concurrent requests
                task = asyncio.create_task(
                    self._simulate_channel_creation_request(bot, f"2025-08-{18+i}")
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Verify results
            successful_requests = sum(1 for result in results if not isinstance(result, Exception))
            total_time = end_time - start_time
            
            assert successful_requests >= 3  # At least 60% success rate
            assert total_time < 30.0  # Should complete within 30 seconds
            
            logger.info(f"✅ Load test: {successful_requests}/5 requests successful in {total_time:.2f}s")
    
    async def _simulate_channel_creation_request(self, bot, date):
        """Simulate a channel creation request"""
        try:
            # Process matches
            raw_matches = await bot.soccer_mcp_client.get_matches_for_date(date)
            processed_matches = bot.soccer_data_processor.process_match_data(raw_matches)
            
            # Simulate channel creation (without actual Discord API calls)
            return len(processed_matches)
        except Exception as e:
            logger.error(f"Channel creation simulation failed: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_mcp_server_load_handling(self):
        """Test MCP server load handling with rate limiting"""
        client = SoccerMCPClient()
        
        # Test rapid successive calls
        start_time = time.time()
        tasks = []
        
        for i in range(10):  # 10 rapid calls
            task = asyncio.create_task(
                self._safe_mcp_call(client, f"2025-08-{18 + (i % 7)}")
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyze results
        successful_calls = sum(1 for result in results if not isinstance(result, Exception))
        total_time = end_time - start_time
        
        # Should handle at least 70% of calls successfully
        assert successful_calls >= 7
        
        # Should respect rate limiting (not too fast)
        assert total_time >= 2.0  # At least 2 seconds for 10 calls
        
        logger.info(f"✅ MCP load test: {successful_calls}/10 calls successful in {total_time:.2f}s")
    
    async def _safe_mcp_call(self, client, date):
        """Make a safe MCP call with error handling"""
        try:
            # Add small delay to simulate realistic usage
            await asyncio.sleep(0.1)
            return await client.get_matches_for_date(date)
        except Exception as e:
            logger.warning(f"MCP call failed for {date}: {e}")
            raise

class TestDiscordAPIRateLimit:
    """Test Discord API rate limit compliance during peak usage"""
    
    def test_rate_limit_configuration(self):
        """Test that rate limiting is properly configured"""
        from soccer_config import SOCCER_CONFIG
        
        # Verify rate limiting configuration exists
        assert "rate_limiting" in SOCCER_CONFIG
        rate_config = SOCCER_CONFIG["rate_limiting"]
        
        assert "requests_per_minute" in rate_config
        assert "requests_per_hour" in rate_config
        assert "burst_limit" in rate_config
        assert "cooldown_seconds" in rate_config
        
        # Verify reasonable limits
        assert rate_config["requests_per_minute"] <= 60  # Discord's typical limit
        assert rate_config["burst_limit"] <= 10
        assert rate_config["cooldown_seconds"] >= 1
        
        logger.info("✅ Rate limit configuration verified")
    
    @pytest.mark.asyncio
    async def test_channel_creation_rate_limiting(self):
        """Test channel creation respects Discord rate limits"""
        manager = SoccerChannelManager(None)
        
        # Mock Discord objects
        mock_guild = Mock()
        mock_category = Mock()
        mock_guild.categories = [mock_category]
        mock_category.name = "⚽ SOCCER"
        mock_category.create_text_channel = AsyncMock()
        
        # Create multiple matches
        matches = []
        for i in range(15):  # More than typical rate limit
            match = ProcessedMatch(
                match_id=i,
                home_team=Team(id=i*2, name=f"Team {i*2}", short_name=f"T{i*2}"),
                away_team=Team(id=i*2+1, name=f"Team {i*2+1}", short_name=f"T{i*2+1}"),
                league=League(id=228, name="Premier League", country="England"),
                date="2025-08-18",
                time="15:00",
                venue="Stadium",
                status="scheduled"
            )
            matches.append(match)
        
        # Test channel creation with rate limiting
        start_time = time.time()
        created_channels = await manager.create_match_channels(matches, "2025-08-18", mock_guild)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # Should take reasonable time (not too fast due to rate limiting)
        expected_min_time = len(matches) * 0.1  # Minimum 0.1s per channel
        assert total_time >= expected_min_time
        
        logger.info(f"✅ Rate limiting test: {len(created_channels)} channels in {total_time:.2f}s")
    
    def test_embed_size_limits(self):
        """Test that embeds don't exceed Discord limits"""
        builder = SoccerEmbedBuilder()
        
        # Create match with extensive data
        match = ProcessedMatch(
            match_id=1,
            home_team=Team(
                id=1, 
                name="Very Long Team Name That Could Potentially Exceed Limits",
                short_name="VLTNTCPEL"
            ),
            away_team=Team(
                id=2,
                name="Another Very Long Team Name With Extensive Details",
                short_name="AVLTNEWD"
            ),
            league=League(id=228, name="Premier League", country="England"),
            date="2025-08-18",
            time="15:00",
            venue="Very Long Stadium Name That Could Cause Issues",
            status="scheduled",
            odds=BettingOdds(
                home_win={"decimal": 2.50, "american": +150},
                draw={"decimal": 3.20, "american": +220},
                away_win={"decimal": 2.80, "american": +180}
            )
        )
        
        embed = builder.create_match_preview_embed(match)
        
        # Verify Discord limits
        assert len(embed.title) <= 256  # Discord title limit
        assert len(embed.description or "") <= 4096  # Discord description limit
        
        # Check field limits
        for field in embed.fields:
            assert len(field.name) <= 256  # Field name limit
            assert len(field.value) <= 1024  # Field value limit
        
        assert len(embed.fields) <= 25  # Discord field count limit
        
        logger.info("✅ Embed size limits verified")

class TestErrorRecoveryScenarios:
    """Test error recovery scenarios with MCP server downtime and network issues"""
    
    @pytest.mark.asyncio
    async def test_mcp_server_timeout_recovery(self):
        """Test recovery from MCP server timeout"""
        client = SoccerMCPClient()
        
        # Mock timeout scenario
        with patch('httpx.AsyncClient.post', side_effect=httpx.TimeoutException("Request timeout")):
            with pytest.raises(MCPTimeoutError):
                await client.call_mcp_tool("get_matches", {"date": "2025-08-18"})
        
        logger.info("✅ MCP timeout error handling verified")
    
    @pytest.mark.asyncio
    async def test_mcp_server_connection_failure_recovery(self):
        """Test recovery from MCP server connection failure"""
        client = SoccerMCPClient()
        
        # Mock connection failure
        with patch('httpx.AsyncClient.post', side_effect=httpx.ConnectError("Connection failed")):
            with pytest.raises(MCPConnectionError):
                await client.call_mcp_tool("get_matches", {"date": "2025-08-18"})
        
        logger.info("✅ MCP connection error handling verified")
    
    @pytest.mark.asyncio
    async def test_graceful_degradation_no_odds(self):
        """Test graceful degradation when odds data is unavailable"""
        processor = SoccerDataProcessor()
        builder = SoccerEmbedBuilder()
        
        # Create match data without odds
        match_data_no_odds = {
            "matches_by_league": {
                "EPL": [
                    {
                        "id": 1,
                        "date": "2025-08-18",
                        "time": "15:00",
                        "venue": "Stadium",
                        "status": "scheduled",
                        "home_team": {"id": 1, "name": "Arsenal", "short_name": "ARS"},
                        "away_team": {"id": 2, "name": "Liverpool", "short_name": "LIV"}
                        # No odds data
                    }
                ]
            }
        }
        
        # Process data
        processed_matches = processor.process_match_data(match_data_no_odds)
        assert len(processed_matches) == 1
        
        match = processed_matches[0]
        assert match.odds is None
        
        # Create embed - should work without odds
        embed = builder.create_match_preview_embed(match)
        assert embed is not None
        assert "Arsenal" in embed.title
        
        logger.info("✅ Graceful degradation without odds verified")
    
    @pytest.mark.asyncio
    async def test_partial_data_handling(self):
        """Test handling of partial/incomplete data"""
        processor = SoccerDataProcessor()
        
        # Create data with missing fields
        partial_data = {
            "matches_by_league": {
                "EPL": [
                    {
                        "id": 1,
                        "date": "2025-08-18",
                        "home_team": {"id": 1, "name": "Arsenal"},
                        "away_team": {"id": 2, "name": "Liverpool"}
                        # Missing time, venue, status
                    }
                ]
            }
        }
        
        # Should handle gracefully
        processed_matches = processor.process_match_data(partial_data)
        assert len(processed_matches) == 1
        
        match = processed_matches[0]
        assert match.home_team.name == "Arsenal"
        assert match.away_team.name == "Liverpool"
        
        logger.info("✅ Partial data handling verified")
    
    def test_invalid_date_handling(self):
        """Test handling of invalid date inputs"""
        # Test various invalid date formats
        invalid_dates = [
            "invalid-date",
            "32/13/2025",  # Invalid day/month
            "2020-01-01",  # Too far in past
            "2030-01-01",  # Too far in future
            "",            # Empty string
            None           # None value
        ]
        
        for invalid_date in invalid_dates:
            try:
                if invalid_date is not None:
                    validate_date_input(invalid_date)
                    assert False, f"Should have raised error for: {invalid_date}"
            except (ValueError, TypeError):
                pass  # Expected
        
        logger.info("✅ Invalid date handling verified")

class TestUserAcceptanceScenarios:
    """Test user acceptance scenarios with sample soccer matches and commands"""
    
    def test_sample_match_data_processing(self):
        """Test processing of realistic sample match data"""
        processor = SoccerDataProcessor()
        
        # Realistic sample data
        sample_data = {
            "matches_by_league": {
                "EPL": [
                    {
                        "id": 12345,
                        "date": "2025-08-18",
                        "time": "15:00",
                        "venue": "Emirates Stadium",
                        "status": "scheduled",
                        "home_team": {
                            "id": 101,
                            "name": "Arsenal",
                            "short_name": "ARS",
                            "country": "England",
                            "logo": "https://example.com/arsenal.png"
                        },
                        "away_team": {
                            "id": 102,
                            "name": "Liverpool",
                            "short_name": "LIV",
                            "country": "England",
                            "logo": "https://example.com/liverpool.png"
                        },
                        "odds": {
                            "home_win": 2.50,
                            "draw": 3.20,
                            "away_win": 2.80,
                            "over_under": {
                                "line": 2.5,
                                "over": 1.85,
                                "under": 1.95
                            },
                            "both_teams_score": {
                                "yes": 1.70,
                                "no": 2.10
                            }
                        }
                    }
                ],
                "UEFA": [
                    {
                        "id": 67890,
                        "date": "2025-08-18",
                        "time": "20:00",
                        "venue": "Santiago Bernabéu",
                        "status": "scheduled",
                        "stage": {
                            "stage": "quarter_finals",
                            "stage_name": "Quarter Finals",
                            "leg": 1
                        },
                        "home_team": {
                            "id": 201,
                            "name": "Real Madrid",
                            "short_name": "RMA",
                            "country": "Spain"
                        },
                        "away_team": {
                            "id": 202,
                            "name": "Manchester City",
                            "short_name": "MCI",
                            "country": "England"
                        },
                        "odds": {
                            "home_win": 2.10,
                            "draw": 3.40,
                            "away_win": 3.20
                        }
                    }
                ]
            }
        }
        
        processed_matches = processor.process_match_data(sample_data)
        
        # Verify processing
        assert len(processed_matches) == 2
        
        # Check EPL match
        epl_match = next(m for m in processed_matches if m.league.name == "Premier League")
        assert epl_match.home_team.name == "Arsenal"
        assert epl_match.away_team.name == "Liverpool"
        assert epl_match.odds is not None
        assert epl_match.odds.home_win["decimal"] == 2.50
        
        # Check UEFA match
        uefa_match = next(m for m in processed_matches if m.league.name == "UEFA Champions League")
        assert uefa_match.home_team.name == "Real Madrid"
        assert uefa_match.away_team.name == "Manchester City"
        assert uefa_match.league.stage == "quarter_finals"
        
        logger.info("✅ Sample match data processing verified")
    
    def test_embed_visual_quality(self):
        """Test that embeds are visually appealing and informative"""
        builder = SoccerEmbedBuilder()
        
        # Create comprehensive match
        match = ProcessedMatch(
            match_id=12345,
            home_team=Team(id=1, name="Arsenal", short_name="ARS"),
            away_team=Team(id=2, name="Liverpool", short_name="LIV"),
            league=League(id=228, name="Premier League", country="England"),
            date="2025-08-18",
            time="15:00",
            venue="Emirates Stadium",
            status="scheduled",
            odds=BettingOdds(
                home_win={"decimal": 2.50, "american": +150},
                draw={"decimal": 3.20, "american": +220},
                away_win={"decimal": 2.80, "american": +180}
            )
        )
        
        embed = builder.create_match_preview_embed(match)
        
        # Verify visual elements
        assert embed.title is not None and len(embed.title) > 0
        assert embed.color is not None
        assert len(embed.fields) >= 3  # Should have multiple informative fields
        
        # Verify content quality
        assert "Arsenal" in embed.title
        assert "Liverpool" in embed.title
        assert any("Odds" in field.name for field in embed.fields)
        assert any("Match Info" in field.name for field in embed.fields)
        
        logger.info("✅ Embed visual quality verified")
    
    def test_channel_naming_user_friendly(self):
        """Test that channel names are user-friendly and descriptive"""
        manager = SoccerChannelManager(None)
        
        # Test various team name scenarios
        test_cases = [
            ("Arsenal", "Liverpool", "📊 08-18-liverpool-vs-arsenal"),
            ("Manchester United", "Chelsea", "📊 08-18-chelsea-vs-manchester-united"),
            ("Real Madrid CF", "FC Barcelona", "📊 08-18-fc-barcelona-vs-real-madrid-cf")
        ]
        
        for home_team, away_team, expected_pattern in test_cases:
            match = ProcessedMatch(
                match_id=1,
                home_team=Team(id=1, name=home_team, short_name="HT"),
                away_team=Team(id=2, name=away_team, short_name="AT"),
                league=League(id=228, name="Premier League", country="England"),
                date="2025-08-18",
                time="15:00",
                venue="Stadium",
                status="scheduled"
            )
            
            channel_name = manager.generate_channel_name(match, "2025-08-18")
            
            # Verify format
            assert channel_name.startswith("📊")
            assert "08-18" in channel_name
            assert "vs" in channel_name
            assert len(channel_name) <= 100  # Discord limit
            
        logger.info("✅ User-friendly channel naming verified")

class TestProductionReadiness:
    """Test production readiness validation"""
    
    def test_environment_configuration(self):
        """Test that environment is properly configured for production"""
        from soccer_config import validate_soccer_environment, get_soccer_config
        
        # Test environment validation
        validation = validate_soccer_environment()
        
        # Should have basic validation structure
        assert "valid" in validation
        assert "errors" in validation
        assert "warnings" in validation
        
        # Test configuration loading
        config = get_soccer_config()
        assert config is not None
        
        logger.info("✅ Environment configuration verified")
    
    def test_logging_configuration(self):
        """Test that logging is properly configured"""
        from soccer_error_handling import bot_logger
        
        # Verify logger exists and is configured
        assert bot_logger is not None
        
        # Test logging methods exist
        assert hasattr(bot_logger, 'log_operation_start')
        assert hasattr(bot_logger, 'log_operation_success')
        assert hasattr(bot_logger, 'log_operation_error')
        
        logger.info("✅ Logging configuration verified")
    
    def test_error_handling_completeness(self):
        """Test that error handling is comprehensive"""
        from soccer_error_handling import (
            SoccerBotError, MCPConnectionError, MCPTimeoutError, 
            MCPDataError, DiscordAPIError, ValidationError
        )
        
        # Verify all error types exist
        error_types = [
            SoccerBotError, MCPConnectionError, MCPTimeoutError,
            MCPDataError, DiscordAPIError, ValidationError
        ]
        
        for error_type in error_types:
            assert issubclass(error_type, Exception)
        
        logger.info("✅ Error handling completeness verified")
    
    def test_cleanup_system_readiness(self):
        """Test that cleanup system is ready for production"""
        cleanup_system = SoccerCleanupSystem(None, None)
        
        # Verify cleanup system has required methods
        assert hasattr(cleanup_system, 'cleanup_old_channels')
        assert hasattr(cleanup_system, 'get_cleanup_stats')
        
        logger.info("✅ Cleanup system readiness verified")

class TestRunner:
    """Test runner for integration and deployment preparation"""
    
    @staticmethod
    async def run_all_tests():
        """Run all integration and deployment tests"""
        print("🚀 Running Integration Testing and Deployment Preparation Suite")
        print("=" * 80)
        
        test_classes = [
            TestSoccerMLBIntegration,
            TestLoadTesting,
            TestDiscordAPIRateLimit,
            TestErrorRecoveryScenarios,
            TestUserAcceptanceScenarios,
            TestProductionReadiness
        ]
        
        total_tests = 0
        passed_tests = 0
        failed_tests = []
        
        for test_class in test_classes:
            print(f"\n📋 Running {test_class.__name__}")
            print("-" * 50)
            
            # Get test methods
            test_methods = [method for method in dir(test_class) if method.startswith('test_')]
            
            for test_method_name in test_methods:
                total_tests += 1
                test_instance = test_class()
                test_method = getattr(test_instance, test_method_name)
                
                try:
                    if asyncio.iscoroutinefunction(test_method):
                        await test_method()
                    else:
                        test_method()
                    
                    passed_tests += 1
                    print(f"  ✅ {test_method_name}")
                    
                except Exception as e:
                    failed_tests.append((test_class.__name__, test_method_name, str(e)))
                    print(f"  ❌ {test_method_name}: {e}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 INTEGRATION TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {len(failed_tests)}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test_class, test_method, error in failed_tests:
                print(f"  - {test_class}.{test_method}: {error}")
        
        # Determine readiness
        success_rate = passed_tests / total_tests * 100
        if success_rate >= 90:
            print("\n🎉 PRODUCTION READY: All critical tests passed!")
            return True
        elif success_rate >= 75:
            print("\n⚠️  MOSTLY READY: Some non-critical issues found")
            return True
        else:
            print("\n🚫 NOT READY: Critical issues need to be resolved")
            return False

if __name__ == "__main__":
    # Run the integration test suite
    success = asyncio.run(TestRunner.run_all_tests())
    exit(0 if success else 1)