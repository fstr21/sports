# Soccer Slash Commands Documentation

This document provides comprehensive documentation for all soccer-specific slash commands implemented in the Discord bot.

## Overview

The soccer integration adds four new slash commands that provide comprehensive soccer data and analysis:

1. `/soccer-schedule` - Display upcoming matches
2. `/soccer-odds` - Get betting odds for specific matchups
3. `/soccer-h2h` - Comprehensive head-to-head analysis
4. `/soccer-standings` - Current league table display

All commands integrate with the Soccer MCP server to provide real-time data across six major leagues: EPL, La Liga, MLS, Bundesliga, Serie A, and UEFA Champions League.

## Commands

### `/soccer-schedule`

**Description:** Display upcoming soccer matches for current day or specified date

**Parameters:**
- `league` (optional): Filter by specific league
  - Choices: Premier League, La Liga, MLS, Bundesliga, Serie A, UEFA Champions League
- `date` (optional): Date in MM/DD/YYYY, DD-MM-YYYY, or YYYY-MM-DD format (defaults to today)

**Usage Examples:**
```
/soccer-schedule
/soccer-schedule league:Premier League
/soccer-schedule date:08/18/2025
/soccer-schedule league:La Liga date:2025-08-20
```

**Response Format:**
- Embed with matches grouped by league
- Shows team names, match times, and venues
- Summary of total matches across leagues
- Suggestion to use `/create-channels` for match discussions

**Error Handling:**
- Invalid date format: Shows format requirements
- No matches found: Informative message with date
- MCP server error: Connection failure message
- General errors: Graceful error handling

### `/soccer-odds`

**Description:** Get betting odds for a specific soccer matchup

**Parameters:**
- `team1` (required): First team name (away team)
- `team2` (required): Second team name (home team)  
- `date` (optional): Date in MM/DD/YYYY, DD-MM-YYYY, or YYYY-MM-DD format (defaults to today)

**Usage Examples:**
```
/soccer-odds team1:Arsenal team2:Liverpool
/soccer-odds team1:Barcelona team2:"Real Madrid" date:08/20/2025
/soccer-odds team1:Chelsea team2:City
```

**Response Format:**
- Detailed betting odds embed with league-specific colors
- Moneyline odds (1X2) in both decimal and American formats
- Over/Under totals when available
- Both Teams to Score (BTTS) odds
- Handicap/Spread betting lines
- Betting insights and recommendations
- Match information (date, time, venue)

**Team Matching:**
- Case-insensitive partial matching
- Works with both full names and common abbreviations
- Searches both home and away team positions

**Error Handling:**
- Match not found: Helpful message with tips
- No odds available: Shows match info without odds
- Invalid date: Format error message
- MCP server error: Connection failure handling

### `/soccer-h2h`

**Description:** Get comprehensive head-to-head analysis between two teams

**Parameters:**
- `team1` (required): First team name
- `team2` (required): Second team name

**Usage Examples:**
```
/soccer-h2h team1:Arsenal team2:Liverpool
/soccer-h2h team1:Barcelona team2:"Real Madrid"
/soccer-h2h team1:Chelsea team2:Tottenham
```

**Response Format:**
- Comprehensive H2H analysis embed
- Overall meeting statistics (wins, draws, losses)
- Win percentages for each team
- Average goals per game
- Recent form (last 5-10 matches per team)
- Key statistics (cards, clean sheets, etc.)
- Betting recommendations based on historical data
- Historical trend analysis

**Team Discovery:**
- Searches recent matches (last 7 days) to find team IDs
- Uses partial name matching for flexibility
- Requires teams to have played recently to be found

**Error Handling:**
- Teams not found: Clear message with spelling tips
- No H2H data: Informative message about data availability
- MCP server error: Connection failure handling
- Processing errors: Graceful error recovery

### `/soccer-standings`

**Description:** Display current league table for a soccer league

**Parameters:**
- `league` (required): Select the league to display standings for
  - Choices: Premier League, La Liga, MLS, Bundesliga, Serie A, UEFA Champions League

**Usage Examples:**
```
/soccer-standings league:"Premier League"
/soccer-standings league:"La Liga"
/soccer-standings league:MLS
```

**Response Format:**
- League-specific colored embed
- Formatted table showing top 10 teams
- Position, team name, games played, wins, draws, losses
- Goals for, goals against, goal difference, points
- Legend explaining abbreviations
- Note if showing partial table (more than 10 teams)

**Table Format:**
```
Pos Team                 P  W  D  L  GF GA GD Pts
──────────────────────────────────────────────────
 1. Arsenal              10  8  1  1  25  8 +17  25
 2. Liverpool            10  7  2  1  22 10 +12  23
```

**Error Handling:**
- No standings data: Clear message about availability
- MCP server error: Connection failure handling
- Invalid league: Unsupported league message

## Parameter Validation

### Date Format Validation

The `validate_date_input()` function accepts multiple date formats:

**Supported Formats:**
- `MM/DD/YYYY` (e.g., "08/18/2025")
- `DD-MM-YYYY` (e.g., "18-08-2025")  
- `YYYY-MM-DD` (e.g., "2025-08-18")

**Validation Rules:**
- Date must be within 30 days past to 1 year future
- Invalid dates (e.g., February 30) are rejected
- All formats are normalized to YYYY-MM-DD for MCP server

**Error Messages:**
- Clear format requirements shown to users
- Specific guidance on acceptable date ranges

### Team Name Matching

**Matching Strategy:**
- Case-insensitive comparison
- Partial name matching (e.g., "Arsenal" matches "Arsenal FC")
- Bidirectional matching (team1 can match either home or away)
- Works with common abbreviations and short names

**Examples:**
- "Arsenal" matches "Arsenal FC", "Arsenal F.C.", "ARS"
- "Real Madrid" matches "Real Madrid CF", "Madrid", "RMA"
- "Man City" matches "Manchester City", "City", "MCFC"

## Error Handling

### MCP Server Errors

**Connection Failures:**
- Clear error messages about server connectivity
- Suggestion to try again later
- No crash or undefined behavior

**Data Errors:**
- Graceful handling of missing or invalid data
- Partial information display when possible
- Clear messages about what data is unavailable

### User Input Errors

**Invalid Parameters:**
- Helpful error messages with examples
- Format requirements clearly stated
- Suggestions for correct usage

**No Results Found:**
- Informative messages explaining why no results
- Tips for better search terms or date selection
- Guidance on using other commands

### General Error Recovery

**Exception Handling:**
- All commands wrapped in try-catch blocks
- Logging of errors for debugging
- User-friendly error messages
- No bot crashes or undefined states

## Integration with Existing Features

### Channel Creation Integration

The `/soccer-schedule` command integrates with the existing `/create-channels` command:
- Schedule shows available matches
- Footer suggests using `/create-channels` for discussions
- Consistent date format handling between commands

### League Configuration

All commands use the centralized `SUPPORTED_LEAGUES` configuration:
- Consistent league IDs across commands
- League-specific colors and emojis
- Centralized league metadata management

### Embed Styling

Commands use league-specific styling:
- Premier League: Purple (#3d195b)
- La Liga: Orange (#ff6900)
- MLS: Blue (#005da6)
- Bundesliga: Red (#d20515)
- Serie A: Blue (#0066cc)
- UEFA: Dark Blue (#00336a)

## Performance Considerations

### MCP Server Communication

**Optimization Strategies:**
- Single MCP call per command when possible
- Efficient data processing and caching
- Timeout handling for slow responses
- Rate limiting compliance

### Discord API Usage

**Best Practices:**
- Deferred responses for long operations
- Embed size limits respected
- Rate limit handling for multiple requests
- Efficient message formatting

### Memory Management

**Resource Usage:**
- Minimal data retention after command completion
- Efficient data structures for processing
- Cleanup of temporary objects

## Testing

### Manual Testing

The implementation includes comprehensive manual testing:
- Command import verification
- Date validation testing
- Command structure validation
- Bot integration testing

**Test Coverage:**
- All four soccer commands
- Parameter validation functions
- Error handling scenarios
- Integration with existing bot features

### Integration Testing

Comprehensive test suite covers:
- Successful command execution
- Error scenarios (MCP failures, invalid input)
- Parameter validation edge cases
- Mock MCP server responses

## Usage Guidelines

### For Users

**Best Practices:**
- Use partial team names for easier matching
- Check `/soccer-schedule` before using other commands
- Use specific dates when looking for historical data
- Try different team name variations if not found

**Common Issues:**
- Team names must be spelled reasonably correctly
- Teams must have played recently for H2H analysis
- Some leagues may have limited data availability
- Betting odds may not be available for all matches

### For Administrators

**Configuration:**
- Ensure Soccer MCP server URL is correctly configured
- Monitor MCP server connectivity and performance
- Review error logs for recurring issues
- Consider rate limiting for high-usage servers

**Maintenance:**
- Regular testing of MCP server connectivity
- Monitoring of command usage and performance
- Updates to league configurations as needed
- Error log review and cleanup

## Future Enhancements

### Planned Features

**Live Match Updates:**
- Real-time score updates in channels
- Goal notifications and match events
- Live betting odds updates

**Enhanced Analytics:**
- Player statistics and prop betting
- Team form analysis and trends
- Advanced betting recommendations

**User Customization:**
- Favorite team notifications
- Personalized match recommendations
- Custom league filters

### Technical Improvements

**Performance:**
- Response caching for frequently requested data
- Batch processing for multiple requests
- Optimized embed generation

**Reliability:**
- Retry logic for failed MCP requests
- Fallback data sources
- Enhanced error recovery

**Usability:**
- Autocomplete for team names
- Interactive buttons for common actions
- Improved mobile formatting

## Troubleshooting

### Common Issues

**"Teams Not Found" Error:**
- Check team name spelling
- Try partial names or abbreviations
- Ensure teams have played recently
- Use `/soccer-schedule` to see available teams

**"No Matches Found" Error:**
- Verify date format is correct
- Check if date is within supported range
- Try different leagues or dates
- Confirm league is currently active

**"MCP Server Error":**
- Check internet connectivity
- Verify MCP server is operational
- Try again after a few minutes
- Contact administrator if persistent

### Debug Information

**For Developers:**
- Error logs include full stack traces
- MCP request/response logging available
- Command execution timing metrics
- User input validation details

**For Users:**
- Clear error messages with actionable advice
- Command usage examples in help text
- Suggestions for alternative approaches
- Contact information for support

## Conclusion

The soccer slash commands provide comprehensive soccer data integration with robust error handling, user-friendly interfaces, and seamless integration with existing bot features. The implementation follows Discord bot best practices and provides a solid foundation for future enhancements.

For technical support or feature requests, please refer to the project documentation or contact the development team.