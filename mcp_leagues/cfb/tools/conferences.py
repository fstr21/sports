#!/usr/bin/env python3
"""
CFB Conferences Tool - Test college football conferences via deployed MCP server
"""

import asyncio
import json
import httpx

# Test the conferences endpoint via MCP server
async def test_cfb_conferences_mcp():
    """Test CFB conferences via deployed MCP server"""
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    
    test_cases = [
        {
            "name": "All CFB Conferences",
            "args": {}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\n🏛️ Testing: {test['name']}")
            print("-" * 40)
            
            # Create MCP request
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "getCFBConferences",
                    "arguments": test['args']
                }
            }
            
            try:
                response = await client.post(
                    mcp_url,
                    json=mcp_request,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if "result" in result and "content" in result["result"]:
                        content = result["result"]["content"]
                        print("✅ MCP Success!")
                        
                        # Parse the content
                        for item in content:
                            if item.get("type") == "text":
                                text = item.get("text", "")
                                if text.startswith("## CFB Conferences"):
                                    # This is the markdown summary
                                    lines = text.split('\n')
                                    for line in lines[:3]:
                                        if line.strip():
                                            print(f"   {line}")
                                elif text.startswith("```json"):
                                    # This is the JSON data
                                    try:
                                        json_text = text.replace("```json\n", "").replace("\n```", "")
                                        data = json.loads(json_text)
                                        
                                        if "conferences" in data:
                                            conferences = data["conferences"]
                                            print(f"   📊 Found {len(conferences)} conferences")
                                            
                                            # Group by classification
                                            classifications = {}
                                            for conf in conferences:
                                                classification = conf.get('classification', 'Unknown')
                                                if classification not in classifications:
                                                    classifications[classification] = []
                                                classifications[classification].append(conf)
                                            
                                            print(f"   🏈 Classifications:")
                                            for classification, conf_list in classifications.items():
                                                print(f"      {classification}: {len(conf_list)} conferences")
                                            
                                            # Show major conferences
                                            print(f"   ⭐ Major conferences:")
                                            major_conferences = ["SEC", "Big Ten", "Big 12", "ACC", "Pac-12"]
                                            found_major = []
                                            for conf in conferences:
                                                name = conf.get('name', '')
                                                short_name = conf.get('short_name', '')
                                                if any(major in name or major in short_name for major in major_conferences):
                                                    found_major.append(conf)
                                            
                                            for i, conf in enumerate(found_major[:10]):
                                                name = conf.get('name', 'Unknown')
                                                short_name = conf.get('short_name', '')
                                                abbreviation = conf.get('abbreviation', '')
                                                classification = conf.get('classification', 'Unknown')
                                                display_name = short_name if short_name else name
                                                print(f"      {i+1}. {display_name} ({abbreviation}, {classification})")
                                    
                                    except json.JSONDecodeError:
                                        print(f"   📄 Raw response: {text[:200]}...")
                    else:
                        print(f"⚠️  Unexpected response format: {result}")
                        
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")

async def save_results_to_json():
    """Run tests and save results to JSON file"""
    from datetime import datetime
    import os
    
    print("🏛️ CFB Conferences MCP Test - Saving Results to JSON")
    print("=" * 60)
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    results = {
        "test_name": "CFB Conferences MCP Test",
        "timestamp": datetime.now().isoformat(),
        "server_url": mcp_url,
        "tests": []
    }
    
    test_cases = [
        {
            "name": "All CFB Conferences",
            "args": {}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\n🏛️ Testing: {test['name']}")
            
            test_result = {
                "name": test['name'],
                "tool": "getCFBConferences",
                "args": test['args'],
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
            
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "getCFBConferences",
                    "arguments": test['args']
                }
            }
            
            try:
                response = await client.post(
                    mcp_url,
                    json=mcp_request,
                    headers={"Content-Type": "application/json"}
                )
                
                test_result["http_status"] = response.status_code
                
                if response.status_code == 200:
                    result = response.json()
                    test_result["mcp_response"] = result
                    
                    if "result" in result and "content" in result["result"]:
                        test_result["success"] = True
                        
                        # Extract data from JSON content
                        for item in result["result"]["content"]:
                            if item.get("type") == "text" and item.get("text", "").startswith("```json"):
                                try:
                                    json_text = item["text"].replace("```json\n", "").replace("\n```", "")
                                    data = json.loads(json_text)
                                    test_result["extracted_data"] = data
                                    
                                    # Add summary stats
                                    if "conferences" in data:
                                        conferences = data["conferences"]
                                        
                                        # Group by classification
                                        classifications = {}
                                        for conf in conferences:
                                            classification = conf.get('classification', 'Unknown')
                                            if classification not in classifications:
                                                classifications[classification] = 0
                                            classifications[classification] += 1
                                        
                                        test_result["summary"] = {
                                            "conferences_count": len(conferences),
                                            "classifications": classifications,
                                            "sample_conferences": conferences[:10]
                                        }
                                except json.JSONDecodeError:
                                    test_result["json_parse_error"] = "Failed to parse JSON from response"
                        
                        print(f"   ✅ Success!")
                    else:
                        test_result["error"] = "Unexpected MCP response format"
                        print(f"   ❌ Unexpected response format")
                else:
                    test_result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                    print(f"   ❌ HTTP Error: {response.status_code}")
                    
            except Exception as e:
                test_result["error"] = str(e)
                print(f"   ❌ Exception: {e}")
            
            results["tests"].append(test_result)
    
    # Save to JSON file
    output_file = "conferences.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"📊 Total tests: {len(results['tests'])}")
    successful_tests = sum(1 for test in results['tests'] if test['success'])
    print(f"✅ Successful: {successful_tests}/{len(results['tests'])}")
    
    return results

if __name__ == "__main__":
    # Run the original test for console output
    asyncio.run(test_cfb_conferences_mcp())
    
    print("\n" + "="*60)
    print("💾 SAVING RESULTS TO JSON...")
    print("="*60)
    
    # Run and save results
    asyncio.run(save_results_to_json())