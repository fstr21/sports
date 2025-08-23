#!/usr/bin/env python3
"""
Manual Chronulus Test Script
Athletics @ Seattle Mariners - August 23, 2025
Run this manually to test real Chronulus service
"""
import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field

# Add parent directory to path to access .env.local
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from parent directory
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env.local'
load_dotenv(env_path)

# Real Chronulus imports
try:
    from chronulus import Session
    from chronulus.estimator import BinaryPredictor
    print("✅ Chronulus SDK imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Chronulus SDK: {e}")
    print("Run: pip install chronulus")
    sys.exit(1)

# Game data model
class GameData(BaseModel):
    home_team: str = Field(description="Home team with context")
    away_team: str = Field(description="Away team with context")
    sport: str = Field(default="Baseball")
    venue: str = Field(description="Venue with context")
    game_date: str = Field(description="Game date")
    home_record: str = Field(description="Home team season record")
    away_record: str = Field(description="Away team season record")
    home_moneyline: int = Field(description="Home team moneyline odds")
    away_moneyline: int = Field(description="Away team moneyline odds")
    additional_context: str = Field(default="", description="Additional game context")

def create_game_data():
    """Create GameData for Athletics @ Seattle Mariners"""
    return GameData(
        home_team="Seattle Mariners (69-60, .535 win%, T-Mobile Park home advantage)",
        away_team="Athletics (59-71, .454 win%, road underdog with recent form)",
        sport="Baseball",
        venue="T-Mobile Park (Seattle home field advantage, evening game atmosphere)",
        game_date="August 23, 2025",
        home_record="69-60 (.535 win percentage, +16 run differential, struggling 3-7 L10)",
        away_record="59-71 (.454 win percentage, -86 run differential, improving 6-4 L10)",
        home_moneyline=-172,  # Seattle heavily favored
        away_moneyline=+144,  # Athletics significant underdog
        additional_context=(
            "LATE SEASON MLB GAME - August 23, 2025, 9:40 PM ET. "
            "TEAM STATS: "
            "Athletics: 59-71 record (.454), -86 run differential, 5.17 runs allowed/game, 6-4 in last 10. "
            "Seattle Mariners: 69-60 record (.535), +16 run differential, 4.41 runs allowed/game, 3-7 in last 10. "
            "BETTING MARKET: Athletics +144 (implied 40.9% win prob), Seattle -172 (implied 63.2% win prob). "
            "RUN LINE: Athletics +1.5 (-142), Seattle -1.5 (+118). "
            "TOTAL: Over/Under 8.0 runs (-110/-110). "
            "SITUATIONAL FACTORS: Seattle at home but struggling lately (3-7 L10), Athletics playing better recently (6-4 L10). "
            "PLAYOFF CONTEXT: Late season game with potential playoff implications for Seattle."
        )
    )

async def run_chronulus_analysis():
    """Run Chronulus analysis manually"""
    
    # Check API key
    api_key = os.getenv("CHRONULUS_API_KEY")
    if not api_key:
        print("❌ CHRONULUS_API_KEY not found in .env.local")
        print("Add: CHRONULUS_API_KEY=your-key-here")
        return
    
    print(f"✅ API Key loaded: {api_key[:8]}****")
    
    # Create game data
    game_data = create_game_data()
    
    print("\n📊 GAME DATA:")
    print("=" * 50)
    print(f"🏟️  {game_data.away_team} @ {game_data.home_team}")
    print(f"📅 {game_data.game_date}")
    print(f"💰 Odds: Away {game_data.away_moneyline:+d}, Home {game_data.home_moneyline:+d}")
    print(f"📈 Records: Away {game_data.away_record}")
    print(f"📈 Records: Home {game_data.home_record}")
    
    try:
        # Create session
        print(f"\n🔄 Creating Chronulus Session...")
        session = Session(
            name="Manual Athletics @ Seattle Analysis",
            situation="Professional MLB betting analysis with real market odds",
            task="Provide expert analysis with win probabilities and betting recommendations",
            env=dict(CHRONULUS_API_KEY=api_key)
        )
        session.create()
        print(f"✅ Session created: {session.session_id}")
        
        # Create predictor
        print(f"\n🤖 Creating Binary Predictor...")
        predictor = BinaryPredictor(session=session, input_type=GameData)
        predictor.create()
        print(f"✅ Predictor created")
        
        # Queue prediction
        print(f"\n⏳ Queuing prediction with 2 experts...")
        queue_response = predictor.queue(
            item=game_data,
            num_experts=2,
            note_length=(12, 18)  # Detailed analysis
        )
        print(f"✅ Queued - Request ID: {queue_response.request_id}")
        print(f"📋 Prediction IDs: {queue_response.prediction_ids}")
        
        # Wait for results
        print(f"\n⌛ Waiting for analysis (2-5 minutes)...")
        print("Progress: ", end="", flush=True)
        
        max_wait = 300  # 5 minutes
        wait_time = 0
        
        while wait_time < max_wait:
            try:
                predictions = predictor.get_request_predictions(queue_response.request_id)
                
                if predictions and len(predictions) > 0:
                    completed = [p for p in predictions if getattr(p, 'status', '') == 'completed']
                    
                    if completed:
                        result = completed[0]
                        print(f"\n✅ Analysis complete!")
                        break
                    else:
                        print(".", end="", flush=True)
                        await asyncio.sleep(15)
                        wait_time += 15
                else:
                    print(".", end="", flush=True)
                    await asyncio.sleep(15)
                    wait_time += 15
                    
            except Exception as e:
                print(f"\n⚠️  Error checking: {e}")
                await asyncio.sleep(15)
                wait_time += 15
        
        if wait_time >= max_wait:
            print(f"\n❌ Timeout after {max_wait/60:.1f} minutes")
            return
        
        # Display results
        print(f"\n" + "=" * 60)
        print(f"🏆 CHRONULUS ANALYSIS RESULTS")
        print(f"=" * 60)
        print(f"🎯 Athletics Win Probability: {result.prob_a:.1%}")
        print(f"🎯 Seattle Win Probability: {(1-result.prob_a):.1%}")
        print(f"👥 Expert Count: {result.expert_count}")
        print(f"📝 Analysis Length: {len(result.text)} characters")
        
        # Check for real odds
        if "+144" in result.text or "-172" in result.text:
            print("✅ Real odds found in analysis!")
        else:
            print("⚠️  Real odds not clearly referenced")
        
        print(f"\n📄 FULL EXPERT ANALYSIS:")
        print("=" * 70)
        print(result.text)
        print("=" * 70)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:/Users/fstr2/Desktop/sports/testing/chronulus_manual_test_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Manual Chronulus Test Results - {datetime.now()}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Game: {game_data.away_team} @ {game_data.home_team}\n")
            f.write(f"Date: {game_data.game_date}\n")
            f.write(f"Odds: Away {game_data.away_moneyline:+d}, Home {game_data.home_moneyline:+d}\n\n")
            f.write(f"Results:\n")
            f.write(f"- Athletics Win Probability: {result.prob_a:.1%}\n")
            f.write(f"- Seattle Win Probability: {(1-result.prob_a):.1%}\n")
            f.write(f"- Expert Count: {result.expert_count}\n")
            f.write(f"- Cost: ~$0.75-1.50\n\n")
            f.write(f"Full Analysis:\n")
            f.write("-" * 40 + "\n")
            f.write(result.text)
            f.write("\n" + "-" * 40 + "\n")
        
        print(f"\n💾 Results saved to: {filename}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 MANUAL CHRONULUS TEST")
    print("Game: Athletics @ Seattle Mariners")
    print("Run this script manually to test real Chronulus service")
    print("")
    
    asyncio.run(run_chronulus_analysis())