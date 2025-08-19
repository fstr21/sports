"""
Configuration management system with environment variable support
"""
import os
import logging
from typing import Dict, Any, Optional
from .models import BotConfig, DiscordConfig, SportConfig, FormattingConfig, MCPConfig


logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Centralized configuration management with environment variable support
    and validation
    """
    
    def __init__(self):
        self._config: Optional[BotConfig] = None
        self._loaded = False
    
    def load_config(self) -> BotConfig:
        """
        Load configuration from environment variables and defaults
        
        Returns:
            BotConfig object with all settings
        """
        if self._loaded and self._config:
            return self._config
        
        logger.info("Loading bot configuration...")
        
        # Load Discord configuration
        discord_config = DiscordConfig(
            token=os.getenv("DISCORD_TOKEN", "").strip(),
            sync_permissions=self._parse_list_env("DISCORD_SYNC_PERMISSIONS", ["manage_channels"]),
            command_prefix=os.getenv("DISCORD_COMMAND_PREFIX"),
            activity_name=os.getenv("DISCORD_ACTIVITY_NAME", "Sports Analysis"),
            activity_type=os.getenv("DISCORD_ACTIVITY_TYPE", "watching")
        )
        
        # Load sports configurations
        sports_config = self._load_sports_config()
        
        # Load formatting configuration
        formatting_config = FormattingConfig(
            embed_colors=self._load_embed_colors(),
            max_embed_fields=int(os.getenv("FORMAT_MAX_EMBED_FIELDS", "25")),
            max_field_value_length=int(os.getenv("FORMAT_MAX_FIELD_VALUE_LENGTH", "1024")),
            use_thumbnails=os.getenv("FORMAT_USE_THUMBNAILS", "true").lower() == "true",
            show_timestamps=os.getenv("FORMAT_SHOW_TIMESTAMPS", "true").lower() == "true"
        )
        
        # Load MCP configuration
        mcp_config = MCPConfig(
            timeout=float(os.getenv("MCP_TIMEOUT", "30.0")),
            max_retries=int(os.getenv("MCP_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("MCP_RETRY_DELAY", "1.0")),
            connection_pool_size=int(os.getenv("MCP_CONNECTION_POOL_SIZE", "10")),
            max_connections=int(os.getenv("MCP_MAX_CONNECTIONS", "20"))
        )
        
        # Create main configuration
        self._config = BotConfig(
            discord=discord_config,
            sports=sports_config,
            formatting=formatting_config,
            mcp=mcp_config,
            debug=os.getenv("DEBUG", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO").upper()
        )
        
        # Validate configuration
        errors = self._config.validate()
        if errors:
            error_msg = "Configuration validation failed:\\n" + "\\n".join(errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self._loaded = True
        logger.info(f"Configuration loaded successfully. Enabled sports: {', '.join(self._config.get_enabled_sports())}")
        
        return self._config
    
    def _load_sports_config(self) -> Dict[str, SportConfig]:
        """Load sports configurations from environment variables"""
        sports = {}
        
        # Soccer configuration
        if os.getenv("SOCCER_MCP_URL"):
            sports["soccer"] = SportConfig(
                name="soccer",
                mcp_url=os.getenv("SOCCER_MCP_URL"),
                category_name=os.getenv("SOCCER_CATEGORY_NAME", "SOCCER GAMES"),
                category_id=self._parse_int_env("SOCCER_CATEGORY_ID"),
                embed_color=self._parse_hex_color("SOCCER_EMBED_COLOR", 0x00ff00),
                date_format=os.getenv("SOCCER_DATE_FORMAT", "%d-%m-%Y"),  # Soccer uses DD-MM-YYYY
                default_league_id=self._parse_int_env("SOCCER_DEFAULT_LEAGUE_ID", 297),
                max_channels_per_operation=int(os.getenv("SOCCER_MAX_CHANNELS", "20")),
                channel_creation_delay=float(os.getenv("SOCCER_CHANNEL_DELAY", "1.0"))
            )
        
        # MLB configuration
        if os.getenv("MLB_MCP_URL"):
            sports["mlb"] = SportConfig(
                name="mlb",
                mcp_url=os.getenv("MLB_MCP_URL"),
                category_name=os.getenv("MLB_CATEGORY_NAME", "MLB GAMES"),
                category_id=self._parse_int_env("MLB_CATEGORY_ID"),
                embed_color=self._parse_hex_color("MLB_EMBED_COLOR", 0x0066cc),
                date_format=os.getenv("MLB_DATE_FORMAT", "%Y-%m-%d"),  # MLB uses YYYY-MM-DD
                max_channels_per_operation=int(os.getenv("MLB_MAX_CHANNELS", "20")),
                channel_creation_delay=float(os.getenv("MLB_CHANNEL_DELAY", "1.0"))
            )
        
        # NFL configuration
        if os.getenv("NFL_MCP_URL"):
            sports["nfl"] = SportConfig(
                name="nfl",
                mcp_url=os.getenv("NFL_MCP_URL"),
                category_name=os.getenv("NFL_CATEGORY_NAME", "NFL GAMES"),
                category_id=self._parse_int_env("NFL_CATEGORY_ID"),
                embed_color=self._parse_hex_color("NFL_EMBED_COLOR", 0xff6600),
                date_format=os.getenv("NFL_DATE_FORMAT", "%Y-%m-%d"),
                max_channels_per_operation=int(os.getenv("NFL_MAX_CHANNELS", "20")),
                channel_creation_delay=float(os.getenv("NFL_CHANNEL_DELAY", "1.0"))
            )
        
        # NBA configuration
        if os.getenv("NBA_MCP_URL"):
            sports["nba"] = SportConfig(
                name="nba",
                mcp_url=os.getenv("NBA_MCP_URL"),
                category_name=os.getenv("NBA_CATEGORY_NAME", "NBA GAMES"),
                category_id=self._parse_int_env("NBA_CATEGORY_ID"),
                embed_color=self._parse_hex_color("NBA_EMBED_COLOR", 0xcc0000),
                date_format=os.getenv("NBA_DATE_FORMAT", "%Y-%m-%d"),
                max_channels_per_operation=int(os.getenv("NBA_MAX_CHANNELS", "20")),
                channel_creation_delay=float(os.getenv("NBA_CHANNEL_DELAY", "1.0"))
            )
        
        return sports
    
    def _load_embed_colors(self) -> Dict[str, int]:
        """Load embed colors from environment variables"""
        return {
            'soccer': self._parse_hex_color("SOCCER_EMBED_COLOR", 0x00ff00),
            'mlb': self._parse_hex_color("MLB_EMBED_COLOR", 0x0066cc),
            'nfl': self._parse_hex_color("NFL_EMBED_COLOR", 0xff6600),
            'nba': self._parse_hex_color("NBA_EMBED_COLOR", 0xcc0000),
            'default': self._parse_hex_color("DEFAULT_EMBED_COLOR", 0x7289da)
        }
    
    def _parse_int_env(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """Parse integer from environment variable"""
        value = os.getenv(key)
        if value:
            try:
                return int(value)
            except ValueError:
                logger.warning(f"Invalid integer value for {key}: {value}")
        return default
    
    def _parse_hex_color(self, key: str, default: int) -> int:
        """Parse hex color from environment variable"""
        value = os.getenv(key)
        if value:
            try:
                # Handle both 0x prefix and without
                if value.startswith('0x'):
                    return int(value, 16)
                else:
                    return int(value, 16)
            except ValueError:
                logger.warning(f"Invalid hex color for {key}: {value}")
        return default
    
    def _parse_list_env(self, key: str, default: list) -> list:
        """Parse comma-separated list from environment variable"""
        value = os.getenv(key)
        if value:
            return [item.strip() for item in value.split(',') if item.strip()]
        return default
    
    def get_config(self) -> Optional[BotConfig]:
        """Get current configuration (may be None if not loaded)"""
        return self._config
    
    def reload_config(self) -> BotConfig:
        """Force reload configuration from environment"""
        self._loaded = False
        self._config = None
        return self.load_config()


# Global configuration manager instance
config_manager = ConfigManager()