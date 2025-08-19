#!/usr/bin/env python3
"""
Test discord import to debug the issue
"""

try:
    import discord
    print(f"Discord module imported successfully")
    print(f"Discord module path: {discord.__file__}")
    print(f"Discord module attributes: {dir(discord)}")
    
    # Try to access Embed
    if hasattr(discord, 'Embed'):
        print("discord.Embed is available")
        embed = discord.Embed(title="Test", description="Test embed")
        print(f"Embed created successfully: {embed}")
    else:
        print("discord.Embed is NOT available")
        
        # Check if it's in a submodule
        if hasattr(discord, 'embeds'):
            print("Found discord.embeds")
        if hasattr(discord, 'types'):
            print("Found discord.types")
            
except ImportError as e:
    print(f"Failed to import discord: {e}")
except Exception as e:
    print(f"Error with discord module: {e}")