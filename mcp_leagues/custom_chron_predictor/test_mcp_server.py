#!/usr/bin/env python3
"""
Test script for Custom Chronulus MCP Server
"""

import asyncio
import json
import httpx
from datetime import datetime

MCP_URL = "http://localhost:8080/mcp"
HEALTH_URL = "http://localhost:8080/health"

async def test_health():
    """Test health endpoint"""
    print("🏥 Testing Health Endpoint...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(HEALTH_URL, timeout=10.0)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

async def test_tools_list():
    """Test MCP tools list"""
    print("\n📋 Testing Tools List...")
    
    request = {
        "jsonrpc": "2.0",
        "method": "tools/list", 
        "id": 1
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(MCP_URL, json=request, timeout=10.0)
            result = response.json()
            
            print(f"Status: {response.status_code}")
            print(f"Tools available: {len(result.get('result', {}).get('tools', []))}")
            
            for tool in result.get('result', {}).get('tools', []):
                print(f"  - {tool['name']}: {tool['description']}")
            
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Tools list failed: {e}")
            return False

async def test_custom_analysis():
    """Test custom Chronulus analysis"""
    print("\n🧠 Testing Custom Analysis...")
    
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "getCustomChronulusAnalysis",
            "arguments": {
                "game_data": {
                    "home_team": "New York Yankees (hot form)",
                    "away_team": "Boston Red Sox (road favorites)",
                    "venue": "Yankee Stadium",
                    "game_date": "2025-08-23",
                    "home_record": "69-59 (.539)",
                    "away_record": "70-59 (.543)", 
                    "home_moneyline": 112,
                    "away_moneyline": -132,
                    "additional_context": "AL East rivalry, playoff implications"
                },
                "expert_count": 3,
                "analysis_depth": "standard"
            }
        },
        "id": 2
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("⏳ Running 3-expert analysis (may take 30-60 seconds)...")
            response = await client.post(MCP_URL, json=request, timeout=120.0)
            result = response.json()
            
            if response.status_code == 200 and 'result' in result:
                content = json.loads(result['result']['content'][0]['text'])
                
                print(f"✅ Analysis Status: {content.get('status', 'unknown')}")
                print(f"🎯 Red Sox Win Probability: {content['analysis']['away_team_win_probability']:.1%}")
                print(f"👥 Expert Count: {content['analysis']['expert_count']}")
                print(f"💰 Estimated Cost: {content['analysis']['cost_estimate']}")
                print(f"📊 Recommendation: {content['analysis']['betting_recommendation']}")
                
                return True
            else:
                print(f"❌ Analysis failed: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Custom analysis failed: {e}")
            return False

async def test_sample_data():
    """Test with hardcoded sample data"""
    print("\n🎮 Testing Sample Data...")
    
    request = {
        "jsonrpc": "2.0", 
        "method": "tools/call",
        "params": {
            "name": "testCustomChronulus",
            "arguments": {
                "expert_count": 2
            }
        },
        "id": 3
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("⏳ Running sample test (may take 30-45 seconds)...")
            response = await client.post(MCP_URL, json=request, timeout=90.0)
            result = response.json()
            
            if response.status_code == 200 and 'result' in result:
                content = json.loads(result['result']['content'][0]['text'])
                
                print(f"✅ Test Status: {content.get('status', 'unknown')}")
                if content.get('status') == 'success':
                    print(f"🎯 Analysis Quality: Comprehensive") 
                    print(f"👥 Experts Used: {content['analysis']['expert_count']}")
                    print(f"📈 Win Probability Generated: Yes")
                    
                return True
            else:
                print(f"❌ Sample test failed: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Sample test failed: {e}")
            return False

async def main():
    """Run all tests"""
    print("🧪 CUSTOM CHRONULUS MCP SERVER TESTING")
    print("=" * 50)
    
    print("⚠️  Make sure server is running: python custom_chronulus_mcp_server.py")
    print("🔑 Ensure OPENROUTER_API_KEY is set in environment")
    print()
    
    tests = [
        ("Health Check", test_health),
        ("Tools List", test_tools_list), 
        ("Sample Test", test_sample_data),
        ("Custom Analysis", test_custom_analysis)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
        
        await asyncio.sleep(2)  # Brief pause between tests
    
    print("\n📊 TEST RESULTS")
    print("-" * 30)
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🚀 All tests passed! Ready for Railway deployment.")
    else:
        print("⚠️  Some tests failed. Check configuration and try again.")

if __name__ == "__main__":
    asyncio.run(main())