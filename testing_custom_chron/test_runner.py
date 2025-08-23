#!/usr/bin/env python3
"""
Quick Test Runner for Custom Chronulus Implementation
Simplified runner to test the OpenRouter integration
"""

import asyncio
import os
from dotenv import load_dotenv
from custom_chronulus_openrouter import test_custom_chronulus_with_real_data

# Load environment variables - try current directory first, then parent
load_dotenv(".env.local")  # Current directory
load_dotenv("../.env.local")  # Parent directory as backup

def check_environment():
    """Check if required environment variables are set"""
    print("🔍 Environment Check:")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
    
    if api_key:
        print(f"✅ OPENROUTER_API_KEY: Set (length: {len(api_key)})")
    else:
        print("❌ OPENROUTER_API_KEY: Not found in environment")
        return False
    
    print(f"✅ OPENROUTER_MODEL: {model}")
    return True

async def run_quick_test():
    """Run a quick test of the custom Chronulus system"""
    
    print("🧪 CUSTOM CHRONULUS - QUICK TEST")
    print("=" * 50)
    
    if not check_environment():
        print("\n❌ Environment setup incomplete. Please check your .env.local file.")
        return
    
    print("\n🚀 Starting Red Sox @ Yankees analysis...")
    print("👥 Using 2-expert panel for cost efficiency")
    print("⏱️ Expected runtime: 30-60 seconds")
    
    try:
        result = await test_custom_chronulus_with_real_data()
        
        if result.get("status") == "success":
            print("\n✅ TEST SUCCESSFUL!")
            print(f"📊 Red Sox Win Probability: {result['analysis']['red_sox_win_probability']:.1%}")
            print(f"🎯 Betting Recommendation: {result['analysis']['betting_recommendation']}")
            print(f"📈 Market Edge: {result['analysis']['market_edge']:+.2%}")
        else:
            print(f"\n❌ TEST FAILED: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(run_quick_test())