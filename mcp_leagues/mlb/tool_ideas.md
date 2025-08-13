Essential Betting Tools (Priority 1)
1. getMLBPlayerPropStats

Pull last N games for specific stats (hits, HRs, RBIs, strikeouts, etc.)
Calculate hit rate vs specific lines (e.g., "Over 1.5 hits in last 10 games")
Include home/away splits
Show recent trend (hot/cold streaks)

2. getMLBPitcherMatchup

Starting pitcher's last 5 starts performance
ERA, WHIP, K/9 for recent games
Historical performance vs today's opponent
Home/away splits for the pitcher

3. getMLBTeamScoringTrends

Team runs scored/allowed last N games
Over/under record in last 10/20 games
Average total runs in games
First 5 innings scoring patterns

4. getMLBBatterVsPitcher

Historical matchup data (career and recent)
Similar pitcher type performance
Key stats: AVG, OPS, HRs against

Advanced Analytics (Priority 2)
5. getMLBGameConditions

Weather data for game (if available in API)
Venue/park factors
Day/night game impacts
Umpire assignment (if available)

6. getMLBTeamForm

Win/loss streaks
Recent series performance
Rest days analysis
Travel schedule impact

7. getMLBSplitStats

Comprehensive splits for players/teams:

vs RHP/LHP
Home/Away
Day/Night
Monthly performance
With RISP



8. getMLBLineupAnalysis

Expected lineup vs pitcher handedness
Team OPS vs starter's pitch type
Bench strength for late innings

Specialized Props Tools (Priority 3)
9. getMLBFirstInningStats

First inning runs scored/allowed
Pitcher first inning ERA
Team first inning scoring rate

10. getMLBPlayerStreaks

Current hitting streaks
Multi-hit game frequency
Home run droughts/streaks
RBI consistency

11. getMLBBullpenStatus

Recent usage (last 3 days)
Available high-leverage arms
Save/blown save situations

12. getMLBCorrelatedStats

When pitcher gets 6+ Ks, team record
High-scoring game indicators
Player combo performance

Data Aggregation Tools
13. getMLBDailySlate

All games with probable pitchers
Key injuries/lineup changes
Recent form summary for all teams

14. getMLBBatchPlayerProps

Bulk fetch multiple players' stats
Optimized for daily prop analysis
Configurable stat selection

15. getMLBHistoricalTrends

Season-long patterns
Team performance by month
Player career numbers vs teams

Implementation Notes:
Start with tools 1-4 as they directly support the most common betting markets:

Player props (hits, HRs, RBIs)
Game totals (O/U)
Moneylines (pitcher matchups)

Each tool should:

Use ET timezone (like your existing tools)
Handle errors gracefully
Support batch operations where possible
Cache responses for same-day queries

Key parameters to support:

count: Last N games/days
season: Default to current
splits: Include split data
venue: Home/away specific