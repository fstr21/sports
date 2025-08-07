#!/usr/bin/env python3
"""
Simple OpenRouter API test to verify connection and model configuration.
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

def test_openrouter():
    """Test OpenRouter API connection and configuration."""
    
    print("=" * 60)
    print("OpenRouter API Test")
    print("=" * 60)
    
    # Get configuration
    api_key = os.getenv('OPENROUTER_API_KEY')
    base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    model = os.getenv('OPENROUTER_MODEL', 'openrouter/horizon-beta')
    
    print(f"API Key: {api_key[:20]}..." if api_key else "None")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print()
    
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not found in .env.local")
        return False
        
    # Test simple API call
    print("Testing API connection...")
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": "Hello! This is a test message. Please respond with 'API test successful'."}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Print usage info
            if 'usage' in result:
                usage = result['usage']
                print(f"Token Usage: {usage}")
                
            # Print response
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0]['message']['content']
                print(f"Response: {message}")
                print("\n✅ OpenRouter API test SUCCESSFUL!")
                return True
            else:
                print(f"❌ Unexpected response format: {result}")
                return False
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_openrouter()
    sys.exit(0 if success else 1)