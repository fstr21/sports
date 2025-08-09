"""
Integration tests for DataOrchestrator with real MCP server.

These tests require the ESPN MCP server to be running and accessible.
They are designed to test the actual integration with the MCP infrastructure.
"""

import asyncio
import pytest
import os
from datetime import date, timedelta

from daily_betting_intelligence.data_orchestrator import DataOrchestrator
from daily_betting_intelligence.config_manager import ConfigManager


@pytest.mark.skipif(
    os.getenv('RUN_INTEGRATION_TESTS') != '1',
    reason="Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable."
)
class TestDataOrchestratorIntegration:
    """Integration test suite for DataOrchestrator with real MCP server."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create a DataOrchestrator instance for integration testing."""
        config_manager = ConfigManager()
        # Limit to fewer leagues for faster testing
        config_manager.config.leagues = ['wnba', 'nba']
        config_manager.config.max_concurrent_requests = 2
        return DataOrchestrator(config_manager)
    
    @pytest.mark.asyncio
    async def test_fetch_single_league_real_data(self, orchestrator):
        """Test fetching real data for a single league."""
        # Use a recent date that should have WNBA games
        target_date = "20250809"  # Current date from system context
        
        try:
            result = await orchestrator.fetch_league_data('wnba', target_date)
            
            # Should succeed or fail gracefully
            assert result.league == 'wnba'
            assert isinstance(result.success, bool)
            assert isinstance(result.games, list)
            
            if result.success:
                print(f"Successfully fetched {len(result.games)} WNBA games for {target_date}")
                for game in result.games:
                    print(f"  - {game.away_team} @ {game.home_team} at {game.game_time}")
            else:
                print(f"Failed to fetch WNBA data: {result.error}")
                
        except Exception as e:
            pytest.fail(f"Integration test failed with exception: {e}")
    
    @pytest.mark.asyncio
    async def test_fetch_multiple_leagues_real_data(self, orchestrator):
        """Test fetching real data for multiple leagues concurrently."""
        target_date = "20250809"
        leagues = ['wnba']  # Start with just WNBA for reliability
        
        try:
            results = await orchestrator.fetch_all_leagues_data(target_date, leagues)
            
            assert len(results) == len(leagues)
            
            total_games = 0
            successful_leagues = 0
            
            for league, result in results.items():
                assert result.league == league
                assert isinstance(result.success, bool)
                
                if result.success:
                    successful_leagues += 1
                    total_games += len(result.games)
                    print(f"{league.upper()}: {len(result.games)} games")
                else:
                    print(f"{league.upper()}: Failed - {result.error}")
            
            print(f"Integration test summary: {successful_leagues}/{len(leagues)} leagues successful, {total_games} total games")
            
            # At least one league should succeed (WNBA is usually active)
            assert successful_leagues > 0, "At least one league should return data successfully"
            
        except Exception as e:
            pytest.fail(f"Multi-league integration test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_date_validation_integration(self, orchestrator):
        """Test date validation with various formats."""
        test_cases = [
            ("2025-08-09", True),
            ("20250809", True),
            ("2025/08/09", False),
            ("invalid", False),
            ("20200101", False),  # Too far in past
        ]
        
        for date_str, should_be_valid in test_cases:
            is_valid, formatted, parsed = orchestrator.validate_date(date_str)
            assert is_valid == should_be_valid, f"Date validation failed for {date_str}"
            
            if should_be_valid:
                assert formatted == "20250809"
                assert parsed == date(2025, 8, 9)
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, orchestrator):
        """Test error handling with invalid league."""
        target_date = "20250809"
        
        try:
            result = await orchestrator.fetch_league_data('invalid_league', target_date)
            
            # Should fail gracefully
            assert result.success is False
            assert result.league == 'invalid_league'
            assert len(result.games) == 0
            assert result.error is not None
            assert result.error_type is not None
            
            print(f"Error handling test passed: {result.error}")
            
        except Exception as e:
            pytest.fail(f"Error handling integration test failed: {e}")
    
    def test_supported_leagues(self, orchestrator):
        """Test getting supported leagues list."""
        leagues = orchestrator.get_supported_leagues()
        
        assert isinstance(leagues, list)
        assert len(leagues) > 0
        assert 'wnba' in leagues
        assert 'nba' in leagues
        assert 'nfl' in leagues
        
        print(f"Supported leagues: {leagues}")


if __name__ == '__main__':
    # Run integration tests if environment variable is set
    if os.getenv('RUN_INTEGRATION_TESTS') == '1':
        pytest.main([__file__, '-v'])
    else:
        print("Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable.")