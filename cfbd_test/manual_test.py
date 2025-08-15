#!/usr/bin/env python3
"""
Manual testing script to explore CFBD endpoints without MCP
This helps understand what data is available before testing through MCP
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class CFBDDirectTester:
    def __init__(self):
        self.api_key = os.getenv('CFBD_API_KEY')
        self.base_url = "https://api.collegefootballdata.com"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json'
        }
    
    def test_endpoint(self, endpoint, params=None):
        """Test a direct API endpoint"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error calling {endpoint}: {e}")
            return None
    
    def run_tests(self):
        """Run various endpoint tests"""
        print("=== CFBD Direct API Testing ===\n")
        
        # Test cases
        tests = [
            {
                "name": "Teams (2024)",
                "endpoint": "/teams",
                "params": {"year": 2024}
            },
            {
                "name": "Conferences",
                "endpoint": "/conferences",
                "params": {}
            },
            {
                "name": "Games (Week 1, 2024)",
                "endpoint": "/games",
                "params": {"year": 2024, "week": 1}
            },
            {
                "name": "Team Stats (2024)",
                "endpoint": "/stats/season",
                "params": {"year": 2024}
            },
            {
                "name": "Rankings (Week 1, 2024)",
                "endpoint": "/rankings",
                "params": {"year": 2024, "week": 1}
            }
        ]
        
        for test in tests:
            print(f"--- {test['name']} ---")
            result = self.test_endpoint(test['endpoint'], test['params'])
            
            if result:
                if isinstance(result, list):
                    print(f"Found {len(result)} results")
                    if len(result) > 0:
                        print("Sample result:")
                        print(json.dumps(result[0], indent=2))
                else:
                    print("Result:")
                    print(json.dumps(result, indent=2))
            else:
                print("No data returned")
            
            print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    if not os.getenv('CFBD_API_KEY'):
        print("Error: CFBD_API_KEY not found in environment variables")
        print("Please create a .env file with your API key")
        exit(1)
    
    tester = CFBDDirectTester()
    tester.run_tests()