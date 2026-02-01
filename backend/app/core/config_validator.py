"""
Configuration Validator for Backend-Frontend Connectivity

Validates environment configuration to ensure reliable connectivity between
the Next.js frontend and FastAPI backend. Checks for:
- Required environment variables
- Port conflicts between services
- URL format validation and accessibility
- Configuration consistency

Validates Requirements: 10.1, 10.2, 10.3, 10.4
"""

import logging
import os
import re
import socket
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from urllib.parse import urlparse

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """
    Result of configuration validation.
    
    Attributes:
        is_valid: Whether all validation checks passed
        errors: List of validation errors
        warnings: List of validation warnings
        config_summary: Summary of validated configuration
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    config_summary: Dict[str, str] = field(default_factory=dict)
    
    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings"""
        return len(self.warnings) > 0


@dataclass
class PortConfig:
    """Configuration for a service port"""
    service: str
    port: int
    url: str


class ConfigValidator:
    """
    Configuration validator for backend-frontend connectivity.
    
    Validates:
    - Required environment variables are present and non-empty
    - Port configurations are consistent and conflict-free
    - URL formats are valid and services are accessible
    - Configuration consistency across environment files
    
    Validates Requirements: 10.1, 10.2, 10.3, 10.4
    """
    
    def __init__(self):
        """Initialize configuration validator"""
        self.result = ValidationResult(is_valid=True)
    
    def validate_all(self) -> ValidationResult:
        """
        Validate all configuration settings.
        
        Returns:
            ValidationResult with all validation results
            
        Validates Requirements: 10.1
        """
        logger.info("Starting configuration validation...")
        
        # Run all validation checks
        self.validate_required_vars()
        self.validate_port_conflicts()
        self.validate_urls()
        
        # Determine overall validity
        self.result.is_valid = not self.result.has_errors()
        
        # Generate configuration summary
        self._generate_config_summary()
        
        logger.info(f"Configuration validation complete: {'✅ PASSED' if self.result.is_valid else '❌ FAILED'}")
        
        return self.result
    
    def validate_required_vars(self) -> List[str]:
        """
        Check all required environment variables are set.
        
        Returns:
            List of missing variable names
            
        Validates Requirements: 10.2
        """
        logger.info("Validating required environment variables...")
        missing_vars = []
        
        # Required variables for backend-frontend connectivity
        required_vars = {
            # Security
            "JWT_SECRET": "JWT signing secret (minimum 32 characters)",
            "SECRET_KEY": "Application secret key",
            
            # Database - PostgreSQL (critical)
            "POSTGRES_HOST": "PostgreSQL host",
            "POSTGRES_PORT": "PostgreSQL port",
            "POSTGRES_DB": "PostgreSQL database name",
            "POSTGRES_USER": "PostgreSQL username",
            "POSTGRES_PASSWORD": "PostgreSQL password",
            
            # Database - Neo4j (critical)
            "NEO4J_URI": "Neo4j connection URI",
            "NEO4J_USER": "Neo4j username",
            "NEO4J_PASSWORD": "Neo4j password",
            
            # Database - Redis (critical)
            "REDIS_HOST": "Redis host",
            "REDIS_PORT": "Redis port",
            
            # Frontend connectivity
            "NEXT_PUBLIC_API_URL": "Frontend API URL for backend connectivity",
        }
        
        for var_name, description in required_vars.items():
            # Check if variable exists in environment first
            value = os.environ.get(var_name)
            
            # If not in environment, check settings object (which loads from .env file)
            if value is None:
                try:
                    value = getattr(settings, var_name, None)
                except Exception:
                    value = None
            
            # Check if value is missing or empty
            is_missing = False
            if value is None:
                is_missing = True
            elif isinstance(value, str) and not value.strip():
                is_missing = True
            elif isinstance(value, int) and value == 0 and var_name not in ["REDIS_DB"]:
                # Port 0 is invalid (except for REDIS_DB which can be 0)
                is_missing = True
            
            if is_missing:
                error_msg = f"Missing required environment variable: {var_name} ({description})"
                self.result.errors.append(error_msg)
                missing_vars.append(var_name)
                logger.error(error_msg)
            else:
                logger.debug(f"✅ {var_name} is set")
        
        # Validate variable formats
        self._validate_variable_formats()
        
        return missing_vars
    
    def _validate_variable_formats(self) -> None:
        """Validate format of environment variables"""
        # JWT_SECRET length validation
        jwt_secret = os.environ.get('JWT_SECRET') or getattr(settings, 'JWT_SECRET', '')
        if jwt_secret and len(jwt_secret) < 32:
            warning = (
                f"JWT_SECRET is only {len(jwt_secret)} characters "
                f"(minimum 32 recommended for security)"
            )
            self.result.warnings.append(warning)
            logger.warning(warning)
        
        # Port number validation
        port_vars = {}
        
        # Get POSTGRES_PORT
        postgres_port = os.environ.get('POSTGRES_PORT')
        if postgres_port:
            try:
                port_vars["POSTGRES_PORT"] = int(postgres_port)
            except ValueError:
                port_vars["POSTGRES_PORT"] = -1
        else:
            port_vars["POSTGRES_PORT"] = getattr(settings, 'POSTGRES_PORT', 5432)
        
        # Get REDIS_PORT
        redis_port = os.environ.get('REDIS_PORT')
        if redis_port:
            try:
                port_vars["REDIS_PORT"] = int(redis_port)
            except ValueError:
                port_vars["REDIS_PORT"] = -1
        else:
            port_vars["REDIS_PORT"] = getattr(settings, 'REDIS_PORT', 6379)
        
        for var_name, port_value in port_vars.items():
            if not isinstance(port_value, int) or port_value <= 0 or port_value > 65535:
                error_msg = f"Invalid port number for {var_name}: {port_value} (must be 1-65535)"
                self.result.errors.append(error_msg)
                logger.error(error_msg)
    
    def validate_port_conflicts(self) -> List[str]:
        """
        Check for port conflicts between services.
        
        Returns:
            List of conflicting port descriptions
            
        Validates Requirements: 10.3
        """
        logger.info("Validating port configurations...")
        conflicts = []
        
        # Define service ports
        service_ports: Dict[str, PortConfig] = {}
        
        # Backend port (from environment or default 8000)
        backend_port = int(os.environ.get("BACKEND_PORT", "8000"))
        service_ports["backend"] = PortConfig(
            service="Backend (FastAPI)",
            port=backend_port,
            url=f"http://localhost:{backend_port}"
        )
        
        # Frontend port (from environment or default 3000)
        frontend_port = int(os.environ.get("FRONTEND_PORT", "3000"))
        service_ports["frontend"] = PortConfig(
            service="Frontend (Next.js)",
            port=frontend_port,
            url=f"http://localhost:{frontend_port}"
        )
        
        # Database ports - get from environment or settings
        postgres_port = os.environ.get("POSTGRES_PORT")
        if postgres_port:
            try:
                postgres_port = int(postgres_port)
            except ValueError:
                postgres_port = 5432
        else:
            postgres_port = getattr(settings, 'POSTGRES_PORT', 5432)
        
        service_ports["postgres"] = PortConfig(
            service="PostgreSQL",
            port=postgres_port,
            url=f"{getattr(settings, 'POSTGRES_HOST', 'localhost')}:{postgres_port}"
        )
        
        redis_port = os.environ.get("REDIS_PORT")
        if redis_port:
            try:
                redis_port = int(redis_port)
            except ValueError:
                redis_port = 6379
        else:
            redis_port = getattr(settings, 'REDIS_PORT', 6379)
        
        service_ports["redis"] = PortConfig(
            service="Redis",
            port=redis_port,
            url=f"{getattr(settings, 'REDIS_HOST', 'localhost')}:{redis_port}"
        )
        
        # Neo4j port (extract from URI)
        neo4j_uri = os.environ.get("NEO4J_URI") or getattr(settings, 'NEO4J_URI', '')
        if neo4j_uri:
            neo4j_port = self._extract_port_from_uri(neo4j_uri, default=7687)
            service_ports["neo4j"] = PortConfig(
                service="Neo4j",
                port=neo4j_port,
                url=neo4j_uri
            )
        
        # Check for port conflicts
        port_to_services: Dict[int, List[str]] = {}
        for service_name, port_config in service_ports.items():
            port = port_config.port
            if port not in port_to_services:
                port_to_services[port] = []
            port_to_services[port].append(port_config.service)
        
        # Report conflicts
        for port, services in port_to_services.items():
            if len(services) > 1:
                conflict_msg = f"Port conflict detected: Port {port} is used by multiple services: {', '.join(services)}"
                self.result.errors.append(conflict_msg)
                conflicts.append(conflict_msg)
                logger.error(conflict_msg)
        
        # Validate backend port consistency
        self._validate_backend_port_consistency(backend_port)
        
        # Store port configuration in summary
        self.result.config_summary["ports"] = {
            service_name: f"{config.service} on port {config.port}"
            for service_name, config in service_ports.items()
        }
        
        return conflicts
    
    def _validate_backend_port_consistency(self, backend_port: int) -> None:
        """
        Validate that backend port is consistent across all configuration.
        
        Validates Requirements: 1.4
        """
        # Check NEXT_PUBLIC_API_URL contains the correct backend port
        api_url = os.environ.get("NEXT_PUBLIC_API_URL", "")
        if api_url:
            # Extract port from URL
            parsed = urlparse(api_url)
            url_port = parsed.port
            
            # If no explicit port, infer from scheme
            if url_port is None:
                if parsed.scheme == "https":
                    url_port = 443
                elif parsed.scheme == "http":
                    url_port = 80
            
            # Check if URL port matches backend port
            if url_port and url_port != backend_port:
                warning = (
                    f"Port mismatch: NEXT_PUBLIC_API_URL uses port {url_port} "
                    f"but backend is configured for port {backend_port}"
                )
                self.result.warnings.append(warning)
                logger.warning(warning)
    
    def _extract_port_from_uri(self, uri: str, default: int = 7687) -> int:
        """Extract port number from URI"""
        try:
            parsed = urlparse(uri)
            if parsed.port:
                return parsed.port
            return default
        except Exception:
            return default
    
    def validate_urls(self) -> List[str]:
        """
        Check URL formats and accessibility.
        
        Returns:
            List of URL validation errors
            
        Validates Requirements: 10.4
        """
        logger.info("Validating URL formats and accessibility...")
        errors = []
        
        # URLs to validate
        urls_to_check = {
            "NEXT_PUBLIC_API_URL": os.environ.get("NEXT_PUBLIC_API_URL", ""),
            "NEO4J_URI": settings.NEO4J_URI if hasattr(settings, 'NEO4J_URI') else "",
        }
        
        for var_name, url in urls_to_check.items():
            if not url:
                continue
            
            # Validate URL format
            if not self._is_valid_url_format(url):
                error_msg = f"Invalid URL format for {var_name}: {url}"
                self.result.errors.append(error_msg)
                errors.append(error_msg)
                logger.error(error_msg)
                continue
            
            # Check URL accessibility (for HTTP/HTTPS URLs only)
            parsed = urlparse(url)
            if parsed.scheme in ["http", "https"]:
                is_accessible, error = self._check_url_accessibility(url)
                if not is_accessible:
                    warning = f"URL may not be accessible: {var_name} ({url}): {error}"
                    self.result.warnings.append(warning)
                    logger.warning(warning)
        
        # Validate database connection strings
        self._validate_database_urls()
        
        return errors
    
    def _is_valid_url_format(self, url: str) -> bool:
        """Validate URL format"""
        try:
            parsed = urlparse(url)
            # Must have scheme and netloc (or path for some schemes)
            return bool(parsed.scheme and (parsed.netloc or parsed.path))
        except Exception:
            return False
    
    def _check_url_accessibility(self, url: str) -> tuple[bool, Optional[str]]:
        """
        Check if URL is accessible (basic connectivity check).
        
        Returns:
            Tuple of (is_accessible, error_message)
        """
        try:
            parsed = urlparse(url)
            host = parsed.hostname
            port = parsed.port
            
            if not host:
                return False, "No hostname in URL"
            
            # Infer port from scheme if not specified
            if port is None:
                if parsed.scheme == "https":
                    port = 443
                elif parsed.scheme == "http":
                    port = 80
                else:
                    return True, None  # Skip check for non-HTTP schemes
            
            # Try to connect to the host:port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)  # 2 second timeout
            
            try:
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    return True, None
                else:
                    return False, f"Connection refused (error code: {result})"
            except socket.gaierror:
                return False, "Hostname could not be resolved"
            except socket.timeout:
                return False, "Connection timeout"
            except Exception as e:
                return False, str(e)
                
        except Exception as e:
            return False, f"URL check failed: {str(e)}"
    
    def _validate_database_urls(self) -> None:
        """Validate database connection URLs"""
        # PostgreSQL URL validation
        if hasattr(settings, 'POSTGRES_HOST') and settings.POSTGRES_HOST:
            postgres_url = f"postgresql://{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
            self.result.config_summary["postgres_url"] = postgres_url
        
        # Redis URL validation
        if hasattr(settings, 'REDIS_HOST') and settings.REDIS_HOST:
            redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            self.result.config_summary["redis_url"] = redis_url
        
        # Neo4j URL validation
        if hasattr(settings, 'NEO4J_URI') and settings.NEO4J_URI:
            self.result.config_summary["neo4j_url"] = settings.NEO4J_URI
    
    def _generate_config_summary(self) -> None:
        """Generate configuration summary"""
        self.result.config_summary.update({
            "environment": getattr(settings, "ENVIRONMENT", "unknown"),
            "backend_port": os.environ.get("BACKEND_PORT", "8000"),
            "frontend_port": os.environ.get("FRONTEND_PORT", "3000"),
            "api_url": os.environ.get("NEXT_PUBLIC_API_URL", "not set"),
            "validation_status": "✅ PASSED" if self.result.is_valid else "❌ FAILED",
            "error_count": len(self.result.errors),
            "warning_count": len(self.result.warnings),
        })
    
    def get_validation_summary(self) -> dict:
        """
        Get complete validation summary.
        
        Returns:
            Dictionary containing validation results and configuration summary
            
        Validates Requirements: 10.1
        """
        return {
            "is_valid": self.result.is_valid,
            "errors": self.result.errors,
            "warnings": self.result.warnings,
            "config_summary": self.result.config_summary,
            "has_errors": self.result.has_errors(),
            "has_warnings": self.result.has_warnings(),
        }
    
    def format_validation_report(self) -> str:
        """
        Format a human-readable validation report.
        
        Returns:
            Formatted validation report string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("CONFIGURATION VALIDATION REPORT")
        lines.append("=" * 70)
        
        # Overall status
        status = "✅ PASSED" if self.result.is_valid else "❌ FAILED"
        lines.append(f"\nStatus: {status}")
        lines.append(f"Errors: {len(self.result.errors)}")
        lines.append(f"Warnings: {len(self.result.warnings)}")
        
        # Configuration summary
        if self.result.config_summary:
            lines.append("\n" + "-" * 70)
            lines.append("CONFIGURATION SUMMARY")
            lines.append("-" * 70)
            for key, value in self.result.config_summary.items():
                if isinstance(value, dict):
                    lines.append(f"\n{key.upper()}:")
                    for sub_key, sub_value in value.items():
                        lines.append(f"  {sub_key}: {sub_value}")
                else:
                    lines.append(f"{key}: {value}")
        
        # Errors
        if self.result.errors:
            lines.append("\n" + "-" * 70)
            lines.append("ERRORS")
            lines.append("-" * 70)
            for i, error in enumerate(self.result.errors, 1):
                lines.append(f"{i}. {error}")
        
        # Warnings
        if self.result.warnings:
            lines.append("\n" + "-" * 70)
            lines.append("WARNINGS")
            lines.append("-" * 70)
            for i, warning in enumerate(self.result.warnings, 1):
                lines.append(f"{i}. {warning}")
        
        lines.append("\n" + "=" * 70)
        
        return "\n".join(lines)


def get_config_validator() -> ConfigValidator:
    """
    Get a ConfigValidator instance.
    
    Returns:
        ConfigValidator instance
    """
    return ConfigValidator()
