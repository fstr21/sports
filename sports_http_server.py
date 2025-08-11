#!/usr/bin/env python3
"""
Railway deployment wrapper for Pure MCP Sports Server
Runs the pure MCP server without FastMCP for maximum reliability.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Import and run the pure MCP server
    from pure_mcp_server import app
    import uvicorn
    
    port = int(os.environ.get('PORT', 8080))  # Railway provides PORT env var
    print(f"🚀 Starting Pure MCP Server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")