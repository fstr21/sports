# Available Sports Data Sources

This document lists all sports available through our data sources for analysis and betting odds.

---

## ESPN Sports Data (via Sports AI MCP)

**✅ Confirmed Working** (based on your `sports_analysis.py` implementation)

Your Sports AI MCP provides comprehensive game analysis for:

### **Supported Sports:**
- ✅ **WNBA** - Women's National Basketball Association
  - Live game matchups and schedules
  - Player statistics (PPG, key matchups)
  - Team records and standings
  - Game analysis and predictions
  
- ✅ **NFL** - National Football League  
  - Weekly game schedules
  - Key player matchups (QB vs QB, etc.)
  - Team records and playoff implications
  - Game analysis and context

### **Available Functions:**
- 🔧 **`analyzeWnbaGames`** - WNBA game analysis with player stats
- 🔧 **`analyzeNflGames`** - NFL game analysis with matchups  
- 🔧 **`customSportsAnalysis`** - Custom analysis with prompts

### **Data Includes:**
- Real-time game schedules and matchups
- Player performance statistics (PPG, key stats)
- Team records and current standings
- AI-powered game analysis and predictions
- Key player vs player matchups
- Playoff implications and context

**Note:** Other sports return "not yet implemented" - currently focused on WNBA and NFL.

---

## The Odds API - Betting Odds Data

**Legend:**
- ✅ = Currently active (in season)
- ❌ = Currently inactive (out of season)  
- (Futures) = Supports futures/outright betting markets

---


## American Football

- ✅ **CFL** (`americanfootball_cfl`)
  - Canadian Football League
- ✅ **NCAAF** (`americanfootball_ncaaf`)
  - US College Football
- ✅ **NCAAF Championship Winner** (`americanfootball_ncaaf_championship_winner`) (Futures)
  - US College Football Championship Winner
- ✅ **NFL** (`americanfootball_nfl`)
  - US Football
- ✅ **NFL Preseason** (`americanfootball_nfl_preseason`)
  - US Football
- ✅ **NFL Super Bowl Winner** (`americanfootball_nfl_super_bowl_winner`) (Futures)
  - Super Bowl Winner 2025/2026


## Aussie Rules

- ✅ **AFL** (`aussierules_afl`)
  - Aussie Football


## Baseball

- ✅ **KBO** (`baseball_kbo`)
  - KBO League
- ✅ **MLB** (`baseball_mlb`)
  - Major League Baseball
- ✅ **MLB World Series Winner** (`baseball_mlb_world_series_winner`) (Futures)
  - World Series Winner 2025
- ✅ **MiLB** (`baseball_milb`)
  - Minor League Baseball
- ✅ **NPB** (`baseball_npb`)
  - Nippon Professional Baseball


## Basketball

- ✅ **NBA Championship Winner** (`basketball_nba_championship_winner`) (Futures)
  - Championship Winner 2025/2026
- ✅ **NCAAB Championship Winner** (`basketball_ncaab_championship_winner`) (Futures)
  - US College Basketball Championship Winner
- ✅ **WNBA** (`basketball_wnba`)
  - US Basketball


## Boxing

- ✅ **Boxing** (`boxing_boxing`)
  - Boxing Bouts


## Cricket

- ✅ **International Twenty20** (`cricket_international_t20`)
  - International Twenty20
- ✅ **One Day Internationals** (`cricket_odi`)
  - One Day Internationals
- ✅ **The Hundred** (`cricket_the_hundred`)
  - The Hundred


## Golf

- ✅ **Masters Tournament Winner** (`golf_masters_tournament_winner`) (Futures)
  - 2026 Winner


## Ice Hockey

- ✅ **NHL** (`icehockey_nhl`)
  - US Ice Hockey
- ✅ **NHL Championship Winner** (`icehockey_nhl_championship_winner`) (Futures)
  - Stanley Cup Winner 2025/2026


## Lacrosse

- ✅ **PLL** (`lacrosse_pll`)
  - Premier Lacrosse League


## Mixed Martial Arts

- ✅ **MMA** (`mma_mixed_martial_arts`)
  - Mixed Martial Arts


## Politics

- ✅ **US Presidential Elections Winner** (`politics_us_presidential_election_winner`) (Futures)
  - 2028 US Presidential Election Winner


## Rugby League

- ✅ **NRL** (`rugbyleague_nrl`)
  - Aussie Rugby League


## Soccer

- ✅ **3. Liga - Germany** (`soccer_germany_liga3`)
  - German Soccer
- ✅ **Allsvenskan - Sweden** (`soccer_sweden_allsvenskan`)
  - Swedish Soccer
- ✅ **Austrian Football Bundesliga** (`soccer_austria_bundesliga`)
  - Austrian Soccer
- ✅ **Belgium First Div** (`soccer_belgium_first_div`)
  - Belgian First Division A
- ✅ **Brazil Série A** (`soccer_brazil_campeonato`)
  - Brasileirão Série A
- ✅ **Brazil Série B** (`soccer_brazil_serie_b`)
  - Campeonato Brasileiro Série B
- ✅ **Bundesliga - Germany** (`soccer_germany_bundesliga`)
  - German Soccer
- ✅ **Bundesliga 2 - Germany** (`soccer_germany_bundesliga2`)
  - German Soccer
- ✅ **Championship** (`soccer_efl_champ`)
  - EFL Championship
- ✅ **Copa Libertadores** (`soccer_conmebol_copa_libertadores`)
  - CONMEBOL Copa Libertadores
- ✅ **Copa Sudamericana** (`soccer_conmebol_copa_sudamericana`)
  - CONMEBOL Copa Sudamericana
- ✅ **Denmark Superliga** (`soccer_denmark_superliga`)
  - Danish Soccer
- ✅ **Dutch Eredivisie** (`soccer_netherlands_eredivisie`)
  - Dutch Soccer
- ✅ **EFL Cup** (`soccer_england_efl_cup`)
  - League Cup
- ✅ **EPL** (`soccer_epl`)
  - English Premier League
- ✅ **Ekstraklasa - Poland** (`soccer_poland_ekstraklasa`)
  - Polish Soccer
- ✅ **Eliteserien - Norway** (`soccer_norway_eliteserien`)
  - Norwegian Soccer
- ✅ **FIFA World Cup Qualifiers - Europe** (`soccer_fifa_world_cup_qualifiers_europe`)
  - FIFA World Cup Qualifiers - UEFA
- ✅ **FIFA World Cup Winner** (`soccer_fifa_world_cup_winner`) (Futures)
  - FIFA World Cup Winner 2026
- ✅ **J League** (`soccer_japan_j_league`)
  - Japan Soccer League
- ✅ **K League 1** (`soccer_korea_kleague1`)
  - Korean Soccer
- ✅ **La Liga - Spain** (`soccer_spain_la_liga`)
  - Spanish Soccer
- ✅ **La Liga 2 - Spain** (`soccer_spain_segunda_division`)
  - Spanish Soccer
- ✅ **League 1** (`soccer_england_league1`)
  - EFL League 1
- ✅ **League 2** (`soccer_england_league2`)
  - EFL League 2 
- ✅ **League of Ireland** (`soccer_league_of_ireland`)
  - Airtricity League Premier Division
- ✅ **Leagues Cup** (`soccer_concacaf_leagues_cup`)
  - CONCACAF Leagues Cup
- ✅ **Liga MX** (`soccer_mexico_ligamx`)
  - Mexican Soccer
- ✅ **Ligue 1 - France** (`soccer_france_ligue_one`)
  - French Soccer
- ✅ **Ligue 2 - France** (`soccer_france_ligue_two`)
  - French Soccer
- ✅ **MLS** (`soccer_usa_mls`)
  - Major League Soccer
- ✅ **Premiership - Scotland** (`soccer_spl`)
  - Scottish Premiership
- ✅ **Primeira Liga - Portugal** (`soccer_portugal_primeira_liga`)
  - Portugese Soccer
- ✅ **Primera División - Argentina** (`soccer_argentina_primera_division`)
  - Argentine Primera División
- ✅ **Primera División - Chile** (`soccer_chile_campeonato`)
  - Campeonato Chileno
- ✅ **Serie A - Italy** (`soccer_italy_serie_a`)
  - Italian Soccer
- ✅ **Super League - China** (`soccer_china_superleague`)
  - Chinese Soccer
- ✅ **Super League - Greece** (`soccer_greece_super_league`)
  - Greek Soccer
- ✅ **Superettan - Sweden** (`soccer_sweden_superettan`)
  - Swedish Soccer
- ✅ **Swiss Superleague** (`soccer_switzerland_superleague`)
  - Swiss Soccer
- ✅ **Turkey Super League** (`soccer_turkey_super_league`)
  - Turkish Soccer
- ✅ **UEFA Champions League Qualification** (`soccer_uefa_champs_league_qualification`)
  - European Champions League Qualification
- ✅ **Veikkausliiga - Finland** (`soccer_finland_veikkausliiga`)
  - Finnish  Soccer


## Tennis

- ✅ **ATP Canadian Open** (`tennis_atp_canadian_open`)
  - Men's Singles
- ✅ **ATP Cincinnati Open** (`tennis_atp_cincinnati_open`)
  - Men's Singles
- ✅ **WTA Cincinnati Open** (`tennis_wta_cincinnati_open`)
  - Women's Singles

---

## Usage in Scripts

### **ESPN Sports Data (via MCP):**
```python
# Get WNBA games and analysis
wnba_analysis = mcp_sports_ai_analyzeWnbaGames()

# Get NFL games and analysis  
nfl_analysis = mcp_sports_ai_analyzeNflGames()

# Custom sports analysis with prompts
custom_analysis = mcp_sports_ai_customSportsAnalysis({
    "sport": "NBA",
    "prompt": "Analyze tonight's games for betting value"
})
```

### **The Odds API (Direct Betting Odds):**
```python
# NFL (regular season)
odds_data = get_odds_for_sport('americanfootball_nfl')

# NFL (preseason) 
odds_data = get_odds_for_sport('americanfootball_nfl_preseason')

# NBA
odds_data = get_odds_for_sport('basketball_nba')

# Premier League
odds_data = get_odds_for_sport('soccer_epl')
```

### **Smart Multi-Endpoint Approach:**

Our scripts automatically check multiple endpoints for sports with seasonal variations:

```python
sport_keys = {
    'nfl': ['americanfootball_nfl', 'americanfootball_nfl_preseason'],
    'nba': ['basketball_nba', 'basketball_nba_preseason'], 
    'mlb': ['baseball_mlb', 'baseball_mlb_preseason'],
    # ... etc
}
```

This ensures you get games regardless of whether it's preseason or regular season.

---

## Data Source Comparison

| Feature | ESPN (Sports AI MCP) | The Odds API |
|---------|---------------------|--------------|
| **Game Schedules** | ✅ Comprehensive | ✅ Games with odds only |
| **Live Scores** | ✅ Real-time | ❌ No scores |
| **Player Stats** | ✅ Detailed | ❌ No player data |
| **Betting Odds** | ❌ No odds | ✅ Multiple sportsbooks |
| **AI Analysis** | ✅ Built-in | ❌ Raw data only |
| **Historical Data** | ✅ Extensive | ❌ Current odds only |
| **International Sports** | ✅ Major leagues | ✅ 70+ sports worldwide |

**Best Practice:** Use ESPN for game analysis and context, The Odds API for current betting lines and odds.

---

*Generated on Fri, 08 Aug 2025 01:09:33 GMT*