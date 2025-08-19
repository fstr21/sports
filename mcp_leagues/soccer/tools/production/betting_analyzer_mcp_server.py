#!/usr/bin/env python3
"""
Enhanced Soccer Betting Analyzer MCP Server

A comprehensive MCP server for advanced soccer betting analysis using SoccerDataAPI.
Provides enhanced betting-focused tools for match analysis, team form assessment,
and value bet identification with confidence scoring.

Based on the standalone enhanced_betting_analyzer.py but converted for MCP protocol.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

# Configuration
SOCCER_API_BASE = "https://api.soccerdataapi.com"
USER_AGENT = "enhanced-betting-analyzer-mcp/1.0"
AUTH_TOKEN = os.environ.get("AUTH_KEY", "a9f37754a540df435e8c40ed89c08565166524ed")

if not AUTH_TOKEN:
    raise EnvironmentError("AUTH_KEY environment variable is required")

# Target leagues for betting analysis
TARGET_LEAGUES = {
    'MLS': {'id': 168, 'name': 'Major League Soccer', 'country': 'USA'},
    'EPL': {'id': 228, 'name': 'Premier League', 'country': 'England'},
    'LA LIGA': {'id': 297, 'name': 'La Liga', 'country': 'Spain'},
    'BUNDESLIGA': {'id': 241, 'name': 'Bundesliga', 'country': 'Germany'},
    'SERIE A': {'id': 253, 'name': 'Serie A', 'country': 'Italy'},
    'UEFA': {'id': 310, 'name': 'UEFA Champions League', 'country': 'Europe'}
}

# HTTP client
_http_client: Optional[httpx.AsyncClient] = None

async def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            headers={
                "User-Agent": USER_AGENT,
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip"
            },
            timeout=30.0
        )
    return _http_client

async def close_http_client():
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None

# Utility Functions

def validate_and_convert_date(date_string: str) -> Optional[str]:
    """Validate and convert date to DD-MM-YYYY format"""
    formats_to_try = [
        "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%y", "%d/%m/%y"
    ]
    
    for date_format in formats_to_try:
        try:
            parsed_date = datetime.strptime(date_string, date_format)
            return parsed_date.strftime("%d-%m-%Y")
        except ValueError:
            continue
    return None

def convert_to_american_odds(decimal_odds) -> str:
    """Convert decimal odds to American format"""
    try:
        decimal = float(decimal_odds)
        if decimal >= 2.0:
            american = int((decimal - 1) * 100)
            return f"+{american}"
        else:
            american = int(-100 / (decimal - 1))
            return str(american)
    except (ValueError, ZeroDivisionError):
        return str(decimal_odds)

def calculate_form_rating(form_chars: List[str]) -> float:
    """Calculate weighted form rating (0-10)"""
    if not form_chars:
        return 5.0
    
    # Weight recent games more heavily
    weights = [3, 2.5, 2, 1.5, 1.2, 1, 1, 1, 1, 1]
    score = 0
    
    for i, result in enumerate(form_chars[:10]):
        weight = weights[i] if i < len(weights) else 1
        if result == 'W':
            score += 3 * weight
        elif result == 'D':
            score += 1 * weight
    
    max_possible = sum(weights[:len(form_chars[:10])]) * 3
    rating = (score / max_possible) * 10 if max_possible > 0 else 5.0
    
    return round(rating, 1)

def calculate_momentum(form_chars: List[str]) -> str:
    """Calculate team momentum"""
    if len(form_chars) < 3:
        return 'Insufficient Data'
    
    last_3 = form_chars[:3]
    last_5 = form_chars[:5] if len(form_chars) >= 5 else form_chars
    
    wins_last_3 = last_3.count('W')
    wins_last_5 = last_5.count('W')
    
    if wins_last_3 >= 2:
        return 'Strong Upward'
    elif wins_last_5 >= 3:
        return 'Upward'
    elif last_3.count('L') >= 2:
        return 'Downward'
    elif last_5.count('L') >= 3:
        return 'Strong Downward'
    else:
        return 'Stable'

async def api_call(endpoint: str, params: Dict, silent: bool = False) -> Optional[Dict]:
    """Make API call with error handling and rate limiting"""
    params['auth_token'] = AUTH_TOKEN
    url = f"{SOCCER_API_BASE}/{endpoint}"
    
    try:
        client = await get_http_client()
        response = await client.get(url, params=params)
        response.raise_for_status()
        await asyncio.sleep(0.1)  # Rate limiting
        return response.json()
    except Exception as e:
        if not silent:
            print(f"API Error: {e}")
        return None

# MCP Tool Implementations

async def get_betting_matches(date: str, league_filter: Optional[str] = None) -> Dict[str, Any]:
    """Get matches for betting analysis on specified date
    
    Args:
        date: Match date in DD-MM-YYYY format
        league_filter: Optional league filter (MLS, EPL, La Liga)
    """
    # Validate date
    api_date = validate_and_convert_date(date)
    if not api_date:
        return {
            "error": f"Invalid date format: {date}. Use DD-MM-YYYY, DD/MM/YYYY, YYYY-MM-DD, or MM/DD/YYYY",
            "supported_formats": ["DD-MM-YYYY", "DD/MM/YYYY", "YYYY-MM-DD", "MM/DD/YYYY"]
        }
    
    # Filter leagues if specified
    leagues_to_search = TARGET_LEAGUES
    if league_filter:
        league_filter = league_filter.upper()
        if league_filter in TARGET_LEAGUES:
            leagues_to_search = {league_filter: TARGET_LEAGUES[league_filter]}
        else:
            return {
                "error": f"Unknown league: {league_filter}",
                "supported_leagues": list(TARGET_LEAGUES.keys())
            }
    
    all_matches = {}
    
    for league_code, league_info in leagues_to_search.items():
        matches_data = await api_call('matches/', {
            'league_id': league_info['id'],
            'date': api_date
        })
        
        if matches_data:
            matches = extract_matches_from_response(matches_data)
            for match in matches:
                match['league_code'] = league_code
                match['league_info'] = league_info
            
            all_matches[league_code] = matches
        else:
            all_matches[league_code] = []
    
    return {
        "date": api_date,
        "matches_by_league": all_matches,
        "total_matches": sum(len(matches) for matches in all_matches.values()),
        "leagues_searched": list(leagues_to_search.keys())
    }

def extract_matches_from_response(response_data) -> List[Dict]:
    """Extract matches from API response, filtering out invalid matches"""
    matches = []
    if not response_data or not isinstance(response_data, list):
        return matches
    
    for league_data in response_data:
        if isinstance(league_data, dict):
            raw_matches = []
            if 'matches' in league_data:
                raw_matches.extend(league_data['matches'])
            elif 'stage' in league_data:
                for stage in league_data['stage']:
                    if 'matches' in stage:
                        raw_matches.extend(stage['matches'])
            
            for match in raw_matches:
                if is_valid_match(match):
                    matches.append(match)
    
    return matches

def is_valid_match(match: Dict) -> bool:
    """Check if match has valid team data"""
    teams = match.get('teams', {})
    home_team = teams.get('home', {})
    away_team = teams.get('away', {})
    
    home_name = home_team.get('name', '').strip()
    away_name = away_team.get('name', '').strip()
    
    if not home_name or not away_name:
        return False
    if home_name.lower() in ['none', 'null', 'undefined', 'tbd']:
        return False
    if away_name.lower() in ['none', 'null', 'undefined', 'tbd']:
        return False
    
    return True

async def analyze_match_betting(home_team: str, away_team: str, league: str, match_date: str) -> Dict[str, Any]:
    """Comprehensive betting analysis for a specific match
    
    Args:
        home_team: Home team name
        away_team: Away team name  
        league: League code (MLS, EPL, La Liga)
        match_date: Match date in DD-MM-YYYY format
    """
    league = league.upper()
    if league not in TARGET_LEAGUES:
        return {
            "error": f"Unsupported league: {league}",
            "supported_leagues": list(TARGET_LEAGUES.keys())
        }
    
    # Get matches for the date to find the specific match
    matches_result = await get_betting_matches(match_date, league)
    
    if "error" in matches_result:
        return matches_result
    
    # Find the specific match
    target_match = None
    for matches in matches_result["matches_by_league"].values():
        for match in matches:
            teams = match.get('teams', {})
            home_name = teams.get('home', {}).get('name', '')
            away_name = teams.get('away', {}).get('name', '')
            
            if (home_team.lower() in home_name.lower() and 
                away_team.lower() in away_name.lower()):
                target_match = match
                break
    
    if not target_match:
        return {
            "error": f"Match not found: {home_team} vs {away_team} on {match_date}",
            "available_matches": [
                f"{m.get('teams', {}).get('home', {}).get('name', 'TBD')} vs {m.get('teams', {}).get('away', {}).get('name', 'TBD')}"
                for matches in matches_result["matches_by_league"].values()
                for m in matches
            ]
        }
    
    # Extract team IDs
    teams = target_match.get('teams', {})
    home_team_id = teams.get('home', {}).get('id')
    away_team_id = teams.get('away', {}).get('id')
    home_team_name = teams.get('home', {}).get('name', home_team)
    away_team_name = teams.get('away', {}).get('name', away_team)
    
    if not home_team_id or not away_team_id:
        return {"error": "Could not extract team IDs for analysis"}
    
    league_id = TARGET_LEAGUES[league]['id']
    
    # Get team analyses
    home_analysis = await get_team_form_analysis(home_team_id, home_team_name, league_id)
    away_analysis = await get_team_form_analysis(away_team_id, away_team_name, league_id)
    
    # Get H2H analysis
    h2h_analysis = await get_h2h_betting_analysis(home_team_id, away_team_id, home_team_name, away_team_name)
    
    # Generate predictions
    predictions = generate_betting_predictions(home_analysis, away_analysis, {
        'home_team_id': home_team_id,
        'away_team_id': away_team_id,
        'home_team_name': home_team_name,
        'away_team_name': away_team_name,
        'league_id': league_id
    })
    
    return {
        "match_info": {
            "home_team": home_team_name,
            "away_team": away_team_name,
            "league": TARGET_LEAGUES[league]['name'],
            "date": match_date,
            "odds": target_match.get('odds', {}),
            "status": target_match.get('status', 'scheduled')
        },
        "team_analysis": {
            "home": home_analysis,
            "away": away_analysis
        },
        "head_to_head": h2h_analysis,
        "predictions": predictions,
        "confidence_level": predictions.get('confidence', 'Medium')
    }

async def get_team_form_analysis(team_id: int, team_name: str, league_id: int) -> Dict[str, Any]:
    """Get comprehensive team form analysis for betting
    
    Args:
        team_id: Team ID from SoccerDataAPI
        team_name: Team name
        league_id: League ID
    """
    # Get recent matches using season-based search
    current_season = "2025-2026"  # Updated for current season
    season_matches = await api_call('matches/', {
        'league_id': league_id,
        'season': current_season
    }, silent=True)
    
    team_matches = []
    
    if season_matches:
        matches = extract_matches_from_response(season_matches)
        
        for match in matches:
            if (team_played_in_match(team_id, match) and 
                match.get('status') == 'finished'):
                
                match_date = match.get('date', '')
                if match_date:
                    try:
                        parsed_date = datetime.strptime(match_date, "%d/%m/%Y")
                        team_matches.append({
                            'match': match,
                            'date': match_date,
                            'parsed_date': parsed_date,
                            'is_home': is_team_home(team_id, match)
                        })
                    except ValueError:
                        team_matches.append({
                            'match': match,
                            'date': match_date,
                            'parsed_date': datetime.now(),
                            'is_home': is_team_home(team_id, match)
                        })
    
    # Sort by date (most recent first) and limit to 10
    team_matches.sort(key=lambda x: x['parsed_date'], reverse=True)
    team_matches = team_matches[:10]
    
    return analyze_team_form_advanced(team_matches, team_name)

def analyze_team_form_advanced(team_matches: List[Dict], team_name: str) -> Dict:
    """Advanced form analysis with betting insights"""
    if not team_matches:
        return {
            'team_name': team_name,
            'matches_found': 0,
            'form_rating': 0,
            'momentum': 'Unknown',
            'betting_trends': {}
        }
    
    wins = draws = losses = 0
    goals_for = goals_against = 0
    form_chars = []
    home_record = {'wins': 0, 'draws': 0, 'losses': 0}
    away_record = {'wins': 0, 'draws': 0, 'losses': 0}
    recent_scores = []
    
    for match_info in team_matches:
        match = match_info['match']
        is_home = match_info['is_home']
        
        teams = match.get('teams', {})
        goals = match.get('goals', {})
        
        home_goals = goals.get('home_ft_goals', 0)
        away_goals = goals.get('away_ft_goals', 0)
        
        if is_home:
            team_goals = home_goals
            opponent_goals = away_goals
            record = home_record
        else:
            team_goals = away_goals
            opponent_goals = home_goals
            record = away_record
        
        goals_for += team_goals
        goals_against += opponent_goals
        recent_scores.append((team_goals, opponent_goals))
        
        # Determine result
        if team_goals > opponent_goals:
            wins += 1
            record['wins'] += 1
            form_chars.append('W')
        elif team_goals < opponent_goals:
            losses += 1
            record['losses'] += 1
            form_chars.append('L')
        else:
            draws += 1
            record['draws'] += 1
            form_chars.append('D')
    
    total_games = len(team_matches)
    win_percentage = (wins / total_games * 100) if total_games > 0 else 0
    
    # Advanced metrics
    form_rating = calculate_form_rating(form_chars)
    momentum = calculate_momentum(form_chars)
    attacking_strength = goals_for / total_games if total_games > 0 else 0
    defensive_strength = goals_against / total_games if total_games > 0 else 0
    
    # Betting trends analysis
    betting_trends = analyze_betting_trends(recent_scores, form_chars)
    
    return {
        'team_name': team_name,
        'matches_found': total_games,
        'record': f"{wins}W-{draws}D-{losses}L",
        'win_percentage': win_percentage,
        'form_string': ''.join(form_chars),
        'form_rating': form_rating,
        'momentum': momentum,
        'goals_for': goals_for,
        'goals_against': goals_against,
        'attacking_strength': attacking_strength,
        'defensive_strength': defensive_strength,
        'home_record': home_record,
        'away_record': away_record,
        'betting_trends': betting_trends,
        'matches_summary': {
            'total_matches': len(team_matches),
            'recent_dates': [match_info['date'] for match_info in team_matches[:5]]
        }
    }

def analyze_betting_trends(recent_scores: List[Tuple], form_chars: List[str]) -> Dict:
    """Analyze betting trends for over/under and other markets"""
    if not recent_scores:
        return {}
    
    total_goals = [sum(score) for score in recent_scores]
    over_2_5 = sum(1 for goals in total_goals if goals > 2.5)
    over_3_5 = sum(1 for goals in total_goals if goals > 3.5)
    
    both_scored = sum(1 for score in recent_scores if score[0] > 0 and score[1] > 0)
    clean_sheets = sum(1 for score in recent_scores if score[1] == 0)
    
    total_matches = len(recent_scores)
    
    return {
        'avg_total_goals': sum(total_goals) / total_matches if total_matches > 0 else 0,
        'over_2_5_percentage': (over_2_5 / total_matches * 100) if total_matches > 0 else 0,
        'over_3_5_percentage': (over_3_5 / total_matches * 100) if total_matches > 0 else 0,
        'both_teams_score_percentage': (both_scored / total_matches * 100) if total_matches > 0 else 0,
        'clean_sheet_percentage': (clean_sheets / total_matches * 100) if total_matches > 0 else 0
    }

async def get_h2h_betting_analysis(team_1_id: int, team_2_id: int, team_1_name: str, team_2_name: str) -> Dict[str, Any]:
    """Get historical head-to-head analysis with betting insights
    
    Args:
        team_1_id: First team ID
        team_2_id: Second team ID
        team_1_name: First team name
        team_2_name: Second team name
    """
    h2h_data = await api_call('head-to-head/', {
        'team_1_id': team_1_id,
        'team_2_id': team_2_id
    })
    
    if not h2h_data:
        return {
            "error": "Historical H2H data not available",
            "teams": f"{team_1_name} vs {team_2_name}"
        }
    
    stats = h2h_data.get('stats', {})
    overall = stats.get('overall', {})
    
    if not overall:
        return {
            "error": "No historical statistics available",
            "teams": f"{team_1_name} vs {team_2_name}"
        }
    
    total_games = overall.get('overall_games_played', 0)
    team_1_wins = overall.get('overall_team1_wins', 0)
    team_2_wins = overall.get('overall_team2_wins', 0)
    draws = overall.get('overall_draws', 0)
    team_1_goals = overall.get('overall_team1_scored', 0)
    team_2_goals = overall.get('overall_team2_scored', 0)
    
    if total_games == 0:
        return {
            "error": "No historical matches found",
            "teams": f"{team_1_name} vs {team_2_name}"
        }
    
    # Enhanced H2H metrics
    team_1_win_rate = (team_1_wins / total_games) * 100
    team_2_win_rate = (team_2_wins / total_games) * 100
    draw_rate = (draws / total_games) * 100
    avg_goals_per_game = (team_1_goals + team_2_goals) / total_games
    
    # Betting insights from H2H
    if avg_goals_per_game > 2.8:
        goals_trend = "HIGH-SCORING fixture (Over 2.5 historically likely)"
    elif avg_goals_per_game < 2.2:
        goals_trend = "LOW-SCORING fixture (Under 2.5 historically likely)"
    else:
        goals_trend = "MODERATE-SCORING fixture"
    
    return {
        "teams": f"{team_1_name} vs {team_2_name}",
        "total_meetings": total_games,
        "team_1_record": {
            "name": team_1_name,
            "wins": team_1_wins,
            "win_rate": team_1_win_rate
        },
        "team_2_record": {
            "name": team_2_name,
            "wins": team_2_wins,
            "win_rate": team_2_win_rate
        },
        "draws": {
            "count": draws,
            "rate": draw_rate
        },
        "goals": {
            "average_per_game": avg_goals_per_game,
            "team_1_total": team_1_goals,
            "team_2_total": team_2_goals
        },
        "betting_insights": {
            "goals_trend": goals_trend,
            "high_scoring": avg_goals_per_game > 2.8,
            "low_scoring": avg_goals_per_game < 2.2
        }
    }

def generate_betting_predictions(home_analysis: Dict, away_analysis: Dict, match_info: Dict) -> Dict[str, Any]:
    """Generate comprehensive betting predictions"""
    
    # Match winner prediction
    home_score = calculate_team_strength_score(home_analysis, True)  # Home advantage
    away_score = calculate_team_strength_score(away_analysis, False)
    
    confidence = calculate_prediction_confidence(home_analysis, away_analysis)
    
    if home_score > away_score + 10:
        prediction = f"{home_analysis['team_name']} Win (Strong)"
        confidence_level = "High" if confidence > 70 else "Medium"
    elif away_score > home_score + 10:
        prediction = f"{away_analysis['team_name']} Win (Strong)"
        confidence_level = "High" if confidence > 70 else "Medium"
    elif home_score > away_score + 5:
        prediction = f"{home_analysis['team_name']} Win (Moderate)"
        confidence_level = "Medium"
    elif away_score > home_score + 5:
        prediction = f"{away_analysis['team_name']} Win (Moderate)"
        confidence_level = "Medium"
    else:
        prediction = "Close Match (Draw or Either Team)"
        confidence_level = "Low"
    
    # Enhanced goals prediction with H2H integration
    home_trends = home_analysis.get('betting_trends', {})
    away_trends = away_analysis.get('betting_trends', {})
    
    goals_prediction = "No prediction available"
    expected_goals = 2.5
    goals_confidence = "Low"
    team_over_percentage = 50
    
    if home_trends and away_trends:
        # Calculate team-based expected goals
        team_expected_goals = (home_trends.get('avg_total_goals', 2.5) + 
                             away_trends.get('avg_total_goals', 2.5)) / 2
        
        team_over_percentage = (home_trends.get('over_2_5_percentage', 50) + 
                              away_trends.get('over_2_5_percentage', 50)) / 2
        
        # Get H2H data to factor in historical trends
        h2h_goals = get_h2h_goals_average(match_info['home_team_id'], match_info['away_team_id'])
        
        # Weight team trends (70%) vs H2H trends (30%)
        if h2h_goals:
            expected_goals = (team_expected_goals * 0.7) + (h2h_goals * 0.3)
        else:
            expected_goals = team_expected_goals
        
        # More nuanced thresholds
        if expected_goals > 2.7 or team_over_percentage > 60:
            goals_prediction = "Over 2.5 Goals"
            if expected_goals > 3.0 and team_over_percentage > 70:
                goals_confidence = "High"
            elif expected_goals > 2.8 or team_over_percentage > 65:
                goals_confidence = "Medium"
            else:
                goals_confidence = "Low-Medium"
        elif expected_goals < 2.3 or team_over_percentage < 40:
            goals_prediction = "Under 2.5 Goals"
            if expected_goals < 2.0 and team_over_percentage < 30:
                goals_confidence = "High"
            elif expected_goals < 2.1 or team_over_percentage < 35:
                goals_confidence = "Medium"
            else:
                goals_confidence = "Low-Medium"
        else:
            goals_prediction = "Around 2.5 Goals (Lean slightly based on team trends)"
            if team_over_percentage > 50:
                goals_prediction = "Slight lean to Over 2.5 Goals"
            elif team_over_percentage < 50:
                goals_prediction = "Slight lean to Under 2.5 Goals"
            goals_confidence = "Low"
    
    # Key betting insights
    insights = []
    insights.append(f"Home Team Form: {home_analysis['form_rating']}/10 ({home_analysis['momentum']})")
    insights.append(f"Away Team Form: {away_analysis['form_rating']}/10 ({away_analysis['momentum']})")
    
    if home_analysis['form_rating'] > 7.5 and home_analysis['momentum'] in ['Strong Upward', 'Upward']:
        insights.append(f"{home_analysis['team_name']} in excellent form - consider backing")
    elif away_analysis['form_rating'] > 7.5 and away_analysis['momentum'] in ['Strong Upward', 'Upward']:
        insights.append(f"{away_analysis['team_name']} in excellent form - consider backing")
    
    if home_analysis['momentum'] == 'Strong Downward':
        insights.append(f"{home_analysis['team_name']} in poor form - avoid backing")
    elif away_analysis['momentum'] == 'Strong Downward':
        insights.append(f"{away_analysis['team_name']} in poor form - avoid backing")
    
    return {
        "match_winner": {
            "prediction": prediction,
            "confidence": confidence_level,
            "confidence_percentage": confidence,
            "home_strength_score": home_score,
            "away_strength_score": away_score
        },
        "goals": {
            "prediction": goals_prediction,
            "expected_goals": expected_goals,
            "team_over_percentage": team_over_percentage,
            "confidence": goals_confidence
        },
        "key_insights": insights,
        "confidence": confidence_level
    }

def get_h2h_goals_average(team_1_id: int, team_2_id: int) -> Optional[float]:
    """Get historical H2H goals average for prediction weighting (sync version for prediction)"""
    # This is a simplified version - in async context, we'd need to handle this differently
    # For now, returning None to use team trends only
    return None

def calculate_team_strength_score(analysis: Dict, is_home: bool) -> float:
    """Calculate overall team strength score"""
    score = 0
    
    # Form rating (40% weight)
    score += analysis.get('form_rating', 5) * 8
    
    # Win percentage (30% weight)
    score += analysis.get('win_percentage', 50) * 0.6
    
    # Momentum bonus (20% weight)
    momentum = analysis.get('momentum', 'Stable')
    if momentum == 'Strong Upward':
        score += 20
    elif momentum == 'Upward':
        score += 10
    elif momentum == 'Downward':
        score -= 10
    elif momentum == 'Strong Downward':
        score -= 20
    
    # Home advantage (10% weight)
    if is_home:
        score += 10
    
    return score

def calculate_prediction_confidence(home_analysis: Dict, away_analysis: Dict) -> float:
    """Calculate confidence in prediction based on data quality"""
    confidence = 50  # Base confidence
    
    # Data availability
    home_matches = home_analysis.get('matches_found', 0)
    away_matches = away_analysis.get('matches_found', 0)
    
    if home_matches >= 8 and away_matches >= 8:
        confidence += 20
    elif home_matches >= 5 and away_matches >= 5:
        confidence += 10
    
    # Form difference
    form_diff = abs(home_analysis.get('form_rating', 5) - away_analysis.get('form_rating', 5))
    if form_diff > 2:
        confidence += 15
    elif form_diff > 1:
        confidence += 10
    
    # Momentum alignment
    home_momentum = home_analysis.get('momentum', 'Stable')
    away_momentum = away_analysis.get('momentum', 'Stable')
    
    if (home_momentum in ['Strong Upward', 'Upward'] and 
        away_momentum in ['Strong Downward', 'Downward']):
        confidence += 15
    elif (away_momentum in ['Strong Upward', 'Upward'] and 
          home_momentum in ['Strong Downward', 'Downward']):
        confidence += 15
    
    return min(confidence, 95)  # Cap at 95%

def team_played_in_match(team_id: int, match: Dict) -> bool:
    """Check if team played in match"""
    teams = match.get('teams', {})
    home_id = teams.get('home', {}).get('id')
    away_id = teams.get('away', {}).get('id')
    return team_id in [home_id, away_id]

def is_team_home(team_id: int, match: Dict) -> bool:
    """Check if team was playing at home"""
    teams = match.get('teams', {})
    home_id = teams.get('home', {}).get('id')
    return team_id == home_id

async def get_league_value_bets(league: str, date: str, min_confidence: float = 60.0) -> Dict[str, Any]:
    """Find potential value bets across all matches in a league
    
    Args:
        league: League code (MLS, EPL, La Liga)
        date: Match date in DD-MM-YYYY format
        min_confidence: Minimum confidence percentage for recommendations (default 60.0)
    """
    # Get all matches for the league and date
    matches_result = await get_betting_matches(date, league)
    
    if "error" in matches_result:
        return matches_result
    
    value_bets = []
    league_matches = matches_result["matches_by_league"].get(league.upper(), [])
    
    for match in league_matches:
        teams = match.get('teams', {})
        home_name = teams.get('home', {}).get('name', '')
        away_name = teams.get('away', {}).get('name', '')
        
        if not home_name or not away_name:
            continue
        
        try:
            # Analyze the match
            analysis = await analyze_match_betting(home_name, away_name, league, date)
            
            if "error" not in analysis:
                predictions = analysis.get('predictions', {})
                match_winner = predictions.get('match_winner', {})
                goals = predictions.get('goals', {})
                
                confidence = match_winner.get('confidence_percentage', 0)
                
                if confidence >= min_confidence:
                    value_bet = {
                        "match": f"{home_name} vs {away_name}",
                        "league": league.upper(),
                        "date": date,
                        "recommended_bet": match_winner.get('prediction', 'N/A'),
                        "confidence": f"{confidence:.1f}%",
                        "confidence_level": match_winner.get('confidence', 'Medium'),
                        "goals_prediction": goals.get('prediction', 'N/A'),
                        "expected_goals": goals.get('expected_goals', 0),
                        "key_insights": predictions.get('key_insights', []),
                        "odds": match.get('odds', {}),
                        "home_form": analysis['team_analysis']['home']['form_rating'],
                        "away_form": analysis['team_analysis']['away']['form_rating']
                    }
                    value_bets.append(value_bet)
        
        except Exception as e:
            continue  # Skip matches that can't be analyzed
    
    return {
        "league": league.upper(),
        "date": date,
        "min_confidence_threshold": min_confidence,
        "total_matches_analyzed": len(league_matches),
        "value_bets_found": len(value_bets),
        "value_bets": value_bets,
        "summary": {
            "high_confidence_bets": len([bet for bet in value_bets if float(bet['confidence'].rstrip('%')) >= 80]),
            "medium_confidence_bets": len([bet for bet in value_bets if 60 <= float(bet['confidence'].rstrip('%')) < 80]),
            "avg_confidence": sum(float(bet['confidence'].rstrip('%')) for bet in value_bets) / len(value_bets) if value_bets else 0
        }
    }

# MCP Server Implementation

MCP_TOOLS = [
    {
        "name": "get_betting_matches",
        "description": "Get soccer matches for betting analysis on a specific date. Supports filtering by league (MLS, EPL, La Liga).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string", 
                    "description": "Match date in DD-MM-YYYY, DD/MM/YYYY, YYYY-MM-DD, or MM/DD/YYYY format"
                },
                "league_filter": {
                    "type": "string",
                    "description": "Optional league filter: MLS, EPL, or La Liga",
                    "enum": ["MLS", "EPL", "La Liga"]
                }
            },
            "required": ["date"]
        }
    },
    {
        "name": "analyze_match_betting",
        "description": "Comprehensive betting analysis for a specific soccer match including team form, H2H history, and predictions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "home_team": {
                    "type": "string",
                    "description": "Home team name (partial matches accepted)"
                },
                "away_team": {
                    "type": "string", 
                    "description": "Away team name (partial matches accepted)"
                },
                "league": {
                    "type": "string",
                    "description": "League code",
                    "enum": ["MLS", "EPL", "La Liga"]
                },
                "match_date": {
                    "type": "string",
                    "description": "Match date in DD-MM-YYYY format"
                }
            },
            "required": ["home_team", "away_team", "league", "match_date"]
        }
    },
    {
        "name": "get_team_form_analysis", 
        "description": "Get comprehensive team form analysis including recent results, momentum, and betting trends.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "team_id": {
                    "type": "integer",
                    "description": "Team ID from SoccerDataAPI"
                },
                "team_name": {
                    "type": "string",
                    "description": "Team name for display"
                },
                "league_id": {
                    "type": "integer", 
                    "description": "League ID (168=MLS, 228=EPL, 297=La Liga)"
                }
            },
            "required": ["team_id", "team_name", "league_id"]
        }
    },
    {
        "name": "get_h2h_betting_analysis",
        "description": "Get historical head-to-head analysis between two teams with betting insights.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "team_1_id": {
                    "type": "integer",
                    "description": "First team ID"
                },
                "team_2_id": {
                    "type": "integer", 
                    "description": "Second team ID"
                },
                "team_1_name": {
                    "type": "string",
                    "description": "First team name"
                },
                "team_2_name": {
                    "type": "string",
                    "description": "Second team name"
                }
            },
            "required": ["team_1_id", "team_2_id", "team_1_name", "team_2_name"]
        }
    },
    {
        "name": "get_league_value_bets",
        "description": "Find potential value bets across all matches in a league for a specific date.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "league": {
                    "type": "string",
                    "description": "League code",
                    "enum": ["MLS", "EPL", "La Liga"]
                },
                "date": {
                    "type": "string",
                    "description": "Match date in DD-MM-YYYY format"
                },
                "min_confidence": {
                    "type": "number",
                    "description": "Minimum confidence percentage for recommendations (default 60.0)",
                    "minimum": 0,
                    "maximum": 100,
                    "default": 60.0
                }
            },
            "required": ["league", "date"]
        }
    }
]

async def handle_mcp_request(request: Request) -> Response:
    """Handle MCP protocol requests"""
    try:
        body = await request.json()
        
        # Handle different MCP methods
        method = body.get("method")
        
        if method == "tools/list":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "tools": MCP_TOOLS
                }
            })
        
        elif method == "tools/call":
            params = body.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            result = None
            
            if tool_name == "get_betting_matches":
                result = await get_betting_matches(**arguments)
            elif tool_name == "analyze_match_betting":
                result = await analyze_match_betting(**arguments)
            elif tool_name == "get_team_form_analysis":
                result = await get_team_form_analysis(**arguments)
            elif tool_name == "get_h2h_betting_analysis":
                result = await get_h2h_betting_analysis(**arguments)
            elif tool_name == "get_league_value_bets":
                result = await get_league_value_bets(**arguments)
            else:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }, status_code=400)
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            })
        
        else:
            return JSONResponse({
                "jsonrpc": "2.0", 
                "id": body.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Unknown method: {method}"
                }
            }, status_code=400)
    
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": body.get("id", None),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }, status_code=500)

async def health_check(request: Request) -> Response:
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "server": "enhanced-soccer-betting-analyzer-mcp",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

# Starlette application
routes = [
    Route("/", health_check, methods=["GET"]),
    Route("/mcp", handle_mcp_request, methods=["POST"]),
]

app = Starlette(routes=routes)

@app.on_event("startup")
async def startup():
    print("Enhanced Soccer Betting Analyzer MCP Server starting up...")
    print(f"AUTH_TOKEN configured: {'Yes' if AUTH_TOKEN else 'No'}")
    print(f"Target leagues: {list(TARGET_LEAGUES.keys())}")

@app.on_event("shutdown") 
async def shutdown():
    await close_http_client()
    print("Enhanced Soccer Betting Analyzer MCP Server shutting down...")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)