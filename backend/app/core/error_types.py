"""
Error Types and Enums for Error Reporting

This module defines error-related enums, data classes, and type definitions
used throughout the error reporting system.

Validates Requirements: 1.6, 5.1, 5.2
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional


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
        self.error_counts[error_info.category] = self.error_counts.get(error_info.category, 0) + 1
        self.component_errors[error_info.component] = self.component_errors.get(error_info.component, 0) + 1
        
        if self.first_seen is None:
            self.first_seen = error_info.timestamp
        self.last_seen = error_info.timestamp
        
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
    pattern: str
    replacement: str
    data_type: SensitiveDataType
    show_first: int = 0
    show_last: int = 0
