#!/usr/bin/env python3
import subprocess
import sys

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def git_status():
    """Check git status"""
    success, stdout, stderr = run_command("git status --porcelain")
    if success:
        return stdout.strip() != ""
    return False

def git_pull(branch="main"):
    """Pull from specified branch"""
    print(f"Pulling from {branch} branch...")
    success, stdout, stderr = run_command(f"git pull origin {branch}")
    if success:
        print("✅ Pull successful!")
        print(stdout)
    else:
        print("❌ Pull failed!")
        print(stderr)
    return success

def git_push(branch="main"):
    """Push to specified branch"""
    # Check if there are changes to commit
    has_changes = git_status()
    
    if has_changes:
        print("📝 Changes detected. Adding and committing files...")
        
        # Add all changes
        success, stdout, stderr = run_command("git add .")
        if not success:
            print("❌ Failed to add files!")
            print(stderr)
            return False
        
        # Commit with default message
        commit_msg = "Update workspace"
        success, stdout, stderr = run_command(f'git commit -m "{commit_msg}"')
        if not success:
            print("❌ Failed to commit changes!")
            print(stderr)
            return False
        
        print(f"✅ Changes committed with message: '{commit_msg}'")
    
    # Push to specified branch
    print(f"🚀 Pushing to {branch} branch...")
    success, stdout, stderr = run_command(f"git push origin {branch}")
    if success:
        print("✅ Push successful!")
        print(stdout)
    else:
        print("❌ Push failed!")
        print(stderr)
    
    return success

def promote_to_production():
    """Promote main branch to production-stable with manual confirmation"""
    print("🚨 PRODUCTION DEPLOYMENT")
    print("=" * 40)
    print("This will update production-stable branch with current main branch.")
    print("⚠️  This affects your live Discord bot and MCP servers!")
    print()
    
    # Show current branch status
    success, stdout, stderr = run_command("git branch --show-current")
    if success:
        current_branch = stdout.strip()
        print(f"Current branch: {current_branch}")
    
    # Show what will be deployed
    success, stdout, stderr = run_command("git log --oneline -5")
    if success:
        print("\nRecent commits on main:")
        print(stdout)
    
    print("\n" + "="*40)
    confirmation = input("Type 'DEPLOY TO PRODUCTION' to confirm: ").strip()
    
    if confirmation != "DEPLOY TO PRODUCTION":
        print("❌ Deployment cancelled!")
        return False
    
    print("\n🚀 Starting production deployment...")
    
    # Switch to production-stable branch
    success, stdout, stderr = run_command("git checkout production-stable")
    if not success:
        print("❌ Failed to switch to production-stable!")
        print(stderr)
        return False
    
    # Merge main into production-stable
    success, stdout, stderr = run_command("git merge main")
    if not success:
        print("❌ Failed to merge main into production-stable!")
        print(stderr)
        return False
    
    # Push to remote
    success, stdout, stderr = run_command("git push origin production-stable")
    if not success:
        print("❌ Failed to push production-stable!")
        print(stderr)
        return False
    
    # Switch back to main
    success, stdout, stderr = run_command("git checkout main")
    
    print("✅ PRODUCTION DEPLOYMENT SUCCESSFUL!")
    print("🎯 production-stable branch updated with latest main")
    return True

def main():
    print("🔧 Git Helper Tool")
    print("==================")
    
    while True:
        print("\nChoose an option:")
        print("1. 📥 Pull from main branch")
        print("2. 📤 Push to main branch") 
        print("3. 📥 Pull from production-stable")
        print("4. 🚨 DEPLOY to production-stable (with confirmation)")
        print("5. 📊 Check git status")
        print("6. ❌ Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            git_pull("main")
            print("\n✅ Operation completed. Press Enter to exit...")
            input()
            sys.exit(0)
        elif choice == "2":
            git_push("main")
            print("\n✅ Operation completed. Press Enter to exit...")
            input()
            sys.exit(0)
        elif choice == "3":
            git_pull("production-stable")
            print("\n✅ Operation completed. Press Enter to exit...")
            input()
            sys.exit(0)
        elif choice == "4":
            promote_to_production()
            print("\n✅ Operation completed. Press Enter to exit...")
            input()
            sys.exit(0)
        elif choice == "5":
            success, stdout, stderr = run_command("git status")
            if success:
                print(stdout)
            else:
                print("❌ Failed to get git status!")
                print(stderr)
            print("\n✅ Status check completed. Press Enter to exit...")
            input()
            sys.exit(0)
        elif choice == "6":
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    main()
