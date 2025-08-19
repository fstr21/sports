# Soccer Discord Bot - User Guide

## Quick Start

### For Server Administrators

1. **Create Soccer Channels**
   ```
   /create-channels sport:Soccer date:08/19/2025
   ```

2. **View Today's Schedule**
   ```
   /soccer-schedule
   ```

3. **Clean Up Old Channels**
   ```
   /cleanup days:3
   ```

### For Users

1. **Check Match Odds**
   ```
   /soccer-odds team1:Arsenal team2:Liverpool
   ```

2. **Get Head-to-Head Analysis**
   ```
   /soccer-h2h team1:Arsenal team2:Liverpool
   ```

3. **View League Standings**
   ```
   /soccer-standings league:EPL
   ```

## Available Commands

### 🔧 Administrative Commands

| Command | Description | Usage | Permissions |
|---------|-------------|-------|-------------|
| `/create-channels` | Create match channels for a date | `/create-channels sport:Soccer date:08/19/2025` | Administrator |
| `/cleanup` | Remove old game channels | `/cleanup days:3` | Administrator |
| `/setup` | Manually create a game channel | `/setup league:SOCCER team1:Arsenal team2:Liverpool` | Administrator |

### ⚽ Soccer Commands

| Command | Description | Usage | Permissions |
|---------|-------------|-------|-------------|
| `/soccer-schedule` | Show upcoming matches | `/soccer-schedule [league:EPL] [date:today]` | Everyone |
| `/soccer-odds` | Get betting odds | `/soccer-odds team1:Arsenal team2:Liverpool` | Everyone |
| `/soccer-h2h` | Head-to-head analysis | `/soccer-h2h team1:Arsenal team2:Liverpool` | Everyone |
| `/soccer-standings` | League table | `/soccer-standings league:EPL` | Everyone |

### 📊 General Commands

| Command | Description | Usage | Permissions |
|---------|-------------|-------|-------------|
| `/schedule` | Show games for any sport | `/schedule` | Everyone |
| `/odds` | Get betting odds | `/odds team1:Yankees team2:Red Sox` | Everyone |
| `/player` | Player statistics | `/player player_name:Messi` | Everyone |

## Supported Leagues

### 🏆 Available Leagues

| Code | League Name | Country | Season |
|------|-------------|---------|---------|
| `EPL` | Premier League | England | Aug-May |
| `La Liga` | La Liga | Spain | Aug-May |
| `MLS` | Major League Soccer | USA | Feb-Nov |
| `Bundesliga` | Bundesliga | Germany | Aug-May |
| `Serie A` | Serie A | Italy | Aug-May |
| `UEFA` | UEFA Champions League | Europe | Sep-May |

### 🗓️ Season Schedule

- **European Leagues** (EPL, La Liga, Bundesliga, Serie A): August - May
- **MLS**: February - November  
- **UEFA Champions League**: September - May (knockout stages)

## Channel System

### 📊 Match Channels

When you create soccer channels, the bot will:

1. **Create Individual Channels** for each match
   - Format: `📊 08-19-arsenal-vs-liverpool`
   - Under the "⚽ SOCCER" category

2. **Post Match Information** including:
   - Team names and league
   - Match date, time, and venue
   - Current betting odds
   - League standings context

3. **Provide Interactive Commands** in each channel:
   - Request H2H analysis
   - Get updated odds
   - View team statistics

### 🧹 Automatic Cleanup

- Channels are automatically deleted after **3 days**
- Channels with recent activity are preserved
- Pinned messages prevent deletion
- Manual cleanup available with `/cleanup` command

## Using Soccer Commands

### 📅 Getting Match Schedules

**Today's matches across all leagues:**
```
/soccer-schedule
```

**Specific league:**
```
/soccer-schedule league:EPL
```

**Specific date:**
```
/soccer-schedule date:08/19/2025
```

**League and date:**
```
/soccer-schedule league:La Liga date:08/20/2025
```

### 💰 Checking Betting Odds

**Basic odds lookup:**
```
/soccer-odds team1:Arsenal team2:Liverpool
```

**Response includes:**
- Moneyline odds (Win/Draw/Win)
- Over/Under totals
- Both Teams to Score (BTTS)
- Odds in both decimal and American formats

### 📊 Head-to-Head Analysis

**Get comprehensive H2H data:**
```
/soccer-h2h team1:Real Madrid team2:Barcelona
```

**Analysis includes:**
- Overall historical record
- Recent form (last 5-10 matches)
- Goals scored/conceded patterns
- Betting recommendations
- Home/away performance splits

### 🏆 League Standings

**Current league table:**
```
/soccer-standings league:EPL
```

**Standings show:**
- Current positions
- Points, wins, draws, losses
- Goals for/against and goal difference
- Recent form indicators
- Champions League/Europa League qualification spots

## Date Formats

The bot accepts multiple date formats:

| Format | Example | Description |
|--------|---------|-------------|
| MM/DD/YYYY | 08/19/2025 | US format |
| DD-MM-YYYY | 19-08-2025 | European format |
| YYYY-MM-DD | 2025-08-19 | ISO format |

**Valid date range:** 30 days in the past to 1 year in the future

## Understanding Match Information

### 🏟️ Match Details

Each match channel shows:

```
⚽ Arsenal vs Liverpool
🏆 Premier League
📅 August 19, 2025 at 15:00 GMT
🏟️ Emirates Stadium, London

💰 Betting Odds
Home Win: Arsenal +150 (2.50)
Draw: +220 (3.20)  
Away Win: Liverpool +180 (2.80)
Over/Under 2.5: Over -110 (1.91)

📊 League Context
Arsenal: 1st place, 30 points
Liverpool: 2nd place, 28 points
```

### 📈 Head-to-Head Analysis

```
📊 Arsenal vs Liverpool - Head to Head

Overall Record (Last 20 meetings)
Arsenal: 8 wins
Liverpool: 7 wins  
Draws: 5

Recent Form (Last 5 matches)
Arsenal: W-W-L-D-W
Liverpool: L-W-W-W-D

🎯 Betting Insights
• Over 2.5 goals in 70% of recent meetings
• Both teams scored in 80% of matches
• Arsenal unbeaten at home vs Liverpool (last 3)

💡 Recommendations
• Over 2.5 goals: Strong value
• Both Teams to Score: Yes
• Arsenal Double Chance: Safe option
```

## Tips for Best Experience

### 🎯 For Administrators

1. **Create channels in advance** - Run `/create-channels` the night before match days
2. **Monitor channel limits** - Discord servers have channel limits
3. **Use cleanup regularly** - Keep server organized with `/cleanup`
4. **Pin important messages** - Prevents automatic deletion

### ⚽ For Users

1. **Use specific team names** - "Arsenal" works better than "The Gunners"
2. **Check multiple leagues** - Use `/soccer-schedule` to see all matches
3. **Request H2H before big matches** - Get detailed analysis
4. **Follow league standings** - Track your team's progress

### 📱 Mobile Users

1. **Commands work on mobile** - All slash commands available
2. **Embeds are mobile-friendly** - Information displays well
3. **Use autocomplete** - Discord suggests team/league names

## Troubleshooting

### ❌ Common Issues

**"No matches found for date"**
- Check date format (MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD)
- Verify the date has scheduled matches
- Some leagues have off-seasons

**"Team not found"**
- Use full team names (e.g., "Arsenal" not "ARS")
- Check spelling and try variations
- Some teams may not be in our database

**"Command not working"**
- Make sure you're using slash commands (start with `/`)
- Check you have permission to use the command
- Try again if the bot seems slow

**"Channel creation failed"**
- Bot needs "Manage Channels" permission
- Server may have reached channel limit
- Try again in a few minutes

### 🔧 Getting Help

1. **Check command syntax** - Use Discord's autocomplete
2. **Try different team names** - Use variations if not found
3. **Contact administrators** - For permission issues
4. **Be patient** - Bot may be processing many requests

## Examples

### 📅 Creating Channels for El Clásico Weekend

```
/create-channels sport:Soccer date:10/26/2025
```

**Result:** Creates channels for all matches including:
- `📊 10-26-barcelona-vs-real-madrid`
- `📊 10-26-atletico-vs-sevilla`
- Plus other La Liga and international matches

### 💰 Checking Champions League Final Odds

```
/soccer-odds team1:Manchester City team2:Real Madrid
```

**Response:**
```
💰 Manchester City vs Real Madrid

🏆 UEFA Champions League Final
📅 May 28, 2025 at 20:00 GMT
🏟️ Wembley Stadium, London

Betting Odds:
Man City Win: +120 (2.20)
Draw (90 min): +240 (3.40)
Real Madrid Win: +200 (3.00)

Over/Under 2.5 Goals:
Over: -115 (1.87)
Under: -105 (1.95)

Both Teams to Score:
Yes: -130 (1.77)
No: +110 (2.10)
```

### 📊 Premier League Title Race Analysis

```
/soccer-h2h team1:Arsenal team2:Manchester City
```

**Shows:** Historical record, recent form, key statistics, and betting insights for the title race.

```
/soccer-standings league:EPL
```

**Shows:** Current table with Arsenal and Man City's positions, points gap, and remaining fixtures.

This user guide covers all the essential information needed to effectively use the Soccer Discord Bot, from basic commands to advanced features and troubleshooting.