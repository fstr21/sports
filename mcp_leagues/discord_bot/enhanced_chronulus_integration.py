#!/usr/bin/env python3
"""
Enhanced Chronulus Integration for Discord Bot
Uses the comprehensive approach from the test script to provide rich analysis
"""

import asyncio
import json
import httpx
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import discord

logger = logging.getLogger(__name__)

class EnhancedChronulusIntegration:
    """Enhanced integration with Custom Chronulus using comprehensive data approach"""
    
    def __init__(self):
        self.chronulus_url = "https://customchronpredictormcp-production.up.railway.app/mcp"
    
    async def create_comprehensive_game_data(self, match, betting_odds: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create comprehensive game data similar to the test script"""
        try:
            # Extract basic info
            home_team = match.home_team
            away_team = match.away_team
            
            # Get enhanced data from match
            additional_data = match.additional_data or {}
            basic_game_info = additional_data.get("basic_game_info", {})
            team_forms = additional_data.get("team_forms", {})
            scoring_trends = additional_data.get("scoring_trends", {})
            
            # Build team context with records and performance
            home_form = team_forms.get("home", {}).get("form", {})
            away_form = team_forms.get("away", {}).get("form", {})
            
            home_record = f"{home_form.get('wins', 'N/A')}-{home_form.get('losses', 'N/A')}"
            away_record = f"{away_form.get('wins', 'N/A')}-{away_form.get('losses', 'N/A')}"
            home_win_pct = home_form.get('win_percentage', 0)
            away_win_pct = away_form.get('win_percentage', 0)
            
            # Enhanced team descriptions
            home_team_enhanced = f"{home_team} ({home_record}, .{home_win_pct:.3f} win%)"
            away_team_enhanced = f"{away_team} ({away_record}, .{away_win_pct:.3f} win%)"
            
            # Get venue and timing
            venue_info = basic_game_info.get("venue", "Stadium")
            start_time = basic_game_info.get("start_et", "TBD")
            venue_enhanced = f"{venue_info} ({start_time} ET)" if start_time != "TBD" else venue_info
            
            # Get moneylines from betting odds or defaults
            home_ml = -150  # Default
            away_ml = 130   # Default
            
            if betting_odds:
                try:
                    # Parse moneylines from betting_odds if available
                    home_ml_str = betting_odds.get("home_moneyline", "-150")
                    away_ml_str = betting_odds.get("away_moneyline", "+130")
                    home_ml = int(home_ml_str.replace("+", ""))
                    away_ml = int(away_ml_str.replace("+", ""))
                except:
                    pass
            
            # Build comprehensive additional context
            context_parts = []
            
            # Market data section
            home_implied = abs(home_ml) / (abs(home_ml) + 100) if home_ml < 0 else 100 / (home_ml + 100)
            away_implied = abs(away_ml) / (abs(away_ml) + 100) if away_ml < 0 else 100 / (away_ml + 100)
            
            context_parts.append(
                f"COMPLETE MARKET DATA: "
                f"Moneyline - {home_team} {home_ml:+d} ({home_implied:.1%} implied), {away_team} {away_ml:+d} ({away_implied:.1%} implied). "
            )
            
            # Team performance section
            home_scoring = scoring_trends.get("home", {}).get("trends", {})
            away_scoring = scoring_trends.get("away", {}).get("trends", {})
            
            home_rpg = home_scoring.get("runs_per_game", "N/A")
            home_rapg = home_scoring.get("runs_allowed_per_game", "N/A")
            away_rpg = away_scoring.get("runs_per_game", "N/A") 
            away_rapg = away_scoring.get("runs_allowed_per_game", "N/A")
            
            context_parts.append(
                f"TEAM PERFORMANCE: "
                f"{home_team}: {home_record} record, {home_rpg} R/G scored, {home_rapg} R/G allowed. "
                f"{away_team}: {away_record} record, {away_rpg} R/G scored, {away_rapg} R/G allowed. "
            )
            
            # Situational factors
            context_parts.append(
                f"SITUATIONAL FACTORS: "
                f"Regular season MLB game with competitive matchup. "
                f"Both teams looking to improve standings. "
                f"Game played at {venue_info} with standard field dimensions. "
            )
            
            # Recent form if available
            home_streak = home_form.get("streak", "N/A")
            away_streak = away_form.get("streak", "N/A")
            if home_streak != "N/A" and away_streak != "N/A":
                context_parts.append(
                    f"RECENT FORM: "
                    f"{home_team} current streak: {home_streak}. "
                    f"{away_team} current streak: {away_streak}. "
                )
            
            additional_context = " ".join(context_parts)
            
            # Create comprehensive game data structure
            comprehensive_game_data = {
                "home_team": home_team_enhanced,
                "away_team": away_team_enhanced,
                "sport": "Baseball",
                "venue": venue_enhanced,
                "game_date": datetime.now().strftime("%B %d, %Y"),
                "home_record": f"{home_record} (.{home_win_pct:.3f} win%), home field advantage",
                "away_record": f"{away_record} (.{away_win_pct:.3f} win%), road team dynamics",
                "home_moneyline": home_ml,
                "away_moneyline": away_ml,
                "additional_context": additional_context
            }
            
            return comprehensive_game_data
            
        except Exception as e:
            logger.error(f"Error creating comprehensive game data: {e}")
            # Fallback to basic data
            return {
                "home_team": match.home_team,
                "away_team": match.away_team,
                "sport": "Baseball", 
                "venue": "Stadium",
                "game_date": datetime.now().strftime("%B %d, %Y"),
                "home_record": "Record TBD",
                "away_record": "Record TBD",
                "home_moneyline": -150,
                "away_moneyline": 130,
                "additional_context": "Basic game analysis with limited data available"
            }
    
    async def call_comprehensive_chronulus_analysis(self, match, betting_odds: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Call Custom Chronulus with comprehensive data approach"""
        try:
            # Create comprehensive game data
            comprehensive_game_data = await self.create_comprehensive_game_data(match, betting_odds)
            
            # MCP request with comprehensive data
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 1,
                "params": {
                    "name": "getCustomChronulusAnalysis",
                    "arguments": {
                        "game_data": comprehensive_game_data,
                        "expert_count": 1,  # Single Chief Analyst
                        "analysis_depth": "comprehensive"
                    }
                }
            }
            
            logger.info(f"Calling comprehensive Chronulus analysis for {match.away_team} @ {match.home_team}")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(self.chronulus_url, json=mcp_request)
                response.raise_for_status()
                result = response.json()
                
                if "result" not in result:
                    error_msg = result.get('error', 'Unknown error')
                    logger.error(f"Chronulus MCP Error: {error_msg}")
                    return None
                
                # Parse response
                mcp_result = result["result"]
                if "content" not in mcp_result or not isinstance(mcp_result["content"], list):
                    logger.error(f"Unexpected Chronulus response format: {mcp_result}")
                    return None
                
                analysis_text = mcp_result["content"][0]["text"]
                
                try:
                    # Parse JSON response
                    analysis_data = json.loads(analysis_text)
                    logger.info(f"Successfully received comprehensive Chronulus analysis")
                    return analysis_data
                    
                except json.JSONDecodeError:
                    # Handle text response
                    logger.warning("Received text response from Chronulus instead of JSON")
                    return {
                        "format": "text",
                        "analysis_text": analysis_text,
                        "status": "success"
                    }
                    
        except Exception as e:
            logger.error(f"Error calling comprehensive Chronulus analysis: {e}")
            return None
    
    async def create_enhanced_analysis_embed(self, match, chronulus_data: Dict[str, Any]) -> Optional[discord.Embed]:
        """Create enhanced Discord embed with comprehensive analysis"""
        try:
            if not chronulus_data:
                return None
            
            # Create main analysis embed
            embed = discord.Embed(
                title=f"🤖 AI Chief Analyst • {match.away_team} @ {match.home_team}",
                description="Institutional-Grade Market Analysis (85% cost savings vs paid services)",
                color=0x00aa00,
                timestamp=datetime.now()
            )
            
            # Handle different response formats
            if chronulus_data.get("format") == "text":
                # Text format response
                analysis_text = chronulus_data.get("analysis_text", "")
                embed.add_field(
                    name="📊 Chief Analyst Report",
                    value=analysis_text[:1000] + "..." if len(analysis_text) > 1000 else analysis_text,
                    inline=False
                )
                
            else:
                # JSON format response
                analysis_data = chronulus_data.get("analysis", {})
                
                if analysis_data:
                    # Win probabilities with market comparison
                    away_prob = analysis_data.get("away_team_win_probability", 0) * 100
                    home_prob = analysis_data.get("home_team_win_probability", 0) * 100
                    
                    embed.add_field(
                        name="🎯 Win Probability Assessment",
                        value=f"**{match.away_team}**: {away_prob:.1f}%\n**{match.home_team}**: {home_prob:.1f}%",
                        inline=True
                    )
                    
                    # Market edge and recommendation
                    market_edge = analysis_data.get("market_edge", 0) * 100
                    recommendation = analysis_data.get("betting_recommendation", "N/A")
                    
                    embed.add_field(
                        name="💰 Betting Intelligence",
                        value=f"**Recommendation**: {recommendation}\n**Market Edge**: {market_edge:+.1f}%",
                        inline=True
                    )
                    
                    # Technical details
                    expert_count = analysis_data.get("expert_count", 1)
                    model_used = analysis_data.get("model_used", "N/A")
                    cost_estimate = analysis_data.get("cost_estimate", "N/A")
                    
                    embed.add_field(
                        name="🔧 Analysis Details",
                        value=f"**Model**: {model_used}\n**Cost**: {cost_estimate}\n**Experts**: {expert_count}",
                        inline=True
                    )
                    
                    # Expert analysis (truncated for Discord)
                    expert_analysis = analysis_data.get("expert_analysis", "")
                    if expert_analysis:
                        # Extract key sections
                        if "[CHIEF ANALYST]" in expert_analysis:
                            analysis_content = expert_analysis.split("[CHIEF ANALYST]", 1)[1].strip()
                        else:
                            analysis_content = expert_analysis
                        
                        # Truncate for Discord limits
                        if len(analysis_content) > 800:
                            analysis_content = analysis_content[:800] + "..."
                        
                        embed.add_field(
                            name="📋 Chief Analyst Report",
                            value=analysis_content,
                            inline=False
                        )
            
            embed.set_footer(text="Enhanced Custom Chronulus MCP • Comprehensive Analysis")
            return embed
            
        except Exception as e:
            logger.error(f"Error creating enhanced analysis embed: {e}")
            return None