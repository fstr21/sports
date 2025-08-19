"""
Integration demo for Soccer H2H Analysis System
Demonstrates the complete workflow from MCP data to Discord embed
"""

import asyncio
import json
from soccer_integration import (
    SoccerMCPClient, SoccerDataProcessor, SoccerEmbedBuilder,
    Team, League, H2HInsights
)


async def demo_h2h_analysis_workflow():
    """Demonstrate the complete H2H analysis workflow"""
    print("🚀 Soccer H2H Analysis Integration Demo")
    print("=" * 50)
    
    # Initialize components
    mcp_client = SoccerMCPClient()
    data_processor = SoccerDataProcessor()
    embed_builder = SoccerEmbedBuilder()
    
    # Sample teams for demo
    liverpool = Team(
        id=123,
        name="Liverpool FC",
        short_name="Liverpool",
        country="England"
    )
    
    arsenal = Team(
        id=456,
        name="Arsenal FC", 
        short_name="Arsenal",
        country="England"
    )
    
    premier_league = League(
        id=228,
        name="Premier League",
        country="England",
        season="2024-25"
    )
    
    # Sample H2H data (simulating MCP response)
    sample_h2h_data = {
        'total_meetings': 15,
        'team1_wins': 6,  # Liverpool wins
        'team2_wins': 5,  # Arsenal wins
        'draws': 4,
        'match_history': [
            {'team1_score': 2, 'team2_score': 1, 'date': '2024-01-15'},
            {'team1_score': 1, 'team2_score': 1, 'date': '2023-12-10'},
            {'team1_score': 0, 'team2_score': 2, 'date': '2023-11-05'},
            {'team1_score': 3, 'team2_score': 1, 'date': '2023-09-20'},
            {'team1_score': 1, 'team2_score': 3, 'date': '2023-08-15'}
        ],
        'recent_form': {
            'team1': [  # Liverpool recent form
                {'result': 'W', 'opponent': 'Chelsea', 'score': '2-1', 'date': '2024-02-01'},
                {'result': 'W', 'opponent': 'Man City', 'score': '1-0', 'date': '2024-01-25'},
                {'result': 'D', 'opponent': 'Tottenham', 'score': '1-1', 'date': '2024-01-20'},
                {'result': 'W', 'opponent': 'Brighton', 'score': '3-0', 'date': '2024-01-15'},
                {'result': 'L', 'opponent': 'Newcastle', 'score': '0-1', 'date': '2024-01-10'}
            ],
            'team2': [  # Arsenal recent form
                {'result': 'W', 'opponent': 'West Ham', 'score': '2-0', 'date': '2024-02-01'},
                {'result': 'L', 'opponent': 'Man United', 'score': '1-2', 'date': '2024-01-25'},
                {'result': 'W', 'opponent': 'Crystal Palace', 'score': '3-1', 'date': '2024-01-20'},
                {'result': 'D', 'opponent': 'Everton', 'score': '0-0', 'date': '2024-01-15'},
                {'result': 'W', 'opponent': 'Brentford', 'score': '2-1', 'date': '2024-01-10'}
            ]
        },
        'advanced_metrics': {
            'team1': {  # Liverpool metrics
                'total_cards': 35,
                'matches_played': 15,
                'clean_sheets': 8,
                'total_goals': 28,
                'goals_conceded': 18,
                'btts_matches': 9,
                'goal_timing': {'first_half': 12, 'second_half': 16}
            },
            'team2': {  # Arsenal metrics
                'total_cards': 28,
                'matches_played': 15,
                'clean_sheets': 6,
                'total_goals': 25,
                'goals_conceded': 20,
                'btts_matches': 10,
                'goal_timing': {'first_half': 10, 'second_half': 15}
            }
        }
    }
    
    print("📊 Step 1: Processing H2H data...")
    
    # Process the H2H data using SoccerDataProcessor
    h2h_insights = data_processor.calculate_h2h_insights(
        sample_h2h_data, liverpool.name, arsenal.name
    )
    
    print(f"✅ Processed {h2h_insights.total_meetings} historical meetings")
    print(f"   Liverpool wins: {h2h_insights.home_team_wins} ({h2h_insights.home_win_percentage:.1f}%)")
    print(f"   Arsenal wins: {h2h_insights.away_team_wins} ({h2h_insights.away_win_percentage:.1f}%)")
    print(f"   Draws: {h2h_insights.draws} ({h2h_insights.draw_percentage:.1f}%)")
    print(f"   Average goals per game: {h2h_insights.avg_goals_per_game:.2f}")
    
    print("\n🎯 Step 2: Generating betting recommendations...")
    
    # Display betting recommendations
    for i, recommendation in enumerate(h2h_insights.betting_recommendations, 1):
        print(f"   {i}. {recommendation}")
    
    print("\n📈 Step 3: Analyzing advanced metrics...")
    
    # Display advanced statistics
    if 'team1' in h2h_insights.key_statistics:
        liverpool_stats = h2h_insights.key_statistics['team1']
        print(f"   Liverpool - Goals/Game: {liverpool_stats.get('goals_per_game', 0):.1f}, "
              f"Clean Sheets: {liverpool_stats.get('clean_sheet_percentage', 0):.1f}%")
    
    if 'team2' in h2h_insights.key_statistics:
        arsenal_stats = h2h_insights.key_statistics['team2']
        print(f"   Arsenal - Goals/Game: {arsenal_stats.get('goals_per_game', 0):.1f}, "
              f"Clean Sheets: {arsenal_stats.get('clean_sheet_percentage', 0):.1f}%")
    
    print("\n🎨 Step 4: Creating Discord embed...")
    
    # Create Discord embed
    embed = embed_builder.create_h2h_analysis_embed(
        h2h_insights, liverpool, arsenal, premier_league
    )
    
    print(f"✅ Created embed: '{embed.title}'")
    print(f"   Color: #{embed.color.value:06x}")
    print(f"   Fields: {len(embed.fields)}")
    
    # Display embed fields
    for field in embed.fields:
        print(f"   📋 {field.name}: {len(field.value)} characters")
    
    print("\n🔍 Step 5: Testing error handling...")
    
    # Test error handling with malformed data
    malformed_data = {
        'total_meetings': 'invalid',
        'team1_wins': None,
        'match_history': 'not_a_list'
    }
    
    error_insights = data_processor.calculate_h2h_insights(
        malformed_data, "Team A", "Team B"
    )
    
    print(f"✅ Error handling test: {error_insights.total_meetings} meetings (graceful degradation)")
    print(f"   Error in key_statistics: {'error' in error_insights.key_statistics}")
    
    print("\n🎉 Demo completed successfully!")
    print("=" * 50)
    
    return {
        'h2h_insights': h2h_insights,
        'embed': embed,
        'error_test_passed': 'error' in error_insights.key_statistics
    }


def demo_betting_recommendations():
    """Demonstrate betting recommendations generation"""
    print("\n💰 Betting Recommendations Demo")
    print("-" * 30)
    
    data_processor = SoccerDataProcessor()
    
    # Test different scenarios
    scenarios = [
        {
            'name': 'High-scoring rivalry',
            'insights': H2HInsights(
                total_meetings=10,
                home_team_wins=3,
                away_team_wins=4,
                draws=3,
                avg_goals_per_game=3.2,
                recent_form={'team1': ['W', 'W', 'L', 'W', 'D'], 'team2': ['L', 'W', 'W', 'L', 'W']},
                key_statistics={'team1': {'clean_sheet_percentage': 20}, 'team2': {'cards_per_game': 4.0}}
            )
        },
        {
            'name': 'Defensive battle',
            'insights': H2HInsights(
                total_meetings=8,
                home_team_wins=2,
                away_team_wins=1,
                draws=5,
                avg_goals_per_game=1.5,
                recent_form={'team1': ['D', 'D', 'L', 'D', 'W'], 'team2': ['D', 'W', 'D', 'D', 'L']},
                key_statistics={'team1': {'clean_sheet_percentage': 60}, 'team2': {'clean_sheet_percentage': 55}}
            )
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📊 Scenario: {scenario['name']}")
        insights = scenario['insights']
        
        # Generate recommendations
        recommendations = data_processor.generate_betting_recommendations(insights, {})
        
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")


if __name__ == '__main__':
    # Run the demo
    result = asyncio.run(demo_h2h_analysis_workflow())
    
    # Run betting recommendations demo
    demo_betting_recommendations()
    
    print(f"\n✨ All demos completed successfully!")
    print(f"   H2H insights generated: ✅")
    print(f"   Discord embed created: ✅") 
    print(f"   Error handling tested: ✅")