#!/usr/bin/env python3
"""
Cross-platform test runner script.
Replaces: run-integration-tests.bat and run-integration-tests.sh
"""
import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_command(cmd: list, cwd: Path = None, description: str = "") -> bool:
    """Run a command and return success status."""
    if description:
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            text=True
        )
        print(f"✓ {description or 'Command'} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description or 'Command'} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"✗ Command not found: {cmd[0]}")
        return False


def run_frontend_tests():
    """Run frontend tests."""
    frontend_dir = Path.cwd() / 'frontend'
    
    if not frontend_dir.exists():
        print(f"✗ Frontend directory not found: {frontend_dir}")
        return False
    
    return run_command(
        ['npm', 'test'],
        cwd=frontend_dir,
        description="Frontend Tests"
    )


def run_backend_tests():
    """Run backend tests."""
    backend_dir = Path.cwd() / 'backend'
    
    if not backend_dir.exists():
        print(f"✗ Backend directory not found: {backend_dir}")
        return False
    
    return run_command(
        ['pytest', '-v'],
        cwd=backend_dir,
        description="Backend Tests"
    )


def run_api_gateway_tests():
    """Run API Gateway tests."""
    api_gateway_dir = Path.cwd() / 'services' / 'api-gateway'
    
    if not api_gateway_dir.exists():
        print(f"✗ API Gateway directory not found: {api_gateway_dir}")
        return False
    
    return run_command(
        ['npm', 'test'],
        cwd=api_gateway_dir,
        description="API Gateway Tests (409 tests)"
    )


def run_integration_tests():
    """Run integration tests."""
    tests_dir = Path.cwd() / 'tests' / 'integration'
    
    if not tests_dir.exists():
        print(f"ℹ️  Integration tests directory not found: {tests_dir}")
        return True  # Not an error if integration tests don't exist yet
    
    return run_command(
        ['pytest', '-v', '--tb=short'],
        cwd=tests_dir,
        description="Integration Tests"
    )


def run_all_tests():
    """Run all tests."""
    results = {
        'Frontend': run_frontend_tests(),
        'Backend': run_backend_tests(),
        'API Gateway': run_api_gateway_tests(),
        'Integration': run_integration_tests()
    }
    
    # Print summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    
    for test_type, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_type:20} {status}")
    
    all_passed = all(results.values())
    
    print(f"{'='*60}")
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    
    return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run tests for the AI Code Review Platform'
    )
    parser.add_argument(
        'test_type',
        nargs='?',
        choices=['all', 'frontend', 'backend', 'api-gateway', 'integration'],
        default='all',
        help='Type of tests to run (default: all)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("AI Code Review Platform - Test Runner")
    print("=" * 60)
    
    success = False
    
    if args.test_type == 'all':
        success = run_all_tests()
    elif args.test_type == 'frontend':
        success = run_frontend_tests()
    elif args.test_type == 'backend':
        success = run_backend_tests()
    elif args.test_type == 'api-gateway':
        success = run_api_gateway_tests()
    elif args.test_type == 'integration':
        success = run_integration_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
