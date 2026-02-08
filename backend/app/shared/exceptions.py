"""
Custom exceptions for the platform

Provides structured exception hierarchy for better error handling
and reporting across all services.

Validates Requirements: 1.8, 7.6
"""

from typing import Optional, Dict, Any


class ServiceException(Exception):
    """Base exception for all service errors"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class LLMProviderException(ServiceException):
    """Exception for LLM provider errors"""
    
    def __init__(
        self,
        message: str,
        provider: str,
        model: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)
        self.provider = provider
        self.model = model


class CircuitBreakerException(ServiceException):
    """Exception when circuit breaker is open"""
    
    def __init__(
        self,
        message: str,
        service_name: str,
        failure_count: int,
        error_code: Optional[str] = "CIRCUIT_OPEN",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)
        self.service_name = service_name
        self.failure_count = failure_count


class CacheException(ServiceException):
    """Exception for cache operations"""
    
    def __init__(
        self,
        message: str,
        operation: str,
        key: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)
        self.operation = operation
        self.key = key


class DatabaseException(ServiceException):
    """Exception for database operations"""
    
    def __init__(
        self,
        message: str,
        database: str,
        operation: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)
        self.database = database
        self.operation = operation


class ValidationException(ServiceException):
    """Exception for validation errors"""
    
    def __init__(
        self,
        message: str,
        field: str,
        value: Optional[Any] = None,
        error_code: Optional[str] = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)
        self.field = field
        self.value = value


class AuthenticationException(ServiceException):
    """Exception for authentication errors"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = "AUTH_FAILED",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class AuthorizationException(ServiceException):
    """Exception for authorization errors"""
    
    def __init__(
        self,
        message: str,
        resource: str,
        action: str,
        error_code: Optional[str] = "FORBIDDEN",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)
        self.resource = resource
        self.action = action
