"""
Core data models for the Daily Betting Intelligence system.

This module defines the data structures used throughout the system for
game data, betting odds, player props, and analysis results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class GameData:
    """Represents a single game with metadata and team information."""
    event_id: str
    league: str
    home_team: str
    away_team: str
    game_time: datetime
    venue: str
    status: str  # pre-game, live, final
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    weather: Optional[str] = None
    additional_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TeamStats:
    """Team statistics and performance data."""
    team_name: str
    recent_performance: Dict[str, Any]
    key_players: List[str]
    injuries: List[str]
    season_record: Optional[str] = None
    last_5_games: Optional[List[str]] = None
    team_stats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BettingOdds:
    """Betting odds for a single game from a specific sportsbook."""
    event_id: str
    sportsbook: str
    moneyline_home: Optional[int] = None
    moneyline_away: Optional[int] = None
    spread_line: Optional[float] = None
    spread_home_odds: Optional[int] = None
    spread_away_odds: Optional[int] = None
    total_line: Optional[float] = None
    total_over_odds: Optional[int] = None
    total_under_odds: Optional[int] = None
    last_updated: Optional[datetime] = None
    additional_markets: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlayerProp:
    """Player proposition betting data."""
    player_name: str
    prop_type: str  # points, rebounds, assists, etc.
    line: float
    over_odds: int
    under_odds: int
    sportsbook: str
    event_id: str
    last_updated: Optional[datetime] = None
    player_position: Optional[str] = None
    season_average: Optional[float] = None


@dataclass
class GameAnalysis:
    """LLM-generated analysis results for a game."""
    event_id: str
    predicted_winner: str
    confidence_score: float
    key_factors: List[str]
    value_bets: List[Dict[str, Any]]
    risk_level: str  # low, medium, high
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    reasoning: str = ""
    matchup_advantages: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class PlayerAnalysis:
    """LLM-generated player analysis and prop recommendations."""
    player_name: str
    projected_stats: Dict[str, float]
    confidence_score: float
    prop_recommendations: List[Dict[str, Any]]
    reasoning: str
    event_id: str
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    injury_concerns: List[str] = field(default_factory=list)
    matchup_factors: List[str] = field(default_factory=list)


@dataclass
class ReportData:
    """Complete report data structure for a daily betting intelligence report."""
    target_date: str
    leagues_analyzed: List[str]
    total_games: int
    games_data: List[GameData]
    betting_odds: Dict[str, List[BettingOdds]]  # event_id -> odds list
    player_props: Dict[str, List[PlayerProp]]  # event_id -> props list
    game_analyses: Dict[str, GameAnalysis]  # event_id -> analysis
    player_analyses: Dict[str, List[PlayerAnalysis]]  # event_id -> player analyses
    generation_timestamp: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ErrorReport:
    """Error tracking and reporting structure."""
    error_type: str
    error_message: str
    context: str
    timestamp: datetime = field(default_factory=datetime.now)
    severity: str = "medium"  # low, medium, high, critical
    affected_component: Optional[str] = None