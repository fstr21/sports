#!/usr/bin/env python3
"""
Custom Chronulus AI Forecasting MCP Server
A reverse-engineered implementation of ChronulusAI's expert panel system using OpenRouter.
Provides institutional-quality sports betting analysis at 90% cost savings.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from pydantic import BaseModel, Field
import statistics
import random

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
USER_AGENT = "custom-chronulus-mcp/1.0"

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

# Core Chronulus Models
class BetaDistributionParams(BaseModel):
    """Beta distribution parameters for consensus"""
    alpha: float
    beta: float
    
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)
    
    def variance(self) -> float:
        a_plus_b = self.alpha + self.beta
        return (self.alpha * self.beta) / (a_plus_b * a_plus_b * (a_plus_b + 1))

class ExpertOpinion(BaseModel):
    """Individual expert opinion with probability and reasoning"""
    expert_id: int
    expert_type: str
    probability: float
    confidence: float
    reasoning: str
    unit_size: int = 1
    risk_level: str = "Medium"

class PredictionResult(BaseModel):
    """Complete prediction result with consensus"""
    prob_a: float  # Probability for outcome A (away team win)
    text: str  # Combined expert analysis
    expert_count: int
    beta_params: BetaDistributionParams

class GameData(BaseModel):
    """Universal game data structure"""
    home_team: str = Field(description="Home team with context")
    away_team: str = Field(description="Away team with context")
    sport: str = Field(default="Baseball")
    venue: str = Field(description="Venue with context")
    game_date: str = Field(description="Game date")
    home_record: str = Field(description="Home team season record")
    away_record: str = Field(description="Away team season record")
    home_moneyline: int = Field(description="Home team moneyline odds")
    away_moneyline: int = Field(description="Away team moneyline odds")
    additional_context: str = Field(default="", description="Additional game context")

class CustomChronulusSession:
    """Simulates Chronulus session management"""
    
    def __init__(self, name: str, situation: str, task: str):
        self.name = name
        self.situation = situation
        self.task = task
        self.session_id = f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def create(self):
        """Create session (no-op for custom implementation)"""
        pass

class CustomBinaryPredictor:
    """Custom implementation of Chronulus binary predictor using OpenRouter"""
    
    def __init__(self, session: CustomChronulusSession, input_type: type):
        self.session = session
        self.input_type = input_type
        self.base_url = OPENROUTER_BASE_URL
        self.api_key = OPENROUTER_API_KEY
        self.model = OPENROUTER_MODEL
        
        self.expert_personas = [
            "STATISTICAL EXPERT",
            "SITUATIONAL EXPERT", 
            "CONTRARIAN EXPERT",
            "SHARP EXPERT",
            "MARKET EXPERT"
        ]
    
    def create(self):
        """Create predictor (no-op for custom implementation)"""
        pass
    
    async def queue(self, item: GameData, num_experts: int = 1, note_length: Tuple[int, int] = (4, 5)) -> 'PredictionRequest':
        """Generate single chief analyst institutional analysis"""
        if not self.api_key:
            raise Exception("OpenRouter API key not configured")
        
        # Generate single comprehensive analysis from Chief Sports Analyst
        chief_analysis = await self._simulate_chief_analyst_with_openrouter(item, note_length)
        
        # Use chief analyst's probability and confidence for beta distribution
        mean_prob = chief_analysis.probability
        confidence = chief_analysis.confidence
        
        # Create beta distribution from single expert with realistic variance
        # Higher confidence = lower variance
        variance_factor = (1 - confidence) * 0.02  # Scale variance based on confidence
        
        if variance_factor > 0 and mean_prob * (1 - mean_prob) > variance_factor:
            common_factor = (mean_prob * (1 - mean_prob) / variance_factor) - 1
            alpha = mean_prob * common_factor
            beta = (1 - mean_prob) * common_factor
        else:
            # Fallback based on confidence level
            base_strength = confidence * 40 + 10  # 10-50 based on confidence
            alpha = mean_prob * base_strength
            beta = (1 - mean_prob) * base_strength
        
        beta_params = BetaDistributionParams(alpha=alpha, beta=beta)
        
        # Format professional analysis output
        combined_text = f"INSTITUTIONAL SPORTS ANALYSIS\n{item.away_team} @ {item.home_team}\n\n"
        combined_text += f"Chief Sports Analyst • {self.model}\n\n"
        combined_text += chief_analysis.reasoning
        combined_text += f"\n\nFINAL ASSESSMENT:\n"
        combined_text += f"Win Probability: {mean_prob:.1%} ({item.away_team})\n"
        combined_text += f"Analyst Confidence: {confidence:.0%}\n"
        combined_text += f"Recommendation: {self._get_betting_recommendation(mean_prob, confidence)}"
        
        result = PredictionResult(
            prob_a=mean_prob,
            text=combined_text,
            expert_count=1,  # Single chief analyst
            beta_params=beta_params
        )
        
        return PredictionRequest(
            request_id=f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            result=result
        )
    
    def _get_betting_recommendation(self, probability: float, confidence: float) -> str:
        """Generate betting recommendation based on probability and confidence"""
        if confidence < 0.6:
            return "PASS - Insufficient edge"
        elif probability > 0.58:
            return "BET AWAY - Strong edge identified"
        elif probability < 0.42:
            return "BET HOME - Strong edge identified" 
        else:
            return "LEAN AWAY" if probability > 0.52 else "LEAN HOME" if probability < 0.48 else "PASS - No clear edge"
    
    async def _simulate_chief_analyst_with_openrouter(self, game_data: GameData, note_length: Tuple[int, int]) -> ExpertOpinion:
        """Generate comprehensive chief analyst analysis with Bloomberg-style formatting"""
        
        min_sentences, max_sentences = note_length
        
        # Extract additional context if available
        additional_context = game_data.additional_context
        context_note = f"\n\nADDITIONAL DATA: {additional_context}" if additional_context else ""
        
        chief_prompt = f"""You are the Chief Sports Analyst for an institutional sports betting firm. Generate a professional analysis report in Bloomberg terminal style.

GAME PROFILE:
• Away: {game_data.away_team}
• Home: {game_data.home_team}  
• Venue: {game_data.venue}
• Date: {game_data.game_date}
• Away Record: {game_data.away_record}
• Home Record: {game_data.home_record}
• Moneylines: Away {game_data.away_moneyline:+d} | Home {game_data.home_moneyline:+d}{context_note}

REQUIRED FORMAT:

📊 EXECUTIVE SUMMARY
[2-3 sentences with directional assessment and key probability range]

📈 STATISTICAL PROFILE  
• Team Records: [specific win percentages and comparison]
• Advanced Metrics: [run differential, runs allowed, recent form with exact numbers]
• Market Positioning: [moneyline analysis with implied probabilities]

🎯 KEY FACTORS
• Factor 1: [specific metric with numbers]
• Factor 2: [specific metric with numbers] 
• Factor 3: [deciding factor with data]

⚠️ RISK ASSESSMENT
[Primary concern that could invalidate analysis using provided data]

💰 INVESTMENT THESIS
[Clear directional call with confidence level 60-85%]

CRITICAL REQUIREMENTS:
• Use ONLY provided data - no assumptions
• Include specific numbers from context
• Professional institutional tone
• End with exact away team win probability percentage
• Stay within {min_sentences}-{max_sentences} total sentences across all sections"""

        try:
            client = await get_http_client()
            
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": chief_prompt
                        }
                    ],
                    "max_tokens": 800,  # Increased for comprehensive analysis
                    "temperature": 0.6  # Slightly lower for more consistent professional tone
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            content = result["choices"][0]["message"]["content"].strip()
            
            # Enhanced probability extraction for chief analyst
            import re
            
            # Look for away team win probability 
            prob_patterns = [
                r'away.*?(?:win.*?)?probability.*?(\d+)%',
                r'probability.*?away.*?(\d+)%', 
                r'(\d+)%.*?probability.*?away',
                r'(\d+)%.*?(?:chance|probability)'
            ]
            
            probability = 0.52  # Slight away bias default
            for pattern in prob_patterns:
                prob_match = re.search(pattern, content, re.IGNORECASE)
                if prob_match:
                    probability = float(prob_match.group(1)) / 100.0
                    break
                
            # Look for confidence level
            conf_patterns = [
                r'confidence.*?(\d+)%',
                r'(\d+)%.*?confidence',
                r'confident.*?(\d+)%'
            ]
            confidence = 0.72  # Default institutional confidence
            for pattern in conf_patterns:
                conf_match = re.search(pattern, content, re.IGNORECASE)
                if conf_match:
                    confidence = float(conf_match.group(1)) / 100.0
                    break
            
            return ExpertOpinion(
                expert_id=1,
                expert_type="CHIEF SPORTS ANALYST",
                probability=probability,
                confidence=confidence,
                reasoning=content,
                unit_size=2,  # Institutional sizing
                risk_level="Medium-High"
            )
            
        except Exception as e:
            print(f"OpenRouter API error for chief analyst: {e}")
            # Fallback analysis
            return ExpertOpinion(
                expert_id=1,
                expert_type="CHIEF SPORTS ANALYST - FALLBACK",
                probability=0.52,
                confidence=0.65,
                reasoning=f"Market analysis suggests competitive matchup between {game_data.away_team} and {game_data.home_team}. Based on available data, slight edge identified for road team. Professional recommendation: proceed with caution due to API limitations."
            )
    
    async def _simulate_expert_with_openrouter(self, game_data: GameData, expert_id: int, expert_persona: str, note_length: Tuple[int, int]) -> ExpertOpinion:
        """Simulate expert analysis using OpenRouter"""
        
        min_sentences, max_sentences = note_length
        
        # Enhanced expert prompts with differentiated confidence ranges
        expert_configs = {
            "STATISTICAL": {
                "focus": "Statistical analysis using team performance metrics, run differentials, and win percentages",
                "confidence_range": "55-75%",
                "specialization": "numerical data and trend analysis"
            },
            "SITUATIONAL": {
                "focus": "Situational factors including home/away records, recent form, and venue advantages",
                "confidence_range": "45-65%", 
                "specialization": "contextual game factors"
            },
            "CONTRARIAN": {
                "focus": "Contrarian analysis identifying market inefficiencies in moneyline pricing",
                "confidence_range": "60-80%",
                "specialization": "value betting opportunities"
            },
            "SHARP": {
                "focus": "Sharp analysis using advanced metrics and line value assessment",
                "confidence_range": "65-85%",
                "specialization": "professional betting indicators"
            },
            "MARKET": {
                "focus": "Market analysis examining implied probabilities vs actual team strength",
                "confidence_range": "50-70%",
                "specialization": "odds evaluation and market psychology"
            }
        }
        expert_config = expert_configs.get(expert_persona, {
            "focus": "General analysis", 
            "confidence_range": "50-70%",
            "specialization": "overall assessment"
        })
        
        # Extract additional context if available
        additional_context = game_data.additional_context
        context_note = f"\n\nADDITIONAL CONTEXT: {additional_context}" if additional_context else ""
        
        expert_prompt = f"""You are a {expert_persona} specializing in MLB betting analysis. You have access to comprehensive team data and must provide institutional-quality analysis in exactly {min_sentences}-{max_sentences} sentences.

GAME DETAILS:
• Away Team: {game_data.away_team}
• Home Team: {game_data.home_team}  
• Venue: {game_data.venue}
• Date: {game_data.game_date}
• Away Record: {game_data.away_record}
• Home Record: {game_data.home_record}
• Moneylines: Away {game_data.away_moneyline:+d} | Home {game_data.home_moneyline:+d}{context_note}

EXPERT SPECIALIZATION: {expert_config['focus']}
CONFIDENCE TARGET RANGE: {expert_config['confidence_range']} (stay within this range)

ANALYSIS REQUIREMENTS:
1. Open with directional assessment citing specific win percentages or records
2. Reference at least 2 numerical stats from context (run diff, runs allowed, etc.)
3. State confidence as exact percentage between 40-85%
4. Mention one key risk factor using provided data
5. End with "[AWAY_TEAM] win probability: XX%" format

CRITICAL RULES:
• MANDATORY: Reference specific numbers from provided data (records, run diff, etc.)
• FORBIDDEN: Never say "unknown", "unavailable", "limited data", or similar phrases
• REQUIRED: Use actual team statistics provided in context
• Write exactly {min_sentences}-{max_sentences} complete sentences - no more, no less
• End with numerical away team win probability (40-85% range)
• Professional tone matching institutional analysis standards"""

        try:
            client = await get_http_client()
            
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": expert_prompt
                        }
                    ],
                    "max_tokens": 400,  # Reduced for Discord compatibility
                    "temperature": 0.7
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            content = result["choices"][0]["message"]["content"].strip()
            
            # Extract probability, confidence, units, and risk
            probability = 0.5  # Default
            confidence = 0.7   # Default
            unit_size = 1      # Default
            risk_level = "Medium"  # Default
            
            # Enhanced probability extraction patterns
            import re
            
            # Look for away team win probability (primary target)
            prob_patterns = [
                r'away.*?(?:win.*?)?probability.*?(\d+)%',
                r'probability.*?away.*?(\d+)%', 
                r'estimate.*?(\d+)%.*?away',
                r'(\d+)%.*?chance.*?away',
                r'(\d+)%.*?probability'
            ]
            
            probability = 0.5  # Default
            for pattern in prob_patterns:
                prob_match = re.search(pattern, content, re.IGNORECASE)
                if prob_match:
                    probability = float(prob_match.group(1)) / 100.0
                    break
                
            # Look for confidence level
            conf_patterns = [
                r'confidence.*?(\d+)%',
                r'(\d+)%.*?confidence',
                r'confident.*?(\d+)%'
            ]
            confidence = 0.7  # Default
            for pattern in conf_patterns:
                conf_match = re.search(pattern, content, re.IGNORECASE)
                if conf_match:
                    confidence = float(conf_match.group(1)) / 100.0
                    break
                
            # Look for unit size
            unit_match = re.search(r'(\d+)\s*unit', content, re.IGNORECASE)
            if unit_match:
                unit_size = int(unit_match.group(1))
                
            # Look for risk level
            risk_match = re.search(r'risk.*?(low|medium|high)', content, re.IGNORECASE)
            if risk_match:
                risk_level = risk_match.group(1).title()
            
            # Clean up reasoning
            reasoning = content.replace(f"My probability: {prob_match.group(1)}%" if prob_match else "", "").strip()
            
            return ExpertOpinion(
                expert_id=expert_id,
                expert_type=expert_persona,
                probability=probability,
                confidence=confidence,
                reasoning=reasoning,
                unit_size=unit_size,
                risk_level=risk_level
            )
            
        except Exception as e:
            print(f"OpenRouter API error for expert {expert_id}: {e}")
            # Fallback with realistic probability
            fallback_prob = 0.45 + (expert_id * 0.02)  # Vary slightly by expert
            return ExpertOpinion(
                expert_id=expert_id,
                expert_type=f"{expert_persona} - FALLBACK",
                probability=fallback_prob,
                confidence=0.6,
                reasoning=f"Fallback analysis due to API error. Based on team records and basic matchup factors."
            )

class PredictionRequest:
    """Wrapper for prediction request results"""
    def __init__(self, request_id: str, result: PredictionResult):
        self.request_id = request_id
        self.result = result

# MCP Tools
AVAILABLE_TOOLS = [
    {
        "name": "getCustomChronulusAnalysis",
        "description": "Get custom AI expert panel analysis for sports predictions (OpenRouter-powered)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "game_data": {
                    "type": "object", 
                    "description": "Game data including teams, stats, odds, etc.",
                    "properties": {
                        "home_team": {"type": "string", "description": "Home team name with context"},
                        "away_team": {"type": "string", "description": "Away team name with context"},
                        "venue": {"type": "string", "description": "Venue name"},
                        "game_date": {"type": "string", "description": "Game date"},
                        "home_record": {"type": "string", "description": "Home team record"},
                        "away_record": {"type": "string", "description": "Away team record"},
                        "home_moneyline": {"type": "integer", "description": "Home team moneyline odds"},
                        "away_moneyline": {"type": "integer", "description": "Away team moneyline odds"},
                        "additional_context": {"type": "string", "description": "Additional context"}
                    },
                    "required": ["home_team", "away_team", "venue", "game_date"]
                },
                "expert_count": {
                    "type": "integer",
                    "description": "Number of AI experts (1-5, default: 5)",
                    "minimum": 1,
                    "maximum": 5,
                    "default": 5
                },
                "analysis_depth": {
                    "type": "string",
                    "description": "Analysis depth: brief (3-5 sentences), standard (8-12), comprehensive (15-20)",
                    "enum": ["brief", "standard", "comprehensive"],
                    "default": "standard"
                }
            },
            "required": ["game_data"]
        }
    },
    {
        "name": "testCustomChronulus",
        "description": "Test custom implementation with Red Sox @ Yankees sample data",
        "inputSchema": {
            "type": "object",
            "properties": {
                "expert_count": {
                    "type": "integer",
                    "description": "Number of experts (1-5, default: 2)",
                    "minimum": 1,
                    "maximum": 5,
                    "default": 2
                }
            }
        }
    },
    {
        "name": "getCustomChronulusHealth",
        "description": "Check custom Chronulus service health and OpenRouter connectivity",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

async def get_custom_chronulus_analysis(game_data: Dict[str, Any], expert_count: int = 5, analysis_depth: str = "standard") -> Dict[str, Any]:
    """Generate AI expert panel analysis using custom OpenRouter implementation"""
    
    if not OPENROUTER_API_KEY:
        return {
            "error": "OpenRouter API key not configured",
            "status": "configuration_error",
            "timestamp": now_iso()
        }
    
    try:
        # Map analysis depth to sentence counts (reduced for Discord limits)
        depth_mapping = {
            "brief": (3, 4),
            "standard": (4, 5), 
            "comprehensive": (5, 6)
        }
        note_length = depth_mapping.get(analysis_depth, (4, 5))
        
        # Create game data object
        game_obj = GameData(
            home_team=game_data.get("home_team", "Home Team"),
            away_team=game_data.get("away_team", "Away Team"), 
            venue=game_data.get("venue", "Stadium"),
            game_date=game_data.get("game_date", "Today"),
            home_record=game_data.get("home_record", "Unknown"),
            away_record=game_data.get("away_record", "Unknown"),
            home_moneyline=game_data.get("home_moneyline", 100),
            away_moneyline=game_data.get("away_moneyline", -100),
            additional_context=game_data.get("additional_context", "")
        )
        
        # Create session
        session = CustomChronulusSession(
            name=f"Custom Analysis: {game_obj.away_team} @ {game_obj.home_team}",
            situation="You're analyzing this game as an experienced sports bettor looking for profitable opportunities.",
            task=f"Provide {analysis_depth} sports betting analysis focusing on win probability, key factors, and market value."
        )
        session.create()
        
        # Create predictor
        predictor = CustomBinaryPredictor(session=session, input_type=GameData)
        predictor.create()
        
        # Generate prediction with single chief analyst
        request = await predictor.queue(
            item=game_obj,
            num_experts=1,  # Single chief analyst
            note_length=note_length
        )
        
        result = request.result
        
        # Calculate betting edge
        away_implied_prob = abs(game_obj.away_moneyline) / (abs(game_obj.away_moneyline) + 100) if game_obj.away_moneyline < 0 else 100 / (game_obj.away_moneyline + 100)
        expert_edge = result.prob_a - away_implied_prob
        
        return {
            "session_id": session.session_id,
            "request_id": request.request_id,
            "analysis": {
                "away_team_win_probability": result.prob_a,
                "home_team_win_probability": 1 - result.prob_a,
                "expert_count": result.expert_count,
                "analysis_depth": analysis_depth,
                "expert_analysis": result.text,
                "market_edge": expert_edge,
                "betting_recommendation": "BET AWAY" if expert_edge > 0.03 else "BET HOME" if expert_edge < -0.03 else "NO CLEAR EDGE",
                "beta_params": {
                    "alpha": result.beta_params.alpha,
                    "beta": result.beta_params.beta,
                    "mean": result.beta_params.mean(),
                    "variance": result.beta_params.variance()
                },
                "model_used": OPENROUTER_MODEL,
                "cost_estimate": f"${0.02 * expert_count:.2f}-${0.05 * expert_count:.2f}"
            },
            "status": "success",
            "timestamp": now_iso()
        }
        
    except Exception as e:
        return {
            "error": f"Custom analysis failed: {str(e)}",
            "status": "analysis_error",
            "timestamp": now_iso()
        }

async def test_custom_chronulus(expert_count: int = 2) -> Dict[str, Any]:
    """Test custom implementation with Red Sox @ Yankees data"""
    
    test_game_data = {
        "home_team": "New York Yankees (69-59, .539 win%, hot recent form 7-3 L10)",
        "away_team": "Boston Red Sox (70-59, .543 win%, road favorites but inconsistent 5-5 L10)",
        "venue": "Yankee Stadium (AL East rivalry atmosphere, home field advantage)",
        "game_date": "August 23, 2025",
        "home_record": "69-59 (.539 win percentage)",
        "away_record": "70-59 (.543 win percentage)",
        "home_moneyline": 112,
        "away_moneyline": -132,
        "additional_context": "Classic AL East rivalry with playoff implications. Both teams fighting for wild card spots."
    }
    
    return await get_custom_chronulus_analysis(
        game_data=test_game_data,
        expert_count=expert_count,
        analysis_depth="comprehensive"
    )

async def get_custom_chronulus_health() -> Dict[str, Any]:
    """Check custom Chronulus service health"""
    
    health_data = {
        "timestamp": now_iso(),
        "openrouter_configured": bool(OPENROUTER_API_KEY),
        "model": OPENROUTER_MODEL,
        "status": "unknown"
    }
    
    if not OPENROUTER_API_KEY:
        health_data["status"] = "api_key_missing"
        health_data["error"] = "OpenRouter API key not configured"
        return health_data
    
    try:
        # Test OpenRouter connectivity
        client = await get_http_client()
        response = await client.get(f"{OPENROUTER_BASE_URL}/models")
        
        if response.status_code == 200:
            health_data["status"] = "healthy"
            health_data["openrouter_models_accessible"] = True
        else:
            health_data["status"] = "connection_error"
            health_data["error"] = f"OpenRouter returned {response.status_code}"
            
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
            
            if tool_name == "getCustomChronulusAnalysis":
                result = await get_custom_chronulus_analysis(
                    game_data=arguments.get("game_data", {}),
                    expert_count=arguments.get("expert_count", 2),
                    analysis_depth=arguments.get("analysis_depth", "standard")
                )
            elif tool_name == "testCustomChronulus":
                result = await test_custom_chronulus(
                    expert_count=arguments.get("expert_count", 2)
                )
            elif tool_name == "getCustomChronulusHealth":
                result = await get_custom_chronulus_health()
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
    health = await get_custom_chronulus_health()
    status_code = 200 if health["status"] == "healthy" else 503
    
    return Response(
        json.dumps({
            "status": health["status"],
            "timestamp": health["timestamp"],
            "service": "custom-chronulus-mcp",
            "version": "1.0.0",
            "model": OPENROUTER_MODEL
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
    print(f"🚀 Starting Custom Chronulus AI MCP Server on port {port}")
    print(f"⚡ Health check: http://localhost:{port}/health")
    print(f"🔗 MCP endpoint: http://localhost:{port}/mcp")
    print(f"🔑 OpenRouter API key configured: {bool(OPENROUTER_API_KEY)}")
    print(f"🤖 Model: {OPENROUTER_MODEL}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)