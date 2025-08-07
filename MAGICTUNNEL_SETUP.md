# Magic Tunnel Sports Betting Analysis System - Setup Guide

**Complete setup documentation for recreating our sports betting analysis system with Magic Tunnel integration**

---

## 🎯 **What We Built**

A comprehensive sports betting analysis system that combines:
- **Sports AI MCP** - ESPN data + AI analysis for WNBA, NFL, and more
- **Wagyu Sports MCP** - Live betting odds from The Odds API
- **Magic Tunnel** - Smart MCP proxy for intelligent tool discovery
- **Interactive Analysis Tool** - Multi-sport betting recommendations

---

## 📋 **Prerequisites**

### **Required Software**
- **Python 3.8+** (tested with Python 3.13)
- **Kiro IDE** (or Claude Desktop with MCP support)
- **Git** (for cloning repositories)
- **Rust** (for Magic Tunnel compilation)

### **Required API Keys**
- **OpenRouter API Key** - For AI analysis ([Get here](https://openrouter.ai/))
- **The Odds API Key** - For betting odds ([Get here](https://the-odds-api.com/))

---

## 🚀 **Installation Steps**

### **Step 1: Clone and Setup Main Project**
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
pip install httpx python-dotenv mcp fastmcp pydantic requests schedule
```

### **Step 3: Configure Environment Variables**
Create `.env.local` in the root directory:

```bash
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-oss-20b:free

# The Odds API Configuration  
ODDS_API_KEY=your_odds_api_key_here
```

**⚠️ Important**: Replace with your actual API keys.

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
      "env": {
        "OPENROUTER_API_KEY": "your_openrouter_api_key_here",
        "OPENROUTER_BASE_URL": "https://openrouter.ai/api/v1",
        "OPENROUTER_MODEL": "openai/gpt-oss-20b:free"
      },
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
      "autoApprove": [
        "get_sports"
      ]
    }
  }
}
```

### **Step 5: Setup Magic Tunnel**
```bash
# Clone Magic Tunnel
git clone https://github.com/MagicBeansAI/magictunnel.git
cd magictunnel

# Build Magic Tunnel with smart discovery
make build-release-semantic && make pregenerate-embeddings-ollama MAGICTUNNEL_ENV=development

# Return to main project
cd ..
```

---

## 🧪 **Testing Your Installation**

### **Test 1: System Status**
```bash
python test/final_integration_test.py
```
**Expected Output**: Complete system status showing all components working.

### **Test 2: Interactive Analysis**
```bash
python sports_analysis.py
```
**Try asking**: 
- "What are the best WNBA bets for tonight?"
- "Show me NFL spreads and recommend which to bet"
- "Which MLB games have the best value?"

### **Test 3: Magic Tunnel Integration**
```bash
cd magictunnel
./magictunnel-supervisor

# Access Web Dashboard
open http://localhost:5173/dashboard

# Test smart discovery
curl -X POST http://localhost:3001/v1/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "smart_tool_discovery", 
    "arguments": {"request": "get WNBA odds"}
  }'
```

---

## 📁 **Project Structure**

```
sports/
├── .env.local                          # Your API keys
├── .kiro/settings/mcp.json            # Kiro MCP configuration
├── sports_analysis.py                 # 🏆 Interactive analysis tool
├── mcp/
│   ├── sports_ai_mcp.py               # Sports AI MCP server
│   └── wagyu_sports/                  # Wagyu Sports MCP
│       └── mcp_server/
│           ├── odds_client_server.py  # Main Wagyu server
│           └── odds_client.py         # Odds API client
├── test/
│   ├── final_integration_test.py      # System status test
│   └── logs/                          # Test logs
├── magictunnel/                       # Magic Tunnel smart proxy
│   ├── magictunnel                    # Main executable
│   ├── magictunnel-supervisor         # Supervisor mode
│   └── frontend/                      # Web dashboard
└── requirements.txt                   # Python dependencies
```

---

## 🔧 **Key Components**

### **Sports AI MCP Capabilities**
- **WNBA Analysis** - Real player data and statistics
- **NFL Analysis** - Game analysis and predictions  
- **Custom Sports** - Flexible analysis for any sport
- **ESPN Integration** - Live scores, team records, player leaders
- **AI Analysis** - Powered by OpenRouter

### **Wagyu Sports MCP Capabilities**
- **Live Betting Odds** - Multiple sportsbooks (DraftKings, FanDuel, BetMGM, etc.)
- **Multiple Sports** - WNBA, NFL, MLB, NHL, Soccer, Tennis, etc.
- **Multiple Markets** - Spreads, moneylines, totals
- **Real-time Data** - No mock data, actual API calls
- **API Quota Tracking** - Monitor usage

### **Magic Tunnel Features**
- **Smart Discovery** - AI-powered tool selection
- **Web Dashboard** - Visual monitoring and management
- **Supervisor Mode** - Manages multiple MCP servers
- **Semantic Search** - Understands natural language requests
- **Protocol Compatibility** - Works with existing MCP servers

### **Interactive Analysis Tool**
- **Multi-Sport Support** - WNBA, NFL, MLB, NHL, Soccer
- **Smart Sport Detection** - Automatically detects which sport you're asking about
- **Live Data Integration** - Combines ESPN data with betting odds
- **AI-Powered Recommendations** - Specific betting advice with reasoning

---

## 💡 **Usage Examples**

### **Direct MCP Tool Usage (via Kiro)**
```
Ask Kiro: "Analyze today's WNBA games"
Result: Detailed analysis with player matchups and AI insights
```

### **Interactive Analysis Tool**
```bash
python sports_analysis.py

💬 Your question: What are the best NFL bets this week?

🔍 Analyzing your question: 'What are the best NFL bets this week?'
🏆 Detected sport: NFL
📈 Getting NFL games analysis from Sports AI MCP...
💰 Getting live NFL betting odds from Wagyu Sports MCP...
🤖 Generating AI-powered betting recommendations...

🎯 AI BETTING ANALYSIS
[Detailed NFL betting recommendations with reasoning]
```

### **Magic Tunnel Smart Discovery**
```bash
# Instead of remembering exact tool names, just ask naturally:
curl -X POST http://localhost:3001/v1/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "smart_tool_discovery", 
    "arguments": {"request": "analyze WNBA player performance"}
  }'
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **"OPENROUTER_API_KEY not found"**
- Check that `.env.local` exists in the root directory
- Verify your API key is correct (starts with `sk-or-v1-`)
- Ensure the key is also in `.kiro/settings/mcp.json`

#### **"MCP Connection Issues"**
- Check that both MCP servers are properly configured in `.kiro/settings/mcp.json`
- Restart Kiro or reconnect MCP servers from the MCP Server view
- Verify Python dependencies are installed

#### **"Magic Tunnel Build Errors"**
- Ensure Rust is installed: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- Install Ollama for embeddings: [ollama.ai](https://ollama.ai/)
- Check build logs for specific dependency issues

#### **"No games found"**
- The system uses Eastern timezone for date handling
- Make sure you're asking about current/upcoming games
- Check ESPN.com to verify games are scheduled
- Verify your Odds API quota at [the-odds-api.com](https://the-odds-api.com/)

### **Debug Commands**
```bash
# Test individual components
python test/final_integration_test.py    # Test system status
python sports_analysis.py               # Test interactive tool

# Check MCP servers in Kiro
# Go to MCP Server view and check connection status

# Check Magic Tunnel logs
cd magictunnel
./magictunnel-supervisor
# Check console output for errors
```

---

## 📊 **API Usage & Costs**

### **OpenRouter**
- **Model**: `openai/gpt-oss-20b:free` (Free tier)
- **Usage**: AI analysis and text generation
- **Monitoring**: Check usage at [openrouter.ai](https://openrouter.ai/)

### **The Odds API**
- **Free Tier**: 500 requests/month
- **Cost**: $0.001 per request after free tier
- **Usage**: Live betting odds data
- **Monitoring**: Check quota with MCP tools or API directly

### **ESPN API**
- **Cost**: Free
- **Usage**: Game data, player statistics, team information
- **Rate Limits**: Reasonable usage is fine

---

## 🔄 **Updating the System**

### **Update Sports MCP**
1. Pull latest changes from your repository
2. Restart Kiro or reconnect MCP servers
3. Test with `python test/final_integration_test.py`

### **Update Magic Tunnel**
```bash
cd magictunnel
git pull origin main
make build-release-semantic
./magictunnel-supervisor
```

### **Update Dependencies**
```bash
pip install -r requirements.txt --upgrade
```

---

## ✅ **Success Indicators**

You'll know everything is working when:

1. **System Status Test Passes** - All components show ✅ WORKING
2. **Interactive Tool Works** - Multi-sport analysis with real data
3. **Magic Tunnel Responds** - Smart discovery finds the right tools
4. **Live Data Flows** - Real player names, current odds, AI analysis
5. **Web Dashboard Loads** - http://localhost:5173/dashboard shows tools

**Final Test**: Ask *"What are the best bets for tonight's games?"* - you should get specific recommendations with detailed reasoning across multiple sports.

---

## 🚧 **Current Limitations & Future Development**

### **Currently Fully Supported**
- ✅ **WNBA** - Complete with player names, statistics, and analysis
- ✅ **NFL** - Basic analysis and live odds
- ✅ **Live Odds** - All major sports via Wagyu Sports MCP

### **Partially Supported**
- ⚠️ **MLB/NHL/Soccer** - Odds available, analysis needs enhancement
- ⚠️ **NBA** - Currently in off-season (inactive in odds API)

### **Magic Tunnel Integration**
- ✅ **Smart Discovery** - Working with semantic search
- ✅ **Web Dashboard** - Visual tool management
- 🔄 **Advanced Routing** - In development for complex multi-tool workflows

---

## 🎉 **System Capabilities Summary**

**🏀 Multi-Sport Analysis**: WNBA, NFL, MLB, NHL, Soccer support  
**💰 Live Betting Odds**: Real-time data from major sportsbooks  
**🤖 AI-Powered Insights**: Detailed analysis using OpenRouter  
**🔍 Smart Discovery**: Magic Tunnel finds the right tool automatically  
**📊 Web Dashboard**: Visual monitoring and management  
**🎯 Interactive Interface**: Natural language sports betting queries  

**Your complete sports betting analysis ecosystem is ready!** 🚀

---

## 📞 **Support & Maintenance**

### **If You Get Stuck**
1. **Check the logs** - `test/logs/` and Magic Tunnel console output
2. **Test components individually** - Use the debug commands above
3. **Verify API keys** - Make sure they're valid and have quota
4. **Check service status** - ESPN, OpenRouter, and Odds API availability

### **Regular Maintenance**
- **Monitor API quotas** - Especially The Odds API usage
- **Update dependencies** - Keep Python packages current
- **Check MCP connections** - Restart if needed
- **Review logs** - Look for any recurring errors

### **Backup Important Files**
- `.env.local` - Your API keys
- `.kiro/settings/mcp.json` - MCP configuration
- `sports_analysis.py` - Your main analysis tool
- This setup guide - For future reference

---

**🎯 This system provides professional-grade sports betting analysis with the intelligence of Magic Tunnel's smart discovery. Perfect for making informed betting decisions across multiple sports!**