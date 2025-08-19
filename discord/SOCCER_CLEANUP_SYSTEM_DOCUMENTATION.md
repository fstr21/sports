# Soccer Channel Cleanup and Maintenance System

## Overview

The Soccer Channel Cleanup and Maintenance System provides automated and manual cleanup capabilities for soccer match channels in Discord. It implements intelligent preservation logic, comprehensive error handling, and detailed reporting to maintain an organized server while preserving valuable content.

## Features

### 🤖 Automated Cleanup
- **Scheduled Cleanup**: Runs every 6 hours automatically
- **Configurable Retention**: Default 3-day retention period
- **Intelligent Preservation**: Preserves channels with recent activity or pinned messages
- **Batch Processing**: Handles large numbers of channels efficiently with rate limiting

### 🛠️ Manual Cleanup Commands
- **`/soccer-cleanup`**: Manual cleanup with customizable parameters
- **`/soccer-cleanup-stats`**: View cleanup system statistics
- **`/soccer-channel-limits`**: Manage channel limits with priority-based retention

### 🧠 Smart Preservation Logic
- **Recent Activity**: Preserves channels with messages in the last 24 hours
- **Pinned Messages**: Preserves channels with pinned content
- **Future Matches**: Preserves channels for upcoming matches
- **Priority Scoring**: Uses weighted scoring system for preservation decisions

### 📊 Comprehensive Reporting
- **Cleanup Statistics**: Detailed metrics on cleanup operations
- **Error Tracking**: Comprehensive error logging and reporting
- **Administrator Notifications**: Automatic notifications for significant cleanup events

## Architecture

### Core Components

#### SoccerCleanupSystem
Main cleanup system class that orchestrates all cleanup operations.

```python
class SoccerCleanupSystem:
    def __init__(self, bot, soccer_channel_manager):
        self.bot = bot
        self.soccer_channel_manager = soccer_channel_manager
        self.default_retention_days = 3
        self.max_channels_per_category = 50
```

#### CleanupStats
Data class for tracking cleanup operation statistics.

```python
@dataclass
class CleanupStats:
    channels_deleted: int = 0
    channels_preserved: int = 0
    channels_with_activity: int = 0
    channels_with_pins: int = 0
    errors: int = 0
    total_processed: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
```

#### ChannelInfo
Data class for storing channel analysis information.

```python
@dataclass
class ChannelInfo:
    channel: discord.TextChannel
    created_at: datetime
    last_message_at: Optional[datetime] = None
    has_pinned_messages: bool = False
    message_count: int = 0
    is_match_channel: bool = False
    match_date: Optional[datetime] = None
    priority_score: int = 0
```

### Priority Scoring System

The system uses a weighted scoring algorithm to determine which channels to preserve:

| Factor | Score | Description |
|--------|-------|-------------|
| Recent Creation | +10 | Channel created within retention period |
| Future Match | +20 | Match date is in the future |
| Recent Match | +15 | Match was today or yesterday |
| Recent Activity | +15 | Messages within last 24 hours |
| Some Activity | +5 | Messages within last 3 days |
| Message Count | +5 | At least 5 messages in channel |
| Pinned Messages | +10 | Channel has pinned messages |

**Preservation Rule**: Channels with score > 0 are preserved, score = 0 are deleted.

## Configuration

### Environment Variables
```bash
# Optional: Override default retention period
SOCCER_CLEANUP_RETENTION_DAYS=3

# Optional: Override channel limits
SOCCER_MAX_CHANNELS_PER_CATEGORY=50
```

### Bot Integration
```python
# In bot_structure.py
from soccer_cleanup_system import SoccerCleanupSystem

class SportsBot(commands.Bot):
    def __init__(self):
        # ... existing initialization ...
        
        # Initialize cleanup system
        self.soccer_cleanup_system = SoccerCleanupSystem(self, self.soccer_channel_manager)
```

## Usage

### Slash Commands

#### `/soccer-cleanup`
Manual cleanup command for administrators.

**Parameters:**
- `days_old` (optional): Number of days old for cleanup (default: 3)
- `preserve_active` (optional): Preserve channels with recent activity (default: True)
- `preserve_pinned` (optional): Preserve channels with pinned messages (default: True)
- `dry_run` (optional): Show what would be deleted without actually deleting (default: False)

**Examples:**
```
/soccer-cleanup
/soccer-cleanup days_old:5 preserve_active:False
/soccer-cleanup dry_run:True
```

#### `/soccer-cleanup-stats`
Display cleanup system statistics and status.

**Output includes:**
- Total cleanups performed
- Last cleanup results
- System configuration
- Next scheduled cleanup time

#### `/soccer-channel-limits`
Manage channel limits with priority-based retention.

**Parameters:**
- `priority_retention` (optional): Use priority-based retention (default: True)

## Automated Cleanup

### Scheduled Task
The system runs automated cleanup every 6 hours:

```python
@tasks.loop(hours=6)
async def scheduled_cleanup_task(self):
    """Scheduled cleanup task that runs automatically"""
    for guild in self.bot.guilds:
        stats = await self.cleanup_old_channels(guild, days_old=self.default_retention_days)
        await self._notify_administrators_if_needed(guild, stats, "scheduled")
```

### Preservation Logic
Channels are preserved if they meet any of these criteria:

1. **Age**: Created within the retention period
2. **Activity**: Have messages within the last 24 hours
3. **Pins**: Have pinned messages
4. **Future Matches**: Match date is in the future
5. **Recent Matches**: Match was today or yesterday

### Rate Limiting
The system implements comprehensive rate limiting:

- **Batch Size**: Processes 10 channels per batch
- **Batch Delay**: 2 seconds between batches
- **Channel Delay**: 0.5 seconds between individual channel operations
- **Retry Logic**: Automatic retry with exponential backoff for rate limits

## Error Handling

### Error Types
The system handles various error scenarios:

- **Discord API Errors**: Rate limits, permissions, network issues
- **Channel Access Errors**: Missing channels, permission denied
- **Data Processing Errors**: Invalid channel data, parsing failures

### Error Recovery
- **Graceful Degradation**: Continues operation when individual channels fail
- **Retry Logic**: Automatic retry for transient failures
- **Error Logging**: Comprehensive logging for debugging
- **Administrator Notifications**: Alerts for significant error conditions

### Logging
```python
# Error logging example
bot_logger.log_operation_error(
    "cleanup_old_channels", 
    error, 
    context
)
```

## Monitoring and Notifications

### Administrator Notifications
The system automatically notifies administrators when:

- 5 or more channels are deleted in a single operation
- 2 or more errors occur during cleanup
- Any scheduled cleanup deletes channels

### Notification Channels
The system looks for notification channels in this order:
1. Channels with keywords: 'admin', 'mod', 'staff', 'log'
2. Guild system messages channel
3. First available text channel

### Notification Format
```
🧹 Soccer Channel Cleanup Report
Automated cleanup completed for **Guild Name**

📊 Statistics
Processed: 15 channels
Deleted: 8 channels
Preserved: 7 channels
Errors: 0

⏱️ Duration: 12.3 seconds
🔧 Cleanup Type: Scheduled

🛡️ Preservation Reasons
Recent Activity: 3
Pinned Messages: 2
```

## Performance Considerations

### Optimization Features
- **Batch Processing**: Reduces API calls and rate limit issues
- **Lazy Loading**: Only loads channel data when needed
- **Efficient Queries**: Minimizes Discord API requests
- **Memory Management**: Processes channels in batches to control memory usage

### Scalability
The system is designed to handle:
- **Large Servers**: Up to 50 channels per category
- **High Activity**: Frequent channel creation and cleanup
- **Multiple Guilds**: Concurrent cleanup across multiple servers

## Testing

### Integration Tests
Run the integration test suite:

```bash
cd discord
python test_cleanup_integration.py
```

### Unit Tests
Run comprehensive unit tests:

```bash
cd discord
python -m pytest test_soccer_cleanup_system.py -v
```

### Test Coverage
The test suite covers:
- Basic cleanup functionality
- Preservation logic
- Priority scoring system
- Error handling scenarios
- Rate limiting behavior
- Statistics tracking

## Troubleshooting

### Common Issues

#### Cleanup Not Running
**Symptoms**: No channels being deleted despite old channels existing
**Solutions**:
1. Check bot permissions (Manage Channels)
2. Verify soccer category exists
3. Check cleanup system initialization
4. Review error logs

#### Channels Not Being Preserved
**Symptoms**: Important channels being deleted unexpectedly
**Solutions**:
1. Check preservation settings
2. Verify activity detection
3. Review priority scoring logic
4. Use dry run mode to test

#### Rate Limiting Issues
**Symptoms**: Cleanup operations timing out or failing
**Solutions**:
1. Reduce batch size
2. Increase delays between operations
3. Check Discord API status
4. Review rate limiting configuration

### Debug Commands
```python
# Get cleanup statistics
stats = bot.soccer_cleanup_system.get_cleanup_statistics()
print(stats)

# Test priority scoring
from soccer_cleanup_system import ChannelInfo
info = ChannelInfo(channel=channel, created_at=datetime.utcnow())
score = cleanup_system._calculate_priority_score(info, cutoff_date, True, True)
print(f"Priority score: {score}")
```

### Log Analysis
Key log messages to monitor:

```
# Successful cleanup
INFO - Operation completed successfully: cleanup_old_channels (took 12.3s) - Deleted 8, preserved 7, errors 0

# Error conditions
ERROR - Failed to delete channel channel-name: Permission denied
WARNING - Rate limited, waiting 5.0s

# Preservation decisions
DEBUG - Preserving channel-name due to recent activity
DEBUG - Preserving channel-name due to pinned messages
```

## Best Practices

### Configuration
1. **Retention Period**: Set appropriate retention based on server activity
2. **Preservation Settings**: Enable both activity and pin preservation
3. **Channel Limits**: Monitor and adjust based on server needs
4. **Notification Channels**: Ensure proper admin notification setup

### Monitoring
1. **Regular Review**: Check cleanup statistics weekly
2. **Error Monitoring**: Monitor error logs for recurring issues
3. **Performance Tracking**: Track cleanup duration and success rates
4. **User Feedback**: Gather feedback on preservation decisions

### Maintenance
1. **Log Rotation**: Implement log rotation for long-term operation
2. **Statistics Archival**: Archive old cleanup statistics
3. **Configuration Updates**: Review and update configuration periodically
4. **Testing**: Run integration tests after bot updates

## API Reference

### SoccerCleanupSystem Methods

#### `cleanup_old_channels(guild, days_old=None, preserve_active=True, preserve_pinned=True, context=None)`
Perform cleanup operation on a guild.

**Parameters:**
- `guild`: Discord guild object
- `days_old`: Age threshold for cleanup
- `preserve_active`: Whether to preserve channels with recent activity
- `preserve_pinned`: Whether to preserve channels with pinned messages
- `context`: Error context for logging

**Returns:** `CleanupStats` object

#### `manual_cleanup_command(interaction, days_old=None, preserve_active=True, preserve_pinned=True)`
Handle manual cleanup slash command.

**Parameters:**
- `interaction`: Discord interaction object
- `days_old`: Age threshold for cleanup
- `preserve_active`: Whether to preserve channels with recent activity
- `preserve_pinned`: Whether to preserve channels with pinned messages

**Returns:** `CleanupStats` object

#### `get_cleanup_statistics()`
Get comprehensive cleanup statistics.

**Returns:** Dictionary with system information and last cleanup results

#### `channel_limit_management(guild, priority_retention=True)`
Manage channel limits with priority-based retention.

**Parameters:**
- `guild`: Discord guild object
- `priority_retention`: Whether to use priority-based retention

**Returns:** Dictionary with management results

## Changelog

### Version 1.0.0 (Current)
- Initial implementation of automated cleanup system
- Manual cleanup slash commands
- Priority-based preservation logic
- Comprehensive error handling and logging
- Administrator notifications
- Integration tests and documentation

### Planned Features
- **Custom Retention Rules**: Per-league retention settings
- **Advanced Analytics**: Detailed cleanup analytics and trends
- **Webhook Integration**: External webhook notifications
- **Backup System**: Channel content backup before deletion
- **User Preferences**: Per-user cleanup preferences