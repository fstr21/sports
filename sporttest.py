import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from the standalone functions
from sports_functions_standalone import get_scoreboard, get_teams, get_news, analyze_wnba_games

TODAY = datetime.utcnow().strftime("%Y%m%d")

TEST_CASES: List[Dict] = [
    {"fn": get_scoreboard, "args": {"sport": "basketball", "league": "wnba", "dates": TODAY}},
    {"fn": get_scoreboard, "args": {"sport": "basketball", "league": "nba", "dates": TODAY}},
    {"fn": get_scoreboard, "args": {"sport": "baseball", "league": "mlb", "dates": TODAY}},
    {"fn": get_scoreboard, "args": {"sport": "hockey", "league": "nhl", "dates": TODAY}},
    {"fn": get_scoreboard, "args": {"sport": "football", "league": "nfl", "dates": TODAY, "seasontype": 2}},
    {"fn": get_scoreboard, "args": {"sport": "football", "league": "college-football", "dates": TODAY, "seasontype": 2}},
    {"fn": get_scoreboard, "args": {"sport": "basketball", "league": "mens-college-basketball", "dates": TODAY}},
    {"fn": get_scoreboard, "args": {"sport": "soccer", "league": "usa.1", "dates": TODAY}},
    {"fn": get_scoreboard, "args": {"sport": "soccer", "league": "eng.1", "dates": TODAY}},
    {"fn": get_teams, "args": {"sport": "basketball", "league": "wnba"}},
    {"fn": get_news, "args": {"sport": "basketball", "league": "wnba"}},
    {"fn": analyze_wnba_games, "args": {"dates": TODAY, "analysis_type": "general"}},
]

async def run_case(case: Dict) -> Dict:
    fn = case["fn"]
    args = case["args"]
    try:
        result = await fn(**args)
    except Exception as e:
        return {"name": fn.__name__, "ok": False, "error": f"exception: {e}"}
    ok = bool(result.get("ok"))
    diag = {
        "name": fn.__name__,
        "ok": ok,
        "count": len(result.get("games", [])) if ok and "games" in result else len(result.get("teams", [])) if ok and "teams" in result else len(result.get("news", [])) if ok and "news" in result else None,
        "meta": result.get("meta"),
        "error": None if ok else result,
    }
    # minimal schema checks
    if ok and "content_md" not in result:
        diag["ok"] = False
        diag["error"] = {"message": "missing content_md"}
    return diag

async def main():
    results = await asyncio.gather(*(run_case(c) for c in TEST_CASES))
    print("\n=== SPORTS MCP TEST SUMMARY ===")
    passed = 0
    for r in results:
        if r["ok"]:
            passed += 1
            print(f"PASS {r['name']} | count={r['count']} meta={r.get('meta',{})}")
        else:
            print(f"FAIL {r['name']} -> {r['error']}")
    print(f"\n{passed}/{len(results)} passed")

if __name__ == "__main__":
    asyncio.run(main())