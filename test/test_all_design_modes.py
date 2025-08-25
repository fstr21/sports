#!/usr/bin/env python3
"""
Test All Enhanced Design Modes - Generate original, light, and dark mode images
"""

import asyncio
import json
import httpx
import sys
from pathlib import Path
from jinja2 import Template
from datetime import datetime
from playwright.async_api import async_playwright

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Custom Chronulus MCP Configuration
CUSTOM_CHRONULUS_URL = "https://customchronpredictormcp-production.up.railway.app/mcp"

async def generate_all_design_modes():
    """Generate images for all design modes: original enhanced, light, and dark"""
    
    print("Enhanced Design Mode Comparison Test")
    print("=" * 50)
    
    # Comprehensive game data (same for all tests)
    game_data = {
        "home_team": "New York Yankees (82-58, .586 win%, AL East leaders)",
        "away_team": "Boston Red Sox (75-65, .536 win%, Wild Card contention)", 
        "sport": "Baseball",
        "venue": "Yankee Stadium (49,642 capacity, pitcher-friendly dimensions)",
        "game_date": "August 24, 2025 - 7:05 PM ET",
        "additional_context": (
            "Yankees starter: Gerrit Cole (12-7, 3.41 ERA, 1.09 WHIP, 198 K). "
            "Red Sox starter: Brayan Bello (11-9, 4.15 ERA, 1.31 WHIP, 156 K). "
            "Key players: Aaron Judge (.312 BA, 48 HR), Juan Soto (.288 BA, 35 HR), "
            "Rafael Devers (.287 BA, 28 HR), Trevor Story (.251 BA, 15 HR). "
            "Analysis must include player-specific comparisons and ERA analysis."
        )
    }
    
    # Get MCP analysis
    print("Step 1: Getting analysis from Custom Chronulus MCP...")
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getCustomChronulusAnalysis",
            "arguments": {
                "game_data": game_data,
                "expert_count": 5,
                "analysis_depth": "comprehensive"
            }
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(CUSTOM_CHRONULUS_URL, json=mcp_request)
            result = response.json()
            
            analysis_text = result["result"]["content"][0]["text"]
            analysis_data = json.loads(analysis_text)
            analysis = analysis_data.get("analysis", {})
            
            print(f"Step 2: Analysis received - {len(analysis.get('expert_analysis', ''))} chars")
            
            # Prepare template data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            template_data = {
                'away_team': 'Boston Red Sox',
                'home_team': 'New York Yankees',
                'game_date': game_data['game_date'],
                'venue_name': 'Yankee Stadium',
                'away_status': 'Wild Card Race',
                'home_status': 'AL East Leaders',
                'away_prob': f"{analysis.get('away_team_win_probability', 0.35) * 100:.1f}",
                'home_prob': f"{analysis.get('home_team_win_probability', 0.65) * 100:.1f}",
                'recommendation_short': 'BET YANKEES',
                'model_name': 'Gemini 2.0',
                'expert_analysis': analysis.get('expert_analysis', 'Sample analysis'),
                'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p ET'),
                'market_edge': '-5.8%',
                'confidence': '75%'
            }
            
            # Load all three templates
            base_path = Path(__file__).parent.parent / "mcp_leagues" / "discord_bot" / "templates"
            templates = {
                'original': base_path / "enhanced_hybrid_analysis.html",
                'light': base_path / "light_enhanced_hybrid_analysis.html", 
                'dark': base_path / "dark_enhanced_hybrid_analysis.html"
            }
            
            print("Step 3: Generating images for all design modes...")
            
            # Generate images for each template
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=True)
                
                results = {}
                for mode, template_path in templates.items():
                    if template_path.exists():
                        print(f"  Generating {mode} mode...")
                        
                        with open(template_path, 'r', encoding='utf-8') as f:
                            html_template = f.read()
                        
                        template = Template(html_template)
                        rendered_html = template.render(**template_data)
                        
                        page = await browser.new_page()
                        await page.set_viewport_size({"width": 1200, "height": 2000})
                        await page.set_content(rendered_html, wait_until="networkidle")
                        await page.wait_for_timeout(1000)
                        
                        screenshot = await page.screenshot(type="png", full_page=True)
                        await page.close()
                        
                        # Save image
                        image_file = Path(__file__).parent / f"{mode}_enhanced_design_{timestamp}.png"
                        with open(image_file, 'wb') as f:
                            f.write(screenshot)
                        
                        results[mode] = {
                            'file': image_file.name,
                            'size': f"{len(screenshot) / 1024:.1f} KB"
                        }
                        print(f"    Saved: {image_file.name} ({results[mode]['size']})")
                    else:
                        print(f"    Template not found: {template_path}")
                
                await browser.close()
            
            # Generate comparison report
            print("\\nStep 4: Generating comparison report...")
            report = f"""
ENHANCED DESIGN MODE COMPARISON COMPLETE!

Generated Files:
"""
            for mode, info in results.items():
                report += f"• {mode.title()} Mode: {info['file']} ({info['size']})\\n"
            
            report += f"""
Design Features Comparison:

ORIGINAL ENHANCED:
- Blue gradient header with baseball emoji
- Professional sports betting aesthetics  
- Enhanced typography (Inter 300-800)
- Green recommendation banner
- Key insights callout section

LIGHT MODE ENHANCED:
- Improved light theme with better contrast
- Brighter colors and cleaner backgrounds
- Blue/green gradient scheme
- Enhanced visual hierarchy
- Better Discord preview readability

DARK MODE ENHANCED:  
- Purple gradient header for premium feel
- Dark backgrounds with light text
- High contrast for better readability
- Glowing effects and animations
- Modern dark theme aesthetics

Analysis Quality:
- Expert Analysis: {len(template_data['expert_analysis'])} characters
- Player Analysis: Cole vs Bello included
- All modes use same comprehensive data

Next Steps:
1. Open each image to compare visual designs
2. Test Discord readability with each mode
3. Choose preferred design for production
4. Update Discord bot to use selected mode
"""
            
            print(report)
            
            # Save report
            report_file = Path(__file__).parent / f"design_comparison_report_{timestamp}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            return results
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("Enhanced Design Mode Comparison")
    print("Testing original, light, and dark mode designs")
    print()
    
    result = asyncio.run(generate_all_design_modes())
    
    if result:
        print(f"\\nComparison complete! Generated {len(result)} design modes.")
        print("Check the PNG files to compare visual designs.")
    else:
        print("\\nComparison failed - check error messages above")

if __name__ == "__main__":
    main()