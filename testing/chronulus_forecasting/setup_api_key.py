#!/usr/bin/env python3
"""
Setup Chronulus API Key
Safely adds API key to .env.local file
"""
import os
from pathlib import Path

def setup_api_key():
    """Setup Chronulus API key in .env.local"""
    
    # Path to .env.local
    env_file = Path(__file__).parent.parent.parent / '.env.local'
    
    print("🔑 CHRONULUS API KEY SETUP")
    print("=" * 40)
    print(f"Target file: {env_file}")
    
    # Check if file exists
    if env_file.exists():
        print("✅ .env.local file exists")
        
        # Check if key already exists
        existing_key = None
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('CHRONULUS_API_KEY='):
                    existing_key = line.split('=', 1)[1].strip()
                    break
        
        if existing_key:
            print(f"⚠️  API key already exists: ...{existing_key[-4:] if len(existing_key) >= 4 else 'SHORT'}")
            overwrite = input("Overwrite existing key? (y/N): ").strip().lower()
            if overwrite != 'y':
                print("❌ Setup cancelled")
                return False
    else:
        print("📝 Creating new .env.local file")
    
    # Get API key
    api_key = input("\nEnter your Chronulus API key (starts with 25b23...): ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return False
    
    if not api_key.startswith('25b23'):
        print("⚠️  Warning: API key doesn't start with expected prefix '25b23'")
        proceed = input("Continue anyway? (y/N): ").strip().lower()
        if proceed != 'y':
            print("❌ Setup cancelled")
            return False
    
    try:
        # Read existing content
        existing_lines = []
        if env_file.exists():
            with open(env_file, 'r') as f:
                existing_lines = [line.rstrip() for line in f.readlines()]
        
        # Remove existing CHRONULUS_API_KEY line
        existing_lines = [line for line in existing_lines if not line.startswith('CHRONULUS_API_KEY=')]
        
        # Add new key
        existing_lines.append(f'CHRONULUS_API_KEY={api_key}')
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.write('\n'.join(existing_lines))
            f.write('\n')  # Ensure newline at end
        
        print(f"✅ API key saved successfully!")
        print(f"   File: {env_file}")
        print(f"   Key: ...{api_key[-4:] if len(api_key) >= 4 else 'SHORT'}")
        print(f"\n🚀 Ready to run manual tests:")
        print(f"   python manual_test.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving API key: {e}")
        return False

if __name__ == "__main__":
    success = setup_api_key()
    
    if success:
        print(f"\n💡 Next steps:")
        print(f"1. Run: python manual_test.py")
        print(f"2. Test with your Discord data")
        print(f"3. Compare predictions vs your current system")
    else:
        print(f"\n❌ Setup failed. Please try again.")