#!/usr/bin/env python3
"""
Deployment Preparation Script for Piano Practice App
Ensures all files are ready for Render deployment
"""

import os
import subprocess

def check_and_create_exports_dir():
    """Ensure exports directory exists with .gitkeep."""
    if not os.path.exists('exports'):
        os.makedirs('exports')
        print("✅ Created exports/ directory")
    
    gitkeep_path = 'exports/.gitkeep'
    if not os.path.exists(gitkeep_path):
        with open(gitkeep_path, 'w') as f:
            f.write('')
        print("✅ Created exports/.gitkeep")

def check_required_files():
    """Check if all required files exist."""
    required_files = [
        'app.py',
        'music_utils.py', 
        'requirements.txt',
        'render.yaml',
        '.gitignore',
        'templates/index.html',
        'templates/key_practice.html',
        'templates/sight_reading.html',
        'static/style.css',
        'static/script.js'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files present")
        return True

def check_git_status():
    """Check if git is initialized and has commits."""
    try:
        # Check if git is initialized
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Git not initialized. Run: git init")
            return False
        
        # Check if there are any commits
        result = subprocess.run(['git', 'log', '--oneline', '-1'], capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️  No commits yet. You'll need to commit your files.")
            return False
        
        # Check if there are uncommitted changes
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.stdout.strip():
            print("⚠️  You have uncommitted changes. Consider committing them.")
        
        print("✅ Git repository ready")
        return True
        
    except FileNotFoundError:
        print("❌ Git not installed or not in PATH")
        return False

def test_app_locally():
    """Test if the app can start locally."""
    try:
        print("🧪 Testing app startup...")
        # Import the app to check for syntax errors
        import app
        print("✅ App imports successfully")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def main():
    print("🎹 Piano Practice App - Deployment Preparation")
    print("=" * 50)
    
    # Run all checks
    checks = [
        ("Creating exports directory", check_and_create_exports_dir),
        ("Checking required files", check_required_files),
        ("Testing app locally", test_app_locally),
        ("Checking git status", check_git_status),
    ]
    
    all_passed = True
    for description, check_func in checks:
        print(f"\n{description}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 Ready for deployment!")
        print("\nNext steps:")
        print("1. Push to GitHub: git add . && git commit -m 'Ready for deployment' && git push")
        print("2. Go to render.com and deploy from your GitHub repository")
        print("3. Follow the Render Deployment Guide")
    else:
        print("❌ Please fix the issues above before deploying")
        print("\nCommon fixes:")
        print("- Install missing dependencies: pip install -r requirements.txt")
        print("- Initialize git: git init")
        print("- Add files to git: git add .")
        print("- Make initial commit: git commit -m 'Initial commit'")

if __name__ == "__main__":
    main()