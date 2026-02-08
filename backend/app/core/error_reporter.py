"""
Error Reporter with Sensitive Data Masking and Database Error Classification

Provides comprehensive error reporting with automatic masking of sensitive data
including passwords, API keys, tokens, and connection strings. Enhanced with
database-specific error categorization and comprehensive logging capabilities.

Validates Requirements: 1.6, 5.1, 5.2, 5.3, 7.1, 7.2, 7.5
"""

import re
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum


class SensitiveDataType(Enum):
    """Types of sensitive data that need masking"""
    PASSWORD = "password"
    API_KEY = "api_key"
    TOKEN = "token"
    CONNECTION_STRING = "connection_string"
    JWT_SECRET = "jwt_secret"
    DATABASE_URL = "database_url"
    WEBHOOK_SECRET = "webhook_secret"


class DatabaseErrorCategory(Enum):
    """Categories of database connectivity errors for classification"""
    CONNECTION_TIMEOUT = "connection_timeout"
    AUTHENTICATION_FAILURE = "authentication_failure"
    ENCODING_ERROR = "encoding_error"
    COMPATIBILITY_ERROR = "compatibility_error"
    POOL_EXHAUSTION = "pool_exhaustion"
    NETWORK_ERROR = "network_error"
    CONFIGURATION_ERROR = "configuration_error"
    MIGRATION_ERROR = "migration_error"
    HEALTH_CHECK_ERROR = "health_check_error"


@dataclass
class DatabaseErrorInfo:
    """Structured database error information with classification"""
    category: DatabaseErrorCategory
    component: str
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    resolution_steps: List[str]
    error_code: Optional[str] = None
    connection_params: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        """Validate database error info"""
        if not self.component:
            raise ValueError("component is required")
        if not self.message:
            raise ValueError("message is required")


@dataclass
class ErrorStatistics:
    """Error statistics for pattern identification"""
    error_counts: Dict[DatabaseErrorCategory, int] = field(default_factory=dict)
    component_errors: Dict[str, int] = field(default_factory=dict)
    recent_errors: List[DatabaseErrorInfo] = field(default_factory=list)
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    
    def add_error(self, error_info: DatabaseErrorInfo) -> None:
        """Add error to statistics"""
        # Update counts
        self.error_counts[error_info.category] = self.error_counts.get(error_info.category, 0) + 1
        self.component_errors[error_info.component] = self.component_errors.get(error_info.component, 0) + 1
        
        # Update timestamps
        if self.first_seen is None:
            self.first_seen = error_info.timestamp
        self.last_seen = error_info.timestamp
        
        # Add to recent errors (keep last 50)
        self.recent_errors.append(error_info)
        if len(self.recent_errors) > 50:
            self.recent_errors.pop(0)
    
    def get_most_frequent_category(self) -> Optional[DatabaseErrorCategory]:
        """Get the most frequent error category"""
        if not self.error_counts:
            return None
        return max(self.error_counts.items(), key=lambda x: x[1])[0]
    
    def get_most_problematic_component(self) -> Optional[str]:
        """Get the component with most errors"""
        if not self.component_errors:
            return None
        return max(self.component_errors.items(), key=lambda x: x[1])[0]


@dataclass
class MaskingRule:
    """Rule for masking a specific type of sensitive data"""
    pattern: str  # Regex pattern to match
    replacement: str  # Replacement pattern
    data_type: SensitiveDataType
    show_first: int = 0  # Number of characters to show at start
    show_last: int = 0  # Number of characters to show at end


class ErrorReporter:
    """
    Comprehensive error reporter with sensitive data masking and database error classification.
    
    Features:
    - Masks sensitive data patterns (passwords, API keys, tokens, connection strings)
    - Classifies database errors by category for easier troubleshooting
    - Provides structured error messages with resolution steps
    - Tracks error statistics for pattern identification
    - Integrates with logging system for comprehensive error reporting
    
    Validates Requirements: 1.6, 5.1, 5.2, 5.3, 7.1, 7.2, 7.5
    """

    # Class-level error statistics for pattern tracking
    _error_statistics = ErrorStatistics()
    
    # Logger for error reporting
    _logger = logging.getLogger(__name__)

    # Masking rules for different sensitive data patterns
    # Order matters - more specific patterns should come first
    MASKING_RULES = [
        # Database URLs with passwords: postgresql://user:password@host:port/db (MUST BE FIRST)
        MaskingRule(
            pattern=r'(postgresql[+\w]*://[^:]+:)([^@]+)(@)',
            replacement=r'\1***\3',
            data_type=SensitiveDataType.DATABASE_URL,
        ),
        # MySQL URLs with passwords
        MaskingRule(
            pattern=r'(mysql[+\w]*://[^:]+:)([^@]+)(@)',
            replacement=r'\1***\3',
            data_type=SensitiveDataType.DATABASE_URL,
        ),
        # MongoDB URLs with passwords
        MaskingRule(
            pattern=r'(mongodb[+\w]*://[^:]+:)([^@]+)(@)',
            replacement=r'\1***\3',
            data_type=SensitiveDataType.DATABASE_URL,
        ),
        # Redis URLs with passwords: redis://:password@host:port
        MaskingRule(
            pattern=r'(redis://):([^@]+)(@)',
            replacement=r'\1***\3',
            data_type=SensitiveDataType.DATABASE_URL,
        ),
        # GitHub tokens: ghp_xxx (BEFORE generic token pattern)
        MaskingRule(
            pattern=r'(ghp_[a-zA-Z0-9_]{36})',
            replacement=r'ghp_***',
            data_type=SensitiveDataType.TOKEN,
        ),
        # Password patterns: password=value, password: value, etc.
        MaskingRule(
            pattern=r'(?i)(password\s*[=:]\s*)([^\s,;"\']*)(?=[,;\s"\']|$)',
            replacement=r'\1***',
            data_type=SensitiveDataType.PASSWORD,
        ),
        # API Keys: sk-xxx, pk-xxx, etc.
        MaskingRule(
            pattern=r'(?i)(sk-|pk-|api[_-]?key\s*[=:]\s*)([a-zA-Z0-9_-]+)',
            replacement=r'\1***',
            data_type=SensitiveDataType.API_KEY,
        ),
        # Generic tokens: token=value, token: value
        MaskingRule(
            pattern=r'(?i)(token\s*[=:]\s*)([^\s,;"\']*)(?=[,;\s"\']|$)',
            replacement=r'\1***',
            data_type=SensitiveDataType.TOKEN,
        ),
        # JWT secrets: jwt_secret=value, JWT_SECRET=value
        MaskingRule(
            pattern=r'(?i)(jwt[_-]?secret\s*[=:]\s*)([^\s,;"\']*)(?=[,;\s"\']|$)',
            replacement=r'\1***',
            data_type=SensitiveDataType.JWT_SECRET,
        ),
        # Generic connection strings with passwords
        MaskingRule(
            pattern=r'(?i)(connection[_-]?string\s*[=:]\s*["\']?)([^"\']*password[^"\']*["\']?)',
            replacement=r'\1***',
            data_type=SensitiveDataType.CONNECTION_STRING,
        ),
        # Webhook secrets
        MaskingRule(
            pattern=r'(?i)(webhook[_-]?secret\s*[=:]\s*)([^\s,;"\']*)(?=[,;\s"\']|$)',
            replacement=r'\1***',
            data_type=SensitiveDataType.WEBHOOK_SECRET,
        ),
    ]

    @staticmethod
    def mask_sensitive_data(value: str) -> str:
        """
        Mask all sensitive data in a string.
        
        Applies all masking rules to the input string and returns the masked version.
        
        Args:
            value: String that may contain sensitive data
            
        Returns:
            String with all sensitive data masked
            
        Validates Requirement: 1.6, 7.5
        """
        if not value:
            return value

        masked = value
        for rule in ErrorReporter.MASKING_RULES:
            masked = re.sub(rule.pattern, rule.replacement, masked)

        return masked

    @staticmethod
    def mask_value(value: str, data_type: SensitiveDataType, show_first: int = 0, show_last: int = 0) -> str:
        """
        Mask a specific value based on its type.
        
        Args:
            value: The value to mask
            data_type: Type of sensitive data
            show_first: Number of characters to show at the start
            show_last: Number of characters to show at the end
            
        Returns:
            Masked value
            
        Validates Requirement: 7.5
        """
        if not value or len(value) == 0:
            return "***"

        if data_type == SensitiveDataType.PASSWORD:
            return "***"
        elif data_type == SensitiveDataType.JWT_SECRET:
            return "***"
        elif data_type == SensitiveDataType.WEBHOOK_SECRET:
            return "***"
        elif data_type in [SensitiveDataType.API_KEY, SensitiveDataType.TOKEN]:
            # Show first N and last N characters
            if len(value) <= show_first + show_last:
                return "***"
            if show_first > 0 and show_last > 0:
                return f"{value[:show_first]}***{value[-show_last:]}"
            elif show_first > 0:
                return f"{value[:show_first]}***"
            elif show_last > 0:
                return f"***{value[-show_last:]}"
            else:
                return "***"
        else:
            return "***"

    @staticmethod
    def mask_connection_string(connection_string: str) -> str:
        """
        Mask password in a connection string while preserving host/port.
        
        Examples:
            postgresql://user:password@host:5432/db -> postgresql://user:***@host:5432/db
            redis://:password@host:6379 -> redis://***@host:6379
            
        Args:
            connection_string: Connection string to mask
            
        Returns:
            Connection string with password masked
            
        Validates Requirement: 7.5
        """
        if not connection_string:
            return connection_string

        # PostgreSQL/async connection strings
        connection_string = re.sub(
            r'(postgresql[+\w]*://[^:]+:)([^@]+)(@)',
            r'\1***\3',
            connection_string
        )

        # Redis connection strings
        connection_string = re.sub(
            r'(redis://):([^@]+)(@)',
            r'\1***\3',
            connection_string
        )

        # MySQL connection strings
        connection_string = re.sub(
            r'(mysql[+\w]*://[^:]+:)([^@]+)(@)',
            r'\1***\3',
            connection_string
        )

        # MongoDB connection strings
        connection_string = re.sub(
            r'(mongodb[+\w]*://[^:]+:)([^@]+)(@)',
            r'\1***\3',
            connection_string
        )

        return connection_string

    @staticmethod
    def format_missing_variable_error(
        var_name: str,
        expected_format: str = "non-empty string",
        remediation: Optional[str] = None
    ) -> str:
        """
        Format error message for missing environment variable.
        
        Args:
            var_name: Name of the missing variable
            expected_format: Expected format/type of the variable
            remediation: Optional remediation guidance
            
        Returns:
            Formatted error message
            
        Validates Requirements: 7.1, 7.2
        """
        message = f"ERROR: Missing required environment variable: {var_name}\n"
        message += f"Expected format: {expected_format}\n"

        if remediation:
            message += f"How to fix: {remediation}\n"
        else:
            # Provide default remediation based on variable name
            if "SECRET" in var_name or "PASSWORD" in var_name:
                message += f"How to fix: Generate a secure value and set {var_name} environment variable\n"
            elif "TOKEN" in var_name:
                message += f"How to fix: Obtain a valid token and set {var_name} environment variable\n"
            elif "URL" in var_name or "HOST" in var_name:
                message += f"How to fix: Set {var_name} to the correct connection URL or hostname\n"
            else:
                message += f"How to fix: Set {var_name} environment variable to the required value\n"

        return message

    @staticmethod
    def format_connection_error(
        service: str,
        error: Exception,
        connection_string: Optional[str] = None,
        is_critical: bool = True
    ) -> str:
        """
        Format error message for database connection failure with enhanced classification.
        
        Args:
            service: Name of the service (PostgreSQL, Neo4j, Redis, etc.)
            error: The exception that occurred
            connection_string: Optional connection string (will be masked)
            is_critical: Whether this is a critical error
            
        Returns:
            Formatted error message with classification and resolution steps
            
        Validates Requirements: 5.1, 5.2, 5.3, 7.1, 7.2
        """
        # Use the new enhanced database connection error formatting
        return ErrorReporter.format_database_connection_error(
            service=service,
            error=error,
            connection_string=connection_string,
            is_critical=is_critical,
            retry_count=0
        )

    @staticmethod
    def format_validation_error(
        field: str,
        reason: str,
        current_value: Optional[str] = None,
        expected_format: Optional[str] = None,
        remediation: Optional[str] = None
    ) -> str:
        """
        Format error message for validation failure.
        
        Args:
            field: Name of the field that failed validation
            reason: Reason for validation failure
            current_value: Current value (will be masked if sensitive)
            expected_format: Expected format
            remediation: Optional remediation guidance
            
        Returns:
            Formatted error message
            
        Validates Requirements: 7.1, 7.2
        """
        message = f"ERROR: Validation failed for {field}\n"
        message += f"Reason: {reason}\n"

        if current_value:
            masked_value = ErrorReporter.mask_sensitive_data(current_value)
            message += f"Current value: {masked_value}\n"

        if expected_format:
            message += f"Expected format: {expected_format}\n"

        if remediation:
            message += f"How to fix: {remediation}\n"
        else:
            message += f"How to fix: Update {field} to meet the validation requirements\n"

        return message

    @staticmethod
    def format_error_report(
        errors: List[str],
        warnings: List[str] = None,
        include_remediation: bool = True
    ) -> str:
        """
        Format a comprehensive error report with multiple errors and warnings.
        
        Args:
            errors: List of error messages
            warnings: Optional list of warning messages
            include_remediation: Whether to include remediation summary
            
        Returns:
            Formatted error report
            
        Validates Requirements: 7.1, 7.2, 7.3, 7.4
        """
        if warnings is None:
            warnings = []

        report = "STARTUP VALIDATION FAILED\n"
        report += "=" * 50 + "\n\n"

        if errors:
            report += "Critical Errors:\n"
            for i, error in enumerate(errors, 1):
                # Mask sensitive data in error messages
                masked_error = ErrorReporter.mask_sensitive_data(error)
                report += f"{i}. {masked_error}\n"
            report += "\n"

        if warnings:
            report += "Warnings:\n"
            for i, warning in enumerate(warnings, 1):
                # Mask sensitive data in warning messages
                masked_warning = ErrorReporter.mask_sensitive_data(warning)
                report += f"{i}. {masked_warning}\n"
            report += "\n"

        if include_remediation:
            report += "How to fix:\n"
            report += "1. Review the errors above\n"
            report += "2. Set missing environment variables\n"
            report += "3. Verify database connectivity\n"
            report += "4. Check configuration values\n"
            report += "5. Restart the application\n\n"
            report += "Application startup aborted.\n"

        return report

    @staticmethod
    def format_configuration_summary(
        config_dict: Dict[str, any],
        mask_all_values: bool = False
    ) -> str:
        """
        Format a configuration summary with sensitive values masked.
        
        Args:
            config_dict: Dictionary of configuration values
            mask_all_values: If True, mask all values; if False, only mask sensitive ones
            
        Returns:
            Formatted configuration summary
            
        Validates Requirements: 7.6, 1.6
        """
        summary = "Configuration Summary:\n"
        summary += "=" * 50 + "\n"

        for key, value in config_dict.items():
            if value is None:
                summary += f"{key}: (not set)\n"
            elif mask_all_values:
                # Mask all values when requested
                summary += f"{key}: ***\n"
            elif ErrorReporter._is_sensitive_key(key):
                # Mask sensitive keys
                masked_value = ErrorReporter.mask_sensitive_data(str(value))
                summary += f"{key}: {masked_value}\n"
            else:
                summary += f"{key}: {value}\n"

        return summary

    @staticmethod
    def _is_sensitive_key(key: str) -> bool:
        """
        Determine if a configuration key contains sensitive data.
        
        Args:
            key: Configuration key name
            
        Returns:
            True if the key is sensitive, False otherwise
        """
        sensitive_keywords = [
            "password", "secret", "token", "key", "credential",
            "auth", "api_key", "webhook", "jwt", "bearer",
            "url", "connection", "dsn"
        ]
        key_lower = key.lower()
        return any(keyword in key_lower for keyword in sensitive_keywords)

    @staticmethod
    def collect_errors(
        error_list: List[Tuple[str, str, Optional[str]]]
    ) -> Tuple[List[str], List[str]]:
        """
        Collect and categorize errors and warnings.
        
        Args:
            error_list: List of tuples (error_type, message, remediation)
                       error_type can be "error" or "warning"
            
        Returns:
            Tuple of (errors, warnings) lists
            
        Validates Requirements: 7.1, 7.2, 7.3
        """
        errors = []
        warnings = []

        for error_type, message, remediation in error_list:
            if remediation:
                formatted = f"{message}\nHow to fix: {remediation}"
            else:
                formatted = message

            if error_type.lower() == "error":
                errors.append(formatted)
            elif error_type.lower() == "warning":
                warnings.append(formatted)

        return errors, warnings

    @staticmethod
    def batch_report_errors(
        errors: List[str],
        warnings: List[str] = None,
        service_name: str = "Application"
    ) -> str:
        """
        Create a batch error report for multiple errors at once.
        
        Args:
            errors: List of error messages
            warnings: Optional list of warning messages
            service_name: Name of the service reporting errors
            
        Returns:
            Formatted batch error report
            
        Validates Requirements: 7.1, 7.2, 7.3, 7.4
        """
        if warnings is None:
            warnings = []

        report = f"{service_name} Startup Failed\n"
        report += "=" * 60 + "\n\n"

        if errors:
            report += f"Found {len(errors)} critical error(s):\n"
            report += "-" * 60 + "\n"
            for i, error in enumerate(errors, 1):
                masked_error = ErrorReporter.mask_sensitive_data(error)
                report += f"\n{i}. {masked_error}\n"
            report += "\n"

        if warnings:
            report += f"Found {len(warnings)} warning(s):\n"
            report += "-" * 60 + "\n"
            for i, warning in enumerate(warnings, 1):
                masked_warning = ErrorReporter.mask_sensitive_data(warning)
                report += f"\n{i}. {masked_warning}\n"
            report += "\n"

        report += "-" * 60 + "\n"
        report += "Next steps:\n"
        report += "1. Review the errors and warnings above\n"
        report += "2. Fix each issue according to the guidance provided\n"
        report += "3. Restart the application\n"
        report += "4. Check logs for additional details\n"

        return report

    # ========================================
    # Database Error Classification Methods
    # ========================================

    @staticmethod
    def classify_database_error(
        error: Exception,
        component: str,
        connection_params: Optional[Dict[str, str]] = None
    ) -> DatabaseErrorCategory:
        """
        Classify database error by analyzing error message and type.
        
        Args:
            error: The exception that occurred
            component: Database component (PostgreSQL, Neo4j, etc.)
            connection_params: Optional connection parameters for context
            
        Returns:
            DatabaseErrorCategory for the error
            
        Validates Requirements: 5.2
        """
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Connection timeout errors
        if any(keyword in error_str for keyword in ['timeout', 'timed out', 'connection timeout']):
            return DatabaseErrorCategory.CONNECTION_TIMEOUT
        
        # Authentication failures
        if any(keyword in error_str for keyword in [
            'authentication', 'password', 'credentials', 'unauthorized', 'access denied',
            'login failed', 'auth', 'permission denied'
        ]):
            return DatabaseErrorCategory.AUTHENTICATION_FAILURE
        
        # Encoding errors
        if any(keyword in error_str for keyword in [
            'encoding', 'decode', 'utf-8', 'unicode', 'codec', 'character'
        ]) or 'encoding' in error_type:
            return DatabaseErrorCategory.ENCODING_ERROR
        
        # Compatibility errors
        if any(keyword in error_str for keyword in [
            'version', 'compatibility', 'incompatible', 'unsupported', 'asyncpg'
        ]):
            return DatabaseErrorCategory.COMPATIBILITY_ERROR
        
        # Pool exhaustion
        if any(keyword in error_str for keyword in [
            'pool', 'connection limit', 'max connections', 'exhausted', 'too many connections',
            'too many active connections', 'connection pool exhausted'
        ]):
            return DatabaseErrorCategory.POOL_EXHAUSTION
        
        # Network errors
        if any(keyword in error_str for keyword in [
            'connection refused', 'network', 'host', 'resolve', 'unreachable', 'dns'
        ]):
            return DatabaseErrorCategory.NETWORK_ERROR
        
        # Configuration errors
        if any(keyword in error_str for keyword in [
            'configuration', 'config', 'invalid', 'missing', 'required'
        ]):
            return DatabaseErrorCategory.CONFIGURATION_ERROR
        
        # Migration errors
        if any(keyword in error_str for keyword in [
            'migration', 'alembic', 'schema', 'table', 'column'
        ]):
            return DatabaseErrorCategory.MIGRATION_ERROR
        
        # Health check errors
        if any(keyword in error_str for keyword in [
            'health', 'check', 'probe', 'status'
        ]):
            return DatabaseErrorCategory.HEALTH_CHECK_ERROR
        
        # Default to network error if no specific category matches
        return DatabaseErrorCategory.NETWORK_ERROR

    @staticmethod
    def create_database_error_info(
        error: Exception,
        component: str,
        connection_params: Optional[Dict[str, str]] = None,
        error_code: Optional[str] = None
    ) -> DatabaseErrorInfo:
        """
        Create structured database error information.
        
        Args:
            error: The exception that occurred
            component: Database component name
            connection_params: Optional connection parameters (will be masked)
            error_code: Optional database-specific error code
            
        Returns:
            DatabaseErrorInfo with classified error details
            
        Validates Requirements: 5.1, 5.2
        """
        category = ErrorReporter.classify_database_error(error, component, connection_params)
        
        # Mask sensitive data in error message
        masked_message = ErrorReporter.mask_sensitive_data(str(error))
        
        # Mask connection parameters if provided
        masked_params = None
        if connection_params:
            masked_params = {
                key: ErrorReporter.mask_sensitive_data(str(value))
                for key, value in connection_params.items()
            }
        
        # Generate resolution steps based on error category
        resolution_steps = ErrorReporter._get_resolution_steps(category, component)
        
        # Create error details
        details = {
            'error_type': type(error).__name__,
            'original_message': masked_message,
            'component': component,
            'category': category.value
        }
        
        if error_code:
            details['error_code'] = error_code
        
        if masked_params:
            details['connection_params'] = masked_params
        
        return DatabaseErrorInfo(
            category=category,
            component=component,
            message=masked_message,
            details=details,
            timestamp=datetime.now(timezone.utc),
            resolution_steps=resolution_steps,
            error_code=error_code,
            connection_params=masked_params
        )

    @staticmethod
    def _get_resolution_steps(category: DatabaseErrorCategory, component: str) -> List[str]:
        """
        Get resolution steps for a specific error category.
        
        Args:
            category: Database error category
            component: Database component name
            
        Returns:
            List of resolution steps
        """
        base_steps = {
            DatabaseErrorCategory.CONNECTION_TIMEOUT: [
                f"Check if {component} database service is running and accessible",
                "Verify network connectivity to the database server",
                "Increase connection timeout values in configuration",
                "Check for network firewalls or security groups blocking access"
            ],
            DatabaseErrorCategory.AUTHENTICATION_FAILURE: [
                f"Verify {component} username and password are correct",
                "Check if the user account exists and has proper permissions",
                "Ensure authentication method matches server configuration",
                "Check for account lockouts or password expiration"
            ],
            DatabaseErrorCategory.ENCODING_ERROR: [
                "Verify migration files are saved with UTF-8 encoding",
                "Check for non-UTF-8 characters in database content",
                "Validate file encoding before processing",
                "Convert files to UTF-8 encoding if necessary"
            ],
            DatabaseErrorCategory.COMPATIBILITY_ERROR: [
                "Check Python version compatibility with database drivers",
                f"Verify {component} driver version is compatible with Python version",
                "Update database drivers to compatible versions",
                "Review compatibility matrix in documentation"
            ],
            DatabaseErrorCategory.POOL_EXHAUSTION: [
                f"Increase {component} connection pool size limits",
                "Check for connection leaks in application code",
                "Implement proper connection cleanup",
                "Monitor connection usage patterns"
            ],
            DatabaseErrorCategory.NETWORK_ERROR: [
                f"Verify {component} server hostname/IP address is correct",
                "Check network connectivity and DNS resolution",
                "Verify firewall rules allow database connections",
                f"Test connectivity using {component} client tools"
            ],
            DatabaseErrorCategory.CONFIGURATION_ERROR: [
                f"Review {component} database configuration parameters",
                "Check environment variables are set correctly",
                "Validate configuration file syntax",
                "Compare with working configuration examples"
            ],
            DatabaseErrorCategory.MIGRATION_ERROR: [
                f"Review {component} migration file syntax and content",
                "Check database schema compatibility",
                "Verify migration dependencies are met",
                "Test migration on development database first"
            ],
            DatabaseErrorCategory.HEALTH_CHECK_ERROR: [
                f"Check {component} database service status and availability",
                "Verify health check query syntax",
                "Review health check timeout settings",
                "Monitor database performance metrics"
            ]
        }
        
        return base_steps.get(category, [
            f"Check {component} database service status and configuration",
            "Review error logs for additional details",
            "Consult database documentation for specific error codes",
            "Contact system administrator if issue persists"
        ])

    @staticmethod
    def log_database_error(
        error_info: DatabaseErrorInfo,
        logger: Optional[logging.Logger] = None,
        include_details: bool = True
    ) -> None:
        """
        Log database error with comprehensive details and security masking.
        
        Args:
            error_info: Structured database error information
            logger: Optional logger instance (uses class logger if not provided)
            include_details: Whether to include detailed error information
            
        Validates Requirements: 5.1, 5.3
        """
        if logger is None:
            logger = ErrorReporter._logger
        
        # Add error to statistics
        ErrorReporter._error_statistics.add_error(error_info)
        
        # Create log message
        log_message = f"Database error in {error_info.component}: {error_info.message}"
        
        # Create extra fields for structured logging
        extra_fields = {
            'error_category': error_info.category.value,
            'component': error_info.component,
            'timestamp': error_info.timestamp.isoformat(),
            'error_count': ErrorReporter._error_statistics.error_counts.get(error_info.category, 0)
        }
        
        if error_info.error_code:
            extra_fields['error_code'] = error_info.error_code
        
        if include_details and error_info.details:
            # Mask any remaining sensitive data in details
            masked_details = {}
            for key, value in error_info.details.items():
                if isinstance(value, str):
                    masked_details[key] = ErrorReporter.mask_sensitive_data(value)
                else:
                    masked_details[key] = value
            extra_fields['error_details'] = masked_details
        
        # Log the error
        logger.error(log_message, extra=extra_fields)
        
        # Log resolution steps as info
        if error_info.resolution_steps:
            resolution_message = f"Resolution steps for {error_info.component} {error_info.category.value}:"
            logger.info(resolution_message)
            for i, step in enumerate(error_info.resolution_steps, 1):
                logger.info(f"  {i}. {step}")

    @staticmethod
    def get_error_statistics() -> ErrorStatistics:
        """
        Get current error statistics for pattern identification.
        
        Returns:
            ErrorStatistics with current error patterns
            
        Validates Requirements: 5.5
        """
        return ErrorReporter._error_statistics

    @staticmethod
    def format_error_statistics_report() -> str:
        """
        Format error statistics into a human-readable report.
        
        Returns:
            Formatted error statistics report
            
        Validates Requirements: 5.5
        """
        stats = ErrorReporter._error_statistics
        
        if not stats.error_counts:
            return "No database errors recorded."
        
        report = "Database Error Statistics Report\n"
        report += "=" * 50 + "\n\n"
        
        # Time range
        if stats.first_seen and stats.last_seen:
            report += f"Time Range: {stats.first_seen.isoformat()} to {stats.last_seen.isoformat()}\n"
            report += f"Total Errors: {sum(stats.error_counts.values())}\n\n"
        
        # Error categories
        report += "Error Categories:\n"
        for category, count in sorted(stats.error_counts.items(), key=lambda x: x[1], reverse=True):
            report += f"  {category.value}: {count}\n"
        report += "\n"
        
        # Component errors
        if stats.component_errors:
            report += "Errors by Component:\n"
            for component, count in sorted(stats.component_errors.items(), key=lambda x: x[1], reverse=True):
                report += f"  {component}: {count}\n"
            report += "\n"
        
        # Most frequent issues
        most_frequent = stats.get_most_frequent_category()
        most_problematic = stats.get_most_problematic_component()
        
        if most_frequent:
            report += f"Most Frequent Error Type: {most_frequent.value}\n"
        if most_problematic:
            report += f"Most Problematic Component: {most_problematic}\n"
        
        # Recent errors summary
        if stats.recent_errors:
            report += f"\nRecent Errors (last {len(stats.recent_errors)}):\n"
            for error in stats.recent_errors[-5:]:  # Show last 5
                report += f"  {error.timestamp.strftime('%H:%M:%S')} - {error.component}: {error.category.value}\n"
        
        return report

    @staticmethod
    def format_structured_error_message(
        error_info: DatabaseErrorInfo,
        include_resolution_steps: bool = True,
        include_context: bool = True
    ) -> str:
        """
        Format a structured error message with comprehensive information.
        
        Args:
            error_info: Database error information
            include_resolution_steps: Whether to include resolution steps
            include_context: Whether to include error context and details
            
        Returns:
            Formatted structured error message
            
        Validates Requirements: 5.4
        """
        message = f"DATABASE ERROR REPORT\n"
        message += "=" * 50 + "\n\n"
        
        # Error summary
        message += f"Component: {error_info.component}\n"
        message += f"Category: {error_info.category.value.replace('_', ' ').title()}\n"
        message += f"Timestamp: {error_info.timestamp.isoformat()}\n"
        
        if error_info.error_code:
            message += f"Error Code: {error_info.error_code}\n"
        
        message += f"Message: {error_info.message}\n\n"
        
        # Error context and details
        if include_context and error_info.details:
            message += "Error Details:\n"
            message += "-" * 20 + "\n"
            
            for key, value in error_info.details.items():
                if key == 'connection_params' and isinstance(value, dict):
                    message += f"{key}:\n"
                    for param_key, param_value in value.items():
                        message += f"  {param_key}: {param_value}\n"
                else:
                    message += f"{key}: {value}\n"
            message += "\n"
        
        # Resolution steps
        if include_resolution_steps and error_info.resolution_steps:
            message += "Resolution Steps:\n"
            message += "-" * 20 + "\n"
            for i, step in enumerate(error_info.resolution_steps, 1):
                message += f"{i}. {step}\n"
            message += "\n"
        
        # Error pattern analysis
        stats = ErrorReporter.get_error_statistics()
        category_count = stats.error_counts.get(error_info.category, 0)
        component_count = stats.component_errors.get(error_info.component, 0)
        
        if category_count > 1 or component_count > 1:
            message += "Pattern Analysis:\n"
            message += "-" * 20 + "\n"
            if category_count > 1:
                message += f"This error type has occurred {category_count} times\n"
            if component_count > 1:
                message += f"Component {error_info.component} has {component_count} total errors\n"
            
            # Suggest pattern-based actions
            if category_count >= 3:
                message += f"⚠️  Frequent {error_info.category.value} errors detected - consider investigating root cause\n"
            if component_count >= 5:
                message += f"⚠️  Component {error_info.component} showing high error rate - review configuration\n"
            message += "\n"
        
        return message

    @staticmethod
    def get_error_pattern_analysis() -> Dict[str, Any]:
        """
        Analyze error patterns and provide insights for troubleshooting.
        
        Returns:
            Dictionary containing pattern analysis results
            
        Validates Requirements: 5.5
        """
        stats = ErrorReporter.get_error_statistics()
        
        if not stats.error_counts:
            return {"status": "no_errors", "message": "No errors to analyze"}
        
        total_errors = sum(stats.error_counts.values())
        analysis = {
            "total_errors": total_errors,
            "unique_categories": len(stats.error_counts),
            "unique_components": len(stats.component_errors),
            "time_span_hours": 0,
            "patterns": [],
            "recommendations": []
        }
        
        # Calculate time span
        if stats.first_seen and stats.last_seen:
            time_diff = stats.last_seen - stats.first_seen
            analysis["time_span_hours"] = round(time_diff.total_seconds() / 3600, 2)
        
        # Identify patterns
        most_frequent_category = stats.get_most_frequent_category()
        most_problematic_component = stats.get_most_problematic_component()
        
        if most_frequent_category:
            category_count = stats.error_counts[most_frequent_category]
            category_percentage = round((category_count / total_errors) * 100, 1)
            analysis["patterns"].append({
                "type": "frequent_error_category",
                "category": most_frequent_category.value,
                "count": category_count,
                "percentage": category_percentage
            })
            
            # Add category-specific recommendations
            if category_percentage > 50:
                analysis["recommendations"].append(
                    f"Focus on resolving {most_frequent_category.value} errors - they represent {category_percentage}% of all issues"
                )
        
        if most_problematic_component:
            component_count = stats.component_errors[most_problematic_component]
            component_percentage = round((component_count / total_errors) * 100, 1)
            analysis["patterns"].append({
                "type": "problematic_component",
                "component": most_problematic_component,
                "count": component_count,
                "percentage": component_percentage
            })
            
            if component_percentage > 60:
                analysis["recommendations"].append(
                    f"Review {most_problematic_component} configuration - it accounts for {component_percentage}% of errors"
                )
        
        # Identify error bursts (multiple errors in short time)
        if len(stats.recent_errors) >= 5:
            recent_timestamps = [error.timestamp for error in stats.recent_errors[-5:]]
            if len(recent_timestamps) >= 2:
                time_span = (recent_timestamps[-1] - recent_timestamps[0]).total_seconds()
                if time_span < 300:  # 5 minutes
                    analysis["patterns"].append({
                        "type": "error_burst",
                        "count": len(recent_timestamps),
                        "time_span_seconds": time_span
                    })
                    analysis["recommendations"].append(
                        "Recent error burst detected - check for system instability or configuration changes"
                    )
        
        # Check for recurring patterns
        category_diversity = len(stats.error_counts) / max(1, total_errors)
        if category_diversity < 0.3 and total_errors >= 5:
            analysis["patterns"].append({
                "type": "low_error_diversity",
                "diversity_ratio": round(category_diversity, 2)
            })
            analysis["recommendations"].append(
                "Low error diversity suggests systematic issue - focus on most common error type"
            )
        
        return analysis

    @staticmethod
    def export_error_statistics(format_type: str = "json") -> str:
        """
        Export error statistics in various formats for external analysis.
        
        Args:
            format_type: Export format ("json", "csv", "summary")
            
        Returns:
            Formatted error statistics data
            
        Validates Requirements: 5.5
        """
        stats = ErrorReporter.get_error_statistics()
        
        if format_type.lower() == "json":
            import json
            export_data = {
                "error_counts": {cat.value: count for cat, count in stats.error_counts.items()},
                "component_errors": stats.component_errors,
                "total_errors": sum(stats.error_counts.values()),
                "first_seen": stats.first_seen.isoformat() if stats.first_seen else None,
                "last_seen": stats.last_seen.isoformat() if stats.last_seen else None,
                "recent_errors": [
                    {
                        "timestamp": error.timestamp.isoformat(),
                        "component": error.component,
                        "category": error.category.value,
                        "message": error.message
                    }
                    for error in stats.recent_errors
                ]
            }
            return json.dumps(export_data, indent=2)
        
        elif format_type.lower() == "csv":
            lines = ["Category,Component,Count,Percentage"]
            total_errors = sum(stats.error_counts.values())
            
            for category, count in stats.error_counts.items():
                percentage = round((count / total_errors) * 100, 1) if total_errors > 0 else 0
                lines.append(f"{category.value},,{count},{percentage}")
            
            lines.append("")  # Empty line separator
            lines.append("Component,Category,Count,Percentage")
            
            for component, count in stats.component_errors.items():
                percentage = round((count / total_errors) * 100, 1) if total_errors > 0 else 0
                lines.append(f"{component},,{count},{percentage}")
            
            return "\n".join(lines)
        
        elif format_type.lower() == "summary":
            return ErrorReporter.format_error_statistics_report()
        
        else:
            raise ValueError(f"Unsupported format type: {format_type}")

    @staticmethod
    def clear_old_error_statistics(hours_threshold: int = 24) -> int:
        """
        Clear error statistics older than the specified threshold.
        
        Args:
            hours_threshold: Remove errors older than this many hours
            
        Returns:
            Number of errors removed
            
        Validates Requirements: 5.5
        """
        stats = ErrorReporter.get_error_statistics()
        
        if not stats.recent_errors:
            return 0
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_threshold)
        original_count = len(stats.recent_errors)
        
        # Filter out old errors
        stats.recent_errors = [
            error for error in stats.recent_errors
            if error.timestamp > cutoff_time
        ]
        
        # Recalculate statistics based on remaining errors
        if stats.recent_errors:
            # Rebuild counts from remaining errors
            new_error_counts = {}
            new_component_errors = {}
            
            for error in stats.recent_errors:
                new_error_counts[error.category] = new_error_counts.get(error.category, 0) + 1
                new_component_errors[error.component] = new_component_errors.get(error.component, 0) + 1
            
            stats.error_counts = new_error_counts
            stats.component_errors = new_component_errors
            stats.first_seen = min(error.timestamp for error in stats.recent_errors)
            stats.last_seen = max(error.timestamp for error in stats.recent_errors)
        else:
            # No errors remaining
            stats.error_counts.clear()
            stats.component_errors.clear()
            stats.first_seen = None
            stats.last_seen = None
        
        return original_count - len(stats.recent_errors)

    @staticmethod
    def reset_error_statistics() -> None:
        """
        Reset error statistics (useful for testing or periodic cleanup).
        
        Validates Requirements: 5.5
        """
        ErrorReporter._error_statistics = ErrorStatistics()

    @staticmethod
    def format_database_connection_error(
        service: str,
        error: Exception,
        connection_string: Optional[str] = None,
        is_critical: bool = True,
        retry_count: int = 0
    ) -> str:
        """
        Format comprehensive database connection error with classification.
        
        Args:
            service: Name of the database service
            error: The exception that occurred
            connection_string: Optional connection string (will be masked)
            is_critical: Whether this is a critical error
            retry_count: Number of retry attempts made
            
        Returns:
            Formatted error message with classification and resolution steps
            
        Validates Requirements: 5.1, 5.2, 5.3
        """
        # Create structured error info
        connection_params = {'connection_string': connection_string} if connection_string else None
        error_info = ErrorReporter.create_database_error_info(error, service, connection_params)
        
        # Log the error
        ErrorReporter.log_database_error(error_info)
        
        # Format the error message
        severity = "ERROR" if is_critical else "WARNING"
        message = f"{severity}: Cannot connect to {service}\n"
        message += f"Error Category: {error_info.category.value}\n"
        
        if connection_string:
            masked_connection = ErrorReporter.mask_connection_string(connection_string)
            masked_connection = ErrorReporter.mask_sensitive_data(masked_connection)
            message += f"Connection: {masked_connection}\n"
        
        if retry_count > 0:
            message += f"Retry Attempts: {retry_count}\n"
        
        # Add error details
        masked_error = ErrorReporter.mask_sensitive_data(str(error))
        message += f"Error: {masked_error}\n"
        
        # Add resolution steps
        message += "\nResolution Steps:\n"
        for i, step in enumerate(error_info.resolution_steps, 1):
            message += f"{i}. {step}\n"
        
        return message
