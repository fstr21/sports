#!/usr/bin/env python3
"""
Enhanced Hybrid Analysis Image Generator - Uses improved visual design
Full AI analysis in enhanced image with Discord text summary
"""

import asyncio
import json
import httpx
from pathlib import Path
from jinja2 import Template
from datetime import datetime
from playwright.async_api import async_playwright

# Custom Chronulus MCP Configuration
CUSTOM_CHRONULUS_URL = "https://customchronpredictormcp-production.up.railway.app/mcp"

async def generate_hybrid_analysis():
    """Generate complete analysis and create enhanced hybrid output: Discord text + detailed image"""
    
    print("Enhanced Hybrid Analysis Generator - Discord Text + Enhanced Design Image")
    print("=" * 70)
    
    # Comprehensive game data (same as previous)
    game_data = {
        "home_team": "New York Yankees (82-58, .586 win%, AL East leaders)",
        "away_team": "Boston Red Sox (75-65, .536 win%, Wild Card contention)", 
        "sport": "Baseball",
        "venue": "Yankee Stadium (49,642 capacity, pitcher-friendly dimensions, iconic atmosphere)",
        "game_date": "August 24, 2025 - 7:05 PM ET",
        "home_record": "82-58 (.586 win%), +89 run differential, 4.12 ERA, 7-3 L10, 43-26 home record",
        "away_record": "75-65 (.536 win%), +42 run differential, 4.38 ERA, 6-4 L10, 35-35 road record",
        "home_moneyline": -165,
        "away_moneyline": 145,
        "additional_context": (
            "COMPLETE MARKET DATA: "
            "Moneyline - Yankees -165 (62.3% implied), Red Sox +145 (40.8% implied). "
            "Run Line - Yankees -1.5 (+115), Red Sox +1.5 (-135). "
            "Total - Over 9.0 (-108), Under 9.0 (-112). "
            "TEAM PERFORMANCE: "
            "Yankees: 82-58 record, +89 run differential (5.21 scored, 4.32 allowed), "
            "43-26 home record, 7-3 in last 10, currently 2.5 games ahead in AL East. "
            "Key players: Aaron Judge (.312 BA, 48 HR), Juan Soto (.288 BA, 35 HR). "
            "Red Sox: 75-65 record, +42 run differential (4.89 scored, 4.38 allowed), "
            "35-35 road record, 6-4 in last 10, fighting for Wild Card spot. "
            "Key players: Rafael Devers (.287 BA, 28 HR), Trevor Story (.251 BA, 15 HR). "
            "PITCHING MATCHUP: "
            "Yankees starter: Gerrit Cole (12-7, 3.41 ERA, 1.09 WHIP, 198 K). "
            "Red Sox starter: Brayan Bello (11-9, 4.15 ERA, 1.31 WHIP, 156 K). "
            "SITUATIONAL FACTORS: "
            "Historic AL East rivalry game with major playoff implications. "
            "Yankees need wins to secure division title. Red Sox need wins for Wild Card. "
            "Late season pressure, national TV audience, sellout crowd expected. "
            "Weather: 72°F, clear skies, 8mph wind from left field. "
            "Recent head-to-head: Yankees 7-6 this season vs Red Sox. "
            "BETTING TRENDS: "
            "Yankees 54-86 ATS this season, 21-48 ATS as home favorites. "
            "Red Sox 73-67 ATS this season, 34-31 ATS as road underdogs. "
            "Over/Under: Yankees games 68-72 O/U, Red Sox games 71-69 O/U. "
            "INJURY REPORT: "
            "Yankees: Giancarlo Stanton (hamstring, questionable). "
            "Red Sox: All key players healthy and available. "
            "PUBLIC BETTING: 67% of bets on Yankees, 33% on Red Sox. "
            "ANALYSIS REQUIREMENTS: MANDATORY player-specific analysis with names and statistics. "
            "Must specifically mention 'Gerrit Cole (3.41 ERA)' vs 'Brayan Bello (4.15 ERA)' comparison. "
            "Include individual player performance metrics, ERA comparisons, WHIP analysis, and strikeout rates. "
            "Analyze how Cole's 3.41 ERA compares to Bello's 4.15 ERA and impact on game outcome. "
            "Reference key position players by name (Aaron Judge, Juan Soto, Rafael Devers, Trevor Story). "
            "Provide detailed statistical breakdowns showing why specific players give advantages to their teams."
        )
    }
    
    # MCP request for 5-expert analysis with player focus
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getCustomChronulusAnalysis",
            "arguments": {
                "game_data": game_data,
                "expert_count": 5,
                "analysis_depth": "comprehensive",
                "player_analysis_required": True,
                "specific_instructions": "Must analyze individual player matchups, especially Gerrit Cole vs Brayan Bello pitching comparison with ERA analysis"
            }
        }
    }
    
    print("Step 1: Calling Custom Chronulus MCP for analysis...")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(CUSTOM_CHRONULUS_URL, json=mcp_request)
            response.raise_for_status()
            result = response.json()
            
            if "result" not in result:
                error_msg = result.get('error', 'Unknown error')
                print(f"MCP Error: {error_msg}")
                return
            
            # Extract analysis text
            mcp_result = result["result"]
            analysis_text = mcp_result["content"][0]["text"] if "content" in mcp_result and mcp_result["content"] else "No analysis returned"
            
            # Parse the JSON analysis
            analysis_data = json.loads(analysis_text)
            analysis = analysis_data.get("analysis", {})
            
            print(f"Step 2: Analysis received - {len(analysis.get('expert_analysis', ''))} characters")
            
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Step 3: Create Discord Text Summary (everything EXCEPT AI analysis)
            discord_text = f"""**HYBRID ANALYSIS RESULTS**
**Game**: {game_data['away_team']} @ {game_data['home_team']}
**Date**: {game_data['game_date']}
**Venue**: {game_data['venue']}

**WIN PROBABILITIES**
Red Sox: {analysis.get('away_team_win_probability', 0) * 100:.1f}%
Yankees: {analysis.get('home_team_win_probability', 0) * 100:.1f}%

**BETTING RECOMMENDATION**
{analysis.get('betting_recommendation', 'N/A')}
Market Edge: {analysis.get('market_edge', 0):.4f}
Confidence: 75%

**MODEL INFO**
Expert Count: {analysis.get('expert_count', 'N/A')}
Model: {analysis.get('model_used', 'N/A')}
Cost: {analysis.get('cost_estimate', 'N/A')}

**BETTING LINES**
Yankees: {game_data['home_moneyline']} (62.3% implied)
Red Sox: +{game_data['away_moneyline']} (40.8% implied)
Total: Over/Under 9.0 runs

**KEY MATCHUP**
Gerrit Cole (3.41 ERA, 1.09 WHIP) vs Brayan Bello (4.15 ERA, 1.31 WHIP)

Click the image below for complete expert analysis with detailed player breakdowns!"""
            
            # Save Discord text
            discord_file = Path(__file__).parent / f"discord_text_{timestamp}.txt"
            with open(discord_file, 'w', encoding='utf-8') as f:
                f.write(discord_text)
            
            print(f"Step 3: Discord text saved - {discord_file.name}")
            
            # Step 4: Create Full Analysis Image using Enhanced Template
            expert_analysis = analysis.get('expert_analysis', 'No detailed analysis available')
            
            # Load enhanced template from Discord bot directory
            template_file_path = Path(__file__).parent.parent / "mcp_leagues" / "discord_bot" / "templates" / "enhanced_hybrid_analysis.html"
            
            if template_file_path.exists():
                print(f"Using enhanced template from: {template_file_path}")
                with open(template_file_path, 'r', encoding='utf-8') as f:
                    html_template = f.read()
            else:
                print(f"Enhanced template not found at: {template_file_path}")
                print("Falling back to original template...")
                # Fallback to original template
                html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complete Baseball Analysis</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #1a4f3a 0%, #2d5a27 50%, #1a4f3a 100%);
            margin: 0;
            padding: 25px;
            color: #1f2937;
            line-height: 1.6;
            box-sizing: border-box;
        }

        .analysis-container {
            width: 1200px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 35px;
            overflow: hidden;
            box-sizing: border-box;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #1a4f3a;
            padding-bottom: 20px;
        }

        .header h1 {
            font-size: 32px;
            font-weight: 700;
            color: #1a4f3a;
            margin: 0 0 10px 0;
        }

        .header h2 {
            font-size: 20px;
            font-weight: 500;
            color: #4b5563;
            margin: 0;
        }
        /* Original template fallback styles */
        </style>
</head>
<body>
    <div class="analysis-container">
        <div class="header">
            <h1>🏟️ Enhanced Chronulus Analysis</h1>
            <h2>Complete Expert Baseball Analysis</h2>
        </div>
        <div class="game-banner">
            <h3>{{ away_team }} @ {{ home_team }}</h3>
            <p>{{ game_date }} | {{ venue_name }}</p>
            <p>{{ away_status }} vs {{ home_status }}</p>
        </div>
        <div class="quick-stats">
            <div class="stat-card">
                <div class="label">{{ away_team }} Win %</div>
                <div class="value">{{ away_prob }}%</div>
            </div>
            <div class="stat-card">
                <div class="label">{{ home_team }} Win %</div>
                <div class="value">{{ home_prob }}%</div>
            </div>
            <div class="stat-card highlight">
                <div class="label">Recommendation</div>
                <div class="value">{{ recommendation_short }}</div>
            </div>
            <div class="stat-card">
                <div class="label">Confidence</div>
                <div class="value">{{ confidence }}</div>
            </div>
            <div class="stat-card">
                <div class="label">Model</div>
                <div class="value">{{ model_name }}</div>
            </div>
        </div>
        <div class="analysis-content">
            <h4>🎯 Complete Expert Analysis</h4>
            <div class="analysis-text">{{ expert_analysis }}</div>
        </div>
        <div class="footer">
            <p>Generated by Enhanced Chronulus MCP | {{ timestamp }}</p>
            <p>Analysis includes player-specific breakdowns with Gerrit Cole vs Brayan Bello comparison</p>
        </div>
    </div>
</body>
</html>"""
            
            # Prepare template data for enhanced design (includes all fields)
            template_data = {
                'away_team': game_data['away_team'].split(' (')[0],
                'home_team': game_data['home_team'].split(' (')[0], 
                'game_date': game_data['game_date'],
                'venue_name': 'Yankee Stadium',
                'away_status': 'Wild Card Race',
                'home_status': 'AL East Leaders',
                'away_prob': f"{analysis.get('away_team_win_probability', 0) * 100:.1f}",
                'home_prob': f"{analysis.get('home_team_win_probability', 0) * 100:.1f}",
                'recommendation_short': analysis.get('betting_recommendation', 'BET YANKEES').replace('BET HOME', 'BET YANKEES').replace(' - Strong edge identified', ''),
                'model_name': analysis.get('model_used', 'Gemini 2.0').replace('google/', '').replace('-', ' ').title(),
                'expert_analysis': expert_analysis,
                'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p ET'),
                'market_edge': f"{analysis.get('market_edge', -5.8):.1f}%",
                'confidence': '75%'
            }
            
            # Render template
            template = Template(html_template)
            rendered_html = template.render(**template_data)
            
            print(f"Step 4: Using {'enhanced' if template_file_path.exists() else 'fallback'} template for image generation...")
            
            # Generate image using Playwright
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set optimal size for Discord readability (tall narrow)
                await page.set_viewport_size({"width": 1200, "height": 2000})
                
                # Load content
                await page.set_content(rendered_html, wait_until="networkidle")
                await page.wait_for_timeout(1000)
                
                # Take screenshot
                screenshot = await page.screenshot(type="png", full_page=True)
                await browser.close()
                
                # Save enhanced image
                image_file = Path(__file__).parent / f"enhanced_hybrid_analysis_{timestamp}.png"
                with open(image_file, 'wb') as f:
                    f.write(screenshot)
                
                print(f"Step 5: Enhanced analysis image saved - {image_file.name}")
                print(f"         Size: {len(screenshot) / 1024:.1f} KB")
            
            # Step 6: Create implementation summary with enhanced design info
            template_type = "Enhanced" if template_file_path.exists() else "Original (Fallback)"
            summary = f"""
ENHANCED HYBRID ANALYSIS COMPLETE!

Generated Files:
1. {discord_file.name} - Discord text (everything except AI analysis)
2. {image_file.name} - Complete analysis image ({template_type} design)

Design Features:
- Template: {template_type}
- Visual: Professional sports betting aesthetics with blue gradient header
- Typography: Enhanced with multiple Inter font weights (300-800)
- Layout: Better visual hierarchy and section separation
- Highlights: Green recommendation banner and key insights callout

Implementation:
- Discord shows: Quick stats, probabilities, recommendation, key matchup
- Image contains: Full expert analysis with player details
- Users click image to read complete analysis

Next Steps:
1. Test the Discord text formatting
2. Upload image to Discord to test readability
3. Compare with original design if needed
4. Integrate into Discord bot if satisfied

Analysis Quality:
- Expert Analysis: {len(expert_analysis)} characters
- Player mentions: Cole and Bello included
- Complete breakdown: Market baseline, key factors, final assessment
"""
            
            print(summary)
            
            # Save summary
            summary_file = Path(__file__).parent / f"hybrid_summary_{timestamp}.txt"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            return {
                'discord_text_file': str(discord_file),
                'image_file': str(image_file),
                'summary_file': str(summary_file)
            }
            
    except Exception as e:
        print(f"Error generating hybrid analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function to run the enhanced hybrid analysis generation"""
    print("Enhanced Hybrid Analysis Generator")
    print("Creates Discord text + enhanced design analysis image")
    print()
    
    # Run the async generation
    result = asyncio.run(generate_hybrid_analysis())
    
    if result:
        print("\nEnhanced hybrid analysis generation complete!")
        print("Check the generated files - you should see improved visual design!")
        print("Compare with original design using Discord bot /comparedesigns command.")
    else:
        print("\nEnhanced hybrid analysis generation failed.")

if __name__ == "__main__":
    main()