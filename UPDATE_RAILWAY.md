# 🚀 Update Railway with Environment Variables

## Current Status
- ✅ Your HTTP server is working perfectly on Railway
- ✅ Natural language interface is coded and ready
- ❓ OpenRouter API key needs to be verified/updated

## Update Railway Environment

Go to your Railway dashboard and add these environment variables:

### Required Variables:
```
SPORTS_API_KEY = 89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ
```

### For Natural Language Features:
```
OPENROUTER_API_KEY = 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
OPENROUTER_BASE_URL = https://openrouter.ai/api/v1
OPENROUTER_MODEL = openai/gpt-oss-20b:free
```

### For Odds Data:
```
ODDS_API_KEY = 85edbe8616f7887b660905e1ecde8600
```

## Steps to Update Railway:

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Select your project**: sports-mcp-server
3. **Go to Variables tab**
4. **Add each variable above**
5. **Click "Deploy"** to restart with new variables

## Test Natural Language (Once Variables Added):

```bash
curl -H "Authorization: Bearer 89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ" \
     -H "Content-Type: application/json" \
     -d '{"question":"What NBA teams are there?"}' \
     https://web-production-b939f.up.railway.app/ask
```

## OpenRouter API Key Issue

If the natural language features still don't work, you may need to:

1. **Check OpenRouter Account**: https://openrouter.ai/account
2. **Verify API Key**: Make sure it's active and has credits
3. **Generate New Key**: If needed, create a fresh API key

## Alternative: Use Without Natural Language

Your HTTP server works perfectly without the natural language features:

```bash
# This works right now:
curl -H "Authorization: Bearer 89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ" \
     -H "Content-Type: application/json" \
     -d '{"leagues":["basketball/nba"],"include_odds":false}' \
     https://web-production-b939f.up.railway.app/daily-intelligence
```

## What's Working Now

✅ **Railway Deployment**: https://web-production-b939f.up.railway.app
✅ **All Endpoints**: Health, Teams, Scoreboard, Daily Intelligence  
✅ **Authentication**: API key security
✅ **ESPN Integration**: 30 NBA teams, games data
✅ **Code Ready**: Natural language interface coded and deployed

The natural language features will work as soon as the OpenRouter API key is valid!