# Discord Bot Configuration
"""
Configuration settings for Sports Betting Discord Bot
Enhanced with comprehensive soccer integration support
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

# Bot Settings
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', 'your-bot-token-here')
COMMAND_PREFIX = '/'
BOT_DESCRIPTION = "Sports Betting Analytics Bot with MCP Integration"

# Server Structure Configuration
LEAGUE_CONFIG = {
    "NFL": {
        "emoji": "🏈",
        "active": False,  # Season starts September
        "category_name": "🏈 NFL",
        "channels_per_week": 16,
        "season_start": "2025-09-05",
        "season_end": "2026-02-15"
    },
    "MLB": {
        "emoji": "⚾",
        "active": True,  # Currently active
        "category_name": "⚾ MLB", 
        "channels_per_day": 15,
        "season_start": "2025-03-20",
        "season_end": "2025-10-31"
    },
    "SOCCER": {
        "emoji": "⚽",
        "active": True,
        "category_name": "⚽ SOCCER",
        "channels_per_day": 15,  # Increased for multi-league support
        "season_start": "2025-08-15",
        "season_end": "2026-05-25",
        "supported_leagues": {
            "EPL": {
                "id": 228,
                "name": "Premier League",
                "country": "England",
                "priority": 1,
                "active": True,
                "color": 0x3d195b,
                "season_format": "2025-26",
                "tournament_type": "league"
            },
            "La Liga": {
                "id": 297,
                "name": "La Liga",
                "country": "Spain", 
                "priority": 2,
                "active": True,
                "color": 0xff6900,
                "season_format": "2025-26",
                "tournament_type": "league"
            },
            "MLS": {
                "id": 168,
                "name": "MLS",
                "country": "USA",
                "priority": 5,
                "active": True,
                "color": 0x005da6,
                "season_format": "2025",
                "tournament_type": "league"
            },
            "Bundesliga": {
                "id": 241,
                "name": "Bundesliga",
                "country": "Germany",
                "priority": 3,
                "active": True,
                "color": 0xd20515,
                "season_format": "2025-26",
                "tournament_type": "league"
            },
            "Serie A": {
                "id": 253,
                "name": "Serie A",
                "country": "Italy",
                "priority": 4,
                "active": True,
                "color": 0x0066cc,
                "season_format": "2025-26",
                "tournament_type": "league"
            },
            "UEFA": {
                "id": 310,
                "name": "UEFA Champions League",
                "country": "Europe",
                "priority": 0,  # Highest priority
                "active": True,
                "color": 0x00336a,
                "season_format": "2025-26",
                "tournament_type": "knockout"
            }
        },
        "priority_leagues": ["UEFA", "EPL", "La Liga", "Bundesliga", "Serie A", "MLS"],
        "default_leagues": ["EPL", "La Liga", "UEFA"]  # Default leagues for commands
    },
    "NBA": {
        "emoji": "🏀",
        "active": False,  # Season starts October
        "category_name": "🏀 NBA",
        "channels_per_day": 12,
        "season_start": "2025-10-15",
        "season_end": "2026-06-20"
    },
    "NHL": {
        "emoji": "🏒",
        "active": False,  # Season starts October
        "category_name": "🏒 NHL",
        "channels_per_day": 12,
        "season_start": "2025-10-10",
        "season_end": "2026-06-30"
    },
    "CFB": {
        "emoji": "🏈",
        "active": False,  # Season starts late August
        "category_name": "🏈 COLLEGE FOOTBALL",
        "channels_per_day": 20,
        "season_start": "2025-08-23",
        "season_end": "2026-01-15"
    }
}

# Channel Management
CHANNEL_CLEANUP_DAYS = 3  # Delete game channels after 3 days
MAX_CHANNELS_PER_CATEGORY = 50  # Discord limit consideration
CHANNEL_NAME_FORMAT = "📊 {team1}-vs-{team2}"

# Embed Colors (hex)
COLORS = {
    "default": 0x0099ff,
    "success": 0x00ff00,
    "error": 0xff0000,
    "warning": 0xffd700,
    "info": 0x0099ff,
    "betting": 0xffd700,
    "analysis": 0x9932cc
}

# Command Categories
GLOBAL_COMMANDS = [
    "schedule",  # Show games for league/date
    "odds",      # Betting odds for matchup
    "player",    # Player stats and history
    "weather",   # Weather conditions
    "bankroll",  # Bankroll management
    "help"       # Command reference
]

CHANNEL_COMMANDS = [
    "gameinfo",   # Detailed matchup analysis
    "props",      # Player props for this game
    "prediction", # AI analysis
    "lineup",     # Starting lineups
    "history",    # Head-to-head data
    "live"        # Real-time updates
]

ADMIN_COMMANDS = [
    "setup",      # Create game channels
    "cleanup",    # Remove old channels
    "toggle",     # Enable/disable leagues
    "broadcast"   # Send message to all channels
]

# MCP Server Configuration
@dataclass
class MCPServerConfig:
    """Configuration for MCP server connections"""
    url: str
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit_requests: int = 60
    rate_limit_window: int = 60  # seconds
    auth_required: bool = False

# MCP Server URLs and configurations
MCP_SERVERS = {
    "MLB": MCPServerConfig(
        url="https://mlbmcp-production.up.railway.app/mcp",
        timeout=30,
        max_retries=3,
        rate_limit_requests=100
    ),
    "SOCCER": MCPServerConfig(
        url=os.getenv('SOCCER_MCP_URL', 'https://soccermcp-production.up.railway.app/mcp'),
        timeout=45,  # Soccer data can be more complex
        max_retries=3,
        rate_limit_requests=120,  # Higher limit for multi-league support
        auth_required=bool(os.getenv('AUTH_KEY'))
    ),
    "CFB": MCPServerConfig(
        url="https://cfbmcp-production.up.railway.app/mcp",
        timeout=30,
        max_retries=3,
        rate_limit_requests=80
    ),
    "ODDS": MCPServerConfig(
        url="https://odds-mcp-v2-production.up.railway.app/mcp",
        timeout=20,
        max_retries=2,
        rate_limit_requests=50
    ),
    "ESPN_PLAYERS": MCPServerConfig(
        url="TBD",  # Your planned ESPN Player ID MCP
        timeout=25,
        max_retries=3,
        rate_limit_requests=60
    )
}

# Subscription Tiers (for future implementation)
SUBSCRIPTION_TIERS = {
    "FREE": {
        "daily_commands": 10,
        "features": ["basic_schedule", "basic_odds"],
        "analysis_depth": "basic"
    },
    "PREMIUM": {
        "daily_commands": 100,
        "features": ["advanced_analysis", "player_props", "ai_predictions"],
        "analysis_depth": "detailed",
        "price_monthly": 19.99
    },
    "PRO": {
        "daily_commands": 500,
        "features": ["all_features", "priority_support", "custom_alerts"],
        "analysis_depth": "comprehensive",
        "price_monthly": 49.99
    }
}

# Rate Limiting
RATE_LIMITS = {
    "commands_per_minute": 5,
    "commands_per_hour": 50,
    "commands_per_day": 200
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "discord_bot.log",
    "max_size": "10MB",
    "backup_count": 5
}

# Error Messages
ERROR_MESSAGES = {
    "no_permission": "❌ You don't have permission to use this command.",
    "rate_limited": "⏱️ You're sending commands too quickly. Please wait.",
    "invalid_league": "❌ Invalid league. Available: NFL, MLB, SOCCER, NBA, NHL, CFB",
    "channel_creation_failed": "❌ Failed to create game channel.",
    "mcp_unavailable": "⚠️ Sports data temporarily unavailable.",
    "unknown_error": "❌ An unexpected error occurred."
}

# Success Messages  
SUCCESS_MESSAGES = {
    "channel_created": "✅ Game channel created successfully!",
    "cleanup_complete": "🧹 Channel cleanup completed.",
    "settings_updated": "⚙️ Settings updated successfully."
}

# Soccer-Specific Configuration
SOCCER_CONFIG = {
    "mcp_url": os.getenv('SOCCER_MCP_URL', 'https://soccermcp-production.up.railway.app/mcp'),
    "auth_key": os.getenv('AUTH_KEY'),  # Required for Soccer MCP authentication
    "default_date_format": "%Y-%m-%d",  # Format expected by Soccer MCP
    "supported_date_formats": ["%m/%d/%Y", "%d-%m-%Y", "%Y-%m-%d"],
    "max_matches_per_day": 50,  # Limit to prevent spam
    "channel_retention_days": 3,
    "enable_standings": True,
    "enable_h2h_analysis": True,
    "enable_betting_recommendations": True,
    "max_leagues_per_request": 6,
    "cache_duration_minutes": 15,  # Cache match data for 15 minutes
    "embed_colors": {
        "EPL": 0x3d195b,
        "La Liga": 0xff6900,
        "MLS": 0x005da6,
        "Bundesliga": 0xd20515,
        "Serie A": 0x0066cc,
        "UEFA": 0x00336a,
        "default": 0x00ff00
    },
    "rate_limiting": {
        "requests_per_minute": 30,
        "requests_per_hour": 300,
        "burst_limit": 10,
        "cooldown_seconds": 2
    },
    "error_handling": {
        "max_retries": 3,
        "retry_delay_seconds": 2,
        "exponential_backoff": True,
        "fallback_to_cache": True,
        "graceful_degradation": True
    }
}

# Environment Variable Validation
REQUIRED_ENV_VARS = {
    "DISCORD_BOT_TOKEN": {
        "description": "Discord bot token for authentication",
        "required": True,
        "validation": lambda x: x and len(x) > 50
    },
    "SOCCER_MCP_URL": {
        "description": "URL for Soccer MCP server",
        "required": False,  # Has default
        "default": "https://soccermcp-production.up.railway.app/mcp",
        "validation": lambda x: x.startswith(('http://', 'https://'))
    },
    "AUTH_KEY": {
        "description": "Authentication key for Soccer MCP server",
        "required": False,  # Optional but recommended
        "validation": lambda x: not x or len(x) > 10
    }
}

# Feature Flags (for gradual rollout)
FEATURES = {
    "live_updates": False,       # Live game tracking
    "player_props": True,        # Player prop betting
    "ai_analysis": True,         # AI predictions
    "weather_integration": True, # Weather data
    "auto_channels": False,      # Automatic channel creation
    "subscription_system": False, # Payment integration
    "soccer_integration": True,  # Enable soccer functionality
    "multi_league_support": True, # Support multiple soccer leagues
    "h2h_analysis": True,        # Head-to-head analysis
    "betting_recommendations": True, # AI betting insights
    "league_standings": True,    # League table display
    "advanced_statistics": True, # Advanced match statistics
    "channel_auto_cleanup": True # Automatic channel cleanup
}

# Configuration Validation Functions
def validate_environment() -> Dict[str, Any]:
    """
    Validate all required environment variables and configuration
    
    Returns:
        Dictionary with validation results and any errors
    """
    validation_results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "missing_optional": []
    }
    
    # Check required environment variables
    for var_name, config in REQUIRED_ENV_VARS.items():
        value = os.getenv(var_name)
        
        if config["required"] and not value:
            validation_results["valid"] = False
            validation_results["errors"].append(
                f"Missing required environment variable: {var_name} - {config['description']}"
            )
        elif not value and "default" in config:
            validation_results["warnings"].append(
                f"Using default value for {var_name}: {config['default']}"
            )
        elif value and "validation" in config:
            try:
                if not config["validation"](value):
                    validation_results["valid"] = False
                    validation_results["errors"].append(
                        f"Invalid value for {var_name}: {config['description']}"
                    )
            except Exception as e:
                validation_results["valid"] = False
                validation_results["errors"].append(
                    f"Validation error for {var_name}: {str(e)}"
                )
        elif not value and not config["required"]:
            validation_results["missing_optional"].append(var_name)
    
    # Validate soccer-specific configuration
    if FEATURES["soccer_integration"]:
        soccer_validation = validate_soccer_config()
        if not soccer_validation["valid"]:
            validation_results["valid"] = False
            validation_results["errors"].extend(soccer_validation["errors"])
        validation_results["warnings"].extend(soccer_validation["warnings"])
    
    return validation_results

def validate_soccer_config() -> Dict[str, Any]:
    """
    Validate soccer-specific configuration
    
    Returns:
        Dictionary with soccer validation results
    """
    results = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Check Soccer MCP URL
    soccer_url = SOCCER_CONFIG["mcp_url"]
    if not soccer_url.startswith(('http://', 'https://')):
        results["valid"] = False
        results["errors"].append("Invalid Soccer MCP URL format")
    
    # Check AUTH_KEY if provided
    auth_key = SOCCER_CONFIG["auth_key"]
    if auth_key and len(auth_key) < 10:
        results["warnings"].append("AUTH_KEY seems too short, may be invalid")
    elif not auth_key:
        results["warnings"].append("No AUTH_KEY provided - some Soccer MCP features may be limited")
    
    # Validate league configurations
    soccer_leagues = LEAGUE_CONFIG["SOCCER"]["supported_leagues"]
    for league_code, league_config in soccer_leagues.items():
        if not all(key in league_config for key in ["id", "name", "country", "priority"]):
            results["valid"] = False
            results["errors"].append(f"Incomplete configuration for league: {league_code}")
    
    # Check rate limiting configuration
    rate_config = SOCCER_CONFIG["rate_limiting"]
    if rate_config["requests_per_minute"] > rate_config["requests_per_hour"]:
        results["warnings"].append("Rate limiting: requests_per_minute exceeds hourly average")
    
    return results

def get_active_soccer_leagues() -> List[str]:
    """
    Get list of currently active soccer leagues
    
    Returns:
        List of active league codes sorted by priority
    """
    if not FEATURES["soccer_integration"]:
        return []
    
    active_leagues = []
    soccer_leagues = LEAGUE_CONFIG["SOCCER"]["supported_leagues"]
    
    for league_code, league_config in soccer_leagues.items():
        if league_config.get("active", False):
            active_leagues.append(league_code)
    
    # Sort by priority (lower number = higher priority)
    priority_order = LEAGUE_CONFIG["SOCCER"]["priority_leagues"]
    active_leagues.sort(key=lambda x: priority_order.index(x) if x in priority_order else 999)
    
    return active_leagues

def get_soccer_league_config(league_code: str) -> Optional[Dict[str, Any]]:
    """
    Get configuration for a specific soccer league
    
    Args:
        league_code: League code (e.g., "EPL", "La Liga")
        
    Returns:
        League configuration dictionary or None if not found
    """
    soccer_leagues = LEAGUE_CONFIG["SOCCER"]["supported_leagues"]
    return soccer_leagues.get(league_code)

def is_feature_enabled(feature_name: str) -> bool:
    """
    Check if a specific feature is enabled
    
    Args:
        feature_name: Name of the feature to check
        
    Returns:
        True if feature is enabled, False otherwise
    """
    return FEATURES.get(feature_name, False)

# Startup Configuration Check
def perform_startup_checks() -> bool:
    """
    Perform comprehensive startup configuration checks
    
    Returns:
        True if all critical checks pass, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    logger.info("Performing startup configuration checks...")
    
    # Validate environment
    env_validation = validate_environment()
    
    if not env_validation["valid"]:
        logger.error("Environment validation failed:")
        for error in env_validation["errors"]:
            logger.error(f"  - {error}")
        return False
    
    # Log warnings
    for warning in env_validation["warnings"]:
        logger.warning(warning)
    
    # Log missing optional variables
    if env_validation["missing_optional"]:
        logger.info(f"Optional environment variables not set: {', '.join(env_validation['missing_optional'])}")
    
    # Check feature dependencies
    if FEATURES["soccer_integration"] and not FEATURES["multi_league_support"]:
        logger.warning("Soccer integration enabled but multi-league support disabled")
    
    if FEATURES["h2h_analysis"] and not FEATURES["soccer_integration"]:
        logger.warning("H2H analysis enabled but soccer integration disabled")
    
    logger.info("Startup configuration checks completed successfully")
    return True