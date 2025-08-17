#!/usr/bin/env python3
"""
Hourly Cycle API Tester

Based on discovery that SoccerDataAPI has:
- ~10-12 calls per hour allowed
- 1-hour cooldown when limit hit
- "Retry-After: 3600" header

This test specifically validates the hourly cycle theory.
"""

import asyncio
import aiohttp
import time
import json
import random
from datetime import datetime, timedelta

# API Configuration
API_BASE_URL = "https://api.soccerdataapi.com/"
AUTH_KEY = "a9f37754a540df435e8c40ed89c08565166524ed"

# Test endpoints
TEST_ENDPOINTS = [
    ("livescores/", {}),
    ("league/", {}),
    ("standing/", {"league_id": 228}),
    ("team/", {"team_id": 4145}),
    ("matches/", {"league_id": 228}),
]

class HourlyCycleTester:
    def __init__(self):
        self.results = []
        self.hourly_stats = {}
        self.current_hour_calls = 0
        self.current_hour_start = None
        self.session = None
        
    def get_current_hour_key(self):
        """Get hour key for tracking (YYYY-MM-DD-HH format)"""
        now = datetime.now()
        return now.strftime("%Y-%m-%d-%H")
    
    def reset_hour_tracking(self):
        """Reset tracking for new hour"""
        hour_key = self.get_current_hour_key()
        if hour_key not in self.hourly_stats:
            self.hourly_stats[hour_key] = {
                "success_count": 0,
                "rate_limited_count": 0,
                "total_calls": 0,
                "first_rate_limit_call": None,
                "started_at": datetime.now().isoformat()
            }
        self.current_hour_calls = self.hourly_stats[hour_key]["total_calls"]
        self.current_hour_start = datetime.now().replace(minute=0, second=0, microsecond=0)

    async def make_api_call(self, endpoint_data, call_number):
        """Make API call and track hourly stats"""
        
        endpoint, endpoint_params = endpoint_data
        
        headers = {
            'Content-Type': 'application/json',
            'Accept-Encoding': 'gzip'
        }
        
        params = {"auth_token": AUTH_KEY}
        params.update(endpoint_params)
        
        url = API_BASE_URL + endpoint
        hour_key = self.get_current_hour_key()
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                
                # Track hourly stats
                self.hourly_stats[hour_key]["total_calls"] += 1
                self.current_hour_calls += 1
                
                result = {
                    "call_number": call_number,
                    "timestamp": datetime.now().isoformat(),
                    "endpoint": endpoint,
                    "hour_key": hour_key,
                    "call_in_hour": self.current_hour_calls,
                    "status_code": response.status,
                    "response_time": time.time(),
                }
                
                if response.status == 429:
                    # Rate limited
                    self.hourly_stats[hour_key]["rate_limited_count"] += 1
                    if not self.hourly_stats[hour_key]["first_rate_limit_call"]:
                        self.hourly_stats[hour_key]["first_rate_limit_call"] = self.current_hour_calls
                    
                    retry_after = response.headers.get('Retry-After', 'unknown')
                    result.update({
                        "rate_limited": True,
                        "retry_after": retry_after
                    })
                    
                    print(f"⚠️  Call #{call_number} (Hour {self.current_hour_calls}): RATE LIMITED - Retry after {retry_after}s")
                    
                elif response.status == 200:
                    # Success
                    self.hourly_stats[hour_key]["success_count"] += 1
                    result["success"] = True
                    
                    response_size = len(await response.text())
                    result["response_size"] = response_size
                    
                    print(f"✅ Call #{call_number} (Hour {self.current_hour_calls}): SUCCESS ({response_size} bytes)")
                
                else:
                    # Other error
                    result["error"] = True
                    result["error_code"] = response.status
                    print(f"❌ Call #{call_number} (Hour {self.current_hour_calls}): ERROR {response.status}")
                
                self.results.append(result)
                return result
                
        except Exception as e:
            print(f"💥 Call #{call_number}: EXCEPTION - {e}")
            result = {
                "call_number": call_number,
                "timestamp": datetime.now().isoformat(),
                "endpoint": endpoint,
                "hour_key": hour_key,
                "call_in_hour": self.current_hour_calls,
                "exception": str(e)
            }
            self.results.append(result)
            return result

    async def run_hourly_cycle_test(self, total_hours=24, calls_per_hour_target=15):
        """
        Test the hourly cycle theory over multiple hours
        
        Args:
            total_hours: How many hours to test
            calls_per_hour_target: Try this many calls per hour to test limits
        """
        
        print("🔬 HOURLY CYCLE API TESTER")
        print("=" * 60)
        print(f"📊 Test Plan:")
        print(f"   • Duration: {total_hours} hours")
        print(f"   • Target: {calls_per_hour_target} calls per hour")
        print(f"   • Total calls: ~{total_hours * calls_per_hour_target}")
        print(f"   • Theory: ~10-12 calls/hour limit with 1-hour reset")
        print("=" * 60)
        
        self.reset_hour_tracking()
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            self.session = session
            
            start_time = datetime.now()
            end_time = start_time + timedelta(hours=total_hours)
            call_number = 1
            
            while datetime.now() < end_time:
                current_hour_key = self.get_current_hour_key()
                
                # Check if we entered a new hour
                if current_hour_key not in self.hourly_stats:
                    self.reset_hour_tracking()
                    print(f"\n🕐 NEW HOUR STARTED: {current_hour_key}")
                    print(f"📊 Previous hour summary: {self.get_previous_hour_summary()}")
                
                # Check if we've hit our target for this hour
                if self.current_hour_calls >= calls_per_hour_target:
                    # Wait until next hour
                    next_hour = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
                    wait_seconds = (next_hour - datetime.now()).total_seconds()
                    print(f"⏳ Hit {calls_per_hour_target} calls this hour. Waiting {wait_seconds/60:.1f} minutes for next hour...")
                    await asyncio.sleep(min(wait_seconds, 300))  # Wait max 5 minutes at a time
                    continue
                
                # Make API call
                endpoint_data = TEST_ENDPOINTS[(call_number - 1) % len(TEST_ENDPOINTS)]
                endpoint_name = endpoint_data[0]
                
                print(f"\n📡 Call #{call_number} - {endpoint_name} (Hour: {current_hour_key}, #{self.current_hour_calls + 1})")
                
                await self.make_api_call(endpoint_data, call_number)
                call_number += 1
                
                # Random wait between calls (30-120 seconds)
                wait_time = random.randint(30, 120)
                print(f"⏳ Waiting {wait_time} seconds...")
                await asyncio.sleep(wait_time)
        
        self.print_final_analysis()
        self.save_results()

    def get_previous_hour_summary(self):
        """Get summary of previous hour's performance"""
        if len(self.hourly_stats) < 2:
            return "No previous hour data"
        
        # Get second-to-last hour (previous hour)
        sorted_hours = sorted(self.hourly_stats.keys())
        if len(sorted_hours) >= 2:
            prev_hour = sorted_hours[-2]
            stats = self.hourly_stats[prev_hour]
            return f"✅{stats['success_count']} ❌{stats['rate_limited_count']} (limit hit at call #{stats['first_rate_limit_call']})"
        return "No data"

    def print_final_analysis(self):
        """Print comprehensive hourly analysis"""
        
        print("\n" + "=" * 80)
        print("🎯 HOURLY CYCLE ANALYSIS RESULTS")
        print("=" * 80)
        
        total_calls = len(self.results)
        total_success = sum(hour["success_count"] for hour in self.hourly_stats.values())
        total_rate_limited = sum(hour["rate_limited_count"] for hour in self.hourly_stats.values())
        
        print(f"\n📊 OVERALL SUMMARY:")
        print(f"   • Total calls made: {total_calls}")
        print(f"   • Hours tested: {len(self.hourly_stats)}")
        print(f"   • Total successful: {total_success}")
        print(f"   • Total rate limited: {total_rate_limited}")
        print(f"   • Overall success rate: {total_success/total_calls*100:.1f}%")
        
        print(f"\n🕐 HOURLY BREAKDOWN:")
        for hour_key in sorted(self.hourly_stats.keys()):
            stats = self.hourly_stats[hour_key]
            success_rate = stats["success_count"] / stats["total_calls"] * 100 if stats["total_calls"] > 0 else 0
            limit_call = stats["first_rate_limit_call"] or "Never"
            
            print(f"   {hour_key}: {stats['success_count']}/{stats['total_calls']} calls succeeded ({success_rate:.1f}%) - Limit hit at call #{limit_call}")
        
        # Analyze the pattern
        first_limits = [stats["first_rate_limit_call"] for stats in self.hourly_stats.values() if stats["first_rate_limit_call"]]
        if first_limits:
            avg_limit = sum(first_limits) / len(first_limits)
            print(f"\n📈 PATTERN ANALYSIS:")
            print(f"   • Average calls before rate limit: {avg_limit:.1f}")
            print(f"   • Rate limit consistency: {len(first_limits)}/{len(self.hourly_stats)} hours hit limits")
            
            if avg_limit >= 10 and avg_limit <= 15:
                print(f"   ✅ CONFIRMS: ~10-15 calls per hour limit theory")
            else:
                print(f"   🤔 UNEXPECTED: Limit pattern differs from theory")
        
        print("=" * 80)

    def save_results(self):
        """Save detailed hourly results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hourly_cycle_test_results_{timestamp}.json"
        
        data = {
            "test_info": {
                "test_type": "hourly_cycle_validation",
                "start_time": self.results[0]["timestamp"] if self.results else None,
                "end_time": self.results[-1]["timestamp"] if self.results else None,
                "total_calls": len(self.results),
                "hours_tested": len(self.hourly_stats)
            },
            "hourly_stats": self.hourly_stats,
            "detailed_results": self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 DETAILED RESULTS SAVED TO: {filename}")

async def main():
    print("🔬 Testing SoccerDataAPI Hourly Cycle Theory")
    print("Based on discovery of 'Retry-After: 3600' pattern")
    print()
    
    # Test parameters
    test_hours = 6  # Start with 6 hours
    calls_per_hour = 15  # Try 15 calls per hour to test the ~10-12 limit
    
    print(f"📋 Test Plan:")
    print(f"   • {test_hours} hours of testing")
    print(f"   • {calls_per_hour} calls per hour target")
    print(f"   • Will validate if limits reset every hour")
    print(f"   • Expected: ~10-12 successful calls per hour")
    print()
    
    tester = HourlyCycleTester()
    await tester.run_hourly_cycle_test(total_hours=test_hours, calls_per_hour_target=calls_per_hour)

if __name__ == "__main__":
    asyncio.run(main())