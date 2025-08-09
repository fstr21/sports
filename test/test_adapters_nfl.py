"""
Unit tests for NFL adapter with frozen JSON samples.
Tests normalization functions with various data scenarios and missing data.
"""

import pytest
import json
from adapters.nfl import normalize, extract_passing_stats, extract_rushing_stats, extract_receiving_stats


class TestNFLAdapter:
    """Test cases for NFL adapter normalization functions."""
    
    def test_normalize_valid_data(self):
        """Test normalize function with valid MCP response data."""
        sample_data = {
            "ok": True,
            "data": {
                "summary": {
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
                                    },
                                    {
                                        "name": "receiving",
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "Mark Andrews"},
                                                "stats": ["6", "85", "14.2", "1", "28", "8"]
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
        
        assert 'passing' in result
        assert 'rushing' in result
        assert 'receiving' in result
        assert len(result['passing']) == 1
        assert len(result['rushing']) == 1
        assert len(result['receiving']) == 1
        
        # Check passing stats
        passing_player = result['passing'][0]
        assert passing_player['name'] == 'Lamar Jackson'
        assert passing_player['team'] == 'Ravens'
        assert passing_player['completions_attempts'] == '15/25'
        assert passing_player['yards'] == '250'
        assert passing_player['touchdowns'] == '2'
        assert passing_player['interceptions'] == '0'
        
        # Check rushing stats
        rushing_player = result['rushing'][0]
        assert rushing_player['name'] == 'Derrick Henry'
        assert rushing_player['carries'] == '20'
        assert rushing_player['yards'] == '120'
        assert rushing_player['touchdowns'] == '1'
        
        # Check receiving stats
        receiving_player = result['receiving'][0]
        assert receiving_player['name'] == 'Mark Andrews'
        assert receiving_player['receptions'] == '6'
        assert receiving_player['yards'] == '85'
        assert receiving_player['touchdowns'] == '1'

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

    def test_extract_passing_stats_complete_data(self):
        """Test passing stats extraction with complete data."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Chiefs"},
                    "statistics": [
                        {
                            "name": "passing",
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Patrick Mahomes"},
                                    "stats": ["22", "30", "320", "10.7", "3", "1", "112.4"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_passing_stats(boxscore)
        assert len(result) == 1
        
        player = result[0]
        assert player['name'] == 'Patrick Mahomes'
        assert player['team'] == 'Chiefs'
        assert player['completions_attempts'] == '22/30'
        assert player['yards'] == '320'
        assert player['touchdowns'] == '3'
        assert player['interceptions'] == '1'
        assert player['rating'] == '112.4'

    def test_extract_passing_stats_insufficient_data(self):
        """Test passing stats extraction with insufficient stat data."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Bills"},
                    "statistics": [
                        {
                            "name": "passing",
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Josh Allen"},
                                    "stats": ["18", "25"]  # Only 2 stats, need at least 5
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_passing_stats(boxscore)
        assert len(result) == 0  # Should not include players with insufficient data

    def test_extract_rushing_stats_complete_data(self):
        """Test rushing stats extraction with complete data."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Cowboys"},
                    "statistics": [
                        {
                            "name": "rushing",
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Ezekiel Elliott"},
                                    "stats": ["18", "95", "5.3", "2", "22"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_rushing_stats(boxscore)
        assert len(result) == 1
        
        player = result[0]
        assert player['name'] == 'Ezekiel Elliott'
        assert player['team'] == 'Cowboys'
        assert player['carries'] == '18'
        assert player['yards'] == '95'
        assert player['average'] == '5.3'
        assert player['touchdowns'] == '2'
        assert player['long'] == '22'

    def test_extract_receiving_stats_complete_data(self):
        """Test receiving stats extraction with complete data."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Packers"},
                    "statistics": [
                        {
                            "name": "receiving",
                            "athletes": [
                                {
                                    "athlete": {"displayName": "Davante Adams"},
                                    "stats": ["8", "110", "13.8", "2", "35", "12"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_receiving_stats(boxscore)
        assert len(result) == 1
        
        player = result[0]
        assert player['name'] == 'Davante Adams'
        assert player['team'] == 'Packers'
        assert player['receptions'] == '8'
        assert player['yards'] == '110'
        assert player['touchdowns'] == '2'
        assert player['targets'] == '12'

    def test_extract_stats_missing_categories(self):
        """Test stat extraction when specific categories are missing."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Steelers"},
                    "statistics": [
                        {
                            "name": "defense",  # Different category, not passing/rushing/receiving
                            "athletes": [
                                {
                                    "athlete": {"displayName": "T.J. Watt"},
                                    "stats": ["5", "2", "1"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        passing_result = extract_passing_stats(boxscore)
        rushing_result = extract_rushing_stats(boxscore)
        receiving_result = extract_receiving_stats(boxscore)
        
        assert len(passing_result) == 0
        assert len(rushing_result) == 0
        assert len(receiving_result) == 0

    def test_extract_stats_empty_boxscore(self):
        """Test stat extraction with empty boxscore."""
        empty_boxscore = {"players": []}
        
        passing_result = extract_passing_stats(empty_boxscore)
        rushing_result = extract_rushing_stats(empty_boxscore)
        receiving_result = extract_receiving_stats(empty_boxscore)
        
        assert len(passing_result) == 0
        assert len(rushing_result) == 0
        assert len(receiving_result) == 0

    def test_extract_stats_missing_athlete_data(self):
        """Test stat extraction when athlete data is missing."""
        boxscore = {
            "players": [
                {
                    "team": {"displayName": "Bengals"},
                    "statistics": [
                        {
                            "name": "passing",
                            "athletes": [
                                {
                                    # Missing athlete data
                                    "stats": ["20", "28", "275", "9.8", "2", "0", "105.2"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_passing_stats(boxscore)
        assert len(result) == 1
        
        player = result[0]
        assert player['name'] == 'Unknown'  # Should default to 'Unknown'
        assert player['team'] == 'Bengals'

    def test_multiple_teams_and_players(self):
        """Test normalization with multiple teams and players."""
        sample_data = {
            "ok": True,
            "data": {
                "summary": {
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
                                    }
                                ]
                            },
                            {
                                "team": {"displayName": "Steelers"},
                                "statistics": [
                                    {
                                        "name": "passing",
                                        "athletes": [
                                            {
                                                "athlete": {"displayName": "Kenny Pickett"},
                                                "stats": ["18", "30", "220", "7.3", "1", "2", "72.1"]
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
        assert len(result['passing']) == 2
        
        # Check both teams are represented
        teams = [player['team'] for player in result['passing']]
        assert 'Ravens' in teams
        assert 'Steelers' in teams


if __name__ == '__main__':
    pytest.main([__file__])