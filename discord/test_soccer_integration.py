"""
Unit tests for Soccer Integration Module
Tests MCP client connection and basic data structures
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any

# Import the module under test
from soccer_integration import (
    SoccerMCPClient,
    ProcessedMatch,
    BettingOdds,
    H2HInsights,
    Team,
    League,
    OddsFormat,
    H2HSummary,
    OverUnder,
    Handicap,
    SoccerMCPError,
    MCPConnectionError,
    MCPDataError,
    MCPTimeoutError,
    SUPPORTED_LEAGUES,
    validate_date_format,
    get_league_config,
    clean_team_name_for_channel
)

# ============================================================================
# TEST DATA
# ============================================================================

MOCK_MCP_RESPONSE = {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "content": [
            {
                "type": "text",
                "text": json.dumps({
                    "matches": [
                        {
                            "match_id": 12345,
                            "home_team": {"id": 1, "name": "Arsenal", "short_name": "ARS"},
                            "away_team": {"id": 2, "name": "Liverpool", "short_name": "LIV"},
                            "league": {"id": 228, "name": "Premier League", "country": "England"},
                            "date": "2025-08-17",
                            "time": "15:00",
                            "venue": "Emirates Stadium",
                            "status": "scheduled"
                        }
                    ]
                })
            }
        ]
    }
}

MOCK_H2H_RESPONSE = {
    "jsonrpc": "2.0", 
    "id": 1,
    "result": {
        "content": [
            {
                "type": "text",
                "text": json.dumps({
                    "total_meetings": 10,
                    "home_team_wins": 4,
                    "away_team_wins": 3,
                    "draws": 3,
                    "avg_goals_per_game": 2.5,
                    "recent_form": {
                        "Arsenal": ["W", "L", "W", "D", "W"],
                        "Liverpool": ["W", "W", "L", "W", "D"]
                    }
                })
            }
        ]
    }
}

MOCK_ERROR_RESPONSE = {
    "jsonrpc": "2.0",
    "id": 1,
    "error": {
        "code": -1,
        "message": "Tool not found"
    }
}

# ============================================================================
# DATA MODEL TESTS
# ============================================================================

class TestOddsFormat:
    """Test OddsFormat data model"""
    
    def test_from_decimal_favorite(self):
        """Test conversion of favorite odds (decimal < 2.0)"""
        odds = OddsFormat.from_decimal(1.5)
        assert odds.decimal == 1.5
        assert odds.american == -200
    
    def test_from_decimal_underdog(self):
        """Test conversion of underdog odds (decimal >= 2.0)"""
        odds = OddsFormat.from_decimal(2.5)
        assert odds.decimal == 2.5
        assert odds.american == 150
    
    def test_from_decimal_even(self):
        """Test conversion of even odds (decimal = 2.0)"""
        odds = OddsFormat.from_decimal(2.0)
        assert odds.decimal == 2.0
        assert odds.american == 100

class TestTeam:
    """Test Team data model"""
    
    def test_team_creation(self):
        """Test basic team creation"""
        team = Team(
            id=1,
            name="Arsenal FC",
            short_name="ARS",
            logo_url="https://example.com/logo.png",
            country="England"
        )
        
        assert team.id == 1
        assert team.name == "Arsenal FC"
        assert team.short_name == "ARS"
        assert team.logo_url == "https://example.com/logo.png"
        assert team.country == "England"
    
    def test_clean_name_property(self):
        """Test team name cleaning for channel creation"""
        team = Team(id=1, name="Manchester United F.C.", short_name="MUN")
        assert team.clean_name == "manchester-united-fc"
        
        team2 = Team(id=2, name="Real Madrid C.F.", short_name="RMA")
        assert team2.clean_name == "real-madrid-cf"

class TestLeague:
    """Test League data model"""
    
    def test_league_creation(self):
        """Test basic league creation"""
        league = League(
            id=228,
            name="Premier League",
            country="England",
            season="2024-25"
        )
        
        assert league.id == 228
        assert league.name == "Premier League"
        assert league.country == "England"
        assert league.season == "2024-25"
    
    def test_config_property(self):
        """Test league config property"""
        league = League(id=228, name="Premier League", country="England")
        config = league.config
        
        assert config is not None
        assert config["name"] == "Premier League"
        assert config["country"] == "England"
        assert config["color"] == 0x3d195b

class TestBettingOdds:
    """Test BettingOdds data model"""
    
    def test_betting_odds_creation(self):
        """Test betting odds creation with all markets"""
        home_win = OddsFormat.from_decimal(2.1)
        draw = OddsFormat.from_decimal(3.2)
        away_win = OddsFormat.from_decimal(3.8)
        
        odds = BettingOdds(
            home_win=home_win,
            draw=draw,
            away_win=away_win
        )
        
        assert odds.home_win == home_win
        assert odds.draw == draw
        assert odds.away_win == away_win
        assert odds.has_odds is True
    
    def test_has_odds_property_false(self):
        """Test has_odds property when no odds available"""
        odds = BettingOdds()
        assert odds.has_odds is False
    
    def test_has_odds_property_true(self):
        """Test has_odds property when odds available"""
        odds = BettingOdds(home_win=OddsFormat.from_decimal(2.0))
        assert odds.has_odds is True

class TestH2HInsights:
    """Test H2HInsights data model"""
    
    def test_h2h_insights_creation(self):
        """Test H2H insights creation"""
        insights = H2HInsights(
            total_meetings=10,
            home_team_wins=4,
            away_team_wins=3,
            draws=3,
            avg_goals_per_game=2.5
        )
        
        assert insights.total_meetings == 10
        assert insights.home_team_wins == 4
        assert insights.away_team_wins == 3
        assert insights.draws == 3
        assert insights.avg_goals_per_game == 2.5
    
    def test_percentage_calculations(self):
        """Test win percentage calculations"""
        insights = H2HInsights(
            total_meetings=10,
            home_team_wins=4,
            away_team_wins=3,
            draws=3,
            avg_goals_per_game=2.5
        )
        
        assert insights.home_win_percentage == 40.0
        assert insights.away_win_percentage == 30.0
        assert insights.draw_percentage == 30.0
    
    def test_percentage_calculations_zero_meetings(self):
        """Test percentage calculations with zero meetings"""
        insights = H2HInsights(
            total_meetings=0,
            home_team_wins=0,
            away_team_wins=0,
            draws=0,
            avg_goals_per_game=0.0
        )
        
        assert insights.home_win_percentage == 0.0
        assert insights.away_win_percentage == 0.0
        assert insights.draw_percentage == 0.0

class TestProcessedMatch:
    """Test ProcessedMatch data model"""
    
    def test_processed_match_creation(self):
        """Test processed match creation"""
        home_team = Team(id=1, name="Arsenal", short_name="ARS")
        away_team = Team(id=2, name="Liverpool", short_name="LIV")
        league = League(id=228, name="Premier League", country="England")
        
        match = ProcessedMatch(
            match_id=12345,
            home_team=home_team,
            away_team=away_team,
            league=league,
            date="2025-08-17",
            time="15:00",
            venue="Emirates Stadium",
            status="scheduled"
        )
        
        assert match.match_id == 12345
        assert match.home_team == home_team
        assert match.away_team == away_team
        assert match.league == league
        assert match.date == "2025-08-17"
        assert match.time == "15:00"
        assert match.venue == "Emirates Stadium"
        assert match.status == "scheduled"
    
    def test_channel_name_property(self):
        """Test channel name generation"""
        home_team = Team(id=1, name="Arsenal", short_name="ARS")
        away_team = Team(id=2, name="Liverpool", short_name="LIV")
        league = League(id=228, name="Premier League", country="England")
        
        match = ProcessedMatch(
            match_id=12345,
            home_team=home_team,
            away_team=away_team,
            league=league,
            date="2025-08-17",
            time="15:00",
            venue="Emirates Stadium",
            status="scheduled"
        )
        
        expected_name = "📊 08-17-liverpool-vs-arsenal"
        assert match.channel_name == expected_name
    
    def test_display_time_property(self):
        """Test time display formatting"""
        home_team = Team(id=1, name="Arsenal", short_name="ARS")
        away_team = Team(id=2, name="Liverpool", short_name="LIV")
        league = League(id=228, name="Premier League", country="England")
        
        match = ProcessedMatch(
            match_id=12345,
            home_team=home_team,
            away_team=away_team,
            league=league,
            date="2025-08-17",
            time="15:00",
            venue="Emirates Stadium",
            status="scheduled"
        )
        
        assert match.display_time == "03:00 PM"
    
    def test_display_time_invalid_format(self):
        """Test time display with invalid format"""
        home_team = Team(id=1, name="Arsenal", short_name="ARS")
        away_team = Team(id=2, name="Liverpool", short_name="LIV")
        league = League(id=228, name="Premier League", country="England")
        
        match = ProcessedMatch(
            match_id=12345,
            home_team=home_team,
            away_team=away_team,
            league=league,
            date="2025-08-17",
            time="invalid",
            venue="Emirates Stadium",
            status="scheduled"
        )
        
        assert match.display_time == "invalid"

# ============================================================================
# MCP CLIENT TESTS
# ============================================================================

class TestSoccerMCPClient:
    """Test SoccerMCPClient functionality"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        return SoccerMCPClient()
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, client):
        """Test client initialization"""
        assert client.mcp_url == "https://soccermcp-production.up.railway.app/mcp"
        assert client.timeout == 30.0
        assert "get_matches" in client.supported_tools
        assert "get_head_to_head" in client.supported_tools
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality"""
        async with SoccerMCPClient() as client:
            assert client._session is not None
        # Session should be closed after exiting context
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_call_mcp_tool_success(self, mock_post, client):
        """Test successful MCP tool call"""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_MCP_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = await client.call_mcp_tool("get_matches", {"date": "2025-08-17"})
        
        assert "content" in result
        mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_call_mcp_tool_error_response(self, mock_post, client):
        """Test MCP tool call with error response"""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_ERROR_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with pytest.raises(MCPDataError, match="MCP server error"):
            await client.call_mcp_tool("get_matches", {"date": "2025-08-17"})
    
    @pytest.mark.asyncio
    async def test_call_mcp_tool_unsupported_tool(self, client):
        """Test calling unsupported MCP tool"""
        with pytest.raises(MCPDataError, match="Tool 'unsupported_tool' not supported"):
            await client.call_mcp_tool("unsupported_tool", {})
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_call_mcp_tool_timeout(self, mock_post, client):
        """Test MCP tool call timeout"""
        import httpx
        mock_post.side_effect = httpx.TimeoutException("Request timed out")
        
        with pytest.raises(MCPTimeoutError, match="Request to MCP server timed out"):
            await client.call_mcp_tool("get_matches", {"date": "2025-08-17"})
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_call_mcp_tool_http_error(self, mock_post, client):
        """Test MCP tool call HTTP error"""
        import httpx
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.side_effect = httpx.HTTPStatusError("Server Error", request=None, response=mock_response)
        
        with pytest.raises(MCPConnectionError, match="HTTP error 500"):
            await client.call_mcp_tool("get_matches", {"date": "2025-08-17"})
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_get_matches_for_date(self, mock_post, client):
        """Test getting matches for specific date"""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_MCP_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = await client.get_matches_for_date("2025-08-17")
        
        assert result is not None
        mock_post.assert_called_once()
        
        # Verify the request payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['params']['name'] == 'get_matches'
        assert payload['params']['arguments']['date'] == '2025-08-17'
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_get_matches_for_date_with_league_filter(self, mock_post, client):
        """Test getting matches with league filter"""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_MCP_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = await client.get_matches_for_date("2025-08-17", "EPL")
        
        assert result is not None
        
        # Verify the request payload includes league filter
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['params']['arguments']['league'] == 'EPL'
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_get_h2h_analysis(self, mock_post, client):
        """Test getting H2H analysis"""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_H2H_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = await client.get_h2h_analysis(1, 2)
        
        assert result is not None
        
        # Verify the request payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['params']['name'] == 'get_head_to_head'
        assert payload['params']['arguments']['team1_id'] == 1
        assert payload['params']['arguments']['team2_id'] == 2
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_validate_connection_success(self, mock_post, client):
        """Test successful connection validation"""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_MCP_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        is_valid = await client.validate_connection()
        
        assert is_valid is True
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_validate_connection_failure(self, mock_post, client):
        """Test failed connection validation"""
        import httpx
        mock_post.side_effect = httpx.RequestError("Connection failed")
        
        is_valid = await client.validate_connection()
        
        assert is_valid is False

# ============================================================================
# UTILITY FUNCTION TESTS
# ============================================================================

class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_validate_date_format_mmddyyyy(self):
        """Test date validation with MM/DD/YYYY format"""
        result = validate_date_format("08/17/2025")
        assert result == "2025-08-17"
    
    def test_validate_date_format_ddmmyyyy(self):
        """Test date validation with DD-MM-YYYY format"""
        result = validate_date_format("17-08-2025")
        assert result == "2025-08-17"
    
    def test_validate_date_format_yyyymmdd(self):
        """Test date validation with YYYY-MM-DD format"""
        result = validate_date_format("2025-08-17")
        assert result == "2025-08-17"
    
    def test_validate_date_format_invalid(self):
        """Test date validation with invalid format"""
        with pytest.raises(ValueError, match="Invalid date format"):
            validate_date_format("invalid-date")
    
    def test_validate_date_format_out_of_range_past(self):
        """Test date validation with date too far in past"""
        past_date = (datetime.now() - timedelta(days=60)).strftime("%m/%d/%Y")
        with pytest.raises(ValueError, match="Date must be within 30 days past to 1 year future"):
            validate_date_format(past_date)
    
    def test_validate_date_format_out_of_range_future(self):
        """Test date validation with date too far in future"""
        future_date = (datetime.now() + timedelta(days=400)).strftime("%m/%d/%Y")
        with pytest.raises(ValueError, match="Date must be within 30 days past to 1 year future"):
            validate_date_format(future_date)
    
    def test_get_league_config_by_name(self):
        """Test getting league config by name"""
        config = get_league_config("EPL")
        assert config is not None
        assert config["name"] == "Premier League"
        assert config["id"] == 228
    
    def test_get_league_config_by_id(self):
        """Test getting league config by ID"""
        config = get_league_config(228)
        assert config is not None
        assert config["name"] == "Premier League"
        assert config["country"] == "England"
    
    def test_get_league_config_not_found(self):
        """Test getting league config for non-existent league"""
        config = get_league_config("INVALID")
        assert config is None
        
        config = get_league_config(999)
        assert config is None
    
    def test_clean_team_name_for_channel_basic(self):
        """Test basic team name cleaning"""
        result = clean_team_name_for_channel("Arsenal FC")
        assert result == "arsenal-fc"
    
    def test_clean_team_name_for_channel_complex(self):
        """Test complex team name cleaning"""
        result = clean_team_name_for_channel("Manchester United F.C.")
        assert result == "manchester-united-fc"
    
    def test_clean_team_name_for_channel_special_chars(self):
        """Test team name cleaning with special characters"""
        result = clean_team_name_for_channel("Real Madrid C.F. (Spain)")
        assert result == "real-madrid-cf-spain"
    
    def test_clean_team_name_for_channel_long_name(self):
        """Test team name cleaning with very long name"""
        long_name = "Very Long Team Name That Exceeds Twenty Characters"
        result = clean_team_name_for_channel(long_name)
        assert len(result) <= 20
        assert not result.endswith('-')
    
    def test_clean_team_name_for_channel_empty(self):
        """Test team name cleaning with empty string"""
        result = clean_team_name_for_channel("")
        assert result == "team"
    
    def test_clean_team_name_for_channel_multiple_dashes(self):
        """Test team name cleaning removes multiple consecutive dashes"""
        result = clean_team_name_for_channel("Team--With--Multiple--Dashes")
        assert "--" not in result
        # The function also truncates to 20 characters, so we expect truncation
        expected = "team-with-multiple-d"  # Truncated to 20 chars and trailing dash removed
        assert result == expected

# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

class TestConfiguration:
    """Test configuration constants"""
    
    def test_supported_leagues_structure(self):
        """Test supported leagues configuration structure"""
        assert "EPL" in SUPPORTED_LEAGUES
        assert "La Liga" in SUPPORTED_LEAGUES
        assert "MLS" in SUPPORTED_LEAGUES
        assert "Bundesliga" in SUPPORTED_LEAGUES
        assert "Serie A" in SUPPORTED_LEAGUES
        assert "UEFA" in SUPPORTED_LEAGUES
        
        for league, config in SUPPORTED_LEAGUES.items():
            assert "id" in config
            assert "name" in config
            assert "country" in config
            assert "color" in config
            assert "emoji" in config
            assert isinstance(config["id"], int)
            assert isinstance(config["color"], int)
    
    def test_league_ids_unique(self):
        """Test that all league IDs are unique"""
        ids = [config["id"] for config in SUPPORTED_LEAGUES.values()]
        assert len(ids) == len(set(ids)), "League IDs must be unique"
    
    def test_league_colors_valid(self):
        """Test that all league colors are valid hex values"""
        for league, config in SUPPORTED_LEAGUES.items():
            color = config["color"]
            assert 0x000000 <= color <= 0xFFFFFF, f"Invalid color for {league}: {hex(color)}"

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])