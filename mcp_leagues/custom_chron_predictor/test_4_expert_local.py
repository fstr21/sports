#!/usr/bin/env python3
"""
Quick test of the updated 4-expert functionality
"""
import asyncio
import json
from custom_chronulus_mcp_server import (
    CustomBinaryPredictor, 
    CustomChronulusSession, 
    GameData
)

async def test_multi_expert():
    """Test that 4 experts actually work now"""
    print("🧪 Testing Updated 4-Expert Functionality")
    print("=" * 50)
    
    # Test game data
    game_data = GameData(
        home_team="New York Yankees",
        away_team="Boston Red Sox",
        venue="Yankee Stadium", 
        game_date="August 25, 2025",
        home_record="82-58 (.586)",
        away_record="75-65 (.536)", 
        home_moneyline=-165,
        away_moneyline=145,
        additional_context="AL East rivalry game"
    )
    
    # Create session and predictor
    session = CustomChronulusSession(
        name="Test 4-Expert Analysis",
        situation="Testing multi-expert functionality",
        task="Generate 4-expert analysis"
    )
    
    predictor = CustomBinaryPredictor(session=session, input_type=GameData)
    
    # Test with 4 experts
    print("📊 Testing 4 experts...")
    try:
        request = await predictor.queue(
            item=game_data,
            num_experts=4,  # Should now work!
            note_length=(4, 5)
        )
        
        result = request.result
        
        print(f"✅ Expert Count: {result.expert_count}")
        print(f"✅ Analysis Length: {len(result.text):,} characters")
        print(f"✅ Away Win Probability: {result.prob_a:.1%}")
        print(f"✅ Request ID: {request.request_id}")
        
        # Check if we got multiple expert sections
        expert_markers = [
            "[STATISTICAL EXPERT]",
            "[SITUATIONAL EXPERT]", 
            "[CONTRARIAN EXPERT]",
            "[SHARP EXPERT]",
            "[MARKET EXPERT]"
        ]
        
        found_experts = []
        for marker in expert_markers:
            if marker in result.text:
                found_experts.append(marker.replace("[", "").replace("]", ""))
        
        print(f"✅ Expert Sections Found: {len(found_experts)}")
        print(f"✅ Expert Types: {', '.join(found_experts)}")
        
        if result.expert_count >= 4:
            print("\n🎉 SUCCESS: 4-Expert functionality is working!")
            return True
        else:
            print(f"\n❌ STILL LIMITED: Only {result.expert_count} expert(s) returned")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_single_expert():
    """Test that single expert still works"""
    print("\n📊 Testing 1 expert (backward compatibility)...")
    
    game_data = GameData(
        home_team="New York Yankees",
        away_team="Boston Red Sox",
        venue="Yankee Stadium",
        game_date="August 25, 2025",
        home_record="82-58",
        away_record="75-65",
        home_moneyline=-165,
        away_moneyline=145
    )
    
    session = CustomChronulusSession(
        name="Test Single Expert",
        situation="Testing single expert mode",
        task="Generate single expert analysis"
    )
    
    predictor = CustomBinaryPredictor(session=session, input_type=GameData)
    
    try:
        request = await predictor.queue(
            item=game_data,
            num_experts=1,
            note_length=(4, 5)
        )
        
        result = request.result
        
        print(f"✅ Expert Count: {result.expert_count}")
        print(f"✅ Analysis Length: {len(result.text):,} characters")
        
        if result.expert_count == 1:
            print("✅ Single expert mode working correctly")
            return True
        else:
            print(f"❌ Expected 1 expert, got {result.expert_count}")
            return False
            
    except Exception as e:
        print(f"❌ Single expert test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("Custom Chronulus MCP Server - Multi-Expert Test")
    print("Testing the updated server functionality locally")
    print()
    
    # Test both modes
    multi_expert_success = await test_multi_expert()
    single_expert_success = await test_single_expert()
    
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    if multi_expert_success:
        print("✅ 4-Expert Analysis: WORKING")
        print("🎯 Ready for Discord bot integration")
    else:
        print("❌ 4-Expert Analysis: NOT WORKING")
        print("🔍 Needs further debugging")
    
    if single_expert_success:
        print("✅ Single Expert Analysis: WORKING")
    else:
        print("❌ Single Expert Analysis: BROKEN")
    
    if multi_expert_success and single_expert_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("The updated MCP server is ready for deployment")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("Review the errors above before deploying")

if __name__ == "__main__":
    asyncio.run(main())