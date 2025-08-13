# test.py — BOS vs WAS 2024-10-24 (clean output, robust to camelCase schema)
from nba_api.stats.endpoints import leaguegamefinder, boxscoretraditionalv3
from nba_api.stats.static import teams
import pandas as pd

GAME_DATE   = "10/24/2024"          # mm/dd/yyyy
SEASON      = "2024-25"
SEASON_TYPE = "Regular Season"
HOME_ABBR   = "BOS"
AWAY_ABBR   = "WAS"

TARGET_PLAYERS = ["Jaylen Brown", "Jordan Poole"]

TEAM_SHOW = [
    ("teamTricode", "Team"),
    ("minutes", "MIN"),
    ("fieldGoalsMade", "FGM"),
    ("fieldGoalsAttempted", "FGA"),
    ("fieldGoalsPercentage", "FG%"),
    ("threePointersMade", "3PM"),
    ("threePointersAttempted", "3PA"),
    ("threePointersPercentage", "3P%"),
    ("freeThrowsMade", "FTM"),
    ("freeThrowsAttempted", "FTA"),
    ("freeThrowsPercentage", "FT%"),
    ("reboundsOffensive", "OREB"),
    ("reboundsDefensive", "DREB"),
    ("reboundsTotal", "REB"),
    ("assists", "AST"),
    ("steals", "STL"),
    ("blocks", "BLK"),
    ("turnovers", "TOV"),
    ("foulsPersonal", "PF"),
    ("points", "PTS"),
    ("plusMinusPoints", "+/-"),
]

PLAYER_SHOW = [
    ("teamTricode", "Team"),
    ("position", "POS"),
    ("minutes", "MIN"),
    ("fieldGoalsMade", "FGM"),
    ("fieldGoalsAttempted", "FGA"),
    ("fieldGoalsPercentage", "FG%"),
    ("threePointersMade", "3PM"),
    ("threePointersAttempted", "3PA"),
    ("threePointersPercentage", "3P%"),
    ("freeThrowsMade", "FTM"),
    ("freeThrowsAttempted", "FTA"),
    ("freeThrowsPercentage", "FT%"),
    ("reboundsOffensive", "OREB"),
    ("reboundsDefensive", "DREB"),
    ("reboundsTotal", "REB"),
    ("assists", "AST"),
    ("steals", "STL"),
    ("blocks", "BLK"),
    ("turnovers", "TOV"),
    ("foulsPersonal", "PF"),
    ("points", "PTS"),
    ("plusMinusPoints", "+/-"),
]

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

def load_box_camel(game_id: str):
    """Return (player_df, team_df) using normalized dict (camelCase schema)."""
    box = boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=game_id)
    nd = box.get_normalized_dict()
    bs = nd.get("boxScoreTraditional", {})
    player_df = pd.DataFrame(bs.get("playerStats", []))
    team_df   = pd.DataFrame(bs.get("teamStats", []))
    return player_df, team_df

def tidy_team(team_df: pd.DataFrame) -> pd.DataFrame:
    if team_df.empty:
        return team_df
    out = team_df.copy()
    # percent columns → pretty %
    for raw, label in TEAM_SHOW:
        if raw.endswith("Percentage") and raw in out.columns:
            out[raw] = (out[raw] * 100).round(1)
    # select & rename
    keep = [raw for raw, _ in TEAM_SHOW if raw in out.columns]
    out = out[keep].rename(columns=dict(TEAM_SHOW))
    return out

def normalize_name(s: str) -> str:
    return "".join(ch.lower() for ch in s if ch.isalnum() or ch.isspace()).strip()

def build_fullname(df: pd.DataFrame) -> pd.Series:
    first = df.get("firstName", pd.Series([""]*len(df)))
    last  = df.get("familyName", pd.Series([""]*len(df)))
    return (first.astype(str).str.strip() + " " + last.astype(str).str.strip()).str.strip()

def find_player_row(player_df: pd.DataFrame, target_name: str):
    if player_df.empty:
        return None
    names = build_fullname(player_df)
    df = player_df.copy()
    df["__FULLNAME"] = names
    # exact (case/space-insensitive)
    n_target = normalize_name(target_name)
    df["__NORM"] = df["__FULLNAME"].map(normalize_name)
    hit = df[df["__NORM"] == n_target]
    if hit.empty:
        # loose contains
        hit = df[df["__FULLNAME"].str.contains(target_name, case=False, regex=False, na=False)]
    return hit.iloc[0] if not hit.empty else None

def format_player_line(row: pd.Series) -> pd.Series:
    if row is None:
        return None
    out = {}
    # percentages scaled for display
    for raw, label in PLAYER_SHOW:
        val = row.get(raw)
        if raw.endswith("Percentage") and pd.notna(val):
            val = round(val * 100, 1)
        out[label] = val
    # prepend name
    out = {"Player": row.get("__FULLNAME", "")} | out
    return pd.Series(out)

def main():
    game_id, dbg = find_game_id_by_date(HOME_ABBR, AWAY_ABBR, GAME_DATE, SEASON, SEASON_TYPE)
    if not game_id:
        print(f"No game found for {AWAY_ABBR} @ {HOME_ABBR} on {GAME_DATE}")
        print("First few returned that day:\n", dbg[["GAME_ID","TEAM_ABBREVIATION","MATCHUP"]].head())
        return

    print(f"Found GAME_ID: {game_id} for {AWAY_ABBR} @ {HOME_ABBR} on {GAME_DATE}")

    player_df, team_df = load_box_camel(game_id)

    # ---- Team game stats (clean table) ----
    tidy = tidy_team(team_df)
    if tidy.empty:
        print("\n=== Team stats ===\n(no team stats returned)")
    else:
        print("\n=== Team stats ===")
        print(tidy.to_string(index=False))

    # ---- Player lines ----
    lines = []
    for name in TARGET_PLAYERS:
        row = find_player_row(player_df, name)
        if row is None:
            lines.append(pd.Series({"Player": f"{name} (NOT FOUND)"}))
        else:
            # inject computed full name for formatter
            row = row.copy()
            row["__FULLNAME"] = f"{row.get('firstName','')} {row.get('familyName','')}".strip()
            lines.append(format_player_line(row))

    print("\n=== Player lines ===")
    out_df = pd.DataFrame(lines)
    print(out_df.to_string(index=False))

if __name__ == "__main__":
    main()
