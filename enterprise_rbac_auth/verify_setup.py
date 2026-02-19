"""
Verification script for Enterprise RBAC Authentication System setup.
Run this script to verify that all dependencies and configurations are properly set up.
"""
import sys
import os


def check_dependencies():
    """Check if all required dependencies are installed."""
    print("Checking dependencies...")
    dependencies = [
        ("fastapi", "FastAPI"),
        ("jwt", "PyJWT"),
        ("bcrypt", "bcrypt"),
        ("sqlalchemy", "SQLAlchemy"),
        ("hypothesis", "Hypothesis"),
        ("pytest", "pytest"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("pydantic_settings", "pydantic-settings"),
    ]
    
    missing = []
    for module, package in dependencies:
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    return len(missing) == 0, missing


def check_directory_structure():
    """Check if all required directories exist."""
    print("\nChecking directory structure...")
    required_dirs = ["models", "services", "middleware", "api", "tests"]
    
    missing = []
    for directory in required_dirs:
        if os.path.isdir(directory):
            print(f"  ✓ {directory}/")
        else:
            print(f"  ✗ {directory}/ - MISSING")
            missing.append(directory)
    
    return len(missing) == 0, missing


def check_configuration():
    """Check if configuration is properly set up."""
    print("\nChecking configuration...")
    try:
        from config import settings
        print(f"  ✓ Configuration loaded")
        print(f"    - App Name: {settings.app_name}")
        print(f"    - Version: {settings.app_version}")
        print(f"    - JWT Algorithm: {settings.jwt_algorithm}")
        print(f"    - Token Expiry: {settings.jwt_access_token_expire_minutes} minutes")
        print(f"    - Database: {settings.database_url}")
        
        # Check if using default secret key
        if settings.jwt_secret_key == "dev-secret-key-change-in-production":
            print(f"  ⚠ WARNING: Using default JWT secret key (change in production!)")
        
        return True, []
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False, [str(e)]


def check_files():
    """Check if all required files exist."""
    print("\nChecking required files...")
    required_files = [
        "config.py",
        "main.py",
        "requirements.txt",
        "pytest.ini",
        ".env.example",
        ".gitignore",
        "README.md",
    ]
    
    missing = []
    for file in required_files:
        if os.path.isfile(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            missing.append(file)
    
    return len(missing) == 0, missing


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Enterprise RBAC Authentication System - Setup Verification")
    print("=" * 60)
    
    all_checks_passed = True
    
    # Run all checks
    deps_ok, missing_deps = check_dependencies()
    dirs_ok, missing_dirs = check_directory_structure()
    config_ok, config_errors = check_configuration()
    files_ok, missing_files = check_files()
    
    all_checks_passed = deps_ok and dirs_ok and config_ok and files_ok
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    if all_checks_passed:
        print("✓ All checks passed! Setup is complete.")
        print("\nNext steps:")
        print("  1. Update JWT_SECRET_KEY in .env for production")
        print("  2. Run 'pytest' to verify tests work")
        print("  3. Run 'python main.py' to start the application")
        return 0
    else:
        print("✗ Some checks failed. Please review the errors above.")
        if missing_deps:
            print(f"\nMissing dependencies: {', '.join(missing_deps)}")
            print("Run: pip install -r requirements.txt")
        if missing_dirs:
            print(f"\nMissing directories: {', '.join(missing_dirs)}")
        if missing_files:
            print(f"\nMissing files: {', '.join(missing_files)}")
        if config_errors:
            print(f"\nConfiguration errors: {', '.join(config_errors)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
