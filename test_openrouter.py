#!/usr/bin/env python3
"""Test OpenRouter API Key"""

import os
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv('.env.local')

api_key = os.getenv("OPENROUTER_API_KEY")
print(f"API Key loaded: {api_key[:10]}..." if api_key else "No API key found")

# Test the API key
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Try a simple test call
data = {
    "model": "openai/gpt-3.5-turbo",
    "messages": [
        {"role": "user", "content": "Hello"}
    ],
    "max_tokens": 10
}

try:
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                           headers=headers, json=data, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        print("[OK] OpenRouter API key is working!")
    elif response.status_code == 401:
        print("[ERROR] API key is invalid or expired")
    else:
        print(f"[WARNING] Unexpected response: {response.status_code}")
        
except Exception as e:
    print(f"[ERROR] Error testing API: {e}")