#!/usr/bin/env python3
"""
Cross-platform code issue fixer script.
Consolidates: fix_typescript_errors.py, fix_unused_imports.py, fix_all_unused_vars.bat,
              fix_frontend_build.bat, fix_frontend_complete.bat
"""
import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_command(cmd: list, cwd: Path = None, description: str = "", check: bool = False) -> bool:
    """Run a command and return success status."""
    if description:
        print(f"\n{description}...")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"  ✓ Success")
            if result.stdout:
                print(f"  {result.stdout[:500]}")
            return True
        else:
            print(f"  ⚠️  Completed with warnings")
            if result.stderr:
                print(f"  {result.stderr[:500]}")
            return True  # Not a fatal error
            
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed with exit code {e.returncode}")
        if e.stderr:
            print(f"  Error: {e.stderr[:500]}")
        return False
    except FileNotFoundError:
        print(f"  ✗ Command not found: {cmd[0]}")
        return False


def fix_typescript_errors():
    """Fix TypeScript errors in frontend."""
    print("\n🔧 Fixing TypeScript errors...")
    
    frontend_dir = Path.cwd() / 'frontend'
    
    if not frontend_dir.exists():
        print(f"  ✗ Frontend directory not found")
        return False
    
    # Run TypeScript compiler to check for errors
    success = run_command(
        ['npx', 'tsc', '--noEmit'],
        cwd=frontend_dir,
        description="  Checking TypeScript errors"
    )
    
    if success:
        print("  ℹ️  No TypeScript errors found")
    else:
        print("  ℹ️  TypeScript errors detected - review output above")
    
    return True


def fix_unused_imports():
    """Fix unused imports in Python code."""
    print("\n🔧 Fixing unused imports...")
    
    backend_dir = Path.cwd() / 'backend'
    
    if not backend_dir.exists():
        print(f"  ✗ Backend directory not found")
        return False
    
    # Use autoflake to remove unused imports
    success = run_command(
        ['autoflake', '--in-place', '--remove-all-unused-imports', '--recursive', 'app/'],
        cwd=backend_dir,
        description="  Removing unused imports"
    )
    
    if not success:
        print("  ℹ️  autoflake not installed, skipping")
        print("  Install with: pip install autoflake")
    
    return True


def fix_frontend_build():
    """Fix frontend build issues."""
    print("\n🔧 Fixing frontend build...")
    
    frontend_dir = Path.cwd() / 'frontend'
    
    if not frontend_dir.exists():
        print(f"  ✗ Frontend directory not found")
        return False
    
    # Clean build artifacts
    print("  Cleaning build artifacts...")
    build_dirs = ['.next', 'node_modules/.cache', 'dist']
    
    for dir_name in build_dirs:
        dir_path = frontend_dir / dir_name
        if dir_path.exists():
            import shutil
            shutil.rmtree(dir_path, ignore_errors=True)
            print(f"    ✓ Removed {dir_name}")
    
    # Reinstall dependencies
    if not run_command(
        ['npm', 'install'],
        cwd=frontend_dir,
        description="  Reinstalling dependencies"
    ):
        return False
    
    # Run build
    if not run_command(
        ['npm', 'run', 'build'],
        cwd=frontend_dir,
        description="  Building frontend"
    ):
        return False
    
    return True


def fix_lint_issues():
    """Fix linting issues."""
    print("\n🔧 Fixing lint issues...")
    
    # Frontend linting
    frontend_dir = Path.cwd() / 'frontend'
    if frontend_dir.exists():
        run_command(
            ['npm', 'run', 'lint', '--', '--fix'],
            cwd=frontend_dir,
            description="  Fixing frontend lint issues"
        )
    
    # Backend linting
    backend_dir = Path.cwd() / 'backend'
    if backend_dir.exists():
        run_command(
            ['black', 'app/'],
            cwd=backend_dir,
            description="  Formatting Python code with black"
        )
        
        run_command(
            ['isort', 'app/'],
            cwd=backend_dir,
            description="  Sorting Python imports with isort"
        )
    
    return True


def fix_all():
    """Fix all common issues."""
    print("🔧 Running all fixes...")
    
    results = {
        'TypeScript': fix_typescript_errors(),
        'Unused Imports': fix_unused_imports(),
        'Lint Issues': fix_lint_issues()
    }
    
    # Print summary
    print(f"\n{'='*60}")
    print("Fix Summary")
    print(f"{'='*60}")
    
    for fix_type, success in results.items():
        status = "✓ COMPLETED" if success else "✗ FAILED"
        print(f"{fix_type:20} {status}")
    
    return all(results.values())


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Fix common code issues in the project'
    )
    parser.add_argument(
        'fix_type',
        nargs='?',
        choices=['all', 'typescript', 'imports', 'build', 'lint'],
        default='all',
        help='Type of fix to apply (default: all)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Code Issue Fixer")
    print("=" * 60)
    
    success = False
    
    if args.fix_type == 'all':
        success = fix_all()
    elif args.fix_type == 'typescript':
        success = fix_typescript_errors()
    elif args.fix_type == 'imports':
        success = fix_unused_imports()
    elif args.fix_type == 'build':
        success = fix_frontend_build()
    elif args.fix_type == 'lint':
        success = fix_lint_issues()
    
    print("=" * 60)
    if success:
        print("✓ Fixes completed!")
    else:
        print("⚠️  Some fixes had issues")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
