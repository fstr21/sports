#!/usr/bin/env python3
"""
CFB Teams Tool - Test college football teams via deployed MCP server
"""

import asyncio
import json
import httpx

# Test the teams endpoint via MCP server
async def test_cfb_teams_mcp():
    """Test CFB teams via deployed MCP server"""
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    
    test_cases = [
        {
            "name": "All Big 12 Teams",
            "args": {"conference": "Big 12"}
        },
        {
            "name": "All SEC Teams",
            "args": {"conference": "SEC"}
        },
        {
            "name": "All Teams 2024",
            "args": {"year": 2024}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\n🏫 Testing: {test['name']}")
            print("-" * 40)
            
            # Create MCP request
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "getCFBTeams",
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
                                if text.startswith("## CFB Teams"):
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
                                        
                                        if "teams" in data:
                                            teams = data["teams"]
                                            print(f"   📊 Found {len(teams)} teams")
                                            
                                            # Group by conference
                                            conferences = {}
                                            for team in teams:
                                                conf = team.get('conference', 'Independent')
                                                if conf not in conferences:
                                                    conferences[conf] = []
                                                conferences[conf].append(team)
                                            
                                            print(f"   🏈 Conferences represented:")
                                            for conf, conf_teams in list(conferences.items())[:5]:
                                                print(f"      {conf}: {len(conf_teams)} teams")
                                            
                                            # Show sample teams
                                            print(f"   ⭐ Sample teams:")
                                            for i, team in enumerate(teams[:5]):
                                                school = team.get('school', 'Unknown')
                                                mascot = team.get('mascot', 'Unknown')
                                                conference = team.get('conference', 'Independent')
                                                classification = team.get('classification', 'Unknown')
                                                print(f"      {i+1}. {school} {mascot} ({conference}, {classification})")
                                    
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
    
    print("🏫 CFB Teams MCP Test - Saving Results to JSON")
    print("=" * 60)
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    results = {
        "test_name": "CFB Teams MCP Test",
        "timestamp": datetime.now().isoformat(),
        "server_url": mcp_url,
        "tests": []
    }
    
    test_cases = [
        {
            "name": "All Big 12 Teams",
            "args": {"conference": "Big 12"}
        },
        {
            "name": "All SEC Teams",
            "args": {"conference": "SEC"}
        },
        {
            "name": "All Teams 2024",
            "args": {"year": 2024}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\n🏫 Testing: {test['name']}")
            
            test_result = {
                "name": test['name'],
                "tool": "getCFBTeams",
                "args": test['args'],
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
            
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "getCFBTeams",
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
                                    if "teams" in data:
                                        teams = data["teams"]
                                        
                                        # Group by conference
                                        conferences = {}
                                        for team in teams:
                                            conf = team.get('conference', 'Independent')
                                            if conf not in conferences:
                                                conferences[conf] = 0
                                            conferences[conf] += 1
                                        
                                        test_result["summary"] = {
                                            "teams_count": len(teams),
                                            "conferences": conferences,
                                            "sample_teams": teams[:5]
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
    output_file = "teams.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"📊 Total tests: {len(results['tests'])}")
    successful_tests = sum(1 for test in results['tests'] if test['success'])
    print(f"✅ Successful: {successful_tests}/{len(results['tests'])}")
    
    return results

if __name__ == "__main__":
    # Run the original test for console output
    asyncio.run(test_cfb_teams_mcp())
    
    print("\n" + "="*60)
    print("💾 SAVING RESULTS TO JSON...")
    print("="*60)
    
    # Run and save results
    asyncio.run(save_results_to_json())