"""
Integration tests for game CLI client with live MCP functionality.

These tests verify that the game CLI works correctly with the MCP server,
adapter integration, and OpenRouter LLM functionality.
"""

import asyncio
import pytest
import subprocess
import sys
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

# Add clients directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "clients"))

from game_cli import (
    get_game_summary_data, 
    format_game_summary, 
    apply_adapter_normalization,
    filter_fields,
    format_normalized_data,
    ask_question_about_game,
    get_adapter_for_league,
    LEAGUE_ADAPTERS
)
from core_mcp import game_summary, MCPError, MCPServerError, MCPValidationError
from core_llm import strict_answer, LLMError, LLMConfigurationError, LLMAPIError


class TestGameCLIIntegration:
    """Integration tests for game CLI with live MCP server."""
    
    @pytest.fixture
    def sample_nfl_game_response(self):
        """Sample NFL game summary response for testing."""
        return {
            "ok": True,
            "data": {
                "summary": {
                    "status": "Final",
                    "teams_meta": [
                        {
                            "id": "33",
                            "displayName": "Baltimore Ravens",
                            "abbrev": "BAL",
                            "score": "27"
                        },
                        {
                            "id": "17", 
                            "displayName": "Indianapolis Colts",
                            "abbrev": "IND",
                            "score": "21"
                        }
                    ],
                    "leaders": [
                        {
                            "displayName": "Lamar Jackson",
                            "displayValue": "250 passing yards"
                        },
                        {
                            "displayName": "Derrick Henry",
                            "displayValue": "120 rushing yards"
                        }
                    ],
                    "boxscore": {
                        "players": [
                            {
                                "team": {"displayName": "Ravens"},
                                "statistics": [
                                    {
                                        "name": "passing",
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "Lamar Jackson"},
                                                "stats": ["15", "25", "250", "10.0", "2", "0", "98.5"]
                                            }
                                        ]
                                    },
                                    {
                                        "name": "rushing",
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "Derrick Henry"},
                                                "stats": ["20", "120", "6.0", "1", "25"]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ],
                        "teams": [
                            {
                                "team": {"displayName": "Ravens"},
                                "statistics": [
                                    {"name": "totalYards", "displayValue": "425"}
                                ]
                            }
                        ]
                    }
                }
            },
            "meta": {
                "league": "nfl",
                "sport": "football",
                "event_id": "401547439"
            }
        }
    
    @pytest.fixture
    def sample_nba_game_response(self):
        """Sample NBA game summary response for testing."""
        return {
            "ok": True,
            "data": {
                "summary": {
                    "status": "Final",
                    "teams_meta": [
                        {
                            "id": "16",
                            "displayName": "Los Angeles Lakers",
                            "abbrev": "LAL",
                            "score": "112"
                        },
                        {
                            "id": "2",
                            "displayName": "Boston Celtics",
                            "abbrev": "BOS", 
                            "score": "108"
                        }
                    ],
                    "boxscore": {
                        "players": [
                            {
                                "team": {"displayName": "Lakers"},
                                "statistics": [
                                    {
                                        "name": "general",
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "LeBron James"},
                                                "stats": ["25", "8", "10", "10", "18", "2", "5", "3", "4"]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }
    
    def test_get_adapter_for_league(self):
        """Test adapter selection for different leagues."""
        # Test NFL
        adapter = get_adapter_for_league('nfl')
        assert adapter is not None
        assert hasattr(adapter, 'normalize')
        
        # Test NBA
        adapter = get_adapter_for_league('nba')
        assert adapter is not None
        
        # Test college football (should use NFL adapter)
        adapter = get_adapter_for_league('ncaaf')
        assert adapter is not None
        
        # Test invalid league
        adapter = get_adapter_for_league('invalid')
        assert adapter is None
    
    def test_apply_adapter_normalization_success(self, sample_nfl_game_response):
        """Test successful adapter normalization."""
        # Mock the NFL adapter
        mock_adapter = MagicMock()
        mock_adapter.normalize.return_value = {
            'passing': [{'name': 'Lamar Jackson', 'yards': '250'}],
            'rushing': [{'name': 'Derrick Henry', 'yards': '120'}]
        }
        
        with patch.dict('game_cli.LEAGUE_ADAPTERS', {'nfl': mock_adapter}):
            result = apply_adapter_normalization(sample_nfl_game_response, 'nfl')
            
            assert 'passing' in result
            assert 'rushing' in result
            mock_adapter.normalize.assert_called_once_with(sample_nfl_game_response)
    
    def test_apply_adapter_normalization_failure(self, sample_nfl_game_response):
        """Test adapter normalization failure handling."""
        # Mock adapter that raises exception
        mock_adapter = MagicMock()
        mock_adapter.normalize.side_effect = Exception("Adapter error")
        
        with patch.dict('game_cli.LEAGUE_ADAPTERS', {'nfl': mock_adapter}):
            result = apply_adapter_normalization(sample_nfl_game_response, 'nfl')
            
            # Should return original data on failure
            assert result == sample_nfl_game_response
    
    def test_apply_adapter_normalization_no_adapter(self, sample_nfl_game_response):
        """Test normalization when no adapter is available."""
        result = apply_adapter_normalization(sample_nfl_game_response, 'unknown_league')
        
        # Should return original data
        assert result == sample_nfl_game_response
    
    def test_filter_fields_nfl_data(self):
        """Test field filtering for NFL data structure."""
        nfl_data = {
            'passing': [
                {
                    'name': 'Lamar Jackson',
                    'team': 'Ravens',
                    'yards': '250',
                    'touchdowns': '2',
                    'completions_attempts': '15/25'
                }
            ],
            'rushing': [
                {
                    'name': 'Derrick Henry',
                    'team': 'Ravens',
                    'yards': '120',
                    'touchdowns': '1'
                }
            ]
        }
        
        # Filter for yards and touchdowns
        result = filter_fields(nfl_data, ['yards', 'touchdowns'], 'nfl')
        
        assert 'passing' in result
        assert 'rushing' in result
        
        # Check passing player
        passing_player = result['passing'][0]
        assert passing_player['name'] == 'Lamar Jackson'
        assert passing_player['team'] == 'Ravens'
        assert passing_player['yards'] == '250'
        assert passing_player['touchdowns'] == '2'
        assert 'completions_attempts' not in passing_player
        
        # Check rushing player
        rushing_player = result['rushing'][0]
        assert rushing_player['yards'] == '120'
        assert rushing_player['touchdowns'] == '1'
    
    def test_filter_fields_nba_data(self):
        """Test field filtering for NBA data structure."""
        nba_data = {
            'players': [
                {
                    'name': 'LeBron James',
                    'team': 'Lakers',
                    'pts': '25',
                    'reb': '8',
                    'ast': '10',
                    'fg': '10/18'
                }
            ]
        }
        
        # Filter for points and rebounds only
        result = filter_fields(nba_data, ['pts', 'reb'], 'nba')
        
        assert 'players' in result
        player = result['players'][0]
        assert player['name'] == 'LeBron James'
        assert player['team'] == 'Lakers'
        assert player['pts'] == '25'
        assert player['reb'] == '8'
        assert 'ast' not in player
        assert 'fg' not in player
    
    def test_filter_fields_unavailable_field(self):
        """Test field filtering with unavailable fields."""
        data = {
            'players': [
                {
                    'name': 'Player 1',
                    'team': 'Team 1',
                    'pts': '20'
                }
            ]
        }
        
        result = filter_fields(data, ['pts', 'nonexistent'], 'nba')
        
        player = result['players'][0]
        assert player['pts'] == '20'
        assert player['nonexistent'] == 'unavailable'
    
    def test_format_normalized_data_nfl(self):
        """Test formatting of normalized NFL data."""
        nfl_data = {
            'passing': [
                {
                    'name': 'Lamar Jackson',
                    'team': 'Ravens',
                    'completions_attempts': '15/25',
                    'yards': '250',
                    'touchdowns': '2'
                }
            ],
            'rushing': [
                {
                    'name': 'Derrick Henry',
                    'team': 'Ravens',
                    'carries': '20',
                    'yards': '120',
                    'touchdowns': '1'
                }
            ]
        }
        
        result = format_normalized_data(nfl_data, 'nfl')
        
        assert "PASSING STATS:" in result
        assert "RUSHING STATS:" in result
        assert "Lamar Jackson (Ravens)" in result
        assert "15/25" in result
        assert "250 yds" in result
        assert "Derrick Henry (Ravens)" in result
        assert "20 car" in result
        assert "120 yds" in result
    
    def test_format_normalized_data_nba(self):
        """Test formatting of normalized NBA data."""
        nba_data = {
            'players': [
                {
                    'name': 'LeBron James',
                    'team': 'Lakers',
                    'pts': '25',
                    'reb': '8',
                    'ast': '10'
                }
            ]
        }
        
        result = format_normalized_data(nba_data, 'nba')
        
        assert "PLAYER STATS:" in result
        assert "LeBron James (Lakers)" in result
        assert "25 pts" in result
        assert "8 reb" in result
        assert "10 ast" in result
    
    def test_format_normalized_data_with_fields(self):
        """Test formatting with field filtering."""
        nfl_data = {
            'passing': [
                {
                    'name': 'Lamar Jackson',
                    'team': 'Ravens',
                    'yards': '250',
                    'touchdowns': '2'
                }
            ]
        }
        
        result = format_normalized_data(nfl_data, 'nfl', fields=['yards'])
        
        assert "Lamar Jackson (Ravens)" in result
        assert "yards: 250" in result
        assert "touchdowns" not in result
    
    def test_format_game_summary_basic(self, sample_nfl_game_response):
        """Test basic game summary formatting."""
        result = format_game_summary(sample_nfl_game_response, 'nfl', '401547439', use_adapter=False)
        
        assert "Game Summary - NFL Event 401547439" in result
        assert "Status: Final" in result
        assert "Baltimore Ravens @ Indianapolis Colts" in result
        assert "Baltimore Ravens 27 - Indianapolis Colts 21" in result
        assert "Game Leaders:" in result
        assert "Lamar Jackson: 250 passing yards" in result
    
    def test_format_game_summary_no_data(self):
        """Test game summary formatting with no data."""
        empty_response = {"data": {}}
        result = format_game_summary(empty_response, 'nfl', '123', use_adapter=False)
        
        assert "No game summary data available" in result
        assert "nfl event 123" in result
    
    @pytest.mark.asyncio
    async def test_get_game_summary_data_success(self, sample_nfl_game_response):
        """Test successful game summary data retrieval."""
        with patch('game_cli.game_summary', new_callable=AsyncMock) as mock_game_summary:
            mock_game_summary.return_value = sample_nfl_game_response
            
            result = await get_game_summary_data('nfl', '401547439')
            
            assert result == sample_nfl_game_response
            mock_game_summary.assert_called_once_with('nfl', '401547439')
    
    @pytest.mark.asyncio
    async def test_get_game_summary_data_mcp_error(self):
        """Test game summary data retrieval with MCP error."""
        with patch('game_cli.game_summary', new_callable=AsyncMock) as mock_game_summary:
            mock_game_summary.side_effect = MCPServerError("Server error")
            
            with pytest.raises(MCPServerError):
                await get_game_summary_data('nfl', '401547439')
    
    @pytest.mark.asyncio
    async def test_ask_question_about_game_success(self, sample_nfl_game_response):
        """Test successful AI question about game data."""
        with patch('game_cli.strict_answer', new_callable=AsyncMock) as mock_strict_answer:
            mock_strict_answer.return_value = (True, "Lamar Jackson had 250 passing yards.")
            
            result = await ask_question_about_game(sample_nfl_game_response, "Who had the most passing yards?")
            
            assert result == "Lamar Jackson had 250 passing yards."
            mock_strict_answer.assert_called_once_with(sample_nfl_game_response, "Who had the most passing yards?")
    
    @pytest.mark.asyncio
    async def test_ask_question_about_game_llm_error(self, sample_nfl_game_response):
        """Test AI question with LLM error."""
        with patch('game_cli.strict_answer', new_callable=AsyncMock) as mock_strict_answer:
            mock_strict_answer.side_effect = LLMAPIError("API error")
            
            with pytest.raises(LLMAPIError):
                await ask_question_about_game(sample_nfl_game_response, "Who scored?")
    
    @pytest.mark.asyncio
    async def test_ask_question_about_game_failed_response(self, sample_nfl_game_response):
        """Test AI question with failed response."""
        with patch('game_cli.strict_answer', new_callable=AsyncMock) as mock_strict_answer:
            mock_strict_answer.return_value = (False, "Error message")
            
            with pytest.raises(LLMAPIError):
                await ask_question_about_game(sample_nfl_game_response, "Who scored?")


class TestGameCLILive:
    """Live integration tests with actual MCP server (skipped if server unavailable)."""
    
    def _is_mcp_server_available(self) -> bool:
        """Check if MCP server is available for testing."""
        try:
            server_path = Path(__file__).parent.parent / "sports_mcp" / "sports_ai_mcp.py"
            return server_path.exists()
        except Exception:
            return False
    
    @pytest.mark.skipif(not _is_mcp_server_available(None), reason="MCP server not available")
    @pytest.mark.asyncio
    async def test_game_summary_live_nfl(self):
        """Test live game summary functionality with NFL."""
        try:
            # Use a known NFL event ID (may need to be updated for current season)
            result = await game_summary('nfl', '401547439')
            
            # Basic response structure validation
            assert isinstance(result, dict)
            
            # If successful, should have game summary data
            if result.get('ok', True):
                data = result.get('data', {})
                summary = data.get('summary', {})
                
                # Should have basic game info
                assert isinstance(summary, dict)
                
                # May have teams_meta, boxscore, etc.
                if 'teams_meta' in summary:
                    teams = summary['teams_meta']
                    assert isinstance(teams, list)
                    if teams:
                        team = teams[0]
                        assert 'displayName' in team or 'id' in team
            
        except MCPError as e:
            # MCP errors are expected for invalid/old event IDs
            pytest.skip(f"MCP server error (expected): {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error in live test: {e}")
    
    @pytest.mark.skipif(not _is_mcp_server_available(None), reason="MCP server not available")
    @pytest.mark.asyncio
    async def test_game_summary_live_invalid_event(self):
        """Test live game summary with invalid event ID."""
        try:
            result = await game_summary('nfl', 'invalid_event_id')
            
            # Should either succeed with error info or raise MCPError
            if isinstance(result, dict) and not result.get('ok', True):
                # Error response is acceptable
                assert 'message' in result or 'error' in result
            
        except MCPError:
            # MCPError is expected for invalid event ID
            pass
        except Exception as e:
            pytest.fail(f"Unexpected error type: {e}")
    
    @pytest.mark.skipif(not _is_mcp_server_available(None), reason="MCP server not available")
    @pytest.mark.asyncio
    async def test_game_summary_live_invalid_league(self):
        """Test live game summary with invalid league."""
        with pytest.raises(MCPValidationError):
            await game_summary('invalid_league', '401547439')
    
    @pytest.mark.skipif(not _is_mcp_server_available(None), reason="MCP server not available")
    @pytest.mark.asyncio
    async def test_game_summary_live_multiple_leagues(self):
        """Test game summary with multiple leagues."""
        # Test different leagues with placeholder event IDs
        test_cases = [
            ('nfl', '401547439'),
            ('nba', '401584123'),
            ('mlb', '401581234')
        ]
        
        for league, event_id in test_cases:
            try:
                result = await game_summary(league, event_id)
                
                # Should return a valid response structure
                assert isinstance(result, dict)
                
                # Should have either success or expected error structure
                if not result.get('ok', True):
                    assert 'message' in result or 'error' in result
                
            except MCPError:
                # MCP errors are acceptable (e.g., event not found)
                continue
            except Exception as e:
                pytest.fail(f"Unexpected error for {league} {event_id}: {e}")


class TestGameCLICommand:
    """Test the command-line interface of game CLI."""
    
    def test_cli_help(self):
        """Test CLI help output."""
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent.parent / "clients" / "game_cli.py"), "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Get game summary data" in result.stdout
        assert "Supported leagues:" in result.stdout
        assert "nfl" in result.stdout
        assert "nba" in result.stdout
        assert "--json" in result.stdout
        assert "--ask" in result.stdout
        assert "--fields" in result.stdout
    
    def test_cli_missing_arguments(self):
        """Test CLI with missing required arguments."""
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent.parent / "clients" / "game_cli.py")],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 2  # argparse error
        assert "required" in result.stderr.lower() or "error" in result.stderr.lower()
    
    def test_cli_debug_flag(self):
        """Test CLI with debug flag (should not crash)."""
        # This test just ensures the debug flag is parsed correctly
        # We can't test actual functionality without a valid event ID
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent.parent / "clients" / "game_cli.py"), 
             "nfl", "test_event", "--debug", "--json"],
            capture_output=True,
            text=True
        )
        
        # Should fail due to invalid event, but not due to argument parsing
        assert "debug" not in result.stderr.lower() or result.returncode != 2


if __name__ == '__main__':
    pytest.main([__file__, "-v"])