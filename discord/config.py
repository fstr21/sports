# Discord Bot Configuration
"""
Configuration settings for Sports Betting Discord Bot
"""

import os
from typing import Dict, List

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
        "active": True,  # EPL/La Liga active
        "category_name": "⚽ SOCCER",
        "channels_per_day": 10,
        "leagues": ["Premier League", "La Liga"],
        "season_start": "2025-08-15",
        "season_end": "2026-05-25"
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

# MCP Server URLs (from your existing infrastructure)
MCP_SERVERS = {
    "MLB": "https://mlbmcp-production.up.railway.app/mcp",
    "SOCCER": "https://soccermcp-production.up.railway.app/mcp", 
    "CFB": "https://cfbmcp-production.up.railway.app/mcp",
    "ODDS": "https://odds-mcp-v2-production.up.railway.app/mcp",
    "ESPN_PLAYERS": "TBD"  # Your planned ESPN Player ID MCP
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

# Feature Flags (for gradual rollout)
FEATURES = {
    "live_updates": False,       # Live game tracking
    "player_props": True,        # Player prop betting
    "ai_analysis": True,         # AI predictions
    "weather_integration": True, # Weather data
    "auto_channels": False,      # Automatic channel creation
    "subscription_system": False # Payment integration
}