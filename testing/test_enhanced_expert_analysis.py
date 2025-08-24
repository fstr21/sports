#!/usr/bin/env python3
"""
Test Enhanced Expert Analysis Improvements

This script tests the improved user-friendly expert analysis format
to ensure the new structure and conversational style are working.
"""

import asyncio
import json
import httpx
from datetime import datetime

async def test_enhanced_expert_analysis():
    """Test the enhanced expert analysis with improved formatting"""
    
    print("🧪 TESTING ENHANCED EXPERT ANALYSIS")
    print("=" * 60)
    
    # Test game data with pitcher context
    game_data = {
        "home_team": "Los Angeles Dodgers (86-57, 1st NL West)",
        "away_team": "San Diego Padres (78-65, 2nd NL West)",
        "venue": "Dodger Stadium, Los Angeles, CA",
        "game_date": "2025-08-24",
        "home_record": "86-57",
        "away_record": "78-65",
        "home_moneyline": -145,
        "away_moneyline": 125,
        "additional_context": "Division rivalry game. Starting Pitchers: Clayton Kershaw (LAD) - 3.21 ERA, 1.15 WHIP, 9.8 K/9 vs Yu Darvish (SD) - 4.05 ERA, 1.32 WHIP, 8.4 K/9. Kershaw has dominated SD historically with 2.45 ERA in career starts."
    }
    
    payload = {
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
            response = await client.post(
                "https://customchronpredictormcp-production.up.railway.app/mcp", 
                json=payload
            )\n            response.raise_for_status()\n            result = response.json()\n            \n            if \"result\" in result:\n                content = result[\"result\"][\"content\"][0][\"text\"]\n                analysis_data = json.loads(content)\n                \n                print(\"✅ Enhanced Analysis Retrieved Successfully!\")\n                print(f\"📊 Away Team Win Probability: {analysis_data.get('analysis', {}).get('away_team_win_probability', 0):.1%}\")\n                print(f\"👥 Expert Count: {analysis_data.get('analysis', {}).get('expert_count', 0)}\")\n                \n                # Extract and display expert analysis\n                expert_text = analysis_data.get('analysis', {}).get('expert_analysis', '')\n                \n                print(\"\\n📋 EXPERT ANALYSIS QUALITY CHECK:\")\n                print(\"-\" * 50)\n                \n                # Check for improved formatting elements\n                formatting_checks = {\n                    \"Opening Stance sections\": \"OPENING STANCE\" in expert_text.upper() or \"opening stance\" in expert_text.lower(),\n                    \"Key Supporting Factors\": \"KEY SUPPORTING FACTORS\" in expert_text.upper() or \"supporting factors\" in expert_text.lower(),\n                    \"Main Risk/Concern\": \"MAIN RISK\" in expert_text.upper() or \"risk\" in expert_text.lower(),\n                    \"Bottom Line sections\": \"BOTTOM LINE\" in expert_text.upper() or \"bottom line\" in expert_text.lower(),\n                    \"Bullet points usage\": \"•\" in expert_text or \"-\" in expert_text,\n                    \"Conversational tone\": any(phrase in expert_text.lower() for phrase in [\"i think\", \"here's\", \"let's\", \"you'll\", \"we need\"]),\n                    \"Plain language explanations\": \"(\" in expert_text and \")\" in expert_text,  # Parenthetical explanations\n                    \"Clear structure\": len(expert_text.split(\"\\n\\n\")) > 5  # Multiple paragraphs\n                }\n                \n                for check, passed in formatting_checks.items():\n                    status = \"✅\" if passed else \"❌\"\n                    print(f\"  {status} {check}: {'FOUND' if passed else 'MISSING'}\")\n                \n                # Display sample expert analysis\n                print(\"\\n📖 SAMPLE EXPERT ANALYSIS:\")\n                print(\"-\" * 50)\n                \n                # Show first 500 characters to verify formatting\n                sample_text = expert_text[:800] + \"...\" if len(expert_text) > 800 else expert_text\n                print(sample_text)\n                \n                # Quality assessment\n                passed_checks = sum(formatting_checks.values())\n                total_checks = len(formatting_checks)\n                quality_score = (passed_checks / total_checks) * 100\n                \n                print(f\"\\n🏆 FORMATTING QUALITY SCORE: {quality_score:.1f}% ({passed_checks}/{total_checks} checks passed)\")\n                \n                if quality_score >= 75:\n                    print(\"🎉 EXCELLENT! Enhanced formatting is working well.\")\n                elif quality_score >= 50:\n                    print(\"⚠️ GOOD! Some improvements detected, but room for enhancement.\")\n                else:\n                    print(\"❌ NEEDS WORK! Formatting improvements may need adjustment.\")\n                \n                # Save full analysis for review\n                timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n                filename = f\"enhanced_analysis_test_{timestamp}.json\"\n                \n                with open(filename, 'w') as f:\n                    json.dump({\n                        \"timestamp\": datetime.now().isoformat(),\n                        \"formatting_checks\": formatting_checks,\n                        \"quality_score\": quality_score,\n                        \"full_analysis\": analysis_data\n                    }, f, indent=2)\n                \n                print(f\"💾 Full analysis saved to: {filename}\")\n                \n            else:\n                print(f\"❌ API Error: {result}\")\n                \n    except Exception as e:\n        print(f\"❌ Test failed: {e}\")\n\nif __name__ == \"__main__\":\n    asyncio.run(test_enhanced_expert_analysis())