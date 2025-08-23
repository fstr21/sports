#!/usr/bin/env python3
"""
Test Chronulus MCP Server on Railway - Remote Testing Script

This script calls the Railway-hosted Chronulus MCP server remotely and saves results
to a local results folder for analysis.
"""

import json
import httpx
import asyncio
from datetime import datetime
from pathlib import Path

# Railway MCP Server URL
RAILWAY_MCP_URL = "https://chronulusmcp-production.up.railway.app/mcp"
RESULTS_DIR = Path(__file__).parent / "chronulus_test_results"

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

def save_results(results: dict, test_name: str):
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
        f.write(f"# Chronulus Railway MCP Test Results\n\n")
        f.write(f"**Test**: {test_name}\n")
        f.write(f"**Timestamp**: {timestamp}\n")
        f.write(f"**Railway URL**: {RAILWAY_MCP_URL}\n\n")
        
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
                        f.write(f"- **Dodgers Win Probability**: {prob:.1%}\n")
                    
                    if "betting_markets_covered" in analysis_data["analysis"]:
                        markets = analysis_data["analysis"]["betting_markets_covered"]
                        f.write(f"- **Markets Analyzed**: {', '.join(markets)}\n")
                    
                    if "cost_estimate" in analysis_data["analysis"]:
                        cost = analysis_data["analysis"]["cost_estimate"]
                        f.write(f"- **Cost Estimate**: {cost}\n")
            except:
                pass
        
        f.write("\n## Full Response\n\n")
        f.write("```json\n")
        f.write(json.dumps(results, indent=2))
        f.write("\n```\n")
    
    print(f"💾 Results saved:")
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
    """Test hard-coded Dodgers @ Padres analysis"""
    print("\n🧠 TESTING HARDCODED ANALYSIS (Dodgers @ Padres)")
    print("=" * 60)
    print("⚾ Game: Los Angeles Dodgers @ San Diego Padres")
    print("💰 Markets: Moneyline, Run Line, Total (Over/Under 8.5)")
    print("👨‍⚖️ Experts: 1 (cost savings)")
    print("📝 Analysis: Detailed explanations requested")
    
    results = await call_railway_mcp("testChronulusHardcoded")
    save_results(results, "hardcoded_dodgers_padres")
    
    return results

async def main():
    """Main testing sequence"""
    print("🚀 RAILWAY CHRONULUS MCP REMOTE TESTING")
    print("=" * 70)
    print(f"🌐 Server: {RAILWAY_MCP_URL}")
    print(f"📁 Results: {RESULTS_DIR}")
    print()
    
    try:
        # Test 1: Health Check
        health_results = await test_health()
        
        # Check if server is healthy enough for analysis
        if "result" in health_results:
            try:
                content = health_results["result"]["content"][0]["text"]
                health_data = json.loads(content)
                server_status = health_data.get("status", "unknown")
                
                print(f"🏥 Server Status: {server_status}")
                
                if server_status == "healthy":
                    print("✅ Server is healthy - proceeding with analysis test")
                    
                    # Test 2: Hard-coded Analysis
                    analysis_results = await test_hardcoded_analysis()
                    
                    # Check analysis results
                    if "result" in analysis_results:
                        try:
                            content = analysis_results["result"]["content"][0]["text"]
                            analysis_data = json.loads(content)
                            
                            if analysis_data.get("status") == "success":
                                print("\n🎉 ANALYSIS COMPLETED SUCCESSFULLY!")
                                print("💡 Check the results folder for detailed analysis")
                                
                                # Quick preview
                                if "analysis" in analysis_data:
                                    analysis = analysis_data["analysis"]
                                    if "dodgers_win_probability" in analysis:
                                        prob = analysis["dodgers_win_probability"]
                                        print(f"📊 Preview - Dodgers Win Probability: {prob:.1%}")
                            else:
                                print(f"⚠️ Analysis completed with status: {analysis_data.get('status')}")
                        except Exception as e:
                            print(f"⚠️ Could not parse analysis results: {e}")
                    else:
                        print("❌ Analysis failed - check results for details")
                        
                else:
                    print(f"⚠️ Server not fully healthy (status: {server_status})")
                    print("💡 Analysis may still work - check results folder")
                    
                    # Try analysis anyway
                    analysis_results = await test_hardcoded_analysis()
                    
            except Exception as e:
                print(f"⚠️ Could not parse health results: {e}")
                print("💡 Attempting analysis anyway...")
                
                # Try analysis regardless
                analysis_results = await test_hardcoded_analysis()
        else:
            print("❌ Health check failed")
    
    except Exception as e:
        print(f"❌ Testing failed: {e}")
    
    print(f"\n📁 All results saved to: {RESULTS_DIR}")
    print("🔍 Check both .json and .md files for complete analysis")

if __name__ == "__main__":
    print("🧪 Starting remote Railway MCP testing...")
    print("⏱️  This may take several minutes for AI analysis...")
    print()
    
    # Run the test
    asyncio.run(main())
    
    print("\n✅ Testing complete!")
    input("Press Enter to exit...")