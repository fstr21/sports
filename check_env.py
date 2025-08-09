#!/usr/bin/env python3
"""
Check environment variables on Railway
"""

import requests
import json

RAILWAY_URL = "https://web-production-b939f.up.railway.app"
API_KEY = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print("Checking Railway environment...")

# Check health to see what services are configured
response = requests.get(f"{RAILWAY_URL}/health")
if response.status_code == 200:
    health = response.json()
    services = health.get("services", {})
    print("Services status:")
    for service, status in services.items():
        print(f"  {service}: {'OK' if status else 'NOT CONFIGURED'}")
    print()
else:
    print("Health check failed")

# Try to make a direct odds API call to see what error we get
print("Testing WNBA odds request...")
response = requests.post(
    f"{RAILWAY_URL}/odds/get-odds",
    headers=headers,
    json={"sport": "basketball_wnba", "regions": "us", "markets": "h2h"}
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print("Response type:", type(data))
    if isinstance(data, dict):
        if "error" in data:
            print("ERROR:", data["error"])
        elif "_metadata" in data:
            print("Getting test data - API key not configured correctly")
        else:
            print("Keys:", list(data.keys())[:5])
elif response.status_code == 503:
    print("Service unavailable - likely no API key configured")
else:
    print("Response:", response.text[:200])