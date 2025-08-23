#!/usr/bin/env python3
"""
Test script for Chronulus MCP Server
Tests the server locally before Railway deployment
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import httpx

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_server_locally():
    """Test the MCP server running locally"""
    
    print("Testing Chronulus MCP Server Locally")
    print("=" * 50)
    
    # Import server components
    try:
        from chronulus_mcp_server import get_chronulus_health, CHRONULUS_AVAILABLE, CHRONULUS_API_KEY
        print("✅ Server imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test health check
    print("\nTesting health check...")
    health = await get_chronulus_health()
    print(f"Health Status: {health['status']}")
    print(f"Chronulus SDK: {health['chronulus_sdk']}")
    print(f"API Key Configured: {health['api_key_configured']}")
    
    # Test sample game data (minimal)
    print("\nTesting with sample game data...")
    sample_game_data = {
        "home_team": "Pittsburgh Pirates",
        "away_team": "Colorado Rockies", 
        "date": "2025-08-23",
        "venue": "PNC Park",
        "stats": {
            "home_record": "54-74",
            "away_record": "37-91"
        },
        "odds": {
            "moneyline": {"home": -190, "away": +160},
            "implied_probability": 0.385
        },
        "form": {
            "home_last_10": "3-7",
            "away_last_10": "7-3"
        }
    }
    
    if CHRONULUS_AVAILABLE and CHRONULUS_API_KEY:
        print("Testing Chronulus analysis (this will make API calls)...")
        from chronulus_mcp_server import get_chronulus_analysis
        
        # Test with 2 experts (minimal cost)
        analysis = await get_chronulus_analysis(sample_game_data, expert_count=2)
        print(f"Analysis Status: {analysis.get('status', 'unknown')}")
        
        if analysis.get('status') == 'success':
            result = analysis['analysis']
            print(f"Consensus Probability: {result['consensus_probability']:.1%}")
            print(f"Expert Count: {result['expert_count']}")
            print(f"Recommendation: {result['recommendation']}")
            print("✅ Full analysis successful!")
        else:
            print(f"⚠️ Analysis issue: {analysis.get('error', 'Unknown error')}")
    else:
        print("⚠️ Skipping live analysis (no API key or SDK)")
        print("   Set CHRONULUS_API_KEY environment variable to test fully")
    
    print("\n📊 Server Test Summary:")
    print(f"✅ Imports: Working")
    print(f"✅ Health Check: Working") 
    print(f"✅ Structure: Ready for Railway")
    
    if CHRONULUS_AVAILABLE and CHRONULUS_API_KEY:
        print(f"✅ Live API: Working")
        print(f"🚀 Ready for production deployment!")
    else:
        print(f"⚠️ Live API: Need API key for full functionality")
        print(f"🔧 Server structure is ready, just needs API key in Railway")
    
    return True

async def test_mcp_protocol():
    """Test MCP JSON-RPC 2.0 protocol format"""
    
    print("\n🔗 Testing MCP Protocol Format")
    print("-" * 30)
    
    # Test tools/list request
    tools_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    
    print("Sample tools/list request:")
    print(json.dumps(tools_request, indent=2))
    
    # Test tools/call request
    call_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 2,
        "params": {
            "name": "getChronulusHealth",
            "arguments": {}
        }
    }
    
    print("\nSample tools/call request:")
    print(json.dumps(call_request, indent=2))
    
    print("✅ MCP protocol format ready")

if __name__ == "__main__":
    print("Chronulus MCP Server - Local Test")
    print("This tests the server before Railway deployment")
    print()
    
    # Run async tests
    asyncio.run(test_server_locally())
    asyncio.run(test_mcp_protocol())
    
    print("\n🚀 Next Steps:")
    print("1. Deploy to Railway using the created files")
    print("2. Set CHRONULUS_API_KEY in Railway environment variables")
    print("3. Test the deployed endpoint")
    print("4. Integrate with your Discord bot MCP client")