"""
Structured logging configuration for the application

Provides:
- JSON logging for log aggregation
- Startup diagnostics and summary
- Request/response logging
- Exception logging with context
- Sensitive data masking

Validates Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6
"""
import logging
import sys
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pythonjsonlogger.json import JsonFormatter

from app.core.error_reporter import ErrorReporter


class CustomJsonFormatter(JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'duration'):
            log_record['duration_ms'] = record.duration


def setup_logging(level: str = "INFO", enable_json: bool = True) -> None:
    """
    Setup application logging
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_json: Whether to use JSON formatting
        
    Validates Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6
    """
    log_level = getattr(logging, level.upper())
    
    # Create formatter
    if enable_json:
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(logger)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # File handler (optional)
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Suppress noisy loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)


def log_startup_summary(
    app_name: str,
    version: str,
    environment: str,
    config_file: str,
    database_status: Dict[str, Any],
    features_enabled: Dict[str, bool],
    security_warnings: Optional[list] = None
) -> None:
    """
    Log comprehensive startup summary.
    
    Args:
        app_name: Application name
        version: Application version
        environment: Environment (development, staging, production)
        config_file: Configuration file path
        database_status: Dictionary of database connection statuses
        features_enabled: Dictionary of enabled/disabled features
        security_warnings: Optional list of security warnings
        
    Validates Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6
    """
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 70)
    logger.info("APPLICATION STARTUP SUMMARY")
    logger.info("=" * 70)
    
    # Application info
    logger.info(f"Application: {app_name}")
    logger.info(f"Version: {version}")
    logger.info(f"Environment: {environment}")
    logger.info(f"Configuration file: {config_file}")
    
    # Database status
    logger.info("\nDatabase Status:")
    for db_name, status in database_status.items():
        if isinstance(status, dict):
            is_connected = status.get('is_connected', False)
            response_time = status.get('response_time_ms', 0)
            status_str = f"✅ ({response_time:.0f}ms)" if is_connected else "❌"
        else:
            status_str = str(status)
        logger.info(f"  {db_name}: {status_str}")
    
    # Features status
    logger.info("\nFeatures:")
    for feature_name, is_enabled in features_enabled.items():
        status_str = "✅ enabled" if is_enabled else "⚠️  disabled"
        logger.info(f"  {feature_name}: {status_str}")
    
    # Security warnings
    if security_warnings:
        logger.warning("\nSecurity Warnings:")
        for warning in security_warnings:
            logger.warning(f"  ⚠️  {warning}")
    
    # API documentation
    logger.info("\nAPI Documentation:")
    logger.info("  Swagger UI: http://localhost:8000/docs")
    logger.info("  ReDoc: http://localhost:8000/redoc")
    logger.info("  OpenAPI JSON: http://localhost:8000/openapi.json")
    
    # Health check endpoints
    logger.info("\nHealth Check Endpoints:")
    logger.info("  Overall health: GET /health")
    logger.info("  Readiness probe: GET /health/ready")
    logger.info("  Liveness probe: GET /health/live")
    
    logger.info("=" * 70)
    logger.info("✅ Application startup complete")
    logger.info("=" * 70)


# Create logger instance
logger = logging.getLogger(__name__)

# Request logging middleware
async def log_request(request, call_next):
    """
    Middleware to log HTTP requests and responses
    """
    import time
    from uuid import uuid4
    
    # Generate request ID
    request_id = str(uuid4())
    request.state.request_id = request_id
    
    # Log request
    logger.info(
        "Request started",
        extra={
            'request_id': request_id,
            'method': request.method,
            'url': str(request.url),
            'client_ip': request.client.host if request.client else None,
        }
    )
    
    # Process request
    start_time = time.time()
    try:
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000  # Convert to ms
        
        # Log response
        logger.info(
            "Request completed",
            extra={
                'request_id': request_id,
                'status_code': response.status_code,
                'duration': duration,
            }
        )
        
        return response
        
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        
        # Log error
        logger.error(
            "Request failed",
            extra={
                'request_id': request_id,
                'duration': duration,
                'error': str(e),
            },
            exc_info=True
        )
        raise


# Error logging
def log_exception(exc: Exception, context: Dict[str, Any] = None):
    """Log exception with context"""
    extra = context or {}
    extra['exception_type'] = type(exc).__name__
    extra['exception_message'] = str(exc)
    
    logger.error(
        "Exception occurred",
        extra=extra,
        exc_info=True
    )


def mask_sensitive_in_logs(message: str) -> str:
    """
    Mask sensitive data in log messages.
    
    Applies masking rules to remove or obscure:
    - Passwords
    - API keys
    - Tokens
    - Connection strings with credentials
    - JWT secrets
    - Database URLs with passwords
    - Webhook secrets
    
    Args:
        message: Log message that may contain sensitive data
        
    Returns:
        Log message with sensitive data masked
        
    Validates Requirements: 1.6, 7.5, 7.6
    """
    if not message:
        return message
    
    return ErrorReporter.mask_sensitive_data(message)


def log_database_status(
    database_status: Dict[str, Any],
    logger_instance: Optional[logging.Logger] = None
) -> None:
    """
    Log database connection status with detailed information.
    
    Logs:
    - Connection status for each database (PostgreSQL, Neo4j, Redis)
    - Response times for successful connections
    - Error messages for failed connections (masked)
    - Overall database health summary
    
    Args:
        database_status: Dictionary mapping database names to status info
        logger_instance: Optional logger instance (uses module logger if not provided)
        
    Validates Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6
    """
    if logger_instance is None:
        logger_instance = logging.getLogger(__name__)
    
    logger_instance.info("Database Connection Status:")
    logger_instance.info("-" * 50)
    
    all_connected = True
    critical_connected = True
    
    for db_name, status in database_status.items():
        if isinstance(status, dict):
            is_connected = status.get('is_connected', False)
            response_time = status.get('response_time_ms', 0)
            error = status.get('error', None)
            is_critical = status.get('is_critical', True)
            
            if is_connected:
                logger_instance.info(
                    f"  {db_name}: ✅ Connected ({response_time:.0f}ms)"
                )
            else:
                all_connected = False
                if is_critical:
                    critical_connected = False
                
                # Mask sensitive data in error message
                masked_error = mask_sensitive_in_logs(error) if error else "Unknown error"
                
                if is_critical:
                    logger_instance.error(
                        f"  {db_name}: ❌ Failed - {masked_error}"
                    )
                else:
                    logger_instance.warning(
                        f"  {db_name}: ⚠️  Failed - {masked_error}"
                    )
        else:
            # Handle ConnectionStatus objects
            status_obj = status
            if hasattr(status_obj, 'is_connected'):
                if status_obj.is_connected:
                    logger_instance.info(
                        f"  {status_obj.service}: ✅ Connected ({status_obj.response_time_ms:.0f}ms)"
                    )
                else:
                    all_connected = False
                    if status_obj.is_critical:
                        critical_connected = False
                    
                    masked_error = mask_sensitive_in_logs(status_obj.error) if status_obj.error else "Unknown error"
                    
                    if status_obj.is_critical:
                        logger_instance.error(
                            f"  {status_obj.service}: ❌ Failed - {masked_error}"
                        )
                    else:
                        logger_instance.warning(
                            f"  {status_obj.service}: ⚠️  Failed - {masked_error}"
                        )
    
    logger_instance.info("-" * 50)
    
    # Log summary
    if all_connected:
        logger_instance.info("✅ All databases connected")
    elif critical_connected:
        logger_instance.warning("⚠️  Some optional databases unavailable, but critical databases connected")
    else:
        logger_instance.error("❌ Critical database(s) unavailable")
