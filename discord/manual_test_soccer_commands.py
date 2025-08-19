"""
Manual Test for Soccer Slash Commands
Simple verification that commands are properly structured
"""

import asyncio
import sys
import os

# Add the discord directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_command_imports():
    """Test that we can import all soccer commands"""
    print("Testing command imports...")
    
    try:
        from bot_structure import (
            soccer_schedule_command,
            soccer_odds_command, 
            soccer_h2h_command,
            soccer_standings_command,
            validate_date_input
        )
        print("✅ All soccer commands imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_date_validation():
    """Test date validation function"""
    print("\nTesting date validation...")
    
    try:
        from bot_structure import validate_date_input
        
        # Test valid dates
        test_cases = [
            ("2025-08-18", "2025-08-18"),
            ("08/18/2025", "2025-08-18"),
            ("18-08-2025", "2025-08-18")
        ]
        
        for input_date, expected in test_cases:
            result = validate_date_input(input_date)
            if result == expected:
                print(f"✅ {input_date} -> {result}")
            else:
                print(f"❌ {input_date} -> {result} (expected {expected})")
                return False
        
        # Test invalid date
        try:
            validate_date_input("invalid-date")
            print("❌ Should have raised ValueError for invalid date")
            return False
        except ValueError:
            print("✅ Invalid date properly rejected")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_command_structure():
    """Test that commands have proper structure"""
    print("\nTesting command structure...")
    
    try:
        from bot_structure import (
            soccer_schedule_command,
            soccer_odds_command,
            soccer_h2h_command,
            soccer_standings_command
        )
        
        # Check if commands exist and have proper structure
        commands = [
            ("soccer_schedule_command", soccer_schedule_command),
            ("soccer_odds_command", soccer_odds_command),
            ("soccer_h2h_command", soccer_h2h_command),
            ("soccer_standings_command", soccer_standings_command)
        ]
        
        for name, cmd in commands:
            print(f"✅ {name} exists (type: {type(cmd).__name__})")
            
            # Check if it's a Discord command object
            if hasattr(cmd, 'callback'):
                print(f"✅ {name} has callback function")
                if asyncio.iscoroutinefunction(cmd.callback):
                    print(f"✅ {name} callback is async")
                else:
                    print(f"❌ {name} callback is not async")
                    return False
            elif callable(cmd):
                print(f"✅ {name} is callable")
                if asyncio.iscoroutinefunction(cmd):
                    print(f"✅ {name} is async function")
                else:
                    print(f"❌ {name} is not async function")
                    return False
            else:
                print(f"❌ {name} is not callable or command object")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_bot_structure():
    """Test that bot structure is properly set up"""
    print("\nTesting bot structure...")
    
    try:
        from bot_structure import bot
        
        if hasattr(bot, 'tree'):
            print("✅ Bot has command tree")
        else:
            print("❌ Bot missing command tree")
            return False
            
        if hasattr(bot, 'soccer_channel_manager'):
            print("✅ Bot has soccer channel manager")
        else:
            print("❌ Bot missing soccer channel manager")
            return False
            
        if hasattr(bot, 'soccer_data_processor'):
            print("✅ Bot has soccer data processor")
        else:
            print("❌ Bot missing soccer data processor")
            return False
            
        if hasattr(bot, 'soccer_embed_builder'):
            print("✅ Bot has soccer embed builder")
        else:
            print("❌ Bot missing soccer embed builder")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Soccer Commands Manual Test\n")
    
    tests = [
        test_command_imports,
        test_date_validation,
        test_command_structure,
        test_bot_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Soccer commands are properly implemented.")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)