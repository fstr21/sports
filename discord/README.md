# 🤖 Sports Betting Discord Bot

## 📋 Overview

Discord bot for sports betting analytics with category-based league organization. Each sport gets its own category, with individual channels for specific game matchups.

## 🏗️ Server Structure

```
🏈 NFL
├── 📊 bears-vs-cardinals
├── 📊 49ers-vs-commanders  
├── 📊 chiefs-vs-bills
└── 📊 cowboys-vs-eagles

⚾ MLB
├── 📊 yankees-vs-red-sox
├── 📊 dodgers-vs-giants
├── 📊 astros-vs-rangers
└── 📊 braves-vs-mets

⚽ SOCCER
├── 📊 liverpool-vs-arsenal
├── 📊 real-madrid-vs-barcelona
├── 📊 man-city-vs-chelsea
└── 📊 bayern-vs-dortmund
```

## 🎯 Key Features

### **Automated Organization**
- Categories by sport (NFL, MLB, Soccer, etc.)
- Game-specific channels with matchup names
- Automatic cleanup of old games
- Season-aware activation/deactivation

### **Comprehensive Commands**
- `/schedule` - Games for specific league/date
- `/odds` - Current betting lines
- `/player` - Player stats and prop history
- `/gameinfo` - Detailed matchup analysis
- `/props` - Player props for specific games

### **MCP Integration Ready**
- Designed to work with existing MCP servers
- MLB, Soccer, College Football, and Odds MCPs
- ESPN Player ID integration planned
- Real-time data updates

## 🚀 Quick Start

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Set Environment Variables**
```bash
# Required
DISCORD_BOT_TOKEN=your_discord_bot_token

# Optional (for MCP integration)
SPORTS_API_KEY=your_api_key
ODDS_API_KEY=your_odds_api_key
```

### **3. Bot Setup**
```python
# Create Discord application and bot
# Get bot token from Discord Developer Portal
# Add bot to your server with proper permissions
```

### **4. Run Bot**
```python
python bot_structure.py
```

## 🔧 Configuration

Edit `config.py` to customize:
- League settings and schedules
- Channel management rules
- Command permissions
- MCP server URLs
- Subscription tiers

## 📊 Command Structure

### **Global Commands** (Any Channel)
- `/schedule [league] [date]` - Show game schedules
- `/odds [team1] [team2]` - Get betting odds
- `/player [name]` - Player statistics
- `/weather [game]` - Weather conditions
- `/bankroll` - Bankroll management tools

### **Channel Commands** (Game Channels Only)
- `/gameinfo` - Detailed matchup analysis
- `/props` - All player props for this game
- `/prediction` - AI analysis and recommendations
- `/lineup` - Starting lineups and key players
- `/history` - Head-to-head historical data

### **Admin Commands**
- `/setup [league] [team1] [team2]` - Create game channel
- `/cleanup [days]` - Remove old channels
- `/toggle [league]` - Enable/disable league

## 🎮 User Flow

### **Daily Usage**
1. Check `/schedule today` for day's games
2. Visit specific game channels for analysis
3. Use `/odds` and `/props` for betting info
4. Get real-time updates during games
5. Review results and prep for tomorrow

### **Channel Lifecycle**
1. **Pre-Game**: Analysis, odds, predictions
2. **Live**: Real-time updates, in-game betting
3. **Post-Game**: Results, performance review
4. **Cleanup**: Auto-delete after 3 days

## 🔌 MCP Integration Points

### **Ready for Integration**
- MLB MCP: Game schedules, player stats, rosters
- Soccer MCP: Fixtures, standings, team data  
- College Football MCP: Games, rankings, player info
- Odds MCP: Live betting lines, player props

### **Planned Integrations**
- ESPN Player ID MCP: Enhanced player data
- Weather API: Game condition analysis
- AI Analysis Engine: Prediction algorithms

## 📈 Roadmap

### **Phase 1: Foundation** ✅
- [x] Discord server structure
- [x] Basic bot commands  
- [x] Channel management system
- [x] MCP integration framework

### **Phase 2: Data Integration** 🔄
- [ ] Connect existing MCP servers
- [ ] Real-time odds updates
- [ ] Player statistics integration
- [ ] Weather data integration

### **Phase 3: Advanced Features** 📋
- [ ] AI-powered predictions
- [ ] Live game tracking
- [ ] User preference system
- [ ] Subscription management

### **Phase 4: Scale** 🚀
- [ ] Multiple server support
- [ ] Performance optimization
- [ ] Advanced analytics
- [ ] Mobile companion app

## 🛡️ Permissions Required

### **Bot Permissions**
- Read Messages
- Send Messages
- Manage Channels
- Embed Links
- Use Slash Commands
- Manage Messages (for cleanup)

### **Admin Commands**
- Administrator role required for:
  - Channel creation (`/setup`)
  - Channel cleanup (`/cleanup`)
  - League toggling (`/toggle`)

## 📝 Development Notes

### **Current Status**
- Bot structure complete
- Command framework ready
- MCP integration points defined
- Ready for data connection

### **Next Steps**
1. Set up Discord bot and get token
2. Connect to existing MCP servers
3. Test basic functionality
4. Add real data integration
5. Beta testing with sample games

### **File Structure**
```
discord/
├── README.md              # This file
├── DISCORD_PLAN.md        # Detailed planning document
├── bot_structure.py       # Main bot code
├── config.py              # Configuration settings
└── requirements.txt       # Python dependencies
```

## 🎯 Your Original Vision

**Perfect implementation of your category-by-league, channel-by-game structure:**
- Categories represent sports leagues
- Channels represent specific matchups
- Focused discussions per game
- Easy navigation and organization
- Scales across multiple sports seasons

The structure supports your vision while providing room for growth and advanced features as the platform develops.