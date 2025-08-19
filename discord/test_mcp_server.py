#!/usr/bin/env python3
"""
Test MCP server directly to understand the expected request format
"""

import asyncio
import httpx
import json

async def test_mcp_server():
    """Test different request formats to the MCP server"""
    print("🔍 Testing Soccer MCP Server")
    print("=" * 40)
    
    mcp_url = "https://soccermcp-production.up.railway.app/mcp"
    
    # Test 1: Basic tools/list request
    print("1. Testing tools/list request...")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }
            response = await client.post(mcp_url, json=payload)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
            else:
                print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 2: get_matches request without auth
    print("\n2. Testing get_matches without auth...")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "get_matches",
                    "arguments": {"date": "2025-08-19"}
                }
            }
            response = await client.post(mcp_url, json=payload)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
            else:
                print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 3: Check if server expects different method
    print("\n3. Testing direct /matches endpoint...")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Try direct REST endpoint
            response = await client.get(f"{mcp_url.replace('/mcp', '')}/matches?date=2025-08-19")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
            else:
                print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 4: Check server root
    print("\n4. Testing server root...")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(mcp_url.replace('/mcp', ''))
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())