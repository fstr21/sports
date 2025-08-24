#!/usr/bin/env python3
"""
CFB Plays Tool - Test college football play-by-play data via deployed MCP server
"""

import asyncio
import json
import httpx

# Test the plays endpoint via MCP server
async def test_cfb_plays_mcp():
    """Test CFB plays via deployed MCP server"""
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    
    test_cases = [
        {
            "name": "Kansas State Week 1 2024 Plays",
            "args": {"year": 2024, "week": 1, "team": "Kansas State"}
        },
        {
            "name": "Big 12 Week 1 2024 Plays (Offense)",
            "args": {"year": 2024, "week": 1, "offense": "Kansas State"}
        },
        {
            "name": "Big 12 Week 1 2024 Plays (Defense)",
            "args": {"year": 2024, "week": 1, "defense": "UT Martin"}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\n🏈 Testing: {test['name']}")
            print("-" * 40)
            
            # Create MCP request
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "getCFBPlays",
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
                                if text.startswith("## CFB Plays"):
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
                                        
                                        if "plays" in data:
                                            plays = data["plays"]
                                            print(f"   📊 Found {len(plays)} plays")
                                            
                                            # Analyze play types
                                            play_types = {}
                                            for play in plays:
                                                play_type = play.get('play_type', 'Unknown')
                                                if play_type not in play_types:
                                                    play_types[play_type] = 0
                                                play_types[play_type] += 1
                                            
                                            print(f"   🏈 Play types found:")
                                            for play_type, count in list(play_types.items())[:8]:
                                                print(f"      {play_type}: {count} plays")
                                            
                                            # Show sample plays
                                            print(f"   ⭐ Sample plays:")
                                            for i, play in enumerate(plays[:5]):
                                                offense = play.get('offense', 'Unknown')
                                                defense = play.get('defense', 'Unknown')
                                                period = play.get('period', 'Unknown')
                                                down = play.get('down', 'Unknown')
                                                distance = play.get('distance', 'Unknown')
                                                yard_line = play.get('yard_line', 'Unknown')
                                                yards_gained = play.get('yards_gained', 0)
                                                play_type = play.get('play_type', 'Unknown')
                                                play_text = play.get('play_text', 'No description')
                                                
                                                # Format down and distance
                                                down_dist = f"{down} & {distance}" if down != 'Unknown' and distance != 'Unknown' else "Unknown down"
                                                
                                                print(f"      {i+1}. {offense} vs {defense} (Q{period})")
                                                print(f"         {down_dist} at {yard_line} - {play_type}")
                                                print(f"         Yards: {yards_gained}, Play: {play_text[:60]}{'...' if len(play_text) > 60 else ''}")
                                    
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
    
    print("🏈 CFB Plays MCP Test - Saving Results to JSON")
    print("=" * 60)
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    results = {
        "test_name": "CFB Plays MCP Test",
        "timestamp": datetime.now().isoformat(),
        "server_url": mcp_url,
        "tests": []
    }
    
    test_cases = [
        {
            "name": "Kansas State Week 1 2024 Plays",
            "args": {"year": 2024, "week": 1, "team": "Kansas State"}
        },
        {
            "name": "Big 12 Week 1 2024 Plays (Offense)",
            "args": {"year": 2024, "week": 1, "offense": "Kansas State"}
        },
        {
            "name": "Big 12 Week 1 2024 Plays (Defense)",
            "args": {"year": 2024, "week": 1, "defense": "UT Martin"}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\n🏈 Testing: {test['name']}")
            
            test_result = {
                "name": test['name'],
                "tool": "getCFBPlays",
                "args": test['args'],
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
            
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "getCFBPlays",
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
                                    if "plays" in data:
                                        plays = data["plays"]
                                        
                                        # Analyze play types and outcomes
                                        play_types = {}
                                        total_yards = 0
                                        periods = set()
                                        
                                        for play in plays:
                                            play_type = play.get('play_type', 'Unknown')
                                            if play_type not in play_types:
                                                play_types[play_type] = 0
                                            play_types[play_type] += 1
                                            
                                            yards_gained = play.get('yards_gained', 0)
                                            if isinstance(yards_gained, (int, float)):
                                                total_yards += yards_gained
                                            
                                            period = play.get('period')
                                            if period:
                                                periods.add(period)
                                        
                                        test_result["summary"] = {
                                            "plays_count": len(plays),
                                            "play_types": play_types,
                                            "total_yards": total_yards,
                                            "periods": sorted(list(periods)),
                                            "sample_plays": plays[:5]
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
    output_file = "plays.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"📊 Total tests: {len(results['tests'])}")
    successful_tests = sum(1 for test in results['tests'] if test['success'])
    print(f"✅ Successful: {successful_tests}/{len(results['tests'])}")
    
    return results

if __name__ == "__main__":
    # Run the original test for console output
    asyncio.run(test_cfb_plays_mcp())
    
    print("\n" + "="*60)
    print("💾 SAVING RESULTS TO JSON...")
    print("="*60)
    
    # Run and save results
    asyncio.run(save_results_to_json())