"""
Simple integration test runner for Soccer Cleanup System
Tests the basic functionality without requiring a full Discord bot setup
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock

# Add the discord directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

# Import our cleanup system
from soccer_cleanup_system import SoccerCleanupSystem, CleanupStats

class MockBot:
    """Simple mock bot for testing"""
    def __init__(self):
        self.guilds = []
        self.wait_until_ready = AsyncMock()

class MockChannelManager:
    """Simple mock channel manager for testing"""
    def __init__(self):
        self.category_name = "⚽ SOCCER"
        self.channel_prefix = "📊"

class MockChannel:
    """Simple mock channel for testing"""
    def __init__(self, name: str, created_at: datetime):
        self.name = name
        self.created_at = created_at
        self.id = hash(name) % 1000000
        self._deleted = False
        self._messages = []
        self._pinned_messages = []
    
    async def delete(self, reason: str = None):
        """Mock deletion"""
        print(f"  Deleting channel: {self.name} (reason: {reason})")
        self._deleted = True
    
    async def pins(self):
        """Mock pinned messages"""
        return self._pinned_messages
    
    def history(self, limit: int = None, after: datetime = None):
        """Mock message history"""
        class AsyncIterator:
            def __init__(self, messages):
                self.messages = iter(messages)
            
            def __aiter__(self):
                return self
            
            async def __anext__(self):
                try:
                    return next(self.messages)
                except StopIteration:
                    raise StopAsyncIteration
        
        messages = self._messages
        if after:
            messages = [msg for msg in messages if msg.created_at > after]
        if limit:
            messages = messages[:limit]
        
        return AsyncIterator(messages)
    
    def add_message(self, content: str, created_at: datetime = None):
        """Add a mock message"""
        if created_at is None:
            created_at = datetime.utcnow()
        
        message = MagicMock()
        message.content = content
        message.created_at = created_at
        self._messages.append(message)
    
    def add_pinned_message(self, content: str):
        """Add a mock pinned message"""
        message = MagicMock()
        message.content = content
        self._pinned_messages.append(message)

class MockCategory:
    """Simple mock category for testing"""
    def __init__(self, name: str):
        self.name = name
        self.channels = []

class MockGuild:
    """Simple mock guild for testing"""
    def __init__(self, name: str):
        self.name = name
        self.id = 12345
        self.categories = []

async def test_basic_cleanup():
    """Test basic cleanup functionality"""
    print("Testing basic cleanup functionality...")
    
    # Create mock objects
    bot = MockBot()
    channel_manager = MockChannelManager()
    
    # Create cleanup system (disable scheduled task for testing)
    import soccer_cleanup_system
    original_tasks = soccer_cleanup_system.tasks
    soccer_cleanup_system.tasks = MagicMock()  # Mock the tasks decorator
    
    cleanup_system = SoccerCleanupSystem(bot, channel_manager)
    
    # Create test guild with channels
    guild = MockGuild("Test Guild")
    soccer_category = MockCategory("⚽ SOCCER")
    
    # Create channels with different ages
    now = datetime.utcnow()
    
    # Old channels (should be deleted)
    old_channel_1 = MockChannel("📊 08-15-liverpool-vs-arsenal", now - timedelta(days=5))
    old_channel_2 = MockChannel("📊 08-14-chelsea-vs-tottenham", now - timedelta(days=6))
    
    # Recent channel (should be preserved)
    recent_channel = MockChannel("📊 08-18-manchester-vs-city", now - timedelta(hours=12))
    
    # Old channel with recent activity (should be preserved)
    active_old_channel = MockChannel("📊 08-13-barcelona-vs-madrid", now - timedelta(days=4))
    active_old_channel.add_message("Great match!", now - timedelta(hours=2))
    
    # Old channel with pinned messages (should be preserved)
    pinned_old_channel = MockChannel("📊 08-12-juventus-vs-milan", now - timedelta(days=7))
    pinned_old_channel.add_pinned_message("Match highlights")
    
    # Add channels to category
    soccer_category.channels = [old_channel_1, old_channel_2, recent_channel, active_old_channel, pinned_old_channel]
    guild.categories = [soccer_category]
    
    # Mock the _find_soccer_category method
    cleanup_system._find_soccer_category = AsyncMock(return_value=soccer_category)
    
    # Mock the _get_soccer_match_channels method to return our test channels
    cleanup_system._get_soccer_match_channels = AsyncMock(return_value=soccer_category.channels)
    
    print(f"  Created {len(soccer_category.channels)} test channels")
    
    # Run cleanup
    print("  Running cleanup with 3-day retention...")
    stats = await cleanup_system.cleanup_old_channels(guild, days_old=3)
    
    # Print results
    print(f"  Results:")
    print(f"    Total processed: {stats.total_processed}")
    print(f"    Channels deleted: {stats.channels_deleted}")
    print(f"    Channels preserved: {stats.channels_preserved}")
    print(f"    Channels with activity: {stats.channels_with_activity}")
    print(f"    Channels with pins: {stats.channels_with_pins}")
    print(f"    Errors: {stats.errors}")
    print(f"    Success rate: {stats.success_rate:.1f}%")
    
    # Verify results
    assert stats.total_processed == 5, f"Expected 5 channels processed, got {stats.total_processed}"
    assert stats.channels_deleted == 2, f"Expected 2 channels deleted, got {stats.channels_deleted}"
    assert stats.channels_preserved == 3, f"Expected 3 channels preserved, got {stats.channels_preserved}"
    assert stats.errors == 0, f"Expected 0 errors, got {stats.errors}"
    
    # Check which channels were deleted
    deleted_channels = [ch for ch in soccer_category.channels if ch._deleted]
    preserved_channels = [ch for ch in soccer_category.channels if not ch._deleted]
    
    print(f"  Deleted channels: {[ch.name for ch in deleted_channels]}")
    print(f"  Preserved channels: {[ch.name for ch in preserved_channels]}")
    
    # Verify specific channels
    assert old_channel_1._deleted, "Old channel 1 should be deleted"
    assert old_channel_2._deleted, "Old channel 2 should be deleted"
    assert not recent_channel._deleted, "Recent channel should be preserved"
    assert not active_old_channel._deleted, "Active old channel should be preserved"
    assert not pinned_old_channel._deleted, "Pinned old channel should be preserved"
    
    print("✅ Basic cleanup test passed!")
    
    # Restore original tasks
    soccer_cleanup_system.tasks = original_tasks

async def test_priority_scoring():
    """Test priority scoring system"""
    print("\nTesting priority scoring system...")
    
    # Create mock objects
    bot = MockBot()
    channel_manager = MockChannelManager()
    
    # Create cleanup system (disable scheduled task for testing)
    import soccer_cleanup_system
    original_tasks = soccer_cleanup_system.tasks
    soccer_cleanup_system.tasks = MagicMock()
    
    cleanup_system = SoccerCleanupSystem(bot, channel_manager)
    
    now = datetime.utcnow()
    cutoff_date = now - timedelta(days=3)
    
    # Test different scenarios
    from soccer_cleanup_system import ChannelInfo
    
    test_cases = [
        {
            "name": "Recent channel",
            "info": ChannelInfo(
                channel=MagicMock(),
                created_at=now - timedelta(hours=12)
            ),
            "should_preserve": True
        },
        {
            "name": "Old channel with activity",
            "info": ChannelInfo(
                channel=MagicMock(),
                created_at=now - timedelta(days=5),
                last_message_at=now - timedelta(hours=2)
            ),
            "should_preserve": True
        },
        {
            "name": "Old channel with pins",
            "info": ChannelInfo(
                channel=MagicMock(),
                created_at=now - timedelta(days=5),
                has_pinned_messages=True
            ),
            "should_preserve": True
        },
        {
            "name": "Old inactive channel",
            "info": ChannelInfo(
                channel=MagicMock(),
                created_at=now - timedelta(days=5)
            ),
            "should_preserve": False
        }
    ]
    
    for case in test_cases:
        score = cleanup_system._calculate_priority_score(
            case["info"], cutoff_date, preserve_active=True, preserve_pinned=True
        )
        
        print(f"  {case['name']}: score = {score}")
        
        if case["should_preserve"]:
            assert score > 0, f"{case['name']} should have score > 0, got {score}"
        else:
            assert score == 0, f"{case['name']} should have score = 0, got {score}"
    
    print("✅ Priority scoring test passed!")
    
    # Restore original tasks
    soccer_cleanup_system.tasks = original_tasks

async def test_statistics():
    """Test statistics functionality"""
    print("\nTesting statistics functionality...")
    
    # Create mock objects
    bot = MockBot()
    channel_manager = MockChannelManager()
    
    # Create cleanup system (disable scheduled task for testing)
    import soccer_cleanup_system
    original_tasks = soccer_cleanup_system.tasks
    soccer_cleanup_system.tasks = MagicMock()
    
    cleanup_system = SoccerCleanupSystem(bot, channel_manager)
    
    # Set some test data
    cleanup_system.total_cleanups_performed = 5
    cleanup_system.last_cleanup_stats = CleanupStats(
        channels_deleted=3,
        channels_preserved=2,
        total_processed=5,
        start_time=datetime.utcnow() - timedelta(minutes=1),
        end_time=datetime.utcnow()
    )
    
    # Get statistics
    stats = cleanup_system.get_cleanup_statistics()
    
    print(f"  System info: {stats['system_info']}")
    print(f"  Last cleanup: {stats['last_cleanup']}")
    
    # Verify structure
    assert "system_info" in stats
    assert "last_cleanup" in stats
    
    # Verify values
    assert stats["system_info"]["total_cleanups_performed"] == 5
    assert stats["last_cleanup"]["channels_deleted"] == 3
    assert stats["last_cleanup"]["channels_preserved"] == 2
    
    print("✅ Statistics test passed!")
    
    # Restore original tasks
    soccer_cleanup_system.tasks = original_tasks

async def main():
    """Run all tests"""
    print("🧹 Soccer Cleanup System Integration Tests")
    print("=" * 50)
    
    try:
        await test_basic_cleanup()
        await test_priority_scoring()
        await test_statistics()
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)