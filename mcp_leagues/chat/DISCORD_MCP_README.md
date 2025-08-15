# Discord MCP Server - Railway Deployment

A Model Context Protocol (MCP) server that enables AI to interact with Discord channels, allowing reading and sending messages through Discord's API.

## 🚀 Railway Deployment

### **URL**: TBD (will be provided after deployment)
### **Status**: Ready for deployment
### **MCP Endpoint**: `https://[railway-url]/mcp`

## 🛠️ Available Tools (2 Total)

### 1. send-message
Send a message to a Discord channel.

**Parameters**:
- `server` (optional): Server name or ID (optional if bot is only in one server)
- `channel`: Channel name (e.g., "general") or ID
- `message`: Message content to send

**Example**:
```json
{
  "channel": "general",
  "message": "Hello from Sports AI!"
}
```

### 2. read-messages
Read recent messages from a Discord channel.

**Parameters**:
- `server` (optional): Server name or ID (optional if bot is only in one server)
- `channel`: Channel name (e.g., "general") or ID
- `limit` (optional): Number of messages to fetch (default: 50, max: 100)

**Example**:
```json
{
  "channel": "general", 
  "limit": 10
}
```

## 🔧 Technical Implementation

### **Server Configuration**
- **Framework**: Starlette + Uvicorn
- **Protocol**: HTTP-based MCP (JSON-RPC 2.0)
- **Discord API**: discord.py library
- **Authentication**: Bot token in environment

### **Railway Settings**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python discord_mcp_server.py`
- **Environment**: `DISCORD_TOKEN` configured
- **Port**: Auto-assigned by Railway

### **Dependencies**
```
starlette==0.38.2
uvicorn[standard]==0.30.1
discord.py==2.3.2
```

## 🔐 Bot Permissions Required

The Discord bot needs these permissions:
- **View Channels** - To see server and channel information
- **Send Messages** - To send messages to channels
- **Read Message History** - To read recent messages

## 📁 File Structure
```
mcp_leagues/chat/chat_mcp/
├── discord_mcp_server.py     # Main MCP server (Python)
├── requirements.txt          # Python dependencies
├── railway.toml             # Railway deployment config
└── DISCORD_MCP_README.md    # This file
```

## 🚀 Deployment Steps

1. **Configure Environment**: Set `DISCORD_TOKEN` in railway.toml
2. **Deploy to Railway**: Push to Railway or deploy via CLI
3. **Verify Deployment**: Check health endpoint at `/health`
4. **Test MCP**: Use MCP endpoint at `/mcp`

## 🧪 Testing

### Health Check
```bash
curl https://[railway-url]/health
```

### MCP Protocol Test
```bash
curl -X POST https://[railway-url]/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1, "params": {}}'
```

## 🔗 Integration with Sports Platform

This Discord MCP integrates with the sports betting analytics platform to:
- **Send daily recommendations** to Discord channels
- **Respond to user queries** about games and odds
- **Post real-time updates** about important betting opportunities
- **Facilitate community interaction** around sports betting

## 🎯 Usage Examples

Once deployed, you can:
1. **Read morning betting discussions**: "What are users saying in the #betting channel?"
2. **Post game updates**: "Send today's MLB recommendations to #mlb-picks"
3. **Engage with community**: "Check recent messages in #general for feedback"

---

*Ready for Railway deployment as part of the sports betting analytics platform ecosystem.*

<!-- Trigger Railway redeploy -->