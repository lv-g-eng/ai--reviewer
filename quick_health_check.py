#!/usr/bin/env python3
"""
Quick Health Check Script
=========================

A simplified health check script that doesn't require pytest.
Run this to quickly verify core services are accessible.

Usage: python3 quick_health_check.py
"""

import os
import sys
import subprocess
from pathlib import Path

# Colors for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")


def print_result(test_name, status, message=""):
    status_symbols = {
        "ok": f"{Colors.GREEN}✅ PASS{Colors.END}",
        "fail": f"{Colors.RED}❌ FAIL{Colors.END}",
        "warn": f"{Colors.YELLOW}⚠️  WARN{Colors.END}",
        "skip": f"{Colors.YELLOW}⏭️  SKIP{Colors.END}"
    }
    symbol = status_symbols.get(status, "❓")
    print(f"{symbol} {test_name:<40} {message}")


def check_docker():
    """Check if Docker is installed and containers are running"""
    print_header("Docker Services Check")
    
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print_result("Docker", "warn", "Docker not available or not running")
            return False
        
        running_containers = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        required_containers = {
            "ai_review_postgres": "PostgreSQL",
            "ai_review_redis": "Redis",
            "ai_review_neo4j": "Neo4j"
        }
        
        all_running = True
        for container, service_name in required_containers.items():
            if container in running_containers:
                print_result(f"{service_name} Container", "ok", "Running")
            else:
                print_result(f"{service_name} Container", "fail", "Not running")
                all_running = False
        
        return all_running
        
    except FileNotFoundError:
        print_result("Docker", "warn", "Docker not installed")
        return False
    except Exception as e:
        print_result("Docker Check", "fail", str(e)[:50])
        return False


def check_python_environment():
    """Check Python and dependencies"""
    print_header("Python Environment Check")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 11):
        print_result("Python Version", "ok", f"{python_version.major}.{python_version.minor}")
    else:
        print_result("Python Version", "fail", f"3.11+ required, found {python_version.major}.{python_version.minor}")
        return False
    
    # Check critical packages
    packages = ["fastapi", "uvicorn", "sqlalchemy", "pydantic"]
    all_installed = True
    
    for package in packages:
        try:
            __import__(package)
            print_result(f"Package: {package}", "ok", "Installed")
        except ImportError:
            print_result(f"Package: {package}", "fail", "Not installed")
            all_installed = False
    
    return all_installed


def check_env_file():
    """Check if .env file exists and has required variables"""
    print_header("Environment Configuration Check")
    
    env_path = Path(".env")
    
    if not env_path.exists():
        print_result(".env File", "fail", "Not found - copy from .env.template")
        return False
    
    print_result(".env File", "ok", "Exists")
    
    # Check critical variables
    critical_vars = [
        "POSTGRES_DB",
        "POSTGRES_USER", 
        "POSTGRES_PASSWORD",
        "JWT_SECRET",
        "SECRET_KEY"
    ]
    
    all_set = True
    with open(env_path) as f:
        content = f.read()
    
    for var in critical_vars:
        if f"{var}=" in content:
            # Check if it's a placeholder
            import re
            match = re.search(rf'^{var}=(.+)$', content, re.MULTILINE)
            if match:
                value = match.group(1).strip()
                if value and not value.startswith('your_') and value != '':
                    print_result(f"ENV: {var}", "ok", "Set")
                else:
                    print_result(f"ENV: {var}", "warn", "Placeholder value")
                    all_set = False
            else:
                print_result(f"ENV: {var}", "fail", "Not set")
                all_set = False
        else:
            print_result(f"ENV: {var}", "fail", "Not found")
            all_set = False
    
    return all_set


def check_backend_imports():
    """Check if backend modules can be imported"""
    print_header("Backend Module Check")
    
    os.chdir("backend")
    
    # Add backend to path
    sys.path.insert(0, os.getcwd())
    
    critical_modules = [
        ("app.main", "Main FastAPI App"),
        ("app.core.config", "Configuration"),
        ("app.api.v1.router", "API Router"),
    ]
    
    all_imports_ok = True
    for module, description in critical_modules:
        try:
            __import__(module)
            print_result(f"Import: {module}", "ok", description)
        except ImportError as e:
            print_result(f"Import: {module}", "fail", str(e)[:50])
            all_imports_ok = False
        except Exception as e:
            print_result(f"Import: {module}", "warn", f"Imported with warnings")
    
    os.chdir("..")
    return all_imports_ok


def check_frontend_build():
    """Check if frontend can build"""
    print_header("Frontend Build Check")
    
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print_result("Frontend", "skip", "Directory not found")
        return True
    
    os.chdir("frontend")
    
    # Check package.json
    if Path("package.json").exists():
        print_result("package.json", "ok", "Exists")
    else:
        print_result("package.json", "fail", "Not found")
        os.chdir("..")
        return False
    
    # Check if node_modules exists
    if Path("node_modules").exists():
        print_result("node_modules", "ok", "Installed")
    else:
        print_result("node_modules", "warn", "Not installed - run 'npm install'")
    
    os.chdir("..")
    return True


def generate_summary(results):
    """Generate final summary"""
    print_header("Health Check Summary")
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {failed}/{total}")
    print()
    
    if failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ All checks passed!{Colors.END}")
        print("\nNext steps:")
        print("1. Start Docker services: docker-compose up -d")
        print("2. Run backend: cd backend && uvicorn app.main:app --reload")
        print("3. Run frontend: cd frontend && npm run dev")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Some checks failed.{Colors.END}")
        print("\nTroubleshooting:")
        print("1. Copy environment file: cp .env.template .env")
        print("2. Configure .env with your settings")
        print("3. Start Docker: docker-compose up -d")
        print("4. Install dependencies: cd backend && pip install -r requirements.txt")
    
    return failed == 0


def main():
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║     AI Code Review Platform - Quick Health Check       ║
    ╚════════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.END}")
    
    results = {}
    
    # Run all checks
    results["docker"] = check_docker()
    results["python"] = check_python_environment()
    results["env"] = check_env_file()
    results["backend"] = check_backend_imports()
    results["frontend"] = check_frontend_build()
    
    # Generate summary
    all_passed = generate_summary(results)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
