#!/usr/bin/env python3
"""
Very simple test - try to hit the MCP server root endpoint
"""

import requests
import json

# Railway MCP configuration
RAILWAY_URL = "https://web-production-b939f.up.railway.app"
API_KEY = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"

def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    try:
        response = requests.get(RAILWAY_URL, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

def test_mcp_endpoint():
    """Test MCP endpoint"""
    print("\nTesting /mcp endpoint...")
    try:
        response = requests.get(f"{RAILWAY_URL}/mcp", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

def test_mcp_info():
    """Test MCP info endpoint"""
    print("\nTesting MCP info/capabilities...")
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    # Try to get server info
    data = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "server/info"
    }
    
    try:
        response = requests.post(f"{RAILWAY_URL}/mcp", headers=headers, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_root()
    test_mcp_endpoint()
    test_mcp_info()