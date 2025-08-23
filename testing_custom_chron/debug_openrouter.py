#!/usr/bin/env python3
"""
Debug OpenRouter API Connection
Test the API key and connection separately
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")
load_dotenv("../.env.local")

async def debug_openrouter():
    """Debug OpenRouter API connection"""
    
    print("🔍 OPENROUTER DEBUG")
    print("=" * 40)
    
    # Check environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")
    base_url = "https://openrouter.ai/api/v1"
    
    print(f"🔑 API Key: {'Present' if api_key else 'Missing'}")
    if api_key:
        print(f"🔑 API Key Length: {len(api_key)}")
        print(f"🔑 API Key Prefix: {api_key[:10]}...")
    print(f"🤖 Model: {model}")
    print(f"🌐 Base URL: {base_url}")
    
    if not api_key:
        print("❌ No API key found. Check your .env.local file.")
        return
    
    # Test 1: Simple models endpoint
    print("\n🧪 TEST 1: Models Endpoint")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{base_url}/models",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"📊 Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Models endpoint works!")
                models = response.json()
                print(f"📋 Found {len(models.get('data', []))} models")
            else:
                print(f"❌ Models endpoint failed: {response.text}")
                
    except Exception as e:
        print(f"❌ Models endpoint error: {e}")
    
    # Test 2: Chat completion with minimal request
    print("\n🧪 TEST 2: Simple Chat Completion")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": "Say 'Hello OpenRouter!'"}
                    ],
                    "max_tokens": 10
                }
            )
            
            print(f"📊 Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "No content")
                print(f"✅ Chat completion works!")
                print(f"🤖 Response: {content}")
            else:
                print(f"❌ Chat completion failed: {response.text}")
                
    except Exception as e:
        print(f"❌ Chat completion error: {e}")
    
    # Test 3: Your configured model from .env
    print(f"\n🧪 TEST 3: Your Configured Model ({model})")
    print(f"🔄 Using model from OPENROUTER_MODEL: {model}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": "Just say 'Working!'"}
                    ],
                    "max_tokens": 5
                }
            )
            
            print(f"📊 Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "No content")
                print(f"✅ Your configured model works!")
                print(f"🤖 Response: {content}")
            else:
                print(f"❌ Configured model failed: {response.text}")
                
    except Exception as e:
        print(f"❌ Configured model error: {e}")
    
    print("\n🔧 TROUBLESHOOTING SUGGESTIONS:")
    print("1. Check if your OpenRouter API key is valid at https://openrouter.ai/keys")
    print("2. Try regenerating your API key")
    print("3. Make sure you have credits/balance in your account")
    print("4. Try a different free model")
    print("5. Check OpenRouter status at https://status.openrouter.ai/")

if __name__ == "__main__":
    asyncio.run(debug_openrouter())