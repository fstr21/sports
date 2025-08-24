#!/usr/bin/env python3
"""
CFB Game Stats Tool - Test college football game statistics via deployed MCP server
"""

import asyncio
import json
import httpx

# Test the game stats endpoint via MCP server
async def test_cfb_game_stats_mcp():
    """Test CFB game stats via deployed MCP server"""
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    
    test_cases = [
        {
            "name": "Kansas State Week 1 2024 Stats",
            "args": {"year": 2024, "week": 1, "team": "Kansas State"}
        },
        {
            "name": "Big 12 Week 1 2024 Stats",
            "args": {"year": 2024, "week": 1, "conference": "Big 12"}
        },
        {
            "name": "All Week 1 2024 Stats",
            "args": {"year": 2024, "week": 1}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\n📊 Testing: {test['name']}")
            print("-" * 40)
            
            # Create MCP request
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "getCFBGameStats",
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
                                if text.startswith("## CFB Game Stats"):
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
                                        
                                        if "game_stats" in data:
                                            game_stats = data["game_stats"]
                                            print(f"   📊 Found {len(game_stats)} games with stats")
                                            
                                            # Show sample game statistics
                                            print(f"   ⭐ Sample game statistics:")
                                            for i, game in enumerate(game_stats[:3]):
                                                week = game.get('week', 'Unknown')
                                                season = game.get('season', 'Unknown')
                                                venue = game.get('venue', 'Unknown')
                                                attendance = game.get('attendance', 'N/A')
                                                teams = game.get('teams', [])
                                                
                                                print(f"      {i+1}. Game (Week {week}, {season}):")
                                                print(f"         Venue: {venue}")
                                                if attendance != 'N/A':
                                                    print(f"         Attendance: {attendance:,}")
                                                
                                                for j, team in enumerate(teams[:2]):
                                                    school = team.get('school', 'Unknown')
                                                    home_away = team.get('home_away', 'Unknown')
                                                    points = team.get('points', 0)
                                                    stats = team.get('stats', {})
                                                    
                                                    print(f"         {school} ({home_away}): {points} points")
                                                    
                                                    # Show key stats
                                                    key_stats = ['totalYards', 'passingYards', 'rushingYards', 'turnovers']
                                                    stat_strings = []
                                                    for stat_name in key_stats:
                                                        if stat_name in stats:
                                                            stat_strings.append(f"{stat_name}: {stats[stat_name]}")
                                                    
                                                    if stat_strings:
                                                        print(f"           {', '.join(stat_strings[:3])}")
                                    
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
    
    print("📊 CFB Game Stats MCP Test - Saving Results to JSON")
    print("=" * 60)
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    results = {
        "test_name": "CFB Game Stats MCP Test",
        "timestamp": datetime.now().isoformat(),
        "server_url": mcp_url,
        "tests": []
    }
    
    test_cases = [
        {
            "name": "Kansas State Week 1 2024 Stats",
            "args": {"year": 2024, "week": 1, "team": "Kansas State"}
        },
        {
            "name": "Big 12 Week 1 2024 Stats",
            "args": {"year": 2024, "week": 1, "conference": "Big 12"}
        },
        {
            "name": "All Week 1 2024 Stats",
            "args": {"year": 2024, "week": 1}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\n📊 Testing: {test['name']}")
            
            test_result = {
                "name": test['name'],
                "tool": "getCFBGameStats",
                "args": test['args'],
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
            
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "getCFBGameStats",
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
                                    if "game_stats" in data:
                                        game_stats = data["game_stats"]
                                        
                                        # Calculate summary statistics
                                        total_attendance = 0
                                        venues = set()
                                        teams_count = 0
                                        
                                        for game in game_stats:
                                            attendance = game.get('attendance')
                                            if attendance:
                                                total_attendance += attendance
                                            
                                            venue = game.get('venue')
                                            if venue:
                                                venues.add(venue)
                                            
                                            teams = game.get('teams', [])
                                            teams_count += len(teams)
                                        
                                        test_result["summary"] = {
                                            "games_count": len(game_stats),
                                            "total_attendance": total_attendance,
                                            "venues_count": len(venues),
                                            "teams_count": teams_count,
                                            "sample_games": game_stats[:3]
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
    output_file = "game_stats.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"📊 Total tests: {len(results['tests'])}")
    successful_tests = sum(1 for test in results['tests'] if test['success'])
    print(f"✅ Successful: {successful_tests}/{len(results['tests'])}")
    
    return results

if __name__ == "__main__":
    # Run the original test for console output
    asyncio.run(test_cfb_game_stats_mcp())
    
    print("\n" + "="*60)
    print("💾 SAVING RESULTS TO JSON...")
    print("="*60)
    
    # Run and save results
    asyncio.run(save_results_to_json())