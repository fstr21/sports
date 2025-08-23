#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Custom Chronulus MCP Server deployed on Railway
Tests the live deployment at customchronpredictormcp-production.up.railway.app
"""

import asyncio
import json
import httpx
import sys
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

# Railway deployment URLs
RAILWAY_BASE_URL = "https://customchronpredictormcp-production.up.railway.app"
MCP_URL = f"{RAILWAY_BASE_URL}/mcp"
HEALTH_URL = f"{RAILWAY_BASE_URL}/health"

async def test_railway_health():
    """Test Railway deployment health endpoint"""
    print("Testing Railway Health Endpoint...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(HEALTH_URL, timeout=30.0)
            print(f"Status: {response.status_code}")
            result = response.json()
            
            print(f"Service: {result.get('service', 'unknown')}")
            print(f"Status: {result.get('status', 'unknown')}")
            print(f"Model: {result.get('model', 'unknown')}")
            print(f"Timestamp: {result.get('timestamp', 'unknown')}")
            
            return response.status_code == 200 and result.get('status') == 'healthy'
        except Exception as e:
            print(f"❌ Railway health check failed: {e}")
            return False

async def test_railway_tools_list():
    """Test MCP tools list on Railway"""
    print("\nTesting Railway Tools List...")
    
    request = {
        "jsonrpc": "2.0",
        "method": "tools/list", 
        "id": 1
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(MCP_URL, json=request, timeout=30.0)
            result = response.json()
            
            print(f"Status: {response.status_code}")
            tools = result.get('result', {}).get('tools', [])
            print(f"Tools available: {len(tools)}")
            
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
            
            return response.status_code == 200 and len(tools) > 0
        except Exception as e:
            print(f"❌ Railway tools list failed: {e}")
            return False

async def test_railway_sample_analysis():
    """Test sample analysis on Railway deployment"""
    print("\nTesting Railway Sample Analysis...")
    
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "testCustomChronulus",
            "arguments": {
                "expert_count": 3  # Use 3 experts for good test
            }
        },
        "id": 2
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("⏳ Running Railway sample test (may take 60-90 seconds)...")
            response = await client.post(MCP_URL, json=request, timeout=180.0)
            
            if response.status_code != 200:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
            result = response.json()
            
            if 'result' in result and result['result']['content']:
                content = json.loads(result['result']['content'][0]['text'])
                
                print(f"✅ Analysis Status: {content.get('status', 'unknown')}")
                
                if content.get('status') == 'success':
                    analysis = content.get('analysis', {})
                    print(f"Red Sox Win Probability: {analysis.get('away_team_win_probability', 0):.1%}")
                    print(f"Yankees Win Probability: {analysis.get('home_team_win_probability', 0):.1%}")
                    print(f"Expert Count: {analysis.get('expert_count', 0)}")
                    print(f"Analysis Depth: {analysis.get('analysis_depth', 'unknown')}")
                    print(f"Cost Estimate: {analysis.get('cost_estimate', 'unknown')}")
                    print(f"Recommendation: {analysis.get('betting_recommendation', 'unknown')}")
                    print(f"Model Used: {analysis.get('model_used', 'unknown')}")
                    
                    # Show brief excerpt of expert analysis
                    expert_text = analysis.get('expert_analysis', '')
                    if expert_text:
                        print(f"\nExpert Analysis Preview:")
                        print(f"   {expert_text[:200]}..." if len(expert_text) > 200 else f"   {expert_text}")
                    
                    return True
                else:
                    print(f"❌ Analysis failed: {content.get('error', 'unknown error')}")
                    return False
            else:
                print(f"❌ Invalid response format: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Railway sample test failed: {e}")
            return False

async def test_railway_custom_game():
    """Test custom game analysis on Railway"""
    print("\nTesting Railway Custom Game Analysis...")
    
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "getCustomChronulusAnalysis",
            "arguments": {
                "game_data": {
                    "home_team": "Los Angeles Dodgers (playoff contenders, strong at home)",
                    "away_team": "San Francisco Giants (division rivals, road underdogs)",
                    "venue": "Dodger Stadium (pitcher-friendly, Dodgers advantage)",
                    "game_date": "August 23, 2025",
                    "home_record": "88-52 (.629 win percentage)",
                    "away_record": "75-65 (.536 win percentage)", 
                    "home_moneyline": -165,
                    "away_moneyline": 145,
                    "additional_context": "NL West division rivals, late season with playoff implications. Dodgers heavily favored at home."
                },
                "expert_count": 4,
                "analysis_depth": "comprehensive"
            }
        },
        "id": 3
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("⏳ Running comprehensive 4-expert analysis (may take 2-3 minutes)...")
            response = await client.post(MCP_URL, json=request, timeout=300.0)
            
            if response.status_code != 200:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
            result = response.json()
            
            if 'result' in result and result['result']['content']:
                content = json.loads(result['result']['content'][0]['text'])
                
                print(f"✅ Custom Analysis Status: {content.get('status', 'unknown')}")
                
                if content.get('status') == 'success':
                    analysis = content.get('analysis', {})
                    
                    # Display comprehensive results
                    print(f"\nCOMPREHENSIVE ANALYSIS RESULTS:")
                    print(f"   Giants Win Probability: {analysis.get('away_team_win_probability', 0):.1%}")
                    print(f"   Dodgers Win Probability: {analysis.get('home_team_win_probability', 0):.1%}")
                    print(f"   Expert Panel Size: {analysis.get('expert_count', 0)}")
                    print(f"   Analysis Quality: {analysis.get('analysis_depth', 'unknown')}")
                    
                    # Market analysis
                    market_edge = analysis.get('market_edge', 0)
                    print(f"\nBETTING ANALYSIS:")
                    print(f"   Market Edge: {market_edge:+.2%}")
                    print(f"   Recommendation: {analysis.get('betting_recommendation', 'unknown')}")
                    print(f"   Cost Estimate: {analysis.get('cost_estimate', 'unknown')}")
                    
                    # Beta distribution parameters
                    beta_params = analysis.get('beta_params', {})
                    print(f"\nSTATISTICAL PARAMETERS:")
                    print(f"   Beta α: {beta_params.get('alpha', 0):.2f}")
                    print(f"   Beta β: {beta_params.get('beta', 0):.2f}")
                    print(f"   Beta Mean: {beta_params.get('mean', 0):.3f}")
                    print(f"   Beta Variance: {beta_params.get('variance', 0):.5f}")
                    
                    return True
                else:
                    print(f"❌ Custom analysis failed: {content.get('error', 'unknown error')}")
                    return False
            else:
                print(f"❌ Invalid response format: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Railway custom analysis failed: {e}")
            return False

async def test_railway_health_check():
    """Test Railway health monitoring"""
    print("\nTesting Railway Health Monitoring...")
    
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "getCustomChronulusHealth",
            "arguments": {}
        },
        "id": 4
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(MCP_URL, json=request, timeout=30.0)
            result = response.json()
            
            if 'result' in result and result['result']['content']:
                content = json.loads(result['result']['content'][0]['text'])
                
                print(f"Health Status: {content.get('status', 'unknown')}")
                print(f"OpenRouter Configured: {content.get('openrouter_configured', False)}")
                print(f"Model: {content.get('model', 'unknown')}")
                print(f"Timestamp: {content.get('timestamp', 'unknown')}")
                
                return content.get('status') == 'healthy'
            else:
                print(f"❌ Health check failed: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Railway health monitoring failed: {e}")
            return False

async def main():
    """Run comprehensive Railway deployment tests"""
    print("CUSTOM CHRONULUS RAILWAY DEPLOYMENT TESTING")
    print("=" * 60)
    print(f"Testing: {RAILWAY_BASE_URL}")
    print(f"MCP Endpoint: {MCP_URL}")
    print(f"Health Endpoint: {HEALTH_URL}")
    print()
    
    tests = [
        ("Railway Health Check", test_railway_health),
        ("MCP Tools List", test_railway_tools_list),
        ("Service Health Monitoring", test_railway_health_check),
        ("Sample Analysis Test", test_railway_sample_analysis),
        ("Custom Game Analysis", test_railway_custom_game)
    ]
    
    results = {}
    start_time = datetime.now()
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        test_start = datetime.now()
        
        try:
            results[test_name] = await test_func()
            test_duration = (datetime.now() - test_start).total_seconds()
            print(f"Test completed in {test_duration:.1f}s")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
        
        if test_name != list(tests)[-1][0]:  # Don't sleep after last test
            await asyncio.sleep(3)  # Brief pause between tests
    
    total_duration = (datetime.now() - start_time).total_seconds()
    
    print(f"\n{'='*60}")
    print("RAILWAY DEPLOYMENT TEST RESULTS")
    print("-" * 40)
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall Results:")
    print(f"   Tests Passed: {passed}/{len(tests)}")
    print(f"   Success Rate: {(passed/len(tests))*100:.1f}%")
    print(f"   Total Duration: {total_duration:.1f}s")
    
    if passed == len(tests):
        print(f"\nDEPLOYMENT SUCCESS!")
        print(f"Custom Chronulus MCP is fully operational on Railway")
        print(f"All features working: Health, Tools, Analysis, Monitoring")
        print(f"Ready for production integration with Discord bot")
        print(f"Providing 90% cost savings vs real Chronulus")
    elif passed >= len(tests) - 1:
        print(f"\nDEPLOYMENT MOSTLY SUCCESSFUL")
        print(f"Core functionality working")
        print(f"Minor issues detected - check failed tests")
    else:
        print(f"\nDEPLOYMENT ISSUES DETECTED")
        print(f"Multiple test failures - check Railway logs")
        print(f"Verify environment variables and deployment")

if __name__ == "__main__":
    asyncio.run(main())