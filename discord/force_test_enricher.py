#!/usr/bin/env python3
"""
Force test enricher by temporarily bypassing enhanced analytics check
"""
import asyncio
import os
import sys
from unittest.mock import MagicMock, patch

# Mock Discord classes
class MockDiscordChannel:
    def __init__(self, name: str):
        self.name = name
        self.id = 12345
        self.messages = []
        self.embed_count = 0
    
    async def send(self, content=None, embed=None, **kwargs):
        message = MagicMock()
        message.content = content
        message.embed = embed
        self.messages.append(message)
        if embed:
            self.embed_count += 1
            print(f"[EMBED] {embed.title or 'No Title'}")
        else:
            print(f"[TEXT] {content}")
        return message
    
    async def history(self, limit=None):
        class AsyncIterator:
            def __init__(self, items):
                self.items = items
                self.index = 0
            def __aiter__(self):
                return self
            async def __anext__(self):
                if self.index >= len(self.items):
                    raise StopAsyncIteration
                item = self.items[self.index]
                self.index += 1
                return item
        return AsyncIterator(self.messages[:limit] if limit else self.messages)

async def test_force_enricher():
    """Test enricher with mocked enhanced analytics"""
    print("Testing Soccer Channel Enricher (FORCED)...")
    
    try:
        from soccer_channel_enricher import SoccerChannelEnricher
        print("[OK] Enricher imported")
        
        # Create enricher
        enricher = SoccerChannelEnricher()
        print("[OK] Enricher initialized")
        
        # Create mock channel
        channel = MockDiscordChannel("test-osasuna-vs-real-madrid")
        print("[OK] Mock channel created")
        
        # Mock the enhanced analytics check to always return True
        original_should_use_enhanced = enricher.__class__.__dict__.get('should_use_enhanced_analytics', None)
        
        def mock_should_use_enhanced(*args):
            print("[MOCK] Forcing enhanced analytics to TRUE")
            return True
        
        # Patch the config function
        import soccer_enricher_config
        original_function = soccer_enricher_config.should_use_enhanced_analytics
        soccer_enricher_config.should_use_enhanced_analytics = mock_should_use_enhanced
        
        try:
            # Test enrichment
            print("[TEST] Running FORCED enrichment...")
            success = await enricher.enrich_channel_on_creation(
                channel=channel,
                home_team="Osasuna", 
                away_team="Real Madrid",
                match_date="2025-08-19",
                league_code="La Liga"
            )
            
            print(f"[RESULT] Enrichment: {'SUCCESS' if success else 'FAILED'}")
            print(f"[STATS] Total messages: {len(channel.messages)}")
            print(f"[STATS] Embeds sent: {channel.embed_count}")
            
            if channel.embed_count > 0:
                print("[SUCCESS] Enricher is working! Embeds were sent.")
            else:
                print("[WARNING] No embeds sent - may be fallback only")
            
            # Show stats
            stats = enricher.get_enrichment_stats()
            print(f"[STATS] Performance: {stats}")
            
            return success and channel.embed_count > 0
            
        finally:
            # Restore original function
            soccer_enricher_config.should_use_enhanced_analytics = original_function
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Set environment to bypass some checks
    os.environ['ENRICHER_CACHE_TTL'] = '10'
    
    result = asyncio.run(test_force_enricher())
    print(f"\n[FINAL] Success: {'YES' if result else 'NO'}")
    
    if result:
        print("[INFO] The enricher is working! The issue is likely just configuration.")
        print("[FIX] Try setting AUTH_KEY environment variable for full functionality.")
    else:
        print("[ERROR] There may be deeper issues with the enricher integration.")