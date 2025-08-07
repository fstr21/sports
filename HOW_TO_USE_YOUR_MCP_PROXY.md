# How to Use Your MCP Proxy

## Current Status ✅

Your MCP proxy is **WORKING** and has these servers available:

- **sports-ai**: Status 200 ✅ (Custom sports analysis)
- **fetch**: Status 200 ✅ (HTTP requests for ESPN APIs, etc.)
- **wagyu-sports**: Status 404 ❌ (Needs config fix)

## Connection Details

**Proxy URL**: `http://localhost:9091`
**Auth Token**: `sports-betting-token` 
**Auth Header**: `Authorization: Bearer sports-betting-token`

## Working Endpoints

### Sports-AI Server
- **URL**: `http://localhost:9091/sports-ai/sse`
- **Purpose**: Custom sports analysis and predictions
- **Status**: ✅ Active SSE stream

### Fetch Server  
- **URL**: `http://localhost:9091/fetch/sse`
- **Purpose**: HTTP requests to external APIs (ESPN, etc.)
- **Status**: ✅ Active SSE stream

## How to Connect

### Option 1: Claude Desktop Integration

Add to your Claude Desktop config (`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "sports-ai": {
      "command": "curl",
      "args": [
        "-H", "Authorization: Bearer sports-betting-token",
        "http://localhost:9091/sports-ai/sse"
      ]
    },
    "fetch": {
      "command": "curl", 
      "args": [
        "-H", "Authorization: Bearer sports-betting-token",
        "http://localhost:9091/fetch/sse"
      ]
    }
  }
}
```

### Option 2: Python Client

```python
import asyncio
from mcp.client.sse import sse_client
from mcp import ClientSession

async def connect_to_sports_ai():
    headers = {"Authorization": "Bearer sports-betting-token"}
    
    async with sse_client("http://localhost:9091/sports-ai/sse", headers=headers) as streams:
        read, write = streams
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")
            
            # Call a tool
            if tools.tools:
                result = await session.call_tool(tools.tools[0].name, {})
                print(f"Result: {result}")

# Run it
asyncio.run(connect_to_sports_ai())
```

### Option 3: OpenRouter + Your Proxy

Use your `simple_openrouter_test.py` - it already works and can be enhanced to call your MCP servers for real data.

## Testing Your Setup

Run these commands to verify everything works:

```bash
# Check proxy is running
curl http://localhost:9091/sports-ai/sse --max-time 2 -H "Authorization: Bearer sports-betting-token"

# Should timeout (good - means SSE is active)
```

## What Each Server Does

### Sports-AI Server (`/sports-ai/sse`)
- Your custom sports analysis logic
- Game predictions and insights  
- Custom algorithms for betting analysis

### Fetch Server (`/fetch/sse`)
- Makes HTTP requests to external APIs
- Perfect for ESPN APIs: `http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard`
- Returns structured data from any web API

### Wagyu-Sports Server (Currently Broken)
- Would provide betting odds from The Odds API
- Needs configuration fix to work

## Next Steps

1. **Test with Claude Desktop**: Add the config above and restart Claude Desktop
2. **Build your application**: Use the working servers to build your sports betting system  
3. **Fix wagyu-sports**: Debug the configuration issue for betting odds
4. **Scale up**: Add more MCP servers for different sports/data sources

## Example Use Cases

### Get NBA Games Today
```
Connect to fetch server → Call with ESPN NBA API → Get today's games
```

### Analyze a Specific Game  
```
Connect to sports-ai server → Pass team data → Get prediction + confidence
```

### Complete Betting Pipeline
```
1. Fetch server: Get games from ESPN
2. Sports-AI server: Analyze each game  
3. Wagyu-sports server: Get current odds (when fixed)
4. OpenRouter: Generate betting recommendations
```

## Troubleshooting

- **Connection timeouts**: Good! SSE streams are supposed to stay open
- **404 errors**: Server not configured properly in proxy
- **Auth errors**: Check your Bearer token
- **Port issues**: Make sure proxy is running on 9091

Your proxy is working! The SSE timeouts you're seeing are expected behavior.