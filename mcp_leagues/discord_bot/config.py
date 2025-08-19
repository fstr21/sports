"""
Configuration management for the Discord Sports Bot
"""
import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class SportConfig:
    """Configuration for a specific sport"""
    name: str
    mcp_url: str
    category_name: str
    category_id: Optional[int] = None
    embed_color: int = 0x00ff00
    date_format: str = "%Y-%m-%d"


class BotConfig:
    """Main bot configuration"""
    
    def __init__(self):
        self.discord_token = os.getenv("DISCORD_TOKEN", "").strip()
        self.sports = self._load_sports_config()
        
        if not self.discord_token:
            raise ValueError("DISCORD_TOKEN environment variable is required")
    
    def _load_sports_config(self) -> Dict[str, SportConfig]:
        """Load sports configurations from environment variables"""
        sports = {}
        
        # Soccer configuration
        if os.getenv("SOCCER_MCP_URL"):
            sports["soccer"] = SportConfig(
                name="soccer",
                mcp_url=os.getenv("SOCCER_MCP_URL"),
                category_name=os.getenv("SOCCER_CATEGORY_NAME", "SOCCER GAMES"),
                category_id=self._parse_int_env("SOCCER_CATEGORY_ID", 1407474278374576178),
                embed_color=0x00ff00,
                date_format="%d-%m-%Y"  # Soccer uses DD-MM-YYYY
            )
        
        # MLB configuration
        if os.getenv("MLB_MCP_URL"):
            sports["mlb"] = SportConfig(
                name="mlb",
                mcp_url=os.getenv("MLB_MCP_URL"),
                category_name=os.getenv("MLB_CATEGORY_NAME", "MLB GAMES"),
                category_id=self._parse_int_env("MLB_CATEGORY_ID"),
                embed_color=0x0066cc,
                date_format="%Y-%m-%d"  # MLB uses YYYY-MM-DD
            )
        
        return sports
    
    def _parse_int_env(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """Parse integer from environment variable"""
        value = os.getenv(key)
        if value:
            try:
                return int(value)
            except ValueError:
                logger.warning(f"Invalid integer value for {key}: {value}")
        return default
    
    def get_sport_config(self, sport_name: str) -> Optional[SportConfig]:
        """Get configuration for a specific sport"""
        return self.sports.get(sport_name.lower())
    
    def get_enabled_sports(self) -> list:
        """Get list of enabled sport names"""
        return list(self.sports.keys())


# Global configuration instance
config = BotConfig()