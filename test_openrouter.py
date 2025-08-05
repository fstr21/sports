#!/usr/bin/env python3
"""
Simple OpenRouter API test to troubleshoot the connection
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

def test_openrouter_connection():
    """Test basic OpenRouter API connection"""
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    model = os.getenv('OPENROUTER_MODEL', 'openrouter/horizon-beta')
    
    print(f"🔑 API Key: {api_key[:20]}..." if api_key else "❌ No API Key found")
    print(f"🌐 Base URL: {base_url}")
    print(f"🤖 Model: {model}")
    print("-" * 50)
    
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in .env.local")
        return
    
    # Test 1: Simple API call with minimal payload
    print("🧪 Test 1: Basic API connection...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Hello, can you respond with just 'OK'?"}
        ],
        "max_tokens": 10,
        "temperature": 0
    }
    
    try:
        print("📡 Sending request...")
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=10  # Short timeout for testing
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ Success! Response: {json.dumps(response_data, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - OpenRouter might be slow")
    except requests.exceptions.ConnectionError:
        print("🌐 Connection error - check internet connection")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_espn_api():
    """Test ESPN API to make sure that part works"""
    print("\n" + "=" * 50)
    print("🏀 Testing ESPN API...")
    
    url = "http://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard"
    params = {"dates": "20250805"}
    headers = {
        "Accept": "application/json",
        "User-Agent": "ESPN-Research/1.0"
    }
    
    try:
        print("📡 Fetching WNBA data...")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            events = data.get("events", [])
            print(f"✅ Success! Found {len(events)} WNBA games")
            
            if events:
                game = events[0]
                print(f"📋 Sample game: {game.get('name', 'Unknown')}")
        else:
            print(f"❌ ESPN API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ESPN API Error: {e}")

if __name__ == "__main__":
    print("🔧 OpenRouter + ESPN API Troubleshooting")
    print("=" * 50)
    
    test_openrouter_connection()
    test_espn_api()
    
    print("\n" + "=" * 50)
    print("🎯 Troubleshooting complete!")