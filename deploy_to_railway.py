#!/usr/bin/env python3
"""
Railway Deployment Helper

This script helps you prepare for Railway deployment.
"""

import os
import subprocess
import sys
from pathlib import Path

def check_git():
    """Check if git is available"""
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Git available: {result.stdout.strip()}")
            return True
        else:
            print("[ERROR] Git not working properly")
            return False
    except FileNotFoundError:
        print("[ERROR] Git not found. Please install Git from https://git-scm.com")
        return False

def check_files():
    """Check if required Railway files exist"""
    required_files = [
        "sports_http_server.py",
        "mcp_wrappers.py", 
        "requirements-railway.txt",
        "Procfile",
        "railway.json"
    ]
    
    print("\n[INFO] Checking required files...")
    all_good = True
    
    for file in required_files:
        if Path(file).exists():
            print(f"[OK] {file}")
        else:
            print(f"[MISSING] {file}")
            all_good = False
    
    return all_good

def setup_gitignore():
    """Set up .gitignore file"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment variables
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Local development
ngrok.exe
*.log
quick_test_local.py
install_ngrok.py
setup_http_server.py

# Temporary files
*.tmp
*.temp

# Railway specific
.railway/
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("[OK] Created .gitignore file")

def init_git_repo():
    """Initialize git repository if needed"""
    if Path('.git').exists():
        print("[OK] Git repository already exists")
        return True
    
    try:
        print("[INFO] Initializing git repository...")
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "branch", "-M", "main"], check=True, capture_output=True)
        print("[OK] Git repository initialized")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to initialize git: {e}")
        return False

def show_next_steps():
    """Show next steps for deployment"""
    print(f"\n" + "="*50)
    print("READY FOR RAILWAY DEPLOYMENT!")
    print("="*50)
    
    print(f"\nNEXT STEPS:")
    print(f"1. Create GitHub repository:")
    print(f"   - Go to https://github.com")
    print(f"   - Click 'New Repository'")
    print(f"   - Name: 'sports-mcp-server'")
    print(f"   - Make it Public")
    print(f"   - Don't initialize with README")
    
    print(f"\n2. Push your code to GitHub:")
    print(f"   git add .")
    print(f'   git commit -m "Initial commit: Sports HTTP Server"')
    print(f"   git remote add origin https://github.com/YOUR_USERNAME/sports-mcp-server.git")
    print(f"   git push -u origin main")
    
    print(f"\n3. Deploy to Railway:")
    print(f"   - Go to https://railway.app")
    print(f"   - Sign in with GitHub")
    print(f"   - Click 'New Project' > 'Deploy from GitHub repo'")
    print(f"   - Choose your repository")
    print(f"   - Add environment variable: SPORTS_API_KEY=89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ")
    
    print(f"\n4. Test your deployment:")
    print(f"   - Get your Railway URL from the dashboard")
    print(f"   - Visit: https://your-url.railway.app/health")
    
    print(f"\nFull guide: RAILWAY_DEPLOYMENT_GUIDE.md")
    print(f"Cost: ~$1-3/month on Railway free tier")

def main():
    print("Railway Deployment Helper")
    print("=" * 30)
    
    # Check git
    if not check_git():
        return
    
    # Check required files
    if not check_files():
        print("\n[ERROR] Missing required files. Run the HTTP server setup first.")
        return
    
    # Set up .gitignore
    setup_gitignore()
    
    # Initialize git repo
    if not init_git_repo():
        return
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main()