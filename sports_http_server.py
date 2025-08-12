#!/usr/bin/env python3
"""
Railway deployment wrapper for sports MCP server
Switches to Pure MCP Server for better compatibility
"""

import sys
import os
import uvicorn
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Run the Pure MCP server via uvicorn for Railway
    port = int(os.environ.get('PORT', 8000))  # Railway provides PORT env var
    print(f"🚀 Starting Pure MCP Sports Server on port {port}")
    
    # Import and run the pure MCP server
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run(
        "pure_mcp_server:app",
        host="0.0.0.0",  # Railway needs 0.0.0.0, not 127.0.0.1
        port=port,
        log_level="info"
    )