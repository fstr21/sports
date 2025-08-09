# Railway Deployment Guide

## 🚀 Deploy Your Sports HTTP Server to Railway

Railway will give you a permanent URL like `https://your-app.railway.app` that works 24/7 from anywhere.

### 📋 Prerequisites

1. ✅ **GitHub Account** - Free at https://github.com
2. ✅ **Railway Account** - Free at https://railway.app (sign up with GitHub)
3. ✅ **Your Code** - Already ready in this directory!

### 🛠️ Step 1: Prepare Your Repository

#### A. Create GitHub Repository

1. Go to https://github.com and click **"New Repository"**
2. Name it: `sports-mcp-server`
3. Make it **Public** (or Private if you prefer)
4. **Don't** initialize with README (we have files already)
5. Click **"Create Repository"**

#### B. Push Your Code to GitHub

```bash
# In your sports directory, run these commands:

# Initialize git (if not already)
git init

# Copy the gitignore file
copy gitignore_for_railway .gitignore

# Add all files
git add .

# Commit with a message
git commit -m "Initial commit: Sports HTTP Server for Railway"

# Connect to your GitHub repo (replace YOUR_USERNAME and YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/sports-mcp-server.git

# Push to GitHub
git push -u origin main
```

### 🚂 Step 2: Deploy to Railway

#### A. Connect Railway to GitHub

1. Go to https://railway.app and **sign in with GitHub**
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `sports-mcp-server` repository
5. Click **"Deploy Now"**

#### B. Set Environment Variables

Railway will start building, but it needs your environment variables:

1. In Railway dashboard, go to your project
2. Click the **"Variables"** tab
3. Add these variables:

```
SPORTS_API_KEY = 89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ
```

**Optional variables** (add if you have them):
```
OPENROUTER_API_KEY = your-openrouter-key-here
ODDS_API_KEY = your-odds-api-key-here
```

4. Click **"Deploy"** to redeploy with the new variables

### 🌐 Step 3: Get Your URL

1. Railway will automatically assign you a URL like: `https://sports-mcp-server-production-xxxx.up.railway.app`
2. Find it in the **"Deployments"** tab or **"Settings"** tab
3. Test it by visiting: `https://your-url.railway.app/health`

### 🧪 Step 4: Test Your Deployment

```bash
# Test health endpoint (no auth required)
curl https://your-railway-url.railway.app/health

# Test NBA teams (with auth)
curl -H "Authorization: Bearer 89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ" \
     -H "Content-Type: application/json" \
     -d '{"sport":"basketball","league":"nba"}' \
     https://your-railway-url.railway.app/espn/teams

# Test daily intelligence
curl -H "Authorization: Bearer 89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ" \
     -H "Content-Type: application/json" \
     -d '{"leagues":["basketball/nba"],"include_odds":false}' \
     https://your-railway-url.railway.app/daily-intelligence
```

### 📱 Step 5: Use From Any Device

Now you can use your API from anywhere:

#### Discord Bot
```python
import requests

# Your permanent Railway URL
BASE_URL = "https://your-railway-url.railway.app"
API_KEY = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"

headers = {"Authorization": f"Bearer {API_KEY}"}

@bot.command()
async def nba(ctx):
    response = requests.post(f"{BASE_URL}/daily-intelligence",
                           json={"leagues": ["basketball/nba"], "include_odds": False},
                           headers=headers)
    data = response.json()
    # Process and send to Discord
```

#### Web App
```javascript
// From your web app frontend
const API_KEY = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ";
const BASE_URL = "https://your-railway-url.railway.app";

fetch(`${BASE_URL}/daily-intelligence`, {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        leagues: ["basketball/nba", "football/nfl"],
        include_odds: false
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

#### Python Script (Any Machine)
```python
import requests

client = requests.Session()
client.headers.update({
    "Authorization": "Bearer 89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"
})

# Get daily sports intelligence
response = client.post("https://your-railway-url.railway.app/daily-intelligence", 
                      json={"leagues": ["basketball/nba", "football/nfl"]})
data = response.json()
print(f"Found {len(data['data'])} leagues")
```

### 💰 Railway Pricing

- **Free Tier**: $5/month in credits (covers most personal use)
- **Usage-based**: Only pay for what you use
- **Typical costs for your API**: $1-3/month (very light usage)

### 🔄 Updating Your Code

When you make changes:

```bash
# Make your changes to the code
# Then push to GitHub:
git add .
git commit -m "Update API features"
git push

# Railway automatically redeploys when you push to GitHub!
```

### 🐛 Troubleshooting

#### Build Fails
- Check the build logs in Railway dashboard
- Make sure `requirements-railway.txt` has all needed packages

#### Server Won't Start
- Check you set `SPORTS_API_KEY` environment variable
- Look at the deployment logs

#### API Returns Errors
- Check the service logs in Railway dashboard
- Test locally first with `python sports_http_server.py`

### 📊 Monitoring

Railway provides:
- **Logs**: See all server output and errors
- **Metrics**: CPU, memory, network usage
- **Deployments**: History of all deployments
- **Custom Domain**: Add your own domain if desired

### 🎯 Success!

Once deployed, you'll have:
- ✅ **Permanent URL** that never changes
- ✅ **24/7 availability** (doesn't depend on your computer)
- ✅ **Automatic scaling** (handles traffic spikes)
- ✅ **Free SSL/HTTPS** (secure by default)
- ✅ **Easy updates** (just push to GitHub)

Your HTTP server is now accessible from any machine, any programming language, anywhere in the world!

## 🔗 Quick Links

- **Railway Dashboard**: https://railway.app/dashboard
- **Your Deployments**: https://railway.app/project/YOUR_PROJECT_ID
- **GitHub Repository**: https://github.com/YOUR_USERNAME/sports-mcp-server
- **API Documentation**: See `MCP_Methods_Reference.md` in your project