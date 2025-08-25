#!/usr/bin/env python3
"""
Test specifically requesting 4 experts
"""
import asyncio
import json
import httpx

async def test_4_experts():
    """Test requesting exactly 4 experts"""
    print("🧪 Testing 4-Expert Request Specifically")
    print("=" * 50)
    
    mcp_url = "https://customchronpredictormcp-production.up.railway.app/mcp"
    
    # Request exactly 4 experts
    request = {
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
                "expert_count": 4,  # Request 4 experts specifically
                "analysis_depth": "comprehensive"
            }
        }
    }
    
    print("📊 Requesting 4 experts with comprehensive analysis...")
    print(f"📡 URL: {mcp_url}")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(mcp_url, json=request)
            print(f"📈 Status: {response.status_code}")
            print(f"📄 Response length: {len(response.text)} chars")
            
            if response.status_code == 200:
                result = response.json()
                
                if "result" in result and result["result"] and "content" in result["result"]:
                    content = result["result"]["content"][0]["text"]
                    print(f"📋 Content length: {len(content)} chars")
                    
                    try:
                        analysis_data = json.loads(content)
                        print(f"🎯 Status: {analysis_data.get('status', 'N/A')}")
                        
                        if "error" in analysis_data:
                            print(f"❌ ERROR: {analysis_data['error']}")
                            print(f"💡 This explains why we're not getting 4 experts!")
                        elif "analysis" in analysis_data:
                            analysis = analysis_data["analysis"]
                            expert_count = analysis.get('expert_count', 0)
                            expert_text = analysis.get('expert_analysis', '')
                            
                            print(f"✅ Expert Count Returned: {expert_count}")
                            print(f"✅ Analysis Length: {len(expert_text)} chars")
                            print(f"✅ Away Prob: {analysis.get('away_team_win_probability', 0):.1%}")
                            print(f"✅ Home Prob: {analysis.get('home_team_win_probability', 0):.1%}")
                            print(f"✅ Recommendation: {analysis.get('betting_recommendation', 'N/A')}")
                            
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
                                if marker in expert_text:
                                    found_experts.append(marker.replace("[", "").replace("]", ""))
                            
                            print(f"🔍 Expert Sections Found: {len(found_experts)}")
                            if found_experts:
                                print(f"📋 Expert Types: {', '.join(found_experts)}")
                            
                            print(f"\n📖 Analysis Preview (first 500 chars):")
                            print("-" * 50)
                            print(expert_text[:500] + "..." if len(expert_text) > 500 else expert_text)
                            print("-" * 50)
                            
                            if expert_count >= 4:
                                print(f"\n🎉 SUCCESS: Got {expert_count} experts!")
                            else:
                                print(f"\n⚠️ STILL LIMITED: Only {expert_count} expert(s)")
                                print("🔍 Need to investigate the multi-expert logic")
                        else:
                            print(f"❌ Unexpected structure: {list(analysis_data.keys())}")
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON Error: {e}")
                        print(f"Raw content: {content[:300]}...")
                else:
                    print(f"❌ No content in response")
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                
    except Exception as e:
        print(f"❌ Request failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function"""
    await test_4_experts()

if __name__ == "__main__":
    asyncio.run(main())