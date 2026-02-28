#!/usr/bin/env python3
"""
Generate OpenAPI specification from FastAPI application.

This script generates the OpenAPI specification in JSON and YAML formats,
validates it, and provides a summary of documented endpoints.

Usage:
    python scripts/generate_openapi_spec.py [--output-dir OUTPUT_DIR] [--validate]

Requirements:
    - FastAPI application must be importable
    - All endpoints should have proper documentation
"""
import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List
import yaml

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.core.config import settings


def generate_openapi_spec() -> Dict[str, Any]:
    """Generate OpenAPI specification from FastAPI app."""
    return app.openapi()


def save_spec_json(spec: Dict[str, Any], output_path: Path) -> None:
    """Save OpenAPI spec as JSON."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved JSON spec to: {output_path}")


def save_spec_yaml(spec: Dict[str, Any], output_path: Path) -> None:
    """Save OpenAPI spec as YAML."""
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(spec, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"✅ Saved YAML spec to: {output_path}")


def validate_spec(spec: Dict[str, Any]) -> List[str]:
    """
    Validate OpenAPI specification for completeness.
    
    Returns list of validation warnings/errors.
    """
    issues = []
    
    # Check basic structure
    if 'info' not in spec:
        issues.append("❌ Missing 'info' section")
    else:
        info = spec['info']
        if 'title' not in info:
            issues.append("❌ Missing API title")
        if 'version' not in info:
            issues.append("❌ Missing API version")
        if 'description' not in info or not info['description']:
            issues.append("⚠️  Missing or empty API description")
    
    # Check paths
    if 'paths' not in spec or not spec['paths']:
        issues.append("❌ No API paths defined")
        return issues
    
    paths = spec['paths']
    total_endpoints = 0
    undocumented_endpoints = []
    missing_auth = []
    missing_responses = []
    
    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ['get', 'post', 'put', 'patch', 'delete']:
                total_endpoints += 1
                
                # Check for description
                if 'description' not in details and 'summary' not in details:
                    undocumented_endpoints.append(f"{method.upper()} {path}")
                
                # Check for authentication documentation
                if 'security' not in details and path not in ['/', '/health', '/docs', '/redoc', '/openapi.json']:
                    # Check if it's a public endpoint
                    if 'auth' not in path and 'health' not in path:
                        missing_auth.append(f"{method.upper()} {path}")
                
                # Check for response documentation
                if 'responses' not in details or len(details['responses']) < 2:
                    missing_responses.append(f"{method.upper()} {path}")
    
    # Report findings
    print(f"\n📊 OpenAPI Specification Summary:")
    print(f"   Total endpoints: {total_endpoints}")
    print(f"   Total paths: {len(paths)}")
    
    if undocumented_endpoints:
        issues.append(f"⚠️  {len(undocumented_endpoints)} endpoints missing description/summary")
        if len(undocumented_endpoints) <= 5:
            for endpoint in undocumented_endpoints:
                issues.append(f"     - {endpoint}")
    
    if missing_auth:
        issues.append(f"⚠️  {len(missing_auth)} endpoints missing authentication documentation")
        if len(missing_auth) <= 5:
            for endpoint in missing_auth:
                issues.append(f"     - {endpoint}")
    
    if missing_responses:
        issues.append(f"⚠️  {len(missing_responses)} endpoints with limited response documentation")
    
    # Check schemas
    if 'components' in spec and 'schemas' in spec['components']:
        schema_count = len(spec['components']['schemas'])
        print(f"   Schemas defined: {schema_count}")
    else:
        issues.append("⚠️  No schemas defined in components")
    
    # Check security schemes
    if 'components' in spec and 'securitySchemes' in spec['components']:
        security_schemes = spec['components']['securitySchemes']
        print(f"   Security schemes: {', '.join(security_schemes.keys())}")
    else:
        issues.append("⚠️  No security schemes defined")
    
    # Check tags
    if 'tags' in spec:
        tag_count = len(spec['tags'])
        print(f"   Tags defined: {tag_count}")
    else:
        issues.append("⚠️  No tags defined for endpoint organization")
    
    return issues


def print_endpoint_summary(spec: Dict[str, Any]) -> None:
    """Print summary of all endpoints by tag."""
    if 'paths' not in spec:
        return
    
    # Group endpoints by tag
    endpoints_by_tag: Dict[str, List[str]] = {}
    
    for path, methods in spec['paths'].items():
        for method, details in methods.items():
            if method in ['get', 'post', 'put', 'patch', 'delete']:
                tags = details.get('tags', ['Untagged'])
                for tag in tags:
                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []
                    
                    summary = details.get('summary', 'No summary')
                    auth_required = 'security' in details
                    auth_marker = "🔒" if auth_required else "🔓"
                    
                    endpoints_by_tag[tag].append(
                        f"   {auth_marker} {method.upper():6} {path:50} - {summary}"
                    )
    
    print("\n📋 Endpoints by Category:")
    print("   🔒 = Authentication required")
    print("   🔓 = Public endpoint\n")
    
    for tag in sorted(endpoints_by_tag.keys()):
        print(f"\n{tag}:")
        for endpoint in sorted(endpoints_by_tag[tag]):
            print(endpoint)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate OpenAPI specification from FastAPI application"
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('docs/api'),
        help='Output directory for generated specs (default: docs/api)'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate the generated specification'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Print detailed endpoint summary'
    )
    
    args = parser.parse_args()
    
    print("🔄 Generating OpenAPI specification...")
    
    # Generate spec
    try:
        spec = generate_openapi_spec()
    except Exception as e:
        print(f"❌ Failed to generate OpenAPI spec: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save in both formats
    json_path = args.output_dir / 'openapi.json'
    yaml_path = args.output_dir / 'openapi.yaml'
    
    try:
        save_spec_json(spec, json_path)
        save_spec_yaml(spec, yaml_path)
    except Exception as e:
        print(f"❌ Failed to save specs: {e}")
        return 1
    
    # Validate if requested
    if args.validate:
        print("\n🔍 Validating OpenAPI specification...")
        issues = validate_spec(spec)
        
        if issues:
            print("\n⚠️  Validation Issues:")
            for issue in issues:
                print(issue)
        else:
            print("\n✅ No validation issues found!")
    
    # Print summary if requested
    if args.summary:
        print_endpoint_summary(spec)
    
    print(f"\n✅ OpenAPI specification generated successfully!")
    print(f"\n📖 View documentation at:")
    print(f"   Swagger UI: http://localhost:8000/docs")
    print(f"   ReDoc:      http://localhost:8000/redoc")
    print(f"   JSON spec:  {json_path}")
    print(f"   YAML spec:  {yaml_path}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
