"""
Utility functions for the Daily Betting Intelligence system.

This module provides common helper functions for date handling, timezone conversion,
data validation, and other shared functionality across the system.
"""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
import pytz


def validate_date_format(date_str: str) -> bool:
    """Validate date string is in YYYY-MM-DD format.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid format, False otherwise
    """
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def convert_to_eastern_time(dt: datetime) -> datetime:
    """Convert datetime to Eastern timezone.
    
    Args:
        dt: Datetime object to convert
        
    Returns:
        Datetime object in Eastern timezone
    """
    eastern = pytz.timezone('US/Eastern')
    
    if dt.tzinfo is None:
        # Assume UTC if no timezone info
        dt = pytz.utc.localize(dt)
    
    return dt.astimezone(eastern)


def parse_date_string(date_str: str) -> datetime:
    """Parse date string to datetime object.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        Datetime object
        
    Raises:
        ValueError: If date format is invalid
    """
    if not validate_date_format(date_str):
        raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")
    
    return datetime.strptime(date_str, '%Y-%m-%d')


def format_odds(odds: int) -> str:
    """Format American odds for display.
    
    Args:
        odds: American odds as integer
        
    Returns:
        Formatted odds string with + or - prefix
    """
    if odds > 0:
        return f"+{odds}"
    return str(odds)


def calculate_implied_probability(odds: int) -> float:
    """Calculate implied probability from American odds.
    
    Args:
        odds: American odds as integer
        
    Returns:
        Implied probability as decimal (0.0 to 1.0)
    """
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)


def find_best_odds(odds_list: List[Dict[str, Any]], bet_type: str) -> Optional[Dict[str, Any]]:
    """Find the best odds for a specific bet type.
    
    Args:
        odds_list: List of odds dictionaries from different sportsbooks
        bet_type: Type of bet ('moneyline_home', 'moneyline_away', etc.)
        
    Returns:
        Dictionary with best odds info or None if not found
    """
    if not odds_list:
        return None
    
    best_odds = None
    best_value = None
    
    for odds_data in odds_list:
        if bet_type not in odds_data or odds_data[bet_type] is None:
            continue
        
        current_odds = odds_data[bet_type]
        
        # For positive odds, higher is better
        # For negative odds, closer to 0 (less negative) is better
        if best_value is None:
            best_odds = odds_data
            best_value = current_odds
        elif current_odds > 0 and best_value > 0:
            if current_odds > best_value:
                best_odds = odds_data
                best_value = current_odds
        elif current_odds < 0 and best_value < 0:
            if current_odds > best_value:  # Less negative is better
                best_odds = odds_data
                best_value = current_odds
        elif current_odds > 0 and best_value < 0:
            # Positive odds are always better than negative
            best_odds = odds_data
            best_value = current_odds
    
    return best_odds


def sanitize_team_name(team_name: str) -> str:
    """Sanitize team name for consistent matching.
    
    Args:
        team_name: Raw team name
        
    Returns:
        Sanitized team name
    """
    # Remove common prefixes and suffixes
    name = team_name.strip()
    
    # Remove location prefixes for consistency
    prefixes_to_remove = ['Los Angeles', 'New York', 'San Francisco', 'Las Vegas']
    for prefix in prefixes_to_remove:
        if name.startswith(prefix):
            name = name[len(prefix):].strip()
    
    return name


def validate_confidence_score(score: float) -> float:
    """Validate and clamp confidence score to valid range.
    
    Args:
        score: Confidence score to validate
        
    Returns:
        Clamped confidence score between 0.0 and 1.0
    """
    return max(0.0, min(1.0, score))


def generate_cache_key(prefix: str, *args: Any) -> str:
    """Generate cache key from prefix and arguments.
    
    Args:
        prefix: Cache key prefix
        *args: Arguments to include in key
        
    Returns:
        Generated cache key string
    """
    key_parts = [prefix]
    for arg in args:
        if isinstance(arg, (list, dict)):
            # Convert complex types to string representation
            key_parts.append(str(hash(str(arg))))
        else:
            key_parts.append(str(arg))
    
    return ":".join(key_parts)


def safe_get_nested(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    """Safely get nested dictionary value.
    
    Args:
        data: Dictionary to search
        keys: List of keys for nested access
        default: Default value if key path not found
        
    Returns:
        Value at key path or default
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size.
    
    Args:
        items: List to chunk
        chunk_size: Maximum size of each chunk
        
    Returns:
        List of chunked lists
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def calculate_value_bet_score(
    odds: int, 
    implied_prob: float, 
    predicted_prob: float
) -> float:
    """Calculate value bet score based on odds and probabilities.
    
    Args:
        odds: American odds
        implied_prob: Implied probability from odds
        predicted_prob: Model's predicted probability
        
    Returns:
        Value score (positive indicates value bet)
    """
    if predicted_prob <= 0 or implied_prob <= 0:
        return 0.0
    
    # Kelly Criterion-inspired value calculation
    edge = predicted_prob - implied_prob
    return edge / implied_prob if implied_prob > 0 else 0.0


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount for display.
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    if currency == "USD":
        return f"${amount:.2f}"
    return f"{amount:.2f} {currency}"


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix