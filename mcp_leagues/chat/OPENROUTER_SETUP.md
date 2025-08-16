# OpenRouter Discord Bridge Setup Guide

## 🎯 Overview
This bridge connects **OpenRouter LLMs** with your **Discord MCP server** to create a powerful middleman for sports betting Discord communities.

**Flow**: `OpenRouter AI ↔ Bridge Script ↔ Discord MCP ↔ Discord Server`

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
cd mcp_leagues/chat
pip install httpx python-dotenv
```

### 2. Get OpenRouter API Key
1. Go to [OpenRouter.ai](https://openrouter.ai)
2. Sign up/login
3. Go to [Keys page](https://openrouter.ai/keys)
4. Create new API key
5. Copy the key

### 3. Configure Environment
```bash
# Copy example config
cp .env.example .env

# Edit .env file and add your key:
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### 4. Fix Discord Bot Permissions
Your Discord bot needs these permissions:
- ✅ **View Channels** (already has)
- ❌ **Send Messages** (needs this)
- ❌ **Read Message History** (needs this)

**Fix in Discord:**
1. Go to your server settings
2. Find your bot in Members
3. Grant missing permissions

### 5. Test the Bridge
```bash
# Test basic connectivity
python test_openrouter_bridge.py

# Test sports integration
python sports_discord_bot.py
```

## 🛠️ Available Components

### Core Bridge (`openrouter_discord_bridge.py`)
- **OpenRouterDiscordBridge**: Main integration class
- **send_discord_message()**: Send AI responses to Discord
- **read_discord_messages()**: Get Discord context for AI
- **call_openrouter()**: Send prompts to AI models

### Sports Bot (`sports_discord_bot.py`)
- **SportsDiscordBot**: Full sports betting Discord bot
- **generate_daily_mlb_picks()**: Automated daily picks
- **handle_user_question()**: Interactive Q&A
- **monitor_discord_chat()**: Continuous monitoring
- **post_line_movement_alert()**: Betting alerts

## 📊 Usage Examples

### Basic AI Chat
```python
from openrouter_discord_bridge import OpenRouterDiscordBridge

async with OpenRouterDiscordBridge(api_key) as bridge:
    # Send AI message to Discord
    result = await bridge.send_discord_message(
        channel="mcp-testing",
        message="Hello from OpenRouter AI!"
    )
    
    # Read Discord messages for context
    messages = await bridge.read_discord_messages(
        channel="chat", 
        limit=5
    )
```

### Sports Betting Integration
```python
from sports_discord_bot import SportsDiscordBot

# Your MCP URLs
sports_mcps = {
    "mlb": "https://mlbmcp-production.up.railway.app/mcp",
    "odds": "https://odds-mcp-v2-production.up.railway.app/mcp"
}

async with SportsDiscordBot(api_key, sports_mcps) as bot:
    # Generate daily picks
    await bot.generate_daily_mlb_picks("aggregated-picks")
    
    # Handle user questions
    await bot.handle_user_question("chat", "Best MLB bets tonight?")
```

### Automated Workflows
```python
# Daily picks at 9 AM
async def daily_picks_job():
    async with SportsDiscordBot(api_key, mcps) as bot:
        await bot.generate_daily_mlb_picks("aggregated-picks")

# Continuous chat monitoring  
async def start_chat_bot():
    async with SportsDiscordBot(api_key, mcps) as bot:
        await bot.monitor_discord_chat("chat", check_interval=30)
```

## 🤖 OpenRouter Models

### Recommended Models:
- **`anthropic/claude-3.5-sonnet`** - Best reasoning, higher cost
- **`anthropic/claude-3.5-haiku`** - Fast and cheap for testing  
- **`openai/gpt-4-turbo`** - Good balance of quality/cost
- **`meta-llama/llama-3.1-8b-instruct`** - Cheapest option

### Model Selection:
```python
# High-quality analysis
bridge = OpenRouterDiscordBridge(
    api_key, 
    default_model="anthropic/claude-3.5-sonnet"
)

# Cost-effective for high volume
bridge = OpenRouterDiscordBridge(
    api_key,
    default_model="anthropic/claude-3.5-haiku"  
)
```

## 🏈 Sports Platform Integration

### Your MCP Ecosystem:
- **MLB MCP**: `https://mlbmcp-production.up.railway.app/mcp`
- **Soccer MCP**: `https://soccermcp-production.up.railway.app/mcp`
- **CFB MCP**: `https://cfbmcp-production.up.railway.app/mcp`
- **Odds MCP**: `https://odds-mcp-v2-production.up.railway.app/mcp`
- **Discord MCP**: `https://chatmcp-production.up.railway.app/mcp`

### Integration Possibilities:
1. **Daily Picks**: AI analyzes games + odds → posts to Discord
2. **Line Movement Alerts**: Odds changes → AI analysis → Discord alerts
3. **User Q&A**: Discord questions → AI + sports data → responses
4. **Community Analysis**: Discord sentiment + game data → insights

## 🔧 Troubleshooting

### Common Issues:

**❌ "Missing Access" Discord Error**
- Fix: Grant bot "Send Messages" and "Read Message History" permissions

**❌ "OpenRouter API error"**  
- Check API key in .env file
- Verify you have OpenRouter credits
- Try a cheaper model first

**❌ "MCP call failed"**
- Verify Discord MCP is running: `https://chatmcp-production.up.railway.app/health`
- Check network connectivity
- Try manual curl test

**❌ "No games found"**
- Sports MCPs might be rate limited
- Check if it's off-season for the sport
- Verify MCP server URLs

### Debug Mode:
```python
# Add verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test individual components
await bridge.call_discord_mcp("read-messages", {"channel": "test"})
```

## 💰 Cost Optimization

### Tips:
1. **Use Haiku for high-volume operations** (chat monitoring)
2. **Use Sonnet for important analysis** (daily picks)
3. **Limit message context** (fewer Discord messages = lower costs)
4. **Cache responses** for repeated questions
5. **Monitor usage** via OpenRouter dashboard

### Example Cost Structure:
- **Chat monitoring**: ~$0.01/hour with Haiku
- **Daily picks**: ~$0.05/day with Sonnet  
- **User Q&A**: ~$0.001/question with Haiku

## 🎯 Next Steps

1. ✅ **Setup complete** - Bridge ready to use
2. 🔧 **Fix Discord permissions** - Enable bot message access
3. 🧪 **Run tests** - Verify all components work
4. 🚀 **Deploy workflows** - Start automated picks/monitoring
5. 📈 **Scale up** - Add more channels and sports

Your OpenRouter Discord Bridge is now ready to power AI-driven sports betting community interactions!