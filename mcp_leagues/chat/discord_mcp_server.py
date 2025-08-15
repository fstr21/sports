#!/usr/bin/env python3
"""
Discord MCP Server for Sports AI

A dedicated MCP implementation focused on Discord integration for chat functionality.
Uses Discord.py for comprehensive Discord API access.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import discord
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Route

# Configuration
USER_AGENT = "sports-ai-discord-mcp/1.0"
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()

# Discord client
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
discord_client = discord.Client(intents=intents)

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# Helper functions for Discord operations
async def find_guild(guild_identifier: Optional[str] = None):
    """Find a guild by name or ID"""
    if not guild_identifier:
        if len(discord_client.guilds) == 1:
            return discord_client.guilds[0]
        guild_list = [f'"{g.name}"' for g in discord_client.guilds]
        raise ValueError(f"Bot is in multiple servers. Please specify server name or ID. Available servers: {', '.join(guild_list)}")
    
    # Try to find by ID first
    guild = discord_client.get_guild(int(guild_identifier)) if guild_identifier.isdigit() else None
    if guild:
        return guild
    
    # Search by name
    guilds = [g for g in discord_client.guilds if g.name.lower() == guild_identifier.lower()]
    if len(guilds) == 0:
        available_guilds = [f'"{g.name}"' for g in discord_client.guilds]
        raise ValueError(f'Server "{guild_identifier}" not found. Available servers: {", ".join(available_guilds)}')
    if len(guilds) > 1:
        guild_list = [f'{g.name} (ID: {g.id})' for g in guilds]
        raise ValueError(f'Multiple servers found with name "{guild_identifier}": {", ".join(guild_list)}. Please specify the server ID.')
    
    return guilds[0]

async def find_channel(channel_identifier: str, guild_identifier: Optional[str] = None):
    """Find a channel by name or ID within a guild"""
    guild = await find_guild(guild_identifier)
    
    # Try to find by ID first
    if channel_identifier.isdigit():
        channel = discord_client.get_channel(int(channel_identifier))
        if channel and isinstance(channel, discord.TextChannel) and channel.guild.id == guild.id:
            return channel
    
    # Search by name in the guild
    channels = [c for c in guild.text_channels if c.name.lower() == channel_identifier.lower().replace('#', '')]
    if len(channels) == 0:
        available_channels = [f'"#{c.name}"' for c in guild.text_channels]
        raise ValueError(f'Channel "{channel_identifier}" not found in server "{guild.name}". Available channels: {", ".join(available_channels)}')
    if len(channels) > 1:
        channel_list = [f'#{c.name} ({c.id})' for c in channels]
        raise ValueError(f'Multiple channels found with name "{channel_identifier}" in server "{guild.name}": {", ".join(channel_list)}. Please specify the channel ID.')
    
    return channels[0]

# Discord MCP Tool implementations
async def handle_send_message(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send a message to a Discord channel"""
    try:
        server = args.get("server")
        channel_id = args.get("channel")
        message = args.get("message")
        
        if not channel_id or not message:
            return {"ok": False, "error": "Channel and message are required"}
        
        channel = await find_channel(channel_id, server)
        sent_message = await channel.send(message)
        
        return {
            "ok": True,
            "data": {
                "message_id": sent_message.id,
                "channel": channel.name,
                "guild": channel.guild.name,
                "timestamp": sent_message.created_at.isoformat(),
                "content": message
            }
        }
    except Exception as e:
        return {"ok": False, "error": f"Failed to send message: {str(e)}"}

async def handle_read_messages(args: Dict[str, Any]) -> Dict[str, Any]:
    """Read recent messages from a Discord channel"""
    try:
        server = args.get("server")
        channel_id = args.get("channel")
        limit = min(int(args.get("limit", 50)), 100)  # Cap at 100 messages
        
        if not channel_id:
            return {"ok": False, "error": "Channel is required"}
        
        channel = await find_channel(channel_id, server)
        messages = []
        
        async for message in channel.history(limit=limit):
            messages.append({
                "id": message.id,
                "author": message.author.display_name,
                "author_tag": str(message.author),
                "content": message.content,
                "timestamp": message.created_at.isoformat(),
                "channel": channel.name,
                "guild": channel.guild.name
            })
        
        return {
            "ok": True,
            "data": {
                "messages": messages,
                "channel": channel.name,
                "guild": channel.guild.name,
                "total": len(messages)
            }
        }
    except Exception as e:
        return {"ok": False, "error": f"Failed to read messages: {str(e)}"}

# MCP Protocol handlers
async def handle_initialize(request: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "discord-mcp",
                "version": "1.0.0"
            }
        }
    }

async def handle_tools_list(request: Dict[str, Any]) -> Dict[str, Any]:
    tools = [
        {
            "name": "send-message",
            "description": "Send a message to a Discord channel",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "server": {
                        "type": "string",
                        "description": "Server name or ID (optional if bot is only in one server)"
                    },
                    "channel": {
                        "type": "string",
                        "description": "Channel name (e.g., 'general') or ID"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message content to send"
                    }
                },
                "required": ["channel", "message"]
            }
        },
        {
            "name": "read-messages",
            "description": "Read recent messages from a Discord channel",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "server": {
                        "type": "string",
                        "description": "Server name or ID (optional if bot is only in one server)"
                    },
                    "channel": {
                        "type": "string",
                        "description": "Channel name (e.g., 'general') or ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of messages to fetch (default: 50, max: 100)",
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["channel"]
            }
        }
    ]
    
    return {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": {"tools": tools}
    }

async def handle_tools_call(request: Dict[str, Any]) -> Dict[str, Any]:
    params = request.get("params", {})
    name = params.get("name")
    arguments = params.get("arguments", {})
    
    try:
        if name == "send-message":
            result = await handle_send_message(arguments)
        elif name == "read-messages":
            result = await handle_read_messages(arguments)
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32601, "message": f"Unknown tool: {name}"}
            }
        
        if result.get("ok"):
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(result["data"], indent=2, ensure_ascii=False)
                    }]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32000, "message": result.get("error", "Unknown error")}
            }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {"code": -32000, "message": f"Tool execution failed: {str(e)}"}
        }

# HTTP endpoints
async def handle_mcp_request(request: Request) -> Response:
    try:
        data = await request.json()
        method = data.get("method")
        
        if method == "initialize":
            response = await handle_initialize(data)
        elif method == "tools/list":
            response = await handle_tools_list(data)
        elif method == "tools/call":
            response = await handle_tools_call(data)
        else:
            response = {
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "error": {"code": -32601, "message": f"Unknown method: {method}"}
            }
        
        return JSONResponse(response)
    
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
        }, status_code=400)

async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({
        "status": "healthy",
        "service": "Discord MCP Server",
        "version": "1.0.0",
        "timestamp": now_iso(),
        "discord_ready": discord_client.is_ready(),
        "guilds": len(discord_client.guilds) if discord_client.is_ready() else 0
    })

async def root_handler(request: Request) -> JSONResponse:
    return JSONResponse({
        "service": "Discord MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health"
        },
        "timestamp": now_iso()
    })

# Discord event handlers
@discord_client.event
async def on_ready():
    print(f"Discord MCP Server - Bot logged in as {discord_client.user}")
    print(f"Connected to {len(discord_client.guilds)} guilds")
    for guild in discord_client.guilds:
        print(f"  - {guild.name} (ID: {guild.id})")

# Starlette app
app = Starlette(routes=[
    Route("/mcp", handle_mcp_request, methods=["POST"]),
    Route("/health", health_check, methods=["GET"]),
    Route("/", root_handler, methods=["GET"])
])

async def main():
    print("Discord MCP Server Starting - v1.0")
    
    # Check for Discord token
    if not DISCORD_TOKEN:
        print("ERROR: DISCORD_TOKEN environment variable is required")
        sys.exit(1)
    
    # Start Discord client
    print("Connecting to Discord...")
    discord_task = asyncio.create_task(discord_client.start(DISCORD_TOKEN))
    
    # Wait for Discord to be ready
    await discord_client.wait_until_ready()
    print("Discord client ready!")
    
    # Start HTTP server
    port = int(os.getenv("PORT", 8080))
    print(f"Starting HTTP server on port {port}")
    
    config = uvicorn.Config(app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)
    
    # Run both Discord and HTTP server
    await asyncio.gather(
        discord_task,
        server.serve()
    )

if __name__ == "__main__":
    asyncio.run(main())