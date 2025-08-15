#!/usr/bin/env python3
"""
CFB Games Tool - Test college football games via deployed MCP server
"""

import asyncio
import json
import httpx
from datetime import datetime

# Test the games endpoint via MCP server
async def test_cfb_games_mcp():
    """Test CFB games via deployed MCP server"""
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    
    test_cases = [
        {
            "name": "August 23, 2025 Games",
            "tool": "getCFBGames",
            "args": {"year": 2025, "week": 1}
        },
        {
            "name": "Kansas State Games 2024",
            "tool": "getCFBGames", 
            "args": {"year": 2024, "team": "Kansas State"}
        },
        {
            "name": "Big 12 Games Week 1 2025",
            "tool": "getCFBGames",
            "args": {"year": 2025, "week": 1, "conference": "Big 12"}
        },
        {
            "name": "Power 5 Teams",
            "tool": "getCFBTeams",
            "args": {"conference": "Big 12"}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # First test health check
        print("🏥 Testing Health Check...")
        try:
            health_response = await client.get("https://cfbmcp-production.up.railway.app/health")
            if health_response.status_code == 200:
                print("✅ Server is healthy!")
                print(f"   Response: {health_response.json()}")
            else:
                print(f"⚠️  Health check returned: {health_response.status_code}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
        
        print("\n" + "="*60)
        
        for test in test_cases:
            print(f"\n🏈 Testing: {test['name']}")
            print("-" * 40)
            
            # Create MCP request
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": test['tool'],
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
                                if text.startswith("## CFB"):
                                    # This is the markdown summary
                                    lines = text.split('\n')
                                    for line in lines[:3]:  # Show first 3 lines
                                        if line.strip():
                                            print(f"   {line}")
                                elif text.startswith("```json"):
                                    # This is the JSON data
                                    try:
                                        json_text = text.replace("```json\n", "").replace("\n```", "")
                                        data = json.loads(json_text)
                                        
                                        if test['tool'] == "getCFBGames" and "games" in data:
                                            games = data["games"]
                                            print(f"   📊 Found {len(games)} games")
                                            
                                            # Show sample games
                                            for i, game in enumerate(games[:3]):
                                                home = game.get('home_team', 'Unknown')
                                                away = game.get('away_team', 'Unknown')
                                                date = game.get('start_date', 'Unknown').split('T')[0]
                                                week = game.get('week', 'Unknown')
                                                print(f"      {i+1}. {away} @ {home} (Week {week}, {date})")
                                            
                                            if len(games) > 3:
                                                print(f"      ... and {len(games) - 3} more games")
                                        
                                        elif test['tool'] == "getCFBTeams" and "teams" in data:
                                            teams = data["teams"]
                                            print(f"   📊 Found {len(teams)} teams")
                                            
                                            # Show sample teams
                                            for i, team in enumerate(teams[:5]):
                                                school = team.get('school', 'Unknown')
                                                conference = team.get('conference', 'Unknown')
                                                print(f"      {i+1}. {school} ({conference})")
                                    
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
    
    print("🏈 CFB Games MCP Test - Saving Results to JSON")
    print("=" * 60)
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    results = {
        "test_name": "CFB Games MCP Test",
        "timestamp": datetime.now().isoformat(),
        "server_url": mcp_url,
        "tests": []
    }
    
    test_cases = [
        {
            "name": "August 23, 2025 Games",
            "tool": "getCFBGames",
            "args": {"year": 2025, "week": 1}
        },
        {
            "name": "Kansas State Games 2024",
            "tool": "getCFBGames", 
            "args": {"year": 2024, "team": "Kansas State"}
        },
        {
            "name": "Big 12 Games Week 1 2025",
            "tool": "getCFBGames",
            "args": {"year": 2025, "week": 1, "conference": "Big 12"}
        },
        {
            "name": "Power 5 Teams",
            "tool": "getCFBTeams",
            "args": {"conference": "Big 12"}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Health check
        health_result = {"test": "health_check", "success": False}
        try:
            health_response = await client.get("https://cfbmcp-production.up.railway.app/health")
            if health_response.status_code == 200:
                health_result["success"] = True
                health_result["response"] = health_response.json()
                print("✅ Server is healthy!")
            else:
                health_result["error"] = f"Status: {health_response.status_code}"
        except Exception as e:
            health_result["error"] = str(e)
        
        results["health_check"] = health_result
        
        # Run MCP tests
        for test in test_cases:
            print(f"\n🏈 Testing: {test['name']}")
            
            test_result = {
                "name": test['name'],
                "tool": test['tool'],
                "args": test['args'],
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
            
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": test['tool'],
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
                                    if test['tool'] == "getCFBGames" and "games" in data:
                                        test_result["summary"] = {
                                            "games_count": len(data["games"]),
                                            "sample_games": data["games"][:3]
                                        }
                                    elif test['tool'] == "getCFBTeams" and "teams" in data:
                                        test_result["summary"] = {
                                            "teams_count": len(data["teams"]),
                                            "sample_teams": data["teams"][:3]
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
    output_file = "games.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"📊 Total tests: {len(results['tests'])}")
    successful_tests = sum(1 for test in results['tests'] if test['success'])
    print(f"✅ Successful: {successful_tests}/{len(results['tests'])}")
    
    return results

if __name__ == "__main__":
    # Run the original test for console output
    asyncio.run(test_cfb_games_mcp())
    
    print("\n" + "="*60)
    print("💾 SAVING RESULTS TO JSON...")
    print("="*60)
    
    # Run and save results
    asyncio.run(save_results_to_json())