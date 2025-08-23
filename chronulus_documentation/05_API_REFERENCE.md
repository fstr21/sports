# 📚 API Reference

Complete reference for all Chronulus MCP server endpoints, tools, and data structures.

## Base URLs

- **Production**: `https://chronulusmcp-production.up.railway.app`
- **Health Check**: `https://chronulusmcp-production.up.railway.app/health`
- **MCP Endpoint**: `https://chronulusmcp-production.up.railway.app/mcp`

## HTTP Endpoints

### GET /health
**Purpose**: Service health check and status verification

**Request**: No parameters required

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2025-08-23T01:30:06.179675+00:00",
  "service": "chronulus-mcp",
  "version": "1.0.0"
}
```

**Error Response** (503 Service Unavailable):
```json
{
  "status": "sdk_unavailable",
  "timestamp": "2025-08-23T01:30:06.179675+00:00",
  "service": "chronulus-mcp",
  "version": "1.0.0"
}
```

### GET /
**Purpose**: Root endpoint (same as /health)
**Response**: Identical to `/health`

### POST /mcp
**Purpose**: MCP JSON-RPC 2.0 protocol endpoint
**Content-Type**: `application/json`

## MCP Tools

### tools/list
**Purpose**: Get list of available tools

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 1
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "testChronulusHardcoded",
        "description": "Test Chronulus with hard-coded Dodgers @ Padres game data (2 experts minimum)",
        "inputSchema": {
          "type": "object",
          "properties": {}
        }
      },
      {
        "name": "getChronulusAnalysis",
        "description": "Get AI expert panel analysis for sports betting predictions",
        "inputSchema": {
          "type": "object",
          "properties": {
            "game_data": {
              "type": "object",
              "description": "Comprehensive game data including teams, stats, odds, etc."
            },
            "expert_count": {
              "type": "integer",
              "description": "Number of AI experts (2-30, default: 2)",
              "minimum": 2,
              "maximum": 30,
              "default": 2
            }
          },
          "required": ["game_data"]
        }
      },
      {
        "name": "getChronulusHealth",
        "description": "Check Chronulus service health and API connectivity",
        "inputSchema": {
          "type": "object",
          "properties": {}
        }
      }
    ]
  }
}
```

## Tool Implementations

### testChronulusHardcoded

**Purpose**: Test Chronulus functionality with pre-configured Dodgers @ Padres game data

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 1,
  "params": {
    "name": "testChronulusHardcoded",
    "arguments": {}
  }
}
```

**Response** (Success):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"session_id\": \"54371f28-de5b-533e-9038-c279f12268c8\",\n  \"request_id\": \"8f8402cd-5722-4615-aba1-8c9fba2e6ced\",\n  \"test_game\": \"Los Angeles Dodgers @ San Diego Padres\",\n  \"analysis\": {\n    \"expert_analysis\": \"[Detailed 12-18 sentence expert analysis...]\",\n    \"dodgers_win_probability\": 0.363,\n    \"confidence\": \"2-expert consensus analysis\",\n    \"betting_markets_covered\": [\"Moneyline\", \"Run Line\", \"Total Runs\"],\n    \"expert_count\": 2,\n    \"cost_estimate\": \"$0.05-0.10\"\n  },\n  \"status\": \"success\",\n  \"timestamp\": \"2025-08-23T01:47:24.268302+00:00\"\n}"
      }
    ]
  }
}
```

**Game Data Used**:
```json
{
  "home_team": "San Diego Padres",
  "away_team": "Los Angeles Dodgers",
  "game_date": "August 22, 2025",
  "game_time": "8:40 PM ET",
  "venue": "Petco Park",
  "home_record": "72-56 (.563 win percentage)",
  "away_record": "73-55 (.570 win percentage)",
  "home_run_differential": -58,
  "away_run_differential": 93,
  "home_runs_per_game": 3.76,
  "away_runs_per_game": 4.48,
  "home_recent_form": "6-4 in last 10 games",
  "away_recent_form": "5-5 in last 10 games",
  "home_moneyline": 102,
  "away_moneyline": -120,
  "over_under": "Over/Under 8.5 runs"
}
```

### getChronulusAnalysis

**Purpose**: Analyze custom game data provided by caller

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 1,
  "params": {
    "name": "getChronulusAnalysis",
    "arguments": {
      "game_data": {
        "home_team": "Team Name",
        "away_team": "Team Name",
        "date": "2025-08-23",
        "venue": "Stadium Name",
        "stats": {
          "home_record": "W-L",
          "away_record": "W-L"
        },
        "odds": {
          "home_moneyline": -150,
          "away_moneyline": +130
        },
        "form": {
          "home_recent": "Recent form description",
          "away_recent": "Recent form description"
        }
      },
      "expert_count": 2
    }
  }
}
```

**Response Structure**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"session_id\": \"uuid\",\n  \"request_id\": \"uuid\",\n  \"analysis\": {\n    \"consensus_probability\": 0.65,\n    \"confidence_range\": 0.12,\n    \"expert_count\": 2,\n    \"market_edge\": 0.045,\n    \"recommendation\": \"BET\",\n    \"expert_analyses\": [\n      {\n        \"expert_id\": 1,\n        \"probability\": 0.62,\n        \"analysis\": \"Expert 1 reasoning...\",\n        \"confidence\": \"high\"\n      },\n      {\n        \"expert_id\": 2,\n        \"probability\": 0.68,\n        \"analysis\": \"Expert 2 reasoning...\",\n        \"confidence\": \"medium\"\n      }\n    ]\n  },\n  \"status\": \"success\"\n}"
      }
    ]
  }
}
```

### getChronulusHealth

**Purpose**: Detailed health check with service diagnostics

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 1,
  "params": {
    "name": "getChronulusHealth",
    "arguments": {}
  }
}
```

**Response** (Healthy):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"timestamp\": \"2025-08-23T01:30:06.179675+00:00\",\n  \"chronulus_sdk\": true,\n  \"api_key_configured\": true,\n  \"status\": \"healthy\",\n  \"session_id\": \"test-session-uuid\"\n}"
      }
    ]
  }
}
```

**Response** (Unhealthy):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"timestamp\": \"2025-08-23T01:30:06.179675+00:00\",\n  \"chronulus_sdk\": false,\n  \"api_key_configured\": true,\n  \"status\": \"sdk_unavailable\",\n  \"error\": \"No module named 'chronulus'\",\n  \"debug_info\": {\n    \"python_version\": \"3.12.0\",\n    \"chronulus_error\": \"Import error details\"\n  }\n}"
      }
    ]
  }
}
```

## Error Responses

### JSON-RPC 2.0 Error Format
All errors follow JSON-RPC 2.0 specification:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Method not found"
  }
}
```

### Common Error Codes

**-32700**: Parse error (invalid JSON)
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "error": {
    "code": -32700,
    "message": "Parse error"
  }
}
```

**-32601**: Method not found
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Unknown tool: invalidToolName"
  }
}
```

**-32603**: Internal error
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Internal error: Chronulus analysis failed"
  }
}
```

## Data Structures

### Analysis Response Structure
```typescript
interface AnalysisResponse {
  session_id: string;
  request_id: string;
  test_game?: string;                    // Present in hardcoded test
  analysis: {
    expert_analysis?: string;            // Detailed text analysis
    dodgers_win_probability?: number;    // Hardcoded test specific
    consensus_probability?: number;      // General analysis
    confidence: string;
    betting_markets_covered: string[];
    expert_count: number;
    cost_estimate: string;
    confidence_range?: number;           // General analysis
    market_edge?: number;                // General analysis  
    recommendation?: string;             // General analysis
    expert_analyses?: ExpertAnalysis[]; // General analysis
  };
  status: "success" | "error";
  timestamp: string;
  error?: string;                       // Present on error
}
```

### Expert Analysis Structure
```typescript
interface ExpertAnalysis {
  expert_id: number;
  probability: number;
  analysis: string;
  confidence: "high" | "medium" | "low";
}
```

### Health Response Structure
```typescript
interface HealthResponse {
  timestamp: string;
  chronulus_sdk: boolean;
  api_key_configured: boolean;
  status: "healthy" | "sdk_unavailable" | "api_key_missing" | "connection_error";
  session_id?: string;                  // Present when healthy
  error?: string;                       // Present on error
  debug_info?: {                        // Present on error
    python_version: string;
    chronulus_error?: string;
  };
}
```

## Rate Limits and Quotas

### Chronulus API Limits
- **Concurrent Requests**: Limited by Chronulus service
- **Rate Limiting**: Handled by Chronulus backend
- **Timeout**: 5 minutes per analysis request

### Railway Limits
- **Request Timeout**: 300 seconds
- **Payload Size**: 10MB maximum
- **Concurrent Connections**: Based on Railway plan

## Authentication

### MCP Server Authentication
- No authentication required for MCP requests
- Chronulus API key managed server-side via environment variables

### Chronulus API Authentication  
- API key stored securely in Railway environment variables
- Automatic authentication handled by MCP server
- No client-side API key management required

## Usage Examples

### Python Client
```python
import httpx
import asyncio

async def test_chronulus():
    url = "https://chronulusmcp-production.up.railway.app/mcp"
    
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "testChronulusHardcoded",
            "arguments": {}
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=request)
        return response.json()

# Run test
result = asyncio.run(test_chronulus())
print(result)
```

### JavaScript Client
```javascript
async function testChronulus() {
    const url = "https://chronulusmcp-production.up.railway.app/mcp";
    
    const request = {
        jsonrpc: "2.0",
        method: "tools/call",
        id: 1,
        params: {
            name: "testChronulusHardcoded",
            arguments: {}
        }
    };
    
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
    });
    
    return await response.json();
}
```

### cURL Example
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