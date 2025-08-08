"""
MCP Client for communicating with the Sports AI MCP server via stdio.

This client handles the JSON-RPC protocol communication with the MCP server
running as a separate process.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

class MCPClientError(Exception):
    """Base exception for MCP client errors."""
    pass

class MCPClient:
    """
    MCP client that communicates with MCP server via subprocess stdio.
    """
    
    def __init__(self, server_script_path: str):
        self.server_script_path = server_script_path
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
    
    async def connect(self):
        """Start the MCP server process."""
        try:
            # Start the MCP server as a subprocess
            self.process = subprocess.Popen(
                [sys.executable, self.server_script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            # Initialize the MCP session
            await self._initialize_session()
            
        except Exception as e:
            raise MCPClientError(f"Failed to start MCP server: {e}")
    
    async def disconnect(self):
        """Stop the MCP server process."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            finally:
                self.process = None
    
    async def _initialize_session(self):
        """Initialize the MCP session with the server."""
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "sports-cli",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await self._send_request(init_request)
        if "error" in response:
            raise MCPClientError(f"MCP initialization failed: {response['error']}")
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        await self._send_notification(initialized_notification)
    
    def _next_request_id(self) -> int:
        """Generate next request ID."""
        self.request_id += 1
        return self.request_id
    
    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a JSON-RPC request and wait for response."""
        if not self.process:
            raise MCPClientError("MCP server not connected")
        
        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Read response
            response_line = self.process.stdout.readline()
            if not response_line:
                raise MCPClientError("MCP server closed connection")
            
            response = json.loads(response_line.strip())
            return response
            
        except Exception as e:
            raise MCPClientError(f"Failed to communicate with MCP server: {e}")
    
    async def _send_notification(self, notification: Dict[str, Any]):
        """Send a JSON-RPC notification (no response expected)."""
        if not self.process:
            raise MCPClientError("MCP server not connected")
        
        try:
            notification_json = json.dumps(notification) + "\n"
            self.process.stdin.write(notification_json)
            self.process.stdin.flush()
        except Exception as e:
            raise MCPClientError(f"Failed to send notification: {e}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server."""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = await self._send_request(request)
        
        if "error" in response:
            error = response["error"]
            raise MCPClientError(f"Tool call failed: {error.get('message', 'Unknown error')}")
        
        return response.get("result", {})
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the MCP server."""
        request = {
            "jsonrpc": "2.0", 
            "id": self._next_request_id(),
            "method": "tools/list",
            "params": {}
        }
        
        response = await self._send_request(request)
        
        if "error" in response:
            error = response["error"]
            raise MCPClientError(f"Failed to list tools: {error.get('message', 'Unknown error')}")
        
        return response.get("result", {}).get("tools", [])

# Helper function to get MCP server path
def get_server_path() -> str:
    """Get the path to the MCP server script."""
    # Get the parent directory of the current file (clients/)
    current_dir = Path(__file__).parent
    # Go up one level to the project root, then into sports_mcp/
    server_path = current_dir.parent / "sports_mcp" / "sports_ai_mcp.py"
    
    if not server_path.exists():
        raise MCPClientError(f"MCP server script not found at {server_path}")
    
    return str(server_path)