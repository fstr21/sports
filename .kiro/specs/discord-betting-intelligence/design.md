# Design Document

## Overview

The Discord Sports Betting Intelligence Service is a daily automated system that collects comprehensive sports data, analyzes betting opportunities using AI, and delivers curated recommendations to Discord subscribers. The system leverages the existing Railway-deployed MCP infrastructure for efficient data collection and integrates with Discord for content delivery.

The service operates on a daily schedule, processing games across multiple sports leagues (NBA, WNBA, NFL, MLB, NHL, Soccer), collecting player statistics and betting lines, performing AI-powered analysis, and delivering formatted reports to subscribers.

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Discord Bot   │    │  Intelligence    │    │   Railway MCP   │
│   (Delivery)    │◄───│    Engine        │───►│   HTTP Server   │
└─────────────────┘    │  (Orchestrator)  │    └─────────────────┘
                       └──────────────────┘             │
                                │                       │
                       ┌──────────────────┐             │
                       │   OpenRouter     │             │
                       │   (AI Analysis)  │             │
                       └──────────────────┘             │
                                                        │
                              ┌─────────────────────────┼─────────────────────────┐
                              │                         │                         │
                    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                    │   ESPN API      │    │   Odds API      │    │  OpenRouter     │
                    │ (Game/Player    │    │ (Betting Lines) │    │ (AI Analysis)   │
                    │  Statistics)    │    │                 │    │                 │
                    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Architecture

The system consists of four main components:

1. **Intelligence Engine** - Core orchestration and analysis logic
2. **Railway MCP Interface** - Data collection from existing HTTP endpoints
3. **AI Analysis Module** - OpenRouter integration for bet recommendations
4. **Discord Delivery System** - Subscriber management and content delivery

## Components and Interfaces

### 1. Intelligence Engine (Core Orchestrator)

**Purpose**: Main application that coordinates daily data collection, analysis, and delivery.

**Key Classes**:
```python
class IntelligenceEngine:
    def run_daily_analysis(self) -> DailyReport
    def collect_sports_data(self) -> SportsDataCollection
    def analyze_betting_opportunities(self, data: SportsDataCollection) -> List[BetRecommendation]
    def generate_discord_report(self, recommendations: List[BetRecommendation]) -> DiscordReport

class SportsDataCollector:
    def get_daily_games(self, leagues: List[str]) -> List[Game]
    def get_player_stats(self, players: List[Player]) -> Dict[str, PlayerStats]
    def get_betting_lines(self, games: List[Game]) -> Dict[str, BettingLines]

class BetAnalyzer:
    def analyze_player_prop(self, prop: PlayerProp, stats: PlayerStats, opponent: Team) -> BetRecommendation
    def calculate_statistical_edge(self, line: float, recent_performance: List[float]) -> float
    def assess_matchup_advantage(self, player: Player, opponent: Team) -> float
```

**Configuration**:
```python
SUPPORTED_LEAGUES = [
    "basketball/nba", "basketball/wnba", 
    "football/nfl", "baseball/mlb", 
    "hockey/nhl", "soccer/eng.1"
]

PLAYER_PROP_MARKETS = {
    "basketball": ["player_points", "player_rebounds", "player_assists", "player_threes"],
    "football": ["player_pass_yds", "player_rush_yds", "player_receptions"],
    "baseball": ["batter_hits", "batter_home_runs", "pitcher_strikeouts"]
}
```

### 2. Railway MCP Interface

**Purpose**: Abstraction layer for communicating with the existing Railway HTTP server.

**Key Classes**:
```python
class RailwayMCPClient:
    def __init__(self, base_url: str, api_key: str)
    
    # ESPN Data Methods
    def get_scoreboard(self, sport: str, league: str) -> List[Game]
    def get_player_stats(self, sport: str, league: str, player_id: str) -> PlayerStats
    def get_team_stats(self, sport: str, league: str, team_id: str) -> TeamStats
    
    # Odds Data Methods  
    def get_game_odds(self, sport: str, markets: str) -> List[GameOdds]
    def get_player_props(self, sport: str, event_id: str, markets: str) -> PlayerPropsData
    
    # AI Analysis Methods
    def analyze_with_ai(self, question: str, context: dict) -> str

class APIUsageTracker:
    def track_call(self, endpoint: str, cost: int)
    def get_daily_usage(self) -> int
    def is_quota_available(self, estimated_cost: int) -> bool
```

**HTTP Endpoints Used**:
- `POST /espn/scoreboard` - Daily games
- `POST /espn/player-stats` - Player performance data  
- `POST /odds/get-odds` - Game-level betting lines
- `POST /odds/event-odds` - Player prop lines (efficient batch collection)
- `POST /natural-language` - AI analysis requests

### 3. AI Analysis Module

**Purpose**: Processes collected data to generate betting recommendations with explanations.

**Key Classes**:
```python
class BetRecommendationEngine:
    def analyze_game(self, game: Game, odds: GameOdds, player_data: Dict) -> List[BetRecommendation]
    def rank_recommendations(self, recommendations: List[BetRecommendation]) -> List[BetRecommendation]
    
class StatisticalAnalyzer:
    def calculate_player_trend(self, recent_games: List[float]) -> TrendAnalysis
    def assess_line_value(self, betting_line: float, expected_value: float, odds: int) -> ValueAssessment
    def factor_opponent_defense(self, player: Player, opponent: Team, stat_type: str) -> float

class AIExplanationGenerator:
    def generate_bet_explanation(self, recommendation: BetRecommendation) -> str
    def create_confidence_assessment(self, statistical_data: dict) -> ConfidenceLevel
```

**Analysis Workflow**:
1. **Statistical Edge Calculation**: Compare betting lines to recent performance averages
2. **Trend Analysis**: Identify hot/cold streaks and performance patterns  
3. **Matchup Assessment**: Factor in opponent defensive rankings and historical matchups
4. **Value Assessment**: Calculate implied probability vs. statistical probability
5. **AI Explanation**: Generate human-readable reasoning for each recommendation

### 4. Discord Delivery System

**Purpose**: Manages subscriber access and delivers formatted betting intelligence reports.

**Key Classes**:
```python
class DiscordBot:
    def send_daily_report(self, report: DailyReport, subscribers: List[str])
    def format_betting_recommendations(self, recommendations: List[BetRecommendation]) -> DiscordEmbed
    def handle_subscription_commands(self, user_id: str, command: str)

class SubscriberManager:
    def add_subscriber(self, user_id: str) -> bool
    def remove_subscriber(self, user_id: str) -> bool
    def get_active_subscribers(self) -> List[str]
    def verify_subscription_status(self, user_id: str) -> bool

class ReportFormatter:
    def create_daily_embed(self, date: str, recommendations: List[BetRecommendation]) -> DiscordEmbed
    def format_game_section(self, game: Game, bets: List[BetRecommendation]) -> str
    def create_summary_statistics(self, total_games: int, total_bets: int) -> str
```

## Data Models

### Core Data Structures

```python
@dataclass
class Game:
    id: str
    sport: str
    league: str
    home_team: str
    away_team: str
    start_time: datetime
    status: str

@dataclass
class PlayerStats:
    player_id: str
    name: str
    team: str
    recent_games: List[GameStats]  # Last 10 games
    season_averages: Dict[str, float]

@dataclass
class GameStats:
    date: datetime
    opponent: str
    points: float
    rebounds: float
    assists: float
    # Sport-specific stats...

@dataclass
class BettingLine:
    market: str
    player_name: str
    line_value: float
    over_odds: int
    under_odds: int
    bookmaker: str

@dataclass
class BetRecommendation:
    game_id: str
    bet_type: str  # "player_prop", "game_total", "spread"
    market: str    # "player_points", "game_total", etc.
    player_name: Optional[str]
    recommendation: str  # "OVER", "UNDER", "HOME", "AWAY"
    line_value: float
    odds: int
    confidence: float  # 0.0 to 1.0
    reasoning: str
    statistical_data: Dict[str, Any]

@dataclass
class DailyReport:
    date: datetime
    total_games: int
    total_recommendations: int
    recommendations_by_sport: Dict[str, List[BetRecommendation]]
    api_calls_used: int
    generation_time: float
```

### Database Schema (SQLite for simplicity)

```sql
-- Subscriber management
CREATE TABLE subscribers (
    user_id TEXT PRIMARY KEY,
    discord_username TEXT,
    subscription_start DATE,
    subscription_status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily report tracking
CREATE TABLE daily_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date DATE UNIQUE,
    total_games INTEGER,
    total_recommendations INTEGER,
    api_calls_used INTEGER,
    generation_time_seconds REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bet recommendation history
CREATE TABLE bet_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date DATE,
    game_id TEXT,
    sport TEXT,
    league TEXT,
    bet_type TEXT,
    market TEXT,
    player_name TEXT,
    recommendation TEXT,
    line_value REAL,
    odds INTEGER,
    confidence REAL,
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Error Handling

### API Error Management
```python
class APIErrorHandler:
    def handle_railway_timeout(self, endpoint: str) -> Optional[Any]
    def handle_quota_exceeded(self) -> None
    def handle_missing_data(self, data_type: str, game_id: str) -> None
    
    def retry_with_backoff(self, func: Callable, max_retries: int = 3) -> Any
```

**Error Scenarios**:
1. **Railway Server Unavailable**: Retry with exponential backoff, fallback to cached data
2. **API Quota Exceeded**: Prioritize high-value games, skip less important data
3. **Missing Player Data**: Continue with available players, note limitations in report
4. **Discord Delivery Failure**: Queue for retry, alert administrators
5. **AI Analysis Failure**: Use fallback statistical analysis, reduced explanations

### Data Quality Assurance
```python
class DataValidator:
    def validate_game_data(self, game: Game) -> bool
    def validate_player_stats(self, stats: PlayerStats) -> bool
    def validate_betting_lines(self, lines: List[BettingLine]) -> List[BettingLine]
    
    def filter_incomplete_data(self, recommendations: List[BetRecommendation]) -> List[BetRecommendation]
```

## Testing Strategy

### Unit Testing
- **Data Collection**: Mock Railway API responses, test parsing logic
- **Statistical Analysis**: Test edge calculation algorithms with known datasets
- **AI Integration**: Mock OpenRouter responses, test explanation generation
- **Discord Formatting**: Test embed generation and message formatting

### Integration Testing  
- **End-to-End Workflow**: Test complete daily analysis cycle with test data
- **API Integration**: Test actual Railway endpoints with rate limiting
- **Discord Bot**: Test message delivery and subscriber management
- **Error Scenarios**: Test graceful degradation and recovery

### Performance Testing
- **API Usage Optimization**: Verify efficient batch collection of player props
- **Memory Usage**: Test with full day's worth of data across all sports
- **Discord Rate Limits**: Test delivery to large subscriber base
- **Concurrent Processing**: Test parallel data collection and analysis

### Test Data Strategy
```python
# Mock data generators for testing
class TestDataGenerator:
    def generate_mock_games(self, sport: str, count: int) -> List[Game]
    def generate_mock_player_stats(self, player_id: str, games: int) -> PlayerStats
    def generate_mock_betting_lines(self, game: Game) -> List[BettingLine]
    
    def create_test_scenarios(self) -> Dict[str, TestScenario]
```

## Deployment and Operations

### Daily Execution Schedule
```python
# Cron-like scheduling
DAILY_SCHEDULE = {
    "data_collection": "08:00 EST",  # Morning data collection
    "analysis": "09:00 EST",         # AI analysis and recommendations  
    "delivery": "10:00 EST",         # Discord report delivery
    "cleanup": "23:00 EST"           # Daily cleanup and archival
}
```

### Monitoring and Alerting
- **API Usage Tracking**: Monitor daily quota consumption
- **Data Quality Metrics**: Track missing data percentages
- **Delivery Success Rate**: Monitor Discord message delivery
- **Performance Metrics**: Track analysis completion times
- **Error Rate Monitoring**: Alert on unusual error patterns

### Configuration Management
```python
# Environment-based configuration
class Config:
    RAILWAY_BASE_URL = os.getenv("RAILWAY_BASE_URL")
    RAILWAY_API_KEY = os.getenv("RAILWAY_API_KEY") 
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    # Analysis parameters
    RECOMMENDATIONS_PER_GAME = 5
    MIN_CONFIDENCE_THRESHOLD = 0.6
    MAX_API_CALLS_PER_DAY = 100
```

This design leverages your existing Railway infrastructure efficiently while providing a scalable foundation for the Discord betting intelligence service. The modular architecture allows for easy testing, maintenance, and future enhancements.