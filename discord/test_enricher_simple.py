#!/usr/bin/env python3
"""
Simple test to verify enricher is working
"""
import asyncio
import os
import sys
from unittest.mock import MagicMock
import discord

# Mock Discord classes
class MockDiscordChannel:
    def __init__(self, name: str):
        self.name = name
        self.id = 12345
        self.messages = []
    
    async def send(self, content=None, embed=None, **kwargs):
        message = MagicMock()
        message.content = content
        message.embed = embed
        self.messages.append(message)
        print(f"[CHANNEL] Sent message: {embed.title if embed else content}")
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

async def test_enricher():
    """Test enricher functionality"""
    print("Testing Soccer Channel Enricher...")
    
    try:
        from soccer_channel_enricher import SoccerChannelEnricher
        print("[OK] Enricher imported successfully")
        
        # Create enricher
        enricher = SoccerChannelEnricher()
        print("[OK] Enricher initialized")
        
        # Create mock channel
        channel = MockDiscordChannel("test-osasuna-vs-real-madrid")
        print("[OK] Mock channel created")
        
        # Test enrichment
        print("[TEST] Running enrichment...")
        success = await enricher.enrich_channel_on_creation(
            channel=channel,
            home_team="Osasuna", 
            away_team="Real Madrid",
            match_date="2025-08-19",
            league_code="La Liga"
        )
        
        print(f"[RESULT] Enrichment completed: {'SUCCESS' if success else 'FAILED'}")
        print(f"[INFO] Messages sent to channel: {len(channel.messages)}")
        
        # Show what was sent
        for i, msg in enumerate(channel.messages, 1):
            if msg.embed:
                print(f"  {i}. EMBED: {msg.embed.title}")
            else:
                print(f"  {i}. TEXT: {msg.content[:50]}...")
        
        # Get stats
        stats = enricher.get_enrichment_stats()
        print(f"[STATS] Enricher Stats: {stats}")
        
        return success
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_enricher())
    print(f"\n[FINAL] Result: {'PASS' if result else 'FAIL'}")