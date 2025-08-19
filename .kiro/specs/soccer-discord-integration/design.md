# Design Document

## Overview

The Soccer Discord Integration will extend the existing Discord bot architecture to support comprehensive soccer match management with automatic dual-endpoint analysis population. The system integrates with the Soccer MCP server (https://soccermcp-production.up.railway.app/mcp) using BOTH the H2H endpoint and matches endpoint to provide complete analysis similar to the schedule.py functionality.

**Key Innovation**: When `/create-channels` is used for soccer, each game channel is automatically populated with comprehensive analysis using three MCP calls per match:
1. **H2H Endpoint**: Direct head-to-head historical record between the two teams
2. **Matches Endpoint (Team 1)**: Recent 10 matches for home team individual analysis  
3. **Matches Endpoint (Team 2)**: Recent 10 matches for away team individual analysis

This dual-endpoint approach provides both historical head-to-head context AND detailed current form analysis, bridging the gap between the working schedule.py comprehensive analysis and the Discord bot integration.

## Architecture

### High-Level System Architecture

```
Discord Bot (bot_structure.py)
├── Command Handlers
│   ├── /create-channels (enhanced with automatic dual-endpoint analysis)
│   ├── /soccer-schedule (new)
│   ├── /soccer-odds (new)
│   ├── /soccer-h2h (new)
│   └── /soccer-standings (new)
├── Soccer Integration Module (new)
│   ├── SoccerMCPClient (dual-endpoint communication)
│   ├── SoccerDataProcessor (combines H2H + matches data)
│   ├── SoccerChannelManager (automatic population workflow)
│   └── SoccerEmbedBuilder (multi-embed generation)
├── Channel Management
│   ├── Category: "⚽ SOCCER"
│   ├── Automatic Analysis Population (3 MCP calls per channel)
│   └── Cleanup Automation
└── Data Sources (Dual-Endpoint Approach)
    ├── H2H Endpoint (direct team vs team history)
    ├── Matches Endpoint (individual team recent form)
    └── Betting Odds Integration
```

### Dual-Endpoint Data Flow

```
/create-channels (soccer) → Date Input → Fetch Daily Matches
                                            ↓
For Each Match Found:
├── Create Discord Channel
├── Post Match Preview Embed
├── [H2H Endpoint Call] → Historical Record Embed
├── [Matches Endpoint Call #1] → Home Team Analysis Embed  
├── [Matches Endpoint Call #2] → Away Team Analysis Embed
└── [Combined Analysis] → Betting Insights Embed

Result: 4-5 embeds per channel with comprehensive analysis
```

### Integration with Existing Bot Structure

The design extends the current `SportsBot` class with soccer-specific functionality:

```python
class SportsBot(commands.Bot):
    def __init__(self):
        # Existing initialization...
        
        # Enhanced league configurations
        self.leagues = {
            "NFL": {...},  # Existing
            "MLB": {...},  # Existing
            "SOCCER": {
                "emoji": "⚽",
                "active": True,
                "channels_per_day": 15,
                "supported_leagues": {
                    "EPL": {"id": 228, "name": "Premier League", "country": "England"},
                    "La Liga": {"id": 297, "name": "La Liga", "country": "Spain"},
                    "MLS": {"id": 168, "name": "MLS", "country": "USA"},
                    "Bundesliga": {"id": 241, "name": "Bundesliga", "country": "Germany"},
                    "Serie A": {"id": 253, "name": "Serie A", "country": "Italy"},
                    "UEFA": {"id": 310, "name": "UEFA Champions League", "country": "Europe"}
                }
            }
        }
        
        # Soccer-specific components
        self.soccer_client = SoccerMCPClient()
        self.soccer_processor = SoccerDataProcessor()
        self.soccer_channel_manager = SoccerChannelManager()
```

## Components and Interfaces

### 1. SoccerMCPClient

**Purpose**: Handle all communication with the Soccer MCP server using BOTH H2H endpoint AND matches endpoint for comprehensive analysis
**Location**: `discord/soccer_integration.py`

```python
class SoccerMCPClient:
    def __init__(self):
        self.mcp_url = "https://soccermcp-production.up.railway.app/mcp"
        self.supported_tools = [
            "get_betting_matches",        # For daily matches and team match history
            "get_h2h_betting_analysis",   # For direct H2H historical record
            "analyze_match_betting",
            "get_team_form_analysis",
            "get_league_value_bets"
        ]
    
    async def get_matches_for_date(self, date: str, league_filter: str = None) -> Dict
    async def get_h2h_direct_analysis(self, team1_id: int, team2_id: int, team1_name: str, team2_name: str) -> Dict  # H2H endpoint
    async def get_team_recent_matches(self, team_id: int, league_id: int, limit: int = 10) -> List[Dict]  # Matches endpoint for individual team
    async def get_comprehensive_match_analysis(self, home_team_id: int, away_team_id: int, home_team_name: str, away_team_name: str, league_id: int) -> Dict  # Combines both
    async def get_betting_odds(self, match_id: int) -> Dict
```

**Key Methods**:
- `call_mcp_tool()`: Generic MCP server communication
- `get_matches_for_date()`: Fetch matches for specific date across leagues using get_betting_matches
- `get_h2h_direct_analysis()`: Get direct head-to-head historical record using H2H endpoint (Team A vs Team B historical meetings)
- `get_team_recent_matches()`: Get recent 10 matches for individual team using matches endpoint (Team A's last 10 games regardless of opponent)
- `get_comprehensive_match_analysis()`: Combines BOTH H2H endpoint data AND matches endpoint data for complete analysis
- `find_recent_h2h_meetings()`: Search for actual H2H meetings using date-by-date match searches (supplement to H2H endpoint)
- `validate_date_format()`: Handle multiple date input formats

**Data Flow for Each Match Channel**:
1. **H2H Endpoint Call**: `get_h2h_direct_analysis(team1_id, team2_id)` → Historical head-to-head record
2. **Matches Endpoint Call #1**: `get_team_recent_matches(home_team_id, league_id, 10)` → Home team's last 10 matches
3. **Matches Endpoint Call #2**: `get_team_recent_matches(away_team_id, league_id, 10)` → Away team's last 10 matches
4. **Combined Analysis**: Process all three data sources into comprehensive analysis embeds

### 2. SoccerDataProcessor

**Purpose**: Process and normalize soccer data from dual-endpoint MCP responses, implementing schedule.py analysis methodology
**Location**: `discord/soccer_integration.py`

```python
class SoccerDataProcessor:
    def __init__(self):
        self.odds_converter = AmericanOddsConverter()
        self.team_name_cleaner = TeamNameCleaner()
    
    # Core data processing
    def process_match_data(self, raw_matches: Dict) -> List[ProcessedMatch]
    def extract_betting_odds(self, match_data: Dict) -> BettingOdds
    
    # H2H endpoint processing
    def process_h2h_historical_record(self, h2h_data: Dict) -> H2HHistoricalRecord
    def extract_h2h_statistics(self, h2h_response: Dict) -> Dict
    
    # Matches endpoint processing  
    def analyze_team_recent_matches(self, team_matches: List[Dict], team_name: str) -> TeamAnalysis
    def extract_comprehensive_match_data(self, match: Dict) -> Dict  # Following schedule.py structure
    def calculate_team_form_metrics(self, recent_matches: List[Dict]) -> Dict
    
    # Combined analysis
    def generate_combined_betting_recommendations(self, h2h_record: H2HHistoricalRecord, home_analysis: TeamAnalysis, away_analysis: TeamAnalysis) -> List[str]
    def create_comprehensive_match_insights(self, h2h_data: Dict, home_team_data: Dict, away_team_data: Dict) -> ComprehensiveInsights
```

**Key Responsibilities**:
- **Dual-Endpoint Processing**: Handle both H2H endpoint responses and matches endpoint responses
- **H2H Data Processing**: Extract direct head-to-head statistics (total meetings, wins/losses/draws, historical goals)
- **Individual Team Analysis**: Process recent 10 matches per team (W-L-D record, goals per game, clean sheets, card discipline)
- **Advanced Metrics Calculation**: Early/late goals, comeback frequency, home vs away splits, BTTS patterns
- **Combined Insights Generation**: Merge H2H historical patterns with current team form for enhanced betting recommendations
- **Data Validation**: Handle partial data scenarios (H2H available but matches missing, or vice versa)
- **Schedule.py Compatibility**: Implement same analysis methodology as working schedule.py script

### 3. SoccerChannelManager

**Purpose**: Manage soccer-specific Discord channel operations with automatic comprehensive H2H population
**Location**: `discord/soccer_integration.py`

```python
class SoccerChannelManager:
    def __init__(self, bot: SportsBot):
        self.bot = bot
        self.category_name = "⚽ SOCCER"
        self.channel_prefix = "📊"
        self.mcp_client = SoccerMCPClient()
        self.data_processor = SoccerDataProcessor()
        self.embed_builder = SoccerEmbedBuilder()
    
    async def create_match_channels_with_analysis(self, matches: List[ProcessedMatch], date: str) -> List[discord.TextChannel]
    async def populate_channel_with_comprehensive_analysis(self, channel: discord.TextChannel, match: ProcessedMatch)
    async def fetch_and_display_h2h_analysis(self, channel: discord.TextChannel, home_team_id: int, away_team_id: int, home_team_name: str, away_team_name: str, league_id: int)
    async def update_channel_content(self, channel: discord.TextChannel, match_data: ProcessedMatch)
    async def cleanup_old_channels(self, days_old: int = 3)
    def generate_channel_name(self, match: ProcessedMatch, date: str) -> str
```

**Channel Creation and Population Workflow**:
1. **Channel Creation**: Create channel with format `📊 {date_short}-{away_team}-vs-{home_team}`
2. **Initial Match Embed**: Post basic match details (teams, time, venue, odds)
3. **H2H Endpoint Analysis**: Fetch direct head-to-head historical record using H2H endpoint
4. **Matches Endpoint Analysis**: Fetch recent 10 matches for home team AND recent 10 matches for away team using matches endpoint
5. **Comprehensive Analysis**: Combine H2H data + both teams' recent form data into detailed analysis embeds
6. **Betting Recommendations**: Generate specific betting insights based on all collected data

**Channel Content Structure (4-5 Embeds per Channel)**:
- **Match Preview Embed**: Basic match information (teams, time, venue, odds)
- **H2H Historical Record Embed**: Direct head-to-head record from H2H endpoint (total meetings, wins/losses/draws)
- **Home Team Analysis Embed**: Recent 10 matches analysis from matches endpoint (form, goals, cards, clean sheets, etc.)
- **Away Team Analysis Embed**: Recent 10 matches analysis from matches endpoint (form, goals, cards, clean sheets, etc.)
- **Betting Insights Embed**: Specific recommendations based on H2H + both teams' recent form (Over/Under, BTTS, Cards markets)

**Data Sources Per Channel**:
- **1x H2H Endpoint Call**: Historical head-to-head between the two teams
- **2x Matches Endpoint Calls**: Recent matches for each team individually (10 matches each)
- **Total**: 3 MCP calls per match channel for comprehensive analysis

### 4. SoccerEmbedBuilder

**Purpose**: Create rich Discord embeds for soccer content
**Location**: `discord/soccer_integration.py`

```python
class SoccerEmbedBuilder:
    def __init__(self):
        self.colors = {
            "EPL": 0x3d195b,      # Premier League purple
            "La Liga": 0xff6900,   # La Liga orange
            "MLS": 0x005da6,       # MLS blue
            "Bundesliga": 0xd20515, # Bundesliga red
            "Serie A": 0x0066cc,   # Serie A blue
            "UEFA": 0x00336a       # UEFA dark blue
        }
    
    def create_match_preview_embed(self, match: ProcessedMatch) -> discord.Embed
    def create_h2h_analysis_embed(self, h2h_data: H2HInsights) -> discord.Embed
    def create_betting_odds_embed(self, odds: BettingOdds) -> discord.Embed
    def create_league_standings_embed(self, standings: Dict) -> discord.Embed
```

**Embed Templates**:
- **Match Preview**: Team info, odds, venue, time
- **H2H Analysis**: Historical records, recent form, betting insights
- **Live Updates**: Goals, cards, substitutions (future enhancement)
- **League Standings**: Current table positions and statistics

## Data Models

### ProcessedMatch

```python
@dataclass
class ProcessedMatch:
    match_id: int
    home_team: Team
    away_team: Team
    league: League
    date: str
    time: str
    venue: str
    status: str
    odds: Optional[BettingOdds]
    h2h_summary: Optional[H2HSummary]
    
    # New fields for dual-endpoint analysis
    h2h_historical_record: Optional[H2HHistoricalRecord] = None
    home_team_analysis: Optional[TeamAnalysis] = None
    away_team_analysis: Optional[TeamAnalysis] = None
    comprehensive_insights: Optional[ComprehensiveInsights] = None
```

### H2HHistoricalRecord (from H2H Endpoint)

```python
@dataclass
class H2HHistoricalRecord:
    total_meetings: int
    home_team_wins: int
    away_team_wins: int
    draws: int
    home_team_goals_total: int
    away_team_goals_total: int
    avg_goals_per_game: float
    last_meeting_date: Optional[str] = None
    last_meeting_result: Optional[str] = None
    
    @property
    def home_win_percentage(self) -> float:
        return (self.home_team_wins / self.total_meetings * 100) if self.total_meetings > 0 else 0.0
```

### TeamAnalysis (from Matches Endpoint)

```python
@dataclass
class TeamAnalysis:
    team_name: str
    recent_matches_count: int
    form_record: Dict[str, int]  # {"wins": 3, "draws": 1, "losses": 1}
    form_string: str  # "W-L-D-W-W"
    goals_per_game: float
    goals_against_per_game: float
    clean_sheet_percentage: float
    btts_percentage: float  # Both teams scored percentage
    high_scoring_percentage: float  # 3+ goals percentage
    card_discipline: Dict[str, float]  # {"yellow_per_game": 2.1, "red_total": 0}
    advanced_metrics: Dict[str, Any]  # Early goals, late drama, comeback wins, etc.
    
    @property
    def win_percentage(self) -> float:
        total_games = sum(self.form_record.values())
        return (self.form_record["wins"] / total_games * 100) if total_games > 0 else 0.0
```

### BettingOdds

```python
@dataclass
class BettingOdds:
    home_win: OddsFormat  # Decimal and American
    draw: OddsFormat
    away_win: OddsFormat
    over_under: Optional[OverUnder]
    handicap: Optional[Handicap]
    both_teams_score: Optional[OddsFormat]
```

### ComprehensiveInsights (Combined Analysis)

```python
@dataclass
class ComprehensiveInsights:
    # H2H insights
    h2h_dominance: str  # "home_team", "away_team", "balanced"
    h2h_goals_trend: str  # "high_scoring", "low_scoring", "average"
    
    # Combined team form insights
    form_momentum: str  # "home_advantage", "away_advantage", "neutral"
    expected_goals_total: float  # Based on both teams' recent scoring
    btts_probability: float  # Based on both teams' BTTS patterns
    
    # Betting recommendations (combining all data sources)
    over_under_recommendation: str  # "Over 2.5", "Under 2.5", "Neutral"
    btts_recommendation: str  # "BTTS Yes", "BTTS No", "Neutral"
    match_outcome_lean: str  # "Home Win", "Away Win", "Draw", "Neutral"
    cards_market_insight: str  # "High Cards", "Low Cards", "Average"
    
    # Supporting evidence
    recommendation_reasoning: List[str] = field(default_factory=list)
    confidence_level: str = "Medium"  # "High", "Medium", "Low"
    
    @classmethod
    def from_dual_endpoint_data(cls, h2h_record: H2HHistoricalRecord, 
                               home_analysis: TeamAnalysis, 
                               away_analysis: TeamAnalysis) -> 'ComprehensiveInsights':
        """Create comprehensive insights from both H2H and matches endpoint data"""
        # Implementation will combine all data sources for enhanced recommendations
        pass
```

### H2HInsights

```python
@dataclass
class H2HInsights:
    total_meetings: int
    home_team_wins: int
    away_team_wins: int
    draws: int
    avg_goals_per_game: float
    recent_form: Dict[str, List[str]]  # Last 5 matches per team
    betting_recommendations: List[str]
    key_statistics: Dict[str, Any]
```

## Error Handling

### MCP Server Communication

```python
class SoccerMCPError(Exception):
    """Base exception for Soccer MCP operations"""
    pass

class MCPConnectionError(SoccerMCPError):
    """MCP server connection issues"""
    pass

class MCPDataError(SoccerMCPError):
    """Invalid or missing data from MCP"""
    pass
```

**Error Handling Strategy**:
1. **Connection Failures**: Retry with exponential backoff, fallback to cached data
2. **Invalid Responses**: Log errors, provide user-friendly messages
3. **Missing Data**: Graceful degradation, partial information display
4. **Rate Limiting**: Implement request queuing and throttling

### Discord API Error Handling

```python
async def safe_channel_creation(self, match: ProcessedMatch) -> Optional[discord.TextChannel]:
    try:
        return await self.create_match_channel(match)
    except discord.HTTPException as e:
        if e.status == 429:  # Rate limited
            await asyncio.sleep(e.retry_after)
            return await self.create_match_channel(match)
        else:
            logger.error(f"Failed to create channel for {match}: {e}")
            return None
    except Exception as e:
        logger.error(f"Unexpected error creating channel: {e}")
        return None
```

## Testing Strategy

### Unit Tests

**Test Coverage Areas**:
1. **MCP Client**: Mock server responses, test data parsing
2. **Data Processor**: Odds conversion, team name cleaning
3. **Channel Manager**: Channel naming, cleanup logic
4. **Embed Builder**: Embed formatting, color schemes

```python
class TestSoccerMCPClient(unittest.TestCase):
    def setUp(self):
        self.client = SoccerMCPClient()
        self.mock_responses = load_test_data("soccer_mcp_responses.json")
    
    @patch('httpx.AsyncClient.post')
    async def test_get_matches_for_date(self, mock_post):
        mock_post.return_value.json.return_value = self.mock_responses['matches']
        result = await self.client.get_matches_for_date("17-08-2025")
        self.assertIsInstance(result, dict)
        self.assertIn('matches_by_league', result)
```

### Integration Tests

**Test Scenarios**:
1. **End-to-End Channel Creation**: Full workflow from command to channel
2. **MCP Server Integration**: Real API calls with test data
3. **Discord Bot Integration**: Command handling and response formatting
4. **Error Recovery**: Network failures, invalid data handling

### Performance Tests

**Metrics to Monitor**:
- MCP server response times
- Channel creation speed
- Memory usage during bulk operations
- Discord API rate limit compliance

## Security Considerations

### API Key Management

```python
# Environment variable configuration
SOCCER_MCP_URL = os.environ.get("SOCCER_MCP_URL", "https://soccermcp-production.up.railway.app/mcp")
AUTH_KEY = os.environ.get("AUTH_KEY")  # Soccer API authentication

if not AUTH_KEY:
    raise EnvironmentError("AUTH_KEY environment variable required for Soccer API")
```

### Input Validation

```python
def validate_date_input(date_string: str) -> str:
    """Validate and normalize date input"""
    allowed_formats = ["%m/%d/%Y", "%d-%m-%Y", "%Y-%m-%d"]
    
    for fmt in allowed_formats:
        try:
            parsed_date = datetime.strptime(date_string, fmt)
            # Validate date is not too far in past/future
            if not (datetime.now() - timedelta(days=30) <= parsed_date <= datetime.now() + timedelta(days=365)):
                raise ValueError("Date must be within 30 days past to 1 year future")
            return parsed_date.strftime("%d-%m-%Y")  # Normalize to Soccer API format
        except ValueError:
            continue
    
    raise ValueError(f"Invalid date format. Use MM/DD/YYYY, DD-MM-YYYY, or YYYY-MM-DD")
```

### Discord Permissions

**Required Bot Permissions**:
- `Send Messages`
- `Embed Links`
- `Manage Channels`
- `Use Slash Commands`
- `Read Message History`

**Permission Validation**:
```python
async def validate_bot_permissions(self, guild: discord.Guild) -> bool:
    """Ensure bot has required permissions"""
    bot_member = guild.get_member(self.bot.user.id)
    required_perms = discord.Permissions(
        send_messages=True,
        embed_links=True,
        manage_channels=True,
        use_slash_commands=True,
        read_message_history=True
    )
    
    return bot_member.guild_permissions >= required_perms
```

This design provides a comprehensive foundation for integrating soccer data into your Discord bot while maintaining consistency with your successful MLB implementation and leveraging the full capabilities of your existing Soccer MCP server.