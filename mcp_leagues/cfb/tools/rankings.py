#!/usr/bin/env python3
"""
CFB Rankings Tool - Test college football rankings via deployed MCP server
"""

import asyncio
import json
import httpx

# Test the rankings endpoint via MCP server
async def test_cfb_rankings_mcp():
    """Test CFB rankings via deployed MCP server"""
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    
    test_cases = [
        {
            "name": "2024 Final Rankings",
            "args": {"year": 2024, "week": 15}
        },
        {
            "name": "2024 Week 1 Rankings", 
            "args": {"year": 2024, "week": 1}
        },
        {
            "name": "2024 Postseason Rankings",
            "args": {"year": 2024, "season_type": "postseason"}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\n🏆 Testing: {test['name']}")
            print("-" * 40)
            
            # Create MCP request
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "getCFBRankings",
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
                                if text.startswith("## CFB Rankings"):
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
                                        
                                        if "rankings" in data:
                                            rankings = data["rankings"]
                                            print(f"   📊 Found {len(rankings)} ranking periods")
                                            
                                            for ranking_period in rankings:
                                                season = ranking_period.get('season')
                                                week = ranking_period.get('week')
                                                season_type = ranking_period.get('season_type')
                                                polls = ranking_period.get('polls', [])
                                                
                                                print(f"   📅 {season} {season_type} Week {week}")
                                                print(f"      Found {len(polls)} polls")
                                                
                                                for poll in polls[:2]:  # Show first 2 polls
                                                    poll_name = poll.get('poll', 'Unknown')
                                                    ranks = poll.get('ranks', [])
                                                    
                                                    print(f"      🗳️  {poll_name} (Top 5):")
                                                    for rank in ranks[:5]:
                                                        rank_num = rank.get('rank')
                                                        school = rank.get('school')
                                                        conference = rank.get('conference', 'Independent')
                                                        points = rank.get('points', 0)
                                                        first_place = rank.get('first_place_votes', 0)
                                                        
                                                        first_place_str = f" ({first_place} 1st)" if first_place > 0 else ""
                                                        print(f"         {rank_num:2}. {school} ({conference}) - {points} pts{first_place_str}")
                                    
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
    
    print("🏆 CFB Rankings MCP Test - Saving Results to JSON")
    print("=" * 60)
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    results = {
        "test_name": "CFB Rankings MCP Test",
        "timestamp": datetime.now().isoformat(),
        "server_url": mcp_url,
        "tests": []
    }
    
    test_cases = [
        {
            "name": "2024 Final Rankings",
            "args": {"year": 2024, "week": 15}
        },
        {
            "name": "2024 Week 1 Rankings", 
            "args": {"year": 2024, "week": 1}
        },
        {
            "name": "2024 Postseason Rankings",
            "args": {"year": 2024, "season_type": "postseason"}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\n🏆 Testing: {test['name']}")
            
            test_result = {
                "name": test['name'],
                "tool": "getCFBRankings",
                "args": test['args'],
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
            
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "getCFBRankings",
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
                                    if "rankings" in data:
                                        rankings = data["rankings"]
                                        
                                        polls_summary = []
                                        total_polls = 0
                                        
                                        for ranking_period in rankings:
                                            polls = ranking_period.get('polls', [])
                                            total_polls += len(polls)
                                            
                                            for poll in polls:
                                                poll_name = poll.get('poll', 'Unknown')
                                                ranks = poll.get('ranks', [])
                                                
                                                polls_summary.append({
                                                    "poll_name": poll_name,
                                                    "teams_count": len(ranks),
                                                    "top_5": ranks[:5] if ranks else []
                                                })
                                        
                                        test_result["summary"] = {
                                            "ranking_periods": len(rankings),
                                            "total_polls": total_polls,
                                            "polls": polls_summary[:5]  # First 5 polls
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
    output_file = "rankings.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"📊 Total tests: {len(results['tests'])}")
    successful_tests = sum(1 for test in results['tests'] if test['success'])
    print(f"✅ Successful: {successful_tests}/{len(results['tests'])}")
    
    return results

if __name__ == "__main__":
    # Run the original test for console output
    asyncio.run(test_cfb_rankings_mcp())
    
    print("\n" + "="*60)
    print("💾 SAVING RESULTS TO JSON...")
    print("="*60)
    
    # Run and save results
    asyncio.run(save_results_to_json())