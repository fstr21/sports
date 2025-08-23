#!/usr/bin/env python3
"""
Chronulus AI Forecasting MCP Server for Sports AI

A dedicated MCP server that provides AI expert panel forecasting for sports betting analysis.
Integrates with existing sports analysis infrastructure via JSON-RPC 2.0.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

# Import Chronulus components
CHRONULUS_AVAILABLE = False
CHRONULUS_ERROR = None

try:
    import chronulus
    from chronulus import Session, BinaryPredictor
    CHRONULUS_AVAILABLE = True
    print(f"✅ Chronulus SDK imported successfully (version: {getattr(chronulus, '__version__', 'unknown')})")
except ImportError as e:
    CHRONULUS_ERROR = str(e)
    print(f"❌ Chronulus SDK import failed: {e}")
    print(f"   This will result in 'sdk_unavailable' status")
except Exception as e:
    CHRONULUS_ERROR = str(e)
    print(f"❌ Unexpected error importing Chronulus: {e}")
    print(f"   This will result in 'sdk_unavailable' status")

# Configuration
CHRONULUS_API_KEY = os.getenv("CHRONULUS_API_KEY")
USER_AGENT = "sports-ai-chronulus-mcp/1.0"

# HTTP client
_http_client: Optional[httpx.AsyncClient] = None

async def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={"user-agent": USER_AGENT, "accept": "application/json"}
        )
    return _http_client

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# MCP Tools
AVAILABLE_TOOLS = [
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

async def get_chronulus_analysis(game_data: Dict[str, Any], expert_count: int = 2) -> Dict[str, Any]:
    """
    Generate AI expert panel analysis using Chronulus
    """
    if not CHRONULUS_AVAILABLE:
        return {
            "error": "Chronulus SDK not available",
            "status": "unavailable"
        }
    
    if not CHRONULUS_API_KEY:
        return {
            "error": "Chronulus API key not configured", 
            "status": "configuration_error"
        }
    
    try:
        # Extract game information
        home_team = game_data.get("home_team", "Home Team")
        away_team = game_data.get("away_team", "Away Team")
        game_date = game_data.get("date", "Today")
        
        # Create Chronulus session
        session = Session(
            name=f"MLB Analysis: {away_team} @ {home_team}",
            situation=f"Analyzing MLB game on {game_date} between {away_team} and {home_team}",
            task="Provide comprehensive sports betting analysis with win probability assessment",
            env=dict(CHRONULUS_API_KEY=CHRONULUS_API_KEY)
        )
        
        # Create session
        await asyncio.to_thread(session.create)
        
        # Create binary predictor
        predictor = BinaryPredictor(session)
        
        # Format comprehensive data for analysis
        analysis_data = {
            "teams": {
                "away": away_team,
                "home": home_team
            },
            "date": game_date,
            "statistics": game_data.get("stats", {}),
            "betting_odds": game_data.get("odds", {}),
            "recent_form": game_data.get("form", {}),
            "venue": game_data.get("venue", "MLB Stadium"),
            "additional_context": game_data.get("context", {})
        }
        
        # Create prediction request
        request = await asyncio.to_thread(
            predictor.create_request,
            data=analysis_data,
            question=f"Will {away_team} win against {home_team}?",
            note_length=(10, 15),  # Detailed analysis
            expert_count=expert_count,
            prompt_additions="Analyze this like experienced sports bettors would - focus on recent form vs season stats, venue factors, and betting value."
        )
        
        # Get predictions with timeout
        predictions = await asyncio.to_thread(
            predictor.get_request_predictions,
            request_id=request.request_id,
            try_every=15,
            max_tries=12  # 3 minutes max
        )
        
        # Process results
        expert_analyses = []
        probabilities = []
        
        for i, pred in enumerate(predictions):
            if hasattr(pred, 'note') and hasattr(pred, 'prob'):
                # Handle probability extraction
                if isinstance(pred.prob, tuple):
                    probability = pred.prob[0]  # First element for binary prediction
                else:
                    probability = float(pred.prob)
                
                probabilities.append(probability)
                expert_analyses.append({
                    "expert_id": i + 1,
                    "probability": probability,
                    "analysis": pred.note,
                    "confidence": "high" if len(pred.note) > 500 else "medium"
                })
        
        # Calculate consensus
        if probabilities:
            consensus_prob = sum(probabilities) / len(probabilities)
            confidence_range = max(probabilities) - min(probabilities)
        else:
            consensus_prob = 0.5
            confidence_range = 0.0
        
        # Generate betting recommendation
        market_prob = game_data.get("odds", {}).get("implied_probability", 0.5)
        edge = consensus_prob - market_prob if market_prob > 0 else 0
        
        recommendation = "BET" if edge > 0.03 else "NO BET"
        
        return {
            "session_id": session.session_id,
            "request_id": request.request_id,
            "analysis": {
                "consensus_probability": consensus_prob,
                "confidence_range": confidence_range,
                "expert_count": len(expert_analyses),
                "market_edge": edge,
                "recommendation": recommendation,
                "expert_analyses": expert_analyses
            },
            "status": "success",
            "timestamp": now_iso()
        }
        
    except Exception as e:
        return {
            "error": f"Chronulus analysis failed: {str(e)}",
            "status": "analysis_error",
            "timestamp": now_iso()
        }

async def get_chronulus_health() -> Dict[str, Any]:
    """
    Check Chronulus service health
    """
    health_data = {
        "timestamp": now_iso(),
        "chronulus_sdk": CHRONULUS_AVAILABLE,
        "api_key_configured": bool(CHRONULUS_API_KEY),
        "status": "unknown"
    }
    
    if not CHRONULUS_AVAILABLE:
        health_data["status"] = "sdk_unavailable"
        health_data["error"] = CHRONULUS_ERROR or "Unknown import error"
        health_data["debug_info"] = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "chronulus_error": CHRONULUS_ERROR
        }
        return health_data
    
    if not CHRONULUS_API_KEY:
        health_data["status"] = "api_key_missing"
        return health_data
    
    try:
        # Test basic connectivity
        test_session = Session(
            name="Health Check",
            situation="Testing API connectivity",
            task="Verify Chronulus service availability",
            env=dict(CHRONULUS_API_KEY=CHRONULUS_API_KEY)
        )
        
        # Try to create session
        await asyncio.to_thread(test_session.create)
        health_data["status"] = "healthy"
        health_data["session_id"] = test_session.session_id
        
    except Exception as e:
        health_data["status"] = "connection_error"
        health_data["error"] = str(e)
    
    return health_data

# MCP Route Handlers
async def handle_mcp_request(request: Request) -> Response:
    try:
        body = await request.json()
        
        if body.get("method") == "tools/list":
            return Response(
                json.dumps({
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {"tools": AVAILABLE_TOOLS}
                }),
                media_type="application/json"
            )
        
        elif body.get("method") == "tools/call":
            params = body.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "getChronulusAnalysis":
                result = await get_chronulus_analysis(
                    game_data=arguments.get("game_data", {}),
                    expert_count=arguments.get("expert_count", 2)
                )
            elif tool_name == "getChronulusHealth":
                result = await get_chronulus_health()
            else:
                return Response(
                    json.dumps({
                        "jsonrpc": "2.0",
                        "id": body.get("id"),
                        "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                    }),
                    media_type="application/json"
                )
            
            return Response(
                json.dumps({
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
                }),
                media_type="application/json"
            )
        
        else:
            return Response(
                json.dumps({
                    "jsonrpc": "2.0", 
                    "id": body.get("id"),
                    "error": {"code": -32601, "message": "Method not found"}
                }),
                media_type="application/json"
            )
            
    except json.JSONDecodeError:
        return Response(
            json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            }),
            media_type="application/json",
            status_code=400
        )
    except Exception as e:
        return Response(
            json.dumps({
                "jsonrpc": "2.0",
                "id": body.get("id", None) if 'body' in locals() else None,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }),
            media_type="application/json",
            status_code=500
        )

async def health_check(request: Request) -> Response:
    """Health check endpoint for Railway"""
    health = await get_chronulus_health()
    status_code = 200 if health["status"] == "healthy" else 503
    
    return Response(
        json.dumps({
            "status": health["status"],
            "timestamp": health["timestamp"],
            "service": "chronulus-mcp",
            "version": "1.0.0"
        }),
        media_type="application/json",
        status_code=status_code
    )

# Routes
routes = [
    Route("/", health_check, methods=["GET"]),
    Route("/health", health_check, methods=["GET"]), 
    Route("/mcp", handle_mcp_request, methods=["POST"])
]

# Application
app = Starlette(routes=routes)

async def cleanup():
    """Cleanup HTTP client on shutdown"""
    global _http_client
    if _http_client:
        await _http_client.aclose()

if __name__ == "__main__":
    import atexit
    atexit.register(lambda: asyncio.run(cleanup()))
    
    port = int(os.getenv("PORT", 8080))
    print(f"🧠 Starting Chronulus AI Forecasting MCP Server on port {port}")
    print(f"⚡ Health check: http://localhost:{port}/health")
    print(f"🔗 MCP endpoint: http://localhost:{port}/mcp")
    print(f"🔑 API key configured: {bool(CHRONULUS_API_KEY)}")
    print(f"📦 Chronulus SDK available: {CHRONULUS_AVAILABLE}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)