"""
Core LLM integration layer with strict OpenRouter integration.

This module provides strict OpenRouter integration that prevents fabrication and ensures
responses are based only on provided JSON data. Uses low temperature and controlled
token limits for precise, factual responses.
"""

import json
import logging
import os
from typing import Any, Dict, Optional, Tuple

import httpx
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env.local')

# Configure logging
logger = logging.getLogger(__name__)

# Configuration from environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free").strip()

# Strict response configuration
TEMPERATURE = 0.1  # Low temperature to prevent fabrication
MAX_TOKENS = 700   # Controlled response length
MAX_INPUT_BYTES = 10000  # Limit input size to prevent issues

# HTTP client for OpenRouter API
_openrouter_client: Optional[httpx.AsyncClient] = None

class LLMError(Exception):
    """Base exception for LLM-related errors."""
    pass

class LLMConfigurationError(LLMError):
    """Exception raised for configuration issues."""
    pass

class LLMAPIError(LLMError):
    """Exception raised for OpenRouter API errors."""
    pass

async def _get_openrouter_client() -> httpx.AsyncClient:
    """Get or create the OpenRouter HTTP client."""
    global _openrouter_client
    if _openrouter_client is None:
        _openrouter_client = httpx.AsyncClient(
            timeout=30.0,  # 30 second timeout for LLM calls
            headers={
                "User-Agent": "sports-ai-mcp-client/1.0",
                "Content-Type": "application/json"
            }
        )
    return _openrouter_client

def _validate_configuration() -> None:
    """
    Validate that required configuration is present.
    
    Raises:
        LLMConfigurationError: If required configuration is missing
    """
    if not OPENROUTER_API_KEY:
        raise LLMConfigurationError(
            "OpenRouter API key not configured. Set OPENROUTER_API_KEY in .env.local"
        )
    
    if not OPENROUTER_BASE_URL:
        raise LLMConfigurationError(
            "OpenRouter base URL not configured. Set OPENROUTER_BASE_URL in .env.local"
        )
    
    if not OPENROUTER_MODEL:
        raise LLMConfigurationError(
            "OpenRouter model not configured. Set OPENROUTER_MODEL in .env.local"
        )

def _truncate_utf8(text: str, limit: int = MAX_INPUT_BYTES) -> str:
    """
    Truncate text to fit within byte limit while preserving UTF-8 encoding.
    
    Args:
        text: Text to truncate
        limit: Maximum bytes allowed
        
    Returns:
        Truncated text that fits within byte limit
    """
    encoded = text.encode("utf-8")
    if len(encoded) <= limit:
        return text
    
    # Truncate and decode, ignoring incomplete characters at the end
    truncated = encoded[:limit].decode("utf-8", "ignore")
    logger.warning(f"Input truncated from {len(encoded)} to {len(truncated.encode('utf-8'))} bytes")
    return truncated

def _create_strict_system_prompt() -> str:
    """
    Create the system prompt that enforces strict, fact-based responses.
    
    Returns:
        System prompt text
    """
    return (
        "You are a precise sports data analyst. Your responses must be based ONLY on the "
        "JSON data provided to you. Follow these strict rules:\n\n"
        "1. NEVER infer, calculate, or fabricate any statistics or information\n"
        "2. If a statistic or piece of information is not present in the JSON, respond with 'unavailable'\n"
        "3. Only summarize and present data that is explicitly present in the provided JSON\n"
        "4. Do not make assumptions about missing data or fill in gaps with general knowledge\n"
        "5. Be concise and factual in your responses\n"
        "6. If asked about something not in the data, clearly state it is not available in the provided data\n\n"
        "Your goal is to provide accurate, data-driven responses without any speculation or fabrication."
    )

async def strict_answer(payload: Dict[str, Any], question: str) -> Tuple[bool, str]:
    """
    Get a strict, fact-based answer from OpenRouter based only on provided JSON data.
    
    Args:
        payload: JSON data to analyze (typically game summary or other sports data)
        question: Question to ask about the data
        
    Returns:
        Tuple of (success: bool, response: str)
        - If success is True, response contains the answer
        - If success is False, response contains the error message
        
    Raises:
        LLMConfigurationError: If configuration is invalid
    """
    try:
        # Validate configuration
        _validate_configuration()
        
        # Prepare the JSON data as a string
        json_data = json.dumps(payload, ensure_ascii=False, indent=2)
        truncated_data = _truncate_utf8(json_data)
        
        if len(json_data) != len(truncated_data):
            logger.warning("JSON payload was truncated due to size limits")
        
        # Create the request payload
        request_payload = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": _create_strict_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"Here is the JSON data to analyze:\n\n{truncated_data}"
                },
                {
                    "role": "user",
                    "content": f"Question: {question}"
                }
            ],
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "stream": False
        }
        
        # Make the API call
        client = await _get_openrouter_client()
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "X-Title": "Sports AI MCP Client"
        }
        
        logger.debug(f"Making OpenRouter API call with model {OPENROUTER_MODEL}")
        
        response = await client.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=request_payload
        )
        
        # Handle HTTP errors
        if response.status_code >= 400:
            error_text = response.text[:300] if response.text else "No error details"
            logger.error(f"OpenRouter API error {response.status_code}: {error_text}")
            return False, f"OpenRouter API error {response.status_code}: {error_text}"
        
        # Parse the response
        try:
            response_data = response.json()
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenRouter response as JSON: {e}")
            return False, f"Invalid JSON response from OpenRouter: {e}"
        
        # Extract the content
        choices = response_data.get("choices", [])
        if not choices:
            logger.error("No choices in OpenRouter response")
            return False, "No response choices returned from OpenRouter"
        
        message = choices[0].get("message", {})
        content = message.get("content", "").strip()
        
        if not content:
            logger.warning("Empty content in OpenRouter response")
            return False, "Empty response from OpenRouter"
        
        logger.debug(f"OpenRouter response successful, {len(content)} characters")
        return True, content
        
    except httpx.RequestError as e:
        logger.error(f"Network error calling OpenRouter: {e}")
        return False, f"Network error: {e}"
    
    except Exception as e:
        logger.error(f"Unexpected error in strict_answer: {e}")
        return False, f"Unexpected error: {e}"

async def close_client() -> None:
    """Close the OpenRouter HTTP client if it exists."""
    global _openrouter_client
    if _openrouter_client is not None:
        await _openrouter_client.aclose()
        _openrouter_client = None
        logger.debug("OpenRouter client closed")

# Configuration validation function for external use
def validate_llm_config() -> Dict[str, Any]:
    """
    Validate LLM configuration and return status information.
    
    Returns:
        Dictionary with configuration status and details
    """
    config_status = {
        "valid": True,
        "errors": [],
        "config": {
            "api_key_configured": bool(OPENROUTER_API_KEY),
            "base_url": OPENROUTER_BASE_URL,
            "model": OPENROUTER_MODEL,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS
        }
    }
    
    try:
        _validate_configuration()
    except LLMConfigurationError as e:
        config_status["valid"] = False
        config_status["errors"].append(str(e))
    
    return config_status