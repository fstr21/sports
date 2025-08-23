# 🏗️ MCP Server Architecture

Technical architecture documentation for the Chronulus AI Forecasting MCP Server.

## System Architecture Overview

```
┌─────────────────┐    JSON-RPC 2.0    ┌─────────────────┐    Chronulus API    ┌─────────────────┐
│   Discord Bot   │ ◄─────────────────► │   Railway MCP   │ ◄──────────────────► │  Chronulus AI   │
│                 │                     │     Server      │                     │   Expert Panel  │
│  - MLB Handler  │                     │                 │                     │                 │
│  - Client Calls │                     │ - Health Check  │                     │ - 2-30 Experts  │
│                 │                     │ - Game Analysis │                     │ - Binary Pred   │
└─────────────────┘                     └─────────────────┘                     └─────────────────┘
```

## Core Components

### 1. FastAPI/Starlette Web Server
```python
# Main application
app = Starlette(routes=routes)

# Routes
routes = [
    Route("/", health_check, methods=["GET"]),
    Route("/health", health_check, methods=["GET"]), 
    Route("/mcp", handle_mcp_request, methods=["POST"])
]
```

### 2. MCP Protocol Handler
```python
async def handle_mcp_request(request: Request) -> Response:
    """
    Handles JSON-RPC 2.0 MCP requests
    - tools/list: Returns available tools
    - tools/call: Executes tool with parameters
    """
```

### 3. Chronulus Integration Layer
```python
# Session management
session = Session(
    name="MLB Expert Analysis",
    situation="Expert betting persona...",
    task="Analyze betting markets...",
    env=dict(CHRONULUS_API_KEY=API_KEY)
)

# Prediction workflow
predictor = BinaryPredictor(session=session, input_type=DataModel)
predictor.create()
request = predictor.queue(item=data, num_experts=2, note_length=(12,18))
predictions = predictor.get_request_predictions(request_id=request.request_id)
```

## Available MCP Tools

### 1. testChronulusHardcoded
**Purpose**: Test functionality with hardcoded Dodgers @ Padres data

**Input Schema**:
```json
{
  "type": "object",
  "properties": {}
}
```

**Process**:
1. Creates hardcoded game data (ComprehensiveSportsData)
2. Sets up expert session with sports betting persona
3. Requests 2-expert analysis with 12-18 sentence detail
4. Returns probability + detailed analysis

**Output**:
```json
{
  "session_id": "uuid",
  "request_id": "uuid", 
  "test_game": "Los Angeles Dodgers @ San Diego Padres",
  "analysis": {
    "expert_analysis": "Detailed 12-18 sentence analysis...",
    "dodgers_win_probability": 0.363,
    "confidence": "2-expert consensus analysis",
    "betting_markets_covered": ["Moneyline", "Run Line", "Total Runs"],
    "expert_count": 2,
    "cost_estimate": "$0.05-0.10"
  },
  "status": "success"
}
```

### 2. getChronulusAnalysis
**Purpose**: Analyze any game data provided by caller

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "game_data": {
      "type": "object",
      "description": "Game data including teams, stats, odds, etc."
    },
    "expert_count": {
      "type": "integer",
      "minimum": 2,
      "maximum": 30,
      "default": 2
    }
  },
  "required": ["game_data"]
}
```

**Process**:
1. Extracts game information from provided data
2. Creates GeneralGameData Pydantic model
3. Sets up analysis session
4. Requests multi-expert analysis
5. Processes and returns consensus results

### 3. getChronulusHealth
**Purpose**: Health check and service status

**Output**:
```json
{
  "timestamp": "2025-08-23T01:30:06Z",
  "chronulus_sdk": true,
  "api_key_configured": true,
  "status": "healthy",
  "session_id": "test-session-uuid"
}
```

## Data Models

### ComprehensiveSportsData (Hardcoded Test)
```python
class ComprehensiveSportsData(BaseModel):
    home_team: str = Field(description="Home team with context")
    away_team: str = Field(description="Away team with context") 
    sport: str = Field(description="Major League Baseball")
    game_date: str = Field(description="Game date")
    game_time: str = Field(description="Game time")
    venue: str = Field(description="Venue with advantage context")
    home_record: str = Field(description="Home team season record")
    away_record: str = Field(description="Away team season record")
    # ... additional fields for comprehensive analysis
```

### GeneralGameData (Dynamic Analysis)
```python
class GeneralGameData(BaseModel):
    away_team: str = Field(description="Away team name")
    home_team: str = Field(description="Home team name")
    date: str = Field(description="Game date")
    venue: str = Field(description="Venue name")
```

## Request/Response Flow

### 1. MCP Request Processing
```
Client Request → JSON-RPC 2.0 Validation → Tool Routing → Tool Execution → Response Formatting → Client Response
```

### 2. Chronulus Analysis Flow
```
Game Data → Pydantic Model → Session Setup → Expert Queuing → Prediction Retrieval → Result Processing → MCP Response
```

### 3. Error Handling Flow
```
Exception → Error Classification → Structured Error Response → Client Notification
```

## Configuration Management

### Environment Variables
- `CHRONULUS_API_KEY`: Chronulus service API key
- `PORT`: Server port (default: 8080)
- `LOG_LEVEL`: Logging level (optional)

### Session Configuration
```python
session = Session(
    name="Analysis Session Name",           # Influences AI approach
    situation="Expert persona and context", # Sets expert personality
    task="Specific analysis instructions",  # Defines output format
    env=dict(CHRONULUS_API_KEY=api_key)    # Authentication
)
```

### Prediction Parameters
```python
predictor.queue(
    item=data_model,           # Pydantic model with game data
    num_experts=2,             # 2-30 experts (minimum 2)
    note_length=(12, 18)       # Sentence count for analysis
)
```

## Performance Characteristics

### Response Times
- **Health Check**: <100ms
- **Hardcoded Test**: 30-60 seconds (2-expert analysis)
- **Dynamic Analysis**: 30-90 seconds (depending on expert count)

### Throughput
- **Concurrent Requests**: Limited by Chronulus API rate limits
- **Railway Resources**: 1 vCPU, 512MB RAM sufficient

### Cost Per Request
- **2-Expert Analysis**: $0.05-0.10
- **Higher Expert Count**: Scales linearly
- **Health Checks**: Free

## Error Handling

### Chronulus SDK Errors
```python
if not CHRONULUS_AVAILABLE:
    return {"error": "Chronulus SDK not available", "status": "unavailable"}

if not CHRONULUS_API_KEY:
    return {"error": "API key not configured", "status": "configuration_error"}
```

### Prediction Errors
```python
try:
    predictions = predictor.get_request_predictions(...)
    if not predictions:
        return {"error": "No predictions received", "status": "analysis_timeout"}
except Exception as e:
    return {"error": f"Analysis failed: {str(e)}", "status": "analysis_error"}
```

### MCP Protocol Errors
```python
# JSON-RPC 2.0 compliant error responses
{
  "jsonrpc": "2.0",
  "id": request_id,
  "error": {
    "code": -32601,
    "message": "Method not found"
  }
}
```

## Security Architecture

### API Key Management
- Stored in Railway environment variables (encrypted at rest)
- Never logged or exposed in responses
- Passed securely to Chronulus SDK

### Request Validation
- JSON-RPC 2.0 protocol compliance
- Input schema validation via Pydantic
- Parameter bounds checking (expert count, note length)

### Response Sanitization
- No sensitive data in responses
- Structured error messages without internal details
- HTTPS enforcement by Railway

## Monitoring and Observability

### Health Monitoring
```python
async def get_chronulus_health():
    # Test SDK availability
    # Test API key validity  
    # Test session creation
    # Return comprehensive status
```

### Logging
```python
print(f"✅ Chronulus SDK imported successfully")
print(f"🔑 API key configured: {bool(CHRONULUS_API_KEY)}")
print(f"📦 Chronulus SDK available: {CHRONULUS_AVAILABLE}")
```

### Metrics Available
- Request count and response times
- Success/failure rates
- Chronulus API usage and costs
- Railway resource utilization

## Deployment Architecture

### Railway Integration
- **Builder**: Nixpacks (automatic Python detection)
- **Runtime**: Python 3.12 on Ubuntu
- **Process Management**: Uvicorn ASGI server
- **Health Checks**: Automated via `/health` endpoint
- **Auto-restart**: On failure with exponential backoff

### Scaling Considerations
- **Vertical Scaling**: Increase RAM for higher concurrent expert counts
- **Horizontal Scaling**: Not recommended due to Chronulus session management
- **Load Balancing**: Handled automatically by Railway

This architecture provides a robust, scalable foundation for AI-powered sports betting analysis with comprehensive error handling and monitoring capabilities.