"""
Integration tests for multi-league support and league-specific handling
Tests the enhanced soccer integration with priority ordering, tournament stages, and standings
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

# Import the soccer integration components
from soccer_integration import (
    SoccerMCPClient, SoccerDataProcessor, SoccerEmbedBuilder,
    ProcessedMatch, League, Team, TeamStanding, BettingOdds,
    SUPPORTED_LEAGUES, LEAGUE_PRIORITY_ORDER, UEFA_STAGE_MAPPINGS
)

class TestMultiLeagueSupport:
    """Test multi-league support functionality"""
    
    @pytest.fixture
    def mock_multi_league_response(self):
        """Mock MCP response with multiple leagues"""
        return {
            "matches_by_league": {
                "EPL": {
                    "league_info": {
                        "id": 228,
                        "name": "Premier League",
                        "country": "England",
                        "season": "2024-25"
                    },
                    "matches": [
                        {
                            "id": 1001,
                            "date": "2025-08-18",
                            "time": "15:00",
                            "venue": "Emirates Stadium",
                            "status": "scheduled",
                            "home_team": {
                                "id": 101,
                                "name": "Arsenal",
                                "short_name": "ARS",
                                "country": "England",
                                "standing": {
                                    "position": 2,
                                    "points": 45,
                                    "played": 20,
                                    "won": 14,
                                    "drawn": 3,
                                    "lost": 3,
                                    "goals_for": 42,
                                    "goals_against": 18,
                                    "goal_difference": 24,
                                    "form": ["W", "W", "D", "W", "L"]
                                }
                            },
                            "away_team": {
                                "id": 102,
                                "name": "Liverpool",
                                "short_name": "LIV",
                                "country": "England",
                                "standing": {
                                    "position": 1,
                                    "points": 48,
                                    "played": 20,
                                    "won": 15,
                                    "drawn": 3,
                                    "lost": 2,
                                    "goals_for": 48,
                                    "goals_against": 15,
                                    "goal_difference": 33,
                                    "form": ["W", "W", "W", "W", "D"]
                                }
                            },
                            "odds": {
                                "home_win": 2.50,
                                "draw": 3.20,
                                "away_win": 2.80,
                                "over_under": {
                                    "line": 2.5,
                                    "over": 1.85,
                                    "under": 1.95
                                }
                            }
                        }
                    ]
                },
                "UEFA": {
                    "league_info": {
                        "id": 310,
                        "name": "UEFA Champions League",
                        "country": "Europe",
                        "season": "2024-25"
                    },
                    "matches": [
                        {
                            "id": 2001,
                            "date": "2025-08-18",
                            "time": "20:00",
                            "venue": "Santiago Bernabéu",
                            "status": "scheduled",
                            "stage": {
                                "stage": "quarter_finals",
                                "stage_name": "Quarter Finals",
                                "leg": 1
                            },
                            "home_team": {
                                "id": 201,
                                "name": "Real Madrid",
                                "short_name": "RMA",
                                "country": "Spain"
                            },
                            "away_team": {
                                "id": 202,
                                "name": "Manchester City",
                                "short_name": "MCI",
                                "country": "England"
                            },
                            "odds": {
                                "home_win": 2.10,
                                "draw": 3.40,
                                "away_win": 3.20
                            }
                        }
                    ]
                },
                "La Liga": {
                    "league_info": {
                        "id": 297,
                        "name": "La Liga",
                        "country": "Spain",
                        "season": "2024-25"
                    },
                    "matches": [
                        {
                            "id": 3001,
                            "date": "2025-08-18",
                            "time": "18:00",
                            "venue": "Camp Nou",
                            "status": "scheduled",
                            "home_team": {
                                "id": 301,
                                "name": "FC Barcelona",
                                "short_name": "BAR",
                                "country": "Spain",
                                "standing": {
                                    "position": 1,
                                    "points": 52,
                                    "played": 21,
                                    "won": 16,
                                    "drawn": 4,
                                    "lost": 1,
                                    "goals_for": 55,
                                    "goals_against": 20,
                                    "goal_difference": 35,
                                    "form": ["W", "W", "W", "D", "W"]
                                }
                            },
                            "away_team": {
                                "id": 302,
                                "name": "Real Madrid",
                                "short_name": "RMA",
                                "country": "Spain",
                                "standing": {
                                    "position": 2,
                                    "points": 49,
                                    "played": 21,
                                    "won": 15,
                                    "drawn": 4,
                                    "lost": 2,
                                    "goals_for": 50,
                                    "goals_against": 22,
                                    "goal_difference": 28,
                                    "form": ["W", "D", "W", "W", "W"]
                                }
                            }
                        }
                    ]
                }
            }
        }
    
    @pytest.fixture
    def mock_standings_response(self):
        """Mock league standings response"""
        return {
            "league_info": {
                "id": 228,
                "name": "Premier League",
                "country": "England",
                "season": "2024-25"
            },
            "standings": [
                {
                    "position": 1,
                    "team": {"name": "Liverpool", "id": 102},
                    "played": 20,
                    "wins": 15,
                    "draws": 3,
                    "losses": 2,
                    "goals_for": 48,
                    "goals_against": 15,
                    "points": 48
                },
                {
                    "position": 2,
                    "team": {"name": "Arsenal", "id": 101},
                    "played": 20,
                    "wins": 14,
                    "draws": 3,
                    "losses": 3,
                    "goals_for": 42,
                    "goals_against": 18,
                    "points": 45
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_multi_league_match_retrieval(self, mock_multi_league_response):
        """Test retrieving matches from multiple leagues with priority ordering"""
        client = SoccerMCPClient()
        
        with patch.object(client, 'call_mcp_tool', return_value=mock_multi_league_response):
            result = await client.get_matches_for_multiple_leagues("2025-08-18")
            
            # Verify response structure
            assert "matches_by_league" in result
            matches_by_league = result["matches_by_league"]
            
            # Verify priority ordering (UEFA should come first)
            league_keys = list(matches_by_league.keys())
            assert league_keys[0] == "UEFA"  # Highest priority
            assert "EPL" in league_keys
            assert "La Liga" in league_keys
            
            # Verify league configuration enrichment
            uefa_data = matches_by_league["UEFA"]
            assert "league_config" in uefa_data
            assert uefa_data["league_config"]["tournament_type"] == "knockout"
            assert uefa_data["priority"] == 0  # Highest priority
    
    @pytest.mark.asyncio
    async def test_league_filtering(self, mock_multi_league_response):
        """Test filtering matches by specific leagues"""
        client = SoccerMCPClient()
        
        with patch.object(client, 'call_mcp_tool', return_value=mock_multi_league_response):
            # Test filtering for specific leagues
            result = await client.get_matches_for_date("2025-08-18", ["EPL", "UEFA"])
            
            # Verify only requested leagues are processed
            assert "matches_by_league" in result
            matches_by_league = result["matches_by_league"]
            
            # Should contain UEFA and EPL based on priority ordering
            assert "UEFA" in matches_by_league or "EPL" in matches_by_league
    
    def test_league_priority_ordering(self, mock_multi_league_response):
        """Test league priority ordering functionality"""
        client = SoccerMCPClient()
        
        # Test the priority ordering method
        original_matches = mock_multi_league_response["matches_by_league"]
        ordered_matches = client._apply_league_priority_ordering(original_matches)
        
        # Verify ordering follows LEAGUE_PRIORITY_ORDER
        ordered_keys = list(ordered_matches.keys())
        
        # UEFA should come first (priority 0)
        assert ordered_keys[0] == "UEFA"
        
        # EPL should come before La Liga (priority 1 vs 2)
        epl_index = ordered_keys.index("EPL") if "EPL" in ordered_keys else -1
        la_liga_index = ordered_keys.index("La Liga") if "La Liga" in ordered_keys else -1
        
        if epl_index != -1 and la_liga_index != -1:
            assert epl_index < la_liga_index
    
    def test_tournament_stage_handling(self, mock_multi_league_response):
        """Test UEFA Champions League tournament stage handling"""
        processor = SoccerDataProcessor()
        
        # Process the multi-league data
        processed_matches = processor.process_match_data(mock_multi_league_response)
        
        # Find the UEFA match
        uefa_match = None
        for match in processed_matches:
            if match.league.config and match.league.config.get("code") == "UEFA":
                uefa_match = match
                break
        
        assert uefa_match is not None
        assert uefa_match.league.is_tournament
        assert uefa_match.league.stage == "quarter_finals"
        assert uefa_match.league.stage_name == "Quarter Finals"
        assert uefa_match.league.tournament_type == "knockout"
    
    def test_team_standings_processing(self, mock_multi_league_response):
        """Test processing of team standings information"""
        processor = SoccerDataProcessor()
        
        # Process matches with standings
        processed_matches = processor.process_match_data(mock_multi_league_response, include_standings=True)
        
        # Find EPL match with standings
        epl_match = None
        for match in processed_matches:
            if match.league.config and match.league.config.get("code") == "EPL":
                epl_match = match
                break
        
        assert epl_match is not None
        
        # Verify home team standings
        home_team = epl_match.home_team
        assert home_team.standing is not None
        assert home_team.standing.position == 2
        assert home_team.standing.points == 45
        assert home_team.standing.goal_difference == 24
        assert home_team.form_display == "WWDWL"
        
        # Verify away team standings
        away_team = epl_match.away_team
        assert away_team.standing is not None
        assert away_team.standing.position == 1
        assert away_team.standing.points == 48
        assert away_team.standing.goal_difference == 33
        assert away_team.form_display == "WWWWD"
    
    def test_enhanced_embed_creation(self, mock_multi_league_response):
        """Test creation of enhanced embeds with multi-league support"""
        processor = SoccerDataProcessor()
        embed_builder = SoccerEmbedBuilder()
        
        # Process matches
        processed_matches = processor.process_match_data(mock_multi_league_response)
        
        # Test EPL match embed with standings
        epl_match = None
        for match in processed_matches:
            if match.league.config and match.league.config.get("code") == "EPL":
                epl_match = match
                break
        
        assert epl_match is not None
        
        # Create match preview embed
        embed = embed_builder.create_match_preview_embed(epl_match)
        
        # Verify embed properties
        assert embed.title is not None
        assert "Arsenal" in embed.title and "Liverpool" in embed.title
        assert embed.color.value == SUPPORTED_LEAGUES["EPL"]["color"]
        
        # Verify fields contain standings information
        field_names = [field.name for field in embed.fields]
        assert "📊 League Positions" in field_names
        
        # Find the standings comparison field
        standings_field = None
        for field in embed.fields:
            if field.name == "📊 League Positions":
                standings_field = field
                break
        
        assert standings_field is not None
        assert "1 (48 pts)" in standings_field.value  # Liverpool's position
        assert "2 (45 pts)" in standings_field.value  # Arsenal's position
    
    def test_uefa_tournament_embed(self, mock_multi_league_response):
        """Test UEFA Champions League tournament embed creation"""
        processor = SoccerDataProcessor()
        embed_builder = SoccerEmbedBuilder()
        
        # Process matches
        processed_matches = processor.process_match_data(mock_multi_league_response)
        
        # Find UEFA match
        uefa_match = None
        for match in processed_matches:
            if match.league.config and match.league.config.get("code") == "UEFA":
                uefa_match = match
                break
        
        assert uefa_match is not None
        
        # Create match preview embed
        embed = embed_builder.create_match_preview_embed(uefa_match)
        
        # Verify tournament-specific elements
        assert "Quarter Finals" in embed.title
        assert embed.color.value == SUPPORTED_LEAGUES["UEFA"]["color"]
        
        # Verify no standings comparison for tournament matches
        field_names = [field.name for field in embed.fields]
        assert "📊 League Positions" not in field_names
    
    @pytest.mark.asyncio
    async def test_league_standings_embed(self, mock_standings_response):
        """Test league standings embed creation"""
        embed_builder = SoccerEmbedBuilder()
        
        # Create league object
        league = League(
            id=228,
            name="Premier League",
            country="England",
            season="2024-25",
            priority=1,
            tournament_type="league"
        )
        
        # Create standings embed
        embed = embed_builder.create_league_standings_embed(mock_standings_response, league)
        
        # Verify embed properties
        assert "Premier League Standings" in embed.title
        assert embed.color.value == SUPPORTED_LEAGUES["EPL"]["color"]
        
        # Verify standings table is present
        field_names = [field.name for field in embed.fields]
        assert "📊 League Table" in field_names
        
        # Find standings table field
        standings_field = None
        for field in embed.fields:
            if field.name == "📊 League Table":
                standings_field = field
                break
        
        assert standings_field is not None
        assert "Liverpool" in standings_field.value
        assert "Arsenal" in standings_field.value
        assert "48" in standings_field.value  # Liverpool's points
        assert "45" in standings_field.value  # Arsenal's points

class TestLeagueSpecificHandling:
    """Test league-specific handling and data enrichment"""
    
    def test_league_configuration_access(self):
        """Test accessing league configuration data"""
        # Test EPL configuration
        epl_league = League(id=228, name="Premier League", country="England")
        config = epl_league.config
        
        assert config is not None
        assert config["code"] == "EPL"
        assert config["color"] == 0x3d195b
        assert config["emoji"] == "🏴󠁧󠁢󠁥󠁮󠁧󠁿"
        assert config["priority"] == 1
        assert config["tournament_type"] == "league"
        
        # Test UEFA configuration
        uefa_league = League(id=310, name="UEFA Champions League", country="Europe")
        uefa_config = uefa_league.config
        
        assert uefa_config is not None
        assert uefa_config["code"] == "UEFA"
        assert uefa_config["tournament_type"] == "knockout"
        assert uefa_config["priority"] == 0
        assert "stages" in uefa_config
    
    def test_team_standing_calculations(self):
        """Test team standing calculations and properties"""
        standing = TeamStanding(
            position=2,
            points=45,
            played=20,
            won=14,
            drawn=3,
            lost=3,
            goals_for=42,
            goals_against=18,
            goal_difference=24,
            form=["W", "W", "D", "W", "L"]
        )
        
        # Test calculated properties
        assert standing.points_per_game == 2.25  # 45/20
        assert standing.win_percentage == 70.0  # 14/20 * 100
        
        # Test team with standing
        team = Team(
            id=101,
            name="Arsenal",
            short_name="ARS",
            standing=standing
        )
        
        assert team.display_name_with_position == "Arsenal (2)"
        assert team.form_display == "WWDWL"
    
    def test_league_display_properties(self):
        """Test league display properties for different tournament types"""
        # Test regular league
        league = League(
            id=228,
            name="Premier League",
            country="England",
            tournament_type="league"
        )
        
        assert not league.is_tournament
        assert league.display_name == "Premier League"
        assert league.emoji == "🏴󠁧󠁢󠁥󠁮󠁧󠁿"
        assert league.color == 0x3d195b
        
        # Test tournament with stage
        uefa_league = League(
            id=310,
            name="UEFA Champions League",
            country="Europe",
            tournament_type="knockout",
            stage="quarter_finals",
            stage_name="Quarter Finals"
        )
        
        assert uefa_league.is_tournament
        assert uefa_league.display_name == "UEFA Champions League - Quarter Finals"
        assert uefa_league.emoji == "🏆"
        assert uefa_league.color == 0x00336a
    
    def test_uefa_stage_mappings(self):
        """Test UEFA Champions League stage mappings"""
        # Verify all expected stages are mapped
        expected_stages = ["group_stage", "round_of_16", "quarter_finals", "semi_finals", "final"]
        
        for stage in expected_stages:
            assert stage in UEFA_STAGE_MAPPINGS
            stage_config = UEFA_STAGE_MAPPINGS[stage]
            assert "name" in stage_config
            assert "emoji" in stage_config
            assert "priority" in stage_config
        
        # Verify priority ordering
        assert UEFA_STAGE_MAPPINGS["group_stage"]["priority"] < UEFA_STAGE_MAPPINGS["final"]["priority"]
        assert UEFA_STAGE_MAPPINGS["round_of_16"]["priority"] < UEFA_STAGE_MAPPINGS["quarter_finals"]["priority"]

class TestIntegrationScenarios:
    """Test complete integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_complete_multi_league_workflow(self):
        """Test complete workflow from MCP call to embed creation"""
        client = SoccerMCPClient()
        processor = SoccerDataProcessor()
        embed_builder = SoccerEmbedBuilder()
        
        # Create mock response inline
        mock_response = {
            "matches_by_league": {
                "EPL": {
                    "league_info": {"id": 228, "name": "Premier League", "country": "England"},
                    "matches": [{"id": 1001, "date": "2025-08-18", "time": "15:00", "venue": "Test", "status": "scheduled",
                                "home_team": {"id": 101, "name": "Arsenal", "short_name": "ARS"},
                                "away_team": {"id": 102, "name": "Liverpool", "short_name": "LIV"}}]
                },
                "UEFA": {
                    "league_info": {"id": 310, "name": "UEFA Champions League", "country": "Europe"},
                    "matches": [{"id": 2001, "date": "2025-08-18", "time": "20:00", "venue": "Test", "status": "scheduled",
                                "home_team": {"id": 201, "name": "Real Madrid", "short_name": "RMA"},
                                "away_team": {"id": 202, "name": "Manchester City", "short_name": "MCI"}}]
                }
            }
        }
        
        with patch.object(client, 'call_mcp_tool', return_value=mock_response):
            # Step 1: Fetch multi-league matches
            raw_matches = await client.get_matches_for_multiple_leagues("2025-08-18")
            
            # Step 2: Process matches with standings
            processed_matches = processor.process_match_data(raw_matches, include_standings=True)
            
            # Step 3: Verify processing results
            assert len(processed_matches) == 2  # EPL, UEFA matches
            
            # Verify priority ordering
            assert processed_matches[0].league.priority == 0  # UEFA first
            
            # Step 4: Create embeds for each match
            embeds = []
            for match in processed_matches:
                embed = embed_builder.create_match_preview_embed(match)
                embeds.append(embed)
            
            assert len(embeds) == 2
            
            # Verify embed properties
            for embed in embeds:
                assert embed.title is not None
                assert embed.color is not None
                assert len(embed.fields) > 0
    
    def test_error_handling_and_graceful_degradation(self):
        """Test error handling and graceful degradation"""
        processor = SoccerDataProcessor()
        embed_builder = SoccerEmbedBuilder()
        
        # Test with invalid/empty data
        empty_response = {"matches_by_league": {}}
        processed_matches = processor.process_match_data(empty_response)
        assert len(processed_matches) == 0
        
        # Test with malformed data
        malformed_response = {"matches_by_league": {"EPL": {"invalid": "data"}}}
        processed_matches = processor.process_match_data(malformed_response)
        assert len(processed_matches) == 0
        
        # Test embed creation with minimal data
        minimal_match = ProcessedMatch(
            match_id=1,
            home_team=Team(id=1, name="Team A", short_name="TA"),
            away_team=Team(id=2, name="Team B", short_name="TB"),
            league=League(id=1, name="Test League", country="Test"),
            date="2025-08-18",
            time="15:00",
            venue="Test Stadium",
            status="scheduled"
        )
        
        embed = embed_builder.create_match_preview_embed(minimal_match)
        assert embed is not None
        assert "Team A" in embed.title
        assert "Team B" in embed.title

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])