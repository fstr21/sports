#!/usr/bin/env python3
"""
Test OpenRouter Discord Bridge
Test the integration between OpenRouter and Discord MCP
"""

import asyncio
import os
import json
from datetime import datetime
from openrouter_discord_bridge import OpenRouterDiscordBridge


async def test_basic_mcp_connection():
    """Test basic MCP server connection"""
    print("Testing Discord MCP connection...")
    
    bridge = OpenRouterDiscordBridge(
        openrouter_api_key="test_key",  # We don't need real key for MCP testing
        discord_mcp_url="https://chatmcp-production.up.railway.app/mcp"
    )
    
    async with bridge:
        # Test reading messages (will show permission error but confirms connection)
        result = await bridge.call_discord_mcp("read-messages", {
            "channel": "mcp-testing",
            "limit": 3
        })
        
        print("MCP Response:", json.dumps(result, indent=2))
        
        # Test if we get channel list in error (proves connection works)
        if "error" in result and "Available channels" in str(result["error"]):
            print("PASS - MCP server connection working - can see channel list")
            return True
        else:
            print("FAIL - Unexpected MCP response")
            return False


async def test_openrouter_connection():
    """Test OpenRouter API connection"""
    print("\nTesting OpenRouter connection...")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your_openrouter_api_key_here":
        print("FAIL - No OpenRouter API key found. Set OPENROUTER_API_KEY environment variable.")
        return False
    
    bridge = OpenRouterDiscordBridge(
        openrouter_api_key=api_key,
        default_model="anthropic/claude-3.5-haiku"  # Cheaper model for testing
    )
    
    async with bridge:
        # Test simple AI call
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Respond with exactly 'Hello World' and nothing else."},
            {"role": "user", "content": "Say hello"}
        ]
        
        response = await bridge.call_openrouter(messages, max_tokens=10)
        print(f"AI Response: '{response}'")
        
        if "Hello World" in response or "hello" in response.lower():
            print("✅ OpenRouter API connection working")
            return True
        else:
            print("❌ Unexpected OpenRouter response")
            return False


async def test_sports_betting_prompt():
    """Test sports betting specific AI responses"""
    print("\n🏈 Testing sports betting AI responses...")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your_openrouter_api_key_here":
        print("❌ Skipping - no OpenRouter API key")
        return False
    
    bridge = OpenRouterDiscordBridge(
        openrouter_api_key=api_key,
        default_model="anthropic/claude-3.5-haiku"
    )
    
    async with bridge:
        # Test sports betting analysis
        game_info = {
            "teams": "Chiefs vs Ravens", 
            "spread": "Chiefs -2.5",
            "total": "O/U 47.5",
            "moneyline": "Chiefs -110, Ravens +105"
        }
        
        messages = [
            {
                "role": "system", 
                "content": "You are a sports betting analyst. Provide brief, actionable insights."
            },
            {
                "role": "user",
                "content": f"Quick analysis of this game: {json.dumps(game_info)}"
            }
        ]
        
        response = await bridge.call_openrouter(messages, max_tokens=150)
        print(f"Sports Analysis: {response}")
        
        if any(word in response.lower() for word in ["chiefs", "ravens", "spread", "game"]):
            print("✅ Sports betting AI working correctly")
            return True
        else:
            print("❌ AI not providing sports-relevant response")
            return False


async def test_full_integration_simulation():
    """Simulate full integration without actually sending to Discord"""
    print("\n🔄 Testing full integration flow (simulation)...")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your_openrouter_api_key_here":
        print("❌ Skipping - no OpenRouter API key")
        return False
    
    bridge = OpenRouterDiscordBridge(
        openrouter_api_key=api_key,
        default_model="anthropic/claude-3.5-haiku"
    )
    
    async with bridge:
        # Simulate a betting alert workflow
        print("📊 Generating automated betting alert...")
        
        game_info = {
            "matchup": "Lakers @ Warriors",
            "date": "Tonight 10:30 PM ET",
            "venue": "Chase Center"
        }
        
        odds_data = {
            "spread": {"Lakers": "+3.5", "Warriors": "-3.5"},
            "moneyline": {"Lakers": "+145", "Warriors": "-165"},
            "total": "O/U 225.5"
        }
        
        # Generate AI alert (but don't send to Discord)
        prompt = f"""
        Create a concise Discord betting alert for:
        Game: {json.dumps(game_info)}
        Odds: {json.dumps(odds_data)}
        
        Format: Emoji + team + pick + brief reason (under 100 chars)
        """
        
        messages = [
            {"role": "system", "content": "You are a sports betting bot. Create short, engaging Discord alerts with emojis."},
            {"role": "user", "content": prompt}
        ]
        
        alert = await bridge.call_openrouter(messages, max_tokens=100)
        print(f"🚨 Generated Alert: {alert}")
        
        # Simulate Discord send (without actually sending)
        print(f"📱 Would send to Discord channel: #aggregated-picks")
        print(f"📱 Message: {alert}")
        
        print("✅ Full integration simulation complete")
        return True


async def run_all_tests():
    """Run all tests"""
    print("OpenRouter Discord Bridge - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Discord MCP Connection", test_basic_mcp_connection),
        ("OpenRouter API", test_openrouter_connection), 
        ("Sports Betting AI", test_sports_betting_prompt),
        ("Full Integration Simulation", test_full_integration_simulation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📋 TEST RESULTS:")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    print(f"\n🎯 Overall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 All systems ready for production!")
    else:
        print("⚠️  Some components need attention before production use")


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()  # This will load .env if it exists
    
    # Run tests
    asyncio.run(run_all_tests())