# Discord Bot Command Troubleshooting Guide

## 🔍 Issue: `/clear-channels` and `/help` commands not working

### **Current Status**
- ✅ `/create-mlb-channels` - Working
- ❌ `/clear-channels` - Not working  
- ❌ `/help` - Not working

### **Code Analysis**
After reviewing `sports_discord_bot.py`, both commands are **properly implemented**:

#### `/clear-channels` Command ✅
```python
@bot.tree.command(name="clear-channels", description="Clear all channels from a specific sport category")
@app_commands.describe(category="Select the sport to clear channels from")
@app_commands.choices(category=[...])
async def clear_channels_command(interaction: discord.Interaction, category: str):
    # Implementation is complete and correct
```

#### `/help` Command ✅  
```python
@bot.tree.command(name="help", description="Show all available bot commands")
async def help_command(interaction: discord.Interaction):
    # Implementation is complete and correct
```

---

## 🚨 **Likely Root Causes**

### **1. Command Sync Issues** (Most Likely)
**Problem**: Commands are defined in code but not synced to Discord servers.

**Symptoms**:
- Some commands work, others don't
- Commands appear/disappear randomly
- New commands don't show up in Discord

**Solutions**:
```bash
# Option A: Use the /sync command in Discord
/sync

# Option B: Manual sync via Discord Developer Portal
1. Go to Discord Developer Portal
2. Select your application
3. Go to "Bot" section
4. Reset bot token (forces re-sync)
5. Update DISCORD_TOKEN environment variable
```

### **2. Deployment State Issues**
**Problem**: Railway is running an older version of the bot code.

**Solutions**:
```bash
# Force redeploy on Railway
railway up --detach

# Or trigger redeploy via git
git add .
git commit -m "Force bot redeploy"
git push
```

### **3. Bot Permissions Issues**
**Problem**: Bot lacks necessary permissions in Discord server.

**Required Permissions**:
- ✅ Send Messages
- ✅ Use Slash Commands  
- ✅ Manage Channels (for `/clear-channels`)
- ✅ Embed Links
- ✅ Read Message History

**Check Permissions**:
1. Right-click bot in Discord server
2. Select "Manage" 
3. Verify permissions listed above

### **4. Guild-Specific Registration**
**Problem**: Commands registered to specific guild vs globally.

**Current Code**: Commands are registered globally (correct)
**Issue**: May take up to 1 hour for global commands to propagate

---

## 🛠️ **Diagnostic Steps**

### **Step 1: Check Command Registration**
Run the debug script:
```bash
python mcp_leagues/discord_bot/debug_commands.py
```

Then use these commands in Discord:
- `/list-commands` - See all registered commands
- `/check-permissions` - Verify bot permissions
- `/test-help` - Test basic functionality
- `/test-clear` - Test clear functionality

### **Step 2: Manual Command Sync**
In Discord, use the working `/sync` command:
```
/sync
```

Expected response: "✅ Synced X slash commands!"

### **Step 3: Check Railway Logs**
```bash
railway logs --tail
```

Look for:
- ✅ "Synced X command(s)" on startup
- ❌ Any error messages during command registration
- ❌ Permission errors

### **Step 4: Verify Environment Variables**
Check Railway environment variables:
```bash
railway variables
```

Ensure these are set:
- `DISCORD_TOKEN` - Bot token
- `MLB_MCP_URL` - MCP server URL
- Other MCP URLs as needed

---

## 🔧 **Quick Fixes**

### **Fix 1: Force Command Re-sync**
Add this temporary command to force re-sync:

```python
@bot.tree.command(name="force-sync", description="Force sync all commands")
async def force_sync(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        synced = await bot.tree.sync()
        await interaction.followup.send(f"✅ Force synced {len(synced)} commands!")
    except Exception as e:
        await interaction.followup.send(f"❌ Sync failed: {str(e)}")
```

### **Fix 2: Clear Command Cache**
Add this to the bot's `on_ready` event:

```python
async def on_ready(self):
    # Clear and re-sync commands
    self.tree.clear_commands(guild=None)  # Clear global commands
    
    # Re-add commands (they're already decorated)
    synced = await self.tree.sync()
    logger.info(f"Cleared and re-synced {len(synced)} commands")
```

### **Fix 3: Guild-Specific Sync** (Temporary)
For immediate testing, sync to specific guild:

```python
# In on_ready()
guild = discord.Object(id=YOUR_GUILD_ID)  # Replace with your server ID
synced = await self.tree.sync(guild=guild)
```

---

## 📊 **Expected Command List**

After successful sync, you should see these commands:

| Command | Status | Description |
|---------|--------|-------------|
| `/sync` | ✅ Working | Manually sync slash commands |
| `/create-mlb-channels` | ✅ Working | Create channels for MLB games |
| `/clear-channels` | ❌ Missing | Clear channels from sport category |
| `/help` | ❌ Missing | Show all available commands |
| `/setup` | ❓ Unknown | Setup channel structure |
| `/debug-mlb` | ❓ Unknown | Debug MLB data |
| `/analyze` | ❓ Unknown | Analyze games (coming soon) |

---

## 🚀 **Immediate Action Plan**

### **Priority 1: Verify Current State**
1. Run `/list-commands` in Discord to see what's actually registered
2. Check Railway logs for any sync errors
3. Verify bot permissions in Discord server

### **Priority 2: Force Re-sync**
1. Use `/sync` command in Discord
2. If that fails, redeploy on Railway
3. Check logs for successful sync message

### **Priority 3: Test Commands**
1. Try `/help` and `/clear-channels` after sync
2. If still not working, check for typos in command names
3. Verify no duplicate command definitions

### **Priority 4: Debug Mode**
1. Deploy the debug script temporarily
2. Use debug commands to diagnose issues
3. Remove debug script after fixing

---

## 📞 **Support Commands**

Add these temporary diagnostic commands to your bot:

```python
@bot.tree.command(name="bot-status", description="Check bot status and command registration")
async def bot_status(interaction: discord.Interaction):
    await interaction.response.defer()
    
    commands = await bot.tree.fetch_commands()
    embed = discord.Embed(title="🤖 Bot Status", color=discord.Color.blue())
    embed.add_field(name="Registered Commands", value=len(commands), inline=True)
    embed.add_field(name="Guilds", value=len(bot.guilds), inline=True)
    embed.add_field(name="Bot Ready", value=bot.is_ready(), inline=True)
    
    command_list = "\\n".join([f"• /{cmd.name}" for cmd in commands])
    embed.add_field(name="Commands", value=command_list or "None", inline=False)
    
    await interaction.followup.send(embed=embed)
```

---

## ✅ **Success Indicators**

You'll know the issue is fixed when:

1. **Command List**: `/list-commands` shows all 7 expected commands
2. **Help Works**: `/help` displays the full command embed
3. **Clear Works**: `/clear-channels` shows the dropdown menu
4. **Logs Clean**: No sync errors in Railway logs
5. **Consistent**: Commands work reliably across server restarts

---

## 🔄 **Prevention**

To prevent this issue in the future:

1. **Always test commands** after deployment
2. **Monitor Railway logs** for sync errors  
3. **Use `/sync` command** after major code changes
4. **Keep backup** of working bot token
5. **Document command changes** in deployment notes

The most likely fix is simply running `/sync` in Discord or redeploying the bot on Railway to force command registration.