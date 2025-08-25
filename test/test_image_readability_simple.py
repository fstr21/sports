#!/usr/bin/env python3
"""
Simple Image Readability Test - Generate analysis images in different dimensions
Uses playwright directly without module dependencies
"""

import asyncio
from pathlib import Path
from jinja2 import Template
from playwright.async_api import async_playwright

async def test_image_readability():
    """Test different image dimensions with full analysis text for Discord readability"""
    
    print("🧪 Testing Image Readability for Discord")
    print("=" * 50)
    
    # Load the full analysis data from our generated file
    analysis_file = Path(__file__).parent / "full_chronulus_analysis_20250824_220926.md"
    
    if not analysis_file.exists():
        print(f"❌ Analysis file not found: {analysis_file}")
        print("Please run the generate_full_analysis.py script first")
        return
    
    # Parse the analysis text (extract the expert analysis section)
    with open(analysis_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the expert analysis section
    start_marker = "## Complete Expert Analysis"
    end_marker = "## Statistical Model Parameters"
    
    if start_marker in content and end_marker in content:
        start_idx = content.find(start_marker) + len(start_marker)
        end_idx = content.find(end_marker)
        expert_analysis = content[start_idx:end_idx].strip()
    else:
        expert_analysis = "Expert analysis not found in the markdown file"
    
    print(f"📄 Loaded analysis: {len(expert_analysis)} characters")
    
    # Test configurations - different dimensions for Discord readability
    test_configs = [
        {
            "name": "Portrait_Mobile",
            "width": 900,
            "height": 1600,
            "description": "Mobile portrait (900x1600)"
        },
        {
            "name": "Square_Large", 
            "width": 1400,
            "height": 1400,
            "description": "Large square (1400x1400)"
        },
        {
            "name": "Tall_Narrow",
            "width": 1200,
            "height": 2000,
            "description": "Tall narrow (1200x2000)"
        },
        {
            "name": "Standard_Wide",
            "width": 1600,
            "height": 1000,
            "description": "Standard wide (1600x1000)"
        }
    ]
    
    # Create HTML template for text-heavy analysis
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Baseball Analysis - Text Focus</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #1a4f3a 0%, #2d5a27 50%, #1a4f3a 100%);
            margin: 0;
            padding: 30px;
            color: #1f2937;
            line-height: 1.6;
            box-sizing: border-box;
        }

        .analysis-container {
            width: 100%;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 30px;
            overflow: hidden;
            box-sizing: border-box;
        }

        .header {
            text-align: center;
            margin-bottom: 25px;
            border-bottom: 3px solid #1a4f3a;
            padding-bottom: 15px;
        }

        .header h1 {
            font-size: {{ header_size }}px;
            font-weight: 700;
            color: #1a4f3a;
            margin: 0 0 8px 0;
        }

        .header h2 {
            font-size: {{ subheader_size }}px;
            font-weight: 500;
            color: #4b5563;
            margin: 0;
        }

        .game-info {
            text-align: center;
            background: #f8fafc;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 25px;
            border-left: 4px solid #1a4f3a;
        }

        .game-info h3 {
            font-size: {{ game_info_size }}px;
            font-weight: 600;
            color: #1f2937;
            margin: 0 0 8px 0;
        }

        .game-info p {
            font-size: {{ text_size }}px;
            color: #6b7280;
            margin: 3px 0;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin: 20px 0;
        }

        .stat-box {
            background: #f1f5f9;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }

        .stat-box .label {
            font-size: {{ small_text_size }}px;
            color: #64748b;
            font-weight: 500;
        }

        .stat-box .value {
            font-size: {{ stat_size }}px;
            color: #1f2937;
            font-weight: 700;
            margin-top: 5px;
        }

        .recommendation-box {
            background: #dcfce7;
            border: 2px solid #16a34a;
            border-radius: 12px;
            padding: 15px;
            margin: 15px 0;
            text-align: center;
        }

        .recommendation-box h4 {
            font-size: {{ recommendation_size }}px;
            font-weight: 700;
            color: #16a34a;
            margin: 0 0 8px 0;
        }

        .analysis-content {
            font-size: {{ text_size }}px;
            line-height: 1.6;
            color: #374151;
            white-space: pre-wrap;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }

        .analysis-content strong {
            color: #1a4f3a;
            font-weight: 600;
        }
        
        @media (max-width: 1000px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="analysis-container">
        <div class="header">
            <h1>🏟️ Enhanced Chronulus Analysis</h1>
            <h2>Professional Baseball Betting Analysis</h2>
        </div>

        <div class="game-info">
            <h3>Boston Red Sox @ New York Yankees</h3>
            <p>August 24, 2025 - 7:05 PM ET | Yankee Stadium</p>
            <p>Wild Card Race vs AL East Leaders</p>
        </div>

        <div class="stats-grid">
            <div class="stat-box">
                <div class="label">Red Sox Win %</div>
                <div class="value">35.0%</div>
            </div>
            <div class="stat-box">
                <div class="label">Yankees Win %</div>
                <div class="value">65.0%</div>
            </div>
            <div class="stat-box">
                <div class="label">Confidence</div>
                <div class="value">75%</div>
            </div>
            <div class="stat-box">
                <div class="label">Model</div>
                <div class="value">Gemini 2.0</div>
            </div>
        </div>

        <div class="recommendation-box">
            <h4>🎯 RECOMMENDATION: BET HOME (Yankees)</h4>
            <p style="font-size: {{ text_size }}px; margin: 0; color: #059669;">Strong edge identified - Market Edge: -5.8%</p>
        </div>

        <div class="analysis-content">{{ analysis_text }}</div>
    </div>
</body>
</html>"""

    # Start Playwright
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        
        try:
            for config in test_configs:
                print(f"\n📊 Testing: {config['description']}")
                
                # Calculate font sizes based on image width
                base_size = max(10, config['width'] // 80)  # Scale with width
                
                template_vars = {
                    'analysis_text': expert_analysis,
                    'header_size': int(base_size * 2.2),
                    'subheader_size': int(base_size * 1.6),
                    'game_info_size': int(base_size * 1.4),
                    'text_size': int(base_size * 1.1),
                    'recommendation_size': int(base_size * 1.3),
                    'stat_size': int(base_size * 1.2),
                    'small_text_size': int(base_size * 0.9)
                }
                
                # Render template
                template = Template(html_template)
                rendered_html = template.render(**template_vars)
                
                # Create page and set viewport
                page = await browser.new_page()
                await page.set_viewport_size({
                    "width": config['width'], 
                    "height": config['height']
                })
                
                # Load HTML content
                await page.set_content(rendered_html, wait_until="networkidle")
                
                # Wait for fonts to load
                await page.wait_for_timeout(1000)
                
                # Take screenshot
                screenshot = await page.screenshot(
                    type="png",
                    full_page=True if config['height'] is None else False
                )
                
                await page.close()
                
                # Save image
                filename = f"readability_test_{config['name']}.png"
                filepath = Path(__file__).parent / filename
                
                with open(filepath, 'wb') as f:
                    f.write(screenshot)
                
                print(f"   ✅ Generated: {filename}")
                print(f"   📏 Size: {config['width']}x{config['height']}")
                print(f"   💾 File: {len(screenshot) / 1024:.1f} KB")
                print(f"   🔤 Font size: {base_size}px base (text: {int(base_size * 1.1)}px)")
                
        finally:
            await browser.close()
    
    print(f"\n🎉 Generated {len(test_configs)} test images!")
    print("\n📋 Next Steps:")
    print("1. Upload each image to Discord")
    print("2. Check which size is most readable in preview")
    print("3. Test on mobile and desktop")
    print("4. Choose the best dimensions for the final implementation")
    
    print("\n📁 Generated files:")
    for config in test_configs:
        filename = f"readability_test_{config['name']}.png"
        print(f"   • {filename} - {config['description']}")

def main():
    """Main function to run the readability tests"""
    print("🔍 Image Readability Testing for Discord")
    print("Testing different dimensions with full analysis text")
    print()
    
    # Run the async test
    asyncio.run(test_image_readability())

if __name__ == "__main__":
    main()