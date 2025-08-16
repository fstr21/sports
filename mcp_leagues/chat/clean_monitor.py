#!/usr/bin/env python3
"""
Clean Discord Monitor - No Unicode issues
"""

import asyncio
import os
import re
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

def clean_unicode(text):
    """Remove Unicode characters that cause Windows encoding issues"""
    # Remove emojis and other Unicode characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text.strip()

async def test_auto_response():
    """Test automatic response to trigger words"""
    print("Testing automatic Discord responses...")
    
    bridge = OpenRouterDiscordBridge()
    
    async with bridge:
        # Read recent messages
        messages = await bridge.read_discord_messages("mcp-testing", limit=5)
        print(f"Found {len(messages)} recent messages")
        
        for msg in messages[:3]:
            content_clean = clean_unicode(msg.content)
            author_clean = clean_unicode(msg.author)
            print(f"  {author_clean}: {content_clean}")
        
        # Look for messages that should trigger AI
        trigger_keywords = ["!ai", "picks", "prediction", "analysis", "odds", "bet", "game", "tonight", "today", "help"]
        
        for message in messages:
            content_lower = message.content.lower()
            
            # Check if message should trigger AI response
            should_respond = any(keyword.lower() in content_lower for keyword in trigger_keywords)
            
            if should_respond and not message.author.lower() in ["chat_mcp", "ai bot"]:
                print(f"\nResponding to trigger: {clean_unicode(message.content[:50])}")
                
                # Generate AI response
                prompt = f"""
You are a helpful sports betting AI assistant in Discord.

User {message.author} said: {message.content}

Provide a helpful, concise response under 150 characters. No emojis.
"""
                
                messages_ai = [{"role": "user", "content": prompt}]
                ai_response = await bridge.call_openrouter(messages_ai, max_tokens=100)
                
                # Clean the response
                ai_response_clean = clean_unicode(ai_response)
                print(f"Generated response: {ai_response_clean}")
                
                # Send to Discord
                result = await bridge.send_discord_message("mcp-testing", ai_response_clean)
                
                if result["success"]:
                    print("SUCCESS: Response sent to Discord!")
                else:
                    print(f"FAILED: {result.get('error', 'Unknown error')}")
                
                break  # Only respond to first trigger found
        
        print("\nTest complete!")

if __name__ == "__main__":
    asyncio.run(test_auto_response())