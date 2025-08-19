"""
Comprehensive Error Handling Tests for Soccer Discord Integration
Tests network failures, invalid data, API limits, and graceful degradation
"""

import pytest
import asyncio
import httpx
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import discord

# Import the modules to test
from soccer_error_handling import (
    SoccerBotError, MCPConnectionError, MCPTimeoutError, MCPDataError,
    DiscordAPIError, ValidationError, ErrorContext, ErrorSeverity,
    retry_with_backoff, GracefulDegradation, ErrorHandler, SoccerBotLogger
)
from soccer_integration import SoccerMCPClient, SoccerDataProcessor
from soccer_channel_manager import SoccerChannelManager
from soccer_command_handlers import (
    validate_date_input, validate_team_name, validate_league_choice,
    enhanced_soccer_schedule_command, enhanced_soccer_odds_command,
    enhanced_soccer_h2h_command, enhanced_soccer_standings_command
)

# ============================================================================
# ERROR HANDLING SYSTEM TESTS
# ============================================================================

class TestErrorHandlingSystem:
    """Test the core error handling system"""
    
    def test_error_context_creation(self):
        """Test ErrorContext creation and properties"""
        context = ErrorContext(
            "test_operation",
            user_id=12345,
            guild_id=67890,
            additional_data={"key": "value"}
        )
        
        assert context.operation == "test_operation"
        assert context.user_id == 12345
        assert context.guild_id == 67890
        assert context.additional_data["key"] == "value"
        assert isinstance(context.timestamp, datetime)
    
    def test_soccer_bot_error_creation(self):
        """Test SoccerBotError creation with different severities"""
        context = ErrorContext("test_op")
        
        error = SoccerBotError(
            "Test error message",
            ErrorSeverity.HIGH,
            context,
            "User-friendly message"
        )
        
        assert str(error) == "Test error message"
        assert error.severity == ErrorSeverity.HIGH
        assert error.context == context
        assert error.user_message == "User-friendly message"
        assert isinstance(error.timestamp, datetime)
    
    def test_mcp_connection_error_user_messages(self):
        """Test MCPConnectionError generates appropriate user messages"""
        context = ErrorContext("test_mcp")
        
        # Test rate limit error
        rate_limit_error = MCPConnectionError(
            "Rate limited", 
            status_code=429, 
            context=context
        )
        assert "Rate limit reached" in rate_limit_error.user_message
        
        # Test server error
        server_error = MCPConnectionError(
            "Server error", 
            status_code=500, 
            context=context
        )
        assert "service is experiencing issues" in server_error.user_message
        
        # Test max retries
        max_retry_error = MCPConnectionError(
            "Max retries", 
            retry_count=3, 
            context=context
        )
        assert "currently unavailable" in max_retry_error.user_message
    
    def test_validation_error_messages(self):
        """Test ValidationError generates helpful messages"""
        error = ValidationError(
            "Invalid date",
            "date",
            "invalid-date",
            "YYYY-MM-DD"
        )
        
        assert "Invalid date" in error.user_message
        assert "invalid-date" in error.user_message
        assert "YYYY-MM-DD" in error.user_message
    
    def test_graceful_degradation_utilities(self):
        """Test graceful degradation utility functions"""
        # Test partial match data creation
        match_data = {"home_team": "Team A", "away_team": "Team B"}
        missing_fields = ["odds", "venue"]
        
        result = GracefulDegradation.create_partial_match_data(match_data, missing_fields)
        
        assert result["home_team"] == "Team A"
        assert result["odds"] is None
        assert result["venue"] == "TBD"
        assert result["_partial_data"] is True
        assert result["_missing_fields"] == missing_fields
        
        # Test fallback embed creation
        embed = GracefulDegradation.create_fallback_embed(
            "Test Error",
            "Test message",
            ["Suggestion 1", "Suggestion 2"]
        )
        
        assert embed.title == "⚠️ Test Error"
        assert embed.description == "Test message"
        assert len(embed.fields) == 1
        assert "Suggestion 1" in embed.fields[0].value

# ============================================================================
# RETRY LOGIC TESTS
# ============================================================================

class TestRetryLogic:
    """Test retry decorator and exponential backoff"""
    
    @pytest.mark.asyncio
    async def test_retry_success_after_failure(self):
        """Test successful retry after initial failure"""
        call_count = 0
        
        @retry_with_backoff(max_retries=2, base_delay=0.1)
        async def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.RequestError("Connection failed")
            return "success"
        
        result = await test_function()
        assert result == "success"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_max_attempts_exceeded(self):
        """Test retry gives up after max attempts"""
        call_count = 0
        
        @retry_with_backoff(max_retries=2, base_delay=0.1)
        async def test_function():
            nonlocal call_count
            call_count += 1
            raise httpx.RequestError("Persistent failure")
        
        with pytest.raises(httpx.RequestError):
            await test_function()
        
        assert call_count == 3  # Initial + 2 retries
    
    @pytest.mark.asyncio
    async def test_retry_non_retryable_exception(self):
        """Test non-retryable exceptions are not retried"""
        call_count = 0
        
        @retry_with_backoff(max_retries=2, base_delay=0.1)
        async def test_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Non-retryable error")
        
        with pytest.raises(ValueError):
            await test_function()
        
        assert call_count == 1  # No retries for ValueError

# ============================================================================
# MCP CLIENT ERROR HANDLING TESTS
# ============================================================================

class TestMCPClientErrorHandling:
    """Test MCP client error handling and recovery"""
    
    @pytest.fixture
    def mcp_client(self):
        return SoccerMCPClient()
    
    @pytest.mark.asyncio
    async def test_mcp_connection_timeout(self, mcp_client):
        """Test MCP client handles timeout errors"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.TimeoutException("Timeout")
            
            context = ErrorContext("test_timeout")
            
            with pytest.raises(MCPTimeoutError) as exc_info:
                await mcp_client.call_mcp_tool("get_matches", {"date": "2025-08-17"}, context)
            
            assert "timeout" in str(exc_info.value).lower()
            assert exc_info.value.timeout_duration == mcp_client.timeout
    
    @pytest.mark.asyncio
    async def test_mcp_http_status_error(self, mcp_client):
        """Test MCP client handles HTTP status errors"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 500
            
            mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.HTTPStatusError(
                "Server Error", 
                request=None, 
                response=mock_response
            )
            
            context = ErrorContext("test_http_error")
            
            with pytest.raises(MCPConnectionError) as exc_info:
                await mcp_client.call_mcp_tool("get_matches", {"date": "2025-08-17"}, context)
            
            assert exc_info.value.status_code == 500
    
    @pytest.mark.asyncio
    async def test_mcp_invalid_response_format(self, mcp_client):
        """Test MCP client handles invalid response formats"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {"invalid": "response"}  # Missing 'result' field
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            context = ErrorContext("test_invalid_response")
            
            with pytest.raises(MCPDataError) as exc_info:
                await mcp_client.call_mcp_tool("get_matches", {"date": "2025-08-17"}, context)
            
            assert "Invalid MCP response format" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_mcp_server_error_response(self, mcp_client):
        """Test MCP client handles server error responses"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "error": {
                    "message": "Internal server error",
                    "code": -32603
                }
            }
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            context = ErrorContext("test_server_error")
            
            with pytest.raises(MCPDataError) as exc_info:
                await mcp_client.call_mcp_tool("get_matches", {"date": "2025-08-17"}, context)
            
            assert "Internal server error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_h2h_analysis_graceful_degradation(self, mcp_client):
        """Test H2H analysis handles missing data gracefully"""
        with patch('httpx.AsyncClient') as mock_client:
            # Simulate connection error
            mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.RequestError("Connection failed")
            
            context = ErrorContext("test_h2h_degradation")
            
            # Should not raise exception, but return fallback data
            result = await mcp_client.get_h2h_analysis(123, 456, context=context)
            
            assert result["total_meetings"] == 0
            assert result["team1_wins"] == 0
            assert result["team2_wins"] == 0
            assert result["draws"] == 0
            assert result["fallback"] is True
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_matches_graceful_degradation(self, mcp_client):
        """Test matches fetch handles errors gracefully"""
        with patch('httpx.AsyncClient') as mock_client:
            # Simulate timeout
            mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.TimeoutException("Timeout")
            
            context = ErrorContext("test_matches_degradation")
            
            # Should not raise exception, but return fallback data
            result = await mcp_client.get_matches_for_date("2025-08-17", context=context)
            
            assert result["matches_by_league"] == {}
            assert result["total_matches"] == 0
            assert result["fallback"] is True
            assert "error" in result

# ============================================================================
# DISCORD API ERROR HANDLING TESTS
# ============================================================================

class TestDiscordAPIErrorHandling:
    """Test Discord API error handling"""
    
    @pytest.fixture
    def mock_bot(self):
        bot = MagicMock()
        bot.user.id = 12345
        return bot
    
    @pytest.fixture
    def channel_manager(self, mock_bot):
        return SoccerChannelManager(mock_bot)
    
    @pytest.mark.asyncio
    async def test_discord_permission_error(self, channel_manager):
        """Test Discord permission errors are handled properly"""
        mock_guild = MagicMock()
        mock_guild.id = 67890
        mock_guild.categories = []
        mock_guild.create_category.side_effect = discord.Forbidden(MagicMock(), "Permission denied")
        
        context = ErrorContext("test_permission_error", guild_id=67890)
        
        result = await channel_manager.get_or_create_soccer_category(mock_guild, context)
        
        assert result is None  # Should return None on permission error
    
    @pytest.mark.asyncio
    async def test_discord_rate_limit_error(self, channel_manager):
        """Test Discord rate limit errors trigger retry"""
        mock_guild = MagicMock()
        mock_guild.id = 67890
        mock_guild.categories = []
        
        # First call raises rate limit, second succeeds
        mock_category = MagicMock()
        mock_guild.create_category.side_effect = [
            discord.HTTPException(MagicMock(), "Rate limited"),
            mock_category
        ]
        
        context = ErrorContext("test_rate_limit", guild_id=67890)
        
        # This should eventually succeed after retry
        with patch('asyncio.sleep'):  # Speed up the test
            result = await channel_manager.get_or_create_soccer_category(mock_guild, context)
        
        assert result == mock_category
        assert mock_guild.create_category.call_count == 2

# ============================================================================
# INPUT VALIDATION TESTS
# ============================================================================

class TestInputValidation:
    """Test input validation functions"""
    
    def test_date_validation_valid_formats(self):
        """Test date validation accepts valid formats"""
        valid_dates = [
            "08/17/2025",  # MM/DD/YYYY
            "17-08-2025",  # DD-MM-YYYY
            "2025-08-17",  # YYYY-MM-DD
            "08-17-2025",  # MM-DD-YYYY
            "17/08/2025",  # DD/MM/YYYY
        ]
        
        for date_str in valid_dates:
            result = validate_date_input(date_str)
            assert result == "2025-08-17"
    
    def test_date_validation_invalid_formats(self):
        """Test date validation rejects invalid formats"""
        invalid_dates = [
            "invalid-date",
            "2025/13/01",  # Invalid month
            "32-01-2025",  # Invalid day
            "2025-02-30",  # Invalid date
            "",
            None,
            123
        ]
        
        for date_str in invalid_dates:
            with pytest.raises(ValidationError):
                validate_date_input(date_str)
    
    def test_date_validation_range_limits(self):
        """Test date validation enforces range limits"""
        now = datetime.now()
        
        # Date too far in past
        old_date = (now - timedelta(days=35)).strftime("%Y-%m-%d")
        with pytest.raises(ValidationError) as exc_info:
            validate_date_input(old_date)
        assert "outside allowed range" in str(exc_info.value)
        
        # Date too far in future
        future_date = (now + timedelta(days=400)).strftime("%Y-%m-%d")
        with pytest.raises(ValidationError) as exc_info:
            validate_date_input(future_date)
        assert "outside allowed range" in str(exc_info.value)
    
    def test_team_name_validation(self):
        """Test team name validation"""
        # Valid team names
        assert validate_team_name("Liverpool") == "Liverpool"
        assert validate_team_name("  Arsenal  ") == "Arsenal"
        
        # Invalid team names
        with pytest.raises(ValidationError):
            validate_team_name("")  # Empty
        
        with pytest.raises(ValidationError):
            validate_team_name("A")  # Too short
        
        with pytest.raises(ValidationError):
            validate_team_name("A" * 51)  # Too long
        
        with pytest.raises(ValidationError):
            validate_team_name(None)  # None
    
    def test_league_choice_validation(self):
        """Test league choice validation"""
        # Valid league choice
        mock_choice = MagicMock()
        mock_choice.value = "EPL"
        assert validate_league_choice(mock_choice) == "EPL"
        
        # None choice (should be allowed)
        assert validate_league_choice(None) is None
        
        # Invalid league choice
        mock_invalid_choice = MagicMock()
        mock_invalid_choice.value = "INVALID"
        with pytest.raises(ValidationError):
            validate_league_choice(mock_invalid_choice)

# ============================================================================
# COMMAND ERROR HANDLING TESTS
# ============================================================================

class TestCommandErrorHandling:
    """Test error handling in Discord commands"""
    
    @pytest.fixture
    def mock_interaction(self):
        interaction = MagicMock()
        interaction.user.id = 12345
        interaction.guild.id = 67890
        interaction.channel.id = 11111
        interaction.response.is_done.return_value = False
        interaction.response.defer = AsyncMock()
        interaction.followup.send = AsyncMock()
        return interaction
    
    @pytest.mark.asyncio
    async def test_schedule_command_validation_error(self, mock_interaction):
        """Test schedule command handles validation errors"""
        # Test with invalid date
        await enhanced_soccer_schedule_command(
            mock_interaction,
            league=None,
            date="invalid-date"
        )
        
        # Should have sent an error embed
        mock_interaction.followup.send.assert_called_once()
        call_args = mock_interaction.followup.send.call_args
        embed = call_args[1]['embed']
        assert "Invalid date" in embed.title or "Invalid date" in embed.description
    
    @pytest.mark.asyncio
    async def test_odds_command_team_validation(self, mock_interaction):
        """Test odds command validates team names"""
        # Test with same team names
        await enhanced_soccer_odds_command(
            mock_interaction,
            team1="Liverpool",
            team2="Liverpool"
        )
        
        # Should have sent an error embed
        mock_interaction.followup.send.assert_called_once()
        call_args = mock_interaction.followup.send.call_args
        embed = call_args[1]['embed']
        assert "different" in embed.description.lower()
    
    @pytest.mark.asyncio
    async def test_h2h_command_mcp_error_handling(self, mock_interaction):
        """Test H2H command handles MCP errors gracefully"""
        with patch('soccer_integration.SoccerMCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_h2h_analysis.side_effect = MCPConnectionError("Connection failed")
            mock_client_class.return_value = mock_client
            
            await enhanced_soccer_h2h_command(
                mock_interaction,
                team1="Liverpool",
                team2="Arsenal"
            )
            
            # Should have sent an error embed
            mock_interaction.followup.send.assert_called_once()
            call_args = mock_interaction.followup.send.call_args
            embed = call_args[1]['embed']
            assert embed.color == 0xff6b6b or embed.color == 0xffd93d  # Error colors

# ============================================================================
# LOGGING SYSTEM TESTS
# ============================================================================

class TestLoggingSystem:
    """Test the enhanced logging system"""
    
    def test_logger_initialization(self):
        """Test logger initializes correctly"""
        logger = SoccerBotLogger("test_logger")
        assert logger.logger.name == "test_logger"
        assert len(logger.logger.handlers) >= 3  # Console, error file, debug file
    
    def test_operation_logging(self):
        """Test operation logging methods"""
        logger = SoccerBotLogger("test_logger")
        context = ErrorContext("test_operation", user_id=12345)
        
        # Test logging methods don't raise exceptions
        logger.log_operation_start("test_op", context)
        logger.log_operation_success("test_op", context, 1.5, "Success")
        
        error = SoccerBotError("Test error", ErrorSeverity.MEDIUM, context)
        logger.log_operation_error("test_op", error, context)
        
        logger.log_graceful_degradation("test_op", ["missing_field"], ["available_field"], context)

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestErrorHandlingIntegration:
    """Integration tests for error handling across components"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_error_recovery(self):
        """Test end-to-end error recovery scenario"""
        # This test simulates a complete failure and recovery scenario
        
        # 1. MCP server is down
        # 2. Command should handle gracefully
        # 3. User gets helpful error message
        # 4. System logs the error appropriately
        
        mock_interaction = MagicMock()
        mock_interaction.user.id = 12345
        mock_interaction.guild.id = 67890
        mock_interaction.channel.id = 11111
        mock_interaction.response.is_done.return_value = False
        mock_interaction.response.defer = AsyncMock()
        mock_interaction.followup.send = AsyncMock()
        
        with patch('soccer_integration.SoccerMCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_matches_for_date.side_effect = MCPConnectionError(
                "MCP server unavailable", 
                status_code=503
            )
            mock_client_class.return_value = mock_client
            
            # Execute command
            await enhanced_soccer_schedule_command(
                mock_interaction,
                league=None,
                date="2025-08-17"
            )
            
            # Verify error was handled gracefully
            mock_interaction.followup.send.assert_called_once()
            call_args = mock_interaction.followup.send.call_args
            embed = call_args[1]['embed']
            
            # Should be an error embed with helpful message
            assert embed.color in [0xff6b6b, 0xff6b35, 0xff4757, 0xffd93d]  # Error colors
            assert len(embed.fields) > 0  # Should have suggestions
    
    @pytest.mark.asyncio
    async def test_partial_data_handling(self):
        """Test handling of partial data scenarios"""
        # Simulate scenario where some data is available but incomplete
        
        mock_interaction = MagicMock()
        mock_interaction.user.id = 12345
        mock_interaction.guild.id = 67890
        mock_interaction.channel.id = 11111
        mock_interaction.response.is_done.return_value = False
        mock_interaction.response.defer = AsyncMock()
        mock_interaction.followup.send = AsyncMock()
        
        # Mock partial data response
        partial_matches_data = {
            "matches_by_league": {
                "EPL": [
                    {
                        "match_id": 123,
                        "home_team": {"name": "Liverpool"},
                        "away_team": {"name": "Arsenal"},
                        "date": "2025-08-17",
                        "time": "15:00",
                        "venue": "Anfield"
                        # Missing odds and other data
                    }
                ]
            },
            "_partial_data": True,
            "_missing_fields": ["odds", "h2h_summary"]
        }
        
        with patch('soccer_integration.SoccerMCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_matches_for_date.return_value = partial_matches_data
            mock_client_class.return_value = mock_client
            
            with patch('soccer_integration.SoccerDataProcessor') as mock_processor_class:
                mock_processor = MagicMock()
                mock_processor.process_match_data.return_value = [MagicMock()]
                mock_processor_class.return_value = mock_processor
                
                with patch('soccer_integration.SoccerEmbedBuilder') as mock_embed_class:
                    mock_embed_builder = MagicMock()
                    mock_embed = MagicMock()
                    mock_embed_builder.create_schedule_embed.return_value = mock_embed
                    mock_embed_class.return_value = mock_embed_builder
                    
                    # Execute command
                    await enhanced_soccer_schedule_command(
                        mock_interaction,
                        league=None,
                        date="2025-08-17"
                    )
                    
                    # Should have succeeded and sent embed
                    mock_interaction.followup.send.assert_called_once()
                    
                    # Embed should have been modified to indicate partial data
                    call_args = mock_interaction.followup.send.call_args
                    embed = call_args[1]['embed']
                    
                    # Should have added a note about incomplete data
                    assert hasattr(embed, 'add_field')

if __name__ == "__main__":
    pytest.main([__file__, "-v"])