#!/usr/bin/env python3
"""
Simple MCP client to test our ESPN server
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_server():
    """Test the MCP server by sending it requests"""
    print("🧪 Testing MCP Server...")
    
    # Start the MCP server as subprocess
    server_path = Path("testing/test_rest_api_mcp.py")
    
    try:
        # Start server process
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(server_path),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        print("🚀 MCP Server started")
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 Sending initialization...")
        request_json = json.dumps(init_request) + "\n"
        process.stdin.write(request_json.encode())
        await process.stdin.drain()
        
        # Read response
        response_line = await process.stdout.readline()
        if response_line:
            response = json.loads(response_line.decode())
            print(f"📥 Init response: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
        
        # Test the ask_espn tool
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "ask_espn",
                "arguments": {
                    "query": "Show me today's WNBA scores"
                }
            }
        }
        
        print("📤 Testing ask_espn tool...")
        request_json = json.dumps(tool_request) + "\n"
        process.stdin.write(request_json.encode())
        await process.stdin.drain()
        
        # Read tool response
        response_line = await process.stdout.readline()
        if response_line:
            response = json.loads(response_line.decode())
            result = response.get('result', {}).get('content', [{}])[0].get('text', 'No response')
            print(f"📥 Tool response preview: {result[:100]}...")
        
        # Clean shutdown
        process.stdin.close()
        await process.wait()
        
        print("✅ MCP Server test completed")
        
    except Exception as e:
        print(f"❌ MCP Server test failed: {e}")
        if 'process' in locals():
            process.terminate()
            await process.wait()

async def main():
    print("🧪 Starting MCP Server Test...")
    print("=" * 50)
    await test_mcp_server()

if __name__ == "__main__":
    asyncio.run(main())