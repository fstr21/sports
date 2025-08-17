#!/usr/bin/env python3
"""
Quick 2-Hour Validation Test

Fast test to validate the hourly cycle theory:
1. Make 15 calls rapidly to hit the limit
2. Wait 1 hour 
3. Make 15 more calls to see if limit resets
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime, timedelta

# API Configuration
API_BASE_URL = "https://api.soccerdataapi.com/"
AUTH_KEY = "a9f37754a540df435e8c40ed89c08565166524ed"

async def test_batch(session, batch_name, target_calls=15):
    """Test a batch of calls to hit the hourly limit"""
    
    print(f"\nSTARTING {batch_name}")
    print(f"Target: {target_calls} calls to test hourly limit")
    print("-" * 50)
    
    endpoint = "livescores/"
    params = {"auth_token": AUTH_KEY}
    headers = {'Content-Type': 'application/json', 'Accept-Encoding': 'gzip'}
    
    results = []
    
    for i in range(1, target_calls + 1):
        print(f"Call #{i} ({batch_name})")
        
        try:
            async with session.get(f"{API_BASE_URL}{endpoint}", headers=headers, params=params) as response:
                
                if response.status == 200:
                    response_size = len(await response.text())
                    print(f"   SUCCESS ({response_size} bytes)")
                    results.append({"call": i, "status": "success", "code": 200})
                    
                elif response.status == 429:
                    retry_after = response.headers.get('Retry-After', 'unknown')
                    print(f"   RATE LIMITED - Retry after {retry_after}s")
                    results.append({"call": i, "status": "rate_limited", "code": 429, "retry_after": retry_after})
                    
                    # If we hit rate limit, note when it happened
                    if i <= 15:
                        print(f"   LIMIT HIT AT CALL #{i} - This confirms ~{i} calls per hour limit")
                    break
                    
                else:
                    print(f"   ERROR {response.status}")
                    results.append({"call": i, "status": "error", "code": response.status})
            
            # Small delay between calls
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"   EXCEPTION: {e}")
            results.append({"call": i, "status": "exception", "error": str(e)})
    
    # Summary
    successful = len([r for r in results if r["status"] == "success"])
    rate_limited = len([r for r in results if r["status"] == "rate_limited"])
    
    print(f"\n{batch_name} SUMMARY:")
    print(f"   Successful calls: {successful}")
    print(f"   Rate limited calls: {rate_limited}")
    
    if rate_limited > 0:
        first_limit = next(r for r in results if r["status"] == "rate_limited")
        print(f"   First rate limit at call #{first_limit['call']}")
        print(f"   Retry after: {first_limit.get('retry_after', 'unknown')} seconds")
    
    return results

async def main():
    print("QUICK HOURLY LIMIT VALIDATION TEST")
    print("=" * 60)
    print("Goal: Validate 1-hour reset theory")
    print("Plan:")
    print("   1. Batch 1: Make calls until rate limited")
    print("   2. Wait 1 hour + 5 minutes")
    print("   3. Batch 2: Test if limit has reset")
    print("=" * 60)
    
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        
        # Batch 1: Hit the limit
        start_time = datetime.now()
        batch1_results = await test_batch(session, "BATCH 1", 15)
        
        # Check if we got rate limited
        rate_limited_calls = [r for r in batch1_results if r["status"] == "rate_limited"]
        
        if rate_limited_calls:
            retry_after = rate_limited_calls[0].get("retry_after", "3600")
            
            if retry_after == "3600":
                print(f"\nCONFIRMED: 1-hour rate limit detected")
                print(f"Waiting 65 minutes (1 hour + 5 minute buffer)...")
                
                # Wait 65 minutes
                wait_seconds = 65 * 60
                end_wait_time = datetime.now() + timedelta(seconds=wait_seconds)
                
                while datetime.now() < end_wait_time:
                    remaining = (end_wait_time - datetime.now()).total_seconds()
                    print(f"   {remaining/60:.1f} minutes remaining...")
                    await asyncio.sleep(60)  # Update every minute
                
                print(f"\nWait complete! Testing if limit has reset...")
                
                # Batch 2: Test reset
                batch2_results = await test_batch(session, "BATCH 2", 15)
                
                # Analysis
                print(f"\n" + "=" * 60)
                print("HOURLY RESET ANALYSIS")
                print("=" * 60)
                
                batch1_success = len([r for r in batch1_results if r["status"] == "success"])
                batch2_success = len([r for r in batch2_results if r["status"] == "success"])
                
                print(f"Batch 1 (before wait): {batch1_success} successful calls")
                print(f"Batch 2 (after 1hr+):  {batch2_success} successful calls")
                
                if batch2_success >= batch1_success:
                    print(f"CONFIRMED: Hourly limit resets after 1 hour!")
                    print(f"API allows ~{batch1_success} calls per hour")
                else:
                    print(f"UNEXPECTED: Limit did not reset properly")
                
                # Save results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"quick_hourly_validation_{timestamp}.json"
                
                results = {
                    "test_type": "quick_hourly_validation",
                    "start_time": start_time.isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "batch1_results": batch1_results,
                    "batch2_results": batch2_results,
                    "conclusion": {
                        "batch1_successful_calls": batch1_success,
                        "batch2_successful_calls": batch2_success,
                        "hourly_limit_confirmed": batch2_success >= batch1_success,
                        "estimated_calls_per_hour": max(batch1_success, batch2_success)
                    }
                }
                
                with open(filename, 'w') as f:
                    json.dump(results, f, indent=2)
                
                print(f"\nResults saved to: {filename}")
                
            else:
                print(f"UNEXPECTED: Retry-After is {retry_after}, not 3600")
        else:
            print(f"UNEXPECTED: No rate limiting detected in batch 1")

if __name__ == "__main__":
    asyncio.run(main())