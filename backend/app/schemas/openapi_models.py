"""
OpenAPI documentation models for standardized responses.

These models are used to document common response patterns in the OpenAPI specification.
"""
from typing import Optional, Any, Dict, List
from datetime import datetime
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str = Field(..., description="Human-readable error message")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")
    timestamp: Optional[str] = Field(None, description="ISO 8601 timestamp of the error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Resource not found",
                "error_code": "RESOURCE_NOT_FOUND",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class ValidationErrorDetail(BaseModel):
    """Validation error detail."""
    loc: List[str] = Field(..., description="Location of the error in the request")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ValidationErrorResponse(BaseModel):
    """Validation error response (422)."""
    detail: List[ValidationErrorDetail] = Field(..., description="List of validation errors")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": [
                    {
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address",
                        "type": "value_error.email"
                    }
                ]
            }
        }


class UnauthorizedResponse(BaseModel):
    """Unauthorized error response (401)."""
    detail: str = Field(default="Not authenticated", description="Error message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Not authenticated"
            }
        }


class ForbiddenResponse(BaseModel):
    """Forbidden error response (403)."""
    detail: str = Field(default="Insufficient permissions", description="Error message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Insufficient permissions"
            }
        }


class NotFoundResponse(BaseModel):
    """Not found error response (404)."""
    detail: str = Field(default="Resource not found", description="Error message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Resource not found"
            }
        }


class RateLimitResponse(BaseModel):
    """Rate limit exceeded response (429)."""
    detail: str = Field(default="Too many requests", description="Error message")
    retry_after: Optional[int] = Field(None, description="Seconds until rate limit resets")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Too many requests. Please try again later.",
                "retry_after": 60
            }
        }


class InternalServerErrorResponse(BaseModel):
    """Internal server error response (500)."""
    detail: str = Field(default="Internal server error", description="Error message")
    error_id: Optional[str] = Field(None, description="Error tracking ID for support")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Internal server error",
                "error_id": "err_abc123xyz"
            }
        }


class ServiceUnavailableResponse(BaseModel):
    """Service unavailable response (503)."""
    detail: str = Field(default="Service temporarily unavailable", description="Error message")
    retry_after: Optional[int] = Field(None, description="Seconds until service may be available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Service temporarily unavailable",
                "retry_after": 300
            }
        }


# Common response documentation for reuse across endpoints
COMMON_RESPONSES = {
    400: {
        "model": ErrorResponse,
        "description": "Bad Request - Invalid input parameters"
    },
    401: {
        "model": UnauthorizedResponse,
        "description": "Unauthorized - Missing or invalid authentication token"
    },
    403: {
        "model": ForbiddenResponse,
        "description": "Forbidden - Insufficient permissions for this operation"
    },
    404: {
        "model": NotFoundResponse,
        "description": "Not Found - Requested resource does not exist"
    },
    422: {
        "model": ValidationErrorResponse,
        "description": "Validation Error - Request data failed validation"
    },
    429: {
        "model": RateLimitResponse,
        "description": "Too Many Requests - Rate limit exceeded"
    },
    500: {
        "model": InternalServerErrorResponse,
        "description": "Internal Server Error - Unexpected server error"
    },
    503: {
        "model": ServiceUnavailableResponse,
        "description": "Service Unavailable - Service temporarily unavailable"
    }
}


# Authentication-specific responses
AUTH_RESPONSES = {
    **COMMON_RESPONSES,
    401: {
        "model": UnauthorizedResponse,
        "description": "Unauthorized - Invalid credentials or expired token"
    }
}


# Protected endpoint responses (requires authentication)
PROTECTED_RESPONSES = {
    **COMMON_RESPONSES,
    401: {
        "model": UnauthorizedResponse,
        "description": "Unauthorized - Authentication required"
    },
    403: {
        "model": ForbiddenResponse,
        "description": "Forbidden - Insufficient permissions"
    }
}
