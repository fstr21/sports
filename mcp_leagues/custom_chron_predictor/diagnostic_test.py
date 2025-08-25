#!/usr/bin/env python3
"""
Diagnostic test to see exactly what the MCP server is returning
"""
import asyncio
import json
import httpx

async def diagnostic_test():
    """Detailed diagnostic of the MCP server response"""
    print("🔍 DIAGNOSTIC TEST - Custom Chronulus MCP Server")
    print("=" * 60)
    
    mcp_url = "https://customchronpredictormcp-production.up.railway.app/mcp"
    
    # Test 1: Simple tools list
    print("📋 Test 1: Tools List")
    tools_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(mcp_url, json=tools_request)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Tools available: {len(result.get('result', {}).get('tools', []))}")
                for tool in result.get('result', {}).get('tools', []):
                    print(f"  - {tool['name']}")
            else:
                print(f"Error: {response.text}")
    except Exception as e:
        print(f"Tools list failed: {e}")
    
    print("\n" + "-" * 60)
    
    # Test 2: Simple test call
    print("📊 Test 2: Test Custom Chronulus")
    test_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 2,
        "params": {
            "name": "testCustomChronulus",
            "arguments": {
                "expert_count": 1  # Start simple
            }
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(mcp_url, json=test_request)
            print(f"Status: {response.status_code}")
            print(f"Response length: {len(response.text)} chars")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response structure: {list(result.keys())}")
                
                if "result" in result and result["result"] and "content" in result["result"]:
                    content = result["result"]["content"][0]["text"]
                    print(f"Content length: {len(content)} chars")
                    print(f"Content preview: {content[:200]}...")
                    
                    try:
                        analysis_data = json.loads(content)
                        print(f"Analysis keys: {list(analysis_data.keys())}")
                        if "analysis" in analysis_data:
                            analysis = analysis_data["analysis"]
                            print(f"Expert count: {analysis.get('expert_count', 'N/A')}")
                            print(f"Analysis text length: {len(analysis.get('expert_analysis', ''))}")
                            print(f"Status: {analysis_data.get('status', 'N/A')}")
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                        print(f"Raw content: {content}")
                else:
                    print(f"Unexpected response format: {result}")
            else:
                print(f"Error response: {response.text}")
                
    except Exception as e:
        print(f"Test call failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "-" * 60)
    
    # Test 3: Full analysis request
    print("📈 Test 3: Full Analysis Request")
    full_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 3,
        "params": {
            "name": "getCustomChronulusAnalysis",
            "arguments": {
                "game_data": {
                    "home_team": "New York Yankees",
                    "away_team": "Boston Red Sox",
                    "venue": "Yankee Stadium",
                    "game_date": "August 25, 2025"
                },
                "expert_count": 1,  # Start with 1 to see if basic functionality works
                "analysis_depth": "standard"
            }
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(mcp_url, json=full_request)
            print(f"Status: {response.status_code}")
            print(f"Response length: {len(response.text)} chars")
            
            if response.status_code == 200:
                result = response.json()
                
                if "result" in result and result["result"] and "content" in result["result"]:
                    content = result["result"]["content"][0]["text"]
                    print(f"Content length: {len(content)} chars")
                    
                    try:
                        analysis_data = json.loads(content)
                        print(f"Analysis status: {analysis_data.get('status', 'N/A')}")
                        
                        if "error" in analysis_data:
                            print(f"❌ Error in analysis: {analysis_data['error']}")
                        elif "analysis" in analysis_data:
                            analysis = analysis_data["analysis"]
                            print(f"✅ Expert count: {analysis.get('expert_count', 0)}")
                            print(f"✅ Probabilities: Away {analysis.get('away_team_win_probability', 0):.1%}, Home {analysis.get('home_team_win_probability', 0):.1%}")
                            print(f"✅ Recommendation: {analysis.get('betting_recommendation', 'N/A')}")
                            expert_text = analysis.get('expert_analysis', '')
                            print(f"✅ Analysis length: {len(expert_text)} chars")
                            if expert_text:
                                print(f"Analysis preview: {expert_text[:300]}...")
                        else:
                            print(f"Unexpected analysis structure: {list(analysis_data.keys())}")
                            
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                        print(f"Raw content: {content[:500]}...")
                else:
                    print(f"No content in response: {result}")
            else:
                print(f"HTTP Error: {response.text}")
                
    except Exception as e:
        print(f"Full analysis failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main diagnostic function"""
    await diagnostic_test()

if __name__ == "__main__":
    asyncio.run(main())