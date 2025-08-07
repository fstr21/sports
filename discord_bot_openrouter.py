#!/usr/bin/env python3
"""
Discord bot that uses OpenRouter + your MCP proxy for sports betting analysis
"""
import discord
import openai
import json
import asyncio
from datetime import datetime

class SportsBettingBot:
    def __init__(self):
        # Your credentials from .env.local
        self.openrouter_key = "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"
        self.openrouter_client = openai.OpenAI(
            api_key=self.openrouter_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # MCP proxy details (when you want to integrate real data)
        self.mcp_proxy = "http://localhost:9091"
        self.mcp_token = "sports-betting-token"
    
    def analyze_betting_opportunity(self, sport, team1, team2):
        """Use OpenRouter to analyze a betting opportunity"""
        
        prompt = f"""
        As a sports betting expert, analyze this {sport} matchup:
        {team1} vs {team2}
        
        Consider:
        1. Recent team performance and trends
        2. Head-to-head history
        3. Key player status and injuries
        4. Home/away advantage
        5. Weather conditions (if applicable)
        6. Line movement and public betting patterns
        
        Provide:
        - Game prediction with confidence level (1-10)
        - 2-3 best betting opportunities
        - Risk level for each bet (Low/Medium/High)
        - Recommended bet size (1-5 units)
        
        Format as a clear, actionable recommendation.
        """
        
        try:
            response = self.openrouter_client.chat.completions.create(
                model="openai/gpt-4o-mini",  # Free model
                messages=[
                    {"role": "system", "content": "You are a professional sports betting analyst with 10+ years experience. Provide data-driven, responsible betting advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error getting analysis: {str(e)}"
    
    def get_daily_picks(self, sport="NBA"):
        """Get daily betting picks for a sport"""
        
        prompt = f"""
        Create today's {sport} betting picks for {datetime.now().strftime('%B %d, %Y')}.
        
        Provide 3-5 games with:
        1. Best bets (moneyline, spread, or totals)
        2. Confidence level (1-10) 
        3. Unit recommendation (1-5)
        4. Brief reasoning (1-2 sentences)
        
        Focus on value bets with good risk/reward ratios.
        Include a "Lock of the Day" - your highest confidence pick.
        
        Format as a Discord-friendly message with clear sections.
        """
        
        try:
            response = self.openrouter_client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a sharp sports bettor known for finding value. Today is game day - give your subscribers actionable picks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error getting daily picks: {str(e)}"
    
    def format_for_discord(self, content):
        """Format analysis for Discord with nice formatting"""
        
        # Add Discord formatting
        formatted = content.replace("**", "**")  # Bold stays
        formatted = formatted.replace("Lock of the Day", "🔒 **LOCK OF THE DAY** 🔒")
        formatted = f"🏀 **SPORTS BETTING ANALYSIS** 🏀\n\n{formatted}\n\n⚠️ *Bet responsibly. Never bet more than you can afford to lose.*"
        
        return formatted

# Example usage functions
def test_analysis():
    """Test the betting analysis"""
    bot = SportsBettingBot()
    
    print("Testing betting analysis...")
    print("=" * 50)
    
    # Test single game analysis
    analysis = bot.analyze_betting_opportunity("NBA", "Lakers", "Warriors")
    formatted = bot.format_for_discord(analysis)
    print("GAME ANALYSIS:")
    print(formatted)
    print("\n" + "=" * 50)
    
    # Test daily picks
    picks = bot.get_daily_picks("NBA")
    formatted_picks = bot.format_for_discord(picks)
    print("DAILY PICKS:")
    print(formatted_picks)

def create_discord_bot_template():
    """Create a template Discord bot using this"""
    
    template = '''
import discord
from discord.ext import commands, tasks
from discord_bot_openrouter import SportsBettingBot

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize sports betting bot
sports_bot = SportsBettingBot()

@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')
    daily_picks_task.start()  # Start daily picks

@bot.command(name='analyze')
async def analyze_game(ctx, sport, team1, team2):
    """Analyze a specific game: !analyze NBA Lakers Warriors"""
    
    analysis = sports_bot.analyze_betting_opportunity(sport, team1, team2)
    formatted = sports_bot.format_for_discord(analysis)
    
    await ctx.send(formatted)

@bot.command(name='picks')
async def daily_picks(ctx, sport="NBA"):
    """Get daily picks: !picks NBA"""
    
    picks = sports_bot.get_daily_picks(sport)
    formatted = sports_bot.format_for_discord(picks)
    
    await ctx.send(formatted)

@tasks.loop(hours=24)  # Run daily at the same time
async def daily_picks_task():
    """Automatically post daily picks"""
    channel = bot.get_channel(YOUR_CHANNEL_ID)  # Replace with your channel ID
    
    picks = sports_bot.get_daily_picks("NBA")
    formatted = sports_bot.format_for_discord(picks)
    
    await channel.send(f"📅 **DAILY PICKS - {datetime.now().strftime('%m/%d/%Y')}**\\n\\n{formatted}")

# Run the bot
# bot.run("YOUR_DISCORD_BOT_TOKEN")
'''
    
    with open("discord_bot_template.py", "w") as f:
        f.write(template)
    
    print("Created discord_bot_template.py - add your Discord bot token to use it!")

if __name__ == "__main__":
    test_analysis()
    print("\n" + "=" * 50)
    create_discord_bot_template()