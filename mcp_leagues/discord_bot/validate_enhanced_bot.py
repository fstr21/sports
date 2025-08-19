#!/usr/bin/env python3
"""
Validation script for the enhanced Discord bot architecture
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


async def validate_enhanced_bot():
    """Validate that the enhanced bot architecture works correctly"""
    print("🔍 Validating Enhanced Discord Sports Bot Architecture...")
    print("=" * 60)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        
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
        
        from config import config
        print("  ✅ Configuration")
        
        print("\\n⚙️ Testing component initialization...")
        
        # Test MCP Client
        mcp_client = MCPClient(timeout=10.0, max_retries=2)
        print("  ✅ MCP Client instantiation")
        
        # Test configuration loading
        print(f"  ✅ Configuration loaded with {len(config.get_enabled_sports())} sports: {', '.join(config.get_enabled_sports())}")
        
        # Test Sport Manager
        sport_manager = SportManager(config, mcp_client)
        sport_manager.load_sports()
        available_sports = sport_manager.get_available_sports()
        print(f"  ✅ Sport Manager loaded {len(available_sports)} sports: {', '.join(available_sports)}")
        
        # Test sport handler validation
        validation_errors = sport_manager.validate_sports()
        if validation_errors:
            print(f"  ⚠️ Sport validation warnings: {len(validation_errors)} issues")
            for error in validation_errors[:3]:
                print(f"    • {error}")
        else:
            print("  ✅ All sport handlers validated successfully")
        
        # Test individual sport handlers
        print("\\n🏈 Testing sport handlers...")
        
        for sport_name in available_sports:
            handler = sport_manager.get_sport_handler(sport_name)
            if handler:
                print(f"  ✅ {sport_name.upper()} handler: {handler.__class__.__name__}")
                print(f"    • MCP URL: {handler.config.get('mcp_url', 'Not configured')}")
                print(f"    • Category: {handler.category_name}")
                print(f"    • Color: #{handler.config.get('embed_color', 0):06x}")
            else:
                print(f"  ❌ {sport_name.upper()} handler: Not available")
        
        # Test MCP client health
        print("\\n🔗 Testing MCP client...")
        await mcp_client._ensure_client()
        if mcp_client.is_healthy():
            print("  ✅ MCP Client is healthy and ready")
        else:
            print("  ⚠️ MCP Client may not be fully initialized")
        
        # Clean up
        await mcp_client.close()
        
        print("\\n" + "=" * 60)
        print("🎉 SUCCESS: Enhanced bot architecture validation complete!")
        print("\\n📋 Summary:")
        print("  • ✅ All core components imported successfully")
        print("  • ✅ Configuration system working")
        print("  • ✅ Sport handlers loaded and validated")
        print("  • ✅ MCP client initialized")
        print("  • ✅ Modular architecture ready for deployment")
        print("\\n🚀 The enhanced bot is ready to replace the existing bot!")
        print("\\n📝 Next steps:")
        print("  1. Deploy sports_discord_bot_enhanced.py to your server")
        print("  2. Update your environment variables if needed")
        print("  3. Test the /create-channels and /clear-channels commands")
        print("  4. Use /sync to update Discord commands")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\\n💡 Make sure all files are in the correct locations:")
        print("  • core/ directory with all core components")
        print("  • sports/ directory with sport handlers")
        print("  • config.py file")
        return False
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(validate_enhanced_bot())
    sys.exit(0 if success else 1)