#!/usr/bin/env python3
"""
Setup Git Hooks for DataExploratoryProject

This script installs the pre-commit hook that automatically runs the
auto-discovery system when new components are added.
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess

def setup_git_hooks():
    """Setup git hooks for the project."""
    project_root = Path(".")
    git_hooks_dir = project_root / ".git" / "hooks"
    
    print("=== SETTING UP GIT HOOKS FOR DATAEXPLORATORYPROJECT ===\n")
    
    # Check if this is a git repository
    if not (project_root / ".git").exists():
        print("❌ Error: This is not a git repository.")
        print("Please initialize git first with: git init")
        return False
    
    # Create hooks directory if it doesn't exist
    git_hooks_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy pre-commit hook
    pre_commit_source = project_root / "pre_commit_hook.py"
    pre_commit_dest = git_hooks_dir / "pre-commit"
    
    if not pre_commit_source.exists():
        print("❌ Error: pre_commit_hook.py not found in project root.")
        return False
    
    try:
        # Copy the hook file
        shutil.copy2(pre_commit_source, pre_commit_dest)
        
        # Make it executable (Unix-like systems)
        if os.name != 'nt':  # Not Windows
            os.chmod(pre_commit_dest, 0o755)
        
        print(f"✅ Pre-commit hook installed: {pre_commit_dest}")
        
    except Exception as e:
        print(f"❌ Error installing pre-commit hook: {e}")
        return False
    
    # Verify auto-discovery system exists
    auto_discovery_script = project_root / "auto_discovery_system.py"
    if not auto_discovery_script.exists():
        print("❌ Warning: auto_discovery_system.py not found.")
        print("The pre-commit hook will not work without this script.")
        return False
    
    print(f"✅ Auto-discovery system found: {auto_discovery_script}")
    
    # Test the hook
    print("\n=== TESTING PRE-COMMIT HOOK ===")
    try:
        result = subprocess.run(
            [str(pre_commit_dest)],
            capture_output=True, text=True, cwd=project_root
        )
        
        if result.returncode == 0:
            print("✅ Pre-commit hook test successful")
            if result.stdout:
                print("Output:")
                for line in result.stdout.strip().split('\n'):
                    print(f"  {line}")
        else:
            print("⚠️  Pre-commit hook test completed with warnings")
            if result.stderr:
                print("Warnings:")
                for line in result.stderr.strip().split('\n'):
                    print(f"  {line}")
    
    except Exception as e:
        print(f"⚠️  Warning: Could not test pre-commit hook: {e}")
    
    print("\n=== GIT HOOKS SETUP COMPLETE ===")
    print("The pre-commit hook will now automatically:")
    print("1. Detect when new estimators or data generators are added")
    print("2. Run the auto-discovery system")
    print("3. Update benchmarking and example scripts")
    print("4. Stage the updated files for commit")
    
    print("\nTo manually run the auto-discovery system:")
    print("  python auto_discovery_system.py")
    
    print("\nTo test the pre-commit hook:")
    print("  .git/hooks/pre-commit")
    
    return True

def remove_git_hooks():
    """Remove git hooks."""
    project_root = Path(".")
    git_hooks_dir = project_root / ".git" / "hooks"
    pre_commit_hook = git_hooks_dir / "pre-commit"
    
    print("=== REMOVING GIT HOOKS ===\n")
    
    if pre_commit_hook.exists():
        try:
            pre_commit_hook.unlink()
            print("✅ Pre-commit hook removed")
        except Exception as e:
            print(f"❌ Error removing pre-commit hook: {e}")
            return False
    else:
        print("ℹ️  No pre-commit hook found to remove")
    
    return True

def main():
    """Main function."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "install" or command == "setup":
            success = setup_git_hooks()
            sys.exit(0 if success else 1)
        
        elif command == "remove" or command == "uninstall":
            success = remove_git_hooks()
            sys.exit(0 if success else 1)
        
        elif command == "help":
            print("Git Hooks Setup for DataExploratoryProject")
            print("\nUsage:")
            print("  python setup_git_hooks.py [install|remove|help]")
            print("\nCommands:")
            print("  install, setup  - Install the pre-commit hook")
            print("  remove, uninstall - Remove the pre-commit hook")
            print("  help           - Show this help message")
            print("\nThe pre-commit hook automatically:")
            print("- Detects new estimators and data generators")
            print("- Runs the auto-discovery system")
            print("- Updates benchmarking and example scripts")
            print("- Stages updated files for commit")
            sys.exit(0)
        
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python setup_git_hooks.py help' for usage information")
            sys.exit(1)
    
    else:
        # Default: install hooks
        success = setup_git_hooks()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

