# Remote Access Setup Options

Your HTTP server is working perfectly locally! Here are your options for remote access:

## Option 1: ngrok (Recommended - Free Account Required)

### Quick Setup:
1. **Sign up** for free at: https://dashboard.ngrok.com/signup
2. **Get your auth token** from: https://dashboard.ngrok.com/get-started/your-authtoken
3. **Set your token**: `./ngrok.exe config add-authtoken YOUR_TOKEN`
4. **Start tunnel**: `./ngrok.exe http 8000`

### What you get:
- Public HTTPS URL like: `https://abc123.ngrok.io`
- Works from any machine anywhere
- Free tier: 1 online ngrok process, 40 connections/minute

## Option 2: LocalTunnel (No Account Required)

### Quick Setup:
```bash
npm install -g localtunnel
lt --port 8000 --subdomain sports-api-unique-name
```

### What you get:
- Public URL like: `https://sports-api-unique-name.loca.lt`
- No account required
- May be less reliable than ngrok

## Option 3: Cloudflare Tunnel (Free)

### Quick Setup:
1. Download cloudflared from: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
2. Run: `cloudflared tunnel --url http://localhost:8000`

### What you get:
- Public HTTPS URL 
- Free, no account needed for temporary tunnels
- Very reliable

## Option 4: Deploy to Railway (Production Ready)

### Quick Setup:
1. Push your code to GitHub
2. Connect Railway to your GitHub repo
3. Add environment variables
4. Deploy

### What you get:
- Permanent URL like: `https://your-app.railway.app`
- Always available (not just when your computer is on)
- Production-ready

## Current Status

✅ **HTTP Server**: Running on localhost:8000
✅ **API Key**: Configured and working
✅ **ESPN Integration**: Working (30 NBA teams found)
✅ **Daily Intelligence**: Working (found games)
✅ **Authentication**: Working

## Quick Test Commands

Once you have a public URL, test from any machine:

```bash
# Health check (no auth)
curl https://your-public-url.com/health

# Get NBA teams (with auth)
curl -H "Authorization: Bearer 89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ" \
     -H "Content-Type: application/json" \
     -d '{"sport":"basketball","league":"nba"}' \
     https://your-public-url.com/espn/teams

# Daily intelligence (with auth)  
curl -H "Authorization: Bearer 89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ" \
     -H "Content-Type: application/json" \
     -d '{"leagues":["basketball/nba","football/nfl"],"include_odds":false}' \
     https://your-public-url.com/daily-intelligence
```

## Discord Bot Example

```python
import requests

class SportsClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def get_daily_games(self, leagues):
        response = requests.post(f"{self.base_url}/daily-intelligence",
                               json={"leagues": leagues, "include_odds": False},
                               headers=self.headers)
        return response.json()

# Usage in Discord bot
client = SportsClient("https://your-public-url.com", "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ")

@bot.command()
async def daily(ctx):
    data = client.get_daily_games(["basketball/nba", "football/nfl"])
    # Process and send to Discord
```

Choose your preferred option and let's get you set up with remote access!