#!/usr/bin/env python3
"""
CFB Tools Individual Runner
Runs each CFB tool individually and confirms outputs are saved in the tools directory
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

def run_individual_tool_tests():
    """Run each CFB tool individually"""
    
    # Change to the tools directory
    tools_dir = Path(__file__).parent
    original_dir = os.getcwd()
    
    try:
        os.chdir(tools_dir)
        print(f"🔧 Changed to tools directory: {tools_dir}")
        print(f"📁 Current working directory: {os.getcwd()}")
        
        # List of tools to test
        tools = [
            ("games.py", "CFB Games Tool"),
            ("roster.py", "CFB Roster Tool"),
            ("rankings.py", "CFB Rankings Tool"),
            ("player_stats.py", "CFB Player Stats Tool")
        ]
        
        print(f"\n🚀 TESTING {len(tools)} CFB TOOLS INDIVIDUALLY")
        print("=" * 60)
        
        for tool_file, tool_name in tools:
            print(f"\n🏈 Running {tool_name} ({tool_file})")
            print("-" * 40)
            
            try:
                # Run the tool
                result = subprocess.run([sys.executable, tool_file], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=60)
                
                if result.returncode == 0:
                    print(f"✅ {tool_name} completed successfully")
                    
                    # Check if JSON file was created/updated
                    json_file = tool_file.replace('.py', '.json')
                    if os.path.exists(json_file):
                        file_size = os.path.getsize(json_file)
                        print(f"   📄 Output file: {json_file} ({file_size:,} bytes)")
                    else:
                        print(f"   ⚠️  No output file found: {json_file}")
                    
                    # Show last few lines of output
                    output_lines = result.stdout.strip().split('\n')
                    if len(output_lines) > 3:
                        print(f"   📝 Last few lines:")
                        for line in output_lines[-3:]:
                            if line.strip():
                                print(f"      {line}")
                    
                else:
                    print(f"❌ {tool_name} failed with return code {result.returncode}")
                    if result.stderr:
                        print(f"   Error: {result.stderr[:200]}")
                
            except subprocess.TimeoutExpired:
                print(f"⏰ {tool_name} timed out after 60 seconds")
            except Exception as e:
                print(f"❌ Error running {tool_name}: {e}")
        
        # Summary of files in directory
        print(f"\n📊 FINAL DIRECTORY CONTENTS")
        print("=" * 60)
        
        json_files = list(Path('.').glob('*.json'))
        py_files = list(Path('.').glob('*.py'))
        
        print(f"Python tools: {len(py_files)}")
        for py_file in sorted(py_files):
            print(f"   🐍 {py_file.name}")
        
        print(f"\nJSON outputs: {len(json_files)}")
        for json_file in sorted(json_files):
            size = json_file.stat().st_size
            print(f"   📄 {json_file.name} ({size:,} bytes)")
        
        print(f"\n✅ All tools tested from directory: {tools_dir}")
        
    finally:
        # Change back to original directory
        os.chdir(original_dir)
        print(f"🔙 Returned to original directory: {original_dir}")

if __name__ == "__main__":
    run_individual_tool_tests()