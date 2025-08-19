# Soccer Discord Integration - Complete Documentation

## Overview

The Soccer Discord Integration provides comprehensive soccer match management for Discord servers, integrating with the Soccer MCP server to deliver real-time match data, betting odds, and detailed analytics across six major soccer leagues.

## Architecture

### Core Components

```
Soccer Integration System
├── SoccerMCPClient          # MCP server communication
├── SoccerDataProcessor      # Data processing and normalization
├── SoccerEmbedBuilder       # Discord embed creation
├── SoccerChannelManager     # Channel management
├── SoccerConfiguration      # Configuration management
└── Data Models              # ProcessedMatch, Team, League, etc.
```

### Supported Leagues

| League Code | Name | Country | Priority | Color |
|-------------|------|---------|----------|-------|
| `UEFA` | UEFA Champions League | Europe | 0 (Highest) | #00336a |
| `EPL` | Premier League | England | 1 | #3d195b |
| `La Liga` | La Liga | Spain | 2 | #ff6900 |
| `Bundesliga` | Bundesliga | Germany | 3 | #d20515 |
| `Serie A` | Serie A | Italy | 4 | #0066cc |
| `MLS` | MLS | USA | 5 | #005da6 |

## Discord Commands

### Administrative Commands

#### `/create-channels`
Creates soccer game channels for a specific date.

**Usage:**
```
/create-channels sport:Soccer date:08/19/2025
```

**Parameters:**
- `sport`: Select "Soccer" from dropdown
- `date`: Date in MM/DD/YYYY, DD-MM-YYYY, or YYYY-MM-DD format

**Example Response:**
```
✅ Soccer Channels Created
Successfully created 8 soccer match channels for 2025-08-19

📊 Created Channels
1. #📊-08-19-arsenal-vs-liverpool
2. #📊-08-19-real-madrid-vs-barcelona
3. #📊-08-19-bayern-vs-dortmund
...

🏆 Leagues
⚽ Premier League: 3 matches
⚽ La Liga: 2 matches
⚽ Bundesliga: 2 matches
⚽ UEFA Champions League: 1 match
```

### User Commands

#### `/soccer-schedule`
Display upcoming soccer matches for the current day.

**Usage:**
```
/soccer-schedule [league:EPL] [date:08/19/2025]
```

**Parameters:**
- `league` (optional): Filter by specific league
- `date` (optional): Specific date (defaults to today)

#### `/soccer-odds`
Get betting odds for a specific matchup.

**Usage:**
```
/soccer-odds team1:Arsenal team2:Liverpool
```

**Parameters:**
- `team1`: First team name
- `team2`: Second team name

#### `/soccer-h2h`
Get comprehensive head-to-head analysis between two teams.

**Usage:**
```
/soccer-h2h team1:Arsenal team2:Liverpool
```

**Parameters:**
- `team1`: First team name
- `team2`: Second team name

#### `/soccer-standings`
Display current league table for a specific league.

**Usage:**
```
/soccer-standings league:EPL
```

**Parameters:**
- `league`: League code (EPL, La Liga, MLS, Bundesliga, Serie A, UEFA)

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
    odds: Optional[BettingOdds] = None
    h2h_summary: Optional[H2HInsights] = None
```

### Team
```python
@dataclass
class Team:
    id: int
    name: str
    short_name: str
    logo_url: Optional[str] = None
    country: Optional[str] = None
    standing: Optional[TeamStanding] = None
    
    @property
    def clean_name(self) -> str:
        """Get cleaned team name for channel creation"""
        return self.name.lower().replace(' ', '-').replace('.', '').replace('&', 'and')
```

### BettingOdds
```python
@dataclass
class BettingOdds:
    home_win: OddsFormat
    draw: OddsFormat
    away_win: OddsFormat
    over_under: Optional[OverUnder] = None
    both_teams_score: Optional[OddsFormat] = None
```

### League
```python
@dataclass
class League:
    id: int
    name: str
    country: str
    season: Optional[str] = None
    priority: int = 999
    tournament_type: str = "league"  # "league" or "knockout"
```

## Channel Management

### Channel Naming Convention
```
📊 {date_short}-{away_team}-vs-{home_team}
```

**Examples:**
- `📊 08-19-liverpool-vs-arsenal`
- `📊 08-19-barcelona-vs-real-madrid`
- `📊 08-19-bayern-vs-dortmund`

### Channel Content

Each soccer match channel contains:

1. **Match Preview Embed**
   - Team names and logos
   - Match date, time, and venue
   - League information
   - Current betting odds (if available)

2. **Head-to-Head Analysis** (on request)
   - Historical record between teams
   - Recent form (last 5-10 matches)
   - Betting recommendations
   - Advanced statistics

3. **League Context**
   - Current league positions
   - Points and goal difference
   - Recent form indicators

### Automatic Cleanup

- Channels older than 3 days are automatically deleted
- Channels with recent activity are preserved
- Pinned messages prevent automatic deletion
- Cleanup statistics are logged for administrators

## Configuration

### Environment Variables

```bash
# Required
DISCORD_BOT_TOKEN=your_discord_bot_token

# Optional
SOCCER_MCP_URL=https://soccermcp-production.up.railway.app/mcp
AUTH_KEY=your_auth_key_for_mcp_server
SOCCER_LEAGUES_CONFIG={"EPL":{"active":true},"CUSTOM":{"id":999,"name":"Custom League"}}
```

### Configuration Validation

The system automatically validates configuration on startup:

```
✅ Configuration modules loaded successfully
✅ Environment validation passed
✅ Startup checks passed

📊 Configuration Summary:
   Soccer MCP URL: https://soccermcp-production.up.railway.app/mcp
   Authentication: Enabled
   Active Leagues: UEFA, EPL, La Liga, Bundesliga, Serie A, MLS
   Max Matches/Day: 50
   Channel Retention: 3 days
```

### Feature Flags

```python
FEATURES = {
    "soccer_integration": True,
    "multi_league_support": True,
    "h2h_analysis": True,
    "betting_recommendations": True,
    "league_standings": True,
    "advanced_statistics": True,
    "channel_auto_cleanup": True
}
```

## Error Handling

### MCP Server Errors

```python
# Connection failures
try:
    matches = await client.get_matches_for_date("2025-08-19")
except ConnectionError:
    # Retry with exponential backoff
    # Fall back to cached data if available
    # Display user-friendly error message
```

### Discord API Errors

```python
# Rate limiting
try:
    channel = await guild.create_text_channel(name)
except discord.HTTPException as e:
    if e.status == 429:  # Rate limited
        await asyncio.sleep(e.retry_after)
        # Retry channel creation
```

### Data Validation Errors

```python
# Invalid match data
if not match_data or 'home_team' not in match_data:
    logger.warning(f"Invalid match data: {match_data}")
    return None  # Skip this match
```

## Testing

### Test Suite Coverage

The comprehensive test suite covers:

- **Unit Tests**: Individual component functionality
- **Integration Tests**: End-to-end workflow testing
- **Configuration Tests**: Environment and setup validation
- **Performance Tests**: Load and stress testing
- **Error Handling Tests**: Failure scenario testing

### Running Tests

```bash
# Run all soccer integration tests
python test_soccer_integration_corrected.py

# Run specific test categories
python -m pytest -k "soccer" -v

# Run configuration tests
python test_soccer_config.py

# Validate configuration
python validate_config.py
```

### Test Results

```
🧪 Running Corrected Soccer Integration Test Suite
============================================================
test_client_initialization ... ok
test_supported_leagues_config ... ok
test_decimal_to_american_odds_conversion ... ok
test_process_match_data_empty_input ... ok
test_process_match_data_valid_input ... ok
...

============================================================
🏁 Test Summary:
   Tests run: 20
   Failures: 0
   Errors: 0
   Success rate: 100.0%
```

## Deployment

### Railway Deployment

1. **Set Environment Variables:**
   ```bash
   DISCORD_BOT_TOKEN=your_discord_bot_token
   SOCCER_MCP_URL=https://soccermcp-production.up.railway.app/mcp
   AUTH_KEY=your_auth_key
   ```

2. **Deploy:**
   ```bash
   railway up
   ```

3. **Verify Deployment:**
   ```bash
   # Check logs for successful startup
   railway logs
   
   # Look for:
   # ✅ Configuration validation completed successfully
   # ✅ Soccer configuration startup checks completed successfully
   # Bot has connected to Discord!
   ```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY discord/ ./discord/
COPY .env .

# Validate configuration during build
RUN python discord/validate_config.py

CMD ["python", "discord/bot_structure.py"]
```

### Health Checks

Monitor these endpoints/logs for system health:

- **Bot Connection**: Discord connection status
- **MCP Server**: Soccer MCP server response times
- **Channel Creation**: Successful channel creation rates
- **Error Rates**: Configuration and runtime errors
- **Memory Usage**: Bot memory consumption

## Troubleshooting

### Common Issues

#### 1. Bot Not Responding to Commands
```
❌ Issue: Commands not working
✅ Solution: 
   - Check DISCORD_BOT_TOKEN is valid
   - Verify bot has required permissions
   - Run /sync command to update slash commands
```

#### 2. No Soccer Matches Found
```
❌ Issue: "No matches found for date"
✅ Solution:
   - Verify Soccer MCP server is accessible
   - Check date format (MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD)
   - Ensure leagues are active for that date
```

#### 3. Channel Creation Fails
```
❌ Issue: Channels not being created
✅ Solution:
   - Check bot has "Manage Channels" permission
   - Verify server hasn't reached channel limit
   - Check for Discord API rate limiting
```

#### 4. MCP Server Connection Issues
```
❌ Issue: "MCP server unavailable"
✅ Solution:
   - Verify SOCCER_MCP_URL is correct
   - Check AUTH_KEY if authentication is required
   - Test MCP server connectivity manually
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.getLogger('soccer_integration').setLevel(logging.DEBUG)
logging.getLogger('soccer_config').setLevel(logging.DEBUG)
```

### Support Channels

For additional support:

1. Check the configuration guide: `SOCCER_CONFIGURATION_GUIDE.md`
2. Run configuration validation: `python validate_config.py`
3. Review test results: `python test_soccer_integration_corrected.py`
4. Check Discord bot logs for specific error messages

## Performance Optimization

### Rate Limiting

The system implements intelligent rate limiting:

- **Burst Protection**: Up to 10 rapid requests
- **Sustained Rate**: 30 requests per minute
- **Hourly Limit**: 1800 requests per hour
- **Exponential Backoff**: Automatic retry with increasing delays

### Caching

- **Match Data**: Cached for 15 minutes
- **League Standings**: Cached for 1 hour
- **Team Information**: Cached for 24 hours

### Memory Management

- **Channel Cleanup**: Automatic cleanup after 3 days
- **Data Structures**: Efficient dataclasses for memory usage
- **Logging**: Rotating logs to prevent disk space issues

## Future Enhancements

### Planned Features

1. **Live Match Updates**
   - Real-time goal notifications
   - Card and substitution updates
   - Match status changes

2. **Advanced Analytics**
   - Player statistics integration
   - Team performance metrics
   - Betting trend analysis

3. **User Preferences**
   - Favorite team notifications
   - Custom league filters
   - Personalized betting insights

4. **Mobile Integration**
   - Push notifications
   - Mobile-optimized embeds
   - Quick action buttons

### API Extensions

1. **Additional Leagues**
   - Ligue 1 (France)
   - Eredivisie (Netherlands)
   - Liga MX (Mexico)

2. **Tournament Support**
   - World Cup integration
   - European Championships
   - Copa America

3. **Enhanced Data**
   - Player injury reports
   - Weather conditions
   - Referee assignments

This documentation provides a complete guide to the Soccer Discord Integration system, covering all aspects from basic usage to advanced configuration and troubleshooting.