# MCP Proxy Setup Guide

## Prerequisites
You'll need either Go or Docker installed to run the MCP proxy.

### Option 1: Install Go (Recommended)
1. Download Go from: https://golang.org/dl/
2. Install Go following the instructions for Windows
3. Restart your terminal/command prompt

### Option 2: Use Docker
1. Install Docker Desktop for Windows
2. Start Docker Desktop

## Building and Running

### With Go:
```bash
cd C:\Users\fstr2\Desktop\sports\mcp-proxy
go build -o mcp-proxy.exe
./mcp-proxy.exe --config sports_config.json
```

### With Docker:
```bash
cd C:\Users\fstr2\Desktop\sports\mcp-proxy
docker run -d -p 9090:9090 -v "$(pwd)/sports_config.json:/config/config.json" ghcr.io/tbxark/mcp-proxy:latest
```

## What This Setup Does

Your `sports_config.json` configures the proxy to:

1. **sports-ai**: Runs your existing `sports_ai_mcp.py` server
2. **wagyu-sports**: Runs your odds/betting MCP server 
3. **fetch**: Adds a general HTTP fetch capability

## Access Points

Once running, your MCP servers will be available at:
- Sports AI: `http://localhost:9090/sports-ai/sse`
- Wagyu Sports: `http://localhost:9090/wagyu-sports/sse`  
- Fetch: `http://localhost:9090/fetch/sse`

## Authentication
- Uses token: `sports-betting-token`
- Add header: `Authorization: Bearer sports-betting-token`

## Next Steps

1. Install Go or start Docker
2. Run the proxy
3. Test the endpoints
4. Integrate with your Discord bot