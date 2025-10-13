#!/usr/bin/env python3
"""
Test script to verify PR Manager setup
"""
import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check if required environment variables are set"""
    load_dotenv()
    
    required_vars = [
        'GITHUB_CLIENT_ID',
        'GITHUB_CLIENT_SECRET',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file with the required variables.")
        print("See SETUP.md for detailed instructions.")
        return False
    
    print("✅ All required environment variables are set")
    return True

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        'flask',
        'flask_cors',
        'authlib',
        'requests',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required Python packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease install them with: pip install -r requiremets.txt")
        return False
    
    print("✅ All required Python packages are installed")
    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        'app.py',
        'client/index.html',
        'client/app.js',
        'requiremets.txt'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ All required files are present")
    return True

def main():
    """Run all checks"""
    print("🔍 Checking PR Manager setup...\n")
    
    checks = [
        ("Files", check_files),
        ("Dependencies", check_dependencies),
        ("Environment", check_environment)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"Checking {check_name}...")
        if not check_func():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All checks passed! Your PR Manager is ready to run.")
        print("\nTo start the application:")
        print("   python app.py")
        print("\nThen open your browser to: http://localhost:5000")
    else:
        print("❌ Some checks failed. Please fix the issues above before running the application.")
        sys.exit(1)

if __name__ == "__main__":
    main()
