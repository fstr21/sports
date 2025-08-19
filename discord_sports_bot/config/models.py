"""
Configuration data models and validation
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import os


@dataclass
class SportConfig:
    """Configuration for a specific sport"""
    name: str
    mcp_url: str
    category_name: str
    category_id: Optional[int] = None
    embed_color: int = 0x00ff00
    date_format: str = "%Y-%m-%d"
    default_league_id: Optional[int] = None
    max_channels_per_operation: int = 20
    channel_creation_delay: float = 1.0
    additional_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.mcp_url:
            raise ValueError(f"MCP URL is required for sport {self.name}")
        if not self.category_name:
            raise ValueError(f"Category name is required for sport {self.name}")


@dataclass
class FormattingConfig:
    """Configuration for message formatting"""
    embed_colors: Dict[str, int] = field(default_factory=lambda: {
        'soccer': 0x00ff00,
        'mlb': 0x0066cc,
        'nfl': 0xff6600,
        'nba': 0xcc0000,
        'default': 0x7289da
    })
    max_embed_fields: int = 25
    max_field_value_length: int = 1024
    use_thumbnails: bool = True
    show_timestamps: bool = True


@dataclass
class DiscordConfig:
    """Discord bot configuration"""
    token: str
    sync_permissions: List[str] = field(default_factory=lambda: ["manage_channels"])
    command_prefix: Optional[str] = None
    activity_name: Optional[str] = "Sports Analysis"
    activity_type: str = "watching"  # watching, playing, listening, streaming
    
    def __post_init__(self):
        """Validate Discord configuration"""
        if not self.token:
            raise ValueError("Discord token is required")


@dataclass
class MCPConfig:
    """MCP client configuration"""
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    connection_pool_size: int = 10
    max_connections: int = 20


@dataclass
class BotConfig:
    """Main bot configuration containing all settings"""
    discord: DiscordConfig
    sports: Dict[str, SportConfig]
    formatting: FormattingConfig = field(default_factory=FormattingConfig)
    mcp: MCPConfig = field(default_factory=MCPConfig)
    debug: bool = False
    log_level: str = "INFO"
    
    def get_sport_config(self, sport_name: str) -> Optional[SportConfig]:
        """Get configuration for a specific sport"""
        return self.sports.get(sport_name.lower())
    
    def get_enabled_sports(self) -> List[str]:
        """Get list of enabled sport names"""
        return list(self.sports.keys())
    
    def validate(self) -> List[str]:
        """
        Validate entire configuration
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate Discord config
        try:
            if not self.discord.token:
                errors.append("Discord token is missing")
        except Exception as e:
            errors.append(f"Discord config error: {e}")
        
        # Validate sports configs
        if not self.sports:
            errors.append("No sports configured")
        
        for sport_name, sport_config in self.sports.items():
            try:
                if not sport_config.mcp_url:
                    errors.append(f"MCP URL missing for sport: {sport_name}")
                if not sport_config.category_name:
                    errors.append(f"Category name missing for sport: {sport_name}")
            except Exception as e:
                errors.append(f"Sport config error for {sport_name}: {e}")
        
        return errors