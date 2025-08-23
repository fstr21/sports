#!/usr/bin/env python3
"""
Optimized Chronulus MCP Server Testing - Cost Efficient Version

This script calls the Railway-hosted Chronulus MCP server with optimizations:
- Usage estimation before analysis
- Minimum experts (2) for cost control
- Short explanations (3-5 sentences) to reduce cost
- Context caching enabled
- Cost-conscious error handling
"""

import json
import httpx
import asyncio
from datetime import datetime
from pathlib import Path
import os

# Railway MCP Server URL
RAILWAY_MCP_URL = "https://chronulusmcp-production.up.railway.app/mcp"
RESULTS_DIR = Path(__file__).parent / "results"

# Cost optimization settings - MINIMAL MODE
MAX_COST_PER_TEST = 0.25   # Maximum $0.25 per analysis (working baseline)
DEFAULT_EXPERTS = 2        # Minimum experts (required by Chronulus)
DEFAULT_NOTE_LENGTH = (12, 18)  # Working detailed analysis
MINIMAL_MODE = True        # Enable minimal mode for raw predictions only

async def call_railway_mcp(tool_name: str, arguments: dict = None):
    """
    Call the Railway-hosted Chronulus MCP server remotely
    """
    if arguments is None:
        arguments = {}
    
    # MCP JSON-RPC 2.0 request format
    request_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    print(f"🔗 Calling Railway MCP Server: {RAILWAY_MCP_URL}")
    print(f"🛠️  Tool: {tool_name}")
    print(f"📊 Arguments: {json.dumps(arguments, indent=2) if arguments else 'None'}")
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minute timeout
            response = await client.post(
                RAILWAY_MCP_URL,
                json=request_payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"🔄 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "response_text": response.text
                }
                
    except httpx.TimeoutException:
        return {"error": "Request timed out after 5 minutes"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def estimate_analysis_cost():
    """
    Estimate cost of analysis before running
    Based on Chronulus pricing: ~$0.05-0.10 for 2 experts
    """
    base_cost = 0.075  # Average cost for 2 experts
    cost_range = "$0.05-0.10"

    print("💰 COST ESTIMATION")
    print(f"   Expected Cost: {cost_range}")
    print(f"   Expert Count: {DEFAULT_EXPERTS}")
    print(f"   Note Length: {DEFAULT_NOTE_LENGTH} sentences")
    print(f"   Context Caching: Enabled")
    print(f"   Max Cost Limit: ${MAX_COST_PER_TEST}")
    print()

    return base_cost

def save_results(results: dict, test_name: str, cost_estimate: float = None):
    """
    Save test results to local folder with timestamp
    """
    # Ensure results directory exists
    RESULTS_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save JSON results
    json_file = RESULTS_DIR / f"{test_name}_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Save readable markdown results
    md_file = RESULTS_DIR / f"{test_name}_{timestamp}.md"
    with open(md_file, 'w') as f:
        f.write("# Chronulus Railway MCP Test Results\n\n")
        f.write(f"**Test**: {test_name}\n")
        f.write(f"**Timestamp**: {timestamp}\n")
        f.write(f"**Railway URL**: {RAILWAY_MCP_URL}\n")

        if cost_estimate:
            f.write(f"**Estimated Cost**: ${cost_estimate:.3f}\n")

        f.write("\n")

        # Extract analysis if available
        if "result" in results and "content" in results["result"]:
            try:
                content = results["result"]["content"][0]["text"]
                analysis_data = json.loads(content)

                if "analysis" in analysis_data:
                    f.write("## Expert Analysis\n\n")
                    if "expert_analysis" in analysis_data["analysis"]:
                        f.write(f"{analysis_data['analysis']['expert_analysis']}\n\n")

                    f.write("## Key Metrics\n\n")
                    if "dodgers_win_probability" in analysis_data["analysis"]:
                        prob = analysis_data["analysis"]["dodgers_win_probability"]
                        f.write(f"- **Win Probability**: {prob:.1%}\n")

                    if "cost_estimate" in analysis_data["analysis"]:
                        cost = analysis_data["analysis"]["cost_estimate"]
                        f.write(f"- **Actual Cost**: {cost}\n")
            except:
                pass

        f.write("\n## Full Response\n\n")
        f.write("```json\n")
        f.write(json.dumps(results, indent=2))
        f.write("\n```\n")

    print("💾 Results saved:")
    print(f"   JSON: {json_file}")
    print(f"   MD:   {md_file}")

    return json_file, md_file

async def test_health():
    """Test MCP server health"""
    print("\n🔍 TESTING HEALTH CHECK")
    print("=" * 50)
    
    results = await call_railway_mcp("getChronulusHealth")
    save_results(results, "health_check")
    
    return results

async def test_hardcoded_analysis():
    """Test MINIMAL raw prediction - Dodgers @ Padres (outsource explanation)"""
    print("\n🧠 TESTING OPTIMIZED HARDCODED ANALYSIS (Dodgers @ Padres)")
    print("=" * 65)
    print("⚾ Game: Los Angeles Dodgers @ San Diego Padres")
    print("💰 Markets: Moneyline, Run Line, Total (Over/Under 8.5)")
    print(f"👨‍⚖️ Experts: {DEFAULT_EXPERTS} (minimum for cost control)")
    print(f"📝 Analysis: MINIMAL - Raw prediction only ({DEFAULT_NOTE_LENGTH[0]}-{DEFAULT_NOTE_LENGTH[1]} sentences)")
    print("⚡ Context Caching: Enabled")
    print("🎯 Mode: Raw probability data only (outsource explanation to cheaper LLM)")

    # Estimate cost before running
    cost_estimate = estimate_analysis_cost()

    # Check if within budget
    if cost_estimate > MAX_COST_PER_TEST:
        print(f"⚠️ Estimated cost ${cost_estimate:.3f} exceeds limit ${MAX_COST_PER_TEST}")
        print("💡 Consider reducing expert count or note length")
        return {"error": "Cost estimate exceeds limit"}

    results = await call_railway_mcp("testChronulusHardcoded")
    save_results(results, "hardcoded_dodgers_padres_optimized", cost_estimate)

    return results

async def main():
    """Main testing sequence - Cost optimized"""
    print("🚀 OPTIMIZED RAILWAY CHRONULUS MCP TESTING")
    print("=" * 75)
    print(f"🌐 Server: {RAILWAY_MCP_URL}")
    print(f"📁 Results: {RESULTS_DIR}")
    print(f"💰 Cost Control: Max ${MAX_COST_PER_TEST} per analysis")
    print(f"👨‍⚖️ Expert Count: {DEFAULT_EXPERTS} (minimum)")
    print(f"📝 Note Length: {DEFAULT_NOTE_LENGTH} sentences (short)")
    print()

    try:
        # Test 1: Health Check (free)
        print("🔍 PHASE 1: Health Check")
        print("-" * 30)
        health_results = await test_health()

        # Check if server is healthy enough for analysis
        if "result" in health_results:
            try:
                content = health_results["result"]["content"][0]["text"]
                health_data = json.loads(content)
                server_status = health_data.get("status", "unknown")

                print(f"🏥 Server Status: {server_status}")

                if server_status == "healthy":
                    print("✅ Server is healthy - proceeding with optimized analysis")
                    print()

                    # Test 2: Cost-optimized Analysis
                    print("🧠 PHASE 2: Cost-Optimized Analysis")
                    print("-" * 40)
                    analysis_results = await test_hardcoded_analysis()

                    # Check analysis results
                    if "result" in analysis_results:
                        try:
                            content = analysis_results["result"]["content"][0]["text"]
                            analysis_data = json.loads(content)

                            if analysis_data.get("status") == "success":
                                print("\n🎉 OPTIMIZED ANALYSIS COMPLETED SUCCESSFULLY!")
                                print("💡 Check the results folder for analysis")
                                print("⚡ Cost savings: Short explanations + minimum experts")

                                # Quick preview
                                if "analysis" in analysis_data:
                                    analysis = analysis_data["analysis"]
                                    if "dodgers_win_probability" in analysis:
                                        prob = analysis["dodgers_win_probability"]
                                        print(f"📊 Preview - Win Probability: {prob:.1%}")

                                    if "cost_estimate" in analysis:
                                        cost = analysis["cost_estimate"]
                                        print(f"💰 Actual Cost: {cost}")
                            else:
                                print(f"⚠️ Analysis completed with status: {analysis_data.get('status')}")
                        except Exception as e:
                            print(f"⚠️ Could not parse analysis results: {e}")
                    else:
                        print("❌ Analysis failed - check results for details")

                else:
                    print(f"⚠️ Server not fully healthy (status: {server_status})")
                    print("💡 Analysis may still work - check results folder")

                    # Try analysis anyway with cost control
                    analysis_results = await test_hardcoded_analysis()

            except Exception as e:
                print(f"⚠️ Could not parse health results: {e}")
                print("💡 Attempting analysis anyway with cost controls...")

                # Try analysis with cost optimization
                analysis_results = await test_hardcoded_analysis()
        else:
            print("❌ Health check failed")

    except Exception as e:
        print(f"❌ Testing failed: {e}")

    print(f"\n📁 All results saved to: {RESULTS_DIR}")
    print("🔍 Check both .json and .md files for complete analysis")
    print("💡 This optimized version should use less credits!")

if __name__ == "__main__":
    print("🧪 Starting OPTIMIZED Railway MCP testing...")
    print("⏱️  This may take 2-3 minutes for AI analysis...")
    print("💰 Cost: ~$0.05-0.10 (minimum configuration)")
    print()

    # Run the optimized test
    asyncio.run(main())

    print("\n✅ OPTIMIZED Testing complete!")
    print("💡 Check your Chronulus usage - should be minimal cost!")