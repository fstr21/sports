#!/usr/bin/env python3
"""
Check what the actual package name should be
"""

import subprocess

def try_package_names():
    """Try different possible package names"""
    possible_names = [
        "lenwood.cfbd-mcp-server",
        "cfbd-mcp-server", 
        "lenwood-cfbd-mcp-server",
        "cfbd_mcp_server",
        "lenwood_cfbd_mcp_server"
    ]
    
    for name in possible_names:
        print(f"\nTrying package name: {name}")
        try:
            result = subprocess.run(
                ["uvx", "run", name, "--help"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            print(f"Return code: {result.returncode}")
            if result.returncode == 0:
                print(f"SUCCESS! Package name is: {name}")
                print(f"Output: {result.stdout}")
                return name
            else:
                print(f"Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("Timeout - might be working but hanging")
        except Exception as e:
            print(f"Exception: {e}")
    
    return None

if __name__ == "__main__":
    print("=== Testing Package Names ===")
    success = try_package_names()
    if not success:
        print("\nNone of the package names worked. Let's try installing from git directly.")
        print("The repository might need to be cloned and run locally.")