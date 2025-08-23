# Custom Chronulus MCP Server

A reverse-engineered implementation of ChronulusAI's expert panel system using OpenRouter, providing institutional-quality sports betting analysis at 90% cost savings.

## 🚀 Railway Deployment

### Environment Variables (Required)
Set these in Railway dashboard:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1  
OPENROUTER_MODEL=google/gemini-2.0-flash-001
PORT=8080
```

### Railway Settings
- **Root Directory**: `mcp_leagues/custom_chron_predictor`
- **Build Command**: Automatic (uses requirements.txt)
- **Start Command**: `python custom_chronulus_mcp_server.py`
- **Healthcheck**: `/health`

## 🎯 Features

- **5 AI Expert Types**: Statistical, Situational, Contrarian, Sharp, Market
- **Beta Distribution Consensus**: Same mathematical approach as real Chronulus
- **Multiple Analysis Depths**: Brief (3-5 sentences), Standard (8-12), Comprehensive (15-20)
- **Cost Effective**: ~$0.02-0.15 per analysis vs $0.75-1.50 for real Chronulus
- **MCP Compatible**: JSON-RPC 2.0 protocol for integration

## 🔧 MCP Tools

1. **getCustomChronulusAnalysis**: Full game analysis with customizable expert count and depth
2. **testCustomChronulus**: Test with Red Sox @ Yankees sample data
3. **getCustomChronulusHealth**: Service health and connectivity check

## 🌐 Endpoints

- **Health**: `GET /health`
- **MCP**: `POST /mcp`

## 💰 Cost Comparison

| Service | Cost per Analysis | Expert Count | Quality |
|---------|------------------|--------------|---------|
| Real Chronulus | $0.75-1.50 | 2-30 | High |
| Custom Implementation | $0.02-0.15 | 1-5 | Comparable |
| **Savings** | **90%** | **Flexible** | **Match** |

## 🎮 Usage Example

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "getCustomChronulusAnalysis",
    "arguments": {
      "game_data": {
        "home_team": "Yankees",
        "away_team": "Red Sox", 
        "venue": "Yankee Stadium",
        "game_date": "2025-08-23",
        "home_record": "69-59",
        "away_record": "70-59",
        "home_moneyline": 112,
        "away_moneyline": -132
      },
      "expert_count": 5,
      "analysis_depth": "comprehensive"
    }
  },
  "id": 1
}
```

Built with ❤️ for sports bettors who want Chronulus-quality analysis without the premium price.