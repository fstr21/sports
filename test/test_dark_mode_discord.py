#!/usr/bin/env python3
"""
Quick test of dark mode template integration for Discord
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add Discord bot directory to path
discord_bot_path = Path(__file__).parent.parent / "mcp_leagues" / "discord_bot"
sys.path.insert(0, str(discord_bot_path))

async def test_dark_mode_discord():
    """Test the dark mode template through Discord bot utils"""
    
    print("Testing Dark Mode Discord Integration")
    print("=" * 40)
    
    try:
        # Import Discord bot function
        from utils.html_to_image import create_dark_enhanced_hybrid_analysis_image
        
        # Sample template data matching Discord bot format
        template_data = {
            'away_team': 'Boston Red Sox',
            'home_team': 'New York Yankees', 
            'game_date': 'August 24, 2025 - 7:05 PM ET',
            'venue_name': 'Yankee Stadium',
            'away_status': 'Wild Card Race',
            'home_status': 'AL East Leaders',
            'away_prob': '35.0',
            'home_prob': '65.0',
            'recommendation_short': 'BET YANKEES',
            'model_name': 'Gemini 2.0',
            'confidence': '75%',
            'market_edge': '-5.8%',
            'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p ET'),
            'expert_analysis': '''**MARKET BASELINE**: The current moneyline implies approximately 40.8% probability for the Boston Red Sox and 62.3% for the New York Yankees.

**KEY FACTORS FROM DATA**: The Yankees' +89 run differential compared to the Red Sox's +42 indicates a stronger overall team. The pitching matchup of Gerrit Cole (3.41 ERA) versus Brayan Bello (4.15 ERA) favors the Yankees, given Cole's lower ERA, WHIP of 1.09, and higher strikeout rate.

**FINAL ASSESSMENT**: Win Probability: 35.0% (Boston Red Sox), 65.0% (New York Yankees). Analyst Confidence: 75%. Recommendation: BET HOME - Strong edge identified'''
        }
        
        print("Step 1: Testing dark mode image generation...")
        
        # Generate dark mode image using Discord bot function
        image_bytes = await create_dark_enhanced_hybrid_analysis_image(template_data)
        
        print(f"Step 2: Dark mode image generated successfully!")
        print(f"         Size: {len(image_bytes) / 1024:.1f} KB")
        
        # Save test image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_file = Path(__file__).parent / f"discord_dark_mode_test_{timestamp}.png"
        
        with open(image_file, 'wb') as f:
            f.write(image_bytes)
        
        print(f"Step 3: Test image saved - {image_file.name}")
        
        print("\n✅ DARK MODE DISCORD INTEGRATION TEST SUCCESSFUL!")
        print("The Discord bot is ready to use the dark mode design.")
        print("\nAvailable Discord Commands:")
        print("• /textonly - Uses dark mode by default now")
        print("• /darkmode - Dedicated dark mode showcase")
        print("• /comparedesigns - Compare all design modes")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Dark Mode Discord Integration Test")
    print("Testing the new dark enhanced template")
    print()
    
    success = asyncio.run(test_dark_mode_discord())
    
    if success:
        print(f"\n🎉 Ready for Discord deployment!")
        print("The dark mode enhanced design is working correctly.")
    else:
        print(f"\n💥 Fix errors before Discord deployment.")

if __name__ == "__main__":
    main()