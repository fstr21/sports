#!/usr/bin/env python3
"""
Auto Discord Monitor - Runs without interactive input
"""

import asyncio
import os
import re
from datetime import datetime, timezone
from dotenv import load_dotenv
from openrouter_discord_bridge import OpenRouterDiscordBridge

# Load .env
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..", "..")
env_file = os.path.join(project_root, ".env")

if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    load_dotenv()

def clean_unicode(text):
    """Remove Unicode characters that cause Windows encoding issues"""
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text.strip()

class DiscordAIMonitor:
    def __init__(self, channel="mcp-testing"):
        self.channel = channel
        self.bridge = None
        self.last_message_time = None
        self.bot_name = "AI Bot"
        
        # Keywords that trigger AI responses
        self.trigger_keywords = [
            "!ai",           # Direct AI command
            "picks",         # Betting picks
            "prediction",    # Game predictions  
            "analysis",      # Sports analysis
            "odds",          # Betting odds
            "bet",           # General betting
            "game",          # Games
            "tonight",       # Tonight's games
            "today",         # Today's games
            "help",          # Help requests
            "question"       # Questions
        ]
        
        # Sports-related keywords for enhanced responses
        self.sports_keywords = [
            "nfl", "nba", "mlb", "nhl", "soccer", "football", "basketball", 
            "baseball", "hockey", "chiefs", "lakers", "yankees", "cowboys"
        ]

    async def start_monitoring(self, max_cycles=10):
        """Start monitoring Discord channel"""
        print(f"Starting AI monitor for #{self.channel}")
        print(f"Trigger keywords: {', '.join(self.trigger_keywords)}")
        print(f"Max cycles: {max_cycles} (for testing)")
        print("-" * 50)
        
        self.bridge = OpenRouterDiscordBridge()
        
        async with self.bridge:
            # Set initial timestamp
            messages = await self.bridge.read_discord_messages(self.channel, limit=1)
            if messages:
                self.last_message_time = messages[0].timestamp
            
            # Monitor loop
            cycles = 0
            while cycles < max_cycles:
                try:
                    await self.check_for_new_messages()
                    cycles += 1
                    print(f"Cycle {cycles}/{max_cycles} completed")
                    await asyncio.sleep(5)  # Check every 5 seconds for testing
                except KeyboardInterrupt:
                    print("Stopping monitor...")
                    break
                except Exception as e:
                    print(f"Error: {clean_unicode(str(e))}")
                    await asyncio.sleep(10)
            
            print("Monitoring complete!")

    async def check_for_new_messages(self):
        """Check for new messages and respond if needed"""
        try:
            messages = await self.bridge.read_discord_messages(self.channel, limit=5)
            
            for message in messages:
                # Skip old messages
                if self.last_message_time and message.timestamp <= self.last_message_time:
                    continue
                
                # Skip our own messages
                if message.author.lower() in [self.bot_name.lower(), "chat_mcp"]:
                    continue
                
                # Check if message should trigger AI response
                if self.should_respond(message.content):
                    print(f"Responding to {clean_unicode(message.author)}: {clean_unicode(message.content[:50])}...")
                    await self.generate_and_send_response(message)
                
                # Update last message time
                self.last_message_time = message.timestamp
                
        except Exception as e:
            print(f"Error checking messages: {clean_unicode(str(e))}")

    def should_respond(self, content):
        """Check if message should trigger AI response"""
        content_lower = content.lower()
        
        # Direct AI commands (always respond)
        if content_lower.startswith("!ai"):
            return True
        
        # Check for trigger keywords
        for keyword in self.trigger_keywords:
            if keyword.lower() in content_lower:
                return True
        
        return False

    async def generate_and_send_response(self, message):
        """Generate AI response and send to Discord"""
        try:
            # Read recent context
            recent_messages = await self.bridge.read_discord_messages(self.channel, limit=5)
            
            # Build context
            context = "Recent Discord conversation:\\n"
            for msg in recent_messages[-3:]:  # Last 3 messages
                context += f"{clean_unicode(msg.author)}: {clean_unicode(msg.content)}\\n"
            
            # Determine if this is sports-related
            is_sports = any(keyword in message.content.lower() for keyword in self.sports_keywords)
            
            # Create appropriate prompt
            if message.content.lower().startswith("!ai"):
                # Direct AI command
                user_question = message.content[3:].strip()
                prompt = f"""
You are a helpful AI assistant in a Discord sports betting community.

Context: {context}

User {message.author} asked: {user_question}

Provide a helpful, concise response (under 200 characters for Discord). No emojis.
"""
            elif is_sports:
                # Sports-related response
                prompt = f"""
You are a sports betting AI assistant in a Discord channel.

Context: {context}

User {message.author} said: {message.content}

Provide helpful sports/betting advice or information. Keep it under 200 characters. No emojis.
"""
            else:
                # General helpful response
                prompt = f"""
You are a helpful AI assistant in a Discord community.

Context: {context}

User {message.author} said: {message.content}

Provide a brief, helpful response (under 150 characters). No emojis.
"""
            
            # Generate response
            messages_ai = [{"role": "user", "content": prompt}]
            ai_response = await self.bridge.call_openrouter(messages_ai, max_tokens=100)
            
            # Clean up response (remove quotes, Unicode, etc.)
            ai_response = ai_response.strip().strip('"')
            ai_response = clean_unicode(ai_response)
            
            # Send to Discord
            result = await self.bridge.send_discord_message(self.channel, ai_response)
            
            if result["success"]:
                print(f"SUCCESS: Sent: {ai_response[:50]}...")
            else:
                print(f"FAILED: {result.get('error')}")
                
        except Exception as e:
            print(f"Error generating response: {clean_unicode(str(e))}")

async def main():
    print("Auto Discord AI Monitor")
    print("=" * 30)
    print("This will monitor Discord and respond to messages automatically")
    print()
    
    monitor = DiscordAIMonitor("mcp-testing")
    await monitor.start_monitoring(max_cycles=20)  # Run 20 cycles for testing

if __name__ == "__main__":
    asyncio.run(main())