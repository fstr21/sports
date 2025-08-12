#!/usr/bin/env python3
"""
Railway deployment wrapper for sports MCP server
Uses FastMCP server with all working tools including getEventOdds and getTeamRoster
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Run the FastMCP server for Railway
    port = int(os.environ.get('PORT', 8000))  # Railway provides PORT env var
    print(f"🚀 Starting FastMCP Sports Server on port {port}")
    
    # Import and run the FastMCP server
    from sports_mcp.sports_ai_mcp import server
    server.run(transport="http", host="0.0.0.0", port=port, log_level="info")