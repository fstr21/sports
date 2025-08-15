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

def git_pull():
    """Pull from main branch"""
    print("Pulling from main branch...")
    success, stdout, stderr = run_command("git pull origin main")
    if success:
        print("✅ Pull successful!")
        print(stdout)
    else:
        print("❌ Pull failed!")
        print(stderr)
    return success

def git_push():
    """Push to main branch"""
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
    
    # Push to main
    print("🚀 Pushing to main branch...")
    success, stdout, stderr = run_command("git push origin main")
    if success:
        print("✅ Push successful!")
        print(stdout)
    else:
        print("❌ Push failed!")
        print(stderr)
    
    return success

def main():
    print("🔧 Git Helper Tool")
    print("==================")
    
    while True:
        print("\nChoose an option:")
        print("1. 📥 Pull from main branch")
        print("2. 📤 Push to main branch")
        print("3. 📊 Check git status")
        print("4. ❌ Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            git_pull()
            print("\n✅ Operation completed. Press Enter to exit...")
            input()
            sys.exit(0)
        elif choice == "2":
            git_push()
            print("\n✅ Operation completed. Press Enter to exit...")
            input()
            sys.exit(0)
        elif choice == "3":
            success, stdout, stderr = run_command("git status")
            if success:
                print(stdout)
            else:
                print("❌ Failed to get git status!")
                print(stderr)
            print("\n✅ Status check completed. Press Enter to exit...")
            input()
            sys.exit(0)
        elif choice == "4":
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()
