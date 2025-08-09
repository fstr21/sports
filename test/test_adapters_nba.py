"""
Unit tests for NBA adapter with frozen JSON samples.
Tests normalization functions with various data scenarios and missing data.
"""

import pytest
import json
from adapters.nba import normalize, extract_player_stats, extract_team_stats


class TestNBAAdapter:
    """Test cases for NBA adapter normalization functions."""
    
    def test_normalize_valid_data(self):
        """Test normalize function with valid MCP response data."""
        sample_data = {
            "ok": True,
            "data": {
                "summary": {
                    "boxscore": {
                        "players": [
                            {
                                "team": {"displayName": "Lakers"},
                                "statistics": [
                                    {
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "LeBron James"},
                                                "stats": ["38:45", "10-18", "2-5", "3-4", "2", "6", "8", "10", "1", "2", "3", "2", "25"]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ],
                        "teams": [
                            {
                                "team": {"displayName": "Lakers"},
                                "statistics": [
                                    {
                                        "stats": ["240:00", "45-90", "12-30", "18-24", "10", "35", "45", "28", "8", "5", "15", "20", "120"]
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }
        
        result = normalize(sample_data)
        
        assert 'players' in result
        assert 'team_stats' in result
        assert len(result['players']) == 1
        assert len(result['team_stats']) == 1
        
        # Check player stats
        player = result['players'][0]
        assert player['name'] == 'LeBron James'
        assert player['team'] == 'Lakers'
        assert player['minutes'] == '38:45'
        assert player['fg'] == '10-18'
        assert player['3p'] == '2-5'
        assert player['ft'] == '3-4'
        assert player['reb'] == '8'
        assert player['ast'] == '10'
        assert player['pts'] == '25'
        
        # Check team stats
        team = result['team_stats'][0]
        assert team['team'] == 'Lakers'
        assert team['fg'] == '45-90'
        assert team['pts'] == '120'

    def test_normalize_invalid_data(self):
        """Test normalize function with invalid MCP response data."""
        invalid_data = {"ok": False}
        result = normalize(invalid_data)
        assert 'error' in result
        assert result['error'] == 'Invalid MCP response data'

    def test_normalize_missing_boxscore(self):
        """Test normalize function with missing boxscore data."""
        missing_boxscore = {
            "ok": True,
            "data": {
                "summary": {}
            }
        }
        result = normalize(missing_boxscore)
        assert 'error' in result
        assert result['error'] == 'No boxscore data available'

    def test_normalize_empty_data(self):
        """Test normalize function with None/empty data."""
        result = normalize(None)
        assert 'error' in result
        assert result['error'] == 'Invalid MCP response data'
        
        result = normalize({})
        assert 'error' in result
        assert result['error'] == 'Invalid MCP response data'

    def test_extract_player_stats_complete_data(self):
        """Test player stats extraction with complete data."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Warriors"},
                    "statistics": [
                        {
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Stephen Curry"},
                                    "stats": ["35:20", "12-22", "8-15", "4-4", "1", "4", "5", "8", "2", "0", "4", "3", "36"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_player_stats(boxscore)
        assert len(result) == 1
        
        player = result[0]
        assert player['name'] == 'Stephen Curry'
        assert player['team'] == 'Warriors'
        assert player['minutes'] == '35:20'
        assert player['fg'] == '12-22'
        assert player['3p'] == '8-15'
        assert player['ft'] == '4-4'
        assert player['reb'] == '5'
        assert player['ast'] == '8'
        assert player['stl'] == '2'
        assert player['pts'] == '36'

    def test_extract_player_stats_insufficient_data(self):
        """Test player stats extraction with insufficient stat data."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Celtics"},
                    "statistics": [
                        {
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Jayson Tatum"},
                                    "stats": ["30:00", "8-15"]  # Only 2 stats, need at least 13
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_player_stats(boxscore)
        assert len(result) == 0  # Should not include players with insufficient data

    def test_extract_team_stats_complete_data(self):
        """Test team stats extraction with complete data."""
        boxscore = {
            "teams": [
                {
                    "team": {"displayName": "Heat"},
                    "statistics": [
                        {
                            "stats": ["240:00", "42-85", "10-28", "16-20", "8", "32", "40", "25", "7", "4", "12", "18", "110"]
                        }
                    ]
                }
            ]
        }
        
        result = extract_team_stats(boxscore)
        assert len(result) == 1
        
        team = result[0]
        assert team['team'] == 'Heat'
        assert team['fg'] == '42-85'
        assert team['3p'] == '10-28'
        assert team['ft'] == '16-20'
        assert team['reb'] == '40'
        assert team['ast'] == '25'
        assert team['pts'] == '110'

    def test_extract_stats_empty_boxscore(self):
        """Test stat extraction with empty boxscore."""
        empty_boxscore = {"players": [], "teams": []}
        
        player_result = extract_player_stats(empty_boxscore)
        team_result = extract_team_stats(empty_boxscore)
        
        assert len(player_result) == 0
        assert len(team_result) == 0

    def test_extract_stats_missing_athlete_data(self):
        """Test stat extraction when athlete data is missing."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Nets"},
                    "statistics": [
                        {
                            "athletes": [
                                {
                                    # Missing athlete data
                                    "stats": ["32:15", "9-16", "3-7", "2-2", "1", "5", "6", "7", "1", "1", "2", "3", "23"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_player_stats(boxscore)
        assert len(result) == 1
        
        player = result[0]
        assert player['name'] == 'Unknown'  # Should default to 'Unknown'
        assert player['team'] == 'Nets'

    def test_multiple_teams_and_players(self):
        """Test normalization with multiple teams and players."""
        sample_data = {
            "ok": True,
            "data": {
                "summary": {
                    "boxscore": {
                        "players": [
                            {
                                "team": {"displayName": "Lakers"},
                                "statistics": [
                                    {
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "LeBron James"},
                                                "stats": ["38:45", "10-18", "2-5", "3-4", "2", "6", "8", "10", "1", "2", "3", "2", "25"]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "team": {"displayName": "Warriors"},
                                "statistics": [
                                    {
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "Stephen Curry"},
                                                "stats": ["35:20", "12-22", "8-15", "4-4", "1", "4", "5", "8", "2", "0", "4", "3", "36"]
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
        
        result = normalize(sample_data)
        assert len(result['players']) == 2
        
        # Check both teams are represented
        teams = [player['team'] for player in result['players']]
        assert 'Lakers' in teams
        assert 'Warriors' in teams


if __name__ == '__main__':
    pytest.main([__file__])