# 🧪 Testing and Troubleshooting Guide

Comprehensive guide for testing Chronulus MCP server deployment and troubleshooting common issues.

## Testing Framework

### Remote Testing Script
**Location**: `testing_chronulus_railway/test_railway_chronulus.py`

**Purpose**: 
- Test Railway MCP server remotely
- Verify all tools and endpoints
- Save results with timestamps for analysis
- Monitor health and performance

### Running Tests
```bash
cd testing_chronulus_railway
python test_railway_chronulus.py
```

**Expected Output**:
```
🚀 RAILWAY CHRONULUS MCP REMOTE TESTING
======================================================================
🌐 Server: https://chronulusmcp-production.up.railway.app/mcp
📁 Results: testing_chronulus_railway/results

🔍 TESTING HEALTH CHECK
==================================================
🔗 Calling Railway MCP Server: https://chronulusmcp-production.up.railway.app/mcp
🛠️  Tool: getChronulusHealth
📊 Arguments: None
🔄 Response Status: 200
💾 Results saved:
   JSON: results/health_check_20250822_213535.json
   MD:   results/health_check_20250822_213535.md
🏥 Server Status: healthy
✅ Server is healthy - proceeding with analysis test

🧠 TESTING HARDCODED ANALYSIS (Dodgers @ Padres)
============================================================
⚾ Game: Los Angeles Dodgers @ San Diego Padres
💰 Markets: Moneyline, Run Line, Total (Over/Under 8.5)
👨‍⚖️ Experts: 2 (cost savings)
📝 Analysis: Detailed explanations requested
🔗 Calling Railway MCP Server: https://chronulusmcp-production.up.railway.app/mcp
🛠️  Tool: testChronulusHardcoded
📊 Arguments: None
🔄 Response Status: 200
💾 Results saved:
   JSON: results/hardcoded_dodgers_padres_20250822_214724.json
   MD:   results/hardcoded_dodgers_padres_20250822_214724.md

🎉 ANALYSIS COMPLETED SUCCESSFULLY!
💡 Check the results folder for detailed analysis
📊 Preview - Dodgers Win Probability: 36.3%

📁 All results saved to: testing_chronulus_railway/results
🔍 Check both .json and .md files for complete analysis

✅ Testing complete!
```

## Test Results Structure

### Results Directory
```
testing_chronulus_railway/results/
├── health_check_TIMESTAMP.json
├── health_check_TIMESTAMP.md
├── hardcoded_dodgers_padres_TIMESTAMP.json
└── hardcoded_dodgers_padres_TIMESTAMP.md
```

### Successful Analysis Result
```markdown
# Chronulus Railway MCP Test Results

**Test**: hardcoded_dodgers_padres
**Timestamp**: 20250822_214724
**Railway URL**: https://chronulusmcp-production.up.railway.app/mcp

## Expert Analysis

[Positive Expert Analysis]
Looking at this NL West showdown, I'm seeing some subtle edges that the market is missing...
[12-18 sentences of detailed analysis]

[Negative/Contrarian Expert Analysis] 
Looking at this key NL West matchup through a contrarian lens...
[12-18 sentences of contrarian analysis]

## Key Metrics

- **Dodgers Win Probability**: 36.3%
- **Markets Analyzed**: Moneyline, Run Line, Total Runs
- **Cost Estimate**: $0.05-0.10
```

## Manual Testing Procedures

### 1. Health Check Test
```bash
curl https://chronulusmcp-production.up.railway.app/health
```

**Expected Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2025-08-23T01:30:06.179675+00:00",
  "service": "chronulus-mcp",
  "version": "1.0.0"
}
```

### 2. MCP Tools List Test  
```bash
curl -X POST https://chronulusmcp-production.up.railway.app/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

**Expected**: List of 3 available tools

### 3. Hardcoded Analysis Test
```bash
curl -X POST https://chronulusmcp-production.up.railway.app/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
      "name": "testChronulusHardcoded", 
      "arguments": {}
    }
  }'
```

**Expected**: Detailed 2-expert analysis with probability and betting recommendations

## Common Issues and Solutions

### 1. Server Health Issues

#### Issue: "sdk_unavailable"
```json
{
  "status": "sdk_unavailable",
  "error": "Chronulus SDK not available"
}
```

**Causes**:
- Chronulus package not installed
- Import errors during startup
- Dependency conflicts

**Solutions**:
1. Check Railway build logs for install errors
2. Verify requirements.txt has correct packages:
   ```
   chronulus>=0.0.14
   chronulus-core>=0.0.23
   ```
3. Redeploy with clean build

#### Issue: "api_key_missing"  
```json
{
  "status": "api_key_missing",
  "api_key_configured": false
}
```

**Solution**: Set `CHRONULUS_API_KEY` in Railway environment variables

#### Issue: "connection_error"
```json
{
  "status": "connection_error",
  "error": "Failed to create session. API Key is not valid or not yet active."
}
```

**Solutions**:
1. Verify API key is correct
2. Wait 1 minute for new API keys to activate
3. Contact Chronulus support for API key issues

### 2. Analysis Request Issues

#### Issue: "num_experts must be between 2 and 30"
```json
{
  "error": "Hard-coded test failed: num_experts must be between 2 and 30",
  "status": "test_error"
}
```

**Solution**: Always use minimum 2 experts:
```python
num_experts=2  # Minimum allowed by Chronulus
```

#### Issue: "BinaryPredictor.queue() got an unexpected keyword argument"
**Cause**: Using invalid parameters in predictor.queue()

**Solution**: Use only valid parameters:
```python
request = predictor.queue(
    item=data_model,           # Pydantic model only
    num_experts=2,             # Integer 2-30
    note_length=(10, 15)       # Tuple of integers
)
# Do NOT use: prompt_additions, context, etc.
```

#### Issue: "Analysis not available" in results
**Cause**: Using wrong attribute name for analysis text

**Solution**: Use correct attribute:
```python
analysis_text = pred.text  # Correct
# NOT: pred.note, pred.analysis, pred.reasoning
```

### 3. Timeout Issues

#### Issue: Request timeout after 5 minutes
**Causes**:
- Large expert count (>10 experts)
- Chronulus service overload
- Network connectivity issues

**Solutions**:
1. Reduce expert count to 2-5
2. Implement retry logic with backoff
3. Check Chronulus service status

#### Issue: Analysis takes too long
**Optimization**:
```python
# Fast analysis (30-45 seconds)
num_experts=2
note_length=(8, 12)

# Balanced analysis (45-90 seconds)  
num_experts=3
note_length=(10, 15)

# Comprehensive analysis (90+ seconds)
num_experts=5
note_length=(15, 20)
```

### 4. Railway Deployment Issues

#### Issue: Build failures
**Check**: Railway build logs for specific errors

**Common Solutions**:
1. Fix requirements.txt syntax errors
2. Resolve dependency conflicts
3. Update Python version compatibility

#### Issue: Deploy succeeds but health check fails
**Check**: Railway application logs for startup errors

**Common Causes**:
1. Environment variables not set
2. Port binding issues  
3. Import failures at runtime

#### Issue: Intermittent failures
**Solutions**:
1. Add retry logic in client code
2. Implement graceful degradation
3. Monitor Railway metrics for resource constraints

### 5. Integration Issues

#### Issue: Discord bot cannot connect to MCP server
**Check**:
1. MCP server URL is correct
2. Network connectivity from bot to Railway
3. JSON-RPC 2.0 request format

**Debug**:
```python
# Test connectivity
response = await client.get("https://chronulusmcp-production.up.railway.app/health")
print(f"Health check: {response.status_code}")

# Test MCP endpoint
mcp_response = await client.post(
    "https://chronulusmcp-production.up.railway.app/mcp",
    json={"jsonrpc": "2.0", "method": "tools/list", "id": 1}
)
print(f"MCP response: {mcp_response.json()}")
```

## Performance Testing

### Load Testing Script
```python
import asyncio
import httpx
import time

async def load_test(concurrent_requests=5):
    url = "https://chronulusmcp-production.up.railway.app/mcp"
    
    request_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getChronulusHealth",
            "arguments": {}
        }
    }
    
    async def single_request():
        async with httpx.AsyncClient(timeout=30) as client:
            start = time.time()
            response = await client.post(url, json=request_payload)
            elapsed = time.time() - start
            return response.status_code, elapsed
    
    # Run concurrent requests
    tasks = [single_request() for _ in range(concurrent_requests)]
    results = await asyncio.gather(*tasks)
    
    # Analyze results
    success_count = sum(1 for status, _ in results if status == 200)
    avg_time = sum(elapsed for _, elapsed in results) / len(results)
    
    print(f"Load Test Results:")
    print(f"  Concurrent Requests: {concurrent_requests}")
    print(f"  Success Rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    print(f"  Average Response Time: {avg_time:.2f}s")

# Run test
asyncio.run(load_test(concurrent_requests=3))
```

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Health Check Response Time**: <500ms expected
2. **Analysis Success Rate**: >95% expected  
3. **Analysis Response Time**: 30-90 seconds expected
4. **Railway Resource Usage**: CPU <50%, Memory <80%
5. **Chronulus API Costs**: Track daily/monthly spend

### Automated Monitoring Script
```python
import asyncio
import httpx
import smtplib
from datetime import datetime

async def health_monitor():
    """Monitor service health and send alerts"""
    url = "https://chronulusmcp-production.up.railway.app/health"
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                await send_alert(f"Health check failed: {response.status_code}")
                return False
                
            data = response.json()
            if data.get("status") != "healthy":
                await send_alert(f"Service unhealthy: {data.get('status')}")
                return False
                
        return True
        
    except Exception as e:
        await send_alert(f"Health check error: {str(e)}")
        return False

async def send_alert(message):
    """Send alert notification"""
    timestamp = datetime.now().isoformat()
    alert = f"[CHRONULUS ALERT] {timestamp}: {message}"
    print(alert)
    # Add email/Slack notification here

# Run monitoring
if __name__ == "__main__":
    asyncio.run(health_monitor())
```

## Debugging Tools

### Railway Logs Analysis
```bash
# View recent logs
railway logs

# Follow logs in real-time  
railway logs --follow

# Filter for errors
railway logs | grep -i error
```

### MCP Request/Response Debugging
```python
import httpx
import json

async def debug_mcp_request(tool_name, arguments=None):
    """Debug MCP requests with detailed logging"""
    url = "https://chronulusmcp-production.up.railway.app/mcp"
    
    request_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        }
    }
    
    print(f"🔍 Debugging MCP Request:")
    print(f"   URL: {url}")
    print(f"   Tool: {tool_name}")
    print(f"   Payload: {json.dumps(request_payload, indent=2)}")
    print()
    
    async with httpx.AsyncClient(timeout=300) as client:
        response = await client.post(url, json=request_payload)
        
        print(f"📥 Response:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Body: {json.dumps(response.json(), indent=2)}")
        
        return response.json()

# Debug specific tool
result = asyncio.run(debug_mcp_request("getChronulusHealth"))
```

This comprehensive testing and troubleshooting guide ensures reliable operation and quick resolution of any issues with the Chronulus MCP server deployment.