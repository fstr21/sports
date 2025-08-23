#!/usr/bin/env python3
"""
Test Custom Chronulus MCP integration
"""
import asyncio
import httpx
import json
from datetime import datetime

async def test_chronulus_mcp():
    """Test Custom Chronulus MCP server"""
    print("Testing Custom Chronulus MCP Integration...")
    
    chronulus_url = "https://customchronpredictormcp-production.up.railway.app/mcp"
    
    # Test 1: Health check
    health_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getCustomChronulusHealth",
            "arguments": {}
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("1. Testing health check...")
            response = await client.post(chronulus_url, json=health_payload)
            response.raise_for_status()
            result = response.json()
            
            if "result" in result:
                print("SUCCESS: Chronulus health check passed")
                print(f"Health result: {result['result']}")
            else:
                print(f"WARNING: Unexpected health response: {result}")
        
        # Test 2: Sample analysis
        print("\n2. Testing sample analysis...")
        test_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 2,
            "params": {
                "name": "testCustomChronulus",
                "arguments": {}
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(chronulus_url, json=test_payload)
            response.raise_for_status()
            result = response.json()
            
            if "result" in result:
                print("SUCCESS: Chronulus test analysis completed")
                # Parse the result
                if "content" in result["result"]:
                    content = result["result"]["content"]
                    if isinstance(content, list) and content:
                        analysis_text = content[0].get("text", "")
                        if analysis_text:
                            try:
                                analysis_data = json.loads(analysis_text)
                                print(f"Win probability: {analysis_data.get('win_probability', 'N/A')}%")
                                print(f"Expert count: {len(analysis_data.get('expert_analyses', []))}")
                                print(f"Recommendation: {analysis_data.get('betting_recommendation', 'N/A')}")
                            except json.JSONDecodeError:
                                print("Analysis text is not JSON format")
                                print(f"Raw text preview: {analysis_text[:200]}...")
                else:
                    print(f"Test result: {result['result']}")
            else:
                print(f"ERROR: Test failed: {result}")
        
        # Test 3: Real game analysis
        print("\n3. Testing real game analysis...")
        real_game_payload = {
            "jsonrpc": "2.0", 
            "method": "tools/call",
            "id": 3,
            "params": {
                "name": "getCustomChronulusAnalysis",
                "arguments": {
                    "home_team": "New York Yankees",
                    "away_team": "Boston Red Sox", 
                    "expert_count": 3,
                    "analysis_depth": "standard"
                }
            }
        }
        
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(chronulus_url, json=real_game_payload)
            response.raise_for_status()
            result = response.json()
            
            if "result" in result:
                print("SUCCESS: Real game analysis completed")
                if "content" in result["result"]:
                    content = result["result"]["content"]
                    if isinstance(content, list) and content:
                        analysis_text = content[0].get("text", "")
                        if analysis_text:
                            try:
                                analysis_data = json.loads(analysis_text)
                                print(f"Yankees win probability: {analysis_data.get('win_probability', 'N/A')}%")
                                print(f"Expert analyses: {len(analysis_data.get('expert_analyses', []))}")
                                print(f"Consensus: {analysis_data.get('consensus_summary', 'N/A')}")
                                print(f"Recommendation: {analysis_data.get('betting_recommendation', 'N/A')}")
                            except json.JSONDecodeError:
                                print("Analysis is not JSON - likely text format")
                                print(f"Text preview: {analysis_text[:300]}...")
            else:
                print(f"ERROR: Real game analysis failed: {result}")
                
    except Exception as e:
        print(f"ERROR testing Chronulus: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chronulus_mcp())