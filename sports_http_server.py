#!/usr/bin/env python3
"""
Railway deployment wrapper for odds MCP server
"""

import sys
import os
import uvicorn
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Run the Odds MCP server via uvicorn for Railway
    port = int(os.environ.get('PORT', 8000))  # Railway provides PORT env var
    print(f"Starting Odds MCP Server on port {port}")
    
    # Import and run the odds MCP server
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run(
        "odds_mcp_server:app",
        host="0.0.0.0",  # Railway needs 0.0.0.0, not 127.0.0.1
        port=port,
        log_level="info"
    )