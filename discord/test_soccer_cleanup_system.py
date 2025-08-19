"""
Integration Tests for Soccer Cleanup System
Tests automated cleanup, manual cleanup, and edge cases
"""

import pytest
import asyncio
import discord
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List

# Import the classes we're testing
from soccer_cleanup_system import SoccerCleanupSystem, CleanupStats, ChannelInfo
from soccer_channel_manager import SoccerChannelManager
from soccer_error_handling import ErrorContext

class MockChannel:
    """Mock Discord TextChannel for testing"""
    
    def __init__(self, name: str, created_at: datetime, channel_id: int = None):
        self.name = name
        self.created_at = created_at
        self.id = channel_id or hash(name) % 1000000
        self.mention = f"<#{self.id}>"
        self._messages = []
        self._pinned_messages = []
        self._deleted = False
    
    async def delete(self, reason: str = None):
        """Mock channel deletion"""
        if self._deleted:
            raise discord.HTTPException(response=MagicMock(), message="Channel already deleted")
        self._deleted = True
    
    async def pins(self):
        """Mock pinned messages"""
        return self._pinned_messages
    
    def history(self, limit: int = None, after: datetime = None):
        """Mock message history"""
        messages = self._messages
        if after:
            messages = [msg for msg in messages if msg.created_at > after]
        if limit:
            messages = messages[:limit]
        
        class AsyncIterator:
            def __init__(self, items):
                self.items = iter(messages)
            
            def __aiter__(self):
                return self
            
            async def __anext__(self):
                try:
                    return next(self.items)
                except StopIteration:
                    raise StopAsyncIteration
        
        return AsyncIterator(messages)
    
    def add_message(self, content: str, created_at: datetime = None):
        """Add a mock message to the channel"""
        if created_at is None:
            created_at = datetime.utcnow()
        
        message = MagicMock()
        message.content = content
        message.created_at = created_at
        self._messages.append(message)
    
    def add_pinned_message(self, content: str):
        """Add a mock pinned message to the channel"""
        message = MagicMock()
        message.content = content
        self._pinned_messages.append(message)

class MockCategory:
    """Mock Discord CategoryChannel for testing"""
    
    def __init__(self, name: str):
        self.name = name
        self.channels = []
    
    def add_channel(self, channel: MockChannel):
        """Add a channel to this category"""
        self.channels.append(channel)

class MockGuild:
    """Mock Discord Guild for testing"""
    
    def __init__(self, name: str, guild_id: int = 12345):
        self.name = name
        self.id = guild_id
        self.categories = []
        self.text_channels = []
    
    def add_category(self, category: MockCategory):
        """Add a category to this guild"""
        self.categories.append(category)

class TestSoccerCleanupSystem:
    """Test suite for SoccerCleanupSystem"""
    
    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot instance"""
        bot = MagicMock()
        bot.guilds = []
        bot.wait_until_ready = AsyncMock()
        return bot
    
    @pytest.fixture
    def mock_channel_manager(self):
        """Create a mock SoccerChannelManager"""
        manager = MagicMock()
        manager.category_name = "⚽ SOCCER"
        manager.channel_prefix = "📊"
        return manager
    
    @pytest.fixture
    def cleanup_system(self, mock_bot, mock_channel_manager):
        """Create a SoccerCleanupSystem instance for testing"""
        with patch('soccer_cleanup_system.tasks'):  # Mock the tasks decorator
            system = SoccerCleanupSystem(mock_bot, mock_channel_manager)
            # Stop the scheduled task for testing
            if hasattr(system, 'scheduled_cleanup_task'):
                system.scheduled_cleanup_task.cancel()
            return system
    
    @pytest.fixture
    def sample_guild(self):
        """Create a sample guild with soccer channels"""
        guild = MockGuild("Test Guild")
        
        # Create soccer category
        soccer_category = MockCategory("⚽ SOCCER")
        
        # Create channels with different ages
        now = datetime.utcnow()
        
        # Old channels (should be deleted)
        old_channel_1 = MockChannel("📊 08-15-liverpool-vs-arsenal", now - timedelta(days=5))
        old_channel_2 = MockChannel("📊 08-14-chelsea-vs-tottenham", now - timedelta(days=6))
        
        # Recent channels (should be preserved)
        recent_channel = MockChannel("📊 08-18-manchester-vs-city", now - timedelta(hours=12))
        
        # Old channel with recent activity (should be preserved)
        active_old_channel = MockChannel("📊 08-13-barcelona-vs-madrid", now - timedelta(days=4))
        active_old_channel.add_message("Great match!", now - timedelta(hours=2))
        
        # Old channel with pinned messages (should be preserved)
        pinned_old_channel = MockChannel("📊 08-12-juventus-vs-milan", now - timedelta(days=7))
        pinned_old_channel.add_pinned_message("Match highlights")
        
        # Add channels to category
        for channel in [old_channel_1, old_channel_2, recent_channel, active_old_channel, pinned_old_channel]:
            soccer_category.add_channel(channel)
        
        guild.add_category(soccer_category)
        return guild
    
    @pytest.mark.asyncio
    async def test_cleanup_old_channels_basic(self, cleanup_system, sample_guild):
        """Test basic cleanup functionality"""
        
        # Mock the _find_soccer_category method
        soccer_category = sample_guild.categories[0]
        cleanup_system._find_soccer_category = AsyncMock(return_value=soccer_category)
        
        # Run cleanup with 3-day retention
        stats = await cleanup_system.cleanup_old_channels(sample_guild, days_old=3)
        
        # Verify statistics
        assert stats.total_processed == 5  # 5 channels total
        assert stats.channels_deleted == 2  # 2 old channels without special preservation
        assert stats.channels_preserved == 3  # 3 channels preserved (recent, active, pinned)
        assert stats.errors == 0
        
        # Verify specific channels were deleted
        old_channels = [ch for ch in soccer_category.channels if ch.name in [
            "📊 08-15-liverpool-vs-arsenal", "📊 08-14-chelsea-vs-tottenham"
        ]]
        for channel in old_channels:
            assert channel._deleted, f"Channel {channel.name} should have been deleted"
    
    @pytest.mark.asyncio
    async def test_cleanup_preserve_active_channels(self, cleanup_system, sample_guild):
        """Test preservation of channels with recent activity"""
        
        soccer_category = sample_guild.categories[0]
        cleanup_system._find_soccer_category = AsyncMock(return_value=soccer_category)
        
        # Run cleanup with activity preservation enabled
        stats = await cleanup_system.cleanup_old_channels(
            sample_guild, days_old=3, preserve_active=True
        )
        
        # Find the active old channel
        active_channel = next(ch for ch in soccer_category.channels 
                            if ch.name == "📊 08-13-barcelona-vs-madrid")
        
        # Verify it was preserved
        assert not active_channel._deleted, "Channel with recent activity should be preserved"
        assert stats.channels_with_activity >= 1
    
    @pytest.mark.asyncio
    async def test_cleanup_preserve_pinned_channels(self, cleanup_system, sample_guild):
        """Test preservation of channels with pinned messages"""
        
        soccer_category = sample_guild.categories[0]
        cleanup_system._find_soccer_category = AsyncMock(return_value=soccer_category)
        
        # Run cleanup with pinned message preservation enabled
        stats = await cleanup_system.cleanup_old_channels(
            sample_guild, days_old=3, preserve_pinned=True
        )
        
        # Find the pinned old channel
        pinned_channel = next(ch for ch in soccer_category.channels 
                            if ch.name == "📊 08-12-juventus-vs-milan")
        
        # Verify it was preserved
        assert not pinned_channel._deleted, "Channel with pinned messages should be preserved"
        assert stats.channels_with_pins >= 1
    
    @pytest.mark.asyncio
    async def test_cleanup_no_preservation(self, cleanup_system, sample_guild):
        """Test cleanup with all preservation disabled"""
        
        soccer_category = sample_guild.categories[0]
        cleanup_system._find_soccer_category = AsyncMock(return_value=soccer_category)
        
        # Run cleanup with all preservation disabled
        stats = await cleanup_system.cleanup_old_channels(
            sample_guild, days_old=3, preserve_active=False, preserve_pinned=False
        )
        
        # Should delete more channels when preservation is disabled
        assert stats.channels_deleted >= 3  # At least the 3 old channels
    
    @pytest.mark.asyncio
    async def test_cleanup_no_soccer_category(self, cleanup_system):
        """Test cleanup when no soccer category exists"""
        
        guild = MockGuild("Empty Guild")
        cleanup_system._find_soccer_category = AsyncMock(return_value=None)
        
        stats = await cleanup_system.cleanup_old_channels(guild)
        
        assert stats.total_processed == 0
        assert stats.channels_deleted == 0
        assert stats.channels_preserved == 0
    
    @pytest.mark.asyncio
    async def test_cleanup_no_channels(self, cleanup_system):
        """Test cleanup when soccer category has no channels"""
        
        guild = MockGuild("Guild with Empty Category")
        empty_category = MockCategory("⚽ SOCCER")
        guild.add_category(empty_category)
        
        cleanup_system._find_soccer_category = AsyncMock(return_value=empty_category)
        
        stats = await cleanup_system.cleanup_old_channels(guild)
        
        assert stats.total_processed == 0
        assert stats.channels_deleted == 0
        assert stats.channels_preserved == 0
    
    @pytest.mark.asyncio
    async def test_cleanup_with_errors(self, cleanup_system, sample_guild):
        """Test cleanup handling of deletion errors"""
        
        soccer_category = sample_guild.categories[0]
        cleanup_system._find_soccer_category = AsyncMock(return_value=soccer_category)
        
        # Make one channel fail to delete
        error_channel = soccer_category.channels[0]
        original_delete = error_channel.delete
        
        async def failing_delete(reason=None):
            raise discord.HTTPException(response=MagicMock(), message="Permission denied")
        
        error_channel.delete = failing_delete
        
        stats = await cleanup_system.cleanup_old_channels(sample_guild, days_old=3)
        
        # Should have some errors
        assert stats.errors > 0
        assert stats.channels_deleted < stats.total_processed
    
    @pytest.mark.asyncio
    async def test_channel_limit_management(self, cleanup_system):
        """Test channel limit management functionality"""
        
        guild = MockGuild("Limit Test Guild")
        soccer_category = MockCategory("⚽ SOCCER")
        
        # Create many channels to exceed limit
        now = datetime.utcnow()
        for i in range(55):  # Exceed the 50 channel limit
            channel = MockChannel(f"📊 08-{i:02d}-team1-vs-team2", now - timedelta(days=i % 10))
            soccer_category.add_channel(channel)
        
        guild.add_category(soccer_category)
        cleanup_system._find_soccer_category = AsyncMock(return_value=soccer_category)
        
        results = await cleanup_system.channel_limit_management(guild)
        
        # Should remove some channels
        assert results["channels_removed"] > 0
        assert results["channels_remaining"] <= cleanup_system.max_channels_per_category
    
    @pytest.mark.asyncio
    async def test_priority_score_calculation(self, cleanup_system):
        """Test priority score calculation for channel preservation"""
        
        now = datetime.utcnow()
        cutoff_date = now - timedelta(days=3)
        
        # Test different channel scenarios
        test_cases = [
            {
                "name": "Recent channel",
                "created_at": now - timedelta(hours=12),
                "expected_score": ">0",  # Should be preserved
            },
            {
                "name": "Old channel with activity",
                "created_at": now - timedelta(days=5),
                "last_message_at": now - timedelta(hours=2),
                "expected_score": ">0",  # Should be preserved
            },
            {
                "name": "Old channel with pins",
                "created_at": now - timedelta(days=5),
                "has_pinned_messages": True,
                "expected_score": ">0",  # Should be preserved
            },
            {
                "name": "Old inactive channel",
                "created_at": now - timedelta(days=5),
                "expected_score": "0",  # Should be deleted
            },
        ]
        
        for case in test_cases:
            info = ChannelInfo(
                channel=MagicMock(),
                created_at=case["created_at"],
                last_message_at=case.get("last_message_at"),
                has_pinned_messages=case.get("has_pinned_messages", False),
                message_count=case.get("message_count", 0)
            )
            
            score = cleanup_system._calculate_priority_score(
                info, cutoff_date, preserve_active=True, preserve_pinned=True
            )
            
            if case["expected_score"] == ">0":
                assert score > 0, f"Case '{case['name']}' should have score > 0, got {score}"
            elif case["expected_score"] == "0":
                assert score == 0, f"Case '{case['name']}' should have score = 0, got {score}"
    
    @pytest.mark.asyncio
    async def test_match_date_extraction(self, cleanup_system):
        """Test extraction of match dates from channel names"""
        
        test_cases = [
            ("📊 08-17-liverpool-vs-arsenal", "should extract August 17"),
            ("📊 12-25-chelsea-vs-tottenham", "should extract December 25"),
            ("📊 invalid-format", "should return None for invalid format"),
            ("not-a-match-channel", "should return None for non-match channel"),
        ]
        
        for channel_name, description in test_cases:
            channel = MockChannel(channel_name, datetime.utcnow())
            result = cleanup_system._extract_match_date_from_channel(channel)
            
            if "should extract" in description:
                assert result is not None, f"Failed to extract date from {channel_name}"
                assert isinstance(result, datetime), f"Expected datetime, got {type(result)}"
            else:
                assert result is None, f"Should not extract date from {channel_name}"
    
    def test_cleanup_stats_properties(self):
        """Test CleanupStats calculated properties"""
        
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(seconds=30)
        
        stats = CleanupStats(
            channels_deleted=8,
            channels_preserved=2,
            errors=1,
            total_processed=10,
            start_time=start_time,
            end_time=end_time
        )
        
        # Test duration calculation
        assert stats.duration == timedelta(seconds=30)
        
        # Test success rate calculation
        expected_success_rate = ((10 - 1) / 10) * 100  # 90%
        assert stats.success_rate == expected_success_rate
    
    def test_cleanup_stats_edge_cases(self):
        """Test CleanupStats edge cases"""
        
        # Test with zero processed channels
        stats = CleanupStats(total_processed=0)
        assert stats.success_rate == 0.0
        
        # Test with no timing information
        stats = CleanupStats()
        assert stats.duration is None
    
    @pytest.mark.asyncio
    async def test_batch_deletion_rate_limiting(self, cleanup_system, sample_guild):
        """Test that batch deletion respects rate limits"""
        
        soccer_category = sample_guild.categories[0]
        cleanup_system._find_soccer_category = AsyncMock(return_value=soccer_category)
        
        # Create many old channels
        now = datetime.utcnow()
        for i in range(25):  # Create more channels than batch size
            channel = MockChannel(f"📊 08-{i:02d}-old-match", now - timedelta(days=5))
            soccer_category.add_channel(channel)
        
        # Mock rate limiting
        rate_limit_count = 0
        original_sleep = asyncio.sleep
        
        async def mock_sleep(duration):
            nonlocal rate_limit_count
            if duration >= cleanup_system.cleanup_delay_between_batches:
                rate_limit_count += 1
            await original_sleep(0.01)  # Very short sleep for testing
        
        with patch('asyncio.sleep', side_effect=mock_sleep):
            stats = await cleanup_system.cleanup_old_channels(sample_guild, days_old=3)
        
        # Should have used batching (and thus rate limiting delays)
        assert rate_limit_count > 0, "Should have used batch delays for rate limiting"
    
    def test_get_cleanup_statistics(self, cleanup_system):
        """Test cleanup statistics retrieval"""
        
        # Set some test data
        cleanup_system.total_cleanups_performed = 5
        cleanup_system.last_cleanup_stats = CleanupStats(
            channels_deleted=3,
            channels_preserved=2,
            total_processed=5,
            start_time=datetime.utcnow() - timedelta(minutes=1),
            end_time=datetime.utcnow()
        )
        
        stats = cleanup_system.get_cleanup_statistics()
        
        # Verify structure
        assert "system_info" in stats
        assert "last_cleanup" in stats
        
        # Verify system info
        system_info = stats["system_info"]
        assert system_info["total_cleanups_performed"] == 5
        assert system_info["default_retention_days"] == cleanup_system.default_retention_days
        
        # Verify last cleanup info
        last_cleanup = stats["last_cleanup"]
        assert last_cleanup["channels_deleted"] == 3
        assert last_cleanup["channels_preserved"] == 2
        assert last_cleanup["total_processed"] == 5

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])