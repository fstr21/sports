"""
Integration tests for SoccerChannelManager
Tests channel creation, naming, cleanup, and management functionality
"""

import pytest
import asyncio
import discord
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from soccer_channel_manager import SoccerChannelManager, ProcessedMatch, Team, League

# Mock data classes for testing
from dataclasses import dataclass
from typing import Optional

@dataclass
class OddsFormat:
    decimal: float
    american: int
    
    @classmethod
    def from_decimal(cls, decimal_odds: float):
        american = int((decimal_odds - 1) * 100) if decimal_odds >= 2.0 else int(-100 / (decimal_odds - 1))
        return cls(decimal=decimal_odds, american=american)

@dataclass
class BettingOdds:
    home_win: Optional[OddsFormat] = None
    draw: Optional[OddsFormat] = None
    away_win: Optional[OddsFormat] = None

@dataclass
class H2HSummary:
    total_meetings: int
    home_team_wins: int
    away_team_wins: int
    draws: int
    last_meeting_result: Optional[str] = None


class TestSoccerChannelManager:
    """Test suite for SoccerChannelManager"""
    
    @pytest.fixture
    def mock_bot(self):
        """Create a mock Discord bot"""
        bot = MagicMock()
        bot.user.id = 12345
        return bot
    
    @pytest.fixture
    def mock_guild(self):
        """Create a mock Discord guild"""
        guild = MagicMock()
        guild.name = "Test Guild"
        guild.categories = []
        guild.create_category = AsyncMock()
        return guild
    
    @pytest.fixture
    def mock_category(self):
        """Create a mock Discord category"""
        category = MagicMock()
        category.name = "⚽ SOCCER"
        category.channels = []
        category.create_text_channel = AsyncMock()
        return category
    
    @pytest.fixture
    def sample_match(self):
        """Create a sample ProcessedMatch for testing"""
        home_team = Team(
            id=1,
            name="Arsenal",
            short_name="ARS",
            logo_url="https://example.com/arsenal.png",
            country="England"
        )
        
        away_team = Team(
            id=2,
            name="Liverpool FC",
            short_name="LIV",
            logo_url="https://example.com/liverpool.png",
            country="England"
        )
        
        league = League(
            id=228,
            name="Premier League",
            country="England",
            season="2024-25"
        )
        
        odds = BettingOdds(
            home_win=OddsFormat.from_decimal(2.50),
            draw=OddsFormat.from_decimal(3.20),
            away_win=OddsFormat.from_decimal(2.80)
        )
        
        h2h_summary = H2HSummary(
            total_meetings=10,
            home_team_wins=4,
            away_team_wins=3,
            draws=3,
            last_meeting_result="Arsenal 2-1 Liverpool"
        )
        
        return ProcessedMatch(
            match_id=12345,
            home_team=home_team,
            away_team=away_team,
            league=league,
            date="2025-08-17",
            time="15:00",
            venue="Emirates Stadium",
            status="scheduled",
            odds=odds,
            h2h_summary=h2h_summary
        )
    
    @pytest.fixture
    def channel_manager(self, mock_bot):
        """Create SoccerChannelManager instance"""
        return SoccerChannelManager(mock_bot)
    
    def test_init(self, mock_bot):
        """Test SoccerChannelManager initialization"""
        manager = SoccerChannelManager(mock_bot)
        
        assert manager.bot == mock_bot
        assert manager.category_name == "⚽ SOCCER"
        assert manager.channel_prefix == "📊"
        assert manager.cleanup_retention_days == 3
        assert manager.max_channels_per_category == 50
    
    def test_generate_channel_name_basic(self, channel_manager, sample_match):
        """Test basic channel name generation"""
        date = "2025-08-17"
        channel_name = channel_manager.generate_channel_name(sample_match, date)
        
        expected = "📊 08-17-liverpool-fc-vs-arsenal"
        assert channel_name == expected
    
    def test_generate_channel_name_long_teams(self, channel_manager):
        """Test channel name generation with long team names"""
        home_team = Team(
            id=1,
            name="Real Madrid Club de Fútbol",
            short_name="RMA"
        )
        
        away_team = Team(
            id=2,
            name="FC Barcelona Futbol Club",
            short_name="BAR"
        )
        
        league = League(id=297, name="La Liga", country="Spain")
        
        match = ProcessedMatch(
            match_id=1,
            home_team=home_team,
            away_team=away_team,
            league=league,
            date="2025-08-17",
            time="20:00",
            venue="Santiago Bernabéu",
            status="scheduled"
        )
        
        date = "2025-08-17"
        channel_name = channel_manager.generate_channel_name(match, date)
        
        # Should be truncated but still readable
        assert len(channel_name) <= 100  # Discord limit
        assert "08-17" in channel_name
        assert "vs" in channel_name
        assert channel_name.startswith("📊")
    
    def test_clean_team_name_for_channel(self, channel_manager):
        """Test team name cleaning for channel creation"""
        test_cases = [
            ("Arsenal", "arsenal"),
            ("Liverpool FC", "liverpool-fc"),
            ("Real Madrid C.F.", "real-madrid-cf"),
            ("Borussia Dortmund", "borussia-dortmund"),
            ("AC Milan", "ac-milan"),
            ("Manchester United F.C.", "manchester-united-fc"),
            ("Bayern München", "bayern-munchen"),  # Accented characters
            ("Team with (Parentheses)", "team-with"),  # Truncated at word boundary
            ("Team/With/Slashes", "team-with-slashes"),
            ("Team & Co", "team-and-co"),
            ("", "team"),  # Empty string fallback
        ]
        
        for input_name, expected in test_cases:
            result = channel_manager._clean_team_name_for_channel(input_name)
            assert result == expected, f"Failed for '{input_name}': got '{result}', expected '{expected}'"
    
    @pytest.mark.asyncio
    async def test_get_or_create_soccer_category_existing(self, channel_manager, mock_guild):
        """Test getting existing soccer category"""
        # Mock existing category
        existing_category = MagicMock()
        existing_category.name = "⚽ SOCCER"
        mock_guild.categories = [existing_category]
        
        with patch('discord.utils.get', return_value=existing_category):
            result = await channel_manager.get_or_create_soccer_category(mock_guild)
            
            assert result == existing_category
            mock_guild.create_category.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_or_create_soccer_category_new(self, channel_manager, mock_guild, mock_category):
        """Test creating new soccer category"""
        mock_guild.categories = []
        mock_guild.create_category.return_value = mock_category
        
        with patch('discord.utils.get', return_value=None):
            result = await channel_manager.get_or_create_soccer_category(mock_guild)
            
            assert result == mock_category
            mock_guild.create_category.assert_called_once_with(
                name="⚽ SOCCER",
                reason="Soccer match channels category"
            )
    
    @pytest.mark.asyncio
    async def test_create_single_match_channel(self, channel_manager, sample_match, mock_category):
        """Test creating a single match channel"""
        mock_channel = MagicMock()
        mock_channel.name = "📊 08-17-liverpool-fc-vs-arsenal"
        mock_category.create_text_channel.return_value = mock_channel
        
        with patch('discord.utils.get', return_value=None):  # No existing channel
            result = await channel_manager._create_single_match_channel(
                sample_match, "2025-08-17", mock_category
            )
            
            assert result == mock_channel
            mock_category.create_text_channel.assert_called_once()
            
            # Check the call arguments
            call_args = mock_category.create_text_channel.call_args
            assert call_args[1]['name'] == "📊 08-17-liverpool-fc-vs-arsenal"
            # Topic format is: home vs away
            assert "Arsenal vs Liverpool FC" in call_args[1]['topic']
            assert "Premier League" in call_args[1]['topic']
    
    @pytest.mark.asyncio
    async def test_create_single_match_channel_existing(self, channel_manager, sample_match, mock_category):
        """Test handling existing channel during creation"""
        existing_channel = MagicMock()
        existing_channel.name = "📊 08-17-liverpool-fc-vs-arsenal"
        
        with patch('discord.utils.get', return_value=existing_channel):
            result = await channel_manager._create_single_match_channel(
                sample_match, "2025-08-17", mock_category
            )
            
            assert result == existing_channel
            mock_category.create_text_channel.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_match_channels_success(self, channel_manager, sample_match, mock_guild, mock_category):
        """Test successful creation of multiple match channels"""
        matches = [sample_match]
        mock_channel = MagicMock()
        mock_category.channels = []
        
        with patch.object(channel_manager, 'get_or_create_soccer_category', return_value=mock_category):
            with patch.object(channel_manager, '_create_single_match_channel', return_value=mock_channel):
                result = await channel_manager.create_match_channels(matches, "2025-08-17", mock_guild)
                
                assert len(result) == 1
                assert result[0] == mock_channel
    
    @pytest.mark.asyncio
    async def test_create_match_channels_no_matches(self, channel_manager, mock_guild):
        """Test handling empty match list"""
        result = await channel_manager.create_match_channels([], "2025-08-17", mock_guild)
        assert result == []
    
    @pytest.mark.asyncio
    async def test_create_match_channels_no_category(self, channel_manager, sample_match, mock_guild):
        """Test handling category creation failure"""
        matches = [sample_match]
        
        with patch.object(channel_manager, 'get_or_create_soccer_category', return_value=None):
            result = await channel_manager.create_match_channels(matches, "2025-08-17", mock_guild)
            assert result == []
    
    @pytest.mark.asyncio
    async def test_cleanup_old_channels_basic(self, channel_manager, mock_guild):
        """Test basic channel cleanup functionality"""
        # Create mock channels
        old_channel = MagicMock()
        old_channel.name = "📊 08-10-team1-vs-team2"
        old_channel.created_at = datetime.now() - timedelta(days=5)
        old_channel.delete = AsyncMock()
        
        new_channel = MagicMock()
        new_channel.name = "📊 08-16-team3-vs-team4"
        new_channel.created_at = datetime.now() - timedelta(days=1)
        
        mock_category = MagicMock()
        mock_category.name = "⚽ SOCCER"
        mock_category.channels = [old_channel, new_channel]
        
        mock_guild.categories = [mock_category]
        
        with patch('discord.utils.get', return_value=mock_category):
            with patch.object(channel_manager, '_should_preserve_channel', side_effect=[False, True]):
                result = await channel_manager.cleanup_old_channels(mock_guild, days_old=3)
                
                assert result["channels_deleted"] == 1
                assert result["channels_preserved"] == 1
                assert result["errors"] == 0
                old_channel.delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup_old_channels_no_category(self, channel_manager, mock_guild):
        """Test cleanup when no soccer category exists"""
        mock_guild.categories = []
        
        with patch('discord.utils.get', return_value=None):
            result = await channel_manager.cleanup_old_channels(mock_guild)
            
            assert result["channels_deleted"] == 0
            assert result["channels_preserved"] == 0
            assert result["errors"] == 0
    
    @pytest.mark.asyncio
    async def test_should_preserve_channel_recent(self, channel_manager):
        """Test channel preservation for recent channels"""
        channel = MagicMock()
        channel.created_at = datetime.now() - timedelta(hours=12)
        cutoff_date = datetime.now() - timedelta(days=3)
        
        result = await channel_manager._should_preserve_channel(channel, cutoff_date)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_should_preserve_channel_recent_activity(self, channel_manager):
        """Test channel preservation for channels with recent activity"""
        channel = MagicMock()
        channel.created_at = datetime.now() - timedelta(days=5)
        
        # Mock recent message
        mock_message = MagicMock()
        channel.history.return_value.__aiter__ = AsyncMock(return_value=iter([mock_message]))
        
        cutoff_date = datetime.now() - timedelta(days=3)
        
        result = await channel_manager._should_preserve_channel(channel, cutoff_date)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_should_preserve_channel_pinned_messages(self, channel_manager):
        """Test channel preservation for channels with pinned messages"""
        channel = MagicMock()
        channel.created_at = datetime.now() - timedelta(days=5)
        channel.history.return_value.__aiter__ = AsyncMock(return_value=iter([]))
        channel.pins.return_value = [MagicMock()]  # Has pinned messages
        
        cutoff_date = datetime.now() - timedelta(days=3)
        
        result = await channel_manager._should_preserve_channel(channel, cutoff_date)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_should_preserve_channel_old_no_activity(self, channel_manager):
        """Test channel deletion for old channels with no activity"""
        channel = MagicMock()
        channel.created_at = datetime.now() - timedelta(days=5)
        
        # Mock history to raise HTTPException (simulating no access to history)
        channel.history.side_effect = discord.HTTPException(MagicMock(), "Forbidden")
        channel.pins = AsyncMock(return_value=[])  # No pinned messages
        
        cutoff_date = datetime.now() - timedelta(days=3)
        
        result = await channel_manager._should_preserve_channel(channel, cutoff_date)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_update_channel_content(self, channel_manager, sample_match):
        """Test channel content update functionality"""
        mock_channel = MagicMock()
        
        result = await channel_manager.update_channel_content(mock_channel, sample_match)
        assert result is True


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])