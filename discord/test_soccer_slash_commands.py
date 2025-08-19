"""
Integration Tests for Soccer Slash Commands
Tests all soccer-specific slash commands with mock MCP responses
"""

import pytest
import asyncio
import discord
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import json

# Import the bot and command functions
from bot_structure import bot, soccer_schedule_command, soccer_odds_command, soccer_h2h_command, soccer_standings_command

# Mock data for testing
MOCK_MATCHES_RESPONSE = {
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
                    "date": "2025-08-18",
                    "time": "15:00",
                    "venue": "Emirates Stadium",
                    "status": "scheduled",
                    "home_team": {
                        "id": 1001,
                        "name": "Arsenal",
                        "short_name": "ARS",
                        "country": "England"
                    },
                    "away_team": {
                        "id": 1002,
                        "name": "Liverpool",
                        "short_name": "LIV",
                        "country": "England"
                    },
                    "odds": {
                        "home_win": 2.50,
                        "draw": 3.20,
                        "away_win": 2.80,
                        "over_under": {
                            "line": 2.5,
                            "over": 1.85,
                            "under": 1.95
                        },
                        "both_teams_score": 1.75
                    },
                    "h2h_summary": {
                        "total_meetings": 10,
                        "home_team_wins": 4,
                        "away_team_wins": 3,
                        "draws": 3,
                        "last_meeting_result": "Arsenal 2-1 Liverpool"
                    }
                }
            ]
        },
        "La Liga": {
            "league_info": {
                "id": 297,
                "name": "La Liga",
                "country": "Spain"
            },
            "matches": [
                {
                    "id": 12346,
                    "date": "2025-08-18",
                    "time": "20:00",
                    "venue": "Camp Nou",
                    "status": "scheduled",
                    "home_team": {
                        "id": 2001,
                        "name": "FC Barcelona",
                        "short_name": "BAR",
                        "country": "Spain"
                    },
                    "away_team": {
                        "id": 2002,
                        "name": "Real Madrid",
                        "short_name": "RMA",
                        "country": "Spain"
                    },
                    "odds": {
                        "home_win": 2.10,
                        "draw": 3.50,
                        "away_win": 3.20
                    }
                }
            ]
        }
    }
}

MOCK_H2H_RESPONSE = {
    "total_meetings": 15,
    "team1_wins": 6,
    "team2_wins": 5,
    "draws": 4,
    "avg_goals_per_game": 2.8,
    "recent_form": {
        "Arsenal": ["W", "L", "W", "D", "W"],
        "Liverpool": ["W", "W", "L", "W", "D"]
    },
    "betting_recommendations": [
        "Over 2.5 goals likely based on historical average",
        "Both teams to score has high probability"
    ],
    "key_statistics": {
        "avg_cards_per_game": 4.2,
        "clean_sheets_home": 3,
        "clean_sheets_away": 2
    }
}

MOCK_STANDINGS_RESPONSE = {
    "standings": [
        {
            "position": 1,
            "team": {"name": "Arsenal", "id": 1001},
            "played": 10,
            "wins": 8,
            "draws": 1,
            "losses": 1,
            "goals_for": 25,
            "goals_against": 8,
            "points": 25
        },
        {
            "position": 2,
            "team": {"name": "Liverpool", "id": 1002},
            "played": 10,
            "wins": 7,
            "draws": 2,
            "losses": 1,
            "goals_for": 22,
            "goals_against": 10,
            "points": 23
        },
        {
            "position": 3,
            "team": {"name": "Manchester City", "id": 1003},
            "played": 10,
            "wins": 6,
            "draws": 3,
            "losses": 1,
            "goals_for": 20,
            "goals_against": 8,
            "points": 21
        }
    ]
}

class MockInteraction:
    """Mock Discord interaction for testing"""
    
    def __init__(self):
        self.response = AsyncMock()
        self.followup = AsyncMock()
        self.user = MagicMock()
        self.user.guild_permissions.administrator = True
        self.guild = MagicMock()
        self.guild.id = 12345

class MockChoice:
    """Mock Discord app command choice"""
    
    def __init__(self, name, value):
        self.name = name
        self.value = value

@pytest.fixture
def mock_interaction():
    """Fixture providing mock Discord interaction"""
    return MockInteraction()

@pytest.fixture
def mock_soccer_client():
    """Fixture providing mock soccer MCP client"""
    with patch('soccer_integration.SoccerMCPClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        yield mock_client

@pytest.fixture
def mock_soccer_processor():
    """Fixture providing mock soccer data processor"""
    with patch('soccer_integration.SoccerDataProcessor') as mock_processor_class:
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        yield mock_processor

@pytest.fixture
def mock_soccer_embed_builder():
    """Fixture providing mock soccer embed builder"""
    with patch('soccer_integration.SoccerEmbedBuilder') as mock_builder_class:
        mock_builder = MagicMock()
        mock_builder_class.return_value = mock_builder
        yield mock_builder

class TestSoccerScheduleCommand:
    """Test cases for /soccer-schedule command"""
    
    @pytest.mark.asyncio
    async def test_schedule_command_success_no_filters(self, mock_interaction, mock_soccer_client, mock_soccer_processor, mock_soccer_embed_builder):
        """Test successful schedule retrieval without filters"""
        # Setup mocks
        mock_soccer_client.get_matches_for_date.return_value = MOCK_MATCHES_RESPONSE
        
        # Mock processed matches
        from soccer_integration import ProcessedMatch, Team, League
        mock_matches = [
            ProcessedMatch(
                match_id=12345,
                home_team=Team(1001, "Arsenal", "ARS"),
                away_team=Team(1002, "Liverpool", "LIV"),
                league=League(228, "Premier League", "England"),
                date="2025-08-18",
                time="15:00",
                venue="Emirates Stadium",
                status="scheduled"
            )
        ]
        mock_soccer_processor.process_match_data.return_value = mock_matches
        
        # Execute command
        await soccer_schedule_command(mock_interaction)
        
        # Verify interactions
        mock_interaction.response.defer.assert_called_once()
        mock_soccer_client.get_matches_for_date.assert_called_once()
        mock_soccer_processor.process_match_data.assert_called_once_with(MOCK_MATCHES_RESPONSE)
        mock_interaction.followup.send.assert_called_once()
        
        # Verify embed was sent
        call_args = mock_interaction.followup.send.call_args
        assert 'embed' in call_args.kwargs
        embed = call_args.kwargs['embed']
        assert "Soccer Schedule" in embed.title
    
    @pytest.mark.asyncio
    async def test_schedule_command_with_league_filter(self, mock_interaction, mock_soccer_client, mock_soccer_processor, mock_soccer_embed_builder):
        """Test schedule command with league filter"""
        # Setup league choice
        league_choice = MockChoice("Premier League", "EPL")
        
        # Setup mocks
        mock_soccer_client.get_matches_for_date.return_value = MOCK_MATCHES_RESPONSE
        mock_soccer_processor.process_match_data.return_value = []
        
        # Execute command
        await soccer_schedule_command(mock_interaction, league=league_choice)
        
        # Verify league filter was passed
        mock_soccer_client.get_matches_for_date.assert_called_once()
        call_args = mock_soccer_client.get_matches_for_date.call_args
        assert call_args[0][1] == "EPL"  # League filter argument
    
    @pytest.mark.asyncio
    async def test_schedule_command_no_matches_found(self, mock_interaction, mock_soccer_client, mock_soccer_processor, mock_soccer_embed_builder):
        """Test schedule command when no matches are found"""
        # Setup mocks
        mock_soccer_client.get_matches_for_date.return_value = MOCK_MATCHES_RESPONSE
        mock_soccer_processor.process_match_data.return_value = []
        
        # Execute command
        await soccer_schedule_command(mock_interaction)
        
        # Verify no matches response
        mock_interaction.followup.send.assert_called_once()
        call_args = mock_interaction.followup.send.call_args
        embed = call_args.kwargs['embed']
        assert "No Matches Found" in embed.title
    
    @pytest.mark.asyncio
    async def test_schedule_command_invalid_date(self, mock_interaction, mock_soccer_client, mock_soccer_processor, mock_soccer_embed_builder):
        """Test schedule command with invalid date format"""
        # Execute command with invalid date
        await soccer_schedule_command(mock_interaction, date="invalid-date")
        
        # Verify error response
        mock_interaction.followup.send.assert_called_once()
        call_args = mock_interaction.followup.send.call_args
        embed = call_args.kwargs['embed']
        assert "Invalid Date Format" in embed.title
    
    @pytest.mark.asyncio
    async def test_schedule_command_mcp_server_error(self, mock_interaction, mock_soccer_client, mock_soccer_processor, mock_soccer_embed_builder):
        """Test schedule command when MCP server fails"""
        # Setup mock to raise exception
        mock_soccer_client.get_matches_for_date.side_effect = Exception("MCP server error")
        
        # Execute command
        await soccer_schedule_command(mock_interaction)
        
        # Verify error response
        mock_interaction.followup.send.assert_called_once()
        call_args = mock_interaction.followup.send.call_args
        embed = call_args.kwargs['embed']
        assert "MCP Server Error" in embed.title

class TestSoccerOddsCommand:
    """Test cases for /soccer-odds command"""
    
    @pytest.mark.asyncio
    async def test_odds_command_success(self, mock_interaction, mock_soccer_client, mock_soccer_processor, mock_soccer_embed_builder):
        """Test successful odds retrieval"""
        # Setup mocks
        mock_soccer_client.get_matches_for_date.return_value = MOCK_MATCHES_RESPONSE
        
        # Mock processed matches with odds
        from soccer_integration import ProcessedMatch, Team, League, BettingOdds, OddsFormat
        mock_match = ProcessedMatch(
            match_id=12345,
            home_team=Team(1001, "Arsenal", "ARS"),
            away_team=Team(1002, "Liverpool", "LIV"),
            league=League(228, "Premier League", "England"),
            date="2025-08-18",
            time="15:00",
            venue="Emirates Stadium",
            status="scheduled",
            odds=BettingOdds(
                home_win=OddsFormat.from_decimal(2.50),
                draw=OddsFormat.from_decimal(3.20),
                away_win=OddsFormat.from_decimal(2.80)
            )
        )
        mock_soccer_processor.process_match_data.return_value = [mock_match]
        
        # Mock embed builder
        mock_embed = MagicMock()
        mock_soccer_embed_builder.create_betting_odds_embed.return_value = mock_embed
        
        # Execute command
        await soccer_odds_command(mock_interaction, "Arsenal", "Liverpool")
        
        # Verify interactions
        mock_interaction.response.defer.assert_called_once()
        mock_soccer_client.get_matches_for_date.assert_called_once()
        mock_soccer_embed_builder.create_betting_odds_embed.assert_called_once_with(mock_match)
        mock_interaction.followup.send.assert_called_once_with(embed=mock_embed)
    
    @pytest.mark.asyncio
    async def test_odds_command_match_not_found(self, mock_interaction, mock_soccer_client, mock_soccer_processor, mock_soccer_embed_builder):
        """Test odds command when match is not found"""
        # Setup mocks
        mock_soccer_client.get_matches_for_date.return_value = MOCK_MATCHES_RESPONSE
        mock_soccer_processor.process_match_data.return_value = []
        
        # Execute command
        await soccer_odds_command(mock_interaction, "NonExistent", "Team")
        
        # Verify match not found response
        mock_interaction.followup.send.assert_called_once()
        call_args = mock_interaction.followup.send.call_args
        embed = call_args.kwargs['embed']
        assert "Match Not Found" in embed.title
    
    @pytest.mark.asyncio
    async def test_odds_command_partial_team_name_matching(self, mock_interaction, mock_soccer_client, mock_soccer_processor, mock_soccer_embed_builder):
        """Test odds command with partial team name matching"""
        # Setup mocks
        mock_soccer_client.get_matches_for_date.return_value = MOCK_MATCHES_RESPONSE
        
        from soccer_integration import ProcessedMatch, Team, League
        mock_match = ProcessedMatch(
            match_id=12345,
            home_team=Team(1001, "Arsenal FC", "ARS"),
            away_team=Team(1002, "Liverpool FC", "LIV"),
            league=League(228, "Premier League", "England"),
            date="2025-08-18",
            time="15:00",
            venue="Emirates Stadium",
            status="scheduled"
        )
        mock_soccer_processor.process_match_data.return_value = [mock_match]
        
        # Execute command with partial names
        await soccer_odds_command(mock_interaction, "Arsenal", "Liverpool")
        
        # Should find the match despite partial names
        mock_interaction.followup.send.assert_called_once()
        call_args = mock_interaction.followup.send.call_args
        embed = call_args.kwargs['embed']
        assert "Arsenal FC vs Liverpool FC" in embed.title or "Match found but no betting odds" in embed.description

class TestSoccerH2HCommand:
    """Test cases for /soccer-h2h command"""
    
    @pytest.mark.asyncio
    async def test_h2h_command_success(self, mock_interaction, mock_soccer_client, mock_soccer_processor, mock_soccer_embed_builder):
        """Test successful H2H analysis retrieval"""
        # Setup mocks for team finding
        mock_soccer_client.get_matches_for_date.return_value = MOCK_MATCHES_RESPONSE
        
        from soccer_integration import ProcessedMatch, Team, League
        mock_match = ProcessedMatch(
            match_id=12345,
            home_team=Team(1001, "Arsenal", "ARS"),
            away_team=Team(1002, "Liverpool", "LIV"),
            league=League(228, "Premier League", "England"),
            date="2025-08-18",
            time="15:00",
            venue="Emirates Stadium",
            status="scheduled"
        )
        mock_soccer_processor.process_match_data.return_value = [mock_match]
        
        # Setup H2H response
        mock_soccer_client.get_h2h_analysis.return_value = MOCK_H2H_RESPONSE
        
        # Mock embed builder
        mock_embed = MagicMock()
        mock_soccer_embed_builder.create_h2h_analysis_embed.return_value = mock_embed
        
        # Execute command
        await soccer_h2h_command(mock_interaction, "Arsenal", "Liverpool")
        
        # Verify interactions
        mock_interaction.response.defer.assert_called_once()
        mock_soccer_client.get_h2h_analysis.assert_called_once_with(1001, 1002)
        mock_soccer_embed_builder.create_h2h_analysis_embed.assert_called_once()
        mock_interaction.followup.send.assert_called_once_with(embed=mock_embed)
    
    @pytest.mark.asyncio
    async def test_h2h_command_teams_not_found(self, mock_interaction, mock_soccer_client, mock_soccer_processor, mock_soccer_embed_builder):
        """Test H2H command when teams are not found"""
        # Setup mocks to return no matches
        mock_soccer_client.get_matches_for_date.return_value = {"matches_by_league": {}}
        mock_soccer_processor.process_match_data.return_value = []
        
        # Execute command
        await soccer_h2h_command(mock_interaction, "NonExistent", "Team")
        
        # Verify teams not found response
        mock_interaction.followup.send.assert_called_once()
        call_args = mock_interaction.followup.send.call_args
        embed = call_args.kwargs['embed']
        assert "Teams Not Found" in embed.title
    
    @pytest.mark.asyncio
    async def test_h2h_command_no_h2h_data(self, mock_interaction, mock_soccer_client, mock_soccer_processor, mock_soccer_embed_builder):
        """Test H2H command when no H2H data is available"""
        # Setup mocks for team finding
        mock_soccer_client.get_matches_for_date.return_value = MOCK_MATCHES_RESPONSE
        
        from soccer_integration import ProcessedMatch, Team, League
        mock_match = ProcessedMatch(
            match_id=12345,
            home_team=Team(1001, "Arsenal", "ARS"),
            away_team=Team(1002, "Liverpool", "LIV"),
            league=League(228, "Premier League", "England"),
            date="2025-08-18",
            time="15:00",
            venue="Emirates Stadium",
            status="scheduled"
        )
        mock_soccer_processor.process_match_data.return_value = [mock_match]
        
        # Setup empty H2H response
        mock_soccer_client.get_h2h_analysis.return_value = {}
        
        # Execute command
        await soccer_h2h_command(mock_interaction, "Arsenal", "Liverpool")
        
        # Verify no H2H data response
        mock_interaction.followup.send.assert_called_once()
        call_args = mock_interaction.followup.send.call_args
        embed = call_args.kwargs['embed']
        assert "No H2H Data" in embed.title

class TestSoccerStandingsCommand:
    """Test cases for /soccer-standings command"""
    
    @pytest.mark.asyncio
    async def test_standings_command_success(self, mock_interaction, mock_soccer_client, mock_soccer_processor, mock_soccer_embed_builder):
        """Test successful standings retrieval"""
        # Setup league choice
        league_choice = MockChoice("Premier League", "EPL")
        
        # Setup mocks
        mock_soccer_client.get_league_standings.return_value = MOCK_STANDINGS_RESPONSE
        
        # Mock embed builder
        mock_embed = MagicMock()
        mock_soccer_embed_builder.create_league_standings_embed.return_value = mock_embed
        
        # Execute command
        await soccer_standings_command(mock_interaction, league_choice)
        
        # Verify interactions
        mock_interaction.response.defer.assert_called_once()
        mock_soccer_client.get_league_standings.assert_called_once_with(228)  # EPL league ID
        mock_soccer_embed_builder.create_league_standings_embed.assert_called_once()
        mock_interaction.followup.send.assert_called_once_with(embed=mock_embed)
    
    @pytest.mark.asyncio
    async def test_standings_command_no_data(self, mock_interaction, mock_soccer_client, mock_soccer_processor, mock_soccer_embed_builder):
        """Test standings command when no data is available"""
        # Setup league choice
        league_choice = MockChoice("Premier League", "EPL")
        
        # Setup mock to return empty data
        mock_soccer_client.get_league_standings.return_value = {}
        
        # Execute command
        await soccer_standings_command(mock_interaction, league_choice)
        
        # Verify no data response
        mock_interaction.followup.send.assert_called_once()
        call_args = mock_interaction.followup.send.call_args
        embed = call_args.kwargs['embed']
        assert "No Standings Data" in embed.title
    
    @pytest.mark.asyncio
    async def test_standings_command_mcp_error(self, mock_interaction, mock_soccer_client, mock_soccer_processor, mock_soccer_embed_builder):
        """Test standings command when MCP server fails"""
        # Setup league choice
        league_choice = MockChoice("Premier League", "EPL")
        
        # Setup mock to raise exception
        mock_soccer_client.get_league_standings.side_effect = Exception("MCP server error")
        
        # Execute command
        await soccer_standings_command(mock_interaction, league_choice)
        
        # Verify error response
        mock_interaction.followup.send.assert_called_once()
        call_args = mock_interaction.followup.send.call_args
        embed = call_args.kwargs['embed']
        assert "MCP Server Error" in embed.title

class TestCommandParameterValidation:
    """Test parameter validation for all commands"""
    
    @pytest.mark.asyncio
    async def test_date_validation_valid_formats(self, mock_interaction, mock_soccer_client, mock_soccer_processor, mock_soccer_embed_builder):
        """Test that various valid date formats are accepted"""
        # Setup mocks
        mock_soccer_client.get_matches_for_date.return_value = MOCK_MATCHES_RESPONSE
        mock_soccer_processor.process_match_data.return_value = []
        
        valid_dates = [
            "08/18/2025",  # MM/DD/YYYY
            "18-08-2025",  # DD-MM-YYYY
            "2025-08-18"   # YYYY-MM-DD
        ]
        
        for date_format in valid_dates:
            # Reset mock
            mock_interaction.followup.send.reset_mock()
            
            # Execute command
            await soccer_schedule_command(mock_interaction, date=date_format)
            
            # Should not get date format error
            call_args = mock_interaction.followup.send.call_args
            embed = call_args.kwargs['embed']
            assert "Invalid Date Format" not in embed.title
    
    @pytest.mark.asyncio
    async def test_date_validation_invalid_formats(self, mock_interaction, mock_soccer_client, mock_soccer_processor, mock_soccer_embed_builder):
        """Test that invalid date formats are rejected"""
        invalid_dates = [
            "2025/13/01",  # Invalid month
            "32-01-2025",  # Invalid day
            "not-a-date",  # Not a date
            "2025-02-30"   # Invalid date
        ]
        
        for invalid_date in invalid_dates:
            # Reset mock
            mock_interaction.followup.send.reset_mock()
            
            # Execute command
            await soccer_schedule_command(mock_interaction, date=invalid_date)
            
            # Should get date format error
            call_args = mock_interaction.followup.send.call_args
            embed = call_args.kwargs['embed']
            assert "Invalid Date Format" in embed.title

class TestCommandErrorHandling:
    """Test error handling for all commands"""
    
    @pytest.mark.asyncio
    async def test_general_exception_handling(self, mock_interaction):
        """Test that general exceptions are handled gracefully"""
        # Mock to raise unexpected exception
        with patch('soccer_integration.SoccerMCPClient', side_effect=Exception("Unexpected error")):
            # Execute command
            await soccer_schedule_command(mock_interaction)
            
            # Should get general error response
            mock_interaction.followup.send.assert_called_once()
            call_args = mock_interaction.followup.send.call_args
            embed = call_args.kwargs['embed']
            assert "Command Error" in embed.title
    
    @pytest.mark.asyncio
    async def test_import_error_handling(self, mock_interaction):
        """Test handling of import errors"""
        # Mock import failure
        with patch('soccer_integration.SoccerMCPClient', side_effect=ImportError("Module not found")):
            # Execute command
            await soccer_schedule_command(mock_interaction)
            
            # Should handle import error gracefully
            mock_interaction.followup.send.assert_called_once()

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])