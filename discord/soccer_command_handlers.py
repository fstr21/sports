"""
Soccer Discord Commands - Enhanced Error Handling
Provides comprehensive error handling for all soccer-related Discord commands
"""

import asyncio
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import discord
from discord.ext import commands

# Import enhanced error handling system
from soccer_error_handling import (
    SoccerBotError, MCPConnectionError, MCPTimeoutError, MCPDataError, 
    DiscordAPIError, ValidationError, ErrorContext, ErrorSeverity,
    retry_with_backoff, GracefulDegradation, error_handler, bot_logger
)

# ============================================================================
# COMMAND ERROR HANDLING DECORATOR
# ============================================================================

def handle_soccer_command_errors(operation_name: str):
    """
    Decorator for handling errors in soccer Discord commands
    
    Args:
        operation_name: Name of the operation for logging
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            # Create error context
            context = ErrorContext(
                operation_name,
                user_id=interaction.user.id,
                guild_id=interaction.guild.id if interaction.guild else None,
                channel_id=interaction.channel.id if interaction.channel else None,
                additional_data={
                    "command": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
            )
            
            # Log operation start
            bot_logger.log_operation_start(operation_name, context)
            
            try:
                # Defer the response to give us more time
                if not interaction.response.is_done():
                    await interaction.response.defer()
                
                # Execute the command
                result = await func(interaction, *args, **kwargs)
                
                # Log successful completion
                bot_logger.log_operation_success(operation_name, context)
                return result
                
            except ValidationError as e:
                # Handle validation errors (user input issues)
                embed = error_handler.create_error_embed(e, [
                    "Check your input format",
                    "Use the command help for examples",
                    "Try again with correct parameters"
                ])
                await _safe_followup_send(interaction, embed=embed)
                
            except (MCPConnectionError, MCPTimeoutError) as e:
                # Handle MCP server issues
                suggestions = [
                    "Try again in a few moments",
                    "Check if the date/teams are valid",
                    "Contact an administrator if the issue persists"
                ]
                
                if isinstance(e, MCPTimeoutError):
                    suggestions.insert(0, "Try with a smaller date range or specific teams")
                
                embed = error_handler.create_error_embed(e, suggestions)
                await _safe_followup_send(interaction, embed=embed)
                
            except MCPDataError as e:
                # Handle data issues with graceful degradation
                if e.partial_data_available:
                    # Try to show partial data
                    embed = GracefulDegradation.create_fallback_embed(
                        "Partial Data Available",
                        e.user_message,
                        ["Some information may be missing", "Data shown is what's currently available"]
                    )
                else:
                    embed = error_handler.create_error_embed(e, [
                        "Try again with different parameters",
                        "Check if the teams/leagues exist",
                        "Try a different date"
                    ])
                
                await _safe_followup_send(interaction, embed=embed)
                
            except DiscordAPIError as e:
                # Handle Discord API issues
                suggestions = []
                if e.error_code == 403:
                    suggestions = [
                        "Contact an administrator to check bot permissions",
                        "Ensure the bot has required permissions in this channel"
                    ]
                elif e.error_code == 429:
                    suggestions = [
                        f"Wait {int(e.retry_after or 60)} seconds before trying again",
                        "Discord is rate limiting requests"
                    ]
                else:
                    suggestions = [
                        "Try again in a moment",
                        "Contact an administrator if the issue persists"
                    ]
                
                embed = error_handler.create_error_embed(e, suggestions)
                await _safe_followup_send(interaction, embed=embed)
                
            except Exception as e:
                # Handle unexpected errors
                error_obj = SoccerBotError(
                    f"Unexpected error in {operation_name}: {str(e)}",
                    ErrorSeverity.HIGH,
                    context,
                    "An unexpected error occurred. Please try again later."
                )
                
                bot_logger.log_operation_error(operation_name, error_obj, context)
                
                embed = error_handler.create_error_embed(error_obj, [
                    "Try the command again",
                    "Contact an administrator if the error persists",
                    "Check the bot logs for more details"
                ])
                
                await _safe_followup_send(interaction, embed=embed)
        
        return wrapper
    return decorator

async def _safe_followup_send(interaction: discord.Interaction, **kwargs):
    """Safely send a followup message with error handling"""
    try:
        await interaction.followup.send(**kwargs)
    except discord.HTTPException as e:
        # If followup fails, try to edit the original response
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(**kwargs)
            else:
                await interaction.edit_original_response(**kwargs)
        except discord.HTTPException:
            # If all else fails, log the error
            logging.getLogger(__name__).error(f"Failed to send error message to user: {e}")

# ============================================================================
# INPUT VALIDATION UTILITIES
# ============================================================================

def validate_date_input(date_string: str) -> str:
    """
    Validate and normalize date input with comprehensive error handling
    
    Args:
        date_string: Date string in various formats
        
    Returns:
        Normalized date string in YYYY-MM-DD format
        
    Raises:
        ValidationError: If date format is invalid or out of range
    """
    if not date_string or not isinstance(date_string, str):
        raise ValidationError(
            "Date string is required",
            "date",
            date_string,
            "MM/DD/YYYY, DD-MM-YYYY, or YYYY-MM-DD"
        )
    
    # Supported date formats
    formats = [
        "%m/%d/%Y",    # MM/DD/YYYY
        "%d-%m-%Y",    # DD-MM-YYYY
        "%Y-%m-%d",    # YYYY-MM-DD
        "%m-%d-%Y",    # MM-DD-YYYY
        "%d/%m/%Y",    # DD/MM/YYYY
    ]
    
    parsed_date = None
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_string.strip(), fmt)
            break
        except ValueError:
            continue
    
    if parsed_date is None:
        raise ValidationError(
            f"Invalid date format: {date_string}",
            "date",
            date_string,
            "MM/DD/YYYY, DD-MM-YYYY, or YYYY-MM-DD"
        )
    
    # Validate date range (30 days past to 1 year future)
    now = datetime.now()
    min_date = now - timedelta(days=30)
    max_date = now + timedelta(days=365)
    
    if not (min_date <= parsed_date <= max_date):
        raise ValidationError(
            f"Date {date_string} is outside allowed range",
            "date",
            date_string,
            "within 30 days past to 1 year future"
        )
    
    return parsed_date.strftime("%Y-%m-%d")

def validate_team_name(team_name: str, field_name: str = "team") -> str:
    """
    Validate team name input
    
    Args:
        team_name: Team name string
        field_name: Field name for error messages
        
    Returns:
        Cleaned team name
        
    Raises:
        ValidationError: If team name is invalid
    """
    if not team_name or not isinstance(team_name, str):
        raise ValidationError(
            f"{field_name.title()} name is required",
            field_name,
            team_name,
            "non-empty string"
        )
    
    cleaned_name = team_name.strip()
    
    if len(cleaned_name) < 2:
        raise ValidationError(
            f"{field_name.title()} name too short",
            field_name,
            team_name,
            "at least 2 characters"
        )
    
    if len(cleaned_name) > 50:
        raise ValidationError(
            f"{field_name.title()} name too long",
            field_name,
            team_name,
            "maximum 50 characters"
        )
    
    return cleaned_name

def validate_league_choice(league_choice: Optional[discord.app_commands.Choice[str]]) -> Optional[str]:
    """
    Validate league choice input
    
    Args:
        league_choice: Discord app command choice for league
        
    Returns:
        League code or None
        
    Raises:
        ValidationError: If league choice is invalid
    """
    if league_choice is None:
        return None
    
    # Valid league codes
    valid_leagues = ["EPL", "La Liga", "MLS", "Bundesliga", "Serie A", "UEFA"]
    
    if league_choice.value not in valid_leagues:
        raise ValidationError(
            f"Invalid league: {league_choice.value}",
            "league",
            league_choice.value,
            f"one of: {', '.join(valid_leagues)}"
        )
    
    return league_choice.value

# ============================================================================
# ENHANCED COMMAND IMPLEMENTATIONS
# ============================================================================

@handle_soccer_command_errors("soccer_schedule_command")
async def enhanced_soccer_schedule_command(interaction: discord.Interaction, 
                                         league: discord.app_commands.Choice[str] = None, 
                                         date: str = None):
    """Enhanced soccer schedule command with comprehensive error handling"""
    
    # Validate inputs
    league_filter = validate_league_choice(league)
    
    # Use current date if none provided
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    else:
        date = validate_date_input(date)
    
    # Create error context
    context = ErrorContext(
        "soccer_schedule_command",
        user_id=interaction.user.id,
        guild_id=interaction.guild.id if interaction.guild else None,
        additional_data={"date": date, "league_filter": league_filter}
    )
    
    # Import soccer components
    from soccer_integration import SoccerMCPClient, SoccerDataProcessor, SoccerEmbedBuilder
    
    # Initialize components
    soccer_client = SoccerMCPClient()
    soccer_processor = SoccerDataProcessor()
    soccer_embed_builder = SoccerEmbedBuilder()
    
    # Fetch matches from MCP server
    matches_data = await soccer_client.get_matches_for_date(date, [league_filter] if league_filter else None, context)
    
    # Process matches data
    processed_matches = soccer_processor.process_match_data(matches_data)
    
    if not processed_matches:
        league_text = f" for {league.name}" if league else ""
        embed = discord.Embed(
            title="📅 No Matches Found",
            description=f"No soccer matches scheduled{league_text} on {date}",
            color=0xffd93d,
            timestamp=datetime.utcnow()
        )
        embed.add_field(
            name="💡 Suggestions",
            value="• Try a different date\n• Check other leagues\n• Verify the date format",
            inline=False
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Create schedule embed
    embed = soccer_embed_builder.create_schedule_embed(processed_matches, date, league_filter)
    
    # Handle partial data scenarios
    if matches_data.get('fallback') or matches_data.get('_partial_data'):
        embed.add_field(
            name="⚠️ Note",
            value="Some match information may be incomplete due to data availability.",
            inline=False
        )
    
    await interaction.followup.send(embed=embed)

@handle_soccer_command_errors("soccer_odds_command")
async def enhanced_soccer_odds_command(interaction: discord.Interaction, 
                                     team1: str, 
                                     team2: str, 
                                     date: str = None):
    """Enhanced soccer odds command with comprehensive error handling"""
    
    # Validate inputs
    team1_clean = validate_team_name(team1, "team1")
    team2_clean = validate_team_name(team2, "team2")
    
    if team1_clean.lower() == team2_clean.lower():
        raise ValidationError(
            "Team names must be different",
            "teams",
            f"{team1}, {team2}",
            "two different team names"
        )
    
    # Validate date if provided
    if date:
        date = validate_date_input(date)
    else:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Create error context
    context = ErrorContext(
        "soccer_odds_command",
        user_id=interaction.user.id,
        guild_id=interaction.guild.id if interaction.guild else None,
        additional_data={"team1": team1_clean, "team2": team2_clean, "date": date}
    )
    
    # Import soccer components
    from soccer_integration import SoccerMCPClient, SoccerDataProcessor, SoccerEmbedBuilder
    
    # Initialize components
    soccer_client = SoccerMCPClient()
    soccer_processor = SoccerDataProcessor()
    soccer_embed_builder = SoccerEmbedBuilder()
    
    # Search for match between the teams
    matches_data = await soccer_client.get_matches_for_date(date, context=context)
    processed_matches = soccer_processor.process_match_data(matches_data)
    
    # Find matching teams
    target_match = None
    for match in processed_matches:
        if (team1_clean.lower() in match.home_team.name.lower() or 
            team1_clean.lower() in match.away_team.name.lower()) and \
           (team2_clean.lower() in match.home_team.name.lower() or 
            team2_clean.lower() in match.away_team.name.lower()):
            target_match = match
            break
    
    if not target_match:
        embed = discord.Embed(
            title="🔍 Match Not Found",
            description=f"No match found between **{team1_clean}** and **{team2_clean}** on {date}",
            color=0xffd93d,
            timestamp=datetime.utcnow()
        )
        embed.add_field(
            name="💡 Suggestions",
            value="• Check team name spelling\n• Try a different date\n• Use partial team names\n• Check if the match exists",
            inline=False
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Create odds embed
    embed = soccer_embed_builder.create_betting_odds_embed(target_match.odds) if target_match.odds else None
    
    if not embed:
        embed = discord.Embed(
            title="📊 Odds Unavailable",
            description=f"Match found: **{target_match.away_team.name}** vs **{target_match.home_team.name}**\n\nBetting odds are not currently available for this match.",
            color=0xffd93d,
            timestamp=datetime.utcnow()
        )
        embed.add_field(
            name="Match Details",
            value=f"**Date:** {target_match.date}\n**Time:** {target_match.time}\n**Venue:** {target_match.venue}",
            inline=False
        )
    
    await interaction.followup.send(embed=embed)

@handle_soccer_command_errors("soccer_h2h_command")
async def enhanced_soccer_h2h_command(interaction: discord.Interaction, 
                                    team1: str, 
                                    team2: str):
    """Enhanced soccer head-to-head command with comprehensive error handling"""
    
    # Validate inputs
    team1_clean = validate_team_name(team1, "team1")
    team2_clean = validate_team_name(team2, "team2")
    
    if team1_clean.lower() == team2_clean.lower():
        raise ValidationError(
            "Team names must be different",
            "teams",
            f"{team1}, {team2}",
            "two different team names"
        )
    
    # Create error context
    context = ErrorContext(
        "soccer_h2h_command",
        user_id=interaction.user.id,
        guild_id=interaction.guild.id if interaction.guild else None,
        additional_data={"team1": team1_clean, "team2": team2_clean}
    )
    
    # Import soccer components
    from soccer_integration import SoccerMCPClient, SoccerDataProcessor, SoccerEmbedBuilder
    
    # Initialize components
    soccer_client = SoccerMCPClient()
    soccer_processor = SoccerDataProcessor()
    soccer_embed_builder = SoccerEmbedBuilder()
    
    # For now, we'll use placeholder team IDs since we need to implement team search
    # In a real implementation, you'd search for teams first
    team1_id = hash(team1_clean.lower()) % 10000  # Placeholder
    team2_id = hash(team2_clean.lower()) % 10000  # Placeholder
    
    # Get H2H analysis
    h2h_data = await soccer_client.get_h2h_analysis(team1_id, team2_id, context=context)
    
    # Process H2H insights
    h2h_insights = soccer_processor.calculate_h2h_insights(h2h_data)
    
    # Create H2H embed
    embed = soccer_embed_builder.create_h2h_analysis_embed(h2h_insights)
    
    # Handle fallback scenarios
    if h2h_data.get('fallback') or h2h_data.get('total_meetings', 0) == 0:
        embed = discord.Embed(
            title="📊 Head-to-Head Analysis",
            description=f"**{team1_clean}** vs **{team2_clean}**\n\nHead-to-head data is currently unavailable or these teams haven't met recently.",
            color=0xffd93d,
            timestamp=datetime.utcnow()
        )
        embed.add_field(
            name="💡 What you can try",
            value="• Check team name spelling\n• Try with full team names\n• These teams may not have played each other recently",
            inline=False
        )
    
    await interaction.followup.send(embed=embed)

@handle_soccer_command_errors("soccer_standings_command")
async def enhanced_soccer_standings_command(interaction: discord.Interaction, 
                                          league: discord.app_commands.Choice[str]):
    """Enhanced soccer standings command with comprehensive error handling"""
    
    # Validate league choice
    league_code = validate_league_choice(league)
    
    # Create error context
    context = ErrorContext(
        "soccer_standings_command",
        user_id=interaction.user.id,
        guild_id=interaction.guild.id if interaction.guild else None,
        additional_data={"league": league_code}
    )
    
    # Import soccer components
    from soccer_integration import SoccerMCPClient, SoccerDataProcessor, SoccerEmbedBuilder, SUPPORTED_LEAGUES
    
    # Initialize components
    soccer_client = SoccerMCPClient()
    soccer_embed_builder = SoccerEmbedBuilder()
    
    # Get league ID
    league_config = SUPPORTED_LEAGUES.get(league_code)
    if not league_config:
        raise ValidationError(
            f"League configuration not found: {league_code}",
            "league",
            league_code,
            "supported league code"
        )
    
    league_id = league_config["id"]
    
    # Get league standings
    standings_data = await soccer_client.get_league_standings(league_id, context=context)
    
    # Create standings embed
    embed = soccer_embed_builder.create_league_standings_embed(standings_data)
    
    # Handle fallback scenarios
    if not standings_data or standings_data.get('error'):
        embed = discord.Embed(
            title=f"📊 {league.name} Standings",
            description="League standings are currently unavailable.",
            color=0xffd93d,
            timestamp=datetime.utcnow()
        )
        embed.add_field(
            name="💡 What you can try",
            value="• Try again in a few minutes\n• Check if the league is currently active\n• Contact an administrator if the issue persists",
            inline=False
        )
    
    await interaction.followup.send(embed=embed)