# Soccer Configuration Module
"""
Comprehensive configuration management for soccer integration
Handles environment validation, league configuration, and feature flags
"""

import os
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)

@dataclass
class SoccerLeagueConfig:
    """Configuration for a soccer league"""
    id: int
    name: str
    country: str
    priority: int
    active: bool = True
    color: int = 0x00ff00
    season_format: str = "2025-26"
    tournament_type: str = "league"  # "league" or "knockout"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "country": self.country,
            "priority": self.priority,
            "active": self.active,
            "color": self.color,
            "season_format": self.season_format,
            "tournament_type": self.tournament_type
        }

@dataclass
class SoccerRateLimitConfig:
    """Rate limiting configuration for Soccer MCP"""
    requests_per_minute: int = 30
    requests_per_hour: int = 1800  # 30 * 60 = 1800 to avoid warning
    burst_limit: int = 10
    cooldown_seconds: float = 2.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requests_per_minute": self.requests_per_minute,
            "requests_per_hour": self.requests_per_hour,
            "burst_limit": self.burst_limit,
            "cooldown_seconds": self.cooldown_seconds
        }

@dataclass
class SoccerErrorHandlingConfig:
    """Error handling configuration for Soccer MCP"""
    max_retries: int = 3
    retry_delay_seconds: float = 2.0
    exponential_backoff: bool = True
    fallback_to_cache: bool = True
    graceful_degradation: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_retries": self.max_retries,
            "retry_delay_seconds": self.retry_delay_seconds,
            "exponential_backoff": self.exponential_backoff,
            "fallback_to_cache": self.fallback_to_cache,
            "graceful_degradation": self.graceful_degradation
        }

@dataclass
class SoccerConfiguration:
    """Complete soccer integration configuration"""
    mcp_url: str
    auth_key: Optional[str] = None
    default_date_format: str = "%Y-%m-%d"
    supported_date_formats: List[str] = field(default_factory=lambda: ["%m/%d/%Y", "%d-%m-%Y", "%Y-%m-%d"])
    max_matches_per_day: int = 50
    channel_retention_days: int = 3
    enable_standings: bool = True
    enable_h2h_analysis: bool = True
    enable_betting_recommendations: bool = True
    max_leagues_per_request: int = 6
    cache_duration_minutes: int = 15
    rate_limiting: SoccerRateLimitConfig = field(default_factory=SoccerRateLimitConfig)
    error_handling: SoccerErrorHandlingConfig = field(default_factory=SoccerErrorHandlingConfig)
    leagues: Dict[str, SoccerLeagueConfig] = field(default_factory=dict)
    priority_leagues: List[str] = field(default_factory=lambda: ["UEFA", "EPL", "La Liga", "Bundesliga", "Serie A", "MLS"])
    
    def __post_init__(self):
        """Initialize default league configurations if not provided"""
        if not self.leagues:
            self.leagues = self._get_default_leagues()
    
    def _get_default_leagues(self) -> Dict[str, SoccerLeagueConfig]:
        """Get default league configurations"""
        return {
            "EPL": SoccerLeagueConfig(
                id=228, name="Premier League", country="England",
                priority=1, color=0x3d195b, tournament_type="league"
            ),
            "La Liga": SoccerLeagueConfig(
                id=297, name="La Liga", country="Spain",
                priority=2, color=0xff6900, tournament_type="league"
            ),
            "MLS": SoccerLeagueConfig(
                id=168, name="MLS", country="USA",
                priority=5, color=0x005da6, tournament_type="league"
            ),
            "Bundesliga": SoccerLeagueConfig(
                id=241, name="Bundesliga", country="Germany",
                priority=3, color=0xd20515, tournament_type="league"
            ),
            "Serie A": SoccerLeagueConfig(
                id=253, name="Serie A", country="Italy",
                priority=4, color=0x0066cc, tournament_type="league"
            ),
            "UEFA": SoccerLeagueConfig(
                id=310, name="UEFA Champions League", country="Europe",
                priority=0, color=0x00336a, tournament_type="knockout"
            )
        }
    
    def get_active_leagues(self) -> List[str]:
        """Get list of active league codes sorted by priority"""
        active_leagues = [
            code for code, config in self.leagues.items() 
            if config.active
        ]
        
        # Sort by priority (lower number = higher priority)
        active_leagues.sort(key=lambda x: self.leagues[x].priority)
        return active_leagues
    
    def get_league_config(self, league_code: str) -> Optional[SoccerLeagueConfig]:
        """Get configuration for a specific league"""
        return self.leagues.get(league_code)
    
    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """
        Validate the soccer configuration
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        
        # Validate MCP URL
        if not self.mcp_url.startswith(('http://', 'https://')):
            errors.append("Invalid Soccer MCP URL format")
        
        # Validate AUTH_KEY
        if self.auth_key and len(self.auth_key) < 10:
            warnings.append("AUTH_KEY seems too short, may be invalid")
        elif not self.auth_key:
            warnings.append("No AUTH_KEY provided - some Soccer MCP features may be limited")
        
        # Validate league configurations
        for league_code, league_config in self.leagues.items():
            if league_config.id <= 0:
                errors.append(f"Invalid league ID for {league_code}: {league_config.id}")
            
            if not league_config.name:
                errors.append(f"Missing league name for {league_code}")
            
            if league_config.priority < 0:
                errors.append(f"Invalid priority for {league_code}: {league_config.priority}")
        
        # Validate rate limiting
        if self.rate_limiting.requests_per_minute * 60 > self.rate_limiting.requests_per_hour:
            warnings.append("Rate limiting: requests_per_minute * 60 exceeds requests_per_hour")
        
        # Validate date formats
        for date_format in self.supported_date_formats:
            try:
                datetime.now().strftime(date_format)
            except ValueError:
                errors.append(f"Invalid date format: {date_format}")
        
        # Validate numeric limits
        if self.max_matches_per_day <= 0:
            errors.append("max_matches_per_day must be positive")
        
        if self.channel_retention_days <= 0:
            errors.append("channel_retention_days must be positive")
        
        if self.cache_duration_minutes <= 0:
            warnings.append("cache_duration_minutes should be positive for optimal performance")
        
        return len(errors) == 0, errors, warnings
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization"""
        return {
            "mcp_url": self.mcp_url,
            "auth_key": self.auth_key,
            "default_date_format": self.default_date_format,
            "supported_date_formats": self.supported_date_formats,
            "max_matches_per_day": self.max_matches_per_day,
            "channel_retention_days": self.channel_retention_days,
            "enable_standings": self.enable_standings,
            "enable_h2h_analysis": self.enable_h2h_analysis,
            "enable_betting_recommendations": self.enable_betting_recommendations,
            "max_leagues_per_request": self.max_leagues_per_request,
            "cache_duration_minutes": self.cache_duration_minutes,
            "rate_limiting": self.rate_limiting.to_dict(),
            "error_handling": self.error_handling.to_dict(),
            "leagues": {code: config.to_dict() for code, config in self.leagues.items()},
            "priority_leagues": self.priority_leagues
        }

class SoccerConfigManager:
    """Manager for soccer configuration with environment validation"""
    
    def __init__(self):
        self.config: Optional[SoccerConfiguration] = None
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from environment variables"""
        try:
            # Load basic configuration from environment
            mcp_url = os.getenv('SOCCER_MCP_URL', 'https://soccermcp-production.up.railway.app/mcp')
            auth_key = os.getenv('AUTH_KEY')
            
            # Create configuration with environment values
            self.config = SoccerConfiguration(
                mcp_url=mcp_url,
                auth_key=auth_key
            )
            
            # Load any custom league configurations from environment
            self._load_custom_league_configs()
            
            logger.info("Soccer configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load soccer configuration: {e}")
            # Create minimal fallback configuration
            self.config = SoccerConfiguration(
                mcp_url='https://soccermcp-production.up.railway.app/mcp'
            )
    
    def _load_custom_league_configs(self):
        """Load custom league configurations from environment"""
        # Check for custom league configuration JSON
        custom_leagues_json = os.getenv('SOCCER_LEAGUES_CONFIG')
        if custom_leagues_json:
            try:
                custom_leagues = json.loads(custom_leagues_json)
                for league_code, league_data in custom_leagues.items():
                    if league_code in self.config.leagues:
                        # Update existing league configuration
                        existing_config = self.config.leagues[league_code]
                        for key, value in league_data.items():
                            if hasattr(existing_config, key):
                                setattr(existing_config, key, value)
                    else:
                        # Add new league configuration
                        self.config.leagues[league_code] = SoccerLeagueConfig(**league_data)
                
                logger.info(f"Loaded custom configurations for {len(custom_leagues)} leagues")
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in SOCCER_LEAGUES_CONFIG: {e}")
            except Exception as e:
                logger.error(f"Error loading custom league configurations: {e}")
    
    def validate_environment(self) -> Dict[str, Any]:
        """
        Validate environment variables and configuration
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "missing_optional": []
        }
        
        # Required environment variables
        required_vars = {
            "DISCORD_BOT_TOKEN": "Discord bot token for authentication"
        }
        
        # Optional environment variables
        optional_vars = {
            "SOCCER_MCP_URL": "URL for Soccer MCP server",
            "AUTH_KEY": "Authentication key for Soccer MCP server",
            "SOCCER_LEAGUES_CONFIG": "Custom league configurations (JSON)"
        }
        
        # Check required variables
        for var_name, description in required_vars.items():
            value = os.getenv(var_name)
            if not value:
                validation_results["valid"] = False
                validation_results["errors"].append(
                    f"Missing required environment variable: {var_name} - {description}"
                )
        
        # Check optional variables
        for var_name, description in optional_vars.items():
            value = os.getenv(var_name)
            if not value:
                validation_results["missing_optional"].append(var_name)
        
        # Validate soccer configuration if loaded
        if self.config:
            is_valid, errors, warnings = self.config.validate()
            if not is_valid:
                validation_results["valid"] = False
                validation_results["errors"].extend(errors)
            validation_results["warnings"].extend(warnings)
        
        return validation_results
    
    def get_config(self) -> SoccerConfiguration:
        """Get the current soccer configuration"""
        if not self.config:
            self._load_configuration()
        return self.config
    
    def reload_config(self):
        """Reload configuration from environment"""
        self._load_configuration()
    
    def export_config(self, file_path: str):
        """Export current configuration to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=2)
            logger.info(f"Configuration exported to {file_path}")
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
    
    def perform_startup_checks(self) -> bool:
        """
        Perform comprehensive startup checks
        
        Returns:
            True if all critical checks pass, False otherwise
        """
        logger.info("Performing soccer configuration startup checks...")
        
        # Validate environment
        env_validation = self.validate_environment()
        
        if not env_validation["valid"]:
            logger.error("Soccer configuration validation failed:")
            for error in env_validation["errors"]:
                logger.error(f"  - {error}")
            return False
        
        # Log warnings
        for warning in env_validation["warnings"]:
            logger.warning(warning)
        
        # Log missing optional variables
        if env_validation["missing_optional"]:
            logger.info(f"Optional environment variables not set: {', '.join(env_validation['missing_optional'])}")
        
        # Test MCP connection if possible
        if self.config and self.config.mcp_url:
            logger.info(f"Soccer MCP URL configured: {self.config.mcp_url}")
            if self.config.auth_key:
                logger.info("Soccer MCP authentication key provided")
            else:
                logger.warning("No Soccer MCP authentication key - some features may be limited")
        
        # Log active leagues
        active_leagues = self.config.get_active_leagues() if self.config else []
        if active_leagues:
            logger.info(f"Active soccer leagues: {', '.join(active_leagues)}")
        else:
            logger.warning("No active soccer leagues configured")
        
        logger.info("Soccer configuration startup checks completed successfully")
        return True

# Global configuration manager instance
soccer_config_manager = SoccerConfigManager()

# Convenience functions for accessing configuration
def get_soccer_config() -> SoccerConfiguration:
    """Get the current soccer configuration"""
    return soccer_config_manager.get_config()

def get_active_soccer_leagues() -> List[str]:
    """Get list of active soccer leagues"""
    config = get_soccer_config()
    return config.get_active_leagues()

def get_soccer_league_config(league_code: str) -> Optional[SoccerLeagueConfig]:
    """Get configuration for a specific soccer league"""
    config = get_soccer_config()
    return config.get_league_config(league_code)

def validate_soccer_environment() -> Dict[str, Any]:
    """Validate soccer environment configuration"""
    return soccer_config_manager.validate_environment()

def perform_soccer_startup_checks() -> bool:
    """Perform soccer configuration startup checks"""
    return soccer_config_manager.perform_startup_checks()