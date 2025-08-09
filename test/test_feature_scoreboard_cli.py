"""
Integration tests for scoreboard CLI client with live MCP functionality.

These tests verify that the scoreboard CLI works correctly with the MCP server
and can handle various scenarios including error conditions.
"""

import asyncio
import pytest
import subprocess
import sys
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock

# Add clients directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "clients"))

from scoreboard_cli import get_events, format_event_table, format_json_output, validate_date
from core_mcp import scoreboard, MCPError, MCPServerError, MCPValidationError, LEAGUE_MAPPING


class TestScoreboardCLIIntegration:
    """Integration tests for scoreboard CLI with live MCP server."""
    
    @pytest.fixture
    def sample_scoreboard_response(self):
        """Sample MCP scoreboard response for testing."""
        return {
            "ok": True,
            "data": {
                "scoreboard": {
                    "events": [
                        {
                            "event_id": "401547439",
                            "date": "2024-08-15T20:00Z",
                            "status": "Final",
                            "home": {
                                "id": "17",
                                "displayName": "Indianapolis Colts",
                                "abbrev": "IND",
                                "score": "21"
                            },
                            "away": {
                                "id": "33", 
                                "displayName": "Baltimore Ravens",
                                "abbrev": "BAL",
                                "score": "27"
                            }
                        },
                        {
                            "event_id": "401547440",
                            "date": "2024-08-15T21:00Z",
                            "status": "Pre-Game",
                            "home": {
                                "id": "2",
                                "displayName": "Buffalo Bills",
                                "abbrev": "BUF",
                                "score": ""
                            },
                            "away": {
                                "id": "12",
                                "displayName": "Kansas City Chiefs", 
                                "abbrev": "KC",
                                "score": ""
                            }
                        }
                    ]
                }
            },
            "meta": {
                "league": "nfl",
                "sport": "football",
                "url": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
            }
        }
    
    @pytest.fixture
    def empty_scoreboard_response(self):
        """Empty scoreboard response for testing."""
        return {
            "ok": True,
            "data": {
                "scoreboard": {
                    "events": []
                }
            },
            "meta": {
                "league": "nfl",
                "sport": "football"
            }
        }
    
    def test_validate_date_valid_formats(self):
        """Test date validation with valid formats."""
        assert validate_date("20240815") is True
        assert validate_date("20231225") is True
        assert validate_date("20240229") is True  # Leap year
    
    def test_validate_date_invalid_formats(self):
        """Test date validation with invalid formats."""
        assert validate_date("2024-08-15") is False  # Wrong format
        assert validate_date("240815") is False      # Too short
        assert validate_date("202408155") is False   # Too long
        assert validate_date("20240832") is False    # Invalid day
        assert validate_date("20241301") is False    # Invalid month
        assert validate_date("abcd1234") is False    # Non-numeric
        assert validate_date("") is False            # Empty string
    
    def test_format_event_table_with_scores(self, sample_scoreboard_response):
        """Test event table formatting with scores."""
        events = sample_scoreboard_response["data"]["scoreboard"]["events"]
        result = format_event_table(events)
        
        assert "EVENT_ID" in result
        assert "AWAY @ HOME" in result
        assert "STATUS" in result
        assert "DATE" in result
        assert "401547439" in result
        assert "BAL 27 @ IND 21" in result
        assert "Final" in result
        assert "KC @ BUF" in result  # No scores for pre-game
        assert "Pre-Game" in result
    
    def test_format_event_table_empty(self):
        """Test event table formatting with empty events."""
        result = format_event_table([])
        assert result == "No events found."
    
    def test_format_event_table_missing_data(self):
        """Test event table formatting with missing data."""
        events = [
            {
                "event_id": "123",
                # Missing other fields
            }
        ]
        result = format_event_table(events)
        assert "123" in result
        assert "N/A" in result
    
    def test_format_json_output(self, sample_scoreboard_response):
        """Test JSON output formatting."""
        result = format_json_output(sample_scoreboard_response)
        
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed["ok"] is True
        assert "data" in parsed
        assert "scoreboard" in parsed["data"]
        
        # Should be pretty-printed (contains newlines and indentation)
        assert "\n" in result
        assert "  " in result
    
    @pytest.mark.asyncio
    async def test_get_events_success_with_mock(self, sample_scoreboard_response, capsys):
        """Test get_events with mocked MCP response."""
        with patch('scoreboard_cli.scoreboard', new_callable=AsyncMock) as mock_scoreboard:
            mock_scoreboard.return_value = sample_scoreboard_response
            
            await get_events('nfl', '20240815', 'pretty')
            
            captured = capsys.readouterr()
            assert "NFL Events - 20240815" in captured.out
            assert "401547439" in captured.out
            assert "BAL 27 @ IND 21" in captured.out
            assert "Final" in captured.out
            
            mock_scoreboard.assert_called_once_with('nfl', '20240815')
    
    @pytest.mark.asyncio
    async def test_get_events_json_output_with_mock(self, sample_scoreboard_response, capsys):
        """Test get_events with JSON output format."""
        with patch('scoreboard_cli.scoreboard', new_callable=AsyncMock) as mock_scoreboard:
            mock_scoreboard.return_value = sample_scoreboard_response
            
            await get_events('nfl', None, 'json')
            
            captured = capsys.readouterr()
            # Should output JSON
            parsed = json.loads(captured.out)
            assert parsed["ok"] is True
            
            mock_scoreboard.assert_called_once_with('nfl', None)
    
    @pytest.mark.asyncio
    async def test_get_events_empty_response_with_mock(self, empty_scoreboard_response, capsys):
        """Test get_events with empty scoreboard response."""
        with patch('scoreboard_cli.scoreboard', new_callable=AsyncMock) as mock_scoreboard:
            mock_scoreboard.return_value = empty_scoreboard_response
            
            await get_events('nfl', '20240815', 'pretty')
            
            captured = capsys.readouterr()
            assert "No events found for NFL on 20240815" in captured.out
            
            mock_scoreboard.assert_called_once_with('nfl', '20240815')
    
    @pytest.mark.asyncio
    async def test_get_events_mcp_error_handling(self, capsys):
        """Test get_events error handling for MCP errors."""
        with patch('scoreboard_cli.scoreboard', new_callable=AsyncMock) as mock_scoreboard:
            mock_scoreboard.side_effect = MCPServerError("ESPN API returned 500 status")
            
            with pytest.raises(SystemExit):
                await get_events('nfl', '20240815', 'pretty')
            
            captured = capsys.readouterr()
            assert "❌ Error: ESPN API returned 500 status" in captured.err
    
    @pytest.mark.asyncio
    async def test_get_events_validation_error_handling(self, capsys):
        """Test get_events error handling for validation errors."""
        with patch('scoreboard_cli.scoreboard', new_callable=AsyncMock) as mock_scoreboard:
            mock_scoreboard.side_effect = MCPValidationError("Invalid league 'xyz'")
            
            with pytest.raises(SystemExit):
                await get_events('xyz', '20240815', 'pretty')
            
            captured = capsys.readouterr()
            assert "❌ Error: Invalid league 'xyz'" in captured.err
    
    @pytest.mark.asyncio
    async def test_get_events_unexpected_error_handling(self, capsys):
        """Test get_events error handling for unexpected errors."""
        with patch('scoreboard_cli.scoreboard', new_callable=AsyncMock) as mock_scoreboard:
            mock_scoreboard.side_effect = ValueError("Unexpected error")
            
            with pytest.raises(SystemExit):
                await get_events('nfl', '20240815', 'pretty')
            
            captured = capsys.readouterr()
            assert "❌ Unexpected error: Unexpected error" in captured.err


class TestScoreboardCLILive:
    """Live integration tests with actual MCP server (skipped if server unavailable)."""
    
    def _is_mcp_server_available(self) -> bool:
        """Check if MCP server is available for testing."""
        try:
            # Try to find the MCP server script
            server_path = Path(__file__).parent.parent / "sports_mcp" / "sports_ai_mcp.py"
            return server_path.exists()
        except Exception:
            return False
    
    @pytest.mark.skipif(not _is_mcp_server_available(None), reason="MCP server not available")
    @pytest.mark.asyncio
    async def test_scoreboard_live_nfl(self):
        """Test live scoreboard functionality with NFL."""
        try:
            # Test with a recent date that should have data
            result = await scoreboard('nfl', '20240815')
            
            # Basic response structure validation
            assert isinstance(result, dict)
            assert 'data' in result or 'ok' in result
            
            # If successful, should have scoreboard data
            if result.get('ok', True):
                data = result.get('data', {})
                scoreboard_data = data.get('scoreboard', {})
                events = scoreboard_data.get('events', [])
                
                # Events should be a list (may be empty)
                assert isinstance(events, list)
                
                # If events exist, validate structure
                if events:
                    event = events[0]
                    assert 'event_id' in event
                    assert 'status' in event
                    assert 'home' in event
                    assert 'away' in event
            
        except MCPError as e:
            # MCP errors are expected in some cases (e.g., no data for date)
            pytest.skip(f"MCP server error (expected): {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error in live test: {e}")
    
    @pytest.mark.skipif(not _is_mcp_server_available(None), reason="MCP server not available")
    @pytest.mark.asyncio
    async def test_scoreboard_live_nba(self):
        """Test live scoreboard functionality with NBA."""
        try:
            # Test NBA scoreboard (may be empty in off-season)
            result = await scoreboard('nba')
            
            # Basic response structure validation
            assert isinstance(result, dict)
            
            # Should not raise exceptions for valid league
            if result.get('ok', True):
                data = result.get('data', {})
                scoreboard_data = data.get('scoreboard', {})
                events = scoreboard_data.get('events', [])
                assert isinstance(events, list)
            
        except MCPError as e:
            # MCP errors are expected in some cases
            pytest.skip(f"MCP server error (expected): {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error in live NBA test: {e}")
    
    @pytest.mark.skipif(not _is_mcp_server_available(None), reason="MCP server not available")
    @pytest.mark.asyncio
    async def test_scoreboard_live_invalid_league(self):
        """Test live scoreboard with invalid league."""
        with pytest.raises(MCPValidationError):
            await scoreboard('invalid_league')
    
    @pytest.mark.skipif(not _is_mcp_server_available(None), reason="MCP server not available")
    @pytest.mark.asyncio
    async def test_scoreboard_live_all_supported_leagues(self):
        """Test that all supported leagues can be called without errors."""
        # Test a subset of leagues to avoid rate limiting
        test_leagues = ['nfl', 'nba', 'mlb']
        
        for league in test_leagues:
            try:
                result = await scoreboard(league)
                
                # Should return a valid response structure
                assert isinstance(result, dict)
                
                # Should have either success or expected error structure
                if not result.get('ok', True):
                    # If not ok, should have error information
                    assert 'message' in result or 'error' in result
                
            except MCPError:
                # MCP errors are acceptable (e.g., no data available)
                continue
            except Exception as e:
                pytest.fail(f"Unexpected error for league {league}: {e}")


class TestScoreboardCLICommand:
    """Test the command-line interface of scoreboard CLI."""
    
    def test_cli_help(self):
        """Test CLI help output."""
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent.parent / "clients" / "scoreboard_cli.py"), "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Get scoreboard events" in result.stdout
        assert "Supported leagues:" in result.stdout
        assert "nfl" in result.stdout
        assert "nba" in result.stdout
    
    def test_cli_invalid_league(self):
        """Test CLI with invalid league."""
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent.parent / "clients" / "scoreboard_cli.py"), 
             "events", "invalid_league"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 1
        assert "Unsupported league 'invalid_league'" in result.stderr
    
    def test_cli_invalid_date(self):
        """Test CLI with invalid date format."""
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent.parent / "clients" / "scoreboard_cli.py"), 
             "events", "nfl", "2024-08-15"],  # Wrong format
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 1
        assert "Invalid date format" in result.stderr


if __name__ == '__main__':
    pytest.main([__file__, "-v"])