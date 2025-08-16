#!/usr/bin/env python3
"""
Manual Discord Testing Script
Easy way to test your OpenRouter Discord Bridge manually
"""

import asyncio
import os
from dotenv import load_dotenv
from openrouter_discord_bridge import OpenRouterDiscordBridge

load_dotenv()

# Configuration from .env
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "anthropic/claude-3.5-haiku")
DISCORD_MCP_URL = os.getenv("DISCORD_MCP_URL", "https://chatmcp-production.up.railway.app/mcp")
DEFAULT_CHANNEL = os.getenv("DEFAULT_CHANNEL", "mcp-testing")

def print_config():
    """Show current configuration"""
    print("=" * 50)
    print("OPENROUTER DISCORD BRIDGE - MANUAL TEST")
    print("=" * 50)
    print(f"API Key: {'FOUND' if OPENROUTER_API_KEY else 'MISSING'}")
    print(f"Model: {DEFAULT_MODEL}")
    print(f"Discord MCP: {DISCORD_MCP_URL}")
    print(f"Test Channel: {DEFAULT_CHANNEL}")
    print("=" * 50)

async def test_ai_response(prompt: str, model: str = None):
    """Test AI response with custom prompt"""
    if not OPENROUTER_API_KEY:
        print("❌ No OpenRouter API key found!")
        return
    
    model_to_use = model or DEFAULT_MODEL
    print(f"\n🤖 Testing AI with model: {model_to_use}")
    print(f"📝 Prompt: {prompt}")
    
    bridge = OpenRouterDiscordBridge(
        openrouter_api_key=OPENROUTER_API_KEY,
        default_model=model_to_use
    )
    
    async with bridge:
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await bridge.call_openrouter(messages, max_tokens=200)
            print(f"💬 AI Response: {response}")
            return response
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

async def test_discord_send(message: str, channel: str = None):
    """Test sending message to Discord"""
    if not OPENROUTER_API_KEY:
        print("❌ No OpenRouter API key found!")
        return
    
    channel_to_use = channel or DEFAULT_CHANNEL
    print(f"\n📤 Testing Discord send to #{channel_to_use}")
    print(f"📝 Message: {message}")
    
    bridge = OpenRouterDiscordBridge(
        openrouter_api_key=OPENROUTER_API_KEY,
        discord_mcp_url=DISCORD_MCP_URL
    )
    
    async with bridge:
        try:
            result = await bridge.send_discord_message(channel_to_use, message)
            
            if result["success"]:
                print("✅ Message sent successfully!")
                print(f"📊 Details: {result.get('data', {})}")
            else:
                print(f"❌ Failed to send: {result.get('error')}")
                
                # Check if it's a permission issue
                if "Missing Access" in str(result.get("error", "")):
                    print("💡 This is likely a Discord bot permission issue")
                    print("   Fix: Grant bot 'Send Messages' permission in Discord server")
            
            return result["success"]
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

async def test_discord_read(channel: str = None, limit: int = 3):
    """Test reading messages from Discord"""
    if not OPENROUTER_API_KEY:
        print("❌ No OpenRouter API key found!")
        return
    
    channel_to_use = channel or DEFAULT_CHANNEL
    print(f"\n📥 Testing Discord read from #{channel_to_use}")
    
    bridge = OpenRouterDiscordBridge(
        openrouter_api_key=OPENROUTER_API_KEY,
        discord_mcp_url=DISCORD_MCP_URL
    )
    
    async with bridge:
        try:
            messages = await bridge.read_discord_messages(channel_to_use, limit)
            
            if messages:
                print(f"✅ Found {len(messages)} messages:")
                for msg in messages:
                    print(f"   {msg.author}: {msg.content[:50]}...")
            else:
                print("❌ No messages found or permission denied")
                print("💡 This might be a Discord bot permission issue")
                print("   Fix: Grant bot 'Read Message History' permission")
            
            return len(messages) > 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

async def test_full_conversation(user_question: str, channel: str = None):
    """Test full conversation flow: AI generates response and sends to Discord"""
    if not OPENROUTER_API_KEY:
        print("❌ No OpenRouter API key found!")
        return
    
    channel_to_use = channel or DEFAULT_CHANNEL
    print(f"\n🔄 Testing full conversation flow in #{channel_to_use}")
    print(f"❓ User Question: {user_question}")
    
    bridge = OpenRouterDiscordBridge(
        openrouter_api_key=OPENROUTER_API_KEY,
        default_model=DEFAULT_MODEL,
        discord_mcp_url=DISCORD_MCP_URL
    )
    
    async with bridge:
        # Step 1: Generate AI response
        print("🤖 Generating AI response...")
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Keep responses concise and friendly."},
            {"role": "user", "content": user_question}
        ]
        
        try:
            ai_response = await bridge.call_openrouter(messages, max_tokens=150)
            print(f"💬 AI Generated: {ai_response}")
            
            # Step 2: Send to Discord
            print("📤 Sending to Discord...")
            result = await bridge.send_discord_message(channel_to_use, ai_response)
            
            if result["success"]:
                print("✅ Full conversation flow successful!")
            else:
                print(f"❌ Discord send failed: {result.get('error')}")
            
            return result["success"]
        except Exception as e:
            print(f"❌ Error in conversation flow: {e}")
            return False

async def interactive_menu():
    """Interactive menu for manual testing"""
    print_config()
    
    while True:
        print("\n" + "=" * 30)
        print("MANUAL TEST OPTIONS:")
        print("1. Test AI Response (custom prompt)")
        print("2. Test Discord Send")
        print("3. Test Discord Read")
        print("4. Test Full Conversation Flow")
        print("5. Change Model")
        print("6. Quick Sports Test")
        print("7. Exit")
        print("=" * 30)
        
        choice = input("Choose option (1-7): ").strip()
        
        if choice == "1":
            prompt = input("Enter prompt for AI: ").strip()
            if prompt:
                await test_ai_response(prompt)
        
        elif choice == "2":
            message = input("Enter message to send to Discord: ").strip()
            if message:
                channel = input(f"Channel (default: {DEFAULT_CHANNEL}): ").strip() or DEFAULT_CHANNEL
                await test_discord_send(message, channel)
        
        elif choice == "3":
            channel = input(f"Channel to read from (default: {DEFAULT_CHANNEL}): ").strip() or DEFAULT_CHANNEL
            await test_discord_read(channel)
        
        elif choice == "4":
            question = input("Enter user question: ").strip()
            if question:
                channel = input(f"Channel (default: {DEFAULT_CHANNEL}): ").strip() or DEFAULT_CHANNEL
                await test_full_conversation(question, channel)
        
        elif choice == "5":
            print("\nAvailable models:")
            models = [
                "anthropic/claude-3.5-haiku (Fast & Cheap)",
                "anthropic/claude-3.5-sonnet (Balanced)",
                "openai/gpt-4-turbo (Creative)",
                "meta-llama/llama-3.1-8b-instruct (Budget)"
            ]
            for i, model in enumerate(models, 1):
                print(f"{i}. {model}")
            
            model_choice = input("Choose model number: ").strip()
            if model_choice.isdigit() and 1 <= int(model_choice) <= len(models):
                model_name = models[int(model_choice)-1].split(" ")[0]
                print(f"Testing with {model_name}...")
                await test_ai_response("Say hello and tell me your model name", model_name)
        
        elif choice == "6":
            print("🏈 Quick Sports Test")
            await test_ai_response("Give me a quick analysis of why the Chiefs are a good team this season. Keep it under 100 words.")
        
        elif choice == "7":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-7.")

async def quick_test():
    """Run a quick automated test of all functions"""
    print_config()
    print("\n🚀 Running Quick Test Suite...")
    
    # Test 1: AI Response
    print("\n1️⃣ Testing AI Response...")
    ai_working = await test_ai_response("Say 'Test successful' and nothing else")
    
    # Test 2: Discord Send
    print("\n2️⃣ Testing Discord Send...")
    discord_send_working = await test_discord_send("Test message from OpenRouter Bridge")
    
    # Test 3: Discord Read  
    print("\n3️⃣ Testing Discord Read...")
    discord_read_working = await test_discord_read()
    
    # Summary
    print("\n" + "=" * 40)
    print("QUICK TEST RESULTS:")
    print(f"✅ AI Response: {'WORKING' if ai_working else 'FAILED'}")
    print(f"📤 Discord Send: {'WORKING' if discord_send_working else 'PERMISSION ISSUE'}")
    print(f"📥 Discord Read: {'WORKING' if discord_read_working else 'PERMISSION ISSUE'}")
    
    if ai_working and (discord_send_working or discord_read_working):
        print("\n🎉 Core integration is working!")
    elif ai_working:
        print("\n⚠️ AI working, Discord needs permissions")
    else:
        print("\n❌ Check API key and configuration")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # Run quick automated test
        asyncio.run(quick_test())
    else:
        # Run interactive menu
        asyncio.run(interactive_menu())