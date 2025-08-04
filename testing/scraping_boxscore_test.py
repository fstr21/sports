#!/usr/bin/env python3
import sys
import httpx
from typing import Any, Dict, List, Optional

BOX_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/summary"

def fetch_boxscore(event_id: str) -> Dict[str, Any]:
    headers = {
        "User-Agent": "Mozilla/5.0 (WNBA-Box-Reader)",
        "Accept": "application/json, text/plain, */*",
    }
    with httpx.Client(headers=headers, timeout=20.0) as client:
        r = client.get(BOX_URL, params={"event": event_id})
        r.raise_for_status()
        return r.json()

def parse_statline(stats: Dict[str, Any]) -> Dict[str, Any]:
    # ESPN stats fields often include these keys
    # Some players may have partial keys depending on minutes/DNP
    return {
        "min": stats.get("minutes", ""),
        "fg": stats.get("fieldGoalsMade", 0), "fga": stats.get("fieldGoalsAttempted", 0),
        "3pm": stats.get("threePointFieldGoalsMade", 0), "3pa": stats.get("threePointFieldGoalsAttempted", 0),
        "ftm": stats.get("freeThrowsMade", 0), "fta": stats.get("freeThrowsAttempted", 0),
        "oreb": stats.get("offensiveRebounds", 0),
        "dreb": stats.get("defensiveRebounds", 0),
        "reb": stats.get("rebounds", 0),
        "ast": stats.get("assists", 0),
        "stl": stats.get("steals", 0),
        "blk": stats.get("blocks", 0),
        "to": stats.get("turnovers", 0),
        "pf": stats.get("fouls", 0),
        "+/-": stats.get("plusMinus", 0),
        "pts": stats.get("points", 0),
        "didNotPlay": stats.get("didNotPlay", False),
        "didNotDress": stats.get("didNotDress", False),
        "reason": stats.get("reason", ""),
        "starter": stats.get("starter", False),
    }

def format_player_row(p: Dict[str, Any]) -> str:
    name = p.get("athlete", {}).get("displayName", "Unknown")
    jersey = p.get("athlete", {}).get("jersey", "")
    stats = parse_statline(p.get("statistics", {}))

    if stats["didNotPlay"] or stats["didNotDress"]:
        reason = stats["reason"] or ("DNP" if stats["didNotPlay"] else "DND")
        return f"{name} #{jersey if jersey else ''} — {reason}".strip()

    # Condensed FG/3PT/FT strings
    fg = f'{stats["fg"]}-{stats["fga"]}'
    tp = f'{stats["3pm"]}-{stats["3pa"]}'
    ft = f'{stats["ftm"]}-{stats["fta"]}'

    return (
        f'{name} #{jersey if jersey else ""} | '
        f'MIN {stats["min"]} | FG {fg} | 3PT {tp} | FT {ft} | '
        f'OREB {stats["oreb"]} | DREB {stats["dreb"]} | REB {stats["reb"]} | '
        f'AST {stats["ast"]} | STL {stats["stl"]} | BLK {stats["blk"]} | '
        f'TO {stats["to"]} | PF {stats["pf"]} | +/- {stats["+/-"]} | PTS {stats["pts"]}'
    ).strip()

def print_team_section(team_block: Dict[str, Any]) -> None:
    header_team = team_block.get("team", {}).get("displayName") or team_block.get("team", {}).get("name", "Unknown Team")
    print(f"\n=== {header_team} ===")

    # Players can be split under "starters" and "bench" or a flat "players"
    starters: List[Dict[str, Any]] = team_block.get("starters", [])
    bench: List[Dict[str, Any]] = team_block.get("bench", [])
    players: List[Dict[str, Any]] = team_block.get("players", [])

    if starters or bench:
        if starters:
            print("\nStarters:")
            for p in starters:
                print(" - " + format_player_row(p))
        if bench:
            print("\nBench:")
            for p in bench:
                print(" - " + format_player_row(p))
    elif players:
        # Fallback shape
        print("\nPlayers:")
        for p in players:
            print(" - " + format_player_row(p))
    else:
        print("No player data found.")

    # Team totals if available
    totals = team_block.get("statistics", {})
    if totals:
        t = parse_statline(totals)
        fg = f'{t["fg"]}-{t["fga"]}'
        tp = f'{t["3pm"]}-{t["3pa"]}'
        ft = f'{t["ftm"]}-{t["fta"]}'
        print(
            "\nTeam Totals:"
            f"\n FG {fg} | 3PT {tp} | FT {ft}"
            f"\n REB {t['reb']} (OREB {t['oreb']}, DREB {t['dreb']})"
            f"\n AST {t['ast']} | STL {t['stl']} | BLK {t['blk']} | TO {t['to']} | PF {t['pf']} | PTS {t['pts']}"
        )

def main(event_id: str = "401736292") -> None:
    box = fetch_boxscore(event_id)

    # Score header (optional)
    header = box.get("header", {})
    comps = header.get("competitions", [{}])
    comp = comps[0] if comps else {}
    teams_hdr = comp.get("competitors", [])

    if teams_hdr and len(teams_hdr) == 2:
        a = teams_hdr[0]
        b = teams_hdr[1]
        def team_line(x):
            return f'{x.get("team", {}).get("displayName", "Team")} {x.get("score","")}'
        print(f"{team_line(a)} vs {team_line(b)}")
        print(f"Status: {header.get('competitions',[{}])[0].get('status',{}).get('type',{}).get('description','')}")

    # Box teams section
    box_teams: List[Dict[str, Any]] = box.get("boxscore", {}).get("teams", []) or box.get("teams", [])
    if not box_teams:
        print("\nNo team boxscore data found.")
        return

    for tb in box_teams:
        print_team_section(tb)

if __name__ == "__main__":
    # Allow passing a different game id: python espn_wnba_boxscore.py 401736292
    ev = sys.argv[1] if len(sys.argv) > 1 else "401736292"
    main(ev)