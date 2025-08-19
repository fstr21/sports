# Soccer Configuration Tests
"""
Comprehensive test suite for soccer configuration system
Tests environment validation, league configuration, and startup checks
"""

import unittest
import os
import json
from unittest.mock import patch, MagicMock
from soccer_config import (
    SoccerLeagueConfig, SoccerConfiguration, SoccerConfigManager,
    get_soccer_config, get_active_soccer_leagues, validate_soccer_environment,
    perform_soccer_startup_checks
)

class TestSoccerLeagueConfig(unittest.TestCase):
    """Test SoccerLeagueConfig dataclass"""
    
    def test_league_config_creation(self):
        """Test creating a league configuration"""
        config = SoccerLeagueConfig(
            id=228,
            name="Premier League",
            country="England",
            priority=1,
            color=0x3d195b
        )
        
        self.assertEqual(config.id, 228)
        self.assertEqual(config.name, "Premier League")
        self.assertEqual(config.country, "England")
        self.assertEqual(config.priority, 1)
        self.assertTrue(config.active)  # Default value
        self.assertEqual(config.tournament_type, "league")  # Default value
    
    def test_league_config_to_dict(self):
        """Test converting league config to dictionary"""
        config = SoccerLeagueConfig(
            id=228,
            name="Premier League",
            country="England",
            priority=1
        )
        
        config_dict = config.to_dict()
        
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict["id"], 228)
        self.assertEqual(config_dict["name"], "Premier League")
        self.assertEqual(config_dict["active"], True)

class TestSoccerConfiguration(unittest.TestCase):
    """Test SoccerConfiguration class"""
    
    def setUp(self):
        """Set up test configuration"""
        self.config = SoccerConfiguration(
            mcp_url="https://test-soccer-mcp.com/mcp",
            auth_key="test_auth_key_123456"
        )
    
    def test_configuration_creation(self):
        """Test creating soccer configuration"""
        self.assertEqual(self.config.mcp_url, "https://test-soccer-mcp.com/mcp")
        self.assertEqual(self.config.auth_key, "test_auth_key_123456")
        self.assertEqual(self.config.max_matches_per_day, 50)
        self.assertTrue(self.config.enable_standings)
        self.assertIsInstance(self.config.leagues, dict)
        self.assertGreater(len(self.config.leagues), 0)
    
    def test_get_active_leagues(self):
        """Test getting active leagues"""
        active_leagues = self.config.get_active_leagues()
        
        self.assertIsInstance(active_leagues, list)
        self.assertIn("EPL", active_leagues)
        self.assertIn("UEFA", active_leagues)
        
        # Check priority ordering (UEFA should be first with priority 0)
        self.assertEqual(active_leagues[0], "UEFA")
    
    def test_get_league_config(self):
        """Test getting specific league configuration"""
        epl_config = self.config.get_league_config("EPL")
        
        self.assertIsNotNone(epl_config)
        self.assertEqual(epl_config.name, "Premier League")
        self.assertEqual(epl_config.country, "England")
        
        # Test non-existent league
        invalid_config = self.config.get_league_config("INVALID")
        self.assertIsNone(invalid_config)
    
    def test_configuration_validation_valid(self):
        """Test validation with valid configuration"""
        is_valid, errors, warnings = self.config.validate()
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        # May have warnings about AUTH_KEY length, but should be valid
    
    def test_configuration_validation_invalid_url(self):
        """Test validation with invalid MCP URL"""
        self.config.mcp_url = "invalid-url"
        
        is_valid, errors, warnings = self.config.validate()
        
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Invalid Soccer MCP URL" in error for error in errors))
    
    def test_configuration_validation_invalid_league(self):
        """Test validation with invalid league configuration"""
        # Add invalid league with negative ID
        self.config.leagues["INVALID"] = SoccerLeagueConfig(
            id=-1,
            name="",
            country="Test",
            priority=-5
        )
        
        is_valid, errors, warnings = self.config.validate()
        
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_to_dict(self):
        """Test converting configuration to dictionary"""
        config_dict = self.config.to_dict()
        
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict["mcp_url"], self.config.mcp_url)
        self.assertIn("leagues", config_dict)
        self.assertIn("rate_limiting", config_dict)
        self.assertIn("error_handling", config_dict)

class TestSoccerConfigManager(unittest.TestCase):
    """Test SoccerConfigManager class"""
    
    def setUp(self):
        """Set up test environment"""
        self.manager = SoccerConfigManager()
    
    @patch.dict(os.environ, {
        'SOCCER_MCP_URL': 'https://test-mcp.com/mcp',
        'AUTH_KEY': 'test_auth_key_123456',
        'DISCORD_BOT_TOKEN': 'test_bot_token_' + 'x' * 50
    })
    def test_load_configuration_from_env(self):
        """Test loading configuration from environment variables"""
        manager = SoccerConfigManager()
        config = manager.get_config()
        
        self.assertEqual(config.mcp_url, 'https://test-mcp.com/mcp')
        self.assertEqual(config.auth_key, 'test_auth_key_123456')
    
    @patch.dict(os.environ, {
        'SOCCER_LEAGUES_CONFIG': json.dumps({
            "TEST_LEAGUE": {
                "id": 999,
                "name": "Test League",
                "country": "Test Country",
                "priority": 10,
                "active": True,
                "color": 0xff0000
            }
        })
    })
    def test_load_custom_league_configs(self):
        """Test loading custom league configurations"""
        manager = SoccerConfigManager()
        config = manager.get_config()
        
        self.assertIn("TEST_LEAGUE", config.leagues)
        test_league = config.leagues["TEST_LEAGUE"]
        self.assertEqual(test_league.name, "Test League")
        self.assertEqual(test_league.id, 999)
    
    @patch.dict(os.environ, {
        'DISCORD_BOT_TOKEN': 'test_bot_token_' + 'x' * 50,
        'SOCCER_MCP_URL': 'https://test-mcp.com/mcp',
        'AUTH_KEY': 'test_auth_key_123456'
    })
    def test_validate_environment_valid(self):
        """Test environment validation with valid environment"""
        manager = SoccerConfigManager()
        validation = manager.validate_environment()
        
        self.assertTrue(validation["valid"])
        self.assertEqual(len(validation["errors"]), 0)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_validate_environment_missing_required(self):
        """Test environment validation with missing required variables"""
        manager = SoccerConfigManager()
        validation = manager.validate_environment()
        
        self.assertFalse(validation["valid"])
        self.assertGreater(len(validation["errors"]), 0)
        self.assertTrue(any("DISCORD_BOT_TOKEN" in error for error in validation["errors"]))
    
    @patch.dict(os.environ, {
        'DISCORD_BOT_TOKEN': 'test_bot_token_' + 'x' * 50
    })
    def test_validate_environment_missing_optional(self):
        """Test environment validation with missing optional variables"""
        manager = SoccerConfigManager()
        validation = manager.validate_environment()
        
        self.assertTrue(validation["valid"])  # Should still be valid
        self.assertIn("SOCCER_MCP_URL", validation["missing_optional"])
        self.assertIn("AUTH_KEY", validation["missing_optional"])
    
    @patch('soccer_config.logger')
    @patch.dict(os.environ, {
        'DISCORD_BOT_TOKEN': 'test_bot_token_' + 'x' * 50,
        'SOCCER_MCP_URL': 'https://test-mcp.com/mcp'
    })
    def test_perform_startup_checks_success(self, mock_logger):
        """Test successful startup checks"""
        manager = SoccerConfigManager()
        result = manager.perform_startup_checks()
        
        self.assertTrue(result)
        mock_logger.info.assert_called()
    
    @patch('soccer_config.logger')
    @patch.dict(os.environ, {}, clear=True)
    def test_perform_startup_checks_failure(self, mock_logger):
        """Test startup checks with missing required environment"""
        manager = SoccerConfigManager()
        result = manager.perform_startup_checks()
        
        self.assertFalse(result)
        mock_logger.error.assert_called()
    
    def test_export_config(self):
        """Test exporting configuration to file"""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            self.manager.export_config(temp_file)
            
            # Verify file was created and contains valid JSON
            with open(temp_file, 'r') as f:
                config_data = json.load(f)
            
            self.assertIsInstance(config_data, dict)
            self.assertIn("mcp_url", config_data)
            self.assertIn("leagues", config_data)
            
        finally:
            os.unlink(temp_file)

class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions for accessing configuration"""
    
    @patch.dict(os.environ, {
        'SOCCER_MCP_URL': 'https://test-mcp.com/mcp',
        'AUTH_KEY': 'test_auth_key_123456'
    })
    def test_get_soccer_config(self):
        """Test get_soccer_config convenience function"""
        # Force reload of configuration to pick up environment changes
        from soccer_config import soccer_config_manager
        soccer_config_manager.reload_config()
        
        config = get_soccer_config()
        
        self.assertIsInstance(config, SoccerConfiguration)
        self.assertEqual(config.mcp_url, 'https://test-mcp.com/mcp')
    
    def test_get_active_soccer_leagues(self):
        """Test get_active_soccer_leagues convenience function"""
        leagues = get_active_soccer_leagues()
        
        self.assertIsInstance(leagues, list)
        self.assertGreater(len(leagues), 0)
        self.assertIn("EPL", leagues)
    
    @patch.dict(os.environ, {
        'DISCORD_BOT_TOKEN': 'test_bot_token_' + 'x' * 50
    })
    def test_validate_soccer_environment(self):
        """Test validate_soccer_environment convenience function"""
        validation = validate_soccer_environment()
        
        self.assertIsInstance(validation, dict)
        self.assertIn("valid", validation)
        self.assertIn("errors", validation)
        self.assertIn("warnings", validation)
    
    @patch.dict(os.environ, {
        'DISCORD_BOT_TOKEN': 'test_bot_token_' + 'x' * 50,
        'SOCCER_MCP_URL': 'https://test-mcp.com/mcp'
    })
    def test_perform_soccer_startup_checks(self):
        """Test perform_soccer_startup_checks convenience function"""
        result = perform_soccer_startup_checks()
        
        self.assertIsInstance(result, bool)

class TestConfigurationIntegration(unittest.TestCase):
    """Integration tests for configuration system"""
    
    @patch.dict(os.environ, {
        'DISCORD_BOT_TOKEN': 'test_bot_token_' + 'x' * 50,
        'SOCCER_MCP_URL': 'https://soccermcp-production.up.railway.app/mcp',
        'AUTH_KEY': 'valid_auth_key_123456789',
        'SOCCER_LEAGUES_CONFIG': json.dumps({
            "EPL": {
                "active": False  # Override default
            },
            "CUSTOM_LEAGUE": {
                "id": 888,
                "name": "Custom League",
                "country": "Custom Country",
                "priority": 99,
                "active": True
            }
        })
    })
    def test_full_configuration_workflow(self):
        """Test complete configuration workflow with custom settings"""
        # Create manager and load configuration
        manager = SoccerConfigManager()
        
        # Validate environment
        validation = manager.validate_environment()
        self.assertTrue(validation["valid"])
        
        # Get configuration
        config = manager.get_config()
        
        # Check custom league was added
        self.assertIn("CUSTOM_LEAGUE", config.leagues)
        custom_league = config.leagues["CUSTOM_LEAGUE"]
        self.assertEqual(custom_league.name, "Custom League")
        self.assertEqual(custom_league.id, 888)
        
        # Check EPL was deactivated
        epl_config = config.leagues["EPL"]
        self.assertFalse(epl_config.active)
        
        # Check active leagues (should not include EPL, should include CUSTOM_LEAGUE)
        active_leagues = config.get_active_leagues()
        self.assertNotIn("EPL", active_leagues)
        self.assertIn("CUSTOM_LEAGUE", active_leagues)
        
        # Perform startup checks
        startup_result = manager.perform_startup_checks()
        self.assertTrue(startup_result)

if __name__ == '__main__':
    # Set up test environment
    os.environ.setdefault('DISCORD_BOT_TOKEN', 'test_bot_token_' + 'x' * 50)
    
    # Run tests
    unittest.main(verbosity=2)