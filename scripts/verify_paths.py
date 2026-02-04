#!/usr/bin/env python3
"""
Cross-platform path verification script.
Replaces: verify-path-clean.bat and verify-path-clean.sh
"""
import sys
import os
from pathlib import Path
import re


def check_path_issues(path: Path) -> list:
    """Check for common path issues."""
    issues = []
    path_str = str(path)
    
    # Check for spaces
    if ' ' in path_str:
        issues.append(f"Path contains spaces: {path_str}")
    
    # Check for special characters that might cause issues
    special_chars = ['&', '%', '$', '#', '@', '!', '(', ')', '[', ']', '{', '}']
    for char in special_chars:
        if char in path_str:
            issues.append(f"Path contains special character '{char}': {path_str}")
    
    # Check for very long paths (Windows limitation)
    if len(path_str) > 260 and sys.platform == 'win32':
        issues.append(f"Path exceeds Windows MAX_PATH (260 chars): {len(path_str)} chars")
    
    # Check for non-ASCII characters
    if not path_str.isascii():
        issues.append(f"Path contains non-ASCII characters: {path_str}")
    
    return issues


def verify_project_paths():
    """Verify all project paths are clean."""
    print("🔍 Verifying project paths...")
    
    all_issues = []
    
    # Check current working directory
    cwd = Path.cwd()
    print(f"\nCurrent directory: {cwd}")
    
    cwd_issues = check_path_issues(cwd)
    if cwd_issues:
        all_issues.extend(cwd_issues)
    
    # Check important project directories
    important_dirs = [
        'frontend',
        'backend',
        'services',
        'scripts',
        'docs'
    ]
    
    for dir_name in important_dirs:
        dir_path = cwd / dir_name
        if dir_path.exists():
            dir_issues = check_path_issues(dir_path)
            if dir_issues:
                all_issues.extend(dir_issues)
    
    # Report results
    if all_issues:
        print("\n✗ Path issues found:")
        for issue in all_issues:
            print(f"  - {issue}")
        print("\n⚠️  Recommendations:")
        print("  1. Move project to a path without spaces or special characters")
        print("  2. Use shorter path names")
        print("  3. Avoid non-ASCII characters in paths")
        return 1
    else:
        print("\n✓ All paths verified successfully")
        print("  No issues found with project paths")
        return 0


def main():
    """Main entry point."""
    print("=" * 60)
    print("Project Path Verifier")
    print("=" * 60)
    
    exit_code = verify_project_paths()
    
    print("=" * 60)
    if exit_code == 0:
        print("✓ Path verification complete!")
    else:
        print("✗ Path verification found issues")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
