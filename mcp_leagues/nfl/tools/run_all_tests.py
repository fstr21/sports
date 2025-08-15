#!/usr/bin/env python3
"""
Run All NFL MCP Tests
Comprehensive test suite for NFL MCP functionality
"""

import asyncio
import subprocess
import sys
import os
from datetime import datetime

class NFLTestRunner:
    """Run all NFL MCP tests in sequence"""
    
    def __init__(self):
        self.test_scripts = [
            "test_schedule.py",
            "test_teams.py", 
            "test_player_stats.py",
            "test_injuries.py",
            "test_nfl_odds_integration.py"
        ]
        
        self.results = {}
        self.start_time = datetime.now()
    
    def run_test_script(self, script_name: str) -> bool:
        """Run a single test script"""
        print(f"\n{'='*60}")
        print(f"RUNNING: {script_name}")
        print(f"{'='*60}")
        
        try:
            # Run the script
            result = subprocess.run([
                sys.executable, script_name
            ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            # Check if successful
            success = result.returncode == 0
            
            # Store results
            self.results[script_name] = {
                "success": success,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": datetime.now()
            }
            
            # Print output
            if result.stdout:
                print(result.stdout)
            
            if result.stderr:
                print("STDERR:", result.stderr)
            
            if success:
                print(f"\n[+] {script_name} completed successfully")
            else:
                print(f"\n[!] {script_name} failed with return code {result.returncode}")
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"[!] {script_name} timed out after 5 minutes")
            self.results[script_name] = {
                "success": False,
                "error": "Timeout after 5 minutes"
            }
            return False
            
        except Exception as e:
            print(f"[!] Error running {script_name}: {e}")
            self.results[script_name] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        end_time = datetime.now()
        total_time = end_time - self.start_time
        
        print(f"\n{'='*80}")
        print("NFL MCP COMPREHENSIVE TEST SUMMARY")
        print(f"{'='*80}")
        
        print(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total execution time: {total_time}")
        
        # Count results
        total_tests = len(self.test_scripts)
        successful_tests = sum(1 for r in self.results.values() if r.get("success", False))
        
        print(f"\nTest Results: {successful_tests}/{total_tests} passed")
        
        # Individual test results
        print(f"\nIndividual Test Results:")
        for script in self.test_scripts:
            if script in self.results:
                result = self.results[script]
                status = "PASS" if result.get("success", False) else "FAIL"
                print(f"  {script:<35} {status}")
                
                if not result.get("success", False) and "error" in result:
                    print(f"    Error: {result['error']}")
            else:
                print(f"  {script:<35} NOT RUN")
        
        # Overall assessment
        print(f"\nOverall Assessment:")
        
        if successful_tests == total_tests:
            print("[+] EXCELLENT: All NFL MCP tests passed")
            print("[+] NFL MCP is fully operational and ready for Week 1")
            print("[+] All tools validated and integration confirmed")
            
        elif successful_tests >= total_tests * 0.8:
            print("[!] GOOD: Most NFL MCP tests passed")
            print("[!] Minor issues detected - review failed tests")
            print("[!] NFL MCP mostly ready for Week 1")
            
        elif successful_tests >= total_tests * 0.5:
            print("[!] PARTIAL: Some NFL MCP tests passed")
            print("[!] Significant issues detected - address failures")
            print("[!] NFL MCP needs fixes before Week 1")
            
        else:
            print("[-] POOR: Most NFL MCP tests failed")
            print("[-] Major issues detected - extensive fixes needed")
            print("[-] NFL MCP not ready for Week 1")
        
        # Recommendations
        print(f"\nRecommendations:")
        
        failed_tests = [script for script in self.test_scripts 
                       if not self.results.get(script, {}).get("success", False)]
        
        if not failed_tests:
            print("✓ NFL MCP deployment successful")
            print("✓ Begin monitoring for Week 1 readiness")
            print("✓ Consider load testing with expected Week 1 traffic")
            
        else:
            print("1. Review and fix failing tests:")
            for failed_test in failed_tests:
                print(f"   - {failed_test}")
            print("2. Re-run tests after fixes")
            print("3. Validate against live data when Week 1 starts")
        
        # Week 1 readiness
        print(f"\nWeek 1 Readiness Status:")
        
        critical_tests = ["test_schedule.py", "test_nfl_odds_integration.py"]
        critical_passed = sum(1 for test in critical_tests 
                            if self.results.get(test, {}).get("success", False))
        
        if critical_passed == len(critical_tests):
            print("✓ READY: Critical functionality validated")
            print("✓ Schedule and odds integration working")
            print("✓ Proceed with Week 1 deployment")
        else:
            print("⚠ NOT READY: Critical tests failed")
            print("⚠ Fix critical issues before Week 1")
            
        return successful_tests, total_tests
    
    def run_all_tests(self):
        """Run all test scripts"""
        print("NFL MCP COMPREHENSIVE TEST SUITE")
        print("Testing all functionality before Week 1")
        print(f"Server: nflmcp-production.up.railway.app")
        print(f"Running {len(self.test_scripts)} test scripts")
        
        # Change to tools directory
        tools_dir = "C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\nfl\\tools"
        os.chdir(tools_dir)
        
        successful_count = 0
        
        # Run each test
        for i, script in enumerate(self.test_scripts, 1):
            print(f"\n[{i}/{len(self.test_scripts)}] Starting {script}...")
            
            if self.run_test_script(script):
                successful_count += 1
            
            # Brief pause between tests
            if i < len(self.test_scripts):
                print(f"\nPausing 3 seconds before next test...")
                import time
                time.sleep(3)
        
        # Generate summary
        self.generate_summary()
        
        return successful_count, len(self.test_scripts)

def main():
    """Main function"""
    runner = NFLTestRunner()
    
    try:
        passed, total = runner.run_all_tests()
        
        # Exit with appropriate code
        if passed == total:
            sys.exit(0)  # All tests passed
        else:
            sys.exit(1)  # Some tests failed
            
    except KeyboardInterrupt:
        print(f"\n\nTest suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()