# Sports Statistics Specification

This document defines the exact player statistics and betting markets we will collect for each sport in the Discord betting intelligence service. This specification ensures efficient API usage by focusing only on relevant data points.

## Basketball (NBA & WNBA)

### Player Statistics to Collect
- **Points** - Primary scoring metric
- **Rebounds** - Total rebounds (offensive + defensive)
- **Assists** - Playmaking metric
- **3-Pointers Made** - Three-point shooting performance
- **Steals** - Defensive metric
- **Blocks** - Defensive metric (primarily for centers/forwards)
- **Field Goal Percentage** - Shooting efficiency
- **Minutes Played** - Playing time context

### Betting Markets to Focus On
- `player_points` - Over/Under point totals
- `player_rebounds` - Over/Under rebound totals
- `player_assists` - Over/Under assist totals
- `player_threes` - Over/Under three-pointers made

### Key Analysis Factors
- Recent 10-game averages vs. betting lines
- Home/away performance splits
- Opponent defensive rankings (points allowed to position)
- Back-to-back game fatigue impact
- Injury reports affecting playing time

---

## Football (NFL & College Football)

### Quarterback Statistics to Collect
- **Passing Yards** - Primary QB metric
- **Passing Attempts** - Volume indicator
- **Passing Touchdowns** - Red zone efficiency
- **Completions** - Accuracy context
- **Interceptions** - Risk assessment
- **Rushing Yards** - Mobile QB factor

### Running Back Statistics to Collect
- **Rushing Yards** - Primary RB metric
- **Rushing Attempts** - Volume/workload
- **Receiving Yards** - Pass-catching backs
- **Receptions** - Target share
- **Total Touchdowns** - Red zone usage

### Wide Receiver Statistics to Collect
- **Receiving Yards** - Primary WR metric
- **Receptions** - Target reliability
- **Receiving Touchdowns** - Red zone targets
- **Targets** - Opportunity volume

### Betting Markets to Focus On
- `player_pass_yds` - QB passing yards
- `player_pass_attempts` - QB passing attempts
- `player_rush_yds` - RB/QB rushing yards
- `player_receptions` - WR/RB receptions
- `player_receiving_yds` - WR/RB receiving yards
- `anytime_touchdown_scorer` - Any position touchdown

### Key Analysis Factors
- Weather conditions for outdoor games
- Opponent defensive rankings by position
- Game script predictions (blowout vs. close game)
- Injury reports affecting target share
- Recent red zone usage trends

---

## Baseball (MLB)

### Batter Statistics to Collect
- **Hits** - Contact success
- **Home Runs** - Power metric
- **RBIs** - Run production
- **Runs Scored** - Offensive contribution
- **Total Bases** - Overall offensive impact
- **Batting Average** - Contact consistency
- **On-Base Percentage** - Getting on base
- **Strikeouts** - Contact struggles

### Pitcher Statistics to Collect
- **Strikeouts** - Dominant pitching metric
- **Walks Allowed** - Control issues
- **Hits Allowed** - Contact management
- **Earned Runs** - Run prevention
- **Innings Pitched** - Workload/stamina

### Betting Markets to Focus On
- `batter_hits` - Over/Under hits for batters
- `batter_home_runs` - Over/Under home runs
- `batter_total_bases` - Over/Under total bases
- `pitcher_strikeouts` - Over/Under strikeouts for pitchers
- `batter_rbis` - Over/Under RBIs

### Key Analysis Factors
- Ballpark factors (hitter/pitcher friendly)
- Weather conditions (wind, temperature)
- Pitcher vs. batter historical matchups
- Recent hot/cold streaks
- Lineup position and protection

---

## Hockey (NHL)

### Player Statistics to Collect
- **Goals** - Primary scoring metric
- **Assists** - Playmaking contribution
- **Points** - Total offensive production (goals + assists)
- **Shots on Goal** - Shooting volume
- **Plus/Minus** - Overall game impact
- **Penalty Minutes** - Discipline factor
- **Time on Ice** - Usage/opportunity

### Goalie Statistics to Collect
- **Saves** - Primary goalie metric
- **Goals Against** - Run prevention
- **Save Percentage** - Efficiency metric

### Betting Markets to Focus On
- `player_points` - Over/Under total points
- `player_assists` - Over/Under assists
- `player_shots_on_goal` - Over/Under shots
- `player_saves` - Over/Under saves (goalies)

### Key Analysis Factors
- Power play opportunities
- Opponent offensive/defensive strength
- Back-to-back game fatigue
- Goalie matchups and recent form
- Line combinations and ice time

---

## Soccer (Premier League, La Liga, MLS)

### Player Statistics to Collect
- **Goals** - Primary scoring metric
- **Assists** - Playmaking contribution
- **Shots** - Shooting volume
- **Shots on Target** - Shooting accuracy
- **Passes** - Ball distribution
- **Tackles** - Defensive contribution
- **Cards** - Disciplinary record

### Betting Markets to Focus On
- `player_shots` - Over/Under shots taken
- `player_shots_on_target` - Over/Under shots on target
- `player_goals` - Anytime goalscorer
- `player_assists` - Over/Under assists

### Key Analysis Factors
- Team formation and tactical approach
- Opponent defensive strength
- Home field advantage
- Recent form and confidence
- Weather conditions for outdoor matches

---

## Data Collection Efficiency Guidelines

### API Call Optimization
1. **Batch Collection**: Use comma-separated markets in single API calls
   - Example: `player_points,player_rebounds,player_assists`
2. **Game-Level Focus**: One API call per game for player props
3. **Priority Players**: Focus on starters and key bench players (15-20 per game)

### Statistical Analysis Priorities
1. **Last 10 Games**: Primary trend analysis window
2. **Home/Away Splits**: Venue-specific performance
3. **Opponent Rankings**: Defensive strength by position/category
4. **Recent Form**: Last 3-5 games for hot/cold streaks
5. **Usage Context**: Minutes, attempts, targets for opportunity assessment

### Data Quality Standards
- Minimum 5 games of recent data for reliable trends
- Exclude games with significant injury/ejection impact
- Weight recent games more heavily than older data
- Account for strength of schedule in opponent analysis

This specification ensures we collect only the most relevant statistics for betting analysis while maintaining efficient API usage across all supported sports.