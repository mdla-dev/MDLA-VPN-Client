#!/usr/bin/env python3
"""Build script for MDLA Android"""
import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run command and handle errors"""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    # Check Python
    if sys.version_info < (3, 8):
        print("Error: Python 3.8+ required")
        return False
    
    # Check buildozer
    try:
        subprocess.run(["buildozer", "--version"], check=True, capture_output=True)
        print("✓ Buildozer found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Buildozer not found. Install with: pip install buildozer")
        return False
    
    # Check Cython
    try:
        import Cython
        print("✓ Cython found")
    except ImportError:
        print("Error: Cython not found. Install with: pip install cython")
        return False
    
    return True


def install_requirements():
    """Install Python requirements"""
    print("Installing requirements...")
    return run_command("pip install -r requirements.txt")


def build_debug():
    """Build debug APK"""
    print("Building debug APK...")
    return run_command("buildozer android debug")


def build_release():
    """Build release APK"""
    print("Building release APK...")
    return run_command("buildozer android release")


def clean():
    """Clean build artifacts"""
    print("Cleaning build artifacts...")
    
    # Remove buildozer directories
    for dir_name in [".buildozer", "bin"]:
        if Path(dir_name).exists():
            run_command(f"rm -rf {dir_name}")
    
    print("Clean completed")


def main():
    """Main build function"""
    if len(sys.argv) < 2:
        print("Usage: python build.py [debug|release|clean|deps]")
        print("  debug   - Build debug APK")
        print("  release - Build release APK") 
        print("  clean   - Clean build artifacts")
        print("  deps    - Install dependencies")
        return
    
    command = sys.argv[1]
    
    if command == "clean":
        clean()
        return
    
    if command == "deps":
        if not check_dependencies():
            sys.exit(1)
        if not install_requirements():
            sys.exit(1)
        print("Dependencies installed successfully")
        return
    
    # Check dependencies for build commands
    if not check_dependencies():
        print("Please install missing dependencies first")
        sys.exit(1)
    
    if command == "debug":
        if not build_debug():
            sys.exit(1)
        print("Debug APK built successfully!")
        print("Output: bin/mdlavpn-*-debug.apk")
    
    elif command == "release":
        if not build_release():
            sys.exit(1)
        print("Release APK built successfully!")
        print("Output: bin/mdlavpn-*-release.apk")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()