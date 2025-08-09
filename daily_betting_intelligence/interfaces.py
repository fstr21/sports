"""
Base interfaces and abstract classes for the Daily Betting Intelligence system.

This module defines the contracts that all system components must implement,
ensuring consistent behavior and enabling dependency injection for testing.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

from .models import (
    GameData, TeamStats, BettingOdds, PlayerProp, 
    GameAnalysis, PlayerAnalysis, ReportData, ErrorReport
)


class DataFetcher(ABC):
    """Abstract base class for data fetching components."""
    
    @abstractmethod
    async def fetch_games_for_date(self, date: str, league: str) -> List[GameData]:
        """Fetch games for a specific date and league.
        
        Args:
            date: Target date in YYYY-MM-DD format
            league: League identifier
            
        Returns:
            List of GameData objects
        """
        pass
    
    @abstractmethod
    async def fetch_team_stats(self, team_name: str, league: str) -> Optional[TeamStats]:
        """Fetch team statistics and performance data.
        
        Args:
            team_name: Name of the team
            league: League identifier
            
        Returns:
            TeamStats object or None if not found
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the data source is available.
        
        Returns:
            True if data source is accessible, False otherwise
        """
        pass


class OddsProvider(ABC):
    """Abstract base class for betting odds providers."""
    
    @abstractmethod
    async def fetch_game_odds(self, event_id: str, markets: List[str]) -> List[BettingOdds]:
        """Fetch betting odds for a specific game.
        
        Args:
            event_id: Unique game identifier
            markets: List of betting markets to fetch
            
        Returns:
            List of BettingOdds objects from different sportsbooks
        """
        pass
    
    @abstractmethod
    async def fetch_player_props(self, event_id: str, prop_types: List[str]) -> List[PlayerProp]:
        """Fetch player proposition bets for a game.
        
        Args:
            event_id: Unique game identifier
            prop_types: List of prop types to fetch
            
        Returns:
            List of PlayerProp objects
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the odds provider is available.
        
        Returns:
            True if provider is accessible, False otherwise
        """
        pass


class GameAnalyzer(ABC):
    """Abstract base class for game analysis components."""
    
    @abstractmethod
    async def analyze_game(
        self, 
        game_data: GameData, 
        team_stats: Dict[str, TeamStats],
        odds_data: List[BettingOdds]
    ) -> GameAnalysis:
        """Analyze a game and generate predictions.
        
        Args:
            game_data: Game information
            team_stats: Team statistics for both teams
            odds_data: Betting odds from various sportsbooks
            
        Returns:
            GameAnalysis object with predictions and recommendations
        """
        pass
    
    @abstractmethod
    async def analyze_players(
        self,
        game_data: GameData,
        team_stats: Dict[str, TeamStats], 
        player_props: List[PlayerProp]
    ) -> List[PlayerAnalysis]:
        """Analyze key players and their prop betting opportunities.
        
        Args:
            game_data: Game information
            team_stats: Team statistics for both teams
            player_props: Available player proposition bets
            
        Returns:
            List of PlayerAnalysis objects for key players
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the analyzer is available.
        
        Returns:
            True if analyzer is accessible, False otherwise
        """
        pass


class ReportFormatter(ABC):
    """Abstract base class for report formatting components."""
    
    @abstractmethod
    def format_daily_report(self, report_data: ReportData) -> str:
        """Format complete daily report data into output format.
        
        Args:
            report_data: Complete report data structure
            
        Returns:
            Formatted report string
        """
        pass
    
    @abstractmethod
    def format_game_section(
        self,
        game_data: GameData,
        odds_data: List[BettingOdds],
        game_analysis: Optional[GameAnalysis],
        player_analyses: List[PlayerAnalysis]
    ) -> str:
        """Format a single game section of the report.
        
        Args:
            game_data: Game information
            odds_data: Betting odds for the game
            game_analysis: Game analysis results
            player_analyses: Player analysis results
            
        Returns:
            Formatted game section string
        """
        pass
    
    @abstractmethod
    def format_executive_summary(self, report_data: ReportData) -> str:
        """Format executive summary section.
        
        Args:
            report_data: Complete report data
            
        Returns:
            Formatted executive summary string
        """
        pass


class ErrorHandler(ABC):
    """Abstract base class for error handling components."""
    
    @abstractmethod
    async def handle_data_fetch_error(
        self, 
        error: Exception, 
        context: Dict[str, Any]
    ) -> Optional[Any]:
        """Handle errors during data fetching with graceful degradation.
        
        Args:
            error: The exception that occurred
            context: Context information about the operation
            
        Returns:
            Fallback data or None if no recovery possible
        """
        pass
    
    @abstractmethod
    async def handle_analysis_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> Optional[Any]:
        """Handle errors during analysis with fallback strategies.
        
        Args:
            error: The exception that occurred
            context: Context information about the operation
            
        Returns:
            Fallback analysis or None if no recovery possible
        """
        pass
    
    @abstractmethod
    def aggregate_errors(self, errors: List[Exception]) -> List[ErrorReport]:
        """Aggregate and categorize errors for reporting.
        
        Args:
            errors: List of exceptions that occurred
            
        Returns:
            List of structured error reports
        """
        pass


class CacheManager(ABC):
    """Abstract base class for caching components."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve cached data by key.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl_minutes: int = 5) -> None:
        """Store data in cache with TTL.
        
        Args:
            key: Cache key
            value: Data to cache
            ttl_minutes: Time to live in minutes
        """
        pass
    
    @abstractmethod
    async def invalidate(self, pattern: str) -> None:
        """Invalidate cached data matching pattern.
        
        Args:
            pattern: Key pattern to match for invalidation
        """
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all cached data."""
        pass


class DataOrchestrator(ABC):
    """Abstract base class for data orchestration components."""
    
    @abstractmethod
    async def fetch_all_leagues_data(
        self,
        target_date: str,
        leagues: List[str],
        markets: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Orchestrate data fetching across multiple leagues.
        
        Args:
            target_date: Target date in YYYY-MM-DD format
            leagues: List of leagues to process
            markets: List of betting markets to fetch
            
        Returns:
            Dictionary mapping league to collected data
        """
        pass
    
    @abstractmethod
    async def fetch_league_data(
        self,
        league: str,
        target_date: str,
        markets: List[str]
    ) -> Dict[str, Any]:
        """Fetch all data for a single league.
        
        Args:
            league: League identifier
            target_date: Target date in YYYY-MM-DD format
            markets: List of betting markets to fetch
            
        Returns:
            Dictionary containing all league data
        """
        pass


class ReportGenerator(ABC):
    """Abstract base class for the main report generation component."""
    
    @abstractmethod
    async def generate_daily_report(
        self,
        target_date: str,
        leagues: Optional[List[str]] = None,
        markets: Optional[List[str]] = None,
        output_format: str = "markdown"
    ) -> ReportData:
        """Generate complete daily betting intelligence report.
        
        Args:
            target_date: Target date in YYYY-MM-DD format
            leagues: Optional list of leagues to include
            markets: Optional list of betting markets to analyze
            output_format: Output format (markdown, json, etc.)
            
        Returns:
            Complete ReportData structure
        """
        pass
    
    @abstractmethod
    async def save_report(
        self,
        report_data: ReportData,
        filename: Optional[str] = None
    ) -> str:
        """Save report to file.
        
        Args:
            report_data: Complete report data
            filename: Optional custom filename
            
        Returns:
            Path to saved report file
        """
        pass