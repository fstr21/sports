# 🎮 Discord Channel Management System

## 📋 **Overview**

Manual channel creation and deletion based on real game schedules from MCP servers. Channels are created for upcoming games and cleaned up when ready after extensive testing and validation.

## 🔄 **Daily Workflow**

### **Manual Channel Creation Process**
1. **Fetch Today's Games** from MCP servers
2. **Create Channels** for each game
3. **Populate Initial Data** (odds, analysis, predictions)
4. **Monitor and Test** functionality

### **Manual Cleanup Process**
1. **Identify Completed Games** (games older than X hours)
2. **Archive Important Data** (results, performance)
3. **Delete Old Channels** when ready
4. **Log Channel Activity** for analytics

## 🏗️ **Channel Creation Process**

### **Step 1: Game Data Retrieval**
```python
# Fetch today's games from each active MCP
mlb_games = await get_mlb_schedule(date=today)
soccer_games = await get_soccer_fixtures(date=today)
cfb_games = await get_cfb_games(date=today)

# Example game data structure:
{
    "league": "MLB",
    "game_id": "mlb_2025_08_16_bos_nyy",
    "team1": "Boston Red Sox",
    "team2": "New York Yankees",
    "team1_short": "BOS",
    "team2_short": "NYY", 
    "date": "2025-08-16",
    "time": "19:10:00",
    "venue": "Yankee Stadium",
    "status": "scheduled"
}
```

### **Step 2: Channel Name Generation**
```python
# Channel naming convention
def generate_channel_name(team1, team2):
    # Convert team names to Discord-friendly format
    team1_clean = clean_team_name(team1)  # "Boston Red Sox" -> "red-sox"
    team2_clean = clean_team_name(team2)  # "New York Yankees" -> "yankees"
    
    return f"📊 {team1_clean}-vs-{team2_clean}"

# Examples:
# "📊 red-sox-vs-yankees"
# "📊 chiefs-vs-bills" 
# "📊 liverpool-vs-arsenal"
# "📊 lakers-vs-warriors"
```

### **Step 3: Automated Channel Creation**
```python
async def create_daily_channels():
    """Create channels for all today's games"""
    
    for league in active_leagues:
        games = await fetch_games_for_league(league, date=today)
        category = get_league_category(league)
        
        for game in games:
            channel_name = generate_channel_name(game.team1, game.team2)
            
            # Check if channel already exists
            if not channel_exists(channel_name, category):
                channel = await create_game_channel(
                    category=category,
                    name=channel_name,
                    topic=f"{game.team1} vs {game.team2} - {game.date} {game.time}"
                )
                
                # Populate with initial game data
                await populate_channel_data(channel, game)
                
                print(f"✅ Created: {channel_name}")
            else:
                print(f"⏭️ Exists: {channel_name}")
```

## 🗑️ **Channel Deletion Process**

### **Automatic Cleanup Rules**
```python
# Deletion criteria
DELETION_RULES = {
    "completed_games": 6,    # Delete 6 hours after game ends
    "cancelled_games": 2,    # Delete 2 hours after cancellation
    "postponed_games": 24,   # Delete 24 hours after postponement
    "max_age": 72           # Force delete after 72 hours regardless
}

async def cleanup_old_channels():
    """Remove channels for completed/old games"""
    
    for category in league_categories:
        for channel in category.channels:
            if channel.name.startswith("📊"):
                
                # Extract game info from channel
                game_info = parse_channel_name(channel.name)
                game_status = await get_game_status(game_info)
                
                should_delete = check_deletion_criteria(
                    channel.created_at, 
                    game_status
                )
                
                if should_delete:
                    # Archive important data first
                    await archive_channel_data(channel)
                    
                    # Delete the channel
                    await channel.delete()
                    print(f"🗑️ Deleted: {channel.name}")
```

### **Manual Cleanup Commands**
```python
# Admin commands for manual control

@bot.tree.command(name="cleanup-league")
async def cleanup_league(interaction, league: str, hours_old: int = 6):
    """Delete all channels in a league older than X hours"""
    # Implementation for targeted cleanup

@bot.tree.command(name="cleanup-completed")  
async def cleanup_completed(interaction):
    """Delete channels for all completed games"""
    # Implementation for completed games only

@bot.tree.command(name="force-cleanup")
async def force_cleanup(interaction, confirm: str):
    """Delete ALL game channels (emergency cleanup)"""
    # Implementation with confirmation required
```

## 🎯 **Team Name Standardization**

### **Name Cleaning Function**
```python
def clean_team_name(team_name):
    """Convert team names to Discord channel format"""
    
    # Team name mappings for consistency
    name_mappings = {
        # MLB
        "Boston Red Sox": "red-sox",
        "New York Yankees": "yankees", 
        "Los Angeles Dodgers": "dodgers",
        "San Francisco Giants": "giants",
        
        # NFL
        "Kansas City Chiefs": "chiefs",
        "Buffalo Bills": "bills",
        "Green Bay Packers": "packers",
        "Dallas Cowboys": "cowboys",
        
        # Soccer
        "Liverpool FC": "liverpool",
        "Arsenal FC": "arsenal", 
        "Manchester City": "man-city",
        "Real Madrid": "real-madrid",
        
        # Add more as needed...
    }
    
    # Check direct mapping first
    if team_name in name_mappings:
        return name_mappings[team_name]
    
    # Auto-generate if no mapping
    return team_name.lower().replace(" ", "-").replace(".", "")
```

### **Handling Special Cases**
```python
# Special cases to handle
SPECIAL_CASES = {
    "same_city_teams": {
        "New York Yankees": "yankees",
        "New York Mets": "mets",
        "Los Angeles Lakers": "lakers", 
        "Los Angeles Clippers": "clippers"
    },
    "international_teams": {
        "Real Madrid": "real-madrid",
        "FC Barcelona": "barcelona",
        "Bayern Munich": "bayern"
    },
    "abbreviation_conflicts": {
        "LA" + "Lakers": "lakers",
        "LA" + "Angels": "angels"  # Avoid "la-la" channels
    }
}
```

## ⚡ **Manual Management Scripts**

### **Main Management Function**
```python
import asyncio
from datetime import datetime

async def manual_channel_management():
    """Main function for manual channel management"""
    
    print(f"🕐 Starting manual channel management - {datetime.now()}")
    
    try:
        # Step 1: Create channels for today's games
        await create_daily_channels()
        
        # Step 2: Update existing channels with latest data
        await update_existing_channels()
        
        # Step 3: Clean up old channels (manual trigger)
        # await cleanup_old_channels()  # Run when ready
        
        # Step 4: Generate summary
        await generate_management_summary()
        
        print("✅ Manual channel management completed")
        
    except Exception as e:
        print(f"❌ Error in management: {e}")
        await send_error_notification(e)

# Run manually when needed
# asyncio.run(manual_channel_management())
```

## 🎮 **Manual Control Commands**

### **Channel Creation Commands**
```python
@bot.tree.command(name="create-game")
async def create_game_channel(interaction, league: str, team1: str, team2: str, date: str = None):
    """Manually create a game channel"""
    # Implementation for manual channel creation

@bot.tree.command(name="create-daily")
async def create_daily_channels(interaction, league: str = None):
    """Create all channels for today's games in specified league"""
    # Implementation for creating today's channels

@bot.tree.command(name="bulk-create")
async def bulk_create_channels(interaction, days_ahead: int = 3):
    """Create channels for next X days of games"""
    # Implementation for bulk creation
```

### **Channel Deletion Commands**
```python
@bot.tree.command(name="delete-game")
async def delete_game_channel(interaction, team1: str, team2: str):
    """Delete specific game channel"""
    # Implementation for targeted deletion

@bot.tree.command(name="delete-completed")
async def delete_completed_games(interaction, league: str = None):
    """Delete all completed game channels"""
    # Implementation for completed games cleanup

@bot.tree.command(name="delete-old")
async def delete_old_channels(interaction, hours: int = 24):
    """Delete channels older than X hours"""
    # Implementation for age-based deletion
```

## 📊 **Channel Analytics & Monitoring**

### **Daily Reports**
```python
async def generate_daily_summary():
    """Generate daily channel management report"""
    
    summary = {
        "channels_created": 0,
        "channels_deleted": 0, 
        "active_channels": 0,
        "games_today": {},
        "errors": []
    }
    
    # Send summary to admin channel
    await send_admin_report(summary)
```

### **Monitoring Dashboard**
```python
@bot.tree.command(name="channel-status")
async def channel_status(interaction):
    """Show current channel statistics"""
    
    stats = {
        "total_channels": len(get_all_game_channels()),
        "channels_by_league": get_channels_by_league(),
        "oldest_channel": get_oldest_channel_age(),
        "newest_channel": get_newest_channel_age()
    }
    
    # Display stats in embed
    await interaction.response.send_message(embed=create_stats_embed(stats))
```

## 🔧 **Configuration Settings**

### **Channel Management Config**
```python
CHANNEL_CONFIG = {
    "manual_mode": True,           # Manual operation mode
    "auto_create": False,          # Disable automatic creation
    "auto_delete": False,          # Disable automatic deletion
    "max_channels_per_league": 50, # Discord limits
    "archive_before_delete": True, # Save data before deletion
    "notification_channel": None   # Admin notification channel
}

DELETION_CONFIG = {
    "completed_games_hours": 6,    # Hours after completion
    "cancelled_games_hours": 2,    # Hours after cancellation  
    "max_channel_age_hours": 72,   # Maximum channel age
    "require_confirmation": False,  # For bulk deletions
    "backup_important_data": True  # Archive key information
}
```

## 🚨 **Error Handling & Recovery**

### **Common Issues & Solutions**
```python
ERROR_HANDLING = {
    "mcp_server_down": "Use cached game data, retry in 30 minutes",
    "discord_rate_limit": "Queue operations, implement backoff",
    "duplicate_channels": "Check existing before creating",
    "permission_errors": "Verify bot permissions, notify admin",
    "api_quota_exceeded": "Switch to backup data source"
}

async def handle_creation_failure(game_data, error):
    """Handle channel creation failures gracefully"""
    
    # Log the error
    logger.error(f"Failed to create channel for {game_data}: {error}")
    
    # Try alternative channel name
    if "already exists" in str(error):
        alternative_name = generate_alternative_name(game_data)
        await retry_channel_creation(game_data, alternative_name)
    
    # Notify admin if critical
    if is_critical_error(error):
        await notify_admin(f"Channel creation failed: {error}")
```

## 🎯 **Implementation Priority**

### **Phase 1: Basic Automation**
1. ✅ Manual channel creation/deletion commands
2. ✅ Team name standardization system
3. ✅ Basic cleanup rules
4. 🔄 Daily automation script

### **Phase 2: Advanced Features**  
1. 📋 Bulk operations
2. 📋 Error handling & recovery
3. 📋 Analytics & monitoring
4. 📋 Archive system

### **Phase 3: Optimization**
1. 📋 Performance improvements
2. 📋 Advanced scheduling
3. 📋 Predictive channel creation
4. 📋 User preference integration

## 📝 **Quick Command Reference**

### **Daily Operations**
- `/create-daily` - Create today's game channels
- `/cleanup-completed` - Remove finished games  
- `/channel-status` - View current statistics

### **Manual Control**
- `/create-game [league] [team1] [team2]` - Create specific game
- `/delete-game [team1] [team2]` - Delete specific game
- `/delete-old [hours]` - Delete channels older than X hours

### **Bulk Operations**
- `/bulk-create [days]` - Create channels for next X days
- `/cleanup-league [league]` - Clean specific league
- `/force-cleanup` - Emergency full cleanup

**This system gives you complete control over daily channel management while automating the repetitive tasks.**