import requests

API_BASE = "https://api.the-odds-api.com/v4"
API_KEY = "76823225714dfa4618643fd701de3d3b"  # dummy tester key

def get_todays_wnba_event_id():
    url = f"{API_BASE}/sports/basketball_wnba/events"
    params = {"regions": "us", "apiKey": API_KEY}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    events = resp.json()
    if not events:
        raise ValueError("No WNBA games found today.")
    return events[0]["id"]

def fetch_marina_mabrey_props(event_id):
    markets = ",".join(["player_points", "player_rebounds", "player_assists", "player_threes"])
    url = f"{API_BASE}/sports/basketball_wnba/events/{event_id}/odds"
    params = {
        "regions": "us",
        "markets": markets,
        "oddsFormat": "decimal",
        "apiKey": API_KEY
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    
    results = {}
    for book in data.get("bookmakers", []):
        for m in book.get("markets", []):
            key = m.get("key")
            for outcome in m.get("outcomes", []):
                if "Marina Mabrey" in outcome.get("description", ""):
                    results.setdefault(key, []).append({
                        "bookmaker": book.get("title"),
                        "side": outcome.get("name"),  # Over/Under
                        "line": outcome.get("point"),
                        "price": outcome.get("price")
                    })
    return results

if __name__ == "__main__":
    try:
        event_id = get_todays_wnba_event_id()
        props = fetch_marina_mabrey_props(event_id)
        if props:
            import pprint; pprint.pprint(props)
        else:
            print("No prop data found for Marina Mabrey today.")
    except Exception as e:
        print("Error:", e)
