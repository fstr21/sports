#!/usr/bin/env python3
"""
Manual Chronulus MCP Testing Script
Optimized for cheapest tier - one call at a time with your Discord data format
"""
import asyncio
import json
import httpx
import os
import sys
from datetime import datetime
from pathlib import Path

# Add to path for .env loading
sys.path.append(str(Path(__file__).parent.parent.parent))

class ChronulusManualTester:
    """Manual tester for Chronulus MCP with your data format"""
    
    def __init__(self):
        # Load API key from .env.local
        env_file = Path(__file__).parent.parent.parent / '.env.local'
        self.api_key = self._load_env_key(env_file)
        
        if not self.api_key:
            print("❌ CHRONULUS_API_KEY not found in .env.local")
            print(f"Expected location: {env_file}")
            sys.exit(1)
        else:
            print(f"✅ API Key loaded (ending in: ...{self.api_key[-4:]})")
    
    def _load_env_key(self, env_file):
        """Load API key from .env.local file"""
        if not env_file.exists():
            return None
        
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('CHRONULUS_API_KEY='):
                        return line.split('=', 1)[1].strip().strip('"\'')
        except Exception as e:
            print(f"Error reading .env.local: {e}")
        
        return None
    
    def format_soccer_data(self):
        """Format your Alaves vs Real Betis data for Chronulus"""
        return {
            "sport": "soccer",
            "league": "LA LIGA", 
            "match": {
                "home_team": "Real Betis",
                "away_team": "Alaves",
                "kickoff": "19:30",
                "date": "2025-08-22"
            },
            "head_to_head": {
                "total_meetings": 26,
                "home_wins": 12,  # Real Betis wins (46%)
                "away_wins": 8,   # Alaves wins (31%)
                "draws": 6,
                "home_win_percentage": 0.46,
                "away_win_percentage": 0.31
            },
            "recent_form": {
                "home_team": {
                    "form": "0W-1D-0L",  # From your image: 3.3/10 
                    "description": "1 for, 1 against"
                },
                "away_team": {
                    "form": "10W-0D-0L",  # From your image: 10.0/10
                    "description": "100% win rate, 2 for, 1 against"
                }
            },
            "betting_odds": {
                "home_win": 1.93,    # Real Betis
                "draw": 3.3,
                "away_win": 4.2,     # Alaves  
                "over_2_0": 1.78,
                "under_2_1": 1.10
            },
            "goals_trend": {
                "average": 2.1,
                "tendency": "Under 2.5 goals"
            },
            "current_ai_prediction": {
                "predicted_winner": "Alaves",
                "confidence": 0.65,
                "note": "Your current system predicts Alaves Win (Strong) 65%"
            },
            "prediction_request": {
                "focus": ["match_result", "goals_total", "value_bets"],
                "confidence_threshold": 0.6,
                "comparison_with_current": True
            }
        }
    
    def format_mlb_data(self):
        """Format your Rockies @ Pirates data for Chronulus"""
        return {
            "sport": "mlb",
            "game": {
                "away_team": "Colorado Rockies",
                "home_team": "Pittsburgh Pirates", 
                "date": "2025-08-22",
                "time": "17:40 ET",
                "venue": "PNC Park"
            },
            "team_performance": {
                "away_team": {
                    "record": "37-91",
                    "win_percentage": 0.289,
                    "run_differential": -339,
                    "runs_allowed_per_game": 6.42,
                    "recent_form": "7-3 L10",
                    "recent_form_note": "Hot streak despite poor overall record"
                },
                "home_team": {
                    "record": "54-74", 
                    "win_percentage": 0.422,
                    "run_differential": -87,
                    "runs_allowed_per_game": 4.19,
                    "recent_form": "3-7 L10",
                    "recent_form_note": "Struggling recently"
                }
            },
            "betting_lines": {
                "moneyline": {
                    "away": 160,      # Rockies +160
                    "home": -190      # Pirates -190
                },
                "run_line": {
                    "away": "+1.5 (-125)",  # Rockies +1.5
                    "home": "-1.5 (+104)"   # Pirates -1.5  
                },
                "total": None  # N/A in your data
            },
            "key_players": [
                {
                    "player": "Ronny Simon",
                    "team": "away",
                    "prop": "hits_over_0.5", 
                    "odds": -360,
                    "recent_performance": {
                        "avg_hits_per_game": 0.8,
                        "games_sample": 2,
                        "trend": "average"
                    }
                },
                {
                    "player": "Nick Gonzales",
                    "team": "home",
                    "prop": "hits_over_0.5",
                    "odds": -350, 
                    "recent_performance": {
                        "avg_hits_per_game": 1.4,
                        "games_sample": 3,
                        "trend": "hot_streak",  # ⚡ in your data
                        "note": "Hot streak indicator"
                    }
                }
            ],
            "prediction_request": {
                "focus": ["game_winner", "run_line", "value_analysis"],
                "confidence_threshold": 0.65,
                "player_props_analysis": True
            }
        }
    
    async def call_chronulus_api(self, data, test_name):
        """Make actual API call to Chronulus"""
        print(f"\n🔮 Calling Chronulus API for: {test_name}")
        print("-" * 50)
        
        # This would be the actual Chronulus API endpoint
        # Replace with actual endpoint when you have it
        api_url = "https://api.chronulus.ai/v1/forecast"  # Example URL
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    json=data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ API call successful!")
                    return True, result
                else:
                    print(f"❌ API call failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return False, response.text
                    
        except Exception as e:
            print(f"❌ API call error: {e}")
            # For testing without real API, return mock data
            return self._get_mock_response(data, test_name)
    
    def _get_mock_response(self, data, test_name):
        """Mock response for testing without real API"""
        print("⚠️  Using mock response (API not available)")
        
        if data.get("sport") == "soccer":
            return True, {
                "prediction": {
                    "match_result": {
                        "home_win_probability": 0.42,    # Real Betis
                        "away_win_probability": 0.38,    # Alaves
                        "draw_probability": 0.20,
                        "confidence": 0.71
                    },
                    "goals_prediction": {
                        "total_goals_expected": 2.1,
                        "over_2_0_probability": 0.48,
                        "under_2_1_probability": 0.52
                    },
                    "value_bets": [
                        {
                            "market": "away_win", 
                            "team": "Alaves",
                            "current_odds": 4.2,
                            "fair_odds": 2.6,
                            "expected_value": 0.15,
                            "recommendation": "STRONG BET",
                            "reasoning": "Alaves recent form (100% win rate) not properly reflected in odds"
                        }
                    ],
                    "comparison_with_current": {
                        "your_prediction": "Alaves Win 65%",
                        "chronulus_prediction": "Alaves Win 38%", 
                        "agreement": "PARTIAL - Both favor underdog but different confidence"
                    },
                    "explanation": "Real Betis favored by bookmakers but Alaves' perfect recent form (10W-0D-0L) suggests strong value at 4.2 odds. Historical H2H favors Real Betis but current form is decisive factor."
                }
            }
        
        elif data.get("sport") == "mlb":
            return True, {
                "prediction": {
                    "game_result": {
                        "away_win_probability": 0.35,    # Rockies
                        "home_win_probability": 0.65,    # Pirates
                        "confidence": 0.68
                    },
                    "run_line": {
                        "away_cover_probability": 0.58,  # Rockies +1.5
                        "home_cover_probability": 0.42,  # Pirates -1.5
                        "recommendation": "Take Rockies +1.5"
                    },
                    "value_bets": [
                        {
                            "market": "moneyline",
                            "team": "Colorado Rockies", 
                            "current_odds": 160,
                            "fair_odds": 120,
                            "expected_value": 0.09,
                            "recommendation": "MODERATE BET",
                            "reasoning": "Rockies 7-3 recent form not reflected in odds"
                        }
                    ],
                    "player_props": [
                        {
                            "player": "Nick Gonzales",
                            "prop": "hits_over_0.5",
                            "probability": 0.78,
                            "current_odds": -350,
                            "fair_odds": -450,
                            "expected_value": 0.05,
                            "recommendation": "TAKE",
                            "reasoning": "Hot streak (1.4 H/G) makes this a solid play"
                        }
                    ],
                    "explanation": "Pirates favored but Rockies recent surge (7-3 L10) creates value. Key factor is Pirates recent struggles (3-7 L10) despite better overall record."
                }
            }
    
    def analyze_response(self, response, test_name):
        """Analyze and display Chronulus response"""
        print(f"\n📊 CHRONULUS ANALYSIS: {test_name}")
        print("=" * 60)
        
        prediction = response.get('prediction', {})
        
        # Match/Game Result
        if 'match_result' in prediction:
            result = prediction['match_result']
            print(f"🏆 MATCH RESULT PREDICTION:")
            print(f"   Home Win: {result.get('home_win_probability', 0):.1%}")
            print(f"   Away Win: {result.get('away_win_probability', 0):.1%}")
            print(f"   Draw: {result.get('draw_probability', 0):.1%}")
            print(f"   Confidence: {result.get('confidence', 0):.1%}")
        
        if 'game_result' in prediction:
            result = prediction['game_result']
            print(f"⚾ GAME RESULT PREDICTION:")
            print(f"   Away Win: {result.get('away_win_probability', 0):.1%}")
            print(f"   Home Win: {result.get('home_win_probability', 0):.1%}")
            print(f"   Confidence: {result.get('confidence', 0):.1%}")
        
        # Value Bets
        value_bets = prediction.get('value_bets', [])
        if value_bets:
            print(f"\n💰 VALUE BETS IDENTIFIED:")
            for bet in value_bets:
                print(f"   🎯 {bet.get('market', 'Unknown')}: {bet.get('team', 'N/A')}")
                print(f"      Current Odds: {bet.get('current_odds')}")
                print(f"      Expected Value: +{bet.get('expected_value', 0):.1%}")
                print(f"      Recommendation: {bet.get('recommendation')}")
                print(f"      Reasoning: {bet.get('reasoning', 'N/A')}")
        
        # Player Props
        player_props = prediction.get('player_props', [])
        if player_props:
            print(f"\n🎯 PLAYER PROPS ANALYSIS:")
            for prop in player_props:
                print(f"   {prop.get('player')}: {prop.get('prop')}")
                print(f"      Probability: {prop.get('probability', 0):.1%}")
                print(f"      Expected Value: +{prop.get('expected_value', 0):.1%}")
                print(f"      Recommendation: {prop.get('recommendation')}")
        
        # Explanation
        explanation = prediction.get('explanation', '')
        if explanation:
            print(f"\n📝 AI EXPLANATION:")
            print(f"   {explanation}")
        
        # Comparison (if available)
        comparison = prediction.get('comparison_with_current')
        if comparison:
            print(f"\n🔄 COMPARISON WITH YOUR SYSTEM:")
            print(f"   Your Prediction: {comparison.get('your_prediction')}")
            print(f"   Chronulus: {comparison.get('chronulus_prediction')}")
            print(f"   Agreement: {comparison.get('agreement')}")
        
        return prediction

async def main():
    """Manual testing interface"""
    print("🧪 CHRONULUS MANUAL TESTING")
    print("Optimized for cheapest tier - one call at a time")
    print("=" * 60)
    
    tester = ChronulusManualTester()
    
    print(f"\n📅 Available Tests:")
    print(f"1. Soccer: Alaves vs Real Betis (La Liga)")
    print(f"2. MLB: Rockies @ Pirates")
    print(f"3. Custom data input")
    print(f"0. Exit")
    
    while True:
        try:
            choice = input(f"\nSelect test (0-3): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                data = tester.format_soccer_data()
                success, response = await tester.call_chronulus_api(data, "Soccer - Alaves vs Real Betis")
                if success:
                    tester.analyze_response(response, "Soccer Match")
            elif choice == '2':
                data = tester.format_mlb_data()
                success, response = await tester.call_chronulus_api(data, "MLB - Rockies @ Pirates")
                if success:
                    tester.analyze_response(response, "MLB Game")
            elif choice == '3':
                print("💡 Custom data input - Edit the script to add your data")
            else:
                print("❌ Invalid choice")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())