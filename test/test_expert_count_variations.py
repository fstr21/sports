#!/usr/bin/env python3
"""
Test Different Expert Count Configurations
Try various parameter combinations to get 4+ experts working
"""
import asyncio
import json
import httpx
from datetime import datetime

async def test_expert_configurations():
    """Test different expert count configurations to find what works"""
    print("🧪 Testing Expert Count Configurations")
    print("=" * 60)
    
    # Base game data
    game_data = {
        "home_team": "New York Yankees (82-58, .586 win%, AL East leaders)",
        "away_team": "Boston Red Sox (75-65, .536 win%, Wild Card contention)", 
        "sport": "Baseball",
        "venue": "Yankee Stadium",
        "game_date": "August 24, 2025 - 7:05 PM ET",
        "additional_context": "ANALYSIS REQUIREMENTS: Must use multiple expert perspectives for comprehensive analysis"
    }
    
    # Custom Chronulus MCP URL
    custom_chronulus_url = "https://customchronpredictormcp-production.up.railway.app/mcp"
    
    # Test different configurations
    test_configs = [
        {
            "name": "Config 1: Basic 4 experts",
            "expert_count": 4,
            "analysis_depth": "comprehensive"
        },
        {
            "name": "Config 2: Forced 5 experts", 
            "expert_count": 5,
            "analysis_depth": "comprehensive"
        },
        {
            "name": "Config 3: 4 experts with multi_expert flag",
            "expert_count": 4,
            "analysis_depth": "comprehensive",
            "multi_expert_analysis": True
        },
        {
            "name": "Config 4: 4 experts with explicit instruction",
            "expert_count": 4,
            "analysis_depth": "comprehensive",
            "specific_instructions": "MANDATORY: Use exactly 4 different expert perspectives - Statistical, Situational, Contrarian, and Sharp experts"
        },
        {
            "name": "Config 5: Deep analysis mode",
            "expert_count": 4,
            "analysis_depth": "deep",
            "use_multi_expert_panel": True
        }
    ]
    
    results = []
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n📊 Test {i}: {config['name']}")
        print("-" * 40)
        
        # Build MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": i,
            "params": {
                "name": "getCustomChronulusAnalysis",
                "arguments": {
                    "game_data": game_data,
                    **{k: v for k, v in config.items() if k != "name"}
                }
            }
        }
        
        print(f"Request: {json.dumps(mcp_request['params']['arguments'], indent=2)}")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(custom_chronulus_url, json=mcp_request)
                response.raise_for_status()
                result = response.json()
                
                if "result" not in result:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
                    results.append({
                        "config": config["name"],
                        "status": "error",
                        "expert_count": 0,
                        "analysis_length": 0
                    })
                    continue
                
                # Extract and parse analysis
                mcp_result = result["result"]
                analysis_text = mcp_result["content"][0]["text"] if "content" in mcp_result and mcp_result["content"] else ""
                
                try:
                    analysis_data = json.loads(analysis_text)
                    analysis = analysis_data.get("analysis", {})
                    
                    actual_expert_count = analysis.get("expert_count", 0)
                    expert_analysis = analysis.get("expert_analysis", "")
                    analysis_length = len(expert_analysis)
                    
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
                    
                    print(f"✅ Response received:")
                    print(f"   Expert Count: {actual_expert_count}")
                    print(f"   Analysis Length: {analysis_length:,} characters")
                    print(f"   Expert Sections Found: {len(found_experts)} ({', '.join(found_experts)})")
                    print(f"   Model: {analysis.get('model_used', 'N/A')}")
                    
                    results.append({
                        "config": config["name"],
                        "status": "success",
                        "expert_count": actual_expert_count,
                        "analysis_length": analysis_length,
                        "expert_sections": len(found_experts),
                        "experts_found": found_experts
                    })
                    
                    # If we found multiple experts, save this config as successful
                    if actual_expert_count >= 4 or len(found_experts) >= 4:
                        print(f"🎉 SUCCESS: Found {max(actual_expert_count, len(found_experts))} experts!")
                    
                except json.JSONDecodeError:
                    print(f"❌ Failed to parse JSON response")
                    print(f"Raw response (first 200 chars): {analysis_text[:200]}...")
                    results.append({
                        "config": config["name"],
                        "status": "parse_error",
                        "expert_count": 0,
                        "analysis_length": len(analysis_text)
                    })
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            results.append({
                "config": config["name"],
                "status": "request_error",
                "expert_count": 0,
                "analysis_length": 0,
                "error": str(e)
            })
    
    # Summary
    print("\n📋 SUMMARY OF ALL TESTS")
    print("=" * 60)
    
    best_config = None
    max_experts = 0
    
    for result in results:
        status_emoji = "✅" if result["status"] == "success" else "❌"
        expert_count = result.get("expert_count", 0)
        expert_sections = result.get("expert_sections", 0)
        max_found = max(expert_count, expert_sections)
        
        print(f"{status_emoji} {result['config']}")
        print(f"   Expert Count: {expert_count} | Sections: {expert_sections} | Length: {result.get('analysis_length', 0):,}")
        
        if max_found > max_experts:
            max_experts = max_found
            best_config = result
    
    print(f"\n🏆 BEST CONFIGURATION:")
    if best_config and max_experts >= 4:
        print(f"✅ {best_config['config']}")
        print(f"✅ Achieved {max_experts} experts")
        print(f"✅ Analysis length: {best_config.get('analysis_length', 0):,} characters")
        
        # Show which experts were found
        if "experts_found" in best_config:
            print(f"✅ Expert types: {', '.join(best_config['experts_found'])}")
    else:
        print("❌ No configuration achieved 4+ experts")
        print("🔍 The MCP server may have limitations or bugs")
        print("💡 Consider fallback strategies or server-side investigation")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"expert_config_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            "test_timestamp": datetime.now().isoformat(),
            "test_summary": {
                "total_configs_tested": len(test_configs),
                "successful_configs": len([r for r in results if r["status"] == "success"]),
                "max_experts_achieved": max_experts,
                "best_config": best_config
            },
            "detailed_results": results
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved: {results_file}")
    
    return best_config, max_experts

async def main():
    """Main test function"""
    print("Expert Count Configuration Test")
    print("Finding the best way to get 4+ experts from Custom Chronulus MCP")
    print()
    
    best_config, max_experts = await test_expert_configurations()
    
    if max_experts >= 4:
        print("\n🎉 SUCCESS: Found a configuration that works!")
        print("This configuration can be applied to the Discord bot.")
    else:
        print("\n⚠️ LIMITATION: MCP server appears to be limited to fewer experts")
        print("Consider:")
        print("• Server-side investigation")
        print("• Alternative MCP servers")
        print("• Fallback strategies")

if __name__ == "__main__":
    asyncio.run(main())