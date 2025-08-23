# 🔧 Chronulus Setup and Installation

Complete guide for setting up Chronulus AI forecasting from scratch.

## Prerequisites

- **Python**: 3.8+ (tested with 3.12 on Railway)
- **API Key**: Chronulus API key (starts with `25b23...`)
- **Railway Account**: For deployment
- **Git**: For version control

## 1. Package Installation

### Core Dependencies
```bash
pip install chronulus>=0.0.14
pip install chronulus-core>=0.0.23
pip install pydantic>=2.9.0,<3.0.0
pip install pydantic-settings>=2.6.0,<3.0.0
pip install python-dotenv==1.0.1
```

### MCP Server Dependencies
```bash
pip install uvicorn[standard]>=0.24.0
pip install starlette>=0.27.0
pip install httpx>=0.25.0
```

### Testing Dependencies
```bash
pip install pandas
pip install numpy
pip install python-dateutil
```

## 2. API Key Setup

### Option A: Environment Variable
```bash
export CHRONULUS_API_KEY=your_chronulus_api_key_here
```

### Option B: .env.local File
Create `.env.local` in project root:
```
CHRONULUS_API_KEY=your_chronulus_api_key_here
```

### Option C: Railway Environment Variables
Set in Railway Dashboard → Variables:
```
CHRONULUS_API_KEY=your_chronulus_api_key_here
PORT=8080
```

## 3. Verify Installation

### Test Basic Import
```python
from chronulus import Session
from chronulus.estimator import BinaryPredictor
print("✅ Chronulus SDK imported successfully")
```

### Test API Connectivity
```python
import os
from chronulus import Session

session = Session(
    name="Test Session",
    situation="Testing API connectivity",
    task="Verify Chronulus service availability",
    env=dict(CHRONULUS_API_KEY=os.getenv("CHRONULUS_API_KEY"))
)

try:
    session.create()
    print(f"✅ API connection successful: {session.session_id}")
except Exception as e:
    print(f"❌ API connection failed: {e}")
```

## 4. Directory Structure

```
your_project/
├── mcp_leagues/
│   └── chronulus/
│       ├── chronulus_mcp_server.py    # Main MCP server
│       ├── requirements.txt           # Dependencies
│       ├── railway.toml              # Railway config
│       └── README.md                 # Server documentation
├── testing_chronulus_railway/
│   ├── test_railway_chronulus.py     # Remote testing script
│   └── results/                      # Test results
└── chronulus_documentation/          # This documentation
```

## 5. Key Configuration Files

### requirements.txt
```
# Core MCP server dependencies
uvicorn[standard]>=0.24.0
starlette>=0.27.0
httpx>=0.25.0

# Chronulus SDK and dependencies
chronulus>=0.0.14
chronulus-core>=0.0.23
pydantic>=2.9.0,<3.0.0
pydantic-settings>=2.6.0,<3.0.0
python-dotenv==1.0.1

# Additional dependencies
pandas
numpy
python-dateutil
```

### railway.toml
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

## 6. Common Installation Issues

### Issue: "No module named 'chronulus'"
**Solution**: Install correct package:
```bash
pip install chronulus  # Not chronulus-mcp
```

### Issue: "BinaryPredictor has no attribute 'create_request'"
**Solution**: Use correct API methods:
```python
predictor = BinaryPredictor(session=session, input_type=DataModel)
predictor.create()  # Create predictor first
request = predictor.queue(item=data, num_experts=2, note_length=(10, 15))
```

### Issue: "num_experts must be between 2 and 30"
**Solution**: Use minimum 2 experts:
```python
num_experts=2  # Minimum allowed
```

### Issue: "Analysis not available"
**Solution**: Use correct attribute for analysis text:
```python
analysis_text = pred.text  # Not pred.note
```

## 7. Verification Checklist

- [ ] Python 3.8+ installed
- [ ] All dependencies installed without errors
- [ ] Chronulus API key configured
- [ ] Basic import test passes
- [ ] API connectivity test passes
- [ ] Directory structure created
- [ ] Configuration files in place

## Next Steps

After successful setup:
1. **Deploy to Railway**: See `02_RAILWAY_DEPLOYMENT.md`
2. **Test deployment**: See `06_TESTING_AND_TROUBLESHOOTING.md`
3. **Integrate with bot**: See `07_INTEGRATION_EXAMPLES.md`