#!/usr/bin/env python3
"""
Test Real Chronulus Service vs Custom Implementation
Athletics @ Seattle Mariners - August 23, 2025
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path to access .env.local
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.local')

# Real Chronulus imports
try:
    from chronulus import Session, BinaryPredictor, GameData
    chronulus_available = True
    print("✅ Real Chronulus SDK imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Chronulus SDK: {e}")
    chronulus_available = False

def create_game_data():
    """Create GameData object for Athletics @ Seattle Mariners from screenshot data"""
    
    # Hard-coded data from chrome_64sxt2O9sA.png screenshot
    # Shows: Athletics (+1.5 +122, O 8 -110, +143) vs SEA Mariners (-1.5 +122, U 8 -111, -175)
    game_data = GameData(
        home_team="SEA Mariners",
        away_team="Athletics", 
        sport="Baseball",
        venue="T-Mobile Park",
        game_date="August 23, 2025",
        home_record="Home team record",
        away_record="Away team record",
        home_moneyline=-175,  # SEA Mariners favored (from screenshot)
        away_moneyline=+143,  # Athletics underdog (from screenshot)
        additional_context=(
            "Hard-coded game data from screenshot: "
            "Athletics: Moneyline +143, Run Line +1.5 (+122), Over 8 (-110). "
            "SEA Mariners: Moneyline -175, Run Line -1.5 (+122), Under 8 (-111). "
            "Game at 9:40 PM. Screenshot shows Jeffrey Springs and George Kirby as key players. "
            "This is real betting market data for testing Chronulus integration accuracy."
        )
    )
    
    return game_data

async def test_real_chronulus():
    """Test real Chronulus service with 2 agents"""
    
    if not chronulus_available:
        print("❌ Chronulus SDK not available")
        return None
    
    api_key = os.getenv("CHRONULUS_API_KEY")
    if not api_key:
        print("❌ CHRONULUS_API_KEY not found in environment")
        return None
    
    print(f"🔑 Using Chronulus API key: {api_key[:8]}**********************")
    
    try:
        # Create game data
        game_data = create_game_data()
        
        print("\n📊 GAME DATA FOR REAL CHRONULUS:")
        print("=" * 50)
        print(f"Matchup: {game_data.away_team} @ {game_data.home_team}")
        print(f"Venue: {game_data.venue}")
        print(f"Date: {game_data.game_date}")
        print(f"Away Record: {game_data.away_record}")
        print(f"Home Record: {game_data.home_record}")
        print(f"Moneylines: Away {game_data.away_moneyline:+d}, Home {game_data.home_moneyline:+d}")
        print(f"Context: {game_data.additional_context[:200]}...")
        
        # Create Chronulus session
        print(f"\n🚀 Creating Real Chronulus Session...")
        session = Session.create(
            name="Athletics @ Seattle Mariners Analysis",
            situation="You're analyzing this MLB game for professional sports betting",
            task="Provide detailed expert analysis focusing on win probability, value betting opportunities, and key factors"
        )
        print(f"✅ Session created: {session.name}")
        
        # Create binary predictor
        print(f"\n🤖 Creating Real Chronulus Binary Predictor...")
        predictor = BinaryPredictor.create(session=session, input_type=GameData)
        print(f"✅ Predictor created for binary outcome prediction")
        
        # Queue prediction with 2 experts as requested
        print(f"\n🧠 Queuing prediction with 2 expert agents...")
        request = await predictor.queue(
            item=game_data,
            num_experts=2,  # As requested
            note_length=(8, 12)  # Standard depth analysis
        )
        print(f"✅ Prediction queued with request ID: {request.request_id}")
        
        # Get results
        print(f"\n⏳ Waiting for Real Chronulus analysis...")
        result = await request.result()
        print(f"✅ Analysis completed!")
        
        # Extract key information
        print(f"\n📈 REAL CHRONULUS RESULTS:")
        print("=" * 50)
        print(f"Away Team (Athletics) Win Probability: {result.prob_a:.1%}")
        print(f"Home Team (Seattle) Win Probability: {(1-result.prob_a):.1%}")
        print(f"Expert Count: {result.expert_count}")
        print(f"Beta Parameters: α={result.beta_params.alpha:.2f}, β={result.beta_params.beta:.2f}")
        
        # Display full expert analysis
        print(f"\n📝 EXPERT ANALYSIS TEXT:")
        print("=" * 70)
        print(result.text)
        print("=" * 70)
        
        return {
            "service": "Real Chronulus",
            "away_win_prob": result.prob_a,
            "home_win_prob": 1 - result.prob_a,
            "expert_count": result.expert_count,
            "analysis_text": result.text,
            "beta_params": {
                "alpha": result.beta_params.alpha,
                "beta": result.beta_params.beta,
                "mean": result.beta_params.mean(),
                "variance": result.beta_params.variance()
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Real Chronulus error: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_results_to_markdown(real_results, custom_results=None):
    """Save comparison results to markdown file"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"C:/Users/fstr2/Desktop/sports/chronulus/results/chronulus_comparison_{timestamp}.md"
    
    # Ensure results directory exists
    os.makedirs("C:/Users/fstr2/Desktop/sports/chronulus/results", exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Chronulus Service Comparison\n\n")
        f.write(f"**Game**: Athletics @ Seattle Mariners\n")
        f.write(f"**Date**: August 23, 2025, 9:40 PM ET\n")
        f.write(f"**Venue**: T-Mobile Park\n")
        f.write(f"**Betting Lines**: Athletics +144, Seattle Mariners -172\n")
        f.write(f"**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Game Context\n\n")
        f.write("**Athletics (59-71, .454)**\n")
        f.write("- Record: 59-71 (.454 win%)\n")
        f.write("- Run Differential: -86\n")
        f.write("- Allowed/Game: 5.17\n")
        f.write("- L10 Form: 6-4\n\n")
        
        f.write("**Seattle Mariners (69-60, .535)**\n")
        f.write("- Record: 69-60 (.535 win%)\n")
        f.write("- Run Differential: +16\n") 
        f.write("- Allowed/Game: 4.41\n")
        f.write("- L10 Form: 3-7\n\n")
        
        f.write("**Betting Market**\n")
        f.write("- Moneyline: Athletics +144, Seattle Mariners -172\n")
        f.write("- Run Line: Athletics +1.5 (-142), Seattle -1.5 (+118)\n")
        f.write("- Total: Over 8.0 (-110), Under 8.0 (-110)\n\n")
        
        if real_results:
            f.write("## Real Chronulus Analysis\n\n")
            f.write(f"**Win Probabilities**\n")
            f.write(f"- Athletics: {real_results['away_win_prob']:.1%}\n")
            f.write(f"- Seattle Mariners: {real_results['home_win_prob']:.1%}\n\n")
            f.write(f"**Expert Count**: {real_results['expert_count']}\n\n")
            f.write(f"**Beta Distribution**\n")
            f.write(f"- Alpha: {real_results['beta_params']['alpha']:.2f}\n")
            f.write(f"- Beta: {real_results['beta_params']['beta']:.2f}\n")
            f.write(f"- Mean: {real_results['beta_params']['mean']:.3f}\n")
            f.write(f"- Variance: {real_results['beta_params']['variance']:.6f}\n\n")
            f.write(f"**Expert Analysis**\n")
            f.write("```\n")
            f.write(real_results['analysis_text'])
            f.write("\n```\n\n")
        
        if custom_results:
            f.write("## Custom Chronulus Analysis\n\n")
            f.write(f"**Win Probabilities**\n")
            f.write(f"- Athletics: {custom_results['away_win_prob']:.1%}\n")
            f.write(f"- Seattle Mariners: {custom_results['home_win_prob']:.1%}\n\n")
            f.write(f"**Expert Count**: {custom_results['expert_count']}\n\n")
            f.write(f"**Expert Analysis**\n")
            f.write("```\n")
            f.write(custom_results['analysis_text'])
            f.write("\n```\n\n")
        
        f.write("## Comparison Summary\n\n")
        if real_results and custom_results:
            real_away = real_results['away_win_prob']
            custom_away = custom_results['away_win_prob']
            prob_diff = abs(real_away - custom_away)
            
            f.write(f"**Probability Difference**: {prob_diff:.1%}\n")
            f.write(f"**Analysis Quality**: {'Very Similar' if prob_diff < 0.05 else 'Different Approaches' if prob_diff < 0.15 else 'Significantly Different'}\n")
            f.write(f"**Cost Comparison**: Real Chronulus ~$0.75-1.50 vs Custom ~$0.06-0.15 (90% savings)\n\n")
        
        f.write("---\n")
        f.write("*Generated for sports analysis platform comparison*\n")
    
    print(f"📄 Results saved to: {filename}")
    return filename

if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("🏟️ REAL CHRONULUS vs CUSTOM CHRONULUS COMPARISON")
        print("Game: Athletics @ Seattle Mariners")
        print("=" * 60)
        
        # Test real Chronulus
        real_results = await test_real_chronulus()
        
        # Save results
        results_file = save_results_to_markdown(real_results)
        
        print(f"\n✅ Comparison complete!")
        print(f"📄 Results saved to: {results_file}")
        print(f"\n🎯 Use this to compare with your Custom Chronulus implementation")
        print(f"💰 Expected: ~90% cost savings with similar analysis quality")
    
    asyncio.run(main())