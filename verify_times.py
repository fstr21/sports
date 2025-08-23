#!/usr/bin/env python3
"""
Quick verification of Eastern Time display
"""
from datetime import datetime, timezone, timedelta

# Test time conversions for verification
test_times = [
    "2025-08-23T16:10:00-04:00",  # Blue Jays @ Marlins
    "2025-08-23T17:10:00Z",       # Example UTC time
    "2025-08-23T13:05:00-04:00"   # Red Sox @ Yankees
]

for time_str in test_times:
    try:
        if time_str.endswith('Z'):
            # UTC time
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            eastern_tz = timezone(timedelta(hours=-4))  # EDT
            dt_eastern = dt.astimezone(eastern_tz)
        else:
            # Already has timezone info
            dt = datetime.fromisoformat(time_str)
            dt_eastern = dt
        
        formatted_time = dt_eastern.strftime("%I:%M %p ET").lstrip('0')
        print(f"Input: {time_str}")
        print(f"Eastern Time: {formatted_time}")
        print()
        
    except Exception as e:
        print(f"Error with {time_str}: {e}")