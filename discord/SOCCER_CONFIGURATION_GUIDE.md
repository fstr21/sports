# Soccer Discord Integration - Configuration Guide

## Overview

This guide covers the comprehensive configuration system for the Soccer Discord Integration, including environment variables, league configurations, feature flags, and deployment setup.

## Environment Variables

### Required Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `DISCORD_BOT_TOKEN` | Discord bot token for authentication | `MTIzNDU2Nzg5MDEyMzQ1Njc4OTA...` | ✅ Yes |

### Optional Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `SOCCER_MCP_URL` | URL for Soccer MCP server | `https://soccermcp-production.up.railway.app/mcp` | `https://custom-soccer-mcp.com/mcp` |
| `AUTH_KEY` | Authentication key for Soccer MCP server | None | `your_auth_key_here_123456` |
| `SOCCER_LEAGUES_CONFIG` | Custom league configurations (JSON) | Built-in defaults | See [Custom League Configuration](#custom-league-configuration) |

### Environment Variable Validation

The system automatically validates all environment variables on startup:

- **DISCORD_BOT_TOKEN**: Must be present and at least 50 characters long
- **SOCCER_MCP_URL**: Must be a valid HTTP/HTTPS URL if provided
- **AUTH_KEY**: Should be at least 10 characters long if provided (warning if shorter)

## League Configuration

### Default Supported Leagues

The system comes with pre-configured support for major soccer leagues:

| League Code | Name | Country | Priority | Tournament Type |
|-------------|------|---------|----------|-----------------|
| `UEFA` | UEFA Champions League | Europe | 0 (Highest) | Knockout |
| `EPL` | Premier League | England | 1 | League |
| `La Liga` | La Liga | Spain | 2 | League |
| `Bundesliga` | Bundesliga | Germany | 3 | League |
| `Serie A` | Serie A | Italy | 4 | League |
| `MLS` | MLS | USA | 5 | League |

### Custom League Configuration

You can customize league configurations using the `SOCCER_LEAGUES_CONFIG` environment variable with JSON format:

```json
{
  "EPL": {
    "active": false,
    "color": 0x123456
  },
  "CUSTOM_LEAGUE": {
    "id": 999,
    "name": "Custom League",
    "country": "Custom Country",
    "priority": 10,
    "active": true,
    "color": 0xff0000,
    "season_format": "2025",
    "tournament_type": "league"
  }
}
```

### League Configuration Properties

| Property | Type | Description | Required |
|----------|------|-------------|----------|
| `id` | int | Unique league identifier for MCP server | ✅ |
| `name` | string | Display name for the league | ✅ |
| `country` | string | Country or region | ✅ |
| `priority` | int | Display priority (lower = higher priority) | ✅ |
| `active` | bool | Whether league is currently active | No (default: true) |
| `color` | int | Hex color for embeds | No (default: 0x00ff00) |
| `season_format` | string | Season format display | No (default: "2025-26") |
| `tournament_type` | string | "league" or "knockout" | No (default: "league") |

## Feature Flags

Control which features are enabled using the configuration system:

### Soccer-Specific Features

| Feature | Default | Description |
|---------|---------|-------------|
| `soccer_integration` | `true` | Enable soccer functionality |
| `multi_league_support` | `true` | Support multiple soccer leagues |
| `h2h_analysis` | `true` | Head-to-head analysis |
| `betting_recommendations` | `true` | AI betting insights |
| `league_standings` | `true` | League table display |
| `advanced_statistics` | `true` | Advanced match statistics |
| `channel_auto_cleanup` | `true` | Automatic channel cleanup |

### General Features

| Feature | Default | Description |
|---------|---------|-------------|
| `live_updates` | `false` | Live game tracking |
| `player_props` | `true` | Player prop betting |
| `ai_analysis` | `true` | AI predictions |
| `weather_integration` | `true` | Weather data |
| `auto_channels` | `false` | Automatic channel creation |

## Rate Limiting Configuration

### Default Rate Limits

```python
rate_limiting = {
    "requests_per_minute": 30,
    "requests_per_hour": 300,
    "burst_limit": 10,
    "cooldown_seconds": 2.0
}
```

### Customizing Rate Limits

Rate limits are automatically configured based on your Soccer MCP server capabilities. The system includes:

- **Burst Protection**: Allows short bursts of requests up to `burst_limit`
- **Cooldown Period**: Enforces minimum time between requests
- **Exponential Backoff**: Automatically increases delays on rate limit hits
- **Request Queuing**: Queues requests when rate limits are reached

## Error Handling Configuration

### Default Error Handling

```python
error_handling = {
    "max_retries": 3,
    "retry_delay_seconds": 2.0,
    "exponential_backoff": True,
    "fallback_to_cache": True,
    "graceful_degradation": True
}
```

### Error Handling Features

- **Automatic Retries**: Retries failed requests up to `max_retries` times
- **Exponential Backoff**: Increases delay between retries exponentially
- **Cache Fallback**: Uses cached data when MCP server is unavailable
- **Graceful Degradation**: Continues operation with reduced functionality

## Deployment Setup

### 1. Environment Setup

Create a `.env` file with your configuration:

```bash
# Required
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# Optional - Soccer MCP Configuration
SOCCER_MCP_URL=https://soccermcp-production.up.railway.app/mcp
AUTH_KEY=your_auth_key_here

# Optional - Custom League Configuration
SOCCER_LEAGUES_CONFIG={"EPL":{"active":true},"CUSTOM":{"id":999,"name":"Custom League","country":"Test","priority":10}}
```

### 2. Configuration Validation

The bot automatically validates configuration on startup. Check logs for:

```
INFO - Performing soccer configuration startup checks...
INFO - Soccer MCP URL configured: https://soccermcp-production.up.railway.app/mcp
INFO - Soccer MCP authentication key provided
INFO - Active soccer leagues: UEFA, EPL, La Liga, Bundesliga, Serie A, MLS
INFO - Soccer configuration startup checks completed successfully
```

### 3. Testing Configuration

Run the configuration tests to verify your setup:

```bash
python -m pytest discord/test_soccer_config.py -v
```

### 4. Production Deployment

#### Railway Deployment

1. Set environment variables in Railway dashboard:
   ```
   DISCORD_BOT_TOKEN=your_token
   SOCCER_MCP_URL=https://soccermcp-production.up.railway.app/mcp
   AUTH_KEY=your_auth_key
   ```

2. Deploy with configuration validation:
   ```bash
   railway up
   ```

#### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY discord/ ./discord/
COPY .env .

# Validate configuration on build
RUN python -c "from discord.soccer_config import perform_soccer_startup_checks; assert perform_soccer_startup_checks()"

CMD ["python", "discord/bot_structure.py"]
```

## Configuration Monitoring

### Startup Checks

The system performs comprehensive startup checks:

1. **Environment Variable Validation**
   - Checks all required variables are present
   - Validates format and content of variables
   - Warns about missing optional variables

2. **Soccer Configuration Validation**
   - Validates MCP URL format
   - Checks authentication key if provided
   - Validates league configurations
   - Tests rate limiting settings

3. **Feature Dependency Checks**
   - Ensures feature dependencies are met
   - Warns about conflicting feature flags
   - Validates league priority ordering

### Runtime Monitoring

Monitor these configuration-related metrics:

- **MCP Connection Status**: Track connection health to Soccer MCP server
- **Rate Limit Usage**: Monitor API request rates and limits
- **Error Rates**: Track configuration-related errors
- **Feature Usage**: Monitor which features are being used

### Troubleshooting

#### Common Configuration Issues

1. **Missing DISCORD_BOT_TOKEN**
   ```
   ERROR - Missing required environment variable: DISCORD_BOT_TOKEN
   ```
   **Solution**: Set the Discord bot token in your environment

2. **Invalid Soccer MCP URL**
   ```
   ERROR - Invalid Soccer MCP URL format
   ```
   **Solution**: Ensure URL starts with `http://` or `https://`

3. **League Configuration Errors**
   ```
   ERROR - Invalid league ID for EPL: -1
   ```
   **Solution**: Check custom league configuration JSON format

4. **Rate Limiting Issues**
   ```
   WARNING - Rate limiting: requests_per_minute * 60 exceeds requests_per_hour
   ```
   **Solution**: Adjust rate limiting configuration for consistency

#### Debug Mode

Enable debug logging for detailed configuration information:

```python
import logging
logging.getLogger('soccer_config').setLevel(logging.DEBUG)
```

## Configuration Best Practices

### Security

1. **Never commit sensitive data** to version control
2. **Use environment variables** for all sensitive configuration
3. **Rotate AUTH_KEY regularly** if using Soccer MCP authentication
4. **Validate all configuration** before deployment

### Performance

1. **Configure appropriate rate limits** based on your usage
2. **Enable caching** for better performance
3. **Use graceful degradation** for reliability
4. **Monitor resource usage** and adjust limits accordingly

### Maintenance

1. **Regularly update league configurations** for new seasons
2. **Monitor feature flag usage** and remove unused features
3. **Review error handling settings** based on actual error patterns
4. **Keep documentation updated** with configuration changes

## Support

For configuration issues:

1. Check the startup logs for validation errors
2. Run the configuration test suite
3. Verify environment variables are set correctly
4. Check Soccer MCP server connectivity
5. Review league configuration JSON format

For additional help, refer to the main project documentation or create an issue with your configuration details (excluding sensitive information).