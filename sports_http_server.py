#!/usr/bin/env python3
"""
Railway deployment wrapper for sports MCP server
This file exists because Railway is looking for 'sports_http_server.py'
but our actual server is at 'sports_mcp/sports_ai_mcp.py'
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the server instance from the actual MCP server
from sports_mcp.sports_ai_mcp import server

if __name__ == "__main__":
    # Run the FastMCP server in HTTP mode for Railway
    port = int(os.environ.get('PORT', 8000))  # Railway provides PORT env var
    server.run(
        transport="http",
        host="0.0.0.0",  # Railway needs 0.0.0.0, not 127.0.0.1
        port=port,
        log_level="info"
    )