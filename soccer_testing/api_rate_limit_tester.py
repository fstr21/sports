#!/usr/bin/env python3
"""
SoccerDataAPI Rate Limit Tester

Test the actual rate limiting behavior by making 100 automated API calls
with 2-second intervals. Track responses, timing, and any rate limiting.

This will help us understand:
1. When/if the 75 calls/day limit actually triggers
2. What happens when we hit the limit
3. Response patterns and error codes
"""

import asyncio
import aiohttp
import time
import json
import random
from datetime import datetime
from collections import defaultdict

# API Configuration
API_BASE_URL = "https://api.soccerdataapi.com/"
AUTH_KEY = "a9f37754a540df435e8c40ed89c08565166524ed"

# Test endpoints (lightweight calls) with parameters
TEST_ENDPOINTS = [
    ("livescores/", {}),                              # Live scores
    ("league/", {}),                                  # All leagues  
    ("standing/", {"league_id": 228}),                # EPL standings
    ("team/", {"team_id": 4145}),                     # West Ham info
    ("matches/", {"league_id": 228}),                 # EPL matches
]

class APIRateLimitTester:
    def __init__(self):
        self.results = []
        self.success_count = 0
        self.error_count = 0
        self.rate_limited_count = 0
        self.start_time = None
        self.session = None
        
    async def make_api_call(self, endpoint_data, call_number):
        """Make a single API call and record results"""
        
        endpoint, endpoint_params = endpoint_data
        
        headers = {
            'Content-Type': 'application/json',
            'Accept-Encoding': 'gzip'
        }
        
        # Add auth token and endpoint-specific parameters
        params = {"auth_token": AUTH_KEY}
        params.update(endpoint_params)
        
        url = API_BASE_URL + endpoint
        call_start_time = time.time()
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                call_end_time = time.time()
                response_time = call_end_time - call_start_time
                
                # Try to get response text
                try:
                    response_text = await response.text()
                    response_size = len(response_text)
                    
                    # Try to parse as JSON
                    try:
                        response_data = json.loads(response_text)
                        data_type = "json"
                    except:
                        response_data = response_text[:200] + "..." if len(response_text) > 200 else response_text
                        data_type = "text"
                        
                except Exception as e:
                    response_text = f"Error reading response: {e}"
                    response_data = None
                    response_size = 0
                    data_type = "error"
                
                # Record the result
                result = {
                    "call_number": call_number,
                    "timestamp": datetime.now().isoformat(),
                    "endpoint": endpoint,
                    "url": url,
                    "status_code": response.status,
                    "response_time_seconds": round(response_time, 3),
                    "response_size_bytes": response_size,
                    "data_type": data_type,
                    "headers": dict(response.headers),
                    "elapsed_time_from_start": round(time.time() - self.start_time, 1)
                }
                
                # Check for rate limiting indicators
                if response.status == 429:
                    result["rate_limited"] = True
                    result["error_type"] = "rate_limit"
                    self.rate_limited_count += 1
                    print(f"⚠️  Call #{call_number} - RATE LIMITED (429)")
                    
                elif response.status == 403:
                    result["rate_limited"] = True
                    result["error_type"] = "forbidden"
                    self.rate_limited_count += 1
                    print(f"⚠️  Call #{call_number} - FORBIDDEN (403)")
                    
                elif response.status != 200:
                    result["error"] = True
                    result["error_type"] = f"http_{response.status}"
                    result["response_preview"] = response_data
                    self.error_count += 1
                    print(f"❌ Call #{call_number} - ERROR {response.status}")
                    
                else:
                    result["success"] = True
                    self.success_count += 1
                    
                    # Sample response data for successful calls
                    if isinstance(response_data, dict):
                        if "data" in response_data:
                            result["data_sample"] = str(response_data["data"])[:100] + "..."
                        elif isinstance(response_data, list) and len(response_data) > 0:
                            result["data_sample"] = f"Array with {len(response_data)} items"
                        else:
                            result["data_sample"] = str(response_data)[:100] + "..."
                    
                    print(f"✅ Call #{call_number} - SUCCESS ({response_time:.2f}s, {response_size} bytes)")
                
                self.results.append(result)
                return result
                
        except asyncio.TimeoutError:
            result = {
                "call_number": call_number,
                "timestamp": datetime.now().isoformat(),
                "endpoint": endpoint,
                "url": url,
                "error": True,
                "error_type": "timeout",
                "elapsed_time_from_start": round(time.time() - self.start_time, 1)
            }
            self.results.append(result)
            self.error_count += 1
            print(f"⏰ Call #{call_number} - TIMEOUT")
            return result
            
        except Exception as e:
            result = {
                "call_number": call_number,
                "timestamp": datetime.now().isoformat(),
                "endpoint": endpoint,
                "url": url,
                "error": True,
                "error_type": "exception",
                "error_message": str(e),
                "elapsed_time_from_start": round(time.time() - self.start_time, 1)
            }
            self.results.append(result)
            self.error_count += 1
            print(f"💥 Call #{call_number} - EXCEPTION: {e}")
            return result

    async def run_test(self, total_calls=100, min_interval=60, max_interval=240):
        """Run the rate limit test"""
        
        print("🚀 STARTING API RATE LIMIT TEST")
        print("=" * 60)
        print(f"📊 Configuration:")
        print(f"   • Total calls: {total_calls}")
        print(f"   • Interval: {min_interval}-{max_interval} seconds (random)")
        print(f"   • Average interval: {(min_interval + max_interval) / 2:.1f} seconds")
        print(f"   • API Key: {AUTH_KEY[:20]}...")
        print(f"   • Test endpoints: {len(TEST_ENDPOINTS)}")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Create HTTP session with timeout
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            self.session = session
            
            for call_num in range(1, total_calls + 1):
                # Cycle through endpoints
                endpoint_data = TEST_ENDPOINTS[(call_num - 1) % len(TEST_ENDPOINTS)]
                endpoint_name = endpoint_data[0]
                endpoint_params = endpoint_data[1]
                
                param_str = f" (params: {endpoint_params})" if endpoint_params else ""
                print(f"\n📡 Call #{call_num}/{total_calls} - {endpoint_name}{param_str}")
                
                # Make the API call
                await self.make_api_call(endpoint_data, call_num)
                
                # Print progress every 10 calls
                if call_num % 10 == 0:
                    elapsed = time.time() - self.start_time
                    print(f"\n📈 Progress Update (Call #{call_num}):")
                    print(f"   ✅ Successful: {self.success_count}")
                    print(f"   ❌ Errors: {self.error_count}")
                    print(f"   ⚠️  Rate Limited: {self.rate_limited_count}")
                    print(f"   ⏱️  Elapsed: {elapsed/60:.1f} minutes")
                
                # Check if we should stop early due to consistent rate limiting
                if self.rate_limited_count >= 5 and call_num > 10:
                    print(f"\n🛑 STOPPING EARLY - Consistent rate limiting detected")
                    break
                
                # Wait before next call (except for last call)
                if call_num < total_calls:
                    # Random interval between min and max
                    wait_time = random.randint(min_interval, max_interval)
                    print(f"⏳ Waiting {wait_time} seconds (random: {min_interval}-{max_interval}s)...")
                    await asyncio.sleep(wait_time)
        
        # Final analysis
        self.print_final_analysis()
        self.save_results()

    def print_final_analysis(self):
        """Print comprehensive analysis of the test results"""
        
        total_calls = len(self.results)
        elapsed_time = time.time() - self.start_time
        
        print("\n" + "=" * 80)
        print("🎯 FINAL ANALYSIS - API RATE LIMIT TEST RESULTS")
        print("=" * 80)
        
        print(f"\n📊 SUMMARY STATISTICS:")
        print(f"   • Total API calls made: {total_calls}")
        print(f"   • Test duration: {elapsed_time/60:.2f} minutes")
        print(f"   • Average call rate: {total_calls/(elapsed_time/60):.1f} calls/minute")
        print(f"   • Successful calls: {self.success_count} ({self.success_count/total_calls*100:.1f}%)")
        print(f"   • Failed calls: {self.error_count} ({self.error_count/total_calls*100:.1f}%)")
        print(f"   • Rate limited calls: {self.rate_limited_count} ({self.rate_limited_count/total_calls*100:.1f}%)")
        
        # Response time analysis
        successful_calls = [r for r in self.results if r.get("success")]
        if successful_calls:
            response_times = [r["response_time_seconds"] for r in successful_calls]
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            print(f"\n⏱️  RESPONSE TIME ANALYSIS:")
            print(f"   • Average response time: {avg_response_time:.3f} seconds")
            print(f"   • Fastest response: {min_response_time:.3f} seconds")
            print(f"   • Slowest response: {max_response_time:.3f} seconds")
        
        # Error analysis
        error_types = defaultdict(int)
        for result in self.results:
            if result.get("error") or result.get("rate_limited"):
                error_type = result.get("error_type", "unknown")
                error_types[error_type] += 1
        
        if error_types:
            print(f"\n❌ ERROR BREAKDOWN:")
            for error_type, count in error_types.items():
                print(f"   • {error_type}: {count} occurrences")
        
        # Rate limiting analysis
        if self.rate_limited_count > 0:
            rate_limited_calls = [r for r in self.results if r.get("rate_limited")]
            first_rate_limit = rate_limited_calls[0]
            
            print(f"\n⚠️  RATE LIMITING DETECTED:")
            print(f"   • First rate limit at call #{first_rate_limit['call_number']}")
            print(f"   • Time to first rate limit: {first_rate_limit['elapsed_time_from_start']/60:.1f} minutes")
            print(f"   • Total rate limited: {self.rate_limited_count} calls")
            
            # Check for patterns
            if self.rate_limited_count >= total_calls * 0.5:
                print(f"   🔥 HEAVY RATE LIMITING - Over 50% of calls blocked")
            elif self.rate_limited_count >= 5:
                print(f"   ⚠️  MODERATE RATE LIMITING - Multiple calls blocked")
        else:
            print(f"\n✅ NO RATE LIMITING DETECTED")
            print(f"   • All {total_calls} calls completed without rate limiting")
            print(f"   • API appears to allow more than documented 75 calls/day")
        
        # Endpoint analysis
        endpoint_stats = defaultdict(lambda: {"success": 0, "error": 0, "rate_limited": 0})
        for result in self.results:
            endpoint = result["endpoint"]
            if result.get("success"):
                endpoint_stats[endpoint]["success"] += 1
            elif result.get("rate_limited"):
                endpoint_stats[endpoint]["rate_limited"] += 1
            else:
                endpoint_stats[endpoint]["error"] += 1
        
        print(f"\n📡 ENDPOINT PERFORMANCE:")
        for endpoint, stats in endpoint_stats.items():
            total_for_endpoint = sum(stats.values())
            success_rate = stats["success"] / total_for_endpoint * 100 if total_for_endpoint > 0 else 0
            print(f"   • {endpoint}: {stats['success']}/{total_for_endpoint} success ({success_rate:.1f}%)")
        
        print("=" * 80)

    def save_results(self):
        """Save detailed results to JSON file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_rate_limit_test_results_{timestamp}.json"
        
        test_summary = {
            "test_info": {
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "end_time": datetime.now().isoformat(),
                "total_calls": len(self.results),
                "duration_minutes": round((time.time() - self.start_time) / 60, 2),
                "api_key_prefix": AUTH_KEY[:20] + "...",
                "endpoints_tested": TEST_ENDPOINTS
            },
            "summary_stats": {
                "successful_calls": self.success_count,
                "failed_calls": self.error_count,
                "rate_limited_calls": self.rate_limited_count,
                "success_rate_percent": round(self.success_count / len(self.results) * 100, 1) if self.results else 0,
                "rate_limit_triggered": self.rate_limited_count > 0
            },
            "detailed_results": self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(test_summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 DETAILED RESULTS SAVED TO: {filename}")
        print(f"📋 Contains {len(self.results)} individual call records")

async def main():
    print("🔬 SoccerDataAPI Rate Limit Tester")
    print("Testing actual API limits vs documented 75 calls/day")
    print()
    
    # Confirm test parameters
    total_calls = 400
    min_interval = 60   # 1 minute
    max_interval = 240  # 4 minutes
    avg_interval = (min_interval + max_interval) / 2
    
    print(f"⚠️  WARNING: This will make {total_calls} API calls over ~{total_calls * avg_interval / 60:.0f} minutes ({total_calls * avg_interval / 3600:.1f} hours)")
    print(f"⚠️  This is a randomized overnight test - 1 to 4 minutes between calls")
    print()
    
    # Create and run the tester
    tester = APIRateLimitTester()
    await tester.run_test(total_calls=total_calls, min_interval=min_interval, max_interval=max_interval)
    
    print(f"\n🎉 RATE LIMIT TEST COMPLETE!")
    print(f"Check the generated JSON file for detailed analysis")

if __name__ == "__main__":
    asyncio.run(main())