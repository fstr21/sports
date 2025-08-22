#!/usr/bin/env python3
"""
Chronulus MCP Installation Script
Handles installation of Chronulus MCP server for testing
"""
import subprocess
import sys
import os
import json
from pathlib import Path

def run_command(command):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success: {command}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {command}")
        print(f"Error: {e.stderr}")
        return False, e.stderr

def install_chronulus():
    """Install Chronulus MCP via pip"""
    print("🔧 Installing Chronulus MCP...")
    success, output = run_command("pip install chronulus-mcp")
    if success:
        print("📦 Chronulus MCP installed successfully!")
    return success

def check_claude_config():
    """Check if Claude desktop config exists"""
    # Windows path
    config_path = Path(os.getenv('APPDATA', '')) / 'Claude' / 'claude_desktop_config.json'
    
    if config_path.exists():
        print(f"✅ Found Claude config at: {config_path}")
        return True, str(config_path)
    else:
        print(f"⚠️  Claude config not found at: {config_path}")
        print("💡 This is needed for Claude Desktop integration")
        return False, str(config_path)

def create_sample_config():
    """Create sample configuration file"""
    config_dir = Path(__file__).parent.parent / 'config'
    sample_config = {
        "mcpServers": {
            "chronulus": {
                "command": "uvx",
                "args": ["chronulus-mcp"],
                "env": {
                    "CHRONULUS_API_KEY": "your-api-key-here"
                }
            }
        }
    }
    
    sample_path = config_dir / 'sample_claude_config.json'
    with open(sample_path, 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print(f"📝 Created sample config at: {sample_path}")
    return sample_path

def main():
    """Main installation process"""
    print("🚀 Chronulus MCP Testing Setup")
    print("=" * 40)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    # Install Chronulus MCP
    if not install_chronulus():
        return False
    
    # Check Claude config
    config_exists, config_path = check_claude_config()
    
    # Create sample config
    sample_path = create_sample_config()
    
    print("\n✅ Installation Complete!")
    print("\n🔧 Next Steps:")
    print("1. Get Chronulus API key")
    print("2. Set CHRONULUS_API_KEY environment variable")
    
    if config_exists:
        print(f"3. Add Chronulus MCP to your Claude config: {config_path}")
    else:
        print("3. Install Claude Desktop and configure MCP servers")
    
    print(f"4. Use sample config as reference: {sample_path}")
    print("5. Run test scripts in ../tests/")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)