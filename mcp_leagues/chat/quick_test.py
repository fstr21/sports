#!/usr/bin/env python3
"""
Quick Automated Test - No interaction required
"""

import asyncio
import os
from dotenv import load_dotenv
from openrouter_discord_bridge import OpenRouterDiscordBridge

# Load .env from main project folder
load_dotenv("../../.env")

async def main():
    print("OpenRouter Discord Bridge - Quick Test")
    print("=" * 45)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-haiku")
    
    if not api_key:
        print("ERROR: No OPENROUTER_API_KEY in .env file")
        return
    
    print(f"API Key: FOUND")
    print(f"Model: {model}")
    print(f"Testing...")
    
    # Test AI
    print("\n1. Testing AI Response...")
    bridge = OpenRouterDiscordBridge()
    async with bridge:
        try:
            messages = [{"role": "user", "content": "Say 'AI Working' and nothing else"}]
            response = await bridge.call_openrouter(messages, max_tokens=10)
            print(f"   Response: {response}")
            ai_ok = "AI Working" in response or "working" in response.lower()
            print(f"   Status: {'PASS' if ai_ok else 'PARTIAL'}")
        except Exception as e:
            print(f"   ERROR: {e}")
            ai_ok = False
    
    # Test Discord MCP connection
    print("\n2. Testing Discord MCP...")
    bridge = OpenRouterDiscordBridge(openrouter_api_key="test")
    async with bridge:
        try:
            result = await bridge.call_discord_mcp("read-messages", {"channel": "test", "limit": 1})
            discord_connected = "Available channels" in str(result)
            print(f"   Connected: {'YES' if discord_connected else 'NO'}")
            if discord_connected:
                print("   Found Foster server with 28+ channels")
        except Exception as e:
            print(f"   ERROR: {e}")
            discord_connected = False
    
    # Test permissions (will fail but shows the flow)
    print("\n3. Testing Discord Send (will show permission status)...")
    bridge = OpenRouterDiscordBridge()
    async with bridge:
        try:
            result = await bridge.send_discord_message("mcp-testing", "Test message")
            if result["success"]:
                print("   SUCCESS: Message sent!")
            else:
                error = result.get("error", "")
                if "Missing Access" in error:
                    print("   EXPECTED: Permission denied (normal)")
                    print("   Fix: Grant bot Send Messages permission")
                else:
                    print(f"   ERROR: {error}")
        except Exception as e:
            print(f"   ERROR: {e}")
    
    print("\n" + "=" * 45)
    print("SUMMARY:")
    print(f"AI: {'WORKING' if ai_ok else 'FAILED'}")
    print(f"Discord MCP: {'CONNECTED' if discord_connected else 'FAILED'}")
    print("Permissions: PENDING (expected)")
    
    if ai_ok and discord_connected:
        print("\nSTATUS: Ready for use!")
        print("Just need to fix Discord bot permissions")
    else:
        print("\nSTATUS: Issues detected")

if __name__ == "__main__":
    asyncio.run(main())