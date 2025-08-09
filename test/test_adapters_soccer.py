"""
Unit tests for Soccer adapter with frozen JSON samples.
Tests normalization functions with various data scenarios and missing data.
"""

import pytest
import json
from adapters.soccer import normalize, extract_player_stats, extract_goalkeeper_stats


class TestSoccerAdapter:
    """Test cases for Soccer adapter normalization functions."""
    
    def test_normalize_valid_data(self):
        """Test normalize function with valid MCP response data."""
        sample_data = {
            "ok": True,
            "data": {
                "summary": {
                    "boxscore": {
                        "players": [
                            {
                                "team": {"displayName": "Manchester City"},
                                "statistics": [
                                    {
                                        "name": "players",
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "Erling Haaland"},
                                                "stats": ["90", "2", "1", "4", "6", "0", "0", "1", "2", "0"]
                                            }
                                        ]
                                    },
                                    {
                                        "name": "goalkeepers",
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "Ederson"},
                                                "stats": ["90", "3", "1", "0", "0", "0"]
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
        
        assert 'players' in result
        assert 'goalkeepers' in result
        assert len(result['players']) == 1
        assert len(result['goalkeepers']) == 1
        
        # Check player stats
        player = result['players'][0]
        assert player['name'] == 'Erling Haaland'
        assert player['team'] == 'Manchester City'
        assert player['minutes'] == '90'
        assert player['goals'] == '2'
        assert player['assists'] == '1'
        assert player['shots_on_goal'] == '4'
        assert player['shots'] == '6'
        
        # Check goalkeeper stats
        goalkeeper = result['goalkeepers'][0]
        assert goalkeeper['name'] == 'Ederson'
        assert goalkeeper['team'] == 'Manchester City'
        assert goalkeeper['minutes'] == '90'
        assert goalkeeper['saves'] == '3'
        assert goalkeeper['goals_against'] == '1'

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
                    "team": {"displayName": "Liverpool"},
                    "statistics": [
                        {
                            "name": "players",
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Mohamed Salah"},
                                    "stats": ["85", "1", "2", "3", "5", "1", "0", "2", "1", "1"]
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
        assert player['name'] == 'Mohamed Salah'
        assert player['team'] == 'Liverpool'
        assert player['minutes'] == '85'
        assert player['goals'] == '1'
        assert player['assists'] == '2'
        assert player['shots_on_goal'] == '3'
        assert player['shots'] == '5'
        assert player['yellow_cards'] == '1'
        assert player['red_cards'] == '0'

    def test_extract_goalkeeper_stats_complete_data(self):
        """Test goalkeeper stats extraction with complete data."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Real Madrid"},
                    "statistics": [
                        {
                            "name": "goalkeepers",
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Thibaut Courtois"},
                                    "stats": ["90", "5", "0", "0", "0", "1"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_goalkeeper_stats(boxscore)
        assert len(result) == 1
        
        player = result[0]
        assert player['name'] == 'Thibaut Courtois'
        assert player['team'] == 'Real Madrid'
        assert player['minutes'] == '90'
        assert player['saves'] == '5'
        assert player['goals_against'] == '0'
        assert player['yellow_cards'] == '0'
        assert player['red_cards'] == '0'
        assert player['clean_sheet'] == '1'

    def test_extract_player_stats_insufficient_data(self):
        """Test player stats extraction with insufficient stat data."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Barcelona"},
                    "statistics": [
                        {
                            "name": "players",
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Lionel Messi"},
                                    "stats": ["75"]  # Only 1 stat, need at least 3
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_player_stats(boxscore)
        assert len(result) == 0  # Should not include players with insufficient data

    def test_extract_goalkeeper_stats_insufficient_data(self):
        """Test goalkeeper stats extraction with insufficient stat data."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Chelsea"},
                    "statistics": [
                        {
                            "name": "goalkeepers",
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Kepa Arrizabalaga"},
                                    "stats": ["90", "2"]  # Only 2 stats, need at least 3
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_goalkeeper_stats(boxscore)
        assert len(result) == 0  # Should not include players with insufficient data

    def test_extract_stats_missing_categories(self):
        """Test stat extraction when specific categories are missing."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Arsenal"},
                    "statistics": [
                        {
                            "name": "officials",  # Different category
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Referee"},
                                    "stats": ["90", "0", "5"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        player_result = extract_player_stats(boxscore)
        goalkeeper_result = extract_goalkeeper_stats(boxscore)
        
        assert len(player_result) == 0
        assert len(goalkeeper_result) == 0

    def test_extract_stats_empty_boxscore(self):
        """Test stat extraction with empty boxscore."""
        empty_boxscore = {"players": []}
        
        player_result = extract_player_stats(empty_boxscore)
        goalkeeper_result = extract_goalkeeper_stats(empty_boxscore)
        
        assert len(player_result) == 0
        assert len(goalkeeper_result) == 0

    def test_extract_stats_missing_athlete_data(self):
        """Test stat extraction when athlete data is missing."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Tottenham"},
                    "statistics": [
                        {
                            "name": "players",
                            "athletes": [
                                {
                                    # Missing athlete data
                                    "stats": ["80", "0", "1", "2", "3", "0", "0", "1", "0", "0"]
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
        assert player['team'] == 'Tottenham'

    def test_multiple_teams_and_players(self):
        """Test normalization with multiple teams and players."""
        sample_data = {
            "ok": True,
            "data": {
                "summary": {
                    "boxscore": {
                        "players": [
                            {
                                "team": {"displayName": "Manchester City"},
                                "statistics": [
                                    {
                                        "name": "players",
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "Erling Haaland"},
                                                "stats": ["90", "2", "1", "4", "6", "0", "0", "1", "2", "0"]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "team": {"displayName": "Liverpool"},
                                "statistics": [
                                    {
                                        "name": "players",
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "Mohamed Salah"},
                                                "stats": ["85", "1", "2", "3", "5", "1", "0", "2", "1", "1"]
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
        assert 'Manchester City' in teams
        assert 'Liverpool' in teams

    def test_alternative_category_names(self):
        """Test extraction with alternative category names."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "PSG"},
                    "statistics": [
                        {
                            "name": "outfield",  # Alternative name for players
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Kylian Mbappe"},
                                    "stats": ["88", "1", "0", "2", "4", "0", "0", "0", "1", "0"]
                                }
                            ]
                        },
                        {
                            "name": "keepers",  # Alternative name for goalkeepers
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Gianluigi Donnarumma"},
                                    "stats": ["90", "4", "1", "0", "0", "0"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        player_result = extract_player_stats(boxscore)
        goalkeeper_result = extract_goalkeeper_stats(boxscore)
        
        assert len(player_result) == 1
        assert len(goalkeeper_result) == 1
        
        assert player_result[0]['name'] == 'Kylian Mbappe'
        assert goalkeeper_result[0]['name'] == 'Gianluigi Donnarumma'


if __name__ == '__main__':
    pytest.main([__file__])