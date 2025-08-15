# Odds MCP Server Documentation

## Overview
This project contains an MCP (Model Context Protocol) server focused exclusively on sports betting odds functionality. It was originally a hybrid ESPN+odds server but has been cleaned up to only serve odds data from The Odds API.

## Project Structure

### Main Files
- **`odds_mcp_server.py`** - The main MCP server file (odds-only)
- **`start_claude.py`** - Claude Code startup script 
- **`pushpull.py`** - Git push/pull utility script
- **`requirements.txt`** - Python dependencies

### Removed Files
- All ESPN-related functionality has been stripped out
- Originally had 8 tools (5 ESPN + 3 odds), now has 4 tools (odds-only)

## Railway Deployment

### Current Deployment
- **Project Name**: helpful-emotion
- **Environment**: production  
- **Service**: web
- **URL**: https://web-production-b939f.up.railway.app
- **MCP Endpoint**: https://web-production-b939f.up.railway.app/mcp

### Environment Variables on Railway
```
ODDS_API_KEY=76823225714dfa4618643fd701de3d3b
OPENROUTER_API_KEY=sk-or-v1-5c5c2733407d9e9f8d2a596eeafb5ccfb00815bcf485609bae6a6b856b7cbc7
RAILWAY_ENVIRONMENT=production
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SPORTS_API_KEY=89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ
```

### Railway Commands
- `railway status` - Check deployment status
- `railway logs` - View server logs
- `railway domain` - Get domain URL
- `railway variables` - List environment variables
- `railway up` - Deploy changes

## MCP Server Details

### Server Configuration
- **Name**: odds-mcp
- **Version**: 4.0.0
- **Port**: 8080 (Railway automatically maps this)
- **Protocol**: MCP 2024-11-05
- **Transport**: HTTP POST to `/mcp` endpoint

### Available Tools (4 total)
1. **`getSports`** - Get available sports from Odds API
   - Parameters: `all_sports` (boolean), `use_test_mode` (boolean)
   - Returns list of available sports for betting

2. **`getOdds`** - Get odds for a specific sport
   - Parameters: `sport` (required), `regions`, `markets`, `odds_format`, `use_test_mode`
   - Returns betting odds for games in specified sport

3. **`getQuotaInfo`** - Get Odds API quota information
   - Parameters: `use_test_mode` (boolean)
   - Returns API usage/quota status

4. **`getEventOdds`** - Get odds for a specific event (player props)
   - Parameters: `sport` (required), `event_id` (required), `regions`, `markets`, `odds_format`, `use_test_mode`
   - Returns detailed event odds including player props

### API Integration
- **The Odds API**: Primary data source for all odds functionality
- **Base URL**: https://api.the-odds-api.com/v4
- **Authentication**: API key via `ODDS_API_KEY` environment variable

### Test Mode
All tools support a `use_test_mode` parameter that returns mock data instead of live API calls. Useful for development/testing without consuming API quota.

## Development Workflow

### Local Testing
```bash
cd "C:\Users\fstr2\Desktop\sports"
python pure_mcp_server.py
```
Server runs on http://localhost:8080 with endpoint at http://localhost:8080/mcp

### Deployment Process
1. Make changes to `pure_mcp_server.py`
2. Test locally
3. Commit changes: `git add . && git commit -m "message"`
4. Deploy: `railway up`
5. Monitor: `railway logs`

### Git Repository
- Main branch: `main`
- Recent commits show progression from ESPN+odds hybrid to odds-only server
- Clean commit history tracking the removal of ESPN functionality

## Architecture Notes

### MCP Protocol Implementation
- Uses standard MCP JSON-RPC protocol over HTTP
- Handles three main MCP methods:
  - `initialize` - Server handshake
  - `tools/list` - Return available tools
  - `tools/call` - Execute specific tool

### HTTP Framework
- **Starlette** - Lightweight ASGI framework
- **Uvicorn** - ASGI server
- **httpx** - Async HTTP client for API calls

### Error Handling
- Comprehensive error handling for API failures
- Timeout protection (20s default)
- Graceful degradation with meaningful error messages

## Configuration

### Required Environment Variables
- `ODDS_API_KEY` - The Odds API authentication key
- `PORT` - Server port (Railway sets this automatically)

### Optional Environment Variables
- `OPENROUTER_API_KEY` - Currently unused but preserved
- `SPORTS_API_KEY` - Currently unused but preserved

## Monitoring & Health

### Health Indicators
- Server startup logs show tool registration
- HTTP 200 responses indicate healthy operation
- API quota monitoring via `getQuotaInfo` tool

### Common Issues
- Unicode encoding issues with emojis (fixed in v4.0)
- API quota exhaustion (monitor via quota tool)
- Network timeouts (handled gracefully)

## Future Considerations

### Replacing ESPN Data Source
The server was designed to easily accommodate a new data source to replace the removed ESPN functionality. The modular tool architecture makes it straightforward to add new tools for:
- Player statistics
- Team information  
- Game schedules/scores
- Team rosters

### Scaling
- Current deployment handles concurrent requests well
- Stateless design allows horizontal scaling
- Connection pooling via httpx for efficient API usage

## Troubleshooting

### Common Commands
```bash
# Check deployment status
railway status

# View live logs
railway logs

# Redeploy
railway up

# Test tools locally
python -c "from pure_mcp_server import TOOLS; print(list(TOOLS.keys()))"
```

### Log Analysis
- Look for "Pure MCP Odds Server Starting - Odds Only v4.0" on startup
- Should show "Total Tools: 4" 
- All registered tools should be odds-related only
- HTTP 200 responses indicate successful API calls

## Contact & Support
This server is deployed and maintained via Railway with all configuration automated. The codebase is clean, focused, and ready for extension with new data sources as needed.