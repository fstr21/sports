#!/usr/bin/env python3
"""
OpenRouter Discord Bridge
Integrates OpenRouter LLMs with Discord MCP Server for bidirectional communication
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import httpx
from dataclasses import dataclass


@dataclass
class DiscordMessage:
    author: str
    content: str
    timestamp: str
    channel: str
    guild: str


class OpenRouterDiscordBridge:
    def __init__(
        self,
        openrouter_api_key: str = None,
        discord_mcp_url: str = None,
        default_model: str = None,
        base_url: str = None
    ):
        # Load from environment if not provided
        import os
        from dotenv import load_dotenv
        
        # Try to load main project .env file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(script_dir, "..", "..")
        env_file = os.path.join(project_root, ".env.local")
        
        if os.path.exists(env_file):
            load_dotenv(env_file)
        else:
            load_dotenv()  # Fallback to current directory
        
        self.openrouter_api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        self.discord_mcp_url = discord_mcp_url or os.getenv("DISCORD_MCP_URL", "https://chatmcp-production.up.railway.app/mcp")
        self.default_model = default_model or os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-haiku")
        self.base_url = base_url or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def call_discord_mcp(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call Discord MCP server with proper JSON-RPC format"""
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            response = await self.client.post(
                self.discord_mcp_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            return response.json()
        except Exception as e:
            return {"error": f"MCP call failed: {str(e)}"}

    async def send_discord_message(self, channel: str, message: str, server: Optional[str] = None) -> Dict[str, Any]:
        """Send message to Discord channel via MCP"""
        args = {"channel": channel, "message": message}
        if server:
            args["server"] = server
            
        result = await self.call_discord_mcp("send-message", args)
        
        if "result" in result:
            return {"success": True, "data": result["result"]}
        else:
            return {"success": False, "error": result.get("error", {}).get("message", "Unknown error")}

    async def read_discord_messages(self, channel: str, limit: int = 10, server: Optional[str] = None) -> List[DiscordMessage]:
        """Read recent messages from Discord channel via MCP"""
        args = {"channel": channel, "limit": limit}
        if server:
            args["server"] = server
            
        result = await self.call_discord_mcp("read-messages", args)
        
        if "result" in result and "content" in result["result"]:
            try:
                # Parse the JSON content from MCP response
                content_text = result["result"]["content"][0]["text"]
                messages_data = json.loads(content_text)
                
                # Handle different response formats
                if isinstance(messages_data, list):
                    return [
                        DiscordMessage(
                            author=msg.get("author", "Unknown") if isinstance(msg, dict) else str(msg),
                            content=msg.get("content", "") if isinstance(msg, dict) else str(msg),
                            timestamp=msg.get("timestamp", "") if isinstance(msg, dict) else "",
                            channel=msg.get("channel", channel) if isinstance(msg, dict) else channel,
                            guild=msg.get("guild", "") if isinstance(msg, dict) else ""
                        )
                        for msg in messages_data
                    ]
                elif isinstance(messages_data, dict) and "messages" in messages_data:
                    # Handle wrapped response format
                    messages = messages_data["messages"]
                    return [
                        DiscordMessage(
                            author=msg.get("author", "Unknown"),
                            content=msg.get("content", ""),
                            timestamp=msg.get("timestamp", ""),
                            channel=msg.get("channel", channel),
                            guild=msg.get("guild", "")
                        )
                        for msg in messages if isinstance(msg, dict)
                    ]
                else:
                    # Unknown format, return empty
                    return []
            except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
                print(f"DEBUG: Error parsing messages: {e}")
                print(f"DEBUG: Raw result: {result}")
                return []
        return []

    async def call_openrouter(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1000
    ) -> str:
        """Call OpenRouter API with conversation"""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "max_tokens": max_tokens
        }
        
        try:
            response = await self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"OpenRouter API error: {str(e)}"

    async def process_discord_conversation(
        self,
        channel: str,
        user_message: str,
        context_messages: int = 5,
        model: Optional[str] = None,
        server: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a Discord conversation:
        1. Read recent Discord messages for context
        2. Add user message to conversation
        3. Get AI response from OpenRouter
        4. Send AI response back to Discord
        """
        
        # Read recent messages for context
        recent_messages = await self.read_discord_messages(channel, context_messages, server)
        
        # Build conversation context for OpenRouter
        conversation = []
        
        # Add system prompt for sports betting context
        conversation.append({
            "role": "system",
            "content": "You are a sports betting AI assistant. You provide analysis, picks, and insights about sports betting. Be helpful, accurate, and responsible about gambling advice."
        })
        
        # Add recent Discord messages as context
        for msg in reversed(recent_messages[-context_messages:]):  # Reverse to get chronological order
            if msg.content.strip():  # Skip empty messages
                conversation.append({
                    "role": "user" if msg.author != "your_bot_name" else "assistant",
                    "content": f"{msg.author}: {msg.content}"
                })
        
        # Add current user message
        conversation.append({
            "role": "user", 
            "content": user_message
        })
        
        # Get AI response
        ai_response = await self.call_openrouter(conversation, model)
        
        # Send response back to Discord
        send_result = await self.send_discord_message(channel, ai_response, server)
        
        return {
            "user_message": user_message,
            "ai_response": ai_response,
            "discord_sent": send_result["success"],
            "context_messages_count": len(recent_messages),
            "error": send_result.get("error") if not send_result["success"] else None
        }

    async def sports_betting_alert(
        self,
        channel: str,
        game_info: Dict[str, Any],
        odds_data: Dict[str, Any],
        server: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate and send sports betting alert using OpenRouter analysis
        """
        
        # Create prompt for AI analysis
        prompt = f"""
        Analyze this sports betting opportunity and provide a concise alert:
        
        Game: {game_info}
        Odds: {odds_data}
        
        Provide:
        1. Quick game summary
        2. Best betting value identified
        3. Brief reasoning (2-3 sentences max)
        4. Risk level (Low/Medium/High)
        
        Format for Discord (use emojis, keep under 200 characters):
        """
        
        # Get AI analysis
        conversation = [
            {"role": "system", "content": "You are a sports betting analyst. Provide concise, actionable betting insights."},
            {"role": "user", "content": prompt}
        ]
        
        alert_message = await self.call_openrouter(conversation, max_tokens=200)
        
        # Send to Discord
        send_result = await self.send_discord_message(channel, alert_message, server)
        
        return {
            "alert_generated": True,
            "alert_content": alert_message,
            "discord_sent": send_result["success"],
            "error": send_result.get("error") if not send_result["success"] else None
        }


# Example usage functions
async def example_chat_interaction():
    """Example: Interactive chat through Discord"""
    
    # Initialize bridge (you'll need to set your API key)
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "your_key_here")
    
    async with OpenRouterDiscordBridge(openrouter_key) as bridge:
        
        # Process a user question about sports betting
        result = await bridge.process_discord_conversation(
            channel="mcp-testing",
            user_message="What do you think about tonight's Lakers vs Warriors game?",
            context_messages=3,
            model="anthropic/claude-3.5-sonnet"
        )
        
        print("Chat Result:", result)


async def example_betting_alert():
    """Example: Automated betting alert"""
    
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "your_key_here")
    
    async with OpenRouterDiscordBridge(openrouter_key) as bridge:
        
        # Send automated betting alert
        game_info = {
            "teams": "Chiefs vs Ravens",
            "date": "2025-08-15",
            "time": "8:00 PM ET"
        }
        
        odds_data = {
            "moneyline": {"Chiefs": -110, "Ravens": +105},
            "spread": {"Chiefs": -2.5, "Ravens": +2.5},
            "total": {"over": 47.5, "under": 47.5}
        }
        
        result = await bridge.sports_betting_alert(
            channel="aggregated-picks",
            game_info=game_info,
            odds_data=odds_data
        )
        
        print("Alert Result:", result)


if __name__ == "__main__":
    # Test the bridge
    print("OpenRouter Discord Bridge - Testing...")
    
    # Uncomment to test:
    # asyncio.run(example_chat_interaction())
    # asyncio.run(example_betting_alert())
    
    print("Bridge ready for integration!")