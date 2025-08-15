# Sports Betting Analytics Platform - Project Overview

## 🎯 Mission Statement
A **subscription-based sports betting analytics service** that provides data-driven betting recommendations across major sports leagues. The platform aggregates real-time odds data with historical statistics to generate educated predictions for various betting markets.

## 🏗️ Architecture Overview

### Dual Architecture Approach
The project operates with **two distinct but complementary systems**:

1. **Railway MCP Server** (Production) - `https://web-production-b939f.up.railway.app`
   - Dedicated odds-only MCP server
   - 4 specialized tools for betting data
   - Uses The Odds API as primary source

2. **Local HTTP Server** (Development/Full Featured) - `sports_http_server.py`
   - Comprehensive ESPN + Odds integration
   - Full REST API with 20+ endpoints
   - AI-powered analysis via OpenRouter

### Core Data Sources
- **The Odds API**: Real-time betting odds, spreads, totals, player props
- **ESPN API**: Sports statistics, game data, team/player information  
- **OpenRouter AI**: Natural language analysis and predictions

## 🏆 Supported Sports & Leagues

### American Sports
- **NFL** (National Football League)
- **NBA** (National Basketball Association) 
- **WNBA** (Women's National Basketball Association)
- **MLB** (Major League Baseball)
- **NHL** (National Hockey League)
- **MLS** (Major League Soccer)

### International Soccer
- **English Premier League** (EPL)
- **La Liga** (Spanish First Division)

### College Sports
- **College Football**
- **Men's College Basketball**

## 🎲 Betting Markets Supported

### Standard Markets
- **Moneylines** (Win/Loss bets)
- **Point Spreads** (Handicap betting)
- **Totals** (Over/Under scoring)

### Player Props
- **Basketball**: Points, rebounds, assists, steals, blocks
- **Football**: Passing yards, rushing yards, touchdowns, receptions
- **Baseball**: Home runs, RBIs, hits, strikeouts
- **Hockey**: Goals, assists, shots, saves

## 📊 User Experience Flow

### Daily Workflow Example (NFL Game Day)
1. **Morning Update**: Display all NFL games scheduled
2. **Current Lines**: Present betting lines (moneylines, spreads, totals)
3. **Historical Analysis**: Team statistics and head-to-head data
4. **AI Predictions**: Generate recommendations with reasoning
5. **Player Props**: Individual player performance analysis

### Subscriber Benefits
- ✅ Aggregated data from multiple sources in one location
- ✅ Time-saving automated analysis  
- ✅ Educational explanations for each recommendation
- ✅ Multi-sport coverage under single subscription
- ✅ ROI tracking capabilities

## 🚀 Deployment Strategy

### Phase 1: Discord Bot (Current Focus)
- Discord server for initial subscriber base
- Real-time notifications and recommendations
- Interactive commands for odds lookup

### Phase 2: Web Application (Future)
- Full web interface for expanded features
- User accounts and preference management
- Advanced visualization and analytics

## 🔧 Technical Stack

### Backend
- **Python 3.11+**: Core runtime
- **FastAPI**: High-performance async web framework
- **Starlette**: Lightweight ASGI for MCP server
- **Uvicorn**: ASGI server for production
- **httpx**: Modern async HTTP client

### Protocols & Standards
- **MCP (Model Context Protocol)**: Standardized AI tool interface
- **JSON-RPC**: Protocol for MCP communication  
- **REST API**: HTTP endpoints for web clients

### Cloud Infrastructure
- **Railway**: Cloud deployment platform
- **Automatic CI/CD**: Git-based deployment pipeline
- **Environment Management**: Secure API key handling

## 📁 Project Structure

```
sports/
├── catchup/                     # 📖 LLM onboarding documentation
├── espn_ids/                    # 🏈 ESPN team/player ID mappings
├── sports_mcp/                  # 🤖 MCP server implementations
│   ├── wagyu_sports/           # 💰 Betting odds MCP server
│   └── sports_ai_mcp.py        # 📊 ESPN sports data integration
├── odds_mcp_server.py          # 🎯 Production MCP server (Railway)
├── sports_http_server.py       # 🌐 Development HTTP server (1,496 lines)
├── requirements.txt            # 📦 Python dependencies
└── README.md                   # 📚 Comprehensive documentation
```

## 🎯 Current Status

### ✅ Fully Operational
- **Railway MCP Server**: Live at `https://web-production-b939f.up.railway.app/mcp`
- **Odds Data Integration**: Real-time betting odds from The Odds API
- **ESPN Data Pipeline**: Comprehensive sports statistics
- **AI Analysis**: Natural language processing via OpenRouter
- **Test Infrastructure**: Mock data support for development

### 🔧 In Development  
- **Discord Bot Integration**: Subscriber interface
- **Prediction Algorithms**: Machine learning models
- **User Management**: Subscription and authentication systems

## 🎪 Key Differentiators

### Technical Excellence
- **Dual Architecture**: MCP for AI integration + HTTP for web clients
- **Real-time Data**: Live odds updates and game statistics
- **AI Integration**: Natural language query processing
- **Scalable Design**: Cloud-native with horizontal scaling

### Business Value
- **Multi-sport Coverage**: Single subscription for all major leagues
- **Educational Focus**: Explains reasoning behind recommendations
- **Time-saving Automation**: Aggregates multiple data sources
- **ROI Tracking**: Helps subscribers measure performance

## 🔮 Success Metrics

### Technical KPIs
- **API Response Time**: < 500ms average
- **Uptime**: 99.9% availability target
- **Data Freshness**: < 30 seconds for odds updates

### Business KPIs  
- **Prediction Accuracy**: Track recommendation success rate
- **Subscriber Retention**: Monthly active user engagement
- **ROI Performance**: Subscriber profit tracking
- **User Engagement**: Daily active users and session duration

---

*This platform represents a comprehensive approach to sports betting intelligence, combining real-time data aggregation, AI-powered analysis, and user-friendly delivery mechanisms to provide subscribers with actionable betting insights across multiple sports and markets.*