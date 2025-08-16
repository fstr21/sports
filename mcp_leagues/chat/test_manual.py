#!/usr/bin/env python3
"""
Simple Manual Testing Script (Windows Compatible)
Test your OpenRouter Discord Bridge easily
"""

import asyncio
import os
from dotenv import load_dotenv
from openrouter_discord_bridge import OpenRouterDiscordBridge

# Load .env from main project folder (handle both run locations)
import os
import sys

# Find the .env file in the main sports directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..", "..")
env_file = os.path.join(project_root, ".env")

if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    # Fallback: try current directory
    load_dotenv()

# Configuration
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-haiku")
DISCORD_URL = os.getenv("DISCORD_MCP_URL", "https://chatmcp-production.up.railway.app/mcp")
CHANNEL = os.getenv("DEFAULT_CHANNEL", "mcp-testing")

async def test_ai(prompt="Hello, are you working?"):
    """Test AI response"""
    print(f"Testing AI with: {prompt}")
    
    if not API_KEY:
        print("ERROR: No API key found in .env file")
        return False
    
    bridge = OpenRouterDiscordBridge()
    
    async with bridge:
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await bridge.call_openrouter(messages, max_tokens=100)
            print(f"AI Response: {response}")
            return True
        except Exception as e:
            print(f"AI Error: {e}")
            return False

async def test_discord_send(message="Test message from OpenRouter"):
    """Test sending to Discord"""
    print(f"Testing Discord send: {message}")
    
    if not API_KEY:
        print("ERROR: No API key found")
        return False
    
    bridge = OpenRouterDiscordBridge()
    
    async with bridge:
        try:
            result = await bridge.send_discord_message(CHANNEL, message)
            
            if result["success"]:
                print("SUCCESS: Message sent to Discord!")
                return True
            else:
                error_msg = result.get("error", "Unknown error")
                print(f"FAILED: {error_msg}")
                
                if "Missing Access" in error_msg:
                    print("HINT: This is a Discord bot permission issue")
                    print("      Grant bot 'Send Messages' permission")
                return False
        except Exception as e:
            print(f"ERROR: {e}")
            return False

async def test_discord_read():
    """Test reading from Discord"""
    print("Testing Discord read...")
    
    if not API_KEY:
        print("ERROR: No API key found")
        return False
    
    bridge = OpenRouterDiscordBridge()
    
    async with bridge:
        try:
            messages = await bridge.read_discord_messages(CHANNEL, limit=3)
            
            if messages and len(messages) > 0:
                print(f"SUCCESS: Read {len(messages)} messages")
                for msg in messages[:2]:  # Show first 2
                    # Handle different message formats
                    if hasattr(msg, 'author') and hasattr(msg, 'content'):
                        print(f"  {msg.author}: {msg.content[:50]}...")
                    elif isinstance(msg, dict):
                        author = msg.get('author', 'Unknown')
                        content = msg.get('content', '')
                        print(f"  {author}: {content[:50]}...")
                    else:
                        print(f"  Message: {str(msg)[:50]}...")
                return True
            else:
                print("FAILED: No messages or permission denied")
                print("HINT: Grant bot 'Read Message History' permission")
                return False
        except Exception as e:
            print(f"ERROR: {e}")
            # Debug: Show what type of data we got
            import traceback
            print(f"DEBUG: Full error: {traceback.format_exc()}")
            return False

async def interactive_test():
    """Interactive testing"""
    print("=" * 50)
    print("OPENROUTER DISCORD BRIDGE - MANUAL TEST")
    print("=" * 50)
    print(f"API Key: {'FOUND' if API_KEY else 'MISSING'}")
    print(f"Model: {MODEL}")
    print(f"Channel: {CHANNEL}")
    print("=" * 50)
    
    if not API_KEY:
        print("ERROR: Set OPENROUTER_API_KEY in .env file first!")
        return
    
    while True:
        print("\nTest Options:")
        print("1. Test AI Response")
        print("2. Test Discord Send") 
        print("3. Test Discord Read")
        print("4. Quick Full Test")
        print("5. Custom AI Prompt")
        print("6. Send Custom Message")
        print("7. Change Model")
        print("8. Exit")
        
        choice = input("\nChoose (1-8): ").strip()
        
        if choice == "1":
            await test_ai()
            
        elif choice == "2":
            await test_discord_send()
            
        elif choice == "3":
            await test_discord_read()
            
        elif choice == "4":
            print("\nRunning quick full test...")
            ai_ok = await test_ai("Say 'Test OK'")
            send_ok = await test_discord_send("Test from OpenRouter Bridge")
            read_ok = await test_discord_read()
            
            print(f"\nResults: AI={ai_ok}, Send={send_ok}, Read={read_ok}")
            
        elif choice == "5":
            prompt = input("Enter AI prompt: ").strip()
            if prompt:
                await test_ai(prompt)
                
        elif choice == "6":
            message = input("Enter message to send: ").strip()
            if message:
                await test_discord_send(message)
                
        elif choice == "7":
            print("\nAvailable models:")
            models = [
                "anthropic/claude-3.5-haiku",
                "anthropic/claude-3.5-sonnet", 
                "openai/gpt-4-turbo",
                "meta-llama/llama-3.1-8b-instruct"
            ]
            for i, model in enumerate(models, 1):
                print(f"{i}. {model}")
            
            try:
                model_choice = int(input("Choose model (1-4): "))
                if 1 <= model_choice <= len(models):
                    selected_model = models[model_choice-1]
                    print(f"Testing with model: {selected_model}")
                    # Test the new model
                    bridge = OpenRouterDiscordBridge(default_model=selected_model)
                    async with bridge:
                        messages = [{"role": "user", "content": "Hello with new model"}]
                        response = await bridge.call_openrouter(messages, max_tokens=50)
                        print(f"Response: {response}")
            except ValueError:
                print("Invalid choice")
                
        elif choice == "8":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice (1-8)")

if __name__ == "__main__":
    asyncio.run(interactive_test())