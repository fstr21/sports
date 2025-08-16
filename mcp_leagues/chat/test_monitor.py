#!/usr/bin/env python3
"""
Test Discord Monitor - Quick test without interactive input
"""

import asyncio
import os
from dotenv import load_dotenv
from openrouter_discord_bridge import OpenRouterDiscordBridge

# Load .env
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..", "..")
env_file = os.path.join(project_root, ".env.local")

if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    load_dotenv()

async def test_monitoring():
    """Quick test of monitoring functionality"""
    print("Testing Discord monitoring...")
    
    bridge = OpenRouterDiscordBridge()
    
    async with bridge:
        # Test 1: Read recent messages
        print("1. Reading recent messages...")
        messages = await bridge.read_discord_messages("mcp-testing", limit=3)
        print(f"Found {len(messages)} messages")
        
        for msg in messages:
            print(f"  {msg.author}: {msg.content}")
        
        # Test 2: Generate AI response
        if messages:
            test_message = messages[0]
            print(f"\n2. Testing AI response to: {test_message.content}")
            
            prompt = f"""
You are a helpful AI assistant in a Discord community.

User {test_message.author} said: {test_message.content}

Provide a brief, helpful response (under 150 characters).
"""
            
            messages_ai = [{"role": "user", "content": prompt}]
            ai_response = await bridge.call_openrouter(messages_ai, max_tokens=100)
            
            print(f"AI Response: {ai_response}")
            
            # Test 3: Send test message
            print("\n3. Testing message sending...")
            test_response = f"Test response: {ai_response[:50]}..."
            
            result = await bridge.send_discord_message("mcp-testing", test_response)
            
            if result["success"]:
                print("SUCCESS: Message sent successfully!")
            else:
                print(f"FAILED: {result.get('error')}")
        
        else:
            print("No messages found to test with")

if __name__ == "__main__":
    asyncio.run(test_monitoring())