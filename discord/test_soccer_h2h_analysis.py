"""
Unit tests for Soccer H2H Analysis System
Tests the comprehensive head-to-head analysis functionality
"""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from datetime import datetime
import sys
import os

# Add the parent directory to the path to import soccer_integration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from soccer_integration import (
    SoccerMCPClient, SoccerDataProcessor, H2HInsights, Team, League,
    MCPConnectionError, MCPDataError, MCPTimeoutError
)


class TestSoccerH2HAnalysis(unittest.TestCase):
    """Test cases for H2H analysis functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mcp_client = SoccerMCPClient()
        self.data_processor = SoccerDataProcessor()
        
        # Sample H2H data for testing
        self.sample_h2h_data = {
            'total_meetings': 10,
            'team1_wins': 4,
            'team2_wins': 3,
            'draws': 3,
            'match_history': [
                {'team1_score': 2, 'team2_score': 1, 'date': '2024-01-15'},
                {'team1_score': 0, 'team2_score': 0, 'date': '2023-12-10'},
                {'team1_score': 1, 'team2_score': 2, 'date': '2023-11-05'},
                {'team1_score': 3, 'team2_score': 1, 'date': '2023-09-20'},
                {'team1_score': 1, 'team2_score': 1, 'date': '2023-08-15'}
            ],
            'recent_form': {
                'team1': [
                    {'result': 'W', 'opponent': 'Team A', 'score': '2-1', 'date': '2024-02-01'},
                    {'result': 'L', 'opponent': 'Team B', 'score': '0-1', 'date': '2024-01-25'},
                    {'result': 'W', 'opponent': 'Team C', 'score': '3-0', 'date': '2024-01-20'},
                    {'result': 'D', 'opponent': 'Team D', 'score': '1-1', 'date': '2024-01-15'},
                    {'result': 'W', 'opponent': 'Team E', 'score': '2-0', 'date': '2024-01-10'}
                ],
                'team2': [
                    {'result': 'L', 'opponent': 'Team F', 'score': '1-2', 'date': '2024-02-01'},
                    {'result': 'W', 'opponent': 'Team G', 'score': '2-0', 'date': '2024-01-25'},
                    {'result': 'D', 'opponent': 'Team H', 'score': '0-0', 'date': '2024-01-20'},
                    {'result': 'L', 'opponent': 'Team I', 'score': '0-3', 'date': '2024-01-15'},
                    {'result': 'W', 'opponent': 'Team J', 'score': '1-0', 'date': '2024-01-10'}
                ]
            },
            'advanced_metrics': {
                'team1': {
                    'total_cards': 25,
                    'matches_played': 10,
                    'clean_sheets': 4,
                    'total_goals': 18,
                    'goals_conceded': 12,
                    'btts_matches': 6,
                    'goal_timing': {'first_half': 8, 'second_half': 10}
                },
                'team2': {
                    'total_cards': 30,
                    'matches_played': 10,
                    'clean_sheets': 2,
                    'total_goals': 15,
                    'goals_conceded': 16,
                    'btts_matches': 7,
                    'goal_timing': {'first_half': 6, 'second_half': 9}
                }
            }
        }
    
    def test_get_h2h_analysis_success(self):
        """Test successful H2H analysis retrieval (sync test)"""
        # This will be tested in the async test class
        pass
    
    def test_get_h2h_analysis_connection_error(self):
        """Test H2H analysis with connection error (sync test)"""
        # This will be tested in the async test class
        pass
    
    def test_calculate_h2h_insights_success(self):
        """Test successful H2H insights calculation"""
        insights = self.data_processor.calculate_h2h_insights(
            self.sample_h2h_data, "Liverpool", "Arsenal"
        )
        
        # Basic assertions
        self.assertIsInstance(insights, H2HInsights)
        self.assertEqual(insights.total_meetings, 10)
        self.assertEqual(insights.home_team_wins, 4)
        self.assertEqual(insights.away_team_wins, 3)
        self.assertEqual(insights.draws, 3)
        
        # Percentage calculations
        self.assertEqual(insights.home_win_percentage, 40.0)
        self.assertEqual(insights.away_win_percentage, 30.0)
        self.assertEqual(insights.draw_percentage, 30.0)
        
        # Average goals calculation
        self.assertGreater(insights.avg_goals_per_game, 0)
        
        # Recent form processing
        self.assertIn('team1', insights.recent_form)
        self.assertIn('team2', insights.recent_form)
        
        # Betting recommendations
        self.assertIsInstance(insights.betting_recommendations, list)
        self.assertGreater(len(insights.betting_recommendations), 0)
    
    def test_calculate_h2h_insights_empty_data(self):
        """Test H2H insights calculation with empty data"""
        empty_data = {
            'total_meetings': 0,
            'team1_wins': 0,
            'team2_wins': 0,
            'draws': 0
        }
        
        insights = self.data_processor.calculate_h2h_insights(
            empty_data, "Team A", "Team B"
        )
        
        # Should handle empty data gracefully
        self.assertIsInstance(insights, H2HInsights)
        self.assertEqual(insights.total_meetings, 0)
        self.assertEqual(insights.avg_goals_per_game, 0.0)
        self.assertIsInstance(insights.betting_recommendations, list)
    
    def test_process_recent_form(self):
        """Test recent form processing"""
        recent_form = self.data_processor._process_recent_form(
            self.sample_h2h_data['recent_form']
        )
        
        # Check structure
        self.assertIn('team1', recent_form)
        self.assertIn('team2', recent_form)
        
        # Check team1 form processing
        team1_form = recent_form['team1']
        self.assertIsInstance(team1_form, list)
        self.assertGreater(len(team1_form), 0)
        
        # Check that form entries contain expected information
        first_entry = team1_form[0]
        self.assertIn('W', first_entry)  # Result
        self.assertIn('Team A', first_entry)  # Opponent
        self.assertIn('2-1', first_entry)  # Score
    
    def test_calculate_advanced_statistics(self):
        """Test advanced statistics calculation"""
        stats = self.data_processor._calculate_advanced_statistics(
            self.sample_h2h_data['advanced_metrics']
        )
        
        # Check structure
        self.assertIn('team1', stats)
        self.assertIn('team2', stats)
        
        # Check team1 statistics
        team1_stats = stats['team1']
        self.assertIn('cards_per_game', team1_stats)
        self.assertIn('clean_sheet_percentage', team1_stats)
        self.assertIn('goals_per_game', team1_stats)
        self.assertIn('goals_conceded_per_game', team1_stats)
        
        # Verify calculations
        self.assertEqual(team1_stats['cards_per_game'], 2.5)  # 25 cards / 10 matches
        self.assertEqual(team1_stats['clean_sheet_percentage'], 40.0)  # 4/10 * 100
        self.assertEqual(team1_stats['goals_per_game'], 1.8)  # 18 goals / 10 matches
    
    def test_generate_betting_recommendations(self):
        """Test betting recommendations generation"""
        insights = H2HInsights(
            total_meetings=10,
            home_team_wins=6,  # 60% win rate
            away_team_wins=2,
            draws=2,
            avg_goals_per_game=3.2,  # High scoring
            recent_form={'team1': ['W', 'W', 'W', 'W', 'L'], 'team2': ['L', 'L', 'L', 'W', 'D']},
            key_statistics={'team1': {'clean_sheet_percentage': 50}, 'team2': {'cards_per_game': 4.0}}
        )
        
        recommendations = self.data_processor.generate_betting_recommendations(
            insights, self.sample_h2h_data
        )
        
        # Check recommendations structure
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        self.assertLessEqual(len(recommendations), 8)  # Should be limited to 8
        
        # Check for expected recommendation types
        recommendations_text = ' '.join(recommendations)
        self.assertIn('Home team', recommendations_text)  # Should mention home team dominance
        self.assertIn('High-scoring', recommendations_text)  # Should mention high scoring
    
    def test_calculate_btts_percentage(self):
        """Test Both Teams to Score percentage calculation"""
        btts_percentage = self.data_processor._calculate_btts_percentage(self.sample_h2h_data)
        
        # From sample data: 4 out of 5 matches had both teams scoring
        # Matches: 2-1 (yes), 0-0 (no), 1-2 (yes), 3-1 (yes), 1-1 (yes)
        expected_percentage = 80.0  # 4/5 * 100
        self.assertEqual(btts_percentage, expected_percentage)
    
    def test_generate_advanced_recommendations(self):
        """Test advanced recommendations generation"""
        key_statistics = {
            'team1': {
                'cards_per_game': 3.5,  # High cards
                'clean_sheet_percentage': 45.0  # Good defense
            },
            'team2': {
                'cards_per_game': 1.5,  # Low cards
                'clean_sheet_percentage': 10.0  # Poor defense
            }
        }
        
        recommendations = self.data_processor._generate_advanced_recommendations(key_statistics)
        
        # Check for expected recommendations
        recommendations_text = ' '.join(recommendations)
        self.assertIn('cards/game', recommendations_text)  # Should mention high cards
        self.assertIn('strong defensively', recommendations_text)  # Should mention good defense
        self.assertIn('vulnerable defensively', recommendations_text)  # Should mention poor defense
    
    def test_analyze_recent_form_trends(self):
        """Test recent form trend analysis"""
        recent_form = {
            'team1': ['W (2-1) vs Team A', 'W (3-0) vs Team B', 'W (1-0) vs Team C', 'W (2-1) vs Team D', 'L (0-1) vs Team E'],
            'team2': ['L (1-2) vs Team F', 'L (0-1) vs Team G', 'L (0-2) vs Team H', 'L (1-3) vs Team I', 'D (1-1) vs Team J']
        }
        
        recommendations = self.data_processor._analyze_recent_form_trends(recent_form)
        
        # Check for form-based recommendations
        recommendations_text = ' '.join(recommendations)
        self.assertIn('excellent form', recommendations_text)  # Team1 has 4 wins
        self.assertIn('struggling', recommendations_text)  # Team2 has 4 losses
    
    def test_error_handling_in_insights_calculation(self):
        """Test error handling in insights calculation"""
        # Test with malformed data
        malformed_data = {
            'total_meetings': 'invalid',  # Should be int
            'team1_wins': None,
            'match_history': 'not_a_list'
        }
        
        insights = self.data_processor.calculate_h2h_insights(
            malformed_data, "Team A", "Team B"
        )
        
        # Should return minimal insights object
        self.assertIsInstance(insights, H2HInsights)
        self.assertEqual(insights.total_meetings, 0)
        self.assertIn('error', insights.key_statistics)


class TestAsyncH2HMethods(unittest.IsolatedAsyncioTestCase):
    """Test async methods for H2H analysis"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mcp_client = SoccerMCPClient()
        
        # Sample H2H data for testing
        self.sample_h2h_data = {
            'total_meetings': 10,
            'team1_wins': 4,
            'team2_wins': 3,
            'draws': 3,
            'match_history': [
                {'team1_score': 2, 'team2_score': 1, 'date': '2024-01-15'},
                {'team1_score': 0, 'team2_score': 0, 'date': '2023-12-10'},
            ],
            'recent_form': {'team1': [], 'team2': []},
            'advanced_metrics': {'team1': {}, 'team2': {}}
        }
    
    @patch('httpx.AsyncClient')
    async def test_get_h2h_analysis_success(self, mock_client):
        """Test successful H2H analysis retrieval"""
        # Mock successful MCP response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'result': self.sample_h2h_data
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Test the method
        result = await self.mcp_client.get_h2h_analysis(123, 456)
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertEqual(result['total_meetings'], 10)
        self.assertEqual(result['team1_wins'], 4)
        self.assertEqual(result['team2_wins'], 3)
        self.assertEqual(result['draws'], 3)
        self.assertIn('recent_form', result)
        self.assertIn('advanced_metrics', result)
    
    @patch('httpx.AsyncClient')
    async def test_h2h_analysis_with_timeout(self, mock_client):
        """Test H2H analysis with timeout error"""
        import httpx
        
        # Mock timeout error
        mock_client_instance = AsyncMock()
        mock_client_instance.post.side_effect = httpx.TimeoutException("Request timeout")
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Should return graceful degradation instead of raising
        result = await self.mcp_client.get_h2h_analysis(123, 456)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['total_meetings'], 0)
        self.assertIn('error', result)
    
    @patch('httpx.AsyncClient')
    async def test_h2h_analysis_with_invalid_response(self, mock_client):
        """Test H2H analysis with invalid MCP response"""
        # Mock invalid response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'error': {'message': 'Invalid team IDs'}
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Should return graceful degradation
        result = await self.mcp_client.get_h2h_analysis(123, 456)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['total_meetings'], 0)
        self.assertIn('error', result)
    
    @patch('httpx.AsyncClient')
    async def test_get_h2h_analysis_connection_error(self, mock_client):
        """Test H2H analysis with connection error"""
        # Mock connection error
        mock_client_instance = AsyncMock()
        mock_client_instance.post.side_effect = Exception("Connection failed")
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Test error handling - should return graceful degradation
        result = await self.mcp_client.get_h2h_analysis(123, 456)
        
        # Should return minimal structure for graceful degradation
        self.assertIsInstance(result, dict)
        self.assertEqual(result['total_meetings'], 0)
        self.assertIn('error', result)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)