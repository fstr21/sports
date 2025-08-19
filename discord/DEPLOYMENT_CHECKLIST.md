# Soccer Discord Integration - Deployment Checklist

## Pre-Deployment Validation

### ✅ Environment Setup
- [ ] **Discord Bot Token**: Valid token with required permissions
- [ ] **Soccer MCP URL**: Accessible and responding
- [ ] **AUTH_KEY**: Valid authentication key for Soccer MCP (if required)
- [ ] **Python Dependencies**: All requirements installed (`pip install -r requirements.txt`)
- [ ] **Environment Variables**: All required variables set in production environment

### ✅ Configuration Validation
- [ ] **Bot Permissions**: Verified bot has required Discord permissions
  - Send Messages
  - Embed Links
  - Manage Channels
  - Use Slash Commands
  - Read Message History
- [ ] **League Configuration**: All supported leagues properly configured
- [ ] **Rate Limiting**: Rate limits configured for production load
- [ ] **Error Handling**: Comprehensive error handling enabled
- [ ] **Logging**: Production logging configured and tested

### ✅ Integration Testing
- [ ] **MLB Compatibility**: Soccer integration doesn't conflict with existing MLB functionality
- [ ] **Load Testing**: System handles multiple concurrent requests
- [ ] **Rate Limit Compliance**: Discord API rate limits respected
- [ ] **Error Recovery**: System recovers gracefully from MCP server issues
- [ ] **User Acceptance**: Sample commands work as expected

### ✅ Security Validation
- [ ] **Token Security**: Bot token stored securely (environment variables)
- [ ] **Input Validation**: All user inputs properly validated
- [ ] **Permission Checks**: Admin commands require proper permissions
- [ ] **Error Information**: No sensitive information leaked in error messages

## Deployment Steps

### 1. Pre-Deployment Backup
```bash
# Backup current bot configuration
cp bot_structure.py bot_structure.py.backup
cp config.py config.py.backup

# Backup any existing channel data
# (Discord channels will be preserved automatically)
```

### 2. Environment Setup
```bash
# Set required environment variables
export DISCORD_BOT_TOKEN="your_bot_token_here"
export SOCCER_MCP_URL="https://soccermcp-production.up.railway.app/mcp"
export AUTH_KEY="your_auth_key_here"  # Optional but recommended

# Verify environment
python discord/validate_config.py
```

### 3. Dependency Installation
```bash
# Install/update Python dependencies
pip install -r requirements.txt

# Verify critical imports
python -c "import discord; import httpx; import asyncio; print('Dependencies OK')"
```

### 4. Pre-Deployment Testing
```bash
# Run comprehensive test suite
python discord/test_integration_deployment.py

# Run specific component tests
python discord/test_comprehensive_soccer_integration.py
python discord/test_multi_league_integration.py

# Verify configuration
python discord/test_soccer_config.py
```

### 5. Gradual Deployment
```bash
# Step 1: Deploy with soccer integration disabled
# Set FEATURES["soccer_integration"] = False in config.py
python bot_structure.py --test-mode

# Step 2: Enable soccer integration
# Set FEATURES["soccer_integration"] = True
# Restart bot

# Step 3: Test with limited leagues
# Start with 1-2 leagues, gradually add more

# Step 4: Full deployment
# Enable all supported leagues
```

### 6. Post-Deployment Verification
- [ ] **Bot Online**: Bot shows as online in Discord
- [ ] **Commands Registered**: Slash commands appear in Discord
- [ ] **Test Channel Creation**: Create test soccer channels
- [ ] **Error Monitoring**: Check logs for any errors
- [ ] **Performance Monitoring**: Monitor response times

## Rollback Procedures

### Immediate Rollback (Critical Issues)
```bash
# 1. Disable soccer integration immediately
# Edit config.py: FEATURES["soccer_integration"] = False

# 2. Restart bot with backup configuration
cp bot_structure.py.backup bot_structure.py
python bot_structure.py

# 3. Verify MLB functionality still works
# Test existing /create-channels command with MLB
```

### Partial Rollback (Non-Critical Issues)
```bash
# 1. Disable specific problematic features
# Edit config.py to disable specific features:
# FEATURES["multi_league_support"] = False
# FEATURES["h2h_analysis"] = False
# FEATURES["betting_recommendations"] = False

# 2. Restart bot
# 3. Monitor for improvements
```

### Data Recovery
```bash
# Discord channels are preserved automatically
# No data loss occurs during rollback

# If needed, manually clean up test channels:
# Use /cleanup command or manual deletion
```

## Monitoring and Maintenance

### Key Metrics to Monitor
- **Response Times**: MCP server response times
- **Error Rates**: Failed channel creation attempts
- **Discord API Usage**: Rate limit compliance
- **Memory Usage**: Bot memory consumption
- **Channel Count**: Number of active soccer channels

### Log Files to Monitor
- `discord_bot.log`: General bot operations
- `soccer_bot_debug.log`: Soccer-specific debug information
- `soccer_bot_errors.log`: Soccer-specific errors

### Regular Maintenance Tasks
- **Daily**: Check error logs for issues
- **Weekly**: Review channel cleanup statistics
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Performance optimization review

## Troubleshooting Guide

### Common Issues and Solutions

#### Bot Not Responding
```bash
# Check bot status
ps aux | grep python

# Check logs
tail -f discord_bot.log

# Restart bot
python bot_structure.py
```

#### Soccer Commands Not Working
```bash
# Verify MCP server connectivity
curl -X POST https://soccermcp-production.up.railway.app/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

# Check soccer configuration
python -c "from soccer_config import validate_soccer_environment; print(validate_soccer_environment())"

# Test soccer integration
python discord/test_soccer_integration.py
```

#### Channel Creation Failures
```bash
# Check Discord permissions
# Verify bot has "Manage Channels" permission

# Check rate limiting
# Review rate limit configuration in config.py

# Test with single channel
# Use /setup command to create one test channel
```

#### MCP Server Issues
```bash
# Check MCP server status
curl -I https://soccermcp-production.up.railway.app/mcp

# Test with fallback data
# Enable graceful degradation in error handling

# Check AUTH_KEY validity
# Verify authentication key is correct
```

## Performance Optimization

### Production Settings
```python
# config.py optimizations for production
SOCCER_CONFIG = {
    "cache_duration_minutes": 15,  # Cache match data
    "max_matches_per_day": 50,     # Limit to prevent spam
    "rate_limiting": {
        "requests_per_minute": 30,  # Conservative rate limiting
        "burst_limit": 5,           # Prevent burst requests
        "cooldown_seconds": 2       # Cooldown between requests
    }
}
```

### Memory Management
```python
# Enable cleanup system
FEATURES["channel_auto_cleanup"] = True

# Set reasonable retention
CHANNEL_CLEANUP_DAYS = 3

# Limit concurrent operations
MAX_CONCURRENT_CHANNELS = 10
```

## Security Considerations

### Token Management
- Store bot token in environment variables only
- Never commit tokens to version control
- Rotate tokens regularly
- Use separate tokens for development/production

### Input Validation
- All date inputs validated before processing
- Team names sanitized for channel creation
- Command parameters validated for type and range
- SQL injection prevention (if using databases)

### Error Handling
- No sensitive information in error messages
- Graceful degradation for missing data
- Rate limiting to prevent abuse
- Logging without exposing secrets

## Success Criteria

### Deployment Considered Successful When:
- [ ] All integration tests pass (>90% success rate)
- [ ] Bot responds to commands within 5 seconds
- [ ] Channel creation works for all supported leagues
- [ ] No conflicts with existing MLB functionality
- [ ] Error rate < 5% over 24 hours
- [ ] Memory usage stable over 48 hours
- [ ] No critical errors in logs

### Performance Benchmarks
- **Command Response Time**: < 3 seconds average
- **Channel Creation Time**: < 10 seconds for 10 channels
- **MCP Server Response**: < 2 seconds average
- **Memory Usage**: < 500MB steady state
- **Error Rate**: < 2% of all operations

## Contact Information

### Support Contacts
- **Primary Developer**: [Your contact information]
- **System Administrator**: [Admin contact]
- **Discord Server Admin**: [Discord admin contact]

### Emergency Procedures
1. **Critical Issue**: Immediate rollback using backup configuration
2. **MCP Server Down**: Enable graceful degradation mode
3. **Discord API Issues**: Reduce rate limits and retry
4. **Memory Leak**: Restart bot and investigate logs

---

**Last Updated**: August 18, 2025
**Version**: 1.0
**Next Review**: September 18, 2025