#!/usr/bin/env python3
"""
Quick smoke test runner for MCP-only client architecture verification.

This script runs the essential smoke tests to verify:
1. No direct ESPN API calls in clients directory
2. MCP server connectivity setup
3. CLI commands work without errors
4. Rate limiting and network awareness

Usage:
    python test/run_smoke_tests.py
"""

import subprocess
import sys
from pathlib import Path

def run_smoke_tests():
    """Run essential smoke tests."""
    test_file = Path(__file__).parent / "test_smoke_e2e.py"
    
    # Essential test classes to run
    essential_tests = [
        "TestNoDirectESPNAPICalls",
        "TestMCPServerConnectivity::test_mcp_server_path_exists",
        "TestMCPServerConnectivity::test_mcp_client_connection", 
        "TestMCPServerConnectivity::test_mcp_server_error_handling",
        "TestCLICommandsSmoke::test_cli_help_commands_work",
        "TestCLICommandsSmoke::test_cli_commands_import_successfully",
        "TestRateLimitingAndNetworkAwareness::test_network_availability_check"
    ]
    
    print("🔍 Running essential smoke tests for MCP-only architecture...")
    print("=" * 60)
    
    all_passed = True
    
    for test in essential_tests:
        print(f"\n📋 Running {test}...")
        
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            f"{test_file}::{test}",
            "-v", "--tb=short", "-q"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {test} - PASSED")
        else:
            print(f"❌ {test} - FAILED")
            print(f"Error: {result.stderr}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All essential smoke tests PASSED!")
        print("\nVerified:")
        print("  ✓ No direct ESPN API calls in clients directory")
        print("  ✓ MCP server setup is correct")
        print("  ✓ CLI commands work without errors")
        print("  ✓ Rate limiting awareness is implemented")
        return 0
    else:
        print("💥 Some smoke tests FAILED!")
        print("\nPlease check the errors above and fix the issues.")
        return 1

if __name__ == "__main__":
    sys.exit(run_smoke_tests())