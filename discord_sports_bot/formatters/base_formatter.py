"""
Base formatter class with common Discord embed utilities
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import discord


logger = logging.getLogger(__name__)


class BaseFormatter:
    """
    Base formatter class providing common Discord embed utilities,
    standardized color schemes, and reusable formatting functions
    """
    
    def __init__(self, sport_name: str, embed_color: int = 0x7289da):
        """
        Initialize base formatter
        
        Args:
            sport_name: Name of the sport
            embed_color: Default embed color for this sport
        """
        self.sport_name = sport_name
        self.embed_color = embed_color
        self.max_field_value_length = 1024
        self.max_embed_fields = 25
    
    def create_base_embed(self, title: str, description: str = None, color: int = None) -> discord.Embed:
        """
        Create base embed with standard formatting
        
        Args:
            title: Embed title
            description: Embed description (optional)
            color: Embed color (optional, uses sport default)
            
        Returns:
            Discord embed object
        """
        embed = discord.Embed(
            title=title,
            description=description,
            color=color or self.embed_color,
            timestamp=datetime.now()
        )
        
        embed.set_footer(text=f"{self.sport_name.upper()} Analysis Bot")
        return embed
    
    def convert_decimal_to_american_odds(self, decimal_odds: float) -> str:
        """
        Convert decimal odds to American format
        
        Args:
            decimal_odds: Decimal odds value
            
        Returns:
            American odds string (e.g., "+150", "-200")
        """
        try:
            decimal = float(decimal_odds)
            if decimal >= 2.0:
                american = int((decimal - 1) * 100)
                return f"+{american}"
            else:
                american = int(-100 / (decimal - 1))
                return str(american)
        except (ValueError, ZeroDivisionError, TypeError):
            return str(decimal_odds)
    
    def format_odds_display(self, decimal_odds: float) -> str:
        """
        Format odds for display with both decimal and American formats
        
        Args:
            decimal_odds: Decimal odds value
            
        Returns:
            Formatted odds string
        """
        american = self.convert_decimal_to_american_odds(decimal_odds)
        return f"{decimal_odds} ({american})"
    
    def format_team_record(self, wins: int, draws: int = None, losses: int = None) -> str:
        """
        Format team record display
        
        Args:
            wins: Number of wins
            draws: Number of draws (optional, for sports with draws)
            losses: Number of losses (optional)
            
        Returns:
            Formatted record string
        """
        if draws is not None:
            return f"{wins}W-{draws}D-{losses}L"
        elif losses is not None:
            return f"{wins}W-{losses}L"
        else:
            return f"{wins}W"
    
    def format_percentage(self, value: float, decimal_places: int = 1) -> str:
        """
        Format percentage value
        
        Args:
            value: Percentage value (0-100)
            decimal_places: Number of decimal places
            
        Returns:
            Formatted percentage string
        """
        return f"{value:.{decimal_places}f}%"
    
    def format_date_display(self, date_obj: datetime, include_time: bool = True) -> str:
        """
        Format date for display
        
        Args:
            date_obj: Datetime object
            include_time: Whether to include time
            
        Returns:
            Formatted date string
        """
        if include_time:
            return date_obj.strftime("%B %d, %Y at %I:%M %p")
        else:
            return date_obj.strftime("%B %d, %Y")
    
    def truncate_field_value(self, value: str, max_length: int = None) -> str:
        """
        Truncate field value to fit Discord limits
        
        Args:
            value: Value to truncate
            max_length: Maximum length (uses default if not provided)
            
        Returns:
            Truncated value
        """
        max_len = max_length or self.max_field_value_length
        if len(value) <= max_len:
            return value
        
        return value[:max_len - 3] + "..."
    
    def add_field_safe(self, embed: discord.Embed, name: str, value: str, inline: bool = False) -> bool:
        """
        Safely add field to embed with length and count validation
        
        Args:
            embed: Discord embed object
            name: Field name
            value: Field value
            inline: Whether field should be inline
            
        Returns:
            True if field was added successfully
        """
        # Check field count limit
        if len(embed.fields) >= self.max_embed_fields:
            logger.warning(f"Cannot add field '{name}': embed field limit reached")
            return False
        
        # Truncate value if needed
        safe_value = self.truncate_field_value(value)
        
        try:
            embed.add_field(name=name, value=safe_value, inline=inline)
            return True
        except Exception as e:
            logger.error(f"Failed to add field '{name}': {e}")
            return False
    
    def create_loading_embed(self, operation: str) -> discord.Embed:
        """
        Create loading indicator embed
        
        Args:
            operation: Description of operation in progress
            
        Returns:
            Loading embed
        """
        embed = self.create_base_embed(
            title="🔄 Loading...",
            description=f"{operation}",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Please wait",
            value="This may take a few moments...",
            inline=False
        )
        
        return embed
    
    def create_success_embed(self, title: str, description: str, details: Dict[str, Any] = None) -> discord.Embed:
        """
        Create success confirmation embed
        
        Args:
            title: Success title
            description: Success description
            details: Additional details to display
            
        Returns:
            Success embed
        """
        embed = self.create_base_embed(
            title=f"✅ {title}",
            description=description,
            color=discord.Color.green()
        )
        
        if details:
            for key, value in details.items():
                self.add_field_safe(embed, key, str(value), inline=True)
        
        return embed
    
    def get_form_emoji(self, result: str) -> str:
        """
        Get emoji for match result
        
        Args:
            result: Match result ('W', 'L', 'D', etc.)
            
        Returns:
            Appropriate emoji
        """
        emoji_map = {
            'W': '🟢',  # Win - Green
            'L': '🔴',  # Loss - Red
            'D': '🟡',  # Draw - Yellow
            'T': '🟡',  # Tie - Yellow
            'N': '⚪',  # No result - White
            '?': '⚪'   # Unknown - White
        }
        
        return emoji_map.get(result.upper(), '⚪')
    
    def format_recent_form(self, form_string: str) -> str:
        """
        Format recent form with emojis
        
        Args:
            form_string: Form string (e.g., "WLDWW")
            
        Returns:
            Form string with emojis
        """
        if not form_string:
            return "No recent form data"
        
        emoji_form = ''.join([self.get_form_emoji(result) for result in form_string])
        return f"{emoji_form} ({form_string})"
    
    def create_progress_bar(self, current: int, total: int, length: int = 10) -> str:
        """
        Create text-based progress bar
        
        Args:
            current: Current progress
            total: Total items
            length: Length of progress bar
            
        Returns:
            Progress bar string
        """
        if total == 0:
            return "▱" * length
        
        filled = int((current / total) * length)
        bar = "▰" * filled + "▱" * (length - filled)
        percentage = (current / total) * 100
        
        return f"{bar} {percentage:.1f}% ({current}/{total})"