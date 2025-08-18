# Soccer MCP Reference Data Guide

## 📍 Quick Reference Location
**Main Reference File**: `latest_key_ids.json`
**Full Data Directory**: `C:\Users\fstr2\Desktop\sports\mcp_leagues\soccer\reference_data`

## 🏆 Major Leagues & IDs

| League | ID | Country | Teams Available |
|--------|----|---------|----|
| **Premier League** | 228 | England | 20 teams |
| **La Liga** | 297 | Spain | 20 teams |
| **Serie A** | 253 | Italy | 20 teams |
| **Bundesliga** | 241 | Germany | 18 teams |
| **Ligue 1** | 235 | France | 18 teams |

## ⚽ Top Teams by League

### Premier League (ID: 228)
| Team ID | Team Name | 
|---------|-----------|
| 4136 | Manchester City |
| 4138 | Liverpool |
| 3068 | Arsenal |
| 2916 | Chelsea |
| 2909 | Tottenham Hotspur |
| 4149 | Nottingham Forest |
| 4145 | Fulham |
| 4140 | Crystal Palace |
| 3200 | Brighton & Hove Albion |
| 3073 | Sunderland |

### La Liga (ID: 297)  
| Team ID | Team Name |
|---------|-----------|
| 4884 | Barcelona |
| 4885 | Real Sociedad |
| 4887 | Athletic Bilbao |
| 4890 | Valencia |
| 4891 | Getafe |
| 4892 | Alaves |
| 4893 | Elche |
| 4895 | Espanyol |
| 2907 | Villarreal |
| 2910 | Rayo Vallecano |

### Serie A (ID: 253)
| Team ID | Team Name |
|---------|-----------|
| 3296 | Inter Milan |
| 2984 | Napoli |
| 3767 | Roma |
| 2820 | Bologna |
| 4411 | Genoa |
| 3206 | Udinese |
| 4408 | Sassuolo |
| 2978 | Lecce |
| 2981 | Cremonese |
| 3388 | Pisa |

### Bundesliga (ID: 241)
| Team ID | Team Name |
|---------|-----------|
| 4270 | Bayern Munich |
| 4271 | Bayer Leverkusen |
| 3204 | Borussia Dortmund |
| 4272 | Borussia M'gladbach |
| 2998 | Eintracht Frankfurt |
| 2983 | Wolfsburg |
| 3297 | Hoffenheim |
| 4273 | Werder Bremen |
| 3775 | Union Berlin |
| 3338 | Hamburg |

### Ligue 1 (ID: 235)
| Team ID | Team Name |
|---------|-----------|
| 4228 | PSG |
| 4230 | Lyon |
| 4229 | Lille |
| 4234 | Monaco |
| 3001 | Rennes |
| 4231 | Strasbourg |
| 3129 | Toulouse |
| 3199 | Brest |
| 2849 | Angers |
| 3002 | Auxerre |

## 🛠️ Usage in Tests

### For League-Based Tests
```python
# Use these confirmed league IDs
PREMIER_LEAGUE = 228
LA_LIGA = 297
SERIE_A = 253
BUNDESLIGA = 241
LIGUE_1 = 235
```

### For Team-Based Tests
```python
# Premier League teams
MANCHESTER_CITY = 4136
LIVERPOOL = 4138
ARSENAL = 3068
CHELSEA = 2916

# La Liga teams  
BARCELONA = 4884
REAL_SOCIEDAD = 4885
ATHLETIC_BILBAO = 4887
VALENCIA = 4890
```

## 📁 Files Available

| File | Description |
|------|-------------|
| `latest_key_ids.json` | Quick reference for league/team IDs |
| `latest_reference_data.json` | Complete reference dataset |
| `soccer_reference_data_YYYYMMDD_HHMMSS.json` | Timestamped complete data |
| `countries_YYYYMMDD_HHMMSS.json` | All 228 countries |
| `all_leagues_YYYYMMDD_HHMMSS.json` | All 15 leagues |
| `major_leagues_teams_YYYYMMDD_HHMMSS.json` | Teams for major leagues |

## 🎯 Key Notes

- **228 countries** available in the system
- **15 total leagues** found (only 5 have team data)
- **96 teams** across 5 major leagues
- Champions League (310) and Europa League (326) have no current standings
- MLS (168) has no current standings data
- All data collected from live MCP server: `soccermcp-production.up.railway.app/mcp`

## 🚀 Ready for Testing

This reference data enables:
- ✅ **Real team IDs** for all tests
- ✅ **Confirmed league IDs** that work
- ✅ **Safe data storage** with timestamps
- ✅ **Quick ID lookups** for development
- ✅ **Complete coverage** of major European leagues

Updated: 2025-08-17 18:53:43