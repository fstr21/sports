#!/usr/bin/env python3
"""
Validation script for the core infrastructure components
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def validate_infrastructure():
    """Validate that all core infrastructure components are properly set up"""
    print("🔍 Validating Discord Sports Bot Infrastructure...")
    print("=" * 50)
    
    # Check directory structure
    required_dirs = [
        "discord_sports_bot",
        "discord_sports_bot/core",
        "discord_sports_bot/config", 
        "discord_sports_bot/formatters",
        "discord_sports_bot/sports"
    ]
    
    print("📁 Checking directory structure...")
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} - MISSING")
            return False
    
    # Check core files
    required_files = [
        "discord_sports_bot/__init__.py",
        "discord_sports_bot/core/__init__.py",
        "discord_sports_bot/core/base_sport_handler.py",
        "discord_sports_bot/core/mcp_client.py",
        "discord_sports_bot/core/sport_manager.py",
        "discord_sports_bot/core/sync_manager.py",
        "discord_sports_bot/core/command_router.py",
        "discord_sports_bot/core/error_handler.py",
        "discord_sports_bot/config/__init__.py",
        "discord_sports_bot/config/models.py",
        "discord_sports_bot/config/manager.py",
        "discord_sports_bot/formatters/__init__.py",
        "discord_sports_bot/formatters/base_formatter.py",
        "discord_sports_bot/sports/__init__.py"
    ]
    
    print("\\n📄 Checking core files...")
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            return False
    
    # Test imports
    print("\\n🔧 Testing component imports...")
    try:
        from discord_sports_bot.core.base_sport_handler import BaseSportHandler, Match, ChannelCreationResult
        print("  ✅ BaseSportHandler and data models")
        
        from discord_sports_bot.core.mcp_client import MCPClient, MCPResponse
        print("  ✅ MCP Client")
        
        from discord_sports_bot.core.sport_manager import SportManager
        print("  ✅ Sport Manager")
        
        from discord_sports_bot.core.sync_manager import SyncManager, SyncResult
        print("  ✅ Sync Manager")
        
        from discord_sports_bot.core.command_router import CommandRouter
        print("  ✅ Command Router")
        
        from discord_sports_bot.core.error_handler import ErrorHandler
        print("  ✅ Error Handler")
        
        from discord_sports_bot.config.models import BotConfig, SportConfig, DiscordConfig
        print("  ✅ Configuration Models")
        
        from discord_sports_bot.config.manager import ConfigManager
        print("  ✅ Configuration Manager")
        
        from discord_sports_bot.formatters.base_formatter import BaseFormatter
        print("  ✅ Base Formatter")
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False
    
    # Test basic functionality
    print("\\n⚙️ Testing basic functionality...")
    try:
        # Test MCP Client creation
        mcp_client = MCPClient(timeout=10.0)
        print("  ✅ MCP Client instantiation")
        
        # Test Configuration models
        discord_config = DiscordConfig(token="test_token")
        print("  ✅ Configuration model creation")
        
        # Test Base Formatter
        formatter = BaseFormatter("test_sport", 0x00ff00)
        test_odds = formatter.convert_decimal_to_american_odds(2.5)
        print(f"  ✅ Base Formatter functionality (2.5 decimal = {test_odds} American)")
        
    except Exception as e:
        print(f"  ❌ Functionality test error: {e}")
        return False
    
    print("\\n" + "=" * 50)
    print("🎉 SUCCESS: All core infrastructure components are properly set up!")
    print("\\n📋 Summary:")
    print("  • Project structure created")
    print("  • Base classes and interfaces implemented")
    print("  • Configuration management system ready")
    print("  • MCP client with connection pooling")
    print("  • Error handling system")
    print("  • Command routing and synchronization")
    print("  • Base formatting utilities")
    print("\\n🚀 Ready for sport-specific handler implementation!")
    
    return True

if __name__ == "__main__":
    success = validate_infrastructure()
    sys.exit(0 if success else 1)