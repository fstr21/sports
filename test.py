# test.py — WAS @ BOS on 2024-10-24
# Robust: tries BoxScoreTraditionalV3 first, falls back to V2; normalizes output; clean printing.

from nba_api.stats.endpoints import leaguegamefinder, boxscoretraditionalv3, boxscoretraditionalv2
import pandas as pd

GAME_DATE   = "10/24/2024"          # mm/dd/yyyy
SEASON      = "2024-25"
SEASON_TYPE = "Regular Season"
HOME_ABBR   = "BOS"
AWAY_ABBR   = "WAS"

TARGET_PLAYERS = ["Jaylen Brown", "Jordan Poole"]

# ---- Find game id by date/teams ----
def find_game_id_by_date(home_abbr, away_abbr, game_date, season, season_type):
    lgf = leaguegamefinder.LeagueGameFinder(
        season_nullable=season,
        season_type_nullable=season_type,
        date_from_nullable=game_date,
        date_to_nullable=game_date
    )
    df = lgf.get_data_frames()[0]
    home_rows = df[(df["TEAM_ABBREVIATION"] == home_abbr) & (df["MATCHUP"].str.contains(r"vs\."))]
    if home_rows.empty:
        mask = df["MATCHUP"].str.contains(home_abbr) & df["MATCHUP"].str.contains(away_abbr)
        home_rows = df[mask]
    if home_rows.empty:
        return None, df
    home_rows = home_rows[home_rows["MATCHUP"].str.contains(away_abbr)]
    if home_rows.empty:
        return None, df
    return str(home_rows.iloc[0]["GAME_ID"]), df

# ---- Load box: try V3 (camelCase), then V2 (ALL_CAPS) ----
def load_box_any(game_id: str):
    # Try V3 (camelCase)
    try:
        b3 = boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=game_id)
        nd = b3.get_normalized_dict()
        box = nd.get("boxScoreTraditional", {})
        p3 = pd.DataFrame(box.get("playerStats", []))
        t3 = pd.DataFrame(box.get("teamStats",   []))
        if not p3.empty or not t3.empty:
            return {"ver": "v3", "player": p3, "team": t3}
    except Exception:
        pass

    # Fallback to V2 (ALL_CAPS)
    b2 = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
    dfs = b2.get_data_frames()  # [PlayerStats, TeamStats]
    p2 = dfs[0].copy() if len(dfs) > 0 else pd.DataFrame()
    t2 = dfs[1].copy() if len(dfs) > 1 else pd.DataFrame()
    return {"ver": "v2", "player": p2, "team": t2}

# ---- Normalize to common column names for display ----
TEAM_MAP_V3 = {
    "teamTricode":"TEAM", "minutes":"MIN",
    "fieldGoalsMade":"FGM","fieldGoalsAttempted":"FGA","fieldGoalsPercentage":"FG%",
    "threePointersMade":"3PM","threePointersAttempted":"3PA","threePointersPercentage":"3P%",
    "freeThrowsMade":"FTM","freeThrowsAttempted":"FTA","freeThrowsPercentage":"FT%",
    "reboundsOffensive":"OREB","reboundsDefensive":"DREB","reboundsTotal":"REB",
    "assists":"AST","steals":"STL","blocks":"BLK","turnovers":"TOV",
    "foulsPersonal":"PF","points":"PTS","plusMinusPoints":"+/-",
}
TEAM_ORDER = ["TEAM","MIN","FGM","FGA","FG%","3PM","3PA","3P%","FTM","FTA","FT%","OREB","DREB","REB","AST","STL","BLK","TOV","PF","PTS","+/-"]

TEAM_MAP_V2 = {
    "TEAM_ABBREVIATION":"TEAM","MIN":"MIN","FGM":"FGM","FGA":"FGA","FG_PCT":"FG%",
    "FG3M":"3PM","FG3A":"3PA","FG3_PCT":"3P%","FTM":"FTM","FTA":"FTA","FT_PCT":"FT%",
    "OREB":"OREB","DREB":"DREB","REB":"REB","AST":"AST","STL":"STL","BLK":"BLK","TOV":"TOV",
    "PF":"PF","PTS":"PTS","PLUS_MINUS":"+/-",
}

PLAYER_MAP_V3 = {
    "teamTricode":"TEAM","position":"POS","minutes":"MIN",
    "fieldGoalsMade":"FGM","fieldGoalsAttempted":"FGA","fieldGoalsPercentage":"FG%",
    "threePointersMade":"3PM","threePointersAttempted":"3PA","threePointersPercentage":"3P%",
    "freeThrowsMade":"FTM","freeThrowsAttempted":"FTA","freeThrowsPercentage":"FT%",
    "reboundsOffensive":"OREB","reboundsDefensive":"DREB","reboundsTotal":"REB",
    "assists":"AST","steals":"STL","blocks":"BLK","turnovers":"TOV",
    "foulsPersonal":"PF","points":"PTS","plusMinusPoints":"+/-",
    # name fields handled separately (firstName/familyName)
}
PLAYER_ORDER = ["Player","TEAM","POS","MIN","FGM","FGA","FG%","3PM","3PA","3P%","FTM","FTA","FT%","OREB","DREB","REB","AST","STL","BLK","TOV","PF","PTS","+/-"]

PLAYER_MAP_V2 = {
    "PLAYER_NAME":"Player","TEAM_ABBREVIATION":"TEAM","START_POSITION":"POS","MIN":"MIN",
    "FGM":"FGM","FGA":"FGA","FG_PCT":"FG%","FG3M":"3PM","FG3A":"3PA","FG3_PCT":"3P%",
    "FTM":"FTM","FTA":"FTA","FT_PCT":"FT%","OREB":"OREB","DREB":"DREB","REB":"REB",
    "AST":"AST","STL":"STL","BLK":"BLK","TOV":"TOV","PF":"PF","PTS":"PTS","PLUS_MINUS":"+/-",
}

def pct_fmt(df: pd.DataFrame, cols: list[str]):
    for c in cols:
        if c in df.columns:
            df[c] = (df[c] * 100).round(1)
    return df

def normalize_team(df: pd.DataFrame, ver: str) -> pd.DataFrame:
    if df.empty: return df
    if ver == "v3":
        out = df.copy()
        out = pct_fmt(out, ["fieldGoalsPercentage","threePointersPercentage","freeThrowsPercentage"])
        out = out[[c for c in TEAM_MAP_V3 if c in out.columns]].rename(columns=TEAM_MAP_V3)
        return out[ [c for c in TEAM_ORDER if c in out.columns] ]
    else:
        out = df.copy()
        out = pct_fmt(out, [])  # already as fraction? in V2 FG_PCT is 0.xx; convert to %
        for c in ["FG_PCT","FG3_PCT","FT_PCT"]:
            if c in out.columns: out[c] = (out[c] * 100).round(1)
        out = out[[c for c in TEAM_MAP_V2 if c in out.columns]].rename(columns=TEAM_MAP_V2)
        return out[ [c for c in TEAM_ORDER if c in out.columns] ]

def normalize_player(df: pd.DataFrame, ver: str) -> pd.DataFrame:
    if df.empty: return df
    if ver == "v3":
        out = df.copy()
        # build Player name
        first = out.get("firstName", pd.Series([""]*len(out))).astype(str).str.strip()
        last  = out.get("familyName", pd.Series([""]*len(out))).astype(str).str.strip()
        out["Player"] = (first + " " + last).str.strip()
        # percentages
        out = pct_fmt(out, ["fieldGoalsPercentage","threePointersPercentage","freeThrowsPercentage"])
        mapped_cols = [c for c in PLAYER_MAP_V3 if c in out.columns]
        out = out[ ["Player"] + mapped_cols ].rename(columns=PLAYER_MAP_V3)
        # ensure column order
        order = [c for c in PLAYER_ORDER if c in out.columns]
        return out[order]
    else:
        out = df.copy()
        # convert percent to % first
        for c in ["FG_PCT","FG3_PCT","FT_PCT"]:
            if c in out.columns: out[c] = (out[c]*100).round(1)
        # select and rename columns
        available_cols = [c for c in PLAYER_MAP_V2 if c in out.columns]
        out = out[available_cols].rename(columns=PLAYER_MAP_V2)
        order = [c for c in PLAYER_ORDER if c in out.columns]
        return out[order]

def find_player_line(players_df: pd.DataFrame, targets: list[str]) -> pd.DataFrame:
    if players_df.empty: 
        return pd.DataFrame({"Player":[f"{t} (NOT FOUND)"] for t in targets})
    names = players_df["Player"].astype(str).str.casefold()
    lines = []
    for t in targets:
        mask = names == t.casefold()
        row = players_df[mask].head(1)
        if row.empty:
            # loose contains
            row = players_df[names.str.contains(t.lower(), na=False)].head(1)
        if row.empty:
            lines.append(pd.Series({"Player": f"{t} (NOT FOUND)"}))
        else:
            lines.append(row.iloc[0])
    return pd.DataFrame(lines)

def main():
    game_id, dbg = find_game_id_by_date(HOME_ABBR, AWAY_ABBR, GAME_DATE, SEASON, SEASON_TYPE)
    if not game_id:
        print(f"No game found for {AWAY_ABBR} @ {HOME_ABBR} on {GAME_DATE}")
        print("First few that day:\n", dbg[["GAME_ID","TEAM_ABBREVIATION","MATCHUP"]].head())
        return

    print(f"Found GAME_ID: {game_id} for {AWAY_ABBR} @ {HOME_ABBR} on {GAME_DATE}")

    box = load_box_any(game_id)
    ver, pdf, tdf = box["ver"], box["player"], box["team"]

    team_tidy = normalize_team(tdf, ver)
    player_tidy = normalize_player(pdf, ver)

    # --- Output ---
    if team_tidy.empty:
        print("\n=== Team stats ===\n(no team stats returned)")
    else:
        print("\n=== Team stats ===")
        print(team_tidy.to_string(index=False))

    print("\n=== Player lines ===")
    out = find_player_line(player_tidy, TARGET_PLAYERS)
    print(out.to_string(index=False))

if __name__ == "__main__":
    main()
