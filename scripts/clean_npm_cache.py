#!/usr/bin/env python3
"""
Cross-platform NPM cache cleaning script.
Replaces: clean-npm-cache.bat and clean-npm-cache.sh
"""
import subprocess
import sys
import os
from pathlib import Path


def clean_npm_cache():
    """Clean NPM cache on any platform."""
    print("🧹 Cleaning NPM cache...")
    
    try:
        # Clean npm cache
        result = subprocess.run(
            ["npm", "cache", "clean", "--force"],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✓ NPM cache cleaned successfully")
        
        # Show cache location
        cache_result = subprocess.run(
            ["npm", "config", "get", "cache"],
            capture_output=True,
            text=True
        )
        
        if cache_result.returncode == 0:
            cache_path = cache_result.stdout.strip()
            print(f"  Cache location: {cache_path}")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error cleaning NPM cache: {e}")
        if e.stderr:
            print(f"  Details: {e.stderr}")
        return 1
    except FileNotFoundError:
        print("✗ Error: npm command not found")
        print("  Please install Node.js and npm first")
        return 1


def main():
    """Main entry point."""
    print("=" * 50)
    print("NPM Cache Cleaner")
    print("=" * 50)
    
    exit_code = clean_npm_cache()
    
    print("=" * 50)
    if exit_code == 0:
        print("✓ Cache cleaning complete!")
    else:
        print("✗ Cache cleaning failed")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
