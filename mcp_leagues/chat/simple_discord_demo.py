#!/usr/bin/env python3
"""
Simple Discord Integration Demo
Shows how to use OpenRouter AI with Discord context
"""

import asyncio
import os
from dotenv import load_dotenv
from openrouter_discord_bridge import OpenRouterDiscordBridge

# Load .env from main project folder
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..", "..")
env_file = os.path.join(project_root, ".env")

if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    load_dotenv()

async def discord_aware_ai(question: str, channel: str = "mcp-testing"):
    """
    AI that can see Discord context and respond accordingly
    """
    print(f"Question: {question}")
    print("Reading Discord context...")
    
    bridge = OpenRouterDiscordBridge()
    
    async with bridge:
        # Read recent Discord messages
        recent_messages = await bridge.read_discord_messages(channel, limit=5)
        
        # Show what the AI can see
        print(f"AI can see {len(recent_messages)} recent messages:")
        for msg in recent_messages[:3]:
            print(f"  {msg.author}: {msg.content[:50]}...")
        
        # Build context for AI
        context = "Recent Discord conversation:\n"
        for msg in recent_messages:
            context += f"{msg.author}: {msg.content}\n"
        
        # Create AI prompt with Discord context
        prompt = f"""
You are an AI assistant that can see Discord messages. Here's what's happening in the channel:

{context}

User question: {question}

Based on what you can see in the Discord channel, provide a helpful response.
"""
        
        # Get AI response
        print("Generating response...")
        messages = [{"role": "user", "content": prompt}]
        ai_response = await bridge.call_openrouter(messages, max_tokens=200)
        
        print(f"AI Response: {ai_response}")
        
        # Ask if user wants to send to Discord
        send_to_discord = input("\nSend this response to Discord? (y/n): ").strip().lower()
        
        if send_to_discord == 'y':
            result = await bridge.send_discord_message(channel, ai_response)
            if result["success"]:
                print("SUCCESS: Posted to Discord!")
            else:
                print(f"FAILED: {result.get('error')}")
        
        return ai_response

async def send_sports_update(channel: str = "mcp-testing"):
    """Send AI-generated sports update to Discord"""
    print("Generating sports update...")
    
    bridge = OpenRouterDiscordBridge()
    
    async with bridge:
        prompt = """
Create a brief sports betting tip or insight for Discord. 
Include practical advice and keep it under 150 characters.
Make it engaging and useful for sports bettors.
"""
        
        messages = [{"role": "user", "content": prompt}]
        update = await bridge.call_openrouter(messages, max_tokens=100)
        
        print(f"Generated update: {update}")
        
        # Send to Discord
        result = await bridge.send_discord_message(channel, update)
        
        if result["success"]:
            print("SUCCESS: Sports update posted to Discord!")
        else:
            print(f"FAILED: {result.get('error')}")

async def main():
    print("Discord Integration Demo")
    print("=" * 30)
    
    while True:
        print("\nOptions:")
        print("1. Ask AI about Discord channel")
        print("2. Send sports update to Discord") 
        print("3. Read Discord messages")
        print("4. Exit")
        
        choice = input("\nChoose (1-4): ").strip()
        
        if choice == "1":
            question = input("Ask AI about the Discord channel: ").strip()
            if question:
                await discord_aware_ai(question)
        
        elif choice == "2":
            await send_sports_update()
        
        elif choice == "3":
            bridge = OpenRouterDiscordBridge()
            async with bridge:
                messages = await bridge.read_discord_messages("mcp-testing", limit=5)
                print(f"\nRecent messages from #mcp-testing:")
                for msg in messages:
                    print(f"  {msg.author}: {msg.content}")
        
        elif choice == "4":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())