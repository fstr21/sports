# Railway Deployment Guide for Enhanced Soccer MCP

## 🚀 Railway Deployment Settings

### **1. Repository Configuration**
- **Repository**: Connect your GitHub repo containing this `mcp-soccer-data` folder
- **Root Directory**: Set to the `mcp-soccer-data` folder path
- **Branch**: main (or your default branch)

### **2. Build Settings** 
These are automatically configured via `railway.toml`:
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python src/enhanced_server.py"
healthcheckPath = "/"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10

[env]
PORT = "8080"
```

### **3. Environment Variables**
**CRITICAL**: Set this environment variable in Railway dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `AUTH_KEY` | `your_soccerdataapi_token` | Your SoccerDataAPI.com authentication token |

### **4. Service Settings**
- **Service Name**: `enhanced-soccer-mcp` (or your preferred name)
- **Region**: Choose closest to your users
- **Plan**: Starter plan is sufficient for this workload

## 🔧 MCP Server Details

### **Available Tools (7 Total)**
1. `get_livescores()` - Live match scores
2. `get_leagues()` - All 128+ available leagues  
3. `get_league_standings(league_id)` - League tables
4. `get_league_matches(league_id)` - Matches with events & players
5. `get_team_info(team_id)` - Team information
6. `get_player_info(player_id)` - Player details
7. `extract_players_from_league(league_id)` - **ADVANCED**: Extract all players with stats

### **Key League IDs**
- **EPL (Premier League)**: 228
- **La Liga**: 207  
- **MLS**: 253
- **Bundesliga**: Check via `get_leagues()` tool
- **Serie A**: Check via `get_leagues()` tool

### **Usage Examples**
```python
# Get all EPL players with statistics
await extract_players_from_league(228)

# Get EPL league table
await get_league_standings(228)

# Get live scores
await get_livescores()
```

## 📊 Expected Results

### **Player Extraction Results**
- **EPL (228)**: ~113 players with comprehensive stats
- **La Liga (207)**: Similar player counts expected
- **Player Data**: Goals, assists, cards, substitutions from match events

### **API Usage**
- **Rate Limit**: 75 requests/hour (SoccerDataAPI free tier)
- **Efficiency**: 1 call extracts 100+ players vs. individual player calls
- **Data Quality**: Real match events with timestamps

## 🌐 Railway URL Structure
After deployment, your MCP server will be available at:
```
https://your-service-name-production.up.railway.app/mcp
```

## ✅ Health Check
The server includes a health check endpoint at `/` that returns:
```json
{"status": "healthy", "service": "enhanced-soccer-data"}
```

## 🔗 Integration with Other MCPs
This enhanced soccer MCP integrates seamlessly with your existing:
- **MLB MCP**: `https://mlbmcp-production.up.railway.app/mcp`
- **College Football MCP**: `https://cfbmcp-production.up.railway.app/mcp`  
- **Odds MCP v2**: `https://odds-mcp-v2-production.up.railway.app/mcp`

Together they provide comprehensive sports analytics across all major leagues!