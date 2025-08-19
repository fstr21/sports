#!/usr/bin/env python3
"""
Test script for the /create-channels command with soccer support
Tests the date validation and basic functionality without Discord connection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import asyncio

# Import the validation function
from bot_structure import validate_date_input

def test_date_validation():
    """Test the date validation function"""
    print("Testing date validation...")
    
    # Test valid formats
    test_cases = [
        ("08/17/2025", "2025-08-17"),  # MM/DD/YYYY
        ("17-08-2025", "2025-08-17"),  # DD-MM-YYYY
        ("2025-08-17", "2025-08-17"),  # YYYY-MM-DD
    ]
    
    for input_date, expected in test_cases:
        try:
            result = validate_date_input(input_date)
            if result == expected:
                print(f"✅ {input_date} -> {result}")
            else:
                print(f"❌ {input_date} -> {result} (expected {expected})")
        except Exception as e:
            print(f"❌ {input_date} -> Error: {e}")
    
    # Test invalid formats
    invalid_cases = [
        "invalid-date",
        "2025/13/01",  # Invalid month
        "32-01-2025",  # Invalid day
        "2020-01-01",  # Too far in past
    ]
    
    for invalid_date in invalid_cases:
        try:
            result = validate_date_input(invalid_date)
            print(f"❌ {invalid_date} should have failed but returned: {result}")
        except ValueError as e:
            print(f"✅ {invalid_date} -> Correctly rejected: {e}")
        except Exception as e:
            print(f"❌ {invalid_date} -> Unexpected error: {e}")

def test_soccer_imports():
    """Test that soccer integration imports work"""
    print("\nTesting soccer integration imports...")
    
    try:
        from soccer_integration import SoccerMCPClient, SoccerDataProcessor, SoccerEmbedBuilder
        print("✅ Soccer integration imports successful")
        
        # Test basic instantiation
        client = SoccerMCPClient()
        processor = SoccerDataProcessor()
        builder = SoccerEmbedBuilder()
        print("✅ Soccer component instantiation successful")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Instantiation error: {e}")

def test_channel_manager_import():
    """Test that channel manager imports work"""
    print("\nTesting channel manager import...")
    
    try:
        from soccer_channel_manager import SoccerChannelManager
        print("✅ Soccer channel manager import successful")
        
        # Test basic instantiation (without bot)
        # manager = SoccerChannelManager(None)  # Would need a bot instance
        print("✅ Soccer channel manager available")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing /create-channels command implementation\n")
    
    test_date_validation()
    test_soccer_imports()
    test_channel_manager_import()
    
    print("\n✅ All tests completed!")