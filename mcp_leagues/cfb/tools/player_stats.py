#!/usr/bin/env python3
"""
CFB Player Stats Tool - Test college football player statistics via deployed MCP server
"""

import asyncio
import json
import httpx

# Test the player stats endpoint via MCP server
async def test_cfb_player_stats_mcp():
    """Test CFB player stats via deployed MCP server"""
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    
    test_cases = [
        {
            "name": "Avery Johnson 2024 Stats",
            "args": {"year": 2024, "team": "Kansas State", "player": "Avery Johnson"}
        },
        {
            "name": "Kansas State 2024 Passing Stats",
            "args": {"year": 2024, "team": "Kansas State", "category": "passing"}
        },
        {
            "name": "Big 12 2024 Rushing Stats",
            "args": {"year": 2024, "conference": "Big 12", "category": "rushing"}
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
                    "name": "getCFBPlayerStats",
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
                                if text.startswith("## CFB Player Stats"):
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
                                        
                                        if "stats" in data:
                                            stats = data["stats"]
                                            print(f"   📊 Found {len(stats)} stat records")
                                            
                                            # Group by player and category
                                            players = {}
                                            categories = {}
                                            
                                            for stat in stats:
                                                player_name = stat.get('player', 'Unknown')
                                                category = stat.get('category', 'Unknown')
                                                stat_type = stat.get('stat_type', 'Unknown')
                                                value = stat.get('stat', 0)
                                                
                                                if player_name not in players:
                                                    players[player_name] = {}
                                                if category not in players[player_name]:
                                                    players[player_name][category] = {}
                                                players[player_name][category][stat_type] = value
                                                
                                                if category not in categories:
                                                    categories[category] = 0
                                                categories[category] += 1
                                            
                                            print(f"   📈 Categories found:")
                                            for cat, count in list(categories.items())[:5]:
                                                print(f"      {cat}: {count} records")
                                            
                                            print(f"   ⭐ Sample player stats:")
                                            for i, (player, player_stats) in enumerate(list(players.items())[:3]):
                                                print(f"      {i+1}. {player}:")
                                                for category, cat_stats in list(player_stats.items())[:2]:
                                                    key_stats = list(cat_stats.items())[:3]
                                                    stats_str = ", ".join([f"{k}: {v}" for k, v in key_stats])
                                                    print(f"         {category}: {stats_str}")
                                    
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
    
    print("📊 CFB Player Stats MCP Test - Saving Results to JSON")
    print("=" * 60)
    
    mcp_url = "https://cfbmcp-production.up.railway.app/mcp"
    results = {
        "test_name": "CFB Player Stats MCP Test",
        "timestamp": datetime.now().isoformat(),
        "server_url": mcp_url,
        "tests": []
    }
    
    test_cases = [
        {
            "name": "Avery Johnson 2024 Stats",
            "args": {"year": 2024, "team": "Kansas State", "player": "Avery Johnson"}
        },
        {
            "name": "Kansas State 2024 Passing Stats",
            "args": {"year": 2024, "team": "Kansas State", "category": "passing"}
        },
        {
            "name": "Big 12 2024 Rushing Stats",
            "args": {"year": 2024, "conference": "Big 12", "category": "rushing"}
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\n📊 Testing: {test['name']}")
            
            test_result = {
                "name": test['name'],
                "tool": "getCFBPlayerStats",
                "args": test['args'],
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
            
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "getCFBPlayerStats",
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
                                    if "stats" in data:
                                        stats = data["stats"]
                                        
                                        # Group by player and category
                                        players = {}
                                        categories = {}
                                        
                                        for stat in stats:
                                            player_name = stat.get('player', 'Unknown')
                                            category = stat.get('category', 'Unknown')
                                            
                                            if player_name not in players:
                                                players[player_name] = 0
                                            players[player_name] += 1
                                            
                                            if category not in categories:
                                                categories[category] = 0
                                            categories[category] += 1
                                        
                                        test_result["summary"] = {
                                            "stats_count": len(stats),
                                            "players": dict(list(players.items())[:10]),  # Top 10 players
                                            "categories": categories,
                                            "sample_stats": stats[:10]
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
    output_file = "player_stats.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"📊 Total tests: {len(results['tests'])}")
    successful_tests = sum(1 for test in results['tests'] if test['success'])
    print(f"✅ Successful: {successful_tests}/{len(results['tests'])}")
    
    return results

if __name__ == "__main__":
    # Run the original test for console output
    asyncio.run(test_cfb_player_stats_mcp())
    
    print("\n" + "="*60)
    print("💾 SAVING RESULTS TO JSON...")
    print("="*60)
    
    # Run and save results
    asyncio.run(save_results_to_json())