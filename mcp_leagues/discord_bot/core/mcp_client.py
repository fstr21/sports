"""
Unified MCP client with connection pooling and error handling
"""
import asyncio
import logging
from typing import Dict, Any, Optional
import httpx
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class MCPResponse:
    """Standardized MCP response wrapper"""
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    raw_response: Optional[Dict[str, Any]]


class MCPClient:
    """
    Unified HTTP client for all MCP services with connection pooling,
    retry logic, and standardized error handling.
    """
    
    def __init__(self, timeout: float = 30.0, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize MCP client
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client: Optional[httpx.AsyncClient] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_client()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        
    async def _ensure_client(self):
        """Ensure HTTP client is initialized"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
            )
    
    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def call_mcp(self, url: str, tool: str, args: Dict[str, Any] = None) -> MCPResponse:
        """
        Call MCP server with retry logic and error handling
        
        Args:
            url: MCP server URL
            tool: Tool name to call
            args: Arguments to pass to the tool
            
        Returns:
            MCPResponse with standardized result
        """
        await self._ensure_client()
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool,
                "arguments": args or {}
            }
        }
        
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"MCP call attempt {attempt + 1}/{self.max_retries + 1}: {tool} to {url}")
                
                response = await self._client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                # Check for JSON-RPC error
                if "error" in result:
                    error_msg = result["error"].get("message", "Unknown MCP error")
                    logger.error(f"MCP JSON-RPC error: {error_msg}")
                    return MCPResponse(
                        success=False,
                        data=None,
                        error=f"MCP Error: {error_msg}",
                        raw_response=result
                    )
                
                # Extract result data
                mcp_result = result.get("result", {})
                
                logger.debug(f"MCP call successful: {tool}")
                return MCPResponse(
                    success=True,
                    data=mcp_result,
                    error=None,
                    raw_response=result
                )
                
            except httpx.TimeoutException as e:
                last_error = f"MCP timeout after {self.timeout}s"
                logger.warning(f"MCP timeout on attempt {attempt + 1}: {e}")
                
            except httpx.HTTPStatusError as e:
                last_error = f"MCP HTTP error {e.response.status_code}: {e.response.text}"
                logger.error(f"MCP HTTP error on attempt {attempt + 1}: {last_error}")
                
            except httpx.RequestError as e:
                last_error = f"MCP connection error: {str(e)}"
                logger.error(f"MCP connection error on attempt {attempt + 1}: {last_error}")
                
            except Exception as e:
                last_error = f"Unexpected MCP error: {str(e)}"
                logger.error(f"Unexpected MCP error on attempt {attempt + 1}: {last_error}")
            
            # Wait before retry (except on last attempt)
            if attempt < self.max_retries:
                await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
        
        logger.error(f"MCP call failed after {self.max_retries + 1} attempts: {last_error}")
        return MCPResponse(
            success=False,
            data=None,
            error=last_error,
            raw_response=None
        )
    
    async def parse_mcp_content(self, mcp_response: MCPResponse) -> Optional[Dict[str, Any]]:
        """
        Parse MCP response content handling different formats
        
        Args:
            mcp_response: MCPResponse object
            
        Returns:
            Parsed data dictionary or None if parsing fails
        """
        if not mcp_response.success or not mcp_response.data:
            return None
            
        try:
            # Handle content array format
            if "content" in mcp_response.data and isinstance(mcp_response.data["content"], list):
                import json
                content_text = mcp_response.data["content"][0]["text"]
                return json.loads(content_text)
            
            # Handle direct data format
            return mcp_response.data
            
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Failed to parse MCP content: {e}")
            return None
    
    def is_healthy(self) -> bool:
        """
        Check if client is in healthy state
        
        Returns:
            True if client is ready for requests
        """
        return self._client is not None and not self._client.is_closed