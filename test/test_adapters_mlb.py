"""
Unit tests for MLB adapter with frozen JSON samples.
Tests normalization functions with various data scenarios and missing data.
"""

import pytest
import json
from adapters.mlb import normalize, extract_batting_stats, extract_pitching_stats


class TestMLBAdapter:
    """Test cases for MLB adapter normalization functions."""
    
    def test_normalize_valid_data(self):
        """Test normalize function with valid MCP response data."""
        sample_data = {
            "ok": True,
            "data": {
                "summary": {
                    "boxscore": {
                        "players": [
                            {
                                "team": {"displayName": "Yankees"},
                                "statistics": [
                                    {
                                        "name": "batting",
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "Aaron Judge"},
                                                "stats": ["4", "2", "3", "2", "1", "0", ".750", ".800", "1.250"]
                                            }
                                        ]
                                    },
                                    {
                                        "name": "pitching",
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "Gerrit Cole"},
                                                "stats": ["7.0", "5", "2", "2", "1", "9", "1", "2.57", "0.86"]
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
        
        assert 'batting' in result
        assert 'pitching' in result
        assert len(result['batting']) == 1
        assert len(result['pitching']) == 1
        
        # Check batting stats
        batting_player = result['batting'][0]
        assert batting_player['name'] == 'Aaron Judge'
        assert batting_player['team'] == 'Yankees'
        assert batting_player['at_bats'] == '4'
        assert batting_player['runs'] == '2'
        assert batting_player['hits'] == '3'
        assert batting_player['rbi'] == '2'
        
        # Check pitching stats
        pitching_player = result['pitching'][0]
        assert pitching_player['name'] == 'Gerrit Cole'
        assert pitching_player['team'] == 'Yankees'
        assert pitching_player['innings_pitched'] == '7.0'
        assert pitching_player['hits_allowed'] == '5'
        assert pitching_player['earned_runs'] == '2'

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

    def test_extract_batting_stats_complete_data(self):
        """Test batting stats extraction with complete data."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Red Sox"},
                    "statistics": [
                        {
                            "name": "batting",
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Mookie Betts"},
                                    "stats": ["4", "2", "3", "2", "1", "0", ".750", ".800", "1.250"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_batting_stats(boxscore)
        assert len(result) == 1
        
        player = result[0]
        assert player['name'] == 'Mookie Betts'
        assert player['team'] == 'Red Sox'
        assert player['at_bats'] == '4'
        assert player['runs'] == '2'
        assert player['hits'] == '3'
        assert player['rbi'] == '2'
        assert player['walks'] == '1'
        assert player['strikeouts'] == '0'
        assert player['avg'] == '.750'

    def test_extract_pitching_stats_complete_data(self):
        """Test pitching stats extraction with complete data."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Dodgers"},
                    "statistics": [
                        {
                            "name": "pitching",
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Clayton Kershaw"},
                                    "stats": ["6.0", "4", "1", "1", "2", "8", "0", "1.50", "1.00"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_pitching_stats(boxscore)
        assert len(result) == 1
        
        player = result[0]
        assert player['name'] == 'Clayton Kershaw'
        assert player['team'] == 'Dodgers'
        assert player['innings_pitched'] == '6.0'
        assert player['hits_allowed'] == '4'
        assert player['runs_allowed'] == '1'
        assert player['earned_runs'] == '1'
        assert player['walks_allowed'] == '2'
        assert player['strikeouts'] == '8'

    def test_extract_stats_insufficient_data(self):
        """Test stat extraction with insufficient data."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Giants"},
                    "statistics": [
                        {
                            "name": "batting",
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Buster Posey"},
                                    "stats": ["3", "1"]  # Only 2 stats, need at least 6
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_batting_stats(boxscore)
        assert len(result) == 0  # Should not include players with insufficient data

    def test_extract_stats_missing_categories(self):
        """Test stat extraction when specific categories are missing."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Cubs"},
                    "statistics": [
                        {
                            "name": "fielding",  # Different category
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Kris Bryant"},
                                    "stats": ["9", "0", "0"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        batting_result = extract_batting_stats(boxscore)
        pitching_result = extract_pitching_stats(boxscore)
        
        assert len(batting_result) == 0
        assert len(pitching_result) == 0

    def test_extract_stats_empty_boxscore(self):
        """Test stat extraction with empty boxscore."""
        empty_boxscore = {"players": []}
        
        batting_result = extract_batting_stats(empty_boxscore)
        pitching_result = extract_pitching_stats(empty_boxscore)
        
        assert len(batting_result) == 0
        assert len(pitching_result) == 0

    def test_multiple_teams_and_players(self):
        """Test normalization with multiple teams and players."""
        sample_data = {
            "ok": True,
            "data": {
                "summary": {
                    "boxscore": {
                        "players": [
                            {
                                "team": {"displayName": "Yankees"},
                                "statistics": [
                                    {
                                        "name": "batting",
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "Aaron Judge"},
                                                "stats": ["4", "2", "3", "2", "1", "0", ".750", ".800", "1.250"]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "team": {"displayName": "Red Sox"},
                                "statistics": [
                                    {
                                        "name": "batting",
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "Rafael Devers"},
                                                "stats": ["4", "1", "2", "1", "0", "1", ".500", ".500", ".750"]
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
        assert len(result['batting']) == 2
        
        # Check both teams are represented
        teams = [player['team'] for player in result['batting']]
        assert 'Yankees' in teams
        assert 'Red Sox' in teams


if __name__ == '__main__':
    pytest.main([__file__])