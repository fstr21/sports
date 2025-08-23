#!/usr/bin/env python3
"""
Simple test script for Railway deployment - no unicode issues
"""

import asyncio
import json
import httpx
from datetime import datetime

RAILWAY_BASE_URL = "https://customchronpredictormcp-production.up.railway.app"
MCP_URL = f"{RAILWAY_BASE_URL}/mcp"
HEALTH_URL = f"{RAILWAY_BASE_URL}/health"

async def test_health():
    """Test health endpoint"""
    print("Testing Railway Health...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(HEALTH_URL, timeout=15.0)
            result = response.json()
            
            print(f"Status: {response.status_code}")
            print(f"Service: {result.get('service', 'unknown')}")
            print(f"Health: {result.get('status', 'unknown')}")
            print(f"Model: {result.get('model', 'unknown')}")
            
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False

async def test_tools():
    """Test tools list"""
    print("\nTesting Tools List...")
    
    request = {
        "jsonrpc": "2.0",
        "method": "tools/list", 
        "id": 1
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(MCP_URL, json=request, timeout=15.0)
            result = response.json()
            
            tools = result.get('result', {}).get('tools', [])
            print(f"Tools available: {len(tools)}")
            
            for tool in tools:
                print(f"  - {tool['name']}")
            
            return len(tools) > 0
        except Exception as e:
            print(f"Tools test failed: {e}")
            return False

async def test_sample():
    """Test sample analysis"""
    print("\nTesting Sample Analysis...")
    
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "testCustomChronulus",
            "arguments": {
                "expert_count": 2
            }
        },
        "id": 2
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("Running 2-expert analysis (60-90 seconds)...")
            response = await client.post(MCP_URL, json=request, timeout=120.0)
            
            if response.status_code != 200:
                print(f"HTTP Error: {response.status_code}")
                return False
                
            result = response.json()
            
            if 'result' in result:
                content = json.loads(result['result']['content'][0]['text'])
                
                print(f"Status: {content.get('status', 'unknown')}")
                
                if content.get('status') == 'success':
                    analysis = content.get('analysis', {})
                    print(f"Red Sox Win Prob: {analysis.get('away_team_win_probability', 0):.1%}")
                    print(f"Yankees Win Prob: {analysis.get('home_team_win_probability', 0):.1%}")
                    print(f"Expert Count: {analysis.get('expert_count', 0)}")
                    print(f"Cost: {analysis.get('cost_estimate', 'unknown')}")
                    print(f"Recommendation: {analysis.get('betting_recommendation', 'unknown')}")
                    return True
                else:
                    print(f"Analysis failed: {content.get('error', 'unknown')}")
                    return False
            else:
                print(f"Invalid response: {result}")
                return False
                
        except Exception as e:
            print(f"Sample test failed: {e}")
            return False

async def main():
    """Run tests"""
    print("TESTING RAILWAY DEPLOYMENT")
    print("=" * 40)
    print(f"URL: {RAILWAY_BASE_URL}")
    print()
    
    tests = [
        ("Health Check", test_health),
        ("Tools List", test_tools),
        ("Sample Analysis", test_sample)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 20)
        
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"Test failed: {e}")
            results[test_name] = False
        
        await asyncio.sleep(2)
    
    print(f"\n{'='*40}")
    print("RESULTS:")
    
    passed = 0
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("\nSUCCESS! Railway deployment is working.")
    else:
        print(f"\nIssues detected. Check failed tests.")

if __name__ == "__main__":
    asyncio.run(main())