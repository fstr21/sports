# How to Test Your OpenRouter Discord Bridge

## 🎯 Quick Start Testing

### 1. Quick Automated Test
```bash
cd mcp_leagues/chat
python quick_test.py
```
**What it does:**
- Tests AI response generation
- Tests Discord MCP connection  
- Shows permission status
- Takes 10 seconds, no interaction needed

### 2. Interactive Manual Testing
```bash
cd mcp_leagues/chat
python test_manual.py
```
**Menu options:**
1. **Test AI Response** - Verify OpenRouter is working
2. **Test Discord Send** - Try sending message to Discord
3. **Test Discord Read** - Try reading Discord messages
4. **Quick Full Test** - Run all tests automatically
5. **Custom AI Prompt** - Test with your own prompts
6. **Send Custom Message** - Test Discord with custom messages
7. **Change Model** - Switch between AI models temporarily
8. **Exit**

### 3. Model Switching
```bash
cd mcp_leagues/chat
python switch_model.py
```
**Available models:**
- `anthropic/claude-3.5-haiku` - Fast & Cheap
- `anthropic/claude-3.5-sonnet` - Balanced (recommended)
- `openai/gpt-4-turbo` - Creative
- `meta-llama/llama-3.1-8b-instruct` - Budget
- `anthropic/claude-3-opus` - Premium (expensive)

## 🔧 Configuration

### Environment Variables (`.env` file)
```bash
# Your OpenRouter API key
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Active model (change this to switch models)
DEFAULT_MODEL=anthropic/claude-3.5-haiku

# Discord settings
DISCORD_MCP_URL=https://chatmcp-production.up.railway.app/mcp
DEFAULT_CHANNEL=mcp-testing
DEFAULT_DISCORD_SERVER=Foster
```

## 🧪 Expected Test Results

### ✅ Working Components
- **AI Response**: Should generate text responses
- **Discord MCP Connection**: Should connect to Foster server
- **Channel Discovery**: Should show 28+ available channels

### ⚠️ Permission Issues (Expected)
- **Discord Send**: Will fail with "Missing Access" 
- **Discord Read**: Will fail with "Missing Access"

**This is normal!** Your Discord bot needs permissions.

## 🔑 Discord Bot Permissions Needed

In your "Foster" Discord server, grant your bot:
1. **Send Messages** - To post AI responses
2. **Read Message History** - To provide context to AI

**How to fix:**
1. Go to Discord server settings
2. Find your bot in Members list
3. Grant the missing permissions
4. Re-run tests

## 🎮 Example Test Sessions

### Testing AI Generation
```bash
python test_manual.py
# Choose option 1: Test AI Response
# Watch AI generate a response
```

### Testing Different Models
```bash
python test_manual.py  
# Choose option 7: Change Model
# Pick a different model (e.g., Sonnet)
# Test AI response with new model
```

### Testing Discord Integration
```bash
python test_manual.py
# Choose option 2: Test Discord Send
# Enter a test message
# See permission status
```

## 🚀 Production Usage Examples

### Send AI-Generated Sports Content
```python
from openrouter_discord_bridge import OpenRouterDiscordBridge

async with OpenRouterDiscordBridge(api_key) as bridge:
    # Generate sports analysis
    prompt = "Analyze tonight's Yankees vs Red Sox game for betting"
    messages = [{"role": "user", "content": prompt}]
    analysis = await bridge.call_openrouter(messages)
    
    # Send to Discord
    await bridge.send_discord_message("aggregated-picks", analysis)
```

### Interactive Chat Bot
```python
# Read recent Discord messages for context
messages = await bridge.read_discord_messages("chat", limit=5)

# Generate contextual response
# Send AI response back to Discord
```

## 📊 Performance & Costs

### Model Performance
- **Haiku**: ~1-2 seconds, $0.001 per response
- **Sonnet**: ~2-4 seconds, $0.01 per response  
- **GPT-4**: ~3-5 seconds, $0.02 per response

### Daily Usage Estimate
- **100 AI responses/day**: $0.10 - $2.00 depending on model
- **Chat monitoring**: $0.01 - $0.10/hour
- **Daily picks generation**: $0.05 - $0.50/day

## 🔍 Troubleshooting

### "No API key found"
- Check `.env` file exists in chat folder
- Verify `OPENROUTER_API_KEY=sk-or-v1-...` is set
- Make sure no spaces around the `=`

### "AI Error" or API failures
- Check you have OpenRouter credits
- Try switching to cheaper model (Haiku)
- Verify API key is correct

### "Discord MCP failed"
- Check Railway deployment is running
- Test: `https://chatmcp-production.up.railway.app/health`
- Verify Discord bot token is set in Railway

### "Permission denied" (Discord)
- This is expected until you fix bot permissions
- Grant "Send Messages" and "Read Message History"
- Test in a channel the bot has access to

## 🎯 Next Steps

1. **Run quick test** to verify everything works
2. **Fix Discord permissions** when ready
3. **Choose your preferred model** for production
4. **Integrate with sports platform** for automated content
5. **Set up monitoring** for continuous operation

Your OpenRouter Discord Bridge is ready to power AI-driven sports betting community interactions!