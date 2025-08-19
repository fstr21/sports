#!/usr/bin/env python3
"""
Integration test for the enhanced /create-channels command
Tests the complete workflow without requiring Discord connection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

def test_command_structure():
    """Test that the command is properly structured"""
    print("Testing command structure...")
    
    try:
        from bot_structure import bot
        
        # Check that the command exists
        commands = [cmd.name for cmd in bot.tree.get_commands()]
        if "create-channels" in commands:
            print("✅ /create-channels command is registered")
        else:
            print("❌ /create-channels command not found")
            return False
        
        # Check that soccer components are initialized
        if hasattr(bot, 'soccer_channel_manager'):
            print("✅ Soccer channel manager initialized")
        else:
            print("❌ Soccer channel manager not initialized")
            return False
            
        if hasattr(bot, 'soccer_data_processor'):
            print("✅ Soccer data processor initialized")
        else:
            print("❌ Soccer data processor not initialized")
            return False
            
        if hasattr(bot, 'soccer_embed_builder'):
            print("✅ Soccer embed builder initialized")
        else:
            print("❌ Soccer embed builder not initialized")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing command structure: {e}")
        return False

def test_mock_soccer_workflow():
    """Test the soccer workflow with mock data"""
    print("\nTesting mock soccer workflow...")
    
    try:
        from bot_structure import validate_date_input, handle_soccer_channel_creation
        from soccer_integration import SoccerMCPClient, SoccerDataProcessor
        from soccer_channel_manager import SoccerChannelManager
        
        # Test date validation
        test_date = "08/17/2025"
        validated_date = validate_date_input(test_date)
        print(f"✅ Date validation: {test_date} -> {validated_date}")
        
        # Test component instantiation
        client = SoccerMCPClient()
        processor = SoccerDataProcessor()
        print("✅ Soccer components instantiated successfully")
        
        # Test mock data processing
        mock_matches_data = {
            "matches_by_league": {
                "Premier League": {
                    "league_info": {
                        "id": 228,
                        "name": "Premier League",
                        "country": "England"
                    },
                    "matches": [
                        {
                            "id": 12345,
                            "date": "2025-08-17",
                            "time": "15:00",
                            "venue": "Old Trafford",
                            "status": "scheduled",
                            "home_team": {
                                "id": 1,
                                "name": "Manchester United",
                                "short_name": "MUN"
                            },
                            "away_team": {
                                "id": 2,
                                "name": "Liverpool",
                                "short_name": "LIV"
                            },
                            "odds": {
                                "home_win": 2.50,
                                "draw": 3.20,
                                "away_win": 2.80
                            }
                        }
                    ]
                }
            }
        }
        
        processed_matches = processor.process_match_data(mock_matches_data)
        if processed_matches and len(processed_matches) == 1:
            print(f"✅ Mock data processed: {len(processed_matches)} matches")
            match = processed_matches[0]
            print(f"   Match: {match.away_team.name} vs {match.home_team.name}")
            print(f"   Channel name: {match.channel_name}")
        else:
            print("❌ Mock data processing failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in mock workflow test: {e}")
        return False

def test_error_handling():
    """Test error handling scenarios"""
    print("\nTesting error handling...")
    
    try:
        from bot_structure import validate_date_input
        from soccer_integration import SoccerDataProcessor
        
        # Test invalid date handling
        try:
            validate_date_input("invalid-date")
            print("❌ Invalid date should have raised ValueError")
            return False
        except ValueError:
            print("✅ Invalid date correctly rejected")
        
        # Test empty data handling
        processor = SoccerDataProcessor()
        empty_result = processor.process_match_data({})
        if empty_result == []:
            print("✅ Empty data handled gracefully")
        else:
            print("❌ Empty data not handled correctly")
            return False
        
        # Test malformed data handling
        malformed_data = {"invalid": "structure"}
        malformed_result = processor.process_match_data(malformed_data)
        if malformed_result == []:
            print("✅ Malformed data handled gracefully")
        else:
            print("❌ Malformed data not handled correctly")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in error handling test: {e}")
        return False

def test_channel_naming():
    """Test channel naming conventions"""
    print("\nTesting channel naming...")
    
    try:
        from soccer_channel_manager import SoccerChannelManager
        from soccer_integration import Team, League, ProcessedMatch
        
        # Create mock objects
        home_team = Team(1, "Manchester United", "MUN")
        away_team = Team(2, "Liverpool FC", "LIV")
        league = League(228, "Premier League", "England")
        
        match = ProcessedMatch(
            match_id=12345,
            home_team=home_team,
            away_team=away_team,
            league=league,
            date="2025-08-17",
            time="15:00",
            venue="Old Trafford",
            status="scheduled"
        )
        
        # Test channel name generation
        manager = SoccerChannelManager(None)  # Mock bot
        channel_name = manager.generate_channel_name(match, "2025-08-17")
        
        expected_pattern = "📊 08-17-liverpool-fc-vs-manchester-united"
        if channel_name == expected_pattern:
            print(f"✅ Channel name generated correctly: {channel_name}")
        else:
            print(f"❌ Channel name incorrect: {channel_name} (expected: {expected_pattern})")
            return False
        
        # Test team name cleaning
        cleaned_name = manager._clean_team_name_for_channel("Manchester United F.C.")
        expected_clean = "manchester-united-fc"
        if cleaned_name == expected_clean:
            print(f"✅ Team name cleaned correctly: {cleaned_name}")
        else:
            print(f"❌ Team name cleaning incorrect: {cleaned_name} (expected: {expected_clean})")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in channel naming test: {e}")
        return False

async def run_all_tests():
    """Run all integration tests"""
    print("🧪 Running integration tests for /create-channels command\n")
    
    tests = [
        test_command_structure,
        test_mock_soccer_workflow,
        test_error_handling,
        test_channel_naming
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All integration tests passed! The /create-channels command is ready.")
    else:
        print("❌ Some tests failed. Please review the implementation.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(run_all_tests())