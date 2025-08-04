#!/usr/bin/env python3
"""
Direct test of ESPN and OpenRouter APIs without MCP server
"""

import asyncio
import json
import os
from pathlib import Path
import httpx

# Load environment
def load_env():
    env_path = Path("C:/Users/fstr2/Desktop/sports/.env.local")
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k] = v
        print(f"✅ Loaded environment from {env_path}")
    else:
        print(f"⚠️ Environment file not found: {env_path}")

load_env()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/horizon-beta")
ESPN_SITE_BASE = "https://site.api.espn.com"

async def test_espn_api():
    """Test ESPN API directly"""
    print("🏀 Testing ESPN API...")
    
    headers = {
        "User-Agent": "Smart-WNBA-MCP/1.0",
        "Accept": "application/json, text/plain, */*",
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=15.0) as client:
        try:
            # Test scoreboard
            print("  📊 Testing scoreboard...")
            url = f"{ESPN_SITE_BASE}/apis/site/v2/sports/basketball/wnba/scoreboard"
            response = await client.get(url)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                events = data.get("events", [])
                print(f"  Found {len(events)} games")
                if events:
                    print(f"  Sample game: {events[0].get('name', 'Unknown')}")
            else:
                print(f"  Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ ESPN API Error: {e}")

async def test_openrouter_api():
    """Test OpenRouter API directly"""
    print("🤖 Testing OpenRouter API...")
    
    if not OPENROUTER_API_KEY:
        print("  ❌ No OpenRouter API key found")
        return
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "You are a test assistant. Respond with 'Hello World' only."},
            {"role": "user", "content": "Say hello"},
        ],
        "max_tokens": 10,
        "temperature": 0.1,
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        try:
            print(f"  🎯 Testing model: {OPENROUTER_MODEL}")
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions", 
                json=payload
            )
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"  Response: {content}")
            else:
                print(f"  Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ OpenRouter API Error: {e}")

async def test_combined_flow():
    """Test the combined flow like the MCP server would do"""
    print("🔄 Testing combined flow...")
    
    # Simple query parsing without OpenRouter
    query = "Show me WNBA scores"
    print(f"  Query: {query}")
    
    # Direct ESPN call
    headers = {
        "User-Agent": "Smart-WNBA-MCP/1.0",
        "Accept": "application/json, text/plain, */*",
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=15.0) as client:
        try:
            url = f"{ESPN_SITE_BASE}/apis/site/v2/sports/basketball/wnba/scoreboard"
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                events = data.get("events", [])
                
                if not events:
                    print("  📭 No WNBA games found")
                else:
                    print("  🏀 WNBA Scoreboard:")
                    for i, event in enumerate(events[:3]):  # Show first 3
                        name = event.get("name", "Unknown matchup")
                        status = event.get("status", {}).get("type", {}).get("description", "Unknown")
                        print(f"    {i+1}. {name} - {status}")
            else:
                print(f"  ❌ ESPN Error: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Combined flow error: {e}")

async def main():
    print("🧪 Starting Direct API Tests...")
    print("=" * 50)
    
    await test_espn_api()
    print()
    
    await test_openrouter_api()
    print()
    
    await test_combined_flow()
    print()
    
    print("✅ Tests completed!")

if __name__ == "__main__":
    asyncio.run(main())