import requests
from pprint import pprint

API_BASE = "https://api.the-odds-api.com/v4"
API_KEY = "76823225714dfa4618643fd701de3d3b"  # dummy tester key

def get_todays_mlb_event_id():
    resp = requests.get(f"{API_BASE}/sports/baseball_mlb/events", params={"regions": "us", "apiKey": API_KEY})
    resp.raise_for_status()
    events = resp.json()
    if not events:
        raise ValueError("No MLB games found for today.")
    return events[0]["id"]

def fetch_player_and_pitcher_props(event_id):
    markets = ["batter_home_runs", "batter_hits", "pitcher_strikeouts"]
    params = {
        "regions": "us",
        "markets": ",".join(markets),
        "oddsFormat": "decimal",
        "apiKey": API_KEY
    }
    resp = requests.get(f"{API_BASE}/sports/baseball_mlb/events/{event_id}/odds", params=params)
    resp.raise_for_status()
    data = resp.json()

    results = {"batter_props": {}, "pitcher_props": {}}
    
    for book in data.get("bookmakers", []):
        bm = book.get("title")
        for m in book.get("markets", []):
            mk = m.get("key")
            for o in m.get("outcomes", []):
                desc = o.get("description", "")
                side_info = {
                    "bookmaker": bm,
                    "side": o.get("name"),
                    "line": o.get("point"),
                    "price": o.get("price")
                }

                if mk.startswith("batter_") and "Kyle Schwarber" in desc:
                    results["batter_props"].setdefault(mk, []).append(side_info)
                elif mk == "pitcher_strikeouts" and "Andrew Abbott" in desc:
                    results["pitcher_props"].setdefault(mk, []).append(side_info)

    return results

if __name__ == "__main__":
    try:
        event_id = get_todays_mlb_event_id()
        props = fetch_player_and_pitcher_props(event_id)
        print("=== Kyle Schwarber Batter Props ===")
        pprint(props.get("batter_props") or "No prop data found for Kyle Schwarber today.")
        print("\n=== Andrew Abbott Pitcher Props ===")
        pprint(props.get("pitcher_props") or "No prop data found for Andrew Abbott today.")
    except Exception as e:
        print("Error:", e)
