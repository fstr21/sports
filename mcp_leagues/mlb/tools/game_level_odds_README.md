# Odds MCP Tool: getOdds (Game-Level)

## Overview
The `getOdds` tool retrieves game-level betting odds for MLB games including moneylines, spreads (run lines), and totals (over/under). This provides live betting odds from multiple sportsbooks for standard game-level betting markets.

**Server URL**: `https://odds-mcp-v2-production.up.railway.app/mcp`  
**Tool Name**: `getOdds`

---

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `sport` | string | Yes | - | Sport key (use "baseball_mlb" for MLB) |
| `markets` | string | No | "h2h" | Comma-separated markets: "h2h", "spreads", "totals" |
| `regions` | string | No | "us" | Comma-separated regions: "us", "uk", "au", "eu" |
| `odds_format` | string | No | "american" | Odds format: "american" or "decimal" |

---

## Supported Markets

| Market | Description | Example |
|--------|-------------|---------|
| `h2h` | Moneylines (head-to-head) | Yankees -150, Red Sox +130 |
| `spreads` | Run lines (point spreads) | Yankees -1.5 (+110), Red Sox +1.5 (-130) |
| `totals` | Over/Under total runs | Over 8.5 (-110), Under 8.5 (-110) |

---

## Usage Examples

### Get Moneylines Only
```python
import httpx
import json

payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
        "name": "getOdds",
        "arguments": {
            "sport": "baseball_mlb",
            "markets": "h2h",
            "regions": "us"
        }
    }
}

async with httpx.AsyncClient() as client:
    response = await client.post("https://odds-mcp-v2-production.up.railway.app/mcp", json=payload)
    result = response.json()
```

### Get All Three Markets
```python
payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
        "name": "getOdds",
        "arguments": {
            "sport": "baseball_mlb",
            "markets": "h2h,spreads,totals",
            "regions": "us"
        }
    }
}
```

### Get Decimal Odds
```python
payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
        "name": "getOdds",
        "arguments": {
            "sport": "baseball_mlb",
            "markets": "h2h,spreads,totals",
            "odds_format": "decimal",
            "regions": "us"
        }
    }
}
```

---

## Response Structure

### Success Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": true,
    "content_md": "## Odds for baseball_mlb\n\nFound 7 games",
    "data": {
      "odds": [
        {
          "id": "91c0e5b89cd6f0f7bb77acfa35024f98",
          "sport_key": "baseball_mlb",
          "commence_time": "2025-08-14T20:40:00Z",
          "home_team": "Colorado Rockies",
          "away_team": "Arizona Diamondbacks",
          "bookmakers": [
            {
              "key": "fanduel",
              "title": "FanDuel",
              "last_update": "2025-08-14T19:30:15Z",
              "markets": [
                {
                  "key": "h2h",
                  "outcomes": [
                    {
                      "name": "Arizona Diamondbacks",
                      "price": -184
                    },
                    {
                      "name": "Colorado Rockies",
                      "price": 154
                    }
                  ]
                },
                {
                  "key": "spreads",
                  "outcomes": [
                    {
                      "name": "Arizona Diamondbacks",
                      "price": -126,
                      "point": -1.5
                    },
                    {
                      "name": "Colorado Rockies",
                      "price": 105,
                      "point": 1.5
                    }
                  ]
                },
                {
                  "key": "totals",
                  "outcomes": [
                    {
                      "name": "Over",
                      "price": -105,
                      "point": 11.5
                    },
                    {
                      "name": "Under",
                      "price": -115,
                      "point": 11.5
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    "meta": {
      "timestamp": "2025-08-14T19:35:00.123456+00:00"
    }
  }
}
```

---

## Data Fields

### Root Level
- `ok` (boolean): Success indicator
- `content_md` (string): Markdown summary of results
- `data` (object): Main data payload with `odds` array
- `meta` (object): Request metadata

### Game Object (in odds array)
- `id` (string): Unique event identifier for this game
- `sport_key` (string): Always "baseball_mlb" for MLB
- `commence_time` (string): Game start time in UTC ISO 8601 format
- `home_team` (string): Home team name
- `away_team` (string): Away team name
- `bookmakers` (array): List of sportsbook odds

### Bookmaker Object
- `key` (string): Sportsbook identifier ("fanduel", "draftkings", etc.)
- `title` (string): Sportsbook display name
- `last_update` (string): When odds were last updated (UTC)
- `markets` (array): Available betting markets

### Market Object
- `key` (string): Market type ("h2h", "spreads", "totals")
- `outcomes` (array): Betting options for this market

### Outcome Object
- `name` (string): Team name or "Over"/"Under" for totals
- `price` (number): Odds in American format (-150, +130) or decimal (1.67, 2.30)
- `point` (number): Point spread or total (only for spreads/totals markets)

---

## Common Sportsbooks

| Key | Title | Availability |
|-----|-------|--------------|
| `fanduel` | FanDuel | Most common |
| `draftkings` | DraftKings | Very common |
| `mybookie_ag` | MyBookie.ag | Common |
| `betmgm` | BetMGM | Common |
| `betrivers` | BetRivers | Less common |
| `pointsbetus` | PointsBet | Less common |

---

## Odds Formats

### American Odds (Default)
- Negative: Favorite (bet $150 to win $100 = -150)
- Positive: Underdog (bet $100 to win $130 = +130)

### Decimal Odds
- Multiply stake by decimal for total return
- Example: 1.67 = bet $100, get back $167 ($67 profit)

---

## Market-Specific Details

### Moneylines (h2h)
- Simple win/lose bets
- Two outcomes: home team or away team
- No point spreads involved

### Spreads (Run Lines)
- Home/away team must cover the spread
- Typically ±1.5 runs in MLB
- Both teams have odds and point values

### Totals (Over/Under)
- Bet on total runs scored by both teams
- Two outcomes: "Over" or "Under" a set number
- Same point value for both outcomes

---

## Error Handling

### Invalid Sport
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": false,
    "error": "Invalid sport key"
  }
}
```

### No Games Available
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": true,
    "data": {
      "odds": []
    }
  }
}
```

### API Quota Exceeded
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "ok": false,
    "error": "The Odds API quota exceeded"
  }
}
```

---

## Testing Notes

### Verified Functionality ✅
- **Moneylines**: Successfully retrieves h2h odds from multiple sportsbooks
- **Spreads**: Run line odds with point spreads (typically ±1.5)
- **Totals**: Over/under odds with total run predictions
- **Combined markets**: All three markets in single call
- **Multiple sportsbooks**: FanDuel, DraftKings, MyBookie typically available
- **Real-time data**: Odds update frequently during active betting periods

### Data Consistency
- Event IDs match across different market calls for same game
- Team names consistent with MLB schedule data
- Commence times in UTC, easily convertible to local time
- American odds format widely supported

---

## Integration Example

```python
import httpx
import json
import asyncio

async def get_mlb_odds_summary():
    """Get comprehensive MLB betting odds"""
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getOdds",
            "arguments": {
                "sport": "baseball_mlb",
                "markets": "h2h,spreads,totals",
                "regions": "us"
            }
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://odds-mcp-v2-production.up.railway.app/mcp",
            json=payload
        )
        result = response.json()
        
        if result["result"]["ok"]:
            games = result["result"]["data"]["odds"]
            
            print(f"Found odds for {len(games)} games:")
            
            for game in games:
                away = game["away_team"]
                home = game["home_team"]
                
                print(f"\n{away} @ {home}")
                
                # Get first bookmaker
                if game["bookmakers"]:
                    bookie = game["bookmakers"][0]
                    print(f"  {bookie['title']}:")
                    
                    for market in bookie["markets"]:
                        market_name = market["key"]
                        print(f"    {market_name}:")
                        
                        for outcome in market["outcomes"]:
                            name = outcome["name"]
                            price = outcome["price"]
                            point = outcome.get("point", "")
                            
                            if point:
                                print(f"      {name} {point:+g}: {price}")
                            else:
                                print(f"      {name}: {price}")
        
        return games

# Run it
asyncio.run(get_mlb_odds_summary())
```

---

## Rate Limiting

- **API Usage**: Managed by server
- **Request Frequency**: No specific limits on calls
- **Data Freshness**: Updates every few minutes during active periods
- **Peak Times**: Most active 2-4 hours before game time

---

## Summary

**Primary Use**: Game-level MLB betting odds retrieval  
**Reliability**: ✅ Production ready  
**Response Time**: < 3 seconds typical  
**Data Source**: The Odds API (aggregates multiple sportsbooks)  
**Markets Supported**: Moneylines, spreads, totals  
**Sportsbook Coverage**: 5-8 major US sportsbooks per game