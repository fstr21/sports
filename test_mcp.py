#!/usr/bin/env python3
"""
Simple test to check MCP server connectivity
"""

import requests
import json

# Railway MCP configuration
RAILWAY_URL = "https://web-production-b939f.up.railway.app"
API_KEY = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}

def initialize_session():
    """Initialize MCP session"""
    print("Initializing MCP session...")
    
    init_data = {
        "jsonrpc": "2.0",
        "id": "init-1",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "sports-test",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        response = requests.post(f"{RAILWAY_URL}/mcp", headers=headers, json=init_data, timeout=30)
        print(f"Initialize Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Session initialized successfully")
            return True
        else:
            print(f"Failed to initialize: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"Exception during initialization: {e}")
        return False

def test_mcp_scoreboard():
    """Test MCP scoreboard tool call"""
    print("\nTesting MCP getScoreboard tool...")
    
    # MCP-over-HTTP uses JSON-RPC format
    tool_data = {
        "jsonrpc": "2.0",
        "id": "test-1",
        "method": "tools/call",
        "params": {
            "name": "getScoreboard",
            "arguments": {
                "sport": "baseball",
                "league": "mlb"
            }
        }
    }
    
    try:
        response = requests.post(f"{RAILWAY_URL}/mcp", headers=headers, json=tool_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS")
            print(json.dumps(result, indent=2)[:500] + "...")
            return True
        else:
            print(f"FAILED: HTTP {response.status_code}")
            print(response.text[:500])
            return False
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False

def test_mcp_teams():
    """Test MCP getTeams tool call"""
    print("\nTesting MCP getTeams tool...")
    
    tool_data = {
        "jsonrpc": "2.0",
        "id": "test-2",
        "method": "tools/call",
        "params": {
            "name": "getTeams",
            "arguments": {
                "sport": "baseball",
                "league": "mlb"
            }
        }
    }
    
    try:
        response = requests.post(f"{RAILWAY_URL}/mcp", headers=headers, json=tool_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS")
            print(json.dumps(result, indent=2)[:500] + "...")
            return True
        else:
            print(f"FAILED: HTTP {response.status_code}")
            print(response.text[:500])
            return False
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  MCP SERVER TEST")
    print("=" * 60)
    print(f"Server URL: {RAILWAY_URL}")
    print(f"API Key: {API_KEY[:20]}...")
    
    # Initialize session first
    if not initialize_session():
        print("Failed to initialize session, stopping")
        exit(1)
    
    # Test scoreboard
    scoreboard_success = test_mcp_scoreboard()
    
    # Test teams
    teams_success = test_mcp_teams()
    
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"Scoreboard: {'PASS' if scoreboard_success else 'FAIL'}")
    print(f"Teams: {'PASS' if teams_success else 'FAIL'}")