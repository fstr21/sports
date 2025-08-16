# 🤖 Sports Discord Bot - Railway Deployment

A production-ready Discord bot for sports betting analytics, integrating with all MCP servers.

## 🚀 Features

### **Slash Commands**
- `/setup` - Setup complete channel structure for server
- `/games [sport]` - Today's games across all sports
- `/odds [sport]` - Current betting odds
- `/analyze <query>` - AI analysis for games/situations  
- `/standings [league]` - League standings
- `/refresh-channels [sport]` - Refresh game channels for today
- `/cleanup [days]` - Clean up old game channels

### **Automated Features**
- **Channel Management** - Automatically creates/organizes channels by sport and date
- **Daily Hot Picks** - Posted automatically to `#🔥-hot-picks` channel
- **Game Channels** - Dynamic channels created for each day's games
- **AI-Powered Analysis** - OpenRouter integration for intelligent responses
- **Multi-MCP Integration** - Connects to MLB, Soccer, CFB, and Odds MCPs
- **Auto Cleanup** - Removes old game channels automatically

### **Channel Management**
The bot automatically creates and manages this complete Discord server structure:

```
📚 BETTING EDUCATION
├── 💰-bankroll-management
├── 📈-tracking-your-bets  
├── 🎯-understanding-value
└── 🤖-how-our-ai-works

🏆 LEADERBOARDS
├── 📊-weekly-winners
├── 💯-accuracy-tracking
└── 👥-community-picks

📌 FEATURED TODAY
├── 🔥-hot-picks (Auto-posted daily)
├── 🎰-high-confidence  
└── 💎-value-plays

⚾ MLB GAMES (Dynamic)
├── 08-16-yankees-vs-red-sox
├── 08-16-dodgers-vs-giants
└── (Auto-created daily)

⚽ SOCCER GAMES (Dynamic)
├── 08-16-liverpool-vs-chelsea
├── 08-16-arsenal-vs-city
└── (Auto-created for match days)

🏈 CFB GAMES (Dynamic)
├── 08-23-iowa-state-vs-kansas-state
└── (Auto-created for game days)

🎲 LIVE BETTING
├── ⚡-live-odds
├── 📊-line-movements
└── 🚨-value-alerts
```

## 🔧 Railway Deployment

### **Environment Variables Required**
```env
# Discord Bot Token (from Discord Developer Portal)
DISCORD_TOKEN=your_discord_bot_token

# OpenRouter API for AI analysis
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=anthropic/claude-3.5-haiku

# MCP Server URLs (default to your Railway deployments)
MLB_MCP_URL=https://mlbmcp-production.up.railway.app/mcp
SOCCER_MCP_URL=https://soccermcp-production.up.railway.app/mcp  
CFB_MCP_URL=https://cfbmcp-production.up.railway.app/mcp
ODDS_MCP_URL=https://odds-mcp-v2-production.up.railway.app/mcp

# Optional Discord Settings
DEFAULT_GUILD=Foster
DEFAULT_CHANNEL=mcp-testing
```

### **Deployment Steps**
1. Push this directory to a GitHub repository
2. Connect to Railway
3. Set environment variables in Railway dashboard
4. Deploy automatically

## 🎯 Discord Bot Setup Required

### **Create Discord Application**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create new application named "Sports Betting AI"
3. Go to "Bot" section → "Add Bot"
4. Copy bot token → Set as `DISCORD_TOKEN` in Railway

### **Required Scopes** (for bot invite):
- ✅ **bot**
- ✅ **applications.commands**

### **Required Permissions** (for bot functionality):
- ✅ **View Channels** 
- ✅ **Send Messages**
- ✅ **Use Slash Commands**
- ✅ **Embed Links**
- ✅ **Attach Files** 
- ✅ **Read Message History**
- ✅ **Add Reactions**
- ✅ **Manage Messages**
- ✅ **Use External Emojis**
- ✅ **Manage Channels** ⚡ **REQUIRED FOR CHANNEL MANAGEMENT**
- ✅ **Create Public Threads** (optional)
- ✅ **Manage Threads** (optional)

### **Required Intents** (in Bot settings):
- ✅ **Message Content Intent** (essential)
- ✅ **Server Members Intent** (for channel permissions)
- ❌ **Presence Intent** (not needed)

## 🧪 Testing

### **Local Testing**
```bash
# Set environment variables in .env.local
DISCORD_TOKEN=your_token
OPENROUTER_API_KEY=your_key

# Run locally
python sports_discord_bot.py
```

### **Health Check**
Railway exposes a health endpoint at `/health` for monitoring.

## 📊 Integration

### **MCP Servers**
The bot integrates with your existing MCP infrastructure:
- **MLB MCP** - Game schedules, scores, stats
- **Soccer MCP** - EPL/La Liga fixtures and standings  
- **CFB MCP** - College football data
- **Odds MCP** - Live betting odds and player props

### **AI Analysis**
Uses OpenRouter API for intelligent sports analysis and betting insights.

## 🚀 Usage

Once deployed and invited to your Discord server:

1. **Run `/setup`** to create the complete channel structure
2. **Game channels** automatically created daily for each sport
3. **Use slash commands** for immediate data access
4. **Daily picks** automatically posted to `#🔥-hot-picks`
5. **AI analysis** available via `/analyze` command
6. **Channel cleanup** with `/cleanup` command
7. **Refresh channels** with `/refresh-channels` command

Perfect for launching your sports betting Discord community with professional-grade automation and data integration!