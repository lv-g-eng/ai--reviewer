#!/usr/bin/env python3
"""
Cross-platform frontend environment verification script.
Replaces: verify-frontend-env.sh and verify-frontend-env-enhanced.sh
"""
import sys
import os
from pathlib import Path
import subprocess


def check_file_exists(file_path: Path, description: str) -> bool:
    """Check if a file exists."""
    if file_path.exists():
        print(f"  ✓ {description}: {file_path}")
        return True
    else:
        print(f"  ✗ {description} not found: {file_path}")
        return False


def check_env_variable(var_name: str, env_file: Path) -> bool:
    """Check if environment variable is set in .env file."""
    if not env_file.exists():
        return False
    
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            if f"{var_name}=" in content:
                # Check if it has a value (not empty)
                for line in content.split('\n'):
                    if line.startswith(f"{var_name}="):
                        value = line.split('=', 1)[1].strip()
                        if value and not value.startswith('#'):
                            return True
        return False
    except Exception as e:
        print(f"  ⚠️  Error reading {env_file}: {e}")
        return False


def verify_frontend_environment():
    """Verify frontend environment setup."""
    print("🔍 Verifying frontend environment...")
    
    frontend_dir = Path.cwd() / 'frontend'
    
    if not frontend_dir.exists():
        print(f"\n✗ Frontend directory not found: {frontend_dir}")
        print("  Are you running this from the project root?")
        return 1
    
    issues = []
    
    # Check essential files
    print("\n📁 Checking essential files:")
    essential_files = [
        (frontend_dir / 'package.json', 'package.json'),
        (frontend_dir / 'next.config.mjs', 'Next.js config'),
        (frontend_dir / 'tsconfig.json', 'TypeScript config'),
    ]
    
    for file_path, description in essential_files:
        if not check_file_exists(file_path, description):
            issues.append(f"Missing {description}")
    
    # Check environment file
    print("\n🔐 Checking environment configuration:")
    env_local = frontend_dir / '.env.local'
    env_example = frontend_dir / '.env.example'
    
    if not env_local.exists():
        print(f"  ✗ .env.local not found")
        if env_example.exists():
            print(f"  ℹ️  Copy .env.example to .env.local:")
            print(f"     cp {env_example} {env_local}")
        issues.append("Missing .env.local")
    else:
        print(f"  ✓ .env.local exists")
        
        # Check required environment variables
        required_vars = [
            'NEXTAUTH_URL',
            'NEXTAUTH_SECRET',
            'NEXT_PUBLIC_API_URL',
            'BACKEND_URL'
        ]
        
        print("\n  Checking required variables:")
        for var in required_vars:
            if check_env_variable(var, env_local):
                print(f"    ✓ {var} is set")
            else:
                print(f"    ✗ {var} is missing or empty")
                issues.append(f"Missing or empty {var}")
    
    # Check node_modules
    print("\n📦 Checking dependencies:")
    node_modules = frontend_dir / 'node_modules'
    if node_modules.exists():
        print(f"  ✓ node_modules exists")
    else:
        print(f"  ✗ node_modules not found")
        print(f"  ℹ️  Run: cd frontend && npm install")
        issues.append("Dependencies not installed")
    
    # Check if npm is available
    print("\n🔧 Checking tools:")
    try:
        npm_version = subprocess.run(
            ['npm', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"  ✓ npm version: {npm_version.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"  ✗ npm not found")
        issues.append("npm not installed")
    
    try:
        node_version = subprocess.run(
            ['node', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"  ✓ Node.js version: {node_version.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"  ✗ Node.js not found")
        issues.append("Node.js not installed")
    
    # Report results
    if issues:
        print("\n✗ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n📝 Next steps:")
        print("  1. Copy .env.example to .env.local if missing")
        print("  2. Fill in all required environment variables")
        print("  3. Run: cd frontend && npm install")
        print("  4. Run this script again to verify")
        return 1
    else:
        print("\n✓ Frontend environment verified successfully")
        print("  All checks passed!")
        print("\n🚀 Ready to start:")
        print("  cd frontend && npm run dev")
        return 0


def main():
    """Main entry point."""
    print("=" * 60)
    print("Frontend Environment Verifier")
    print("=" * 60)
    
    exit_code = verify_frontend_environment()
    
    print("=" * 60)
    if exit_code == 0:
        print("✓ Verification complete!")
    else:
        print("✗ Verification found issues")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
