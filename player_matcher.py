#!/usr/bin/env python3
"""
Player Matching System for Value Betting Analysis

This module provides file-based player matching between betting odds APIs
and ESPN roster data to enable value betting analysis.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
from datetime import datetime, timezone


class PlayerMatcher:
    """File-based player matching system for odds-to-ESPN correlation."""
    
    def __init__(self, base_dir: str = None):
        """Initialize the PlayerMatcher with file paths."""
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        
        # JSON file paths
        self.confirmed_matches_file = self.base_dir / "confirmed_matches.json"
        self.pending_review_file = self.base_dir / "pending_review.json" 
        self.espn_rosters_dir = self.base_dir / "espn ids" / "players"
        
        # Load existing data
        self.confirmed_matches = self._load_json(self.confirmed_matches_file, {})
        self.pending_review = self._load_json(self.pending_review_file, {})
        
        # Cache for ESPN rosters (loaded on demand)
        self._espn_rosters_cache = {}
        
        # Sport key mappings
        self.ODDS_TO_ESPN_SPORT = {
            "basketball_nba": ("basketball", "nba"),
            "basketball_wnba": ("basketball", "wnba"),
            "americanfootball_nfl": ("football", "nfl"),
            "baseball_mlb": ("baseball", "mlb"),
            "icehockey_nhl": ("hockey", "nhl")
        }
    
    def match_player(self, odds_player_name: str, sport_key: str) -> Optional[Dict]:
        """
        Match a player name from odds API to ESPN ID.
        
        Args:
            odds_player_name: Player name as it appears in betting odds
            sport_key: Sport key from odds API (e.g. 'basketball_nba')
            
        Returns:
            Dict with match info or None if no match found
            {
                "espn_id": "1966",
                "espn_name": "LeBron James", 
                "confidence": 1.0,
                "source": "confirmed",  # or "fuzzy", "pending"
                "team": "Los Angeles Lakers"
            }
        """
        # 1. Check confirmed matches first (instant lookup)
        confirmed_match = self._check_confirmed_match(odds_player_name, sport_key)
        if confirmed_match:
            return confirmed_match
            
        # 2. Check pending review (might be already processed)  
        pending_match = self._check_pending_match(odds_player_name, sport_key)
        if pending_match:
            return pending_match
            
        # 3. Try fuzzy matching against ESPN rosters
        fuzzy_match = self._fuzzy_match(odds_player_name, sport_key)
        if fuzzy_match:
            # Add to pending review for confirmation
            self._add_to_pending(odds_player_name, sport_key, fuzzy_match)
            return fuzzy_match
            
        # 4. No match found
        return None
    
    def confirm_match(self, odds_player_name: str, sport_key: str, 
                     espn_id: str, verified_by: str = "manual") -> bool:
        """
        Confirm a pending match and move it to confirmed matches.
        
        Args:
            odds_player_name: Player name from odds
            sport_key: Sport key 
            espn_id: ESPN player ID to confirm
            verified_by: Who verified this match
            
        Returns:
            True if successfully confirmed
        """
        # Get ESPN player details
        espn_player = self._get_espn_player_by_id(espn_id, sport_key)
        if not espn_player:
            return False
            
        # Initialize sport key in confirmed matches if needed
        if sport_key not in self.confirmed_matches:
            self.confirmed_matches[sport_key] = {}
            
        # Add confirmed match
        self.confirmed_matches[sport_key][odds_player_name] = {
            "espn_id": espn_id,
            "espn_name": espn_player["name"],
            "team": espn_player.get("team", "Unknown"),
            "position": espn_player.get("position", ""),
            "confidence": 1.0,
            "verified_by": verified_by,
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "last_seen": datetime.now(timezone.utc).isoformat()
        }
        
        # Remove from pending review if it exists
        if sport_key in self.pending_review and odds_player_name in self.pending_review[sport_key]:
            del self.pending_review[sport_key][odds_player_name]
            
        # Save files
        self._save_json(self.confirmed_matches_file, self.confirmed_matches)
        self._save_json(self.pending_review_file, self.pending_review)
        
        return True
    
    def reject_match(self, odds_player_name: str, sport_key: str) -> bool:
        """Mark a pending match as rejected (no ESPN equivalent)."""
        if sport_key in self.pending_review and odds_player_name in self.pending_review[sport_key]:
            self.pending_review[sport_key][odds_player_name]["status"] = "rejected"
            self.pending_review[sport_key][odds_player_name]["rejected_at"] = datetime.now(timezone.utc).isoformat()
            self._save_json(self.pending_review_file, self.pending_review)
            return True
        return False
    
    def get_pending_matches(self, sport_key: str = None) -> Dict:
        """Get all pending matches for manual review."""
        if sport_key:
            return self.pending_review.get(sport_key, {})
        return self.pending_review
    
    def get_match_stats(self) -> Dict:
        """Get statistics about the matching system."""
        confirmed_count = sum(len(sport_matches) for sport_matches in self.confirmed_matches.values())
        pending_count = sum(len(sport_matches) for sport_matches in self.pending_review.values())
        
        return {
            "confirmed_matches": confirmed_count,
            "pending_matches": pending_count,
            "sports_covered": list(self.confirmed_matches.keys()),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    
    # Private methods
    
    def _check_confirmed_match(self, odds_player_name: str, sport_key: str) -> Optional[Dict]:
        """Check if player already has confirmed match."""
        if sport_key in self.confirmed_matches and odds_player_name in self.confirmed_matches[sport_key]:
            match = self.confirmed_matches[sport_key][odds_player_name].copy()
            match["source"] = "confirmed"
            # Update last seen
            self.confirmed_matches[sport_key][odds_player_name]["last_seen"] = datetime.now(timezone.utc).isoformat()
            self._save_json(self.confirmed_matches_file, self.confirmed_matches)
            return match
        return None
    
    def _check_pending_match(self, odds_player_name: str, sport_key: str) -> Optional[Dict]:
        """Check if player is in pending review."""
        if (sport_key in self.pending_review and 
            odds_player_name in self.pending_review[sport_key] and
            self.pending_review[sport_key][odds_player_name].get("status") != "rejected"):
            
            match = self.pending_review[sport_key][odds_player_name].copy()
            match["source"] = "pending"
            return match
        return None
    
    def _fuzzy_match(self, odds_player_name: str, sport_key: str) -> Optional[Dict]:
        """Attempt fuzzy matching against ESPN rosters."""
        if sport_key not in self.ODDS_TO_ESPN_SPORT:
            return None
            
        sport, league = self.ODDS_TO_ESPN_SPORT[sport_key]
        espn_roster = self._load_espn_roster(sport, league)
        
        if not espn_roster:
            return None
            
        best_match = None
        best_score = 0.0
        
        # Clean the odds player name for better matching
        cleaned_odds_name = self._clean_name(odds_player_name)
        
        for player in espn_roster:
            cleaned_espn_name = self._clean_name(player["name"])
            
            # Try exact match first
            if cleaned_odds_name == cleaned_espn_name:
                return {
                    "espn_id": player["id"],
                    "espn_name": player["name"],
                    "team": player.get("team", "Unknown"),
                    "position": player.get("position", ""),
                    "confidence": 1.0,
                    "source": "fuzzy"
                }
            
            # Try fuzzy matching
            similarity = SequenceMatcher(None, cleaned_odds_name, cleaned_espn_name).ratio()
            
            # Also try matching parts (first name, last name)
            odds_parts = cleaned_odds_name.split()
            espn_parts = cleaned_espn_name.split()
            
            if len(odds_parts) >= 2 and len(espn_parts) >= 2:
                # Check if first and last names match
                first_match = SequenceMatcher(None, odds_parts[0], espn_parts[0]).ratio()
                last_match = SequenceMatcher(None, odds_parts[-1], espn_parts[-1]).ratio()
                part_similarity = (first_match + last_match) / 2
                similarity = max(similarity, part_similarity)
            
            if similarity > best_score and similarity > 0.8:  # 80% threshold
                best_score = similarity
                best_match = {
                    "espn_id": player["id"],
                    "espn_name": player["name"],
                    "team": player.get("team", "Unknown"),
                    "position": player.get("position", ""),
                    "confidence": similarity,
                    "source": "fuzzy"
                }
        
        return best_match if best_score > 0.8 else None
    
    def _clean_name(self, name: str) -> str:
        """Clean player name for better matching."""
        # Remove common prefixes/suffixes, normalize case
        cleaned = name.lower().strip()
        cleaned = re.sub(r'\s+', ' ', cleaned)  # Normalize whitespace
        cleaned = re.sub(r'[.,\'"]', '', cleaned)  # Remove punctuation
        return cleaned
    
    def _add_to_pending(self, odds_player_name: str, sport_key: str, match: Dict):
        """Add a fuzzy match to pending review."""
        if sport_key not in self.pending_review:
            self.pending_review[sport_key] = {}
            
        self.pending_review[sport_key][odds_player_name] = {
            "espn_id": match["espn_id"],
            "espn_name": match["espn_name"],
            "team": match.get("team", "Unknown"),
            "position": match.get("position", ""),
            "confidence": match["confidence"],
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_seen": datetime.now(timezone.utc).isoformat()
        }
        
        self._save_json(self.pending_review_file, self.pending_review)
    
    def _load_espn_roster(self, sport: str, league: str) -> List[Dict]:
        """Load ESPN roster data for a sport/league."""
        cache_key = f"{sport}_{league}"
        
        if cache_key in self._espn_rosters_cache:
            return self._espn_rosters_cache[cache_key]
            
        roster = []
        sport_dir = self.espn_rosters_dir / sport
        
        if not sport_dir.exists():
            return roster
            
        # Load all team rosters for this sport
        for team_file in sport_dir.glob("**/*.json"):
            try:
                with open(team_file, 'r', encoding='utf-8') as f:
                    team_roster = json.load(f)
                    
                # Add team name to each player if available
                team_name = team_file.stem.replace('_', ' ')
                if isinstance(team_roster, list):
                    for player in team_roster:
                        if isinstance(player, dict):
                            player["team"] = team_name
                            roster.append(player)
                            
            except Exception as e:
                print(f"[WARNING] Could not load roster {team_file}: {e}")
                continue
        
        self._espn_rosters_cache[cache_key] = roster
        return roster
    
    def _get_espn_player_by_id(self, espn_id: str, sport_key: str) -> Optional[Dict]:
        """Get ESPN player details by ID."""
        if sport_key not in self.ODDS_TO_ESPN_SPORT:
            return None
            
        sport, league = self.ODDS_TO_ESPN_SPORT[sport_key]
        roster = self._load_espn_roster(sport, league)
        
        for player in roster:
            if player.get("id") == espn_id:
                return player
        return None
    
    def _load_json(self, filepath: Path, default=None):
        """Load JSON file with error handling."""
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load {filepath}: {e}")
        return default or {}
    
    def _save_json(self, filepath: Path, data):
        """Save JSON file with error handling."""
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Could not save {filepath}: {e}")


# Example usage and testing
if __name__ == "__main__":
    matcher = PlayerMatcher()
    
    # Test matching
    test_cases = [
        ("LeBron James", "basketball_nba"),
        ("Patrick Mahomes", "americanfootball_nfl"),
        ("L. James", "basketball_nba"),  # Should fuzzy match to LeBron
    ]
    
    print("=== Player Matching Test ===")
    for player_name, sport_key in test_cases:
        result = matcher.match_player(player_name, sport_key)
        if result:
            print(f"✅ {player_name} -> {result['espn_name']} (ID: {result['espn_id']}, Confidence: {result['confidence']:.2f})")
        else:
            print(f"❌ {player_name} -> No match found")
    
    print(f"\nMatch Stats: {matcher.get_match_stats()}")