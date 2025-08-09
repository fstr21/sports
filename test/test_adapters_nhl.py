"""
Unit tests for NHL adapter with frozen JSON samples.
Tests normalization functions with various data scenarios and missing data.
"""

import pytest
import json
from adapters.nhl import normalize, extract_skater_stats, extract_goalie_stats


class TestNHLAdapter:
    """Test cases for NHL adapter normalization functions."""
    
    def test_normalize_valid_data(self):
        """Test normalize function with valid MCP response data."""
        sample_data = {
            "ok": True,
            "data": {
                "summary": {
                    "boxscore": {
                        "players": [
                            {
                                "team": {"displayName": "Rangers"},
                                "statistics": [
                                    {
                                        "name": "skaters",
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "Artemi Panarin"},
                                                "stats": ["2", "1", "3", "+2", "0", "4", "18:45", "3", "1"]
                                            }
                                        ]
                                    },
                                    {
                                        "name": "goalies",
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "Igor Shesterkin"},
                                                "stats": ["28", "2", "26", ".929", "60:00", "W"]
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
        
        assert 'skaters' in result
        assert 'goalies' in result
        assert len(result['skaters']) == 1
        assert len(result['goalies']) == 1
        
        # Check skater stats
        skater = result['skaters'][0]
        assert skater['name'] == 'Artemi Panarin'
        assert skater['team'] == 'Rangers'
        assert skater['goals'] == '2'
        assert skater['assists'] == '1'
        assert skater['points'] == '3'
        assert skater['plus_minus'] == '+2'
        assert skater['shots_on_goal'] == '4'
        
        # Check goalie stats
        goalie = result['goalies'][0]
        assert goalie['name'] == 'Igor Shesterkin'
        assert goalie['team'] == 'Rangers'
        assert goalie['shots_against'] == '28'
        assert goalie['goals_against'] == '2'
        assert goalie['saves'] == '26'
        assert goalie['save_percentage'] == '.929'

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

    def test_extract_skater_stats_complete_data(self):
        """Test skater stats extraction with complete data."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Bruins"},
                    "statistics": [
                        {
                            "name": "skaters",
                            "athletes": [
                                {
                                    "athlete": {"displayName": "David Pastrnak"},
                                    "stats": ["1", "2", "3", "+1", "2", "6", "20:15", "4", "2"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_skater_stats(boxscore)
        assert len(result) == 1
        
        player = result[0]
        assert player['name'] == 'David Pastrnak'
        assert player['team'] == 'Bruins'
        assert player['goals'] == '1'
        assert player['assists'] == '2'
        assert player['points'] == '3'
        assert player['plus_minus'] == '+1'
        assert player['penalty_minutes'] == '2'
        assert player['shots_on_goal'] == '6'
        assert player['time_on_ice'] == '20:15'

    def test_extract_goalie_stats_complete_data(self):
        """Test goalie stats extraction with complete data."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Lightning"},
                    "statistics": [
                        {
                            "name": "goalies",
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Andrei Vasilevskiy"},
                                    "stats": ["32", "1", "31", ".969", "60:00", "W"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_goalie_stats(boxscore)
        assert len(result) == 1
        
        player = result[0]
        assert player['name'] == 'Andrei Vasilevskiy'
        assert player['team'] == 'Lightning'
        assert player['shots_against'] == '32'
        assert player['goals_against'] == '1'
        assert player['saves'] == '31'
        assert player['save_percentage'] == '.969'
        assert player['time_on_ice'] == '60:00'
        assert player['decision'] == 'W'

    def test_extract_skater_stats_insufficient_data(self):
        """Test skater stats extraction with insufficient stat data."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Capitals"},
                    "statistics": [
                        {
                            "name": "skaters",
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Alex Ovechkin"},
                                    "stats": ["1", "0"]  # Only 2 stats, need at least 6
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_skater_stats(boxscore)
        assert len(result) == 0  # Should not include players with insufficient data

    def test_extract_goalie_stats_insufficient_data(self):
        """Test goalie stats extraction with insufficient stat data."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Penguins"},
                    "statistics": [
                        {
                            "name": "goalies",
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Tristan Jarry"},
                                    "stats": ["20", "3"]  # Only 2 stats, need at least 4
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_goalie_stats(boxscore)
        assert len(result) == 0  # Should not include players with insufficient data

    def test_extract_stats_missing_categories(self):
        """Test stat extraction when specific categories are missing."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Devils"},
                    "statistics": [
                        {
                            "name": "officials",  # Different category
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Referee"},
                                    "stats": ["1", "2", "3"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        skater_result = extract_skater_stats(boxscore)
        goalie_result = extract_goalie_stats(boxscore)
        
        assert len(skater_result) == 0
        assert len(goalie_result) == 0

    def test_extract_stats_empty_boxscore(self):
        """Test stat extraction with empty boxscore."""
        empty_boxscore = {"players": []}
        
        skater_result = extract_skater_stats(empty_boxscore)
        goalie_result = extract_goalie_stats(empty_boxscore)
        
        assert len(skater_result) == 0
        assert len(goalie_result) == 0

    def test_extract_stats_missing_athlete_data(self):
        """Test stat extraction when athlete data is missing."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Flyers"},
                    "statistics": [
                        {
                            "name": "skaters",
                            "athletes": [
                                {
                                    # Missing athlete data
                                    "stats": ["0", "1", "1", "0", "0", "2", "15:30", "1", "0"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_skater_stats(boxscore)
        assert len(result) == 1
        
        player = result[0]
        assert player['name'] == 'Unknown'  # Should default to 'Unknown'
        assert player['team'] == 'Flyers'

    def test_multiple_teams_and_players(self):
        """Test normalization with multiple teams and players."""
        sample_data = {
            "ok": True,
            "data": {
                "summary": {
                    "boxscore": {
                        "players": [
                            {
                                "team": {"displayName": "Rangers"},
                                "statistics": [
                                    {
                                        "name": "skaters",
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "Artemi Panarin"},
                                                "stats": ["2", "1", "3", "+2", "0", "4", "18:45", "3", "1"]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "team": {"displayName": "Bruins"},
                                "statistics": [
                                    {
                                        "name": "skaters",
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "David Pastrnak"},
                                                "stats": ["1", "2", "3", "+1", "2", "6", "20:15", "4", "2"]
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
        assert len(result['skaters']) == 2
        
        # Check both teams are represented
        teams = [player['team'] for player in result['skaters']]
        assert 'Rangers' in teams
        assert 'Bruins' in teams


if __name__ == '__main__':
    pytest.main([__file__])