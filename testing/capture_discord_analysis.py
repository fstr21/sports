#!/usr/bin/env python3
"""
Discord Analysis Capture Script
Captures what SHOULD appear in Discord after /create-channel mlb
Generates markdown report showing full vs truncated analysis
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
import httpx

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'mcp_leagues', 'discord_bot'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'mcp_leagues', 'discord_bot', 'sports'))

from enhanced_chronulus_integration import EnhancedChronulusIntegration

class DiscordAnalysisCapture:
    """Capture and compare Discord analysis with full analysis"""
    
    def __init__(self):
        self.mlb_mcp_url = "https://mlbmcp-production.up.railway.app/mcp"
        self.enhanced_integration = EnhancedChronulusIntegration()
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def get_sample_match_data(self):
        """Create a sample match object similar to Discord bot"""
        # Mock match object like Discord would create
        class MockMatch:
            def __init__(self):
                self.home_team = "New York Yankees"
                self.away_team = "Boston Red Sox"
                self.additional_data = {
                    "basic_game_info": {
                        "venue": "Yankee Stadium",
                        "start_et": "7:05 PM"
                    },
                    "team_forms": {
                        "home": {"wins": 82, "losses": 58, "win_percentage": 0.586},
                        "away": {"wins": 75, "losses": 65, "win_percentage": 0.536}
                    },
                    "scoring_trends": {
                        "home": {"runs_per_game": 5.21, "runs_allowed_per_game": 4.32},
                        "away": {"runs_per_game": 4.89, "runs_allowed_per_game": 4.38}
                    }
                }
        
        return MockMatch()
    
    async def get_sample_betting_odds(self):
        """Mock betting odds like Discord would get"""
        return {
            "home_moneyline": "-165",
            "away_moneyline": "+145"
        }
    
    async def capture_full_analysis(self):
        """Capture the full analysis that should appear in Discord"""
        print("DISCORD ANALYSIS CAPTURE")
        print("=" * 60)
        print("Simulating: /create-channel mlb command")
        print("Capturing: What SHOULD appear in Discord")
        print()
        
        try:
            # 1. Create mock match data (like Discord bot does)
            match = await self.get_sample_match_data()
            betting_odds = await self.get_sample_betting_odds()
            
            print(f"Analyzing: {match.away_team} @ {match.home_team}")
            print(f"Betting Odds: {betting_odds}")
            print()
            
            # 2. Call enhanced integration (exactly like Discord does)
            print("Calling Enhanced Chronulus Integration...")
            chronulus_data = await self.enhanced_integration.call_comprehensive_chronulus_analysis(
                match, betting_odds
            )
            
            if not chronulus_data:
                print("No Chronulus data received")
                return None
            
            print("Chronulus data received!")
            print(f"Data keys: {list(chronulus_data.keys())}")
            
            # 3. Create Discord embed (exactly like Discord does)
            print("\nCreating Discord Embed...")
            discord_embed = await self.enhanced_integration.create_enhanced_analysis_embed(
                match, chronulus_data
            )
            
            if not discord_embed:
                print("No Discord embed created")
                return None
            
            # 4. Extract raw analysis data
            analysis_data = None
            if chronulus_data.get("format") != "text":
                analysis_data = chronulus_data.get("analysis", {})
            
            # 5. Generate comparison report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"discord_analysis_capture_{timestamp}.md"
            filepath = os.path.join(os.path.dirname(__file__), report_file)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("# Discord Analysis Capture Report\n\n")
                f.write(f"**Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}\\n")
                f.write(f"**Purpose**: Compare what Discord shows vs full analysis\\n")
                f.write(f"**Game**: {match.away_team} @ {match.home_team}\\n\\n")
                
                f.write("---\\n\\n")
                
                # Discord Embed Simulation
                f.write("## 📱 What SHOULD Appear in Discord\\n\\n")
                
                # Simulate Discord embed fields
                f.write(f"### {discord_embed.title}\\n\\n")
                f.write(f"*{discord_embed.description}*\\n\\n")
                
                for field in discord_embed.fields:
                    f.write(f"#### {field.name}\\n\\n")
                    f.write(f"{field.value}\\n\\n")
                
                f.write(f"*{discord_embed.footer.text}*\\n\\n")
                
                # Raw Analysis Data
                if analysis_data:
                    f.write("---\\n\\n")
                    f.write("## 🔍 Raw Analysis Data (Full)\\n\\n")
                    
                    expert_analysis = analysis_data.get("expert_analysis", "")
                    if expert_analysis:
                        f.write("### Complete Expert Analysis\\n\\n")
                        f.write("```\\n")
                        f.write(expert_analysis)
                        f.write("\\n```\\n\\n")
                        
                        f.write(f"**Full Analysis Length**: {len(expert_analysis)} characters\\n\\n")
                    
                    # Other analysis details
                    f.write("### Analysis Metadata\\n\\n")
                    f.write(f"- **Away Probability**: {analysis_data.get('away_team_win_probability', 'N/A')}\\n")
                    f.write(f"- **Home Probability**: {analysis_data.get('home_team_win_probability', 'N/A')}\\n")
                    f.write(f"- **Market Edge**: {analysis_data.get('market_edge', 'N/A')}\\n")
                    f.write(f"- **Recommendation**: {analysis_data.get('betting_recommendation', 'N/A')}\\n")
                    f.write(f"- **Expert Count**: {analysis_data.get('expert_count', 'N/A')}\\n")
                    f.write(f"- **Model**: {analysis_data.get('model_used', 'N/A')}\\n")
                    f.write(f"- **Cost**: {analysis_data.get('cost_estimate', 'N/A')}\\n\\n")
                
                # Comparison Section
                f.write("---\\n\\n")
                f.write("## ⚖️ Discord vs Full Analysis Comparison\\n\\n")
                
                if analysis_data and analysis_data.get("expert_analysis"):
                    full_analysis = analysis_data["expert_analysis"]
                    
                    # Extract what Discord would show
                    discord_analysis = "Not captured"
                    for field in discord_embed.fields:
                        if "Chief Analyst" in field.name:
                            discord_analysis = field.value
                            break
                    
                    f.write("### Length Comparison\\n\\n")
                    f.write(f"- **Full Analysis**: {len(full_analysis)} characters\\n")
                    f.write(f"- **Discord Shows**: {len(discord_analysis)} characters\\n")
                    f.write(f"- **Truncated**: {len(full_analysis) - len(discord_analysis)} characters lost\\n\\n")
                    
                    f.write("### Content Comparison\\n\\n")
                    f.write("**What Discord Shows:**\\n")
                    f.write("```\\n")
                    f.write(discord_analysis)
                    f.write("\\n```\\n\\n")
                    
                    f.write("**What's Missing:**\\n")
                    if len(discord_analysis) < len(full_analysis):
                        missing_part = full_analysis[len(discord_analysis):]
                        f.write("```\\n")
                        f.write(missing_part[:500] + ("..." if len(missing_part) > 500 else ""))
                        f.write("\\n```\\n\\n")
                    else:
                        f.write("*Nothing missing - Discord shows full analysis*\\n\\n")
                
                # Comprehensive Game Data Used
                f.write("---\\n\\n")
                f.write("## 📋 Comprehensive Game Data Sent to Chronulus\\n\\n")
                
                # Show what data was sent
                comprehensive_data = await self.enhanced_integration.create_comprehensive_game_data_like_test_script(
                    match, betting_odds
                )
                
                f.write("### Game Data Structure\\n\\n")
                f.write("```json\\n")
                f.write(json.dumps(comprehensive_data, indent=2))
                f.write("\\n```\\n\\n")
                
                if comprehensive_data.get("additional_context"):
                    f.write("### Additional Context (The Rich Data)\\n\\n")
                    f.write("```\\n")
                    f.write(comprehensive_data["additional_context"])
                    f.write("\\n```\\n\\n")
                    
                    f.write(f"**Context Length**: {len(comprehensive_data['additional_context'])} characters\\n\\n")
                
                # Footer
                f.write("---\\n\\n")
                f.write("*This report shows exactly what Discord should display vs what the full Custom Chronulus analysis contains. Use this to identify where analysis is being truncated or lost.*\\n")
            
            print(f"\\nDISCORD ANALYSIS CAPTURE COMPLETE")
            print("=" * 60)
            print(f"Report saved: {filepath}")
            print(f"\\nQuick Summary:")
            if analysis_data and analysis_data.get("expert_analysis"):
                full_len = len(analysis_data["expert_analysis"])
                print(f"Full Analysis: {full_len} characters")
                
                # Check Discord field
                discord_len = 0
                for field in discord_embed.fields:
                    if "Chief Analyst" in field.name:
                        discord_len = len(field.value)
                        break
                
                print(f"Discord Shows: {discord_len} characters")
                print(f"Lost: {full_len - discord_len} characters ({((full_len - discord_len) / full_len * 100):.1f}%)")
            
            return filepath
            
        except Exception as e:
            print(f"Error capturing analysis: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            await self.client.aclose()

async def main():
    """Run the Discord analysis capture"""
    print("DISCORD ANALYSIS CAPTURE SCRIPT")
    print("This simulates /create-channel mlb and shows what SHOULD appear")
    print("=" * 70)
    
    capture = DiscordAnalysisCapture()
    result = await capture.capture_full_analysis()
    
    if result:
        print(f"\\nSUCCESS!")
        print(f"Analysis captured and saved to: {result}")
        print(f"\\nThis shows exactly what Discord displays vs the full analysis.")
        print(f"Use this to debug truncation issues!")
    else:
        print(f"\\nFAILED to capture analysis")

if __name__ == "__main__":
    asyncio.run(main())