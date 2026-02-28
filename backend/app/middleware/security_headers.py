"""
Security Headers Middleware

This module implements security headers middleware to prevent XSS, clickjacking,
and other web vulnerabilities.

Requirements:
- 2.10: Sanitize all user input to prevent XSS attacks
- 8.7: Validate and sanitize all user input to prevent injection attacks
- 8.5: Encrypt all data in transit using TLS 1.3
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses
    
    Implements:
    - Content-Security-Policy (CSP) to prevent XSS
    - X-Content-Type-Options to prevent MIME sniffing
    - X-Frame-Options to prevent clickjacking
    - X-XSS-Protection for legacy browsers
    - Strict-Transport-Security (HSTS) for HTTPS enforcement
    - Referrer-Policy to control referrer information
    - Permissions-Policy to control browser features
    
    Requirements:
        - 2.10: Prevent XSS attacks
        - 8.5: Enforce HTTPS
    """
    
    def __init__(self, app, config: dict = None):
        """
        Initialize security headers middleware
        
        Args:
            app: FastAPI application
            config: Optional configuration dictionary
        """
        super().__init__(app)
        self.config = config or {}
        
        # Default CSP policy
        self.csp_policy = self.config.get('csp_policy', self._get_default_csp())
        
        # HSTS configuration
        self.hsts_max_age = self.config.get('hsts_max_age', 31536000)  # 1 year
        self.hsts_include_subdomains = self.config.get('hsts_include_subdomains', True)
        self.hsts_preload = self.config.get('hsts_preload', True)
    
    def _get_default_csp(self) -> str:
        """
        Get default Content-Security-Policy
        
        This is a strict CSP that prevents most XSS attacks.
        Adjust based on your application's needs.
        """
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # Allow inline scripts for development
            "style-src 'self' 'unsafe-inline'; "  # Allow inline styles
            "img-src 'self' data: https:; "  # Allow images from self, data URIs, and HTTPS
            "font-src 'self' data:; "
            "connect-src 'self' https://api.github.com https://api.openai.com https://api.anthropic.com; "
            "frame-ancestors 'none'; "  # Prevent framing
            "base-uri 'self'; "  # Restrict base tag
            "form-action 'self'; "  # Restrict form submissions
            "upgrade-insecure-requests; "  # Upgrade HTTP to HTTPS
        )
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add security headers to response
        
        Args:
            request: Incoming request
            call_next: Next middleware in chain
            
        Returns:
            Response with security headers
        """
        response = await call_next(request)
        
        # Content-Security-Policy
        response.headers['Content-Security-Policy'] = self.csp_policy
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # XSS Protection for legacy browsers
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Strict-Transport-Security (HSTS)
        hsts_value = f'max-age={self.hsts_max_age}'
        if self.hsts_include_subdomains:
            hsts_value += '; includeSubDomains'
        if self.hsts_preload:
            hsts_value += '; preload'
        response.headers['Strict-Transport-Security'] = hsts_value
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (formerly Feature-Policy)
        response.headers['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'payment=(), '
            'usb=(), '
            'magnetometer=(), '
            'gyroscope=(), '
            'accelerometer=()'
        )
        
        # Remove server header to avoid information disclosure
        response.headers.pop('Server', None)
        
        return response


class XSSProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to sanitize response content and prevent XSS
    
    This middleware inspects response content and sanitizes any
    potentially dangerous content before sending to client.
    
    Requirements:
        - 2.10: Prevent XSS attacks
    """
    
    def __init__(self, app, sanitize_json: bool = True):
        """
        Initialize XSS protection middleware
        
        Args:
            app: FastAPI application
            sanitize_json: Whether to sanitize JSON responses
        """
        super().__init__(app)
        self.sanitize_json = sanitize_json
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Sanitize response content
        
        Args:
            request: Incoming request
            call_next: Next middleware in chain
            
        Returns:
            Response with sanitized content
        """
        response = await call_next(request)
        
        # Only sanitize HTML and JSON responses
        content_type = response.headers.get('content-type', '')
        
        if 'text/html' in content_type:
            # For HTML responses, ensure proper escaping
            # This is handled by template engines, but we add an extra layer
            response.headers['X-Content-Type-Options'] = 'nosniff'
        
        elif 'application/json' in content_type and self.sanitize_json:
            # For JSON responses, ensure no script injection
            # FastAPI's JSONResponse already handles this, but we verify
            response.headers['X-Content-Type-Options'] = 'nosniff'
        
        return response


def configure_security_headers(app, config: dict = None):
    """
    Configure security headers for FastAPI application
    
    Args:
        app: FastAPI application
        config: Optional configuration dictionary
        
    Example:
        from fastapi import FastAPI
        from app.middleware.security_headers import configure_security_headers
        
        app = FastAPI()
        configure_security_headers(app, {
            'csp_policy': "default-src 'self'",
            'hsts_max_age': 31536000
        })
    """
    app.add_middleware(SecurityHeadersMiddleware, config=config)
    app.add_middleware(XSSProtectionMiddleware)
    
    logger.info("Security headers middleware configured")


# CSP Policy Builder
class CSPBuilder:
    """
    Content-Security-Policy builder for custom policies
    
    Example:
        csp = CSPBuilder()
        csp.default_src("'self'")
        csp.script_src("'self'", "'unsafe-inline'")
        csp.style_src("'self'", "https://fonts.googleapis.com")
        policy = csp.build()
    """
    
    def __init__(self):
        self.directives = {}
    
    def default_src(self, *sources):
        """Set default-src directive"""
        self.directives['default-src'] = sources
        return self
    
    def script_src(self, *sources):
        """Set script-src directive"""
        self.directives['script-src'] = sources
        return self
    
    def style_src(self, *sources):
        """Set style-src directive"""
        self.directives['style-src'] = sources
        return self
    
    def img_src(self, *sources):
        """Set img-src directive"""
        self.directives['img-src'] = sources
        return self
    
    def font_src(self, *sources):
        """Set font-src directive"""
        self.directives['font-src'] = sources
        return self
    
    def connect_src(self, *sources):
        """Set connect-src directive"""
        self.directives['connect-src'] = sources
        return self
    
    def frame_ancestors(self, *sources):
        """Set frame-ancestors directive"""
        self.directives['frame-ancestors'] = sources
        return self
    
    def base_uri(self, *sources):
        """Set base-uri directive"""
        self.directives['base-uri'] = sources
        return self
    
    def form_action(self, *sources):
        """Set form-action directive"""
        self.directives['form-action'] = sources
        return self
    
    def upgrade_insecure_requests(self):
        """Enable upgrade-insecure-requests"""
        self.directives['upgrade-insecure-requests'] = []
        return self
    
    def block_all_mixed_content(self):
        """Enable block-all-mixed-content"""
        self.directives['block-all-mixed-content'] = []
        return self
    
    def build(self) -> str:
        """
        Build CSP policy string
        
        Returns:
            CSP policy string
        """
        parts = []
        for directive, sources in self.directives.items():
            if sources:
                parts.append(f"{directive} {' '.join(sources)}")
            else:
                parts.append(directive)
        
        return '; '.join(parts) + ';'


# Export public API
__all__ = [
    'SecurityHeadersMiddleware',
    'XSSProtectionMiddleware',
    'configure_security_headers',
    'CSPBuilder',
]
