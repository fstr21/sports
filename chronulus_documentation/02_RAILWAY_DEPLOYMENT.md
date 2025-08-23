# 🚀 Railway Deployment Guide

Complete guide for deploying Chronulus MCP server to Railway.

## Current Production Deployment

- **URL**: `https://chronulusmcp-production.up.railway.app`
- **Health Check**: `https://chronulusmcp-production.up.railway.app/health`
- **MCP Endpoint**: `https://chronulusmcp-production.up.railway.app/mcp`
- **Status**: ✅ Fully Operational

## 1. Railway Account Setup

### Prerequisites
- Railway account (https://railway.app)
- GitHub repository with your code
- Railway CLI (optional, for advanced usage)

### Login to Railway
1. Go to https://railway.app/dashboard
2. Sign in with GitHub
3. Connect your repository

## 2. Project Creation

### Option A: Deploy from GitHub (Recommended)
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose repository: `fstr21/sports` (or your fork)
4. **Root Directory**: `mcp_leagues/chronulus`
5. **Branch**: `main`

### Option B: Railway CLI
```bash
cd mcp_leagues/chronulus
railway login
railway init
railway up
```

## 3. Environment Configuration

### Required Environment Variables
Set in Railway Dashboard → Variables tab:

```
CHRONULUS_API_KEY=your_chronulus_api_key_here
PORT=8080
```

### Optional Environment Variables
```
RAILWAY_ENVIRONMENT=production
LOG_LEVEL=INFO
```

## 4. Deployment Configuration

### Automatic Configuration (railway.toml)
Railway uses our `railway.toml` file:

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python chronulus_mcp_server.py"
healthcheckPath = "/"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10

[env]
PORT = "8080"
```

### Manual Configuration (if needed)
If `railway.toml` is missing, configure manually:

1. **Build Command**: `pip install -r requirements.txt`
2. **Start Command**: `python chronulus_mcp_server.py`
3. **Healthcheck Path**: `/health`
4. **Port**: `8080`

## 5. Deployment Process

### Automatic Deployment
1. Railway detects `railway.toml` and `requirements.txt`
2. Uses nixpacks builder (recommended for Python)
3. Installs dependencies from requirements.txt
4. Starts server with configured command
5. Runs health checks on `/health` endpoint

### Build Logs to Monitor
```
Building with nixpacks...
Installing Python dependencies...
chronulus>=0.0.14
chronulus-core>=0.0.23
uvicorn[standard]>=0.24.0
...
Starting Chronulus AI Forecasting MCP Server on port 8080
✅ Chronulus SDK imported successfully
🧠 Starting server...
```

## 6. Health Check Verification

### Endpoint: GET /health
**Expected Response** (Status 200):
```json
{
  "status": "healthy",
  "timestamp": "2025-08-23T01:30:06.179675+00:00",
  "service": "chronulus-mcp",
  "version": "1.0.0"
}
```

### Troubleshooting Health Checks
**Status 503 - Service Unavailable**:
```json
{
  "status": "sdk_unavailable",
  "error": "Chronulus SDK not available",
  "debug_info": {
    "python_version": "3.12.0",
    "chronulus_error": "Import error details"
  }
}
```

## 7. MCP Endpoint Verification

### Endpoint: POST /mcp
**Test Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 1
}
```

**Expected Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "testChronulusHardcoded",
        "description": "Test Chronulus with hard-coded Dodgers @ Padres game data"
      },
      {
        "name": "getChronulusAnalysis",
        "description": "Get AI expert panel analysis for sports betting predictions"
      },
      {
        "name": "getChronulusHealth",
        "description": "Check Chronulus service health and API connectivity"
      }
    ]
  }
}
```

## 8. Monitoring and Logs

### Railway Dashboard Monitoring
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: History of deployments
- **Health**: Service health status

### Log Examples
**Successful Start**:
```
🧠 Starting Chronulus AI Forecasting MCP Server on port 8080
✅ Chronulus SDK imported successfully (version: 0.0.14)
⚡ Health check: http://localhost:8080/health
🔗 MCP endpoint: http://localhost:8080/mcp
🔑 API key configured: True
📦 Chronulus SDK available: True
INFO: Started server process [1]
INFO: Uvicorn running on http://0.0.0.0:8080
```

## 9. Deployment Updates

### Automatic Updates
- **Git Push**: Automatically triggers rebuild and redeploy
- **Environment Variables**: Changes trigger restart
- **railway.toml**: Changes trigger full rebuild

### Manual Deployment
```bash
railway deploy  # If using Railway CLI
```

### Rollback
```bash
railway rollback <deployment-id>
```

## 10. Production Settings

### Resource Allocation
- **CPU**: 1-2 vCPU (sufficient for MCP server)
- **Memory**: 512MB - 1GB (depends on usage)
- **Regions**: US East (Virginia) - recommended for performance

### Scaling Configuration
- **Replicas**: 1 (sufficient for current usage)
- **Auto-scaling**: Not needed for MCP server
- **Load balancing**: Handled by Railway

## 11. Security Considerations

### API Key Security
- ✅ Stored in Railway environment variables (encrypted)
- ✅ Not exposed in code or logs
- ✅ Only accessible by Railway deployment

### Network Security
- ✅ HTTPS enforced on all endpoints
- ✅ CORS headers configured appropriately
- ✅ No sensitive data in response headers

## 12. Cost Management

### Railway Pricing
- **Free Tier**: $0 for light usage
- **Pro Plan**: $20/month for higher limits
- **Resource Usage**: ~$1-5/month for typical MCP server usage

### Chronulus API Costs
- **2-Expert Analysis**: $0.05-0.10 per analysis
- **Daily Usage**: ~$1.50-3.00 (15 games)
- **Monthly Estimate**: ~$25-50 for regular analysis

## 13. Troubleshooting

### Common Issues
1. **Build Failures**: Check requirements.txt syntax
2. **Import Errors**: Verify package names and versions
3. **API Key Issues**: Ensure environment variable is set
4. **Port Conflicts**: Railway handles port assignment automatically

### Support Resources
- **Railway Discord**: Community support
- **Railway Documentation**: https://docs.railway.app
- **GitHub Issues**: Project-specific issues

## Next Steps

After successful deployment:
1. **Test the deployment**: `06_TESTING_AND_TROUBLESHOOTING.md`
2. **Configure integration**: `07_INTEGRATION_EXAMPLES.md`
3. **Customize prompts**: `04_PROMPTING_AND_CUSTOMIZATION.md`