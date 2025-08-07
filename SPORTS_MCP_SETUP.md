# Sports MCP Setup Guide
**Complete installation guide for Sports AI MCP + Wagyu Sports MCP integration**

---

## 🎯 **What You're Installing**

This setup provides two powerful MCP servers for sports betting analysis:

1. **Sports AI MCP** - ESPN data + AI analysis (custom built)
2. **Wagyu Sports MCP** - Live betting odds from The Odds API
3. **Integration Test Suite** - Combined analysis with OpenRouter AI

**Result**: Ask questions like *"Who will score the most points in tonight's WNBA games?"* and get specific player predictions with reasoning.

---

## 📋 **Prerequisites**

### **Required Software**
- **Python 3.8+** (tested with Python 3.13)
- **Kiro IDE** (or Claude Desktop with MCP support)
- **Git** (for cloning repositories)

### **Required API Keys**
- **OpenRouter API Key** - For AI analysis ([Get here](https://openrouter.ai/))
- **The Odds API Key** - For betting odds ([Get here](https://the-odds-api.com/))

---

## 🚀 **Installation Steps**

### **Step 1: Clone the Repository**
```bash
# Clone your sports MCP repository
git clone [YOUR_REPO_URL] sports
cd sports
```

### **Step 2: Install Python Dependencies**
```bash
# Install required packages
pip install -r requirements.txt

# If requirements.txt doesn't exist, install manually:
pip install httpx python-dotenv mcp fastmcp pydantic requests
```

### **Step 3: Configure Environment Variables**
Create `.env.local` in the root directory:

```bash
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openrouter/horizon-beta

# The Odds API Configuration  
ODDS_API_KEY=your_odds_api_key_here
```

**⚠️ Important**: Replace `your_openrouter_api_key_here` and `your_odds_api_key_here` with your actual API keys.

### **Step 4: Configure Kiro MCP Settings**
Create or update `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "sports-ai": {
      "command": "python",
      "args": [
        "mcp/sports_ai_mcp.py"
      ],
      "disabled": false,
      "autoApprove": []
    },
    "wagyu-sports": {
      "command": "python",
      "args": [
        "mcp/wagyu_sports/mcp_server/odds_client_server.py"
      ],
      "env": {
        "ODDS_API_KEY": "your_odds_api_key_here"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**⚠️ Important**: Replace `your_odds_api_key_here` with your actual Odds API key.

---

## 🧪 **Testing Your Installation**

### **Test 1: OpenRouter Connection**
```bash
python test/openrouter_test.py
```
**Expected Output**: `✅ OpenRouter API test SUCCESSFUL!`

### **Test 2: Sports AI MCP**
```bash
python test/debug_sports_ai.py
```
**Expected Output**: Should show 3 WNBA games with actual player names like "Allisha Gray", "Kelsey Plum", etc.

### **Test 3: Full Integration**
```bash
python test/mcp_integration_test.py
```
**Try asking**: *"Who will score the most points in each WNBA game today?"*

**Expected Output**: Detailed analysis with specific player predictions and reasoning.

---

## 📁 **Project Structure**

```
sports/
├── .env.local                          # Your API keys (create this)
├── .kiro/settings/mcp.json            # Kiro MCP configuration
├── mcp/
│   ├── sports_ai_mcp.py               # Custom Sports AI MCP server
│   └── wagyu_sports/                  # Wagyu Sports MCP
│       └── mcp_server/
│           ├── odds_client_server.py  # Main Wagyu server
│           └── odds_client.py         # Odds API client
├── test/
│   ├── mcp_integration_test.py        # 🏆 Main testing script
│   ├── debug_sports_ai.py             # Sports AI MCP testing
│   ├── openrouter_test.py             # OpenRouter connection test
│   └── logs/                          # Test logs and debugging
└── docs/
    └── custom-mcp/
        └── data-availability.md       # ESPN API data reference
```

---

## 🔧 **Key Features**

### **Sports AI MCP Capabilities**
- **Real player data** - Actual names and statistics
- **ESPN integration** - Live scores, team records, player leaders
- **Eastern timezone** - Proper date/time handling
- **AI analysis** - Powered by OpenRouter

### **Wagyu Sports MCP Capabilities**
- **Live betting odds** - Multiple sportsbooks
- **Real-time data** - No mock data, actual API calls
- **Multiple markets** - Spreads, moneylines, totals
- **API quota tracking** - Monitor usage

### **Integration Features**
- **Combined analysis** - ESPN data + betting odds + AI insights
- **Intent detection** - Automatically determines what data is needed
- **Detailed logging** - Full debugging and performance tracking
- **Error handling** - Graceful failures with helpful messages

---

## 💡 **Usage Examples**

### **Player Analysis**
```
Question: "Who will get the most rebounds in tonight's WNBA games?"
Response: Detailed analysis with specific players like "Kamilla Cardoso (8.3 RPG) should lead Chicago in rebounds because..."
```

### **Betting Analysis**
```
Question: "What are the best spread bets for tonight's games?"
Response: Specific recommendations with odds, reasoning, and risk assessment
```

### **Combined Analysis**
```
Question: "Based on player matchups and betting lines, which game has the best value?"
Response: Comprehensive analysis combining ESPN player data with live betting odds
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **"No module named 'mcp'"**
```bash
pip install mcp fastmcp
```

#### **"OPENROUTER_API_KEY not found"**
- Check that `.env.local` exists in the root directory
- Verify your API key is correct (starts with `sk-or-v1-`)

#### **"ESPN API returned 0 events"**
- The Sports AI MCP uses Eastern timezone
- Make sure you're asking about current/upcoming games
- Check ESPN.com to verify games are scheduled

#### **"Wagyu Sports MCP connection failed"**
- Verify your Odds API key is valid
- Check your API quota at [the-odds-api.com](https://the-odds-api.com/)
- Try running in test mode first

#### **"Only getting generic player descriptions"**
- This was fixed in the latest version
- Make sure you're using the updated `mcp/sports_ai_mcp.py`
- The system should return actual names like "Allisha Gray", not "Atlanta's primary scorer"

### **Debug Commands**
```bash
# Test individual components
python test/openrouter_test.py          # Test OpenRouter connection
python test/debug_sports_ai.py          # Test Sports AI MCP
python test/debug_espn_data.py          # Examine raw ESPN data

# Check logs
ls test/logs/                           # View all log files
cat test/logs/mcp_test_*.log           # View latest integration test log
```

---

## 📊 **API Usage & Costs**

### **OpenRouter**
- **Cost**: ~$0.01-0.05 per query
- **Usage**: AI analysis and text generation
- **Monitoring**: Check usage at [openrouter.ai](https://openrouter.ai/)

### **The Odds API**
- **Free Tier**: 500 requests/month
- **Cost**: $0.001 per request after free tier
- **Usage**: Live betting odds data
- **Monitoring**: Check quota with `get_quota_info` tool

### **ESPN API**
- **Cost**: Free
- **Usage**: Game data, player statistics, team information
- **Rate Limits**: Reasonable usage is fine

---

## 🔄 **Updating**

### **To Update Sports AI MCP**
1. Pull latest changes from your repository
2. Restart Kiro or reconnect MCP servers
3. Test with `python test/debug_sports_ai.py`

### **To Update Wagyu Sports MCP**
1. Pull latest changes from the wagyu repository
2. Update `.kiro/settings/mcp.json` if needed
3. Test with the integration script

---

## 🆘 **Support**

### **If You Get Stuck**
1. **Check the logs** - `test/logs/` contains detailed debugging info
2. **Test components individually** - Use the debug scripts
3. **Verify API keys** - Make sure they're valid and have quota
4. **Check ESPN data** - Visit ESPN.com to verify games exist

### **Known Working Configuration**
- **Python**: 3.13
- **OS**: Windows 11
- **Kiro**: Latest version
- **APIs**: OpenRouter + The Odds API
- **Timezone**: Eastern (EDT/EST)

---

## ✅ **Success Indicators**

You'll know everything is working when:

1. **OpenRouter test passes** - API connection successful
2. **Sports AI returns player names** - "Allisha Gray", not "Atlanta's scorer"
3. **Wagyu returns real odds** - Actual sportsbook data, not mock
4. **Integration test works** - Combined analysis with specific recommendations
5. **Logs show real data** - API calls successful, no errors

**Final Test**: Ask *"Who will score the most points in tonight's WNBA games and why?"* - you should get specific player names with detailed reasoning.

---

---

## 🚧 **Known Limitations & Future Development**

### **Currently Supported Sports**
- ✅ **WNBA** - Fully functional with player names and statistics
- ⚠️ **NFL** - Function exists but needs testing
- ❌ **MLB** - Detected but not properly handled (returns 400 error)
- ❌ **NBA** - Not implemented yet

### **Current MLB Issue**
When asking about MLB games, you'll see this error:
```
Client error '400 Bad Request' for url 'http://site.api.espn.com/apis/site/v2/sports/baseball_mlb/wnba/scoreboard'
```

**Root Cause**: The integration test tries to call MLB but the Sports AI MCP doesn't have proper MLB endpoint handling.

**Workaround**: Use WNBA queries for now, MLB support is planned for next development cycle.

---

**🎉 Congratulations! You now have a complete sports betting analysis system with real player data and live odds integration for WNBA games.**