"""
Comprehensive test suite for Soccer Channel Enricher functionality
Tests channel population, analytics generation, and error handling
"""

import asyncio
import json
import logging
import discord
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List

# Import the enricher and related components
from soccer_channel_enricher import (
    SoccerChannelEnricher, TeamFormAnalysis, H2HAnalysis, MatchPreview
)
from soccer_channel_manager import ProcessedMatch, Team, League

# Setup logging for testing
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockDiscordChannel:
    """Mock Discord channel for testing"""
    
    def __init__(self, name: str, id: int = 12345):
        self.name = name
        self.id = id
        self.messages = []
        self.pins = []
    
    async def send(self, content=None, embed=None, **kwargs):
        """Mock send message"""
        message = MockDiscordMessage(content=content, embed=embed)
        self.messages.append(message)
        return message
    
    async def history(self, limit=None):
        """Mock message history"""
        class AsyncIterator:
            def __init__(self, items):
                self.items = items
                self.index = 0
            
            def __aiter__(self):
                return self
            
            async def __anext__(self):
                if self.index >= len(self.items):
                    raise StopAsyncIteration
                item = self.items[self.index]
                self.index += 1
                return item
        
        return AsyncIterator(self.messages[:limit] if limit else self.messages)
    
    def get_message_count(self):
        """Get total message count"""
        return len(self.messages)
    
    def get_messages_with_embeds(self):
        """Get messages that have embeds"""
        return [msg for msg in self.messages if msg.embed is not None]

class MockDiscordMessage:
    """Mock Discord message for testing"""
    
    def __init__(self, content=None, embed=None):
        self.content = content
        self.embed = embed
        self.id = len(str(datetime.now().timestamp()))
    
    async def pin(self, reason=None):
        """Mock pin message"""
        pass

class SoccerChannelEnricherTester:
    """Comprehensive testing suite for Soccer Channel Enricher"""
    
    def __init__(self):
        self.enricher = SoccerChannelEnricher()
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_test_result(self, test_name: str, passed: bool, error: str = None):
        """Log test result"""
        if passed:
            self.test_results["passed"] += 1
            logger.info(f"✅ {test_name} - PASSED")
        else:
            self.test_results["failed"] += 1
            error_msg = f"❌ {test_name} - FAILED: {error}"
            logger.error(error_msg)
            self.test_results["errors"].append(error_msg)
    
    def create_mock_match(self, home_team: str = "Liverpool", away_team: str = "Arsenal") -> ProcessedMatch:
        """Create a mock match for testing"""
        return ProcessedMatch(
            match_id=12345,
            home_team=Team(id=4138, name=home_team, short_name=home_team[:3]),
            away_team=Team(id=4140, name=away_team, short_name=away_team[:3]),
            league=League(id=228, name="Premier League", country="England"),
            date="2025-08-19",
            time="15:00",
            venue="Anfield",
            odds=None,
            h2h_summary=None
        )
    
    # ============================================================================
    # BASIC FUNCTIONALITY TESTS
    # ============================================================================
    
    async def test_enricher_initialization(self):
        """Test that enricher initializes correctly"""
        try:
            enricher = SoccerChannelEnricher()
            
            # Check that components are initialized
            assert hasattr(enricher, 'soccer_client'), "soccer_client not initialized"
            assert hasattr(enricher, 'soccer_processor'), "soccer_processor not initialized" 
            assert hasattr(enricher, 'embed_builder'), "embed_builder not initialized"
            
            self.log_test_result("Enricher Initialization", True)
            
        except Exception as e:
            self.log_test_result("Enricher Initialization", False, str(e))
    
    async def test_team_matching_logic(self):
        """Test team name matching with various formats"""
        try:
            enricher = SoccerChannelEnricher()
            
            # Test exact matches
            assert enricher._teams_match("Liverpool", "Liverpool"), "Exact match failed"
            
            # Test case insensitive
            assert enricher._teams_match("liverpool", "Liverpool"), "Case insensitive failed"
            
            # Test partial matches  
            assert enricher._teams_match("Arsenal", "Arsenal FC"), "Partial match failed"
            
            # Test abbreviations
            assert enricher._teams_match("Man City", "Manchester City"), "Abbreviation match failed"
            
            # Test negative cases
            assert not enricher._teams_match("Liverpool", "Arsenal"), "False positive match"
            
            self.log_test_result("Team Matching Logic", True)
            
        except Exception as e:
            self.log_test_result("Team Matching Logic", False, str(e))
    
    # ============================================================================
    # CHANNEL ENRICHMENT TESTS
    # ============================================================================
    
    async def test_fallback_content_creation(self):
        """Test fallback content when full data is unavailable"""
        try:
            channel = MockDiscordChannel("test-liverpool-vs-arsenal")
            
            # Mock the _send_fallback_content method
            await self.enricher._send_fallback_content(
                channel, "Liverpool", "Arsenal", "2025-08-19", "EPL"
            )
            
            # Check that fallback content was sent
            assert channel.get_message_count() > 0, "No fallback messages sent"
            
            messages_with_embeds = channel.get_messages_with_embeds()
            assert len(messages_with_embeds) > 0, "No fallback embed created"
            
            self.log_test_result("Fallback Content Creation", True)
            
        except Exception as e:
            self.log_test_result("Fallback Content Creation", False, str(e))
    
    async def test_welcome_message_creation(self):
        """Test welcome message creation with match preview"""
        try:
            channel = MockDiscordChannel("test-liverpool-vs-arsenal")
            
            # Create mock match preview
            mock_preview = MatchPreview(
                match_id=12345,
                home_team="Liverpool",
                away_team="Arsenal", 
                date="2025-08-19",
                time="15:00",
                venue="Anfield",
                league="Premier League",
                h2h_analysis=H2HAnalysis("Liverpool", "Arsenal", 10, 4, 3, 3, 12, 8, 2.5, [], {}, {}),
                home_form=TeamFormAnalysis("Liverpool", 4138, [], 3, 1, 1, 8, 4, 2, 3, 2, 1, 1, 0, 1, {}, {}, "W-W-L-W-D", {}),
                away_form=TeamFormAnalysis("Arsenal", 4140, [], 2, 2, 1, 6, 5, 1, 2, 1, 0, 2, 1, 0, {}, {}, "W-D-L-W-D", {}),
                betting_odds={"match_winner": {"home": 2.5, "draw": 3.2, "away": 2.8}},
                predictions={"expected_total_goals": 2.7, "btts_probability": 65},
                key_insights=["Liverpool has strong home record", "Arsenal improved away form"]
            )
            
            await self.enricher._send_welcome_message(channel, mock_preview)
            
            # Verify welcome message was sent
            assert channel.get_message_count() > 0, "No welcome message sent"
            
            messages_with_embeds = channel.get_messages_with_embeds()
            assert len(messages_with_embeds) > 0, "No welcome embed created"
            
            # Check embed content
            welcome_embed = messages_with_embeds[0].embed
            assert "Liverpool vs Arsenal" in str(welcome_embed.title), "Match teams not in title"
            
            self.log_test_result("Welcome Message Creation", True)
            
        except Exception as e:
            self.log_test_result("Welcome Message Creation", False, str(e))
    
    # ============================================================================
    # ANALYTICS GENERATION TESTS  
    # ============================================================================
    
    async def test_h2h_analysis_generation(self):
        """Test head-to-head analysis generation"""
        try:
            # Mock H2H data
            mock_h2h_data = {
                "total_meetings": 10,
                "team_1_record": {"wins": 4, "name": "Liverpool"},
                "team_2_record": {"wins": 3, "name": "Arsenal"},
                "draws": {"count": 3},
                "goals": {"team_1_total": 12, "team_2_total": 8, "average_per_game": 2.0}
            }
            
            # Mock the soccer client call
            with patch.object(self.enricher.soccer_client, 'get_h2h_analysis', return_value=mock_h2h_data):
                context = None  # For testing
                h2h_analysis = await self.enricher._generate_h2h_analysis(
                    4138, 4140, "Liverpool", "Arsenal", 228, context
                )
                
                # Verify H2H analysis structure
                assert h2h_analysis.total_meetings == 10, "Total meetings incorrect"
                assert h2h_analysis.home_team_wins == 4, "Home wins incorrect"
                assert h2h_analysis.away_team_wins == 3, "Away wins incorrect"
                assert h2h_analysis.draws == 3, "Draws incorrect"
                
            self.log_test_result("H2H Analysis Generation", True)
            
        except Exception as e:
            self.log_test_result("H2H Analysis Generation", False, str(e))
    
    async def test_team_form_analysis_generation(self):
        """Test team form analysis generation"""
        try:
            # Mock recent matches data
            mock_matches = [
                {
                    'team_context': {'result_from_team_perspective': 'W', 'is_home': True},
                    'goals': {'fulltime': {'home': 2, 'away': 1}},
                    'insights': {'clean_sheet': {'home': False, 'away': False}, 'both_teams_scored': True},
                    'goal_timing': {'early_goals': 1, 'late_goals': 0},
                    'card_discipline': {'total_cards': 3}
                },
                {
                    'team_context': {'result_from_team_perspective': 'L', 'is_home': False}, 
                    'goals': {'fulltime': {'home': 1, 'away': 0}},
                    'insights': {'clean_sheet': {'home': True, 'away': False}, 'both_teams_scored': False},
                    'goal_timing': {'early_goals': 0, 'late_goals': 1},
                    'card_discipline': {'total_cards': 2}
                }
            ]
            
            # Mock the comprehensive matches call
            with patch.object(self.enricher, '_get_comprehensive_team_matches', return_value=mock_matches):
                context = None  # For testing
                form_analysis = await self.enricher._generate_team_form_analysis(
                    4138, "Liverpool", 228, True, context
                )
                
                # Verify form analysis structure
                assert form_analysis.team_name == "Liverpool", "Team name incorrect"
                assert form_analysis.wins > 0, "No wins recorded"
                assert form_analysis.form_string != '', "Form string empty"
                
            self.log_test_result("Team Form Analysis Generation", True)
            
        except Exception as e:
            self.log_test_result("Team Form Analysis Generation", False, str(e))
    
    async def test_predictions_generation(self):
        """Test match predictions generation"""
        try:
            # Create mock form analyses
            home_form = TeamFormAnalysis(
                "Liverpool", 4138, [], 3, 1, 1, 8, 4, 2, 3, 2, 1, 1, 0, 1, {}, {}, "W-W-L-W-D",
                {"attack_strength": "strong", "btts_tendency": "likely"}
            )
            
            away_form = TeamFormAnalysis(
                "Arsenal", 4140, [], 2, 2, 1, 6, 5, 1, 2, 1, 0, 2, 1, 0, {}, {}, "W-D-L-W-D", 
                {"attack_strength": "average", "btts_tendency": "likely"}
            )
            
            h2h_analysis = H2HAnalysis("Liverpool", "Arsenal", 10, 4, 3, 3, 12, 8, 2.5, [], {}, {})
            
            betting_odds = {"match_winner": {"home": 2.5, "draw": 3.2, "away": 2.8}}
            
            # Generate predictions
            predictions = self.enricher._generate_predictions(h2h_analysis, home_form, away_form, betting_odds)
            
            # Verify predictions structure
            assert isinstance(predictions, dict), "Predictions not a dictionary"
            assert "btts_probability" in predictions, "BTTS probability missing"
            assert "expected_total_goals" in predictions, "Expected goals missing"
            
            self.log_test_result("Predictions Generation", True)
            
        except Exception as e:
            self.log_test_result("Predictions Generation", False, str(e))
    
    async def test_key_insights_generation(self):
        """Test key insights generation"""
        try:
            # Create mock analyses
            h2h_analysis = H2HAnalysis("Liverpool", "Arsenal", 10, 6, 2, 2, 15, 8, 2.8, [], {}, {})
            
            home_form = TeamFormAnalysis(
                "Liverpool", 4138, [], 4, 0, 1, 10, 3, 3, 4, 3, 2, 0, 1, 2, {}, {}, "W-W-W-W-L", {}
            )
            
            away_form = TeamFormAnalysis(
                "Arsenal", 4140, [], 1, 2, 2, 4, 6, 0, 2, 0, 0, 3, 0, 0, {}, {}, "L-D-L-W-D", {}
            )
            
            predictions = {"btts_probability": 75, "expected_total_goals": 3.1, "btts_recommendation": "YES"}
            
            # Generate insights
            insights = self.enricher._generate_key_insights(h2h_analysis, home_form, away_form, predictions)
            
            # Verify insights
            assert isinstance(insights, list), "Insights not a list"
            assert len(insights) > 0, "No insights generated"
            
            # Check for specific insight patterns
            insights_text = " ".join(insights)
            assert any(word in insights_text.lower() for word in ["form", "historical", "advantage"]), "No meaningful insights"
            
            self.log_test_result("Key Insights Generation", True)
            
        except Exception as e:
            self.log_test_result("Key Insights Generation", False, str(e))
    
    # ============================================================================
    # ERROR HANDLING TESTS
    # ============================================================================
    
    async def test_error_handling_missing_data(self):
        """Test error handling when data is missing or invalid"""
        try:
            channel = MockDiscordChannel("test-error-handling")
            
            # Test with invalid match data
            with patch.object(self.enricher, '_find_match_data', return_value=None):
                success = await self.enricher.enrich_channel_on_creation(
                    channel, "InvalidTeam1", "InvalidTeam2", "2025-08-19", "EPL"
                )
                
                # Should return False but not crash
                assert success is False, "Should return False for invalid data"
                
                # Should still send fallback content
                assert channel.get_message_count() > 0, "No fallback content sent on error"
            
            self.log_test_result("Error Handling - Missing Data", True)
            
        except Exception as e:
            self.log_test_result("Error Handling - Missing Data", False, str(e))
    
    async def test_error_handling_api_failures(self):
        """Test error handling when APIs fail"""
        try:
            # Mock API failures
            with patch.object(self.enricher.soccer_client, 'get_matches_for_date', side_effect=Exception("API Error")):
                context = None
                match_data = await self.enricher._find_match_data("Liverpool", "Arsenal", "2025-08-19", "EPL", context)
                
                # Should handle gracefully and return None
                assert match_data is None, "Should return None on API failure"
            
            self.log_test_result("Error Handling - API Failures", True)
            
        except Exception as e:
            self.log_test_result("Error Handling - API Failures", False, str(e))
    
    # ============================================================================
    # INTEGRATION TESTS
    # ============================================================================
    
    async def test_full_channel_enrichment_flow(self):
        """Test complete channel enrichment flow with mocked data"""
        try:
            channel = MockDiscordChannel("test-full-enrichment")
            
            # Mock all the data dependencies
            mock_match = self.create_mock_match()
            
            with patch.object(self.enricher, '_find_match_data', return_value=mock_match), \
                 patch.object(self.enricher, '_generate_match_preview') as mock_preview, \
                 patch.object(self.enricher, '_send_welcome_message') as mock_welcome, \
                 patch.object(self.enricher, '_send_h2h_analysis') as mock_h2h, \
                 patch.object(self.enricher, '_send_team_form_analysis') as mock_form, \
                 patch.object(self.enricher, '_send_betting_analysis') as mock_betting, \
                 patch.object(self.enricher, '_send_tactical_insights') as mock_tactical:
                
                # Mock the preview generation
                mock_preview_data = MatchPreview(
                    12345, "Liverpool", "Arsenal", "2025-08-19", "15:00", "Anfield", "EPL",
                    H2HAnalysis("Liverpool", "Arsenal", 10, 4, 3, 3, 12, 8, 2.5, [], {}, {}),
                    TeamFormAnalysis("Liverpool", 4138, [], 3, 1, 1, 8, 4, 2, 3, 2, 1, 1, 0, 1, {}, {}, "W-W-L", {}),
                    TeamFormAnalysis("Arsenal", 4140, [], 2, 2, 1, 6, 5, 1, 2, 1, 0, 2, 1, 0, {}, {}, "W-D-L", {}),
                    {}, {}, []
                )
                mock_preview.return_value = mock_preview_data
                
                # Run full enrichment
                success = await self.enricher.enrich_channel_on_creation(
                    channel, "Liverpool", "Arsenal", "2025-08-19", "EPL"
                )
                
                # Verify all components were called
                mock_preview.assert_called_once()
                mock_welcome.assert_called_once() 
                mock_h2h.assert_called_once()
                mock_form.assert_called_once()
                mock_betting.assert_called_once()
                mock_tactical.assert_called_once()
                
                assert success is True, "Full enrichment should succeed"
            
            self.log_test_result("Full Channel Enrichment Flow", True)
            
        except Exception as e:
            self.log_test_result("Full Channel Enrichment Flow", False, str(e))
    
    # ============================================================================
    # PERFORMANCE TESTS
    # ============================================================================
    
    async def test_enrichment_performance(self):
        """Test enrichment performance and timing"""
        try:
            import time
            
            channel = MockDiscordChannel("test-performance")
            
            # Mock fast data responses
            with patch.object(self.enricher, '_find_match_data', return_value=self.create_mock_match()), \
                 patch.object(self.enricher, '_generate_match_preview') as mock_preview, \
                 patch.object(self.enricher, '_send_welcome_message'), \
                 patch.object(self.enricher, '_send_h2h_analysis'), \
                 patch.object(self.enricher, '_send_team_form_analysis'), \
                 patch.object(self.enricher, '_send_betting_analysis'), \
                 patch.object(self.enricher, '_send_tactical_insights'):
                
                # Mock preview with minimal processing
                mock_preview_data = MatchPreview(
                    12345, "Liverpool", "Arsenal", "2025-08-19", "15:00", "Anfield", "EPL",
                    H2HAnalysis("Liverpool", "Arsenal", 0, 0, 0, 0, 0, 0, 0, [], {}, {}),
                    TeamFormAnalysis("Liverpool", 4138, [], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, {}, {}, "", {}),
                    TeamFormAnalysis("Arsenal", 4140, [], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, {}, {}, "", {}),
                    {}, {}, []
                )
                mock_preview.return_value = mock_preview_data
                
                # Time the enrichment
                start_time = time.time()
                
                success = await self.enricher.enrich_channel_on_creation(
                    channel, "Liverpool", "Arsenal", "2025-08-19", "EPL"
                )
                
                elapsed_time = time.time() - start_time
                
                # Performance should be reasonable (under 5 seconds with mocked data)
                assert elapsed_time < 5.0, f"Enrichment took too long: {elapsed_time:.2f}s"
                assert success is True, "Performance test should succeed"
                
                logger.info(f"Enrichment completed in {elapsed_time:.2f} seconds")
            
            self.log_test_result("Enrichment Performance", True)
            
        except Exception as e:
            self.log_test_result("Enrichment Performance", False, str(e))
    
    # ============================================================================
    # SUMMARY AND REPORTING
    # ============================================================================
    
    async def run_all_tests(self):
        """Run all test suites"""
        logger.info("🚀 Starting comprehensive Soccer Channel Enricher tests...")
        logger.info("=" * 80)
        
        # Basic functionality tests
        logger.info("📋 Running basic functionality tests...")
        await self.test_enricher_initialization()
        await self.test_team_matching_logic()
        
        # Channel enrichment tests
        logger.info("📊 Running channel enrichment tests...")
        await self.test_fallback_content_creation()
        await self.test_welcome_message_creation()
        
        # Analytics generation tests
        logger.info("🔍 Running analytics generation tests...")
        await self.test_h2h_analysis_generation()
        await self.test_team_form_analysis_generation()
        await self.test_predictions_generation()
        await self.test_key_insights_generation()
        
        # Error handling tests
        logger.info("⚠️ Running error handling tests...")
        await self.test_error_handling_missing_data()
        await self.test_error_handling_api_failures()
        
        # Integration tests
        logger.info("🔗 Running integration tests...")
        await self.test_full_channel_enrichment_flow()
        
        # Performance tests
        logger.info("⚡ Running performance tests...")
        await self.test_enrichment_performance()
        
        # Generate summary report
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        success_rate = (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🎯 SOCCER CHANNEL ENRICHER TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {self.test_results['passed']}")
        logger.info(f"❌ Failed: {self.test_results['failed']}")
        logger.info(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.test_results["errors"]:
            logger.info("\n❌ FAILED TESTS:")
            for error in self.test_results["errors"]:
                logger.info(f"  {error}")
        
        logger.info("\n🎉 Testing completed!")
        logger.info("=" * 80)
        
        # Return summary for external use
        return {
            "total_tests": total_tests,
            "passed": self.test_results["passed"],
            "failed": self.test_results["failed"],
            "success_rate": success_rate,
            "errors": self.test_results["errors"],
            "ready_for_production": success_rate >= 80  # 80% pass rate minimum
        }

# ============================================================================
# TEST RUNNER
# ============================================================================

async def main():
    """Main test runner"""
    tester = SoccerChannelEnricherTester()
    
    try:
        summary = await tester.run_all_tests()
        
        # Print final status
        if summary["ready_for_production"]:
            logger.info("🎉 ENRICHER READY FOR PRODUCTION!")
        else:
            logger.warning("⚠️ ENRICHER NEEDS MORE WORK")
            logger.warning(f"Success rate: {summary['success_rate']:.1f}% (minimum 80% required)")
        
        return summary
        
    except Exception as e:
        logger.error(f"Testing failed with error: {e}")
        return None

if __name__ == "__main__":
    # Run the comprehensive test suite
    asyncio.run(main())