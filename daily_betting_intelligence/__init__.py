"""
Daily Betting Intelligence Report System

A comprehensive system for generating automated daily betting analysis reports
that combines sports data from ESPN MCP, betting odds from Wagyu MCP, and
AI-powered analysis from OpenRouter LLM.
"""

__version__ = "1.0.0"
__author__ = "Sports AI Team"

# Core data models
from .models import (
    GameData, TeamStats, BettingOdds, PlayerProp, 
    GameAnalysis, PlayerAnalysis, ReportData, ErrorReport
)

# Configuration management
from .config_manager import ConfigManager, SystemConfig, DEFAULT_CONFIG, LEAGUE_CONFIG

# Base interfaces
from .interfaces import (
    DataFetcher, OddsProvider, GameAnalyzer, ReportFormatter,
    ErrorHandler, CacheManager, DataOrchestrator, ReportGenerator
)

# Utilities and exceptions
from .utils import (
    validate_date_format, convert_to_eastern_time, parse_date_string,
    format_odds, calculate_implied_probability, find_best_odds
)
from .exceptions import (
    DailyBettingIntelligenceError, DataFetchError, MCPServerError,
    ESPNMCPError, WagyuMCPError, AnalysisError, LLMAnalysisError,
    ConfigurationError, ValidationError, ReportGenerationError
)

__all__ = [
    # Data models
    "GameData", "TeamStats", "BettingOdds", "PlayerProp",
    "GameAnalysis", "PlayerAnalysis", "ReportData", "ErrorReport",
    
    # Configuration
    "ConfigManager", "SystemConfig", "DEFAULT_CONFIG", "LEAGUE_CONFIG",
    
    # Interfaces
    "DataFetcher", "OddsProvider", "GameAnalyzer", "ReportFormatter",
    "ErrorHandler", "CacheManager", "DataOrchestrator", "ReportGenerator",
    
    # Utilities
    "validate_date_format", "convert_to_eastern_time", "parse_date_string",
    "format_odds", "calculate_implied_probability", "find_best_odds",
    
    # Exceptions
    "DailyBettingIntelligenceError", "DataFetchError", "MCPServerError",
    "ESPNMCPError", "WagyuMCPError", "AnalysisError", "LLMAnalysisError",
    "ConfigurationError", "ValidationError", "ReportGenerationError"
]