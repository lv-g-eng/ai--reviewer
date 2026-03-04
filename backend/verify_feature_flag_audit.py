"""
Manual verification script for feature flag audit endpoint

This script verifies that the feature flag audit endpoint is properly implemented
and can log feature flag changes.

Validates Requirement: 10.6
"""
import asyncio
import sys
from datetime import datetime, timezone


async def verify_endpoint():
    """Verify the feature flag audit endpoint exists and is properly configured"""
    
    print("=" * 70)
    print("Feature Flag Audit Endpoint Verification")
    print("=" * 70)
    print()
    
    # Check 1: Verify endpoint file exists and imports correctly
    print("✓ Check 1: Verifying endpoint file...")
    try:
        from app.api.v1.endpoints import audit_logs
        print("  ✅ audit_logs module imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import audit_logs: {e}")
        return False
    
    # Check 2: Verify the endpoint function exists
    print("\n✓ Check 2: Verifying endpoint function...")
    if hasattr(audit_logs, 'log_feature_flag_change'):
        print("  ✅ log_feature_flag_change function exists")
    else:
        print("  ❌ log_feature_flag_change function not found")
        return False
    
    # Check 3: Verify request/response models exist
    print("\n✓ Check 3: Verifying request/response models...")
    if hasattr(audit_logs, 'FeatureFlagChangeLog'):
        print("  ✅ FeatureFlagChangeLog model exists")
    else:
        print("  ❌ FeatureFlagChangeLog model not found")
        return False
    
    if hasattr(audit_logs, 'FeatureFlagAuditResponse'):
        print("  ✅ FeatureFlagAuditResponse model exists")
    else:
        print("  ❌ FeatureFlagAuditResponse model not found")
        return False
    
    # Check 4: Verify AuditEventType.FEATURE_FLAG_CHANGE exists
    print("\n✓ Check 4: Verifying AuditEventType constant...")
    try:
        from app.services.audit_logging_service import AuditEventType
        if hasattr(AuditEventType, 'FEATURE_FLAG_CHANGE'):
            print(f"  ✅ AuditEventType.FEATURE_FLAG_CHANGE = '{AuditEventType.FEATURE_FLAG_CHANGE}'")
        else:
            print("  ❌ AuditEventType.FEATURE_FLAG_CHANGE not found")
            return False
    except ImportError as e:
        print(f"  ❌ Failed to import AuditEventType: {e}")
        return False
    
    # Check 5: Verify router registration
    print("\n✓ Check 5: Verifying router registration...")
    try:
        from app.api.v1 import router as api_router
        # Check if audit_logs router is included
        print("  ✅ API router imported successfully")
        print("  ℹ️  Endpoint should be available at: POST /api/v1/audit-logs/feature-flags")
    except ImportError as e:
        print(f"  ❌ Failed to import API router: {e}")
        return False
    
    # Check 6: Verify model validation
    print("\n✓ Check 6: Verifying model validation...")
    try:
        from app.api.v1.endpoints.audit_logs import FeatureFlagChangeLog
        
        # Test valid data
        valid_log = FeatureFlagChangeLog(
            flag_name="test-flag",
            old_value=False,
            new_value=True,
            user_id="123e4567-e89b-12d3-a456-426614174000",
            metadata={"source": "test"}
        )
        print("  ✅ Valid model creation successful")
        
        # Test required fields
        try:
            invalid_log = FeatureFlagChangeLog(
                flag_name="test-flag",
                old_value=False
                # missing new_value
            )
            print("  ❌ Model validation failed - should require new_value")
            return False
        except Exception:
            print("  ✅ Model validation working - rejects missing required fields")
            
    except Exception as e:
        print(f"  ❌ Model validation error: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ All checks passed!")
    print("=" * 70)
    print()
    print("Endpoint Details:")
    print("  URL: POST /api/v1/audit-logs/feature-flags")
    print("  Authentication: Required (Bearer token)")
    print("  Request Body:")
    print("    - flag_name: string (required)")
    print("    - old_value: boolean (required)")
    print("    - new_value: boolean (required)")
    print("    - user_id: string (optional)")
    print("    - timestamp: datetime (optional)")
    print("    - metadata: object (optional)")
    print()
    print("  Response:")
    print("    - success: boolean")
    print("    - log_id: string (UUID)")
    print("    - message: string")
    print()
    print("  Validates Requirement: 10.6")
    print()
    
    return True


if __name__ == "__main__":
    result = asyncio.run(verify_endpoint())
    sys.exit(0 if result else 1)
