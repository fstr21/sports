# Design Document

## Overview

The Soccer Discord Integration will extend the existing Discord bot architecture to support comprehensive soccer match management, following the proven patterns from the successful MLB implementation. The system will integrate with the existing Soccer MCP server (https://soccermcp-production.up.railway.app/mcp) to provide real-time match data, betting odds, and detailed analytics across six major soccer leagues.

The design leverages the existing bot structure while adding soccer-specific functionality through new command handlers, data processing modules, and channel management systems. The architecture maintains consistency with the current MLB implementation while accommodating soccer's unique characteristics (draws, multiple leagues, tournament structures).

## Architecture

### High-Level System Architecture

```
Discord Bot (bot_structure.py)
├── Command Handlers
│   ├── /create-channels (enhanced with soccer support)
│   ├── /soccer-schedule (new)
│   ├── /soccer-odds (new)
│   ├── /soccer-h2h (new)
│   └── /soccer-standings (new)
├── Soccer Integration Module (new)
│   ├── SoccerMCPClient
│   ├── SoccerDataProcessor
│   ├── SoccerChannelManager
│   └── SoccerEmbedBuilder
├── Channel Management
│   ├── Category: "⚽ SOCCER"
│   ├── Channel Creation Logic
│   └── Cleanup Automation
└── Data Sources
    ├── Soccer MCP Server (primary)
    ├── Betting Odds Integration
    └── H2H Analysis Engine
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

**Purpose**: Handle all communication with the Soccer MCP server
**Location**: `discord/soccer_integration.py`

```python
class SoccerMCPClient:
    def __init__(self):
        self.mcp_url = "https://soccermcp-production.up.railway.app/mcp"
        self.supported_tools = [
            "get_matches",
            "get_head_to_head", 
            "get_league_standings",
            "get_match_details",
            "get_team_info"
        ]
    
    async def get_matches_for_date(self, date: str, league_filter: str = None) -> Dict
    async def get_h2h_analysis(self, team1_id: int, team2_id: int) -> Dict
    async def get_betting_odds(self, match_id: int) -> Dict
    async def get_league_standings(self, league_id: int) -> Dict
```

**Key Methods**:
- `call_mcp_tool()`: Generic MCP server communication
- `get_matches_for_date()`: Fetch matches for specific date across leagues
- `get_comprehensive_match_data()`: Get detailed match information with odds
- `get_h2h_analysis()`: Retrieve head-to-head statistics
- `validate_date_format()`: Handle multiple date input formats

### 2. SoccerDataProcessor

**Purpose**: Process and normalize soccer data from MCP responses
**Location**: `discord/soccer_integration.py`

```python
class SoccerDataProcessor:
    def __init__(self):
        self.odds_converter = AmericanOddsConverter()
        self.team_name_cleaner = TeamNameCleaner()
    
    def process_match_data(self, raw_matches: Dict) -> List[ProcessedMatch]
    def extract_betting_odds(self, match_data: Dict) -> BettingOdds
    def calculate_h2h_insights(self, h2h_data: Dict) -> H2HInsights
    def generate_betting_recommendations(self, match_analysis: Dict) -> List[str]
```

**Key Responsibilities**:
- Convert decimal odds to American format
- Clean and standardize team names for channel creation
- Extract comprehensive match statistics
- Generate betting insights and recommendations
- Handle missing or incomplete data gracefully

### 3. SoccerChannelManager

**Purpose**: Manage soccer-specific Discord channel operations
**Location**: `discord/soccer_integration.py`

```python
class SoccerChannelManager:
    def __init__(self, bot: SportsBot):
        self.bot = bot
        self.category_name = "⚽ SOCCER"
        self.channel_prefix = "📊"
    
    async def create_match_channels(self, matches: List[ProcessedMatch], date: str) -> List[discord.TextChannel]
    async def update_channel_content(self, channel: discord.TextChannel, match_data: ProcessedMatch)
    async def cleanup_old_channels(self, days_old: int = 3)
    def generate_channel_name(self, match: ProcessedMatch, date: str) -> str
```

**Channel Naming Convention**:
- Format: `📊 {date_short}-{away_team}-vs-{home_team}`
- Example: `📊 08-17-liverpool-vs-arsenal`
- Maximum length: 100 characters (Discord limit)
- Special character handling for team names

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