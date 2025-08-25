#!/usr/bin/env python3
"""
Test Enhanced Hybrid Design Locally - Generate images with enhanced template
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

async def generate_enhanced_hybrid_test():
    """Generate enhanced hybrid analysis image for testing"""
    
    print("Enhanced Hybrid Design Test")
    print("=" * 50)
    
    # Comprehensive game data
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
    
    # MCP request for 5-expert analysis
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
            expert_analysis = analysis.get('expert_analysis', 'No detailed analysis available')
            
            print(f"Step 2: Analysis received - {len(expert_analysis)} characters")
            
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Step 3: Use Enhanced Template
            template_file_path = Path(__file__).parent.parent / "mcp_leagues" / "discord_bot" / "templates" / "enhanced_hybrid_analysis.html"
            
            if template_file_path.exists():
                print(f"Step 3: Using enhanced template from: {template_file_path}")
                with open(template_file_path, 'r', encoding='utf-8') as f:
                    html_template = f.read()
            else:
                print("Step 3: Enhanced template not found, cannot continue")
                print(f"Expected location: {template_file_path}")
                return
            
            # Prepare template data for enhanced design
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
            
            print("Step 4: Rendering enhanced template...")
            
            # Render template
            template = Template(html_template)
            rendered_html = template.render(**template_data)
            
            print("Step 5: Generating enhanced image...")
            
            # Generate image using Playwright
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set optimal size for Discord readability
                await page.set_viewport_size({"width": 1200, "height": 2000})
                
                # Load content
                await page.set_content(rendered_html, wait_until="networkidle")
                await page.wait_for_timeout(1000)
                
                # Take screenshot
                screenshot = await page.screenshot(type="png", full_page=True)
                await browser.close()
                
                # Save enhanced image
                image_file = Path(__file__).parent / f"enhanced_hybrid_test_{timestamp}.png"
                with open(image_file, 'wb') as f:
                    f.write(screenshot)
                
                print(f"Step 6: Enhanced image saved - {image_file.name}")
                print(f"         Size: {len(screenshot) / 1024:.1f} KB")
                
                # Also save the HTML for preview
                html_file = Path(__file__).parent / f"enhanced_preview_{timestamp}.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(rendered_html)
                
                print(f"Step 7: HTML preview saved - {html_file.name}")
                
                print("\nENHANCED DESIGN TEST COMPLETE!")
                print("Key improvements you'll see:")
                print("- Professional blue gradient header with baseball emoji")
                print("- Better visual hierarchy with clear sections")
                print("- Enhanced typography with multiple font weights")
                print("- Prominent recommendation banner in green")
                print("- Key insights callout section")
                print("- Better spacing and contrast for Discord readability")
                
                return {
                    'image_file': str(image_file),
                    'html_file': str(html_file),
                    'analysis_length': len(expert_analysis)
                }
            
    except Exception as e:
        print(f"Error generating enhanced test: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function to run the enhanced design test"""
    print("Enhanced Hybrid Design Test")
    print("Testing the new improved visual design")
    print()
    
    # Run the async generation
    result = asyncio.run(generate_enhanced_hybrid_test())
    
    if result:
        print(f"\nTest complete! Check the generated files:")
        print(f"- Image: {Path(result['image_file']).name}")
        print(f"- HTML Preview: {Path(result['html_file']).name}")
        print(f"- Analysis: {result['analysis_length']} characters with player details")
    else:
        print("\nTest failed - check error messages above")

if __name__ == "__main__":
    main()