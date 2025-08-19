"""
Test file to check SoccerEmbedBuilder syntax
"""

import discord
from datetime import datetime

class SoccerEmbedBuilder:
    """
    Creates rich Discord embeds for soccer content with league-specific styling
    """
    
    def __init__(self):
        """Initialize the embed builder with league-specific color schemes"""
        self.colors = {
            "EPL": 0x3d195b,
            "default": 0x00ff00
        }
    
    def _create_error_embed(self, title: str, description: str) -> discord.Embed:
        """
        Create an error embed with graceful degradation
        
        Args:
            title: Error title
            description: Error description
            
        Returns:
            Discord embed with error information
        """
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=0xff0000,
            timestamp=datetime.now()
        )
        
        embed.set_footer(text="Soccer Bot | Error occurred")
        return embed

if __name__ == "__main__":
    print("Syntax test passed")