#!/usr/bin/env python3
"""
Test Image Generation Pipeline - Verify HTML-to-image works locally
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from utils.html_to_image import create_baseball_analysis_image

async def test_image_generation():
    """Test the complete HTML-to-image pipeline"""
    
    print("Testing HTML-to-Image Generation")
    print("=" * 40)
    
    # Sample template data (Yankees vs Red Sox)
    sample_data = {
        # Game details
        'game_date': 'August 24, 2025 - 7:05 PM ET',
        'venue_name': 'Yankee Stadium',
        'venue_details': '49,642 capacity • Pitcher-friendly dimensions • Iconic atmosphere',
        
        # Team information
        'home_team_name': 'New York Yankees',
        'away_team_name': 'Boston Red Sox',
        'home_team_logo': 'NY',
        'away_team_logo': 'B',
        'home_team_color_primary': '#132448',
        'home_team_color_secondary': '#0d1835',
        'away_team_color_primary': '#bd3039',
        'away_team_color_secondary': '#a02128',
        
        # Team records and status
        'home_team_record': '82-58 (.586)',
        'away_team_record': '75-65 (.536)',
        'home_team_status': 'AL East Leaders',
        'away_team_status': 'Wild Card Race',
        
        # Pitcher information
        'home_pitcher_name': 'Gerrit Cole',
        'away_pitcher_name': 'Brayan Bello',
        'home_pitcher_record': '12-7',
        'away_pitcher_record': '11-9',
        'home_pitcher_era': '3.41',
        'away_pitcher_era': '4.15',
        'home_pitcher_whip': '1.09',
        'away_pitcher_whip': '1.31',
        'home_pitcher_strikeouts': '198',
        'away_pitcher_strikeouts': '156',
        
        # Betting information
        'home_moneyline': '-165',
        'away_moneyline': '+145',
        'home_implied_prob': '62.3%',
        'away_implied_prob': '40.8%',
        'home_team_odds_class': 'favorite',
        'away_team_odds_class': 'underdog',
        'total_line': 'Over/Under 9.0 runs',
        
        # AI Analysis
        'home_win_probability': '65.0%',
        'away_win_probability': '35.0%',
        'home_probability_class': 'positive',
        'ai_confidence': '60% (Moderate)',
        'home_market_edge': '+2.7pp',
        'away_market_edge': '-5.8pp',
        'home_edge_class': 'positive',
        'away_edge_class': 'negative',
        'model_cost': '$0.10-$0.25',
        'ai_key_insight': 'Yankees are 21-48 ATS as home favorites, suggesting they underperform market expectations in this situation. However, their underlying metrics and pitching advantage provide counterbalance.',
        
        # Recommendation
        'betting_recommendation_title': '🎯 BET HOME (Yankees)',
        'betting_recommendation_text': 'Strong edge identified based on AI model showing 2.7 percentage point advantage over market pricing, despite Yankees\' poor ATS record as home favorites',
        
        # Game context
        'series_context': 'Historic AL East rivalry with major playoff implications',
        'home_recent_form': '7-3 in last 10 • 2.5 games ahead in AL East',
        'away_recent_form': '6-4 in last 10 • Fighting for Wild Card spot',
        'head_to_head': 'Yankees lead season series 7-6',
        'weather_info': '72°F, clear skies, 8mph wind from left field'
    }
    
    try:
        print("Step 1: Creating template data... OK")
        
        print("Step 2: Starting browser and generating image...")
        image_bytes = await create_baseball_analysis_image(sample_data)
        
        print(f"Step 3: Image generated successfully! ({len(image_bytes)} bytes)")
        
        # Save the image to file for testing
        output_file = "test_baseball_analysis.png"
        with open(output_file, "wb") as f:
            f.write(image_bytes)
        
        print(f"Step 4: Image saved as: {output_file}")
        print(f"File size: {len(image_bytes) / 1024:.1f} KB")
        
        print("\n" + "="*40)
        print("SUCCESS! Image generation pipeline working!")
        print(f"[OK] Check the generated image: {output_file}")
        print("[OK] Ready to test Discord integration")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: Image generation failed")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("TESTING IMAGE GENERATION PIPELINE")
    print("Testing HTML -> Image conversion locally")
    print()
    
    # Run the async test
    success = asyncio.run(test_image_generation())
    
    if success:
        print("\nAll tests passed! Ready for Discord integration.")
    else:
        print("\nTests failed. Need to fix issues before Discord.")