"""
Soccer Channel Enricher Configuration
Quality of Life improvements and performance optimizations
"""

import os
from datetime import timedelta
from typing import Dict, Any, List

# ============================================================================
# ENRICHER CONFIGURATION
# ============================================================================

ENRICHER_CONFIG = {
    # Performance Settings
    "cache_ttl_seconds": 300,  # 5 minutes cache for team data
    "max_concurrent_enrichments": 3,  # Limit concurrent channel enrichments
    "enrichment_timeout_seconds": 60,  # Max time for single enrichment
    "batch_delay_seconds": 1.0,  # Delay between batch enrichments
    
    # Content Settings
    "max_insights_per_channel": 8,  # Limit insights to prevent spam
    "max_h2h_meetings_to_show": 5,  # Recent H2H meetings to display
    "max_form_matches_to_analyze": 10,  # Recent matches for form analysis
    "min_matches_for_reliable_analysis": 3,  # Minimum matches for analysis
    
    # Fallback Settings
    "enable_fallback_content": True,  # Always show some content
    "fallback_timeout_seconds": 10,  # Quick fallback if main enrichment fails
    "retry_failed_enrichments": True,  # Retry failed enrichments once
    "retry_delay_seconds": 5,  # Delay before retry
    
    # Data Quality Settings
    "min_h2h_meetings_for_analysis": 2,  # Minimum H2H meetings for reliable analysis
    "min_team_matches_for_form": 3,  # Minimum matches for form analysis
    "confidence_threshold": 0.6,  # Minimum confidence for predictions
    
    # UI/UX Settings
    "use_progressive_loading": True,  # Load content progressively
    "pin_welcome_message": True,  # Pin the main match preview
    "use_reaction_indicators": True,  # Add reactions for key insights
    "embed_color_by_league": True,  # Use league colors for embeds
    
    # Error Handling
    "log_enrichment_performance": True,  # Log timing and performance metrics
    "alert_on_enrichment_failures": False,  # Alert admins on failures (not implemented)
    "graceful_degradation": True,  # Always provide some content
}

# League-specific configurations
LEAGUE_ENRICHMENT_CONFIG = {
    "EPL": {
        "priority": 1,
        "color": 0x3d195b,  # Premier League purple
        "emoji": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        "enhanced_analytics": True,  # Full analytics for major leagues
        "betting_insights": True,
        "historical_depth_days": 365,  # Look back 1 year for H2H
    },
    "La Liga": {
        "priority": 2,
        "color": 0xff6900,  # La Liga orange
        "emoji": "🇪🇸",
        "enhanced_analytics": True,
        "betting_insights": True,
        "historical_depth_days": 365,
    },
    "UEFA": {
        "priority": 0,  # Highest priority
        "color": 0x00336a,  # UEFA dark blue
        "emoji": "🏆",
        "enhanced_analytics": True,
        "betting_insights": True,
        "historical_depth_days": 730,  # Look back 2 years for Champions League
    },
    "Bundesliga": {
        "priority": 3,
        "color": 0xd20515,  # Bundesliga red
        "emoji": "🇩🇪",
        "enhanced_analytics": True,
        "betting_insights": True,
        "historical_depth_days": 365,
    },
    "Serie A": {
        "priority": 4,
        "color": 0x0066cc,  # Serie A blue
        "emoji": "🇮🇹",
        "enhanced_analytics": True,
        "betting_insights": True,
        "historical_depth_days": 365,
    },
    "MLS": {
        "priority": 5,
        "color": 0x005da6,  # MLS blue
        "emoji": "🇺🇸",
        "enhanced_analytics": False,  # Basic analytics for lower priority
        "betting_insights": False,
        "historical_depth_days": 180,  # 6 months for MLS
    }
}

# Content templates for consistency
CONTENT_TEMPLATES = {
    "welcome_message": {
        "title_format": "⚽ {home_team} vs {away_team}",
        "description_format": "**{league}** | {date} at {time}\n📍 {venue}",
        "footer_text": "🔄 Loading comprehensive analysis..."
    },
    
    "h2h_analysis": {
        "title_format": "📈 Head-to-Head Analysis", 
        "no_data_message": "These teams haven't met recently or data is unavailable.",
        "min_meetings_message": "Limited historical data available ({meetings} meetings found)",
    },
    
    "team_form": {
        "title_format_home": "🏠 {team_name} - Recent Form Analysis",
        "title_format_away": "✈️ {team_name} - Recent Form Analysis",
        "no_data_message": "Recent match data unavailable",
        "form_summary_format": "**Record:** {wins}W-{draws}D-{losses}L ({win_rate:.1f}%)\n**Form:** {form_string}\n**Goals:** {goals_for:.1f} for, {goals_against:.1f} against"
    },
    
    "betting_analysis": {
        "title_format": "💰 Betting Analysis & Predictions",
        "confidence_indicators": {
            "high": "🔥 HIGH",
            "medium": "⚖️ MEDIUM", 
            "low": "⚠️ LOW"
        },
        "recommendation_format": "**{market}:** {recommendation} ({confidence} confidence)"
    },
    
    "tactical_insights": {
        "title_format": "🎯 Key Tactical Insights",
        "methodology_note": "Analysis based on historical data and current form",
        "categories": {
            "historical": "📈 Historical Patterns",
            "form": "🔥 Current Form", 
            "tactical": "⚽ Tactical Patterns",
            "betting": "💰 Betting Opportunities"
        }
    }
}

# Insight generation rules
INSIGHT_RULES = {
    "form_insights": {
        "excellent_form_threshold": 0.8,  # 80%+ win rate
        "poor_form_threshold": 0.3,  # 30% or less win rate
        "strong_attack_threshold": 2.0,  # 2+ goals per game
        "weak_attack_threshold": 1.0,  # <1 goal per game
        "solid_defense_threshold": 1.0,  # <1 goal conceded per game
        "leaky_defense_threshold": 2.0,  # 2+ goals conceded per game
    },
    
    "h2h_insights": {
        "dominance_threshold": 0.6,  # 60%+ win rate = dominance
        "high_scoring_threshold": 3.0,  # 3+ goals average = high scoring
        "low_scoring_threshold": 2.0,  # <2 goals average = low scoring
        "home_advantage_threshold": 0.1,  # 10% better at home
    },
    
    "betting_insights": {
        "btts_likely_threshold": 0.6,  # 60%+ BTTS rate
        "btts_unlikely_threshold": 0.3,  # 30% or less BTTS rate
        "over_likely_threshold": 0.6,  # 60%+ over 2.5 rate
        "under_likely_threshold": 0.3,  # 30% or less over 2.5 rate
        "high_cards_threshold": 4.0,  # 4+ cards per game
        "late_drama_threshold": 0.5,  # 50%+ games with late goals
    }
}

# Performance monitoring thresholds
PERFORMANCE_THRESHOLDS = {
    "enrichment_time_warning": 30.0,  # Warn if enrichment takes >30s
    "enrichment_time_error": 60.0,    # Error if enrichment takes >60s
    "api_response_warning": 10.0,     # Warn if API takes >10s
    "api_response_error": 20.0,       # Error if API takes >20s
    "memory_usage_warning": 100,      # Warn if using >100MB
    "cache_hit_rate_minimum": 0.3,    # Minimum 30% cache hit rate
}

# Rate limiting and throttling
RATE_LIMITS = {
    "max_enrichments_per_minute": 10,  # Limit to prevent spam
    "max_api_calls_per_minute": 30,    # API rate limiting
    "cooldown_between_similar_requests": 60,  # 1 minute cooldown for same match
    "backoff_on_api_errors": True,     # Exponential backoff on errors
    "max_retries": 3,                  # Maximum retry attempts
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_league_config(league_code: str) -> Dict[str, Any]:
    """Get configuration for a specific league"""
    return LEAGUE_ENRICHMENT_CONFIG.get(league_code, LEAGUE_ENRICHMENT_CONFIG["EPL"])

def get_league_color(league_code: str) -> int:
    """Get embed color for league"""
    config = get_league_config(league_code)
    return config.get("color", 0x00ff00)

def should_use_enhanced_analytics(league_code: str) -> bool:
    """Check if league should use enhanced analytics"""
    config = get_league_config(league_code)
    return config.get("enhanced_analytics", False)

def get_historical_depth_days(league_code: str) -> int:
    """Get how far back to look for historical data"""
    config = get_league_config(league_code)
    return config.get("historical_depth_days", 365)

def get_confidence_indicator(confidence: float) -> str:
    """Get confidence indicator string"""
    indicators = CONTENT_TEMPLATES["betting_analysis"]["confidence_indicators"]
    if confidence >= 0.7:
        return indicators["high"]
    elif confidence >= 0.5:
        return indicators["medium"]
    else:
        return indicators["low"]

def should_generate_insight(insight_type: str, value: float, threshold_key: str) -> bool:
    """Check if an insight should be generated based on thresholds"""
    thresholds = INSIGHT_RULES.get(insight_type, {})
    threshold = thresholds.get(threshold_key, 0.5)
    
    if "likely" in threshold_key or "strong" in threshold_key or "excellent" in threshold_key:
        return value >= threshold
    elif "unlikely" in threshold_key or "weak" in threshold_key or "poor" in threshold_key:
        return value <= threshold
    else:
        return abs(value) >= threshold

def get_content_template(template_type: str, template_key: str) -> str:
    """Get content template string"""
    templates = CONTENT_TEMPLATES.get(template_type, {})
    return templates.get(template_key, "")

def is_performance_warning(metric: str, value: float) -> bool:
    """Check if performance metric indicates a warning"""
    warning_threshold = PERFORMANCE_THRESHOLDS.get(f"{metric}_warning", float('inf'))
    return value >= warning_threshold

def is_performance_error(metric: str, value: float) -> bool:
    """Check if performance metric indicates an error"""
    error_threshold = PERFORMANCE_THRESHOLDS.get(f"{metric}_error", float('inf'))
    return value >= error_threshold

def get_rate_limit(limit_type: str) -> int:
    """Get rate limit value"""
    return RATE_LIMITS.get(limit_type, 10)

# ============================================================================
# ENVIRONMENT-SPECIFIC OVERRIDES
# ============================================================================

def apply_environment_overrides():
    """Apply environment-specific configuration overrides"""
    
    # Override from environment variables
    if os.getenv('ENRICHER_CACHE_TTL'):
        ENRICHER_CONFIG['cache_ttl_seconds'] = int(os.getenv('ENRICHER_CACHE_TTL'))
    
    if os.getenv('ENRICHER_MAX_CONCURRENT'):
        ENRICHER_CONFIG['max_concurrent_enrichments'] = int(os.getenv('ENRICHER_MAX_CONCURRENT'))
    
    if os.getenv('ENRICHER_TIMEOUT'):
        ENRICHER_CONFIG['enrichment_timeout_seconds'] = int(os.getenv('ENRICHER_TIMEOUT'))
    
    # Production vs Development settings
    environment = os.getenv('ENVIRONMENT', 'development').lower()
    
    if environment == 'production':
        # More conservative settings for production
        ENRICHER_CONFIG['max_concurrent_enrichments'] = 2
        ENRICHER_CONFIG['enrichment_timeout_seconds'] = 45
        ENRICHER_CONFIG['log_enrichment_performance'] = True
        RATE_LIMITS['max_enrichments_per_minute'] = 5
        
    elif environment == 'development':
        # More liberal settings for development
        ENRICHER_CONFIG['cache_ttl_seconds'] = 60  # Shorter cache for testing
        ENRICHER_CONFIG['max_concurrent_enrichments'] = 5
        ENRICHER_CONFIG['log_enrichment_performance'] = True
        
    elif environment == 'testing':
        # Fast settings for testing
        ENRICHER_CONFIG['cache_ttl_seconds'] = 10
        ENRICHER_CONFIG['enrichment_timeout_seconds'] = 20
        ENRICHER_CONFIG['enable_fallback_content'] = True
        ENRICHER_CONFIG['retry_failed_enrichments'] = False

# Apply overrides on import
apply_environment_overrides()

# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_enricher_config() -> Dict[str, Any]:
    """Validate enricher configuration"""
    validation_result = {
        "valid": True,
        "warnings": [],
        "errors": []
    }
    
    # Check required settings
    if ENRICHER_CONFIG['enrichment_timeout_seconds'] < 10:
        validation_result["warnings"].append("Enrichment timeout is very low, may cause incomplete data")
    
    if ENRICHER_CONFIG['cache_ttl_seconds'] < 30:
        validation_result["warnings"].append("Cache TTL is very low, may impact performance")
    
    if ENRICHER_CONFIG['max_concurrent_enrichments'] > 10:
        validation_result["warnings"].append("High concurrent enrichments may overwhelm APIs")
    
    # Check league configurations
    for league_code, config in LEAGUE_ENRICHMENT_CONFIG.items():
        if config['historical_depth_days'] > 1095:  # 3 years
            validation_result["warnings"].append(f"{league_code}: Historical depth is very high")
    
    # Check performance thresholds
    if PERFORMANCE_THRESHOLDS['enrichment_time_warning'] > PERFORMANCE_THRESHOLDS['enrichment_time_error']:
        validation_result["errors"].append("Performance warning threshold is higher than error threshold")
        validation_result["valid"] = False
    
    return validation_result

# Validate configuration on import
_validation = validate_enricher_config()
if not _validation["valid"]:
    raise ValueError(f"Invalid enricher configuration: {_validation['errors']}")

if _validation["warnings"]:
    import logging
    logger = logging.getLogger(__name__)
    for warning in _validation["warnings"]:
        logger.warning(f"Enricher config warning: {warning}")