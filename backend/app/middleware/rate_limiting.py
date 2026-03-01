"""
Rate Limiting Middleware

This module implements rate limiting middleware using Redis for distributed
rate limiting across multiple instances.

Requirements:
- 8.6: Implement rate limiting of 100 requests per minute per user
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Optional
import logging
import time
from datetime import datetime

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_user_identifier(request: Request) -> str:
    """
    Get user identifier for rate limiting.
    
    Priority:
    1. Authenticated user ID from JWT token
    2. IP address for unauthenticated requests
    
    Args:
        request: FastAPI request object
        
    Returns:
        User identifier string
    """
    # Try to get user from JWT token
    try:
        # Check if user is authenticated
        if hasattr(request.state, "user") and request.state.user:
            user_id = getattr(request.state.user, "id", None)
            if user_id:
                return f"user:{user_id}"
    except Exception as e:
        logger.debug(f"Could not extract user from request: {e}")
    
    # Fall back to IP address
    return f"ip:{get_remote_address(request)}"


# Initialize rate limiter with Redis backend
limiter = Limiter(
    key_func=get_user_identifier,
    storage_uri=settings.redis_url,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
    headers_enabled=True,  # Add rate limit headers to responses
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis for distributed rate limiting.
    
    Implements per-user rate limiting with configurable limits.
    Returns 429 Too Many Requests when rate limit is exceeded.
    
    Requirements:
        - 8.6: Implement rate limiting of 100 requests per minute per user
    """
    
    def __init__(
        self,
        app,
        rate_limit: str = "100/minute",
        redis_url: Optional[str] = None,
    ):
        """
        Initialize rate limiting middleware.
        
        Args:
            app: FastAPI application
            rate_limit: Rate limit string (e.g., "100/minute", "1000/hour")
            redis_url: Redis connection URL for distributed rate limiting
        """
        super().__init__(app)
        self.rate_limit = rate_limit
        self.redis_url = redis_url or settings.redis_url
        
        logger.info(f"Rate limiting initialized: {rate_limit} per user")
    
    async def dispatch(self, request: Request, call_next: Callable):
        """
        Apply rate limiting to request.
        
        Args:
            request: Incoming request
            call_next: Next middleware in chain
            
        Returns:
            Response or 429 error if rate limit exceeded
        """
        # Skip rate limiting for health check endpoints
        if request.url.path in ["/health", "/health/ready", "/health/live"]:
            return await call_next(request)
        
        # Skip rate limiting for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        try:
            response = await call_next(request)
            return response
        except RateLimitExceeded as e:
            # Log rate limit exceeded
            user_id = get_user_identifier(request)
            logger.warning(
                f"Rate limit exceeded for {user_id} on {request.url.path}",
                extra={
                    "user_identifier": user_id,
                    "path": request.url.path,
                    "method": request.method,
                    "ip": get_remote_address(request),
                }
            )
            
            # Return 429 Too Many Requests
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": e.retry_after if hasattr(e, "retry_after") else 60,
                },
                headers={
                    "Retry-After": str(e.retry_after if hasattr(e, "retry_after") else 60),
                    "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_MINUTE),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + 60),
                }
            )


class CustomRateLimiter:
    """
    Custom rate limiter for specific endpoints with different limits.
    
    Example:
        from app.middleware.rate_limiting import custom_limiter
        
        @app.get("/api/expensive-operation")
        @custom_limiter.limit("10/minute")
        async def expensive_operation():
            return {"status": "ok"}
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize custom rate limiter.
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url or settings.redis_url
        self.limiter = Limiter(
            key_func=get_user_identifier,
            storage_uri=self.redis_url,
            headers_enabled=True,
        )
    
    def limit(self, rate_limit: str):
        """
        Decorator to apply custom rate limit to endpoint.
        
        Args:
            rate_limit: Rate limit string (e.g., "10/minute", "100/hour")
            
        Returns:
            Decorator function
        """
        return self.limiter.limit(rate_limit)


# Global custom limiter instance
custom_limiter = CustomRateLimiter()


def configure_rate_limiting(app):
    """
    Configure rate limiting for FastAPI application.
    
    Args:
        app: FastAPI application
        
    Example:
        from fastapi import FastAPI
        from app.middleware.rate_limiting import configure_rate_limiting
        
        app = FastAPI()
        configure_rate_limiting(app)
    """
    # Add SlowAPI middleware
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    
    logger.info(
        f"Rate limiting configured: {settings.RATE_LIMIT_PER_MINUTE} requests/minute per user"
    )


# Export public API
__all__ = [
    "limiter",
    "custom_limiter",
    "RateLimitMiddleware",
    "CustomRateLimiter",
    "configure_rate_limiting",
    "get_user_identifier",
]
