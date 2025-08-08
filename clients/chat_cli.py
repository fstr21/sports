#!/usr/bin/env python3
"""
Chat CLI for natural language sports queries.

This module provides a natural language interface for asking questions about sports games.
It uses team name matching, date resolution, and MCP analyze_game_strict for contextual responses.

Usage:
    python chat_cli.py ask <league> <date|today> <TEAM1> vs <TEAM2> <question>

Examples:
    python chat_cli.py ask nfl 20241215 Ravens vs Steelers "Who had more rushing yards?"
    python chat_cli.py ask nba today Lakers vs Warriors "What was the final score?"
    python chat_cli.py ask nfl today "Kansas City" vs "Buffalo" "How did Mahomes perform?"
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import difflib

from core_mcp import (
    scoreboard, analyze_game_strict, teams,
    MCPError, MCPServerError, MCPValidationError,
    LEAGUE_MAPPING
)

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def get_today_date() -> Tuple[str, str]:
    """
    Get today's date in YYYYMMDD format using UTC timezone.
    
    Returns:
        Tuple of (date_string, timezone_info) for clarity in responses
    """
    now_utc = datetime.now(timezone.utc)
    date_str = now_utc.strftime('%Y%m%d')
    tz_info = f"UTC {now_utc.strftime('%H:%M')}"
    return date_str, tz_info

def validate_date(date_str: str) -> bool:
    """
    Validate date format (YYYYMMDD).
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if len(date_str) != 8:
        return False
    
    try:
        datetime.strptime(date_str, '%Y%m%d')
        return True
    except ValueError:
        return False

def normalize_team_name(name: str) -> str:
    """
    Normalize team name for matching by removing common variations.
    
    Args:
        name: Team name to normalize
        
    Returns:
        Normalized team name (lowercase, no extra spaces)
    """
    # Remove quotes and normalize whitespace
    normalized = name.strip().strip('"\'').lower()
    
    # Remove common prefixes/suffixes
    prefixes_to_remove = ['the ', 'fc ', 'cf ', 'ac ']
    suffixes_to_remove = [' fc', ' cf', ' ac']
    
    for prefix in prefixes_to_remove:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
    
    for suffix in suffixes_to_remove:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)]
    
    # Common team name normalizations (more comprehensive)
    normalizations = {
        # NFL teams
        'kansas city': 'kansas city',
        'kc': 'kansas city',
        'chiefs': 'kansas city',
        'new england': 'new england',
        'patriots': 'new england',
        'pats': 'new england',
        'green bay': 'green bay',
        'packers': 'green bay',
        'san francisco': 'san francisco',
        '49ers': 'san francisco',
        'niners': 'san francisco',
        'los angeles': 'los angeles',
        'la': 'los angeles',
        'rams': 'los angeles rams',
        'chargers': 'los angeles chargers',
        'new york': 'new york',
        'ny': 'new york',
        'giants': 'new york giants',
        'jets': 'new york jets',
        'tampa bay': 'tampa bay',
        'bucs': 'tampa bay',
        'buccaneers': 'tampa bay',
        'pittsburgh': 'pittsburgh',
        'steelers': 'pittsburgh',
        'baltimore': 'baltimore',
        'ravens': 'baltimore',
        'cleveland': 'cleveland',
        'browns': 'cleveland',
        'cincinnati': 'cincinnati',
        'bengals': 'cincinnati',
        'buffalo': 'buffalo',
        'bills': 'buffalo',
        'miami': 'miami',
        'dolphins': 'miami',
        'denver': 'denver',
        'broncos': 'denver',
        'las vegas': 'las vegas',
        'raiders': 'las vegas',
        'seattle': 'seattle',
        'seahawks': 'seattle',
        'arizona': 'arizona',
        'cardinals': 'arizona',
        
        # NBA teams
        'lakers': 'los angeles lakers',
        'clippers': 'los angeles clippers',
        'warriors': 'golden state',
        'golden state': 'golden state',
        'gsw': 'golden state',
        'celtics': 'boston',
        'heat': 'miami',
        'spurs': 'san antonio',
        'mavs': 'dallas',
        'mavericks': 'dallas',
        'rockets': 'houston',
        'thunder': 'oklahoma city',
        'okc': 'oklahoma city',
        'blazers': 'portland',
        'trail blazers': 'portland',
        'nuggets': 'denver',
        'jazz': 'utah',
        'suns': 'phoenix',
        'kings': 'sacramento',
        'knicks': 'new york knicks',
        'nets': 'brooklyn',
        'sixers': 'philadelphia',
        '76ers': 'philadelphia',
        'bulls': 'chicago',
        'pistons': 'detroit',
        'pacers': 'indiana',
        'cavaliers': 'cleveland',
        'cavs': 'cleveland',
        'bucks': 'milwaukee',
        'hawks': 'atlanta',
        'hornets': 'charlotte',
        'magic': 'orlando',
        'wizards': 'washington',
        'raptors': 'toronto',
        
        # Soccer teams (common abbreviations)
        'man city': 'manchester city',
        'man utd': 'manchester united',
        'man united': 'manchester united',
        'liverpool': 'liverpool',
        'chelsea': 'chelsea',
        'arsenal': 'arsenal',
        'tottenham': 'tottenham',
        'spurs': 'tottenham',  # Note: conflicts with NBA, context matters
        'real madrid': 'real madrid',
        'barcelona': 'barcelona',
        'barca': 'barcelona',
        'atletico': 'atletico madrid',
        'valencia': 'valencia',
        'sevilla': 'sevilla'
    }
    
    # Apply normalizations
    for key, value in normalizations.items():
        if key == normalized or key in normalized:
            normalized = value
            break
    
    return normalized.strip()

def match_team_name(search_name: str, team_data: Dict[str, Any]) -> Tuple[float, str]:
    """
    Calculate match score between search name and team data using fuzzy matching.
    
    Args:
        search_name: Name to search for (normalized)
        team_data: Team data from ESPN API
        
    Returns:
        Tuple of (match_score, matched_field) where score is 0.0 to 1.0
    """
    # Get team names from data
    display_name = team_data.get('displayName', '').lower()
    abbrev = team_data.get('abbrev', '').lower()
    short_name = team_data.get('shortDisplayName', '').lower()
    name = team_data.get('name', '').lower()
    location = team_data.get('location', '').lower()
    
    # All possible team identifiers
    team_identifiers = [
        (display_name, 'displayName'),
        (abbrev, 'abbrev'),
        (short_name, 'shortDisplayName'),
        (name, 'name'),
        (location, 'location')
    ]
    
    best_score = 0.0
    best_field = 'unknown'
    
    for identifier, field_name in team_identifiers:
        if not identifier:
            continue
        
        # Exact matches get highest score
        if search_name == identifier:
            return 1.0, field_name
        
        # Fuzzy string matching using difflib
        similarity = difflib.SequenceMatcher(None, search_name, identifier).ratio()
        if similarity > best_score:
            best_score = similarity
            best_field = field_name
        
        # Check containment matches
        if search_name in identifier:
            containment_score = len(search_name) / len(identifier)
            if containment_score > best_score:
                best_score = containment_score
                best_field = field_name
        
        if identifier in search_name:
            containment_score = len(identifier) / len(search_name)
            if containment_score > best_score:
                best_score = containment_score
                best_field = field_name
    
    # Word-based matching for multi-word names
    search_words = set(search_name.split())
    display_words = set(display_name.split())
    
    if search_words and display_words:
        word_overlap = len(search_words & display_words) / len(search_words | display_words)
        if word_overlap > best_score:
            best_score = word_overlap
            best_field = 'word_overlap'
    
    return best_score, best_field

async def find_matching_teams(league: str, team1_name: str, team2_name: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Find team data that best matches the given team names using fuzzy matching.
    
    Args:
        league: League key (e.g., 'nfl', 'nba')
        team1_name: First team name to match
        team2_name: Second team name to match
        
    Returns:
        Tuple of (team1_data, team2_data) with match info or (None, None) if not found
    """
    try:
        # Get teams list for the league
        teams_response = await teams(league)
        
        if not teams_response.get('ok', True):
            logger.error(f"Failed to get teams for {league}")
            return None, None
        
        # Extract teams data
        teams_data = teams_response.get('data', {}).get('teams', [])
        if not teams_data:
            logger.error(f"No teams data found for {league}")
            return None, None
        
        # Normalize search names
        norm_team1 = normalize_team_name(team1_name)
        norm_team2 = normalize_team_name(team2_name)
        
        # Find best matches
        best_team1 = None
        best_team1_score = 0.0
        best_team1_field = 'unknown'
        best_team2 = None
        best_team2_score = 0.0
        best_team2_field = 'unknown'
        
        for team in teams_data:
            team_id = team.get('id')
            if not team_id:
                continue
            
            # Check match for team1
            score1, field1 = match_team_name(norm_team1, team)
            if score1 > best_team1_score:
                best_team1_score = score1
                best_team1 = team
                best_team1_field = field1
            
            # Check match for team2
            score2, field2 = match_team_name(norm_team2, team)
            if score2 > best_team2_score:
                best_team2_score = score2
                best_team2 = team
                best_team2_field = field2
        
        # Only return matches if they meet minimum threshold
        min_threshold = 0.3
        
        team1_result = None
        if best_team1_score >= min_threshold:
            team1_result = {
                'id': best_team1.get('id'),
                'displayName': best_team1.get('displayName', 'Unknown'),
                'abbrev': best_team1.get('abbrev', ''),
                'match_score': best_team1_score,
                'match_field': best_team1_field,
                'original_search': team1_name
            }
        
        team2_result = None
        if best_team2_score >= min_threshold:
            team2_result = {
                'id': best_team2.get('id'),
                'displayName': best_team2.get('displayName', 'Unknown'),
                'abbrev': best_team2.get('abbrev', ''),
                'match_score': best_team2_score,
                'match_field': best_team2_field,
                'original_search': team2_name
            }
        
        logger.debug(f"Team matching: '{team1_name}' -> {team1_result['id'] if team1_result else None} (score: {best_team1_score:.2f}, field: {best_team1_field})")
        logger.debug(f"Team matching: '{team2_name}' -> {team2_result['id'] if team2_result else None} (score: {best_team2_score:.2f}, field: {best_team2_field})")
        
        return team1_result, team2_result
        
    except Exception as e:
        logger.error(f"Error finding matching teams: {e}")
        return None, None

async def find_game_event(league: str, date: str, team1_id: str, team2_id: str) -> Optional[str]:
    """
    Find the event ID for a game between two teams on a specific date.
    
    Args:
        league: League key (e.g., 'nfl', 'nba')
        date: Date in YYYYMMDD format
        team1_id: First team ID
        team2_id: Second team ID
        
    Returns:
        Event ID if found, None otherwise
    """
    try:
        # Get scoreboard for the date
        scoreboard_response = await scoreboard(league, date)
        
        if not scoreboard_response.get('ok', True):
            logger.error(f"Failed to get scoreboard for {league} on {date}")
            return None
        
        # Extract events
        events = scoreboard_response.get('data', {}).get('scoreboard', {}).get('events', [])
        
        # Find matching game
        for event in events:
            home_team = event.get('home', {})
            away_team = event.get('away', {})
            
            home_id = home_team.get('id')
            away_id = away_team.get('id')
            
            # Check if this event matches our teams
            if ((home_id == team1_id and away_id == team2_id) or 
                (home_id == team2_id and away_id == team1_id)):
                return event.get('event_id')
        
        return None
        
    except Exception as e:
        logger.error(f"Error finding game event: {e}")
        return None

async def ask_game_question(league: str, date_input: str, team1_name: str, team2_name: str, question: str) -> None:
    """
    Ask a natural language question about a specific game with enhanced date and team resolution.
    
    Args:
        league: League key (e.g., 'nfl', 'nba')
        date_input: Date string ('today' or YYYYMMDD)
        team1_name: First team name
        team2_name: Second team name
        question: Question to ask about the game
    """
    try:
        # Resolve date with timezone information
        if date_input.lower() == 'today':
            actual_date, tz_info = get_today_date()
            date_used = f"today ({actual_date} {tz_info})"
        else:
            if not validate_date(date_input):
                print(f"❌ Error: Invalid date format '{date_input}'. Use YYYYMMDD format or 'today'.", file=sys.stderr)
                return
            actual_date = date_input
            date_used = actual_date
        
        print(f"🔍 Looking for {league.upper()} game: {team1_name} vs {team2_name} on {date_used}")
        
        # Find matching teams with enhanced fuzzy matching
        team1_data, team2_data = await find_matching_teams(league, team1_name, team2_name)
        
        if not team1_data:
            print(f"❌ Error: Could not find team matching '{team1_name}' in {league.upper()}", file=sys.stderr)
            print(f"   Try using the team's full name, city, or common abbreviation.", file=sys.stderr)
            return
        
        if not team2_data:
            print(f"❌ Error: Could not find team matching '{team2_name}' in {league.upper()}", file=sys.stderr)
            print(f"   Try using the team's full name, city, or common abbreviation.", file=sys.stderr)
            return
        
        # Display team matching results for user confirmation
        print(f"✅ Team 1: '{team1_name}' matched to {team1_data['displayName']} ({team1_data['abbrev']}) [score: {team1_data['match_score']:.2f}]")
        print(f"✅ Team 2: '{team2_name}' matched to {team2_data['displayName']} ({team2_data['abbrev']}) [score: {team2_data['match_score']:.2f}]")
        
        # Find the game event
        event_id = await find_game_event(league, actual_date, team1_data['id'], team2_data['id'])
        
        if not event_id:
            print(f"❌ Error: No game found between {team1_data['displayName']} and {team2_data['displayName']} on {date_used}", file=sys.stderr)
            print(f"   Check the date and team names. Games may not be scheduled for this date.", file=sys.stderr)
            return
        
        print(f"✅ Found game (Event ID: {event_id})")
        print(f"🤖 Analyzing game data to answer: \"{question}\"")
        print()
        
        # Use MCP analyze_game_strict for the answer
        analysis_response = await analyze_game_strict(league, event_id, question)
        
        if not analysis_response.get('ok', True):
            error_msg = analysis_response.get('message', 'Unknown error')
            print(f"❌ Error analyzing game: {error_msg}", file=sys.stderr)
            return
        
        # Extract and display the answer
        answer = analysis_response.get('content', 'No answer available')
        if isinstance(answer, dict):
            # If it's structured data, try to extract text content
            answer = answer.get('content', str(answer))
        
        print("📊 Analysis Result:")
        print("-" * 50)
        print(answer)
        print()
        
        # Enhanced metadata display
        print("📋 Query Metadata:")
        print(f"   📅 Date used: {date_used}")
        print(f"   🏟️  Event ID: {event_id}")
        print(f"   🏈 Teams: {team1_data['displayName']} vs {team2_data['displayName']}")
        print(f"   🎯 Team matching: {team1_data['match_field']} / {team2_data['match_field']}")
        
    except MCPValidationError as e:
        print(f"❌ Validation Error: {e}", file=sys.stderr)
    except MCPServerError as e:
        print(f"❌ Server Error: {e}", file=sys.stderr)
    except MCPError as e:
        print(f"❌ MCP Error: {e}", file=sys.stderr)
    except Exception as e:
        logger.error(f"Unexpected error in ask_game_question: {e}")
        print(f"❌ Unexpected error: {e}", file=sys.stderr)

def main():
    """Main entry point for the chat CLI."""
    parser = argparse.ArgumentParser(
        description="Natural language interface for sports game queries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ask nfl 20241215 Ravens vs Steelers "Who had more rushing yards?"
  %(prog)s ask nba today Lakers vs Warriors "What was the final score?"
  %(prog)s ask nfl today "Kansas City" vs "Buffalo" "How did Mahomes perform?"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Ask command
    ask_parser = subparsers.add_parser('ask', help='Ask a question about a specific game')
    ask_parser.add_argument('league', help='League (e.g., nfl, nba, mlb)')
    ask_parser.add_argument('date', help='Date (YYYYMMDD format or "today")')
    ask_parser.add_argument('team1', help='First team name (can be quoted)')
    ask_parser.add_argument('vs', help='Literal "vs" separator')
    ask_parser.add_argument('team2', help='Second team name (can be quoted)')
    ask_parser.add_argument('question', help='Question to ask about the game')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Validate league
    if args.league not in LEAGUE_MAPPING:
        supported = ', '.join(sorted(LEAGUE_MAPPING.keys()))
        print(f"❌ Error: Unsupported league '{args.league}'. Supported: {supported}", file=sys.stderr)
        sys.exit(1)
    
    # Validate vs separator
    if args.vs.lower() != 'vs':
        print(f"❌ Error: Expected 'vs' separator, got '{args.vs}'", file=sys.stderr)
        sys.exit(1)
    
    # Run async function
    try:
        asyncio.run(ask_game_question(args.league, args.date, args.team1, args.team2, args.question))
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()