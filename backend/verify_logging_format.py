"""
Simple verification script for structured logging format

This script verifies that the logging system outputs JSON format correctly
without running the full test suite.
"""

import sys
import json
import logging
from io import StringIO
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.logging_config import (
    CustomJsonFormatter,
    set_request_context,
    clear_request_context,
)


def verify_json_logging():
    """Verify JSON logging format"""
    print("=" * 70)
    print("  Verifying JSON Structured Logging Format")
    print("=" * 70)
    
    # Setup formatter
    formatter = CustomJsonFormatter(service_name="test-service")
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    
    # Create string buffer to capture log output
    log_buffer = StringIO()
    handler = logging.StreamHandler(log_buffer)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Set request context
    set_request_context(
        request_id="req-test-123",
        user_id="user-test-456",
        correlation_id="corr-test-789"
    )
    
    # Log a test message
    logger.info("Test log message", extra={"test_field": "test_value"})
    
    # Get log output
    log_output = log_buffer.getvalue().strip()
    
    print("\nLog Output:")
    print("-" * 70)
    print(log_output)
    print("-" * 70)
    
    # Parse JSON
    try:
        log_data = json.loads(log_output)
        print("\n✅ Log output is valid JSON")
    except json.JSONDecodeError as e:
        print(f"\n❌ Log output is not valid JSON: {e}")
        return False
    
    # Verify required fields
    print("\nVerifying Required Fields:")
    print("-" * 70)
    
    required_fields = {
        'timestamp': 'Timestamp',
        'level': 'Log level',
        'message': 'Log message',
        'logger': 'Logger name',
        'service_name': 'Service name',
        'request_id': 'Request ID',
        'user_id': 'User ID',
        'correlation_id': 'Correlation ID'
    }
    
    all_present = True
    for field, description in required_fields.items():
        if field in log_data:
            value = log_data[field]
            print(f"  ✅ {description:20} ({field}): {value}")
        else:
            print(f"  ❌ {description:20} ({field}): MISSING")
            all_present = False
    
    # Verify values
    print("\nVerifying Field Values:")
    print("-" * 70)
    
    checks = [
        (log_data.get('level') == 'INFO', "Log level is INFO"),
        (log_data.get('message') == 'Test log message', "Message is correct"),
        (log_data.get('service_name') == 'test-service', "Service name is correct"),
        (log_data.get('request_id') == 'req-test-123', "Request ID is correct"),
        (log_data.get('user_id') == 'user-test-456', "User ID is correct"),
        (log_data.get('correlation_id') == 'corr-test-789', "Correlation ID is correct"),
        ('test_field' in log_data, "Extra fields are included"),
    ]
    
    all_correct = True
    for check, description in checks:
        if check:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description}")
            all_correct = False
    
    # Cleanup
    clear_request_context()
    logger.removeHandler(handler)
    
    print("\n" + "=" * 70)
    if all_present and all_correct:
        print("✅ JSON STRUCTURED LOGGING VERIFICATION PASSED")
        print("\nStructured logging is correctly configured with:")
        print("  - JSON format output")
        print("  - All required fields (timestamp, level, message, etc.)")
        print("  - Request context tracking (request_id, user_id, correlation_id)")
        print("  - Extra field support")
        print("\nRequirement 7.1 validated: Structured JSON logging")
        print("=" * 70)
        return True
    else:
        print("❌ JSON STRUCTURED LOGGING VERIFICATION FAILED")
        print("=" * 70)
        return False


def verify_log_rotation():
    """Verify log rotation configuration"""
    print("\n" + "=" * 70)
    print("  Verifying Log Rotation Configuration")
    print("=" * 70)
    
    from logging.handlers import TimedRotatingFileHandler
    from app.core.logging_config import setup_logging
    
    # Setup logging
    setup_logging(level='INFO', enable_json=True)
    
    # Find TimedRotatingFileHandler
    root_logger = logging.getLogger()
    rotating_handlers = [
        h for h in root_logger.handlers 
        if isinstance(h, TimedRotatingFileHandler)
    ]
    
    if not rotating_handlers:
        print("\n❌ No TimedRotatingFileHandler found")
        return False
    
    handler = rotating_handlers[0]
    
    print("\nLog Rotation Configuration:")
    print("-" * 70)
    print(f"  File: {handler.baseFilename}")
    print(f"  Rotation: {handler.when}")
    print(f"  Interval: {handler.interval} seconds")
    print(f"  Backup Count: {handler.backupCount} days")
    print(f"  Suffix: {handler.suffix}")
    
    print("\nVerifying Configuration:")
    print("-" * 70)
    
    checks = [
        (handler.when == 'MIDNIGHT', "Rotation at midnight"),
        (handler.interval == 86400, "Daily rotation (86400 seconds)"),
        (handler.backupCount == 30, "30-day retention"),
        (handler.suffix == "%Y-%m-%d", "Date suffix format"),
    ]
    
    all_correct = True
    for check, description in checks:
        if check:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description}")
            all_correct = False
    
    print("\n" + "=" * 70)
    if all_correct:
        print("✅ LOG ROTATION VERIFICATION PASSED")
        print("\nLog rotation is correctly configured:")
        print("  - Daily rotation at midnight")
        print("  - 30-day retention period")
        print("  - Date-based file naming")
        print("\nRequirement 7.6 validated: 30-day log retention")
        print("=" * 70)
        return True
    else:
        print("❌ LOG ROTATION VERIFICATION FAILED")
        print("=" * 70)
        return False


def main():
    """Main verification function"""
    results = []
    
    # Verify JSON logging
    results.append(verify_json_logging())
    
    # Verify log rotation
    results.append(verify_log_rotation())
    
    # Summary
    print("\n" + "=" * 70)
    print("  VERIFICATION SUMMARY")
    print("=" * 70)
    
    if all(results):
        print("\n✅ ALL LOGGING VERIFICATIONS PASSED")
        print("\nStructured logging implementation is complete and correct.")
        return 0
    else:
        print("\n❌ SOME LOGGING VERIFICATIONS FAILED")
        print("\nPlease review the failed checks above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
