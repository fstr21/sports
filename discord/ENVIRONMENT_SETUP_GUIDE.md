# Soccer Discord Integration - Environment Setup Guide

## Overview

This guide provides step-by-step instructions for setting up the environment for the Soccer Discord Integration. Follow these instructions carefully to ensure proper deployment and operation.

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 512MB RAM available
- **Network**: Stable internet connection
- **Discord**: Bot application created in Discord Developer Portal

### Required Accounts/Services
- **Discord Developer Account**: For bot token
- **Soccer MCP Server Access**: For match data
- **Server/Hosting**: For bot deployment (optional)

## Step 1: Discord Bot Setup

### 1.1 Create Discord Application
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Enter application name (e.g., "Soccer Bot")
4. Click "Create"

### 1.2 Create Bot User
1. Navigate to "Bot" section in left sidebar
2. Click "Add Bot"
3. Confirm by clicking "Yes, do it!"
4. **Copy the bot token** (keep this secure!)

### 1.3 Configure Bot Permissions
Required permissions:
- ✅ Send Messages
- ✅ Embed Links
- ✅ Manage Channels
- ✅ Use Slash Commands
- ✅ Read Message History
- ✅ View Channels

Permission integer: `2147485696`

### 1.4 Invite Bot to Server
1. Go to "OAuth2" > "URL Generator"
2. Select scopes: `bot` and `applications.commands`
3. Select permissions listed above
4. Copy generated URL and open in browser
5. Select your Discord server and authorize

## Step 2: Environment Variables

### 2.1 Required Environment Variables

Create a `.env` file in your project root:

```bash
# Discord Configuration
DISCORD_BOT_TOKEN=your_bot_token_here

# Soccer MCP Configuration
SOCCER_MCP_URL=https://soccermcp-production.up.railway.app/mcp
AUTH_KEY=your_auth_key_here

# Optional Configuration
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### 2.2 Environment Variable Descriptions

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DISCORD_BOT_TOKEN` | ✅ Yes | Discord bot authentication token | `MTIzNDU2Nzg5MDEyMzQ1Njc4OTA...` |
| `SOCCER_MCP_URL` | ❌ No | Soccer MCP server URL | `https://soccermcp-production.up.railway.app/mcp` |
| `AUTH_KEY` | ❌ No | Authentication key for Soccer MCP | `your_secret_key_here` |
| `LOG_LEVEL` | ❌ No | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `ENVIRONMENT` | ❌ No | Environment type (development, production) | `production` |

### 2.3 Setting Environment Variables

#### Windows (Command Prompt)
```cmd
set DISCORD_BOT_TOKEN=your_bot_token_here
set SOCCER_MCP_URL=https://soccermcp-production.up.railway.app/mcp
set AUTH_KEY=your_auth_key_here
```

#### Windows (PowerShell)
```powershell
$env:DISCORD_BOT_TOKEN="your_bot_token_here"
$env:SOCCER_MCP_URL="https://soccermcp-production.up.railway.app/mcp"
$env:AUTH_KEY="your_auth_key_here"
```

#### macOS/Linux (Bash)
```bash
export DISCORD_BOT_TOKEN="your_bot_token_here"
export SOCCER_MCP_URL="https://soccermcp-production.up.railway.app/mcp"
export AUTH_KEY="your_auth_key_here"
```

#### Using .env file (Recommended)
```bash
# Create .env file
echo "DISCORD_BOT_TOKEN=your_bot_token_here" > .env
echo "SOCCER_MCP_URL=https://soccermcp-production.up.railway.app/mcp" >> .env
echo "AUTH_KEY=your_auth_key_here" >> .env
```

## Step 3: Python Environment Setup

### 3.1 Check Python Version
```bash
python --version
# Should be 3.8 or higher
```

### 3.2 Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv soccer_bot_env

# Activate virtual environment
# Windows:
soccer_bot_env\Scripts\activate
# macOS/Linux:
source soccer_bot_env/bin/activate
```

### 3.3 Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Or install manually:
pip install discord.py>=2.3.0
pip install httpx>=0.24.0
pip install python-dotenv>=1.0.0
pip install asyncio
pip install pytest>=7.0.0
pip install pytest-asyncio>=0.21.0
```

### 3.4 Verify Installation
```bash
# Test imports
python -c "import discord; import httpx; import asyncio; print('All dependencies installed successfully!')"
```

## Step 4: Configuration Validation

### 4.1 Run Configuration Validator
```bash
# Navigate to discord directory
cd discord

# Run configuration validator
python validate_config.py
```

Expected output:
```
✅ Environment validation passed
✅ Discord bot token format valid
✅ Soccer MCP URL accessible
✅ All required dependencies installed
🎉 Configuration ready for deployment!
```

### 4.2 Test Soccer MCP Connection
```bash
# Test MCP server connectivity
python -c "
import asyncio
import httpx

async def test_mcp():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://soccermcp-production.up.railway.app/mcp',
            json={'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list'},
            timeout=10
        )
        print(f'MCP Server Status: {response.status_code}')
        if response.status_code == 200:
            print('✅ MCP Server accessible')
        else:
            print('❌ MCP Server connection failed')

asyncio.run(test_mcp())
"
```

## Step 5: Initial Testing

### 5.1 Run Unit Tests
```bash
# Run comprehensive test suite
python test_comprehensive_soccer_integration.py

# Run integration tests
python test_integration_deployment.py
```

### 5.2 Test Bot Startup
```bash
# Test bot initialization (dry run)
python -c "
from bot_structure import SportsBot
bot = SportsBot()
print('✅ Bot initialized successfully')
print(f'Leagues configured: {list(bot.leagues.keys())}')
print(f'Soccer integration: {\"SOCCER\" in bot.leagues}')
"
```

### 5.3 Test Command Registration
```bash
# Test slash command setup
python -c "
from bot_structure import bot
commands = [cmd.name for cmd in bot.tree.get_commands()]
print(f'Registered commands: {commands}')
if 'create-channels' in commands:
    print('✅ Core commands registered')
else:
    print('❌ Commands not registered properly')
"
```

## Step 6: Production Deployment

### 6.1 Production Environment Variables
```bash
# Production .env file
DISCORD_BOT_TOKEN=your_production_bot_token
SOCCER_MCP_URL=https://soccermcp-production.up.railway.app/mcp
AUTH_KEY=your_production_auth_key
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### 6.2 Start Bot
```bash
# Start bot in production mode
python bot_structure.py
```

### 6.3 Verify Deployment
1. **Check Bot Status**: Bot should appear online in Discord
2. **Test Commands**: Try `/create-channels` command
3. **Monitor Logs**: Check for any errors in console output
4. **Test Channel Creation**: Create test soccer channels

## Step 7: Monitoring Setup

### 7.1 Log File Configuration
```bash
# Ensure log directory exists
mkdir -p logs

# Set log file permissions (Linux/macOS)
chmod 644 logs/discord_bot.log
```

### 7.2 Health Check Script
Create `health_check.py`:
```python
#!/usr/bin/env python3
import asyncio
import httpx
import os
from datetime import datetime

async def health_check():
    print(f"Health Check - {datetime.now()}")
    
    # Check MCP server
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                os.getenv('SOCCER_MCP_URL'),
                json={'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list'},
                timeout=5
            )
            if response.status_code == 200:
                print("✅ MCP Server: OK")
            else:
                print(f"❌ MCP Server: {response.status_code}")
    except Exception as e:
        print(f"❌ MCP Server: {e}")
    
    # Check environment variables
    required_vars = ['DISCORD_BOT_TOKEN', 'SOCCER_MCP_URL']
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Missing")

if __name__ == "__main__":
    asyncio.run(health_check())
```

Run health check:
```bash
python health_check.py
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: "ModuleNotFoundError: No module named 'discord'"
**Solution:**
```bash
pip install discord.py
# Or if using virtual environment:
source soccer_bot_env/bin/activate
pip install discord.py
```

#### Issue: "Invalid Bot Token"
**Solution:**
1. Verify token is correct in Discord Developer Portal
2. Check for extra spaces or characters in environment variable
3. Regenerate token if necessary

#### Issue: "MCP Server Connection Failed"
**Solution:**
```bash
# Test MCP server directly
curl -X POST https://soccermcp-production.up.railway.app/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

# Check firewall/network restrictions
# Verify AUTH_KEY if required
```

#### Issue: "Bot Not Responding to Commands"
**Solution:**
1. Check bot permissions in Discord server
2. Verify bot is online (green status)
3. Re-sync slash commands:
```python
# In Python console:
import asyncio
from bot_structure import bot
asyncio.run(bot.tree.sync())
```

#### Issue: "Channel Creation Fails"
**Solution:**
1. Verify bot has "Manage Channels" permission
2. Check Discord server channel limits
3. Test with single channel creation first

### Getting Help

#### Log Analysis
```bash
# Check recent logs
tail -f discord_bot.log

# Search for errors
grep -i error discord_bot.log

# Check soccer-specific logs
tail -f soccer_bot_errors.log
```

#### Debug Mode
```bash
# Run bot in debug mode
LOG_LEVEL=DEBUG python bot_structure.py
```

#### Test Individual Components
```bash
# Test MCP client
python test_soccer_integration.py

# Test data processing
python test_soccer_data_processor.py

# Test embed creation
python test_soccer_embed_builder.py
```

## Security Best Practices

### Token Security
- ✅ Store tokens in environment variables only
- ✅ Never commit tokens to version control
- ✅ Use different tokens for development/production
- ✅ Rotate tokens regularly
- ✅ Restrict bot permissions to minimum required

### Network Security
- ✅ Use HTTPS for all external API calls
- ✅ Validate all input data
- ✅ Implement rate limiting
- ✅ Monitor for unusual activity

### Access Control
- ✅ Restrict admin commands to authorized users
- ✅ Log all administrative actions
- ✅ Regular permission audits

## Performance Optimization

### Production Settings
```python
# config.py optimizations
SOCCER_CONFIG = {
    "cache_duration_minutes": 15,
    "max_matches_per_day": 50,
    "rate_limiting": {
        "requests_per_minute": 30,
        "burst_limit": 5,
        "cooldown_seconds": 2
    }
}
```

### Memory Management
- Enable automatic channel cleanup
- Set reasonable cache limits
- Monitor memory usage regularly

### Network Optimization
- Use connection pooling for HTTP requests
- Implement request caching
- Set appropriate timeouts

---

**Setup Complete!** 🎉

Your Soccer Discord Integration environment is now ready for deployment. Follow the deployment checklist for production deployment.

**Support**: If you encounter issues, check the troubleshooting section or review the deployment checklist for additional guidance.