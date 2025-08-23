# 🧠 Chronulus AI Forecasting MCP Server

AI expert panel forecasting service for sports betting analysis, integrated with your existing sports analysis infrastructure.

## Overview

This MCP server provides:
- **AI Expert Panel Analysis**: 2-30 AI experts analyzing game data
- **Consensus Predictions**: Averaged expert opinions with confidence ranges
- **Market Value Analysis**: Edge detection vs betting odds
- **Professional Quality**: Institutional-level sports betting analysis

## Railway Deployment

### 1. Create Railway Project

```bash
# From this directory
railway login
railway init
railway up
```

### 2. Set Environment Variables

In Railway Dashboard → Variables:
```
CHRONULUS_API_KEY=your_chronulus_api_key_here
PORT=8080
```

### 3. Deploy

```bash
railway deploy
```

The service will be available at: `https://your-project.up.railway.app`

## MCP Tools

### `getChronulusAnalysis`
Get AI expert panel analysis for sports betting predictions.

**Parameters:**
- `game_data` (object): Comprehensive game data including teams, stats, odds
- `expert_count` (integer, optional): Number of AI experts (2-30, default: 2)

**Returns:**
```json
{
  "analysis": {
    "consensus_probability": 0.657,
    "confidence_range": 0.12,
    "expert_count": 2,
    "market_edge": 0.045,
    "recommendation": "BET",
    "expert_analyses": [
      {
        "expert_id": 1,
        "probability": 0.65,
        "analysis": "Detailed expert reasoning...",
        "confidence": "high"
      }
    ]
  },
  "status": "success"
}
```

### `getChronulusHealth`
Check service health and API connectivity.

## Integration with Discord Bot

Add to your Discord bot's MCP configuration:

```python
CHRONULUS_MCP_URL = "https://your-chronulus-mcp.up.railway.app/mcp"

# Usage in MLB handler
async def get_ai_forecast(self, game_data):
    response = await self.mcp_client.call_tool(
        url=CHRONULUS_MCP_URL,
        tool_name="getChronulusAnalysis", 
        arguments={
            "game_data": game_data,
            "expert_count": 2
        }
    )
    return response
```

## Health Monitoring

- **Health Check**: `GET /health`
- **Root Check**: `GET /`
- **MCP Endpoint**: `POST /mcp`

## Cost Management

- **2-Expert Analysis**: ~$0.05-0.10 per game
- **Daily MLB Slate**: ~$1.50-3.00 (15 games)
- **Monthly Usage**: ~$25-50 for regular analysis

## Status

- ✅ MCP server implementation
- ✅ Railway deployment configuration
- ✅ Health monitoring
- ✅ Error handling and graceful degradation
- ✅ Ready for production testing