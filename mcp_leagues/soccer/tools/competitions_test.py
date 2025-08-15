#!/usr/bin/env python3
"""
Test #1: Soccer MCP - Get Available Competitions
Tests the getCompetitions tool specifically for EPL and La Liga access
Exports results to JSON file for analysis
"""

import httpx
import json
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, Optional

class SoccerCompetitionsTester:
    """Test Soccer MCP competitions functionality"""
    
    def __init__(self):
        # Update this URL when your Soccer MCP is deployed
        self.server_url = "https://your-soccer-mcp.up.railway.app/mcp"  # TODO: Update with actual URL
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "server_url": self.server_url,
            "target_competitions": {
                "EPL": {"id": "PL", "name": "Premier League", "found": False},
                "La_Liga": {"id": "PD", "name": "Primera División", "found": False}
            },
            "tests": {},
            "summary": {}
        }
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Call an MCP tool"""
        if arguments is None:
            arguments = {}
            
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        print(f"[*] Calling Soccer MCP: {tool_name}")
        if arguments:
            print(f"    Arguments: {arguments}")
        
        try:
            response = await self.client.post(self.server_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                print(f"[!] MCP Error: {result['error']}")
                return None
            
            return result.get("result", {})
            
        except Exception as e:
            print(f"[!] Request failed: {e}")
            return None
    
    async def test_competitions_access(self):
        """Test getting available competitions and verify EPL/La Liga access"""
        print("=" * 60)
        print("TEST #1: Soccer MCP - Available Competitions")
        print("=" * 60)
        print("Target: EPL (Premier League) and La Liga access verification")
        
        # Test 1A: Get all competitions (test mode first)
        print("\n--- Test 1A: Test Mode (Mock Data) ---")
        test_result = await self.call_mcp_tool("getCompetitions", {"use_test_mode": True})
        
        if test_result:
            self.analyze_competitions_result(test_result, "Test Mode")
            self.results["tests"]["test_mode"] = {
                "success": True,
                "method": "test mode with mock data",
                "raw_data": test_result
            }
        else:
            self.results["tests"]["test_mode"] = {"success": False, "error": "No data returned"}
        
        # Test 1B: Get all competitions (live API)
        print("\n--- Test 1B: Live API ---")
        live_result = await self.call_mcp_tool("getCompetitions")
        
        if live_result:
            self.analyze_competitions_result(live_result, "Live API", check_target_leagues=True)
            self.results["tests"]["live_api"] = {
                "success": True,
                "method": "live Football-Data.org API",
                "raw_data": live_result
            }
        else:
            self.results["tests"]["live_api"] = {"success": False, "error": "No data returned"}
        
        # Test 1C: Check API key configuration
        print("\n--- Test 1C: API Key Verification ---")
        if live_result:
            if self.check_api_error(live_result):
                print("[!] API Key issues detected")
                self.results["tests"]["api_key"] = {"success": False, "error": "API key configuration issue"}
            else:
                print("[+] API Key working correctly")
                self.results["tests"]["api_key"] = {"success": True, "message": "API key valid"}
        
        # Summary
        print(f"\n{'=' * 60}")
        print("TEST #1 SUMMARY - Competition Access")
        print(f"{'=' * 60}")
        
        summary = {"status": "UNKNOWN", "available_leagues": [], "missing_leagues": []}
        
        if live_result and live_result.get("ok"):
            print("[+] Soccer MCP getCompetitions: WORKING")
            
            # Check which target leagues we found
            epl_found = self.results["target_competitions"]["EPL"]["found"]
            liga_found = self.results["target_competitions"]["La_Liga"]["found"]
            
            if epl_found and liga_found:
                print("[+] SUCCESS: Both EPL and La Liga accessible")
                summary["status"] = "SUCCESS"
                summary["available_leagues"] = ["EPL", "La Liga"]
            elif epl_found or liga_found:
                found_league = "EPL" if epl_found else "La Liga"
                missing_league = "La Liga" if epl_found else "EPL"
                print(f"[!] PARTIAL: Only {found_league} found, missing {missing_league}")
                summary["status"] = "PARTIAL"
                summary["available_leagues"] = [found_league]
                summary["missing_leagues"] = [missing_league]
            else:
                print("[!] WARNING: Neither EPL nor La Liga found")
                print("    This could indicate:")
                print("    - API plan limitations")
                print("    - Incorrect competition IDs")
                print("    - API access issues")
                summary["status"] = "WARNING"
                summary["missing_leagues"] = ["EPL", "La Liga"]
        else:
            print("[-] Soccer MCP getCompetitions: FAILED")
            summary["status"] = "FAILED"
        
        self.results["summary"] = summary
        
        # Export results
        await self.export_results()
    
    def analyze_competitions_result(self, result: Dict[str, Any], test_name: str, check_target_leagues: bool = False):
        """Analyze and display competitions result"""
        print(f"\n[*] Analyzing: {test_name}")
        
        # Check result structure
        if not isinstance(result, dict):
            print(f"[!] ERROR: Result is not a dict: {type(result)}")
            return
        
        print(f"    Result keys: {list(result.keys())}")
        
        # Check success
        if not result.get("ok"):
            print(f"[!] ERROR: Result indicates failure")
            error_msg = result.get("error", "Unknown error")
            print(f"    Error: {error_msg}")
            return
        
        # Check data field
        data = result.get("data")
        if not data:
            print(f"[!] ERROR: No 'data' field in result")
            return
        
        print(f"    Data keys: {list(data.keys())}")
        
        # Extract competitions
        competitions = data.get("competitions", [])
        count = data.get("count", len(competitions))
        source = data.get("source", "unknown")
        
        print(f"    Source: {source}")
        print(f"    Competition count: {count}")
        print(f"    Actual competitions: {len(competitions)}")
        
        # Show competitions
        if competitions:
            print(f"\n    All competitions found:")
            for i, comp in enumerate(competitions):
                comp_id = comp.get("id", "Unknown")
                name = comp.get("name", "Unknown")
                code = comp.get("code", "Unknown") 
                area = comp.get("area", {}).get("name", "Unknown")
                comp_type = comp.get("type", "Unknown")
                
                print(f"      {i+1:2d}. {name} ({code})")
                print(f"          ID: {comp_id}, Area: {area}, Type: {comp_type}")
                
                # Check if this is one of our target leagues
                if check_target_leagues:
                    if code == "PL" or comp_id == 2021:
                        print(f"          *** EPL FOUND ***")
                        self.results["target_competitions"]["EPL"]["found"] = True
                        self.results["target_competitions"]["EPL"]["full_data"] = comp
                    elif code == "PD" or comp_id == 2014:
                        print(f"          *** LA LIGA FOUND ***")
                        self.results["target_competitions"]["La_Liga"]["found"] = True
                        self.results["target_competitions"]["La_Liga"]["full_data"] = comp
        else:
            print(f"    [!] No competitions found")
        
        # Check meta info
        meta = result.get("meta")
        if meta:
            timestamp = meta.get("timestamp", "unknown")
            test_mode = meta.get("test_mode", False)
            print(f"    Timestamp: {timestamp}")
            print(f"    Test mode: {test_mode}")
    
    def check_api_error(self, result: Dict[str, Any]) -> bool:
        """Check if result indicates API key or quota issues"""
        # Common API error indicators
        error_indicators = [
            "unauthorized", "forbidden", "quota", "limit", "key", 
            "authentication", "401", "403", "429"
        ]
        
        result_str = str(result).lower()
        
        for indicator in error_indicators:
            if indicator in result_str:
                return True
        
        return False
    
    async def export_results(self):
        """Export test results to JSON file"""
        output_dir = "C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\soccer\\tools"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"competitions_test_results_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"\n[+] Results exported to: {filepath}")
            
            # Show file size
            file_size = os.path.getsize(filepath)
            if file_size > 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size} bytes"
            
            print(f"[+] File size: {size_str}")
            
            # Show key findings
            summary = self.results.get("summary", {})
            status = summary.get("status", "UNKNOWN")
            print(f"[+] Test status: {status}")
            
            available = summary.get("available_leagues", [])
            missing = summary.get("missing_leagues", [])
            
            if available:
                print(f"[+] Available leagues: {', '.join(available)}")
            if missing:
                print(f"[!] Missing leagues: {', '.join(missing)}")
            
        except Exception as e:
            print(f"[!] Failed to export results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Run the competitions test"""
    tester = SoccerCompetitionsTester()
    
    print("Soccer MCP - Competitions Test")
    print("Checking access to EPL and La Liga")
    print("NOTE: Update server_url in script with your deployed Soccer MCP URL")
    
    try:
        await tester.test_competitions_access()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())