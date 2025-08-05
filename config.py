"""
Configuration for WNBA Daily Analyzer
"""

# API Configuration
ESPN_BASE_URL = "http://site.api.espn.com"
REQUEST_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "ESPN-Research/1.0"
}

# Analysis Settings
HOME_COURT_ADVANTAGE = 0.05  # 5% advantage for home teams
CONFIDENCE_THRESHOLDS = {
    'STRONG': 0.8,
    'MODERATE': 0.6,
    'LEAN': 0.4,
    'AVOID': 0.0
}

# Output Settings
OUTPUT_DIR = "daily_reports"
REPORT_FORMAT = "markdown"  # or "json", "csv"

# Rate Limiting (to be nice to ESPN's API)
REQUEST_DELAY = 0.5  # seconds between requests
MAX_RETRIES = 3

# Betting Categories
BET_TYPES = {
    'moneyline': {'weight': 1.0, 'description': 'Team to win'},
    'spread': {'weight': 0.8, 'description': 'Point spread'},
    'total': {'weight': 0.6, 'description': 'Over/Under points'}
}

# Team Performance Weights
STAT_WEIGHTS = {
    'win_percentage': 0.3,
    'point_differential': 0.25,
    'home_away_record': 0.2,
    'recent_form': 0.15,
    'head_to_head': 0.1
}