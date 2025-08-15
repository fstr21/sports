#!/usr/bin/env python3
"""
Simple MCP test to check if the CFBD server is working
"""

import subprocess
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_uvx_cfbd():
    """Test if we can run the CFBD MCP server directly"""
    api_key = os.getenv('CFBD_API_KEY')
    if not api_key:
        print("Error: CFBD_API_KEY not found")
        return
    
    print("Testing uvx CFBD server...")
    
    try:
        # Try to run the server and see if it starts
        cmd = ["uvx", "lenwood.cfbd-mcp-server@latest", "--help"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
    except subprocess.TimeoutExpired:
        print("Command timed out - this might be normal for MCP servers")
    except Exception as e:
        print(f"Error running uvx command: {e}")

def test_direct_uvx():
    """Test uvx installation"""
    try:
        result = subprocess.run(["uvx", "--version"], capture_output=True, text=True)
        print(f"uvx version: {result.stdout.strip()}")
        
        # List available packages
        result = subprocess.run(["uvx", "list"], capture_output=True, text=True)
        print(f"Installed uvx packages: {result.stdout}")
        
    except Exception as e:
        print(f"Error with uvx: {e}")

if __name__ == "__main__":
    print("=== Simple MCP Test ===\n")
    test_direct_uvx()
    print("\n" + "="*50 + "\n")
    test_uvx_cfbd()