"""
Base sport handler interface that all sport implementations must follow
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import discord


@dataclass
class ChannelCreationResult:
    """Result of channel creation operation"""
    success: bool
    channels_created: int
    total_matches: int
    errors: List[str]
    message: str


@dataclass
class ClearResult:
    """Result of channel clearing operation"""
    success: bool
    channels_deleted: int
    total_channels: int
    errors: List[str]
    message: str


@dataclass
class Match:
    """Standard match data structure"""
    id: str
    home_team: str
    away_team: str
    league: str
    datetime: Optional[datetime]
    odds: Optional[Dict[str, Any]]
    status: str
    additional_data: Dict[str, Any]


class BaseSportHandler(ABC):
    """
    Abstract base class that all sport handlers must inherit from.
    Provides consistent interface for channel creation, data fetching, and formatting.
    """
    
    def __init__(self, sport_name: str, config: Dict[str, Any], mcp_client):
        """
        Initialize sport handler with configuration and MCP client
        
        Args:
            sport_name: Name of the sport (e.g., 'soccer', 'mlb')
            config: Sport-specific configuration dictionary
            mcp_client: MCP client instance for API calls
        """
        self.sport_name = sport_name
        self.config = config
        self.mcp_client = mcp_client
        self.category_name = config.get('category_name', f'{sport_name.upper()} GAMES')
        self.category_id = config.get('category_id')
        
    @abstractmethod
    async def create_channels(self, interaction: discord.Interaction, date: str) -> ChannelCreationResult:
        """
        Create channels for matches on the specified date
        
        Args:
            interaction: Discord interaction object
            date: Date string in YYYY-MM-DD format
            
        Returns:
            ChannelCreationResult with operation details
        """
        pass
    
    @abstractmethod
    async def clear_channels(self, interaction: discord.Interaction, category_name: str) -> ClearResult:
        """
        Clear all channels from the sport's category
        
        Args:
            interaction: Discord interaction object
            category_name: Name of category to clear
            
        Returns:
            ClearResult with operation details
        """
        pass
    
    @abstractmethod
    async def get_matches(self, date: str) -> List[Match]:
        """
        Fetch matches for the specified date from MCP service
        
        Args:
            date: Date string in format expected by the sport's MCP service
            
        Returns:
            List of Match objects
        """
        pass
    
    @abstractmethod
    async def format_match_analysis(self, match: Match) -> discord.Embed:
        """
        Create formatted Discord embed for match analysis
        
        Args:
            match: Match object with data to format
            
        Returns:
            Discord embed with formatted match analysis
        """
        pass
    
    def get_category(self, guild: discord.Guild) -> Optional[discord.CategoryChannel]:
        """
        Get or find the category for this sport
        
        Args:
            guild: Discord guild object
            
        Returns:
            CategoryChannel if found, None otherwise
        """
        if self.category_id:
            return discord.utils.get(guild.categories, id=self.category_id)
        return discord.utils.get(guild.categories, name=self.category_name)
    
    async def create_category(self, guild: discord.Guild) -> discord.CategoryChannel:
        """
        Create category for this sport if it doesn't exist
        
        Args:
            guild: Discord guild object
            
        Returns:
            CategoryChannel object
        """
        category = self.get_category(guild)
        if not category:
            category = await guild.create_category(self.category_name)
        return category
    
    def format_channel_name(self, home_team: str, away_team: str, max_length: int = 20) -> str:
        """
        Create standardized channel name from team names
        
        Args:
            home_team: Home team name
            away_team: Away team name
            max_length: Maximum length for each team name part
            
        Returns:
            Formatted channel name
        """
        home_clean = home_team.lower().replace(' ', '-').replace('_', '-')[:max_length]
        away_clean = away_team.lower().replace(' ', '-').replace('_', '-')[:max_length]
        return f"{away_clean}-vs-{home_clean}"
    
    def validate_permissions(self, interaction: discord.Interaction) -> bool:
        """
        Check if user has required permissions for channel operations
        
        Args:
            interaction: Discord interaction object
            
        Returns:
            True if user has manage_channels permission
        """
        return interaction.user.guild_permissions.manage_channels