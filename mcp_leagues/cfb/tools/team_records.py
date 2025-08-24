#!/usr/bin/env python3
"""
CFB Team Records Tool - Test college football team records via deployed MCP server
"""

import asyncio
import json
import httpx

# Test the team records endpoint via MCP server
async def test_cfb_team_records_mcp():
    """Test CFB team records via deployed MCP server"""
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    
    test_cases = [
        {
            "name": "Kansas State 2024 Record",
            "args": {"year": 2024, "team": "Kansas State"}
        },
        {
            "name": "Big 12 2024 Records",
            "args": {"year": 2024, "conference": "Big 12"}
        },
        {
            "name": "All 2024 Records",
            "args": {"year": 2024}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\n📈 Testing: {test['name']}")
            print("-" * 40)
            
            # Create MCP request
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "getCFBTeamRecords",
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
                                if text.startswith("## CFB Team Records"):
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
                                        
                                        if "records" in data:
                                            records = data["records"]
                                            print(f"   📊 Found {len(records)} team records")
                                            
                                            # Show sample records with key metrics
                                            print(f"   ⭐ Sample team records:")
                                            for i, record in enumerate(records[:5]):
                                                team = record.get('team', 'Unknown')
                                                year = record.get('year', 'Unknown')
                                                total = record.get('total', {})
                                                wins = total.get('wins', 0)
                                                losses = total.get('losses', 0)
                                                expected_wins = record.get('expected_wins', 'N/A')
                                                conference = record.get('conference', 'Independent')
                                                
                                                # Format expected wins
                                                expected_str = f" (Expected: {expected_wins:.1f})" if isinstance(expected_wins, (int, float)) else ""
                                                
                                                print(f"      {i+1}. {team} ({year}): {wins}-{losses}{expected_str} ({conference})")
                                                
                                                # Show additional record breakdowns
                                                conf_games = record.get('conference_games', {})
                                                home_games = record.get('home_games', {})
                                                away_games = record.get('away_games', {})
                                                
                                                if conf_games.get('wins') is not None:
                                                    conf_record = f"{conf_games.get('wins', 0)}-{conf_games.get('losses', 0)}"
                                                    print(f"         Conference: {conf_record}")
                                                
                                                if home_games.get('wins') is not None and away_games.get('wins') is not None:
                                                    home_record = f"{home_games.get('wins', 0)}-{home_games.get('losses', 0)}"
                                                    away_record = f"{away_games.get('wins', 0)}-{away_games.get('losses', 0)}"
                                                    print(f"         Home: {home_record}, Away: {away_record}")
                                    
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
    
    print("📈 CFB Team Records MCP Test - Saving Results to JSON")
    print("=" * 60)
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    results = {
        "test_name": "CFB Team Records MCP Test",
        "timestamp": datetime.now().isoformat(),
        "server_url": mcp_url,
        "tests": []
    }
    
    test_cases = [
        {
            "name": "Kansas State 2024 Record",
            "args": {"year": 2024, "team": "Kansas State"}
        },
        {
            "name": "Big 12 2024 Records",
            "args": {"year": 2024, "conference": "Big 12"}
        },
        {
            "name": "All 2024 Records",
            "args": {"year": 2024}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\n📈 Testing: {test['name']}")
            
            test_result = {
                "name": test['name'],
                "tool": "getCFBTeamRecords",
                "args": test['args'],
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
            
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "getCFBTeamRecords",
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
                                    if "records" in data:
                                        records = data["records"]
                                        
                                        # Calculate summary statistics
                                        conferences = {}
                                        total_wins = 0
                                        total_losses = 0
                                        
                                        for record in records:
                                            conf = record.get('conference', 'Independent')
                                            if conf not in conferences:
                                                conferences[conf] = 0
                                            conferences[conf] += 1
                                            
                                            total_record = record.get('total', {})
                                            total_wins += total_record.get('wins', 0)
                                            total_losses += total_record.get('losses', 0)
                                        
                                        test_result["summary"] = {
                                            "records_count": len(records),
                                            "conferences": conferences,
                                            "total_wins": total_wins,
                                            "total_losses": total_losses,
                                            "sample_records": records[:5]
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
    output_file = "team_records.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"📊 Total tests: {len(results['tests'])}")
    successful_tests = sum(1 for test in results['tests'] if test['success'])
    print(f"✅ Successful: {successful_tests}/{len(results['tests'])}")
    
    return results

if __name__ == "__main__":
    # Run the original test for console output
    asyncio.run(test_cfb_team_records_mcp())
    
    print("\n" + "="*60)
    print("💾 SAVING RESULTS TO JSON...")
    print("="*60)
    
    # Run and save results
    asyncio.run(save_results_to_json())