#!/usr/bin/env python3
"""
Verify API documentation setup.

This script verifies that:
1. Swagger UI is accessible at /docs
2. ReDoc is accessible at /redoc
3. OpenAPI spec includes authentication examples
4. Security schemes are properly configured

Usage:
    python scripts/verify_api_documentation.py [--url URL]

Requirements:
    - Backend server must be running
    - requests library must be installed
"""
import argparse
import sys
import requests
from typing import Dict, Any, List


def check_endpoint(url: str, endpoint: str, expected_content: List[str]) -> bool:
    """
    Check if an endpoint is accessible and contains expected content.
    
    Args:
        url: Base URL of the API
        endpoint: Endpoint path to check
        expected_content: List of strings that should be in the response
    
    Returns:
        True if all checks pass, False otherwise
    """
    full_url = f"{url}{endpoint}"
    print(f"\n🔍 Checking {full_url}...")
    
    try:
        response = requests.get(full_url, timeout=10)
        
        if response.status_code != 200:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            return False
        
        print(f"   ✅ Accessible (HTTP {response.status_code})")
        
        # Check content
        content = response.text.lower()
        missing_content = []
        
        for expected in expected_content:
            if expected.lower() not in content:
                missing_content.append(expected)
        
        if missing_content:
            print(f"   ⚠️  Missing expected content:")
            for item in missing_content:
                print(f"      - {item}")
            return False
        
        print(f"   ✅ Contains all expected content")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False


def check_openapi_spec(url: str) -> bool:
    """
    Check OpenAPI specification for completeness.
    
    Args:
        url: Base URL of the API
    
    Returns:
        True if all checks pass, False otherwise
    """
    spec_url = f"{url}/api/v1/openapi.json"
    print(f"\n🔍 Checking OpenAPI spec at {spec_url}...")
    
    try:
        response = requests.get(spec_url, timeout=10)
        
        if response.status_code != 200:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            return False
        
        spec = response.json()
        print(f"   ✅ OpenAPI spec accessible")
        
        # Check basic structure
        checks_passed = True
        
        # Check info section
        if "info" not in spec:
            print("   ❌ Missing 'info' section")
            checks_passed = False
        else:
            info = spec["info"]
            if "title" in info:
                print(f"   ✅ Title: {info['title']}")
            else:
                print("   ❌ Missing title")
                checks_passed = False
            
            if "version" in info:
                print(f"   ✅ Version: {info['version']}")
            else:
                print("   ❌ Missing version")
                checks_passed = False
            
            if "description" in info and info["description"]:
                desc = info["description"]
                print(f"   ✅ Description: {len(desc)} characters")
                
                # Check for authentication documentation
                auth_keywords = ["authentication", "bearer", "authorization", "jwt", "token"]
                found_keywords = [kw for kw in auth_keywords if kw.lower() in desc.lower()]
                
                if found_keywords:
                    print(f"   ✅ Authentication documented (found: {', '.join(found_keywords)})")
                else:
                    print("   ⚠️  Authentication documentation may be incomplete")
                
                # Check for examples
                if "curl" in desc.lower() or "example" in desc.lower():
                    print("   ✅ Includes examples")
                else:
                    print("   ⚠️  No examples found")
                
                # Check for Swagger UI instructions
                if "swagger" in desc.lower() and "authorize" in desc.lower():
                    print("   ✅ Includes Swagger UI usage instructions")
                else:
                    print("   ⚠️  Swagger UI instructions not found")
            else:
                print("   ❌ Missing or empty description")
                checks_passed = False
        
        # Check security schemes
        if "components" in spec and "securitySchemes" in spec["components"]:
            schemes = spec["components"]["securitySchemes"]
            print(f"   ✅ Security schemes defined: {', '.join(schemes.keys())}")
            
            if "HTTPBearer" in schemes:
                bearer = schemes["HTTPBearer"]
                if bearer.get("type") == "http" and bearer.get("scheme") == "bearer":
                    print("   ✅ HTTPBearer properly configured")
                else:
                    print("   ⚠️  HTTPBearer configuration may be incorrect")
                    checks_passed = False
        else:
            print("   ❌ No security schemes defined")
            checks_passed = False
        
        # Check paths
        if "paths" in spec:
            path_count = len(spec["paths"])
            print(f"   ✅ Endpoints documented: {path_count}")
            
            # Count protected endpoints
            protected_count = 0
            for path, methods in spec["paths"].items():
                for method, details in methods.items():
                    if "security" in details:
                        protected_count += 1
            
            print(f"   ✅ Protected endpoints: {protected_count}")
        else:
            print("   ❌ No paths defined")
            checks_passed = False
        
        # Check tags
        if "tags" in spec:
            tag_count = len(spec["tags"])
            print(f"   ✅ Tags defined: {tag_count}")
        else:
            print("   ⚠️  No tags defined")
        
        # Check contact info
        if "contact" in spec.get("info", {}):
            contact = spec["info"]["contact"]
            if "name" in contact and "email" in contact:
                print(f"   ✅ Contact info: {contact['name']} ({contact['email']})")
            else:
                print("   ⚠️  Incomplete contact info")
        else:
            print("   ⚠️  No contact info")
        
        # Check license
        if "license" in spec.get("info", {}):
            license_info = spec["info"]["license"]
            if "name" in license_info:
                print(f"   ✅ License: {license_info['name']}")
            else:
                print("   ⚠️  Incomplete license info")
        else:
            print("   ⚠️  No license info")
        
        return checks_passed
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error parsing spec: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify API documentation setup"
    )
    parser.add_argument(
        '--url',
        type=str,
        default='http://localhost:8000',
        help='Base URL of the API (default: http://localhost:8000)'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("API Documentation Verification")
    print("=" * 70)
    print(f"\nTarget URL: {args.url}")
    
    all_checks_passed = True
    
    # Check Swagger UI
    swagger_checks = check_endpoint(
        args.url,
        "/docs",
        ["swagger", "openapi"]
    )
    all_checks_passed = all_checks_passed and swagger_checks
    
    # Check ReDoc
    redoc_checks = check_endpoint(
        args.url,
        "/redoc",
        ["redoc", "openapi"]
    )
    all_checks_passed = all_checks_passed and redoc_checks
    
    # Check OpenAPI spec
    spec_checks = check_openapi_spec(args.url)
    all_checks_passed = all_checks_passed and spec_checks
    
    # Summary
    print("\n" + "=" * 70)
    if all_checks_passed:
        print("✅ All checks passed!")
        print("\n📖 Documentation is accessible at:")
        print(f"   Swagger UI: {args.url}/docs")
        print(f"   ReDoc:      {args.url}/redoc")
        print(f"   OpenAPI:    {args.url}/api/v1/openapi.json")
        print("\n💡 To use authentication in Swagger UI:")
        print("   1. Click the 'Authorize' button")
        print("   2. Enter your JWT token (get it from /api/v1/auth/login)")
        print("   3. Click 'Authorize' to apply")
        return 0
    else:
        print("❌ Some checks failed")
        print("\n⚠️  Please ensure:")
        print("   1. The backend server is running")
        print("   2. The server is accessible at the specified URL")
        print("   3. All required configuration is in place")
        return 1


if __name__ == '__main__':
    sys.exit(main())
