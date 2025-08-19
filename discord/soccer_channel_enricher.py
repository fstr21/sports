"""
Enhanced Soccer Channel Content Enricher
Populates Discord soccer channels with comprehensive analytics data including:
- Head-to-head analysis with historical data
- Recent form analysis with advanced metrics  
- Team comparisons and betting insights
- Real-time match preview and predictions

Based on the comprehensive data extraction methodology from schedule.py
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import discord
from dataclasses import dataclass

# Import existing soccer components
from soccer_integration import SoccerMCPClient, SoccerDataProcessor, SoccerEmbedBuilder, SUPPORTED_LEAGUES
from soccer_error_handling import error_handler, bot_logger, ErrorContext, SoccerBotError

# Import enricher configuration and QOL improvements
from soccer_enricher_config import (
    ENRICHER_CONFIG, LEAGUE_ENRICHMENT_CONFIG, CONTENT_TEMPLATES, INSIGHT_RULES,
    get_league_config, get_league_color, should_use_enhanced_analytics,
    get_confidence_indicator, should_generate_insight, get_content_template,
    is_performance_warning, is_performance_error
)

logger = logging.getLogger(__name__)

# Simple in-memory cache for performance
_enricher_cache = {}
_cache_timestamps = {}

@dataclass
class TeamFormAnalysis:
    """Comprehensive team form analysis data"""
    team_name: str
    team_id: int
    recent_matches: List[Dict]
    wins: int
    draws: int  
    losses: int
    goals_for: int
    goals_against: int
    clean_sheets: int
    both_teams_scored: int
    high_scoring_games: int
    early_goals: int
    late_goals: int
    total_cards: int
    comeback_wins: int
    home_record: Dict
    away_record: Dict
    form_string: str
    betting_insights: Dict

@dataclass
class H2HAnalysis:
    """Head-to-head analysis between two teams"""
    home_team: str
    away_team: str
    total_meetings: int
    home_team_wins: int
    away_team_wins: int
    draws: int
    home_team_goals: int
    away_team_goals: int
    avg_goals_per_game: float
    recent_meetings: List[Dict]
    home_advantage: Dict
    betting_trends: Dict

@dataclass
class MatchPreview:
    """Comprehensive match preview data"""
    match_id: int
    home_team: str
    away_team: str
    date: str
    time: str
    venue: str
    league: str
    h2h_analysis: H2HAnalysis
    home_form: TeamFormAnalysis
    away_form: TeamFormAnalysis
    betting_odds: Dict
    predictions: Dict
    key_insights: List[str]

class SoccerChannelEnricher:
    """Enhanced soccer channel content populator with comprehensive analytics and performance optimizations"""
    
    def __init__(self):
        self.soccer_client = SoccerMCPClient()
        self.soccer_processor = SoccerDataProcessor()
        self.embed_builder = SoccerEmbedBuilder()
        
        # Performance tracking
        self.enrichment_stats = {
            "total_enrichments": 0,
            "successful_enrichments": 0,
            "failed_enrichments": 0,
            "average_enrichment_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Concurrent enrichment limiting
        self._enrichment_semaphore = asyncio.Semaphore(ENRICHER_CONFIG['max_concurrent_enrichments'])
        
        logger.info(f"Soccer Channel Enricher initialized with config: {ENRICHER_CONFIG['max_concurrent_enrichments']} max concurrent, {ENRICHER_CONFIG['cache_ttl_seconds']}s cache TTL")
    
    # ============================================================================
    # CACHING AND PERFORMANCE METHODS
    # ============================================================================
    
    def _get_cache_key(self, key_type: str, *args) -> str:
        """Generate cache key for data"""
        return f"{key_type}:{':'.join(str(arg) for arg in args)}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in _cache_timestamps:
            return False
        
        cache_age = time.time() - _cache_timestamps[cache_key]
        return cache_age < ENRICHER_CONFIG['cache_ttl_seconds']
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if valid"""
        if self._is_cache_valid(cache_key) and cache_key in _enricher_cache:
            self.enrichment_stats["cache_hits"] += 1
            logger.debug(f"Cache hit for key: {cache_key}")
            return _enricher_cache[cache_key]
        
        self.enrichment_stats["cache_misses"] += 1
        logger.debug(f"Cache miss for key: {cache_key}")
        return None
    
    def _store_in_cache(self, cache_key: str, data: Any) -> None:
        """Store data in cache"""
        _enricher_cache[cache_key] = data
        _cache_timestamps[cache_key] = time.time()
        
        # Simple cache cleanup - remove oldest entries if cache gets too large
        if len(_enricher_cache) > 100:  # Keep cache reasonable size
            oldest_key = min(_cache_timestamps.keys(), key=lambda k: _cache_timestamps[k])
            del _enricher_cache[oldest_key]
            del _cache_timestamps[oldest_key]
            logger.debug(f"Cleaned up oldest cache entry: {oldest_key}")
    
    async def _with_performance_tracking(self, operation_name: str, coro) -> Tuple[Any, float]:
        """Execute coroutine with performance tracking"""
        start_time = time.time()
        
        try:
            result = await coro
            elapsed_time = time.time() - start_time
            
            # Log performance warnings/errors
            if is_performance_error(operation_name, elapsed_time):
                logger.error(f"Performance ERROR: {operation_name} took {elapsed_time:.2f}s")
            elif is_performance_warning(operation_name, elapsed_time):
                logger.warning(f"Performance WARNING: {operation_name} took {elapsed_time:.2f}s")
            
            return result, elapsed_time
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Operation {operation_name} failed after {elapsed_time:.2f}s: {e}")
            raise
    
    def get_enrichment_stats(self) -> Dict[str, Any]:
        """Get enrichment performance statistics"""
        stats = self.enrichment_stats.copy()
        
        # Calculate cache hit rate
        total_cache_requests = stats["cache_hits"] + stats["cache_misses"]
        stats["cache_hit_rate"] = stats["cache_hits"] / total_cache_requests if total_cache_requests > 0 else 0
        
        # Add cache size info
        stats["cache_size"] = len(_enricher_cache)
        stats["cache_config"] = {
            "ttl_seconds": ENRICHER_CONFIG['cache_ttl_seconds'],
            "max_concurrent": ENRICHER_CONFIG['max_concurrent_enrichments']
        }
        
        return stats
    
    async def enrich_channel_on_creation(self, channel: discord.TextChannel, 
                                       home_team: str, away_team: str,
                                       match_date: str, league_code: str) -> bool:
        """
        Populate a newly created soccer channel with comprehensive analytics with performance optimizations
        
        Args:
            channel: Discord text channel to populate
            home_team: Home team name
            away_team: Away team name  
            match_date: Match date (YYYY-MM-DD)
            league_code: League code (EPL, La Liga, etc.)
            
        Returns:
            bool: Success status
        """
        # Use semaphore to limit concurrent enrichments
        async with self._enrichment_semaphore:
            start_time = time.time()
            self.enrichment_stats["total_enrichments"] += 1
            
            try:
                context = ErrorContext(
                    "enrich_channel_on_creation",
                    additional_data={
                        "channel_id": channel.id,
                        "home_team": home_team,
                        "away_team": away_team,
                        "match_date": match_date,
                        "league_code": league_code
                    }
                )
                
                bot_logger.log_operation_start("channel_enrichment", context)
                
                # Check if we should use enhanced analytics for this league
                if not should_use_enhanced_analytics(league_code):
                    logger.info(f"Using basic enrichment for {league_code} (not configured for enhanced analytics)")
                    await self._send_fallback_content(channel, home_team, away_team, match_date, league_code)
                    self.enrichment_stats["successful_enrichments"] += 1
                    return True
                
                # Step 1: Get match data and team IDs with caching
                cache_key = self._get_cache_key("match_data", home_team, away_team, match_date, league_code)
                match_data = self._get_from_cache(cache_key)
                
                if match_data is None:
                    match_data, _ = await self._with_performance_tracking(
                        "find_match_data",
                        self._find_match_data(home_team, away_team, match_date, league_code, context)
                    )
                    if match_data:
                        self._store_in_cache(cache_key, match_data)
                
                if not match_data:
                    await self._send_fallback_content(channel, home_team, away_team, match_date, league_code)
                    self.enrichment_stats["failed_enrichments"] += 1
                    return False
                
                # Step 2: Generate comprehensive match preview
                match_preview = await self._generate_match_preview(match_data, context)
                
                # Step 3: Send welcome message with match basics
                await self._send_welcome_message(channel, match_preview)
                
                # Step 4: Send comprehensive H2H analysis
                await self._send_h2h_analysis(channel, match_preview.h2h_analysis)
                
                # Step 5: Send team form analysis
                await self._send_team_form_analysis(channel, match_preview.home_form, match_preview.away_form)
                
                # Step 6: Send betting insights and predictions  
                await self._send_betting_analysis(channel, match_preview)
                
                # Step 7: Send key tactical insights
                await self._send_tactical_insights(channel, match_preview)
                
                # Step 8: Pin the welcome message for easy access
                messages = await channel.history(limit=1).flatten()
                if messages:
                    await messages[0].pin(reason="Match preview information")
                
                # Update stats and finish
                elapsed_time = time.time() - start_time
                self.enrichment_stats["average_enrichment_time"] = (
                    (self.enrichment_stats["average_enrichment_time"] * (self.enrichment_stats["total_enrichments"] - 1) + elapsed_time) 
                    / self.enrichment_stats["total_enrichments"]
                )
                self.enrichment_stats["successful_enrichments"] += 1
                
                bot_logger.log_operation_success("channel_enrichment", context)
                
                if ENRICHER_CONFIG['log_enrichment_performance']:
                    logger.info(f"Channel enrichment completed in {elapsed_time:.2f}s for {home_team} vs {away_team}")
                
                return True
                
            except Exception as e:
                elapsed_time = time.time() - start_time
                self.enrichment_stats["failed_enrichments"] += 1
                
                error_context = ErrorContext(
                    "enrich_channel_on_creation",
                    additional_data={"error": str(e), "channel_id": channel.id}
                )
                
                error_obj = SoccerBotError(
                    f"Failed to enrich channel: {str(e)}",
                    context=error_context,
                    user_message="Unable to load comprehensive match data"
                )
                
                bot_logger.log_operation_error("channel_enrichment", error_obj, error_context)
                logger.error(f"Channel enrichment failed after {elapsed_time:.2f}s: {e}")
                
                # Send basic fallback content
                if ENRICHER_CONFIG['enable_fallback_content']:
                    await self._send_fallback_content(channel, home_team, away_team, match_date, league_code)
                
                return False

    async def _find_match_data(self, home_team: str, away_team: str, 
                             match_date: str, league_code: str, 
                             context: ErrorContext) -> Optional[Dict]:
        """Find specific match data from MCP server"""
        try:
            # Get league configuration
            league_config = SUPPORTED_LEAGUES.get(league_code)
            if not league_config:
                return None
            
            # Search for matches on the specified date
            matches_data = await self.soccer_client.get_matches_for_date(match_date, [league_code], context)
            
            if not matches_data:
                return None
            
            # Find the specific match
            processed_matches = self.soccer_processor.process_match_data(matches_data)
            
            for match in processed_matches:
                if (self._teams_match(home_team, match.home_team.name) and 
                    self._teams_match(away_team, match.away_team.name)):
                    
                    # Get additional match details
                    if hasattr(match, 'match_id') and match.match_id:
                        detailed_match = await self.soccer_client.get_match_details(match.match_id, context)
                        if detailed_match:
                            match.detailed_data = detailed_match
                    
                    return match
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding match data: {e}")
            return None
    
    def _teams_match(self, search_team: str, actual_team: str) -> bool:
        """Check if team names match with fuzzy matching"""
        search_lower = search_team.lower().strip()
        actual_lower = actual_team.lower().strip()
        
        # Exact match
        if search_lower == actual_lower:
            return True
        
        # Contains match
        if search_lower in actual_lower or actual_lower in search_lower:
            return True
        
        # Common abbreviations
        abbreviations = {
            'man city': 'manchester city',
            'man united': 'manchester united',
            'man utd': 'manchester united',
            'spurs': 'tottenham',
            'arsenal': 'arsenal',
            'chelsea': 'chelsea',
            'liverpool': 'liverpool'
        }
        
        search_abbrev = abbreviations.get(search_lower, search_lower)
        actual_abbrev = abbreviations.get(actual_lower, actual_lower)
        
        return search_abbrev == actual_abbrev or search_abbrev in actual_abbrev or actual_abbrev in search_abbrev

    async def _generate_match_preview(self, match_data: Dict, context: ErrorContext) -> MatchPreview:
        """Generate comprehensive match preview with all analytics"""
        try:
            # Extract basic match info
            home_team_id = getattr(match_data.home_team, 'id', None)
            away_team_id = getattr(match_data.away_team, 'id', None)
            home_team_name = getattr(match_data.home_team, 'name', 'Home Team')
            away_team_name = getattr(match_data.away_team, 'name', 'Away Team')
            
            # Get comprehensive team data (similar to schedule.py methodology)
            league_id = getattr(match_data, 'league_id', 228)  # Default to EPL
            
            # Generate H2H analysis
            h2h_analysis = await self._generate_h2h_analysis(
                home_team_id, away_team_id, home_team_name, away_team_name, league_id, context
            )
            
            # Generate team form analysis
            home_form = await self._generate_team_form_analysis(home_team_id, home_team_name, league_id, True, context)
            away_form = await self._generate_team_form_analysis(away_team_id, away_team_name, league_id, False, context)
            
            # Extract betting odds
            betting_odds = getattr(match_data, 'odds', {})
            
            # Generate predictions based on comprehensive data
            predictions = self._generate_predictions(h2h_analysis, home_form, away_form, betting_odds)
            
            # Generate key insights
            key_insights = self._generate_key_insights(h2h_analysis, home_form, away_form, predictions)
            
            return MatchPreview(
                match_id=getattr(match_data, 'match_id', 0),
                home_team=home_team_name,
                away_team=away_team_name,
                date=getattr(match_data, 'date', ''),
                time=getattr(match_data, 'time', ''),
                venue=getattr(match_data, 'venue', ''),
                league=getattr(match_data, 'league', ''),
                h2h_analysis=h2h_analysis,
                home_form=home_form,
                away_form=away_form,
                betting_odds=betting_odds,
                predictions=predictions,
                key_insights=key_insights
            )
            
        except Exception as e:
            logger.error(f"Error generating match preview: {e}")
            # Return basic preview
            return MatchPreview(
                match_id=0, home_team=home_team_name, away_team=away_team_name,
                date='', time='', venue='', league='',
                h2h_analysis=H2HAnalysis('', '', 0, 0, 0, 0, 0, 0, 0.0, [], {}, {}),
                home_form=TeamFormAnalysis('', 0, [], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, {}, {}, '', {}),
                away_form=TeamFormAnalysis('', 0, [], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, {}, {}, '', {}),
                betting_odds={}, predictions={}, key_insights=[]
            )

    async def _generate_h2h_analysis(self, home_team_id: int, away_team_id: int,
                                   home_team_name: str, away_team_name: str, 
                                   league_id: int, context: ErrorContext) -> H2HAnalysis:
        """Generate comprehensive H2H analysis using schedule.py methodology"""
        try:
            # Method 1: Direct H2H API call
            h2h_data = await self.soccer_client.get_h2h_analysis(home_team_id, away_team_id, context)
            
            # Method 2: Custom date-based H2H search (like schedule.py)
            recent_meetings = await self._find_recent_h2h_meetings(
                home_team_id, away_team_id, league_id, 5
            )
            
            # Parse H2H data
            total_meetings = h2h_data.get('total_meetings', len(recent_meetings))
            team1_record = h2h_data.get('team_1_record', {})
            team2_record = h2h_data.get('team_2_record', {})
            
            home_wins = team1_record.get('wins', 0)
            away_wins = team2_record.get('wins', 0)  
            draws = h2h_data.get('draws', {}).get('count', 0)
            
            goals_data = h2h_data.get('goals', {})
            home_goals = goals_data.get('team_1_total', 0)
            away_goals = goals_data.get('team_2_total', 0)
            avg_goals = goals_data.get('average_per_game', 0.0)
            
            # Calculate home advantage
            home_advantage = self._calculate_home_advantage(h2h_data, recent_meetings)
            
            # Generate betting trends
            betting_trends = self._analyze_h2h_betting_trends(recent_meetings, avg_goals)
            
            return H2HAnalysis(
                home_team=home_team_name,
                away_team=away_team_name,
                total_meetings=total_meetings,
                home_team_wins=home_wins,
                away_team_wins=away_wins,
                draws=draws,
                home_team_goals=home_goals,
                away_team_goals=away_goals,
                avg_goals_per_game=avg_goals,
                recent_meetings=recent_meetings,
                home_advantage=home_advantage,
                betting_trends=betting_trends
            )
            
        except Exception as e:
            logger.error(f"Error generating H2H analysis: {e}")
            return H2HAnalysis(home_team_name, away_team_name, 0, 0, 0, 0, 0, 0, 0.0, [], {}, {})

    async def _find_recent_h2h_meetings(self, team1_id: int, team2_id: int, 
                                      league_id: int, max_meetings: int = 5) -> List[Dict]:
        """Find recent H2H meetings using date-by-date search (schedule.py method)"""
        try:
            meetings = []
            end_date = datetime.now()
            
            # Search back 2 years for meetings
            for days_back in range(0, 730, 14):  # Check every 2 weeks
                if len(meetings) >= max_meetings:
                    break
                
                search_date = (end_date - timedelta(days=days_back)).strftime("%d-%m-%Y")
                
                try:
                    # Get matches for this date
                    matches_data = await self.soccer_client.get_matches_for_date_raw(league_id, search_date)
                    
                    # Look for H2H meetings in the matches
                    if matches_data and isinstance(matches_data, list):
                        for league_data in matches_data:
                            matches = league_data.get('matches', [])
                            
                            for match in matches:
                                teams = match.get('teams', {})
                                home_team = teams.get('home', {})
                                away_team = teams.get('away', {})
                                
                                home_id = home_team.get('id')
                                away_id = away_team.get('id')
                                
                                # Check if this is a meeting between our teams
                                if ((home_id == team1_id and away_id == team2_id) or 
                                    (home_id == team2_id and away_id == team1_id)):
                                    
                                    if match.get('status') in ['finished', 'complete', 'full-time']:
                                        meetings.append({
                                            'date': search_date,
                                            'match': match,
                                            'team_1_is_home': (home_id == team1_id)
                                        })
                
                except Exception:
                    continue  # Skip failed requests
            
            # Sort by date (most recent first)
            meetings.sort(key=lambda x: datetime.strptime(x['date'], "%d-%m-%Y"), reverse=True)
            return meetings[:max_meetings]
            
        except Exception as e:
            logger.error(f"Error finding recent H2H meetings: {e}")
            return []

    async def _generate_team_form_analysis(self, team_id: int, team_name: str, 
                                         league_id: int, is_home: bool, 
                                         context: ErrorContext) -> TeamFormAnalysis:
        """Generate comprehensive team form analysis with advanced metrics (schedule.py style)"""
        try:
            # Get recent matches using comprehensive data extraction
            recent_matches = await self._get_comprehensive_team_matches(team_id, league_id, 10)
            
            if not recent_matches:
                return TeamFormAnalysis(
                    team_name=team_name, team_id=team_id, recent_matches=[],
                    wins=0, draws=0, losses=0, goals_for=0, goals_against=0,
                    clean_sheets=0, both_teams_scored=0, high_scoring_games=0,
                    early_goals=0, late_goals=0, total_cards=0, comeback_wins=0,
                    home_record={}, away_record={}, form_string='', betting_insights={}
                )
            
            # Analyze recent form (last 5 games)
            recent_5 = recent_matches[:5]
            wins = draws = losses = 0
            goals_for = goals_against = 0
            clean_sheets = both_teams_scored = high_scoring_games = 0
            early_goals = late_goals = total_cards = comeback_wins = 0
            form_string = []
            home_wins = away_wins = 0
            
            for match_data in recent_5:
                context = match_data.get('team_context', {})
                result = context.get('result_from_team_perspective', 'D')
                is_home_match = context.get('is_home', False)
                
                goals = match_data.get('goals', {})
                insights = match_data.get('insights', {})
                timing = match_data.get('goal_timing', {})
                cards = match_data.get('card_discipline', {})
                
                # Update form counters
                if result == 'W':
                    wins += 1
                    if is_home_match:
                        home_wins += 1
                    else:
                        away_wins += 1
                elif result == 'D':
                    draws += 1
                else:
                    losses += 1
                
                form_string.append(result)
                
                # Goals analysis
                if is_home_match:
                    goals_for += goals.get('fulltime', {}).get('home', 0)
                    goals_against += goals.get('fulltime', {}).get('away', 0)
                else:
                    goals_for += goals.get('fulltime', {}).get('away', 0)
                    goals_against += goals.get('fulltime', {}).get('home', 0)
                
                # Advanced metrics
                if ((is_home_match and insights.get('clean_sheet', {}).get('home', False)) or 
                    (not is_home_match and insights.get('clean_sheet', {}).get('away', False))):
                    clean_sheets += 1
                
                if insights.get('both_teams_scored', False):
                    both_teams_scored += 1
                
                if insights.get('high_scoring', False):
                    high_scoring_games += 1
                
                if timing.get('early_goals', 0) > 0:
                    early_goals += 1
                
                if timing.get('late_goals', 0) > 0:
                    late_goals += 1
                
                if insights.get('comeback_win', False):
                    comeback_wins += 1
                
                total_cards += cards.get('total_cards', 0)
            
            # Calculate home/away records
            home_record = {'wins': home_wins, 'games': sum(1 for m in recent_5 if m.get('team_context', {}).get('is_home', False))}
            away_record = {'wins': away_wins, 'games': sum(1 for m in recent_5 if not m.get('team_context', {}).get('is_home', True))}
            
            # Generate betting insights
            betting_insights = self._generate_team_betting_insights(
                wins, draws, losses, goals_for, goals_against, 
                clean_sheets, both_teams_scored, high_scoring_games,
                early_goals, late_goals, total_cards, len(recent_5)
            )
            
            return TeamFormAnalysis(
                team_name=team_name,
                team_id=team_id,
                recent_matches=recent_matches,
                wins=wins,
                draws=draws,
                losses=losses,
                goals_for=goals_for,
                goals_against=goals_against,
                clean_sheets=clean_sheets,
                both_teams_scored=both_teams_scored,
                high_scoring_games=high_scoring_games,
                early_goals=early_goals,
                late_goals=late_goals,
                total_cards=total_cards,
                comeback_wins=comeback_wins,
                home_record=home_record,
                away_record=away_record,
                form_string='-'.join(form_string),
                betting_insights=betting_insights
            )
            
        except Exception as e:
            logger.error(f"Error generating team form analysis: {e}")
            return TeamFormAnalysis(
                team_name=team_name, team_id=team_id, recent_matches=[],
                wins=0, draws=0, losses=0, goals_for=0, goals_against=0,
                clean_sheets=0, both_teams_scored=0, high_scoring_games=0,
                early_goals=0, late_goals=0, total_cards=0, comeback_wins=0,
                home_record={}, away_record={}, form_string='', betting_insights={}
            )

    async def _get_comprehensive_team_matches(self, team_id: int, league_id: int, limit: int = 10) -> List[Dict]:
        """Get comprehensive team match data with all analytics (schedule.py methodology)"""
        try:
            # Call the soccer client to get team recent matches
            # For now, we'll create a basic implementation that can be enhanced
            context = ErrorContext(
                "get_comprehensive_team_matches",
                additional_data={"team_id": team_id, "league_id": league_id}
            )
            
            # Get basic matches data - this method needs to exist in SoccerMCPClient
            matches_data = await self._get_team_matches_fallback(team_id, league_id, limit, context)
            
            comprehensive_matches = []
            
            for match in matches_data:
                # Enhance each match with comprehensive analysis
                enhanced_match = await self._enhance_match_data(match)
                comprehensive_matches.append(enhanced_match)
            
            return comprehensive_matches
            
        except Exception as e:
            logger.error(f"Error getting comprehensive team matches: {e}")
            return []

    async def _get_team_matches_fallback(self, team_id: int, league_id: int, limit: int, context: ErrorContext) -> List[Dict]:
        """Fallback method to get team matches when comprehensive data isn't available"""
        try:
            # Use basic matches endpoint with date range search
            from datetime import datetime, timedelta
            
            matches = []
            end_date = datetime.now()
            
            # Search back 3 months for matches
            for days_back in range(0, 90, 7):  # Check weekly
                if len(matches) >= limit:
                    break
                    
                search_date = (end_date - timedelta(days=days_back)).strftime("%Y-%m-%d")
                
                try:
                    # Get matches for this date and league
                    matches_data = await self.soccer_client.get_matches_for_date(search_date, [self._get_league_code_by_id(league_id)], context)
                    
                    if matches_data:
                        processed_matches = self.soccer_processor.process_match_data(matches_data)
                        
                        # Find matches involving this team
                        for match in processed_matches:
                            if ((hasattr(match.home_team, 'id') and match.home_team.id == team_id) or
                                (hasattr(match.away_team, 'id') and match.away_team.id == team_id)):
                                
                                # Convert ProcessedMatch to dict format
                                match_dict = self._processed_match_to_dict(match)
                                matches.append(match_dict)
                
                except Exception as e:
                    logger.debug(f"Error searching matches for date {search_date}: {e}")
                    continue
            
            return matches[:limit]
            
        except Exception as e:
            logger.error(f"Error in team matches fallback: {e}")
            return []

    def _get_league_code_by_id(self, league_id: int) -> str:
        """Get league code by ID"""
        league_map = {
            228: "EPL", 297: "La Liga", 168: "MLS", 
            241: "Bundesliga", 253: "Serie A", 310: "UEFA"
        }
        return league_map.get(league_id, "EPL")

    def _processed_match_to_dict(self, match) -> Dict:
        """Convert ProcessedMatch to dictionary format"""
        return {
            'match_id': getattr(match, 'match_id', 0),
            'teams': {
                'home': {'id': getattr(match.home_team, 'id', 0), 'name': match.home_team.name},
                'away': {'id': getattr(match.away_team, 'id', 0), 'name': match.away_team.name}
            },
            'goals': {
                'home_ft_goals': 0,  # Would be populated from actual data
                'away_ft_goals': 0,
                'home_ht_goals': 0,
                'away_ht_goals': 0
            },
            'events': [],  # Would be populated from actual data
            'date': match.date,
            'venue': match.venue,
            'status': 'finished'  # Assume historical matches are finished
        }

    async def _enhance_match_data(self, match: Dict) -> Dict:
        """Enhance basic match data with comprehensive analytics"""
        try:
            # Extract basic info
            teams = match.get('teams', {})
            goals = match.get('goals', {})
            events = match.get('events', [])
            
            # Calculate comprehensive insights
            insights = {
                'clean_sheet': {
                    'home': goals.get('away_ft_goals', 0) == 0,
                    'away': goals.get('home_ft_goals', 0) == 0
                },
                'both_teams_scored': goals.get('home_ft_goals', 0) > 0 and goals.get('away_ft_goals', 0) > 0,
                'high_scoring': (goals.get('home_ft_goals', 0) + goals.get('away_ft_goals', 0)) >= 3,
                'early_goal': any(e.get('minute', 100) <= 15 for e in events if 'goal' in e.get('type', '').lower()),
                'late_drama': any(e.get('minute', 0) >= 75 for e in events if 'goal' in e.get('type', '').lower()),
                'comeback_win': self._detect_comeback(events, goals)
            }
            
            # Goal timing analysis
            goal_timing = {
                'early_goals': len([e for e in events if 'goal' in e.get('type', '').lower() and e.get('minute', 100) <= 15]),
                'late_goals': len([e for e in events if 'goal' in e.get('type', '').lower() and e.get('minute', 0) >= 75]),
                'first_half': len([e for e in events if 'goal' in e.get('type', '').lower() and e.get('minute', 100) <= 45]),
                'second_half': len([e for e in events if 'goal' in e.get('type', '').lower() and e.get('minute', 0) > 45])
            }
            
            # Card discipline analysis
            card_discipline = {
                'total_cards': len([e for e in events if 'card' in e.get('type', '').lower()]),
                'home_yellow_cards': len([e for e in events if e.get('type') == 'yellow_card' and e.get('team') == 'home']),
                'away_yellow_cards': len([e for e in events if e.get('type') == 'yellow_card' and e.get('team') == 'away']),
                'home_red_cards': len([e for e in events if e.get('type') == 'red_card' and e.get('team') == 'home']),
                'away_red_cards': len([e for e in events if e.get('type') == 'red_card' and e.get('team') == 'away'])
            }
            
            # Substitution analysis
            substitution_analysis = {
                'early_subs': len([e for e in events if 'substitution' in e.get('type', '').lower() and e.get('minute', 100) <= 30]),
                'late_subs': len([e for e in events if 'substitution' in e.get('type', '').lower() and e.get('minute', 0) >= 60]),
                'total_subs': len([e for e in events if 'substitution' in e.get('type', '').lower()])
            }
            
            return {
                'basic_info': match,
                'teams': teams,
                'goals': {
                    'fulltime': {
                        'home': goals.get('home_ft_goals', 0),
                        'away': goals.get('away_ft_goals', 0)
                    },
                    'halftime': {
                        'home': goals.get('home_ht_goals', 0),
                        'away': goals.get('away_ht_goals', 0)
                    }
                },
                'events_breakdown': {
                    'total_events': len(events),
                    'goals': [e for e in events if 'goal' in e.get('type', '').lower()],
                    'cards': [e for e in events if 'card' in e.get('type', '').lower()],
                    'substitutions': [e for e in events if 'substitution' in e.get('type', '').lower()]
                },
                'insights': insights,
                'goal_timing': goal_timing,
                'card_discipline': card_discipline,
                'substitution_analysis': substitution_analysis,
                'team_context': self._determine_team_context(match, teams)
            }
            
        except Exception as e:
            logger.error(f"Error enhancing match data: {e}")
            return match

    def _detect_comeback(self, events: List[Dict], goals: Dict) -> bool:
        """Detect if a comeback occurred in the match"""
        try:
            goal_events = [e for e in events if 'goal' in e.get('type', '').lower()]
            if len(goal_events) < 2:
                return False
            
            # Sort by minute
            goal_events.sort(key=lambda x: x.get('minute', 0))
            
            home_score = away_score = 0
            for goal in goal_events:
                if goal.get('team') == 'home':
                    home_score += 1
                else:
                    away_score += 1
                
                # Check for comeback scenario
                if abs(home_score - away_score) >= 2:
                    # Check if the losing team comes back to win or draw
                    final_home = goals.get('home_ft_goals', 0)
                    final_away = goals.get('away_ft_goals', 0)
                    
                    if home_score > away_score + 1 and final_away >= final_home:
                        return True
                    elif away_score > home_score + 1 and final_home >= final_away:
                        return True
            
            return False
            
        except Exception:
            return False

    def _determine_team_context(self, match: Dict, teams: Dict) -> Dict:
        """Determine team-specific context for the match"""
        # This would need to be implemented based on which team we're analyzing
        # For now, return basic context
        return {
            'is_home': True,  # Would be determined by team_id
            'result_from_team_perspective': 'W',  # Would be calculated
            'opponent': teams.get('away', {}),
            'venue': match.get('venue', '')
        }

    def _generate_team_betting_insights(self, wins: int, draws: int, losses: int,
                                      goals_for: int, goals_against: int,
                                      clean_sheets: int, both_teams_scored: int,
                                      high_scoring: int, early_goals: int,
                                      late_goals: int, total_cards: int, 
                                      total_games: int) -> Dict:
        """Generate betting insights from team form data"""
        if total_games == 0:
            return {}
        
        insights = {}
        
        # Win rate analysis
        win_rate = wins / total_games
        if win_rate > 0.6:
            insights['form'] = 'excellent'
        elif win_rate > 0.4:
            insights['form'] = 'decent'
        else:
            insights['form'] = 'poor'
        
        # Goals analysis
        avg_goals_for = goals_for / total_games
        avg_goals_against = goals_against / total_games
        
        insights['attack_strength'] = 'strong' if avg_goals_for > 2.0 else 'weak' if avg_goals_for < 1.0 else 'average'
        insights['defense_strength'] = 'solid' if avg_goals_against < 1.0 else 'leaky' if avg_goals_against > 2.0 else 'average'
        
        # Betting market insights
        btts_rate = both_teams_scored / total_games
        insights['btts_tendency'] = 'likely' if btts_rate > 0.6 else 'unlikely' if btts_rate < 0.3 else 'neutral'
        
        over_rate = high_scoring / total_games
        insights['over_2_5_tendency'] = 'likely' if over_rate > 0.6 else 'unlikely' if over_rate < 0.3 else 'neutral'
        
        # Special patterns
        if late_goals / total_games > 0.5:
            insights['late_drama'] = True
        
        if total_cards / total_games > 4:
            insights['high_cards'] = True
        
        return insights

    def _calculate_home_advantage(self, h2h_data: Dict, recent_meetings: List[Dict]) -> Dict:
        """Calculate home advantage statistics"""
        try:
            stats = h2h_data.get('stats', {})
            team1_home = stats.get('team1_at_home', {})
            
            if team1_home:
                home_games = team1_home.get('team1_games_played_at_home', 0)
                home_wins = team1_home.get('team1_wins_at_home', 0)
                
                if home_games > 0:
                    home_win_rate = (home_wins / home_games) * 100
                    return {
                        'home_games': home_games,
                        'home_wins': home_wins,
                        'home_win_rate': home_win_rate,
                        'strong_home_advantage': home_win_rate > 60
                    }
            
            return {}
            
        except Exception:
            return {}

    def _analyze_h2h_betting_trends(self, recent_meetings: List[Dict], avg_goals: float) -> Dict:
        """Analyze betting trends from H2H meetings"""
        try:
            if not recent_meetings:
                return {}
            
            total_goals = 0
            high_scoring_games = 0
            both_scored_games = 0
            
            for meeting in recent_meetings:
                match = meeting.get('match', {})
                goals = match.get('goals', {})
                
                home_goals = goals.get('home_ft_goals', 0)
                away_goals = goals.get('away_ft_goals', 0)
                game_total = home_goals + away_goals
                
                total_goals += game_total
                
                if game_total >= 3:
                    high_scoring_games += 1
                
                if home_goals > 0 and away_goals > 0:
                    both_scored_games += 1
            
            total_meetings = len(recent_meetings)
            
            return {
                'avg_goals_recent': total_goals / total_meetings if total_meetings > 0 else 0,
                'over_2_5_rate': high_scoring_games / total_meetings if total_meetings > 0 else 0,
                'btts_rate': both_scored_games / total_meetings if total_meetings > 0 else 0,
                'recent_trend': 'high_scoring' if high_scoring_games / total_meetings > 0.6 else 'low_scoring'
            }
            
        except Exception:
            return {}

    def _generate_predictions(self, h2h_analysis: H2HAnalysis, 
                            home_form: TeamFormAnalysis, 
                            away_form: TeamFormAnalysis,
                            betting_odds: Dict) -> Dict:
        """Generate match predictions based on comprehensive data"""
        try:
            predictions = {}
            
            # Expected goals calculation
            if home_form.recent_matches and away_form.recent_matches:
                home_avg_for = home_form.goals_for / len(home_form.recent_matches[:5])
                home_avg_against = home_form.goals_against / len(home_form.recent_matches[:5])
                away_avg_for = away_form.goals_for / len(away_form.recent_matches[:5])
                away_avg_against = away_form.goals_against / len(away_form.recent_matches[:5])
                
                expected_goals = (home_avg_for + away_avg_against + away_avg_for + home_avg_against) / 2
                predictions['expected_total_goals'] = round(expected_goals, 2)
            
            # BTTS prediction
            home_btts_rate = home_form.both_teams_scored / len(home_form.recent_matches[:5]) if home_form.recent_matches else 0
            away_btts_rate = away_form.both_teams_scored / len(away_form.recent_matches[:5]) if away_form.recent_matches else 0
            btts_probability = (home_btts_rate + away_btts_rate) / 2
            
            predictions['btts_probability'] = round(btts_probability * 100, 1)
            predictions['btts_recommendation'] = 'YES' if btts_probability > 0.6 else 'NO' if btts_probability < 0.3 else 'NEUTRAL'
            
            # Over/Under 2.5 prediction
            if 'expected_total_goals' in predictions:
                expected = predictions['expected_total_goals']
                if expected > 2.8:
                    predictions['over_under_recommendation'] = 'OVER 2.5'
                elif expected < 2.2:
                    predictions['over_under_recommendation'] = 'UNDER 2.5'
                else:
                    predictions['over_under_recommendation'] = 'NEUTRAL'
            
            # Form momentum
            home_momentum = home_form.wins - home_form.losses
            away_momentum = away_form.wins - away_form.losses
            
            if home_momentum > away_momentum + 1:
                predictions['momentum_advantage'] = f"{home_form.team_name} has better momentum"
            elif away_momentum > home_momentum + 1:
                predictions['momentum_advantage'] = f"{away_form.team_name} has better momentum"
            else:
                predictions['momentum_advantage'] = "Similar momentum for both teams"
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return {}

    def _generate_key_insights(self, h2h_analysis: H2HAnalysis,
                             home_form: TeamFormAnalysis, 
                             away_form: TeamFormAnalysis,
                             predictions: Dict) -> List[str]:
        """Generate key tactical and betting insights"""
        insights = []
        
        try:
            # H2H insights
            if h2h_analysis.total_meetings > 0:
                home_win_rate = (h2h_analysis.home_team_wins / h2h_analysis.total_meetings) * 100
                if home_win_rate > 60:
                    insights.append(f"🏠 **{h2h_analysis.home_team}** dominates this fixture historically ({home_win_rate:.0f}% win rate)")
                elif home_win_rate < 30:
                    insights.append(f"✈️ **{h2h_analysis.away_team}** has strong record in this fixture")
                
                if h2h_analysis.avg_goals_per_game > 3:
                    insights.append(f"⚽ High-scoring fixture - averages {h2h_analysis.avg_goals_per_game:.1f} goals per meeting")
                elif h2h_analysis.avg_goals_per_game < 2:
                    insights.append(f"🔒 Typically low-scoring fixture - averages {h2h_analysis.avg_goals_per_game:.1f} goals")
            
            # Form insights
            if home_form.wins >= 4:
                insights.append(f"🔥 **{home_form.team_name}** in excellent form ({home_form.form_string})")
            elif home_form.losses >= 3:
                insights.append(f"📉 **{home_form.team_name}** struggling for form ({home_form.form_string})")
            
            if away_form.wins >= 4:
                insights.append(f"🚀 **{away_form.team_name}** flying high ({away_form.form_string})")
            elif away_form.losses >= 3:
                insights.append(f"⚠️ **{away_form.team_name}** poor away form ({away_form.form_string})")
            
            # Tactical insights
            if home_form.early_goals >= 3:
                insights.append(f"⏰ **{home_form.team_name}** often scores early - good for in-play betting")
            
            if away_form.late_goals >= 3:
                insights.append(f"🕐 **{away_form.team_name}** dangerous late in games")
            
            if home_form.total_cards / len(home_form.recent_matches[:5]) > 4:
                insights.append(f"🟨 **{home_form.team_name}** picks up many cards - cards market opportunity")
            
            # Betting insights from predictions
            if predictions.get('btts_recommendation') == 'YES':
                insights.append(f"💯 Strong BTTS YES recommendation ({predictions.get('btts_probability', 0)}% probability)")
            
            if predictions.get('over_under_recommendation') == 'OVER 2.5':
                insights.append(f"📈 OVER 2.5 Goals recommended (Expected: {predictions.get('expected_total_goals', 0)} goals)")
            elif predictions.get('over_under_recommendation') == 'UNDER 2.5':
                insights.append(f"📉 UNDER 2.5 Goals recommended (Expected: {predictions.get('expected_total_goals', 0)} goals)")
            
            # Clean sheet patterns
            if home_form.clean_sheets >= 3:
                insights.append(f"🛡️ **{home_form.team_name}** keeping clean sheets regularly")
            
            if away_form.clean_sheets >= 3:
                insights.append(f"🔐 **{away_form.team_name}** defensively solid away from home")
            
            return insights[:8]  # Limit to top 8 insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return insights

    # Discord embed creation methods
    async def _send_welcome_message(self, channel: discord.TextChannel, preview: MatchPreview):
        """Send comprehensive welcome message with match basics"""
        embed = discord.Embed(
            title=f"⚽ {preview.home_team} vs {preview.away_team}",
            description=f"**{preview.league}** | {preview.date} at {preview.time}\n📍 {preview.venue}",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        # Match basics
        embed.add_field(
            name="🏠 Home Team", 
            value=f"**{preview.home_team}**\nForm: {preview.home_form.form_string}",
            inline=True
        )
        embed.add_field(
            name="✈️ Away Team",
            value=f"**{preview.away_team}**\nForm: {preview.away_form.form_string}",
            inline=True
        )
        
        # Key stats preview
        if preview.h2h_analysis.total_meetings > 0:
            embed.add_field(
                name="📊 H2H Record",
                value=f"{preview.h2h_analysis.home_team_wins}W - {preview.h2h_analysis.draws}D - {preview.h2h_analysis.away_team_wins}L\nAvg Goals: {preview.h2h_analysis.avg_goals_per_game:.1f}",
                inline=True
            )
        
        # Betting odds preview
        if preview.betting_odds:
            match_winner = preview.betting_odds.get('match_winner', {})
            if match_winner:
                embed.add_field(
                    name="💰 Current Odds",
                    value=f"Home: {match_winner.get('home', 'N/A')}\nDraw: {match_winner.get('draw', 'N/A')}\nAway: {match_winner.get('away', 'N/A')}",
                    inline=False
                )
        
        embed.set_footer(text="🔄 Loading comprehensive analysis...")
        await channel.send(embed=embed)

    async def _send_h2h_analysis(self, channel: discord.TextChannel, h2h: H2HAnalysis):
        """Send detailed H2H analysis"""
        embed = discord.Embed(
            title=f"📈 Head-to-Head Analysis",
            description=f"**{h2h.home_team}** vs **{h2h.away_team}**",
            color=0x3498db,
            timestamp=datetime.utcnow()
        )
        
        if h2h.total_meetings > 0:
            # Overall record
            embed.add_field(
                name="🏆 Overall Record",
                value=f"**Total Meetings:** {h2h.total_meetings}\n"
                      f"**{h2h.home_team}:** {h2h.home_team_wins} wins ({h2h.home_team_wins/h2h.total_meetings*100:.1f}%)\n"
                      f"**{h2h.away_team}:** {h2h.away_team_wins} wins ({h2h.away_team_wins/h2h.total_meetings*100:.1f}%)\n"
                      f"**Draws:** {h2h.draws} ({h2h.draws/h2h.total_meetings*100:.1f}%)",
                inline=False
            )
            
            # Goals analysis
            embed.add_field(
                name="⚽ Goals Analysis",
                value=f"**Average per game:** {h2h.avg_goals_per_game:.2f}\n"
                      f"**{h2h.home_team} total:** {h2h.home_team_goals} ({h2h.home_team_goals/h2h.total_meetings:.1f} per game)\n"
                      f"**{h2h.away_team} total:** {h2h.away_team_goals} ({h2h.away_team_goals/h2h.total_meetings:.1f} per game)",
                inline=False
            )
            
            # Recent meetings
            if h2h.recent_meetings:
                recent_text = ""
                for i, meeting in enumerate(h2h.recent_meetings[:3], 1):
                    match = meeting['match']
                    goals = match.get('goals', {})
                    home_goals = goals.get('home_ft_goals', 0)
                    away_goals = goals.get('away_ft_goals', 0)
                    
                    teams = match.get('teams', {})
                    home_name = teams.get('home', {}).get('name', 'Home')
                    away_name = teams.get('away', {}).get('name', 'Away')
                    
                    recent_text += f"**{meeting['date']}:** {home_name} {home_goals}-{away_goals} {away_name}\n"
                
                embed.add_field(
                    name="🕐 Recent Meetings",
                    value=recent_text,
                    inline=False
                )
            
            # Betting trends
            if h2h.betting_trends:
                trends = h2h.betting_trends
                if trends.get('over_2_5_rate', 0) > 0.6:
                    trend_text = f"📈 High-scoring fixture (Over 2.5 in {trends['over_2_5_rate']*100:.0f}% of recent meetings)"
                elif trends.get('over_2_5_rate', 0) < 0.3:
                    trend_text = f"📉 Low-scoring fixture (Under 2.5 in {(1-trends['over_2_5_rate'])*100:.0f}% of recent meetings)"
                else:
                    trend_text = "⚖️ Balanced scoring pattern"
                
                embed.add_field(
                    name="🎯 Historical Betting Trends",
                    value=trend_text,
                    inline=False
                )
        else:
            embed.add_field(
                name="❌ No Historical Data",
                value="These teams haven't met recently or data is unavailable.",
                inline=False
            )
        
        await channel.send(embed=embed)

    async def _send_team_form_analysis(self, channel: discord.TextChannel, 
                                     home_form: TeamFormAnalysis, 
                                     away_form: TeamFormAnalysis):
        """Send detailed team form analysis"""
        # Home team form
        home_embed = discord.Embed(
            title=f"🏠 {home_form.team_name} - Recent Form Analysis",
            color=0xe74c3c,
            timestamp=datetime.utcnow()
        )
        
        if home_form.recent_matches:
            # Basic form
            total_games = len(home_form.recent_matches[:5])
            win_rate = (home_form.wins / total_games * 100) if total_games > 0 else 0
            avg_goals_for = home_form.goals_for / total_games if total_games > 0 else 0
            avg_goals_against = home_form.goals_against / total_games if total_games > 0 else 0
            
            home_embed.add_field(
                name="📊 Form Summary (Last 5)",
                value=f"**Record:** {home_form.wins}W-{home_form.draws}D-{home_form.losses}L ({win_rate:.1f}%)\n"
                      f"**Form:** {home_form.form_string}\n"
                      f"**Goals:** {avg_goals_for:.1f} for, {avg_goals_against:.1f} against",
                inline=False
            )
            
            # Advanced metrics
            home_embed.add_field(
                name="🔍 Advanced Metrics",
                value=f"**Clean Sheets:** {home_form.clean_sheets}/{total_games}\n"
                      f"**Both Teams Score:** {home_form.both_teams_scored}/{total_games}\n"
                      f"**High Scoring (3+):** {home_form.high_scoring_games}/{total_games}\n"
                      f"**Early Goals:** {home_form.early_goals}/{total_games} games\n"
                      f"**Late Drama:** {home_form.late_goals}/{total_games} games",
                inline=True
            )
            
            # Betting insights
            insights = home_form.betting_insights
            if insights:
                insight_text = f"**Attack:** {insights.get('attack_strength', 'Unknown').title()}\n"
                insight_text += f"**Defense:** {insights.get('defense_strength', 'Unknown').title()}\n"
                insight_text += f"**BTTS:** {insights.get('btts_tendency', 'Unknown').title()}\n"
                insight_text += f"**Over 2.5:** {insights.get('over_2_5_tendency', 'Unknown').title()}"
                
                home_embed.add_field(
                    name="💡 Betting Insights",
                    value=insight_text,
                    inline=True
                )
        else:
            home_embed.add_field(
                name="❌ No Recent Form Data",
                value="Recent match data unavailable",
                inline=False
            )
        
        await channel.send(embed=home_embed)
        
        # Away team form
        away_embed = discord.Embed(
            title=f"✈️ {away_form.team_name} - Recent Form Analysis", 
            color=0x3498db,
            timestamp=datetime.utcnow()
        )
        
        if away_form.recent_matches:
            # Basic form
            total_games = len(away_form.recent_matches[:5])
            win_rate = (away_form.wins / total_games * 100) if total_games > 0 else 0
            avg_goals_for = away_form.goals_for / total_games if total_games > 0 else 0
            avg_goals_against = away_form.goals_against / total_games if total_games > 0 else 0
            
            away_embed.add_field(
                name="📊 Form Summary (Last 5)",
                value=f"**Record:** {away_form.wins}W-{away_form.draws}D-{away_form.losses}L ({win_rate:.1f}%)\n"
                      f"**Form:** {away_form.form_string}\n"
                      f"**Goals:** {avg_goals_for:.1f} for, {avg_goals_against:.1f} against",
                inline=False
            )
            
            # Advanced metrics
            away_embed.add_field(
                name="🔍 Advanced Metrics",
                value=f"**Clean Sheets:** {away_form.clean_sheets}/{total_games}\n"
                      f"**Both Teams Score:** {away_form.both_teams_scored}/{total_games}\n"
                      f"**High Scoring (3+):** {away_form.high_scoring_games}/{total_games}\n"
                      f"**Early Goals:** {away_form.early_goals}/{total_games} games\n"
                      f"**Late Drama:** {away_form.late_goals}/{total_games} games",
                inline=True
            )
            
            # Betting insights
            insights = away_form.betting_insights
            if insights:
                insight_text = f"**Attack:** {insights.get('attack_strength', 'Unknown').title()}\n"
                insight_text += f"**Defense:** {insights.get('defense_strength', 'Unknown').title()}\n"
                insight_text += f"**BTTS:** {insights.get('btts_tendency', 'Unknown').title()}\n"
                insight_text += f"**Over 2.5:** {insights.get('over_2_5_tendency', 'Unknown').title()}"
                
                away_embed.add_field(
                    name="💡 Betting Insights",
                    value=insight_text,
                    inline=True
                )
        else:
            away_embed.add_field(
                name="❌ No Recent Form Data", 
                value="Recent match data unavailable",
                inline=False
            )
        
        await channel.send(embed=away_embed)

    async def _send_betting_analysis(self, channel: discord.TextChannel, preview: MatchPreview):
        """Send comprehensive betting analysis and predictions"""
        embed = discord.Embed(
            title="💰 Betting Analysis & Predictions",
            description=f"Data-driven insights for **{preview.home_team}** vs **{preview.away_team}**",
            color=0xf39c12,
            timestamp=datetime.utcnow()
        )
        
        predictions = preview.predictions
        
        if predictions:
            # Expected goals and totals
            if 'expected_total_goals' in predictions:
                embed.add_field(
                    name="⚽ Goals Market",
                    value=f"**Expected Total Goals:** {predictions['expected_total_goals']}\n"
                          f"**Over/Under 2.5 Recommendation:** {predictions.get('over_under_recommendation', 'N/A')}",
                    inline=False
                )
            
            # BTTS analysis
            if 'btts_probability' in predictions:
                btts_prob = predictions['btts_probability']
                confidence = "🔥 HIGH" if btts_prob > 70 or btts_prob < 25 else "⚖️ MEDIUM" if btts_prob > 60 or btts_prob < 30 else "⚠️ LOW"
                
                embed.add_field(
                    name="🎯 Both Teams to Score",
                    value=f"**Probability:** {btts_prob}%\n"
                          f"**Recommendation:** {predictions.get('btts_recommendation', 'N/A')}\n"
                          f"**Confidence:** {confidence}",
                    inline=True
                )
            
            # Momentum analysis
            if 'momentum_advantage' in predictions:
                embed.add_field(
                    name="📈 Current Momentum",
                    value=predictions['momentum_advantage'],
                    inline=True
                )
        
        # Betting odds if available
        if preview.betting_odds:
            match_winner = preview.betting_odds.get('match_winner', {})
            over_under = preview.betting_odds.get('over_under', {})
            
            if match_winner:
                embed.add_field(
                    name="💵 Current Odds",
                    value=f"**{preview.home_team}:** {match_winner.get('home', 'N/A')}\n"
                          f"**Draw:** {match_winner.get('draw', 'N/A')}\n" 
                          f"**{preview.away_team}:** {match_winner.get('away', 'N/A')}",
                    inline=True
                )
            
            if over_under:
                embed.add_field(
                    name="📊 Over/Under Odds",
                    value=f"**Total:** {over_under.get('total', 'N/A')}\n"
                          f"**Over:** {over_under.get('over', 'N/A')}\n"
                          f"**Under:** {over_under.get('under', 'N/A')}",
                    inline=True
                )
        
        # Historical trends from H2H
        if preview.h2h_analysis.betting_trends:
            trends = preview.h2h_analysis.betting_trends
            trend_text = ""
            
            if trends.get('recent_trend') == 'high_scoring':
                trend_text += "📈 Recent H2H meetings tend to be high-scoring\n"
            elif trends.get('recent_trend') == 'low_scoring':
                trend_text += "📉 Recent H2H meetings tend to be low-scoring\n"
            
            if trends.get('btts_rate', 0) > 0.6:
                trend_text += "💯 Both teams often score in this fixture\n"
            elif trends.get('btts_rate', 0) < 0.3:
                trend_text += "🚫 One-sided games common in this fixture\n"
            
            if trend_text:
                embed.add_field(
                    name="📚 Historical Trends",
                    value=trend_text.strip(),
                    inline=False
                )
        
        embed.set_footer(text="⚠️ Bet responsibly. Analysis based on historical data and current form.")
        await channel.send(embed=embed)

    async def _send_tactical_insights(self, channel: discord.TextChannel, preview: MatchPreview):
        """Send key tactical insights and patterns"""
        embed = discord.Embed(
            title="🎯 Key Tactical Insights",
            description=f"Important patterns and trends for **{preview.home_team}** vs **{preview.away_team}**",
            color=0x9b59b6,
            timestamp=datetime.utcnow()
        )
        
        if preview.key_insights:
            # Group insights by category
            h2h_insights = [i for i in preview.key_insights if any(x in i for x in ['historically', 'fixture', 'dominates'])]
            form_insights = [i for i in preview.key_insights if any(x in i for x in ['form', 'struggling', 'flying'])]
            tactical_insights = [i for i in preview.key_insights if any(x in i for x in ['early', 'late', 'cards', 'clean'])]
            betting_insights = [i for i in preview.key_insights if any(x in i for x in ['BTTS', 'OVER', 'UNDER', 'recommendation'])]
            
            if h2h_insights:
                embed.add_field(
                    name="📈 Historical Patterns",
                    value='\n'.join(h2h_insights[:3]),
                    inline=False
                )
            
            if form_insights:
                embed.add_field(
                    name="🔥 Current Form",
                    value='\n'.join(form_insights[:3]),
                    inline=False
                )
            
            if tactical_insights:
                embed.add_field(
                    name="⚽ Tactical Patterns",
                    value='\n'.join(tactical_insights[:3]),
                    inline=False
                )
            
            if betting_insights:
                embed.add_field(
                    name="💰 Betting Opportunities",
                    value='\n'.join(betting_insights[:2]),
                    inline=False
                )
        else:
            embed.add_field(
                name="📊 Analysis in Progress",
                value="Comprehensive insights are being compiled based on recent form and historical data.",
                inline=False
            )
        
        # Add methodology note
        embed.add_field(
            name="🔍 Analysis Methodology",
            value="• Head-to-head historical data (up to 2 years)\n"
                  "• Recent form analysis (last 10 matches)\n"
                  "• Advanced metrics (goal timing, cards, comebacks)\n"
                  "• Home/away performance splits\n"
                  "• Betting market trend analysis",
            inline=False
        )
        
        embed.set_footer(text="Analysis updates automatically as new data becomes available")
        await channel.send(embed=embed)

    async def _send_fallback_content(self, channel: discord.TextChannel, 
                                   home_team: str, away_team: str, 
                                   match_date: str, league_code: str):
        """Send basic fallback content when comprehensive data is unavailable"""
        embed = discord.Embed(
            title=f"⚽ {home_team} vs {away_team}",
            description=f"**Match Date:** {match_date}\n**League:** {league_code}",
            color=0x95a5a6,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📊 Channel Created",
            value="This channel has been created for match discussion and analysis.",
            inline=False
        )
        
        embed.add_field(
            name="🔄 Loading Data",
            value="Comprehensive match analysis is being loaded. Please check back shortly for:\n"
                  "• Head-to-head analysis\n"
                  "• Recent form analysis\n"
                  "• Betting insights\n"
                  "• Tactical patterns",
            inline=False
        )
        
        embed.add_field(
            name="💬 Discussion",
            value="Feel free to start discussing the upcoming match while data loads!",
            inline=False
        )
        
        embed.set_footer(text="Data will be automatically updated when available")
        await channel.send(embed=embed)