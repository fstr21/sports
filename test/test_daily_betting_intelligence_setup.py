"""
Tests for Daily Betting Intelligence system setup and core interfaces.

This module tests the basic functionality of the project structure,
data models, configuration management, and utility functions.
"""

import pytest
from datetime import datetime
from daily_betting_intelligence import (
    GameData, TeamStats, BettingOdds, PlayerProp, GameAnalysis, PlayerAnalysis,
    ConfigManager, DEFAULT_CONFIG, validate_date_format, format_odds,
    calculate_implied_probability, DailyBettingIntelligenceError
)


class TestDataModels:
    """Test core data model functionality."""
    
    def test_game_data_creation(self):
        """Test GameData model creation and attributes."""
        game_time = datetime.now()
        game = GameData(
            event_id="test_123",
            league="nba",
            home_team="Lakers",
            away_team="Warriors",
            game_time=game_time,
            venue="Crypto.com Arena",
            status="pre-game"
        )
        
        assert game.event_id == "test_123"
        assert game.league == "nba"
        assert game.home_team == "Lakers"
        assert game.away_team == "Warriors"
        assert game.game_time == game_time
        assert game.venue == "Crypto.com Arena"
        assert game.status == "pre-game"
        assert game.home_score is None
        assert game.away_score is None
    
    def test_betting_odds_creation(self):
        """Test BettingOdds model creation and attributes."""
        odds = BettingOdds(
            event_id="test_123",
            sportsbook="DraftKings",
            moneyline_home=-150,
            moneyline_away=130,
            spread_line=-2.5,
            spread_home_odds=-110,
            spread_away_odds=-110
        )
        
        assert odds.event_id == "test_123"
        assert odds.sportsbook == "DraftKings"
        assert odds.moneyline_home == -150
        assert odds.moneyline_away == 130
        assert odds.spread_line == -2.5
        assert odds.spread_home_odds == -110
        assert odds.spread_away_odds == -110
    
    def test_player_prop_creation(self):
        """Test PlayerProp model creation and attributes."""
        prop = PlayerProp(
            player_name="LeBron James",
            prop_type="points",
            line=25.5,
            over_odds=-110,
            under_odds=-110,
            sportsbook="FanDuel",
            event_id="test_123"
        )
        
        assert prop.player_name == "LeBron James"
        assert prop.prop_type == "points"
        assert prop.line == 25.5
        assert prop.over_odds == -110
        assert prop.under_odds == -110
        assert prop.sportsbook == "FanDuel"
        assert prop.event_id == "test_123"


class TestConfigManager:
    """Test configuration management functionality."""
    
    def test_default_config_loading(self):
        """Test loading default configuration."""
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        assert config.leagues == DEFAULT_CONFIG["leagues"]
        assert config.betting_markets == DEFAULT_CONFIG["betting_markets"]
        assert config.timezone == DEFAULT_CONFIG["timezone"]
        assert config.timeout_seconds == DEFAULT_CONFIG["timeout_seconds"]
        assert config.max_concurrent_requests == DEFAULT_CONFIG["max_concurrent_requests"]
    
    def test_league_validation(self):
        """Test league validation functionality."""
        config_manager = ConfigManager()
        
        # Test valid leagues
        valid_leagues = config_manager.validate_leagues(["nba", "nfl", "mlb"])
        assert valid_leagues == ["nba", "nfl", "mlb"]
        
        # Test invalid leagues are filtered out
        mixed_leagues = config_manager.validate_leagues(["nba", "invalid_league", "nfl"])
        assert mixed_leagues == ["nba", "nfl"]
        
        # Test empty list
        empty_leagues = config_manager.validate_leagues([])
        assert empty_leagues == []
    
    def test_market_validation(self):
        """Test betting market validation functionality."""
        config_manager = ConfigManager()
        
        # Test valid markets
        valid_markets = config_manager.validate_markets(["h2h", "spreads", "totals"])
        assert valid_markets == ["h2h", "spreads", "totals"]
        
        # Test invalid markets are filtered out
        mixed_markets = config_manager.validate_markets(["h2h", "invalid_market", "spreads"])
        assert mixed_markets == ["h2h", "spreads"]
    
    def test_league_config_retrieval(self):
        """Test league configuration retrieval."""
        config_manager = ConfigManager()
        
        # Test known league
        nba_config = config_manager.get_league_config("nba")
        assert nba_config["display_name"] == "NBA"
        assert nba_config["full_name"] == "National Basketball Association"
        assert "h2h" in nba_config["primary_markets"]
        
        # Test unknown league
        unknown_config = config_manager.get_league_config("unknown")
        assert unknown_config["display_name"] == "UNKNOWN"
        assert "Unknown League" in unknown_config["full_name"]


class TestUtilityFunctions:
    """Test utility function functionality."""
    
    def test_date_validation(self):
        """Test date format validation."""
        # Valid dates
        assert validate_date_format("2025-08-09") is True
        assert validate_date_format("2024-12-31") is True
        assert validate_date_format("2025-01-01") is True
        
        # Invalid formats
        assert validate_date_format("08-09-2025") is False
        assert validate_date_format("2025/08/09") is False
        assert validate_date_format("2025-8-9") is False
        assert validate_date_format("invalid") is False
        assert validate_date_format("") is False
        
        # Invalid dates
        assert validate_date_format("2025-13-01") is False
        assert validate_date_format("2025-02-30") is False
    
    def test_odds_formatting(self):
        """Test odds formatting functionality."""
        # Positive odds
        assert format_odds(150) == "+150"
        assert format_odds(200) == "+200"
        
        # Negative odds
        assert format_odds(-150) == "-150"
        assert format_odds(-200) == "-200"
        
        # Even odds
        assert format_odds(100) == "+100"
        assert format_odds(-100) == "-100"
    
    def test_implied_probability_calculation(self):
        """Test implied probability calculation from odds."""
        # Positive odds
        prob_150 = calculate_implied_probability(150)
        assert abs(prob_150 - 0.4) < 0.01  # Should be approximately 40%
        
        prob_200 = calculate_implied_probability(200)
        assert abs(prob_200 - 0.333) < 0.01  # Should be approximately 33.3%
        
        # Negative odds
        prob_neg_150 = calculate_implied_probability(-150)
        assert abs(prob_neg_150 - 0.6) < 0.01  # Should be approximately 60%
        
        prob_neg_200 = calculate_implied_probability(-200)
        assert abs(prob_neg_200 - 0.667) < 0.01  # Should be approximately 66.7%
        
        # Even odds
        prob_100 = calculate_implied_probability(100)
        assert abs(prob_100 - 0.5) < 0.01  # Should be exactly 50%


class TestExceptions:
    """Test custom exception functionality."""
    
    def test_base_exception(self):
        """Test base exception creation and attributes."""
        context = {"test": "data"}
        error = DailyBettingIntelligenceError("Test error", context)
        
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.context == context
    
    def test_exception_without_context(self):
        """Test exception creation without context."""
        error = DailyBettingIntelligenceError("Test error")
        
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.context == {}


if __name__ == "__main__":
    pytest.main([__file__])