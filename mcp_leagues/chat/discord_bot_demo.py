#!/usr/bin/env python3
"""
Discord Bot Demo - Shows how to use OpenRouter with Discord
"""

import asyncio
import os
from dotenv import load_dotenv
from openrouter_discord_bridge import OpenRouterDiscordBridge

# Load .env from main project folder
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..", "..")
env_file = os.path.join(project_root, ".env.local")

if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    load_dotenv()

async def answer_discord_question(question: str, channel: str = "mcp-testing"):
    """
    Complete flow: Read Discord context + Answer question + Send to Discord
    """
    print(f"🤖 Processing Discord question: {question}")
    
    bridge = OpenRouterDiscordBridge()
    
    async with bridge:
        # Step 1: Read recent Discord messages for context
        print("📥 Reading Discord context...")
        recent_messages = await bridge.read_discord_messages(channel, limit=5)
        
        # Step 2: Build context for AI
        context = "Recent Discord messages:\n"
        for msg in recent_messages:
            context += f"{msg.author}: {msg.content}\n"
        
        # Step 3: Create AI prompt with Discord context
        prompt = f"""
You are a helpful assistant in a Discord channel. Here's the recent conversation context:

{context}

User question: {question}

Please provide a helpful response. If the question is about sports, betting, or games, provide useful information.
"""
        
        # Step 4: Get AI response
        print("🧠 Generating AI response...")
        messages = [{"role": "user", "content": prompt}]
        ai_response = await bridge.call_openrouter(messages, max_tokens=300)
        
        # Step 5: Send AI response to Discord
        print("📤 Sending response to Discord...")
        result = await bridge.send_discord_message(channel, ai_response)
        
        if result["success"]:
            print("✅ Successfully posted AI response to Discord!")
            print(f"💬 AI said: {ai_response}")
        else:
            print(f"❌ Failed to send: {result.get('error')}")
        
        return ai_response

async def monitor_and_respond(channel: str = "mcp-testing", keywords: list = None):
    """
    Monitor Discord channel and respond to mentions/keywords
    """
    if keywords is None:
        keywords = ["@bot", "question:", "help", "betting", "picks"]
    
    print(f"👀 Monitoring #{channel} for keywords: {keywords}")
    
    bridge = OpenRouterDiscordBridge()
    last_checked = None
    
    async with bridge:
        while True:
            try:
                # Read recent messages
                messages = await bridge.read_discord_messages(channel, limit=3)
                
                for msg in messages:
                    # Skip if we've already seen this message
                    if last_checked and msg.timestamp <= last_checked:
                        continue
                    
                    # Check if message contains keywords
                    content_lower = msg.content.lower()
                    if any(keyword.lower() in content_lower for keyword in keywords):
                        print(f"🎯 Found keyword in: {msg.content}")
                        
                        # Generate contextual response
                        prompt = f"""
User {msg.author} said: {msg.content}

Provide a helpful response. If it's about sports/betting, give useful information.
Keep it conversational and under 200 characters.
"""
                        
                        messages_ai = [{"role": "user", "content": prompt}]
                        response = await bridge.call_openrouter(messages_ai, max_tokens=150)
                        
                        # Send response
                        await bridge.send_discord_message(channel, f"@{msg.author} {response}")
                        print(f"📤 Responded to {msg.author}")
                
                # Update last checked time
                if messages:
                    last_checked = max(msg.timestamp for msg in messages)
                
                # Wait before checking again
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                print("🛑 Monitoring stopped")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                await asyncio.sleep(60)  # Wait longer on error

async def interactive_discord_demo():
    """Interactive demo of Discord features"""
    print("🤖 Discord Bot Demo")
    print("=" * 40)
    
    while True:
        print("\nDiscord Bot Options:")
        print("1. Answer a question (with Discord context)")
        print("2. Send AI-generated sports update")
        print("3. Read Discord messages")
        print("4. Start monitoring mode (responds automatically)")
        print("5. Exit")
        
        choice = input("\nChoose (1-5): ").strip()
        
        if choice == "1":
            question = input("Enter question to answer: ").strip()
            if question:
                await answer_discord_question(question)
        
        elif choice == "2":
            bridge = OpenRouterDiscordBridge()
            async with bridge:
                # Generate sports update
                prompt = "Generate a brief, engaging sports update or betting tip for a Discord channel. Keep it under 200 characters and include an emoji."
                messages = [{"role": "user", "content": prompt}]
                update = await bridge.call_openrouter(messages, max_tokens=100)
                
                # Send to Discord
                result = await bridge.send_discord_message("mcp-testing", update)
                if result["success"]:
                    print(f"✅ Posted update: {update}")
                else:
                    print(f"❌ Failed: {result.get('error')}")
        
        elif choice == "3":
            bridge = OpenRouterDiscordBridge()
            async with bridge:
                messages = await bridge.read_discord_messages("mcp-testing", limit=5)
                print(f"\n📥 Last {len(messages)} messages from #mcp-testing:")
                for msg in messages:
                    print(f"  {msg.author}: {msg.content}")
        
        elif choice == "4":
            print("🤖 Starting monitoring mode... (Ctrl+C to stop)")
            await monitor_and_respond()
        
        elif choice == "5":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    print("🤖 OpenRouter Discord Bot Demo")
    print("This shows how to use AI with Discord integration")
    print()
    
    asyncio.run(interactive_discord_demo())