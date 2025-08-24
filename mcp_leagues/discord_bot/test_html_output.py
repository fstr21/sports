#!/usr/bin/env python3
"""
Test HTML Template Output - Generate sample HTML file to preview design
"""
from pathlib import Path
from jinja2 import Template
import webbrowser
import os

def test_html_template():
    """Generate test HTML file with sample data to preview the design"""
    
    # Load the HTML template
    template_path = Path("templates/baseball_analysis.html")
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Sample template data (Yankees vs Red Sox like your original)
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
    
    # Render template with sample data
    template = Template(template_content)
    rendered_html = template.render(**sample_data)
    
    # Save rendered HTML to test file
    output_file = Path("test_analysis_output.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(rendered_html)
    
    print(f"Generated test HTML file: {output_file.absolute()}")
    print("Opening in browser...")
    
    # Open in default browser
    webbrowser.open(f"file://{output_file.absolute()}")
    
    return str(output_file.absolute())

if __name__ == "__main__":
    print("TESTING HTML TEMPLATE OUTPUT")
    print("=" * 50)
    print("Generating sample baseball analysis HTML...")
    print()
    
    try:
        result = test_html_template()
        print(f"\nSuccess! HTML file created and opened in browser")
        print(f"File location: {result}")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()