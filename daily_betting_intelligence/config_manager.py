"""
Configuration management for the Daily Betting Intelligence system.

This module handles system configuration, league mappings, market selections,
and provides default settings for all system components.
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


# Default system configuration
DEFAULT_CONFIG = {
    "leagues": [
        "nfl", "nba", "wnba", "mlb", "nhl", 
        "mls", "epl", "laliga", "ncaaf", "ncaab"
    ],
    "betting_markets": ["h2h", "spreads", "totals"],
    "player_prop_markets": [
        "player_points", "player_rebounds", "player_assists",
        "player_steals", "player_blocks", "player_threes"
    ],
    "timezone": "US/Eastern",
    "timeout_seconds": 30,
    "max_concurrent_requests": 5,
    "confidence_threshold": 0.7,
    "retry_attempts": 3,
    "retry_delay_seconds": 2,
    "cache_duration_minutes": 5,
    "report_output_format": "markdown",
    "include_player_props": True,
    "include_llm_analysis": True,
    "min_odds_threshold": -300,  # Don't show heavily favored bets
    "max_odds_threshold": 500,   # Don't show extremely long shots
}

# League display names and configurations
LEAGUE_CONFIG = {
    "nfl": {
        "display_name": "NFL",
        "full_name": "National Football League",
        "season_type": "regular",
        "primary_markets": ["h2h", "spreads", "totals"],
        "key_player_props": ["player_passing_yards", "player_rushing_yards", "player_receiving_yards"]
    },
    "nba": {
        "display_name": "NBA", 
        "full_name": "National Basketball Association",
        "season_type": "regular",
        "primary_markets": ["h2h", "spreads", "totals"],
        "key_player_props": ["player_points", "player_rebounds", "player_assists"]
    },
    "wnba": {
        "display_name": "WNBA",
        "full_name": "Women's National Basketball Association", 
        "season_type": "regular",
        "primary_markets": ["h2h", "spreads", "totals"],
        "key_player_props": ["player_points", "player_rebounds", "player_assists"]
    },
    "mlb": {
        "display_name": "MLB",
        "full_name": "Major League Baseball",
        "season_type": "regular", 
        "primary_markets": ["h2h", "spreads", "totals"],
        "key_player_props": ["player_hits", "player_runs", "player_rbis"]
    },
    "nhl": {
        "display_name": "NHL",
        "full_name": "National Hockey League",
        "season_type": "regular",
        "primary_markets": ["h2h", "spreads", "totals"], 
        "key_player_props": ["player_goals", "player_assists", "player_shots"]
    },
    "mls": {
        "display_name": "MLS",
        "full_name": "Major League Soccer",
        "season_type": "regular",
        "primary_markets": ["h2h", "spreads", "totals"],
        "key_player_props": ["player_goals", "player_assists", "player_shots"]
    },
    "epl": {
        "display_name": "EPL", 
        "full_name": "English Premier League",
        "season_type": "regular",
        "primary_markets": ["h2h", "spreads", "totals"],
        "key_player_props": ["player_goals", "player_assists", "player_shots"]
    },
    "laliga": {
        "display_name": "La Liga",
        "full_name": "Spanish La Liga",
        "season_type": "regular", 
        "primary_markets": ["h2h", "spreads", "totals"],
        "key_player_props": ["player_goals", "player_assists", "player_shots"]
    },
    "ncaaf": {
        "display_name": "NCAAF",
        "full_name": "NCAA Football",
        "season_type": "regular",
        "primary_markets": ["h2h", "spreads", "totals"],
        "key_player_props": ["player_passing_yards", "player_rushing_yards"]
    },
    "ncaab": {
        "display_name": "NCAAB", 
        "full_name": "NCAA Basketball",
        "season_type": "regular",
        "primary_markets": ["h2h", "spreads", "totals"],
        "key_player_props": ["player_points", "player_rebounds", "player_assists"]
    }
}

# Betting market configurations
BETTING_MARKETS_CONFIG = {
    "h2h": {
        "display_name": "Moneyline",
        "description": "Straight win/loss betting",
        "priority": 1
    },
    "spreads": {
        "display_name": "Point Spread", 
        "description": "Betting against the spread",
        "priority": 2
    },
    "totals": {
        "display_name": "Over/Under",
        "description": "Total points/goals scored",
        "priority": 3
    }
}


@dataclass
class SystemConfig:
    """System configuration data structure."""
    leagues: List[str] = field(default_factory=lambda: DEFAULT_CONFIG["leagues"].copy())
    betting_markets: List[str] = field(default_factory=lambda: DEFAULT_CONFIG["betting_markets"].copy())
    player_prop_markets: List[str] = field(default_factory=lambda: DEFAULT_CONFIG["player_prop_markets"].copy())
    timezone: str = DEFAULT_CONFIG["timezone"]
    timeout_seconds: int = DEFAULT_CONFIG["timeout_seconds"]
    max_concurrent_requests: int = DEFAULT_CONFIG["max_concurrent_requests"]
    confidence_threshold: float = DEFAULT_CONFIG["confidence_threshold"]
    retry_attempts: int = DEFAULT_CONFIG["retry_attempts"]
    retry_delay_seconds: int = DEFAULT_CONFIG["retry_delay_seconds"]
    cache_duration_minutes: int = DEFAULT_CONFIG["cache_duration_minutes"]
    report_output_format: str = DEFAULT_CONFIG["report_output_format"]
    include_player_props: bool = DEFAULT_CONFIG["include_player_props"]
    include_llm_analysis: bool = DEFAULT_CONFIG["include_llm_analysis"]
    min_odds_threshold: int = DEFAULT_CONFIG["min_odds_threshold"]
    max_odds_threshold: int = DEFAULT_CONFIG["max_odds_threshold"]


class ConfigManager:
    """Manages system configuration with support for environment variables and config files."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_file: Optional path to JSON configuration file
        """
        self.config = SystemConfig()
        self.config_file = config_file
        self._load_configuration()
    
    def _load_configuration(self) -> None:
        """Load configuration from file and environment variables."""
        # Load from config file if provided
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                self._update_config_from_dict(file_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
        
        # Override with environment variables
        self._load_from_environment()
    
    def _update_config_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        for key, value in config_dict.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def _load_from_environment(self) -> None:
        """Load configuration overrides from environment variables."""
        env_mappings = {
            "DBI_TIMEZONE": "timezone",
            "DBI_TIMEOUT_SECONDS": ("timeout_seconds", int),
            "DBI_MAX_CONCURRENT": ("max_concurrent_requests", int),
            "DBI_CONFIDENCE_THRESHOLD": ("confidence_threshold", float),
            "DBI_RETRY_ATTEMPTS": ("retry_attempts", int),
            "DBI_RETRY_DELAY": ("retry_delay_seconds", int),
            "DBI_CACHE_DURATION": ("cache_duration_minutes", int),
            "DBI_OUTPUT_FORMAT": "report_output_format",
            "DBI_INCLUDE_PROPS": ("include_player_props", lambda x: x.lower() == 'true'),
            "DBI_INCLUDE_LLM": ("include_llm_analysis", lambda x: x.lower() == 'true'),
            "DBI_MIN_ODDS": ("min_odds_threshold", int),
            "DBI_MAX_ODDS": ("max_odds_threshold", int),
        }
        
        for env_var, config_mapping in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                if isinstance(config_mapping, tuple):
                    attr_name, converter = config_mapping
                    try:
                        converted_value = converter(env_value)
                        setattr(self.config, attr_name, converted_value)
                    except (ValueError, TypeError) as e:
                        print(f"Warning: Invalid value for {env_var}: {env_value} ({e})")
                else:
                    setattr(self.config, config_mapping, env_value)
        
        # Handle list-based environment variables
        leagues_env = os.getenv("DBI_LEAGUES")
        if leagues_env:
            self.config.leagues = [league.strip() for league in leagues_env.split(",")]
        
        markets_env = os.getenv("DBI_BETTING_MARKETS") 
        if markets_env:
            self.config.betting_markets = [market.strip() for market in markets_env.split(",")]
    
    def get_league_config(self, league: str) -> Dict[str, Any]:
        """Get configuration for a specific league.
        
        Args:
            league: League identifier
            
        Returns:
            League configuration dictionary
        """
        return LEAGUE_CONFIG.get(league, {
            "display_name": league.upper(),
            "full_name": f"Unknown League ({league})",
            "season_type": "regular",
            "primary_markets": ["h2h", "spreads", "totals"],
            "key_player_props": []
        })
    
    def get_market_config(self, market: str) -> Dict[str, Any]:
        """Get configuration for a specific betting market.
        
        Args:
            market: Market identifier
            
        Returns:
            Market configuration dictionary
        """
        return BETTING_MARKETS_CONFIG.get(market, {
            "display_name": market.title(),
            "description": f"Unknown market ({market})",
            "priority": 999
        })
    
    def validate_leagues(self, leagues: List[str]) -> List[str]:
        """Validate and filter league list against supported leagues.
        
        Args:
            leagues: List of league identifiers to validate
            
        Returns:
            List of valid league identifiers
        """
        valid_leagues = []
        for league in leagues:
            if league in LEAGUE_CONFIG:
                valid_leagues.append(league)
            else:
                print(f"Warning: Unsupported league '{league}' will be skipped")
        return valid_leagues
    
    def validate_markets(self, markets: List[str]) -> List[str]:
        """Validate and filter betting markets against supported markets.
        
        Args:
            markets: List of market identifiers to validate
            
        Returns:
            List of valid market identifiers
        """
        valid_markets = []
        for market in markets:
            if market in BETTING_MARKETS_CONFIG:
                valid_markets.append(market)
            else:
                print(f"Warning: Unsupported market '{market}' will be skipped")
        return valid_markets
    
    def save_config(self, filepath: str) -> None:
        """Save current configuration to file.
        
        Args:
            filepath: Path to save configuration file
        """
        config_dict = {
            "leagues": self.config.leagues,
            "betting_markets": self.config.betting_markets,
            "player_prop_markets": self.config.player_prop_markets,
            "timezone": self.config.timezone,
            "timeout_seconds": self.config.timeout_seconds,
            "max_concurrent_requests": self.config.max_concurrent_requests,
            "confidence_threshold": self.config.confidence_threshold,
            "retry_attempts": self.config.retry_attempts,
            "retry_delay_seconds": self.config.retry_delay_seconds,
            "cache_duration_minutes": self.config.cache_duration_minutes,
            "report_output_format": self.config.report_output_format,
            "include_player_props": self.config.include_player_props,
            "include_llm_analysis": self.config.include_llm_analysis,
            "min_odds_threshold": self.config.min_odds_threshold,
            "max_odds_threshold": self.config.max_odds_threshold,
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(config_dict, f, indent=2)
        except IOError as e:
            raise RuntimeError(f"Could not save configuration to {filepath}: {e}")
    
    def get_config(self) -> SystemConfig:
        """Get current system configuration.
        
        Returns:
            Current SystemConfig instance
        """
        return self.config