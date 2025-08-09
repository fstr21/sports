"""
Unit tests for WNBA adapter with frozen JSON samples.
Tests normalization functions with various data scenarios and missing data.
"""

import pytest
import json
from adapters.wnba import normalize, extract_player_stats, extract_team_stats


class TestWNBAAdapter:
    """Test cases for WNBA adapter normalization functions."""
    
    def test_normalize_valid_data(self):
        """Test normalize function with valid MCP response data."""
        sample_data = {
            "ok": True,
            "data": {
                "summary": {
                    "boxscore": {
                        "players": [
                            {
                                "team": {"displayName": "Aces"},
                                "statistics": [
                                    {
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "A'ja Wilson"},
                                                "stats": ["35:30", "8-15", "1-3", "6-8", "3", "8", "11", "4", "2", "3", "2", "1", "23"]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ],
                        "teams": [
                            {
                                "team": {"displayName": "Aces"},
                                "statistics": [
                                    {
                                        "stats": ["200:00", "32-70", "8-22", "12-16", "8", "28", "36", "20", "6", "4", "12", "15", "84"]
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
        assert player['name'] == "A'ja Wilson"
        assert player['team'] == 'Aces'
        assert player['minutes'] == '35:30'
        assert player['fg'] == '8-15'
        assert player['3p'] == '1-3'
        assert player['ft'] == '6-8'
        assert player['reb'] == '11'
        assert player['ast'] == '4'
        assert player['pts'] == '23'
        
        # Check team stats
        team = result['team_stats'][0]
        assert team['team'] == 'Aces'
        assert team['fg'] == '32-70'
        assert team['pts'] == '84'

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
                    "team": {"displayName": "Storm"},
                    "statistics": [
                        {
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Breanna Stewart"},
                                    "stats": ["38:15", "10-18", "3-8", "4-4", "2", "7", "9", "6", "1", "2", "3", "2", "27"]
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
        assert player['name'] == 'Breanna Stewart'
        assert player['team'] == 'Storm'
        assert player['minutes'] == '38:15'
        assert player['fg'] == '10-18'
        assert player['3p'] == '3-8'
        assert player['ft'] == '4-4'
        assert player['reb'] == '9'
        assert player['ast'] == '6'
        assert player['pts'] == '27'

    def test_extract_player_stats_insufficient_data(self):
        """Test player stats extraction with insufficient stat data."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Mercury"},
                    "statistics": [
                        {
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Diana Taurasi"},
                                    "stats": ["25:00", "6-12"]  # Only 2 stats, need at least 13
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
                    "team": {"displayName": "Liberty"},
                    "statistics": [
                        {
                            "stats": ["200:00", "28-65", "6-18", "14-18", "10", "25", "35", "18", "5", "3", "10", "12", "76"]
                        }
                    ]
                }
            ]
        }
        
        result = extract_team_stats(boxscore)
        assert len(result) == 1
        
        team = result[0]
        assert team['team'] == 'Liberty'
        assert team['fg'] == '28-65'
        assert team['3p'] == '6-18'
        assert team['ft'] == '14-18'
        assert team['reb'] == '35'
        assert team['ast'] == '18'
        assert team['pts'] == '76'

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
                    "team": {"displayName": "Sky"},
                    "statistics": [
                        {
                            "athletes": [
                                {
                                    # Missing athlete data
                                    "stats": ["30:45", "7-14", "2-5", "3-4", "1", "6", "7", "5", "2", "1", "2", "2", "19"]
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
        assert player['team'] == 'Sky'

    def test_multiple_teams_and_players(self):
        """Test normalization with multiple teams and players."""
        sample_data = {
            "ok": True,
            "data": {
                "summary": {
                    "boxscore": {
                        "players": [
                            {
                                "team": {"displayName": "Aces"},
                                "statistics": [
                                    {
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "A'ja Wilson"},
                                                "stats": ["35:30", "8-15", "1-3", "6-8", "3", "8", "11", "4", "2", "3", "2", "1", "23"]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "team": {"displayName": "Storm"},
                                "statistics": [
                                    {
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "Breanna Stewart"},
                                                "stats": ["38:15", "10-18", "3-8", "4-4", "2", "7", "9", "6", "1", "2", "3", "2", "27"]
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
        assert 'Aces' in teams
        assert 'Storm' in teams


if __name__ == '__main__':
    pytest.main([__file__])