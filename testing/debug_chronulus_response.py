#!/usr/bin/env python3
"""
Debug Custom Chronulus MCP response format
"""
import asyncio
import httpx
import json
from datetime import datetime

async def debug_chronulus_response():
    """Debug what Chronulus actually returns"""
    print("Debugging Custom Chronulus MCP Response...")
    print("=" * 60)
    
    chronulus_url = "https://customchronpredictormcp-production.up.railway.app/mcp"
    
    # Test the same call that the Discord bot makes
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getCustomChronulusAnalysis",
            "arguments": {
                "home_team": "Seattle Mariners",
                "away_team": "Athletics",
                "expert_count": 3,
                "analysis_depth": "standard"
            }
        }
    }
    
    try:
        print("Making Chronulus analysis request...")
        print(f"URL: {chronulus_url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print()
        
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(chronulus_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            print("RAW RESPONSE:")
            print("=" * 40)
            print(json.dumps(result, indent=2))
            print()
            
            if "result" not in result:
                print("ERROR: No 'result' key in response")
                if "error" in result:
                    print(f"Error: {result['error']}")
                return
            
            mcp_result = result["result"]
            print("MCP RESULT STRUCTURE:")
            print("=" * 30)
            print(f"Keys in result: {list(mcp_result.keys())}")
            
            if "content" in mcp_result:
                content = mcp_result["content"]
                print(f"Content type: {type(content)}")
                
                if isinstance(content, list) and content:
                    first_content = content[0]
                    print(f"First content keys: {list(first_content.keys()) if isinstance(first_content, dict) else 'Not a dict'}")
                    
                    if "text" in first_content:
                        analysis_text = first_content["text"]
                        print(f"Text length: {len(analysis_text)}")
                        print("Text preview (first 300 chars):")
                        print("-" * 30)
                        print(analysis_text[:300])
                        print("-" * 30)
                        
                        # Try to parse as JSON
                        try:
                            analysis_data = json.loads(analysis_text)
                            print("\nSUCCESS: Text is valid JSON")
                            print("JSON Keys:", list(analysis_data.keys()))
                            
                            # Check for expected fields
                            expected_fields = [
                                "win_probability", "expert_analyses", "consensus_summary", 
                                "betting_recommendation", "session_id", "analysis"
                            ]
                            
                            print("\nField Analysis:")
                            for field in expected_fields:
                                if field in analysis_data:
                                    value = analysis_data[field]
                                    if isinstance(value, list):
                                        print(f"✓ {field}: List with {len(value)} items")
                                    elif isinstance(value, dict):
                                        print(f"✓ {field}: Dict with keys {list(value.keys())}")
                                    else:
                                        print(f"✓ {field}: {type(value).__name__} = {str(value)[:50]}...")
                                else:
                                    print(f"✗ {field}: Missing")
                            
                            # Check if 'analysis' field contains nested data
                            if "analysis" in analysis_data:
                                nested_analysis = analysis_data["analysis"]
                                if isinstance(nested_analysis, dict):
                                    print(f"\nNested 'analysis' field has keys: {list(nested_analysis.keys())}")
                        
                        except json.JSONDecodeError as e:
                            print(f"\nWARNING: Text is not valid JSON: {e}")
                            print("This might be plain text analysis")
            
            print("\nCOMPARISON WITH DISCORD BOT PARSING:")
            print("=" * 40)
            
            # Simulate what Discord bot does
            if "content" in mcp_result and isinstance(mcp_result["content"], list):
                if mcp_result["content"] and "text" in mcp_result["content"][0]:
                    analysis_text = mcp_result["content"][0]["text"]
                    
                    try:
                        analysis_data = json.loads(analysis_text)
                        
                        # What Discord bot tries to extract
                        nested_analysis = analysis_data.get("analysis", {})
                        
                        if isinstance(nested_analysis, dict):
                            win_probability = nested_analysis.get("win_probability", 0)
                            expert_analyses = nested_analysis.get("expert_analyses", [])
                            consensus = nested_analysis.get("consensus_summary", nested_analysis.get("summary", "Analysis completed"))
                            recommendation = nested_analysis.get("betting_recommendation", nested_analysis.get("recommendation", "No recommendation"))
                            
                            print(f"Extracted win_probability: {win_probability}")
                            print(f"Extracted expert_analyses: {len(expert_analyses)} experts")
                            print(f"Extracted consensus: {consensus}")
                            print(f"Extracted recommendation: {recommendation}")
                        else:
                            print(f"'analysis' field is not a dict: {type(nested_analysis)}")
                            print(f"Content: {str(nested_analysis)[:100]}...")
                        
                    except json.JSONDecodeError:
                        print("Could not parse as JSON - this explains the Discord bot issue!")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_chronulus_response())