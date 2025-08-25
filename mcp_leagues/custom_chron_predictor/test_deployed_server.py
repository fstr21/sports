#!/usr/bin/env python3
"""
Quick test of the updated 4-expert MCP server
"""
import asyncio
import json
import httpx

async def test_updated_server():
    """Test that the updated server returns 4 experts"""
    print("🧪 Testing Updated 4-Expert Custom Chronulus MCP")
    print("=" * 60)
    
    # Test with the deployed server URL
    mcp_url = "https://customchronpredictormcp-production.up.railway.app/mcp"
    
    # Test request for 4 experts
    test_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getCustomChronulusAnalysis",
            "arguments": {
                "game_data": {
                    "home_team": "New York Yankees (82-58, .586 win%, AL East leaders)",
                    "away_team": "Boston Red Sox (75-65, .536 win%, Wild Card contention)",
                    "venue": "Yankee Stadium", 
                    "game_date": "August 25, 2025 - 7:05 PM ET",
                    "home_record": "82-58 (.586)",
                    "away_record": "75-65 (.536)",
                    "home_moneyline": -165,
                    "away_moneyline": 145,
                    "additional_context": "AL East rivalry with playoff implications"
                },
                "expert_count": 4,  # Request 4 experts
                "analysis_depth": "comprehensive"
            }
        }
    }
    
    print(f"📡 Testing deployed server: {mcp_url}")
    print(f"📊 Requesting {test_request['params']['arguments']['expert_count']} experts")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(mcp_url, json=test_request)
            response.raise_for_status()
            result = response.json()
            
            if "result" not in result:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                return False
            
            # Extract analysis text
            mcp_result = result["result"]
            analysis_text = mcp_result["content"][0]["text"] if "content" in mcp_result and mcp_result["content"] else ""
            
            try:
                analysis_data = json.loads(analysis_text)
                analysis = analysis_data.get("analysis", {})
                
                expert_count = analysis.get("expert_count", 0)
                expert_analysis = analysis.get("expert_analysis", "")
                analysis_length = len(expert_analysis)
                
                print(f"✅ Response received ({len(analysis_text)} chars)")
                print(f"📈 Expert Count: {expert_count}")
                print(f"📄 Analysis Length: {analysis_length:,} characters")
                
                # Check for expert sections
                expert_markers = [
                    "[STATISTICAL EXPERT]",
                    "[SITUATIONAL EXPERT]", 
                    "[CONTRARIAN EXPERT]",
                    "[SHARP EXPERT]",
                    "[MARKET EXPERT]"
                ]
                
                found_experts = []
                for marker in expert_markers:
                    if marker in expert_analysis:
                        found_experts.append(marker.replace("[", "").replace("]", ""))
                
                print(f"🔍 Expert Sections Found: {len(found_experts)}")
                if found_experts:
                    print(f"📋 Expert Types: {', '.join(found_experts)}")
                
                # Print first 500 chars of analysis to see content
                print(f"\n📖 Analysis Preview:")
                print("-" * 40)
                print(expert_analysis[:500] + "..." if len(expert_analysis) > 500 else expert_analysis)
                print("-" * 40)
                
                if expert_count >= 4:
                    print(f"\n🎉 SUCCESS: Server returned {expert_count} experts!")
                    print("✅ The 4-expert update is working!")
                    return True
                else:
                    print(f"\n⚠️ STILL LIMITED: Only {expert_count} expert(s) returned")
                    print("🔍 The update may not be deployed yet")
                    return False
                    
            except json.JSONDecodeError:
                print(f"❌ Failed to parse JSON response")
                print(f"Raw response: {analysis_text[:200]}...")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("Testing Updated Custom Chronulus MCP Server")
    print("Checking if 4-expert functionality is deployed")
    print()
    
    success = await test_updated_server()
    
    if success:
        print("\n🎉 The 4-expert update is working!")
        print("Discord bot should now get rich analysis")
    else:
        print("\n❌ Update not working yet")
        print("Need to deploy the updated server")

if __name__ == "__main__":
    asyncio.run(main())