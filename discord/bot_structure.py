# Discord Bot Structure - Foundation Code
"""
Sports Betting Discord Bot - Core Structure
Implements category-based league organization with game-specific channels
"""

import discord
from discord.ext import commands
from typing import Dict, List, Optional
import asyncio
from datetime import datetime, timedelta

# Bot configuration
BOT_TOKEN = "your-bot-token-here"  # Store in environment variables
COMMAND_PREFIX = "/"

class SportsBot(commands.Bot):
    """Main bot class with sports betting focus"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        
        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            description="Sports Betting Analytics Bot"
        )
        
        # Category and channel tracking
        self.league_categories: Dict[str, discord.CategoryChannel] = {}
        self.game_channels: Dict[str, discord.TextChannel] = {}
        
        # League configurations
        self.leagues = {
            "NFL": {
                "emoji": "🏈",
                "active": False,  # Will be True when season starts
                "channels_per_week": 16
            },
            "MLB": {
                "emoji": "⚾",
                "active": True,
                "channels_per_day": 15
            },
            "SOCCER": {
                "emoji": "⚽",
                "active": True,
                "channels_per_day": 10
            },
            "NBA": {
                "emoji": "🏀",
                "active": False,  # Future season
                "channels_per_day": 12
            },
            "NHL": {
                "emoji": "🏒",
                "active": False,  # Future season
                "channels_per_day": 12
            }
        }

    async def on_ready(self):
        """Bot startup - initialize server structure"""
        print(f'{self.user} has connected to Discord!')
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
            
        # Initialize server structure
        await self.setup_server_structure()

    async def setup_server_structure(self):
        """Create league categories and basic structure"""
        guild = self.guilds[0] if self.guilds else None
        if not guild:
            print("Bot not connected to any guilds")
            return
            
        print(f"Setting up server structure for {guild.name}")
        
        # Create league categories
        for league, config in self.leagues.items():
            category_name = f"{config['emoji']} {league}"
            
            # Check if category already exists
            existing_category = discord.utils.get(guild.categories, name=category_name)
            if not existing_category:
                category = await guild.create_category(category_name)
                print(f"Created category: {category_name}")
            else:
                category = existing_category
                print(f"Found existing category: {category_name}")
                
            self.league_categories[league] = category

    async def create_game_channel(self, league: str, team1: str, team2: str, 
                                game_date: datetime) -> Optional[discord.TextChannel]:
        """Create a new game channel under appropriate league category"""
        
        if league not in self.league_categories:
            print(f"League {league} not found in categories")
            return None
            
        category = self.league_categories[league]
        channel_name = f"📊 {team1.lower().replace(' ', '-')}-vs-{team2.lower().replace(' ', '-')}"
        
        # Check if channel already exists
        existing_channel = discord.utils.get(category.channels, name=channel_name)
        if existing_channel:
            return existing_channel
            
        # Create new channel
        try:
            channel = await category.create_text_channel(
                name=channel_name,
                topic=f"{team1} vs {team2} - {game_date.strftime('%B %d, %Y')}"
            )
            
            # Store channel reference
            game_key = f"{league}_{team1}_{team2}_{game_date.strftime('%Y%m%d')}"
            self.game_channels[game_key] = channel
            
            print(f"Created game channel: {channel_name}")
            return channel
            
        except Exception as e:
            print(f"Failed to create channel {channel_name}: {e}")
            return None

    async def cleanup_old_channels(self, days_old: int = 3):
        """Remove game channels older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for guild in self.guilds:
            for category in guild.categories:
                if any(league in category.name for league in self.leagues.keys()):
                    for channel in category.channels:
                        if channel.name.startswith("📊"):
                            # Extract date from channel topic or creation time
                            channel_age = datetime.now() - channel.created_at
                            if channel_age.days > days_old:
                                try:
                                    await channel.delete()
                                    print(f"Deleted old channel: {channel.name}")
                                except Exception as e:
                                    print(f"Failed to delete {channel.name}: {e}")

# Global bot instance
bot = SportsBot()

# ============================================================================
# SLASH COMMANDS
# ============================================================================

@bot.tree.command(name="schedule", description="Show games for today or specific date")
async def schedule_command(interaction: discord.Interaction, 
                          league: str = None, 
                          date: str = None):
    """Display game schedule"""
    
    await interaction.response.defer()
    
    # This will integrate with your MCP servers
    embed = discord.Embed(
        title="🗓️ Game Schedule",
        description="*Integration with MCP servers pending*",
        color=0x00ff00
    )
    
    if league:
        embed.add_field(name="League", value=league.upper(), inline=True)
    if date:
        embed.add_field(name="Date", value=date, inline=True)
        
    embed.add_field(
        name="Coming Soon", 
        value="Schedule data from MLB, Soccer, and other MCPs", 
        inline=False
    )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="odds", description="Get betting odds for a matchup")
async def odds_command(interaction: discord.Interaction, 
                      team1: str, 
                      team2: str):
    """Display betting odds"""
    
    await interaction.response.defer()
    
    # This will integrate with your Odds MCP
    embed = discord.Embed(
        title="💰 Betting Odds",
        description=f"**{team1.title()} vs {team2.title()}**",
        color=0xffd700
    )
    
    embed.add_field(
        name="Moneyline", 
        value="*Odds MCP integration pending*", 
        inline=True
    )
    embed.add_field(
        name="Spread", 
        value="*Coming soon*", 
        inline=True
    )
    embed.add_field(
        name="Total", 
        value="*Coming soon*", 
        inline=True
    )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="player", description="Get player stats and prop history")
async def player_command(interaction: discord.Interaction, 
                        player_name: str):
    """Display player information"""
    
    await interaction.response.defer()
    
    # This will integrate with your ESPN Player ID MCP
    embed = discord.Embed(
        title="👤 Player Stats",
        description=f"**{player_name.title()}**",
        color=0x0099ff
    )
    
    embed.add_field(
        name="Current Stats", 
        value="*ESPN Player ID MCP integration pending*", 
        inline=False
    )
    embed.add_field(
        name="Prop History", 
        value="*Coming soon*", 
        inline=False
    )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="setup", description="Admin command to create game channels")
async def setup_command(interaction: discord.Interaction, 
                       league: str, 
                       team1: str, 
                       team2: str):
    """Admin command to manually create game channels"""
    
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ You need administrator permissions to use this command.", 
            ephemeral=True
        )
        return
    
    await interaction.response.defer()
    
    # Create game channel
    game_date = datetime.now()
    channel = await bot.create_game_channel(league.upper(), team1, team2, game_date)
    
    if channel:
        embed = discord.Embed(
            title="✅ Channel Created",
            description=f"Game channel created: {channel.mention}",
            color=0x00ff00
        )
    else:
        embed = discord.Embed(
            title="❌ Channel Creation Failed",
            description="Could not create the game channel",
            color=0xff0000
        )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="cleanup", description="Admin command to remove old game channels")
async def cleanup_command(interaction: discord.Interaction, days: int = 3):
    """Admin command to cleanup old channels"""
    
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ You need administrator permissions to use this command.", 
            ephemeral=True
        )
        return
    
    await interaction.response.defer()
    
    await bot.cleanup_old_channels(days)
    
    embed = discord.Embed(
        title="🧹 Cleanup Complete",
        description=f"Removed game channels older than {days} days",
        color=0x00ff00
    )
    
    await interaction.followup.send(embed=embed)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def send_game_analysis(channel: discord.TextChannel, 
                           team1: str, 
                           team2: str, 
                           game_data: dict):
    """Send comprehensive game analysis to specific channel"""
    
    embed = discord.Embed(
        title=f"📊 {team1} vs {team2}",
        description="Pre-Game Analysis",
        color=0x0099ff,
        timestamp=datetime.now()
    )
    
    # Game information
    embed.add_field(
        name="🏟️ Game Info",
        value=f"**Date:** {game_data.get('date', 'TBD')}\n"
              f"**Time:** {game_data.get('time', 'TBD')}\n"
              f"**Venue:** {game_data.get('venue', 'TBD')}",
        inline=True
    )
    
    # Betting lines
    embed.add_field(
        name="💰 Betting Lines",
        value=f"**Spread:** {game_data.get('spread', 'TBD')}\n"
              f"**Total:** {game_data.get('total', 'TBD')}\n"
              f"**Moneyline:** {game_data.get('moneyline', 'TBD')}",
        inline=True
    )
    
    # AI Prediction
    embed.add_field(
        name="🤖 AI Analysis",
        value="*MCP integration pending*\n"
              "Detailed analysis coming soon",
        inline=False
    )
    
    embed.set_footer(text="Sports Betting Bot | Data from MCP Servers")
    
    await channel.send(embed=embed)

# ============================================================================
# BOT STARTUP
# ============================================================================

if __name__ == "__main__":
    print("Starting Sports Betting Discord Bot...")
    print("Make sure to set BOT_TOKEN environment variable")
    
    # In production, load from environment variables
    # bot.run(os.getenv('DISCORD_BOT_TOKEN'))
    
    # For development
    print("Bot structure ready - add your Discord bot token to run")