"""
Shared utility functions for enterprise_rbac_auth.
"""
from fastapi import Request


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.
    
    Supports X-Forwarded-For header for proxied requests.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address or "0.0.0.0" if unavailable
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"
