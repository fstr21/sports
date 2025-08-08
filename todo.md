TODO: Split clients by data type (not sport) + lock all ESPN access behind MCP
Goals
Reorganize client code so features are by data type: scoreboard, game summary, season, odds, and chat.

Never call ESPN directly from clients. All ESPN data must flow through sports_ai_mcp.py tools.

Keep OpenRouter usage strict: LLM only sees JSON fetched by MCP; no guessing.

Non-negotiable constraints
❌ No requests.get("https://site.api.espn.com/...") in any client.

✅ Only use MCP tools: getScoreboard, findEvents, getGameSummary, analyzeGameByTeams (plus Odds MCP if needed).

✅ Respect .env.local for OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL.

✅ If a stat isn’t present in JSON, answer “unavailable”—no fabrication.

Deliverables
clients/core_mcp.py – thin wrapper around MCP tool functions (+ simple error handling).

clients/core_llm.py – strict OpenRouter call (system prompt, tokens, base URL).

clients/scoreboard_cli.py – list/filter events for a date; prints event_id, teams, status.

clients/game_cli.py – fetch a game summary (by event_id) and:

(a) pretty-print core team/player stats, or

(b) ask OpenRouter strictly (“How did the QBs do?”).

clients/season_cli.py – calls getTeamSeasonStats/getPlayerSeasonStats (currently returns supported:false).

clients/odds_cli.py – talks to Odds MCP only (no ESPN) for betting markets.

clients/chat_cli.py – NL interface:

events <league> [YYYYMMDD]

find <league> <YYYYMMDD> <team>

ask <league> <date|today> <TEAM1> vs <TEAM2> <question...> → uses analyzeGameByTeams.

adapters/*.py – tiny sport adapters (only when necessary) to normalize box-score shapes:

adapters/nfl.py, nba.py, wnba.py, mlb.py, nhl.py, soccer.py

Each returns a minimal, consistent dict (e.g., NFL: passing/rushing/receiving; NBA: players[pts,reb,ast,fg,3p,ft]; MLB: batting/pitching; NHL: skaters/goalies; Soccer: players[min,goals,assists,cards,saves] when available).

tests/ – unit + integration tests:

test_adapters_*.py (frozen JSON samples)

test_feature_game_cli.py (live MCP smoke: fetch summary for a known event_id)

test_scoreboard_cli.py (live MCP: date with/without events)

Directory layout (target)
bash
Copy
Edit
/clients/
  core_mcp.py
  core_llm.py
  scoreboard_cli.py
  game_cli.py
  season_cli.py
  odds_cli.py
  chat_cli.py
/adapters/
  nfl.py
  nba.py
  wnba.py
  mlb.py
  nhl.py
  soccer.py
/tests/
  test_adapters_nfl.py
  test_feature_game_cli.py
  test_scoreboard_cli.py
/mcp/
  sports_ai_mcp.py   # existing (with findEvents, analyzeGameByTeams, etc.)
.env.local           # OPENROUTER_* here
Implementation steps
A) Core wrappers
clients/core_mcp.py

Functions:

scoreboard(league, date) → calls getScoreboard

find_events(league, date, team_query) → calls findEvents

game_summary(league, event_id) → calls getGameSummary

analyze_by_teams(league, date, team1, team2, question) → calls analyzeGameByTeams

Ensure these accept league keys: nfl, ncaaf, nba, wnba, ncaab, mlb, nhl, mls, epl, laliga and map them to (sport, league) internally.

clients/core_llm.py

strict_answer(payload, question):

System prompt: “Only summarize fields from provided JSON; if missing say ‘unavailable’; never infer or fabricate.”

Send to OPENROUTER_BASE_URL/chat/completions with OPENROUTER_MODEL.

Low temp (0.0–0.2), max_tokens ~700.

B) Feature clients
scoreboard_cli.py

events <league> [YYYYMMDD] → print rows: event_id | AWAY @ HOME | status.

game_cli.py

game <league> <event_id> [--json] [--ask "question"]

If --ask, call core_llm.strict_answer with the MCP summary JSON.

season_cli.py

team-season <league> <team_id> [season]

player-season <league> <player_id> [season]

Print supported:false clearly when MCP says so.

odds_cli.py

Ensure only Odds MCP is used (no ESPN).

Commands: odds <sport> [filters...]

chat_cli.py

ask <league> <date|today> <TEAM1> vs <TEAM2> <question...> → fire core_mcp.analyze_by_teams.

C) Adapters
Add adapters only where you need consistent rendering in game_cli.py:

Implement normalize(summary_json) per sport to produce a tidy dict.

Keep logic minimal; no totals unless ESPN provides them.

D) MCP server guardrails
Confirm sports_ai_mcp.py exposes:

getScoreboard, findEvents, getGameSummary, analyzeGameByTeams

Strict OpenRouter usage inside analyzeGameByTeams (already added)

.env.local loading and OPENROUTER_BASE_URL support (already added)

Timezone: optional—make today use America/Los_Angeles if desired.

Acceptance criteria
✅ Grep shows zero direct ESPN calls in /clients/**:

grep -R "site.api.espn.com" clients/ returns no matches.

✅ chat_cli.py:

ask nfl today ravens vs colts how did the qbs do? → returns QB lines matching ESPN’s summary.

✅ scoreboard_cli.py events epl 20250815 prints event IDs when EPL calendar starts.

✅ game_cli.py game mlb <EVENT_ID> --json outputs ESPN boxscore payload verbatim.

✅ Tests:

Adapters: pass with frozen samples.

Live MCP smoke tests pass (scoreboard + one game summary per enabled league).

Testing plan (quick)
Unit: adapters with saved ESPN summary JSON (no network).

Integration: run MCP locally; feature CLIs hit MCP only.

E2E: Chat client ask nfl today ravens vs colts ... → verify against live box score.

Migration notes
Keep existing “all-in-one” scripts for now; mark them legacy. New CLIs become the primary entry points.

Move OpenRouter strict prompt to one place (core_llm.py or MCP) so wording stays in sync.

Future enhancements (optional)
Add getStandingsLink/getNews passthroughs from MCP to clients.

Add --tz flag or default to America/Los_Angeles for “today”.

Add caching only for league/team lists (not scoreboards) if needed.

Reminder: lock it to MCP — no direct ESPN calls in clients.




MCP logging verbosity levels:

DEBUG: show full ESPN URLs and timing

INFO: only league/date/event and OK/ERR

Structured logging: output JSON logs if LOG_FORMAT=json for integration with log aggregation.

🛠 CLI UX & Productivity
--json flag everywhere in feature CLIs to dump raw MCP output (good for debugging adapters).

--fields flag in game CLI to output only selected columns (e.g., --fields=pts,reb,ast).

--pretty default for human-readable output with aligned columns.

Team/league autocomplete in chat CLI (optional, via prompt_toolkit).

🔄 Testing & CI
Integration smoke tests that:

Start MCP locally

Hit each data type CLI

Assert ok:true and non-empty data

Rate-limit aware: throttle ESPN calls in tests to avoid bans.

Skip live tests if no network or API key.

🌐 Timezone & Dates
Decide one canonical timezone for “today” (UTC vs. local).

In MCP, always return meta.date_used so clients know which date actually ran.

📈 Future-proofing
Play-by-play support in MCP (getPlayByPlay) for sports that have it → later you can generate advanced analytics.

Multi-event analysis: let analyzeGameByTeams accept a list of team pairs or event IDs for batch queries.

Odds + stats join in MCP: optional, but could be handy for “value play” queries.

