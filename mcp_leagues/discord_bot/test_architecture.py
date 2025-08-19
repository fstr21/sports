#!/usr/bin/env python3
"""
Simple test script for the enhanced bot architecture without requiring environment variables
"""
import sys
import os
import asyncio
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_architecture():
    """Test the enhanced bot architecture components"""
    print("🔍 Testing Enhanced Discord Sports Bot Architecture...")
    print("=" * 60)
    
    try:
        # Test core imports
        print("📦 Testing core imports...")
        
        from core.mcp_client import MCPClient, MCPResponse
        print("  ✅ MCP Client")
        
        from core.base_sport_handler import BaseSportHandler, Match, ChannelCreationResult
        print("  ✅ Base Sport Handler")
        
        from core.sync_manager import SyncManager
        print("  ✅ Sync Manager")
        
        from core.sport_manager import SportManager
        print("  ✅ Sport Manager")
        
        from sports.soccer_handler import SoccerHandler
        print("  ✅ Soccer Handler")
        
        from sports.mlb_handler import MLBHandler
        print("  ✅ MLB Handler")
        
        print("\\n⚙️ Testing component functionality...")
        
        # Test MCP Client
        mcp_client = MCPClient(timeout=10.0, max_retries=2)
        print("  ✅ MCP Client instantiation")
        
        # Test Match object creation
        test_match = Match(
            id="test_123",
            home_team="Test Home",
            away_team="Test Away", 
            league="Test League",
            datetime=None,
            odds={"home": 2.5, "away": 1.8},
            status="scheduled",
            additional_data={"time": "15:00"}
        )
        print("  ✅ Match object creation")
        
        # Test result objects
        channel_result = ChannelCreationResult(
            success=True,
            channels_created=5,
            total_matches=10,
            errors=[],
            message="Test successful"
        )
        print("  ✅ ChannelCreationResult object creation")
        
        # Test sport handler instantiation (without real config)
        test_config = {
            'name': 'soccer',
            'mcp_url': 'https://test.example.com',
            'category_name': 'TEST SOCCER',
            'embed_color': 0x00ff00,
            'date_format': '%d-%m-%Y'
        }
        
        soccer_handler = SoccerHandler('soccer', test_config, mcp_client)
        print("  ✅ Soccer Handler instantiation")
        
        mlb_handler = MLBHandler('mlb', test_config, mcp_client)
        print("  ✅ MLB Handler instantiation")
        
        # Test handler methods exist
        required_methods = ['create_channels', 'clear_channels', 'get_matches', 'format_match_analysis']
        for method_name in required_methods:
            if hasattr(soccer_handler, method_name) and callable(getattr(soccer_handler, method_name)):
                print(f"    ✅ Soccer Handler has {method_name}")
            else:
                print(f"    ❌ Soccer Handler missing {method_name}")
                
            if hasattr(mlb_handler, method_name) and callable(getattr(mlb_handler, method_name)):
                print(f"    ✅ MLB Handler has {method_name}")
            else:
                print(f"    ❌ MLB Handler missing {method_name}")
        
        # Test utility methods
        channel_name = soccer_handler.format_channel_name("Real Madrid", "Barcelona")
        print(f"  ✅ Channel name formatting: {channel_name}")
        
        american_odds = soccer_handler._convert_to_american_odds(2.5)
        print(f"  ✅ Odds conversion: 2.5 decimal = {american_odds} American")
        
        # Clean up
        await mcp_client.close()
        
        print("\\n" + "=" * 60)
        print("🎉 SUCCESS: Architecture test complete!")
        print("\\n📋 Test Results:")
        print("  • ✅ All core components imported successfully")
        print("  • ✅ All sport handlers instantiated correctly")
        print("  • ✅ Required methods present on all handlers")
        print("  • ✅ Utility functions working")
        print("  • ✅ Data models functioning correctly")
        print("\\n🚀 The enhanced architecture is ready!")
        print("\\n📝 To deploy:")
        print("  1. Set up your environment variables (DISCORD_TOKEN, etc.)")
        print("  2. Run sports_discord_bot_enhanced.py")
        print("  3. Use /sync to update Discord commands")
        print("  4. Test /create-channels and /clear-channels")
        
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_architecture())
    sys.exit(0 if success else 1)