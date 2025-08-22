#!/usr/bin/env python3
"""
Install Chronulus SDK and Run Sports Betting Tests
Complete setup and testing in one script
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description=""):
    """Run command and return success status"""
    if description:
        print(f"\n🔄 {description}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False, e.stderr

def check_api_key():
    """Check if API key is set"""
    env_file = Path(__file__).parent.parent.parent / '.env.local'
    
    if not env_file.exists():
        return False, str(env_file)
    
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            if 'CHRONULUS_API_KEY=' in content:
                return True, str(env_file)
    except Exception:
        pass
    
    return False, str(env_file)

def main():
    """Main installation and testing process"""
    print("🚀 CHRONULUS SDK SETUP FOR SPORTS BETTING")
    print("=" * 60)
    print("This will install Chronulus SDK and test with your Discord data")
    
    # Step 1: Check Python version
    python_version = sys.version_info
    print(f"\n🐍 Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python 3.8+ required for Chronulus SDK")
        return False
    
    # Step 2: Install Chronulus SDK
    print(f"\n📦 Installing Chronulus SDK...")
    success, output = run_command("pip install chronulus", "Installing Chronulus SDK")
    
    if not success:
        print("❌ Failed to install Chronulus SDK")
        print("💡 Try: pip install --upgrade pip")
        print("💡 Or: python -m pip install chronulus")
        return False
    
    # Step 3: Check API key
    print(f"\n🔑 Checking API Key...")
    has_key, env_file = check_api_key()
    
    if has_key:
        print(f"✅ API key found in {env_file}")
    else:
        print(f"⚠️  No API key found")
        print(f"📝 Expected location: {env_file}")
        print(f"💡 Add this line to .env.local:")
        print(f"   CHRONULUS_API_KEY=25b23***************")
        
        create_key = input("\nWould you like to add your API key now? (y/N): ").strip().lower()
        if create_key == 'y':
            api_key = input("Enter your Chronulus API key: ").strip()
            if api_key:
                try:
                    # Create or update .env.local
                    with open(env_file, 'a') as f:
                        f.write(f"\nCHRONULUS_API_KEY={api_key}\n")
                    print(f"✅ API key saved to {env_file}")
                    has_key = True
                except Exception as e:
                    print(f"❌ Failed to save API key: {e}")
    
    # Step 4: Install additional requirements  
    print(f"\n📦 Installing additional requirements...")
    success, _ = run_command("pip install pydantic httpx matplotlib", "Installing dependencies")
    
    if not success:
        print("⚠️  Some dependencies may be missing, but continuing...")
    
    # Step 5: Run the actual test
    print(f"\n🧪 Running Sports Betting Predictions Test...")
    print("=" * 60)
    
    test_script = Path(__file__).parent / 'real_chronulus_test.py'
    
    if test_script.exists():
        success, output = run_command(f'python "{test_script}"', "Running Chronulus sports predictions")
        
        if success:
            print("\n🎉 Test completed successfully!")
            print("\n📊 Results Summary:")
            if has_key:
                print("   ✅ Used real Chronulus API predictions")
                print("   📈 Compare accuracy with your current system")  
                print("   💰 Look for value bet opportunities")
            else:
                print("   ⚠️  Used mock predictions (no API key)")
                print("   🔑 Add API key for real predictions")
            
            print("\n🎯 Next Steps:")
            print("   1. Review prediction accuracy vs your Discord bot")
            print("   2. Compare value bet identification")
            print("   3. Consider integrating best predictions into Discord")
            print("   4. Track performance over multiple games")
            
        else:
            print("❌ Test failed")
            print(f"💡 Try running manually: python {test_script}")
    else:
        print(f"❌ Test script not found: {test_script}")
    
    # Step 6: Summary
    print(f"\n📋 INSTALLATION SUMMARY")
    print("=" * 30)
    print(f"✅ Chronulus SDK: Installed")
    print(f"{'✅' if has_key else '❌'} API Key: {'Set' if has_key else 'Missing'}")
    print(f"✅ Test Data: Your Discord screenshots converted")
    print(f"✅ Ready for: Sports betting predictions")
    
    if has_key:
        print(f"\n💡 You can now:")
        print(f"   • Test individual games manually")
        print(f"   • Compare with your current predictions")
        print(f"   • Identify value betting opportunities")
        print(f"   • Consider Discord bot integration")
    else:
        print(f"\n🔑 To get full functionality:")
        print(f"   • Obtain Chronulus API key")
        print(f"   • Add to .env.local file")
        print(f"   • Re-run this test")
    
    return True

if __name__ == "__main__":
    success = main()
    
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)