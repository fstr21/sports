#!/usr/bin/env python3
"""
CFB Roster Tool - Test college football roster via deployed MCP server
"""

import asyncio
import json
import httpx

# Test the roster endpoint via MCP server
async def test_cfb_roster_mcp():
    """Test CFB roster via deployed MCP server"""
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    
    test_cases = [
        {
            "name": "Kansas State 2024 Roster",
            "args": {"team": "Kansas State", "year": 2024}
        },
        {
            "name": "Iowa State 2024 Roster", 
            "args": {"team": "Iowa State", "year": 2024}
        },
        {
            "name": "Stanford 2024 Roster",
            "args": {"team": "Stanford", "year": 2024}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\n👥 Testing: {test['name']}")
            print("-" * 40)
            
            # Create MCP request
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "getCFBRoster",
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
                                if text.startswith("## CFB Roster"):
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
                                        
                                        if "players" in data:
                                            players = data["players"]
                                            print(f"   📊 Found {len(players)} players")
                                            
                                            # Group by position
                                            positions = {}
                                            for player in players:
                                                pos = player.get('position', 'Unknown')
                                                if pos not in positions:
                                                    positions[pos] = []
                                                positions[pos].append(player)
                                            
                                            print(f"   📈 Position breakdown:")
                                            for pos, pos_players in sorted(positions.items()):
                                                if pos and pos != 'Unknown':
                                                    print(f"      {pos}: {len(pos_players)} players")
                                            
                                            # Show sample players
                                            print(f"   ⭐ Sample players:")
                                            for i, player in enumerate(players[:5]):
                                                first_name = player.get('first_name', '')
                                                last_name = player.get('last_name', '')
                                                name = f"{first_name} {last_name}".strip()
                                                pos = player.get('position', 'Unknown')
                                                jersey = player.get('jersey', 'N/A')
                                                year = player.get('year', 'Unknown')
                                                print(f"      {i+1}. #{jersey} {name} - {pos} (Year {year})")
                                    
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
    
    print("👥 CFB Roster MCP Test - Saving Results to JSON")
    print("=" * 60)
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    results = {
        "test_name": "CFB Roster MCP Test",
        "timestamp": datetime.now().isoformat(),
        "server_url": mcp_url,
        "tests": []
    }
    
    test_cases = [
        {
            "name": "Kansas State 2024 Roster",
            "args": {"team": "Kansas State", "year": 2024}
        },
        {
            "name": "Iowa State 2024 Roster", 
            "args": {"team": "Iowa State", "year": 2024}
        },
        {
            "name": "Stanford 2024 Roster",
            "args": {"team": "Stanford", "year": 2024}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\n👥 Testing: {test['name']}")
            
            test_result = {
                "name": test['name'],
                "tool": "getCFBRoster",
                "args": test['args'],
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
            
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "getCFBRoster",
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
                                    if "players" in data:
                                        players = data["players"]
                                        
                                        # Group by position
                                        positions = {}
                                        for player in players:
                                            pos = player.get('position', 'Unknown')
                                            if pos not in positions:
                                                positions[pos] = 0
                                            positions[pos] += 1
                                        
                                        test_result["summary"] = {
                                            "players_count": len(players),
                                            "positions": positions,
                                            "sample_players": players[:5]
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
    output_file = "roster.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"📊 Total tests: {len(results['tests'])}")
    successful_tests = sum(1 for test in results['tests'] if test['success'])
    print(f"✅ Successful: {successful_tests}/{len(results['tests'])}")
    
    return results

if __name__ == "__main__":
    # Run the original test for console output
    asyncio.run(test_cfb_roster_mcp())
    
    print("\n" + "="*60)
    print("💾 SAVING RESULTS TO JSON...")
    print("="*60)
    
    # Run and save results
    asyncio.run(save_results_to_json())