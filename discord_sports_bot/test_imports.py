#!/usr/bin/env python3
"""
Simple test to verify core components can be imported correctly
"""

def test_core_imports():
    """Test that all core components can be imported"""
    try:
        # Test core imports
        from discord_sports_bot.core import (
            BaseSportHandler, 
            MCPClient, 
            SportManager, 
            SyncManager, 
            CommandRouter, 
            ErrorHandler
        )
        print("✅ Core components imported successfully")
        
        # Test config imports
        from discord_sports_bot.config.models import BotConfig, SportConfig, DiscordConfig
        from discord_sports_bot.config.manager import ConfigManager
        print("✅ Configuration components imported successfully")
        
        # Test formatter imports
        from discord_sports_bot.formatters.base_formatter import BaseFormatter
        print("✅ Formatter components imported successfully")
        
        print("\\n🎉 All core infrastructure components are properly set up!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_core_imports()